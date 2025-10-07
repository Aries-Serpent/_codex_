import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Union, cast
from urllib.parse import unquote, urlparse

from codex_ml.utils.hf_revision import get_hf_revision
from codex_ml.utils.optional import optional_import

if TYPE_CHECKING:  # pragma: no cover - import for typing only
    from transformers import (  # type: ignore
        AutoModel as HF_AutoModel,
        AutoModelForCausalLM as HF_AutoModelForCausalLM,
        AutoTokenizer as HF_AutoTokenizer,
        PreTrainedModel as HF_PreTrainedModel,
        PreTrainedTokenizerBase as HF_PreTrainedTokenizerBase,
    )
else:  # pragma: no cover - fall back to ``Any`` when dependency missing at runtime
    HF_AutoModel = HF_AutoModelForCausalLM = HF_AutoTokenizer = Any  # type: ignore
    HF_PreTrainedModel = HF_PreTrainedTokenizerBase = Any  # type: ignore


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
    AutoModel = cast("type[HF_AutoModel]", transformers.AutoModel)  # type: ignore[attr-defined]
    AutoModelForCausalLM = cast("type[HF_AutoModelForCausalLM]", transformers.AutoModelForCausalLM)  # type: ignore[attr-defined]
    AutoTokenizer = cast("type[HF_AutoTokenizer]", transformers.AutoTokenizer)  # type: ignore[attr-defined]
    PreTrainedModel = cast("type[HF_PreTrainedModel]", transformers.PreTrainedModel)  # type: ignore[attr-defined]
    PreTrainedTokenizerBase = cast(
        "type[HF_PreTrainedTokenizerBase]", transformers.PreTrainedTokenizerBase
    )  # type: ignore[attr-defined]
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
except Exception:  # pragma: no cover - torch is optional at import time
    torch = None  # type: ignore[assignment]


_CAUSAL_LM_REGISTRY: Dict[str, Callable[..., Any]] = {}


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
        "Set HF_REVISION/HF_MODEL_REVISION/CODEX_HF_REVISION/HUGGINGFACE_REVISION env var or pass `revision=`."
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
) -> PreTrainedTokenizerBase:
    if not TRANSFORMERS_AVAILABLE or AutoTokenizer is None:
        raise ImportError("transformers is required to load tokenizers")
    rev = _required_revision(repo_id, revision)
    return AutoTokenizer.from_pretrained(  # nosec B615 - revision enforced via _required_revision
        repo_id,
        revision=rev,
        trust_remote_code=trust_remote_code,
    )


def load_model(
    repo_id: RepoId,
    *,
    revision: Optional[str] = None,
    trust_remote_code: bool = False,
    peft_path: Optional[Union[str, os.PathLike[str]]] = None,
) -> PreTrainedModel:
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
                from peft import PeftModel  # type: ignore
            except Exception as exc:  # pragma: no cover - optional dependency
                logger.info(
                    "load_model: PEFT adapter not applied (dependency missing): %s",
                    exc,
                )
            else:
                try:
                    model = PeftModel.from_pretrained(model, str(resolved))
                    logger.info("load_model: PEFT adapter loaded from %s", resolved)
                except Exception as exc:  # pragma: no cover - runtime failure
                    logger.info("load_model: PEFT adapter not applied (runtime error): %s", exc)
    return model


def load_causal_lm(
    repo_id: RepoId,
    *,
    revision: Optional[str] = None,
    trust_remote_code: bool = False,
    device: Optional[str] = None,
    dtype: Optional[str] = None,
    peft_cfg: Optional[Dict[str, Any]] = None,
    peft_path: Optional[Union[str, os.PathLike[str]]] = None,
) -> PreTrainedModel:
    if not TRANSFORMERS_AVAILABLE or AutoModelForCausalLM is None:
        raise ImportError("transformers is required to load causal language models")
    if isinstance(repo_id, str):
        ctor = get_registered_causal_lm(repo_id)
        if ctor is not None:
            kwargs: Dict[str, Any] = {}
            if device is not None:
                kwargs["device"] = device
            if dtype is not None:
                kwargs["dtype"] = dtype
            if peft_cfg is not None:
                kwargs["peft_cfg"] = peft_cfg
            return ctor(**kwargs)

    rev = _required_revision(repo_id, revision)
    torch_dtype = _map_amp_dtype(dtype)
    loader_kwargs: Dict[str, Any] = {
        "revision": rev,
        "trust_remote_code": trust_remote_code,
    }
    if torch_dtype is not None:
        loader_kwargs["torch_dtype"] = torch_dtype

    try:
        model = AutoModelForCausalLM.from_pretrained(  # nosec B615 - revision enforced via _required_revision
            repo_id,
            **loader_kwargs,
        )
    except TypeError:
        # Older versions of transformers do not support the ``torch_dtype`` kwarg.
        loader_kwargs.pop("torch_dtype", None)
        model = AutoModelForCausalLM.from_pretrained(  # type: ignore[call-arg]  # nosec B615 - revision enforced
            repo_id,
            **loader_kwargs,
        )

    if device:
        try:
            model = model.to(device)
        except Exception as exc:  # pragma: no cover - device mapping best-effort
            logger.info("load_causal_lm: unable to move model to %s: %s", device, exc)

    if peft_cfg:
        try:
            from peft import LoraConfig, get_peft_model  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency
            logger.info("load_causal_lm: LoRA not applied (dependency missing): %s", exc)
        else:
            try:
                lora = LoraConfig(**peft_cfg)
            except Exception as exc:  # pragma: no cover - invalid config values
                logger.info("load_causal_lm: LoRA config rejected: %s", exc)
            else:
                try:
                    model = get_peft_model(model, lora)
                    logger.info(
                        "load_causal_lm: LoRA attached (r=%s, alpha=%s)",
                        getattr(lora, "r", "?"),
                        getattr(lora, "lora_alpha", "?"),
                    )
                except Exception as exc:  # pragma: no cover - PEFT runtime failure
                    logger.info("load_causal_lm: LoRA not applied (runtime error): %s", exc)

    adapter_path = peft_path or os.getenv("PEFT_ADAPTER_PATH")
    if adapter_path:
        try:
            from peft import PeftModel  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency
            logger.info(
                "load_causal_lm: PEFT adapter not applied (dependency missing): %s",
                exc,
            )
        else:
            try:
                model = PeftModel.from_pretrained(model, adapter_path)
                logger.info(
                    "load_causal_lm: PEFT adapter loaded from %s",
                    adapter_path,
                )
            except Exception as exc:  # pragma: no cover - runtime failure
                logger.info("load_causal_lm: PEFT adapter not applied (runtime error): %s", exc)

    return model


__all__ = [
    "register_causal_lm",
    "unregister_causal_lm",
    "get_registered_causal_lm",
    "load_tokenizer",
    "load_model",
    "load_causal_lm",
]
