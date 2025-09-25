"""Optional PEFT/LoRA integration helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Union

if TYPE_CHECKING:  # pragma: no cover - typing only
    from peft import TaskType  # type: ignore

DEFAULT_TASK_TYPE = "CAUSAL_LM"


def apply_lora_if_available(
    model: Any,
    *,
    r: int = 8,
    alpha: int = 16,
    dropout: float = 0.05,
    task_type: Optional[Union["TaskType", str]] = None,
) -> Any:
    """Wrap ``model`` with LoRA adapters when ``peft`` is installed.

    The helper keeps LoRA strictly optional—if ``peft`` (and its dependencies)
    are unavailable the function simply returns ``model`` unchanged. This keeps
    training code paths offline-friendly while enabling quick experimentation
    when the dependency is present.
    """

    try:  # pragma: no cover - optional dependency
        from peft import LoraConfig, TaskType, get_peft_model  # type: ignore
    except Exception:  # pragma: no cover - dependency missing
        return model

    selected_task_type: Union["TaskType", str] = task_type or DEFAULT_TASK_TYPE
    if isinstance(selected_task_type, str):
        try:
            selected_task_type = TaskType[selected_task_type]
        except KeyError:
            selected_task_type = TaskType(selected_task_type)

    cfg = LoraConfig(
        r=r,
        lora_alpha=alpha,
        lora_dropout=dropout,
        bias="none",
        task_type=selected_task_type,
    )
    return get_peft_model(model, cfg)


__all__ = ["apply_lora_if_available"]
