"""LoRA adapter shim that behaves sensibly without the peft dependency."""

from __future__ import annotations

from typing import Any, Mapping

__all__ = ["apply_lora"]


def apply_lora(model: Any, config: Mapping[str, Any]) -> Any:
    """Return ``model`` when peft is unavailable; otherwise delegate."""

    try:  # pragma: no cover - optional dependency
        from peft import LoraConfig, get_peft_model  # type: ignore

        lora_cfg = LoraConfig(**{str(k): v for k, v in config.items()})
        return get_peft_model(model, lora_cfg)
    except Exception:
        return model
