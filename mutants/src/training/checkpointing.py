"""
Checkpointing Module

This module provides functionality for checkpointing.

Usage:
    from training.checkpointing import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import inspect
import json
import logging
logger = logging.getLogger(__name__)
import math
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

try:  # pragma: no cover - torch is optional in minimal environments
    import torch
except Exception:  # pragma: no cover - gracefully degrade when torch missing
    torch = None  # type: ignore[assignment]


LOGGER = logging.getLogger(__name__)
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


def x__extract_lora_state__mutmut_orig(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_1(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is not None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_2(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning(None, exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_3(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=None)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_4(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning(exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_5(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", )
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_6(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("XXException occurredXX", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_7(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_8(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("EXCEPTION OCCURRED", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_9(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=False)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_10(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning(None, exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_11(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=None)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_12(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning(exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_13(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", )
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_14(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("XXException occurredXX", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_15(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_16(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("EXCEPTION OCCURRED", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_17(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=False)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_18(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = None
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_19(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(None)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_20(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug(None, exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_21(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", None)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_22(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug(exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_23(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", )
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_24(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("XXUnable to capture LoRA state: %sXX", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_25(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("unable to capture lora state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_26(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("UNABLE TO CAPTURE LORA STATE: %S", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_27(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) and not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_28(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_29(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_30(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = None
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_31(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = None
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_32(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") or hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_33(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(None, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_34(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, None) and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_35(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr("detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_36(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, ) and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_37(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "XXdetachXX") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_38(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "DETACH") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_39(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(None, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_40(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, None):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_41(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr("cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_42(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, ):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_43(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "XXcpuXX"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_44(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "CPU"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_45(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = None
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_46(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug(None, key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_47(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", None, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_48(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, None)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_49(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug(key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_50(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_51(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, )
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_52(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("XXFailed to detach/move tensor to CPU for key %s: %sXX", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_53(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("failed to detach/move tensor to cpu for key %s: %s", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_54(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("FAILED TO DETACH/MOVE TENSOR TO CPU FOR KEY %S: %S", key, exc)
        cpu_state[str(key)] = tensor
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_55(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(key)] = None
    return cpu_state if cpu_state else None


def x__extract_lora_state__mutmut_56(model: Any) -> dict[str, Any] | None:
    """Return a CPU copy of the LoRA/PEFT state when available."""

    if torch is None:
        return None
    try:  # pragma: no cover - optional dependency
        from peft import get_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None
    try:
        state = get_peft_model_state_dict(model)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Unable to capture LoRA state: %s", exc)
        return None
    if not isinstance(state, Mapping) or not state:
        return None
    cpu_state: dict[str, Any] = {}
    for key, value in state.items():
        tensor = value
        try:
            if hasattr(tensor, "detach") and hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
        except Exception as exc:  # pragma: no cover - optional conversion failures
            LOGGER.debug("Failed to detach/move tensor to CPU for key %s: %s", key, exc)
        cpu_state[str(None)] = tensor
    return cpu_state if cpu_state else None

x__extract_lora_state__mutmut_mutants : ClassVar[MutantDict] = {
'x__extract_lora_state__mutmut_1': x__extract_lora_state__mutmut_1, 
    'x__extract_lora_state__mutmut_2': x__extract_lora_state__mutmut_2, 
    'x__extract_lora_state__mutmut_3': x__extract_lora_state__mutmut_3, 
    'x__extract_lora_state__mutmut_4': x__extract_lora_state__mutmut_4, 
    'x__extract_lora_state__mutmut_5': x__extract_lora_state__mutmut_5, 
    'x__extract_lora_state__mutmut_6': x__extract_lora_state__mutmut_6, 
    'x__extract_lora_state__mutmut_7': x__extract_lora_state__mutmut_7, 
    'x__extract_lora_state__mutmut_8': x__extract_lora_state__mutmut_8, 
    'x__extract_lora_state__mutmut_9': x__extract_lora_state__mutmut_9, 
    'x__extract_lora_state__mutmut_10': x__extract_lora_state__mutmut_10, 
    'x__extract_lora_state__mutmut_11': x__extract_lora_state__mutmut_11, 
    'x__extract_lora_state__mutmut_12': x__extract_lora_state__mutmut_12, 
    'x__extract_lora_state__mutmut_13': x__extract_lora_state__mutmut_13, 
    'x__extract_lora_state__mutmut_14': x__extract_lora_state__mutmut_14, 
    'x__extract_lora_state__mutmut_15': x__extract_lora_state__mutmut_15, 
    'x__extract_lora_state__mutmut_16': x__extract_lora_state__mutmut_16, 
    'x__extract_lora_state__mutmut_17': x__extract_lora_state__mutmut_17, 
    'x__extract_lora_state__mutmut_18': x__extract_lora_state__mutmut_18, 
    'x__extract_lora_state__mutmut_19': x__extract_lora_state__mutmut_19, 
    'x__extract_lora_state__mutmut_20': x__extract_lora_state__mutmut_20, 
    'x__extract_lora_state__mutmut_21': x__extract_lora_state__mutmut_21, 
    'x__extract_lora_state__mutmut_22': x__extract_lora_state__mutmut_22, 
    'x__extract_lora_state__mutmut_23': x__extract_lora_state__mutmut_23, 
    'x__extract_lora_state__mutmut_24': x__extract_lora_state__mutmut_24, 
    'x__extract_lora_state__mutmut_25': x__extract_lora_state__mutmut_25, 
    'x__extract_lora_state__mutmut_26': x__extract_lora_state__mutmut_26, 
    'x__extract_lora_state__mutmut_27': x__extract_lora_state__mutmut_27, 
    'x__extract_lora_state__mutmut_28': x__extract_lora_state__mutmut_28, 
    'x__extract_lora_state__mutmut_29': x__extract_lora_state__mutmut_29, 
    'x__extract_lora_state__mutmut_30': x__extract_lora_state__mutmut_30, 
    'x__extract_lora_state__mutmut_31': x__extract_lora_state__mutmut_31, 
    'x__extract_lora_state__mutmut_32': x__extract_lora_state__mutmut_32, 
    'x__extract_lora_state__mutmut_33': x__extract_lora_state__mutmut_33, 
    'x__extract_lora_state__mutmut_34': x__extract_lora_state__mutmut_34, 
    'x__extract_lora_state__mutmut_35': x__extract_lora_state__mutmut_35, 
    'x__extract_lora_state__mutmut_36': x__extract_lora_state__mutmut_36, 
    'x__extract_lora_state__mutmut_37': x__extract_lora_state__mutmut_37, 
    'x__extract_lora_state__mutmut_38': x__extract_lora_state__mutmut_38, 
    'x__extract_lora_state__mutmut_39': x__extract_lora_state__mutmut_39, 
    'x__extract_lora_state__mutmut_40': x__extract_lora_state__mutmut_40, 
    'x__extract_lora_state__mutmut_41': x__extract_lora_state__mutmut_41, 
    'x__extract_lora_state__mutmut_42': x__extract_lora_state__mutmut_42, 
    'x__extract_lora_state__mutmut_43': x__extract_lora_state__mutmut_43, 
    'x__extract_lora_state__mutmut_44': x__extract_lora_state__mutmut_44, 
    'x__extract_lora_state__mutmut_45': x__extract_lora_state__mutmut_45, 
    'x__extract_lora_state__mutmut_46': x__extract_lora_state__mutmut_46, 
    'x__extract_lora_state__mutmut_47': x__extract_lora_state__mutmut_47, 
    'x__extract_lora_state__mutmut_48': x__extract_lora_state__mutmut_48, 
    'x__extract_lora_state__mutmut_49': x__extract_lora_state__mutmut_49, 
    'x__extract_lora_state__mutmut_50': x__extract_lora_state__mutmut_50, 
    'x__extract_lora_state__mutmut_51': x__extract_lora_state__mutmut_51, 
    'x__extract_lora_state__mutmut_52': x__extract_lora_state__mutmut_52, 
    'x__extract_lora_state__mutmut_53': x__extract_lora_state__mutmut_53, 
    'x__extract_lora_state__mutmut_54': x__extract_lora_state__mutmut_54, 
    'x__extract_lora_state__mutmut_55': x__extract_lora_state__mutmut_55, 
    'x__extract_lora_state__mutmut_56': x__extract_lora_state__mutmut_56
}

def _extract_lora_state(*args, **kwargs):
    result = _mutmut_trampoline(x__extract_lora_state__mutmut_orig, x__extract_lora_state__mutmut_mutants, args, kwargs)
    return result 

_extract_lora_state.__signature__ = _mutmut_signature(x__extract_lora_state__mutmut_orig)
x__extract_lora_state__mutmut_orig.__name__ = 'x__extract_lora_state'


def x__restore_lora_state__mutmut_orig(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_1(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is not None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_2(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = None
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_3(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get(None)
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_4(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("XXpeft_stateXX")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_5(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("PEFT_STATE")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_6(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_7(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning(None, exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_8(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=None)
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_9(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning(exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_10(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", )
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_11(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("XXException occurredXX", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_12(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_13(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("EXCEPTION OCCURRED", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_14(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=False)
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_15(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning(None, exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_16(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=None)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_17(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning(exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_18(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", )
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_19(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("XXException occurredXX", exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_20(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("exception occurred", exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_21(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("EXCEPTION OCCURRED", exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_22(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=False)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_23(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug(None)
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_24(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug("XXpeft not available; skipping LoRA restoreXX")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_25(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug("peft not available; skipping lora restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_26(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug("PEFT NOT AVAILABLE; SKIPPING LORA RESTORE")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_27(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(None, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_28(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, None)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_29(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_30(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, )
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_31(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(None))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", exc)


def x__restore_lora_state__mutmut_32(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug(None, exc)


def x__restore_lora_state__mutmut_33(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", None)


def x__restore_lora_state__mutmut_34(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug(exc)


def x__restore_lora_state__mutmut_35(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to restore LoRA weights: %s", )


def x__restore_lora_state__mutmut_36(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("XXFailed to restore LoRA weights: %sXX", exc)


def x__restore_lora_state__mutmut_37(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("failed to restore lora weights: %s", exc)


def x__restore_lora_state__mutmut_38(model: Any, payload: Mapping[str, Any]) -> None:
    if torch is None:
        return
    lora_state = payload.get("peft_state")
    if not isinstance(lora_state, Mapping):
        return
    try:  # pragma: no cover - optional dependency
        from peft import set_peft_model_state_dict
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        LOGGER.debug("peft not available; skipping LoRA restore")
        return
    try:
        set_peft_model_state_dict(model, dict(lora_state))
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("FAILED TO RESTORE LORA WEIGHTS: %S", exc)

x__restore_lora_state__mutmut_mutants : ClassVar[MutantDict] = {
'x__restore_lora_state__mutmut_1': x__restore_lora_state__mutmut_1, 
    'x__restore_lora_state__mutmut_2': x__restore_lora_state__mutmut_2, 
    'x__restore_lora_state__mutmut_3': x__restore_lora_state__mutmut_3, 
    'x__restore_lora_state__mutmut_4': x__restore_lora_state__mutmut_4, 
    'x__restore_lora_state__mutmut_5': x__restore_lora_state__mutmut_5, 
    'x__restore_lora_state__mutmut_6': x__restore_lora_state__mutmut_6, 
    'x__restore_lora_state__mutmut_7': x__restore_lora_state__mutmut_7, 
    'x__restore_lora_state__mutmut_8': x__restore_lora_state__mutmut_8, 
    'x__restore_lora_state__mutmut_9': x__restore_lora_state__mutmut_9, 
    'x__restore_lora_state__mutmut_10': x__restore_lora_state__mutmut_10, 
    'x__restore_lora_state__mutmut_11': x__restore_lora_state__mutmut_11, 
    'x__restore_lora_state__mutmut_12': x__restore_lora_state__mutmut_12, 
    'x__restore_lora_state__mutmut_13': x__restore_lora_state__mutmut_13, 
    'x__restore_lora_state__mutmut_14': x__restore_lora_state__mutmut_14, 
    'x__restore_lora_state__mutmut_15': x__restore_lora_state__mutmut_15, 
    'x__restore_lora_state__mutmut_16': x__restore_lora_state__mutmut_16, 
    'x__restore_lora_state__mutmut_17': x__restore_lora_state__mutmut_17, 
    'x__restore_lora_state__mutmut_18': x__restore_lora_state__mutmut_18, 
    'x__restore_lora_state__mutmut_19': x__restore_lora_state__mutmut_19, 
    'x__restore_lora_state__mutmut_20': x__restore_lora_state__mutmut_20, 
    'x__restore_lora_state__mutmut_21': x__restore_lora_state__mutmut_21, 
    'x__restore_lora_state__mutmut_22': x__restore_lora_state__mutmut_22, 
    'x__restore_lora_state__mutmut_23': x__restore_lora_state__mutmut_23, 
    'x__restore_lora_state__mutmut_24': x__restore_lora_state__mutmut_24, 
    'x__restore_lora_state__mutmut_25': x__restore_lora_state__mutmut_25, 
    'x__restore_lora_state__mutmut_26': x__restore_lora_state__mutmut_26, 
    'x__restore_lora_state__mutmut_27': x__restore_lora_state__mutmut_27, 
    'x__restore_lora_state__mutmut_28': x__restore_lora_state__mutmut_28, 
    'x__restore_lora_state__mutmut_29': x__restore_lora_state__mutmut_29, 
    'x__restore_lora_state__mutmut_30': x__restore_lora_state__mutmut_30, 
    'x__restore_lora_state__mutmut_31': x__restore_lora_state__mutmut_31, 
    'x__restore_lora_state__mutmut_32': x__restore_lora_state__mutmut_32, 
    'x__restore_lora_state__mutmut_33': x__restore_lora_state__mutmut_33, 
    'x__restore_lora_state__mutmut_34': x__restore_lora_state__mutmut_34, 
    'x__restore_lora_state__mutmut_35': x__restore_lora_state__mutmut_35, 
    'x__restore_lora_state__mutmut_36': x__restore_lora_state__mutmut_36, 
    'x__restore_lora_state__mutmut_37': x__restore_lora_state__mutmut_37, 
    'x__restore_lora_state__mutmut_38': x__restore_lora_state__mutmut_38
}

def _restore_lora_state(*args, **kwargs):
    result = _mutmut_trampoline(x__restore_lora_state__mutmut_orig, x__restore_lora_state__mutmut_mutants, args, kwargs)
    return result 

_restore_lora_state.__signature__ = _mutmut_signature(x__restore_lora_state__mutmut_orig)
x__restore_lora_state__mutmut_orig.__name__ = 'x__restore_lora_state'


def x__torch_supports_weights_only__mutmut_orig() -> bool:
    if torch is None:
        return False
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        return False
    try:
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_1() -> bool:
    if torch is not None:
        return False
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        return False
    try:
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_2() -> bool:
    if torch is None:
        return True
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        return False
    try:
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_3() -> bool:
    if torch is None:
        return False
    load_fn = None
    if load_fn is None:
        return False
    try:
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_4() -> bool:
    if torch is None:
        return False
    load_fn = getattr(None, "load", None)
    if load_fn is None:
        return False
    try:
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_5() -> bool:
    if torch is None:
        return False
    load_fn = getattr(torch, None, None)
    if load_fn is None:
        return False
    try:
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_6() -> bool:
    if torch is None:
        return False
    load_fn = getattr("load", None)
    if load_fn is None:
        return False
    try:
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_7() -> bool:
    if torch is None:
        return False
    load_fn = getattr(torch, None)
    if load_fn is None:
        return False
    try:
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_8() -> bool:
    if torch is None:
        return False
    load_fn = getattr(torch, "load", )
    if load_fn is None:
        return False
    try:
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_9() -> bool:
    if torch is None:
        return False
    load_fn = getattr(torch, "XXloadXX", None)
    if load_fn is None:
        return False
    try:
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_10() -> bool:
    if torch is None:
        return False
    load_fn = getattr(torch, "LOAD", None)
    if load_fn is None:
        return False
    try:
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_11() -> bool:
    if torch is None:
        return False
    load_fn = getattr(torch, "load", None)
    if load_fn is not None:
        return False
    try:
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_12() -> bool:
    if torch is None:
        return False
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        return True
    try:
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_13() -> bool:
    if torch is None:
        return False
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        return False
    try:
        signature = None
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_14() -> bool:
    if torch is None:
        return False
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        return False
    try:
        signature = inspect.signature(None)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_15() -> bool:
    if torch is None:
        return False
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        return False
    try:
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return True
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_16() -> bool:
    if torch is None:
        return False
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        return False
    try:
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "XXweights_onlyXX" in signature.parameters


def x__torch_supports_weights_only__mutmut_17() -> bool:
    if torch is None:
        return False
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        return False
    try:
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "WEIGHTS_ONLY" in signature.parameters


def x__torch_supports_weights_only__mutmut_18() -> bool:
    if torch is None:
        return False
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        return False
    try:
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" not in signature.parameters

x__torch_supports_weights_only__mutmut_mutants : ClassVar[MutantDict] = {
'x__torch_supports_weights_only__mutmut_1': x__torch_supports_weights_only__mutmut_1, 
    'x__torch_supports_weights_only__mutmut_2': x__torch_supports_weights_only__mutmut_2, 
    'x__torch_supports_weights_only__mutmut_3': x__torch_supports_weights_only__mutmut_3, 
    'x__torch_supports_weights_only__mutmut_4': x__torch_supports_weights_only__mutmut_4, 
    'x__torch_supports_weights_only__mutmut_5': x__torch_supports_weights_only__mutmut_5, 
    'x__torch_supports_weights_only__mutmut_6': x__torch_supports_weights_only__mutmut_6, 
    'x__torch_supports_weights_only__mutmut_7': x__torch_supports_weights_only__mutmut_7, 
    'x__torch_supports_weights_only__mutmut_8': x__torch_supports_weights_only__mutmut_8, 
    'x__torch_supports_weights_only__mutmut_9': x__torch_supports_weights_only__mutmut_9, 
    'x__torch_supports_weights_only__mutmut_10': x__torch_supports_weights_only__mutmut_10, 
    'x__torch_supports_weights_only__mutmut_11': x__torch_supports_weights_only__mutmut_11, 
    'x__torch_supports_weights_only__mutmut_12': x__torch_supports_weights_only__mutmut_12, 
    'x__torch_supports_weights_only__mutmut_13': x__torch_supports_weights_only__mutmut_13, 
    'x__torch_supports_weights_only__mutmut_14': x__torch_supports_weights_only__mutmut_14, 
    'x__torch_supports_weights_only__mutmut_15': x__torch_supports_weights_only__mutmut_15, 
    'x__torch_supports_weights_only__mutmut_16': x__torch_supports_weights_only__mutmut_16, 
    'x__torch_supports_weights_only__mutmut_17': x__torch_supports_weights_only__mutmut_17, 
    'x__torch_supports_weights_only__mutmut_18': x__torch_supports_weights_only__mutmut_18
}

def _torch_supports_weights_only(*args, **kwargs):
    result = _mutmut_trampoline(x__torch_supports_weights_only__mutmut_orig, x__torch_supports_weights_only__mutmut_mutants, args, kwargs)
    return result 

_torch_supports_weights_only.__signature__ = _mutmut_signature(x__torch_supports_weights_only__mutmut_orig)
x__torch_supports_weights_only__mutmut_orig.__name__ = 'x__torch_supports_weights_only'


_TORCH_SUPPORTS_WEIGHTS_ONLY = _torch_supports_weights_only()


def x__torch_rng_get_state__mutmut_orig() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_1() -> Any:
    if torch is not None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_2() -> Any:
    if torch is None:
        raise RuntimeError(None)
    random_mod = getattr(torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_3() -> Any:
    if torch is None:
        raise RuntimeError("XXtorch is required to capture RNG stateXX")
    random_mod = getattr(torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_4() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture rng state")
    random_mod = getattr(torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_5() -> Any:
    if torch is None:
        raise RuntimeError("TORCH IS REQUIRED TO CAPTURE RNG STATE")
    random_mod = getattr(torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_6() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = None
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_7() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(None, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_8() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, None, None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_9() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr("random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_10() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_11() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, "random", )
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_12() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, "XXrandomXX", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_13() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, "RANDOM", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_14() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, "random", None)
    getter = None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_15() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, "random", None)
    getter = getattr(None, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_16() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, "random", None)
    getter = getattr(random_mod, None, None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_17() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, "random", None)
    getter = getattr("get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_18() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, "random", None)
    getter = getattr(random_mod, None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_19() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", ) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_20() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, "random", None)
    getter = getattr(random_mod, "XXget_rng_stateXX", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_21() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, "random", None)
    getter = getattr(random_mod, "GET_RNG_STATE", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_22() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_23() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(None):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_24() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = None
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_25() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(None, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_26() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, None, None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_27() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr("get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_28() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_29() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", )
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_30() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "XXget_rng_stateXX", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_31() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "GET_RNG_STATE", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_32() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", None)
    if callable(None):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_33() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError(None)


def x__torch_rng_get_state__mutmut_34() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("XXCurrent torch build lacks RNG state APIsXX")


def x__torch_rng_get_state__mutmut_35() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("current torch build lacks rng state apis")


def x__torch_rng_get_state__mutmut_36() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("CURRENT TORCH BUILD LACKS RNG STATE APIS")

x__torch_rng_get_state__mutmut_mutants : ClassVar[MutantDict] = {
'x__torch_rng_get_state__mutmut_1': x__torch_rng_get_state__mutmut_1, 
    'x__torch_rng_get_state__mutmut_2': x__torch_rng_get_state__mutmut_2, 
    'x__torch_rng_get_state__mutmut_3': x__torch_rng_get_state__mutmut_3, 
    'x__torch_rng_get_state__mutmut_4': x__torch_rng_get_state__mutmut_4, 
    'x__torch_rng_get_state__mutmut_5': x__torch_rng_get_state__mutmut_5, 
    'x__torch_rng_get_state__mutmut_6': x__torch_rng_get_state__mutmut_6, 
    'x__torch_rng_get_state__mutmut_7': x__torch_rng_get_state__mutmut_7, 
    'x__torch_rng_get_state__mutmut_8': x__torch_rng_get_state__mutmut_8, 
    'x__torch_rng_get_state__mutmut_9': x__torch_rng_get_state__mutmut_9, 
    'x__torch_rng_get_state__mutmut_10': x__torch_rng_get_state__mutmut_10, 
    'x__torch_rng_get_state__mutmut_11': x__torch_rng_get_state__mutmut_11, 
    'x__torch_rng_get_state__mutmut_12': x__torch_rng_get_state__mutmut_12, 
    'x__torch_rng_get_state__mutmut_13': x__torch_rng_get_state__mutmut_13, 
    'x__torch_rng_get_state__mutmut_14': x__torch_rng_get_state__mutmut_14, 
    'x__torch_rng_get_state__mutmut_15': x__torch_rng_get_state__mutmut_15, 
    'x__torch_rng_get_state__mutmut_16': x__torch_rng_get_state__mutmut_16, 
    'x__torch_rng_get_state__mutmut_17': x__torch_rng_get_state__mutmut_17, 
    'x__torch_rng_get_state__mutmut_18': x__torch_rng_get_state__mutmut_18, 
    'x__torch_rng_get_state__mutmut_19': x__torch_rng_get_state__mutmut_19, 
    'x__torch_rng_get_state__mutmut_20': x__torch_rng_get_state__mutmut_20, 
    'x__torch_rng_get_state__mutmut_21': x__torch_rng_get_state__mutmut_21, 
    'x__torch_rng_get_state__mutmut_22': x__torch_rng_get_state__mutmut_22, 
    'x__torch_rng_get_state__mutmut_23': x__torch_rng_get_state__mutmut_23, 
    'x__torch_rng_get_state__mutmut_24': x__torch_rng_get_state__mutmut_24, 
    'x__torch_rng_get_state__mutmut_25': x__torch_rng_get_state__mutmut_25, 
    'x__torch_rng_get_state__mutmut_26': x__torch_rng_get_state__mutmut_26, 
    'x__torch_rng_get_state__mutmut_27': x__torch_rng_get_state__mutmut_27, 
    'x__torch_rng_get_state__mutmut_28': x__torch_rng_get_state__mutmut_28, 
    'x__torch_rng_get_state__mutmut_29': x__torch_rng_get_state__mutmut_29, 
    'x__torch_rng_get_state__mutmut_30': x__torch_rng_get_state__mutmut_30, 
    'x__torch_rng_get_state__mutmut_31': x__torch_rng_get_state__mutmut_31, 
    'x__torch_rng_get_state__mutmut_32': x__torch_rng_get_state__mutmut_32, 
    'x__torch_rng_get_state__mutmut_33': x__torch_rng_get_state__mutmut_33, 
    'x__torch_rng_get_state__mutmut_34': x__torch_rng_get_state__mutmut_34, 
    'x__torch_rng_get_state__mutmut_35': x__torch_rng_get_state__mutmut_35, 
    'x__torch_rng_get_state__mutmut_36': x__torch_rng_get_state__mutmut_36
}

def _torch_rng_get_state(*args, **kwargs):
    result = _mutmut_trampoline(x__torch_rng_get_state__mutmut_orig, x__torch_rng_get_state__mutmut_mutants, args, kwargs)
    return result 

_torch_rng_get_state.__signature__ = _mutmut_signature(x__torch_rng_get_state__mutmut_orig)
x__torch_rng_get_state__mutmut_orig.__name__ = 'x__torch_rng_get_state'


def x__torch_rng_set_state__mutmut_orig(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_1(state: Any) -> None:
    if torch is not None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_2(state: Any) -> None:
    if torch is None:
        raise RuntimeError(None)
    random_mod = getattr(torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_3(state: Any) -> None:
    if torch is None:
        raise RuntimeError("XXtorch is required to restore RNG stateXX")
    random_mod = getattr(torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_4(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore rng state")
    random_mod = getattr(torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_5(state: Any) -> None:
    if torch is None:
        raise RuntimeError("TORCH IS REQUIRED TO RESTORE RNG STATE")
    random_mod = getattr(torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_6(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = None
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_7(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(None, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_8(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, None, None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_9(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr("random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_10(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_11(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "random", )
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_12(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "XXrandomXX", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_13(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "RANDOM", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_14(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "random", None)
    setter = None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_15(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "random", None)
    setter = getattr(None, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_16(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "random", None)
    setter = getattr(random_mod, None, None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_17(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "random", None)
    setter = getattr("set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_18(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "random", None)
    setter = getattr(random_mod, None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_19(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", ) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_20(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "random", None)
    setter = getattr(random_mod, "XXset_rng_stateXX", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_21(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "random", None)
    setter = getattr(random_mod, "SET_RNG_STATE", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_22(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_23(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(None):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_24(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(None)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_25(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = None
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_26(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(None, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_27(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, None, None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_28(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr("set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_29(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_30(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", )
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_31(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "XXset_rng_stateXX", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_32(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "SET_RNG_STATE", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_33(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(None):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_34(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(None)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_35(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError(None)


def x__torch_rng_set_state__mutmut_36(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("XXCurrent torch build lacks RNG state APIsXX")


def x__torch_rng_set_state__mutmut_37(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("current torch build lacks rng state apis")


def x__torch_rng_set_state__mutmut_38(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("CURRENT TORCH BUILD LACKS RNG STATE APIS")

x__torch_rng_set_state__mutmut_mutants : ClassVar[MutantDict] = {
'x__torch_rng_set_state__mutmut_1': x__torch_rng_set_state__mutmut_1, 
    'x__torch_rng_set_state__mutmut_2': x__torch_rng_set_state__mutmut_2, 
    'x__torch_rng_set_state__mutmut_3': x__torch_rng_set_state__mutmut_3, 
    'x__torch_rng_set_state__mutmut_4': x__torch_rng_set_state__mutmut_4, 
    'x__torch_rng_set_state__mutmut_5': x__torch_rng_set_state__mutmut_5, 
    'x__torch_rng_set_state__mutmut_6': x__torch_rng_set_state__mutmut_6, 
    'x__torch_rng_set_state__mutmut_7': x__torch_rng_set_state__mutmut_7, 
    'x__torch_rng_set_state__mutmut_8': x__torch_rng_set_state__mutmut_8, 
    'x__torch_rng_set_state__mutmut_9': x__torch_rng_set_state__mutmut_9, 
    'x__torch_rng_set_state__mutmut_10': x__torch_rng_set_state__mutmut_10, 
    'x__torch_rng_set_state__mutmut_11': x__torch_rng_set_state__mutmut_11, 
    'x__torch_rng_set_state__mutmut_12': x__torch_rng_set_state__mutmut_12, 
    'x__torch_rng_set_state__mutmut_13': x__torch_rng_set_state__mutmut_13, 
    'x__torch_rng_set_state__mutmut_14': x__torch_rng_set_state__mutmut_14, 
    'x__torch_rng_set_state__mutmut_15': x__torch_rng_set_state__mutmut_15, 
    'x__torch_rng_set_state__mutmut_16': x__torch_rng_set_state__mutmut_16, 
    'x__torch_rng_set_state__mutmut_17': x__torch_rng_set_state__mutmut_17, 
    'x__torch_rng_set_state__mutmut_18': x__torch_rng_set_state__mutmut_18, 
    'x__torch_rng_set_state__mutmut_19': x__torch_rng_set_state__mutmut_19, 
    'x__torch_rng_set_state__mutmut_20': x__torch_rng_set_state__mutmut_20, 
    'x__torch_rng_set_state__mutmut_21': x__torch_rng_set_state__mutmut_21, 
    'x__torch_rng_set_state__mutmut_22': x__torch_rng_set_state__mutmut_22, 
    'x__torch_rng_set_state__mutmut_23': x__torch_rng_set_state__mutmut_23, 
    'x__torch_rng_set_state__mutmut_24': x__torch_rng_set_state__mutmut_24, 
    'x__torch_rng_set_state__mutmut_25': x__torch_rng_set_state__mutmut_25, 
    'x__torch_rng_set_state__mutmut_26': x__torch_rng_set_state__mutmut_26, 
    'x__torch_rng_set_state__mutmut_27': x__torch_rng_set_state__mutmut_27, 
    'x__torch_rng_set_state__mutmut_28': x__torch_rng_set_state__mutmut_28, 
    'x__torch_rng_set_state__mutmut_29': x__torch_rng_set_state__mutmut_29, 
    'x__torch_rng_set_state__mutmut_30': x__torch_rng_set_state__mutmut_30, 
    'x__torch_rng_set_state__mutmut_31': x__torch_rng_set_state__mutmut_31, 
    'x__torch_rng_set_state__mutmut_32': x__torch_rng_set_state__mutmut_32, 
    'x__torch_rng_set_state__mutmut_33': x__torch_rng_set_state__mutmut_33, 
    'x__torch_rng_set_state__mutmut_34': x__torch_rng_set_state__mutmut_34, 
    'x__torch_rng_set_state__mutmut_35': x__torch_rng_set_state__mutmut_35, 
    'x__torch_rng_set_state__mutmut_36': x__torch_rng_set_state__mutmut_36, 
    'x__torch_rng_set_state__mutmut_37': x__torch_rng_set_state__mutmut_37, 
    'x__torch_rng_set_state__mutmut_38': x__torch_rng_set_state__mutmut_38
}

def _torch_rng_set_state(*args, **kwargs):
    result = _mutmut_trampoline(x__torch_rng_set_state__mutmut_orig, x__torch_rng_set_state__mutmut_mutants, args, kwargs)
    return result 

_torch_rng_set_state.__signature__ = _mutmut_signature(x__torch_rng_set_state__mutmut_orig)
x__torch_rng_set_state__mutmut_orig.__name__ = 'x__torch_rng_set_state'


def x__torch_load__mutmut_orig(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_1(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is not None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_2(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError(None)
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_3(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("XXtorch is required to load checkpointsXX")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_4(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("TORCH IS REQUIRED TO LOAD CHECKPOINTS")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_5(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = None
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_6(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(None, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_7(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, None, None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_8(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr("load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_9(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_10(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", )
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_11(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "XXloadXX", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_12(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "LOAD", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_13(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is not None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_14(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError(None)
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_15(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("XXCurrent torch build does not expose torch.loadXX")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_16(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_17(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("CURRENT TORCH BUILD DOES NOT EXPOSE TORCH.LOAD")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_18(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = None
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_19(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_20(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = None
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_21(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["XXmap_locationXX"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_22(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["MAP_LOCATION"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_23(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = None
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_24(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["XXweights_onlyXX"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_25(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["WEIGHTS_ONLY"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_26(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = False
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_27(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(None, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_28(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(**kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_29(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, )
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_30(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(None, exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_31(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", None)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_32(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_33(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", )
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_34(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("XXTypeError: %sXX", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_35(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("typeerror: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_36(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TYPEERROR: %S", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_37(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY or "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_38(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "XXweights_onlyXX" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_39(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "WEIGHTS_ONLY" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_40(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" not in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_41(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(None):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_42(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop(None, None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_43(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop(None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_44(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", )
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_45(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("XXweights_onlyXX", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_46(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("WEIGHTS_ONLY", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_47(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(None, **kwargs)
        raise


def x__torch_load__mutmut_48(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(**kwargs)
        raise


def x__torch_load__mutmut_49(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug("TypeError: %s", exc)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, )
        raise

x__torch_load__mutmut_mutants : ClassVar[MutantDict] = {
'x__torch_load__mutmut_1': x__torch_load__mutmut_1, 
    'x__torch_load__mutmut_2': x__torch_load__mutmut_2, 
    'x__torch_load__mutmut_3': x__torch_load__mutmut_3, 
    'x__torch_load__mutmut_4': x__torch_load__mutmut_4, 
    'x__torch_load__mutmut_5': x__torch_load__mutmut_5, 
    'x__torch_load__mutmut_6': x__torch_load__mutmut_6, 
    'x__torch_load__mutmut_7': x__torch_load__mutmut_7, 
    'x__torch_load__mutmut_8': x__torch_load__mutmut_8, 
    'x__torch_load__mutmut_9': x__torch_load__mutmut_9, 
    'x__torch_load__mutmut_10': x__torch_load__mutmut_10, 
    'x__torch_load__mutmut_11': x__torch_load__mutmut_11, 
    'x__torch_load__mutmut_12': x__torch_load__mutmut_12, 
    'x__torch_load__mutmut_13': x__torch_load__mutmut_13, 
    'x__torch_load__mutmut_14': x__torch_load__mutmut_14, 
    'x__torch_load__mutmut_15': x__torch_load__mutmut_15, 
    'x__torch_load__mutmut_16': x__torch_load__mutmut_16, 
    'x__torch_load__mutmut_17': x__torch_load__mutmut_17, 
    'x__torch_load__mutmut_18': x__torch_load__mutmut_18, 
    'x__torch_load__mutmut_19': x__torch_load__mutmut_19, 
    'x__torch_load__mutmut_20': x__torch_load__mutmut_20, 
    'x__torch_load__mutmut_21': x__torch_load__mutmut_21, 
    'x__torch_load__mutmut_22': x__torch_load__mutmut_22, 
    'x__torch_load__mutmut_23': x__torch_load__mutmut_23, 
    'x__torch_load__mutmut_24': x__torch_load__mutmut_24, 
    'x__torch_load__mutmut_25': x__torch_load__mutmut_25, 
    'x__torch_load__mutmut_26': x__torch_load__mutmut_26, 
    'x__torch_load__mutmut_27': x__torch_load__mutmut_27, 
    'x__torch_load__mutmut_28': x__torch_load__mutmut_28, 
    'x__torch_load__mutmut_29': x__torch_load__mutmut_29, 
    'x__torch_load__mutmut_30': x__torch_load__mutmut_30, 
    'x__torch_load__mutmut_31': x__torch_load__mutmut_31, 
    'x__torch_load__mutmut_32': x__torch_load__mutmut_32, 
    'x__torch_load__mutmut_33': x__torch_load__mutmut_33, 
    'x__torch_load__mutmut_34': x__torch_load__mutmut_34, 
    'x__torch_load__mutmut_35': x__torch_load__mutmut_35, 
    'x__torch_load__mutmut_36': x__torch_load__mutmut_36, 
    'x__torch_load__mutmut_37': x__torch_load__mutmut_37, 
    'x__torch_load__mutmut_38': x__torch_load__mutmut_38, 
    'x__torch_load__mutmut_39': x__torch_load__mutmut_39, 
    'x__torch_load__mutmut_40': x__torch_load__mutmut_40, 
    'x__torch_load__mutmut_41': x__torch_load__mutmut_41, 
    'x__torch_load__mutmut_42': x__torch_load__mutmut_42, 
    'x__torch_load__mutmut_43': x__torch_load__mutmut_43, 
    'x__torch_load__mutmut_44': x__torch_load__mutmut_44, 
    'x__torch_load__mutmut_45': x__torch_load__mutmut_45, 
    'x__torch_load__mutmut_46': x__torch_load__mutmut_46, 
    'x__torch_load__mutmut_47': x__torch_load__mutmut_47, 
    'x__torch_load__mutmut_48': x__torch_load__mutmut_48, 
    'x__torch_load__mutmut_49': x__torch_load__mutmut_49
}

def _torch_load(*args, **kwargs):
    result = _mutmut_trampoline(x__torch_load__mutmut_orig, x__torch_load__mutmut_mutants, args, kwargs)
    return result 

_torch_load.__signature__ = _mutmut_signature(x__torch_load__mutmut_orig)
x__torch_load__mutmut_orig.__name__ = 'x__torch_load'


@dataclass
class RNGState:
    """Container capturing CPU and (optionally) CUDA RNG states."""

    cpu: torch.Tensor | None = None
    cuda_all: list[torch.Tensor] | None = None


def x_snapshot_rng_state__mutmut_orig() -> RNGState:
    """Snapshot the current RNG state for CPU and CUDA generators."""

    if torch is None:
        return RNGState()
    cpu_state = _torch_rng_get_state()
    cuda_state = None
    if hasattr(torch, "cuda") and torch.cuda.is_available():
        cuda_state = torch.cuda.get_rng_state_all()  # type: ignore[attr-defined]
    return RNGState(cpu=cpu_state, cuda_all=cuda_state)


def x_snapshot_rng_state__mutmut_1() -> RNGState:
    """Snapshot the current RNG state for CPU and CUDA generators."""

    if torch is not None:
        return RNGState()
    cpu_state = _torch_rng_get_state()
    cuda_state = None
    if hasattr(torch, "cuda") and torch.cuda.is_available():
        cuda_state = torch.cuda.get_rng_state_all()  # type: ignore[attr-defined]
    return RNGState(cpu=cpu_state, cuda_all=cuda_state)


def x_snapshot_rng_state__mutmut_2() -> RNGState:
    """Snapshot the current RNG state for CPU and CUDA generators."""

    if torch is None:
        return RNGState()
    cpu_state = None
    cuda_state = None
    if hasattr(torch, "cuda") and torch.cuda.is_available():
        cuda_state = torch.cuda.get_rng_state_all()  # type: ignore[attr-defined]
    return RNGState(cpu=cpu_state, cuda_all=cuda_state)


def x_snapshot_rng_state__mutmut_3() -> RNGState:
    """Snapshot the current RNG state for CPU and CUDA generators."""

    if torch is None:
        return RNGState()
    cpu_state = _torch_rng_get_state()
    cuda_state = ""
    if hasattr(torch, "cuda") and torch.cuda.is_available():
        cuda_state = torch.cuda.get_rng_state_all()  # type: ignore[attr-defined]
    return RNGState(cpu=cpu_state, cuda_all=cuda_state)


def x_snapshot_rng_state__mutmut_4() -> RNGState:
    """Snapshot the current RNG state for CPU and CUDA generators."""

    if torch is None:
        return RNGState()
    cpu_state = _torch_rng_get_state()
    cuda_state = None
    if hasattr(torch, "cuda") or torch.cuda.is_available():
        cuda_state = torch.cuda.get_rng_state_all()  # type: ignore[attr-defined]
    return RNGState(cpu=cpu_state, cuda_all=cuda_state)


def x_snapshot_rng_state__mutmut_5() -> RNGState:
    """Snapshot the current RNG state for CPU and CUDA generators."""

    if torch is None:
        return RNGState()
    cpu_state = _torch_rng_get_state()
    cuda_state = None
    if hasattr(None, "cuda") and torch.cuda.is_available():
        cuda_state = torch.cuda.get_rng_state_all()  # type: ignore[attr-defined]
    return RNGState(cpu=cpu_state, cuda_all=cuda_state)


def x_snapshot_rng_state__mutmut_6() -> RNGState:
    """Snapshot the current RNG state for CPU and CUDA generators."""

    if torch is None:
        return RNGState()
    cpu_state = _torch_rng_get_state()
    cuda_state = None
    if hasattr(torch, None) and torch.cuda.is_available():
        cuda_state = torch.cuda.get_rng_state_all()  # type: ignore[attr-defined]
    return RNGState(cpu=cpu_state, cuda_all=cuda_state)


def x_snapshot_rng_state__mutmut_7() -> RNGState:
    """Snapshot the current RNG state for CPU and CUDA generators."""

    if torch is None:
        return RNGState()
    cpu_state = _torch_rng_get_state()
    cuda_state = None
    if hasattr("cuda") and torch.cuda.is_available():
        cuda_state = torch.cuda.get_rng_state_all()  # type: ignore[attr-defined]
    return RNGState(cpu=cpu_state, cuda_all=cuda_state)


def x_snapshot_rng_state__mutmut_8() -> RNGState:
    """Snapshot the current RNG state for CPU and CUDA generators."""

    if torch is None:
        return RNGState()
    cpu_state = _torch_rng_get_state()
    cuda_state = None
    if hasattr(torch, ) and torch.cuda.is_available():
        cuda_state = torch.cuda.get_rng_state_all()  # type: ignore[attr-defined]
    return RNGState(cpu=cpu_state, cuda_all=cuda_state)


def x_snapshot_rng_state__mutmut_9() -> RNGState:
    """Snapshot the current RNG state for CPU and CUDA generators."""

    if torch is None:
        return RNGState()
    cpu_state = _torch_rng_get_state()
    cuda_state = None
    if hasattr(torch, "XXcudaXX") and torch.cuda.is_available():
        cuda_state = torch.cuda.get_rng_state_all()  # type: ignore[attr-defined]
    return RNGState(cpu=cpu_state, cuda_all=cuda_state)


def x_snapshot_rng_state__mutmut_10() -> RNGState:
    """Snapshot the current RNG state for CPU and CUDA generators."""

    if torch is None:
        return RNGState()
    cpu_state = _torch_rng_get_state()
    cuda_state = None
    if hasattr(torch, "CUDA") and torch.cuda.is_available():
        cuda_state = torch.cuda.get_rng_state_all()  # type: ignore[attr-defined]
    return RNGState(cpu=cpu_state, cuda_all=cuda_state)


def x_snapshot_rng_state__mutmut_11() -> RNGState:
    """Snapshot the current RNG state for CPU and CUDA generators."""

    if torch is None:
        return RNGState()
    cpu_state = _torch_rng_get_state()
    cuda_state = None
    if hasattr(torch, "cuda") and torch.cuda.is_available():
        cuda_state = None  # type: ignore[attr-defined]
    return RNGState(cpu=cpu_state, cuda_all=cuda_state)


def x_snapshot_rng_state__mutmut_12() -> RNGState:
    """Snapshot the current RNG state for CPU and CUDA generators."""

    if torch is None:
        return RNGState()
    cpu_state = _torch_rng_get_state()
    cuda_state = None
    if hasattr(torch, "cuda") and torch.cuda.is_available():
        cuda_state = torch.cuda.get_rng_state_all()  # type: ignore[attr-defined]
    return RNGState(cpu=None, cuda_all=cuda_state)


def x_snapshot_rng_state__mutmut_13() -> RNGState:
    """Snapshot the current RNG state for CPU and CUDA generators."""

    if torch is None:
        return RNGState()
    cpu_state = _torch_rng_get_state()
    cuda_state = None
    if hasattr(torch, "cuda") and torch.cuda.is_available():
        cuda_state = torch.cuda.get_rng_state_all()  # type: ignore[attr-defined]
    return RNGState(cpu=cpu_state, cuda_all=None)


def x_snapshot_rng_state__mutmut_14() -> RNGState:
    """Snapshot the current RNG state for CPU and CUDA generators."""

    if torch is None:
        return RNGState()
    cpu_state = _torch_rng_get_state()
    cuda_state = None
    if hasattr(torch, "cuda") and torch.cuda.is_available():
        cuda_state = torch.cuda.get_rng_state_all()  # type: ignore[attr-defined]
    return RNGState(cuda_all=cuda_state)


def x_snapshot_rng_state__mutmut_15() -> RNGState:
    """Snapshot the current RNG state for CPU and CUDA generators."""

    if torch is None:
        return RNGState()
    cpu_state = _torch_rng_get_state()
    cuda_state = None
    if hasattr(torch, "cuda") and torch.cuda.is_available():
        cuda_state = torch.cuda.get_rng_state_all()  # type: ignore[attr-defined]
    return RNGState(cpu=cpu_state, )

x_snapshot_rng_state__mutmut_mutants : ClassVar[MutantDict] = {
'x_snapshot_rng_state__mutmut_1': x_snapshot_rng_state__mutmut_1, 
    'x_snapshot_rng_state__mutmut_2': x_snapshot_rng_state__mutmut_2, 
    'x_snapshot_rng_state__mutmut_3': x_snapshot_rng_state__mutmut_3, 
    'x_snapshot_rng_state__mutmut_4': x_snapshot_rng_state__mutmut_4, 
    'x_snapshot_rng_state__mutmut_5': x_snapshot_rng_state__mutmut_5, 
    'x_snapshot_rng_state__mutmut_6': x_snapshot_rng_state__mutmut_6, 
    'x_snapshot_rng_state__mutmut_7': x_snapshot_rng_state__mutmut_7, 
    'x_snapshot_rng_state__mutmut_8': x_snapshot_rng_state__mutmut_8, 
    'x_snapshot_rng_state__mutmut_9': x_snapshot_rng_state__mutmut_9, 
    'x_snapshot_rng_state__mutmut_10': x_snapshot_rng_state__mutmut_10, 
    'x_snapshot_rng_state__mutmut_11': x_snapshot_rng_state__mutmut_11, 
    'x_snapshot_rng_state__mutmut_12': x_snapshot_rng_state__mutmut_12, 
    'x_snapshot_rng_state__mutmut_13': x_snapshot_rng_state__mutmut_13, 
    'x_snapshot_rng_state__mutmut_14': x_snapshot_rng_state__mutmut_14, 
    'x_snapshot_rng_state__mutmut_15': x_snapshot_rng_state__mutmut_15
}

def snapshot_rng_state(*args, **kwargs):
    result = _mutmut_trampoline(x_snapshot_rng_state__mutmut_orig, x_snapshot_rng_state__mutmut_mutants, args, kwargs)
    return result 

snapshot_rng_state.__signature__ = _mutmut_signature(x_snapshot_rng_state__mutmut_orig)
x_snapshot_rng_state__mutmut_orig.__name__ = 'x_snapshot_rng_state'


def x_restore_rng_state__mutmut_orig(state: RNGState) -> None:
    """Restore RNG state captured by :func:`snapshot_rng_state`."""

    if torch is None:
        return
    if state.cpu is not None:
        _torch_rng_set_state(state.cpu)
    if state.cuda_all is not None and hasattr(torch, "cuda") and torch.cuda.is_available():
        with suppress(Exception):  # pragma: no cover - best effort restoration
            torch.cuda.set_rng_state_all(state.cuda_all)  # type: ignore[attr-defined]


def x_restore_rng_state__mutmut_1(state: RNGState) -> None:
    """Restore RNG state captured by :func:`snapshot_rng_state`."""

    if torch is not None:
        return
    if state.cpu is not None:
        _torch_rng_set_state(state.cpu)
    if state.cuda_all is not None and hasattr(torch, "cuda") and torch.cuda.is_available():
        with suppress(Exception):  # pragma: no cover - best effort restoration
            torch.cuda.set_rng_state_all(state.cuda_all)  # type: ignore[attr-defined]


def x_restore_rng_state__mutmut_2(state: RNGState) -> None:
    """Restore RNG state captured by :func:`snapshot_rng_state`."""

    if torch is None:
        return
    if state.cpu is None:
        _torch_rng_set_state(state.cpu)
    if state.cuda_all is not None and hasattr(torch, "cuda") and torch.cuda.is_available():
        with suppress(Exception):  # pragma: no cover - best effort restoration
            torch.cuda.set_rng_state_all(state.cuda_all)  # type: ignore[attr-defined]


def x_restore_rng_state__mutmut_3(state: RNGState) -> None:
    """Restore RNG state captured by :func:`snapshot_rng_state`."""

    if torch is None:
        return
    if state.cpu is not None:
        _torch_rng_set_state(None)
    if state.cuda_all is not None and hasattr(torch, "cuda") and torch.cuda.is_available():
        with suppress(Exception):  # pragma: no cover - best effort restoration
            torch.cuda.set_rng_state_all(state.cuda_all)  # type: ignore[attr-defined]


def x_restore_rng_state__mutmut_4(state: RNGState) -> None:
    """Restore RNG state captured by :func:`snapshot_rng_state`."""

    if torch is None:
        return
    if state.cpu is not None:
        _torch_rng_set_state(state.cpu)
    if state.cuda_all is not None and hasattr(torch, "cuda") or torch.cuda.is_available():
        with suppress(Exception):  # pragma: no cover - best effort restoration
            torch.cuda.set_rng_state_all(state.cuda_all)  # type: ignore[attr-defined]


def x_restore_rng_state__mutmut_5(state: RNGState) -> None:
    """Restore RNG state captured by :func:`snapshot_rng_state`."""

    if torch is None:
        return
    if state.cpu is not None:
        _torch_rng_set_state(state.cpu)
    if state.cuda_all is not None or hasattr(torch, "cuda") and torch.cuda.is_available():
        with suppress(Exception):  # pragma: no cover - best effort restoration
            torch.cuda.set_rng_state_all(state.cuda_all)  # type: ignore[attr-defined]


def x_restore_rng_state__mutmut_6(state: RNGState) -> None:
    """Restore RNG state captured by :func:`snapshot_rng_state`."""

    if torch is None:
        return
    if state.cpu is not None:
        _torch_rng_set_state(state.cpu)
    if state.cuda_all is None and hasattr(torch, "cuda") and torch.cuda.is_available():
        with suppress(Exception):  # pragma: no cover - best effort restoration
            torch.cuda.set_rng_state_all(state.cuda_all)  # type: ignore[attr-defined]


def x_restore_rng_state__mutmut_7(state: RNGState) -> None:
    """Restore RNG state captured by :func:`snapshot_rng_state`."""

    if torch is None:
        return
    if state.cpu is not None:
        _torch_rng_set_state(state.cpu)
    if state.cuda_all is not None and hasattr(None, "cuda") and torch.cuda.is_available():
        with suppress(Exception):  # pragma: no cover - best effort restoration
            torch.cuda.set_rng_state_all(state.cuda_all)  # type: ignore[attr-defined]


def x_restore_rng_state__mutmut_8(state: RNGState) -> None:
    """Restore RNG state captured by :func:`snapshot_rng_state`."""

    if torch is None:
        return
    if state.cpu is not None:
        _torch_rng_set_state(state.cpu)
    if state.cuda_all is not None and hasattr(torch, None) and torch.cuda.is_available():
        with suppress(Exception):  # pragma: no cover - best effort restoration
            torch.cuda.set_rng_state_all(state.cuda_all)  # type: ignore[attr-defined]


def x_restore_rng_state__mutmut_9(state: RNGState) -> None:
    """Restore RNG state captured by :func:`snapshot_rng_state`."""

    if torch is None:
        return
    if state.cpu is not None:
        _torch_rng_set_state(state.cpu)
    if state.cuda_all is not None and hasattr("cuda") and torch.cuda.is_available():
        with suppress(Exception):  # pragma: no cover - best effort restoration
            torch.cuda.set_rng_state_all(state.cuda_all)  # type: ignore[attr-defined]


def x_restore_rng_state__mutmut_10(state: RNGState) -> None:
    """Restore RNG state captured by :func:`snapshot_rng_state`."""

    if torch is None:
        return
    if state.cpu is not None:
        _torch_rng_set_state(state.cpu)
    if state.cuda_all is not None and hasattr(torch, ) and torch.cuda.is_available():
        with suppress(Exception):  # pragma: no cover - best effort restoration
            torch.cuda.set_rng_state_all(state.cuda_all)  # type: ignore[attr-defined]


def x_restore_rng_state__mutmut_11(state: RNGState) -> None:
    """Restore RNG state captured by :func:`snapshot_rng_state`."""

    if torch is None:
        return
    if state.cpu is not None:
        _torch_rng_set_state(state.cpu)
    if state.cuda_all is not None and hasattr(torch, "XXcudaXX") and torch.cuda.is_available():
        with suppress(Exception):  # pragma: no cover - best effort restoration
            torch.cuda.set_rng_state_all(state.cuda_all)  # type: ignore[attr-defined]


def x_restore_rng_state__mutmut_12(state: RNGState) -> None:
    """Restore RNG state captured by :func:`snapshot_rng_state`."""

    if torch is None:
        return
    if state.cpu is not None:
        _torch_rng_set_state(state.cpu)
    if state.cuda_all is not None and hasattr(torch, "CUDA") and torch.cuda.is_available():
        with suppress(Exception):  # pragma: no cover - best effort restoration
            torch.cuda.set_rng_state_all(state.cuda_all)  # type: ignore[attr-defined]


def x_restore_rng_state__mutmut_13(state: RNGState) -> None:
    """Restore RNG state captured by :func:`snapshot_rng_state`."""

    if torch is None:
        return
    if state.cpu is not None:
        _torch_rng_set_state(state.cpu)
    if state.cuda_all is not None and hasattr(torch, "cuda") and torch.cuda.is_available():
        with suppress(None):  # pragma: no cover - best effort restoration
            torch.cuda.set_rng_state_all(state.cuda_all)  # type: ignore[attr-defined]


def x_restore_rng_state__mutmut_14(state: RNGState) -> None:
    """Restore RNG state captured by :func:`snapshot_rng_state`."""

    if torch is None:
        return
    if state.cpu is not None:
        _torch_rng_set_state(state.cpu)
    if state.cuda_all is not None and hasattr(torch, "cuda") and torch.cuda.is_available():
        with suppress(Exception):  # pragma: no cover - best effort restoration
            torch.cuda.set_rng_state_all(None)  # type: ignore[attr-defined]

x_restore_rng_state__mutmut_mutants : ClassVar[MutantDict] = {
'x_restore_rng_state__mutmut_1': x_restore_rng_state__mutmut_1, 
    'x_restore_rng_state__mutmut_2': x_restore_rng_state__mutmut_2, 
    'x_restore_rng_state__mutmut_3': x_restore_rng_state__mutmut_3, 
    'x_restore_rng_state__mutmut_4': x_restore_rng_state__mutmut_4, 
    'x_restore_rng_state__mutmut_5': x_restore_rng_state__mutmut_5, 
    'x_restore_rng_state__mutmut_6': x_restore_rng_state__mutmut_6, 
    'x_restore_rng_state__mutmut_7': x_restore_rng_state__mutmut_7, 
    'x_restore_rng_state__mutmut_8': x_restore_rng_state__mutmut_8, 
    'x_restore_rng_state__mutmut_9': x_restore_rng_state__mutmut_9, 
    'x_restore_rng_state__mutmut_10': x_restore_rng_state__mutmut_10, 
    'x_restore_rng_state__mutmut_11': x_restore_rng_state__mutmut_11, 
    'x_restore_rng_state__mutmut_12': x_restore_rng_state__mutmut_12, 
    'x_restore_rng_state__mutmut_13': x_restore_rng_state__mutmut_13, 
    'x_restore_rng_state__mutmut_14': x_restore_rng_state__mutmut_14
}

def restore_rng_state(*args, **kwargs):
    result = _mutmut_trampoline(x_restore_rng_state__mutmut_orig, x_restore_rng_state__mutmut_mutants, args, kwargs)
    return result 

restore_rng_state.__signature__ = _mutmut_signature(x_restore_rng_state__mutmut_orig)
x_restore_rng_state__mutmut_orig.__name__ = 'x_restore_rng_state'


def x__score_key__mutmut_orig(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    is_nan = 1
    if metric is not None and not (isinstance(metric, float) and math.isnan(metric)):
        is_nan = 0
    value: float
    if metric is None or (isinstance(metric, float) and math.isnan(metric)):
        value = math.inf
    else:
        value = float(metric)
    best_scalar = value if mode == "min" else -value
    return (is_nan, best_scalar, -int(epoch))


def x__score_key__mutmut_1(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    is_nan = 1
    if metric is not None and not (isinstance(metric, float) and math.isnan(metric)):
        is_nan = 0
    value: float
    if metric is None or (isinstance(metric, float) and math.isnan(metric)):
        value = math.inf
    else:
        value = float(metric)
    best_scalar = value if mode == "min" else -value
    return (is_nan, best_scalar, -int(epoch))


def x__score_key__mutmut_2(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"XXminXX", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    is_nan = 1
    if metric is not None and not (isinstance(metric, float) and math.isnan(metric)):
        is_nan = 0
    value: float
    if metric is None or (isinstance(metric, float) and math.isnan(metric)):
        value = math.inf
    else:
        value = float(metric)
    best_scalar = value if mode == "min" else -value
    return (is_nan, best_scalar, -int(epoch))


def x__score_key__mutmut_3(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"MIN", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    is_nan = 1
    if metric is not None and not (isinstance(metric, float) and math.isnan(metric)):
        is_nan = 0
    value: float
    if metric is None or (isinstance(metric, float) and math.isnan(metric)):
        value = math.inf
    else:
        value = float(metric)
    best_scalar = value if mode == "min" else -value
    return (is_nan, best_scalar, -int(epoch))


def x__score_key__mutmut_4(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"min", "XXmaxXX"}:
        raise ValueError("mode must be 'min' or 'max'")
    is_nan = 1
    if metric is not None and not (isinstance(metric, float) and math.isnan(metric)):
        is_nan = 0
    value: float
    if metric is None or (isinstance(metric, float) and math.isnan(metric)):
        value = math.inf
    else:
        value = float(metric)
    best_scalar = value if mode == "min" else -value
    return (is_nan, best_scalar, -int(epoch))


def x__score_key__mutmut_5(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"min", "MAX"}:
        raise ValueError("mode must be 'min' or 'max'")
    is_nan = 1
    if metric is not None and not (isinstance(metric, float) and math.isnan(metric)):
        is_nan = 0
    value: float
    if metric is None or (isinstance(metric, float) and math.isnan(metric)):
        value = math.inf
    else:
        value = float(metric)
    best_scalar = value if mode == "min" else -value
    return (is_nan, best_scalar, -int(epoch))


def x__score_key__mutmut_6(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"min", "max"}:
        raise ValueError(None)
    is_nan = 1
    if metric is not None and not (isinstance(metric, float) and math.isnan(metric)):
        is_nan = 0
    value: float
    if metric is None or (isinstance(metric, float) and math.isnan(metric)):
        value = math.inf
    else:
        value = float(metric)
    best_scalar = value if mode == "min" else -value
    return (is_nan, best_scalar, -int(epoch))


def x__score_key__mutmut_7(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"min", "max"}:
        raise ValueError("XXmode must be 'min' or 'max'XX")
    is_nan = 1
    if metric is not None and not (isinstance(metric, float) and math.isnan(metric)):
        is_nan = 0
    value: float
    if metric is None or (isinstance(metric, float) and math.isnan(metric)):
        value = math.inf
    else:
        value = float(metric)
    best_scalar = value if mode == "min" else -value
    return (is_nan, best_scalar, -int(epoch))


def x__score_key__mutmut_8(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"min", "max"}:
        raise ValueError("MODE MUST BE 'MIN' OR 'MAX'")
    is_nan = 1
    if metric is not None and not (isinstance(metric, float) and math.isnan(metric)):
        is_nan = 0
    value: float
    if metric is None or (isinstance(metric, float) and math.isnan(metric)):
        value = math.inf
    else:
        value = float(metric)
    best_scalar = value if mode == "min" else -value
    return (is_nan, best_scalar, -int(epoch))


def x__score_key__mutmut_9(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    is_nan = None
    if metric is not None and not (isinstance(metric, float) and math.isnan(metric)):
        is_nan = 0
    value: float
    if metric is None or (isinstance(metric, float) and math.isnan(metric)):
        value = math.inf
    else:
        value = float(metric)
    best_scalar = value if mode == "min" else -value
    return (is_nan, best_scalar, -int(epoch))


def x__score_key__mutmut_10(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    is_nan = 2
    if metric is not None and not (isinstance(metric, float) and math.isnan(metric)):
        is_nan = 0
    value: float
    if metric is None or (isinstance(metric, float) and math.isnan(metric)):
        value = math.inf
    else:
        value = float(metric)
    best_scalar = value if mode == "min" else -value
    return (is_nan, best_scalar, -int(epoch))


def x__score_key__mutmut_11(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    is_nan = 1
    if metric is not None or not (isinstance(metric, float) and math.isnan(metric)):
        is_nan = 0
    value: float
    if metric is None or (isinstance(metric, float) and math.isnan(metric)):
        value = math.inf
    else:
        value = float(metric)
    best_scalar = value if mode == "min" else -value
    return (is_nan, best_scalar, -int(epoch))


def x__score_key__mutmut_12(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    is_nan = 1
    if metric is None and not (isinstance(metric, float) and math.isnan(metric)):
        is_nan = 0
    value: float
    if metric is None or (isinstance(metric, float) and math.isnan(metric)):
        value = math.inf
    else:
        value = float(metric)
    best_scalar = value if mode == "min" else -value
    return (is_nan, best_scalar, -int(epoch))


def x__score_key__mutmut_13(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    is_nan = 1
    if metric is not None and (isinstance(metric, float) and math.isnan(metric)):
        is_nan = 0
    value: float
    if metric is None or (isinstance(metric, float) and math.isnan(metric)):
        value = math.inf
    else:
        value = float(metric)
    best_scalar = value if mode == "min" else -value
    return (is_nan, best_scalar, -int(epoch))


def x__score_key__mutmut_14(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    is_nan = 1
    if metric is not None and not (isinstance(metric, float) or math.isnan(metric)):
        is_nan = 0
    value: float
    if metric is None or (isinstance(metric, float) and math.isnan(metric)):
        value = math.inf
    else:
        value = float(metric)
    best_scalar = value if mode == "min" else -value
    return (is_nan, best_scalar, -int(epoch))


def x__score_key__mutmut_15(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    is_nan = 1
    if metric is not None and not (isinstance(metric, float) and math.isnan(None)):
        is_nan = 0
    value: float
    if metric is None or (isinstance(metric, float) and math.isnan(metric)):
        value = math.inf
    else:
        value = float(metric)
    best_scalar = value if mode == "min" else -value
    return (is_nan, best_scalar, -int(epoch))


def x__score_key__mutmut_16(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    is_nan = 1
    if metric is not None and not (isinstance(metric, float) and math.isnan(metric)):
        is_nan = None
    value: float
    if metric is None or (isinstance(metric, float) and math.isnan(metric)):
        value = math.inf
    else:
        value = float(metric)
    best_scalar = value if mode == "min" else -value
    return (is_nan, best_scalar, -int(epoch))


def x__score_key__mutmut_17(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    is_nan = 1
    if metric is not None and not (isinstance(metric, float) and math.isnan(metric)):
        is_nan = 1
    value: float
    if metric is None or (isinstance(metric, float) and math.isnan(metric)):
        value = math.inf
    else:
        value = float(metric)
    best_scalar = value if mode == "min" else -value
    return (is_nan, best_scalar, -int(epoch))


def x__score_key__mutmut_18(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    is_nan = 1
    if metric is not None and not (isinstance(metric, float) and math.isnan(metric)):
        is_nan = 0
    value: float
    if metric is None and (isinstance(metric, float) and math.isnan(metric)):
        value = math.inf
    else:
        value = float(metric)
    best_scalar = value if mode == "min" else -value
    return (is_nan, best_scalar, -int(epoch))


def x__score_key__mutmut_19(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    is_nan = 1
    if metric is not None and not (isinstance(metric, float) and math.isnan(metric)):
        is_nan = 0
    value: float
    if metric is not None or (isinstance(metric, float) and math.isnan(metric)):
        value = math.inf
    else:
        value = float(metric)
    best_scalar = value if mode == "min" else -value
    return (is_nan, best_scalar, -int(epoch))


def x__score_key__mutmut_20(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    is_nan = 1
    if metric is not None and not (isinstance(metric, float) and math.isnan(metric)):
        is_nan = 0
    value: float
    if metric is None or (isinstance(metric, float) or math.isnan(metric)):
        value = math.inf
    else:
        value = float(metric)
    best_scalar = value if mode == "min" else -value
    return (is_nan, best_scalar, -int(epoch))


def x__score_key__mutmut_21(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    is_nan = 1
    if metric is not None and not (isinstance(metric, float) and math.isnan(metric)):
        is_nan = 0
    value: float
    if metric is None or (isinstance(metric, float) and math.isnan(None)):
        value = math.inf
    else:
        value = float(metric)
    best_scalar = value if mode == "min" else -value
    return (is_nan, best_scalar, -int(epoch))


def x__score_key__mutmut_22(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    is_nan = 1
    if metric is not None and not (isinstance(metric, float) and math.isnan(metric)):
        is_nan = 0
    value: float
    if metric is None or (isinstance(metric, float) and math.isnan(metric)):
        value = None
    else:
        value = float(metric)
    best_scalar = value if mode == "min" else -value
    return (is_nan, best_scalar, -int(epoch))


def x__score_key__mutmut_23(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    is_nan = 1
    if metric is not None and not (isinstance(metric, float) and math.isnan(metric)):
        is_nan = 0
    value: float
    if metric is None or (isinstance(metric, float) and math.isnan(metric)):
        value = math.inf
    else:
        value = None
    best_scalar = value if mode == "min" else -value
    return (is_nan, best_scalar, -int(epoch))


def x__score_key__mutmut_24(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    is_nan = 1
    if metric is not None and not (isinstance(metric, float) and math.isnan(metric)):
        is_nan = 0
    value: float
    if metric is None or (isinstance(metric, float) and math.isnan(metric)):
        value = math.inf
    else:
        value = float(None)
    best_scalar = value if mode == "min" else -value
    return (is_nan, best_scalar, -int(epoch))


def x__score_key__mutmut_25(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    is_nan = 1
    if metric is not None and not (isinstance(metric, float) and math.isnan(metric)):
        is_nan = 0
    value: float
    if metric is None or (isinstance(metric, float) and math.isnan(metric)):
        value = math.inf
    else:
        value = float(metric)
    best_scalar = None
    return (is_nan, best_scalar, -int(epoch))


def x__score_key__mutmut_26(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    is_nan = 1
    if metric is not None and not (isinstance(metric, float) and math.isnan(metric)):
        is_nan = 0
    value: float
    if metric is None or (isinstance(metric, float) and math.isnan(metric)):
        value = math.inf
    else:
        value = float(metric)
    best_scalar = value if mode != "min" else -value
    return (is_nan, best_scalar, -int(epoch))


def x__score_key__mutmut_27(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    is_nan = 1
    if metric is not None and not (isinstance(metric, float) and math.isnan(metric)):
        is_nan = 0
    value: float
    if metric is None or (isinstance(metric, float) and math.isnan(metric)):
        value = math.inf
    else:
        value = float(metric)
    best_scalar = value if mode == "XXminXX" else -value
    return (is_nan, best_scalar, -int(epoch))


def x__score_key__mutmut_28(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    is_nan = 1
    if metric is not None and not (isinstance(metric, float) and math.isnan(metric)):
        is_nan = 0
    value: float
    if metric is None or (isinstance(metric, float) and math.isnan(metric)):
        value = math.inf
    else:
        value = float(metric)
    best_scalar = value if mode == "MIN" else -value
    return (is_nan, best_scalar, -int(epoch))


def x__score_key__mutmut_29(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    is_nan = 1
    if metric is not None and not (isinstance(metric, float) and math.isnan(metric)):
        is_nan = 0
    value: float
    if metric is None or (isinstance(metric, float) and math.isnan(metric)):
        value = math.inf
    else:
        value = float(metric)
    best_scalar = value if mode == "min" else +value
    return (is_nan, best_scalar, -int(epoch))


def x__score_key__mutmut_30(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    is_nan = 1
    if metric is not None and not (isinstance(metric, float) and math.isnan(metric)):
        is_nan = 0
    value: float
    if metric is None or (isinstance(metric, float) and math.isnan(metric)):
        value = math.inf
    else:
        value = float(metric)
    best_scalar = value if mode == "min" else -value
    return (is_nan, best_scalar, +int(epoch))


def x__score_key__mutmut_31(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    is_nan = 1
    if metric is not None and not (isinstance(metric, float) and math.isnan(metric)):
        is_nan = 0
    value: float
    if metric is None or (isinstance(metric, float) and math.isnan(metric)):
        value = math.inf
    else:
        value = float(metric)
    best_scalar = value if mode == "min" else -value
    return (is_nan, best_scalar, -int(None))

x__score_key__mutmut_mutants : ClassVar[MutantDict] = {
'x__score_key__mutmut_1': x__score_key__mutmut_1, 
    'x__score_key__mutmut_2': x__score_key__mutmut_2, 
    'x__score_key__mutmut_3': x__score_key__mutmut_3, 
    'x__score_key__mutmut_4': x__score_key__mutmut_4, 
    'x__score_key__mutmut_5': x__score_key__mutmut_5, 
    'x__score_key__mutmut_6': x__score_key__mutmut_6, 
    'x__score_key__mutmut_7': x__score_key__mutmut_7, 
    'x__score_key__mutmut_8': x__score_key__mutmut_8, 
    'x__score_key__mutmut_9': x__score_key__mutmut_9, 
    'x__score_key__mutmut_10': x__score_key__mutmut_10, 
    'x__score_key__mutmut_11': x__score_key__mutmut_11, 
    'x__score_key__mutmut_12': x__score_key__mutmut_12, 
    'x__score_key__mutmut_13': x__score_key__mutmut_13, 
    'x__score_key__mutmut_14': x__score_key__mutmut_14, 
    'x__score_key__mutmut_15': x__score_key__mutmut_15, 
    'x__score_key__mutmut_16': x__score_key__mutmut_16, 
    'x__score_key__mutmut_17': x__score_key__mutmut_17, 
    'x__score_key__mutmut_18': x__score_key__mutmut_18, 
    'x__score_key__mutmut_19': x__score_key__mutmut_19, 
    'x__score_key__mutmut_20': x__score_key__mutmut_20, 
    'x__score_key__mutmut_21': x__score_key__mutmut_21, 
    'x__score_key__mutmut_22': x__score_key__mutmut_22, 
    'x__score_key__mutmut_23': x__score_key__mutmut_23, 
    'x__score_key__mutmut_24': x__score_key__mutmut_24, 
    'x__score_key__mutmut_25': x__score_key__mutmut_25, 
    'x__score_key__mutmut_26': x__score_key__mutmut_26, 
    'x__score_key__mutmut_27': x__score_key__mutmut_27, 
    'x__score_key__mutmut_28': x__score_key__mutmut_28, 
    'x__score_key__mutmut_29': x__score_key__mutmut_29, 
    'x__score_key__mutmut_30': x__score_key__mutmut_30, 
    'x__score_key__mutmut_31': x__score_key__mutmut_31
}

def _score_key(*args, **kwargs):
    result = _mutmut_trampoline(x__score_key__mutmut_orig, x__score_key__mutmut_mutants, args, kwargs)
    return result 

_score_key.__signature__ = _mutmut_signature(x__score_key__mutmut_orig)
x__score_key__mutmut_orig.__name__ = 'x__score_key'


def x__parse_epoch_metric__mutmut_orig(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_1(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = None
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_2(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") and "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_3(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_4(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith(None) or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_5(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("XXepochXX") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_6(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("EPOCH") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_7(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "XX-metricXX" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_8(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-METRIC" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_9(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_10(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = None
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_11(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split(None, 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_12(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", None)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_13(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split(1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_14(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", )
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_15(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.rsplit("-metric", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_16(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("XX-metricXX", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_17(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-METRIC", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_18(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 2)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_19(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = None
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_20(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(None)
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_21(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace(None, ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_22(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", None))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_23(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace(""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_24(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", ))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_25(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("XXepochXX", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_26(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("EPOCH", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_27(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", "XXXX"))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_28(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = None
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_29(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(None)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_30(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning(None, exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_31(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=None)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_32(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning(exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_33(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", )
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_34(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("XXException occurredXX", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_35(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_36(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("EXCEPTION OCCURRED", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_37(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=False)
        logger.warning("Exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_38(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning(None, exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_39(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=None)
        return None, None


def x__parse_epoch_metric__mutmut_40(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning(exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_41(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", )
        return None, None


def x__parse_epoch_metric__mutmut_42(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("XXException occurredXX", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_43(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("exception occurred", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_44(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("EXCEPTION OCCURRED", exc_info=True)
        return None, None


def x__parse_epoch_metric__mutmut_45(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=False)
        return None, None

x__parse_epoch_metric__mutmut_mutants : ClassVar[MutantDict] = {
'x__parse_epoch_metric__mutmut_1': x__parse_epoch_metric__mutmut_1, 
    'x__parse_epoch_metric__mutmut_2': x__parse_epoch_metric__mutmut_2, 
    'x__parse_epoch_metric__mutmut_3': x__parse_epoch_metric__mutmut_3, 
    'x__parse_epoch_metric__mutmut_4': x__parse_epoch_metric__mutmut_4, 
    'x__parse_epoch_metric__mutmut_5': x__parse_epoch_metric__mutmut_5, 
    'x__parse_epoch_metric__mutmut_6': x__parse_epoch_metric__mutmut_6, 
    'x__parse_epoch_metric__mutmut_7': x__parse_epoch_metric__mutmut_7, 
    'x__parse_epoch_metric__mutmut_8': x__parse_epoch_metric__mutmut_8, 
    'x__parse_epoch_metric__mutmut_9': x__parse_epoch_metric__mutmut_9, 
    'x__parse_epoch_metric__mutmut_10': x__parse_epoch_metric__mutmut_10, 
    'x__parse_epoch_metric__mutmut_11': x__parse_epoch_metric__mutmut_11, 
    'x__parse_epoch_metric__mutmut_12': x__parse_epoch_metric__mutmut_12, 
    'x__parse_epoch_metric__mutmut_13': x__parse_epoch_metric__mutmut_13, 
    'x__parse_epoch_metric__mutmut_14': x__parse_epoch_metric__mutmut_14, 
    'x__parse_epoch_metric__mutmut_15': x__parse_epoch_metric__mutmut_15, 
    'x__parse_epoch_metric__mutmut_16': x__parse_epoch_metric__mutmut_16, 
    'x__parse_epoch_metric__mutmut_17': x__parse_epoch_metric__mutmut_17, 
    'x__parse_epoch_metric__mutmut_18': x__parse_epoch_metric__mutmut_18, 
    'x__parse_epoch_metric__mutmut_19': x__parse_epoch_metric__mutmut_19, 
    'x__parse_epoch_metric__mutmut_20': x__parse_epoch_metric__mutmut_20, 
    'x__parse_epoch_metric__mutmut_21': x__parse_epoch_metric__mutmut_21, 
    'x__parse_epoch_metric__mutmut_22': x__parse_epoch_metric__mutmut_22, 
    'x__parse_epoch_metric__mutmut_23': x__parse_epoch_metric__mutmut_23, 
    'x__parse_epoch_metric__mutmut_24': x__parse_epoch_metric__mutmut_24, 
    'x__parse_epoch_metric__mutmut_25': x__parse_epoch_metric__mutmut_25, 
    'x__parse_epoch_metric__mutmut_26': x__parse_epoch_metric__mutmut_26, 
    'x__parse_epoch_metric__mutmut_27': x__parse_epoch_metric__mutmut_27, 
    'x__parse_epoch_metric__mutmut_28': x__parse_epoch_metric__mutmut_28, 
    'x__parse_epoch_metric__mutmut_29': x__parse_epoch_metric__mutmut_29, 
    'x__parse_epoch_metric__mutmut_30': x__parse_epoch_metric__mutmut_30, 
    'x__parse_epoch_metric__mutmut_31': x__parse_epoch_metric__mutmut_31, 
    'x__parse_epoch_metric__mutmut_32': x__parse_epoch_metric__mutmut_32, 
    'x__parse_epoch_metric__mutmut_33': x__parse_epoch_metric__mutmut_33, 
    'x__parse_epoch_metric__mutmut_34': x__parse_epoch_metric__mutmut_34, 
    'x__parse_epoch_metric__mutmut_35': x__parse_epoch_metric__mutmut_35, 
    'x__parse_epoch_metric__mutmut_36': x__parse_epoch_metric__mutmut_36, 
    'x__parse_epoch_metric__mutmut_37': x__parse_epoch_metric__mutmut_37, 
    'x__parse_epoch_metric__mutmut_38': x__parse_epoch_metric__mutmut_38, 
    'x__parse_epoch_metric__mutmut_39': x__parse_epoch_metric__mutmut_39, 
    'x__parse_epoch_metric__mutmut_40': x__parse_epoch_metric__mutmut_40, 
    'x__parse_epoch_metric__mutmut_41': x__parse_epoch_metric__mutmut_41, 
    'x__parse_epoch_metric__mutmut_42': x__parse_epoch_metric__mutmut_42, 
    'x__parse_epoch_metric__mutmut_43': x__parse_epoch_metric__mutmut_43, 
    'x__parse_epoch_metric__mutmut_44': x__parse_epoch_metric__mutmut_44, 
    'x__parse_epoch_metric__mutmut_45': x__parse_epoch_metric__mutmut_45
}

def _parse_epoch_metric(*args, **kwargs):
    result = _mutmut_trampoline(x__parse_epoch_metric__mutmut_orig, x__parse_epoch_metric__mutmut_mutants, args, kwargs)
    return result 

_parse_epoch_metric.__signature__ = _mutmut_signature(x__parse_epoch_metric__mutmut_orig)
x__parse_epoch_metric__mutmut_orig.__name__ = 'x__parse_epoch_metric'


def x__best_k_retention__mutmut_orig(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(dirpath.glob("epoch*-metric*.pt"))
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(path)
        if epoch is None:
            continue
        scored.append((_score_key(metric, epoch, mode), path))
    if not scored or len(scored) <= keep_best_k:
        return
    scored_sorted = sorted(scored, key=lambda item: item[0])
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=True)


def x__best_k_retention__mutmut_1(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = None
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(path)
        if epoch is None:
            continue
        scored.append((_score_key(metric, epoch, mode), path))
    if not scored or len(scored) <= keep_best_k:
        return
    scored_sorted = sorted(scored, key=lambda item: item[0])
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=True)


def x__best_k_retention__mutmut_2(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(None)
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(path)
        if epoch is None:
            continue
        scored.append((_score_key(metric, epoch, mode), path))
    if not scored or len(scored) <= keep_best_k:
        return
    scored_sorted = sorted(scored, key=lambda item: item[0])
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=True)


def x__best_k_retention__mutmut_3(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(dirpath.glob(None))
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(path)
        if epoch is None:
            continue
        scored.append((_score_key(metric, epoch, mode), path))
    if not scored or len(scored) <= keep_best_k:
        return
    scored_sorted = sorted(scored, key=lambda item: item[0])
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=True)


def x__best_k_retention__mutmut_4(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(dirpath.glob("XXepoch*-metric*.ptXX"))
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(path)
        if epoch is None:
            continue
        scored.append((_score_key(metric, epoch, mode), path))
    if not scored or len(scored) <= keep_best_k:
        return
    scored_sorted = sorted(scored, key=lambda item: item[0])
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=True)


def x__best_k_retention__mutmut_5(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(dirpath.glob("EPOCH*-METRIC*.PT"))
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(path)
        if epoch is None:
            continue
        scored.append((_score_key(metric, epoch, mode), path))
    if not scored or len(scored) <= keep_best_k:
        return
    scored_sorted = sorted(scored, key=lambda item: item[0])
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=True)


def x__best_k_retention__mutmut_6(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(dirpath.glob("epoch*-metric*.pt"))
    scored: list[tuple[tuple[int, float, int], Path]] = None
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(path)
        if epoch is None:
            continue
        scored.append((_score_key(metric, epoch, mode), path))
    if not scored or len(scored) <= keep_best_k:
        return
    scored_sorted = sorted(scored, key=lambda item: item[0])
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=True)


def x__best_k_retention__mutmut_7(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(dirpath.glob("epoch*-metric*.pt"))
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = None
        if epoch is None:
            continue
        scored.append((_score_key(metric, epoch, mode), path))
    if not scored or len(scored) <= keep_best_k:
        return
    scored_sorted = sorted(scored, key=lambda item: item[0])
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=True)


def x__best_k_retention__mutmut_8(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(dirpath.glob("epoch*-metric*.pt"))
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(None)
        if epoch is None:
            continue
        scored.append((_score_key(metric, epoch, mode), path))
    if not scored or len(scored) <= keep_best_k:
        return
    scored_sorted = sorted(scored, key=lambda item: item[0])
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=True)


def x__best_k_retention__mutmut_9(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(dirpath.glob("epoch*-metric*.pt"))
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(path)
        if epoch is not None:
            continue
        scored.append((_score_key(metric, epoch, mode), path))
    if not scored or len(scored) <= keep_best_k:
        return
    scored_sorted = sorted(scored, key=lambda item: item[0])
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=True)


def x__best_k_retention__mutmut_10(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(dirpath.glob("epoch*-metric*.pt"))
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(path)
        if epoch is None:
            break
        scored.append((_score_key(metric, epoch, mode), path))
    if not scored or len(scored) <= keep_best_k:
        return
    scored_sorted = sorted(scored, key=lambda item: item[0])
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=True)


def x__best_k_retention__mutmut_11(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(dirpath.glob("epoch*-metric*.pt"))
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(path)
        if epoch is None:
            continue
        scored.append(None)
    if not scored or len(scored) <= keep_best_k:
        return
    scored_sorted = sorted(scored, key=lambda item: item[0])
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=True)


def x__best_k_retention__mutmut_12(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(dirpath.glob("epoch*-metric*.pt"))
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(path)
        if epoch is None:
            continue
        scored.append((_score_key(None, epoch, mode), path))
    if not scored or len(scored) <= keep_best_k:
        return
    scored_sorted = sorted(scored, key=lambda item: item[0])
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=True)


def x__best_k_retention__mutmut_13(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(dirpath.glob("epoch*-metric*.pt"))
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(path)
        if epoch is None:
            continue
        scored.append((_score_key(metric, None, mode), path))
    if not scored or len(scored) <= keep_best_k:
        return
    scored_sorted = sorted(scored, key=lambda item: item[0])
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=True)


def x__best_k_retention__mutmut_14(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(dirpath.glob("epoch*-metric*.pt"))
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(path)
        if epoch is None:
            continue
        scored.append((_score_key(metric, epoch, None), path))
    if not scored or len(scored) <= keep_best_k:
        return
    scored_sorted = sorted(scored, key=lambda item: item[0])
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=True)


def x__best_k_retention__mutmut_15(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(dirpath.glob("epoch*-metric*.pt"))
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(path)
        if epoch is None:
            continue
        scored.append((_score_key(epoch, mode), path))
    if not scored or len(scored) <= keep_best_k:
        return
    scored_sorted = sorted(scored, key=lambda item: item[0])
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=True)


def x__best_k_retention__mutmut_16(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(dirpath.glob("epoch*-metric*.pt"))
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(path)
        if epoch is None:
            continue
        scored.append((_score_key(metric, mode), path))
    if not scored or len(scored) <= keep_best_k:
        return
    scored_sorted = sorted(scored, key=lambda item: item[0])
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=True)


def x__best_k_retention__mutmut_17(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(dirpath.glob("epoch*-metric*.pt"))
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(path)
        if epoch is None:
            continue
        scored.append((_score_key(metric, epoch, ), path))
    if not scored or len(scored) <= keep_best_k:
        return
    scored_sorted = sorted(scored, key=lambda item: item[0])
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=True)


def x__best_k_retention__mutmut_18(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(dirpath.glob("epoch*-metric*.pt"))
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(path)
        if epoch is None:
            continue
        scored.append((_score_key(metric, epoch, mode), path))
    if not scored and len(scored) <= keep_best_k:
        return
    scored_sorted = sorted(scored, key=lambda item: item[0])
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=True)


def x__best_k_retention__mutmut_19(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(dirpath.glob("epoch*-metric*.pt"))
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(path)
        if epoch is None:
            continue
        scored.append((_score_key(metric, epoch, mode), path))
    if scored or len(scored) <= keep_best_k:
        return
    scored_sorted = sorted(scored, key=lambda item: item[0])
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=True)


def x__best_k_retention__mutmut_20(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(dirpath.glob("epoch*-metric*.pt"))
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(path)
        if epoch is None:
            continue
        scored.append((_score_key(metric, epoch, mode), path))
    if not scored or len(scored) < keep_best_k:
        return
    scored_sorted = sorted(scored, key=lambda item: item[0])
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=True)


def x__best_k_retention__mutmut_21(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(dirpath.glob("epoch*-metric*.pt"))
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(path)
        if epoch is None:
            continue
        scored.append((_score_key(metric, epoch, mode), path))
    if not scored or len(scored) <= keep_best_k:
        return
    scored_sorted = None
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=True)


def x__best_k_retention__mutmut_22(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(dirpath.glob("epoch*-metric*.pt"))
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(path)
        if epoch is None:
            continue
        scored.append((_score_key(metric, epoch, mode), path))
    if not scored or len(scored) <= keep_best_k:
        return
    scored_sorted = sorted(None, key=lambda item: item[0])
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=True)


def x__best_k_retention__mutmut_23(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(dirpath.glob("epoch*-metric*.pt"))
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(path)
        if epoch is None:
            continue
        scored.append((_score_key(metric, epoch, mode), path))
    if not scored or len(scored) <= keep_best_k:
        return
    scored_sorted = sorted(scored, key=None)
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=True)


def x__best_k_retention__mutmut_24(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(dirpath.glob("epoch*-metric*.pt"))
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(path)
        if epoch is None:
            continue
        scored.append((_score_key(metric, epoch, mode), path))
    if not scored or len(scored) <= keep_best_k:
        return
    scored_sorted = sorted(key=lambda item: item[0])
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=True)


def x__best_k_retention__mutmut_25(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(dirpath.glob("epoch*-metric*.pt"))
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(path)
        if epoch is None:
            continue
        scored.append((_score_key(metric, epoch, mode), path))
    if not scored or len(scored) <= keep_best_k:
        return
    scored_sorted = sorted(scored, )
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=True)


def x__best_k_retention__mutmut_26(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(dirpath.glob("epoch*-metric*.pt"))
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(path)
        if epoch is None:
            continue
        scored.append((_score_key(metric, epoch, mode), path))
    if not scored or len(scored) <= keep_best_k:
        return
    scored_sorted = sorted(scored, key=lambda item: None)
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=True)


def x__best_k_retention__mutmut_27(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(dirpath.glob("epoch*-metric*.pt"))
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(path)
        if epoch is None:
            continue
        scored.append((_score_key(metric, epoch, mode), path))
    if not scored or len(scored) <= keep_best_k:
        return
    scored_sorted = sorted(scored, key=lambda item: item[1])
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=True)


def x__best_k_retention__mutmut_28(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(dirpath.glob("epoch*-metric*.pt"))
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(path)
        if epoch is None:
            continue
        scored.append((_score_key(metric, epoch, mode), path))
    if not scored or len(scored) <= keep_best_k:
        return
    scored_sorted = sorted(scored, key=lambda item: item[0])
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(None):
            path.unlink(missing_ok=True)


def x__best_k_retention__mutmut_29(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(dirpath.glob("epoch*-metric*.pt"))
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(path)
        if epoch is None:
            continue
        scored.append((_score_key(metric, epoch, mode), path))
    if not scored or len(scored) <= keep_best_k:
        return
    scored_sorted = sorted(scored, key=lambda item: item[0])
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=None)


def x__best_k_retention__mutmut_30(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(dirpath.glob("epoch*-metric*.pt"))
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(path)
        if epoch is None:
            continue
        scored.append((_score_key(metric, epoch, mode), path))
    if not scored or len(scored) <= keep_best_k:
        return
    scored_sorted = sorted(scored, key=lambda item: item[0])
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=False)

x__best_k_retention__mutmut_mutants : ClassVar[MutantDict] = {
'x__best_k_retention__mutmut_1': x__best_k_retention__mutmut_1, 
    'x__best_k_retention__mutmut_2': x__best_k_retention__mutmut_2, 
    'x__best_k_retention__mutmut_3': x__best_k_retention__mutmut_3, 
    'x__best_k_retention__mutmut_4': x__best_k_retention__mutmut_4, 
    'x__best_k_retention__mutmut_5': x__best_k_retention__mutmut_5, 
    'x__best_k_retention__mutmut_6': x__best_k_retention__mutmut_6, 
    'x__best_k_retention__mutmut_7': x__best_k_retention__mutmut_7, 
    'x__best_k_retention__mutmut_8': x__best_k_retention__mutmut_8, 
    'x__best_k_retention__mutmut_9': x__best_k_retention__mutmut_9, 
    'x__best_k_retention__mutmut_10': x__best_k_retention__mutmut_10, 
    'x__best_k_retention__mutmut_11': x__best_k_retention__mutmut_11, 
    'x__best_k_retention__mutmut_12': x__best_k_retention__mutmut_12, 
    'x__best_k_retention__mutmut_13': x__best_k_retention__mutmut_13, 
    'x__best_k_retention__mutmut_14': x__best_k_retention__mutmut_14, 
    'x__best_k_retention__mutmut_15': x__best_k_retention__mutmut_15, 
    'x__best_k_retention__mutmut_16': x__best_k_retention__mutmut_16, 
    'x__best_k_retention__mutmut_17': x__best_k_retention__mutmut_17, 
    'x__best_k_retention__mutmut_18': x__best_k_retention__mutmut_18, 
    'x__best_k_retention__mutmut_19': x__best_k_retention__mutmut_19, 
    'x__best_k_retention__mutmut_20': x__best_k_retention__mutmut_20, 
    'x__best_k_retention__mutmut_21': x__best_k_retention__mutmut_21, 
    'x__best_k_retention__mutmut_22': x__best_k_retention__mutmut_22, 
    'x__best_k_retention__mutmut_23': x__best_k_retention__mutmut_23, 
    'x__best_k_retention__mutmut_24': x__best_k_retention__mutmut_24, 
    'x__best_k_retention__mutmut_25': x__best_k_retention__mutmut_25, 
    'x__best_k_retention__mutmut_26': x__best_k_retention__mutmut_26, 
    'x__best_k_retention__mutmut_27': x__best_k_retention__mutmut_27, 
    'x__best_k_retention__mutmut_28': x__best_k_retention__mutmut_28, 
    'x__best_k_retention__mutmut_29': x__best_k_retention__mutmut_29, 
    'x__best_k_retention__mutmut_30': x__best_k_retention__mutmut_30
}

def _best_k_retention(*args, **kwargs):
    result = _mutmut_trampoline(x__best_k_retention__mutmut_orig, x__best_k_retention__mutmut_mutants, args, kwargs)
    return result 

_best_k_retention.__signature__ = _mutmut_signature(x__best_k_retention__mutmut_orig)
x__best_k_retention__mutmut_orig.__name__ = 'x__best_k_retention'


def x_save_checkpoint__mutmut_orig(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_1(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "XXminXX",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_2(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "MIN",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_3(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 4,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_4(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is not None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_5(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError(None)
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_6(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("XXtorch is required for checkpointingXX")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_7(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("TORCH IS REQUIRED FOR CHECKPOINTING")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_8(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_9(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"XXminXX", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_10(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"MIN", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_11(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "XXmaxXX"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_12(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "MAX"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_13(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError(None)
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_14(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("XXmode must be 'min' or 'max'XX")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_15(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("MODE MUST BE 'MIN' OR 'MAX'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_16(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = None
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_17(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(None)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_18(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=None, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_19(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=None)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_20(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_21(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, )
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_22(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=False, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_23(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=False)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_24(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = None
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_25(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = None
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_26(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path * f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_27(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = None
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_28(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "XXmodel_stateXX": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_29(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "MODEL_STATE": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_30(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "XXoptimizer_stateXX": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_31(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "OPTIMIZER_STATE": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_32(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "XXval_metricXX": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_33(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "VAL_METRIC": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_34(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(None),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_35(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "XXepochXX": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_36(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "EPOCH": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_37(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(None),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_38(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "XXrng_cpuXX": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_39(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "RNG_CPU": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_40(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "XXrng_cuda_allXX": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_41(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "RNG_CUDA_ALL": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_42(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = None
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_43(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(None)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_44(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = None
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_45(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["XXpeft_stateXX"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_46(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["PEFT_STATE"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_47(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(None)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_48(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(None, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_49(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, None)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_50(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_51(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, )
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_52(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_53(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = None
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_54(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path * "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_55(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "XXmanifest.jsonXX"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_56(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "MANIFEST.JSON"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_57(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = None
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_58(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(None, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_59(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=None, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_60(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=None)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_61(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_62(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_63(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, )
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_64(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=3, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_65(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=False)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_66(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(None, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_67(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding=None)
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_68(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_69(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, )
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_70(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="XXutf-8XX")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_71(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="UTF-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_72(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug(None, manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_73(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", None, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_74(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, None)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_75(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug(manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_76(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_77(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, )
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_78(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("XXFailed to write checkpoint manifest at %s: %sXX", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_79(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_80(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("FAILED TO WRITE CHECKPOINT MANIFEST AT %S: %S", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_81(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(None, keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_82(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=None, mode=mode)
    return filename


def x_save_checkpoint__mutmut_83(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=None)
    return filename


def x_save_checkpoint__mutmut_84(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(keep_best_k=keep_best_k, mode=mode)
    return filename


def x_save_checkpoint__mutmut_85(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, mode=mode)
    return filename


def x_save_checkpoint__mutmut_86(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    lora_state = _extract_lora_state(model)
    if lora_state:
        payload["peft_state"] = lora_state
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    if manifest is not None:
        manifest_path = out_path / "manifest.json"
        try:
            manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
            manifest_path.write_text(manifest_payload, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.debug("Failed to write checkpoint manifest at %s: %s", manifest_path, exc)
    _best_k_retention(out_path, keep_best_k=keep_best_k, )
    return filename

x_save_checkpoint__mutmut_mutants : ClassVar[MutantDict] = {
'x_save_checkpoint__mutmut_1': x_save_checkpoint__mutmut_1, 
    'x_save_checkpoint__mutmut_2': x_save_checkpoint__mutmut_2, 
    'x_save_checkpoint__mutmut_3': x_save_checkpoint__mutmut_3, 
    'x_save_checkpoint__mutmut_4': x_save_checkpoint__mutmut_4, 
    'x_save_checkpoint__mutmut_5': x_save_checkpoint__mutmut_5, 
    'x_save_checkpoint__mutmut_6': x_save_checkpoint__mutmut_6, 
    'x_save_checkpoint__mutmut_7': x_save_checkpoint__mutmut_7, 
    'x_save_checkpoint__mutmut_8': x_save_checkpoint__mutmut_8, 
    'x_save_checkpoint__mutmut_9': x_save_checkpoint__mutmut_9, 
    'x_save_checkpoint__mutmut_10': x_save_checkpoint__mutmut_10, 
    'x_save_checkpoint__mutmut_11': x_save_checkpoint__mutmut_11, 
    'x_save_checkpoint__mutmut_12': x_save_checkpoint__mutmut_12, 
    'x_save_checkpoint__mutmut_13': x_save_checkpoint__mutmut_13, 
    'x_save_checkpoint__mutmut_14': x_save_checkpoint__mutmut_14, 
    'x_save_checkpoint__mutmut_15': x_save_checkpoint__mutmut_15, 
    'x_save_checkpoint__mutmut_16': x_save_checkpoint__mutmut_16, 
    'x_save_checkpoint__mutmut_17': x_save_checkpoint__mutmut_17, 
    'x_save_checkpoint__mutmut_18': x_save_checkpoint__mutmut_18, 
    'x_save_checkpoint__mutmut_19': x_save_checkpoint__mutmut_19, 
    'x_save_checkpoint__mutmut_20': x_save_checkpoint__mutmut_20, 
    'x_save_checkpoint__mutmut_21': x_save_checkpoint__mutmut_21, 
    'x_save_checkpoint__mutmut_22': x_save_checkpoint__mutmut_22, 
    'x_save_checkpoint__mutmut_23': x_save_checkpoint__mutmut_23, 
    'x_save_checkpoint__mutmut_24': x_save_checkpoint__mutmut_24, 
    'x_save_checkpoint__mutmut_25': x_save_checkpoint__mutmut_25, 
    'x_save_checkpoint__mutmut_26': x_save_checkpoint__mutmut_26, 
    'x_save_checkpoint__mutmut_27': x_save_checkpoint__mutmut_27, 
    'x_save_checkpoint__mutmut_28': x_save_checkpoint__mutmut_28, 
    'x_save_checkpoint__mutmut_29': x_save_checkpoint__mutmut_29, 
    'x_save_checkpoint__mutmut_30': x_save_checkpoint__mutmut_30, 
    'x_save_checkpoint__mutmut_31': x_save_checkpoint__mutmut_31, 
    'x_save_checkpoint__mutmut_32': x_save_checkpoint__mutmut_32, 
    'x_save_checkpoint__mutmut_33': x_save_checkpoint__mutmut_33, 
    'x_save_checkpoint__mutmut_34': x_save_checkpoint__mutmut_34, 
    'x_save_checkpoint__mutmut_35': x_save_checkpoint__mutmut_35, 
    'x_save_checkpoint__mutmut_36': x_save_checkpoint__mutmut_36, 
    'x_save_checkpoint__mutmut_37': x_save_checkpoint__mutmut_37, 
    'x_save_checkpoint__mutmut_38': x_save_checkpoint__mutmut_38, 
    'x_save_checkpoint__mutmut_39': x_save_checkpoint__mutmut_39, 
    'x_save_checkpoint__mutmut_40': x_save_checkpoint__mutmut_40, 
    'x_save_checkpoint__mutmut_41': x_save_checkpoint__mutmut_41, 
    'x_save_checkpoint__mutmut_42': x_save_checkpoint__mutmut_42, 
    'x_save_checkpoint__mutmut_43': x_save_checkpoint__mutmut_43, 
    'x_save_checkpoint__mutmut_44': x_save_checkpoint__mutmut_44, 
    'x_save_checkpoint__mutmut_45': x_save_checkpoint__mutmut_45, 
    'x_save_checkpoint__mutmut_46': x_save_checkpoint__mutmut_46, 
    'x_save_checkpoint__mutmut_47': x_save_checkpoint__mutmut_47, 
    'x_save_checkpoint__mutmut_48': x_save_checkpoint__mutmut_48, 
    'x_save_checkpoint__mutmut_49': x_save_checkpoint__mutmut_49, 
    'x_save_checkpoint__mutmut_50': x_save_checkpoint__mutmut_50, 
    'x_save_checkpoint__mutmut_51': x_save_checkpoint__mutmut_51, 
    'x_save_checkpoint__mutmut_52': x_save_checkpoint__mutmut_52, 
    'x_save_checkpoint__mutmut_53': x_save_checkpoint__mutmut_53, 
    'x_save_checkpoint__mutmut_54': x_save_checkpoint__mutmut_54, 
    'x_save_checkpoint__mutmut_55': x_save_checkpoint__mutmut_55, 
    'x_save_checkpoint__mutmut_56': x_save_checkpoint__mutmut_56, 
    'x_save_checkpoint__mutmut_57': x_save_checkpoint__mutmut_57, 
    'x_save_checkpoint__mutmut_58': x_save_checkpoint__mutmut_58, 
    'x_save_checkpoint__mutmut_59': x_save_checkpoint__mutmut_59, 
    'x_save_checkpoint__mutmut_60': x_save_checkpoint__mutmut_60, 
    'x_save_checkpoint__mutmut_61': x_save_checkpoint__mutmut_61, 
    'x_save_checkpoint__mutmut_62': x_save_checkpoint__mutmut_62, 
    'x_save_checkpoint__mutmut_63': x_save_checkpoint__mutmut_63, 
    'x_save_checkpoint__mutmut_64': x_save_checkpoint__mutmut_64, 
    'x_save_checkpoint__mutmut_65': x_save_checkpoint__mutmut_65, 
    'x_save_checkpoint__mutmut_66': x_save_checkpoint__mutmut_66, 
    'x_save_checkpoint__mutmut_67': x_save_checkpoint__mutmut_67, 
    'x_save_checkpoint__mutmut_68': x_save_checkpoint__mutmut_68, 
    'x_save_checkpoint__mutmut_69': x_save_checkpoint__mutmut_69, 
    'x_save_checkpoint__mutmut_70': x_save_checkpoint__mutmut_70, 
    'x_save_checkpoint__mutmut_71': x_save_checkpoint__mutmut_71, 
    'x_save_checkpoint__mutmut_72': x_save_checkpoint__mutmut_72, 
    'x_save_checkpoint__mutmut_73': x_save_checkpoint__mutmut_73, 
    'x_save_checkpoint__mutmut_74': x_save_checkpoint__mutmut_74, 
    'x_save_checkpoint__mutmut_75': x_save_checkpoint__mutmut_75, 
    'x_save_checkpoint__mutmut_76': x_save_checkpoint__mutmut_76, 
    'x_save_checkpoint__mutmut_77': x_save_checkpoint__mutmut_77, 
    'x_save_checkpoint__mutmut_78': x_save_checkpoint__mutmut_78, 
    'x_save_checkpoint__mutmut_79': x_save_checkpoint__mutmut_79, 
    'x_save_checkpoint__mutmut_80': x_save_checkpoint__mutmut_80, 
    'x_save_checkpoint__mutmut_81': x_save_checkpoint__mutmut_81, 
    'x_save_checkpoint__mutmut_82': x_save_checkpoint__mutmut_82, 
    'x_save_checkpoint__mutmut_83': x_save_checkpoint__mutmut_83, 
    'x_save_checkpoint__mutmut_84': x_save_checkpoint__mutmut_84, 
    'x_save_checkpoint__mutmut_85': x_save_checkpoint__mutmut_85, 
    'x_save_checkpoint__mutmut_86': x_save_checkpoint__mutmut_86
}

def save_checkpoint(*args, **kwargs):
    result = _mutmut_trampoline(x_save_checkpoint__mutmut_orig, x_save_checkpoint__mutmut_mutants, args, kwargs)
    return result 

save_checkpoint.__signature__ = _mutmut_signature(x_save_checkpoint__mutmut_orig)
x_save_checkpoint__mutmut_orig.__name__ = 'x_save_checkpoint'


def x_load_checkpoint__mutmut_orig(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_1(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = False,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_2(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = False,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_3(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is not None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_4(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError(None)
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_5(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("XXtorch is required for checkpointingXX")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_6(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("TORCH IS REQUIRED FOR CHECKPOINTING")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_7(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = None
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_8(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location and (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_9(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "XXcpuXX" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_10(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "CPU" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_11(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) and not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_12(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_13(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(None, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_14(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, None, None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_15(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr("cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_16(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_17(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", ) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_18(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "XXcudaXX", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_19(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "CUDA", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_20(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_21(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "XXcudaXX"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_22(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "CUDA"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_23(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = None
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_24(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(None, map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_25(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=None)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_26(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_27(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), )
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_28(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(None), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_29(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(None, strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_30(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=None)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_31(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_32(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], )
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_33(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["XXmodel_stateXX"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_34(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["MODEL_STATE"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_35(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(None, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_36(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, None)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_37(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_38(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, )
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_39(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None or "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_40(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_41(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "XXoptimizer_stateXX" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_42(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "OPTIMIZER_STATE" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_43(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" not in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_44(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(None)
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_45(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["XXoptimizer_stateXX"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_46(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["OPTIMIZER_STATE"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_47(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            None
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_48(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=None, cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_49(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=None)
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_50(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_51(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), )
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_52(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get(None), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_53(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("XXrng_cpuXX"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_54(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("RNG_CPU"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_55(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get(None))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_56(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("XXrng_cuda_allXX"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_57(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("RNG_CUDA_ALL"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_58(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(None), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_59(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get(None, 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_60(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", None)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_61(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get(0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_62(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", )), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_63(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("XXepochXX", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_64(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("EPOCH", 0)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_65(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 1)), float(payload.get("val_metric", float("nan")))


def x_load_checkpoint__mutmut_66(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(None)


def x_load_checkpoint__mutmut_67(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get(None, float("nan")))


def x_load_checkpoint__mutmut_68(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", None))


def x_load_checkpoint__mutmut_69(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get(float("nan")))


def x_load_checkpoint__mutmut_70(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", ))


def x_load_checkpoint__mutmut_71(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("XXval_metricXX", float("nan")))


def x_load_checkpoint__mutmut_72(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("VAL_METRIC", float("nan")))


def x_load_checkpoint__mutmut_73(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float(None)))


def x_load_checkpoint__mutmut_74(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("XXnanXX")))


def x_load_checkpoint__mutmut_75(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    _restore_lora_state(model, payload)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("NAN")))

x_load_checkpoint__mutmut_mutants : ClassVar[MutantDict] = {
'x_load_checkpoint__mutmut_1': x_load_checkpoint__mutmut_1, 
    'x_load_checkpoint__mutmut_2': x_load_checkpoint__mutmut_2, 
    'x_load_checkpoint__mutmut_3': x_load_checkpoint__mutmut_3, 
    'x_load_checkpoint__mutmut_4': x_load_checkpoint__mutmut_4, 
    'x_load_checkpoint__mutmut_5': x_load_checkpoint__mutmut_5, 
    'x_load_checkpoint__mutmut_6': x_load_checkpoint__mutmut_6, 
    'x_load_checkpoint__mutmut_7': x_load_checkpoint__mutmut_7, 
    'x_load_checkpoint__mutmut_8': x_load_checkpoint__mutmut_8, 
    'x_load_checkpoint__mutmut_9': x_load_checkpoint__mutmut_9, 
    'x_load_checkpoint__mutmut_10': x_load_checkpoint__mutmut_10, 
    'x_load_checkpoint__mutmut_11': x_load_checkpoint__mutmut_11, 
    'x_load_checkpoint__mutmut_12': x_load_checkpoint__mutmut_12, 
    'x_load_checkpoint__mutmut_13': x_load_checkpoint__mutmut_13, 
    'x_load_checkpoint__mutmut_14': x_load_checkpoint__mutmut_14, 
    'x_load_checkpoint__mutmut_15': x_load_checkpoint__mutmut_15, 
    'x_load_checkpoint__mutmut_16': x_load_checkpoint__mutmut_16, 
    'x_load_checkpoint__mutmut_17': x_load_checkpoint__mutmut_17, 
    'x_load_checkpoint__mutmut_18': x_load_checkpoint__mutmut_18, 
    'x_load_checkpoint__mutmut_19': x_load_checkpoint__mutmut_19, 
    'x_load_checkpoint__mutmut_20': x_load_checkpoint__mutmut_20, 
    'x_load_checkpoint__mutmut_21': x_load_checkpoint__mutmut_21, 
    'x_load_checkpoint__mutmut_22': x_load_checkpoint__mutmut_22, 
    'x_load_checkpoint__mutmut_23': x_load_checkpoint__mutmut_23, 
    'x_load_checkpoint__mutmut_24': x_load_checkpoint__mutmut_24, 
    'x_load_checkpoint__mutmut_25': x_load_checkpoint__mutmut_25, 
    'x_load_checkpoint__mutmut_26': x_load_checkpoint__mutmut_26, 
    'x_load_checkpoint__mutmut_27': x_load_checkpoint__mutmut_27, 
    'x_load_checkpoint__mutmut_28': x_load_checkpoint__mutmut_28, 
    'x_load_checkpoint__mutmut_29': x_load_checkpoint__mutmut_29, 
    'x_load_checkpoint__mutmut_30': x_load_checkpoint__mutmut_30, 
    'x_load_checkpoint__mutmut_31': x_load_checkpoint__mutmut_31, 
    'x_load_checkpoint__mutmut_32': x_load_checkpoint__mutmut_32, 
    'x_load_checkpoint__mutmut_33': x_load_checkpoint__mutmut_33, 
    'x_load_checkpoint__mutmut_34': x_load_checkpoint__mutmut_34, 
    'x_load_checkpoint__mutmut_35': x_load_checkpoint__mutmut_35, 
    'x_load_checkpoint__mutmut_36': x_load_checkpoint__mutmut_36, 
    'x_load_checkpoint__mutmut_37': x_load_checkpoint__mutmut_37, 
    'x_load_checkpoint__mutmut_38': x_load_checkpoint__mutmut_38, 
    'x_load_checkpoint__mutmut_39': x_load_checkpoint__mutmut_39, 
    'x_load_checkpoint__mutmut_40': x_load_checkpoint__mutmut_40, 
    'x_load_checkpoint__mutmut_41': x_load_checkpoint__mutmut_41, 
    'x_load_checkpoint__mutmut_42': x_load_checkpoint__mutmut_42, 
    'x_load_checkpoint__mutmut_43': x_load_checkpoint__mutmut_43, 
    'x_load_checkpoint__mutmut_44': x_load_checkpoint__mutmut_44, 
    'x_load_checkpoint__mutmut_45': x_load_checkpoint__mutmut_45, 
    'x_load_checkpoint__mutmut_46': x_load_checkpoint__mutmut_46, 
    'x_load_checkpoint__mutmut_47': x_load_checkpoint__mutmut_47, 
    'x_load_checkpoint__mutmut_48': x_load_checkpoint__mutmut_48, 
    'x_load_checkpoint__mutmut_49': x_load_checkpoint__mutmut_49, 
    'x_load_checkpoint__mutmut_50': x_load_checkpoint__mutmut_50, 
    'x_load_checkpoint__mutmut_51': x_load_checkpoint__mutmut_51, 
    'x_load_checkpoint__mutmut_52': x_load_checkpoint__mutmut_52, 
    'x_load_checkpoint__mutmut_53': x_load_checkpoint__mutmut_53, 
    'x_load_checkpoint__mutmut_54': x_load_checkpoint__mutmut_54, 
    'x_load_checkpoint__mutmut_55': x_load_checkpoint__mutmut_55, 
    'x_load_checkpoint__mutmut_56': x_load_checkpoint__mutmut_56, 
    'x_load_checkpoint__mutmut_57': x_load_checkpoint__mutmut_57, 
    'x_load_checkpoint__mutmut_58': x_load_checkpoint__mutmut_58, 
    'x_load_checkpoint__mutmut_59': x_load_checkpoint__mutmut_59, 
    'x_load_checkpoint__mutmut_60': x_load_checkpoint__mutmut_60, 
    'x_load_checkpoint__mutmut_61': x_load_checkpoint__mutmut_61, 
    'x_load_checkpoint__mutmut_62': x_load_checkpoint__mutmut_62, 
    'x_load_checkpoint__mutmut_63': x_load_checkpoint__mutmut_63, 
    'x_load_checkpoint__mutmut_64': x_load_checkpoint__mutmut_64, 
    'x_load_checkpoint__mutmut_65': x_load_checkpoint__mutmut_65, 
    'x_load_checkpoint__mutmut_66': x_load_checkpoint__mutmut_66, 
    'x_load_checkpoint__mutmut_67': x_load_checkpoint__mutmut_67, 
    'x_load_checkpoint__mutmut_68': x_load_checkpoint__mutmut_68, 
    'x_load_checkpoint__mutmut_69': x_load_checkpoint__mutmut_69, 
    'x_load_checkpoint__mutmut_70': x_load_checkpoint__mutmut_70, 
    'x_load_checkpoint__mutmut_71': x_load_checkpoint__mutmut_71, 
    'x_load_checkpoint__mutmut_72': x_load_checkpoint__mutmut_72, 
    'x_load_checkpoint__mutmut_73': x_load_checkpoint__mutmut_73, 
    'x_load_checkpoint__mutmut_74': x_load_checkpoint__mutmut_74, 
    'x_load_checkpoint__mutmut_75': x_load_checkpoint__mutmut_75
}

def load_checkpoint(*args, **kwargs):
    result = _mutmut_trampoline(x_load_checkpoint__mutmut_orig, x_load_checkpoint__mutmut_mutants, args, kwargs)
    return result 

load_checkpoint.__signature__ = _mutmut_signature(x_load_checkpoint__mutmut_orig)
x_load_checkpoint__mutmut_orig.__name__ = 'x_load_checkpoint'


__all__ = [
    "RNGState",
    "snapshot_rng_state",
    "restore_rng_state",
    "save_checkpoint",
    "load_checkpoint",
]
