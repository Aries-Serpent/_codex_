from __future__ import annotations

import contextlib
import importlib.util
import json
import logging
import math
import types
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter
from typing import Any, Dict, List, Mapping, Optional, Tuple

from codex_ml.data.jsonl_loader import load_jsonl
from codex_ml.data.split_utils import split_dataset
from codex_ml.logging.file_logger import FileLogger
from codex_ml.logging.run_metadata import log_run_metadata
from codex_ml.metrics.evaluator import batch_metrics
from codex_ml.models.utils.peft import apply_lora_if_available
from codex_ml.registry.tokenizers import encode_cached
from codex_ml.safety import (
    SafetyConfig,
    SafetyFilters,
    SafetyViolation,
    sanitize_prompt,
)
from codex_ml.training.dataloader_utils import make_generator, seed_worker
from codex_ml.training.eval import evaluate
from codex_ml.utils.checkpointing import load_training_checkpoint, save_checkpoint
from codex_ml.utils.error_log import log_error
from codex_ml.utils.hf_pinning import load_from_pretrained
from codex_ml.utils.hf_revision import get_hf_revision
from codex_ml.utils.provenance import export_environment
from codex_ml.utils.seeding import set_reproducible
from codex_ml.utils.train_helpers import maybe_autocast

logger = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency in tests
    from omegaconf import DictConfig, OmegaConf  # type: ignore
except Exception as exc:  # pragma: no cover - OmegaConf optional
    logger.debug("OmegaConf unavailable: %s", exc)
    DictConfig = None  # type: ignore[assignment]
    OmegaConf = None  # type: ignore[assignment]

try:  # pragma: no cover - guard should never raise fatally
    from codex_ml.tracking.mlflow_guard import (
        bootstrap_offline_tracking as _ensure_mlflow_file_backend,
    )
except Exception:  # pragma: no cover - guard import optional
    _ensure_mlflow_file_backend = None
else:
    try:
        _ensure_mlflow_file_backend()
    except Exception:  # pragma: no cover - best-effort
        logger.debug("MLflow guard initialization failed", exc_info=True)

__all__ = [
    "SafetySettings",
    "OptimizerSettings",
    "SchedulerSettings",
    "TrainingRunConfig",
    "run_functional_training",
    "build_dataloader",
]


@dataclass
class SafetySettings:
    enabled: bool = True
    policy_path: Optional[str] = None
    bypass: bool = False


@dataclass
class OptimizerSettings:
    name: str = "adamw_torch"
    weight_decay: float = 0.01
    betas: Tuple[float, float] = (0.9, 0.999)
    eps: float = 1e-8


@dataclass
class SchedulerSettings:
    name: str = "linear"
    warmup_steps: int = 0
    num_cycles: float = 1.0


@dataclass
class TrainingRunConfig:
    seed: int = 42
    deterministic: bool = True
    model: Any = "minilm"
    learning_rate: float = 0.0003
    batch_size: int = 32
    max_epochs: int = 5
    scheduler: SchedulerSettings = field(default_factory=SchedulerSettings)
    warmup_steps: int = 0
    gradient_accumulation: int = 1
    eval_every_epochs: int = 1
    tensorboard: bool = True
    mlflow_enable: bool = False
    mlflow_tracking_uri: Optional[str] = None
    amp_enable: bool = False
    amp_dtype: Optional[str] = None
    grad_clip_norm: Optional[float] = None
    lora_enable: bool = False
    lora_r: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    output_dir: str = "runs/default"
    checkpoint_dir: Optional[str] = None
    checkpoint_every_n_steps: int = 100
    resume_from: Optional[str] = None
    keep_last_n: Optional[int] = 5
    metrics_out: str = ".codex/metrics.ndjson"
    log_dir: str = "logs"
    log_formats: Tuple[str, ...] = ("ndjson",)
    log_system_metrics: bool = False
    system_metrics_interval: float = 60.0
    system_metrics_path: Optional[str] = None
    optimizer: OptimizerSettings = field(default_factory=OptimizerSettings)
    dataset: Dict[str, Any] = field(
        default_factory=lambda: {
            "train_path": "data/train_samples.jsonl",
            "eval_path": None,
            "format": "jsonl",
            "train_texts": [],
            "eval_texts": [],
        }
    )
    safety: SafetySettings = field(default_factory=SafetySettings)
    num_workers: int = 0
    pin_memory: bool = False
    padding: bool | str = True
    truncation: bool = True
    max_length: int | None = None


_OPTIONAL_TELEMETRY_MODULES = ("psutil", "pynvml", "wandb", "mlflow")


def _collect_system_metrics(enabled: bool) -> Dict[str, float]:
    if not enabled:
        return {}
    try:
        from codex_ml.utils.system_metrics import collect_metrics
    except Exception:  # pragma: no cover - optional dependency chain missing
        logger.debug("system metrics collector unavailable", exc_info=True)
        return {}
    try:
        return collect_metrics()
    except Exception:  # pragma: no cover - runtime errors best effort
        logger.debug("system metrics collection failed", exc_info=True)
        return {}


def _log_optional_dependencies() -> list[str]:
    missing: list[str] = []
    for name in _OPTIONAL_TELEMETRY_MODULES:
        if importlib.util.find_spec(name) is None:
            missing.append(name)
    if missing:
        logger.warning(
            "[telemetry] Optional packages not installed: %s",
            ", ".join(sorted(set(missing))),
        )
    return missing


def _listify_texts(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    try:
        return [str(item) for item in list(value)]
    except TypeError:
        return [str(value)]


def _load_texts(path: str | None, fmt: str = "text") -> List[str]:
    if not path:
        return []
    target = Path(path)
    if not target.exists():
        return []
    fmt_lower = fmt.lower()
    texts: List[str] = []
    if fmt_lower == "jsonl":
        for line in target.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                texts.append(line)
                continue
            if isinstance(item, dict) and "text" in item:
                texts.append(str(item["text"]))
            elif isinstance(item, str):
                texts.append(item)
            else:
                texts.append(line if isinstance(item, (int, float)) else json.dumps(item))
        return texts
    for line in target.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            texts.append(line)
    return texts


def _coerce_safety(raw: Any, default: Optional[SafetySettings] = None) -> SafetySettings:
    base = default or SafetySettings()
    if isinstance(raw, SafetySettings):
        return raw
    if not isinstance(raw, Mapping):
        return SafetySettings(base.enabled, base.policy_path, base.bypass)
    policy = raw.get("policy_path") or raw.get("policy")
    policy_path = str(policy) if policy not in (None, "") else base.policy_path
    return SafetySettings(
        enabled=bool(raw.get("enabled", base.enabled)),
        policy_path=policy_path,
        bypass=bool(raw.get("bypass", base.bypass)),
    )


def _normalize_config(raw: Mapping[str, Any]) -> Dict[str, Any]:
    if DictConfig is not None and isinstance(raw, DictConfig):  # type: ignore[arg-type]
        container = OmegaConf.to_container(raw, resolve=True)  # type: ignore[union-attr]
        if isinstance(container, dict):
            return container
        raise TypeError("DictConfig did not resolve to a mapping container")
    if isinstance(raw, Mapping):
        return dict(raw)
    raise TypeError("config must be a mapping or DictConfig")


def _merge_dataset_config(dataset: Dict[str, Any], mapping: Mapping[str, Any]) -> None:
    dataset.update({k: v for k, v in mapping.items() if v is not None})
    if "texts" in mapping:
        dataset["train_texts"] = _listify_texts(mapping["texts"])
    if "train_texts" in mapping:
        dataset["train_texts"] = _listify_texts(mapping["train_texts"])
    if "val_texts" in mapping:
        dataset["eval_texts"] = _listify_texts(mapping["val_texts"])
    if "eval_texts" in mapping:
        dataset["eval_texts"] = _listify_texts(mapping["eval_texts"])


def _maybe_resolve_container(value: Any) -> Any:
    """Resolve DictConfig objects into plain Python containers when possible."""

    if DictConfig is not None and isinstance(value, DictConfig):  # type: ignore[arg-type]
        resolved = OmegaConf.to_container(value, resolve=True)  # type: ignore[union-attr]
        return resolved
    return value


def _coerce_optimizer(raw: Any, default: OptimizerSettings) -> OptimizerSettings:
    if isinstance(raw, OptimizerSettings):
        return raw
    if isinstance(raw, Mapping):
        name = str(raw.get("name", default.name) or default.name)
        weight_decay = float(raw.get("weight_decay", default.weight_decay))
        betas_val = raw.get("betas", default.betas)
        beta1, beta2 = default.betas
        if isinstance(betas_val, (list, tuple)) and len(betas_val) >= 2:
            try:
                beta1 = float(betas_val[0])
                beta2 = float(betas_val[1])
            except (TypeError, ValueError):
                beta1, beta2 = default.betas
        eps = float(raw.get("eps", default.eps))
        return OptimizerSettings(
            name=name, weight_decay=weight_decay, betas=(beta1, beta2), eps=eps
        )
    if isinstance(raw, str) and raw:
        return OptimizerSettings(
            name=raw,
            weight_decay=default.weight_decay,
            betas=default.betas,
            eps=default.eps,
        )
    return OptimizerSettings(default.name, default.weight_decay, default.betas, default.eps)


def _coerce_scheduler(raw: Any, default: SchedulerSettings) -> SchedulerSettings:
    if isinstance(raw, SchedulerSettings):
        return raw
    if isinstance(raw, Mapping):
        name = str(raw.get("name", default.name) or default.name)
        warmup_val = raw.get("warmup_steps", raw.get("warmup", default.warmup_steps))
        num_cycles_val = raw.get("num_cycles", default.num_cycles)
        try:
            warmup_steps = int(warmup_val) if warmup_val is not None else default.warmup_steps
        except (TypeError, ValueError):
            warmup_steps = default.warmup_steps
        try:
            num_cycles = float(num_cycles_val) if num_cycles_val is not None else default.num_cycles
        except (TypeError, ValueError):
            num_cycles = default.num_cycles
        return SchedulerSettings(name=name, warmup_steps=warmup_steps, num_cycles=num_cycles)
    if isinstance(raw, str) and raw:
        return SchedulerSettings(
            name=raw, warmup_steps=default.warmup_steps, num_cycles=default.num_cycles
        )
    return SchedulerSettings(default.name, default.warmup_steps, default.num_cycles)


def _coerce_model_entry(value: Any, default: Any) -> Any:
    entry = value if value is not None else default
    entry = _maybe_resolve_container(entry)
    if isinstance(entry, Mapping):
        return dict(entry)
    if isinstance(entry, str):
        return entry
    return str(entry)


def _model_name_from_value(value: Any, default: str = "MiniLM") -> str:
    entry = _maybe_resolve_container(value)
    if isinstance(entry, Mapping):
        candidate = entry.get("name")
        if isinstance(candidate, str) and candidate:
            return candidate
    if isinstance(entry, str) and entry:
        return entry
    return default


def _normalize_model_config(value: Any, fallback_name: str = "MiniLM") -> Dict[str, Any]:
    entry = _maybe_resolve_container(value)
    if isinstance(entry, Mapping):
        cfg = dict(entry)
    elif isinstance(entry, str) and entry:
        cfg = {"name": entry}
    else:
        cfg = {}
    name = cfg.get("name")
    if not isinstance(name, str) or not name:
        cfg["name"] = fallback_name or "MiniLM"
    return cfg


def _find_latest_checkpoint(directory: Path) -> Optional[Path]:
    """Return the most recent checkpoint file within ``directory`` if present."""

    if not directory.exists():
        return None

    marker = directory / "last"
    with contextlib.suppress(Exception):
        text = marker.read_text(encoding="utf-8").strip()
        if text:
            target = Path(text)
            if not target.is_absolute():
                target = directory / text
            if target.exists():
                return target

    step_candidates = sorted(
        {
            candidate
            for pattern in ("step*.ptz", "step*.pt")
            for candidate in directory.glob(pattern)
            if candidate.is_file()
        },
        key=lambda path: path.stat().st_mtime,
    )
    if step_candidates:
        return step_candidates[-1]

    generic = sorted(
        {
            candidate
            for pattern in ("*.ptz", "*.pt")
            for candidate in directory.glob(pattern)
            if candidate.is_file()
        },
        key=lambda path: path.stat().st_mtime,
    )
    if generic:
        return generic[-1]

    return None


def _checkpoint_sidecars(path: Path) -> tuple[Path, ...]:
    meta = path.with_suffix(".meta.json")
    return (meta,)


def _prune_checkpoint_files(directory: Path, pattern: str, keep_last: Optional[int]) -> None:
    if keep_last is None or keep_last <= 0:
        return
    candidates = [p for p in directory.glob(pattern) if p.is_file()]
    if len(candidates) <= keep_last:
        return
    candidates.sort(key=lambda item: item.stat().st_mtime)
    for stale in candidates[:-keep_last]:
        with contextlib.suppress(FileNotFoundError):
            stale.unlink()
        for sidecar in _checkpoint_sidecars(stale):
            with contextlib.suppress(FileNotFoundError):
                sidecar.unlink()


def _resolve_system_metrics_path(cfg: TrainingRunConfig, base_dir: Path) -> Optional[Path]:
    path_value = getattr(cfg, "system_metrics_path", None)
    if isinstance(path_value, str) and path_value.strip():
        target = Path(path_value.strip())
        if not target.is_absolute():
            return base_dir / target
        return target
    return base_dir / "system_metrics.ndjson"


def _start_system_metrics_logger(path: Path, interval: float):
    try:
        from codex_ml.monitoring.system_metrics import SystemMetricsLogger
    except Exception:
        return None

    try:
        logger = SystemMetricsLogger(path, interval=max(0.5, float(interval)))
    except Exception:
        return None

    try:
        logger.start()
    except Exception:
        return None
    return logger


def _stop_system_metrics_logger(logger: Any) -> None:
    if logger is None:
        return
    stopper = getattr(logger, "stop", None)
    if callable(stopper):
        try:
            stopper()
        except Exception:
            pass


def _coerce_config(raw: Mapping[str, Any]) -> TrainingRunConfig:
    mapping = _normalize_config(raw)
    base = TrainingRunConfig()

    dataset_cfg = dict(base.dataset)
    dataset_cfg["train_texts"] = list(dataset_cfg.get("train_texts", []))
    dataset_cfg["eval_texts"] = list(dataset_cfg.get("eval_texts", []))

    maybe_dataset = mapping.get("dataset", {})
    if isinstance(maybe_dataset, Mapping):
        _merge_dataset_config(dataset_cfg, maybe_dataset)

    training_section = mapping.get("training", {})
    if isinstance(training_section, Mapping):
        _merge_dataset_config(dataset_cfg, training_section)
        nested_dataset = training_section.get("dataset")
        if isinstance(nested_dataset, Mapping):
            _merge_dataset_config(dataset_cfg, nested_dataset)
    else:
        training_section = {}

    safety_mapping: Any = mapping.get("safety")
    if isinstance(training_section, Mapping) and training_section.get("safety") is not None:
        safety_mapping = training_section.get("safety")
    safety_cfg = _coerce_safety(safety_mapping, base.safety)

    def _scalar(default: Any, *keys: str) -> Any:
        for key in keys:
            if key in mapping and mapping[key] is not None:
                return mapping[key]
        if isinstance(training_section, Mapping):
            for key in keys:
                if key in training_section and training_section[key] is not None:
                    return training_section[key]
        return default

    def _coerce_bool_value(raw: Any, default: bool) -> bool:
        if isinstance(raw, bool):
            return raw
        if raw is None:
            return default
        if isinstance(raw, str):
            lowered = raw.strip().lower()
            if lowered in {"true", "1", "yes", "y", "on"}:
                return True
            if lowered in {"false", "0", "no", "n", "off"}:
                return False
        try:
            return bool(int(raw))  # type: ignore[arg-type]
        except Exception:
            return bool(raw)

    checkpoint_dir = _scalar(None, "checkpoint_dir")
    checkpoint_every_value: Any = _scalar(
        base.checkpoint_every_n_steps, "checkpoint_every_n_steps", "save_every"
    )
    checkpoint_section: Mapping[str, Any] | None = None
    maybe_checkpoint = mapping.get("checkpoint")
    if isinstance(maybe_checkpoint, Mapping):
        checkpoint_section = maybe_checkpoint
    if isinstance(training_section, Mapping):
        if checkpoint_dir is None:
            checkpoint_dir = training_section.get("checkpoint_dir")
        nested_checkpoint = training_section.get("checkpoint")
        if isinstance(nested_checkpoint, Mapping):
            checkpoint_section = nested_checkpoint
    if isinstance(checkpoint_section, Mapping):
        if checkpoint_dir is None and checkpoint_section.get("dir") is not None:
            checkpoint_dir = checkpoint_section.get("dir")
        if checkpoint_section.get("every_n_steps") is not None:
            checkpoint_every_value = checkpoint_section.get("every_n_steps")

    tensorboard_value = _scalar(base.tensorboard, "tensorboard")
    mlflow_value = _scalar(base.mlflow_enable, "mlflow_enable")
    mlflow_uri_value = _scalar(base.mlflow_tracking_uri, "mlflow_tracking_uri", "mlflow_uri")

    amp_raw = _scalar(base.amp_enable, "amp_enable", "amp")
    amp_enable = _coerce_bool_value(amp_raw, base.amp_enable)
    amp_dtype_raw = _scalar(base.amp_dtype, "amp_dtype")
    amp_dtype_value = str(amp_dtype_raw) if amp_dtype_raw not in (None, "") else None
    grad_clip_raw = _scalar(base.grad_clip_norm, "grad_clip_norm", "max_grad_norm")
    try:
        grad_clip_value = float(grad_clip_raw) if grad_clip_raw is not None else None
    except (TypeError, ValueError):
        grad_clip_value = base.grad_clip_norm

    eval_every_raw = _scalar(base.eval_every_epochs, "eval_every_epochs", "eval_every")
    try:
        eval_every_value = int(eval_every_raw)
    except (TypeError, ValueError):
        eval_every_value = base.eval_every_epochs

    metrics_out_raw = _scalar(base.metrics_out, "metrics_out", "metrics_path")
    metrics_out_value = (
        str(metrics_out_raw) if metrics_out_raw not in (None, "") else base.metrics_out
    )

    lora_enable = _coerce_bool_value(_scalar(None, "lora_enable"), base.lora_enable)
    lora_r_value = base.lora_r
    lora_alpha_value = base.lora_alpha
    lora_dropout_value = base.lora_dropout

    raw_lora_r = _scalar(None, "lora_r")
    if raw_lora_r is not None:
        try:
            lora_r_value = int(raw_lora_r)
        except (TypeError, ValueError):
            lora_r_value = base.lora_r

    raw_lora_alpha = _scalar(None, "lora_alpha")
    if raw_lora_alpha is not None:
        try:
            lora_alpha_value = int(raw_lora_alpha)
        except (TypeError, ValueError):
            lora_alpha_value = base.lora_alpha

    raw_lora_dropout = _scalar(None, "lora_dropout")
    if raw_lora_dropout is not None:
        try:
            lora_dropout_value = float(raw_lora_dropout)
        except (TypeError, ValueError):
            lora_dropout_value = base.lora_dropout

    lora_section: Mapping[str, Any] | None = None
    maybe_lora = mapping.get("lora")
    if isinstance(maybe_lora, Mapping):
        lora_section = maybe_lora
    if isinstance(training_section, Mapping):
        nested_lora = training_section.get("lora")
        if isinstance(nested_lora, Mapping):
            lora_section = nested_lora
    if isinstance(lora_section, Mapping):
        if lora_section.get("enable") is not None:
            lora_enable = _coerce_bool_value(lora_section.get("enable"), lora_enable)
        if lora_section.get("r") is not None:
            try:
                lora_r_value = int(lora_section.get("r"))
            except (TypeError, ValueError):
                lora_r_value = base.lora_r
        if lora_section.get("alpha") is not None:
            try:
                lora_alpha_value = int(lora_section.get("alpha"))
            except (TypeError, ValueError):
                lora_alpha_value = base.lora_alpha
        if lora_section.get("dropout") is not None:
            try:
                lora_dropout_value = float(lora_section.get("dropout"))
            except (TypeError, ValueError):
                lora_dropout_value = base.lora_dropout

    model_value = _coerce_model_entry(_scalar(base.model, "model"), base.model)

    optimizer_raw = _scalar(base.optimizer, "optimizer")
    scheduler_raw = _scalar(base.scheduler, "scheduler")
    warmup_override = _scalar(None, "warmup_steps")

    optimizer_cfg = _coerce_optimizer(optimizer_raw, base.optimizer)
    scheduler_cfg = _coerce_scheduler(scheduler_raw, base.scheduler)
    if warmup_override is not None:
        try:
            warmup_value = int(warmup_override)
            scheduler_cfg = SchedulerSettings(
                name=scheduler_cfg.name,
                warmup_steps=warmup_value,
                num_cycles=scheduler_cfg.num_cycles,
            )
        except (TypeError, ValueError):
            warmup_value = scheduler_cfg.warmup_steps
    else:
        warmup_value = scheduler_cfg.warmup_steps

    log_system_metrics = _coerce_bool_value(
        _scalar(base.log_system_metrics, "log_system_metrics", "system_metrics_logging"),
        base.log_system_metrics,
    )

    sys_interval_raw = _scalar(base.system_metrics_interval, "system_metrics_interval")
    try:
        system_metrics_interval = float(sys_interval_raw)
    except (TypeError, ValueError):
        system_metrics_interval = base.system_metrics_interval

    sys_path_raw = _scalar(base.system_metrics_path, "system_metrics_path")
    system_metrics_path = None
    if isinstance(sys_path_raw, str) and sys_path_raw.strip():
        system_metrics_path = sys_path_raw.strip()

    keep_last_raw = _scalar(base.keep_last_n, "keep_last_n", "keep_last")
    try:
        keep_last_n = int(keep_last_raw) if keep_last_raw is not None else base.keep_last_n
    except (TypeError, ValueError):
        keep_last_n = base.keep_last_n
    if keep_last_n is not None and keep_last_n <= 0:
        keep_last_n = None

    return TrainingRunConfig(
        seed=int(_scalar(base.seed, "seed")),
        model=model_value,
        learning_rate=float(_scalar(base.learning_rate, "learning_rate", "lr")),
        batch_size=int(_scalar(base.batch_size, "batch_size")),
        max_epochs=int(_scalar(base.max_epochs, "max_epochs", "epochs")),
        scheduler=scheduler_cfg,
        warmup_steps=int(warmup_value),
        gradient_accumulation=int(
            _scalar(base.gradient_accumulation, "gradient_accumulation", "grad_accum")
        ),
        tensorboard=(
            tensorboard_value if isinstance(tensorboard_value, bool) else bool(tensorboard_value)
        ),
        mlflow_enable=(mlflow_value if isinstance(mlflow_value, bool) else bool(mlflow_value)),
        mlflow_tracking_uri=(str(mlflow_uri_value) if mlflow_uri_value not in (None, "") else None),
        amp_enable=amp_enable,
        amp_dtype=amp_dtype_value,
        grad_clip_norm=grad_clip_value,
        eval_every_epochs=int(eval_every_value),
        lora_enable=lora_enable,
        lora_r=int(lora_r_value),
        lora_alpha=int(lora_alpha_value),
        lora_dropout=float(lora_dropout_value),
        output_dir=str(_scalar(base.output_dir, "output_dir")),
        checkpoint_dir=str(checkpoint_dir) if checkpoint_dir else None,
        checkpoint_every_n_steps=int(checkpoint_every_value),
        metrics_out=str(metrics_out_value),
        log_system_metrics=log_system_metrics,
        system_metrics_interval=system_metrics_interval,
        system_metrics_path=system_metrics_path,
        optimizer=optimizer_cfg,
        dataset=dataset_cfg,
        safety=safety_cfg,
        keep_last_n=keep_last_n,
    )


def run_functional_training(
    config: Mapping[str, Any] | TrainingRunConfig, *, resume: bool = False
) -> Dict[str, Any]:
    """Run the Codex functional training loop with optional resume support."""

    missing_optional = _log_optional_dependencies()
    normalized_mapping: Dict[str, Any] | None = None
    training_mapping: Mapping[str, Any] | None = None
    if isinstance(config, TrainingRunConfig):
        cfg = config
    else:
        normalized_mapping = _normalize_config(config)
        cfg = _coerce_config(normalized_mapping)
        maybe_training = normalized_mapping.get("training") if normalized_mapping else None
        if isinstance(maybe_training, Mapping):
            training_mapping = maybe_training

    deterministic_flag = bool(getattr(cfg, "deterministic", True))
    set_reproducible(cfg.seed, deterministic=deterministic_flag)

    dataset_cfg = cfg.dataset or {}
    dataset_format = str(dataset_cfg.get("format", "text")).lower()
    val_fraction = float(
        dataset_cfg.get("val_fraction") or dataset_cfg.get("validation_fraction") or 0.0
    )
    split_ratio = dataset_cfg.get("split_ratio") or dataset_cfg.get("split_ratios")

    train_texts = _listify_texts(dataset_cfg.get("train_texts"))
    if not train_texts:
        train_texts = _listify_texts(dataset_cfg.get("texts"))

    val_texts = _listify_texts(dataset_cfg.get("eval_texts"))
    if not val_texts:
        val_texts = _listify_texts(dataset_cfg.get("val_texts"))

    train_path = dataset_cfg.get("train_path")
    eval_path = dataset_cfg.get("eval_path")

    if split_ratio:
        if dataset_format != "jsonl":
            raise ValueError("dataset.split_ratio currently supports only JSONL datasets")
        base_source = (
            dataset_cfg.get("dataset_path")
            or dataset_cfg.get("path")
            or dataset_cfg.get("data_path")
            or train_path
        )
        if not base_source:
            raise ValueError("dataset.split_ratio requires a dataset 'path' or 'train_path'")
        try:
            ratios_tuple = tuple(float(x) for x in split_ratio)
        except TypeError as exc:  # pragma: no cover - invalid ratio specification
            raise ValueError("dataset.split_ratio must be an iterable of three floats") from exc
        split_paths = split_dataset(base_source, ratios_tuple, seed=cfg.seed)
        dataset_cfg["train_path"] = str(split_paths.train)
        dataset_cfg.setdefault("eval_path", str(split_paths.val))
        dataset_cfg.setdefault("test_path", str(split_paths.test))
        train_path = dataset_cfg["train_path"]
        eval_path = dataset_cfg.get("eval_path")

    if train_path:
        if dataset_format == "jsonl":
            auto_train, auto_val = load_jsonl(
                train_path,
                seed=cfg.seed,
                val_fraction=val_fraction,
            )
            if auto_train:
                train_texts.extend(auto_train)
            else:
                train_texts.extend(_load_texts(train_path, "jsonl"))
            if not val_texts and not eval_path and auto_val:
                val_texts.extend(auto_val)
        else:
            train_texts.extend(_load_texts(train_path, dataset_format))

    if eval_path:
        if dataset_format == "jsonl":
            _, eval_auto = load_jsonl(eval_path, seed=cfg.seed, val_fraction=0.0)
            if eval_auto:
                val_texts.extend(eval_auto)
            else:
                val_texts.extend(_load_texts(eval_path, "jsonl"))
        else:
            val_texts.extend(_load_texts(eval_path, dataset_format))

    if not train_texts:
        ctx = {"path": dataset_cfg.get("train_path"), "texts": len(train_texts)}
        log_error("train.dataset", "training dataset is empty or missing", json.dumps(ctx))
        raise ValueError("training dataset is empty or missing")

    raw_safety = cfg.safety
    safety_cfg = (
        raw_safety
        if isinstance(raw_safety, SafetySettings)
        else _coerce_safety(raw_safety, SafetySettings())
    )
    prompt_safety = SafetyConfig()
    safety_filters: SafetyFilters | None = None

    def _apply_safety(texts: List[str], stage: str) -> List[str]:
        nonlocal safety_filters
        if not texts:
            return []
        sanitized_items: List[str] = []
        for raw_text in texts:
            prompt_entry = sanitize_prompt(raw_text, prompt_safety)
            sanitized_text = prompt_entry.get("text", raw_text)
            if safety_cfg.enabled:
                safety_filters = safety_filters or SafetyFilters.from_policy_file(
                    safety_cfg.policy_path
                )
                try:
                    sanitized_text = safety_filters.enforce(
                        sanitized_text, stage=stage, bypass=safety_cfg.bypass
                    )
                except SafetyViolation as exc:
                    match_ids: list[str] = []
                    for match in exc.decision.matches:
                        if isinstance(match, dict):
                            rule_id = match.get("rule_id")
                        else:
                            rule_id = getattr(match, "rule_id", None)
                        if rule_id:
                            match_ids.append(rule_id)
                    context = json.dumps(
                        {
                            "stage": stage,
                            "matches": match_ids,
                            "policy": safety_cfg.policy_path,
                        }
                    )
                    log_error("train.safety", str(exc), context)
                    raise
            sanitized_items.append(sanitized_text)
        return sanitized_items

    train_texts = _apply_safety(train_texts, "prompt")
    if val_texts:
        val_texts = _apply_safety(val_texts, "eval")

    output_dir = Path(cfg.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    provenance_summary = export_environment(
        output_dir / "provenance",
        seed=cfg.seed,
        command="train",
        extras={"resume": bool(resume)},
    )

    checkpoint_candidate = (
        Path(cfg.checkpoint_dir) if cfg.checkpoint_dir else output_dir / "checkpoints"
    )
    if checkpoint_candidate.suffix:
        checkpoint_dir = checkpoint_candidate.parent
    else:
        checkpoint_dir = checkpoint_candidate
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    try:
        from datasets import Dataset  # type: ignore
        from transformers import AutoTokenizer  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependencies
        if isinstance(exc, ImportError):
            for module_name in ("datasets", "transformers"):
                if module_name not in missing_optional:
                    missing_optional.append(module_name)
        try:
            import torch
            from torch.utils.data import DataLoader
        except Exception:
            tokens = sum(len(text.split()) for text in train_texts)
            metrics = [
                {"epoch": epoch, "tokens": tokens, "loss": round(1.0 / (epoch + 1), 4)}
                for epoch in range(max(cfg.max_epochs, 1))
            ]
            return {"metrics": metrics, "checkpoint_dir": None, "resumed_from": None}

        pad_token = "<pad>"
        unk_token = "<unk>"

        def _encode_texts(
            texts: List[str], vocab: Dict[str, int], *, update: bool
        ) -> List[List[int]]:
            encoded: List[List[int]] = []
            for text in texts:
                pieces = [piece for piece in text.split() if piece]
                if not pieces:
                    pieces = [unk_token]
                indices: List[int] = []
                for piece in pieces:
                    if update:
                        if piece not in vocab:
                            vocab[piece] = len(vocab)
                        indices.append(vocab[piece])
                    else:
                        indices.append(vocab.get(piece, vocab[unk_token]))
                encoded.append(indices if indices else [vocab[unk_token]])
            return encoded

        vocab: Dict[str, int] = {pad_token: 0, unk_token: 1}
        train_sequences = _encode_texts(train_texts, vocab, update=True)
        val_sequences: List[List[int]] = []
        if val_texts:
            val_sequences = _encode_texts(val_texts, vocab, update=False)

        def _prepare_dataset(sequences: List[List[int]]) -> Dict[str, Any]:
            if not sequences:
                return {
                    "input_ids": torch.empty((0, 0), dtype=torch.long),
                    "attention_mask": torch.empty((0, 0), dtype=torch.long),
                    "labels": torch.empty((0, 0), dtype=torch.long),
                }
            max_len = max(len(seq) for seq in sequences)
            input_ids: List[List[int]] = []
            attention: List[List[int]] = []
            labels: List[List[int]] = []
            for seq in sequences:
                padded = seq + [vocab[pad_token]] * (max_len - len(seq))
                mask = [1] * len(seq) + [0] * (max_len - len(seq))
                label_row = [tok if mask[idx] else -100 for idx, tok in enumerate(padded)]
                input_ids.append(padded)
                attention.append(mask)
                labels.append(label_row)
            return {
                "input_ids": torch.tensor(input_ids, dtype=torch.long),
                "attention_mask": torch.tensor(attention, dtype=torch.long),
                "labels": torch.tensor(labels, dtype=torch.long),
            }

        class _TinyLanguageModel(torch.nn.Module):
            def __init__(self, vocab_size: int, hidden_size: int = 32) -> None:
                super().__init__()
                self.embed = torch.nn.Embedding(vocab_size, hidden_size)
                self.lm_head = torch.nn.Linear(hidden_size, vocab_size)
                self.loss_fn = torch.nn.CrossEntropyLoss(ignore_index=-100)

            def forward(
                self,
                input_ids: torch.Tensor,
                attention_mask: Optional[torch.Tensor] = None,
                labels: Optional[torch.Tensor] = None,
            ) -> Any:
                logits = self.lm_head(self.embed(input_ids))
                loss: Optional[torch.Tensor] = None
                if labels is not None:
                    loss = self.loss_fn(logits.view(-1, logits.size(-1)), labels.view(-1))
                output = types.SimpleNamespace(logits=logits)
                if loss is not None:
                    output.loss = loss
                return output

        train_data = _prepare_dataset(train_sequences)
        val_data = _prepare_dataset(val_sequences) if val_sequences else None

        class _DictDataset(torch.utils.data.Dataset):
            def __init__(self, mapping: Dict[str, torch.Tensor]) -> None:
                self._mapping = mapping

            def __len__(self) -> int:
                if not self._mapping:
                    return 0
                first = next(iter(self._mapping.values()))
                return int(first.shape[0]) if hasattr(first, "shape") else 0

            def __getitem__(self, index: int) -> Dict[str, torch.Tensor]:
                return {key: value[index] for key, value in self._mapping.items()}

        train_dataset = _DictDataset(train_data)
        val_dataset = _DictDataset(val_data) if val_data else None

        batch_size = max(int(cfg.batch_size), 1)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size) if val_dataset else None

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = _TinyLanguageModel(len(vocab)).to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=float(cfg.learning_rate))

        metrics: List[Dict[str, Any]] = []
        grad_accum = max(int(cfg.gradient_accumulation), 1)
        eval_every = max(int(cfg.eval_every_epochs), 1)

        log_formats = tuple(getattr(cfg, "log_formats", ("ndjson",)))
        metrics_target = Path(cfg.metrics_out)
        metrics_root = metrics_target.parent if str(metrics_target.parent) else Path(".")
        logger = FileLogger(
            root=metrics_root,
            formats=log_formats,
            filename_stem=metrics_target.stem,
        )

        def _safe_len(obj: Any) -> int | None:
            try:
                return int(len(obj))  # type: ignore[arg-type]
            except Exception:
                return None

        metadata_extras: Dict[str, Any] = {"log_formats": list(log_formats)}
        if isinstance(provenance_summary, Mapping):
            fingerprint = provenance_summary.get("hardware_fingerprint")
        else:
            fingerprint = None
        if fingerprint:
            metadata_extras["hardware_fingerprint"] = str(fingerprint)

        metadata_logger: Any = logger
        if "csv" in log_formats:
            ndjson_target = logger.paths().get("ndjson")

            class _NdjsonOnlyLogger:
                def __init__(self, target: Path) -> None:
                    self._target = target

                def log(self, row: Mapping[str, object]) -> None:
                    with self._target.open("a", encoding="utf-8") as handle:
                        handle.write(json.dumps(dict(row), ensure_ascii=False) + "\n")

            metadata_logger = (
                _NdjsonOnlyLogger(ndjson_target) if ndjson_target is not None else None
            )

        if metadata_logger is not None:
            log_run_metadata(
                metadata_logger,
                seed=cfg.seed,
                deterministic=deterministic_flag,
                resume=bool(resume or cfg.resume_from),
                dataset_format=dataset_format,
                dataset_source=(
                    dataset_cfg.get("train_path")
                    or dataset_cfg.get("path")
                    or dataset_cfg.get("data_path")
                ),
                train_examples=_safe_len(train_dataset),
                eval_examples=_safe_len(val_dataset) if val_dataset is not None else 0,
                missing_optional=missing_optional,
                extras=metadata_extras,
            )
        num_epochs = max(int(cfg.max_epochs), 1)
        num_batches = len(train_loader)
        system_logger = None
        system_metrics_base = checkpoint_dir if checkpoint_dir is not None else output_dir
        if getattr(cfg, "log_system_metrics", False):
            target = _resolve_system_metrics_path(cfg, system_metrics_base)
            if target is not None:
                system_logger = _start_system_metrics_logger(
                    target, float(getattr(cfg, "system_metrics_interval", 60.0))
                )
        try:
            for epoch in range(num_epochs):
                model.train()
                optimizer.zero_grad()
                total_loss = 0.0
                seen_batches = 0
                t0 = perf_counter()
                for step, batch in enumerate(train_loader):
                    prepared = {k: v.to(device) for k, v in batch.items()}
                    outputs = model(**prepared)
                    raw_loss = getattr(outputs, "loss", None)
                    if raw_loss is None:
                        continue
                    loss = raw_loss / grad_accum
                    loss.backward()
                    if (step + 1) % grad_accum == 0 or (step + 1) == num_batches:
                        optimizer.step()
                        optimizer.zero_grad()
                    total_loss += float(raw_loss.detach().cpu())
                    seen_batches += 1
                elapsed = perf_counter() - t0
                avg_loss = total_loss / max(seen_batches, 1)
                train_rec = {
                    "epoch": epoch + 1,
                    "train_loss": avg_loss,
                    "train_time_s": round(elapsed, 4),
                }
                logger.log({"phase": "train", **train_rec})
                metrics.append(train_rec)

                if val_loader is not None and (epoch + 1) % eval_every == 0:
                    eval_metrics = evaluate(
                        model,
                        val_loader,
                        loss_fn=lambda outputs, _: getattr(
                            outputs, "loss", torch.tensor(0.0, device=device)
                        ),
                        device=device,
                        metrics_fn=batch_metrics,
                    )
                    eval_rec = {"epoch": epoch + 1, **eval_metrics}
                    logger.log({"phase": "eval", **eval_rec})
                    metrics.append(eval_rec)

                if checkpoint_dir is not None:
                    ckpt_path = checkpoint_dir / f"epoch-{epoch + 1:04d}.ptz"
                    save_checkpoint(
                        ckpt_path,
                        model,
                        optimizer,
                        None,
                        epoch + 1,
                        {},
                    )
                    _prune_checkpoint_files(checkpoint_dir, "epoch-*.pt*", cfg.keep_last_n)
        finally:
            _stop_system_metrics_logger(system_logger)

        return {"metrics": metrics, "checkpoint_dir": None, "resumed_from": None}

    import numpy as np  # type: ignore

    from codex_ml.models.registry import get_model
    from training.functional_training import TrainCfg, run_custom_trainer

    def _lookup(*keys: str, default: Any = None) -> Any:
        for key in keys:
            if (
                isinstance(training_mapping, Mapping)
                and key in training_mapping
                and training_mapping[key] is not None
            ):
                return _maybe_resolve_container(training_mapping[key])
            if (
                normalized_mapping is not None
                and key in normalized_mapping
                and normalized_mapping[key] is not None
            ):
                return _maybe_resolve_container(normalized_mapping[key])
        return default

    model_entry = _lookup("model", default=cfg.model)
    fallback_name = _model_name_from_value(cfg.model)
    model_cfg = _normalize_model_config(model_entry, fallback_name)

    tokenizer_name = str(
        model_cfg.get("pretrained_model_name_or_path")
        or model_cfg.get("tokenizer_name")
        or model_cfg.get("name")
        or "sshleifer/tiny-gpt2"
    )
    tokenizer = load_from_pretrained(
        AutoTokenizer,
        tokenizer_name,
        revision=get_hf_revision(),
    )
    if getattr(tokenizer, "pad_token", None) is None:
        tokenizer.pad_token = tokenizer.eos_token

    pad_token_id = getattr(tokenizer, "pad_token_id", None)
    if pad_token_id is None:
        raise RuntimeError("Tokenizer must expose a pad_token_id after pad token assignment")

    try:  # pragma: no cover - optional collator dependency
        from transformers import DataCollatorWithPadding  # type: ignore

        data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
    except Exception as exc:  # pragma: no cover - optional path
        logger.debug("DataCollatorWithPadding unavailable: %s", exc)
        data_collator = None

    def _normalize_feature(seq: Any) -> list[int]:
        if isinstance(seq, (str, bytes, bytearray)):
            raise TypeError("Token sequences must be iterable containers of integers")
        if isinstance(seq, Mapping):
            raise TypeError("Nested mappings are not supported in tokenizer encodings")
        try:
            iterator = list(seq)  # type: ignore[arg-type]
        except TypeError as err:
            raise TypeError("Tokenizer encodings must be sequences") from err
        normalized: list[int] = []
        for item in iterator:
            try:
                normalized.append(int(item))
            except (TypeError, ValueError):
                normalized.append(item)
        return normalized

    def _pad_sequence(items: list[int], pad_value: int, target: int) -> list[int]:
        if len(items) >= target:
            return items[:target]
        padded = list(items)
        padded.extend([pad_value] * (target - len(items)))
        return padded

    def _collect_encodings(texts: List[str]) -> tuple[list[dict[str, list[int]]], int]:
        encodings: list[dict[str, list[int]]] = []
        longest = 0
        for raw in texts:
            encoding = encode_cached(
                tokenizer,
                raw,
                padding=cfg.padding,
                truncation=cfg.truncation,
                max_length=cfg.max_length,
            )
            features: dict[str, list[int]] = {}
            for key, value in encoding.items():
                if isinstance(value, (list, tuple)):
                    features[key] = _normalize_feature(value)
            ids = features.get("input_ids", [])
            if "attention_mask" not in features:
                features["attention_mask"] = [1] * len(ids)
            longest = max(longest, len(ids))
            encodings.append(features)
        return encodings, longest

    def _build_dataset(texts: List[str]) -> Dataset | None:
        if not texts:
            empty = {
                "input_ids": np.zeros((0, 0), dtype=np.int64),
                "attention_mask": np.zeros((0, 0), dtype=np.int64),
                "labels": np.zeros((0, 0), dtype=np.int64),
            }
            return Dataset.from_dict(empty)

        encodings, observed_max = _collect_encodings(texts)
        if not encodings:
            empty = {
                "input_ids": np.zeros((0, 0), dtype=np.int64),
                "attention_mask": np.zeros((0, 0), dtype=np.int64),
                "labels": np.zeros((0, 0), dtype=np.int64),
            }
            return Dataset.from_dict(empty)

        use_manual_padding = data_collator is None or bool(cfg.padding)
        pad_to = (
            cfg.max_length
            if cfg.max_length is not None
            else (observed_max if use_manual_padding else None)
        )

        if pad_to is None:
            records: list[dict[str, Any]] = []
            for record in encodings:
                ids = list(record.get("input_ids", []))
                mask = list(record.get("attention_mask", [1] * len(ids)))
                labels = [token if attn else -100 for token, attn in zip(ids, mask)]
                payload = {k: list(v) for k, v in record.items()}
                payload["input_ids"] = ids
                payload["attention_mask"] = mask
                payload["labels"] = labels
                records.append(payload)
            return Dataset.from_list(records)

        features: dict[str, list[list[int]]] = {}
        labels: list[list[int]] = []
        for record in encodings:
            ids = list(record.get("input_ids", []))
            mask = list(record.get("attention_mask", [1] * len(ids)))
            ids = _pad_sequence(ids, int(pad_token_id), int(pad_to))
            mask = _pad_sequence(mask, 0, int(pad_to))
            labels.append([token if attn else -100 for token, attn in zip(ids, mask)])
            features.setdefault("input_ids", []).append(ids)
            features.setdefault("attention_mask", []).append(mask)
            for key, value in record.items():
                if key in {"input_ids", "attention_mask"}:
                    continue
                seq = list(value)
                features.setdefault(key, []).append(_pad_sequence(seq, 0, int(pad_to)))

        arrays = {k: np.array(v, dtype=np.int64) for k, v in features.items()}
        arrays["labels"] = np.array(labels, dtype=np.int64)
        return Dataset.from_dict(arrays)

    train_ds = _build_dataset(list(train_texts))

    val_ds = _build_dataset(list(val_texts)) if val_texts else None

    model = get_model(model_cfg.get("name", fallback_name), model_cfg)

    train_kwargs: Dict[str, Any] = {}
    for field_name in TrainCfg.__dataclass_fields__:
        value = _lookup(field_name)
        if value is not None:
            train_kwargs[field_name] = value

    train_kwargs.setdefault("lr", cfg.learning_rate)
    train_kwargs.setdefault("batch_size", cfg.batch_size)
    train_kwargs.setdefault("epochs", cfg.max_epochs)
    train_kwargs.setdefault("grad_accum", cfg.gradient_accumulation)
    train_kwargs.setdefault("save_every", cfg.checkpoint_every_n_steps)
    train_kwargs.setdefault("warmup_steps", cfg.scheduler.warmup_steps)
    train_kwargs.setdefault("weight_decay", cfg.optimizer.weight_decay)
    train_kwargs.setdefault("seed", cfg.seed)
    train_kwargs.setdefault("mlflow_enable", bool(cfg.mlflow_enable))
    train_kwargs.setdefault("log_system_metrics", bool(cfg.log_system_metrics))
    if cfg.mlflow_tracking_uri and "mlflow_tracking_uri" not in train_kwargs:
        train_kwargs["mlflow_tracking_uri"] = cfg.mlflow_tracking_uri

    train_kwargs["lr"] = float(train_kwargs["lr"])
    train_kwargs["batch_size"] = int(train_kwargs["batch_size"])
    train_kwargs["epochs"] = int(train_kwargs["epochs"])
    train_kwargs["grad_accum"] = int(train_kwargs["grad_accum"])
    train_kwargs["save_every"] = int(train_kwargs["save_every"])
    train_kwargs["warmup_steps"] = int(train_kwargs["warmup_steps"])
    train_kwargs["weight_decay"] = float(train_kwargs["weight_decay"])
    train_kwargs["seed"] = int(train_kwargs["seed"])
    if train_kwargs.get("keep_last") is not None:
        try:
            train_kwargs["keep_last"] = int(train_kwargs["keep_last"])
        except (TypeError, ValueError):
            train_kwargs.pop("keep_last", None)
    train_kwargs["log_system_metrics"] = bool(train_kwargs.get("log_system_metrics", False))

    if cfg.grad_clip_norm is not None and "max_grad_norm" not in train_kwargs:
        try:
            train_kwargs["max_grad_norm"] = float(cfg.grad_clip_norm)
        except (TypeError, ValueError):
            pass

    if cfg.amp_enable and "dtype" not in train_kwargs:
        dtype_override: Optional[str]
        if isinstance(cfg.amp_dtype, str):
            lower = cfg.amp_dtype.strip().lower()
        else:
            lower = ""
        if lower in {"bf16", "bfloat16"}:
            dtype_override = "bf16"
        elif lower in {"fp16", "float16", "half"}:
            dtype_override = "fp16"
        else:
            dtype_override = "fp16"
        train_kwargs.setdefault("dtype", dtype_override)

    train_kwargs["checkpoint_dir"] = str(checkpoint_dir)
    if cfg.resume_from and "resume_from" not in train_kwargs:
        train_kwargs["resume_from"] = str(cfg.resume_from)

    lora_cfg = _lookup("lora")
    if isinstance(lora_cfg, Mapping):
        if "enable" in lora_cfg:
            train_kwargs["use_lora"] = bool(lora_cfg["enable"])
        if lora_cfg.get("r") is not None:
            train_kwargs["lora_r"] = int(lora_cfg["r"])
        if lora_cfg.get("alpha") is not None:
            train_kwargs["lora_alpha"] = int(lora_cfg["alpha"])
        if lora_cfg.get("dropout") is not None:
            train_kwargs["lora_dropout"] = float(lora_cfg["dropout"])

    lora_from_kwargs = bool(train_kwargs.get("use_lora"))
    if cfg.lora_enable and not lora_from_kwargs:
        model = apply_lora_if_available(
            model,
            r=cfg.lora_r,
            alpha=cfg.lora_alpha,
            dropout=cfg.lora_dropout,
        )
        train_kwargs.pop("use_lora", None)

    if cfg.lora_enable or lora_from_kwargs:
        train_kwargs.setdefault("lora_r", int(cfg.lora_r))
        train_kwargs.setdefault("lora_alpha", int(cfg.lora_alpha))
        train_kwargs.setdefault("lora_dropout", float(cfg.lora_dropout))

    keep_last_override = train_kwargs.pop("keep_last_n", None)

    if getattr(cfg, "log_system_metrics", False):
        train_kwargs.setdefault("log_system_metrics", True)
        interval = getattr(cfg, "system_metrics_interval", 60.0)
        try:
            train_kwargs.setdefault("system_metrics_interval", float(interval))
        except (TypeError, ValueError):
            pass
        system_path = getattr(cfg, "system_metrics_path", None)
        if isinstance(system_path, str) and system_path.strip():
            train_kwargs.setdefault("system_metrics_path", system_path.strip())

    keep_last = keep_last_override
    if keep_last is None:
        keep_last = getattr(cfg, "keep_last_n", None)
    try:
        parsed_keep_last = int(keep_last) if keep_last is not None else None
    except (TypeError, ValueError):
        parsed_keep_last = None
    if parsed_keep_last is not None and parsed_keep_last <= 0:
        parsed_keep_last = None
    if parsed_keep_last is not None:
        train_kwargs.setdefault("keep_last", parsed_keep_last)

    resume_path: Optional[Path] = None
    if resume:
        resume_value = train_kwargs.get("resume_from")
        if resume_value:
            candidate = Path(str(resume_value))
            if candidate.is_dir():
                resume_path = _find_latest_checkpoint(candidate)
            elif candidate.exists():
                resume_path = candidate
        if resume_path is None:
            resume_path = _find_latest_checkpoint(checkpoint_dir)
        if resume_path is not None:
            train_kwargs["resume_from"] = str(resume_path)
            with contextlib.suppress(Exception):
                load_training_checkpoint(str(resume_path))

    train_cfg = TrainCfg(**train_kwargs)
    result = run_custom_trainer(model, tokenizer, train_ds, val_ds, train_cfg)
    if val_ds is not None and isinstance(result, dict):
        eval_batch_raw = (
            train_kwargs.get("eval_batch_size") or train_kwargs.get("batch_size") or cfg.batch_size
        )
        try:
            eval_batch_size = int(eval_batch_raw)
        except (TypeError, ValueError):
            eval_batch_size = int(cfg.batch_size)
        eval_metrics = _evaluate_model(model, val_ds, batch_size=eval_batch_size, cfg=cfg)
        if eval_metrics:
            result.setdefault("metrics", {}).update(eval_metrics)
    if missing_optional:
        logger.info(
            "[telemetry] Optional packages not installed: %s",
            ", ".join(missing_optional),
        )
    else:
        logger.info("[telemetry] All optional monitoring dependencies available.")
    return result


def build_dataloader(dataset: Any, cfg: TrainingRunConfig | Mapping[str, Any]) -> Any:
    """Create a reproducible ``DataLoader`` when PyTorch is present.

    Returns ``iter(dataset)`` when torch is unavailable which keeps unit tests
    and minimal CPU environments operational albeit without shuffling.
    """

    try:
        from torch.utils.data import DataLoader
    except Exception:  # pragma: no cover - torch optional dependency
        return iter(dataset)

    def _lookup(key: str, default: Any) -> Any:
        if isinstance(cfg, Mapping):
            return cfg.get(key, default)
        return getattr(cfg, key, default)

    batch_size = int(_lookup("batch_size", 8))
    shuffle = bool(_lookup("shuffle", True))
    num_workers = int(_lookup("num_workers", 0))
    pin_memory = bool(_lookup("pin_memory", False))
    generator = make_generator(_lookup("seed", 42))

    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=pin_memory,
        worker_init_fn=seed_worker,
        generator=generator,
    )


def _evaluate_model(
    model: Any,
    dataset: Any,
    *,
    batch_size: int = 8,
    cfg: Optional[TrainingRunConfig] = None,
) -> Dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning validation loss/perplexity."""

    try:
        from torch.utils.data import DataLoader
    except Exception:  # pragma: no cover - torch optional
        return {}

    try:
        if len(dataset) == 0:  # type: ignore[arg-type]
            return {}
    except Exception:  # pragma: no cover - len may not be defined
        pass

    torch_dataset = dataset
    if hasattr(dataset, "with_format"):
        try:
            formatted = dataset.with_format("torch")
            if formatted is not None:
                torch_dataset = formatted
        except Exception:  # pragma: no cover - fallback to raw dataset
            pass

    loader = DataLoader(torch_dataset, batch_size=batch_size)

    device = getattr(model, "device", None)
    if device is None and hasattr(model, "parameters"):
        try:
            first_param = next(model.parameters())  # type: ignore[attr-defined]
        except StopIteration:
            first_param = None
        except Exception:  # pragma: no cover - non-module models
            first_param = None
        if first_param is not None:
            device = getattr(first_param, "device", None)

    autocast_enabled = bool(getattr(cfg, "amp_enable", False))
    autocast_dtype = getattr(cfg, "amp_dtype", None)

    class _EvalWrapper:
        def __init__(self, base):
            self._base = base

        @property
        def training(self) -> bool:
            return bool(getattr(self._base, "training", False))

        def eval(self):
            if hasattr(self._base, "eval"):
                self._base.eval()
            return self

        def train(self, mode: bool = True):
            if hasattr(self._base, "train"):
                self._base.train(mode)
            return self

        def __call__(self, *args, **kwargs):
            with maybe_autocast(enabled=autocast_enabled, dtype=autocast_dtype):
                return self._base(*args, **kwargs)

    def _loss_selector(outputs, _batch):
        if isinstance(outputs, dict):
            return outputs.get("loss")
        return getattr(outputs, "loss", None)

    device_arg = device if device is not None else "cpu"
    metrics = evaluate(
        _EvalWrapper(model),
        loader,
        loss_fn=_loss_selector,
        device=device_arg,
        metrics_fn=batch_metrics,
    )

    if not metrics:
        return {}

    result: Dict[str, float] = {}
    if "eval_loss" in metrics:
        result["val_loss"] = float(metrics["eval_loss"])
    if "perplexity" in metrics:
        result["val_perplexity"] = float(metrics["perplexity"])
    elif "val_loss" in result:
        try:
            result["val_perplexity"] = float(math.exp(result["val_loss"]))
        except OverflowError:
            result["val_perplexity"] = float("inf")
    if "token_accuracy" in metrics:
        result["val_token_accuracy"] = float(metrics["token_accuracy"])
    if "exact_match" in metrics:
        result["val_exact_match"] = float(metrics["exact_match"])
    if "f1" in metrics:
        result["val_f1"] = float(metrics["f1"])

    try:
        result.setdefault("num_batches", float(len(loader)))
    except TypeError:
        pass

    return result
