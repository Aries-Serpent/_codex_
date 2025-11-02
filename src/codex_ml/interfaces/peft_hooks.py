"""Guarded PEFT/LoRA helper utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:  # pragma: no cover - optional dependency
    from peft import LoraConfig, PeftModel, TaskType, get_peft_model
except Exception:  # pragma: no cover - gracefully degrade when peft unavailable
    LoraConfig = None  # type: ignore[assignment]
    PeftModel = None  # type: ignore[assignment]
    TaskType = None  # type: ignore[assignment]
    get_peft_model = None  # type: ignore[assignment]

__all__ = ["build_peft_config", "enable_peft", "load_adapter_for_inference", "ensure_peft_available"]


@dataclass(frozen=True)
class PeftUnavailable(RuntimeError):
    """Raised when PEFT helpers are used without the dependency installed."""

    reason: str = "peft is not installed"

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.reason


def ensure_peft_available() -> None:
    if LoraConfig is None or get_peft_model is None or TaskType is None:
        raise PeftUnavailable()


def build_peft_config(
    task: str = "CAUSAL_LM",
    r: int = 8,
    alpha: int = 32,
    dropout: float = 0.1,
) -> Any:
    """Construct a ``peft.LoraConfig`` when PEFT is available."""

    ensure_peft_available()
    task_type = getattr(TaskType, task)
    return LoraConfig(  # type: ignore[operator]
        task_type=task_type,
        r=r,
        lora_alpha=alpha,
        lora_dropout=dropout,
        inference_mode=False,
    )


def enable_peft(model: Any, peft_cfg: Any, adapter_name: str = "lora") -> Any:
    """Wrap ``model`` with a PEFT adapter when available."""

    ensure_peft_available()
    adapted = get_peft_model(model, peft_cfg, adapter_name=adapter_name)  # type: ignore[misc]
    try:  # pragma: no cover - optional diagnostics
        adapted.print_trainable_parameters()
    except Exception:
        pass
    return adapted


def load_adapter_for_inference(model: Any, adapter_path: str) -> Any:
    """Load an inference adapter via ``peft.PeftModel`` when available."""

    ensure_peft_available()
    if PeftModel is None:  # pragma: no cover - defensive guard
        raise PeftUnavailable("peft.PeftModel unavailable")
    return PeftModel.from_pretrained(model, adapter_path)
