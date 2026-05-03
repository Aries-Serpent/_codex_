"""Reasoning adapters and tool-use heads for Codex models."""

from __future__ import annotations

import logging
from collections import deque
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Optional

import torch
from codex_ml.config import ReasoningConfig, ReasoningHeadConfig, ToolAdapterConfig

nn = torch.nn
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

    def forward(self, hidden_state: torch.Tensor) -> torch.Tensor:
        if hidden_state.ndim == 1:
            hidden_state = hidden_state.unsqueeze(0)
        return self.decoder(self.dropout(self.activation(self.projection(hidden_state))))

    def summarise(self, logits: torch.Tensor, top_k: int) -> dict[str, Any]:
        if logits.ndim == 1:
            logits = logits.unsqueeze(0)
        probs = torch.softmax(logits, dim=-1)
        k = max(1, min(int(top_k), probs.size(-1)))
        values, indices = torch.topk(probs, k, dim=-1)
        top_tokens = [
            {"token": int(idx), "probability": float(val)}
            for idx, val in zip(indices[0], values[0], strict=False)
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
        self, hidden_state: torch.Tensor, attention_mask: Optional[torch.Tensor]
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

    def forward(
        self,
        hidden_state: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
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
    - ``trace_mode='disabled'`` skips capture entirely.
    - ``trace_mode='weights'`` logs a deterministic summary of trainable
      weights for reproducibility audits (safe fallback).
    - ``trace_mode='activations'`` pools forward activations when provided via
      the training loop. This remains offline-only and review-gated.

    Never market emitted traces as chain-of-thought.
    """

    config: ReasoningConfig
    head: ReasoningHead
    tool_adapter: Optional[ToolUseAdapter]

    def __post_init__(self) -> None:
        self.history: deque[dict[str, Any]] = deque(maxlen=self.config.trace_history)
        self.model: Optional[nn.Module] = None
        trace_mode = str(getattr(self.config, "trace_mode", "weights")).lower()
        allowed = {"disabled", "weights", "activations"}
        if trace_mode not in allowed:
            logger.warning("Unknown trace mode '%s'; defaulting to 'weights'", trace_mode)
            trace_mode = "weights"
        self._trace_mode = trace_mode

    def attach(self, model: Any) -> Any:
        if isinstance(model, nn.Module):
            self.model = model
            try:
                device = next(model.parameters()).device
            except StopIteration:
                device = torch.device("cpu")
            self.head.to(device=device)
            model.reasoning_head = self.head
            if self.tool_adapter is not None:
                self.tool_adapter.to(device=device)
                model.tool_use_adapter = self.tool_adapter
        else:
            self.model = None
        return model

    def record(self, payload: Mapping[str, Any]) -> None:
        self.history.append(dict(payload))

    def history_snapshot(self) -> list[dict[str, Any]]:
        return [dict(item) for item in self.history]

    def _pool_hidden_states(
        self, hidden_states: Any, device: torch.device, size: int
    ) -> torch.Tensor:
        tensor = hidden_states
        if isinstance(tensor, Mapping):
            for key in ("hidden_states", "last_hidden_state"):
                if key in tensor:
                    tensor = tensor[key]
                    break
        if isinstance(tensor, (list, tuple)):
            tensor = tensor[-1]
        if not torch.is_tensor(tensor):
            try:
                tensor = torch.as_tensor(tensor)
            except Exception as err:
                logger.warning("Exception occurred", exc_info=True)
                raise TypeError("hidden_states must be convertible to a tensor") from err
        tensor = tensor.to(device=device, dtype=torch.float32)
        if tensor.ndim >= 2:
            dims = tuple(range(tensor.ndim - 1))
            tensor = tensor.mean(dim=dims)
        if tensor.ndim == 0:
            tensor = tensor.unsqueeze(0)
        if tensor.numel() >= size:
            return tensor[:size]
        buffer = torch.zeros(size, dtype=torch.float32, device=device)
        buffer[: tensor.numel()] = tensor
        return buffer

    # Trace capture semantics are configured via `training.reasoning.trace_mode`
    # (see configs/training/reasoning/baseline.yaml). Keep this comment aligned
    # with config guidance so downstream surfaces stay honest.
    def _vectorise_model(
        self, model: Any, *, hidden_states: Optional[Any] = None
    ) -> tuple[torch.Tensor, str]:
        """Produce a trace vector and record the effective capture mode."""

        size = int(self.head.cfg.hidden_size)
        try:
            head_device = next(self.head.parameters()).device
        except StopIteration:  # pragma: no cover - Linear modules always have params
            head_device = torch.device("cpu")

        mode_used = self._trace_mode
        if self._trace_mode == "activations":
            if hidden_states is None:
                logger.info(
                    "Activation trace requested but hidden states missing; "
                    "recording weight fingerprint instead",
                )
                mode_used = "weights"
            else:
                try:
                    tensor = self._pool_hidden_states(hidden_states, head_device, size)
                    return tensor, mode_used
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
                    logger.warning(
                        "Activation vectorization failed; falling back to weights: %s",
                        exc,
                    )
                    mode_used = "weights"

        buffer = torch.zeros(size, dtype=torch.float32, device=head_device)
        if not isinstance(model, nn.Module):
            return buffer, mode_used
        first_param = None
        for param in model.parameters():
            if param.requires_grad and param.ndim > 0:
                first_param = param.detach().float().flatten()
                break
        if first_param is None:
            return buffer, mode_used
        data = first_param.to(device=head_device)
        if data.numel() >= size:
            return data[:size], mode_used
        buffer[: data.numel()] = data
        return buffer, mode_used

    def capture_trace(
        self,
        model: Any,
        *,
        epoch: int,
        step: int,
        top_k: int,
        step_ctx: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        hidden_states = None
        if isinstance(step_ctx, Mapping):
            hidden_states = step_ctx.get("hidden_states")
        with torch.no_grad():
            embedding, trace_mode = self._vectorise_model(model, hidden_states=hidden_states)
            logits = self.head(embedding)
            summary = self.head.summarise(logits, top_k)
            payload: dict[str, Any] = {
                "epoch": epoch,
                "step": step,
                "top_tokens": summary["top_tokens"],
                "top_probability": summary.get("top_probability"),
                "embedding_norm": (
                    float(torch.sqrt(torch.sum(embedding * embedding)).item())
                    if embedding.numel()
                    else 0.0
                ),
                "trace_mode": trace_mode,
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
    adapter: Optional[ToolUseAdapter] = None
    if config.tool_adapter is not None and config.tool_adapter.enabled:
        adapter = ToolUseAdapter(config.tool_adapter, hidden_size=config.head.hidden_size)
    harness = ReasoningHarness(config=config, head=head, tool_adapter=adapter)
    harness.attach(model)
    return harness


__all__ = [
    "ReasoningHarness",
    "ReasoningHead",
    "ToolUseAdapter",
    "attach_reasoning_adapters",
]
