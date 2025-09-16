from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

from codex_ml.utils.checkpointing import CheckpointManager
from codex_ml.utils.error_log import log_error

try:  # pragma: no cover - optional dependency in tests
    from omegaconf import DictConfig, OmegaConf  # type: ignore
except Exception:  # pragma: no cover - OmegaConf optional
    DictConfig = None  # type: ignore[assignment]
    OmegaConf = None  # type: ignore[assignment]

__all__ = ["TrainingRunConfig", "run_functional_training"]


class _SimpleModel:
    def __init__(self) -> None:
        self.step = 0

    def state_dict(self) -> Dict[str, Any]:
        return {"step": self.step}

    def load_state_dict(self, state: Mapping[str, Any]) -> None:
        self.step = int(state.get("step", 0))


class _SimpleOptimizer:
    def __init__(self) -> None:
        self.state: Dict[str, Any] = {}

    def state_dict(self) -> Dict[str, Any]:
        return {"state": dict(self.state)}

    def load_state_dict(self, state: Mapping[str, Any]) -> None:
        self.state = dict(state.get("state", {}))


class _SimpleScheduler(_SimpleOptimizer):
    """Scheduler stub sharing persistence helpers."""

    pass


@dataclass
class TrainingRunConfig:
    seed: int = 42
    model: str = "minilm"
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

    return TrainingRunConfig(
        seed=int(_scalar(base.seed, "seed")),
        model=str(_scalar(base.model, "model")),
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
    """Run a lightweight training loop with checkpointing support."""

    if isinstance(config, TrainingRunConfig):
        cfg = config
    else:
        cfg = _coerce_config(config)

    random.seed(cfg.seed)

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

    checkpoint_root = Path(cfg.checkpoint_dir) if cfg.checkpoint_dir else output_dir / "checkpoints"
    checkpoint_root.mkdir(parents=True, exist_ok=True)

    model = _SimpleModel()
    optimizer = _SimpleOptimizer()
    scheduler = _SimpleScheduler()

    manager = CheckpointManager(checkpoint_root, keep_last=max(cfg.max_epochs, 1), keep_best=1)

    start_epoch = 0
    resumed_from: Optional[Path] = None
    if resume:
        marker = checkpoint_root / "last"
        if marker.exists():
            try:
                resume_path = Path(marker.read_text(encoding="utf-8").strip())
                if resume_path.exists():
                    manager.resume_from(
                        resume_path, model=model, optimizer=optimizer, scheduler=scheduler
                    )
                    resumed_from = resume_path
                    try:
                        start_epoch = int(resume_path.name.split("-")[-1]) + 1
                    except ValueError:
                        start_epoch = 0
            except Exception as exc:
                log_error(
                    "train.resume",
                    f"{exc.__class__.__name__}: {exc}",
                    json.dumps({"path": str(locals().get("resume_path", ""))}),
                )

    metrics: List[Dict[str, Any]] = []
    last_checkpoint: Optional[Path] = None
    total_tokens = sum(len(text.split()) for text in train_texts)

    for epoch in range(start_epoch, cfg.max_epochs):
        model.step += len(train_texts)
        metric = {"epoch": epoch, "tokens": total_tokens, "loss": round(1.0 / (epoch + 1), 4)}
        metrics.append(metric)
        last_checkpoint = manager.save(
            epoch,
            model=model,
            optimizer=optimizer,
            scheduler=scheduler,
            config={
                "seed": cfg.seed,
                "model": cfg.model,
                "learning_rate": cfg.learning_rate,
                "batch_size": cfg.batch_size,
            },
            metrics=metric,
        )

    return {
        "metrics": metrics,
        "checkpoint_dir": str(last_checkpoint) if last_checkpoint else None,
        "resumed_from": str(resumed_from) if resumed_from else None,
    }
