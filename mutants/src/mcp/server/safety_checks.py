"""
Safety Checks Module

This module provides functionality for safety checks.

Usage:
    from server.safety_checks import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations
import os
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


def x_live_tests_enabled__mutmut_orig() -> bool:
    """
    Returns True only if ENABLE_LIVE_TESTS env var is set to a truthy value.
    This function is used as a guard before attempting live network calls.
    """
    return os.environ.get("ENABLE_LIVE_TESTS", "false").lower() in ("1", "true", "yes")


def x_live_tests_enabled__mutmut_1() -> bool:
    """
    Returns True only if ENABLE_LIVE_TESTS env var is set to a truthy value.
    This function is used as a guard before attempting live network calls.
    """
    return os.environ.get("ENABLE_LIVE_TESTS", "false").upper() in ("1", "true", "yes")


def x_live_tests_enabled__mutmut_2() -> bool:
    """
    Returns True only if ENABLE_LIVE_TESTS env var is set to a truthy value.
    This function is used as a guard before attempting live network calls.
    """
    return os.environ.get(None, "false").lower() in ("1", "true", "yes")


def x_live_tests_enabled__mutmut_3() -> bool:
    """
    Returns True only if ENABLE_LIVE_TESTS env var is set to a truthy value.
    This function is used as a guard before attempting live network calls.
    """
    return os.environ.get("ENABLE_LIVE_TESTS", None).lower() in ("1", "true", "yes")


def x_live_tests_enabled__mutmut_4() -> bool:
    """
    Returns True only if ENABLE_LIVE_TESTS env var is set to a truthy value.
    This function is used as a guard before attempting live network calls.
    """
    return os.environ.get("false").lower() in ("1", "true", "yes")


def x_live_tests_enabled__mutmut_5() -> bool:
    """
    Returns True only if ENABLE_LIVE_TESTS env var is set to a truthy value.
    This function is used as a guard before attempting live network calls.
    """
    return os.environ.get("ENABLE_LIVE_TESTS", ).lower() in ("1", "true", "yes")


def x_live_tests_enabled__mutmut_6() -> bool:
    """
    Returns True only if ENABLE_LIVE_TESTS env var is set to a truthy value.
    This function is used as a guard before attempting live network calls.
    """
    return os.environ.get("XXENABLE_LIVE_TESTSXX", "false").lower() in ("1", "true", "yes")


def x_live_tests_enabled__mutmut_7() -> bool:
    """
    Returns True only if ENABLE_LIVE_TESTS env var is set to a truthy value.
    This function is used as a guard before attempting live network calls.
    """
    return os.environ.get("enable_live_tests", "false").lower() in ("1", "true", "yes")


def x_live_tests_enabled__mutmut_8() -> bool:
    """
    Returns True only if ENABLE_LIVE_TESTS env var is set to a truthy value.
    This function is used as a guard before attempting live network calls.
    """
    return os.environ.get("ENABLE_LIVE_TESTS", "XXfalseXX").lower() in ("1", "true", "yes")


def x_live_tests_enabled__mutmut_9() -> bool:
    """
    Returns True only if ENABLE_LIVE_TESTS env var is set to a truthy value.
    This function is used as a guard before attempting live network calls.
    """
    return os.environ.get("ENABLE_LIVE_TESTS", "FALSE").lower() in ("1", "true", "yes")


def x_live_tests_enabled__mutmut_10() -> bool:
    """
    Returns True only if ENABLE_LIVE_TESTS env var is set to a truthy value.
    This function is used as a guard before attempting live network calls.
    """
    return os.environ.get("ENABLE_LIVE_TESTS", "false").lower() not in ("1", "true", "yes")


def x_live_tests_enabled__mutmut_11() -> bool:
    """
    Returns True only if ENABLE_LIVE_TESTS env var is set to a truthy value.
    This function is used as a guard before attempting live network calls.
    """
    return os.environ.get("ENABLE_LIVE_TESTS", "false").lower() in ("XX1XX", "true", "yes")


def x_live_tests_enabled__mutmut_12() -> bool:
    """
    Returns True only if ENABLE_LIVE_TESTS env var is set to a truthy value.
    This function is used as a guard before attempting live network calls.
    """
    return os.environ.get("ENABLE_LIVE_TESTS", "false").lower() in ("1", "XXtrueXX", "yes")


def x_live_tests_enabled__mutmut_13() -> bool:
    """
    Returns True only if ENABLE_LIVE_TESTS env var is set to a truthy value.
    This function is used as a guard before attempting live network calls.
    """
    return os.environ.get("ENABLE_LIVE_TESTS", "false").lower() in ("1", "TRUE", "yes")


def x_live_tests_enabled__mutmut_14() -> bool:
    """
    Returns True only if ENABLE_LIVE_TESTS env var is set to a truthy value.
    This function is used as a guard before attempting live network calls.
    """
    return os.environ.get("ENABLE_LIVE_TESTS", "false").lower() in ("1", "true", "XXyesXX")


def x_live_tests_enabled__mutmut_15() -> bool:
    """
    Returns True only if ENABLE_LIVE_TESTS env var is set to a truthy value.
    This function is used as a guard before attempting live network calls.
    """
    return os.environ.get("ENABLE_LIVE_TESTS", "false").lower() in ("1", "true", "YES")

x_live_tests_enabled__mutmut_mutants : ClassVar[MutantDict] = {
'x_live_tests_enabled__mutmut_1': x_live_tests_enabled__mutmut_1, 
    'x_live_tests_enabled__mutmut_2': x_live_tests_enabled__mutmut_2, 
    'x_live_tests_enabled__mutmut_3': x_live_tests_enabled__mutmut_3, 
    'x_live_tests_enabled__mutmut_4': x_live_tests_enabled__mutmut_4, 
    'x_live_tests_enabled__mutmut_5': x_live_tests_enabled__mutmut_5, 
    'x_live_tests_enabled__mutmut_6': x_live_tests_enabled__mutmut_6, 
    'x_live_tests_enabled__mutmut_7': x_live_tests_enabled__mutmut_7, 
    'x_live_tests_enabled__mutmut_8': x_live_tests_enabled__mutmut_8, 
    'x_live_tests_enabled__mutmut_9': x_live_tests_enabled__mutmut_9, 
    'x_live_tests_enabled__mutmut_10': x_live_tests_enabled__mutmut_10, 
    'x_live_tests_enabled__mutmut_11': x_live_tests_enabled__mutmut_11, 
    'x_live_tests_enabled__mutmut_12': x_live_tests_enabled__mutmut_12, 
    'x_live_tests_enabled__mutmut_13': x_live_tests_enabled__mutmut_13, 
    'x_live_tests_enabled__mutmut_14': x_live_tests_enabled__mutmut_14, 
    'x_live_tests_enabled__mutmut_15': x_live_tests_enabled__mutmut_15
}

def live_tests_enabled(*args, **kwargs):
    result = _mutmut_trampoline(x_live_tests_enabled__mutmut_orig, x_live_tests_enabled__mutmut_mutants, args, kwargs)
    return result 

live_tests_enabled.__signature__ = _mutmut_signature(x_live_tests_enabled__mutmut_orig)
x_live_tests_enabled__mutmut_orig.__name__ = 'x_live_tests_enabled'
