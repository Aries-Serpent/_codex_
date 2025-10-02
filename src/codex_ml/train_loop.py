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

import json
import logging
import os
import random
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

from codex_ml.logging.ndjson_logger import is_legacy_mode
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

    _HAS_TORCH = True
except Exception:  # noqa: BLE001
    torch = None  # type: ignore
    nn = None  # type: ignore
    optim = None  # type: ignore
    StepLR = None  # type: ignore
    DataLoader = None  # type: ignore
    Dataset = object  # type: ignore
    _HAS_TORCH = False

try:
    from codex_ml.models.registry import get_model as instantiate_model
except Exception:  # noqa: BLE001
    instantiate_model = None  # type: ignore

try:
    from codex_ml.lora import apply_lora
except Exception:  # noqa: BLE001
    apply_lora = None  # type: ignore

try:
    from codex_ml.data import loaders as data_loaders
except Exception:  # noqa: BLE001
    data_loaders = None  # type: ignore

try:
    from codex_ml.callbacks import (
        Callback,
        EvaluationCallback,
        LoggingCallback,
        merge_callback_results,
    )
except Exception:  # noqa: BLE001

    class Callback:  # type: ignore
        def on_train_start(self, state: Dict[str, Any]) -> None: ...

        def on_epoch_start(self, epoch: int, state: Dict[str, Any]) -> None: ...

        def on_epoch_end(
            self,
            epoch: int,
            metrics: Dict[str, Any],
            state: Dict[str, Any],
        ) -> None: ...

        def on_train_end(self, state: Dict[str, Any]) -> None: ...

    def merge_callback_results(
        base: Dict[str, Any], addon: Dict[str, Any] | None
    ) -> Dict[str, Any]:
        if addon:
            base.update(addon)
        return base

    EvaluationCallback = Callback  # type: ignore
    LoggingCallback = Callback  # type: ignore

try:
    from codex_ml.utils.determinism import set_cudnn_deterministic
except Exception:  # noqa: BLE001

    def set_cudnn_deterministic(enable: bool, benchmark: bool = False):  # type: ignore
        return


try:
    from codex_ml.utils.retention import prune_checkpoints
except Exception:  # noqa: BLE001

    def prune_checkpoints(*args, **kwargs):  # type: ignore
        return {"dry_run": True}


if _HAS_TORCH:

    class ToyDataset(Dataset):
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

    class ToyDataset:  # type: ignore[override]
        def __init__(self, *_, **__):
            raise RuntimeError("Torch is required to construct ToyDataset")

        def __len__(self) -> int:  # pragma: no cover - defensive
            return 0

        def __getitem__(self, index: int):  # pragma: no cover - defensive
            raise RuntimeError("Torch is required to construct ToyDataset")


_DEFAULT_SEED = 1234


def _set_seed(seed: Optional[int]) -> int:
    if seed in (None, 0):
        seed = _DEFAULT_SEED
    resolved_seed = int(seed)
    random.seed(resolved_seed)
    try:
        import numpy as np  # noqa

        np.random.seed(resolved_seed)  # type: ignore
    except Exception:  # noqa: BLE001
        pass
    if _HAS_TORCH:
        torch.manual_seed(resolved_seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(resolved_seed)
    return resolved_seed


def _now_ts() -> str:
    return datetime.utcnow().isoformat() + "Z"


_LEGACY_NDJSON = is_legacy_mode()
_TRAIN_RUN_ID = os.environ.get("CODEX_RUN_ID") or uuid4().hex


def _coerce_telemetry_event(record: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure a telemetry record has required keys: type, event, timestamp.

    Any missing keys are populated with defaults; additional keys are preserved.
    """
    out = dict(record)
    out.setdefault("type", "telemetry")
    out.setdefault("event", "unknown")
    out.setdefault("timestamp", _now_ts())
    return out


def demo_epoch(epoch: int, *, grad_accum: int = 1) -> Dict[str, Any]:
    """Return deterministic demo metrics for documentation and tests."""

    return {
        "epoch": int(epoch),
        "grad_accum": int(grad_accum),
        "timestamp": _now_ts(),
    }


def record_metrics(
    prefix: str | None = None,
    epoch: int | None = None,
    metrics: Dict[str, Any] | None = None,
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

    payload: Dict[str, Any] = {
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
    history: list[Dict[str, Any]] = []
    if json_path.exists():
        try:
            loaded = json.loads(json_path.read_text(encoding="utf-8"))
            if isinstance(loaded, list):
                history = loaded
        except Exception:
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
    return mapping.get(dtype.lower(), None)


def _resolve_device(device: Optional[str]):
    if not _HAS_TORCH:
        return device or "cpu"
    if device is None:
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    try:
        return torch.device(device)
    except (TypeError, ValueError, RuntimeError) as exc:
        logger.warning("Invalid device '%s': %s. Falling back to CPU.", device, exc)
        return torch.device("cpu")


def _load_or_create_model(
    model: Any | None, model_name: str | None, model_kwargs: Dict[str, Any]
) -> tuple[Any, bool]:
    if model is not None:
        return model, False
    if instantiate_model is None:
        raise RuntimeError("Model registry is not available")
    if not model_name:
        raise ValueError("model_name must be provided when no model instance is supplied")
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
        import torch as _torch  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
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
            except Exception:
                # If placement fails, let the matmul attempt occur on default device.
                pass
        _ = a @ b
    except Exception as exc:  # pragma: no cover - runtime check
        raise RuntimeError("bf16 required but runtime cannot construct bfloat16 tensors") from exc


def _attempt_resume(model, optimizer, scheduler, checkpoint_dir: str | Path):
    resume_meta = {}
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
        except Exception as e:  # noqa
            resume_meta["model_state_loaded"] = False
            resume_meta["optimizer_state_loaded"] = False
            resume_meta["scheduler_state_loaded"] = False
            resume_meta["model_state_error"] = str(e)
            return 1, resume_meta
    except Exception as e:  # noqa: BLE001
        resume_meta["resume_error"] = f"latest.json parse failure: {e}"
        return 1, resume_meta


def _select_parameters_for_optimization(model):
    if model is None:
        return []
    return [p for p in model.parameters() if p.requires_grad]


def _synthetic_step(model):
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
    except Exception:  # pragma: no cover - defensive
        return None
    return None


def _log_dtype_mismatch_if_any(requested: Any, model) -> None:
    """Log a clear message if requested dtype differs from effective param dtype."""
    if requested is None or model is None:
        return
    try:
        import torch as _torch  # noqa: F401
    except Exception:
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
        import torch as _torch  # noqa: F401
    except Exception:
        return
    try:
        sample = dataset[0]
        ds_dtype = getattr(sample, "dtype", None)
    except Exception:
        ds_dtype = None
    if ds_dtype is not None and desired is not None:
        logger.info(
            "Dataset dtype=%s; model requested dtype=%s (casting may occur during forward)",
            str(ds_dtype),
            str(desired),
        )


def _append_metrics_event(art_dir_path: Path | None, record: Dict[str, Any]) -> None:
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
    except Exception as exc:  # noqa: BLE001
        logger.debug("Failed to append telemetry event: %s", exc)


def _telemetry_max_items() -> int:
    try:
        raw = os.environ.get("CODEX_TELEMETRY_MAX_ITEMS", "1000").strip()
        n = int(raw)
        return n if n > 0 else 1000
    except Exception:
        return 1000


def _append_telemetry_json_rollover(base_dir: Path, record: Dict[str, Any]) -> None:
    """Append record to artifacts/telemetry.json with simple rollover (best-effort)."""
    try:
        if not _telemetry_json_enabled():
            return
        path = base_dir / "telemetry.json"
        history: list[Dict[str, Any]] = []
        if path.exists():
            try:
                loaded = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(loaded, list):
                    history = list(loaded)
            except Exception:
                history = []
        roll = len(history) >= _telemetry_max_items()
        max_bytes = _telemetry_max_bytes()
        if not roll and max_bytes > 0 and path.exists():
            try:
                roll = path.stat().st_size >= max_bytes
            except Exception:
                roll = False
        if roll:
            ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S%fZ")
            try:
                path.rename(base_dir / f"telemetry-{ts}.json")
            except Exception:
                history = []
            else:
                history = []
        history.append(dict(record))
        path.write_text(json.dumps(history, indent=2, sort_keys=True), encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        logger.debug("Failed to append telemetry.json: %s", exc)


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
    except Exception:
        return 0


def _append_telemetry_ndjson(base_dir: Path, record: Dict[str, Any]) -> None:
    """Append record to artifacts/telemetry.ndjson (best-effort)."""
    if not _telemetry_ndjson_enabled():
        return
    try:
        path = base_dir / "telemetry.ndjson"
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True) + "\n")
    except Exception:
        pass


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


def _telemetry_should_sample(record: Dict[str, Any]) -> bool:
    # Lightweight random sampling based on sample_rate; could be extended per-event.
    try:
        rate = _telemetry_sample_rate()
        if rate >= 1.0:
            return True
        if rate <= 0.0:
            return False
        import random as _random

        return _random.random() < rate
    except Exception:
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
    try:
        import torch as _torch
    except Exception:
        return sample
    try:
        src_dtype = getattr(sample, "dtype", None)
    except Exception:
        src_dtype = None
    target_dtype = None
    if policy_norm == "to_model_dtype" and desired is not None:
        target_dtype = desired
    elif policy_norm == "to_fp32":
        target_dtype = getattr(_torch, "float32", None)
    else:
        return sample
    casted = sample
    try:
        if target_dtype is not None and hasattr(sample, "to"):
            casted = sample.to(device if device is not None else _torch.device("cpu"))
            casted = casted.to(dtype=target_dtype)
            _append_metrics_event(
                art_dir_path,
                {
                    "type": "telemetry",
                    "event": "dataset_cast",
                    "policy": policy_norm,
                    "from": str(src_dtype),
                    "to": str(target_dtype),
                },
            )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Dataset cast policy '%s' failed: %s", policy_norm, exc)
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
        try:
            return [_cast_batch_for_policy(x, policy, desired, device, art_dir_path) for x in batch]
        except Exception:
            return batch

    return _collate


def _init_scheduler(scheduler_cfg: Optional[dict], optimizer, total_epochs: int):
    if not scheduler_cfg or optimizer is None or not _HAS_TORCH:
        return None
    sched_type = scheduler_cfg.get("type")
    if not sched_type:
        return None
    base_lrs = [g["lr"] for g in optimizer.param_groups]

    if sched_type == "linear":
        final_lr_scale = float(scheduler_cfg.get("final_lr_scale", 0.0))

        class _LinearEpochScheduler:
            def __init__(self, opt, total_epochs, final_scale, base_lrs):
                self.opt = opt
                self.total_epochs = max(total_epochs, 1)
                self.final_scale = final_scale
                self.base_lrs = base_lrs
                self.last_epoch = 0

            def get_lr(self):
                progress = min(self.last_epoch / self.total_epochs, 1.0)
                scale = (1 - progress) + progress * self.final_scale
                return [lr * scale for lr in self.base_lrs]

            def step(self):
                self.last_epoch += 1
                new_lrs = self.get_lr()
                for g, lr in zip(self.opt.param_groups, new_lrs):
                    g["lr"] = lr

            def state_dict(self):
                return {
                    "last_epoch": self.last_epoch,
                    "total_epochs": self.total_epochs,
                    "final_lr_scale": self.final_scale,
                    "base_lrs": self.base_lrs,
                    "type": "linear",
                }

            def load_state_dict(self, state):
                self.last_epoch = state.get("last_epoch", 0)

        return _LinearEpochScheduler(optimizer, total_epochs, final_lr_scale, base_lrs)

    if sched_type == "step":
        if StepLR is None:
            return None
        step_size = int(scheduler_cfg.get("step_size", 1))
        gamma = float(scheduler_cfg.get("gamma", 0.9))
        return StepLR(optimizer, step_size=step_size, gamma=gamma)

    logger.warning("Unknown scheduler type '%s' - ignoring.", sched_type)
    return None


def _scheduler_current_lr(scheduler, optimizer):
    if scheduler is None or optimizer is None:
        return None
    try:
        return [pg["lr"] for pg in optimizer.param_groups]
    except Exception:  # noqa: BLE001
        return None


def _checkpoint_digest(ckpt_dir: Path) -> str | None:
    sha_file = ckpt_dir / "checkpoint.sha256"
    if sha_file.exists():
        try:
            return sha_file.read_text(encoding="utf-8").strip() or None
        except Exception:  # noqa: BLE001
            return None
    model_file = ckpt_dir / "model.pt"
    if model_file.exists():
        try:
            return sha256sum(model_file)
        except Exception:  # noqa: BLE001
            return None
    return None


@dataclass
class TrainingMetrics:
    epoch: int
    synthetic_loss: float | None = None
    optimizer_steps: int = 0
    total_steps: int = 0

    def to_dict(self):
        return asdict(self)


def run_training(
    epochs: int = 1,
    grad_accum: int = 1,
    seed: int | None = None,
    art_dir: str | Path | None = None,
    model: Optional[Any] = None,
    model_name: str | None = None,
    model_cfg: Optional[Dict[str, Any]] = None,
    lora: bool = False,
    lora_cfg: dict | None = None,
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
    scheduler_cfg: dict | None = None,
    dataset_sources: Optional[List[str | Path]] = None,
    dataset_cache_dir: Optional[str | Path] = None,
    callbacks: Optional[List[Callback]] = None,
    eval_fn: Optional[Callable[[int, Dict[str, Any]], Dict[str, Any]]] = None,
    mlflow_enable: bool = False,
    mlflow_uri: str | None = None,
    mlflow_experiment: str | None = None,
    telemetry_enable: bool = False,
    telemetry_port: int | None = None,
    # NEW:
    deterministic_cudnn: bool = False,
    run_config: Optional[Dict[str, Any]] = None,
    retention_policy: Optional[Dict[str, Any]] = None,
    bf16_require_capability: bool = False,
    dataset_cast_policy: str | None = None,
    **extra_kwargs: Any,
) -> Dict[str, Any]:
    """
    Training loop (extended):
      - CUDNN determinism (opt-in)
      - checkpoint sha256
      - config snapshot
      - retention policy
    """
    t_start = time.time()
    if extra_kwargs:
        logger.debug("Ignoring unused training kwargs: %s", sorted(extra_kwargs))
    resolved_seed = _set_seed(seed)
    try:
        set_reproducible(resolved_seed, deterministic=bool(deterministic_cudnn))
    except Exception:  # noqa: BLE001 - seeding best effort
        pass
    if deterministic_cudnn:
        set_cudnn_deterministic(True, benchmark=False)

    if grad_accum < 1:
        grad_accum = 1
    if steps_per_epoch < 1:
        steps_per_epoch = 1

    art_dir_path: Path | None = None
    if art_dir is not None:
        try:
            art_dir_path = Path(art_dir)
            art_dir_path.mkdir(parents=True, exist_ok=True)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to prepare artifacts directory '%s': %s", art_dir, exc)
            art_dir_path = None

    model_cfg = dict(model_cfg or {})

    # Dataset ingestion (summaries only)
    dataset_files_count = len(dataset_sources or [])
    dataset_total_records = 0
    dataset_checksums: List[str] = []
    dataset_checksum_map: Dict[str, str] = {}
    if dataset_sources:
        paths = [Path(p) for p in dataset_sources]
        checksum_target = (
            (art_dir_path / "dataset_checksums.json") if art_dir_path is not None else None
        )
        recorded = record_dataset_checksums(paths, checksum_target)
        if isinstance(recorded, dict):
            dataset_checksum_map = recorded
            dataset_checksums = list(recorded.values())

    if telemetry_enable:
        start_metrics_server(port=telemetry_port)

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
                except Exception:
                    logger.warning(
                        "Unable to coerce MLflow URI '%s'; using %s", mlflow_uri, safe_uri
                    )
        mlflow.set_tracking_uri(safe_uri)
        mlflow.set_experiment(mlflow_experiment)
        mlflow.start_run()
        mlflow.log_params({"epochs": epochs, "grad_accum": grad_accum, "model": model_name})

    device_obj = _resolve_device(device)
    dtype_obj = _resolve_dtype(dtype)
    _assert_bf16_capability(dtype, dtype_obj, bf16_require_capability, device_obj)

    model_kwargs: Dict[str, Any] = dict(model_cfg or {})
    model_kwargs.setdefault("device", str(device_obj))
    if dtype_obj is not None:
        model_kwargs.setdefault("dtype", dtype_obj)
    if lora:
        model_kwargs["lora"] = {"enabled": True, **(lora_cfg or {})}
    internal_model_created = False
    model, internal_model_created = _load_or_create_model(model, model_name, model_kwargs)

    if _HAS_TORCH and model is not None:
        try:
            model.to(device_obj)
            if dtype_obj is not None:
                model = model.to(dtype=dtype_obj)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to move model to device/dtype: %s", exc)
        else:
            # Verify effective dtype and surface implicit downcasts (e.g., bf16->fp32)
            _log_dtype_mismatch_if_any(dtype_obj, model)
            # Emit telemetry event when bf16 was requested but effective dtype differs
            try:
                import torch as _torch  # noqa: F401
            except Exception:
                pass
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
    if _HAS_TORCH:
        effective_batch = batch_size or 8
        dataset = ToyDataset(
            num_samples=64,
            seq_len=16,
            vocab_size=vocab_size,
            seed=resolved_seed,
        )
        collate = _make_casting_collate(dataset_cast_policy, dtype_obj, device_obj, art_dir_path)
        DataLoader(dataset, batch_size=effective_batch, shuffle=True, collate_fn=collate)
        _dataset_dtype_gate(dataset, dtype_obj)
        # Optional: apply dataset casting policy (pre-forward) and log telemetry
        if dataset_cast_policy:
            try:
                sample0 = dataset[0]
            except Exception:
                sample0 = None
            _ = _cast_batch_for_policy(
                sample0, dataset_cast_policy, dtype_obj, device_obj, art_dir_path
            )

    if model is not None and lora and apply_lora is not None:
        try:
            apply_lora(model, **(lora_cfg or {}))
        except Exception as e:  # noqa: BLE001
            logger.warning("Failed to apply LoRA: %s", e)

    model_params_count = None
    if model is not None and _HAS_TORCH:
        try:
            model_params_count = sum(p.numel() for p in model.parameters())
        except Exception:  # noqa: BLE001
            model_params_count = None

    optimizer = None
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
            except Exception:
                pass

    if _HAS_TORCH:
        scheduler = _init_scheduler(scheduler_cfg, optimizer, total_epochs=epochs)
    else:
        scheduler = None

    cb_list: List[Callback] = []
    if callbacks:
        cb_list.extend(callbacks)
    if eval_fn:
        cb_list.append(EvaluationCallback(eval_fn))
    cb_list.append(LoggingCallback())

    state: Dict[str, Any] = {
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
    }

    for cb in cb_list:
        try:
            cb.on_train_start(state)
        except Exception as e:  # noqa: BLE001
            cb.record_error("on_train_start", e, state)
            logger.warning("Callback on_train_start error: %s", e)

    # Persist config snapshot (if provided)
    if run_config and checkpoint_dir:
        try:
            ckpt_root = Path(checkpoint_dir)
            ckpt_root.mkdir(parents=True, exist_ok=True)
            (ckpt_root / "config.snapshot.json").write_text(
                json.dumps(run_config, indent=2, sort_keys=True)
            )
        except Exception as e:  # noqa: BLE001
            logger.warning("Failed to write config snapshot: %s", e)

    start_epoch = 1
    resume_meta = {}
    if resume and checkpoint_dir:
        start_epoch, resume_meta = _attempt_resume(
            model,
            optimizer,
            scheduler,
            checkpoint_dir,
        )

    latest_payload: Dict[str, Any] | None = None
    best_k_index: Optional[int] = None
    if retention_policy:
        for key in ("keep_best_k", "keep_best"):
            if key in retention_policy:
                try:
                    candidate = int(retention_policy[key])  # type: ignore[index]
                except (TypeError, ValueError):
                    continue
                if candidate > 0:
                    best_k_index = candidate
                    break

    def _persist_artifacts(best_checkpoint: Dict[str, Any] | None, completed_epochs: int) -> None:
        if art_dir_path is None:
            return

        metrics_entries: List[Dict[str, Any]] = []
        history = state.get("epoch_history")
        if isinstance(history, list):
            for entry in history:
                metrics_entry: Dict[str, Any] = {"phase": "epoch_end"}
                if isinstance(entry, dict):
                    metrics_entry.update(entry)
                metrics_entries.append(metrics_entry)

        best_entry: Dict[str, Any] = {"phase": "best_checkpoint"}
        if best_checkpoint:
            best_entry.update(best_checkpoint)
        else:
            best_entry["epoch"] = completed_epochs
        metrics_entries.append(best_entry)

        try:
            (art_dir_path / "metrics.json").write_text(json.dumps(metrics_entries, indent=2))
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to write metrics.json: %s", exc)

        env_payload: Dict[str, Any] = {
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
        if batch_size is not None:
            env_payload["batch_size"] = batch_size
        if _HAS_TORCH and torch is not None:
            env_payload["torch_version"] = torch.__version__

        try:
            (art_dir_path / "environment.json").write_text(json.dumps(env_payload, indent=2))
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to write environment.json: %s", exc)

        try:
            (art_dir_path / "dataset_checksums.json").write_text(
                json.dumps(dataset_checksum_map, indent=2)
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to write dataset_checksums.json: %s", exc)

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
        _persist_artifacts(resume_meta if resume_meta else None, target_epochs)
        if return_state:
            result["model"] = model
            result["optimizer"] = optimizer
            result["scheduler"] = scheduler
            result["state"] = state
        return result

    total_optimizer_steps = 0
    total_steps = 0
    learning_rate_history: List[List[float]] = []
    last_checkpoint_sha = None

    for epoch in range(start_epoch, target_epochs + 1):
        epoch_checkpoint_sha = None
        for cb in cb_list:
            try:
                cb.on_epoch_start(epoch, state)
            except Exception as e:  # noqa: BLE001
                cb.record_error("on_epoch_start", e, state)
                logger.warning("Callback on_epoch_start error: %s", e)

        epoch_loss_accum = 0.0
        synthetic_losses: List[float] = []
        steps_this_epoch = 0
        optimizer_steps_this_epoch = 0

        if model is not None and optimizer is not None and _HAS_TORCH:
            if dtype_obj is not None:
                try:
                    model.to(dtype=dtype_obj)
                except Exception:  # noqa: BLE001
                    pass
            model.to(device_obj)
            model.train()
            optimizer.zero_grad(set_to_none=True)

            for step in range(steps_per_epoch):
                steps_this_epoch += 1
                total_steps += 1
                loss_val = _synthetic_step(model)
                epoch_loss_accum += loss_val
                synthetic_losses.append(loss_val)
                if (step + 1) % grad_accum == 0:
                    try:
                        optimizer.step()
                        optimizer.zero_grad(set_to_none=True)
                        optimizer_steps_this_epoch += 1
                        total_optimizer_steps += 1
                    except Exception as e:  # noqa: BLE001
                        logger.warning("Optimizer step failed: %s", e)

            if steps_per_epoch % grad_accum != 0:
                try:
                    optimizer.step()
                    optimizer.zero_grad(set_to_none=True)
                    optimizer_steps_this_epoch += 1
                    total_optimizer_steps += 1
                except Exception as e:  # noqa: BLE001
                    logger.warning("Final optimizer step failed: %s", e)
        else:
            steps_this_epoch = steps_per_epoch
            total_steps += steps_per_epoch

        avg_loss = None
        if synthetic_losses:
            avg_loss = epoch_loss_accum / max(len(synthetic_losses), 1)

        if scheduler is not None and optimizer is not None:
            try:
                scheduler.step()
            except Exception as e:  # noqa: BLE001
                logger.warning("Scheduler step failed: %s", e)
            current_lrs = _scheduler_current_lr(scheduler, optimizer)
        else:
            current_lrs = _scheduler_current_lr(None, optimizer)

        learning_rate_history.append(current_lrs or [])

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
                cb.record_error("merge_callback_results", merge_exc, state)
                logger.warning("Callback merge error: %s", merge_exc)
            except Exception as e:  # noqa: BLE001
                cb.record_error("on_epoch_end", e, state)
                logger.warning("Callback on_epoch_end error: %s", e)

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
                except Exception as e:  # noqa: BLE001
                    msg = "Failed to save checkpoint for epoch %d: %s"
                    logger.warning(msg, epoch, e)
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
            except Exception as e:  # noqa: BLE001
                logger.warning("Failed to write latest.json: %s", e)

            # Retention pruning
            if retention_policy:
                try:
                    prune_result = prune_checkpoints(checkpoint_dir, **retention_policy)
                    state["retention_last"] = prune_result
                except Exception as e:  # noqa: BLE001
                    logger.warning("Retention pruning failed: %s", e)
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

    for cb in cb_list:
        try:
            cb.on_train_end(state)
        except Exception as e:  # noqa: BLE001
            cb.record_error("on_train_end", e, state)
            logger.warning("Callback on_train_end error: %s", e)

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
    }
    if resume_meta:
        result["resume_meta"] = resume_meta

    _persist_artifacts(latest_payload, target_epochs)

    if return_state:
        result["model"] = model
        result["optimizer"] = optimizer
        result["scheduler"] = scheduler
        result["state"] = state

    return result


__all__ = ["run_training"]
