"""Reasoning adapters and tool-use heads for Codex models."""

from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass
from typing import Any, Dict, Mapping

import torch
from codex_ml.config import ReasoningConfig, ReasoningHeadConfig, ToolAdapterConfig
from torch import nn

logger = logging.getLogger(__name__)


class ReasoningHead(nn.Module):
    """Projection head that maps hidden states to reasoning logits."""

    def __init__(self, cfg: ReasoningHeadConfig) -> None:
        super().__init__()
        self.cfg = cfg
        input_size = int(cfg.hidden_size)
        proj_size = int(cfg.projection_size)
        vocab = int(cfg.trace_vocab_size)
        self.projection = nn.Linear(input_size, proj_size)
        self.activation = nn.Tanh()
        self.dropout = nn.Dropout(cfg.dropout)
        self.decoder = nn.Linear(proj_size, vocab)

    def forward(self, hidden_state: torch.Tensor) -> torch.Tensor:  # type: ignore[override]
        if hidden_state.ndim == 1:
            hidden_state = hidden_state.unsqueeze(0)
        return self.decoder(self.dropout(self.activation(self.projection(hidden_state))))

    def summarise(self, logits: torch.Tensor, top_k: int) -> Dict[str, Any]:
        if logits.ndim == 1:
            logits = logits.unsqueeze(0)
        probs = torch.softmax(logits, dim=-1)
        k = max(1, min(int(top_k), probs.size(-1)))
        values, indices = torch.topk(probs, k, dim=-1)
        top_tokens = [
            {"token": int(idx), "probability": float(val)}
            for idx, val in zip(indices[0], values[0])
        ]
        top_probability = float(values[0, 0]) if values.numel() else None
        return {"top_tokens": top_tokens, "top_probability": top_probability}


class _Identity(nn.Module):
    def forward(self, x: torch.Tensor) -> torch.Tensor:  # pragma: no cover - trivial op
        return x


class ToolUseAdapter(nn.Module):
    """Lightweight classifier that proposes which tool to call."""

    def __init__(self, cfg: ToolAdapterConfig, hidden_size: int) -> None:
        super().__init__()
        if not cfg.enabled:
            raise ValueError("ToolUseAdapter requires an enabled configuration")
        self.cfg = cfg
        self.tools = tuple(str(tool) for tool in cfg.tools)
        if not self.tools:
            raise ValueError("ToolUseAdapter requires at least one tool name")
        target_dim = int(cfg.hidden_size or hidden_size)
        if target_dim != hidden_size:
            self.preprocess: nn.Module = nn.Linear(hidden_size, target_dim)
        else:
            self.preprocess = _Identity()
        self.classifier = nn.Linear(target_dim, len(self.tools))

    def _pool(
        self, hidden_state: torch.Tensor, attention_mask: torch.Tensor | None
    ) -> torch.Tensor:
        if hidden_state.ndim == 1:
            hidden_state = hidden_state.unsqueeze(0)
        if hidden_state.ndim == 2:
            return hidden_state
        if self.cfg.pooling == "cls":
            return hidden_state[:, 0]
        if self.cfg.pooling == "last":
            if attention_mask is not None and attention_mask.ndim == 2:
                lengths = attention_mask.sum(dim=1).to(dtype=torch.long)
                lengths = torch.clamp(lengths - 1, min=0)
                return hidden_state[torch.arange(hidden_state.size(0)), lengths]
            return hidden_state[:, -1]
        return hidden_state.mean(dim=1)

    def forward(  # type: ignore[override]
        self,
        hidden_state: torch.Tensor,
        attention_mask: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        pooled = self._pool(hidden_state, attention_mask)
        features = self.preprocess(pooled)
        logits = self.classifier(features)
        if self.cfg.temperature != 1.0:
            logits = logits / float(self.cfg.temperature)
        return logits, features


@dataclass
class ReasoningHarness:
    """Attach reasoning heads and optional tool adapters to a base model.

    Product / UI guidance:
    - ``trace_mode='disabled'`` is the safe baseline. Nothing beyond standard
      metrics is captured.
    - ``trace_mode='param-slice'`` is a diagnostic fingerprint only. It helps
      answer "is this the same model/config?" but it is **not** a narrative of
      how the model reasoned.
    - ``trace_mode='activation-snapshot'`` (future) will pool hidden activations
      plus metadata (curriculum phase, tool usage, evaluation preset) for richer
      offline audits. Even then the traces remain review-gated.

    Never market emitted traces as chain-of-thought.
    """

    config: ReasoningConfig
    head: ReasoningHead
    tool_adapter: ToolUseAdapter | None

    def __post_init__(self) -> None:
        self.history: deque[Dict[str, Any]] = deque(maxlen=self.config.trace_history)
        self.model: nn.Module | None = None

    def attach(self, model: Any) -> Any:
        if isinstance(model, nn.Module):
            self.model = model
            try:
                device = next(model.parameters()).device
            except StopIteration:
                device = torch.device("cpu")
            self.head.to(device=device)
            setattr(model, "reasoning_head", self.head)
            if self.tool_adapter is not None:
                self.tool_adapter.to(device=device)
                setattr(model, "tool_use_adapter", self.tool_adapter)
        else:
            self.model = None
        return model

    def record(self, payload: Mapping[str, Any]) -> None:
        self.history.append(dict(payload))

    def history_snapshot(self) -> list[Dict[str, Any]]:
        return [dict(item) for item in self.history]

    # Trace capture semantics are configured via `training.reasoning.trace_mode`
    # (see configs/training/reasoning/baseline.yaml). Keep this comment aligned
    # with config guidance so downstream surfaces stay honest.
    #
    #   "disabled" (current baseline)
    #       Skip trace capture entirely. Use this for day-to-day iteration.
    #
    #   "param-slice" (diagnostic fingerprint)
    #       Take a deterministic slice of the first trainable parameter tensor
    #       and log it. Useful for reproducibility / regression audits only.
    #       Not an interpretable chain-of-thought.
    #
    #   "activation-snapshot" (planned offline introspection)
    #       Pool forward-pass activations plus metadata (curriculum phase,
    #       tool usage, evaluation preset, etc.) for richer analysis.
    def _vectorise_model(self, model: Any) -> torch.Tensor:
        """Produce a trace vector for logging when traces are enabled.

        Current implementation (``trace_mode='param-slice'``) flattens a
        deterministic slice of the first trainable parameter tensor to produce
        a reproducibility fingerprint. Future "activation-snapshot" work will
        pool hidden activations together with curriculum/tool metadata.
        """
        size = int(self.head.cfg.hidden_size)
        try:
            head_device = next(self.head.parameters()).device
        except StopIteration:  # pragma: no cover - Linear modules always have params
            head_device = torch.device("cpu")
        buffer = torch.zeros(size, dtype=torch.float32, device=head_device)
        if not isinstance(model, nn.Module):
            return buffer
        first_param = None
        for param in model.parameters():
            if param.requires_grad and param.ndim > 0:
                first_param = param.detach().float().flatten()
                break
        if first_param is None:
            return buffer
        data = first_param.to(device=head_device)
        if data.numel() >= size:
            return data[:size]
        buffer[: data.numel()] = data
        return buffer

    def capture_trace(
        self,
        model: Any,
        *,
        epoch: int,
        step: int,
        top_k: int,
    ) -> Dict[str, Any]:
        with torch.no_grad():
            embedding = self._vectorise_model(model)
            logits = self.head(embedding)
            summary = self.head.summarise(logits, top_k)
            payload: Dict[str, Any] = {
                "epoch": epoch,
                "step": step,
                "top_tokens": summary["top_tokens"],
                "top_probability": summary.get("top_probability"),
                "embedding_norm": (
                    float(torch.sqrt(torch.sum(embedding * embedding)).item())
                    if embedding.numel()
                    else 0.0
                ),
            }
            if self.tool_adapter is not None and self.tool_adapter.cfg.enabled:
                tool_logits, pooled = self.tool_adapter(embedding)
                probs = torch.softmax(tool_logits, dim=-1)
                probs = probs.squeeze(0)
                best_idx = int(torch.argmax(probs))
                payload["tool_decision"] = {
                    "tool": self.tool_adapter.tools[best_idx],
                    "confidence": float(probs[best_idx]),
                    "distribution": {
                        name: float(probs[idx]) for idx, name in enumerate(self.tool_adapter.tools)
                    },
                }
                payload["tool_embedding_norm"] = float(
                    torch.sqrt(torch.sum(pooled * pooled)).item()
                )
        return payload


def attach_reasoning_adapters(
    model: Any,
    config: ReasoningConfig | Mapping[str, Any],
) -> ReasoningHarness:
    if not isinstance(config, ReasoningConfig):
        config = ReasoningConfig.from_mapping(dict(config))
    config.validate("training.reasoning")
    head = ReasoningHead(config.head)
    adapter: ToolUseAdapter | None = None
    if config.tool_adapter is not None and config.tool_adapter.enabled:
        adapter = ToolUseAdapter(config.tool_adapter, hidden_size=config.head.hidden_size)
    harness = ReasoningHarness(config=config, head=head, tool_adapter=adapter)
    harness.attach(model)
    return harness


__all__ = [
    "ReasoningHead",
    "ToolUseAdapter",
    "ReasoningHarness",
    "attach_reasoning_adapters",
]
