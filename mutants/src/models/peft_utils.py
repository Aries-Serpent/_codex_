"""
Peft Utils Module

This module provides functionality for peft utils.

Usage:
    from models.peft_utils import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)
"""Helpers for interrogating optional PEFT adapters at runtime."""


from typing import Any
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


def x_summarize_peft__mutmut_orig(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_1(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug(None, exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_2(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=None)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_3(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug(exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_4(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", )
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_5(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("XXException caught, returningXX", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_6(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_7(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("EXCEPTION CAUGHT, RETURNING", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_8(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=False)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_9(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"XXpeftXX": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_10(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"PEFT": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_11(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "XXunavailableXX"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_12(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "UNAVAILABLE"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_13(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = None  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_14(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(None)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_15(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug(None, exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_16(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=None)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_17(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug(exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_18(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", )
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_19(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("XXException caught, returningXX", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_20(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_21(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("EXCEPTION CAUGHT, RETURNING", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_22(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=False)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_23(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"XXpeftXX": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_24(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"PEFT": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_25(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "XXnot_wrappedXX"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_26(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "NOT_WRAPPED"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_27(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "XXbase_model_typeXX": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_28(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "BASE_MODEL_TYPE": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_29(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(None, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_30(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, None, "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_31(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", None),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_32(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr("base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_33(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_34(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", ),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_35(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "XXbase_model_typeXX", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_36(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "BASE_MODEL_TYPE", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_37(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "XXunknownXX"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_38(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "UNKNOWN"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_39(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "XXadapter_model_typeXX": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_40(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "ADAPTER_MODEL_TYPE": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_41(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(None, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_42(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, None, "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_43(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", None),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_44(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr("adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_45(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_46(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", ),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_47(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "XXadapter_model_typeXX", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_48(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "ADAPTER_MODEL_TYPE", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_49(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "XXunknownXX"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_50(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "UNKNOWN"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_51(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "XXtrainable_paramsXX": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_52(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "TRAINABLE_PARAMS": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_53(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(None),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_54(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(None, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_55(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, None, -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_56(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", None)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_57(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr("trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_58(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_59(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", )),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_60(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "XXtrainable_paramsXX", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_61(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "TRAINABLE_PARAMS", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_62(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", +1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_63(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -2)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_64(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "XXtotal_paramsXX": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_65(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "TOTAL_PARAMS": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_66(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(None),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_67(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(None, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_68(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, None, -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_69(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", None)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_70(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr("total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_71(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_72(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", )),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_73(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "XXtotal_paramsXX", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_74(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "TOTAL_PARAMS", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_75(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", +1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_76(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -2)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_77(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "XXnum_adapter_layersXX": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_78(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "NUM_ADAPTER_LAYERS": int(getattr(status, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_79(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(None),
    }


def x_summarize_peft__mutmut_80(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(None, "num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_81(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, None, -1)),
    }


def x_summarize_peft__mutmut_82(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", None)),
    }


def x_summarize_peft__mutmut_83(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr("num_adapter_layers", -1)),
    }


def x_summarize_peft__mutmut_84(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, -1)),
    }


def x_summarize_peft__mutmut_85(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", )),
    }


def x_summarize_peft__mutmut_86(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "XXnum_adapter_layersXX", -1)),
    }


def x_summarize_peft__mutmut_87(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "NUM_ADAPTER_LAYERS", -1)),
    }


def x_summarize_peft__mutmut_88(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", +1)),
    }


def x_summarize_peft__mutmut_89(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -2)),
    }

x_summarize_peft__mutmut_mutants : ClassVar[MutantDict] = {
'x_summarize_peft__mutmut_1': x_summarize_peft__mutmut_1, 
    'x_summarize_peft__mutmut_2': x_summarize_peft__mutmut_2, 
    'x_summarize_peft__mutmut_3': x_summarize_peft__mutmut_3, 
    'x_summarize_peft__mutmut_4': x_summarize_peft__mutmut_4, 
    'x_summarize_peft__mutmut_5': x_summarize_peft__mutmut_5, 
    'x_summarize_peft__mutmut_6': x_summarize_peft__mutmut_6, 
    'x_summarize_peft__mutmut_7': x_summarize_peft__mutmut_7, 
    'x_summarize_peft__mutmut_8': x_summarize_peft__mutmut_8, 
    'x_summarize_peft__mutmut_9': x_summarize_peft__mutmut_9, 
    'x_summarize_peft__mutmut_10': x_summarize_peft__mutmut_10, 
    'x_summarize_peft__mutmut_11': x_summarize_peft__mutmut_11, 
    'x_summarize_peft__mutmut_12': x_summarize_peft__mutmut_12, 
    'x_summarize_peft__mutmut_13': x_summarize_peft__mutmut_13, 
    'x_summarize_peft__mutmut_14': x_summarize_peft__mutmut_14, 
    'x_summarize_peft__mutmut_15': x_summarize_peft__mutmut_15, 
    'x_summarize_peft__mutmut_16': x_summarize_peft__mutmut_16, 
    'x_summarize_peft__mutmut_17': x_summarize_peft__mutmut_17, 
    'x_summarize_peft__mutmut_18': x_summarize_peft__mutmut_18, 
    'x_summarize_peft__mutmut_19': x_summarize_peft__mutmut_19, 
    'x_summarize_peft__mutmut_20': x_summarize_peft__mutmut_20, 
    'x_summarize_peft__mutmut_21': x_summarize_peft__mutmut_21, 
    'x_summarize_peft__mutmut_22': x_summarize_peft__mutmut_22, 
    'x_summarize_peft__mutmut_23': x_summarize_peft__mutmut_23, 
    'x_summarize_peft__mutmut_24': x_summarize_peft__mutmut_24, 
    'x_summarize_peft__mutmut_25': x_summarize_peft__mutmut_25, 
    'x_summarize_peft__mutmut_26': x_summarize_peft__mutmut_26, 
    'x_summarize_peft__mutmut_27': x_summarize_peft__mutmut_27, 
    'x_summarize_peft__mutmut_28': x_summarize_peft__mutmut_28, 
    'x_summarize_peft__mutmut_29': x_summarize_peft__mutmut_29, 
    'x_summarize_peft__mutmut_30': x_summarize_peft__mutmut_30, 
    'x_summarize_peft__mutmut_31': x_summarize_peft__mutmut_31, 
    'x_summarize_peft__mutmut_32': x_summarize_peft__mutmut_32, 
    'x_summarize_peft__mutmut_33': x_summarize_peft__mutmut_33, 
    'x_summarize_peft__mutmut_34': x_summarize_peft__mutmut_34, 
    'x_summarize_peft__mutmut_35': x_summarize_peft__mutmut_35, 
    'x_summarize_peft__mutmut_36': x_summarize_peft__mutmut_36, 
    'x_summarize_peft__mutmut_37': x_summarize_peft__mutmut_37, 
    'x_summarize_peft__mutmut_38': x_summarize_peft__mutmut_38, 
    'x_summarize_peft__mutmut_39': x_summarize_peft__mutmut_39, 
    'x_summarize_peft__mutmut_40': x_summarize_peft__mutmut_40, 
    'x_summarize_peft__mutmut_41': x_summarize_peft__mutmut_41, 
    'x_summarize_peft__mutmut_42': x_summarize_peft__mutmut_42, 
    'x_summarize_peft__mutmut_43': x_summarize_peft__mutmut_43, 
    'x_summarize_peft__mutmut_44': x_summarize_peft__mutmut_44, 
    'x_summarize_peft__mutmut_45': x_summarize_peft__mutmut_45, 
    'x_summarize_peft__mutmut_46': x_summarize_peft__mutmut_46, 
    'x_summarize_peft__mutmut_47': x_summarize_peft__mutmut_47, 
    'x_summarize_peft__mutmut_48': x_summarize_peft__mutmut_48, 
    'x_summarize_peft__mutmut_49': x_summarize_peft__mutmut_49, 
    'x_summarize_peft__mutmut_50': x_summarize_peft__mutmut_50, 
    'x_summarize_peft__mutmut_51': x_summarize_peft__mutmut_51, 
    'x_summarize_peft__mutmut_52': x_summarize_peft__mutmut_52, 
    'x_summarize_peft__mutmut_53': x_summarize_peft__mutmut_53, 
    'x_summarize_peft__mutmut_54': x_summarize_peft__mutmut_54, 
    'x_summarize_peft__mutmut_55': x_summarize_peft__mutmut_55, 
    'x_summarize_peft__mutmut_56': x_summarize_peft__mutmut_56, 
    'x_summarize_peft__mutmut_57': x_summarize_peft__mutmut_57, 
    'x_summarize_peft__mutmut_58': x_summarize_peft__mutmut_58, 
    'x_summarize_peft__mutmut_59': x_summarize_peft__mutmut_59, 
    'x_summarize_peft__mutmut_60': x_summarize_peft__mutmut_60, 
    'x_summarize_peft__mutmut_61': x_summarize_peft__mutmut_61, 
    'x_summarize_peft__mutmut_62': x_summarize_peft__mutmut_62, 
    'x_summarize_peft__mutmut_63': x_summarize_peft__mutmut_63, 
    'x_summarize_peft__mutmut_64': x_summarize_peft__mutmut_64, 
    'x_summarize_peft__mutmut_65': x_summarize_peft__mutmut_65, 
    'x_summarize_peft__mutmut_66': x_summarize_peft__mutmut_66, 
    'x_summarize_peft__mutmut_67': x_summarize_peft__mutmut_67, 
    'x_summarize_peft__mutmut_68': x_summarize_peft__mutmut_68, 
    'x_summarize_peft__mutmut_69': x_summarize_peft__mutmut_69, 
    'x_summarize_peft__mutmut_70': x_summarize_peft__mutmut_70, 
    'x_summarize_peft__mutmut_71': x_summarize_peft__mutmut_71, 
    'x_summarize_peft__mutmut_72': x_summarize_peft__mutmut_72, 
    'x_summarize_peft__mutmut_73': x_summarize_peft__mutmut_73, 
    'x_summarize_peft__mutmut_74': x_summarize_peft__mutmut_74, 
    'x_summarize_peft__mutmut_75': x_summarize_peft__mutmut_75, 
    'x_summarize_peft__mutmut_76': x_summarize_peft__mutmut_76, 
    'x_summarize_peft__mutmut_77': x_summarize_peft__mutmut_77, 
    'x_summarize_peft__mutmut_78': x_summarize_peft__mutmut_78, 
    'x_summarize_peft__mutmut_79': x_summarize_peft__mutmut_79, 
    'x_summarize_peft__mutmut_80': x_summarize_peft__mutmut_80, 
    'x_summarize_peft__mutmut_81': x_summarize_peft__mutmut_81, 
    'x_summarize_peft__mutmut_82': x_summarize_peft__mutmut_82, 
    'x_summarize_peft__mutmut_83': x_summarize_peft__mutmut_83, 
    'x_summarize_peft__mutmut_84': x_summarize_peft__mutmut_84, 
    'x_summarize_peft__mutmut_85': x_summarize_peft__mutmut_85, 
    'x_summarize_peft__mutmut_86': x_summarize_peft__mutmut_86, 
    'x_summarize_peft__mutmut_87': x_summarize_peft__mutmut_87, 
    'x_summarize_peft__mutmut_88': x_summarize_peft__mutmut_88, 
    'x_summarize_peft__mutmut_89': x_summarize_peft__mutmut_89
}

def summarize_peft(*args, **kwargs):
    result = _mutmut_trampoline(x_summarize_peft__mutmut_orig, x_summarize_peft__mutmut_mutants, args, kwargs)
    return result 

summarize_peft.__signature__ = _mutmut_signature(x_summarize_peft__mutmut_orig)
x_summarize_peft__mutmut_orig.__name__ = 'x_summarize_peft'


__all__ = ["summarize_peft"]
