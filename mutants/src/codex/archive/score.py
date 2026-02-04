"""
Score Module

This module provides functionality for score.

Usage:
    from archive.score import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

from dataclasses import dataclass
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


@dataclass
class ScoreInput:
    age_days: int
    ref_count: int
    coverage: float
    has_deprecation_tag: bool


def x_archive_score__mutmut_orig(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_1(
    inp: ScoreInput,
    *,
    w1: float = 1.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_2(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 1.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_3(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 1.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_4(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 1.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_5(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 181,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_6(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = None
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_7(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 1.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_8(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s = w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_9(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s -= w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_10(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 / (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_11(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (2.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_12(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days >= tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_13(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 1.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_14(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s = w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_15(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s -= w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_16(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 / (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_17(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (2.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_18(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count != 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_19(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 1 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_20(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 1.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_21(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s = w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_22(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s -= w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_23(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 / (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_24(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (2.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_25(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage < 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_26(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 1.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_27(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 1.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_28(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s = w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_29(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s -= w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_30(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 / (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_31(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (2.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_32(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 1.0)
    return round(min(max(s, 0.0), 1.0), 3)


def x_archive_score__mutmut_33(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(None, 3)


def x_archive_score__mutmut_34(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), None)


def x_archive_score__mutmut_35(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(3)


def x_archive_score__mutmut_36(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), )


def x_archive_score__mutmut_37(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(None, 1.0), 3)


def x_archive_score__mutmut_38(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), None), 3)


def x_archive_score__mutmut_39(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(1.0), 3)


def x_archive_score__mutmut_40(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), ), 3)


def x_archive_score__mutmut_41(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(None, 0.0), 1.0), 3)


def x_archive_score__mutmut_42(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, None), 1.0), 3)


def x_archive_score__mutmut_43(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(0.0), 1.0), 3)


def x_archive_score__mutmut_44(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, ), 1.0), 3)


def x_archive_score__mutmut_45(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 1.0), 1.0), 3)


def x_archive_score__mutmut_46(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 2.0), 3)


def x_archive_score__mutmut_47(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 4)

x_archive_score__mutmut_mutants : ClassVar[MutantDict] = {
'x_archive_score__mutmut_1': x_archive_score__mutmut_1, 
    'x_archive_score__mutmut_2': x_archive_score__mutmut_2, 
    'x_archive_score__mutmut_3': x_archive_score__mutmut_3, 
    'x_archive_score__mutmut_4': x_archive_score__mutmut_4, 
    'x_archive_score__mutmut_5': x_archive_score__mutmut_5, 
    'x_archive_score__mutmut_6': x_archive_score__mutmut_6, 
    'x_archive_score__mutmut_7': x_archive_score__mutmut_7, 
    'x_archive_score__mutmut_8': x_archive_score__mutmut_8, 
    'x_archive_score__mutmut_9': x_archive_score__mutmut_9, 
    'x_archive_score__mutmut_10': x_archive_score__mutmut_10, 
    'x_archive_score__mutmut_11': x_archive_score__mutmut_11, 
    'x_archive_score__mutmut_12': x_archive_score__mutmut_12, 
    'x_archive_score__mutmut_13': x_archive_score__mutmut_13, 
    'x_archive_score__mutmut_14': x_archive_score__mutmut_14, 
    'x_archive_score__mutmut_15': x_archive_score__mutmut_15, 
    'x_archive_score__mutmut_16': x_archive_score__mutmut_16, 
    'x_archive_score__mutmut_17': x_archive_score__mutmut_17, 
    'x_archive_score__mutmut_18': x_archive_score__mutmut_18, 
    'x_archive_score__mutmut_19': x_archive_score__mutmut_19, 
    'x_archive_score__mutmut_20': x_archive_score__mutmut_20, 
    'x_archive_score__mutmut_21': x_archive_score__mutmut_21, 
    'x_archive_score__mutmut_22': x_archive_score__mutmut_22, 
    'x_archive_score__mutmut_23': x_archive_score__mutmut_23, 
    'x_archive_score__mutmut_24': x_archive_score__mutmut_24, 
    'x_archive_score__mutmut_25': x_archive_score__mutmut_25, 
    'x_archive_score__mutmut_26': x_archive_score__mutmut_26, 
    'x_archive_score__mutmut_27': x_archive_score__mutmut_27, 
    'x_archive_score__mutmut_28': x_archive_score__mutmut_28, 
    'x_archive_score__mutmut_29': x_archive_score__mutmut_29, 
    'x_archive_score__mutmut_30': x_archive_score__mutmut_30, 
    'x_archive_score__mutmut_31': x_archive_score__mutmut_31, 
    'x_archive_score__mutmut_32': x_archive_score__mutmut_32, 
    'x_archive_score__mutmut_33': x_archive_score__mutmut_33, 
    'x_archive_score__mutmut_34': x_archive_score__mutmut_34, 
    'x_archive_score__mutmut_35': x_archive_score__mutmut_35, 
    'x_archive_score__mutmut_36': x_archive_score__mutmut_36, 
    'x_archive_score__mutmut_37': x_archive_score__mutmut_37, 
    'x_archive_score__mutmut_38': x_archive_score__mutmut_38, 
    'x_archive_score__mutmut_39': x_archive_score__mutmut_39, 
    'x_archive_score__mutmut_40': x_archive_score__mutmut_40, 
    'x_archive_score__mutmut_41': x_archive_score__mutmut_41, 
    'x_archive_score__mutmut_42': x_archive_score__mutmut_42, 
    'x_archive_score__mutmut_43': x_archive_score__mutmut_43, 
    'x_archive_score__mutmut_44': x_archive_score__mutmut_44, 
    'x_archive_score__mutmut_45': x_archive_score__mutmut_45, 
    'x_archive_score__mutmut_46': x_archive_score__mutmut_46, 
    'x_archive_score__mutmut_47': x_archive_score__mutmut_47
}

def archive_score(*args, **kwargs):
    result = _mutmut_trampoline(x_archive_score__mutmut_orig, x_archive_score__mutmut_mutants, args, kwargs)
    return result 

archive_score.__signature__ = _mutmut_signature(x_archive_score__mutmut_orig)
x_archive_score__mutmut_orig.__name__ = 'x_archive_score'
