"""Utility helpers for optional model integrations (e.g., PEFT)."""

from .peft import apply_lora_if_available

__all__ = ["apply_lora_if_available"]
