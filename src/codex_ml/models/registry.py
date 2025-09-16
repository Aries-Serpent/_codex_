"""Model registry built on :mod:`codex_ml.registry` primitives."""

from __future__ import annotations

from typing import Any, Dict

import torch
from transformers import AutoModelForCausalLM, PreTrainedModel

from codex_ml.peft.peft_adapter import apply_lora
from codex_ml.registry.base import Registry

model_registry = Registry("model", entry_point_group="codex_ml.models")


@model_registry.register("MiniLM")
def _build_minilm(cfg: Dict[str, Any]) -> Any:
    from codex_ml.models.minilm import MiniLM, MiniLMConfig

    return MiniLM(MiniLMConfig(vocab_size=int(cfg.get("vocab_size", 128))))


def _load_hf_causal_lm(name: str) -> PreTrainedModel:
    """Load a causal LM from HuggingFace with offline-first semantics."""

    try:
        return AutoModelForCausalLM.from_pretrained(name, local_files_only=True)
    except OSError as exc:  # pragma: no cover - network/IO errors
        raise RuntimeError(
            f"Unable to load weights for {name!r} from local cache. "
            "Download the model beforehand or provide a local path via ``pretrained_model_name_or_path``."
        ) from exc


@model_registry.register("bert-base-uncased")
def _build_default_bert(cfg: Dict[str, Any]) -> PreTrainedModel:
    target = cfg.get("pretrained_model_name_or_path") or "bert-base-uncased"
    return _load_hf_causal_lm(str(target))


def register_model(name: str, obj: Any | None = None, *, override: bool = False) -> Any:
    """Register a model constructor under ``name``."""

    return model_registry.register(name, obj, override=override)


def get_model(name: str, cfg: Dict[str, Any]) -> Any:
    """Instantiate a model by name and apply LoRA/device settings when requested."""

    builder = model_registry.get(name)
    model = builder(cfg) if callable(builder) else builder
    lora_cfg = cfg.get("lora", {})
    if isinstance(lora_cfg, dict) and lora_cfg.get("enabled"):
        model = apply_lora(model, lora_cfg)
    dtype = cfg.get("dtype")
    if dtype is not None:
        try:
            model = model.to(getattr(torch, str(dtype)))
        except Exception:  # pragma: no cover - invalid dtype
            pass
    device = cfg.get("device")
    if device is not None:
        try:
            model = model.to(device)
        except Exception:  # pragma: no cover - invalid device
            pass
    return model


def list_models() -> list[str]:
    """Return available model registrations."""

    return model_registry.list()


__all__ = ["model_registry", "register_model", "get_model", "list_models"]
