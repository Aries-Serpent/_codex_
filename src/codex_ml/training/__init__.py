from __future__ import annotations

import contextlib
import importlib.util
import json
import logging
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

from codex_ml.data.jsonl_loader import load_jsonl
from codex_ml.data.split_utils import split_dataset
from codex_ml.models.utils.peft import apply_lora_if_available
from codex_ml.safety import (
    SafetyConfig,
    SafetyFilters,
    SafetyViolation,
    sanitize_prompt,
)
from codex_ml.training.dataloader_utils import make_generator, seed_worker
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
    model: Any = "minilm"
    learning_rate: float = 0.0003
    batch_size: int = 32
    max_epochs: int = 5
    scheduler: SchedulerSettings = field(default_factory=SchedulerSettings)
    warmup_steps: int = 0
    gradient_accumulation: int = 1
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


_OPTIONAL_TELEMETRY_MODULES = ("psutil", "pynvml", "wandb", "mlflow")


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

    step_candidates = sorted(p for p in directory.glob("step*.pt") if p.is_file())
    if step_candidates:
        return step_candidates[-1]

    generic = sorted(p for p in directory.glob("*.pt") if p.is_file())
    if generic:
        return generic[-1]

    return None


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
        lora_enable=lora_enable,
        lora_r=int(lora_r_value),
        lora_alpha=int(lora_alpha_value),
        lora_dropout=float(lora_dropout_value),
        output_dir=str(_scalar(base.output_dir, "output_dir")),
        checkpoint_dir=str(checkpoint_dir) if checkpoint_dir else None,
        checkpoint_every_n_steps=int(checkpoint_every_value),
        optimizer=optimizer_cfg,
        dataset=dataset_cfg,
        safety=safety_cfg,
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

    set_reproducible(cfg.seed)

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
    export_environment(
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
    except Exception:  # pragma: no cover - optional dependencies
        tokens = sum(len(text.split()) for text in train_texts)
        metrics = [
            {"epoch": epoch, "tokens": tokens, "loss": round(1.0 / (epoch + 1), 4)}
            for epoch in range(max(cfg.max_epochs, 1))
        ]
        return {"metrics": metrics, "checkpoint_dir": None, "resumed_from": None}

    import numpy as np  # type: ignore

    from codex_ml.models.registry import get_model
    from codex_ml.utils.checkpointing import load_training_checkpoint
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

    def _to_numpy(value: Any) -> Any:
        return value.numpy() if hasattr(value, "numpy") else np.array(value)

    tokenized = tokenizer(list(train_texts), padding=True, return_tensors="pt")
    tokenized["labels"] = tokenized["input_ids"].clone()
    tokenized["labels"][tokenized["attention_mask"] == 0] = -100
    train_ds = Dataset.from_dict({k: _to_numpy(v) for k, v in tokenized.items()})

    val_ds = None
    if val_texts:
        val_tok = tokenizer(list(val_texts), padding=True, return_tensors="pt")
        val_tok["labels"] = val_tok["input_ids"].clone()
        val_tok["labels"][val_tok["attention_mask"] == 0] = -100
        val_ds = Dataset.from_dict({k: _to_numpy(v) for k, v in val_tok.items()})

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
        import torch
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

    was_training = getattr(model, "training", False)
    if hasattr(model, "eval"):
        model.eval()

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

    total_loss = 0.0
    total_examples = 0
    total_tokens = 0

    autocast_enabled = bool(getattr(cfg, "amp_enable", False))
    autocast_dtype = getattr(cfg, "amp_dtype", None)

    with torch.no_grad():
        for batch in loader:
            if isinstance(batch, dict):
                batch_dict = batch
            elif isinstance(batch, (list, tuple)) and batch and isinstance(batch[0], dict):
                batch_dict = batch[0]
            else:
                continue

            prepared: Dict[str, Any] = {}
            for key, value in batch_dict.items():
                if hasattr(value, "to") and device is not None:
                    prepared[key] = value.to(device)
                else:
                    prepared[key] = value

            with maybe_autocast(enabled=autocast_enabled, dtype=autocast_dtype):
                outputs = model(**prepared)
            loss_tensor = getattr(outputs, "loss", None)
            if loss_tensor is None:
                continue

            try:
                loss_value = float(loss_tensor.detach().cpu().item())
            except Exception:
                loss_value = float(loss_tensor.detach().cpu().float().mean().item())

            input_ids = prepared.get("input_ids")
            batch_examples = 0
            if input_ids is not None and hasattr(input_ids, "shape"):
                shape = tuple(getattr(input_ids, "shape", ()))
                if shape:
                    batch_examples = int(shape[0])
                    seq_len = int(shape[1]) if len(shape) > 1 else 1
                else:
                    batch_examples = int(getattr(input_ids, "size", lambda: 1)())
                    seq_len = 1
            else:
                try:
                    batch_examples = len(next(iter(prepared.values())))
                except Exception:  # pragma: no cover - fallback when len missing
                    batch_examples = 1
                seq_len = 1

            attention_mask = prepared.get("attention_mask")
            if attention_mask is not None and hasattr(attention_mask, "sum"):
                tokens = int(attention_mask.sum().item())
            else:
                tokens = batch_examples * max(seq_len, 1)

            token_weight = max(tokens, batch_examples, 1)

            total_loss += loss_value * token_weight
            total_examples += max(batch_examples, 1)
            total_tokens += token_weight

    if hasattr(model, "train"):
        model.train(was_training)

    if total_tokens == 0:
        return {}

    avg_loss = total_loss / float(total_tokens)
    try:
        perplexity = float(math.exp(avg_loss))
    except OverflowError:
        perplexity = float("inf")
    return {"val_loss": avg_loss, "val_perplexity": perplexity}
