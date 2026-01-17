```yaml
branch: 0D_base_
pr: 1926
rollout_ring: 0D_base_
eval_preset: base
deployment_preset: reasoning_pod
generated_utc: 2025-10-30T03:51:18Z
```text

## File Survey: Branch 0D_base_ / PR #1926

### >>> FILE: src/codex_ml/training/unified_training.py@0D_base_

```python
[BEGIN CONTENT]
"""Unified Training Orchestrator (Superseding preliminary patch)

Capabilities:
 - Backend strategy selection (functional / legacy) with easy future extension.
 - Deterministic seeding.
 - Resume support via consolidated checkpoint_core.
 - Callback dispatch points.
 - Deprecation channel for legacy loop.
 - Structured result dictionary.

Schema Alignment:
 - Checkpoint metadata uses schema_version=2 (see checkpoint_core).

Usage:
    from codex_ml.training.unified_training import UnifiedTrainingConfig, run_unified_training
    cfg = UnifiedTrainingConfig(model_name="demo", epochs=1)
    run_unified_training(cfg)
"""

from __future__ import annotations

import contextlib
import importlib
import importlib.util
import json
import time
import warnings
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from codex_ml.training.strategies import TrainingCallback, TrainingResult, resolve_strategy
from codex_ml.utils.checkpoint_core import CheckpointMeta, load_checkpoint, save_checkpoint

try:  # optional torch
    import torch
except Exception:  # pragma: no cover
    torch = None  # type: ignore


# ----------------------------- Config & Validation ----------------------------


def _to_plain_container(value: Any) -> Any:
    """Best-effort conversion of OmegaConf containers to builtin types."""

    if isinstance(value, Mapping):
        return {k: _to_plain_container(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_to_plain_container(v) for v in value]
    return value


def _materialise_mapping(value: Mapping[str, Any] | None) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise TypeError("continual sections must be mappings")
    return {str(k): _to_plain_container(v) for k, v in value.items()}


@dataclass
class ContinualPhase:
    name: str
    epochs: int = 1
    dataset: dict[str, Any] = field(default_factory=dict)
    replay_ratio: float | None = None
    notes: str | None = None

    def __post_init__(self) -> None:
        if int(self.epochs) < 1:
            raise ValueError("continual phase epochs must be >= 1")
        self.epochs = int(self.epochs)
        if isinstance(self.dataset, Mapping):
            self.dataset = _materialise_mapping(self.dataset)
        if self.replay_ratio is not None:
            ratio = float(self.replay_ratio)
            if not 0.0 <= ratio <= 1.0:
                raise ValueError("continual replay_ratio must be between 0 and 1")
            self.replay_ratio = ratio


@dataclass
class ContinualConfig:
    strategy: str = "replay"
    buffer_size: int | None = None
    replay_ratio: float | None = None
    active_corpus: str | None = None
    corpora: dict[str, Any] = field(default_factory=dict)
    curriculum: dict[str, Any] = field(default_factory=dict)
    rehearsal: dict[str, Any] = field(default_factory=dict)
    phases: list[ContinualPhase] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.buffer_size is not None:
            self.buffer_size = int(self.buffer_size)
            if self.buffer_size < 0:
                raise ValueError("continual buffer_size must be >= 0")
        if self.replay_ratio is not None:
            ratio = float(self.replay_ratio)
            if not 0.0 <= ratio <= 1.0:
                raise ValueError("continual replay_ratio must be between 0 and 1")
            self.replay_ratio = ratio
        if self.active_corpus is not None:
            self.active_corpus = str(self.active_corpus)
        self.corpora = _materialise_mapping(self.corpora)
        self.curriculum = _materialise_mapping(self.curriculum)
        self.rehearsal = _materialise_mapping(self.rehearsal)
        raw_phases: Sequence[Any] | None = self.phases
        normalised: list[ContinualPhase] = []
        for phase in raw_phases or []:
            if isinstance(phase, ContinualPhase):
                normalised.append(phase)
            elif isinstance(phase, Mapping):
                normalised.append(ContinualPhase(**_materialise_mapping(phase)))
            else:
                raise TypeError("continual phases must be mappings or ContinualPhase instances")
        self.phases = normalised

# ... [omitted for brevity] ...
    with contextlib.suppress(Exception):  # pragma: no cover
        (ckpt_dir / "metadata.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
        )


def run_unified_training(
    cfg: UnifiedTrainingConfig,
    callbacks: Iterable[TrainingCallback] | None = None,
    ndjson_log_path: str | None = None,
) -> dict[str, Any]:
    """Execute training under unified orchestrator."""
    start = time.time()
    _seed_all(cfg.seed)

    backend_name = _auto_backend(cfg)
    strategy = resolve_strategy(backend_name)

    # State object passed to callbacks (extendable)
    state: dict[str, Any] = {
        "backend_name": backend_name,
        "global_step": 0,
        "resume_from": cfg.resume_from,
    }
    if isinstance(cfg.continual, ContinualConfig):
        state["continual"] = asdict(cfg.continual)

    # Pre-resume load if requested
    if cfg.resume_from:
        try:
            loaded_state, _ = load_checkpoint(cfg.resume_from)
            payload_keys = sorted(loaded_state.keys()) if isinstance(loaded_state, dict) else []
            state.update({"resume_loaded": True, "resume_payload_keys": payload_keys})
        except Exception as exc:  # pragma: no cover
            state.update({"resume_error": repr(exc)})

    class _StateRelay:
        __slots__ = ("_callback", "_shared_state")

        def __init__(self, callback: TrainingCallback, shared_state: dict[str, Any]) -> None:
            self._callback = callback
            self._shared_state = shared_state

        def __getattr__(self, name: str) -> Any:  # pragma: no cover - passthrough
            return getattr(self._callback, name)

        def _merge_state(self, payload: Any) -> None:
            if isinstance(payload, dict):
                self._shared_state.update(payload)

        def on_train_start(self, state: dict[str, Any]) -> None:
            del state
            method = getattr(self._callback, "on_train_start", None)
            if callable(method):
                method(self._shared_state)

        def on_epoch_start(self, epoch: int, state: dict[str, Any]) -> None:
            self._merge_state(state)
            method = getattr(self._callback, "on_epoch_start", None)
            if callable(method):
                method(epoch, self._shared_state)

        def on_epoch_end(self, epoch: int, metrics: dict[str, Any], state: dict[str, Any]) -> Any:
            self._merge_state(state)
            method = getattr(self._callback, "on_epoch_end", None)
            if callable(method):
                return method(epoch, metrics, self._shared_state)
            return None

        def on_step(
            self, batch_index: int, global_step: int, loss: float, state: dict[str, Any]
        ) -> Any:
            self._merge_state(state)
            method = getattr(self._callback, "on_step", None)
            if callable(method):
                return method(batch_index, global_step, loss, self._shared_state)
            return None

        def on_checkpoint(
            self, epoch: int, path: str, metrics: dict[str, Any], state: dict[str, Any]
        ) -> Any:
[END CONTENT]
```text

### >>> FILE: src/codex_ml/train_loop.py@0D_base_

```python
[BEGIN CONTENT]
# PATCH: Added CUDNN determinism helper, checkpoint SHA256 hashing, config snapshot,
# retention policy execution, & metadata enhancements.
#
# New params:
#   deterministic_cudnn: bool = False
#   run_config: dict | None  (persisted to config.snapshot.json if provided)
#   retention_policy: dict | None  (e.g. {"keep_last":3, "keep_every":5})
#
# Metadata additions:
#   - latest.json now includes "checkpoint_sha256"
#   - metadata.json includes "checkpoint_sha256"
#   - final result includes "checkpoint_sha256_last"
#
# Behavior:
#   - Config snapshot written once per run (overwrites existing file).
#   - After saving an epoch checkpoint, optional retention pruning executes.

from __future__ import annotations

import argparse
import json
import logging
import os
import random
import sys
import time
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional
from uuid import uuid4

from codex_ml.codex_structured_logging import get_session_id, get_session_logger
from codex_ml.config import (
    ConfigError,
    ReasoningConfig,
    ReasoningHeadConfig,
    ReasoningObjectiveConfig,
    ToolAdapterConfig,
)
from codex_ml.logging.ndjson_logger import is_legacy_mode

if TYPE_CHECKING:
    from codex_ml.models.reasoning import ReasoningHarness

try:
    from codex_ml.models.reasoning import attach_reasoning_adapters

    _HAS_REASONING_ADAPTERS = True
except Exception:  # noqa: BLE001
    attach_reasoning_adapters = None  # type: ignore[assignment]
    _HAS_REASONING_ADAPTERS = False
from codex_ml.monitoring import CodexMetricsRegistry, metrics_enabled
from codex_ml.training.dp_config import DifferentialPrivacyConfig, make_private_model
from codex_ml.utils.checkpoint import load_checkpoint, save_checkpoint
from codex_ml.utils.checksum import sha256sum

try:
    from codex_ml.utils.repro import record_dataset_checksums
except Exception:  # noqa: BLE001

    def record_dataset_checksums(*_, **__):  # type: ignore
        return {}


try:
    from codex_ml.utils.seeding import set_reproducible
except Exception:  # noqa: BLE001

    def set_reproducible(*_, **__):  # type: ignore
        return None


try:
    from codex_ml.telemetry import start_metrics_server
except Exception:  # noqa: BLE001

    def start_metrics_server(*_, **__):  # type: ignore
        return None


try:
    import mlflow

    _HAS_MLFLOW = True
except Exception:  # noqa: BLE001
    mlflow = None  # type: ignore
    _HAS_MLFLOW = False

logger = logging.getLogger(__name__)
ART_DIR = Path("artifacts")
_TELEMETRY_JSON_ENABLED = True

try:
    import torch
    from torch import nn, optim
    from torch.optim.lr_scheduler import StepLR
    from torch.utils.data import DataLoader, Dataset

# ... [omitted for brevity] ...

        def __len__(self) -> int:  # pragma: no cover - simple container
            return self._data.size(0)

        def __getitem__(self, index: int):  # pragma: no cover - exercised indirectly
            return self._data[index]

else:

    class ToyDataset:  # type: ignore[override]
        def __init__(self, *_, **__):
            raise RuntimeError("Torch is required to construct ToyDataset")

        def __len__(self) -> int:  # pragma: no cover - defensive
            return 0

        def __getitem__(self, index: int):  # pragma: no cover - defensive
            raise RuntimeError("Torch is required to construct ToyDataset")


@dataclass
class ReasoningRuntime:
    config: ReasoningConfig
    harness: ReasoningHarness
    store_path: Path | None
    per_epoch_limit: int
    top_k: int
    threshold: float | None
    traces_written: int = 0

    def bind_model(self, model: Any) -> None:
        try:
            self.harness.attach(model)
        except Exception as exc:  # pragma: no cover - defensive attachment guard
            logger.warning("Failed to bind reasoning modules to model: %s", exc)

    def on_new_epoch(self) -> None:
        self.traces_written = 0

    def should_capture(self) -> bool:
        if getattr(self.config, "trace_mode", None) == "disabled":
            return False
        if self.per_epoch_limit <= 0:
            return True
        return self.traces_written < self.per_epoch_limit

    def record_trace(
        self,
        model: Any,
        *,
        epoch: int,
        step: int,
        art_dir_path: Path | None,
        session_id: str | None,
        step_ctx: Mapping[str, Any] | None = None,
    ) -> None:
        if not self.should_capture():
            return
        try:
            trace = self.harness.capture_trace(
                model,
                epoch=epoch,
                step=step,
                top_k=self.top_k,
                step_ctx=step_ctx,
            )
        except Exception as exc:  # pragma: no cover - defensive capture guard
            logger.debug("Skipping reasoning trace capture: %s", exc)
            return
        if not trace:
            return
        probability = trace.get("top_probability")
        if self.threshold is not None and probability is not None and probability < self.threshold:
            return
        payload = {
            "type": "reasoning_trace",
            "timestamp": _now_ts(),
            "epoch": epoch,
            "step": step,
            "mode": self.config.objective.mode,
            "session_id": session_id or get_session_id(),
# ... [omitted for brevity] ...
    desired: Any,
    device: Any,
    art_dir_path: Path | None,
) -> Any:
    """Cast a batch/tensor according to policy and emit telemetry.

    Policies:
      - to_model_dtype: cast to the model dtype if available
      - to_fp32: cast to torch.float32
      - none/other: no-op
    """
    if policy is None:
        return sample
    policy_norm = str(policy).lower()
    event_payload: Dict[str, Any] = {
        "type": "telemetry",
        "event": "dataset_cast",
        "policy": policy_norm,
    }
    status = "skipped"
    reason: Optional[str] = None
    try:
        import torch as _torch
    except Exception:
        reason = "torch_unavailable"
        event_payload["status"] = status
        event_payload["reason"] = reason
        _append_metrics_event(art_dir_path, event_payload)
        return sample
    try:
        src_dtype = getattr(sample, "dtype", None)
    except Exception:
        src_dtype = None
    if src_dtype is not None:
        event_payload["from"] = str(src_dtype)
    target_dtype = None
    if policy_norm == "to_model_dtype" and desired is not None:
        target_dtype = desired
    elif policy_norm == "to_fp32":
        target_dtype = getattr(_torch, "float32", None)
    else:
        reason = "policy_unhandled"
    if target_dtype is None:
        if target_dtype is not None:
            event_payload["to"] = str(target_dtype)
        event_payload["status"] = status
        event_payload["reason"] = reason or "no_target_dtype"
        _append_metrics_event(art_dir_path, event_payload)
        return sample
    casted = sample
    event_payload["to"] = str(target_dtype)
    try:
        if target_dtype is not None and hasattr(sample, "to"):
            casted = sample.to(device if device is not None else _torch.device("cpu"))
            casted = casted.to(dtype=target_dtype)
            status = "cast"
        else:
            reason = "no_to_method"
    except Exception as exc:  # noqa: BLE001
        logger.warning("Dataset cast policy '%s' failed: %s", policy_norm, exc)
        reason = f"cast_failed:{exc.__class__.__name__}"
    if reason is not None:
        event_payload["reason"] = reason
    event_payload["status"] = status
    _append_metrics_event(art_dir_path, event_payload)
    return casted


def _make_casting_collate(policy: str | None, desired: Any, device: Any, art_dir_path: Path | None):
    """Return a DataLoader collate_fn that casts batch elements per policy.

    The collate keeps shapes and simply applies _cast_batch_for_policy element‑wise.
    """

    def _collate(batch):
        if policy is None:
            return batch
        try:
            import torch as _torch  # noqa: F401
        except Exception:
            return batch
[END CONTENT]
```text

### >>> FILE: src/codex_ml/training/strategies.py@0D_base_

```python
[BEGIN CONTENT]
"""Backend strategy interfaces for the unified training orchestrator.

Each strategy MUST implement:
    - run(config, callbacks) -> TrainingResult
    - name (property / attribute)

Callbacks receive:
    on_epoch_start(epoch, state)
    on_epoch_end(epoch, metrics, state)
    on_step(batch_index, global_step, loss, state)
    on_checkpoint(epoch, path, metrics, state)

Minimal surface keeps legacy + functional backends pluggable.
"""

from __future__ import annotations

from collections.abc import Iterable as IterableABC
from contextlib import suppress
from copy import deepcopy
from dataclasses import asdict, dataclass, is_dataclass, replace
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Protocol

from codex_ml.data.jsonl_loader import load_jsonl


class TrainingCallback(Protocol):
    def on_epoch_start(self, epoch: int, state: Dict[str, Any]) -> None: ...

    def on_epoch_end(
        self, epoch: int, metrics: Dict[str, float], state: Dict[str, Any]
    ) -> None: ...

    def on_step(
        self, batch_index: int, global_step: int, loss: float, state: Dict[str, Any]
    ) -> None: ...

    def on_checkpoint(
        self, epoch: int, path: str, metrics: Dict[str, float], state: Dict[str, Any]
    ) -> None: ...


class NoOpCallback:
    def on_epoch_start(self, epoch: int, state: Dict[str, Any]) -> None: ...

    def on_epoch_end(
        self, epoch: int, metrics: Dict[str, float], state: Dict[str, Any]
    ) -> None: ...

    def on_step(
        self, batch_index: int, global_step: int, loss: float, state: Dict[str, Any]
    ) -> None: ...

    def on_checkpoint(
        self, epoch: int, path: str, metrics: Dict[str, float], state: Dict[str, Any]
    ) -> None: ...


@dataclass
class TrainingResult:
    status: str
    backend: str
    final_epoch: int
    output_dir: str
    extra: Dict[str, Any]


class BackendStrategy(Protocol):
    backend_name: str

    def run(
        self,
        config: Any,
        callbacks: Iterable[TrainingCallback],
        resume_from: Optional[str] = None,
    ) -> TrainingResult: ...


def _safe_callbacks(callbacks: Iterable[TrainingCallback]) -> List[TrainingCallback]:
    return list(callbacks) if callbacks else [NoOpCallback()]


# ---- Strategy Implementations ------------------------------------------------


class FunctionalStrategy:
    """Adapter around existing functional_training module."""

    backend_name = "functional"

    def run(
        self,
        config: Any,
        callbacks: Iterable[TrainingCallback],
        resume_from: Optional[str] = None,
    ) -> TrainingResult:
        ft_module = import_module("codex_ml.training.functional_training")
        TrainConfig = getattr(ft_module, "TrainConfig")
        train_fn = getattr(ft_module, "train")

        extra_payload: Dict[str, Any] = {}

        # Minimal shim; functional loop currently handles internal logging.
        for cb in callbacks:
            try:
                cb.on_epoch_start(0, {"resume_from": resume_from})
            except Exception:
                pass

        functional_overrides: Dict[str, Any] = {}
        if isinstance(getattr(config, "extra", None), dict):
            functional_overrides.update(config.extra)
            nested = config.extra.get("functional")
            if isinstance(nested, dict):
                functional_overrides.update(nested)
            nested = config.extra.get("functional_training")
            if isinstance(nested, dict):
                functional_overrides.update(nested)

        train_texts = functional_overrides.pop("train_texts", None)
        if train_texts is None:
            train_texts = functional_overrides.pop("texts", [])
        if isinstance(train_texts, str):
            train_texts = [train_texts]
        elif isinstance(train_texts, IterableABC):
            train_texts = list(train_texts)
        elif train_texts and not isinstance(train_texts, bool):
            train_texts = [train_texts]
        else:
            train_texts = []
        val_texts = functional_overrides.pop(
            "val_texts", functional_overrides.pop("eval_texts", None)
        )
        model_override = functional_overrides.pop("model", None)

        cfg_payload: Dict[str, Any] = {
            "model_name": config.model_name,
            "epochs": config.epochs,
# ... [omitted for brevity] ...


class ContinualReplayStrategy:
    """Phase-by-phase continual-learning wrapper around the functional strategy."""

    backend_name = "continual_replay"

    def __init__(self, base_strategy: BackendStrategy | None = None) -> None:
        self._base = base_strategy or FunctionalStrategy()

    def _coerce_text_list(self, value: Any) -> list[str]:
        if value is None or value is False:
            return []
        if isinstance(value, str):
            return [value]
        if isinstance(value, IterableABC):
            return [str(item) for item in value if item]
        return [str(value)]

    def _materialize_dataset_texts(
        self, dataset: Any, *, seed: int
    ) -> tuple[list[str], list[str]] | None:
        if not isinstance(dataset, dict):
            return None

        if "texts" in dataset:
            train_items = self._coerce_text_list(dataset.get("texts"))
            val_items = self._coerce_text_list(dataset.get("val_texts"))
            return train_items, val_items

        path = dataset.get("path")
        if not path:
            return None

        format_hint = str(dataset.get("format", "jsonl") or "").lower()
        dataset_seed_raw = dataset.get("seed")
        try:
            dataset_seed = int(dataset_seed_raw if dataset_seed_raw is not None else seed)
        except (TypeError, ValueError):
            dataset_seed = seed

        val_fraction_raw = dataset.get("val_fraction")
        try:
            val_fraction = float(val_fraction_raw) if val_fraction_raw is not None else 0.0
        except (TypeError, ValueError):
            val_fraction = 0.0

        target_path = Path(str(path))

        if format_hint in {"jsonl", "ndjson"}:
            train_texts, val_texts = load_jsonl(
                target_path,
                seed=dataset_seed,
                val_fraction=val_fraction,
            )
            return train_texts, val_texts

        if format_hint in {"text", "txt"}:
            try:
                payload = target_path.read_text(encoding="utf-8")
            except OSError:
                return [], []
            texts = [line.strip() for line in payload.splitlines() if line.strip()]
            return texts, []

        # Fallback: treat the provided path (or object) as direct training text.
        return self._coerce_text_list(path), []

    def _resolve_schedule(self, config: Any) -> list[dict[str, Any]]:
        extra = getattr(config, "extra", {}) or {}
        continual = extra.get("continual", {}) if isinstance(extra, dict) else {}
        phases = continual.get("phases") if isinstance(continual, dict) else None
        if not phases:
            continual_cfg = getattr(config, "continual", None)
            if continual_cfg:
                if isinstance(continual_cfg, dict):
                    phases = continual_cfg.get("phases")
                else:
                    phases = getattr(continual_cfg, "phases", None)
        if not phases:
            phases = getattr(config, "continual_schedule", None)
[END CONTENT]
```text

### >>> FILE: src/codex_ml/models/reasoning.py@0D_base_

```python
[BEGIN CONTENT]
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
    - ``trace_mode='disabled'`` skips capture entirely.
    - ``trace_mode='weights'`` logs a deterministic summary of trainable
      weights for reproducibility audits (safe fallback).
    - ``trace_mode='activations'`` pools forward activations when provided via
      the training loop. This remains offline-only and review-gated.

    Never market emitted traces as chain-of-thought.
    """

    config: ReasoningConfig
    head: ReasoningHead
    tool_adapter: ToolUseAdapter | None

    def __post_init__(self) -> None:
        self.history: deque[Dict[str, Any]] = deque(maxlen=self.config.trace_history)
        self.model: nn.Module | None = None
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

    def _pool_hidden_states(
        self, hidden_states: Any, device: torch.device, size: int
    ) -> torch.Tensor:
        tensor = hidden_states
        if isinstance(tensor, Mapping):
            for key in ("hidden_states", "last_hidden_state"):
                if key in tensor:
                    tensor = tensor[key]
# ... [omitted for brevity] ...
                    "recording weight fingerprint instead",
                )
                mode_used = "weights"
            else:
                try:
                    tensor = self._pool_hidden_states(hidden_states, head_device, size)
                    return tensor, mode_used
                except Exception as exc:
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
        step_ctx: Mapping[str, Any] | None = None,
    ) -> Dict[str, Any]:
        hidden_states = None
        if isinstance(step_ctx, Mapping):
            hidden_states = step_ctx.get("hidden_states")
        with torch.no_grad():
            embedding, trace_mode = self._vectorise_model(model, hidden_states=hidden_states)
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
[END CONTENT]
```text

### >>> FILE: configs/training/reasoning/baseline.yaml@0D_base_

```yaml
[BEGIN CONTENT]
# Template: Baseline reasoning overlay enabling traces and curriculum hooks.
# @package _global_
defaults:
  - ../base

# === CONTROL SURFACE (local-first) ===
# The fields below are the documented knobs surfaced via `codex repo-map --reasoning`
# and the deployment dry-run workflow. Adjusting them does not require code changes.

# Trace capture mode controls what is recorded for reasoning analysis.
# - weights:     legacy mode; summarize trainable weights (safe fallback)
# - activations: new mode; capture forward activations when available
trace_capture:
  mode: weights

curriculum:
  # preset is the curriculum name exposed to PM/infra reviewers.
  preset: starter
  phase_schedule: ${.preset}

evaluation:
  # preset defines which evaluation suite must pass before promotion.
  preset: base

deployment:
  # preset points at the expected dry-run deployment manifest.
  preset: reasoning_pod

reasoning:
  template: baseline

training:
  reasoning:
    enabled: true
    # Trace capture inherits from the top-level `trace_capture.mode` knob.
    trace_mode: "weights"
    trace_history: 128
    log_probability_threshold: 0.15
    objective:
      mode: chain_of_thought
      weight: 1.0
      max_traces_per_epoch: 6
      log_top_k: 5
      trace_store: reasoning_traces.ndjson
    head:
      hidden_size: 768
      projection_size: 256
      trace_vocab_size: 64
      dropout: 0.05
    tool_adapter:
      enabled: false

logging:
  reasoning_trace: true

metadata:
  # rollout_ring declares intent in the promotion ladder and is enforced by
  # `codex deploy --dry-run` when composing the dry-run manifest.
  # 0A_base_ → 0B_base_ → 0C_base_ → 0D_base_ → main.
  # It is an intent badge, not permission to ship.
  rollout_ring: 0D_base_
  owner: reasoning-foundations

# Documentation:
# Switch `trace_capture.mode` to `activations` when the model / loop supports
# passing hidden states. If unavailable, the system falls back to `weights`.
# See `src/codex_ml/models/reasoning.py` for details.

[END CONTENT]
```text

### >>> FILE: configs/training/reasoning/curricula/starter.yaml@0D_base_

```yaml
[BEGIN CONTENT]
phase_schedule:
  - id: warmup
    dataset: datasets/reasoning/warmup.jsonl
    steps: 200
    metrics:
      - reasoning.trace_coverage
  - id: first_principles
    dataset: datasets/reasoning/first_principles.jsonl
    steps: 400
    metrics:
      - reasoning.win_rate
      - reasoning.critique_density
  - id: challenge
    dataset: datasets/reasoning/challenge.jsonl
    steps: 300
    metrics:
      - reasoning.latency_p95
      - reasoning.judge_disagreement

[END CONTENT]
```text

### >>> FILE: configs/evaluation/reasoning/base.yaml@0D_base_

```yaml
[BEGIN CONTENT]
# Base reasoning evaluation configuration.
# Runs theorem proving accuracy, math verification, and tool trace audits
# over the sample reasoning corpora bundled with Codex ML.

defaults:
  - override hydra/job_logging: disabled
  - override hydra/hydra_logging: disabled
  - _self_

datasets:
  proof_logs:
    path: ${oc.env:CODEX_REASONING_DATA_DIR, ${hydra:runtime.cwd}/data/sample/reasoning}/proof_logs.jsonl
    limit: ${oc.env:CODEX_REASONING_PROOF_LIMIT, 50}
  math_word_problems:
    path: ${oc.env:CODEX_REASONING_DATA_DIR, ${hydra:runtime.cwd}/data/sample/reasoning}/math_word_problems.jsonl
    limit: ${oc.env:CODEX_REASONING_MATH_LIMIT, 50}
  tool_traces:
    path: ${oc.env:CODEX_REASONING_DATA_DIR, ${hydra:runtime.cwd}/data/sample/reasoning}/tool_traces.jsonl
    limit: ${oc.env:CODEX_REASONING_TOOL_LIMIT, 50}

probes:
  - theorem_proving
  - math_verification
  - tool_audit

output:
  dir: ${oc.env:CODEX_REASONING_EVAL_DIR, ${hydra:runtime.cwd}/artifacts/reasoning_eval}
  summary_filename: summary.json
  records_filename: records.ndjson
  metrics_filename: metrics.ndjson

logging:
  tags:
    gate: reasoning
    severity: info

hydra:
  run:
    dir: .
  output_subdir: null
  job:
    chdir: false

[END CONTENT]
```text

### >>> FILE: src/codex_ml/eval/evaluator.py@0D_base_

```python
[BEGIN CONTENT]
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import uuid
from collections.abc import Callable, Iterable, Mapping, MutableMapping, Sequence
from contextlib import suppress
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from codex_ml.metrics.registry import register as register_metric
from codex_ml.utils.hf_pinning import load_from_pretrained
from codex_ml.utils.hf_revision import get_hf_revision
from codex_ml.utils.optional import optional_import

from ..tracking.writers import NdjsonWriter
from .fallback import synthetic_alignment
from .metrics import perplexity, token_accuracy

torch, _HAS_TORCH = optional_import("torch")
datasets, _HAS_DATASETS = optional_import("datasets")
transformers, _HAS_TRANSFORMERS = optional_import("transformers")
lean_dojo, _HAS_LEAN_DOJO = optional_import("lean_dojo")
sympy, _HAS_SYMPY = optional_import("sympy")
jsonschema, _HAS_JSONSCHEMA = optional_import("jsonschema")

try:  # pragma: no cover - optional dependency
    from omegaconf import DictConfig, OmegaConf
except Exception:  # pragma: no cover - optional dependency absent
    DictConfig = OmegaConf = None  # type: ignore[assignment]
else:  # pragma: no cover - register lightweight env resolver
    with suppress(Exception):
        if not OmegaConf.has_resolver("oc.env"):
            OmegaConf.register_new_resolver(
                "oc.env",
                lambda key, default=None: os.environ.get(key, default),
            )

try:  # pragma: no cover - optional dependency
    import hydra
except Exception:  # pragma: no cover - optional dependency absent
    hydra = None  # type: ignore[assignment]

if _HAS_SYMPY:
    simplify = getattr(sympy, "simplify", None)
    sympify = getattr(sympy, "sympify", None)
else:  # pragma: no cover - optional dependency absent
    simplify = sympify = None  # type: ignore[assignment]

if _HAS_JSONSCHEMA:
    Draft7Validator = getattr(jsonschema, "Draft7Validator", None)
else:  # pragma: no cover - optional dependency absent
    Draft7Validator = None  # type: ignore[assignment]

_TOOL_EVENT_VALIDATOR: Any | None = None
if _HAS_JSONSCHEMA and Draft7Validator is not None:  # pragma: no cover - optional path
    try:
        _TOOL_EVENT_VALIDATOR = Draft7Validator(  # type: ignore[assignment]
            {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "arguments": {"type": "object"},
                    "observation": {"type": ["string", "number"]},
                },
                "required": ["name"],
                "additionalProperties": True,
            }
        )
    except Exception:  # pragma: no cover - schema compilation best-effort
        _TOOL_EVENT_VALIDATOR = None

ReasoningRecord = Mapping[str, Any]
ReasoningDatasetMap = Mapping[str, Sequence[ReasoningRecord]]
ProbeResult = Mapping[str, float | int | None]

Dataset = datasets.Dataset if _HAS_DATASETS else None  # type: ignore[attr-defined,assignment]
AutoModelForCausalLM = (
    transformers.AutoModelForCausalLM if _HAS_TRANSFORMERS else None
)  # type: ignore[attr-defined,assignment]
AutoTokenizer = (
    transformers.AutoTokenizer if _HAS_TRANSFORMERS else None
)  # type: ignore[attr-defined,assignment]


class EvaluationDependencyError(ImportError):
    """Raised when optional evaluation dependencies are unavailable."""

    def __init__(self, missing: Sequence[str]) -> None:
        self.missing = tuple(missing)
        super().__init__("Evaluation requires optional packages: " + ", ".join(self.missing))

    @property
    def hint(self) -> str:
        return (
            "Install the evaluation extras or call "
            "`codex_ml.eval.fallback.synthetic_alignment` for lightweight metrics."
        )


def _missing_dependencies(
    require_transformers: bool = False, *, require_datasets: bool = False
) -> list[str]:
    missing: list[str] = []
    if not _HAS_TORCH:
        missing.append("torch")
    if require_datasets and not _HAS_DATASETS:
        missing.append("datasets")
    if require_transformers and not _HAS_TRANSFORMERS:
        missing.append("transformers")
    return missing


def evaluate_model(model, tokenizer, texts: Iterable[str]) -> dict[str, float]:
    missing = _missing_dependencies(require_datasets=True)
    if missing:
        raise EvaluationDependencyError(missing)
    ds = Dataset.from_dict({"text": list(texts)})
    column = list(ds["text"])
    toks = tokenizer(column, return_tensors="pt", padding=True)
    input_ids = toks["input_ids"]
    with torch.no_grad():
        out = model(input_ids, labels=input_ids)
    logits = out.logits
    pred_ids = logits.argmax(-1).reshape(-1).tolist()
    target_ids = input_ids.reshape(-1).tolist()
    pad = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else -100
    acc = token_accuracy(pred_ids, target_ids, ignore_index=pad)
    ppl = perplexity(logits.reshape(-1, logits.shape[-1]).tolist(), target_ids, ignore_index=pad)
    return {"token_accuracy": acc, "perplexity": ppl}


def _to_float(value: Any) -> float | None:
    if value is None:
# ... [omitted for brevity] ...
        if callable(candidate):
            metric_fn = candidate  # type: ignore[assignment]
    max_batches = 0
    if isinstance(config, Mapping):
        with suppress(Exception):
            max_batches = int(config.get("max_batches", 0) or 0)

    aggregator = _MetricAggregator()
    was_training = getattr(model, "training", False)

    if hasattr(model, "eval"):
        model.eval()

    try:
        with torch.no_grad():
            for idx, batch in enumerate(dataloader):
                if max_batches and idx >= max_batches:
                    break
                moved_batch = _move_batch_to_device(batch, device)
                outputs = _invoke_model(model, moved_batch)
                metrics: MutableMapping[str, Any] = _collect_metric_candidates(outputs, metric_keys)
                if metric_fn is not None:
                    try:
                        extra_metrics = metric_fn(outputs, moved_batch)
                    except Exception as exc:  # pragma: no cover - surfacing user errors
                        raise RuntimeError("metric_fn raised an exception") from exc
                    else:
                        if extra_metrics:
                            metrics.update(dict(extra_metrics))
                aggregator.update(metrics, batch_size=_infer_batch_size(moved_batch))
    finally:
        if hasattr(model, "train"):
            model.train(was_training)

    return aggregator.summary()


def run_evaluator(model_name: str, texts: Iterable[str]) -> dict[str, float]:
    missing = _missing_dependencies(require_transformers=True, require_datasets=True)
    if missing:
        raise EvaluationDependencyError(missing)
    tokenizer = load_from_pretrained(
        AutoTokenizer,
        model_name,
        revision=get_hf_revision(),
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = load_from_pretrained(
        AutoModelForCausalLM,
        model_name,
        revision=get_hf_revision(),
    )
    return evaluate_model(model, tokenizer, texts)


def lite_sequence_evaluation(
    predictions: Iterable[str], references: Iterable[str]
) -> dict[str, float]:
    """Compute lightweight metrics without importing torch/datasets."""

    summary = synthetic_alignment(predictions, references)
    return summary.as_dict()


_NUMERIC_PATTERN = re.compile(r"-?\d+(?:\.\d+)?(?:/[1-9]\d*(?:\.\d+)?)?")
_TOOL_PATTERN = re.compile(r"Tool\[(?P<name>[^\]]+)\]", re.IGNORECASE)
_ENV_PATTERN = re.compile(r"\${oc\.env:([^,}]+)(?:,\s*([^}]+))?}")
_HYDRA_CWD_PATTERN = re.compile(r"\${hydra:runtime\.cwd}")


def _resolve_string_placeholders(text: str) -> str:
    result = text
    if not result:
        return result
    result = _HYDRA_CWD_PATTERN.sub(Path.cwd().as_posix(), result)
    while True:
        match = _ENV_PATTERN.search(result)
        if not match:
            break
        var = match.group(1).strip()
        default = match.group(2)
        default_value = default.strip() if default is not None else ""
        replacement = os.environ.get(var, default_value)
        replacement_str = (
            _resolve_string_placeholders(str(replacement))
            if isinstance(replacement, str)
            else str(replacement)
        )
        result = result[: match.start()] + replacement_str + result[match.end() :]
    return os.path.expanduser(result)


def _resolve_structure_placeholders(value: Any) -> Any:
    if isinstance(value, str):
        return _resolve_string_placeholders(value)
    if isinstance(value, Mapping):
        return {key: _resolve_structure_placeholders(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_resolve_structure_placeholders(item) for item in value]
    if isinstance(value, tuple):
# ... [omitted for brevity] ...
        records_filename: str | None = None
    elif isinstance(records_filename_raw, str) and records_filename_raw.strip():
        records_filename = records_filename_raw
    elif records_filename_raw is None:
        records_filename = "records.ndjson"
    else:
        records_filename = None

    metrics_raw = output_cfg.get("metrics_filename") if isinstance(output_cfg, Mapping) else None
    metrics_filename = (
        metrics_raw if isinstance(metrics_raw, str) and metrics_raw else "metrics.ndjson"
    )

    probes_cfg = resolved_cfg.get("probes") if isinstance(resolved_cfg, Mapping) else None
    probes: Sequence[str] | None
    if isinstance(probes_cfg, str):
        probes = [probes_cfg]
    elif isinstance(probes_cfg, Sequence) and not isinstance(probes_cfg, (str, bytes)):
        probes = [str(item) for item in probes_cfg]
    else:
        probes = None

    logging_cfg = resolved_cfg.get("logging") if isinstance(resolved_cfg, Mapping) else None
    tags_cfg = logging_cfg.get("tags") if isinstance(logging_cfg, Mapping) else None
    tags = dict(tags_cfg) if isinstance(tags_cfg, Mapping) else None
    result = run_reasoning_probes(
        datasets,
        probes=probes,
        output_dir=output_dir,
        summary_filename=summary_filename,
        records_filename=records_filename,
        metrics_filename=metrics_filename,
        tags=tags,
    )
    return result


_BOOLEAN_TRUE = {
    "true",
    "t",
    "yes",
    "y",
    "1",
    "pass",
    "proved",
    "valid",
    "success",
    "ok",
}
_BOOLEAN_FALSE = {"false", "f", "no", "n", "0", "fail", "invalid", "error"}


def _normalise_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    return " ".join(text.split()).strip().lower()


def _coerce_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    if isinstance(value, (int, float)):
        if value in {0, 1}:
            return bool(value)
        return None
    if isinstance(value, str):
        token = value.strip().lower()
        if token in _BOOLEAN_TRUE:
[END CONTENT]
```text

### >>> FILE: src/codex_cli/app.py@0D_base_

```python
[BEGIN CONTENT]

from __future__ import annotations

import os
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Optional, Tuple

REASONING_TEMPLATE_ROOT = Path(__file__).resolve().parents[2] / "configs" / "training" / "reasoning"
REASONING_CURRICULA_ROOT = REASONING_TEMPLATE_ROOT / "curricula"

_USE_TYPER = False
try:  # pragma: no cover - prefer Typer when available
    import typer as _typer  # type: ignore
    if hasattr(_typer, "Typer"):
        _USE_TYPER = True
except Exception:  # pragma: no cover - Typer shadowed/unavailable
    _USE_TYPER = False

if _USE_TYPER:
    echo = _typer.echo
    Exit = _typer.Exit
else:  # pragma: no cover - click fallback
    import click as _click

    echo = _click.echo

    class Exit(SystemExit):
        def __init__(self, code: int = 0) -> None:
            super().__init__(code)


def _track_smoke_impl(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 1)
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def _split_smoke_impl(seed: int) -> None:
    total = 20
    try:
        import torch
        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def _checkpoint_smoke_impl(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint
        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2)
    echo(f"Saved {path}")


if _USE_TYPER:
    app = _typer.Typer(
        name="codex",
        add_completion=False,
        help="Codex CLI for reasoning templates plus local/offline runs (tokenize/train/eval/tracking).",
    )

    def _discover_reasoning_templates() -> Sequence[Tuple[str, str, Path]]:
        if not REASONING_TEMPLATE_ROOT.exists():
            return []
        entries: list[Tuple[str, str, Path]] = []
        for path in sorted(REASONING_TEMPLATE_ROOT.glob("*.yaml")):
            description = "Reasoning template"
            try:
                with path.open("r", encoding="utf-8") as handle:
                    for line in handle:
                        stripped = line.strip()
                        if stripped.startswith("#"):
                            text = stripped.lstrip("#").strip()
                            if text and "Template" in text:
                                description = text
                                break
                        elif stripped:
                            break
            except OSError:
                description = "Reasoning template"
            entries.append((path.stem, description, path))
        return entries

    def _load_yaml(path: Path) -> dict:
        try:
            import yaml  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency missing
            echo(f"PyYAML not available: {exc}")
            raise Exit(code=1)
        try:
            with path.open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle) or {}
        except Exception as exc:
            echo(f"Failed to load {path}: {exc}")
            raise Exit(code=1)
        if not isinstance(data, dict):
            echo(f"Unexpected config structure in {path}")
            raise Exit(code=1)
        return data

    reasoning_templates = _typer.Typer(
        name="reasoning-templates",
        help="Surface reasoning training presets and curricula metadata.",
    )

    @reasoning_templates.command("list")
    def list_reasoning_templates() -> None:
        entries = _discover_reasoning_templates()
        if not entries:
            echo("No reasoning templates found under configs/training/reasoning.")
            return
        for name, description, path in entries:
            try:
                relative = path.relative_to(Path.cwd())
            except ValueError:
                relative = path
            echo(f"{name}\t{description} ({relative})")

    @reasoning_templates.command("explain")
    def explain_reasoning_template(name: str) -> None:
        entries = {entry[0]: entry for entry in _discover_reasoning_templates()}
        if name not in entries:
            echo(f"Unknown reasoning template: {name}")
            available = ", ".join(sorted(entries)) or "<none>"
            echo(f"Available templates: {available}")
            raise Exit(code=1)
        _, description, path = entries[name]
        echo(description)
        echo(f"Path: {path}")
        data = _load_yaml(path)
        curriculum_name = data.get("curriculum", {}).get("phase_schedule") if isinstance(data.get("curriculum"), dict) else None
        if curriculum_name:
            schedule_path = REASONING_CURRICULA_ROOT / f"{curriculum_name}.yaml"
            if schedule_path.exists():
                schedule_data = _load_yaml(schedule_path)
                phases = schedule_data.get("phase_schedule")
                if isinstance(phases, Iterable):
                    echo("Phases:")
                    for phase in phases:
                        if isinstance(phase, dict):
                            phase_id = phase.get("id", "<unknown>")
                            dataset = phase.get("dataset", "<dataset>")
                            steps = phase.get("steps", "?")
                            echo(f"  - {phase_id}: {dataset} (steps={steps})")
# ... [omitted for brevity] ...
        _track_smoke_impl(dir)

    @app.command("split-smoke")
    def split_smoke(seed: int = 1337) -> None:
        _split_smoke_impl(seed)

    @app.command("checkpoint-smoke")
    def checkpoint_smoke(
        out_dir: Path = _typer.Option(Path(".checkpoints"), "--out", help="Checkpoint directory"),
    ) -> None:
        _checkpoint_smoke_impl(out_dir)
else:  # pragma: no cover - click fallback
    import click as _click

    @_click.group(name="codex", help="Codex CLI for reasoning templates plus local/offline runs (tokenize/train/eval/tracking).")
    def app() -> None:
        """Codex offline smoke helpers."""

    def _discover_reasoning_templates() -> Sequence[Tuple[str, str, Path]]:
        if not REASONING_TEMPLATE_ROOT.exists():
            return []
        entries: list[Tuple[str, str, Path]] = []
        for path in sorted(REASONING_TEMPLATE_ROOT.glob("*.yaml")):
            description = "Reasoning template"
            try:
                with path.open("r", encoding="utf-8") as handle:
                    for line in handle:
                        stripped = line.strip()
                        if stripped.startswith("#"):
                            text = stripped.lstrip("#").strip()
                            if text and "Template" in text:
                                description = text
                                break
                        elif stripped:
                            break
            except OSError:
                description = "Reasoning template"
            entries.append((path.stem, description, path))
        return entries

    def _load_yaml(path: Path) -> dict:
        try:
            import yaml  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency missing
            echo(f"PyYAML not available: {exc}")
            raise Exit(code=1)
        try:
            with path.open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle) or {}
        except Exception as exc:
            echo(f"Failed to load {path}: {exc}")
            raise Exit(code=1)
        if not isinstance(data, dict):
            echo(f"Unexpected config structure in {path}")
            raise Exit(code=1)
        return data

    @app.command("version")
    def version() -> None:
        try:
            from . import __version__
        except Exception:  # pragma: no cover - defensive fallback
            __version__ = "unknown"
        echo(__version__)

    @app.command("track-smoke")
    @_click.option("--dir", "dir_", type=_click.Path(path_type=Path), default=None, help="Local mlruns dir")
    def track_smoke(dir_: Optional[Path]) -> None:
        _track_smoke_impl(dir_)

    @app.command("split-smoke")
    @_click.option("--seed", type=int, default=1337, show_default=True, help="Seed for deterministic split")
    def split_smoke(seed: int) -> None:
        _split_smoke_impl(seed)

    @app.command("checkpoint-smoke")
    @_click.option("--out", "out_dir", type=_click.Path(path_type=Path), default=Path(".checkpoints"), show_default=True, help="Checkpoint directory")
    def checkpoint_smoke(out_dir: Path) -> None:
        _checkpoint_smoke_impl(out_dir)

    @app.group(name="reasoning-templates", help="Surface reasoning training presets and curricula metadata.")
    def reasoning_templates() -> None:
        """Reasoning template helpers."""

    @reasoning_templates.command("list")
    def list_reasoning_templates() -> None:
        entries = _discover_reasoning_templates()
        if not entries:
            echo("No reasoning templates found under configs/training/reasoning.")
            return
        for name, description, path in entries:
            try:
                relative = path.relative_to(Path.cwd())
            except ValueError:
                relative = path
            echo(f"{name}\t{description} ({relative})")

    @reasoning_templates.command("explain")
    @_click.argument("name")
    def explain_reasoning_template(name: str) -> None:
        entries = {entry[0]: entry for entry in _discover_reasoning_templates()}
[END CONTENT]
```text

### >>> FILE: src/codex_ml/cli/codex_cli.py@0D_base_

```python
[BEGIN CONTENT]
from __future__ import annotations

import json
import sys
from collections.abc import Sequence
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import click

from codex_ml.cli.status_report import build_status_report
from codex_ml.codex_structured_logging import (
    ArgparseJSONParser,
    capture_exceptions,
    init_json_logging,
    log_event,
    run_cmd,
)
from codex_ml.config import ConfigError, load_app_config
from codex_ml.telemetry import start_metrics_server
from codex_ml.utils.provenance import export_environment, load_environment_summary
from codex_utils.ndjson import NDJSONLogger

_ = (ArgparseJSONParser, run_cmd)

DEFAULT_TOKENIZER_CONFIG = "configs/training/tokenization/base.yaml"
DEFAULT_TOKENIZER_JSON = "artifacts/tokenizers/default/default/tokenizer.json"


@lru_cache(maxsize=1)
def _get_tokenizer_pipeline():
    try:
        from codex_ml.tokenization import pipeline as tokenizer_pipeline
    except ModuleNotFoundError as exc:  # pragma: no cover - surfaced via Click
        missing = (exc.name or "").split(".", 1)[0]
        if missing == "tokenizers":
            raise click.ClickException(
                "Tokenizer commands require the optional 'tokenizers' dependency. "
                "Install it to enable tokenizer CLI functionality."
            ) from exc
        raise
    return tokenizer_pipeline


@click.group()
def codex() -> None:
    """Codex command line interface."""


def _emit_provenance_summary(provenance_dir: Path) -> None:
    summary = load_environment_summary(provenance_dir)
    if summary:
        click.echo(json.dumps(summary, sort_keys=True))


@codex.group()
def tokenizer() -> None:
    """Tokenizer pipeline utilities."""


@tokenizer.command("train")
@click.option(
    "--config",
    default=DEFAULT_TOKENIZER_CONFIG,
    show_default=True,
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    help="Path to the tokenizer pipeline configuration file.",
)
@click.option(
    "--streaming/--no-streaming",
    default=None,
    help="Enable or disable streaming ingestion (defaults to the config value).",
)
@click.option(
    "--stream-chunk-size",
    type=click.IntRange(min=1),
    default=None,
    help=(
        "Override the streaming chunk size in characters "
        "(defaults to 1 MiB when streaming is enabled)."
    ),
)
@click.option("--dry-run", is_flag=True, help="Print the training plan without running.")
def tokenizer_train(
    config: str, streaming: bool | None, stream_chunk_size: int | None, dry_run: bool
) -> None:
    """Train a tokenizer according to the provided configuration."""
    tokenizer_pipeline = _get_tokenizer_pipeline()
    try:
        out_dir = tokenizer_pipeline.run_train(
            config,
            streaming=streaming,
            stream_chunk_size=stream_chunk_size,
            dry_run=dry_run,
        )
    except tokenizer_pipeline.TokenizerPipelineError as exc:
        raise click.ClickException(str(exc)) from exc
    if dry_run:
        click.echo("dry run complete")
        return
    click.echo(f"tokenizer artifacts written to {out_dir}")


@tokenizer.command("validate")
@click.option(
    "--config",
    default=DEFAULT_TOKENIZER_CONFIG,
    show_default=True,
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    help="Path to the tokenizer pipeline configuration file.",
)
def tokenizer_validate(config: str) -> None:
    """Validate dataset manifests and cached tokenizer artifacts."""
    tokenizer_pipeline = _get_tokenizer_pipeline()
    try:
        report = tokenizer_pipeline.run_validate(config)
    except tokenizer_pipeline.TokenizerPipelineError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(report, indent=2, sort_keys=True))
# ... [omitted for brevity] ...
    else:
        click.echo("prometheus_client missing", err=True)


@codex.command()
@click.argument("text")
def tokenize(text: str) -> None:
    from codex_ml.tokenization.hf_tokenizer import HFTokenizerAdapter

    tok = HFTokenizerAdapter.load()
    ids = tok.encode(text)
    click.echo(str(ids))


@codex.command()
@click.option(
    "--reasoning",
    is_flag=True,
    help=(
        "Emit reasoning-specific control surface entries (curriculum preset, "
        "trace_mode, rollout ring, evaluation preset, deployment preset)."
    ),
)
def repo_map(reasoning: bool) -> None:
    """Print a repository summary (optionally including reasoning knobs)."""

    from codex_ml.cli.repo_map import render_repo_map

    try:
        click.echo(render_repo_map(reasoning=reasoning))
    except TypeError:
        # Back-compat with older render_repo_map signatures lacking the flag.
        click.echo(render_repo_map())


@codex.command()
@click.option(
    "--config",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to deployment preset YAML (e.g. configs/deploy/reasoning_pod.yaml).",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Required flag. Perform offline validation only; never touch live infra.",
)
@click.option(
    "--run-metadata-dir",
    default=Path("runs/train_loop"),
    show_default=True,
    type=click.Path(file_okay=False, path_type=Path),
    help="Directory containing run_metadata.json from the latest TrainLoop run.",
)
def deploy(config: Path, dry_run: bool, run_metadata_dir: Path) -> None:
    """Validate reasoning pod deployment readiness in dry-run mode."""

    from codex_ml.cli.deploy import run_deploy_dry_run

    if not dry_run:
        click.secho(
            "DEPLOYMENT BLOCKED: --dry-run is required in this rollout ring.",
            err=True,
        )
        raise SystemExit(1)

    try:
        summary = run_deploy_dry_run(
            config_path=config,
            dry_run=dry_run,
            run_metadata_dir=run_metadata_dir,
        )
    except RuntimeError as exc:
        click.secho(f"DEPLOYMENT BLOCKED: {exc}", err=True)
        raise SystemExit(1) from exc

    click.echo(json.dumps(summary, indent=2))


@codex.command("status-report")
@click.option(
    "--run-metadata-dir",
    default=Path("runs/train_loop"),
    show_default=True,
    type=click.Path(file_okay=False, path_type=Path),
    help=(
        "Directory containing run_metadata.json / evaluation.json / reasoning.json "
        "from the most recent TrainLoop run."
    ),
)
def status_report(run_metadata_dir: Path) -> None:
    """Summarize offline promotion readiness for `0D_base_` → `main`."""

    summary = build_status_report(run_metadata_dir)
    click.echo(json.dumps(summary, indent=2))


@codex.command()
@click.option(
    "--config",
    default="configs/evaluation/base.yaml",
    show_default=True,
    type=click.Path(dir_okay=False, path_type=str),
    help="Path to the evaluation configuration.",
)
@click.argument("overrides", nargs=-1)
@click.option(
    "--metrics-only",
    is_flag=True,
    help="Print only the `metrics` mapping to stdout (machine-readable).",
)
@click.option(
    "--seed",
    type=int,
    default=None,
    help="Override the evaluation seed (best-effort determinism).",
)
@click.option(
    "--log-metrics",
    type=click.Path(dir_okay=False, path_type=str),
    default=None,
[END CONTENT]
```text

### >>> FILE: docs/README_ROOT.md@0D_base_

````markdown
[BEGIN CONTENT]
# codex-universal

<!-- manifest-digest:start -->
[![Manifest SHA256](https://img.shields.io/badge/manifest-unknown-blue)](#)
<!-- manifest-digest:end -->

The `_codex_` image now centers on **reasoning agents**. Use this document as the top-level map for roadmap milestones,
architecture references, and the bespoke-model hosting workflow that underpins every guided rollout.

## Orientation

| Goal | Where to start |
| --- | --- |
| Understand the reasoning roadmap | [Reasoning milestones](#reasoning-roadmap-milestones) |
| Skim architecture dependencies | [Architecture diagrams](#architecture-at-a-glance) |
| Launch a bespoke model | [Hosting bespoke reasoning models](#hosting-bespoke-reasoning-models) |
| Train/evaluate/deploy | [Guided pipelines](#guided-reasoning-pipelines) |

### Repo Map (Reasoning-Focused)
You can now surface a reasoning-focused repository map:

````bash
codex repo-map --reasoning
```text

This highlights reasoning overlays, evaluation presets, and trace-capture knobs.

## Reasoning roadmap milestones

| Milestone | Focus | Target signal |
| --- | --- | --- |
| **M0: Observability baseline** | Boot instrumented inference traces across offline smoke runs. | Trace coverage ≥95% on curated reasoning templates. |
| **M1: Curriculum-first training** | Establish first-principles curricula and replay strategies. | `reasoning.win_rate` ≥0.55 on `benchmarks/cot-lite`. |
| **M2: Model hosting hardening** | Promote bespoke models into hermetic serving pods. | Shadow-hosted latency p95 ≤ 700 ms with parity alerts. |
| **M3: Flywheel automation** | Continuous evaluation + redeploy gates orchestrated via Codex. | Weekly redeploy cadence with zero manual overrides. |

Track milestone burndown using the `reasoning_status` table exported by:

```bash
codex repo-map --reasoning
```text

Slice specific categories (for example, rollout rings and curricula) with:

```bash
codex repo-map --reasoning --include rollout_ring --include curriculum
```text

For backlog triage, anchor discussions in [`docs/guides/reasoning_overview.md`](guides/reasoning_overview.md).

### Control surface knobs and promotion checklist

`codex repo-map --reasoning` surfaces a shared set of knobs defined in
[`configs/training/reasoning/baseline.yaml`](../configs/training/reasoning/baseline.yaml):

- `trace_mode`
- `curriculum.preset`
- `evaluation.preset`
- `deployment.preset`
- `metadata.rollout_ring`

Every smoke run of the training loop writes machine-readable artifacts under `runs/train_loop/`:

- `run_metadata.json` — captures `metadata.*`, the selected presets, and the rollout ring.
- `reasoning.json` — snapshot of the reasoning harness configuration plus runtime summary.
- `evaluation.json` — evaluation preset enforced for the run.

Promotion toward `main` requires:

1. The evaluation preset to pass (or carry explicit sign-off in status reports).
2. `metadata.rollout_ring` declared in the training config and matching the target pod ring.
3. `codex deploy --dry-run` to succeed, which enforces the ring match between training output and `configs/deploy/reasoning_pod.yaml`.

Reviewers preparing a `0D_base_` → `main` merge should walk the dedicated checklist in [`docs/ops/promotion_checklist.md`](ops/promotion_checklist.md).
It also requires attaching the outputs of:

- `codex_ml.cli.codex_cli status-report`
- `codex_ml.cli.codex_cli deploy --dry-run`
- and linking the latest `docs/status_updates/survey-<ring>-and-<PR>-<DATESTAMP>.md`

## Architecture at a glance

The canonical topology is captured in [`docs/diagrams/architecture.svg`](diagrams/architecture.svg). Pair it with the
Mermaid source (`architecture.mmd`) when proposing changes so reviewers can diff rendered assets and source together.

Key flows:

1. **Authoring** — Hydra configuration layers resolve reasoning templates from `configs/training/reasoning/*` before model
   instantiation.
2. **Training** — Training is orchestrated by:
   - `src/codex_ml/training/unified_training.py`
     (deterministic seeding, checkpoint / resume plumbing,
      continual replay strategy hooks),
   - `src/codex_ml/train_loop.py`
     (per-run executor that injects the reasoning harness,
      logs traces, and rotates checkpoints).
   These modules together are "the trainer".
   They replace older references to a standalone
   `codex_ml.trainer.ReasoningTrainer`.
3. **Deployment** — Bespoke models are packaged with manifest digests
   and signed hooks for downstream registries.

When modifying the topology, update both the diagram and [`docs/guides/serving_reproducibility.md`](guides/serving_reproducibility.md).

## Hosting bespoke reasoning models

1. **Bootstrap the project**
   ```bash
   uv sync --extra reasoning --extra cli --frozen
   source .venv/bin/activate
   codex repo-map --reasoning
   ```
2. **Select a template** using `codex reasoning-templates list` (see [`codex_cli`](../src/codex_cli/app.py)). Templates
   live under `configs/training/reasoning/` and ship default datasets plus evaluator bindings.
3. **Materialise runtime overlays**
   ```bash
   codex-train +reasoning=baseline curriculum.phase_schedule=starter
   ```
   This composes reasoning overrides on top of the legacy defaults so classical experiments keep working.
4. **Register the artifact** with deterministic metadata before handoff:
   ```bash
   codex register --bundle artifacts/runs/reasoning-baseline \
     --expect manifest.sha256 --tag reasoning/m0/bespoke
   ```

For service integrations, adopt the PodSpec defined in
[`docs/deployment/reasoning_pod.md`](deployment/reasoning_pod.md).
This PodSpec is a **dry-run template**, not production hosting.
Its job is to make resource shape, telemetry, curriculum phase,
trace capture mode, and rollout ring explicit before anything moves
toward `main`. A dry-run configuration is provided at
[`configs/deploy/reasoning_pod.yaml`](https://github.com/Aries-Serpent/_codex_/blob/main/configs/deploy/reasoning_pod.yaml).
Link the generated manifest to your rollout plan.

## Guided reasoning pipelines

Follow the deep dives in the new guides:

- [`docs/guides/reasoning_overview.md`](guides/reasoning_overview.md) — systems overview and milestone guardrails.
- [`docs/guides/first_principles_curricula.md`](guides/first_principles_curricula.md) — curriculum design and evaluation cadences.

### Training quickstart

```bash
codex-train +reasoning=baseline \
  curriculum.phase_schedule=starter \
  training.max_steps=500 \
  logging.reasoning_trace=true \
  training.output_dir=artifacts/runs/reasoning-starter
```text

The `+reasoning=baseline` defaults hook into `configs/training/reasoning/baseline.yaml` and emit trace artefacts that downstream
analysis notebooks can load. Curricula definitions are stored as YAML fragments so you can diff changes between cohorts.

### Evaluation handoff

```bash
codex evaluate --config configs/evaluation/reasoning.yaml \
  --log-metrics .codex/metrics/reasoning.ndjson \
  --run-id reasoning-milestone-m1
```text

Every evaluation appends to the NDJSON ledger with per-phase metrics. Use `codex metrics summarize` for quick trend
checks when preparing milestone readouts.

### Deployment checks

```bash
codex deploy --config configs/deploy/reasoning_pod.yaml \
  --dry-run

# Optional: if your train loop emits run metadata to a non-default path:
# codex deploy --config configs/deploy/reasoning_pod.yaml \
#   --run-metadata-dir runs/train_loop \
#   --dry-run
```text
Always leave `--dry-run` in place. The manifest is a review artifact, not a production action, and the embedded
`rollout_ring` is an intent badge rather than permission to ship. Dry runs confirm manifest parity, bundler signatures,
and runtime allowances required by bespoke hosts. Redeployments should always be paired with
`codex reasoning-templates explain <name>` to document why a template was chosen.

## Offline validation helpers

```bash
HF_DATASETS_OFFLINE=1 TRANSFORMERS_OFFLINE=1 CODEX_MLFLOW_ENABLE=0 WANDB_MODE=offline \
  nox -s tests_offline
```text

This run exports standard offline toggles and keeps artefacts under `.codex/` for reproducibility (metrics, checkpoints,
reasoning traces). Combine it with `codex_cli.app checkpoint-smoke` to validate serialization paths without GPUs.

## Next steps

1. Align sprint planning with the [milestones](#reasoning-roadmap-milestones).
2. Review [`docs/guides/reasoning_overview.md`](guides/reasoning_overview.md) before opening architecture PRs.
3. Wire bespoke hosting expectations into status reports using the templates in [`docs/templates`](templates/README.md).

[END CONTENT]
````

### >>> FILE: docs/README.md@0D_base_

````markdown
[BEGIN CONTENT]
# Documentation index

Welcome to the `_codex_` knowledge base. Start here to navigate the reasoning roadmap, architectural references, and
hands-on guides that keep bespoke model hosting disciplined.

## 🧭 Orientation pillars
- **Reasoning roadmap** — Track milestone health and forward-looking bets in [`README_ROOT.md`](./README_ROOT.md).
- **Architecture** — Pair [`diagrams/architecture.svg`](./diagrams/architecture.svg) with the systems notes in
  [`guides/reasoning_overview.md`](./guides/reasoning_overview.md).
- **Curriculum design** — Apply the phased training playbooks from
  [`guides/first_principles_curricula.md`](./guides/first_principles_curricula.md).
- **Bespoke hosting expectations** — Align ops and status updates with [`deployment/reasoning_pod.md`](./deployment/reasoning_pod.md)
  and the rollout checklists under [`templates/`](./templates/README.md).

### Reasoning Pod Deployment
Refer to [`deployment/reasoning_pod.md`](./deployment/reasoning_pod.md) and
[`https://github.com/Aries-Serpent/_codex_/blob/main/configs/deploy/reasoning_pod.yaml`](https://github.com/Aries-Serpent/_codex_/blob/main/configs/deploy/reasoning_pod.yaml) for dry-run deployment guidance.
These assets are designed for offline validation and do not require hosted services.

## 🚀 Quick links for reasoning teams
- **Reasoning templates in the CLI** — `codex reasoning-templates list` surfaces curated training/eval bundles. See the
  [`codex_cli` help](../src/codex_cli/app.py) for command details.
- **End-to-end quickstart** — Follow [`quickstart.md`](./quickstart.md) with the `+reasoning=baseline` overrides highlighted in
  [`README_ROOT.md`](./README_ROOT.md#training-quickstart).
- **Evaluation ledger** — Use [`guides/reasoning_overview.md`](./guides/reasoning_overview.md#evaluation-readiness) to configure
  NDJSON metrics pipelines.
- **Deployment guardrails** — Cross-check bespoke model expectations against [`guides/serving_reproducibility.md`](./guides/serving_reproducibility.md).

## 📋 Operational templates
Operational templates encode recurring delivery rituals so teams can execute migrations, hardening passes, and planning
checkpoints with consistent safeguards. Begin with the [Operational Templates index](./templates/README.md) to review
prerequisites, required metadata, and cross-references before copying a template into your service.

### When to use a template
- You are planning a migration or hardening effort that will cross team boundaries.
- You need an auditable checklist with rollback, communications, and verification steps.
- You want a consistent structure for maintaining ≥85% coverage through scoped test additions.

### Quick links
- [Migration — Python File Relocation](./templates/Migration_PythonFileRelocation.md)
- [Migration — CLI Hardening](./templates/Migration_CLIHardening.md)
- [Planning — Intent Validation](./templates/Planning_IntentValidation.md)

### Handoff checklist
Each template includes role guidance (developers draft → maintainers execute), `[PLACEHOLDER: …]` prompts, and success
criteria aligned with the coverage standard. Ensure the following before requesting review:

1. All placeholders are replaced with repo-specific context and linked artifacts.
2. Rollback and communication steps point to real runbooks or dashboards.
3. The template is stored alongside the service codebase (usually under `docs/`) and linked from the change description or PR.

See [`docs/CONTRIBUTING.md`](./CONTRIBUTING.md#using-operational-templates) for the full drafting workflow and role expectations.

## Conventions
- Keep docs small and composable.
- Use a single fenced `diff` block for proposed patches in prompts/guides.
- Prefer citations to live repo files when referencing code or config.

## Deployment and Operational Expectations

To generate and review a deployment manifest for a bespoke reasoning agent,
run a dry-run deploy. Example:

```bash
codex deploy \
  --config configs/deploy/reasoning_pod.yaml \
  --model artifacts/runs/reasoning-starter:last \
  --dry-run
```text

This renders the "reasoning pod" manifest for inspection. It does **not**
create or update any live service. See [`deployment/reasoning_pod.md`](./deployment/reasoning_pod.md)
for what that pod is expected to look like (resources, telemetry, trace
capture mode, curriculum phase, etc.). The CLI intentionally supports
dry-run review only — there is no automatic apply step, and the embedded
`rollout_ring` is declarative intent, not permission.

Always keep `--dry-run` in place; manifests must be reviewed before any
apply/rollout tooling is engaged.

### Rollout rings

This repository uses staged rollout rings to represent maturity and review
state:

* `0A_base_` / `0B_base_`: active development, unstable knobs.
* `0C_base_`: integration of multiple features landing together.
* `0D_base_`: release candidate. Content here should be explainable
  to Engineering and Product.
* `main`: canonical internal "alpha product" surface after approval.

When you generate a deployment manifest (`configs/deploy/reasoning_pod.yaml`),
it includes a `rollout_ring` field. That field is a declaration of intent
("this artifact is targeting 0D_base_ next"), not permission to ship.

Nothing targeting `main` should be treated as eligible for hosting without:
1. offline evaluation gates passing,
2. trace/curriculum settings documented,
3. explicit signoff.

## Related
- Project audit ritual: see `AUDIT_PROMPT.md`
- CHANGELOG practices follow “Keep a Changelog” with an **Unreleased** section at the top.

---
Last updated: 2025-10-25

[END CONTENT]
````

### >>> FILE: docs/guides/reasoning_overview.md@0D_base_

````markdown
[BEGIN CONTENT]
# Reasoning overview

This guide orients you across the systems, checkpoints, and metrics that define the reasoning roadmap. Keep it close when
triaging milestones or proposing architectural changes.

## Milestone guardrails

| Milestone | Gate | Acceptance notes |
| --- | --- | --- |
| M0 | Trace coverage ≥95% on curated templates | Validate with `codex metrics summarize --metric reasoning.trace_coverage`. |
| M1 | Curriculum win rate ≥0.55 on `benchmarks/cot-lite` | Run the curriculum smoke in [First principles curricula](first_principles_curricula.md). |
| M2 | Shadow latency p95 ≤700 ms | Capture with `codex deploy --dry-run --latency-report`. |
| M3 | Weekly redeploy cadence with zero manual overrides | Enforced by the deployment checklist in [`templates/`](../templates/README.md). |

Milestones build sequentially: do not advance without closing action items or documenting explicit risk trade-offs in
[`status_updates/`](../status_updates/).

## Systems topology

1. **Authoring** — Hydra defaults stitch reasoning templates from `configs/training/reasoning/` with classical knobs. Updating a
   template requires bumping the manifest digest and notifying deployment partners.
2. **Training** — Training and trace capture are coordinated by the
   unified training stack:
   - `src/codex_ml/training/unified_training.py`
     exposes configuration for curriculum phases, continual replay,
     and resume strategy,
   - `src/codex_ml/train_loop.py`
     executes a single run, attaches the reasoning harness,
     and logs traces / checkpoints.
   When these docs refer to "the trainer", they mean this pair of
   modules (plus the Hydra overlays in
   `configs/training/reasoning/*`), not a class literally named
   `ReasoningTrainer`.
   Trace payloads mirror the schema described in [`../reference/reasoning_trace.md`](../reference/reasoning_trace.md).
3. **Evaluation** — Evaluators register under `codex_ml.eval.registry`. The reasoning profile uses tiered NDJSON ledgers
   (`.codex/metrics/reasoning.ndjson`) that feed status reports.
4. **Deployment** — Serving pods mount bespoke model bundles and rely on `codex deploy` to enforce manifest parity.

When proposing topology changes, update [`../diagrams/architecture.svg`](../diagrams/architecture.svg) and include a short
rationale in `status_updates/`.

## Training pipeline

1. Select a template: `codex reasoning-templates list` → choose an entry (for example `baseline`).
2. Compose overrides:
   ```bash
   codex-train +reasoning=baseline \
     curriculum.phase_schedule=starter \
     training.max_steps=500
   ```
3. Inspect traces:
   ```bash
   codex metrics summarize --metric reasoning.trace_coverage \
     --source .codex/metrics/reasoning.ndjson
   ```
4. Promote artifacts via `codex register --bundle ... --tag reasoning/<milestone>`.

Use the `curriculum.phase_schedule` knob to align experiment duration with milestone targets. For ablations, document the
variant name in `training.output_dir` so trace comparisons remain legible.

## Evaluation pipeline

1. Generate evaluation inputs with `codex datasets materialize --preset reasoning/baseline`.
2. Run the evaluator:
   ```bash
   codex evaluate --config configs/evaluation/reasoning.yaml \
     --run-id reasoning-milestone-m1 \
     --log-metrics .codex/metrics/reasoning.ndjson
   ```
3. Append commentary to `status_updates/<milestone>.md` summarising regressions or deltas.
4. Trigger the optional smoke: `codex evaluate --config ... --metrics-only` for dashboard-friendly output.

## Deployment pipeline

1. Validate manifests:
   ```bash
   codex deploy --config configs/deploy/reasoning_pod.yaml \
     --model artifacts/runs/reasoning-starter:last \
     --dry-run
   ```
2. Shadow host in the target environment and confirm p95 latency ≤700 ms.
3. Update [`../deployment/reasoning_pod.md`](../deployment/reasoning_pod.md) with any override notes.
4. Promote the template via `codex reasoning-templates explain <name>` and store the explanation alongside the rollout PR.

## Observability

- **Trace ledger** — `.codex/metrics/reasoning.ndjson` (mirrors the evaluation ledger for quick correlation).
- **Model registry** — `artifacts/runs/<experiment>` seeded by `codex register`.
- **Redeploy dashboard** — Link your dashboards in [`../status_updates/README.md`](../status_updates/README.md) so releases can
  reference the same views.

Keep observability wiring hermetic: do not rely on third-party plugins without documenting mocks or fallbacks.

[END CONTENT]
````

### >>> FILE: docs/guides/first_principles_curricula.md@0D_base_

````markdown
[BEGIN CONTENT]
# First principles curricula

Curriculum-first training anchors the reasoning roadmap. This guide walks through how we design, stage, and evaluate
curricula across training, evaluation, and deployment.

## Design principles

1. **Start from the target metric** — Anchor every phase on the milestone gate (for example M1 win rate ≥0.55).
2. **Minimise hidden state** — Curriculum YAML fragments must be diff-friendly; prefer declarative overrides to custom code.
3. **Embed observability** — Each phase should emit trace markers (`phase_id`, `prompt_complexity`) for downstream dashboards.
4. **Document fallback paths** — Capture baselines in [`../status_updates/`](../status_updates/) before experimenting.

## Curriculum blueprint

| Phase | Objective | Dataset preset | Signals |
| --- | --- | --- | --- |
| Warm-up | Stabilise reasoning traces | `datasets/reasoning/warmup.jsonl` | Trace coverage, loss | 
| First principles | Teach decomposition heuristics | `datasets/reasoning/first_principles.jsonl` | Win rate, critique density |
| Challenge set | Stress bespoke behaviors | `datasets/reasoning/challenge.jsonl` | Latency deltas, judge disagreement |

Phase definitions live in `configs/training/reasoning/curricula/`. Each YAML file exports:

```yaml
phase_schedule:
  - id: warmup
    dataset: datasets/reasoning/warmup.jsonl
    steps: 200
  - id: first_principles
    dataset: datasets/reasoning/first_principles.jsonl
    steps: 400
  - id: challenge
    dataset: datasets/reasoning/challenge.jsonl
    steps: 300
```text

## Training pipeline

1. **Select** a curriculum file (for example `curriculum=first_principles`).
2. **Launch** training with explicit overrides:
   ```bash
   codex-train +reasoning=baseline \
     curriculum=first_principles \
     logging.reasoning_trace=true \
     training.output_dir=artifacts/runs/first-principles
   ```
3. **Monitor** traces with `codex metrics summarize --metric reasoning.trace_coverage`.
4. **Record** qualitative notes (prompt outliers, judge disagreements) in `status_updates/first_principles.md`.

## Evaluation pipeline

1. Materialise evaluation packs:
   ```bash
   codex datasets materialize --preset reasoning/first_principles
   ```
2. Run evaluators with curriculum tags:
   ```bash
   codex evaluate --config configs/evaluation/reasoning.yaml \
     curriculum.id=first_principles \
     --log-metrics .codex/metrics/reasoning.ndjson
   ```
3. Compare against baselines via `codex metrics compare --metric reasoning.win_rate --reference baseline`.
4. Capture feedback loops in `status_updates/first_principles.md`.

## Deployment pipeline

1. Verify the bundle:
   ```bash
   codex deploy --config configs/deploy/reasoning_pod.yaml \
     --model artifacts/runs/first-principles:last \
     --dry-run
   ```
2. Shadow host until latency and judge deltas meet the milestone gate.
3. Register the model with curriculum metadata:
   ```bash
   codex register --bundle artifacts/runs/first-principles:last \
     --tag reasoning/m1/first-principles \
     --notes "Curriculum M1 rollout"
   ```
4. Update rollout docs under [`../deployment/`](../deployment/) with observed risks or mitigations.

## Troubleshooting

- **Trace gaps** — Re-run with `logging.reasoning_trace=true` and verify `.codex/reasoning_runs/` contains phase markers.
- **Evaluator regressions** — Use `codex evaluate --metrics-only` to isolate metric drift before replaying full judge sweeps.
- **Deployment parity** — If bespoke hosts diverge, capture diffs in `status_updates/` and raise an action item against the M2
  gate.

Curricula evolve with the roadmap. Submit updates alongside milestone retrospectives and link the diff in your status report.

[END CONTENT]
````

### >>> FILE: docs/deployment/reasoning_pod.md@0D_base_

````markdown
[BEGIN CONTENT]
# Reasoning Pod: Dry-Run Deployment Guide

This guide defines the **dry-run** flow for a reasoning pod. All steps are **local-first** and **offline-friendly**.

## Objectives
- Validate manifests and resource expectations without contacting hosted services.
- Produce artifacts (MD + JSON) suitable for PR review and promotion gates.

## Control Surface (Knobs)
- **Curriculum phases**: `configs/training/reasoning/curricula/*`
- **Trace capture mode**: `trace_capture.mode ∈ {weights, activations}` (see `configs/training/reasoning/baseline.yaml`)
- **Evaluation presets**: `configs/evaluation/reasoning/*`
- **Deployment preset**: `configs/deploy/reasoning_pod.yaml`

> Formalism (signal tracking): let **R** be reasoning-readiness and **A** be artifact completeness.
> We model readiness heuristic as: **R = α·E + β·T + γ·D**, where E=evaluation pass ratio, T=trace coverage, D=deployment dry-run parity.
> Choose α,β,γ per your milestone; ensure **R ≥ R_min** before promotion.

## Dry-Run Steps
1) **Repo Map (Reasoning)**
   ```bash
   codex repo-map --reasoning > docs/status_updates/repo_map_reasoning.txt
   ```

2) **Status Report (Artifacts)**
   ```bash
   python tools/status_report.py \
     --emit-md docs/status_updates/status_report.md \
     --emit-json docs/status_updates/status_report.json
   ```

3) **Compose Deployment (Dry-Run)**
   ```bash
   python tools/selection_report.py --config configs/deploy/reasoning_pod.yaml \
     --dry-run \
     --emit-md docs/status_updates/deploy_dry_run.md \
     --emit-json docs/status_updates/deploy_dry_run.json
   ```

4) **Link in PR**
   Include the above artifacts in your promotion PR.

## Promotion Checklist (excerpt)
- [ ] Status report (MD+JSON) attached.
- [ ] Dry-run deploy artifacts (MD+JSON) attached.
- [ ] Trace capture mode documented (`weights` or `activations`).
- [ ] Evaluation preset recorded (e.g., `configs/evaluation/reasoning/base.yaml`).

## Notes
- This flow intentionally avoids CI and remote deployment to remain offline-first.
- For actual hosting, adapt these manifests to your environment (k8s, container runtime, etc.), preserving the artifact trail.

[END CONTENT]
````

### >>> FILE: configs/deploy/reasoning_pod.yaml@0D_base_

````yaml
[BEGIN CONTENT]
# Offline-first dry-run config for a "reasoning pod".
# This file is used by local tools (e.g., selection_report.py) to validate
# inputs and render deployment expectations without calling external services.
kind: ReasoningPod
name: codex-reasoning-pod
version: 0
rollout_ring: 0D_base_  # Must match training metadata to pass dry-run validation.

image:
  repository: local/offline/codex
  tag: latest
  # NOTE: This is descriptive-only in dry-run mode. No pulls are executed.

resources:
  cpu: "2"
  memory: "8Gi"
  # Disk, GPU fields may be added later; keep this minimal and deterministic.

reasoning:
  trace_capture:
    mode: weights  # {weights, activations}; switch in baseline.yaml as desired
  evaluation_preset: configs/evaluation/reasoning/base.yaml
  curriculum_template: configs/training/reasoning/baseline.yaml

artifacts:
  emit_markdown: docs/status_updates/deploy_dry_run.md
  emit_json: docs/status_updates/deploy_dry_run.json

notes:
  - "This config is safe to commit; it does not perform deployment or network I/O."
  - "Use Python local tools to generate review artifacts for promotion gates."

[END CONTENT]
```text

## Survey Results

### >>> RESULT: Control surface knobs@0D_base_

```text
[BEGIN CONTENT]
- trace_mode: weights
- curriculum.preset: starter
- evaluation.preset: base
- deployment.preset: reasoning_pod
- metadata.rollout_ring: 0D_base_
[END CONTENT]
```text

### >>> RESULT: ReasoningTrainer search@0D_base_

```text
[BEGIN CONTENT]
ReasoningTrainer: NOT FOUND in code. References exist only in docs (e.g., docs/README_ROOT.md, docs/guides/reasoning_overview.md).
[END CONTENT]
```text

### >>> RESULT: Rollout ring context@0D_base_

```text
[BEGIN CONTENT]
--- docs/README.md ---
- **Deployment guardrails** — Cross-check bespoke model expectations against [`guides/serving_reproducibility.md`](./guides/serving_reproducibility.md).

## 📋 Operational templates
Operational templates encode recurring delivery rituals so teams can execute migrations, hardening passes, and planning
checkpoints with consistent safeguards. Begin with the [Operational Templates index](./templates/README.md) to review
prerequisites, required metadata, and cross-references before copying a template into your service.

### When to use a template
- You are planning a migration or hardening effort that will cross team boundaries.
- You need an auditable checklist with rollback, communications, and verification steps.
- You want a consistent structure for maintaining ≥85% coverage through scoped test additions.

### Quick links
- [Migration — Python File Relocation](./templates/Migration_PythonFileRelocation.md)
- [Migration — CLI Hardening](./templates/Migration_CLIHardening.md)
- [Planning — Intent Validation](./templates/Planning_IntentValidation.md)

### Handoff checklist
Each template includes role guidance (developers draft → maintainers execute), `[PLACEHOLDER: …]` prompts, and success
criteria aligned with the coverage standard. Ensure the following before requesting review:

- You are planning a migration or hardening effort that will cross team boundaries.
- You need an auditable checklist with rollback, communications, and verification steps.
- You want a consistent structure for maintaining ≥85% coverage through scoped test additions.

### Quick links
- [Migration — Python File Relocation](./templates/Migration_PythonFileRelocation.md)
- [Migration — CLI Hardening](./templates/Migration_CLIHardening.md)
- [Planning — Intent Validation](./templates/Planning_IntentValidation.md)

### Handoff checklist
Each template includes role guidance (developers draft → maintainers execute), `[PLACEHOLDER: …]` prompts, and success
criteria aligned with the coverage standard. Ensure the following before requesting review:

1. All placeholders are replaced with repo-specific context and linked artifacts.
2. Rollback and communication steps point to real runbooks or dashboards.
3. The template is stored alongside the service codebase (usually under `docs/`) and linked from the change description or PR.

See [`docs/CONTRIBUTING.md`](./CONTRIBUTING.md#using-operational-templates) for the full drafting workflow and role expectations.

## Conventions
- Keep docs small and composable.

`rollout_ring` is declarative intent, not permission.

Always keep `--dry-run` in place; manifests must be reviewed before any
apply/rollout tooling is engaged.

### Rollout rings

This repository uses staged rollout rings to represent maturity and review
state:

* `0A_base_` / `0B_base_`: active development, unstable knobs.
* `0C_base_`: integration of multiple features landing together.
* `0D_base_`: release candidate. Content here should be explainable
  to Engineering and Product.
* `main`: canonical internal "alpha product" surface after approval.

When you generate a deployment manifest (`configs/deploy/reasoning_pod.yaml`),
it includes a `rollout_ring` field. That field is a declaration of intent
("this artifact is targeting 0D_base_ next"), not permission to ship.

Nothing targeting `main` should be treated as eligible for hosting without:

Always keep `--dry-run` in place; manifests must be reviewed before any
apply/rollout tooling is engaged.

### Rollout rings

This repository uses staged rollout rings to represent maturity and review
state:

* `0A_base_` / `0B_base_`: active development, unstable knobs.
* `0C_base_`: integration of multiple features landing together.
* `0D_base_`: release candidate. Content here should be explainable
  to Engineering and Product.
* `main`: canonical internal "alpha product" surface after approval.

When you generate a deployment manifest (`configs/deploy/reasoning_pod.yaml`),
it includes a `rollout_ring` field. That field is a declaration of intent
("this artifact is targeting 0D_base_ next"), not permission to ship.

Nothing targeting `main` should be treated as eligible for hosting without:
1. offline evaluation gates passing,

Always keep `--dry-run` in place; manifests must be reviewed before any
apply/rollout tooling is engaged.

### Rollout rings

This repository uses staged rollout rings to represent maturity and review
state:

* `0A_base_` / `0B_base_`: active development, unstable knobs.
* `0C_base_`: integration of multiple features landing together.
* `0D_base_`: release candidate. Content here should be explainable
  to Engineering and Product.
* `main`: canonical internal "alpha product" surface after approval.

When you generate a deployment manifest (`configs/deploy/reasoning_pod.yaml`),
it includes a `rollout_ring` field. That field is a declaration of intent
("this artifact is targeting 0D_base_ next"), not permission to ship.

Nothing targeting `main` should be treated as eligible for hosting without:
1. offline evaluation gates passing,
2. trace/curriculum settings documented,

### Rollout rings

This repository uses staged rollout rings to represent maturity and review
state:

* `0A_base_` / `0B_base_`: active development, unstable knobs.
* `0C_base_`: integration of multiple features landing together.
* `0D_base_`: release candidate. Content here should be explainable
  to Engineering and Product.
* `main`: canonical internal "alpha product" surface after approval.

When you generate a deployment manifest (`configs/deploy/reasoning_pod.yaml`),
it includes a `rollout_ring` field. That field is a declaration of intent
("this artifact is targeting 0D_base_ next"), not permission to ship.

Nothing targeting `main` should be treated as eligible for hosting without:
1. offline evaluation gates passing,
2. trace/curriculum settings documented,
3. explicit signoff.

state:

* `0A_base_` / `0B_base_`: active development, unstable knobs.
* `0C_base_`: integration of multiple features landing together.
* `0D_base_`: release candidate. Content here should be explainable
  to Engineering and Product.
* `main`: canonical internal "alpha product" surface after approval.

When you generate a deployment manifest (`configs/deploy/reasoning_pod.yaml`),
it includes a `rollout_ring` field. That field is a declaration of intent
("this artifact is targeting 0D_base_ next"), not permission to ship.

Nothing targeting `main` should be treated as eligible for hosting without:
1. offline evaluation gates passing,
2. trace/curriculum settings documented,
3. explicit signoff.

## Related
- Project audit ritual: see `AUDIT_PROMPT.md`
- CHANGELOG practices follow “Keep a Changelog” with an **Unreleased** section at the top.

* `0A_base_` / `0B_base_`: active development, unstable knobs.
* `0C_base_`: integration of multiple features landing together.
* `0D_base_`: release candidate. Content here should be explainable
  to Engineering and Product.
* `main`: canonical internal "alpha product" surface after approval.

When you generate a deployment manifest (`configs/deploy/reasoning_pod.yaml`),
it includes a `rollout_ring` field. That field is a declaration of intent
("this artifact is targeting 0D_base_ next"), not permission to ship.

Nothing targeting `main` should be treated as eligible for hosting without:
1. offline evaluation gates passing,
2. trace/curriculum settings documented,
3. explicit signoff.

## Related
- Project audit ritual: see `AUDIT_PROMPT.md`
- CHANGELOG practices follow “Keep a Changelog” with an **Unreleased** section at the top.

---
Last updated: 2025-10-25

--- docs/README_ROOT.md ---
- `evaluation.preset`
- `deployment.preset`
- `metadata.rollout_ring`

Every smoke run of the training loop writes machine-readable artifacts under `runs/train_loop/`:

- `run_metadata.json` — captures `metadata.*`, the selected presets, and the rollout ring.
- `reasoning.json` — snapshot of the reasoning harness configuration plus runtime summary.
- `evaluation.json` — evaluation preset enforced for the run.

Promotion toward `main` requires:

1. The evaluation preset to pass (or carry explicit sign-off in status reports).
2. `metadata.rollout_ring` declared in the training config and matching the target pod ring.
3. `codex deploy --dry-run` to succeed, which enforces the ring match between training output and `configs/deploy/reasoning_pod.yaml`.

Reviewers preparing a `0D_base_` → `main` merge should walk the dedicated checklist in [`docs/ops/promotion_checklist.md`](ops/promotion_checklist.md).
It also requires attaching the outputs of:

- `codex_ml.cli.codex_cli status-report`
- `codex_ml.cli.codex_cli deploy --dry-run`

- `run_metadata.json` — captures `metadata.*`, the selected presets, and the rollout ring.
- `reasoning.json` — snapshot of the reasoning harness configuration plus runtime summary.
- `evaluation.json` — evaluation preset enforced for the run.

Promotion toward `main` requires:

1. The evaluation preset to pass (or carry explicit sign-off in status reports).
2. `metadata.rollout_ring` declared in the training config and matching the target pod ring.
3. `codex deploy --dry-run` to succeed, which enforces the ring match between training output and `configs/deploy/reasoning_pod.yaml`.

Reviewers preparing a `0D_base_` → `main` merge should walk the dedicated checklist in [`docs/ops/promotion_checklist.md`](ops/promotion_checklist.md).
It also requires attaching the outputs of:

- `codex_ml.cli.codex_cli status-report`
- `codex_ml.cli.codex_cli deploy --dry-run`
- and linking the latest `docs/status_updates/survey-<ring>-and-<PR>-<DATESTAMP>.md`

## Architecture at a glance

The canonical topology is captured in [`docs/diagrams/architecture.svg`](diagrams/architecture.svg). Pair it with the
Mermaid source (`architecture.mmd`) when proposing changes so reviewers can diff rendered assets and source together.

```bash
   codex register --bundle artifacts/runs/reasoning-baseline \
     --expect manifest.sha256 --tag reasoning/m0/bespoke
   ```

For service integrations, adopt the PodSpec defined in
[`docs/deployment/reasoning_pod.md`](deployment/reasoning_pod.md).
This PodSpec is a **dry-run template**, not production hosting.
Its job is to make resource shape, telemetry, curriculum phase,
trace capture mode, and rollout ring explicit before anything moves
toward `main`. A dry-run configuration is provided at
[`configs/deploy/reasoning_pod.yaml`](https://github.com/Aries-Serpent/_codex_/blob/main/configs/deploy/reasoning_pod.yaml).
Link the generated manifest to your rollout plan.

## Guided reasoning pipelines

Follow the deep dives in the new guides:

- [`docs/guides/reasoning_overview.md`](guides/reasoning_overview.md) — systems overview and milestone guardrails.
- [`docs/guides/first_principles_curricula.md`](guides/first_principles_curricula.md) — curriculum design and evaluation cadences.

--- docs/ops/promotion_checklist.md ---
# Promotion Checklist: `0D_base_` → `main`

This checklist is the approval gate to move staged reasoning work from the `0D_base_` ring toward `main`.
It aligns Product, Infra, and Model/Training without requiring network access or external CI.

## 1. Artifacts captured
Before requesting promotion, the branch owner MUST have run at least one local training/eval cycle
using the approved reasoning config (for example `configs/training/reasoning/baseline.yaml`)
and MUST have these files in the training output directory (default `runs/train_loop/`):

- `run_metadata.json`

# Promotion Checklist: `0D_base_` → `main`

This checklist is the approval gate to move staged reasoning work from the `0D_base_` ring toward `main`.
It aligns Product, Infra, and Model/Training without requiring network access or external CI.

## 1. Artifacts captured
Before requesting promotion, the branch owner MUST have run at least one local training/eval cycle
using the approved reasoning config (for example `configs/training/reasoning/baseline.yaml`)
and MUST have these files in the training output directory (default `runs/train_loop/`):

- `run_metadata.json`
- `reasoning.json` (if reasoning harness was active)
- `evaluation.json` (if evaluation harness was active)

3. We are explicitly in `--dry-run` mode (no live infra touch in this ring).

## 4. Status update document
There MUST be a survey/status file checked in under:

```text
docs/status_updates/survey-<ring>-and-<PR>-<DATESTAMP>.md
```text

For example:
`docs/status_updates/survey-0D_base_-and-1926-2025-10-29.md`

This file captures the reconciled view of:
- training orchestration code (TrainLoop, UnifiedTraining)
- reasoning harness state (`_vectorise_model` / trace capture)
- curricula and baseline knobs
- evaluation presets
- deployment story and ring semantics
- any doc/code mismatches discovered in that survey

## 5. Explicit sign-off on evaluation preset

- evaluation presets
- deployment story and ring semantics
- any doc/code mismatches discovered in that survey

## 5. Explicit sign-off on evaluation preset
The reviewer MUST confirm one of:
1. The evaluation preset in `run_metadata.json.knobs.evaluation_preset` has passed offline evaluation, OR
2. The PR description includes an explicit human sign-off noting why it is acceptable to proceed (for example,
   "We accept limited evaluation coverage because this branch only fixes docs and CLI surface; no model behavior changes").

## 6. Final check list for `main`
Promotion from `0D_base_` toward `main` may proceed ONLY if:

- rollout_ring is declared AND matches pod ring.
- `codex_ml.cli.codex_cli status-report` has been attached to the PR.
- `codex_ml.cli.codex_cli deploy --dry-run` succeeded.
- Latest `docs/status_updates/survey-...` exists and is linked in the PR.
- The evaluation preset is either passing offline or explicitly signed off.

When all of the above boxes are checked, merge to `main` is allowed.
If any box is unchecked, promotion is blocked.

- deployment story and ring semantics
- any doc/code mismatches discovered in that survey

## 5. Explicit sign-off on evaluation preset
The reviewer MUST confirm one of:
1. The evaluation preset in `run_metadata.json.knobs.evaluation_preset` has passed offline evaluation, OR
2. The PR description includes an explicit human sign-off noting why it is acceptable to proceed (for example,
   "We accept limited evaluation coverage because this branch only fixes docs and CLI surface; no model behavior changes").

## 6. Final check list for `main`
Promotion from `0D_base_` toward `main` may proceed ONLY if:

- rollout_ring is declared AND matches pod ring.
- `codex_ml.cli.codex_cli status-report` has been attached to the PR.
- `codex_ml.cli.codex_cli deploy --dry-run` succeeded.
- Latest `docs/status_updates/survey-...` exists and is linked in the PR.
- The evaluation preset is either passing offline or explicitly signed off.

When all of the above boxes are checked, merge to `main` is allowed.
If any box is unchecked, promotion is blocked.

## 6. Final check list for `main`
Promotion from `0D_base_` toward `main` may proceed ONLY if:

- rollout_ring is declared AND matches pod ring.
- `codex_ml.cli.codex_cli status-report` has been attached to the PR.
- `codex_ml.cli.codex_cli deploy --dry-run` succeeded.
- Latest `docs/status_updates/survey-...` exists and is linked in the PR.
- The evaluation preset is either passing offline or explicitly signed off.

When all of the above boxes are checked, merge to `main` is allowed.
If any box is unchecked, promotion is blocked.

---

## 7. Control surface / future UI contract
The future "control surface" (front-end knobs for Product / Infra) is expected to read
exactly the fields surfaced by:

```bash
python -m codex_ml.cli.codex_cli status-report \
[END CONTENT]
```text

### >>> RESULT: CLI mismatch audit@0D_base_

```text
[BEGIN CONTENT]
- Docs such as docs/README.md and docs/guides/reasoning_overview.md instruct `codex deploy --config ... --model ... --dry-run`.
- Actual CLI (`src/codex_ml/cli/codex_cli.py`) defines `deploy` with options `--config`, `--dry-run`, and `--run-metadata-dir` only (no `--model`).
- `repo-map --reasoning` is implemented in both Typer (`src/codex_cli/app.py`) and Click (`src/codex_ml/cli/codex_cli.py`) variants and matches docs, including optional `--include` filtering in the Typer path.
[END CONTENT]
```text

### >>> RESULT: PR #1926 diff availability@PR#1926

```text
[BEGIN CONTENT]
No local diff artifacts for PR #1926 were found in the repository; survey limited to current branch contents.
[END CONTENT]
```text