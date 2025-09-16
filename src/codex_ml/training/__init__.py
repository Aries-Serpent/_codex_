from __future__ import annotations

import contextlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

from codex_ml.utils.error_log import log_error
from codex_ml.utils.provenance import export_environment
from codex_ml.utils.seeding import set_reproducible

try:  # pragma: no cover - optional dependency in tests
    from omegaconf import DictConfig, OmegaConf  # type: ignore
except Exception:  # pragma: no cover - OmegaConf optional
    DictConfig = None  # type: ignore[assignment]
    OmegaConf = None  # type: ignore[assignment]

__all__ = ["TrainingRunConfig", "run_functional_training"]


@dataclass
class TrainingRunConfig:
    seed: int = 42
    model: Any = "minilm"
    learning_rate: float = 0.0003
    batch_size: int = 32
    max_epochs: int = 5
    scheduler: str = "linear"
    warmup_steps: int = 0
    gradient_accumulation: int = 1
    tensorboard: bool = True
    mlflow_enable: bool = False
    output_dir: str = "runs/default"
    checkpoint_dir: Optional[str] = None
    checkpoint_every_n_steps: int = 100
    dataset: Dict[str, Any] = field(
        default_factory=lambda: {
            "train_path": "data/train_samples.jsonl",
            "eval_path": None,
            "format": "jsonl",
            "train_texts": [],
            "eval_texts": [],
        }
    )


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

    def _scalar(default: Any, *keys: str) -> Any:
        for key in keys:
            if key in mapping and mapping[key] is not None:
                return mapping[key]
        if isinstance(training_section, Mapping):
            for key in keys:
                if key in training_section and training_section[key] is not None:
                    return training_section[key]
        return default

    checkpoint_dir = _scalar(None, "checkpoint_dir")
    if checkpoint_dir is None and isinstance(training_section, Mapping):
        checkpoint_dir = training_section.get("checkpoint_dir")

    tensorboard_value = _scalar(base.tensorboard, "tensorboard")
    mlflow_value = _scalar(base.mlflow_enable, "mlflow_enable")

    model_value = _coerce_model_entry(_scalar(base.model, "model"), base.model)

    return TrainingRunConfig(
        seed=int(_scalar(base.seed, "seed")),
        model=model_value,
        learning_rate=float(_scalar(base.learning_rate, "learning_rate", "lr")),
        batch_size=int(_scalar(base.batch_size, "batch_size")),
        max_epochs=int(_scalar(base.max_epochs, "max_epochs", "epochs")),
        scheduler=str(_scalar(base.scheduler, "scheduler")),
        warmup_steps=int(_scalar(base.warmup_steps, "warmup_steps")),
        gradient_accumulation=int(
            _scalar(base.gradient_accumulation, "gradient_accumulation", "grad_accum")
        ),
        tensorboard=(
            tensorboard_value if isinstance(tensorboard_value, bool) else bool(tensorboard_value)
        ),
        mlflow_enable=mlflow_value if isinstance(mlflow_value, bool) else bool(mlflow_value),
        output_dir=str(_scalar(base.output_dir, "output_dir")),
        checkpoint_dir=str(checkpoint_dir) if checkpoint_dir else None,
        checkpoint_every_n_steps=int(
            _scalar(base.checkpoint_every_n_steps, "checkpoint_every_n_steps", "save_every")
        ),
        dataset=dataset_cfg,
    )


def run_functional_training(
    config: Mapping[str, Any] | TrainingRunConfig, *, resume: bool = False
) -> Dict[str, Any]:
    """Run the Codex functional training loop with optional resume support."""

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
    dataset_format = str(dataset_cfg.get("format", "text"))

    train_texts = _listify_texts(dataset_cfg.get("train_texts"))
    if not train_texts:
        train_texts = _listify_texts(dataset_cfg.get("texts"))
    if dataset_cfg.get("train_path"):
        train_texts.extend(_load_texts(dataset_cfg.get("train_path"), dataset_format))

    val_texts = _listify_texts(dataset_cfg.get("eval_texts"))
    if not val_texts:
        val_texts = _listify_texts(dataset_cfg.get("val_texts"))
    if dataset_cfg.get("eval_path"):
        val_texts.extend(_load_texts(dataset_cfg.get("eval_path"), dataset_format))

    if not train_texts:
        ctx = {"path": dataset_cfg.get("train_path"), "texts": len(train_texts)}
        log_error("train.dataset", "training dataset is empty or missing", json.dumps(ctx))
        raise ValueError("training dataset is empty or missing")

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
    except Exception as exc:  # pragma: no cover - optional dependencies
        raise RuntimeError("datasets and transformers are required for training") from exc

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
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
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
    train_kwargs.setdefault("warmup_steps", cfg.warmup_steps)
    train_kwargs.setdefault("seed", cfg.seed)

    train_kwargs["lr"] = float(train_kwargs["lr"])
    train_kwargs["batch_size"] = int(train_kwargs["batch_size"])
    train_kwargs["epochs"] = int(train_kwargs["epochs"])
    train_kwargs["grad_accum"] = int(train_kwargs["grad_accum"])
    train_kwargs["save_every"] = int(train_kwargs["save_every"])
    train_kwargs["warmup_steps"] = int(train_kwargs["warmup_steps"])
    train_kwargs["seed"] = int(train_kwargs["seed"])

    train_kwargs["checkpoint_dir"] = str(checkpoint_dir)

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
    return run_custom_trainer(model, tokenizer, train_ds, val_ds, train_cfg)
