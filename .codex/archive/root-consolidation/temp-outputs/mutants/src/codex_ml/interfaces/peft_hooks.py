"""Guarded PEFT/LoRA helper utilities."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from dataclasses import dataclass  # noqa: E402
from typing import Any  # noqa: E402

try:  # pragma: no cover - optional dependency
    from peft import LoraConfig, PeftModel, TaskType, get_peft_model
except (ImportError, AttributeError):  # pragma: no cover - gracefully degrade when peft unavailable
    LoraConfig = None
    PeftModel = None
    TaskType = None
    get_peft_model = None

__all__ = [
    "build_peft_config",
    "enable_peft",
    "ensure_peft_available",
    "load_adapter_for_inference",
]


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
    return LoraConfig(
        task_type=task_type,
        r=r,
        lora_alpha=alpha,
        lora_dropout=dropout,
        inference_mode=False,
    )


def enable_peft(model: Any, peft_cfg: Any, adapter_name: str = "lora") -> Any:
    """Wrap ``model`` with a PEFT adapter when available."""

    ensure_peft_available()
    adapted = get_peft_model(model, peft_cfg, adapter_name=adapter_name)
    try:  # pragma: no cover - optional diagnostics
        adapted.print_trainable_parameters()
    except (IOError, OSError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        logger.warning("Exception: <ERROR_TYPE>", exc_info=True)
    return adapted


def load_adapter_for_inference(model: Any, adapter_path: str) -> Any:
    """Load an inference adapter via ``peft.PeftModel`` when available."""

    ensure_peft_available()
    if PeftModel is None:  # pragma: no cover - defensive guard
        raise PeftUnavailable("peft.PeftModel unavailable")
    return PeftModel.from_pretrained(model, adapter_path)
