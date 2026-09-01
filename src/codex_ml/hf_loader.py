"""
Hf Loader Module

This module provides functionality for hf loader.

Usage:
    from codex_ml.hf_loader import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

import logging
import os
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Union, cast
from urllib.parse import unquote, urlparse

from codex_ml.utils.hf_revision import get_hf_revision
from codex_ml.utils.optional import optional_import

if TYPE_CHECKING:  # pragma: no cover - import for typing only
    from transformers import AutoModel as HF_AutoModel
    from transformers import AutoModelForCausalLM as HF_AutoModelForCausalLM
    from transformers import AutoTokenizer as HF_AutoTokenizer
    from transformers import PreTrainedModel as HF_PreTrainedModel
    from transformers import PreTrainedTokenizerBase as HF_PreTrainedTokenizerBase
else:  # pragma: no cover - fall back to ``Any`` when dependency missing at runtime
    HF_AutoModel = HF_AutoModelForCausalLM = HF_AutoTokenizer = Any
    HF_PreTrainedModel = HF_PreTrainedTokenizerBase = Any


transformers, _HAS_TRANSFORMERS = optional_import("transformers")
if (
    _HAS_TRANSFORMERS
    and transformers is not None
    and all(
        hasattr(transformers, attr)
        for attr in [
            "AutoModel",
            "AutoModelForCausalLM",
            "AutoTokenizer",
            "PreTrainedModel",
            "PreTrainedTokenizerBase",
        ]
    )
):
    AutoModel = cast(type[HF_AutoModel], transformers.AutoModel)
    AutoModelForCausalLM = cast(type[HF_AutoModelForCausalLM], transformers.AutoModelForCausalLM)
    AutoTokenizer = cast(type[HF_AutoTokenizer], transformers.AutoTokenizer)
    PreTrainedModel = cast(type[HF_PreTrainedModel], transformers.PreTrainedModel)
    PreTrainedTokenizerBase = cast(
        type[HF_PreTrainedTokenizerBase],
        transformers.PreTrainedTokenizerBase,
    )
else:  # pragma: no cover - optional dependency missing
    AutoModel = None  # type: ignore[assignment]
    AutoModelForCausalLM = None  # type: ignore[assignment]
    AutoTokenizer = None  # type: ignore[assignment]
    PreTrainedModel = cast("type[HF_PreTrainedModel]", object)
    PreTrainedTokenizerBase = cast("type[HF_PreTrainedTokenizerBase]", object)

TRANSFORMERS_AVAILABLE = _HAS_TRANSFORMERS

RepoId = Union[str, os.PathLike[str]]


logger = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency
    import torch
except (ImportError, AttributeError):  # pragma: no cover - torch is optional at import time
    torch = None


_CAUSAL_LM_REGISTRY: dict[str, Callable[..., Any]] = {}


def register_causal_lm(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Register a custom causal LM constructor.

    Registered callables are invoked by :func:`load_causal_lm` when the
    ``repo_id`` matches ``name`` exactly.  Constructors receive the keyword
    arguments ``device``, ``dtype`` and ``peft_cfg`` so they can mirror the
    behaviour of the default loader.
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        _CAUSAL_LM_REGISTRY[name] = fn
        return fn

    return decorator


def unregister_causal_lm(name: str) -> None:
    """Remove a previously registered constructor if present."""

    _CAUSAL_LM_REGISTRY.pop(name, None)


def get_registered_causal_lm(name: str) -> Optional[Callable[..., Any]]:
    """Return the constructor registered under ``name`` (if any)."""

    return _CAUSAL_LM_REGISTRY.get(name)


def _is_local_identifier(repo_id: RepoId) -> bool:
    if isinstance(repo_id, os.PathLike):
        candidate_path = Path(repo_id).expanduser()
        if candidate_path.exists():
            return True
        candidate_str = str(candidate_path)
    else:
        candidate_str = str(repo_id)
        candidate_path = Path(candidate_str).expanduser()
        if candidate_path.exists():
            return True

    parsed = urlparse(candidate_str)
    if parsed.scheme != "file":
        return False
    local_path = Path(unquote(parsed.path)).expanduser()
    if parsed.netloc and not local_path.is_absolute():
        local_path = Path(f"//{parsed.netloc}{local_path}")
    return local_path.exists()


def _required_revision(repo_id: RepoId, explicit: Optional[str]) -> Optional[str]:
    if _is_local_identifier(repo_id):
        return explicit
    if explicit:
        return explicit

    env_revision = os.environ.get("HUGGINGFACE_REVISION")
    if env_revision:
        return env_revision

    resolved_revision = get_hf_revision()
    if resolved_revision:
        return resolved_revision

    raise RuntimeError(
        "Hugging Face `revision` is required (Bandit B615). "
        "Set HF_REVISION/HF_MODEL_REVISION/CODEX_HF_REVISION/HUGGINGFACE_REVISION env var or pass `revision=`."  # noqa: E501
    )


def _map_amp_dtype(dtype: Optional[str]):
    """Translate user-friendly AMP dtype flags into ``torch.dtype`` values."""

    if torch is None or dtype is None:
        return None
    normalised = dtype.lower()
    if normalised in {"bf16", "bfloat16"}:
        return getattr(torch, "bfloat16", None)
    if normalised in {"fp16", "float16", "half"}:
        return getattr(torch, "float16", None)
    return None


def load_tokenizer(
    repo_id: RepoId,
    *,
    revision: Optional[str] = None,
    trust_remote_code: bool = False,
) -> PreTrainedTokenizerBase:  # type: ignore[valid-type]
    if not TRANSFORMERS_AVAILABLE or AutoTokenizer is None:
        raise ImportError("transformers is required to load tokenizers")
    rev = _required_revision(repo_id, revision)
    tokenizer = (
        AutoTokenizer.from_pretrained(  # nosec B615 - revision enforced via _required_revision
            repo_id,
            revision=rev,
            trust_remote_code=trust_remote_code,
        )
    )
    # Ensure pad_token is set; decoder-only models (GPT-2, LLaMA, Mistral …) omit it
    # because they use eos_token to pad — both serve as sequence terminators.
    if tokenizer is not None and tokenizer.pad_token is None and tokenizer.eos_token is not None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer


def load_model(
    repo_id: RepoId,
    *,
    revision: Optional[str] = None,
    trust_remote_code: bool = False,
    peft_path: Optional[str | os.PathLike[str]] = None,
) -> PreTrainedModel:  # type: ignore[valid-type]
    """Load a base transformer model and optionally attach a PEFT adapter."""

    if not TRANSFORMERS_AVAILABLE or AutoModel is None:
        raise ImportError("transformers is required to load models")
    rev = _required_revision(repo_id, revision)
    model = AutoModel.from_pretrained(  # nosec B615 - revision enforced via _required_revision
        repo_id,
        revision=rev,
        trust_remote_code=trust_remote_code,
    )
    adapter_path = peft_path or os.getenv("PEFT_ADAPTER_PATH")
    if adapter_path:
        resolved = Path(adapter_path).expanduser()
        if not resolved.exists():
            logger.info(
                "load_model: PEFT adapter not applied (path missing): %s",
                resolved,
            )
        else:
            try:
                from peft import PeftModel
            except (ImportError, AttributeError) as exc:  # pragma: no cover - optional dependency
                logger.info(
                    "load_model: PEFT adapter not applied (dependency missing): %s",
                    exc,
                )
            else:
                try:
                    model = PeftModel.from_pretrained(model, str(resolved))
                    logger.info("load_model: PEFT adapter loaded from %s", resolved)
                except (
                    ValueError,
                    TypeError,
                    RuntimeError,
                ) as exc:  # pragma: no cover - runtime failure
                    logger.info("load_model: PEFT adapter not applied (runtime error): %s", exc)
    return model


def _build_loader_kwargs(
    repo_id: RepoId,
    revision: Optional[str],
    trust_remote_code: bool,
    dtype: Optional[str],
) -> tuple[str, dict[str, Any]]:
    """Build kwargs for AutoModelForCausalLM.from_pretrained.
    
    Reduces complexity by extracting argument building logic (5+ branches).
    """
    from typing import Any

    from codex_ml.hf_loader import _map_amp_dtype, _required_revision
    
    rev = _required_revision(repo_id, revision)
    torch_dtype = _map_amp_dtype(dtype)
    loader_kwargs: dict[str, Any] = {
        "revision": rev,
        "trust_remote_code": trust_remote_code,
    }
    if torch_dtype is not None:
        loader_kwargs["torch_dtype"] = torch_dtype
    
    return rev, loader_kwargs


def _load_model_with_fallback(
    repo_id: RepoId,
    loader_kwargs: dict[str, Any],
) -> Any:
    """Load model with fallback for older transformers versions.
    
    Reduces complexity by extracting fallback logic (2 branches).
    """
    import logging

    from transformers import AutoModelForCausalLM
    
    logger = logging.getLogger(__name__)
    
    try:
        model = AutoModelForCausalLM.from_pretrained(
            repo_id,
            **loader_kwargs,
        )
    except TypeError:
        logger.debug("TypeError during model load with torch_dtype, retrying without it")
        logger.warning("TypeError: retrying", exc_info=True)
        # Older versions of transformers do not support the ``torch_dtype`` kwarg.
        loader_kwargs.pop("torch_dtype", None)
        model = AutoModelForCausalLM.from_pretrained(
            repo_id,
            **loader_kwargs,
        )
    
    return model


def _move_model_to_device(model: Any, device: Optional[str]) -> None:
    """Move model to target device (best-effort).
    
    Reduces complexity by extracting device movement (1 branch).
    """
    if device and model is not None:
        try:
            model.to(device)
        except (ImportError, AttributeError) as exc:
            logger.info("load_causal_lm: unable to move model to %s: %s", device, exc)


def _apply_lora_config(model: Any, peft_cfg: dict[str, Any]) -> None:
    """Apply LoRA configuration to model.
    
    Reduces complexity by extracting LoRA setup (5 nested try-except blocks → 1).
    """
    try:
        from peft import LoraConfig, get_peft_model
    except (ImportError, AttributeError) as exc:
        logger.info("load_causal_lm: LoRA not applied (dependency missing): %s", exc)
        return
    
    try:
        lora = LoraConfig(**peft_cfg)
    except (ValueError, TypeError, RuntimeError) as exc:
        logger.info("load_causal_lm: LoRA config rejected: %s", exc)
        return
    
    try:
        model = get_peft_model(model, lora)
        logger.info(
            "load_causal_lm: LoRA attached (r=%s, alpha=%s)",
            getattr(lora, "r", "?"),
            getattr(lora, "lora_alpha", "?"),
        )
    except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:
        logger.info("load_causal_lm: LoRA not applied (runtime error): %s", exc)


def _load_peft_adapter(model: Any, adapter_path: str | os.PathLike[str]) -> None:
    """Load PEFT adapter from path.
    
    Reduces complexity by extracting adapter loading (2 nested try-except blocks → 1).
    """
    resolved_path = str(adapter_path)
    try:
        from peft import PeftModel
    except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:
        logger.info(
            "load_causal_lm: PEFT adapter not applied (dependency missing): %s",
            exc,
        )
        return
    
    try:
        model = PeftModel.from_pretrained(model, resolved_path)
        logger.info(
            "load_causal_lm: PEFT adapter loaded from %s",
            resolved_path,
        )
    except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:
        logger.info("load_causal_lm: PEFT adapter not applied (runtime error): %s", exc)


def load_causal_lm(
    repo_id: RepoId,
    *,
    revision: Optional[str] = None,
    trust_remote_code: bool = False,
    device: Optional[str] = None,
    dtype: Optional[str] = None,
    peft_cfg: Optional[dict[str, Any]] = None,
    peft_path: Optional[str | os.PathLike[str]] = None,
) -> PreTrainedModel:  # type: ignore[valid-type]
    """Load a causal language model from HuggingFace Hub.
    
    Reduced complexity through strategic helper extraction.
    """
    if not TRANSFORMERS_AVAILABLE or AutoModelForCausalLM is None:
        raise ImportError("transformers is required to load causal language models")
    
    if isinstance(repo_id, str):
        ctor = get_registered_causal_lm(repo_id)
        if ctor is not None:
            kwargs: dict[str, Any] = {}
            if device is not None:
                kwargs["device"] = device
            if dtype is not None:
                kwargs["dtype"] = dtype
            if peft_cfg is not None:
                kwargs["peft_cfg"] = peft_cfg
            return ctor(**kwargs)

    # Extract model loading with helper
    _, loader_kwargs = _build_loader_kwargs(repo_id, revision, trust_remote_code, dtype)
    model = _load_model_with_fallback(repo_id, loader_kwargs)
    
    # Move to device (best-effort)
    _move_model_to_device(model, device)

    # Apply LoRA configuration if provided
    if peft_cfg:
        _apply_lora_config(model, peft_cfg)

    # Load PEFT adapter if provided
    adapter_path = peft_path or os.getenv("PEFT_ADAPTER_PATH")
    if adapter_path:
        _load_peft_adapter(model, adapter_path)

    return model


__all__ = [
    "get_registered_causal_lm",
    "load_causal_lm",
    "load_model",
    "load_tokenizer",
    "register_causal_lm",
    "unregister_causal_lm",
]
