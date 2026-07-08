"""
Train Loop Module

This module provides functionality for train loop.

Usage:
    from codex_ml.train_loop import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

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
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass, is_dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional
from uuid import uuid4

__version__ = "0.1.0"


from codex_ml.codex_structured_logging import get_session_id, get_session_logger
from codex_ml.config import (
    ConfigError,
    ReasoningConfig,
)
from codex_ml.logging.ndjson_logger import is_legacy_mode

# ---------------------------------------------------------------------------
# Training failure alerting — imported lazily at call site to keep the
# import cheap and to avoid hard failures if the package is unavailable.
# ---------------------------------------------------------------------------
try:
    from codex.alerting import TrainingAlertManager as _TrainingAlertManager

    _ALERTING_AVAILABLE = True
except (ImportError, AttributeError):  # pragma: no cover — optional dependency
    _ALERTING_AVAILABLE = False
    _TrainingAlertManager = None

if TYPE_CHECKING:
    from codex_ml.models.reasoning import ReasoningHarness

try:
    from codex_ml.models.reasoning import attach_reasoning_adapters

    _HAS_REASONING_ADAPTERS = True
except (ImportError, AttributeError):
    attach_reasoning_adapters = None
    _HAS_REASONING_ADAPTERS = False
from codex_ml.monitoring import CodexMetricsRegistry, metrics_enabled
from codex_ml.monitoring.data_drift import DataDriftDetector as _DataDriftDetector
from codex_ml.training.dp_config import DifferentialPrivacyConfig, make_private_model
from codex_ml.utils.checkpoint import load_checkpoint, save_checkpoint
from codex_ml.utils.checksum import sha256sum

try:
    from codex_ml.utils.repro import record_dataset_checksums
except (ImportError, AttributeError):

    def record_dataset_checksums(*_, **__) -> dict[str, Any]:
        return {}


try:
    from codex_ml.utils.seeding import set_reproducible
except (ImportError, AttributeError):

    def set_reproducible(*_, **__) -> None:
        return None


try:
    from codex_ml.telemetry import start_metrics_server
except (ImportError, AttributeError):

    def start_metrics_server(*_, **__) -> None:
        return None


try:
    import mlflow

    _HAS_MLFLOW = True
except (IOError, OSError):
    mlflow = None
    _HAS_MLFLOW = False

logger = logging.getLogger(__name__)
ART_DIR = Path("artifacts")
_TELEMETRY_JSON_ENABLED = True

try:
    import torch

    StepLR = torch.optim.lr_scheduler.StepLR
    optim = torch.optim
    DataLoader = torch.utils.data.DataLoader
    Dataset = torch.utils.data.Dataset
    # Verify torch is functional
    _ = torch.Tensor
    _HAS_TORCH = True
except Exception:
    torch = None  # type: ignore[assignment]
    optim = None
    StepLR = None
    DataLoader = None
    Dataset = object
    _HAS_TORCH = False

try:
    from codex_ml.models.registry import get_model as instantiate_model
except (ImportError, AttributeError):
    instantiate_model = None

try:
    from codex_ml.lora import apply_lora
except (ImportError, AttributeError):
    apply_lora = None

try:
    from codex_ml.callbacks import (
        Callback,
        EvaluationCallback,
        LoggingCallback,
        merge_callback_results,
    )
except Exception:
    # fmt: off
    class Callback:  # type: ignore
        def on_train_start(self, state: dict[str, Any]) -> None:
            pass

        def on_epoch_start(self, epoch: int, state: dict[str, Any]) -> None:
            pass

        def on_epoch_end(
            self,
            epoch: int,
            metrics: dict[str, Any],
            state: dict[str, Any],
        ) -> None:
            pass

        def on_train_end(self, state: dict[str, Any]) -> None:
            pass
    # fmt: on

    def merge_callback_results(
        base: dict[str, Any], addon: dict[str, Any] | None
    ) -> dict[str, Any]:
        if addon:
            base.update(addon)
        return base

    EvaluationCallback = Callback
    LoggingCallback = Callback

try:
    from codex_ml.utils.determinism import set_cudnn_deterministic
except (ImportError, AttributeError):

    def set_cudnn_deterministic(enable: bool, benchmark: bool = False) -> None:
        _ = (enable, benchmark)
        return


try:
    from codex_ml.utils.retention import prune_checkpoints
except (ImportError, AttributeError):

    def prune_checkpoints(*args, **kwargs) -> dict[str, Any]:
        return {"dry_run": True}


if _HAS_TORCH:

    class ToyDataset(Dataset):  # type: ignore[valid-type,misc]
        def __init__(
            self,
            *,
            num_samples: int,
            seq_len: int,
            vocab_size: int,
            seed: int,
        ) -> None:
            generator = torch.Generator()
            generator.manual_seed(int(seed))
            self._data = torch.randint(
                0,
                int(vocab_size),
                (int(num_samples), int(seq_len)),
                dtype=torch.long,
                generator=generator,
            )

        def __len__(self) -> int:  # pragma: no cover - simple container
            return self._data.size(0)

        def __getitem__(self, index: int):  # pragma: no cover - exercised indirectly
            return self._data[index]

else:

    class ToyDataset:  # type: ignore[no-redef]
        def __len__(self) -> int:  # pragma: no cover - defensive
            return 0

        def __getitem__(self, index: int):  # pragma: no cover - defensive
            raise IndexError("Torch is required to construct ToyDataset")


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
        except (
            ImportError,
            AttributeError,
        ) as exc:  # pragma: no cover - defensive attachment guard
            logger.warning(
                "Failed to bind reasoning modules to model: %s", exc
            )  # codeql[py/clear-text-logging-sensitive-data]

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
        except (
            ValueError,
            TypeError,
            RuntimeError,
        ) as exc:  # pragma: no cover - defensive capture guard
            logger.debug(
                "Skipping reasoning trace capture: %s", exc
            )  # codeql[py/clear-text-logging-sensitive-data]
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
        }
        payload.update(trace)
        _append_metrics_event(art_dir_path, payload)
        if self.store_path is not None:
            _persist_reasoning_trace(self.store_path, payload)
        try:
            self.harness.record(payload)
        except (IOError, OSError):  # pragma: no cover - history append best effort
            logger.debug(
                "Suppressed exception in handler", exc_info=True
            )  # codeql[py/clear-text-logging-sensitive-data]
        self.traces_written += 1


def _coerce_reasoning_config(payload: Any) -> ReasoningConfig | None:
    if payload is None:
        return None
    if isinstance(payload, ReasoningConfig):
        payload.validate("training.reasoning")
        return payload
    if isinstance(payload, Mapping):
        cfg = ReasoningConfig.from_mapping(payload)
        cfg.validate("training.reasoning")
        return cfg
    if isinstance(payload, bool):
        if not payload:
            return ReasoningConfig(enabled=False)
        cfg = ReasoningConfig()
        cfg.validate("training.reasoning")
        return cfg
    raise ConfigError(
        "training.reasoning",
        "Reasoning configuration must be a mapping or boolean when provided",
        payload,
    )


def _initialize_reasoning_runtime(
    model: Any,
    raw_cfg: Any,
    art_dir_path: Path | None,
) -> tuple[Any, ReasoningRuntime | None]:
    if raw_cfg and not _HAS_TORCH:
        raise ImportError(
            "Reasoning adapters require torch; install the dependency before enabling training.reasoning"  # noqa: E501
        )
    if raw_cfg and not _HAS_REASONING_ADAPTERS:
        raise ImportError(
            "Reasoning adapters are unavailable; install optional reasoning dependencies before enabling training.reasoning",  # noqa: E501
        )
    try:
        reasoning_cfg = _coerce_reasoning_config(raw_cfg)
    except ConfigError as exc:
        type(exc).__name__
        logger.debug("ConfigError: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        logger.warning(
            "Invalid reasoning configuration: %s", exc
        )  # codeql[py/clear-text-logging-sensitive-data]
        return model, None
    if reasoning_cfg is None or not reasoning_cfg.enabled:
        return model, None
    try:
        harness = attach_reasoning_adapters(model, reasoning_cfg)
    except (IOError, OSError) as exc:  # pragma: no cover - adapter construction best effort
        logger.warning(
            "Failed to attach reasoning adapters: %s", exc
        )  # codeql[py/clear-text-logging-sensitive-data]
        return model, None
    store_path = None
    if art_dir_path is not None:
        trace_name = reasoning_cfg.objective.trace_store or "reasoning_traces.ndjson"
        store_path = Path(art_dir_path) / trace_name
    runtime = ReasoningRuntime(
        config=reasoning_cfg,
        harness=harness,
        store_path=store_path,
        per_epoch_limit=int(reasoning_cfg.objective.max_traces_per_epoch),
        top_k=int(reasoning_cfg.objective.log_top_k),
        threshold=reasoning_cfg.log_probability_threshold,
    )
    runtime.bind_model(model)
    return model, runtime


_DEFAULT_SEED = 1234


def _normalise_snapshot(value: Any) -> Any:
    if is_dataclass(value):
        return _normalise_snapshot(asdict(value))  # type: ignore[arg-type]
    if isinstance(value, Mapping):
        return {str(key): _normalise_snapshot(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_normalise_snapshot(item) for item in value]
    return value


def _snapshot_payload(payload: Any) -> dict[str, Any] | None:
    if payload is None:
        return None
    normalised = _normalise_snapshot(payload)
    if isinstance(normalised, Mapping):
        return dict(normalised)
    return None


def _apply_metadata_to_state(
    state: dict[str, Any], metadata: Mapping[str, Any] | None
) -> dict[str, Any]:
    metadata_dict = dict(metadata) if metadata is not None else {}
    state["metadata"] = metadata_dict
    if "rollout_ring" not in metadata_dict:
        logger.warning(
            "rollout_ring not declared; reasoning promotion may be blocked."
        )  # codeql[py/clear-text-logging-sensitive-data]
    return metadata_dict


def _write_json_report(output_dir: Path | None, name: str, payload: Mapping[str, Any]) -> None:
    if output_dir is None or not payload:
        return
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / name).write_text(
            json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
        )
    except (IOError, OSError) as exc:
        logger.warning(
            "Failed to write %s: %s", name, exc
        )  # codeql[py/clear-text-logging-sensitive-data]


def _render_reasoning_report(output_dir: Path | None, state: Mapping[str, Any]) -> None:
    payload = state.get("reasoning") if isinstance(state, Mapping) else None
    if isinstance(payload, Mapping) and payload:
        _write_json_report(output_dir, "reasoning.json", payload)


def _render_evaluation_report(output_dir: Path | None, state: Mapping[str, Any]) -> None:
    payload = state.get("evaluation") if isinstance(state, Mapping) else None
    if isinstance(payload, Mapping) and payload:
        _write_json_report(output_dir, "evaluation.json", payload)


def _set_seed(seed: Optional[int]) -> int:
    if seed in (None, 0):
        seed = _DEFAULT_SEED
    resolved_seed = int(seed)  # type: ignore[arg-type]
    random.seed(resolved_seed)
    try:
        import numpy as np

        np.random.seed(resolved_seed)
    except (ImportError, AttributeError):
        logger.debug(
            "Suppressed exception in handler", exc_info=True
        )  # codeql[py/clear-text-logging-sensitive-data]
    if _HAS_TORCH:
        torch.manual_seed(resolved_seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(resolved_seed)
    return resolved_seed


def _now_ts() -> str:
    """Generate ISO 8601 timestamp with 'Z' suffix.

    Returns:
        Timestamp string like "2026-02-01T12:34:56.789Z"
    """
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


_LEGACY_NDJSON = is_legacy_mode()
_TRAIN_RUN_ID = os.environ.get("CODEX_RUN_ID") or uuid4().hex


def _coerce_telemetry_event(record: dict[str, Any]) -> dict[str, Any]:
    """Ensure a telemetry record has required keys: type, event, timestamp.

    Any missing keys are populated with defaults; additional keys are preserved.
    """
    out = dict(record)
    out.setdefault("type", "telemetry")
    out.setdefault("event", "unknown")
    out.setdefault("timestamp", _now_ts())
    return out


def demo_epoch(epoch: int, *, grad_accum: int = 1) -> dict[str, Any]:
    """Return deterministic demo metrics for documentation and tests."""

    return {
        "epoch": int(epoch),
        "grad_accum": int(grad_accum),
        "timestamp": _now_ts(),
    }


def record_metrics(
    prefix: str | None = None,
    epoch: int | None = None,
    metrics: dict[str, Any] | None = None,
    config_id: str | None = None,
    **kwargs: Any,
) -> Path:
    """Persist metrics in both JSON and NDJSON formats with backwards compatibility."""

    phase_alias = kwargs.pop("phase", None)
    cfg_alias = kwargs.pop("cfg_hash", None)
    notes = kwargs.pop("notes", None)
    if kwargs:
        unexpected = ", ".join(sorted(kwargs))
        raise TypeError(f"record_metrics() got unexpected keyword arguments: {unexpected}")

    resolved_prefix = prefix if prefix is not None else phase_alias
    if resolved_prefix is None:
        raise TypeError("record_metrics() missing required argument 'prefix'/'phase'")
    if epoch is None:
        raise TypeError("record_metrics() missing required argument 'epoch'")
    if metrics is None:
        raise TypeError("record_metrics() missing required argument 'metrics'")
    resolved_cfg = config_id if config_id is not None else cfg_alias
    if resolved_cfg is None:
        raise TypeError("record_metrics() missing required argument 'config_id'/'cfg_hash'")

    ART_DIR.mkdir(parents=True, exist_ok=True)

    payload: dict[str, Any] = {
        "phase": resolved_prefix,
        "prefix": resolved_prefix,
        "epoch": int(epoch),
        "cfg_hash": resolved_cfg,
        "config_id": resolved_cfg,
        "metrics": dict(metrics),
        "timestamp": _now_ts(),
    }
    if not _LEGACY_NDJSON:
        payload["run_id"] = _TRAIN_RUN_ID
    if notes is not None:
        payload["notes"] = notes

    serialized = json.dumps(payload, sort_keys=True)

    ndjson_path = ART_DIR / "metrics.ndjson"
    with ndjson_path.open("a", encoding="utf-8") as handle:
        handle.write(serialized + "\n")

    json_path = ART_DIR / "metrics.json"
    history: list[dict[str, Any]] = []
    if json_path.exists():
        try:
            loaded = json.loads(json_path.read_text(encoding="utf-8"))
            if isinstance(loaded, list):
                history = loaded
        except (IOError, OSError):
            history = []
    history.append(payload)
    json_path.write_text(json.dumps(history, indent=2, sort_keys=True), encoding="utf-8")

    return ndjson_path


def _resolve_dtype(dtype: Optional[str]):
    if not _HAS_TORCH or dtype is None:
        return None
    mapping = {
        "fp32": torch.float32,
        "float32": torch.float32,
        "f32": torch.float32,
        "bf16": getattr(torch, "bfloat16", None),
        "bfloat16": getattr(torch, "bfloat16", None),
        "fp16": torch.float16,
        "float16": torch.float16,
        "f16": torch.float16,
    }
    return mapping.get(dtype.lower())


def _resolve_device(device: Optional[str]):
    if not _HAS_TORCH:
        return device or "cpu"
    if device is None:
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    try:
        return torch.device(device)
    except (TypeError, ValueError, RuntimeError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        logger.warning(
            "Invalid device '%s': %s. Falling back to CPU.", device, exc
        )  # codeql[py/clear-text-logging-sensitive-data]
        return torch.device("cpu")


def _load_or_create_model(
    model: Any | None, model_name: str | None, model_kwargs: dict[str, Any]
) -> tuple[Any, bool]:
    if model is not None:
        return model, False
    if instantiate_model is None:
        logger.warning(
            "Model registry is not available; proceeding without instantiating '%s'",
            model_name or "model",
        )
        return None, False
    if not model_name:
        # If no model_name but instantiate_model exists, return None (allow tests without models)
        logger.warning(
            "No model or model_name provided; proceeding without model"
        )  # codeql[py/clear-text-logging-sensitive-data]
        return None, False
    created = instantiate_model(model_name, model_kwargs)
    return created, True


def _assert_bf16_capability(
    requested_dtype: str | None,
    dtype_obj: Any,
    require: bool,
    device: Any | None = None,
) -> None:
    """If ``require`` is True and bf16 is requested, ensure runtime supports it.

    The check is intentionally lightweight and only verifies that torch exposes
    ``bfloat16`` and can construct a tensor of that dtype. If torch is missing
    or bf16 is not available, raise ``RuntimeError`` early to fail fast.
    """
    if not require:
        return
    want_bf16 = False
    try:
        import torch as _torch
    except (ConnectionError, TimeoutError) as exc:  # pragma: no cover - environment dependent
        if requested_dtype and str(requested_dtype).lower() in {"bf16", "bfloat16"}:
            raise RuntimeError("bf16 required but PyTorch is not installed") from exc
        return

    bf16 = getattr(_torch, "bfloat16", None)
    if requested_dtype and str(requested_dtype).lower() in {"bf16", "bfloat16"}:
        want_bf16 = True
    if dtype_obj is not None and bf16 is not None and dtype_obj == bf16:
        want_bf16 = True
    if not want_bf16:
        return
    if bf16 is None:
        raise RuntimeError("bf16 required but torch.bfloat16 is unavailable in this build")
    try:
        # Construct tiny tensors and attempt a matmul to catch device/arch issues.
        a = _torch.ones((2, 2), dtype=bf16)
        b = _torch.ones((2, 2), dtype=bf16)
        if device is not None:
            try:
                a = a.to(device)
                b = b.to(device)
            except (ValueError, TypeError, RuntimeError):
                # If placement fails, let the matmul attempt occur on default device.
                logger.debug(
                    "Suppressed exception in handler", exc_info=True
                )  # codeql[py/clear-text-logging-sensitive-data]
        _ = a @ b
    except (IOError, OSError) as exc:  # pragma: no cover - runtime check
        raise RuntimeError("bf16 required but runtime cannot construct bfloat16 tensors") from exc


def _attempt_resume(model, optimizer, scheduler, checkpoint_dir: str | Path):
    resume_meta: dict[str, Any] = {}
    if not checkpoint_dir:
        return 1, resume_meta
    ckpt_dir = Path(checkpoint_dir)
    latest_file = ckpt_dir / "latest.json"
    if not latest_file.exists():
        return 1, resume_meta
    try:
        data = json.loads(latest_file.read_text())
        last_epoch = int(data.get("epoch", 0))
        if last_epoch < 1:
            return 1, resume_meta
        path_hint = data.get("path")
        ckpt_path = ckpt_dir / path_hint if path_hint else ckpt_dir
        if ckpt_path.is_file():
            model_file = ckpt_path
            ckpt_base = ckpt_path.parent
        else:
            ckpt_base = ckpt_path
            model_file = ckpt_base / "model.pt"

        resume_meta["resumed_from_epoch"] = last_epoch
        resume_meta["latest_checkpoint_path"] = str(ckpt_base)

        if model is None:
            resume_meta["model_state_loaded"] = False
            resume_meta["resume_warning"] = "No model instance available"
            return 1, resume_meta

        if not model_file.exists():
            resume_meta["model_state_loaded"] = False
            resume_meta["missing_checkpoint"] = str(model_file)
            return 1, resume_meta

        try:
            load_checkpoint(
                model=model,
                optimizer=optimizer,
                scheduler=scheduler,
                ckpt_dir=ckpt_base,
            )
            resume_meta["model_state_loaded"] = True
            resume_meta["optimizer_state_loaded"] = optimizer is not None
            resume_meta["scheduler_state_loaded"] = scheduler is not None
            # propagate sha256 if present
            sha = data.get("checkpoint_sha256")
            if sha:
                resume_meta["previous_checkpoint_sha256"] = sha
            return last_epoch + 1, resume_meta
        except (ValueError, TypeError) as e:
            resume_meta["model_state_loaded"] = False
            resume_meta["optimizer_state_loaded"] = False
            resume_meta["scheduler_state_loaded"] = False
            resume_meta["model_state_error"] = str(e)
            return 1, resume_meta
    except (ValueError, TypeError) as e:
        resume_meta["resume_error"] = f"latest.json parse failure: {e}"
        return 1, resume_meta


def _select_parameters_for_optimization(model) -> list[Any]:
    if model is None:
        return []
    return [p for p in model.parameters() if p.requires_grad]


def _synthetic_step(model) -> float:
    if model is None:
        return 0.0
    first_param = None
    for p in model.parameters():
        if p.requires_grad and p.ndim > 0:
            first_param = p
            break
    if first_param is None:
        return 0.0
    loss_tensor = (first_param.float() ** 2).mean()
    loss_tensor.backward()
    return float(loss_tensor.detach().cpu().item())


def _first_param_dtype(model) -> str | None:
    """Return string name of the first parameter dtype, if available."""
    if not _HAS_TORCH or model is None:
        return None
    try:
        for p in model.parameters():
            if p.requires_grad:
                return str(p.dtype)
    except (ConnectionError, TimeoutError):  # pragma: no cover - defensive
        return None
    return None


def _log_dtype_mismatch_if_any(requested: Any, model) -> None:
    """Log a clear message if requested dtype differs from effective param dtype."""
    if requested is None or model is None:
        return
    eff = _first_param_dtype(model)
    req = str(requested)
    if eff is not None and eff != req:
        logger.warning(
            "Model parameter dtype differs from requested dtype: requested=%s effective=%s",
            req,
            eff,
        )


def _dataset_dtype_gate(dataset, desired: Any) -> None:
    """Inspect dataset tensor dtype and log casting notes.

    Our ToyDataset yields integer token IDs (long). When a floating dtype is
    requested for the model (e.g., bf16/fp32), casting typically occurs in the
    model. This gate logs the observed dataset dtype and the requested model dtype
    so operators are aware of potential casts.
    """
    if dataset is None or not _HAS_TORCH:
        return
    try:
        sample = dataset[0]
        ds_dtype = getattr(sample, "dtype", None)
    except (ConnectionError, TimeoutError):
        ds_dtype = None
    if ds_dtype is not None and desired is not None:
        logger.info(
            "Dataset dtype=%s; model requested dtype=%s (casting may occur during forward)",
            str(ds_dtype),
            str(desired),
        )


def _append_metrics_event(art_dir_path: Path | None, record: dict[str, Any]) -> None:
    """Append a single JSON line to artifacts/metrics.ndjson (best-effort)."""
    try:
        base = Path(art_dir_path) if art_dir_path is not None else ART_DIR
        base.mkdir(parents=True, exist_ok=True)
        # Normalize record to telemetry schema
        record = _coerce_telemetry_event(record)
        ndjson_path = base / "metrics.ndjson"
        with ndjson_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True) + "\n")
        # Dedicated telemetry sinks (subject to sampling to reduce volume)
        if _telemetry_should_sample(record):
            _append_telemetry_ndjson(base, record)
            _append_telemetry_json_rollover(base, record)
    except (IOError, OSError) as exc:
        logger.debug(
            "Failed to append telemetry event: %s", exc
        )  # codeql[py/clear-text-logging-sensitive-data]


def _persist_reasoning_trace(path: Path, payload: dict[str, Any]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, sort_keys=True) + "\n")
    except (IOError, OSError) as exc:
        logger.debug(
            "Failed to persist reasoning trace: %s", exc
        )  # codeql[py/clear-text-logging-sensitive-data]


def _telemetry_max_items() -> int:
    try:
        raw = os.environ.get("CODEX_TELEMETRY_MAX_ITEMS", "1000").strip()
        n = int(raw)
        return n if n > 0 else 1000
    except (IOError, OSError):
        return 1000


def _append_telemetry_json_rollover(base_dir: Path, record: dict[str, Any]) -> None:
    """Append record to artifacts/telemetry.json with simple rollover (best-effort)."""
    try:
        if not _telemetry_json_enabled():
            return
        path = base_dir / "telemetry.json"
        history: list[dict[str, Any]] = []
        if path.exists():
            try:
                loaded = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(loaded, list):
                    history = list(loaded)
            except (IOError, OSError):
                history = []
        roll = len(history) >= _telemetry_max_items()
        max_bytes = _telemetry_max_bytes()
        if not roll and max_bytes > 0 and path.exists():
            try:
                roll = path.stat().st_size >= max_bytes
            except (IOError, OSError):
                roll = False
        if roll:
            ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
            try:
                path.rename(base_dir / f"telemetry-{ts}.json")
            except (IOError, OSError):
                history = []
            else:
                history = []
        history.append(dict(record))
        path.write_text(json.dumps(history, indent=2, sort_keys=True), encoding="utf-8")
    except (IOError, OSError) as exc:
        logger.debug(
            "Failed to append telemetry.json: %s", exc
        )  # codeql[py/clear-text-logging-sensitive-data]


def _telemetry_json_enabled() -> bool:
    if not _TELEMETRY_JSON_ENABLED:
        return False
    raw = os.environ.get("CODEX_TELEMETRY_JSON_DISABLE") or os.environ.get(
        "CODEX_TELEMETRY_JSON_DISABLED"
    )
    if raw is None:
        return True
    val = str(raw).strip().lower()
    return val not in {"1", "true", "yes", "y"}


def _telemetry_ndjson_enabled() -> bool:
    raw = os.environ.get("CODEX_TELEMETRY_NDJSON_DISABLE")
    if raw is None:
        return True
    val = str(raw).strip().lower()
    return val not in {"1", "true", "yes", "y"}


def _telemetry_max_bytes() -> int:
    try:
        raw = os.environ.get("CODEX_TELEMETRY_MAX_BYTES", "0").strip()
        n = int(raw)
        return n if n > 0 else 0
    except (IOError, OSError):
        return 0


def _append_telemetry_ndjson(base_dir: Path, record: dict[str, Any]) -> None:
    """Append record to artifacts/telemetry.ndjson (best-effort)."""
    if not _telemetry_ndjson_enabled():
        return
    try:
        path = base_dir / "telemetry.ndjson"
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True) + "\n")
    except (IOError, OSError) as e:
        logger.debug(
            "Telemetry write failed (best-effort): %s", e
        )  # codeql[py/clear-text-logging-sensitive-data]


def _telemetry_sample_rate() -> float:
    try:
        raw = os.environ.get("CODEX_TELEMETRY_SAMPLE_RATE", "1.0").strip()
        rate = float(raw)
        if rate <= 0:
            return 0.0
        if rate >= 1:
            return 1.0
        return rate
    except Exception:
        return 1.0


def _telemetry_should_sample(record: dict[str, Any]) -> bool:
    # Lightweight random sampling based on sample_rate; could be extended per-event.
    try:
        rate = _telemetry_sample_rate()
        if rate >= 1.0:
            return True
        if rate <= 0.0:
            return False
        import random as _random

        return _random.random() < rate  # nosec B311 — non-cryptographic ML sampling/shuffling
    except (ImportError, AttributeError):
        return True


def _cast_batch_for_policy(
    sample: Any,
    policy: str | None,
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
    event_payload: dict[str, Any] = {
        "type": "telemetry",
        "event": "dataset_cast",
        "policy": policy_norm,
    }
    status = "skipped"
    reason: Optional[str] = None
    try:
        import torch as _torch
    except (IOError, OSError):
        reason = "torch_unavailable"
        event_payload["status"] = status
        event_payload["reason"] = reason
        _append_metrics_event(art_dir_path, event_payload)
        return sample
    try:
        src_dtype = getattr(sample, "dtype", None)
    except (IOError, OSError):
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
    except (IOError, OSError) as exc:
        logger.warning(
            "Dataset cast policy '%s' failed: %s", policy_norm, exc
        )  # codeql[py/clear-text-logging-sensitive-data]
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

    def _collate(batch) -> Any:
        if policy is None:
            return batch
        try:
            return [_cast_batch_for_policy(x, policy, desired, device, art_dir_path) for x in batch]
        except (IOError, OSError):
            return batch

    return _collate


def _init_scheduler(scheduler_cfg: Optional[dict[str, Any]], optimizer, total_epochs: int):
    if not scheduler_cfg or optimizer is None or not _HAS_TORCH:
        return None
    sched_type = scheduler_cfg.get("type")
    if not sched_type:
        return None
    base_lrs = [g["lr"] for g in optimizer.param_groups]

    if sched_type == "linear":
        final_lr_scale = float(scheduler_cfg.get("final_lr_scale", 0.0))

        class _LinearEpochScheduler:
            def __init__(self, opt, total_epochs, final_scale, base_lrs) -> None:
                self.opt = opt
                self.total_epochs = max(total_epochs, 1)
                self.final_scale = final_scale
                self.base_lrs = base_lrs
                self.last_epoch = 0

            def get_lr(self) -> list[float]:
                progress = min(self.last_epoch / self.total_epochs, 1.0)
                scale = (1 - progress) + progress * self.final_scale
                return [lr * scale for lr in self.base_lrs]

            def step(self) -> None:
                self.last_epoch += 1
                new_lrs = self.get_lr()
                for g, lr in zip(self.opt.param_groups, new_lrs, strict=False):
                    g["lr"] = lr

            def state_dict(self) -> dict[str, Any]:
                return {
                    "last_epoch": self.last_epoch,
                    "total_epochs": self.total_epochs,
                    "final_lr_scale": self.final_scale,
                    "base_lrs": self.base_lrs,
                    "type": "linear",
                }

            def load_state_dict(self, state) -> None:
                self.last_epoch = state.get("last_epoch", 0)

        return _LinearEpochScheduler(optimizer, total_epochs, final_lr_scale, base_lrs)

    if sched_type == "step":
        if StepLR is None:
            return None
        step_size = int(scheduler_cfg.get("step_size", 1))
        gamma = float(scheduler_cfg.get("gamma", 0.9))
        return StepLR(optimizer, step_size=step_size, gamma=gamma)

    logger.warning(
        "Unknown scheduler type '%s' - ignoring.", sched_type
    )  # codeql[py/clear-text-logging-sensitive-data]
    return None


def _scheduler_current_lr(scheduler, optimizer) -> list[float] | None:
    if scheduler is None or optimizer is None:
        return None
    try:
        return [pg["lr"] for pg in optimizer.param_groups]
    except (IOError, OSError):
        return None


def _checkpoint_digest(ckpt_dir: Path) -> str | None:
    sha_file = ckpt_dir / "checkpoint.sha256"
    if sha_file.exists():
        try:
            return sha_file.read_text(encoding="utf-8").strip() or None
        except (IOError, OSError):
            return None
    model_file = ckpt_dir / "model.pt"
    if model_file.exists():
        try:
            return sha256sum(model_file)
        except (IOError, OSError):
            return None
    return None


def _json_ready(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {k: _json_ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_ready(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    return value


@dataclass
class TrainingMetrics:
    epoch: int
    synthetic_loss: float | None = None
    optimizer_steps: int = 0
    total_steps: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_training(
    epochs: int = 1,
    grad_accum: int = 1,
    seed: int | None = None,
    art_dir: str | Path | None = None,
    model: Optional[Any] = None,
    model_name: str | None = None,
    model_cfg: Optional[dict[str, Any]] = None,
    lora: bool = False,
    lora_cfg: dict[str, Any] | None = None,
    device: str | None = None,
    dtype: str | None = None,
    amp: bool = False,
    amp_dtype: str | None = None,
    learning_rate: float = 1e-3,
    batch_size: int | None = None,
    checkpoint_dir: str | None = None,
    resume: bool = False,
    steps_per_epoch: int = 4,
    return_state: bool = False,
    scheduler_cfg: dict[str, Any] | None = None,
    dp_config: DifferentialPrivacyConfig | dict[str, Any] | None = None,
    dataset_sources: Optional[list[str | Path]] = None,
    dataset_cache_dir: Optional[str | Path] = None,
    callbacks: Optional[list[Callback]] = None,
    eval_fn: Optional[Callable[[int, dict[str, Any]], dict[str, Any]]] = None,
    mlflow_enable: bool = False,
    mlflow_uri: str | None = None,
    mlflow_experiment: str | None = None,
    telemetry_enable: bool = False,
    telemetry_port: int | None = None,
    # NEW:
    deterministic_cudnn: bool = False,
    run_config: Optional[dict[str, Any]] = None,
    retention_policy: Optional[dict[str, Any]] = None,
    bf16_require_capability: bool = False,
    dataset_cast_policy: str | None = None,
    reasoning: Mapping[str, Any] | ReasoningConfig | None = None,
    metadata: Mapping[str, Any] | None = None,
    evaluation: Mapping[str, Any] | None = None,
    **extra_kwargs: Any,
) -> dict[str, Any]:
    """
    Training loop (extended):
      - CUDNN determinism (opt-in)
      - checkpoint sha256
      - config snapshot
      - retention policy
    """
    t_start = time.time()
    _ = dataset_cache_dir
    if extra_kwargs:
        logger.debug(
            "Ignoring unused training kwargs: %s", sorted(extra_kwargs)
        )  # codeql[py/clear-text-logging-sensitive-data]
    resolved_seed = _set_seed(seed)
    try:
        set_reproducible(resolved_seed, deterministic=bool(deterministic_cudnn))
    except (ValueError, TypeError, RuntimeError):
        logger.debug(
            "Suppressed exception in handler", exc_info=True
        )  # codeql[py/clear-text-logging-sensitive-data]
    if deterministic_cudnn:
        set_cudnn_deterministic(True, benchmark=False)

    if grad_accum < 1:
        grad_accum = 1
    if steps_per_epoch < 1:
        steps_per_epoch = 1

    reasoning_runtime: ReasoningRuntime | None = None
    default_art_dir = Path(art_dir) if art_dir is not None else Path("runs/train_loop")
    art_dir_path: Path | None = default_art_dir
    try:
        art_dir_path.mkdir(parents=True, exist_ok=True)  # type: ignore[union-attr]
        if _telemetry_ndjson_enabled() and _telemetry_sample_rate() > 0:
            telemetry_file = art_dir_path / "telemetry.ndjson"  # type: ignore[operator]
            telemetry_file.touch(exist_ok=True)
        metrics_ndjson = art_dir_path / "metrics.ndjson"  # type: ignore[operator]
        metrics_ndjson.touch(exist_ok=True)
        metrics_json = art_dir_path / "metrics.json"  # type: ignore[operator]
        if not metrics_json.exists():
            metrics_json.write_text("[]\n", encoding="utf-8")
    except (IOError, OSError) as exc:
        logger.warning(
            "Failed to prepare artifacts directory '%s': %s", default_art_dir, exc
        )  # codeql[py/clear-text-logging-sensitive-data]
        art_dir_path = None

    model_cfg = dict(model_cfg or {})

    metadata_snapshot = _snapshot_payload(metadata)
    evaluation_snapshot = _snapshot_payload(evaluation)
    reasoning_snapshot = _snapshot_payload(reasoning)

    dp_settings: DifferentialPrivacyConfig | None = None
    if isinstance(dp_config, DifferentialPrivacyConfig):
        dp_settings = dp_config
    elif isinstance(dp_config, dict):
        try:
            dp_settings = DifferentialPrivacyConfig(**dp_config)
        except TypeError as exc:  # pragma: no cover - defensive
            logger.warning(
                "Invalid differential privacy config provided: %s", exc
            )  # codeql[py/clear-text-logging-sensitive-data]
    else:
        env_flag = os.getenv("CODEX_DP_ENABLED")
        if env_flag and str(env_flag).strip().lower() in {"1", "true", "yes", "on"}:
            dp_kwargs: dict[str, Any] = {"enabled": True}
            for field_name, env_name in (
                ("epsilon", "CODEX_DP_EPSILON"),
                ("delta", "CODEX_DP_DELTA"),
                ("noise_multiplier", "CODEX_DP_NOISE_MULTIPLIER"),
                ("max_grad_norm", "CODEX_DP_MAX_GRAD_NORM"),
            ):
                raw = os.getenv(env_name)
                if raw is None:
                    continue
                try:
                    dp_kwargs[field_name] = float(raw)
                except ValueError as e:
                    error_type = type(e).__name__
                    logger.debug(
                        "ValueError: <ERROR_TYPE>"
                    )  # codeql[py/clear-text-logging-sensitive-data]
                    logger.debug(
                        "Unable to parse %s env var %s", field_name, env_name
                    )  # codeql[py/clear-text-logging-sensitive-data]
            secure_rng_flag = os.getenv("CODEX_DP_SECURE_RNG")
            if secure_rng_flag and secure_rng_flag.lower() in {
                "1",
                "true",
                "yes",
                "on",
            }:
                dp_kwargs["secure_rng"] = True
            try:
                dp_settings = DifferentialPrivacyConfig(**dp_kwargs)
            except ImportError as exc:
                error_type = type(exc).__name__
                logger.debug(
                    "ImportError: <ERROR_TYPE>"
                )  # codeql[py/clear-text-logging-sensitive-data]
                logger.warning(
                    "Differential privacy disabled: %s", exc
                )  # codeql[py/clear-text-logging-sensitive-data]
                dp_settings = None

    # Dataset ingestion (summaries only)
    dataset_files_count = len(dataset_sources or [])
    dataset_total_records = 0
    dataset_checksums: list[str] = []
    dataset_checksum_map: dict[str, str] = {}
    if dataset_sources:
        paths = [Path(p) for p in dataset_sources]
        checksum_target = (
            (art_dir_path / "dataset_checksums.json") if art_dir_path is not None else None
        )
        recorded = record_dataset_checksums(paths, checksum_target)
        if isinstance(recorded, dict):
            dataset_checksum_map = recorded
            dataset_checksums = list(recorded.values())

    session_logger = None
    session_id = None
    try:
        session_logger = get_session_logger()
        session_id = session_logger.session_id
    except (ValueError, TypeError, RuntimeError):  # pragma: no cover - defensive
        session_logger = None
        session_id = None
    if session_logger is not None:
        try:
            session_logger.log_event(
                "training_start",
                {
                    "epochs": int(epochs),
                    "grad_accum": int(grad_accum),
                    "steps_per_epoch": int(steps_per_epoch),
                    "telemetry_enabled": bool(telemetry_enable),
                    "dp": (dp_settings.as_dict() if dp_settings else {"enabled": False}),
                    "dataset_files": dataset_files_count,
                },
            )
        except (IOError, OSError):  # pragma: no cover - best effort logging
            logger.debug(
                "Suppressed exception in handler", exc_info=True
            )  # codeql[py/clear-text-logging-sensitive-data]
    metrics_registry: CodexMetricsRegistry | None = None
    metrics_port_value: int | None = None
    metrics_env_port = os.getenv("CODEX_METRICS_PORT")
    if metrics_env_port:
        try:
            metrics_port_value = int(metrics_env_port)
        except ValueError as e:
            error_type = type(e).__name__
            logger.debug("ValueError: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
            logger.debug(
                "Invalid CODEX_METRICS_PORT value '%s'", metrics_env_port
            )  # codeql[py/clear-text-logging-sensitive-data]
    if metrics_port_value is None and telemetry_port is not None:
        metrics_port_value = int(telemetry_port)
    if metrics_enabled() or telemetry_enable:
        try:
            metrics_registry = CodexMetricsRegistry()
            metrics_registry.active_sessions.set(1)
        except (IOError, OSError) as exc:  # pragma: no cover - optional dependency path
            logger.debug(
                "Prometheus metrics disabled: %s", exc
            )  # codeql[py/clear-text-logging-sensitive-data]
            metrics_registry = None
        port_candidate = metrics_port_value or 8000
        start_metrics_server(port=port_candidate)

    if mlflow_enable and _HAS_MLFLOW:
        from codex_ml.tracking.mlflow_guard import bootstrap_offline_tracking

        safe_uri = bootstrap_offline_tracking()
        if mlflow_uri:
            if str(mlflow_uri).startswith("file:"):
                safe_uri = str(mlflow_uri)
            elif str(mlflow_uri).startswith("http"):
                logger.warning(
                    "Blocking remote MLflow URI '%s'; using local file backend %s",
                    mlflow_uri,
                    safe_uri,
                )
            else:
                try:
                    safe_uri = Path(mlflow_uri).expanduser().resolve().as_uri()
                except (IOError, OSError):
                    logger.warning(
                        "Unable to coerce MLflow URI '%s'; using %s",
                        mlflow_uri,
                        safe_uri,
                    )
        mlflow.set_tracking_uri(safe_uri)
        mlflow.set_experiment(mlflow_experiment)
        mlflow.start_run()
        mlflow.log_params({"epochs": epochs, "grad_accum": grad_accum, "model": model_name})

    device_obj = _resolve_device(device)
    dtype_obj = _resolve_dtype(dtype)
    _assert_bf16_capability(dtype, dtype_obj, bf16_require_capability, device_obj)

    model_kwargs: dict[str, Any] = dict(model_cfg or {})
    model_kwargs.setdefault("device", str(device_obj))
    if dtype_obj is not None:
        model_kwargs.setdefault("dtype", dtype_obj)
    if lora:
        model_kwargs["lora"] = {"enabled": True, **(lora_cfg or {})}
    internal_model_created = False
    model, internal_model_created = _load_or_create_model(model, model_name, model_kwargs)
    model, reasoning_runtime = _initialize_reasoning_runtime(model, reasoning, art_dir_path)
    if reasoning_runtime is not None:
        runtime_snapshot = _snapshot_payload(reasoning_runtime.config)
        if runtime_snapshot:
            reasoning_snapshot = runtime_snapshot

    if _HAS_TORCH and model is not None:
        try:
            model.to(device_obj)
            if dtype_obj is not None:
                model = model.to(dtype=dtype_obj)
        except (ConnectionError, TimeoutError) as exc:
            logger.warning(
                "Failed to move model to device/dtype: %s", exc
            )  # codeql[py/clear-text-logging-sensitive-data]
        else:
            # Verify effective dtype and surface implicit downcasts (e.g., bf16->fp32)
            _log_dtype_mismatch_if_any(dtype_obj, model)
            # Emit telemetry event when bf16 was requested but effective dtype differs
            try:
                import torch as _torch
            except (ConnectionError, TimeoutError) as e:
                logger.debug(
                    "Torch import failed for dtype telemetry: %s", e
                )  # codeql[py/clear-text-logging-sensitive-data]
            else:
                eff = _first_param_dtype(model)
                requested_is_bf16 = False
                req_str = None
                if dtype_obj is not None:
                    requested_is_bf16 = str(dtype_obj) == str(getattr(_torch, "bfloat16", None))
                    req_str = str(dtype_obj)
                if (
                    not requested_is_bf16
                    and isinstance(dtype, str)
                    and dtype.lower() in {"bf16", "bfloat16"}
                ):
                    requested_is_bf16 = True
                    req_str = dtype
                if (
                    requested_is_bf16
                    and eff is not None
                    and eff != str(getattr(_torch, "bfloat16", None))
                ):
                    _append_metrics_event(
                        art_dir_path,
                        {
                            "type": "telemetry",
                            "event": "bf16_downcast",
                            "requested": req_str or "bf16",
                            "effective": eff,
                            "message": "bf16 requested but parameters not bf16 (downcast)",
                            "timestamp": _now_ts(),
                        },
                    )

    cfg = getattr(model, "cfg", None)
    if cfg is not None and hasattr(cfg, "vocab_size") and cfg.vocab_size is not None:
        vocab_size = cfg.vocab_size
    else:
        vocab_size = 128

    dataset = None
    train_loader = None
    if _HAS_TORCH:
        effective_batch = batch_size or 8
        dataset = ToyDataset(
            num_samples=64,
            seq_len=16,
            vocab_size=vocab_size,
            seed=resolved_seed,
        )
        collate = _make_casting_collate(dataset_cast_policy, dtype_obj, device_obj, art_dir_path)
        train_loader = DataLoader(
            dataset,
            batch_size=effective_batch,
            shuffle=True,
            collate_fn=collate,
        )
        _dataset_dtype_gate(dataset, dtype_obj)
        # Optional: apply dataset casting policy (pre-forward) and log telemetry
        if dataset_cast_policy:
            try:
                sample0 = dataset[0]
            except (IOError, OSError):
                sample0 = None
            _ = _cast_batch_for_policy(
                sample0, dataset_cast_policy, dtype_obj, device_obj, art_dir_path
            )
    elif dataset_cast_policy:
        _append_metrics_event(
            art_dir_path,
            {
                "type": "telemetry",
                "event": "dataset_cast",
                "policy": str(dataset_cast_policy).lower(),
                "status": "skipped",
                "reason": "torch_unavailable",
            },
        )

    if model is not None and lora and apply_lora is not None:
        try:
            apply_lora(model, **(lora_cfg or {}))
        except (ValueError, TypeError, RuntimeError) as e:
            logger.warning(
                "Failed to apply LoRA: %s", e
            )  # codeql[py/clear-text-logging-sensitive-data]

    model_params_count = None
    if model is not None and _HAS_TORCH:
        try:
            model_params_count = sum(p.numel() for p in model.parameters())
        except Exception:
            model_params_count = None

    optimizer = None
    privacy_engine = None
    if model is not None and _HAS_TORCH:
        params = _select_parameters_for_optimization(model)
        if params:
            try:
                lr_value = float(learning_rate)
            except (TypeError, ValueError):
                lr_value = 1e-3
            optimizer = optim.Adam(params, lr=lr_value)
            # Optimizer-level gate: log parameter dtype in the first param group.
            try:
                eff_dtype = _first_param_dtype(model)
                if eff_dtype is not None and dtype_obj is not None and eff_dtype != str(dtype_obj):
                    logger.warning(
                        "Optimizer built for params dtype=%s; requested model dtype=%s",
                        eff_dtype,
                        str(dtype_obj),
                    )
            except (ConnectionError, TimeoutError) as e:
                logger.debug(
                    "Failed to check optimizer dtype compatibility: %s", e
                )  # codeql[py/clear-text-logging-sensitive-data]

    if (
        dp_settings is not None
        and _HAS_TORCH
        and optimizer is not None
        and train_loader is not None
    ):
        try:
            model, optimizer, train_loader, privacy_engine = make_private_model(
                model, optimizer, train_loader, dp_settings
            )
            if reasoning_runtime is not None:
                reasoning_runtime.bind_model(model)
        except ImportError as exc:
            error_type = type(exc).__name__
            logger.debug(
                "ImportError: <ERROR_TYPE>"
            )  # codeql[py/clear-text-logging-sensitive-data]
            logger.warning(
                "Differential privacy disabled: %s", exc
            )  # codeql[py/clear-text-logging-sensitive-data]
            dp_settings = None
        except (IOError, OSError) as exc:  # pragma: no cover - optional dependency path
            logger.warning(
                "Failed to enable differential privacy: %s", exc
            )  # codeql[py/clear-text-logging-sensitive-data]
            dp_settings = None
    elif dp_settings is not None and not _HAS_TORCH:
        logger.warning(
            "Differential privacy requested but torch is unavailable; skipping"
        )  # codeql[py/clear-text-logging-sensitive-data]
        dp_settings = None

    if _HAS_TORCH:
        scheduler = _init_scheduler(scheduler_cfg, optimizer, total_epochs=epochs)
    else:
        scheduler = None

    cb_list: list[Callback] = []
    if callbacks:
        cb_list.extend(callbacks)
    if eval_fn:
        cb_list.append(EvaluationCallback(eval_fn))
    cb_list.append(LoggingCallback())

    state: dict[str, Any] = {
        "start_time": _now_ts(),
        "model": model,
        "optimizer": optimizer,
        "scheduler": scheduler,
        "dataset_total_records": dataset_total_records,
        "run_config": run_config,
        "artifacts_dir": str(art_dir_path) if art_dir_path else None,
        "amp": {"enabled": amp, "dtype": amp_dtype},
        "mlflow": {
            "enabled": mlflow_enable,
            "uri": mlflow_uri,
            "experiment": mlflow_experiment,
        },
        "telemetry": {"enabled": telemetry_enable, "port": telemetry_port},
        "grad_accum": int(grad_accum),
        "deterministic_cudnn": bool(deterministic_cudnn),
        "callback_errors": [],
        "dp": dp_settings.as_dict() if dp_settings else {"enabled": False},
        "privacy_engine": bool(privacy_engine),
        "metrics_enabled": bool(metrics_registry),
        "session_id": session_id or get_session_id(),
    }

    applied_metadata = _apply_metadata_to_state(state, metadata_snapshot)

    reasoning_state: dict[str, Any] = {
        "enabled": bool(reasoning_runtime),
        "mode": reasoning_runtime.config.objective.mode if reasoning_runtime else None,
        "top_k": reasoning_runtime.top_k if reasoning_runtime else None,
        "threshold": reasoning_runtime.threshold if reasoning_runtime else None,
    }
    if reasoning_snapshot:
        reasoning_state["config"] = reasoning_snapshot
        trace_mode = reasoning_snapshot.get("trace_mode")
        if trace_mode is not None:
            reasoning_state.setdefault("trace_mode", trace_mode)
    if applied_metadata:
        reasoning_state.setdefault("metadata", applied_metadata)
    state["reasoning"] = reasoning_state

    if evaluation_snapshot:
        state["evaluation"] = {"config": evaluation_snapshot}

    for cb in cb_list:
        try:
            cb.on_train_start(state)
        except (IOError, OSError) as e:
            cb.record_error("on_train_start", e, state)
            logger.warning(
                "Callback on_train_start error: %s", e
            )  # codeql[py/clear-text-logging-sensitive-data]

    # Persist config snapshot (if provided)
    if run_config and checkpoint_dir:
        try:
            ckpt_root = Path(checkpoint_dir)
            ckpt_root.mkdir(parents=True, exist_ok=True)
            (ckpt_root / "config.snapshot.json").write_text(
                json.dumps(run_config, indent=2, sort_keys=True)
            )
        except (IOError, OSError) as e:
            logger.warning(
                "Failed to write config snapshot: %s", e
            )  # codeql[py/clear-text-logging-sensitive-data]

    start_epoch = 1
    resume_meta = {}
    if resume and checkpoint_dir:
        start_epoch, resume_meta = _attempt_resume(
            model,
            optimizer,
            scheduler,
            checkpoint_dir,
        )

    latest_payload: dict[str, Any] | None = None
    best_k_index: Optional[int] = None
    if retention_policy:
        for key in ("keep_best_k", "keep_best"):
            if key in retention_policy:
                try:
                    candidate = int(retention_policy[key])
                except (TypeError, ValueError):
                    continue
                if candidate > 0:
                    best_k_index = candidate
                    break

    def _persist_artifacts(best_checkpoint: dict[str, Any] | None, completed_epochs: int) -> None:
        if art_dir_path is None:
            return

        metrics_entries: list[dict[str, Any]] = []
        history = state.get("epoch_history")
        if isinstance(history, list):
            for entry in history:
                metrics_entry: dict[str, Any] = {"phase": "epoch_end"}
                if isinstance(entry, dict):
                    metrics_entry.update(entry)
                metrics_entries.append(metrics_entry)

        best_entry: dict[str, Any] = {"phase": "best_checkpoint"}
        if best_checkpoint:
            best_entry.update(best_checkpoint)
        else:
            best_entry["epoch"] = completed_epochs
        metrics_entries.append(best_entry)

        try:
            (art_dir_path / "metrics.json").write_text(json.dumps(metrics_entries, indent=2))
        except (IOError, OSError) as exc:
            logger.warning(
                "Failed to write metrics.json: %s", exc
            )  # codeql[py/clear-text-logging-sensitive-data]

        env_payload: dict[str, Any] = {
            "python": sys.version,
            "seed": seed if seed not in (None, 0) else _DEFAULT_SEED,
            "deterministic_cudnn": deterministic_cudnn,
            "amp": {"enabled": amp, "dtype": amp_dtype},
            "mlflow": {
                "enabled": mlflow_enable,
                "uri": mlflow_uri,
                "experiment": mlflow_experiment,
            },
            "telemetry": {"enabled": telemetry_enable, "port": telemetry_port},
        }
        if reasoning_runtime is not None:
            env_payload["reasoning"] = {
                "mode": reasoning_runtime.config.objective.mode,
                "top_k": reasoning_runtime.top_k,
                "threshold": reasoning_runtime.threshold,
            }
        metadata_state = state.get("metadata")
        if isinstance(metadata_state, dict) and metadata_state:
            env_payload["metadata"] = metadata_state
        if batch_size is not None:
            env_payload["batch_size"] = batch_size
        if _HAS_TORCH and torch is not None:
            try:
                env_payload["torch_version"] = torch.__version__
            except AttributeError:
                # torch might be a mock without __version__
                env_payload["torch_version"] = "unknown"

        try:
            (art_dir_path / "environment.json").write_text(json.dumps(env_payload, indent=2))
        except (IOError, OSError) as exc:
            logger.warning(
                "Failed to write environment.json: %s", exc
            )  # codeql[py/clear-text-logging-sensitive-data]

        if reasoning_runtime is not None:
            try:
                reasoning_history = reasoning_runtime.harness.history_snapshot()
            except (IOError, OSError):  # pragma: no cover - defensive snapshot
                reasoning_history = []
            if reasoning_history:
                try:
                    (art_dir_path / "reasoning_traces.json").write_text(
                        json.dumps(reasoning_history, indent=2)
                    )
                except (IOError, OSError) as exc:
                    logger.warning(
                        "Failed to write reasoning_traces.json: %s", exc
                    )  # codeql[py/clear-text-logging-sensitive-data]

        try:
            (art_dir_path / "dataset_checksums.json").write_text(
                json.dumps(dataset_checksum_map, indent=2)
            )
        except (IOError, OSError) as exc:
            logger.warning(
                "Failed to write dataset_checksums.json: %s", exc
            )  # codeql[py/clear-text-logging-sensitive-data]

    def _persist_control_surface_artifacts() -> None:
        if art_dir_path is None:
            return

        try:
            art_dir_path.mkdir(parents=True, exist_ok=True)
        except (IOError, OSError) as exc:
            logger.warning(
                "Failed to prepare metadata directory '%s': %s", art_dir_path, exc
            )  # codeql[py/clear-text-logging-sensitive-data]
            return

        cfg: dict[str, Any] = {}
        if isinstance(run_config, (Mapping, dict)):
            cfg = dict(run_config)

        meta_payload: dict[str, Any] = {}
        metadata_section = cfg.get("metadata")
        if isinstance(metadata_section, Mapping):
            meta_payload.update(_json_ready(metadata_section))

        session_id_val = state.get("session_id") if isinstance(state, dict) else None
        if session_id_val:
            meta_payload.setdefault("session_id", session_id_val)
        if art_dir_path is not None:
            meta_payload.setdefault("artifacts_dir", str(art_dir_path))

        control_surface: dict[str, Any] = {}
        trace_mode = cfg.get("trace_mode")
        training_section = cfg.get("training") if isinstance(cfg.get("training"), Mapping) else {}
        if not trace_mode and isinstance(training_section, Mapping):
            reasoning_cfg = training_section.get("reasoning")
            if isinstance(reasoning_cfg, Mapping):
                trace_mode = reasoning_cfg.get("trace_mode")
        if trace_mode:
            control_surface["trace_mode"] = trace_mode

        curriculum_cfg = cfg.get("curriculum")
        if isinstance(curriculum_cfg, Mapping):
            preset = curriculum_cfg.get("preset") or curriculum_cfg.get("phase_schedule")
            if preset:
                control_surface["curriculum.preset"] = preset

        evaluation_cfg = cfg.get("evaluation")
        if not isinstance(evaluation_cfg, Mapping) and isinstance(training_section, Mapping):
            evaluation_cfg = training_section.get("evaluation")
        if isinstance(evaluation_cfg, Mapping):
            preset = evaluation_cfg.get("preset")
            if preset:
                control_surface["evaluation.preset"] = preset

        deployment_cfg = cfg.get("deployment")
        if isinstance(deployment_cfg, Mapping):
            preset = deployment_cfg.get("preset")
            if preset:
                control_surface["deployment.preset"] = preset

        ring = meta_payload.get("rollout_ring") if isinstance(meta_payload, dict) else None
        if not ring:
            metadata_cfg = cfg.get("metadata")
            if isinstance(metadata_cfg, Mapping):
                ring = metadata_cfg.get("rollout_ring")
            if ring:
                meta_payload["rollout_ring"] = ring
        if ring:
            control_surface.setdefault("rollout_ring", ring)

        if control_surface:
            meta_payload["control_surface"] = _json_ready(control_surface)

        knobs_snapshot = {
            "trace_mode": trace_mode,
            "curriculum_preset": (
                curriculum_cfg.get("preset") if isinstance(curriculum_cfg, Mapping) else None
            ),
            "evaluation_preset": (
                evaluation_cfg.get("preset") if isinstance(evaluation_cfg, Mapping) else None
            ),
            "deployment_preset": (
                deployment_cfg.get("preset") if isinstance(deployment_cfg, Mapping) else None
            ),
        }

        meta_payload["knobs"] = _json_ready(knobs_snapshot)

        try:
            (art_dir_path / "run_metadata.json").write_text(
                json.dumps(_json_ready(meta_payload), indent=2),
                encoding="utf-8",
            )
        except (IOError, OSError) as exc:
            logger.warning(
                "Failed to write run_metadata.json: %s", exc
            )  # codeql[py/clear-text-logging-sensitive-data]

        reasoning_payload: dict[str, Any] = {}
        reasoning_cfg = cfg.get("reasoning")
        if not isinstance(reasoning_cfg, Mapping) and isinstance(training_section, Mapping):
            reasoning_cfg = training_section.get("reasoning")
        if isinstance(reasoning_cfg, Mapping):
            reasoning_payload["config"] = _json_ready(reasoning_cfg)
        if reasoning_runtime is not None:
            runtime_details = {
                "mode": getattr(reasoning_runtime.config.objective, "mode", None),
                "top_k": getattr(reasoning_runtime, "top_k", None),
                "threshold": getattr(reasoning_runtime, "threshold", None),
            }
            reasoning_payload["runtime"] = _json_ready(runtime_details)
            try:
                reasoning_payload["harness"] = _json_ready(reasoning_runtime.harness.describe())
            except (IOError, OSError):
                logger.debug(
                    "Suppressed exception in handler", exc_info=True
                )  # codeql[py/clear-text-logging-sensitive-data]
        if reasoning_payload:
            try:
                (art_dir_path / "reasoning.json").write_text(
                    json.dumps(_json_ready(reasoning_payload), indent=2),
                    encoding="utf-8",
                )
            except (IOError, OSError) as exc:
                logger.warning(
                    "Failed to write reasoning.json: %s", exc
                )  # codeql[py/clear-text-logging-sensitive-data]

        if isinstance(evaluation_cfg, Mapping):
            try:
                (art_dir_path / "evaluation.json").write_text(
                    json.dumps(_json_ready(evaluation_cfg), indent=2),
                    encoding="utf-8",
                )
            except (IOError, OSError) as exc:
                logger.warning(
                    "Failed to write evaluation.json: %s", exc
                )  # codeql[py/clear-text-logging-sensitive-data]

    target_epochs = int(epochs)
    if start_epoch > target_epochs:
        result = {
            "resumed": bool(resume_meta),
            "resumed_from_epoch": resume_meta.get("resumed_from_epoch"),
            "final_epoch": start_epoch - 1,
            "start_epoch": start_epoch,
            "message": "No epochs to run; already completed.",
            "optimizer_steps": 0,
            "total_steps": 0,
            "steps_per_epoch": steps_per_epoch,
            "grad_accum": grad_accum,
            "scheduler_type": scheduler_cfg.get("type") if scheduler_cfg else None,
            "dataset_files_count": dataset_files_count,
            "dataset_total_records": dataset_total_records,
            "learning_rate_history": [],
            "callback_errors": list(state.get("callback_errors", [])),
        }
        if resume_meta:
            result["resume_meta"] = resume_meta
        if reasoning_runtime is not None:
            try:
                result["reasoning_traces"] = reasoning_runtime.harness.history_snapshot()
            except (IOError, OSError):  # pragma: no cover - defensive snapshot
                result["reasoning_traces"] = []
        _persist_artifacts(resume_meta if resume_meta else None, target_epochs)
        report_dir = Path(checkpoint_dir) if checkpoint_dir else art_dir_path
        _render_reasoning_report(report_dir, state)
        _render_evaluation_report(report_dir, state)
        if return_state:
            result["model"] = model
            result["optimizer"] = optimizer
            result["scheduler"] = scheduler
            result["state"] = state
        return result

    total_optimizer_steps = 0
    total_steps = 0
    learning_rate_history: list[list[float]] = []
    last_checkpoint_sha = None

    # ------------------------------------------------------------------
    # Performance monitor — imported lazily to avoid hard failures.
    # ------------------------------------------------------------------
    _perf_monitor = None
    try:
        from codex.monitoring.performance_monitor import PerformanceMonitor as _PerfMon
        from codex.monitoring.performance_monitor import PerformanceSnapshot as _PerfSnap

        _perf_monitor = _PerfMon.from_env(run_id=_TRAIN_RUN_ID)
    except (ImportError, AttributeError):  # pragma: no cover — optional dependency
        pass

    # ------------------------------------------------------------------
    # Model drift detector (Gap 18) — imported lazily; never crashes training.
    # ------------------------------------------------------------------
    _drift_detector = None
    try:
        from codex_ml.monitoring.model_drift import ModelDriftDetector as _DriftDet

        _drift_detector = _DriftDet()
    except (ImportError, AttributeError):  # pragma: no cover — optional dependency
        logger.debug(
            "ModelDriftDetector unavailable; drift monitoring disabled."
        )  # codeql[py/clear-text-logging-sensitive-data]

    # ------------------------------------------------------------------
    # Data drift detector — initialised once per run; called after the
    # performance monitor block inside the epoch loop.
    # ------------------------------------------------------------------
    _drift_detector = _DataDriftDetector()
    _drift_reference: list[float] | None = None  # set on first epoch

    # ------------------------------------------------------------------
    # Epoch loop — wrapped to emit training-failure alerts on unhandled
    # exceptions while still re-raising so callers remain unaffected.
    # ------------------------------------------------------------------
    try:
        for epoch in range(start_epoch, target_epochs + 1):
            epoch_start = time.perf_counter()
            epoch_checkpoint_sha = None
            for cb in cb_list:
                try:
                    cb.on_epoch_start(epoch, state)
                except (ValueError, TypeError, RuntimeError) as e:
                    cb.record_error("on_epoch_start", e, state)
                    logger.warning(
                        "Callback on_epoch_start error: %s", e
                    )  # codeql[py/clear-text-logging-sensitive-data]

            epoch_loss_accum = 0.0
            synthetic_losses: list[float] = []
            steps_this_epoch = 0
            optimizer_steps_this_epoch = 0
            if reasoning_runtime is not None:
                reasoning_runtime.on_new_epoch()

            if model is not None and optimizer is not None and _HAS_TORCH:
                if dtype_obj is not None:
                    try:
                        model.to(dtype=dtype_obj)
                    except (ValueError, TypeError, RuntimeError):
                        logger.debug(
                            "Suppressed exception in handler", exc_info=True
                        )  # codeql[py/clear-text-logging-sensitive-data]
                model.to(device_obj)
                model.train()
                optimizer.zero_grad(set_to_none=True)

                loader_iter = iter(train_loader) if train_loader is not None else None
                for step in range(steps_per_epoch):
                    steps_this_epoch += 1
                    total_steps += 1
                    if loader_iter is not None:
                        load_start = time.perf_counter()
                        try:
                            _batch = next(loader_iter)
                        except StopIteration:
                            if train_loader is not None:
                                loader_iter = iter(train_loader)
                                _batch = next(loader_iter)
                            else:
                                raise RuntimeError(
                                    "Training cannot proceed without a valid train_loader."
                                )
                        finally:
                            load_duration = time.perf_counter() - load_start
                            if metrics_registry is not None:
                                metrics_registry.observe_data_loading(load_duration)
                    loss_val = _synthetic_step(model)
                    epoch_loss_accum += loss_val
                    synthetic_losses.append(loss_val)
                    if metrics_registry is not None:
                        metrics_registry.record_training_step(loss_val)
                    if reasoning_runtime is not None:
                        hidden_states = None
                        try:
                            hidden_states = getattr(model, "hidden_states", None)
                        except (ImportError, AttributeError):
                            hidden_states = None
                        step_ctx = (
                            {"hidden_states": hidden_states} if hidden_states is not None else None
                        )
                        reasoning_runtime.record_trace(
                            model,
                            epoch=epoch,
                            step=step + 1,
                            art_dir_path=art_dir_path,
                            session_id=session_id,
                            step_ctx=step_ctx,
                        )
                    if (step + 1) % grad_accum == 0:
                        try:
                            optimizer.step()
                            optimizer.zero_grad(set_to_none=True)
                            optimizer_steps_this_epoch += 1
                            total_optimizer_steps += 1
                        except (ValueError, TypeError, RuntimeError) as e:
                            logger.warning(
                                "Optimizer step failed: %s", e
                            )  # codeql[py/clear-text-logging-sensitive-data]

                if steps_per_epoch % grad_accum != 0:
                    try:
                        optimizer.step()
                        optimizer.zero_grad(set_to_none=True)
                        optimizer_steps_this_epoch += 1
                        total_optimizer_steps += 1
                    except (ValueError, TypeError, RuntimeError) as e:
                        logger.warning(
                            "Final optimizer step failed: %s", e
                        )  # codeql[py/clear-text-logging-sensitive-data]
            else:
                steps_this_epoch = steps_per_epoch
                total_steps += steps_per_epoch

            avg_loss = None
            if synthetic_losses:
                avg_loss = epoch_loss_accum / max(len(synthetic_losses), 1)

            if scheduler is not None and optimizer is not None:
                try:
                    scheduler.step()
                except (ValueError, TypeError, RuntimeError) as e:
                    logger.warning(
                        "Scheduler step failed: %s", e
                    )  # codeql[py/clear-text-logging-sensitive-data]
                current_lrs = _scheduler_current_lr(scheduler, optimizer)
            else:
                current_lrs = _scheduler_current_lr(None, optimizer)

            learning_rate_history.append(current_lrs or [])

            epoch_duration = time.perf_counter() - epoch_start
            if metrics_registry is not None:
                metrics_registry.observe_training_duration(epoch_duration)

            epoch_metrics = TrainingMetrics(
                epoch=epoch,
                synthetic_loss=avg_loss,
                optimizer_steps=optimizer_steps_this_epoch,
                total_steps=steps_this_epoch,
            ).to_dict()
            epoch_metrics["lr"] = current_lrs

            for cb in cb_list:
                try:
                    addon = cb.on_epoch_end(epoch, epoch_metrics, state)
                    merge_callback_results(epoch_metrics, addon)
                except TypeError as merge_exc:
                    logger.debug(
                        f"TypeError: {merge_exc}"
                    )  # codeql[py/clear-text-logging-sensitive-data]
                    cb.record_error("merge_callback_results", merge_exc, state)
                    logger.warning(
                        "Callback merge error: %s", merge_exc
                    )  # codeql[py/clear-text-logging-sensitive-data]
                except (ValueError, RuntimeError) as e:
                    cb.record_error("on_epoch_end", e, state)
                    logger.warning(
                        "Callback on_epoch_end error: %s", e
                    )  # codeql[py/clear-text-logging-sensitive-data]

            metric_session_id = session_id or get_session_id()
            metrics_payload = {
                "type": "metric",
                "timestamp": _now_ts(),
                "metric_name": "training.loss",
                "value": avg_loss,
                "epoch": epoch,
                "optimizer_steps": optimizer_steps_this_epoch,
                "total_steps": total_steps,
                "session_id": metric_session_id,
            }
            _append_metrics_event(art_dir_path, metrics_payload)
            duration_payload = {
                "type": "metric",
                "timestamp": _now_ts(),
                "metric_name": "training.epoch_duration_seconds",
                "value": epoch_duration,
                "epoch": epoch,
                "session_id": metric_session_id,
            }
            _append_metrics_event(art_dir_path, duration_payload)

            if checkpoint_dir:
                epoch_dir = Path(checkpoint_dir) / f"epoch-{epoch:04d}"
                epoch_dir.mkdir(parents=True, exist_ok=True)
                ckpt_metadata = {
                    "epoch": epoch,
                    "created_at": _now_ts(),
                    "model_params": model_params_count,
                    "optimizer_steps_total": total_optimizer_steps,
                    "optimizer_steps_epoch": optimizer_steps_this_epoch,
                    "steps_per_epoch": steps_per_epoch,
                    "grad_accum": grad_accum,
                    "avg_loss": avg_loss,
                    "scheduler_type": scheduler_cfg.get("type") if scheduler_cfg else None,
                    "current_lrs": current_lrs,
                    "learning_rate_history_len": len(learning_rate_history),
                }
                if model is not None and _HAS_TORCH:
                    try:
                        save_checkpoint(
                            model=model,
                            optimizer=optimizer,
                            scheduler=scheduler,
                            out_dir=epoch_dir,
                            metadata=ckpt_metadata,
                            metric_name="avg_loss",
                            metric_value=avg_loss,
                            best_k=best_k_index,
                        )
                    except (ValueError, TypeError, RuntimeError) as e:
                        msg = "Failed to save checkpoint for epoch %d: %s"
                        logger.warning(
                            msg, epoch, e
                        )  # codeql[py/clear-text-logging-sensitive-data]
                epoch_checkpoint_sha = _checkpoint_digest(epoch_dir)
                if epoch_checkpoint_sha:
                    last_checkpoint_sha = epoch_checkpoint_sha

                latest_payload = {
                    "epoch": epoch,
                    "path": epoch_dir.name,
                    "created_at": _now_ts(),
                    "model_params": model_params_count,
                    "optimizer_steps_total": total_optimizer_steps,
                    "scheduler_type": scheduler_cfg.get("type") if scheduler_cfg else None,
                    "checkpoint_sha256": epoch_checkpoint_sha,
                }
                try:
                    (Path(checkpoint_dir) / "latest.json").write_text(
                        json.dumps(latest_payload, indent=2)
                    )
                except (IOError, OSError) as e:
                    logger.warning(
                        "Failed to write latest.json: %s", e
                    )  # codeql[py/clear-text-logging-sensitive-data]

                # Retention pruning
                if retention_policy:
                    try:
                        prune_result = prune_checkpoints(checkpoint_dir, **retention_policy)
                        state["retention_last"] = prune_result
                    except (ValueError, TypeError, RuntimeError) as e:
                        logger.warning(
                            "Retention pruning failed: %s", e
                        )  # codeql[py/clear-text-logging-sensitive-data]
            else:
                latest_payload = {
                    "epoch": epoch,
                    "created_at": _now_ts(),
                    "model_params": model_params_count,
                    "optimizer_steps_total": total_optimizer_steps,
                    "scheduler_type": scheduler_cfg.get("type") if scheduler_cfg else None,
                }

            state["latest_checkpoint"] = latest_payload

            sha_for_log = locals().get("epoch_checkpoint_sha") or last_checkpoint_sha
            if sha_for_log:
                sha_for_log = sha_for_log[:12]

            # Performance degradation monitoring — must never crash training.
            if _perf_monitor is not None:
                try:
                    _epoch_throughput = (
                        steps_this_epoch / epoch_duration if epoch_duration > 0 else None
                    )
                    _perf_monitor.record(
                        _PerfSnap(epoch=epoch, loss=avg_loss, throughput=_epoch_throughput)
                    )
                except (ValueError, TypeError, RuntimeError) as _perf_exc:
                    logger.debug(
                        "Performance monitor record failed (non-fatal): %s", _perf_exc
                    )  # codeql[py/clear-text-logging-sensitive-data]

            # ------------------------------------------------------------------
            # Data drift monitoring — runs after the performance monitor block.
            # On the first epoch the current loss distribution is stored as the
            # reference baseline; on subsequent epochs it is compared against it.
            # All exceptions are swallowed so drift monitoring never crashes training.
            # ------------------------------------------------------------------
            try:
                # Build a simple 4-bucket histogram from the epoch's synthetic losses
                # (or fall back to a single-value distribution if losses are unavailable).
                _loss_dist: list[float]
                if synthetic_losses:
                    _n = len(synthetic_losses)
                    _q = max(_n // 4, 1)
                    _loss_dist = [
                        sum(synthetic_losses[i * _q : (i + 1) * _q]) + 1e-9 for i in range(4)
                    ]
                else:
                    _loss_dist = [max(avg_loss or 1e-9, 1e-9), 1e-9, 1e-9, 1e-9]

                if _drift_reference is None:
                    # Epoch 1 — seed the reference distribution
                    _drift_reference = _loss_dist
                    logger.debug(
                        "Data drift: reference distribution seeded at epoch %d", epoch
                    )  # codeql[py/clear-text-logging-sensitive-data]
                else:
                    _drift_results = _drift_detector.check_epoch(
                        _drift_reference,
                        _loss_dist,
                        epoch=epoch,
                        feature_name="training_loss_hist",
                    )
                    _psi_r = _drift_results["psi"]
                    _kl_r = _drift_results["kl"]
                    _append_metrics_event(
                        art_dir_path,
                        {
                            "type": "data_drift",
                            "timestamp": _now_ts(),
                            "epoch": epoch,
                            "psi_score": _psi_r.score,
                            "psi_drifted": _psi_r.drifted,
                            "psi_severity": _psi_r.severity,
                            "kl_score": _kl_r.score,
                            "kl_drifted": _kl_r.drifted,
                            "kl_severity": _kl_r.severity,
                        },
                    )
            except (ValueError, TypeError, RuntimeError) as _drift_exc:
                logger.debug(
                    "Data drift check failed (non-fatal): %s", _drift_exc
                )  # codeql[py/clear-text-logging-sensitive-data]

            # Model drift detection (Gap 18) — must never crash training.
            if _drift_detector is not None:
                try:
                    # Derive per-step confidence proxies from the synthetic loss values
                    # collected during this epoch: confidence ≈ exp(-loss), clipped to [0,1].
                    import math as _math

                    _epoch_conf_scores = (
                        [max(0.0, min(1.0, _math.exp(-loss))) for loss in synthetic_losses]
                        if synthetic_losses
                        else None
                    )

                    if _epoch_conf_scores:
                        if not _drift_detector.has_baseline():
                            # First epoch always becomes the baseline reference.
                            _drift_detector.update_baseline(_epoch_conf_scores)
                        else:
                            _drift_result = _drift_detector.check(_epoch_conf_scores, epoch=epoch)
                            if _drift_result.drift_detected:
                                logger.warning(
                                    "Model drift detected at epoch %d: %s",
                                    epoch,
                                    _drift_result.summary(),
                                )
                            if state is not None and isinstance(state, dict):
                                state["drift_result_epoch"] = _drift_result.to_dict()
                except (ValueError, TypeError, RuntimeError) as _drift_exc:
                    logger.debug(
                        "Drift detector failed (non-fatal): %s", _drift_exc
                    )  # codeql[py/clear-text-logging-sensitive-data]

            logger.info(
                "Epoch %d/%d | loss=%s | steps=%d | opt_steps=%d | lr=%s | sha=%s",
                epoch,
                target_epochs,
                f"{avg_loss:.6f}" if avg_loss is not None else "n/a",
                steps_this_epoch,
                optimizer_steps_this_epoch,
                current_lrs,
                sha_for_log,
            )
    except Exception as _train_exc:
        # Emit a failure alert and re-raise so the caller still sees the error.
        if _ALERTING_AVAILABLE and _TrainingAlertManager is not None:
            try:
                _TrainingAlertManager.from_env().alert_training_failure(
                    _train_exc,
                    run_id=_TRAIN_RUN_ID,
                    epoch=locals().get("epoch", 0),
                )
            except (
                ValueError,
                TypeError,
                RuntimeError,
            ):  # pragma: no cover — alerting must never crash training
                logger.debug(
                    "Suppressed alerting exception in training failure handler", exc_info=True
                )
        raise

    for cb in cb_list:
        try:
            cb.on_train_end(state)
        except (ValueError, TypeError, RuntimeError) as e:
            cb.record_error("on_train_end", e, state)
            logger.warning(
                "Callback on_train_end error: %s", e
            )  # codeql[py/clear-text-logging-sensitive-data]

    if metrics_registry is not None:
        try:
            metrics_registry.active_sessions.set(0)
        except (ValueError, TypeError, RuntimeError):  # pragma: no cover - defensive
            logger.debug(
                "Suppressed exception in handler", exc_info=True
            )  # codeql[py/clear-text-logging-sensitive-data]
    wall = time.time() - t_start
    result = {
        "resumed": bool(resume_meta),
        "resumed_from_epoch": resume_meta.get("resumed_from_epoch"),
        "final_epoch": target_epochs,
        "start_epoch": start_epoch,
        "epochs": target_epochs,
        "optimizer_steps": total_optimizer_steps,
        "total_steps": total_steps,
        "steps_per_epoch": steps_per_epoch,
        "grad_accum": grad_accum,
        "model_params": model_params_count,
        "internal_model_created": internal_model_created,
        "wall_time_sec": wall,
        "scheduler_type": scheduler_cfg.get("type") if scheduler_cfg else None,
        "learning_rate_history": learning_rate_history,
        "dataset_files_count": dataset_files_count,
        "dataset_total_records": dataset_total_records,
        "dataset_checksums": dataset_checksums,
        "checkpoint_sha256_last": last_checkpoint_sha,
        "retention_last": state.get("retention_last"),
        "artifacts_dir": str(art_dir_path) if art_dir_path else None,
        "deterministic_cudnn": bool(deterministic_cudnn),
        "callback_errors": list(state.get("callback_errors", [])),
        "dp": dp_settings.as_dict() if dp_settings else {"enabled": False},
        "metrics_enabled": bool(metrics_registry),
        "privacy_engine": bool(privacy_engine),
        "session_id": session_id or get_session_id(),
    }
    if resume_meta:
        result["resume_meta"] = resume_meta
    if reasoning_runtime is not None:
        try:
            result["reasoning_traces"] = reasoning_runtime.harness.history_snapshot()
        except Exception:  # pragma: no cover - defensive snapshot
            result["reasoning_traces"] = []
        result["reasoning_objective"] = reasoning_runtime.config.objective.mode
        result["reasoning_top_k"] = reasoning_runtime.top_k

    _persist_artifacts(latest_payload, target_epochs)
    _persist_control_surface_artifacts()

    if session_logger is not None:
        try:
            session_logger.log_event(
                "training_end",
                {
                    "epochs_completed": target_epochs,
                    "optimizer_steps": total_optimizer_steps,
                    "wall_time_sec": wall,
                    "dp": result.get("dp", {"enabled": False}),
                    "metrics_enabled": bool(metrics_registry),
                },
            )
        except (ValueError, TypeError, RuntimeError):  # pragma: no cover - best effort logging
            logger.debug(
                "Suppressed exception in handler", exc_info=True
            )  # codeql[py/clear-text-logging-sensitive-data]
    if return_state:
        result["model"] = model
        result["optimizer"] = optimizer
        result["scheduler"] = scheduler
        result["state"] = state

    report_dir = Path(checkpoint_dir) if checkpoint_dir else art_dir_path
    _render_reasoning_report(report_dir, state)
    _render_evaluation_report(report_dir, state)

    # Emit training-complete alert (best-effort; never raises).
    if _ALERTING_AVAILABLE and _TrainingAlertManager is not None:
        try:
            _final_loss = result.get("learning_rate_history") and state.get("avg_loss")
            _final_loss_val: float = float(_final_loss) if _final_loss is not None else 0.0  # type: ignore[arg-type]
            _TrainingAlertManager.from_env().alert_training_complete(
                run_id=_TRAIN_RUN_ID,
                epochs=int(result.get("epochs", 0)),  # type: ignore[arg-type]
                final_loss=_final_loss_val,
                wall_time_sec=result.get("wall_time_sec", 0),
            )
        except (
            ValueError,
            TypeError,
            RuntimeError,
        ):  # pragma: no cover — alerting must never crash training
            logger.debug(
                "Suppressed alerting exception in training complete handler", exc_info=True
            )

    return result


def main(argv: Sequence[str] | None = None) -> None:
    """Minimal CLI entry point preserving legacy train_loop behavior."""

    parser = argparse.ArgumentParser(description="Run the legacy Codex training loop")
    parser.add_argument("--epochs", type=int, default=1, help="Number of training epochs")
    parser.add_argument("--grad-accum", type=int, default=1, help="Gradient accumulation steps")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument(
        "--art-dir",
        type=str,
        default=None,
        help="Artifacts directory for metrics output",
    )
    args = parser.parse_args(argv)

    run_training(
        epochs=args.epochs,
        grad_accum=args.grad_accum,
        seed=args.seed,
        art_dir=args.art_dir,
    )


if __name__ == "__main__":  # pragma: no cover - CLI invocation
    main()

__all__ = ["run_training"]
