from __future__ import annotations

from typing import Any, Optional

from transformers import AutoModelForCausalLM

__all__ = ["load_model_with_optional_lora"]


def _maybe_import_peft():
    try:  # optional dependency
        from peft import LoraConfig, PeftModel, get_peft_model  # type: ignore

        return LoraConfig, get_peft_model, PeftModel
    except Exception:  # pragma: no cover - optional dep
        return None, None, None


def load_model_with_optional_lora(
    name_or_path: str,
    *,
    dtype: Optional[str] = None,
    device_map: Optional[str] = None,
    lora_enabled: bool = False,
    lora_path: Optional[str] = None,
    lora_r: int = 8,
    lora_alpha: int = 16,
    lora_dropout: float = 0.05,
    lora_target_modules: Optional[list[str]] = None,
    **kw: Any,
) -> Any:
    """Load a base model and optionally apply LoRA adapters.

    - If PEFT is unavailable or lora_enabled is False, the base model is returned unchanged.
    - Provide ``lora_path`` to load LoRA adapters from disk via ``PeftModel``.
    - dtype is a string name of a torch dtype (e.g., 'float16', 'bfloat16'); resolved dynamically.
    """
    # Resolve torch dtype safely without a hard dependency at import time
    torch_dtype = None
    if dtype:
        try:
            import importlib

            torch = importlib.import_module("torch")  # type: ignore
            torch_dtype = getattr(torch, dtype, None)
        except Exception:  # pragma: no cover - torch missing or invalid dtype
            torch_dtype = None

    # Load base model
    model = AutoModelForCausalLM.from_pretrained(
        name_or_path, torch_dtype=torch_dtype, device_map=device_map, **kw
    )

    # Early exit if LoRA is disabled
    if not lora_enabled:
        return model

    # Try to import PEFT pieces
    LoraConfig, get_peft_model, PeftModel = _maybe_import_peft()
    if LoraConfig is None or get_peft_model is None or PeftModel is None:
        # PEFT not installed; return base model unchanged for backward compatibility
        return model

    if lora_path:
        # Raise any underlying errors so misconfigured paths or remote
        # adapters surface loudly instead of silently training without LoRA.
        return PeftModel.from_pretrained(model, lora_path)

    # Optional TaskType support for broader PEFT compatibility
    TaskType = None
    try:  # pragma: no cover - optional enum
        from peft import TaskType as _TaskType  # type: ignore

        TaskType = _TaskType
    except Exception:
        TaskType = None

    # Prepare LoRA config with compatibility for PEFT versions that may not accept task_type
    cfg_kwargs: dict[str, Any] = {
        "r": lora_r,
        "lora_alpha": lora_alpha,
        "lora_dropout": lora_dropout,
        "target_modules": lora_target_modules or ["q_proj", "v_proj"],
    }
    # Prefer enum when available; otherwise pass a string (older versions accept this)
    task_type_value: Any = TaskType.CAUSAL_LM if TaskType is not None else "CAUSAL_LM"
    cfg = None
    try:
        cfg = LoraConfig(task_type=task_type_value, **cfg_kwargs)  # type: ignore[call-arg]
    except TypeError:
        # Fallback for PEFT versions where task_type is not a recognized argument
        cfg = LoraConfig(**cfg_kwargs)  # type: ignore[call-arg]

    # Apply LoRA adapters
    return get_peft_model(model, cfg)  # type: ignore[misc]
