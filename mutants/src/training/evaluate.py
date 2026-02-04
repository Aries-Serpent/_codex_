"""
Evaluate Module

This module provides functionality for evaluate.

Usage:
    from training.evaluate import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)
"""Simple evaluation helpers for language-model datasets."""


import contextlib
import json
import math
from collections.abc import Iterable, Mapping
from importlib import import_module
from pathlib import Path
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


def x__require_torch__mutmut_orig():
    return import_module("torch")


def x__require_torch__mutmut_1():
    return import_module(None)


def x__require_torch__mutmut_2():
    return import_module("XXtorchXX")


def x__require_torch__mutmut_3():
    return import_module("TORCH")

x__require_torch__mutmut_mutants : ClassVar[MutantDict] = {
'x__require_torch__mutmut_1': x__require_torch__mutmut_1, 
    'x__require_torch__mutmut_2': x__require_torch__mutmut_2, 
    'x__require_torch__mutmut_3': x__require_torch__mutmut_3
}

def _require_torch(*args, **kwargs):
    result = _mutmut_trampoline(x__require_torch__mutmut_orig, x__require_torch__mutmut_mutants, args, kwargs)
    return result 

_require_torch.__signature__ = _mutmut_signature(x__require_torch__mutmut_orig)
x__require_torch__mutmut_orig.__name__ = 'x__require_torch'


def x__infer_device__mutmut_orig(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_1(model: Any) -> str | None:
    if hasattr(None, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_2(model: Any) -> str | None:
    if hasattr(model, None):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_3(model: Any) -> str | None:
    if hasattr("device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_4(model: Any) -> str | None:
    if hasattr(model, ):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_5(model: Any) -> str | None:
    if hasattr(model, "XXdeviceXX"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_6(model: Any) -> str | None:
    if hasattr(model, "DEVICE"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_7(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = None
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_8(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(None, "device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_9(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, None)
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_10(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr("device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_11(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, )
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_12(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "XXdeviceXX")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_13(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "DEVICE")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_14(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(None)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_15(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = None
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_16(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(None, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_17(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, None, None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_18(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr("parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_19(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_20(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "parameters", )
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_21(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "XXparametersXX", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_22(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "PARAMETERS", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_23(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(None):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_24(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = None
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_25(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = None
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_26(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(None)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_27(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug(None, exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_28(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=None)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_29(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug(exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_30(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", )
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_31(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("XXException caught, returningXX", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_32(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_33(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("EXCEPTION CAUGHT, RETURNING", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_34(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=False)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_35(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = None
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_36(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(None, "device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_37(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, None, None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_38(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr("device", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_39(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_40(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", )
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_41(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "XXdeviceXX", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_42(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "DEVICE", None)
        return str(dev) if dev is not None else None
    return None


def x__infer_device__mutmut_43(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(None) if dev is not None else None
    return None


def x__infer_device__mutmut_44(model: Any) -> str | None:
    if hasattr(model, "device"):
        device = getattr(model, "device")
        return str(device)
    parameters = getattr(model, "parameters", None)
    if callable(parameters):
        iterator = parameters()
        try:
            first = next(iterator)
        except StopIteration:
            logger.debug("Exception caught, returning", exc_info=True)
            return None
        dev = getattr(first, "device", None)
        return str(dev) if dev is None else None
    return None

x__infer_device__mutmut_mutants : ClassVar[MutantDict] = {
'x__infer_device__mutmut_1': x__infer_device__mutmut_1, 
    'x__infer_device__mutmut_2': x__infer_device__mutmut_2, 
    'x__infer_device__mutmut_3': x__infer_device__mutmut_3, 
    'x__infer_device__mutmut_4': x__infer_device__mutmut_4, 
    'x__infer_device__mutmut_5': x__infer_device__mutmut_5, 
    'x__infer_device__mutmut_6': x__infer_device__mutmut_6, 
    'x__infer_device__mutmut_7': x__infer_device__mutmut_7, 
    'x__infer_device__mutmut_8': x__infer_device__mutmut_8, 
    'x__infer_device__mutmut_9': x__infer_device__mutmut_9, 
    'x__infer_device__mutmut_10': x__infer_device__mutmut_10, 
    'x__infer_device__mutmut_11': x__infer_device__mutmut_11, 
    'x__infer_device__mutmut_12': x__infer_device__mutmut_12, 
    'x__infer_device__mutmut_13': x__infer_device__mutmut_13, 
    'x__infer_device__mutmut_14': x__infer_device__mutmut_14, 
    'x__infer_device__mutmut_15': x__infer_device__mutmut_15, 
    'x__infer_device__mutmut_16': x__infer_device__mutmut_16, 
    'x__infer_device__mutmut_17': x__infer_device__mutmut_17, 
    'x__infer_device__mutmut_18': x__infer_device__mutmut_18, 
    'x__infer_device__mutmut_19': x__infer_device__mutmut_19, 
    'x__infer_device__mutmut_20': x__infer_device__mutmut_20, 
    'x__infer_device__mutmut_21': x__infer_device__mutmut_21, 
    'x__infer_device__mutmut_22': x__infer_device__mutmut_22, 
    'x__infer_device__mutmut_23': x__infer_device__mutmut_23, 
    'x__infer_device__mutmut_24': x__infer_device__mutmut_24, 
    'x__infer_device__mutmut_25': x__infer_device__mutmut_25, 
    'x__infer_device__mutmut_26': x__infer_device__mutmut_26, 
    'x__infer_device__mutmut_27': x__infer_device__mutmut_27, 
    'x__infer_device__mutmut_28': x__infer_device__mutmut_28, 
    'x__infer_device__mutmut_29': x__infer_device__mutmut_29, 
    'x__infer_device__mutmut_30': x__infer_device__mutmut_30, 
    'x__infer_device__mutmut_31': x__infer_device__mutmut_31, 
    'x__infer_device__mutmut_32': x__infer_device__mutmut_32, 
    'x__infer_device__mutmut_33': x__infer_device__mutmut_33, 
    'x__infer_device__mutmut_34': x__infer_device__mutmut_34, 
    'x__infer_device__mutmut_35': x__infer_device__mutmut_35, 
    'x__infer_device__mutmut_36': x__infer_device__mutmut_36, 
    'x__infer_device__mutmut_37': x__infer_device__mutmut_37, 
    'x__infer_device__mutmut_38': x__infer_device__mutmut_38, 
    'x__infer_device__mutmut_39': x__infer_device__mutmut_39, 
    'x__infer_device__mutmut_40': x__infer_device__mutmut_40, 
    'x__infer_device__mutmut_41': x__infer_device__mutmut_41, 
    'x__infer_device__mutmut_42': x__infer_device__mutmut_42, 
    'x__infer_device__mutmut_43': x__infer_device__mutmut_43, 
    'x__infer_device__mutmut_44': x__infer_device__mutmut_44
}

def _infer_device(*args, **kwargs):
    result = _mutmut_trampoline(x__infer_device__mutmut_orig, x__infer_device__mutmut_mutants, args, kwargs)
    return result 

_infer_device.__signature__ = _mutmut_signature(x__infer_device__mutmut_orig)
x__infer_device__mutmut_orig.__name__ = 'x__infer_device'


def x__encoding_to_mapping__mutmut_orig(batch: Any) -> Mapping[str, Any]:
    if isinstance(batch, Mapping):
        return batch
    data = getattr(batch, "data", None)
    if isinstance(data, Mapping):
        return data
    raise TypeError(f"Unsupported batch encoding type: {type(batch)!r}")


def x__encoding_to_mapping__mutmut_1(batch: Any) -> Mapping[str, Any]:
    if isinstance(batch, Mapping):
        return batch
    data = None
    if isinstance(data, Mapping):
        return data
    raise TypeError(f"Unsupported batch encoding type: {type(batch)!r}")


def x__encoding_to_mapping__mutmut_2(batch: Any) -> Mapping[str, Any]:
    if isinstance(batch, Mapping):
        return batch
    data = getattr(None, "data", None)
    if isinstance(data, Mapping):
        return data
    raise TypeError(f"Unsupported batch encoding type: {type(batch)!r}")


def x__encoding_to_mapping__mutmut_3(batch: Any) -> Mapping[str, Any]:
    if isinstance(batch, Mapping):
        return batch
    data = getattr(batch, None, None)
    if isinstance(data, Mapping):
        return data
    raise TypeError(f"Unsupported batch encoding type: {type(batch)!r}")


def x__encoding_to_mapping__mutmut_4(batch: Any) -> Mapping[str, Any]:
    if isinstance(batch, Mapping):
        return batch
    data = getattr("data", None)
    if isinstance(data, Mapping):
        return data
    raise TypeError(f"Unsupported batch encoding type: {type(batch)!r}")


def x__encoding_to_mapping__mutmut_5(batch: Any) -> Mapping[str, Any]:
    if isinstance(batch, Mapping):
        return batch
    data = getattr(batch, None)
    if isinstance(data, Mapping):
        return data
    raise TypeError(f"Unsupported batch encoding type: {type(batch)!r}")


def x__encoding_to_mapping__mutmut_6(batch: Any) -> Mapping[str, Any]:
    if isinstance(batch, Mapping):
        return batch
    data = getattr(batch, "data", )
    if isinstance(data, Mapping):
        return data
    raise TypeError(f"Unsupported batch encoding type: {type(batch)!r}")


def x__encoding_to_mapping__mutmut_7(batch: Any) -> Mapping[str, Any]:
    if isinstance(batch, Mapping):
        return batch
    data = getattr(batch, "XXdataXX", None)
    if isinstance(data, Mapping):
        return data
    raise TypeError(f"Unsupported batch encoding type: {type(batch)!r}")


def x__encoding_to_mapping__mutmut_8(batch: Any) -> Mapping[str, Any]:
    if isinstance(batch, Mapping):
        return batch
    data = getattr(batch, "DATA", None)
    if isinstance(data, Mapping):
        return data
    raise TypeError(f"Unsupported batch encoding type: {type(batch)!r}")


def x__encoding_to_mapping__mutmut_9(batch: Any) -> Mapping[str, Any]:
    if isinstance(batch, Mapping):
        return batch
    data = getattr(batch, "data", None)
    if isinstance(data, Mapping):
        return data
    raise TypeError(None)


def x__encoding_to_mapping__mutmut_10(batch: Any) -> Mapping[str, Any]:
    if isinstance(batch, Mapping):
        return batch
    data = getattr(batch, "data", None)
    if isinstance(data, Mapping):
        return data
    raise TypeError(f"Unsupported batch encoding type: {type(None)!r}")

x__encoding_to_mapping__mutmut_mutants : ClassVar[MutantDict] = {
'x__encoding_to_mapping__mutmut_1': x__encoding_to_mapping__mutmut_1, 
    'x__encoding_to_mapping__mutmut_2': x__encoding_to_mapping__mutmut_2, 
    'x__encoding_to_mapping__mutmut_3': x__encoding_to_mapping__mutmut_3, 
    'x__encoding_to_mapping__mutmut_4': x__encoding_to_mapping__mutmut_4, 
    'x__encoding_to_mapping__mutmut_5': x__encoding_to_mapping__mutmut_5, 
    'x__encoding_to_mapping__mutmut_6': x__encoding_to_mapping__mutmut_6, 
    'x__encoding_to_mapping__mutmut_7': x__encoding_to_mapping__mutmut_7, 
    'x__encoding_to_mapping__mutmut_8': x__encoding_to_mapping__mutmut_8, 
    'x__encoding_to_mapping__mutmut_9': x__encoding_to_mapping__mutmut_9, 
    'x__encoding_to_mapping__mutmut_10': x__encoding_to_mapping__mutmut_10
}

def _encoding_to_mapping(*args, **kwargs):
    result = _mutmut_trampoline(x__encoding_to_mapping__mutmut_orig, x__encoding_to_mapping__mutmut_mutants, args, kwargs)
    return result 

_encoding_to_mapping.__signature__ = _mutmut_signature(x__encoding_to_mapping__mutmut_orig)
x__encoding_to_mapping__mutmut_orig.__name__ = 'x__encoding_to_mapping'


def x__to_device__mutmut_orig(batch: Mapping[str, Any], device: str | None) -> dict[str, Any]:
    if device is None:
        return dict(batch)
    moved: dict[str, Any] = {}
    for key, value in batch.items():
        if hasattr(value, "to"):
            moved[key] = value.to(device)
        else:
            moved[key] = value
    return moved


def x__to_device__mutmut_1(batch: Mapping[str, Any], device: str | None) -> dict[str, Any]:
    if device is not None:
        return dict(batch)
    moved: dict[str, Any] = {}
    for key, value in batch.items():
        if hasattr(value, "to"):
            moved[key] = value.to(device)
        else:
            moved[key] = value
    return moved


def x__to_device__mutmut_2(batch: Mapping[str, Any], device: str | None) -> dict[str, Any]:
    if device is None:
        return dict(None)
    moved: dict[str, Any] = {}
    for key, value in batch.items():
        if hasattr(value, "to"):
            moved[key] = value.to(device)
        else:
            moved[key] = value
    return moved


def x__to_device__mutmut_3(batch: Mapping[str, Any], device: str | None) -> dict[str, Any]:
    if device is None:
        return dict(batch)
    moved: dict[str, Any] = None
    for key, value in batch.items():
        if hasattr(value, "to"):
            moved[key] = value.to(device)
        else:
            moved[key] = value
    return moved


def x__to_device__mutmut_4(batch: Mapping[str, Any], device: str | None) -> dict[str, Any]:
    if device is None:
        return dict(batch)
    moved: dict[str, Any] = {}
    for key, value in batch.items():
        if hasattr(None, "to"):
            moved[key] = value.to(device)
        else:
            moved[key] = value
    return moved


def x__to_device__mutmut_5(batch: Mapping[str, Any], device: str | None) -> dict[str, Any]:
    if device is None:
        return dict(batch)
    moved: dict[str, Any] = {}
    for key, value in batch.items():
        if hasattr(value, None):
            moved[key] = value.to(device)
        else:
            moved[key] = value
    return moved


def x__to_device__mutmut_6(batch: Mapping[str, Any], device: str | None) -> dict[str, Any]:
    if device is None:
        return dict(batch)
    moved: dict[str, Any] = {}
    for key, value in batch.items():
        if hasattr("to"):
            moved[key] = value.to(device)
        else:
            moved[key] = value
    return moved


def x__to_device__mutmut_7(batch: Mapping[str, Any], device: str | None) -> dict[str, Any]:
    if device is None:
        return dict(batch)
    moved: dict[str, Any] = {}
    for key, value in batch.items():
        if hasattr(value, ):
            moved[key] = value.to(device)
        else:
            moved[key] = value
    return moved


def x__to_device__mutmut_8(batch: Mapping[str, Any], device: str | None) -> dict[str, Any]:
    if device is None:
        return dict(batch)
    moved: dict[str, Any] = {}
    for key, value in batch.items():
        if hasattr(value, "XXtoXX"):
            moved[key] = value.to(device)
        else:
            moved[key] = value
    return moved


def x__to_device__mutmut_9(batch: Mapping[str, Any], device: str | None) -> dict[str, Any]:
    if device is None:
        return dict(batch)
    moved: dict[str, Any] = {}
    for key, value in batch.items():
        if hasattr(value, "TO"):
            moved[key] = value.to(device)
        else:
            moved[key] = value
    return moved


def x__to_device__mutmut_10(batch: Mapping[str, Any], device: str | None) -> dict[str, Any]:
    if device is None:
        return dict(batch)
    moved: dict[str, Any] = {}
    for key, value in batch.items():
        if hasattr(value, "to"):
            moved[key] = None
        else:
            moved[key] = value
    return moved


def x__to_device__mutmut_11(batch: Mapping[str, Any], device: str | None) -> dict[str, Any]:
    if device is None:
        return dict(batch)
    moved: dict[str, Any] = {}
    for key, value in batch.items():
        if hasattr(value, "to"):
            moved[key] = value.to(None)
        else:
            moved[key] = value
    return moved


def x__to_device__mutmut_12(batch: Mapping[str, Any], device: str | None) -> dict[str, Any]:
    if device is None:
        return dict(batch)
    moved: dict[str, Any] = {}
    for key, value in batch.items():
        if hasattr(value, "to"):
            moved[key] = value.to(device)
        else:
            moved[key] = None
    return moved

x__to_device__mutmut_mutants : ClassVar[MutantDict] = {
'x__to_device__mutmut_1': x__to_device__mutmut_1, 
    'x__to_device__mutmut_2': x__to_device__mutmut_2, 
    'x__to_device__mutmut_3': x__to_device__mutmut_3, 
    'x__to_device__mutmut_4': x__to_device__mutmut_4, 
    'x__to_device__mutmut_5': x__to_device__mutmut_5, 
    'x__to_device__mutmut_6': x__to_device__mutmut_6, 
    'x__to_device__mutmut_7': x__to_device__mutmut_7, 
    'x__to_device__mutmut_8': x__to_device__mutmut_8, 
    'x__to_device__mutmut_9': x__to_device__mutmut_9, 
    'x__to_device__mutmut_10': x__to_device__mutmut_10, 
    'x__to_device__mutmut_11': x__to_device__mutmut_11, 
    'x__to_device__mutmut_12': x__to_device__mutmut_12
}

def _to_device(*args, **kwargs):
    result = _mutmut_trampoline(x__to_device__mutmut_orig, x__to_device__mutmut_mutants, args, kwargs)
    return result 

_to_device.__signature__ = _mutmut_signature(x__to_device__mutmut_orig)
x__to_device__mutmut_orig.__name__ = 'x__to_device'


def x__loss_to_float__mutmut_orig(loss: Any) -> float:
    if isinstance(loss, (int, float)):
        return float(loss)
    if hasattr(loss, "detach"):
        detached = loss.detach()
        return _loss_to_float(detached)
    if hasattr(loss, "cpu"):
        cpu = loss.cpu()
        return _loss_to_float(cpu)
    if hasattr(loss, "item"):
        return float(loss.item())
    raise TypeError(f"Cannot convert loss of type {type(loss)!r} to float")


def x__loss_to_float__mutmut_1(loss: Any) -> float:
    if isinstance(loss, (int, float)):
        return float(None)
    if hasattr(loss, "detach"):
        detached = loss.detach()
        return _loss_to_float(detached)
    if hasattr(loss, "cpu"):
        cpu = loss.cpu()
        return _loss_to_float(cpu)
    if hasattr(loss, "item"):
        return float(loss.item())
    raise TypeError(f"Cannot convert loss of type {type(loss)!r} to float")


def x__loss_to_float__mutmut_2(loss: Any) -> float:
    if isinstance(loss, (int, float)):
        return float(loss)
    if hasattr(None, "detach"):
        detached = loss.detach()
        return _loss_to_float(detached)
    if hasattr(loss, "cpu"):
        cpu = loss.cpu()
        return _loss_to_float(cpu)
    if hasattr(loss, "item"):
        return float(loss.item())
    raise TypeError(f"Cannot convert loss of type {type(loss)!r} to float")


def x__loss_to_float__mutmut_3(loss: Any) -> float:
    if isinstance(loss, (int, float)):
        return float(loss)
    if hasattr(loss, None):
        detached = loss.detach()
        return _loss_to_float(detached)
    if hasattr(loss, "cpu"):
        cpu = loss.cpu()
        return _loss_to_float(cpu)
    if hasattr(loss, "item"):
        return float(loss.item())
    raise TypeError(f"Cannot convert loss of type {type(loss)!r} to float")


def x__loss_to_float__mutmut_4(loss: Any) -> float:
    if isinstance(loss, (int, float)):
        return float(loss)
    if hasattr("detach"):
        detached = loss.detach()
        return _loss_to_float(detached)
    if hasattr(loss, "cpu"):
        cpu = loss.cpu()
        return _loss_to_float(cpu)
    if hasattr(loss, "item"):
        return float(loss.item())
    raise TypeError(f"Cannot convert loss of type {type(loss)!r} to float")


def x__loss_to_float__mutmut_5(loss: Any) -> float:
    if isinstance(loss, (int, float)):
        return float(loss)
    if hasattr(loss, ):
        detached = loss.detach()
        return _loss_to_float(detached)
    if hasattr(loss, "cpu"):
        cpu = loss.cpu()
        return _loss_to_float(cpu)
    if hasattr(loss, "item"):
        return float(loss.item())
    raise TypeError(f"Cannot convert loss of type {type(loss)!r} to float")


def x__loss_to_float__mutmut_6(loss: Any) -> float:
    if isinstance(loss, (int, float)):
        return float(loss)
    if hasattr(loss, "XXdetachXX"):
        detached = loss.detach()
        return _loss_to_float(detached)
    if hasattr(loss, "cpu"):
        cpu = loss.cpu()
        return _loss_to_float(cpu)
    if hasattr(loss, "item"):
        return float(loss.item())
    raise TypeError(f"Cannot convert loss of type {type(loss)!r} to float")


def x__loss_to_float__mutmut_7(loss: Any) -> float:
    if isinstance(loss, (int, float)):
        return float(loss)
    if hasattr(loss, "DETACH"):
        detached = loss.detach()
        return _loss_to_float(detached)
    if hasattr(loss, "cpu"):
        cpu = loss.cpu()
        return _loss_to_float(cpu)
    if hasattr(loss, "item"):
        return float(loss.item())
    raise TypeError(f"Cannot convert loss of type {type(loss)!r} to float")


def x__loss_to_float__mutmut_8(loss: Any) -> float:
    if isinstance(loss, (int, float)):
        return float(loss)
    if hasattr(loss, "detach"):
        detached = None
        return _loss_to_float(detached)
    if hasattr(loss, "cpu"):
        cpu = loss.cpu()
        return _loss_to_float(cpu)
    if hasattr(loss, "item"):
        return float(loss.item())
    raise TypeError(f"Cannot convert loss of type {type(loss)!r} to float")


def x__loss_to_float__mutmut_9(loss: Any) -> float:
    if isinstance(loss, (int, float)):
        return float(loss)
    if hasattr(loss, "detach"):
        detached = loss.detach()
        return _loss_to_float(None)
    if hasattr(loss, "cpu"):
        cpu = loss.cpu()
        return _loss_to_float(cpu)
    if hasattr(loss, "item"):
        return float(loss.item())
    raise TypeError(f"Cannot convert loss of type {type(loss)!r} to float")


def x__loss_to_float__mutmut_10(loss: Any) -> float:
    if isinstance(loss, (int, float)):
        return float(loss)
    if hasattr(loss, "detach"):
        detached = loss.detach()
        return _loss_to_float(detached)
    if hasattr(None, "cpu"):
        cpu = loss.cpu()
        return _loss_to_float(cpu)
    if hasattr(loss, "item"):
        return float(loss.item())
    raise TypeError(f"Cannot convert loss of type {type(loss)!r} to float")


def x__loss_to_float__mutmut_11(loss: Any) -> float:
    if isinstance(loss, (int, float)):
        return float(loss)
    if hasattr(loss, "detach"):
        detached = loss.detach()
        return _loss_to_float(detached)
    if hasattr(loss, None):
        cpu = loss.cpu()
        return _loss_to_float(cpu)
    if hasattr(loss, "item"):
        return float(loss.item())
    raise TypeError(f"Cannot convert loss of type {type(loss)!r} to float")


def x__loss_to_float__mutmut_12(loss: Any) -> float:
    if isinstance(loss, (int, float)):
        return float(loss)
    if hasattr(loss, "detach"):
        detached = loss.detach()
        return _loss_to_float(detached)
    if hasattr("cpu"):
        cpu = loss.cpu()
        return _loss_to_float(cpu)
    if hasattr(loss, "item"):
        return float(loss.item())
    raise TypeError(f"Cannot convert loss of type {type(loss)!r} to float")


def x__loss_to_float__mutmut_13(loss: Any) -> float:
    if isinstance(loss, (int, float)):
        return float(loss)
    if hasattr(loss, "detach"):
        detached = loss.detach()
        return _loss_to_float(detached)
    if hasattr(loss, ):
        cpu = loss.cpu()
        return _loss_to_float(cpu)
    if hasattr(loss, "item"):
        return float(loss.item())
    raise TypeError(f"Cannot convert loss of type {type(loss)!r} to float")


def x__loss_to_float__mutmut_14(loss: Any) -> float:
    if isinstance(loss, (int, float)):
        return float(loss)
    if hasattr(loss, "detach"):
        detached = loss.detach()
        return _loss_to_float(detached)
    if hasattr(loss, "XXcpuXX"):
        cpu = loss.cpu()
        return _loss_to_float(cpu)
    if hasattr(loss, "item"):
        return float(loss.item())
    raise TypeError(f"Cannot convert loss of type {type(loss)!r} to float")


def x__loss_to_float__mutmut_15(loss: Any) -> float:
    if isinstance(loss, (int, float)):
        return float(loss)
    if hasattr(loss, "detach"):
        detached = loss.detach()
        return _loss_to_float(detached)
    if hasattr(loss, "CPU"):
        cpu = loss.cpu()
        return _loss_to_float(cpu)
    if hasattr(loss, "item"):
        return float(loss.item())
    raise TypeError(f"Cannot convert loss of type {type(loss)!r} to float")


def x__loss_to_float__mutmut_16(loss: Any) -> float:
    if isinstance(loss, (int, float)):
        return float(loss)
    if hasattr(loss, "detach"):
        detached = loss.detach()
        return _loss_to_float(detached)
    if hasattr(loss, "cpu"):
        cpu = None
        return _loss_to_float(cpu)
    if hasattr(loss, "item"):
        return float(loss.item())
    raise TypeError(f"Cannot convert loss of type {type(loss)!r} to float")


def x__loss_to_float__mutmut_17(loss: Any) -> float:
    if isinstance(loss, (int, float)):
        return float(loss)
    if hasattr(loss, "detach"):
        detached = loss.detach()
        return _loss_to_float(detached)
    if hasattr(loss, "cpu"):
        cpu = loss.cpu()
        return _loss_to_float(None)
    if hasattr(loss, "item"):
        return float(loss.item())
    raise TypeError(f"Cannot convert loss of type {type(loss)!r} to float")


def x__loss_to_float__mutmut_18(loss: Any) -> float:
    if isinstance(loss, (int, float)):
        return float(loss)
    if hasattr(loss, "detach"):
        detached = loss.detach()
        return _loss_to_float(detached)
    if hasattr(loss, "cpu"):
        cpu = loss.cpu()
        return _loss_to_float(cpu)
    if hasattr(None, "item"):
        return float(loss.item())
    raise TypeError(f"Cannot convert loss of type {type(loss)!r} to float")


def x__loss_to_float__mutmut_19(loss: Any) -> float:
    if isinstance(loss, (int, float)):
        return float(loss)
    if hasattr(loss, "detach"):
        detached = loss.detach()
        return _loss_to_float(detached)
    if hasattr(loss, "cpu"):
        cpu = loss.cpu()
        return _loss_to_float(cpu)
    if hasattr(loss, None):
        return float(loss.item())
    raise TypeError(f"Cannot convert loss of type {type(loss)!r} to float")


def x__loss_to_float__mutmut_20(loss: Any) -> float:
    if isinstance(loss, (int, float)):
        return float(loss)
    if hasattr(loss, "detach"):
        detached = loss.detach()
        return _loss_to_float(detached)
    if hasattr(loss, "cpu"):
        cpu = loss.cpu()
        return _loss_to_float(cpu)
    if hasattr("item"):
        return float(loss.item())
    raise TypeError(f"Cannot convert loss of type {type(loss)!r} to float")


def x__loss_to_float__mutmut_21(loss: Any) -> float:
    if isinstance(loss, (int, float)):
        return float(loss)
    if hasattr(loss, "detach"):
        detached = loss.detach()
        return _loss_to_float(detached)
    if hasattr(loss, "cpu"):
        cpu = loss.cpu()
        return _loss_to_float(cpu)
    if hasattr(loss, ):
        return float(loss.item())
    raise TypeError(f"Cannot convert loss of type {type(loss)!r} to float")


def x__loss_to_float__mutmut_22(loss: Any) -> float:
    if isinstance(loss, (int, float)):
        return float(loss)
    if hasattr(loss, "detach"):
        detached = loss.detach()
        return _loss_to_float(detached)
    if hasattr(loss, "cpu"):
        cpu = loss.cpu()
        return _loss_to_float(cpu)
    if hasattr(loss, "XXitemXX"):
        return float(loss.item())
    raise TypeError(f"Cannot convert loss of type {type(loss)!r} to float")


def x__loss_to_float__mutmut_23(loss: Any) -> float:
    if isinstance(loss, (int, float)):
        return float(loss)
    if hasattr(loss, "detach"):
        detached = loss.detach()
        return _loss_to_float(detached)
    if hasattr(loss, "cpu"):
        cpu = loss.cpu()
        return _loss_to_float(cpu)
    if hasattr(loss, "ITEM"):
        return float(loss.item())
    raise TypeError(f"Cannot convert loss of type {type(loss)!r} to float")


def x__loss_to_float__mutmut_24(loss: Any) -> float:
    if isinstance(loss, (int, float)):
        return float(loss)
    if hasattr(loss, "detach"):
        detached = loss.detach()
        return _loss_to_float(detached)
    if hasattr(loss, "cpu"):
        cpu = loss.cpu()
        return _loss_to_float(cpu)
    if hasattr(loss, "item"):
        return float(None)
    raise TypeError(f"Cannot convert loss of type {type(loss)!r} to float")


def x__loss_to_float__mutmut_25(loss: Any) -> float:
    if isinstance(loss, (int, float)):
        return float(loss)
    if hasattr(loss, "detach"):
        detached = loss.detach()
        return _loss_to_float(detached)
    if hasattr(loss, "cpu"):
        cpu = loss.cpu()
        return _loss_to_float(cpu)
    if hasattr(loss, "item"):
        return float(loss.item())
    raise TypeError(None)


def x__loss_to_float__mutmut_26(loss: Any) -> float:
    if isinstance(loss, (int, float)):
        return float(loss)
    if hasattr(loss, "detach"):
        detached = loss.detach()
        return _loss_to_float(detached)
    if hasattr(loss, "cpu"):
        cpu = loss.cpu()
        return _loss_to_float(cpu)
    if hasattr(loss, "item"):
        return float(loss.item())
    raise TypeError(f"Cannot convert loss of type {type(None)!r} to float")

x__loss_to_float__mutmut_mutants : ClassVar[MutantDict] = {
'x__loss_to_float__mutmut_1': x__loss_to_float__mutmut_1, 
    'x__loss_to_float__mutmut_2': x__loss_to_float__mutmut_2, 
    'x__loss_to_float__mutmut_3': x__loss_to_float__mutmut_3, 
    'x__loss_to_float__mutmut_4': x__loss_to_float__mutmut_4, 
    'x__loss_to_float__mutmut_5': x__loss_to_float__mutmut_5, 
    'x__loss_to_float__mutmut_6': x__loss_to_float__mutmut_6, 
    'x__loss_to_float__mutmut_7': x__loss_to_float__mutmut_7, 
    'x__loss_to_float__mutmut_8': x__loss_to_float__mutmut_8, 
    'x__loss_to_float__mutmut_9': x__loss_to_float__mutmut_9, 
    'x__loss_to_float__mutmut_10': x__loss_to_float__mutmut_10, 
    'x__loss_to_float__mutmut_11': x__loss_to_float__mutmut_11, 
    'x__loss_to_float__mutmut_12': x__loss_to_float__mutmut_12, 
    'x__loss_to_float__mutmut_13': x__loss_to_float__mutmut_13, 
    'x__loss_to_float__mutmut_14': x__loss_to_float__mutmut_14, 
    'x__loss_to_float__mutmut_15': x__loss_to_float__mutmut_15, 
    'x__loss_to_float__mutmut_16': x__loss_to_float__mutmut_16, 
    'x__loss_to_float__mutmut_17': x__loss_to_float__mutmut_17, 
    'x__loss_to_float__mutmut_18': x__loss_to_float__mutmut_18, 
    'x__loss_to_float__mutmut_19': x__loss_to_float__mutmut_19, 
    'x__loss_to_float__mutmut_20': x__loss_to_float__mutmut_20, 
    'x__loss_to_float__mutmut_21': x__loss_to_float__mutmut_21, 
    'x__loss_to_float__mutmut_22': x__loss_to_float__mutmut_22, 
    'x__loss_to_float__mutmut_23': x__loss_to_float__mutmut_23, 
    'x__loss_to_float__mutmut_24': x__loss_to_float__mutmut_24, 
    'x__loss_to_float__mutmut_25': x__loss_to_float__mutmut_25, 
    'x__loss_to_float__mutmut_26': x__loss_to_float__mutmut_26
}

def _loss_to_float(*args, **kwargs):
    result = _mutmut_trampoline(x__loss_to_float__mutmut_orig, x__loss_to_float__mutmut_mutants, args, kwargs)
    return result 

_loss_to_float.__signature__ = _mutmut_signature(x__loss_to_float__mutmut_orig)
x__loss_to_float__mutmut_orig.__name__ = 'x__loss_to_float'


def x__resolve_text__mutmut_orig(sample: Any, text_key: str) -> str | None:
    if sample is None:
        return None
    if isinstance(sample, str):
        return sample
    if isinstance(sample, Mapping):
        value = sample.get(text_key)
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return str(value)
    return str(sample)


def x__resolve_text__mutmut_1(sample: Any, text_key: str) -> str | None:
    if sample is not None:
        return None
    if isinstance(sample, str):
        return sample
    if isinstance(sample, Mapping):
        value = sample.get(text_key)
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return str(value)
    return str(sample)


def x__resolve_text__mutmut_2(sample: Any, text_key: str) -> str | None:
    if sample is None:
        return None
    if isinstance(sample, str):
        return sample
    if isinstance(sample, Mapping):
        value = None
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return str(value)
    return str(sample)


def x__resolve_text__mutmut_3(sample: Any, text_key: str) -> str | None:
    if sample is None:
        return None
    if isinstance(sample, str):
        return sample
    if isinstance(sample, Mapping):
        value = sample.get(None)
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return str(value)
    return str(sample)


def x__resolve_text__mutmut_4(sample: Any, text_key: str) -> str | None:
    if sample is None:
        return None
    if isinstance(sample, str):
        return sample
    if isinstance(sample, Mapping):
        value = sample.get(text_key)
        if value is not None:
            return None
        if isinstance(value, str):
            return value
        return str(value)
    return str(sample)


def x__resolve_text__mutmut_5(sample: Any, text_key: str) -> str | None:
    if sample is None:
        return None
    if isinstance(sample, str):
        return sample
    if isinstance(sample, Mapping):
        value = sample.get(text_key)
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return str(None)
    return str(sample)


def x__resolve_text__mutmut_6(sample: Any, text_key: str) -> str | None:
    if sample is None:
        return None
    if isinstance(sample, str):
        return sample
    if isinstance(sample, Mapping):
        value = sample.get(text_key)
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return str(value)
    return str(None)

x__resolve_text__mutmut_mutants : ClassVar[MutantDict] = {
'x__resolve_text__mutmut_1': x__resolve_text__mutmut_1, 
    'x__resolve_text__mutmut_2': x__resolve_text__mutmut_2, 
    'x__resolve_text__mutmut_3': x__resolve_text__mutmut_3, 
    'x__resolve_text__mutmut_4': x__resolve_text__mutmut_4, 
    'x__resolve_text__mutmut_5': x__resolve_text__mutmut_5, 
    'x__resolve_text__mutmut_6': x__resolve_text__mutmut_6
}

def _resolve_text(*args, **kwargs):
    result = _mutmut_trampoline(x__resolve_text__mutmut_orig, x__resolve_text__mutmut_mutants, args, kwargs)
    return result 

_resolve_text.__signature__ = _mutmut_signature(x__resolve_text__mutmut_orig)
x__resolve_text__mutmut_orig.__name__ = 'x__resolve_text'


def x_evaluate__mutmut_orig(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_1(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 129,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_2(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "XXtextXX",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_3(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "TEXT",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_4(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = None
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_5(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = None
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_6(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(None, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_7(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, None, contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_8(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", None)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_9(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr("no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_10(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_11(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", )
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_12(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "XXno_gradXX", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_13(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "NO_GRAD", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_14(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = None

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_15(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(None)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_16(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_17(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(None) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_18(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_19(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = ""
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_20(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_21(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=None, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_22(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=None)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_23(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_24(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, )
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_25(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=False, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_26(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=False)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_27(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = None

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_28(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open(None, encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_29(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding=None)

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_30(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open(encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_31(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", )

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_32(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("XXwXX", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_33(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("W", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_34(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="XXutf-8XX")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_35(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="UTF-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_36(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = None
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_37(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = None
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_38(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(None, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_39(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, None)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_40(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_41(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, )
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_42(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_43(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                break
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_44(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = None
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_45(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                None,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_46(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors=None,
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_47(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=None,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_48(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=None,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_49(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_50(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_51(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_52(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_53(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="XXptXX",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_54(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="PT",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_55(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=False,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_56(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = None
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_57(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(None)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_58(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = None
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_59(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(None, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_60(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, None)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_61(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_62(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, )
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_63(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs or "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_64(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "XXlabelsXX" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_65(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "LABELS" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_66(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_67(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "XXinput_idsXX" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_68(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "INPUT_IDS" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_69(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" not in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_70(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = None
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_71(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["XXlabelsXX"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_72(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["LABELS"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_73(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["XXinput_idsXX"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_74(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["INPUT_IDS"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_75(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = None
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_76(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = None
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_77(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(None)
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_78(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(None, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_79(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, None, outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_80(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", None))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_81(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr("loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_82(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_83(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", ))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_84(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "XXlossXX", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_85(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "LOSS", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_86(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(None)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_87(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_88(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump(None, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_89(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, None)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_90(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump(writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_91(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, )
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_92(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"XXtextXX": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_93(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"TEXT": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_94(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "XXlossXX": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_95(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "LOSS": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_96(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write(None)
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_97(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("XX\nXX")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_98(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_99(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = None
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_100(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count != 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_101(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 1:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_102(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"XXlossXX": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_103(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"LOSS": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_104(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float(None), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_105(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("XXnanXX"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_106(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("NAN"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_107(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "XXperplexityXX": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_108(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "PERPLEXITY": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_109(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float(None), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_110(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("XXnanXX"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_111(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("NAN"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_112(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "XXcountXX": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_113(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "COUNT": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_114(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 1}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_115(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = None
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_116(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) * count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_117(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(None) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_118(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = None
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_119(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(None)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_120(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(None)
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_121(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(None, exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_122(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=None)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_123(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_124(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", )
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_125(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=False)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_126(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = None
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_127(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float(None)
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_128(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("XXinfXX")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_129(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("INF")
    return {"loss": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_130(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"XXlossXX": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_131(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"LOSS": mean_loss, "perplexity": perplexity, "count": count}


def x_evaluate__mutmut_132(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "XXperplexityXX": perplexity, "count": count}


def x_evaluate__mutmut_133(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "PERPLEXITY": perplexity, "count": count}


def x_evaluate__mutmut_134(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "XXcountXX": count}


def x_evaluate__mutmut_135(
    model: Any,
    tokenizer: Any,
    dataset: Iterable[Any],
    *,
    max_length: int = 128,
    output_path: str | Path | None = None,
    text_key: str = "text",
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataset`` returning average loss and perplexity."""

    torch = _require_torch()
    no_grad = getattr(torch, "no_grad", contextlib.nullcontext)
    device = _infer_device(model)

    path = Path(output_path) if output_path is not None else None
    writer = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = path.open("w", encoding="utf-8")

    losses: list[float] = []
    try:
        for sample in dataset:
            text = _resolve_text(sample, text_key)
            if not text:
                continue
            batch = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            inputs = _encoding_to_mapping(batch)
            forward_inputs = _to_device(inputs, device)
            if "labels" not in forward_inputs and "input_ids" in forward_inputs:
                forward_inputs["labels"] = forward_inputs["input_ids"]
            with no_grad():  # type: ignore[misc]
                outputs = model(**forward_inputs)
            loss_value = _loss_to_float(getattr(outputs, "loss", outputs))
            losses.append(loss_value)
            if writer is not None:
                json.dump({"text": text, "loss": loss_value}, writer)
                writer.write("\n")
    finally:
        if writer is not None:
            writer.close()

    count = len(losses)
    if count == 0:
        return {"loss": float("nan"), "perplexity": float("nan"), "count": 0}
    mean_loss = sum(losses) / count
    try:
        perplexity = math.exp(mean_loss)
    except OverflowError as e:
        logger.debug(f"OverflowError: {e}")
        logger.warning(f"OverflowError: {e}", exc_info=True)
        perplexity = float("inf")
    return {"loss": mean_loss, "perplexity": perplexity, "COUNT": count}

x_evaluate__mutmut_mutants : ClassVar[MutantDict] = {
'x_evaluate__mutmut_1': x_evaluate__mutmut_1, 
    'x_evaluate__mutmut_2': x_evaluate__mutmut_2, 
    'x_evaluate__mutmut_3': x_evaluate__mutmut_3, 
    'x_evaluate__mutmut_4': x_evaluate__mutmut_4, 
    'x_evaluate__mutmut_5': x_evaluate__mutmut_5, 
    'x_evaluate__mutmut_6': x_evaluate__mutmut_6, 
    'x_evaluate__mutmut_7': x_evaluate__mutmut_7, 
    'x_evaluate__mutmut_8': x_evaluate__mutmut_8, 
    'x_evaluate__mutmut_9': x_evaluate__mutmut_9, 
    'x_evaluate__mutmut_10': x_evaluate__mutmut_10, 
    'x_evaluate__mutmut_11': x_evaluate__mutmut_11, 
    'x_evaluate__mutmut_12': x_evaluate__mutmut_12, 
    'x_evaluate__mutmut_13': x_evaluate__mutmut_13, 
    'x_evaluate__mutmut_14': x_evaluate__mutmut_14, 
    'x_evaluate__mutmut_15': x_evaluate__mutmut_15, 
    'x_evaluate__mutmut_16': x_evaluate__mutmut_16, 
    'x_evaluate__mutmut_17': x_evaluate__mutmut_17, 
    'x_evaluate__mutmut_18': x_evaluate__mutmut_18, 
    'x_evaluate__mutmut_19': x_evaluate__mutmut_19, 
    'x_evaluate__mutmut_20': x_evaluate__mutmut_20, 
    'x_evaluate__mutmut_21': x_evaluate__mutmut_21, 
    'x_evaluate__mutmut_22': x_evaluate__mutmut_22, 
    'x_evaluate__mutmut_23': x_evaluate__mutmut_23, 
    'x_evaluate__mutmut_24': x_evaluate__mutmut_24, 
    'x_evaluate__mutmut_25': x_evaluate__mutmut_25, 
    'x_evaluate__mutmut_26': x_evaluate__mutmut_26, 
    'x_evaluate__mutmut_27': x_evaluate__mutmut_27, 
    'x_evaluate__mutmut_28': x_evaluate__mutmut_28, 
    'x_evaluate__mutmut_29': x_evaluate__mutmut_29, 
    'x_evaluate__mutmut_30': x_evaluate__mutmut_30, 
    'x_evaluate__mutmut_31': x_evaluate__mutmut_31, 
    'x_evaluate__mutmut_32': x_evaluate__mutmut_32, 
    'x_evaluate__mutmut_33': x_evaluate__mutmut_33, 
    'x_evaluate__mutmut_34': x_evaluate__mutmut_34, 
    'x_evaluate__mutmut_35': x_evaluate__mutmut_35, 
    'x_evaluate__mutmut_36': x_evaluate__mutmut_36, 
    'x_evaluate__mutmut_37': x_evaluate__mutmut_37, 
    'x_evaluate__mutmut_38': x_evaluate__mutmut_38, 
    'x_evaluate__mutmut_39': x_evaluate__mutmut_39, 
    'x_evaluate__mutmut_40': x_evaluate__mutmut_40, 
    'x_evaluate__mutmut_41': x_evaluate__mutmut_41, 
    'x_evaluate__mutmut_42': x_evaluate__mutmut_42, 
    'x_evaluate__mutmut_43': x_evaluate__mutmut_43, 
    'x_evaluate__mutmut_44': x_evaluate__mutmut_44, 
    'x_evaluate__mutmut_45': x_evaluate__mutmut_45, 
    'x_evaluate__mutmut_46': x_evaluate__mutmut_46, 
    'x_evaluate__mutmut_47': x_evaluate__mutmut_47, 
    'x_evaluate__mutmut_48': x_evaluate__mutmut_48, 
    'x_evaluate__mutmut_49': x_evaluate__mutmut_49, 
    'x_evaluate__mutmut_50': x_evaluate__mutmut_50, 
    'x_evaluate__mutmut_51': x_evaluate__mutmut_51, 
    'x_evaluate__mutmut_52': x_evaluate__mutmut_52, 
    'x_evaluate__mutmut_53': x_evaluate__mutmut_53, 
    'x_evaluate__mutmut_54': x_evaluate__mutmut_54, 
    'x_evaluate__mutmut_55': x_evaluate__mutmut_55, 
    'x_evaluate__mutmut_56': x_evaluate__mutmut_56, 
    'x_evaluate__mutmut_57': x_evaluate__mutmut_57, 
    'x_evaluate__mutmut_58': x_evaluate__mutmut_58, 
    'x_evaluate__mutmut_59': x_evaluate__mutmut_59, 
    'x_evaluate__mutmut_60': x_evaluate__mutmut_60, 
    'x_evaluate__mutmut_61': x_evaluate__mutmut_61, 
    'x_evaluate__mutmut_62': x_evaluate__mutmut_62, 
    'x_evaluate__mutmut_63': x_evaluate__mutmut_63, 
    'x_evaluate__mutmut_64': x_evaluate__mutmut_64, 
    'x_evaluate__mutmut_65': x_evaluate__mutmut_65, 
    'x_evaluate__mutmut_66': x_evaluate__mutmut_66, 
    'x_evaluate__mutmut_67': x_evaluate__mutmut_67, 
    'x_evaluate__mutmut_68': x_evaluate__mutmut_68, 
    'x_evaluate__mutmut_69': x_evaluate__mutmut_69, 
    'x_evaluate__mutmut_70': x_evaluate__mutmut_70, 
    'x_evaluate__mutmut_71': x_evaluate__mutmut_71, 
    'x_evaluate__mutmut_72': x_evaluate__mutmut_72, 
    'x_evaluate__mutmut_73': x_evaluate__mutmut_73, 
    'x_evaluate__mutmut_74': x_evaluate__mutmut_74, 
    'x_evaluate__mutmut_75': x_evaluate__mutmut_75, 
    'x_evaluate__mutmut_76': x_evaluate__mutmut_76, 
    'x_evaluate__mutmut_77': x_evaluate__mutmut_77, 
    'x_evaluate__mutmut_78': x_evaluate__mutmut_78, 
    'x_evaluate__mutmut_79': x_evaluate__mutmut_79, 
    'x_evaluate__mutmut_80': x_evaluate__mutmut_80, 
    'x_evaluate__mutmut_81': x_evaluate__mutmut_81, 
    'x_evaluate__mutmut_82': x_evaluate__mutmut_82, 
    'x_evaluate__mutmut_83': x_evaluate__mutmut_83, 
    'x_evaluate__mutmut_84': x_evaluate__mutmut_84, 
    'x_evaluate__mutmut_85': x_evaluate__mutmut_85, 
    'x_evaluate__mutmut_86': x_evaluate__mutmut_86, 
    'x_evaluate__mutmut_87': x_evaluate__mutmut_87, 
    'x_evaluate__mutmut_88': x_evaluate__mutmut_88, 
    'x_evaluate__mutmut_89': x_evaluate__mutmut_89, 
    'x_evaluate__mutmut_90': x_evaluate__mutmut_90, 
    'x_evaluate__mutmut_91': x_evaluate__mutmut_91, 
    'x_evaluate__mutmut_92': x_evaluate__mutmut_92, 
    'x_evaluate__mutmut_93': x_evaluate__mutmut_93, 
    'x_evaluate__mutmut_94': x_evaluate__mutmut_94, 
    'x_evaluate__mutmut_95': x_evaluate__mutmut_95, 
    'x_evaluate__mutmut_96': x_evaluate__mutmut_96, 
    'x_evaluate__mutmut_97': x_evaluate__mutmut_97, 
    'x_evaluate__mutmut_98': x_evaluate__mutmut_98, 
    'x_evaluate__mutmut_99': x_evaluate__mutmut_99, 
    'x_evaluate__mutmut_100': x_evaluate__mutmut_100, 
    'x_evaluate__mutmut_101': x_evaluate__mutmut_101, 
    'x_evaluate__mutmut_102': x_evaluate__mutmut_102, 
    'x_evaluate__mutmut_103': x_evaluate__mutmut_103, 
    'x_evaluate__mutmut_104': x_evaluate__mutmut_104, 
    'x_evaluate__mutmut_105': x_evaluate__mutmut_105, 
    'x_evaluate__mutmut_106': x_evaluate__mutmut_106, 
    'x_evaluate__mutmut_107': x_evaluate__mutmut_107, 
    'x_evaluate__mutmut_108': x_evaluate__mutmut_108, 
    'x_evaluate__mutmut_109': x_evaluate__mutmut_109, 
    'x_evaluate__mutmut_110': x_evaluate__mutmut_110, 
    'x_evaluate__mutmut_111': x_evaluate__mutmut_111, 
    'x_evaluate__mutmut_112': x_evaluate__mutmut_112, 
    'x_evaluate__mutmut_113': x_evaluate__mutmut_113, 
    'x_evaluate__mutmut_114': x_evaluate__mutmut_114, 
    'x_evaluate__mutmut_115': x_evaluate__mutmut_115, 
    'x_evaluate__mutmut_116': x_evaluate__mutmut_116, 
    'x_evaluate__mutmut_117': x_evaluate__mutmut_117, 
    'x_evaluate__mutmut_118': x_evaluate__mutmut_118, 
    'x_evaluate__mutmut_119': x_evaluate__mutmut_119, 
    'x_evaluate__mutmut_120': x_evaluate__mutmut_120, 
    'x_evaluate__mutmut_121': x_evaluate__mutmut_121, 
    'x_evaluate__mutmut_122': x_evaluate__mutmut_122, 
    'x_evaluate__mutmut_123': x_evaluate__mutmut_123, 
    'x_evaluate__mutmut_124': x_evaluate__mutmut_124, 
    'x_evaluate__mutmut_125': x_evaluate__mutmut_125, 
    'x_evaluate__mutmut_126': x_evaluate__mutmut_126, 
    'x_evaluate__mutmut_127': x_evaluate__mutmut_127, 
    'x_evaluate__mutmut_128': x_evaluate__mutmut_128, 
    'x_evaluate__mutmut_129': x_evaluate__mutmut_129, 
    'x_evaluate__mutmut_130': x_evaluate__mutmut_130, 
    'x_evaluate__mutmut_131': x_evaluate__mutmut_131, 
    'x_evaluate__mutmut_132': x_evaluate__mutmut_132, 
    'x_evaluate__mutmut_133': x_evaluate__mutmut_133, 
    'x_evaluate__mutmut_134': x_evaluate__mutmut_134, 
    'x_evaluate__mutmut_135': x_evaluate__mutmut_135
}

def evaluate(*args, **kwargs):
    result = _mutmut_trampoline(x_evaluate__mutmut_orig, x_evaluate__mutmut_mutants, args, kwargs)
    return result 

evaluate.__signature__ = _mutmut_signature(x_evaluate__mutmut_orig)
x_evaluate__mutmut_orig.__name__ = 'x_evaluate'


__all__ = ["evaluate"]
