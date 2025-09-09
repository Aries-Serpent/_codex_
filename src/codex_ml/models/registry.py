"""Model registry and factory helpers.

This module exposes a simple mapping from model names to callables that
construct the corresponding model instances.  It provides a ``get_model``
helper that optionally applies LoRA adapters via :func:`apply_lora` when
requested in the configuration.
"""

from __future__ import annotations

from typing import Any, Callable, Dict

import torch
from transformers import AutoModelForCausalLM, PreTrainedModel

from codex_ml.peft.peft_adapter import apply_lora


def _build_minilm(cfg: Dict[str, Any]) -> Any:
    from codex_ml.models.minilm import MiniLM, MiniLMConfig

    return MiniLM(MiniLMConfig(vocab_size=int(cfg.get("vocab_size", 128))))


# Mapping from model names to callables that construct them.  The callable
# receives the model configuration dictionary and returns an ``nn.Module``.
MODEL_REGISTRY: Dict[str, Callable[[Dict[str, Any]], Any]] = {
    "MiniLM": _build_minilm,
    # The default HuggingFace example.  Users may supply a different
    # ``pretrained_model_name_or_path`` in ``cfg`` to load other checkpoints.
    "bert-base-uncased": lambda cfg: _load_hf_causal_lm(
        cfg.get("pretrained_model_name_or_path") or "bert-base-uncased"
    ),
}


def _load_hf_causal_lm(name: str) -> PreTrainedModel:
    """Load a causal LM from HuggingFace with graceful failure.

    The function operates in **offline** mode by passing
    ``local_files_only=True`` to ``from_pretrained``.  This prevents
    inadvertent network access.  When the requested weights are not present in
    the local cache a ``RuntimeError`` is raised with guidance on how to
    resolve the situation (for example by downloading the model ahead of time
    or supplying a different local path).

    Parameters
    ----------
    name:
        Model identifier or path understood by ``transformers``.
    """

    try:
        return AutoModelForCausalLM.from_pretrained(name, local_files_only=True)
    except OSError as exc:  # pragma: no cover - network/IO errors
        raise RuntimeError(
            f"Unable to load weights for {name!r} from local cache. "
            "Download the model beforehand or provide a local path via ``pretrained_model_name_or_path``."
        ) from exc


# ----------------------------------------------------------------------------
# Registration helpers
# ----------------------------------------------------------------------------


def register_model(
    name: str,
) -> Callable[[Callable[[Dict[str, Any]], Any]], Callable[[Dict[str, Any]], Any]]:
    """Decorator to register additional model constructors."""

    def decorator(fn: Callable[[Dict[str, Any]], Any]) -> Callable[[Dict[str, Any]], Any]:
        MODEL_REGISTRY[name] = fn
        return fn

    return decorator


# ----------------------------------------------------------------------------
# Factory API
# ----------------------------------------------------------------------------


def get_model(name: str, cfg: Dict[str, Any]) -> Any:
    """Instantiate a model by name and apply LoRA if requested.

    Parameters
    ----------
    name:
        Registry key identifying the model to construct.
    cfg:
        Configuration mapping.  If ``cfg['lora']['enabled']`` is truthy the
        model will be adapted using :func:`apply_lora`.
    """

    if name not in MODEL_REGISTRY:
        raise ValueError(f"Unknown model: {name}")
    model = MODEL_REGISTRY[name](cfg)
    lora_cfg = cfg.get("lora", {})
    if lora_cfg.get("enabled"):
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


__all__ = ["MODEL_REGISTRY", "register_model", "get_model"]
