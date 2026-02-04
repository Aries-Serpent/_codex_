"""Secret management helpers used across infrastructure tooling."""

from __future__ import annotations

import math
import secrets
import string
import time
from collections.abc import Iterable
from dataclasses import dataclass, field

from .core import SecurityError
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


def x__character_pool__mutmut_orig(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(pool, len(set(value)))
    return max(pool, 1)


def x__character_pool__mutmut_1(value: str) -> int:
    pool = None
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(pool, len(set(value)))
    return max(pool, 1)


def x__character_pool__mutmut_2(value: str) -> int:
    pool = 1
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(pool, len(set(value)))
    return max(pool, 1)


def x__character_pool__mutmut_3(value: str) -> int:
    pool = 0
    if any(None):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(pool, len(set(value)))
    return max(pool, 1)


def x__character_pool__mutmut_4(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool = 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(pool, len(set(value)))
    return max(pool, 1)


def x__character_pool__mutmut_5(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool -= 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(pool, len(set(value)))
    return max(pool, 1)


def x__character_pool__mutmut_6(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 27
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(pool, len(set(value)))
    return max(pool, 1)


def x__character_pool__mutmut_7(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 26
    if any(None):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(pool, len(set(value)))
    return max(pool, 1)


def x__character_pool__mutmut_8(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool = 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(pool, len(set(value)))
    return max(pool, 1)


def x__character_pool__mutmut_9(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool -= 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(pool, len(set(value)))
    return max(pool, 1)


def x__character_pool__mutmut_10(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool += 27
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(pool, len(set(value)))
    return max(pool, 1)


def x__character_pool__mutmut_11(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(None):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(pool, len(set(value)))
    return max(pool, 1)


def x__character_pool__mutmut_12(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool = 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(pool, len(set(value)))
    return max(pool, 1)


def x__character_pool__mutmut_13(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool -= 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(pool, len(set(value)))
    return max(pool, 1)


def x__character_pool__mutmut_14(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool += 11
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(pool, len(set(value)))
    return max(pool, 1)


def x__character_pool__mutmut_15(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(None):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(pool, len(set(value)))
    return max(pool, 1)


def x__character_pool__mutmut_16(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch not in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(pool, len(set(value)))
    return max(pool, 1)


def x__character_pool__mutmut_17(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool = len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(pool, len(set(value)))
    return max(pool, 1)


def x__character_pool__mutmut_18(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool -= len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(pool, len(set(value)))
    return max(pool, 1)


def x__character_pool__mutmut_19(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = None
    pool += len(extras)
    pool = max(pool, len(set(value)))
    return max(pool, 1)


def x__character_pool__mutmut_20(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(pool, len(set(value)))
    return max(pool, 1)


def x__character_pool__mutmut_21(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits - string.punctuation
    }
    pool += len(extras)
    pool = max(pool, len(set(value)))
    return max(pool, 1)


def x__character_pool__mutmut_22(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters - string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(pool, len(set(value)))
    return max(pool, 1)


def x__character_pool__mutmut_23(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool = len(extras)
    pool = max(pool, len(set(value)))
    return max(pool, 1)


def x__character_pool__mutmut_24(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool -= len(extras)
    pool = max(pool, len(set(value)))
    return max(pool, 1)


def x__character_pool__mutmut_25(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = None
    return max(pool, 1)


def x__character_pool__mutmut_26(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(None, len(set(value)))
    return max(pool, 1)


def x__character_pool__mutmut_27(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(pool, None)
    return max(pool, 1)


def x__character_pool__mutmut_28(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(len(set(value)))
    return max(pool, 1)


def x__character_pool__mutmut_29(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(pool, )
    return max(pool, 1)


def x__character_pool__mutmut_30(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(pool, len(set(value)))
    return max(None, 1)


def x__character_pool__mutmut_31(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(pool, len(set(value)))
    return max(pool, None)


def x__character_pool__mutmut_32(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(pool, len(set(value)))
    return max(1)


def x__character_pool__mutmut_33(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(pool, len(set(value)))
    return max(pool, )


def x__character_pool__mutmut_34(value: str) -> int:
    pool = 0
    if any(ch.islower() for ch in value):
        pool += 26
    if any(ch.isupper() for ch in value):
        pool += 26
    if any(ch.isdigit() for ch in value):
        pool += 10
    if any(ch in string.punctuation for ch in value):
        pool += len(string.punctuation)
    extras = {
        ch for ch in value if ch not in string.ascii_letters + string.digits + string.punctuation
    }
    pool += len(extras)
    pool = max(pool, len(set(value)))
    return max(pool, 2)

x__character_pool__mutmut_mutants : ClassVar[MutantDict] = {
'x__character_pool__mutmut_1': x__character_pool__mutmut_1, 
    'x__character_pool__mutmut_2': x__character_pool__mutmut_2, 
    'x__character_pool__mutmut_3': x__character_pool__mutmut_3, 
    'x__character_pool__mutmut_4': x__character_pool__mutmut_4, 
    'x__character_pool__mutmut_5': x__character_pool__mutmut_5, 
    'x__character_pool__mutmut_6': x__character_pool__mutmut_6, 
    'x__character_pool__mutmut_7': x__character_pool__mutmut_7, 
    'x__character_pool__mutmut_8': x__character_pool__mutmut_8, 
    'x__character_pool__mutmut_9': x__character_pool__mutmut_9, 
    'x__character_pool__mutmut_10': x__character_pool__mutmut_10, 
    'x__character_pool__mutmut_11': x__character_pool__mutmut_11, 
    'x__character_pool__mutmut_12': x__character_pool__mutmut_12, 
    'x__character_pool__mutmut_13': x__character_pool__mutmut_13, 
    'x__character_pool__mutmut_14': x__character_pool__mutmut_14, 
    'x__character_pool__mutmut_15': x__character_pool__mutmut_15, 
    'x__character_pool__mutmut_16': x__character_pool__mutmut_16, 
    'x__character_pool__mutmut_17': x__character_pool__mutmut_17, 
    'x__character_pool__mutmut_18': x__character_pool__mutmut_18, 
    'x__character_pool__mutmut_19': x__character_pool__mutmut_19, 
    'x__character_pool__mutmut_20': x__character_pool__mutmut_20, 
    'x__character_pool__mutmut_21': x__character_pool__mutmut_21, 
    'x__character_pool__mutmut_22': x__character_pool__mutmut_22, 
    'x__character_pool__mutmut_23': x__character_pool__mutmut_23, 
    'x__character_pool__mutmut_24': x__character_pool__mutmut_24, 
    'x__character_pool__mutmut_25': x__character_pool__mutmut_25, 
    'x__character_pool__mutmut_26': x__character_pool__mutmut_26, 
    'x__character_pool__mutmut_27': x__character_pool__mutmut_27, 
    'x__character_pool__mutmut_28': x__character_pool__mutmut_28, 
    'x__character_pool__mutmut_29': x__character_pool__mutmut_29, 
    'x__character_pool__mutmut_30': x__character_pool__mutmut_30, 
    'x__character_pool__mutmut_31': x__character_pool__mutmut_31, 
    'x__character_pool__mutmut_32': x__character_pool__mutmut_32, 
    'x__character_pool__mutmut_33': x__character_pool__mutmut_33, 
    'x__character_pool__mutmut_34': x__character_pool__mutmut_34
}

def _character_pool(*args, **kwargs):
    result = _mutmut_trampoline(x__character_pool__mutmut_orig, x__character_pool__mutmut_mutants, args, kwargs)
    return result 

_character_pool.__signature__ = _mutmut_signature(x__character_pool__mutmut_orig)
x__character_pool__mutmut_orig.__name__ = 'x__character_pool'


def x_check_secret_entropy__mutmut_orig(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_1(
    value: str,
    *,
    min_length: int = 13,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_2(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 4,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_3(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_4(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return True

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_5(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) <= min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_6(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return True

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_7(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = None
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_8(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 1
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_9(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(None):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_10(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories = 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_11(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories -= 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_12(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 2
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_13(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(None):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_14(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories = 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_15(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories -= 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_16(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 2
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_17(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(None):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_18(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories = 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_19(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories -= 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_20(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 2
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_21(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(None):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_22(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch not in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_23(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories = 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_24(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories -= 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_25(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 2

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_26(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories or categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_27(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories <= require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_28(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return True

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_29(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_30(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = None
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_31(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(None)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_32(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = None
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_33(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) / math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_34(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(None)
        if estimated_bits < min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_35(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits <= min_bits:
            return False

    return True


def x_check_secret_entropy__mutmut_36(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return True

    return True


def x_check_secret_entropy__mutmut_37(
    value: str,
    *,
    min_length: int = 12,
    require_categories: int = 3,
    min_bits: float | None = None,
) -> bool:
    """Return True when the provided secret meets strength requirements."""

    if not value:
        return False

    if len(value) < min_length:
        return False

    categories = 0
    if any(ch.islower() for ch in value):
        categories += 1
    if any(ch.isupper() for ch in value):
        categories += 1
    if any(ch.isdigit() for ch in value):
        categories += 1
    if any(ch in string.punctuation for ch in value):
        categories += 1

    if require_categories and categories < require_categories:
        return False

    if min_bits is not None:
        pool = _character_pool(value)
        estimated_bits = len(value) * math.log2(pool)
        if estimated_bits < min_bits:
            return False

    return False

x_check_secret_entropy__mutmut_mutants : ClassVar[MutantDict] = {
'x_check_secret_entropy__mutmut_1': x_check_secret_entropy__mutmut_1, 
    'x_check_secret_entropy__mutmut_2': x_check_secret_entropy__mutmut_2, 
    'x_check_secret_entropy__mutmut_3': x_check_secret_entropy__mutmut_3, 
    'x_check_secret_entropy__mutmut_4': x_check_secret_entropy__mutmut_4, 
    'x_check_secret_entropy__mutmut_5': x_check_secret_entropy__mutmut_5, 
    'x_check_secret_entropy__mutmut_6': x_check_secret_entropy__mutmut_6, 
    'x_check_secret_entropy__mutmut_7': x_check_secret_entropy__mutmut_7, 
    'x_check_secret_entropy__mutmut_8': x_check_secret_entropy__mutmut_8, 
    'x_check_secret_entropy__mutmut_9': x_check_secret_entropy__mutmut_9, 
    'x_check_secret_entropy__mutmut_10': x_check_secret_entropy__mutmut_10, 
    'x_check_secret_entropy__mutmut_11': x_check_secret_entropy__mutmut_11, 
    'x_check_secret_entropy__mutmut_12': x_check_secret_entropy__mutmut_12, 
    'x_check_secret_entropy__mutmut_13': x_check_secret_entropy__mutmut_13, 
    'x_check_secret_entropy__mutmut_14': x_check_secret_entropy__mutmut_14, 
    'x_check_secret_entropy__mutmut_15': x_check_secret_entropy__mutmut_15, 
    'x_check_secret_entropy__mutmut_16': x_check_secret_entropy__mutmut_16, 
    'x_check_secret_entropy__mutmut_17': x_check_secret_entropy__mutmut_17, 
    'x_check_secret_entropy__mutmut_18': x_check_secret_entropy__mutmut_18, 
    'x_check_secret_entropy__mutmut_19': x_check_secret_entropy__mutmut_19, 
    'x_check_secret_entropy__mutmut_20': x_check_secret_entropy__mutmut_20, 
    'x_check_secret_entropy__mutmut_21': x_check_secret_entropy__mutmut_21, 
    'x_check_secret_entropy__mutmut_22': x_check_secret_entropy__mutmut_22, 
    'x_check_secret_entropy__mutmut_23': x_check_secret_entropy__mutmut_23, 
    'x_check_secret_entropy__mutmut_24': x_check_secret_entropy__mutmut_24, 
    'x_check_secret_entropy__mutmut_25': x_check_secret_entropy__mutmut_25, 
    'x_check_secret_entropy__mutmut_26': x_check_secret_entropy__mutmut_26, 
    'x_check_secret_entropy__mutmut_27': x_check_secret_entropy__mutmut_27, 
    'x_check_secret_entropy__mutmut_28': x_check_secret_entropy__mutmut_28, 
    'x_check_secret_entropy__mutmut_29': x_check_secret_entropy__mutmut_29, 
    'x_check_secret_entropy__mutmut_30': x_check_secret_entropy__mutmut_30, 
    'x_check_secret_entropy__mutmut_31': x_check_secret_entropy__mutmut_31, 
    'x_check_secret_entropy__mutmut_32': x_check_secret_entropy__mutmut_32, 
    'x_check_secret_entropy__mutmut_33': x_check_secret_entropy__mutmut_33, 
    'x_check_secret_entropy__mutmut_34': x_check_secret_entropy__mutmut_34, 
    'x_check_secret_entropy__mutmut_35': x_check_secret_entropy__mutmut_35, 
    'x_check_secret_entropy__mutmut_36': x_check_secret_entropy__mutmut_36, 
    'x_check_secret_entropy__mutmut_37': x_check_secret_entropy__mutmut_37
}

def check_secret_entropy(*args, **kwargs):
    result = _mutmut_trampoline(x_check_secret_entropy__mutmut_orig, x_check_secret_entropy__mutmut_mutants, args, kwargs)
    return result 

check_secret_entropy.__signature__ = _mutmut_signature(x_check_secret_entropy__mutmut_orig)
x_check_secret_entropy__mutmut_orig.__name__ = 'x_check_secret_entropy'


@dataclass
class SecretRotationPolicy:
    """Policy defining rotation thresholds for secrets."""

    min_entropy_bits: float = 48.0
    max_age_seconds: int = 60 * 60 * 24 * 30
    history_size: int = 5


@dataclass
class SecretRotationState:
    """Book-keeping information for a managed secret."""

    identifier: str
    last_rotated: float = field(default_factory=lambda: time.time())
    history: list[str] = field(default_factory=list)

    def remember(self, secret: str) -> None:
        self.history.append(secret)
        if len(self.history) > SecretRotationPolicy().history_size:
            self.history = self.history[-SecretRotationPolicy().history_size :]


def x_rotate_secret__mutmut_orig(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_1(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = None
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_2(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy and SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_3(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = None
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_4(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator and secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_5(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = None

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_6(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now + state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_7(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated <= policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_8(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError(None)

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_9(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("XXSecret rotation requested too soonXX")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_10(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_11(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("SECRET ROTATION REQUESTED TOO SOON")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_12(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = None
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_13(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "XXabcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+XX"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_14(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_15(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_16(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(None):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_17(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(11):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_18(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = None
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_19(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(None)
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_20(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "XXXX".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_21(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(None) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_22(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(None))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_23(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(33))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_24(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            None,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_25(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=None,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_26(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=None,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_27(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=None,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_28(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_29(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_30(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_31(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_32(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=1,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_33(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=1,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_34(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = None
            state.remember(candidate)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_35(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(None)
            return candidate

    raise SecurityError("Unable to generate high-entropy secret")


def x_rotate_secret__mutmut_36(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError(None)


def x_rotate_secret__mutmut_37(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("XXUnable to generate high-entropy secretXX")


def x_rotate_secret__mutmut_38(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("unable to generate high-entropy secret")


def x_rotate_secret__mutmut_39(
    state: SecretRotationState,
    *,
    policy: SecretRotationPolicy | None = None,
    generator: secrets.SystemRandom | None = None,
) -> str:
    """Rotate the secret associated with the provided state."""

    policy = policy or SecretRotationPolicy()
    generator = generator or secrets.SystemRandom()
    now = time.time()

    if now - state.last_rotated < policy.max_age_seconds:
        raise SecurityError("Secret rotation requested too soon")

    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    for _ in range(10):
        candidate = "".join(generator.choice(alphabet) for _ in range(32))
        if check_secret_entropy(
            candidate,
            min_bits=policy.min_entropy_bits,
            min_length=0,
            require_categories=0,
        ):
            state.last_rotated = now
            state.remember(candidate)
            return candidate

    raise SecurityError("UNABLE TO GENERATE HIGH-ENTROPY SECRET")

x_rotate_secret__mutmut_mutants : ClassVar[MutantDict] = {
'x_rotate_secret__mutmut_1': x_rotate_secret__mutmut_1, 
    'x_rotate_secret__mutmut_2': x_rotate_secret__mutmut_2, 
    'x_rotate_secret__mutmut_3': x_rotate_secret__mutmut_3, 
    'x_rotate_secret__mutmut_4': x_rotate_secret__mutmut_4, 
    'x_rotate_secret__mutmut_5': x_rotate_secret__mutmut_5, 
    'x_rotate_secret__mutmut_6': x_rotate_secret__mutmut_6, 
    'x_rotate_secret__mutmut_7': x_rotate_secret__mutmut_7, 
    'x_rotate_secret__mutmut_8': x_rotate_secret__mutmut_8, 
    'x_rotate_secret__mutmut_9': x_rotate_secret__mutmut_9, 
    'x_rotate_secret__mutmut_10': x_rotate_secret__mutmut_10, 
    'x_rotate_secret__mutmut_11': x_rotate_secret__mutmut_11, 
    'x_rotate_secret__mutmut_12': x_rotate_secret__mutmut_12, 
    'x_rotate_secret__mutmut_13': x_rotate_secret__mutmut_13, 
    'x_rotate_secret__mutmut_14': x_rotate_secret__mutmut_14, 
    'x_rotate_secret__mutmut_15': x_rotate_secret__mutmut_15, 
    'x_rotate_secret__mutmut_16': x_rotate_secret__mutmut_16, 
    'x_rotate_secret__mutmut_17': x_rotate_secret__mutmut_17, 
    'x_rotate_secret__mutmut_18': x_rotate_secret__mutmut_18, 
    'x_rotate_secret__mutmut_19': x_rotate_secret__mutmut_19, 
    'x_rotate_secret__mutmut_20': x_rotate_secret__mutmut_20, 
    'x_rotate_secret__mutmut_21': x_rotate_secret__mutmut_21, 
    'x_rotate_secret__mutmut_22': x_rotate_secret__mutmut_22, 
    'x_rotate_secret__mutmut_23': x_rotate_secret__mutmut_23, 
    'x_rotate_secret__mutmut_24': x_rotate_secret__mutmut_24, 
    'x_rotate_secret__mutmut_25': x_rotate_secret__mutmut_25, 
    'x_rotate_secret__mutmut_26': x_rotate_secret__mutmut_26, 
    'x_rotate_secret__mutmut_27': x_rotate_secret__mutmut_27, 
    'x_rotate_secret__mutmut_28': x_rotate_secret__mutmut_28, 
    'x_rotate_secret__mutmut_29': x_rotate_secret__mutmut_29, 
    'x_rotate_secret__mutmut_30': x_rotate_secret__mutmut_30, 
    'x_rotate_secret__mutmut_31': x_rotate_secret__mutmut_31, 
    'x_rotate_secret__mutmut_32': x_rotate_secret__mutmut_32, 
    'x_rotate_secret__mutmut_33': x_rotate_secret__mutmut_33, 
    'x_rotate_secret__mutmut_34': x_rotate_secret__mutmut_34, 
    'x_rotate_secret__mutmut_35': x_rotate_secret__mutmut_35, 
    'x_rotate_secret__mutmut_36': x_rotate_secret__mutmut_36, 
    'x_rotate_secret__mutmut_37': x_rotate_secret__mutmut_37, 
    'x_rotate_secret__mutmut_38': x_rotate_secret__mutmut_38, 
    'x_rotate_secret__mutmut_39': x_rotate_secret__mutmut_39
}

def rotate_secret(*args, **kwargs):
    result = _mutmut_trampoline(x_rotate_secret__mutmut_orig, x_rotate_secret__mutmut_mutants, args, kwargs)
    return result 

rotate_secret.__signature__ = _mutmut_signature(x_rotate_secret__mutmut_orig)
x_rotate_secret__mutmut_orig.__name__ = 'x_rotate_secret'


def x_assert_secret_not_reused__mutmut_orig(secret: str, history: Iterable[str]) -> None:
    if secret in history:
        raise SecurityError("Secret reuse detected")


def x_assert_secret_not_reused__mutmut_1(secret: str, history: Iterable[str]) -> None:
    if secret not in history:
        raise SecurityError("Secret reuse detected")


def x_assert_secret_not_reused__mutmut_2(secret: str, history: Iterable[str]) -> None:
    if secret in history:
        raise SecurityError(None)


def x_assert_secret_not_reused__mutmut_3(secret: str, history: Iterable[str]) -> None:
    if secret in history:
        raise SecurityError("XXSecret reuse detectedXX")


def x_assert_secret_not_reused__mutmut_4(secret: str, history: Iterable[str]) -> None:
    if secret in history:
        raise SecurityError("secret reuse detected")


def x_assert_secret_not_reused__mutmut_5(secret: str, history: Iterable[str]) -> None:
    if secret in history:
        raise SecurityError("SECRET REUSE DETECTED")

x_assert_secret_not_reused__mutmut_mutants : ClassVar[MutantDict] = {
'x_assert_secret_not_reused__mutmut_1': x_assert_secret_not_reused__mutmut_1, 
    'x_assert_secret_not_reused__mutmut_2': x_assert_secret_not_reused__mutmut_2, 
    'x_assert_secret_not_reused__mutmut_3': x_assert_secret_not_reused__mutmut_3, 
    'x_assert_secret_not_reused__mutmut_4': x_assert_secret_not_reused__mutmut_4, 
    'x_assert_secret_not_reused__mutmut_5': x_assert_secret_not_reused__mutmut_5
}

def assert_secret_not_reused(*args, **kwargs):
    result = _mutmut_trampoline(x_assert_secret_not_reused__mutmut_orig, x_assert_secret_not_reused__mutmut_mutants, args, kwargs)
    return result 

assert_secret_not_reused.__signature__ = _mutmut_signature(x_assert_secret_not_reused__mutmut_orig)
x_assert_secret_not_reused__mutmut_orig.__name__ = 'x_assert_secret_not_reused'
