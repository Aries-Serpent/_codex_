"""
Peft Module

This module provides functionality for peft.

Usage:
    from utils.peft import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


from collections.abc import Iterable, Sequence  # noqa: E402
from typing import TYPE_CHECKING, Any, Optional  # noqa: E402

if TYPE_CHECKING:  # pragma: no cover - typing only
    from peft import TaskType

DEFAULT_TASK_TYPE = "CAUSAL_LM"


def apply_lora_if_available(
    model: Any,
    *,
    r: int = 8,
    alpha: int = 16,
    dropout: float = 0.05,
    task_type: Optional[TaskType | str] = None,
    target_modules: Optional[Iterable[str]] = None,
) -> Any:
    """Wrap ``model`` with LoRA adapters when ``peft`` is installed.

    The helper keeps LoRA strictly optional—if ``peft`` (and its dependencies)
    are unavailable the function simply returns ``model`` unchanged. This keeps
    training code paths offline-friendly while enabling quick experimentation
    when the dependency is present.
    """

    try:  # pragma: no cover - optional dependency
        from peft import LoraConfig, TaskType, get_peft_model
    except Exception:  # pragma: no cover - dependency missing
        return model

    selected_task_type: TaskType | str = task_type or DEFAULT_TASK_TYPE
    if isinstance(selected_task_type, str):
        try:
            selected_task_type = TaskType[selected_task_type]
        except KeyError as e:
            logger.debug(f"KeyError: {e}")
            logger.warning(f"KeyError: {e}", exc_info=True)
            selected_task_type = TaskType(selected_task_type)

    modules: Optional[Sequence[str]]
    modules = None if target_modules is None else tuple(str(module) for module in target_modules)

    cfg = LoraConfig(
        r=r,
        lora_alpha=alpha,
        lora_dropout=dropout,
        bias="none",
        task_type=selected_task_type,
        target_modules=modules,
    )
    return get_peft_model(model, cfg)


__all__ = ["apply_lora_if_available"]
