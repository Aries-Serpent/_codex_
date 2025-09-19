"""Model registry built on :mod:`codex_ml.registry` primitives."""

from __future__ import annotations

from typing import Any, Dict

import torch
from transformers import AutoModelForCausalLM, AutoModelForMaskedLM, PreTrainedModel

from codex_ml.peft.peft_adapter import apply_lora
from codex_ml.registry.base import Registry

model_registry = Registry("model", entry_point_group="codex_ml.models")


@model_registry.register("MiniLM")
def _build_minilm(cfg: Dict[str, Any]) -> Any:
    from codex_ml.models.minilm import MiniLM, MiniLMConfig

    return MiniLM(MiniLMConfig(vocab_size=int(cfg.get("vocab_size", 128))))


def _resolve_pretrained_identifier(cfg: Dict[str, Any], default: str) -> str:
    for key in ("local_path", "path", "model_path", "pretrained_model_name_or_path", "model_id"):
        value = cfg.get(key)
        if value:
            return str(value)
    return default


def _load_hf_model(task: str, cfg: Dict[str, Any], default: str) -> PreTrainedModel:
    """Load a transformers model with offline-first semantics."""

    model_id = _resolve_pretrained_identifier(cfg, default)
    local_only = bool(cfg.get("local_files_only", True))
    trust_remote_code = cfg.get("trust_remote_code")

    if task == "causal":
        loader = AutoModelForCausalLM
    elif task == "mlm":
        loader = AutoModelForMaskedLM
    else:
        raise ValueError(f"Unsupported task for registry entry: {task}")

    kwargs: Dict[str, Any] = {"local_files_only": local_only}
    if trust_remote_code is not None:
        kwargs["trust_remote_code"] = bool(trust_remote_code)

    try:
        return loader.from_pretrained(model_id, **kwargs)
    except OSError as exc:  # pragma: no cover - network/IO errors
        raise RuntimeError(
            f"Unable to load weights for {model_id!r} from local cache. "
            "Provide a `local_path` or set `local_files_only=False` if remote downloads are permitted."
        ) from exc


@model_registry.register("bert-base-uncased")
def _build_default_bert(cfg: Dict[str, Any]) -> PreTrainedModel:
    return _load_hf_model("mlm", cfg, "bert-base-uncased")


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
