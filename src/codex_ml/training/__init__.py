from __future__ import annotations

import contextlib
from typing import Any, Iterable, Mapping

from omegaconf import DictConfig, OmegaConf


def run_functional_training(
    config: DictConfig | Mapping[str, Any],
    *,
    resume: bool = False,
) -> dict[str, Any]:
    """Run the Codex functional training loop with optional resume support."""

    from collections.abc import Mapping as _Mapping
    from pathlib import Path as _Path

    import numpy as _np

    try:
        from datasets import Dataset as _Dataset  # type: ignore
        from transformers import AutoTokenizer as _AutoTokenizer  # type: ignore
    except Exception as exc:  # pragma: no cover - optional deps
        raise RuntimeError("datasets and transformers are required for training") from exc

    from codex_ml.models.registry import get_model as _get_model
    from codex_ml.utils.checkpointing import load_training_checkpoint as _load_ckpt
    from training.functional_training import TrainCfg as _TrainCfg
    from training.functional_training import run_custom_trainer as _run_custom_trainer

    if isinstance(config, DictConfig):
        container = OmegaConf.to_container(config, resolve=True)  # type: ignore[arg-type]
    elif isinstance(config, _Mapping):
        container = dict(config)
        config = OmegaConf.create(container)
    else:
        raise TypeError("config must be a mapping or DictConfig")

    training_section = container.get("training", {}) if isinstance(container, dict) else {}
    if not isinstance(training_section, dict):
        training_section = {}

    def _pop(keys: Iterable[str], default: Any = None) -> Any:
        for key in keys:
            if key in training_section:
                return training_section[key]
            if isinstance(container, dict) and key in container:
                return container[key]
        return default

    texts = _pop(["texts"]) or []
    if not texts:
        raise ValueError("training texts are required in the config")
    val_texts = _pop(["val_texts"], None)

    model_cfg = training_section.get("model") or container.get("model") or {"name": "MiniLM"}
    tokenizer_name = (
        model_cfg.get("pretrained_model_name_or_path")
        or model_cfg.get("name")
        or "sshleifer/tiny-gpt2"
    )

    checkpoint_dir_value = (
        training_section.get("checkpoint_dir")
        or container.get("output_dir")
        or "runs/default/checkpoints"
    )
    checkpoint_dir = _Path(checkpoint_dir_value)
    if checkpoint_dir.suffix:
        checkpoint_dir.parent.mkdir(parents=True, exist_ok=True)
    else:
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
    training_section["checkpoint_dir"] = str(checkpoint_dir)

    train_kwargs: dict[str, Any] = {}
    for field in _TrainCfg.__dataclass_fields__:
        if field in training_section:
            train_kwargs[field] = training_section[field]
    if "lr" not in train_kwargs:
        train_kwargs["lr"] = _pop(["learning_rate", "lr"], 5e-4)
    if "batch_size" not in train_kwargs:
        train_kwargs["batch_size"] = _pop(["batch_size"], 8)
    if "epochs" not in train_kwargs:
        train_kwargs["epochs"] = _pop(["epochs", "max_epochs"], 1)
    if "grad_accum" not in train_kwargs:
        train_kwargs["grad_accum"] = _pop(["grad_accum", "gradient_accumulation"], 1)
    train_kwargs.setdefault("checkpoint_dir", str(checkpoint_dir))

    if resume:
        candidates = sorted(checkpoint_dir.glob("*.pt"))
        if candidates:
            latest_ckpt = str(candidates[-1])
            train_kwargs["resume_from"] = latest_ckpt
            with contextlib.suppress(Exception):
                _load_ckpt(latest_ckpt)

    train_cfg = _TrainCfg(**train_kwargs)

    tokenizer = _AutoTokenizer.from_pretrained(tokenizer_name)
    if getattr(tokenizer, "pad_token", None) is None:
        tokenizer.pad_token = tokenizer.eos_token

    tokenized = tokenizer(list(texts), padding=True, return_tensors="pt")
    tokenized["labels"] = tokenized["input_ids"].clone()
    tokenized["labels"][tokenized["attention_mask"] == 0] = -100
    train_ds = _Dataset.from_dict(
        {k: v.numpy() if hasattr(v, "numpy") else _np.array(v) for k, v in tokenized.items()}
    )

    val_ds = None
    if val_texts:
        val_tok = tokenizer(list(val_texts), padding=True, return_tensors="pt")
        val_tok["labels"] = val_tok["input_ids"].clone()
        val_tok["labels"][val_tok["attention_mask"] == 0] = -100
        val_ds = _Dataset.from_dict(
            {k: v.numpy() if hasattr(v, "numpy") else _np.array(v) for k, v in val_tok.items()}
        )

    model = _get_model(model_cfg.get("name", "MiniLM"), model_cfg)
    return _run_custom_trainer(model, tokenizer, train_ds, val_ds, train_cfg)
