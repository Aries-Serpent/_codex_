from __future__ import annotations

from pathlib import Path
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
    """Load a base model and optionally apply LoRA adapters."""

    torch_dtype = None
    if dtype:
        import importlib

        torch = importlib.import_module("torch")  # type: ignore
        torch_dtype = getattr(torch, dtype, None)
        if torch_dtype is None:
            raise ValueError(f"Unknown dtype: {dtype}")

    if name_or_path == "decoder_only":
        try:
            from codex_ml.models.decoder_only import DecoderOnlyLM, ModelConfig

            cfg_dict = kw.pop("model_config", {})
            cfg = cfg_dict if isinstance(cfg_dict, ModelConfig) else ModelConfig(**cfg_dict)
            model = DecoderOnlyLM(cfg)
            if torch_dtype is not None:
                model = model.to(dtype=torch_dtype)
            if device_map is not None:
                model = model.to(device_map)
        except Exception:  # pragma: no cover - fallback to HF
            model = AutoModelForCausalLM.from_pretrained(
                name_or_path, torch_dtype=torch_dtype, device_map=device_map, **kw
            )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            name_or_path, torch_dtype=torch_dtype, device_map=device_map, **kw
        )

    if not lora_enabled:
        return model

    LoraConfig, get_peft_model, PeftModel = _maybe_import_peft()
    if LoraConfig is None or get_peft_model is None or PeftModel is None:
        return model

    if lora_path:
        from urllib.parse import urlparse

        parsed = urlparse(lora_path)
        is_remote = bool(parsed.scheme) or lora_path.count("/") == 1
        if not is_remote:
            lp = Path(lora_path)
            if not lp.exists():
                raise FileNotFoundError(f"LoRA path '{lora_path}' does not exist")
        try:  # pragma: no cover - optional dependency may fail
            return PeftModel.from_pretrained(model, lora_path)
        except Exception:
            return model

    TaskType = None
    try:  # pragma: no cover - optional enum
        from peft import TaskType as _TaskType  # type: ignore

        TaskType = _TaskType
    except Exception:
        TaskType = None

    cfg_kwargs: dict[str, Any] = {
        "r": lora_r,
        "lora_alpha": lora_alpha,
        "lora_dropout": lora_dropout,
        "target_modules": lora_target_modules or ["qkv", "proj", "fc1", "fc2"],
    }
    task_type_value: Any = TaskType.CAUSAL_LM if TaskType is not None else "CAUSAL_LM"
    cfg = None
    try:
        cfg = LoraConfig(task_type=task_type_value, **cfg_kwargs)  # type: ignore[call-arg]
    except TypeError:
        cfg = LoraConfig(**cfg_kwargs)  # type: ignore[call-arg]

    return get_peft_model(model, cfg)  # type: ignore[misc]
