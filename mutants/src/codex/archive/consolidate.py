"""
Consolidate Module

This module provides functionality for consolidate.

Usage:
    from archive.consolidate import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)
"""Consolidation planning for near-duplicate files."""


import time
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
from typing import Iterable

from .detect import FileMeta, stat_file
from .similarity import Similarity, compute_similarity
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


def x__serialise_path__mutmut_orig(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=True)
        return path.as_posix()


def x__serialise_path__mutmut_1(path: Path, root: Path) -> str:
    try:
        return path.relative_to(None).as_posix()
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=True)
        return path.as_posix()


def x__serialise_path__mutmut_2(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError as e:
        logger.debug(None)
        logger.warning(f"ValueError: {e}", exc_info=True)
        return path.as_posix()


def x__serialise_path__mutmut_3(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(None, exc_info=True)
        return path.as_posix()


def x__serialise_path__mutmut_4(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=None)
        return path.as_posix()


def x__serialise_path__mutmut_5(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(exc_info=True)
        return path.as_posix()


def x__serialise_path__mutmut_6(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", )
        return path.as_posix()


def x__serialise_path__mutmut_7(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=False)
        return path.as_posix()

x__serialise_path__mutmut_mutants : ClassVar[MutantDict] = {
'x__serialise_path__mutmut_1': x__serialise_path__mutmut_1, 
    'x__serialise_path__mutmut_2': x__serialise_path__mutmut_2, 
    'x__serialise_path__mutmut_3': x__serialise_path__mutmut_3, 
    'x__serialise_path__mutmut_4': x__serialise_path__mutmut_4, 
    'x__serialise_path__mutmut_5': x__serialise_path__mutmut_5, 
    'x__serialise_path__mutmut_6': x__serialise_path__mutmut_6, 
    'x__serialise_path__mutmut_7': x__serialise_path__mutmut_7
}

def _serialise_path(*args, **kwargs):
    result = _mutmut_trampoline(x__serialise_path__mutmut_orig, x__serialise_path__mutmut_mutants, args, kwargs)
    return result 

_serialise_path.__signature__ = _mutmut_signature(x__serialise_path__mutmut_orig)
x__serialise_path__mutmut_orig.__name__ = 'x__serialise_path'


def x__in_excludes__mutmut_orig(path: Path, patterns: Iterable[str]) -> bool:
    serial = path.as_posix()
    return any(fnmatch(serial, pattern) for pattern in patterns)


def x__in_excludes__mutmut_1(path: Path, patterns: Iterable[str]) -> bool:
    serial = None
    return any(fnmatch(serial, pattern) for pattern in patterns)


def x__in_excludes__mutmut_2(path: Path, patterns: Iterable[str]) -> bool:
    serial = path.as_posix()
    return any(None)


def x__in_excludes__mutmut_3(path: Path, patterns: Iterable[str]) -> bool:
    serial = path.as_posix()
    return any(fnmatch(None, pattern) for pattern in patterns)


def x__in_excludes__mutmut_4(path: Path, patterns: Iterable[str]) -> bool:
    serial = path.as_posix()
    return any(fnmatch(serial, None) for pattern in patterns)


def x__in_excludes__mutmut_5(path: Path, patterns: Iterable[str]) -> bool:
    serial = path.as_posix()
    return any(fnmatch(pattern) for pattern in patterns)


def x__in_excludes__mutmut_6(path: Path, patterns: Iterable[str]) -> bool:
    serial = path.as_posix()
    return any(fnmatch(serial, ) for pattern in patterns)

x__in_excludes__mutmut_mutants : ClassVar[MutantDict] = {
'x__in_excludes__mutmut_1': x__in_excludes__mutmut_1, 
    'x__in_excludes__mutmut_2': x__in_excludes__mutmut_2, 
    'x__in_excludes__mutmut_3': x__in_excludes__mutmut_3, 
    'x__in_excludes__mutmut_4': x__in_excludes__mutmut_4, 
    'x__in_excludes__mutmut_5': x__in_excludes__mutmut_5, 
    'x__in_excludes__mutmut_6': x__in_excludes__mutmut_6
}

def _in_excludes(*args, **kwargs):
    result = _mutmut_trampoline(x__in_excludes__mutmut_orig, x__in_excludes__mutmut_mutants, args, kwargs)
    return result 

_in_excludes.__signature__ = _mutmut_signature(x__in_excludes__mutmut_orig)
x__in_excludes__mutmut_orig.__name__ = 'x__in_excludes'


def x__freshness__mutmut_orig(now: float, mtime_epoch: float) -> float:
    age_days = max(0.0, (now - mtime_epoch) / 86400.0)
    if age_days <= 7:
        return 1.0
    if age_days <= 30:
        return 0.8
    if age_days <= 180:
        return 0.5
    if age_days <= 365:
        return 0.3
    return 0.1


def x__freshness__mutmut_1(now: float, mtime_epoch: float) -> float:
    age_days = None
    if age_days <= 7:
        return 1.0
    if age_days <= 30:
        return 0.8
    if age_days <= 180:
        return 0.5
    if age_days <= 365:
        return 0.3
    return 0.1


def x__freshness__mutmut_2(now: float, mtime_epoch: float) -> float:
    age_days = max(None, (now - mtime_epoch) / 86400.0)
    if age_days <= 7:
        return 1.0
    if age_days <= 30:
        return 0.8
    if age_days <= 180:
        return 0.5
    if age_days <= 365:
        return 0.3
    return 0.1


def x__freshness__mutmut_3(now: float, mtime_epoch: float) -> float:
    age_days = max(0.0, None)
    if age_days <= 7:
        return 1.0
    if age_days <= 30:
        return 0.8
    if age_days <= 180:
        return 0.5
    if age_days <= 365:
        return 0.3
    return 0.1


def x__freshness__mutmut_4(now: float, mtime_epoch: float) -> float:
    age_days = max((now - mtime_epoch) / 86400.0)
    if age_days <= 7:
        return 1.0
    if age_days <= 30:
        return 0.8
    if age_days <= 180:
        return 0.5
    if age_days <= 365:
        return 0.3
    return 0.1


def x__freshness__mutmut_5(now: float, mtime_epoch: float) -> float:
    age_days = max(0.0, )
    if age_days <= 7:
        return 1.0
    if age_days <= 30:
        return 0.8
    if age_days <= 180:
        return 0.5
    if age_days <= 365:
        return 0.3
    return 0.1


def x__freshness__mutmut_6(now: float, mtime_epoch: float) -> float:
    age_days = max(1.0, (now - mtime_epoch) / 86400.0)
    if age_days <= 7:
        return 1.0
    if age_days <= 30:
        return 0.8
    if age_days <= 180:
        return 0.5
    if age_days <= 365:
        return 0.3
    return 0.1


def x__freshness__mutmut_7(now: float, mtime_epoch: float) -> float:
    age_days = max(0.0, (now - mtime_epoch) * 86400.0)
    if age_days <= 7:
        return 1.0
    if age_days <= 30:
        return 0.8
    if age_days <= 180:
        return 0.5
    if age_days <= 365:
        return 0.3
    return 0.1


def x__freshness__mutmut_8(now: float, mtime_epoch: float) -> float:
    age_days = max(0.0, (now + mtime_epoch) / 86400.0)
    if age_days <= 7:
        return 1.0
    if age_days <= 30:
        return 0.8
    if age_days <= 180:
        return 0.5
    if age_days <= 365:
        return 0.3
    return 0.1


def x__freshness__mutmut_9(now: float, mtime_epoch: float) -> float:
    age_days = max(0.0, (now - mtime_epoch) / 86401.0)
    if age_days <= 7:
        return 1.0
    if age_days <= 30:
        return 0.8
    if age_days <= 180:
        return 0.5
    if age_days <= 365:
        return 0.3
    return 0.1


def x__freshness__mutmut_10(now: float, mtime_epoch: float) -> float:
    age_days = max(0.0, (now - mtime_epoch) / 86400.0)
    if age_days < 7:
        return 1.0
    if age_days <= 30:
        return 0.8
    if age_days <= 180:
        return 0.5
    if age_days <= 365:
        return 0.3
    return 0.1


def x__freshness__mutmut_11(now: float, mtime_epoch: float) -> float:
    age_days = max(0.0, (now - mtime_epoch) / 86400.0)
    if age_days <= 8:
        return 1.0
    if age_days <= 30:
        return 0.8
    if age_days <= 180:
        return 0.5
    if age_days <= 365:
        return 0.3
    return 0.1


def x__freshness__mutmut_12(now: float, mtime_epoch: float) -> float:
    age_days = max(0.0, (now - mtime_epoch) / 86400.0)
    if age_days <= 7:
        return 2.0
    if age_days <= 30:
        return 0.8
    if age_days <= 180:
        return 0.5
    if age_days <= 365:
        return 0.3
    return 0.1


def x__freshness__mutmut_13(now: float, mtime_epoch: float) -> float:
    age_days = max(0.0, (now - mtime_epoch) / 86400.0)
    if age_days <= 7:
        return 1.0
    if age_days < 30:
        return 0.8
    if age_days <= 180:
        return 0.5
    if age_days <= 365:
        return 0.3
    return 0.1


def x__freshness__mutmut_14(now: float, mtime_epoch: float) -> float:
    age_days = max(0.0, (now - mtime_epoch) / 86400.0)
    if age_days <= 7:
        return 1.0
    if age_days <= 31:
        return 0.8
    if age_days <= 180:
        return 0.5
    if age_days <= 365:
        return 0.3
    return 0.1


def x__freshness__mutmut_15(now: float, mtime_epoch: float) -> float:
    age_days = max(0.0, (now - mtime_epoch) / 86400.0)
    if age_days <= 7:
        return 1.0
    if age_days <= 30:
        return 1.8
    if age_days <= 180:
        return 0.5
    if age_days <= 365:
        return 0.3
    return 0.1


def x__freshness__mutmut_16(now: float, mtime_epoch: float) -> float:
    age_days = max(0.0, (now - mtime_epoch) / 86400.0)
    if age_days <= 7:
        return 1.0
    if age_days <= 30:
        return 0.8
    if age_days < 180:
        return 0.5
    if age_days <= 365:
        return 0.3
    return 0.1


def x__freshness__mutmut_17(now: float, mtime_epoch: float) -> float:
    age_days = max(0.0, (now - mtime_epoch) / 86400.0)
    if age_days <= 7:
        return 1.0
    if age_days <= 30:
        return 0.8
    if age_days <= 181:
        return 0.5
    if age_days <= 365:
        return 0.3
    return 0.1


def x__freshness__mutmut_18(now: float, mtime_epoch: float) -> float:
    age_days = max(0.0, (now - mtime_epoch) / 86400.0)
    if age_days <= 7:
        return 1.0
    if age_days <= 30:
        return 0.8
    if age_days <= 180:
        return 1.5
    if age_days <= 365:
        return 0.3
    return 0.1


def x__freshness__mutmut_19(now: float, mtime_epoch: float) -> float:
    age_days = max(0.0, (now - mtime_epoch) / 86400.0)
    if age_days <= 7:
        return 1.0
    if age_days <= 30:
        return 0.8
    if age_days <= 180:
        return 0.5
    if age_days < 365:
        return 0.3
    return 0.1


def x__freshness__mutmut_20(now: float, mtime_epoch: float) -> float:
    age_days = max(0.0, (now - mtime_epoch) / 86400.0)
    if age_days <= 7:
        return 1.0
    if age_days <= 30:
        return 0.8
    if age_days <= 180:
        return 0.5
    if age_days <= 366:
        return 0.3
    return 0.1


def x__freshness__mutmut_21(now: float, mtime_epoch: float) -> float:
    age_days = max(0.0, (now - mtime_epoch) / 86400.0)
    if age_days <= 7:
        return 1.0
    if age_days <= 30:
        return 0.8
    if age_days <= 180:
        return 0.5
    if age_days <= 365:
        return 1.3
    return 0.1


def x__freshness__mutmut_22(now: float, mtime_epoch: float) -> float:
    age_days = max(0.0, (now - mtime_epoch) / 86400.0)
    if age_days <= 7:
        return 1.0
    if age_days <= 30:
        return 0.8
    if age_days <= 180:
        return 0.5
    if age_days <= 365:
        return 0.3
    return 1.1

x__freshness__mutmut_mutants : ClassVar[MutantDict] = {
'x__freshness__mutmut_1': x__freshness__mutmut_1, 
    'x__freshness__mutmut_2': x__freshness__mutmut_2, 
    'x__freshness__mutmut_3': x__freshness__mutmut_3, 
    'x__freshness__mutmut_4': x__freshness__mutmut_4, 
    'x__freshness__mutmut_5': x__freshness__mutmut_5, 
    'x__freshness__mutmut_6': x__freshness__mutmut_6, 
    'x__freshness__mutmut_7': x__freshness__mutmut_7, 
    'x__freshness__mutmut_8': x__freshness__mutmut_8, 
    'x__freshness__mutmut_9': x__freshness__mutmut_9, 
    'x__freshness__mutmut_10': x__freshness__mutmut_10, 
    'x__freshness__mutmut_11': x__freshness__mutmut_11, 
    'x__freshness__mutmut_12': x__freshness__mutmut_12, 
    'x__freshness__mutmut_13': x__freshness__mutmut_13, 
    'x__freshness__mutmut_14': x__freshness__mutmut_14, 
    'x__freshness__mutmut_15': x__freshness__mutmut_15, 
    'x__freshness__mutmut_16': x__freshness__mutmut_16, 
    'x__freshness__mutmut_17': x__freshness__mutmut_17, 
    'x__freshness__mutmut_18': x__freshness__mutmut_18, 
    'x__freshness__mutmut_19': x__freshness__mutmut_19, 
    'x__freshness__mutmut_20': x__freshness__mutmut_20, 
    'x__freshness__mutmut_21': x__freshness__mutmut_21, 
    'x__freshness__mutmut_22': x__freshness__mutmut_22
}

def _freshness(*args, **kwargs):
    result = _mutmut_trampoline(x__freshness__mutmut_orig, x__freshness__mutmut_mutants, args, kwargs)
    return result 

_freshness.__signature__ = _mutmut_signature(x__freshness__mutmut_orig)
x__freshness__mutmut_orig.__name__ = 'x__freshness'


def x__path_fitness__mutmut_orig(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_1(path: str) -> float:
    normalised = None
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_2(path: str) -> float:
    normalised = path.replace(None, "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_3(path: str) -> float:
    normalised = path.replace("\\", None)
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_4(path: str) -> float:
    normalised = path.replace("/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_5(path: str) -> float:
    normalised = path.replace("\\", )
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_6(path: str) -> float:
    normalised = path.replace("XX\\XX", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_7(path: str) -> float:
    normalised = path.replace("\\", "XX/XX")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_8(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = None
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_9(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 1.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_10(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith(None):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_11(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("XXsrc/codex/XX"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_12(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("SRC/CODEX/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_13(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score = 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_14(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score -= 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_15(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 1.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_16(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised and normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_17(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "XX/legacy/XX" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_18(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/LEGACY/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_19(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" not in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_20(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith(None):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_21(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("XXlegacy/XX"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_22(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("LEGACY/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_23(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score = 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_24(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score += 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_25(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 1.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_26(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith(None):
        score += 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_27(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("XX_v2.pyXX"):
        score += 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_28(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_V2.PY"):
        score += 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_29(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score = 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_30(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score -= 0.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_31(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 1.1
    return max(0.0, min(1.0, score))


def x__path_fitness__mutmut_32(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(None, min(1.0, score))


def x__path_fitness__mutmut_33(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, None)


def x__path_fitness__mutmut_34(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(min(1.0, score))


def x__path_fitness__mutmut_35(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, )


def x__path_fitness__mutmut_36(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(1.0, min(1.0, score))


def x__path_fitness__mutmut_37(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(None, score))


def x__path_fitness__mutmut_38(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(1.0, None))


def x__path_fitness__mutmut_39(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(score))


def x__path_fitness__mutmut_40(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(1.0, ))


def x__path_fitness__mutmut_41(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(2.0, score))

x__path_fitness__mutmut_mutants : ClassVar[MutantDict] = {
'x__path_fitness__mutmut_1': x__path_fitness__mutmut_1, 
    'x__path_fitness__mutmut_2': x__path_fitness__mutmut_2, 
    'x__path_fitness__mutmut_3': x__path_fitness__mutmut_3, 
    'x__path_fitness__mutmut_4': x__path_fitness__mutmut_4, 
    'x__path_fitness__mutmut_5': x__path_fitness__mutmut_5, 
    'x__path_fitness__mutmut_6': x__path_fitness__mutmut_6, 
    'x__path_fitness__mutmut_7': x__path_fitness__mutmut_7, 
    'x__path_fitness__mutmut_8': x__path_fitness__mutmut_8, 
    'x__path_fitness__mutmut_9': x__path_fitness__mutmut_9, 
    'x__path_fitness__mutmut_10': x__path_fitness__mutmut_10, 
    'x__path_fitness__mutmut_11': x__path_fitness__mutmut_11, 
    'x__path_fitness__mutmut_12': x__path_fitness__mutmut_12, 
    'x__path_fitness__mutmut_13': x__path_fitness__mutmut_13, 
    'x__path_fitness__mutmut_14': x__path_fitness__mutmut_14, 
    'x__path_fitness__mutmut_15': x__path_fitness__mutmut_15, 
    'x__path_fitness__mutmut_16': x__path_fitness__mutmut_16, 
    'x__path_fitness__mutmut_17': x__path_fitness__mutmut_17, 
    'x__path_fitness__mutmut_18': x__path_fitness__mutmut_18, 
    'x__path_fitness__mutmut_19': x__path_fitness__mutmut_19, 
    'x__path_fitness__mutmut_20': x__path_fitness__mutmut_20, 
    'x__path_fitness__mutmut_21': x__path_fitness__mutmut_21, 
    'x__path_fitness__mutmut_22': x__path_fitness__mutmut_22, 
    'x__path_fitness__mutmut_23': x__path_fitness__mutmut_23, 
    'x__path_fitness__mutmut_24': x__path_fitness__mutmut_24, 
    'x__path_fitness__mutmut_25': x__path_fitness__mutmut_25, 
    'x__path_fitness__mutmut_26': x__path_fitness__mutmut_26, 
    'x__path_fitness__mutmut_27': x__path_fitness__mutmut_27, 
    'x__path_fitness__mutmut_28': x__path_fitness__mutmut_28, 
    'x__path_fitness__mutmut_29': x__path_fitness__mutmut_29, 
    'x__path_fitness__mutmut_30': x__path_fitness__mutmut_30, 
    'x__path_fitness__mutmut_31': x__path_fitness__mutmut_31, 
    'x__path_fitness__mutmut_32': x__path_fitness__mutmut_32, 
    'x__path_fitness__mutmut_33': x__path_fitness__mutmut_33, 
    'x__path_fitness__mutmut_34': x__path_fitness__mutmut_34, 
    'x__path_fitness__mutmut_35': x__path_fitness__mutmut_35, 
    'x__path_fitness__mutmut_36': x__path_fitness__mutmut_36, 
    'x__path_fitness__mutmut_37': x__path_fitness__mutmut_37, 
    'x__path_fitness__mutmut_38': x__path_fitness__mutmut_38, 
    'x__path_fitness__mutmut_39': x__path_fitness__mutmut_39, 
    'x__path_fitness__mutmut_40': x__path_fitness__mutmut_40, 
    'x__path_fitness__mutmut_41': x__path_fitness__mutmut_41
}

def _path_fitness(*args, **kwargs):
    result = _mutmut_trampoline(x__path_fitness__mutmut_orig, x__path_fitness__mutmut_mutants, args, kwargs)
    return result 

_path_fitness.__signature__ = _mutmut_signature(x__path_fitness__mutmut_orig)
x__path_fitness__mutmut_orig.__name__ = 'x__path_fitness'


def x__complexity_penalty__mutmut_orig(size_bytes: int, sloc: int) -> float:
    return min(0.4, (sloc / 2000.0) + (size_bytes / (512 * 1024)))


def x__complexity_penalty__mutmut_1(size_bytes: int, sloc: int) -> float:
    return min(None, (sloc / 2000.0) + (size_bytes / (512 * 1024)))


def x__complexity_penalty__mutmut_2(size_bytes: int, sloc: int) -> float:
    return min(0.4, None)


def x__complexity_penalty__mutmut_3(size_bytes: int, sloc: int) -> float:
    return min((sloc / 2000.0) + (size_bytes / (512 * 1024)))


def x__complexity_penalty__mutmut_4(size_bytes: int, sloc: int) -> float:
    return min(0.4, )


def x__complexity_penalty__mutmut_5(size_bytes: int, sloc: int) -> float:
    return min(1.4, (sloc / 2000.0) + (size_bytes / (512 * 1024)))


def x__complexity_penalty__mutmut_6(size_bytes: int, sloc: int) -> float:
    return min(0.4, (sloc / 2000.0) - (size_bytes / (512 * 1024)))


def x__complexity_penalty__mutmut_7(size_bytes: int, sloc: int) -> float:
    return min(0.4, (sloc * 2000.0) + (size_bytes / (512 * 1024)))


def x__complexity_penalty__mutmut_8(size_bytes: int, sloc: int) -> float:
    return min(0.4, (sloc / 2001.0) + (size_bytes / (512 * 1024)))


def x__complexity_penalty__mutmut_9(size_bytes: int, sloc: int) -> float:
    return min(0.4, (sloc / 2000.0) + (size_bytes * (512 * 1024)))


def x__complexity_penalty__mutmut_10(size_bytes: int, sloc: int) -> float:
    return min(0.4, (sloc / 2000.0) + (size_bytes / (512 / 1024)))


def x__complexity_penalty__mutmut_11(size_bytes: int, sloc: int) -> float:
    return min(0.4, (sloc / 2000.0) + (size_bytes / (513 * 1024)))


def x__complexity_penalty__mutmut_12(size_bytes: int, sloc: int) -> float:
    return min(0.4, (sloc / 2000.0) + (size_bytes / (512 * 1025)))

x__complexity_penalty__mutmut_mutants : ClassVar[MutantDict] = {
'x__complexity_penalty__mutmut_1': x__complexity_penalty__mutmut_1, 
    'x__complexity_penalty__mutmut_2': x__complexity_penalty__mutmut_2, 
    'x__complexity_penalty__mutmut_3': x__complexity_penalty__mutmut_3, 
    'x__complexity_penalty__mutmut_4': x__complexity_penalty__mutmut_4, 
    'x__complexity_penalty__mutmut_5': x__complexity_penalty__mutmut_5, 
    'x__complexity_penalty__mutmut_6': x__complexity_penalty__mutmut_6, 
    'x__complexity_penalty__mutmut_7': x__complexity_penalty__mutmut_7, 
    'x__complexity_penalty__mutmut_8': x__complexity_penalty__mutmut_8, 
    'x__complexity_penalty__mutmut_9': x__complexity_penalty__mutmut_9, 
    'x__complexity_penalty__mutmut_10': x__complexity_penalty__mutmut_10, 
    'x__complexity_penalty__mutmut_11': x__complexity_penalty__mutmut_11, 
    'x__complexity_penalty__mutmut_12': x__complexity_penalty__mutmut_12
}

def _complexity_penalty(*args, **kwargs):
    result = _mutmut_trampoline(x__complexity_penalty__mutmut_orig, x__complexity_penalty__mutmut_mutants, args, kwargs)
    return result 

_complexity_penalty.__signature__ = _mutmut_signature(x__complexity_penalty__mutmut_orig)
x__complexity_penalty__mutmut_orig.__name__ = 'x__complexity_penalty'


def x__usage_heuristic__mutmut_orig(path: Path) -> float:
    serial = path.as_posix()
    if "legacy" in serial:
        return 0.1
    if serial.startswith("src/codex/"):
        return 0.7
    return 0.4


def x__usage_heuristic__mutmut_1(path: Path) -> float:
    serial = None
    if "legacy" in serial:
        return 0.1
    if serial.startswith("src/codex/"):
        return 0.7
    return 0.4


def x__usage_heuristic__mutmut_2(path: Path) -> float:
    serial = path.as_posix()
    if "XXlegacyXX" in serial:
        return 0.1
    if serial.startswith("src/codex/"):
        return 0.7
    return 0.4


def x__usage_heuristic__mutmut_3(path: Path) -> float:
    serial = path.as_posix()
    if "LEGACY" in serial:
        return 0.1
    if serial.startswith("src/codex/"):
        return 0.7
    return 0.4


def x__usage_heuristic__mutmut_4(path: Path) -> float:
    serial = path.as_posix()
    if "legacy" not in serial:
        return 0.1
    if serial.startswith("src/codex/"):
        return 0.7
    return 0.4


def x__usage_heuristic__mutmut_5(path: Path) -> float:
    serial = path.as_posix()
    if "legacy" in serial:
        return 1.1
    if serial.startswith("src/codex/"):
        return 0.7
    return 0.4


def x__usage_heuristic__mutmut_6(path: Path) -> float:
    serial = path.as_posix()
    if "legacy" in serial:
        return 0.1
    if serial.startswith(None):
        return 0.7
    return 0.4


def x__usage_heuristic__mutmut_7(path: Path) -> float:
    serial = path.as_posix()
    if "legacy" in serial:
        return 0.1
    if serial.startswith("XXsrc/codex/XX"):
        return 0.7
    return 0.4


def x__usage_heuristic__mutmut_8(path: Path) -> float:
    serial = path.as_posix()
    if "legacy" in serial:
        return 0.1
    if serial.startswith("SRC/CODEX/"):
        return 0.7
    return 0.4


def x__usage_heuristic__mutmut_9(path: Path) -> float:
    serial = path.as_posix()
    if "legacy" in serial:
        return 0.1
    if serial.startswith("src/codex/"):
        return 1.7
    return 0.4


def x__usage_heuristic__mutmut_10(path: Path) -> float:
    serial = path.as_posix()
    if "legacy" in serial:
        return 0.1
    if serial.startswith("src/codex/"):
        return 0.7
    return 1.4

x__usage_heuristic__mutmut_mutants : ClassVar[MutantDict] = {
'x__usage_heuristic__mutmut_1': x__usage_heuristic__mutmut_1, 
    'x__usage_heuristic__mutmut_2': x__usage_heuristic__mutmut_2, 
    'x__usage_heuristic__mutmut_3': x__usage_heuristic__mutmut_3, 
    'x__usage_heuristic__mutmut_4': x__usage_heuristic__mutmut_4, 
    'x__usage_heuristic__mutmut_5': x__usage_heuristic__mutmut_5, 
    'x__usage_heuristic__mutmut_6': x__usage_heuristic__mutmut_6, 
    'x__usage_heuristic__mutmut_7': x__usage_heuristic__mutmut_7, 
    'x__usage_heuristic__mutmut_8': x__usage_heuristic__mutmut_8, 
    'x__usage_heuristic__mutmut_9': x__usage_heuristic__mutmut_9, 
    'x__usage_heuristic__mutmut_10': x__usage_heuristic__mutmut_10
}

def _usage_heuristic(*args, **kwargs):
    result = _mutmut_trampoline(x__usage_heuristic__mutmut_orig, x__usage_heuristic__mutmut_mutants, args, kwargs)
    return result 

_usage_heuristic.__signature__ = _mutmut_signature(x__usage_heuristic__mutmut_orig)
x__usage_heuristic__mutmut_orig.__name__ = 'x__usage_heuristic'


def x__testcov_heuristic__mutmut_orig(path: Path) -> float:
    guess = Path("tests") / f"{path.stem}.py"
    return 0.6 if guess.exists() else 0.0


def x__testcov_heuristic__mutmut_1(path: Path) -> float:
    guess = None
    return 0.6 if guess.exists() else 0.0


def x__testcov_heuristic__mutmut_2(path: Path) -> float:
    guess = Path("tests") * f"{path.stem}.py"
    return 0.6 if guess.exists() else 0.0


def x__testcov_heuristic__mutmut_3(path: Path) -> float:
    guess = Path(None) / f"{path.stem}.py"
    return 0.6 if guess.exists() else 0.0


def x__testcov_heuristic__mutmut_4(path: Path) -> float:
    guess = Path("XXtestsXX") / f"{path.stem}.py"
    return 0.6 if guess.exists() else 0.0


def x__testcov_heuristic__mutmut_5(path: Path) -> float:
    guess = Path("TESTS") / f"{path.stem}.py"
    return 0.6 if guess.exists() else 0.0


def x__testcov_heuristic__mutmut_6(path: Path) -> float:
    guess = Path("tests") / f"{path.stem}.py"
    return 1.6 if guess.exists() else 0.0


def x__testcov_heuristic__mutmut_7(path: Path) -> float:
    guess = Path("tests") / f"{path.stem}.py"
    return 0.6 if guess.exists() else 1.0

x__testcov_heuristic__mutmut_mutants : ClassVar[MutantDict] = {
'x__testcov_heuristic__mutmut_1': x__testcov_heuristic__mutmut_1, 
    'x__testcov_heuristic__mutmut_2': x__testcov_heuristic__mutmut_2, 
    'x__testcov_heuristic__mutmut_3': x__testcov_heuristic__mutmut_3, 
    'x__testcov_heuristic__mutmut_4': x__testcov_heuristic__mutmut_4, 
    'x__testcov_heuristic__mutmut_5': x__testcov_heuristic__mutmut_5, 
    'x__testcov_heuristic__mutmut_6': x__testcov_heuristic__mutmut_6, 
    'x__testcov_heuristic__mutmut_7': x__testcov_heuristic__mutmut_7
}

def _testcov_heuristic(*args, **kwargs):
    result = _mutmut_trampoline(x__testcov_heuristic__mutmut_orig, x__testcov_heuristic__mutmut_mutants, args, kwargs)
    return result 

_testcov_heuristic.__signature__ = _mutmut_signature(x__testcov_heuristic__mutmut_orig)
x__testcov_heuristic__mutmut_orig.__name__ = 'x__testcov_heuristic'


def x_canon_score__mutmut_orig(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_1(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = None
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_2(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 1.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_3(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 1.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_4(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 1.2, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_5(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 1.2, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_6(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 1.1
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_7(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = None
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_8(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov)) - d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_9(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage)) - c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_10(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness)) - b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_11(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a / max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_12(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(None, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_13(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, None)
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_14(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_15(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, )
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_16(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(1.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_17(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(None, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_18(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, None))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_19(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_20(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, ))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_21(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(2.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_22(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b / max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_23(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(None, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_24(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, None)
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_25(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_26(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, )
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_27(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(1.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_28(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(None, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_29(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, None))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_30(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_31(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, ))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_32(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(2.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_33(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c / max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_34(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(None, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_35(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, None)
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_36(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_37(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, )
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_38(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(1.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_39(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(None, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_40(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, None))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_41(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_42(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, ))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_43(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(2.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_44(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d / _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_45(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(None)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_46(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = None
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_47(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps / _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_48(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(None, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_49(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, None)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_50(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_51(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, )
    return round(max(0.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_52(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(None, 4)


def x_canon_score__mutmut_53(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), None)


def x_canon_score__mutmut_54(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(4)


def x_canon_score__mutmut_55(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), )


def x_canon_score__mutmut_56(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(None, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_57(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, None), 4)


def x_canon_score__mutmut_58(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_59(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, ), 4)


def x_canon_score__mutmut_60(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(1.0, min(1.0, base - penalty)), 4)


def x_canon_score__mutmut_61(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(None, base - penalty)), 4)


def x_canon_score__mutmut_62(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, None)), 4)


def x_canon_score__mutmut_63(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(base - penalty)), 4)


def x_canon_score__mutmut_64(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, )), 4)


def x_canon_score__mutmut_65(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(2.0, base - penalty)), 4)


def x_canon_score__mutmut_66(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base + penalty)), 4)


def x_canon_score__mutmut_67(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 5)

x_canon_score__mutmut_mutants : ClassVar[MutantDict] = {
'x_canon_score__mutmut_1': x_canon_score__mutmut_1, 
    'x_canon_score__mutmut_2': x_canon_score__mutmut_2, 
    'x_canon_score__mutmut_3': x_canon_score__mutmut_3, 
    'x_canon_score__mutmut_4': x_canon_score__mutmut_4, 
    'x_canon_score__mutmut_5': x_canon_score__mutmut_5, 
    'x_canon_score__mutmut_6': x_canon_score__mutmut_6, 
    'x_canon_score__mutmut_7': x_canon_score__mutmut_7, 
    'x_canon_score__mutmut_8': x_canon_score__mutmut_8, 
    'x_canon_score__mutmut_9': x_canon_score__mutmut_9, 
    'x_canon_score__mutmut_10': x_canon_score__mutmut_10, 
    'x_canon_score__mutmut_11': x_canon_score__mutmut_11, 
    'x_canon_score__mutmut_12': x_canon_score__mutmut_12, 
    'x_canon_score__mutmut_13': x_canon_score__mutmut_13, 
    'x_canon_score__mutmut_14': x_canon_score__mutmut_14, 
    'x_canon_score__mutmut_15': x_canon_score__mutmut_15, 
    'x_canon_score__mutmut_16': x_canon_score__mutmut_16, 
    'x_canon_score__mutmut_17': x_canon_score__mutmut_17, 
    'x_canon_score__mutmut_18': x_canon_score__mutmut_18, 
    'x_canon_score__mutmut_19': x_canon_score__mutmut_19, 
    'x_canon_score__mutmut_20': x_canon_score__mutmut_20, 
    'x_canon_score__mutmut_21': x_canon_score__mutmut_21, 
    'x_canon_score__mutmut_22': x_canon_score__mutmut_22, 
    'x_canon_score__mutmut_23': x_canon_score__mutmut_23, 
    'x_canon_score__mutmut_24': x_canon_score__mutmut_24, 
    'x_canon_score__mutmut_25': x_canon_score__mutmut_25, 
    'x_canon_score__mutmut_26': x_canon_score__mutmut_26, 
    'x_canon_score__mutmut_27': x_canon_score__mutmut_27, 
    'x_canon_score__mutmut_28': x_canon_score__mutmut_28, 
    'x_canon_score__mutmut_29': x_canon_score__mutmut_29, 
    'x_canon_score__mutmut_30': x_canon_score__mutmut_30, 
    'x_canon_score__mutmut_31': x_canon_score__mutmut_31, 
    'x_canon_score__mutmut_32': x_canon_score__mutmut_32, 
    'x_canon_score__mutmut_33': x_canon_score__mutmut_33, 
    'x_canon_score__mutmut_34': x_canon_score__mutmut_34, 
    'x_canon_score__mutmut_35': x_canon_score__mutmut_35, 
    'x_canon_score__mutmut_36': x_canon_score__mutmut_36, 
    'x_canon_score__mutmut_37': x_canon_score__mutmut_37, 
    'x_canon_score__mutmut_38': x_canon_score__mutmut_38, 
    'x_canon_score__mutmut_39': x_canon_score__mutmut_39, 
    'x_canon_score__mutmut_40': x_canon_score__mutmut_40, 
    'x_canon_score__mutmut_41': x_canon_score__mutmut_41, 
    'x_canon_score__mutmut_42': x_canon_score__mutmut_42, 
    'x_canon_score__mutmut_43': x_canon_score__mutmut_43, 
    'x_canon_score__mutmut_44': x_canon_score__mutmut_44, 
    'x_canon_score__mutmut_45': x_canon_score__mutmut_45, 
    'x_canon_score__mutmut_46': x_canon_score__mutmut_46, 
    'x_canon_score__mutmut_47': x_canon_score__mutmut_47, 
    'x_canon_score__mutmut_48': x_canon_score__mutmut_48, 
    'x_canon_score__mutmut_49': x_canon_score__mutmut_49, 
    'x_canon_score__mutmut_50': x_canon_score__mutmut_50, 
    'x_canon_score__mutmut_51': x_canon_score__mutmut_51, 
    'x_canon_score__mutmut_52': x_canon_score__mutmut_52, 
    'x_canon_score__mutmut_53': x_canon_score__mutmut_53, 
    'x_canon_score__mutmut_54': x_canon_score__mutmut_54, 
    'x_canon_score__mutmut_55': x_canon_score__mutmut_55, 
    'x_canon_score__mutmut_56': x_canon_score__mutmut_56, 
    'x_canon_score__mutmut_57': x_canon_score__mutmut_57, 
    'x_canon_score__mutmut_58': x_canon_score__mutmut_58, 
    'x_canon_score__mutmut_59': x_canon_score__mutmut_59, 
    'x_canon_score__mutmut_60': x_canon_score__mutmut_60, 
    'x_canon_score__mutmut_61': x_canon_score__mutmut_61, 
    'x_canon_score__mutmut_62': x_canon_score__mutmut_62, 
    'x_canon_score__mutmut_63': x_canon_score__mutmut_63, 
    'x_canon_score__mutmut_64': x_canon_score__mutmut_64, 
    'x_canon_score__mutmut_65': x_canon_score__mutmut_65, 
    'x_canon_score__mutmut_66': x_canon_score__mutmut_66, 
    'x_canon_score__mutmut_67': x_canon_score__mutmut_67
}

def canon_score(*args, **kwargs):
    result = _mutmut_trampoline(x_canon_score__mutmut_orig, x_canon_score__mutmut_mutants, args, kwargs)
    return result 

canon_score.__signature__ = _mutmut_signature(x_canon_score__mutmut_orig)
x_canon_score__mutmut_orig.__name__ = 'x_canon_score'


@dataclass(slots=True)
class ConsolidationCandidate:
    path: str
    score: float
    freshness: float
    usage: float
    testcov: float
    size_bytes: int
    sloc: int
    mtime_epoch: float
    mime: str
    lang: str


def x__candidate_from_meta__mutmut_orig(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_1(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = None
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_2(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(None, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_3(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, None)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_4(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_5(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, )
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_6(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = None
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_7(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(None)
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_8(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(None))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_9(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = None
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_10(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(None)
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_11(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(None))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_12(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=None,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_13(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=None,
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_14(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        freshness=None,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_15(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=None,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_16(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=None,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_17(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=None,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_18(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=None,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_19(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=None,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_20(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=None,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_21(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=None,
    )


def x__candidate_from_meta__mutmut_22(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_23(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_24(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_25(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_26(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_27(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_28(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_29(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_30(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_31(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        )


def x__candidate_from_meta__mutmut_32(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(None, freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_33(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=None, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_34(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=None, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_35(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=None),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_36(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_37(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_38(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def x__candidate_from_meta__mutmut_39(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, ),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )

x__candidate_from_meta__mutmut_mutants : ClassVar[MutantDict] = {
'x__candidate_from_meta__mutmut_1': x__candidate_from_meta__mutmut_1, 
    'x__candidate_from_meta__mutmut_2': x__candidate_from_meta__mutmut_2, 
    'x__candidate_from_meta__mutmut_3': x__candidate_from_meta__mutmut_3, 
    'x__candidate_from_meta__mutmut_4': x__candidate_from_meta__mutmut_4, 
    'x__candidate_from_meta__mutmut_5': x__candidate_from_meta__mutmut_5, 
    'x__candidate_from_meta__mutmut_6': x__candidate_from_meta__mutmut_6, 
    'x__candidate_from_meta__mutmut_7': x__candidate_from_meta__mutmut_7, 
    'x__candidate_from_meta__mutmut_8': x__candidate_from_meta__mutmut_8, 
    'x__candidate_from_meta__mutmut_9': x__candidate_from_meta__mutmut_9, 
    'x__candidate_from_meta__mutmut_10': x__candidate_from_meta__mutmut_10, 
    'x__candidate_from_meta__mutmut_11': x__candidate_from_meta__mutmut_11, 
    'x__candidate_from_meta__mutmut_12': x__candidate_from_meta__mutmut_12, 
    'x__candidate_from_meta__mutmut_13': x__candidate_from_meta__mutmut_13, 
    'x__candidate_from_meta__mutmut_14': x__candidate_from_meta__mutmut_14, 
    'x__candidate_from_meta__mutmut_15': x__candidate_from_meta__mutmut_15, 
    'x__candidate_from_meta__mutmut_16': x__candidate_from_meta__mutmut_16, 
    'x__candidate_from_meta__mutmut_17': x__candidate_from_meta__mutmut_17, 
    'x__candidate_from_meta__mutmut_18': x__candidate_from_meta__mutmut_18, 
    'x__candidate_from_meta__mutmut_19': x__candidate_from_meta__mutmut_19, 
    'x__candidate_from_meta__mutmut_20': x__candidate_from_meta__mutmut_20, 
    'x__candidate_from_meta__mutmut_21': x__candidate_from_meta__mutmut_21, 
    'x__candidate_from_meta__mutmut_22': x__candidate_from_meta__mutmut_22, 
    'x__candidate_from_meta__mutmut_23': x__candidate_from_meta__mutmut_23, 
    'x__candidate_from_meta__mutmut_24': x__candidate_from_meta__mutmut_24, 
    'x__candidate_from_meta__mutmut_25': x__candidate_from_meta__mutmut_25, 
    'x__candidate_from_meta__mutmut_26': x__candidate_from_meta__mutmut_26, 
    'x__candidate_from_meta__mutmut_27': x__candidate_from_meta__mutmut_27, 
    'x__candidate_from_meta__mutmut_28': x__candidate_from_meta__mutmut_28, 
    'x__candidate_from_meta__mutmut_29': x__candidate_from_meta__mutmut_29, 
    'x__candidate_from_meta__mutmut_30': x__candidate_from_meta__mutmut_30, 
    'x__candidate_from_meta__mutmut_31': x__candidate_from_meta__mutmut_31, 
    'x__candidate_from_meta__mutmut_32': x__candidate_from_meta__mutmut_32, 
    'x__candidate_from_meta__mutmut_33': x__candidate_from_meta__mutmut_33, 
    'x__candidate_from_meta__mutmut_34': x__candidate_from_meta__mutmut_34, 
    'x__candidate_from_meta__mutmut_35': x__candidate_from_meta__mutmut_35, 
    'x__candidate_from_meta__mutmut_36': x__candidate_from_meta__mutmut_36, 
    'x__candidate_from_meta__mutmut_37': x__candidate_from_meta__mutmut_37, 
    'x__candidate_from_meta__mutmut_38': x__candidate_from_meta__mutmut_38, 
    'x__candidate_from_meta__mutmut_39': x__candidate_from_meta__mutmut_39
}

def _candidate_from_meta(*args, **kwargs):
    result = _mutmut_trampoline(x__candidate_from_meta__mutmut_orig, x__candidate_from_meta__mutmut_mutants, args, kwargs)
    return result 

_candidate_from_meta.__signature__ = _mutmut_signature(x__candidate_from_meta__mutmut_orig)
x__candidate_from_meta__mutmut_orig.__name__ = 'x__candidate_from_meta'


def x__is_near_duplicate__mutmut_orig(
    path_a: Path, path_b: Path, *, sim: Similarity, jaccard_min: float, hd_max: int
) -> bool:
    if path_a.suffix == ".py" and path_b.suffix == ".py" and sim.py_ast_equal:
        return True
    if sim.jaccard >= jaccard_min:
        return True
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        return sim.doc_hd <= hd_max
    return False


def x__is_near_duplicate__mutmut_1(
    path_a: Path, path_b: Path, *, sim: Similarity, jaccard_min: float, hd_max: int
) -> bool:
    if path_a.suffix == ".py" and path_b.suffix == ".py" or sim.py_ast_equal:
        return True
    if sim.jaccard >= jaccard_min:
        return True
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        return sim.doc_hd <= hd_max
    return False


def x__is_near_duplicate__mutmut_2(
    path_a: Path, path_b: Path, *, sim: Similarity, jaccard_min: float, hd_max: int
) -> bool:
    if path_a.suffix == ".py" or path_b.suffix == ".py" and sim.py_ast_equal:
        return True
    if sim.jaccard >= jaccard_min:
        return True
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        return sim.doc_hd <= hd_max
    return False


def x__is_near_duplicate__mutmut_3(
    path_a: Path, path_b: Path, *, sim: Similarity, jaccard_min: float, hd_max: int
) -> bool:
    if path_a.suffix != ".py" and path_b.suffix == ".py" and sim.py_ast_equal:
        return True
    if sim.jaccard >= jaccard_min:
        return True
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        return sim.doc_hd <= hd_max
    return False


def x__is_near_duplicate__mutmut_4(
    path_a: Path, path_b: Path, *, sim: Similarity, jaccard_min: float, hd_max: int
) -> bool:
    if path_a.suffix == "XX.pyXX" and path_b.suffix == ".py" and sim.py_ast_equal:
        return True
    if sim.jaccard >= jaccard_min:
        return True
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        return sim.doc_hd <= hd_max
    return False


def x__is_near_duplicate__mutmut_5(
    path_a: Path, path_b: Path, *, sim: Similarity, jaccard_min: float, hd_max: int
) -> bool:
    if path_a.suffix == ".PY" and path_b.suffix == ".py" and sim.py_ast_equal:
        return True
    if sim.jaccard >= jaccard_min:
        return True
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        return sim.doc_hd <= hd_max
    return False


def x__is_near_duplicate__mutmut_6(
    path_a: Path, path_b: Path, *, sim: Similarity, jaccard_min: float, hd_max: int
) -> bool:
    if path_a.suffix == ".py" and path_b.suffix != ".py" and sim.py_ast_equal:
        return True
    if sim.jaccard >= jaccard_min:
        return True
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        return sim.doc_hd <= hd_max
    return False


def x__is_near_duplicate__mutmut_7(
    path_a: Path, path_b: Path, *, sim: Similarity, jaccard_min: float, hd_max: int
) -> bool:
    if path_a.suffix == ".py" and path_b.suffix == "XX.pyXX" and sim.py_ast_equal:
        return True
    if sim.jaccard >= jaccard_min:
        return True
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        return sim.doc_hd <= hd_max
    return False


def x__is_near_duplicate__mutmut_8(
    path_a: Path, path_b: Path, *, sim: Similarity, jaccard_min: float, hd_max: int
) -> bool:
    if path_a.suffix == ".py" and path_b.suffix == ".PY" and sim.py_ast_equal:
        return True
    if sim.jaccard >= jaccard_min:
        return True
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        return sim.doc_hd <= hd_max
    return False


def x__is_near_duplicate__mutmut_9(
    path_a: Path, path_b: Path, *, sim: Similarity, jaccard_min: float, hd_max: int
) -> bool:
    if path_a.suffix == ".py" and path_b.suffix == ".py" and sim.py_ast_equal:
        return False
    if sim.jaccard >= jaccard_min:
        return True
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        return sim.doc_hd <= hd_max
    return False


def x__is_near_duplicate__mutmut_10(
    path_a: Path, path_b: Path, *, sim: Similarity, jaccard_min: float, hd_max: int
) -> bool:
    if path_a.suffix == ".py" and path_b.suffix == ".py" and sim.py_ast_equal:
        return True
    if sim.jaccard > jaccard_min:
        return True
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        return sim.doc_hd <= hd_max
    return False


def x__is_near_duplicate__mutmut_11(
    path_a: Path, path_b: Path, *, sim: Similarity, jaccard_min: float, hd_max: int
) -> bool:
    if path_a.suffix == ".py" and path_b.suffix == ".py" and sim.py_ast_equal:
        return True
    if sim.jaccard >= jaccard_min:
        return False
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        return sim.doc_hd <= hd_max
    return False


def x__is_near_duplicate__mutmut_12(
    path_a: Path, path_b: Path, *, sim: Similarity, jaccard_min: float, hd_max: int
) -> bool:
    if path_a.suffix == ".py" and path_b.suffix == ".py" and sim.py_ast_equal:
        return True
    if sim.jaccard >= jaccard_min:
        return True
    if path_a.suffix in {".md", ".txt"} or path_b.suffix in {".md", ".txt"}:
        return sim.doc_hd <= hd_max
    return False


def x__is_near_duplicate__mutmut_13(
    path_a: Path, path_b: Path, *, sim: Similarity, jaccard_min: float, hd_max: int
) -> bool:
    if path_a.suffix == ".py" and path_b.suffix == ".py" and sim.py_ast_equal:
        return True
    if sim.jaccard >= jaccard_min:
        return True
    if path_a.suffix not in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        return sim.doc_hd <= hd_max
    return False


def x__is_near_duplicate__mutmut_14(
    path_a: Path, path_b: Path, *, sim: Similarity, jaccard_min: float, hd_max: int
) -> bool:
    if path_a.suffix == ".py" and path_b.suffix == ".py" and sim.py_ast_equal:
        return True
    if sim.jaccard >= jaccard_min:
        return True
    if path_a.suffix in {"XX.mdXX", ".txt"} and path_b.suffix in {".md", ".txt"}:
        return sim.doc_hd <= hd_max
    return False


def x__is_near_duplicate__mutmut_15(
    path_a: Path, path_b: Path, *, sim: Similarity, jaccard_min: float, hd_max: int
) -> bool:
    if path_a.suffix == ".py" and path_b.suffix == ".py" and sim.py_ast_equal:
        return True
    if sim.jaccard >= jaccard_min:
        return True
    if path_a.suffix in {".MD", ".txt"} and path_b.suffix in {".md", ".txt"}:
        return sim.doc_hd <= hd_max
    return False


def x__is_near_duplicate__mutmut_16(
    path_a: Path, path_b: Path, *, sim: Similarity, jaccard_min: float, hd_max: int
) -> bool:
    if path_a.suffix == ".py" and path_b.suffix == ".py" and sim.py_ast_equal:
        return True
    if sim.jaccard >= jaccard_min:
        return True
    if path_a.suffix in {".md", "XX.txtXX"} and path_b.suffix in {".md", ".txt"}:
        return sim.doc_hd <= hd_max
    return False


def x__is_near_duplicate__mutmut_17(
    path_a: Path, path_b: Path, *, sim: Similarity, jaccard_min: float, hd_max: int
) -> bool:
    if path_a.suffix == ".py" and path_b.suffix == ".py" and sim.py_ast_equal:
        return True
    if sim.jaccard >= jaccard_min:
        return True
    if path_a.suffix in {".md", ".TXT"} and path_b.suffix in {".md", ".txt"}:
        return sim.doc_hd <= hd_max
    return False


def x__is_near_duplicate__mutmut_18(
    path_a: Path, path_b: Path, *, sim: Similarity, jaccard_min: float, hd_max: int
) -> bool:
    if path_a.suffix == ".py" and path_b.suffix == ".py" and sim.py_ast_equal:
        return True
    if sim.jaccard >= jaccard_min:
        return True
    if path_a.suffix in {".md", ".txt"} and path_b.suffix not in {".md", ".txt"}:
        return sim.doc_hd <= hd_max
    return False


def x__is_near_duplicate__mutmut_19(
    path_a: Path, path_b: Path, *, sim: Similarity, jaccard_min: float, hd_max: int
) -> bool:
    if path_a.suffix == ".py" and path_b.suffix == ".py" and sim.py_ast_equal:
        return True
    if sim.jaccard >= jaccard_min:
        return True
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {"XX.mdXX", ".txt"}:
        return sim.doc_hd <= hd_max
    return False


def x__is_near_duplicate__mutmut_20(
    path_a: Path, path_b: Path, *, sim: Similarity, jaccard_min: float, hd_max: int
) -> bool:
    if path_a.suffix == ".py" and path_b.suffix == ".py" and sim.py_ast_equal:
        return True
    if sim.jaccard >= jaccard_min:
        return True
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".MD", ".txt"}:
        return sim.doc_hd <= hd_max
    return False


def x__is_near_duplicate__mutmut_21(
    path_a: Path, path_b: Path, *, sim: Similarity, jaccard_min: float, hd_max: int
) -> bool:
    if path_a.suffix == ".py" and path_b.suffix == ".py" and sim.py_ast_equal:
        return True
    if sim.jaccard >= jaccard_min:
        return True
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", "XX.txtXX"}:
        return sim.doc_hd <= hd_max
    return False


def x__is_near_duplicate__mutmut_22(
    path_a: Path, path_b: Path, *, sim: Similarity, jaccard_min: float, hd_max: int
) -> bool:
    if path_a.suffix == ".py" and path_b.suffix == ".py" and sim.py_ast_equal:
        return True
    if sim.jaccard >= jaccard_min:
        return True
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".TXT"}:
        return sim.doc_hd <= hd_max
    return False


def x__is_near_duplicate__mutmut_23(
    path_a: Path, path_b: Path, *, sim: Similarity, jaccard_min: float, hd_max: int
) -> bool:
    if path_a.suffix == ".py" and path_b.suffix == ".py" and sim.py_ast_equal:
        return True
    if sim.jaccard >= jaccard_min:
        return True
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        return sim.doc_hd < hd_max
    return False


def x__is_near_duplicate__mutmut_24(
    path_a: Path, path_b: Path, *, sim: Similarity, jaccard_min: float, hd_max: int
) -> bool:
    if path_a.suffix == ".py" and path_b.suffix == ".py" and sim.py_ast_equal:
        return True
    if sim.jaccard >= jaccard_min:
        return True
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        return sim.doc_hd <= hd_max
    return True

x__is_near_duplicate__mutmut_mutants : ClassVar[MutantDict] = {
'x__is_near_duplicate__mutmut_1': x__is_near_duplicate__mutmut_1, 
    'x__is_near_duplicate__mutmut_2': x__is_near_duplicate__mutmut_2, 
    'x__is_near_duplicate__mutmut_3': x__is_near_duplicate__mutmut_3, 
    'x__is_near_duplicate__mutmut_4': x__is_near_duplicate__mutmut_4, 
    'x__is_near_duplicate__mutmut_5': x__is_near_duplicate__mutmut_5, 
    'x__is_near_duplicate__mutmut_6': x__is_near_duplicate__mutmut_6, 
    'x__is_near_duplicate__mutmut_7': x__is_near_duplicate__mutmut_7, 
    'x__is_near_duplicate__mutmut_8': x__is_near_duplicate__mutmut_8, 
    'x__is_near_duplicate__mutmut_9': x__is_near_duplicate__mutmut_9, 
    'x__is_near_duplicate__mutmut_10': x__is_near_duplicate__mutmut_10, 
    'x__is_near_duplicate__mutmut_11': x__is_near_duplicate__mutmut_11, 
    'x__is_near_duplicate__mutmut_12': x__is_near_duplicate__mutmut_12, 
    'x__is_near_duplicate__mutmut_13': x__is_near_duplicate__mutmut_13, 
    'x__is_near_duplicate__mutmut_14': x__is_near_duplicate__mutmut_14, 
    'x__is_near_duplicate__mutmut_15': x__is_near_duplicate__mutmut_15, 
    'x__is_near_duplicate__mutmut_16': x__is_near_duplicate__mutmut_16, 
    'x__is_near_duplicate__mutmut_17': x__is_near_duplicate__mutmut_17, 
    'x__is_near_duplicate__mutmut_18': x__is_near_duplicate__mutmut_18, 
    'x__is_near_duplicate__mutmut_19': x__is_near_duplicate__mutmut_19, 
    'x__is_near_duplicate__mutmut_20': x__is_near_duplicate__mutmut_20, 
    'x__is_near_duplicate__mutmut_21': x__is_near_duplicate__mutmut_21, 
    'x__is_near_duplicate__mutmut_22': x__is_near_duplicate__mutmut_22, 
    'x__is_near_duplicate__mutmut_23': x__is_near_duplicate__mutmut_23, 
    'x__is_near_duplicate__mutmut_24': x__is_near_duplicate__mutmut_24
}

def _is_near_duplicate(*args, **kwargs):
    result = _mutmut_trampoline(x__is_near_duplicate__mutmut_orig, x__is_near_duplicate__mutmut_mutants, args, kwargs)
    return result 

_is_near_duplicate.__signature__ = _mutmut_signature(x__is_near_duplicate__mutmut_orig)
x__is_near_duplicate__mutmut_orig.__name__ = 'x__is_near_duplicate'


def x_build_consolidation_plan__mutmut_orig(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_1(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 1.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_2(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 4,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_3(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = None
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_4(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = None
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_5(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        None,
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_6(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=None,
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_7(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_8(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_9(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob(None) if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_10(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("XX*XX") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_11(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() or not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_12(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_13(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(None, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_14(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, None)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_15(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_16(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, )],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_17(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: None,
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_18(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = None
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_19(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = None
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_20(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = None
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_21(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(None, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_22(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, None)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_23(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_24(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, )
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_25(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = None
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_26(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(None)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_27(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = None
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_28(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = None
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_29(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = None
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_30(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = None
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_31(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = None

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_32(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(None):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_33(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = None
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_34(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(None, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_35(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, None)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_36(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_37(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, )
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_38(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial not in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_39(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            break
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_40(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = None
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_41(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx - 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_42(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 2 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_43(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = None
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_44(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(None, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_45(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, None)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_46(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_47(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, )
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_48(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial not in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_49(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                break
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_50(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = None
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_51(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(None, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_52(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, None)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_53(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_54(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, )
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_55(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(None, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_56(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, None, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_57(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=None, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_58(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=None, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_59(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=None):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_60(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_61(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_62(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_63(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_64(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, ):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_65(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(None)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_66(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(None)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_67(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) != 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_68(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 2:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_69(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(None)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_70(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            break
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_71(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = None
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_72(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(None, now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_73(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=None) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_74(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_75(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], ) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_76(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=None)
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_77(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: None)
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_78(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (+c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_79(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = None
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_80(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[1]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_81(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = None
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_82(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = None
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_83(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[2:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_84(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = None
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_85(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = None
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_86(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(None, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_87(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, None)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_88(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_89(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, )
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_90(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                None
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_91(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "XXpathXX": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_92(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "PATH": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_93(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "XXsimilarityXX": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_94(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "SIMILARITY": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_95(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "XXjaccardXX": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_96(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "JACCARD": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_97(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "XXdoc_hdXX": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_98(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "DOC_HD": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_99(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(None),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_100(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "XXpy_ast_equalXX": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_101(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "PY_AST_EQUAL": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_102(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 2.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_103(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 1.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_104(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(None)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_105(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            None
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_106(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "XXcanonicalXX": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_107(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "CANONICAL": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_108(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "XXpathXX": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_109(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "PATH": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_110(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "XXscoreXX": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_111(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "SCORE": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_112(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "XXfreshnessXX": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_113(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "FRESHNESS": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_114(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "XXusageXX": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_115(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "USAGE": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_116(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "XXtestcovXX": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_117(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "TESTCOV": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_118(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "XXsize_bytesXX": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_119(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "SIZE_BYTES": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_120(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "XXslocXX": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_121(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "SLOC": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_122(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "XXmtime_epochXX": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_123(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "MTIME_EPOCH": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_124(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "XXmimeXX": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_125(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "MIME": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_126(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "XXlangXX": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_127(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "LANG": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_128(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "XXduplicatesXX": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_129(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "DUPLICATES": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_130(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(None)

    return {"generated_at": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_131(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"XXgenerated_atXX": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_132(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"GENERATED_AT": int(now), "clusters": clusters}


def x_build_consolidation_plan__mutmut_133(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(None), "clusters": clusters}


def x_build_consolidation_plan__mutmut_134(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "XXclustersXX": clusters}


def x_build_consolidation_plan__mutmut_135(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: dict[str, FileMeta] = {}
    path_lookup: dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: list[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: list[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "CLUSTERS": clusters}

x_build_consolidation_plan__mutmut_mutants : ClassVar[MutantDict] = {
'x_build_consolidation_plan__mutmut_1': x_build_consolidation_plan__mutmut_1, 
    'x_build_consolidation_plan__mutmut_2': x_build_consolidation_plan__mutmut_2, 
    'x_build_consolidation_plan__mutmut_3': x_build_consolidation_plan__mutmut_3, 
    'x_build_consolidation_plan__mutmut_4': x_build_consolidation_plan__mutmut_4, 
    'x_build_consolidation_plan__mutmut_5': x_build_consolidation_plan__mutmut_5, 
    'x_build_consolidation_plan__mutmut_6': x_build_consolidation_plan__mutmut_6, 
    'x_build_consolidation_plan__mutmut_7': x_build_consolidation_plan__mutmut_7, 
    'x_build_consolidation_plan__mutmut_8': x_build_consolidation_plan__mutmut_8, 
    'x_build_consolidation_plan__mutmut_9': x_build_consolidation_plan__mutmut_9, 
    'x_build_consolidation_plan__mutmut_10': x_build_consolidation_plan__mutmut_10, 
    'x_build_consolidation_plan__mutmut_11': x_build_consolidation_plan__mutmut_11, 
    'x_build_consolidation_plan__mutmut_12': x_build_consolidation_plan__mutmut_12, 
    'x_build_consolidation_plan__mutmut_13': x_build_consolidation_plan__mutmut_13, 
    'x_build_consolidation_plan__mutmut_14': x_build_consolidation_plan__mutmut_14, 
    'x_build_consolidation_plan__mutmut_15': x_build_consolidation_plan__mutmut_15, 
    'x_build_consolidation_plan__mutmut_16': x_build_consolidation_plan__mutmut_16, 
    'x_build_consolidation_plan__mutmut_17': x_build_consolidation_plan__mutmut_17, 
    'x_build_consolidation_plan__mutmut_18': x_build_consolidation_plan__mutmut_18, 
    'x_build_consolidation_plan__mutmut_19': x_build_consolidation_plan__mutmut_19, 
    'x_build_consolidation_plan__mutmut_20': x_build_consolidation_plan__mutmut_20, 
    'x_build_consolidation_plan__mutmut_21': x_build_consolidation_plan__mutmut_21, 
    'x_build_consolidation_plan__mutmut_22': x_build_consolidation_plan__mutmut_22, 
    'x_build_consolidation_plan__mutmut_23': x_build_consolidation_plan__mutmut_23, 
    'x_build_consolidation_plan__mutmut_24': x_build_consolidation_plan__mutmut_24, 
    'x_build_consolidation_plan__mutmut_25': x_build_consolidation_plan__mutmut_25, 
    'x_build_consolidation_plan__mutmut_26': x_build_consolidation_plan__mutmut_26, 
    'x_build_consolidation_plan__mutmut_27': x_build_consolidation_plan__mutmut_27, 
    'x_build_consolidation_plan__mutmut_28': x_build_consolidation_plan__mutmut_28, 
    'x_build_consolidation_plan__mutmut_29': x_build_consolidation_plan__mutmut_29, 
    'x_build_consolidation_plan__mutmut_30': x_build_consolidation_plan__mutmut_30, 
    'x_build_consolidation_plan__mutmut_31': x_build_consolidation_plan__mutmut_31, 
    'x_build_consolidation_plan__mutmut_32': x_build_consolidation_plan__mutmut_32, 
    'x_build_consolidation_plan__mutmut_33': x_build_consolidation_plan__mutmut_33, 
    'x_build_consolidation_plan__mutmut_34': x_build_consolidation_plan__mutmut_34, 
    'x_build_consolidation_plan__mutmut_35': x_build_consolidation_plan__mutmut_35, 
    'x_build_consolidation_plan__mutmut_36': x_build_consolidation_plan__mutmut_36, 
    'x_build_consolidation_plan__mutmut_37': x_build_consolidation_plan__mutmut_37, 
    'x_build_consolidation_plan__mutmut_38': x_build_consolidation_plan__mutmut_38, 
    'x_build_consolidation_plan__mutmut_39': x_build_consolidation_plan__mutmut_39, 
    'x_build_consolidation_plan__mutmut_40': x_build_consolidation_plan__mutmut_40, 
    'x_build_consolidation_plan__mutmut_41': x_build_consolidation_plan__mutmut_41, 
    'x_build_consolidation_plan__mutmut_42': x_build_consolidation_plan__mutmut_42, 
    'x_build_consolidation_plan__mutmut_43': x_build_consolidation_plan__mutmut_43, 
    'x_build_consolidation_plan__mutmut_44': x_build_consolidation_plan__mutmut_44, 
    'x_build_consolidation_plan__mutmut_45': x_build_consolidation_plan__mutmut_45, 
    'x_build_consolidation_plan__mutmut_46': x_build_consolidation_plan__mutmut_46, 
    'x_build_consolidation_plan__mutmut_47': x_build_consolidation_plan__mutmut_47, 
    'x_build_consolidation_plan__mutmut_48': x_build_consolidation_plan__mutmut_48, 
    'x_build_consolidation_plan__mutmut_49': x_build_consolidation_plan__mutmut_49, 
    'x_build_consolidation_plan__mutmut_50': x_build_consolidation_plan__mutmut_50, 
    'x_build_consolidation_plan__mutmut_51': x_build_consolidation_plan__mutmut_51, 
    'x_build_consolidation_plan__mutmut_52': x_build_consolidation_plan__mutmut_52, 
    'x_build_consolidation_plan__mutmut_53': x_build_consolidation_plan__mutmut_53, 
    'x_build_consolidation_plan__mutmut_54': x_build_consolidation_plan__mutmut_54, 
    'x_build_consolidation_plan__mutmut_55': x_build_consolidation_plan__mutmut_55, 
    'x_build_consolidation_plan__mutmut_56': x_build_consolidation_plan__mutmut_56, 
    'x_build_consolidation_plan__mutmut_57': x_build_consolidation_plan__mutmut_57, 
    'x_build_consolidation_plan__mutmut_58': x_build_consolidation_plan__mutmut_58, 
    'x_build_consolidation_plan__mutmut_59': x_build_consolidation_plan__mutmut_59, 
    'x_build_consolidation_plan__mutmut_60': x_build_consolidation_plan__mutmut_60, 
    'x_build_consolidation_plan__mutmut_61': x_build_consolidation_plan__mutmut_61, 
    'x_build_consolidation_plan__mutmut_62': x_build_consolidation_plan__mutmut_62, 
    'x_build_consolidation_plan__mutmut_63': x_build_consolidation_plan__mutmut_63, 
    'x_build_consolidation_plan__mutmut_64': x_build_consolidation_plan__mutmut_64, 
    'x_build_consolidation_plan__mutmut_65': x_build_consolidation_plan__mutmut_65, 
    'x_build_consolidation_plan__mutmut_66': x_build_consolidation_plan__mutmut_66, 
    'x_build_consolidation_plan__mutmut_67': x_build_consolidation_plan__mutmut_67, 
    'x_build_consolidation_plan__mutmut_68': x_build_consolidation_plan__mutmut_68, 
    'x_build_consolidation_plan__mutmut_69': x_build_consolidation_plan__mutmut_69, 
    'x_build_consolidation_plan__mutmut_70': x_build_consolidation_plan__mutmut_70, 
    'x_build_consolidation_plan__mutmut_71': x_build_consolidation_plan__mutmut_71, 
    'x_build_consolidation_plan__mutmut_72': x_build_consolidation_plan__mutmut_72, 
    'x_build_consolidation_plan__mutmut_73': x_build_consolidation_plan__mutmut_73, 
    'x_build_consolidation_plan__mutmut_74': x_build_consolidation_plan__mutmut_74, 
    'x_build_consolidation_plan__mutmut_75': x_build_consolidation_plan__mutmut_75, 
    'x_build_consolidation_plan__mutmut_76': x_build_consolidation_plan__mutmut_76, 
    'x_build_consolidation_plan__mutmut_77': x_build_consolidation_plan__mutmut_77, 
    'x_build_consolidation_plan__mutmut_78': x_build_consolidation_plan__mutmut_78, 
    'x_build_consolidation_plan__mutmut_79': x_build_consolidation_plan__mutmut_79, 
    'x_build_consolidation_plan__mutmut_80': x_build_consolidation_plan__mutmut_80, 
    'x_build_consolidation_plan__mutmut_81': x_build_consolidation_plan__mutmut_81, 
    'x_build_consolidation_plan__mutmut_82': x_build_consolidation_plan__mutmut_82, 
    'x_build_consolidation_plan__mutmut_83': x_build_consolidation_plan__mutmut_83, 
    'x_build_consolidation_plan__mutmut_84': x_build_consolidation_plan__mutmut_84, 
    'x_build_consolidation_plan__mutmut_85': x_build_consolidation_plan__mutmut_85, 
    'x_build_consolidation_plan__mutmut_86': x_build_consolidation_plan__mutmut_86, 
    'x_build_consolidation_plan__mutmut_87': x_build_consolidation_plan__mutmut_87, 
    'x_build_consolidation_plan__mutmut_88': x_build_consolidation_plan__mutmut_88, 
    'x_build_consolidation_plan__mutmut_89': x_build_consolidation_plan__mutmut_89, 
    'x_build_consolidation_plan__mutmut_90': x_build_consolidation_plan__mutmut_90, 
    'x_build_consolidation_plan__mutmut_91': x_build_consolidation_plan__mutmut_91, 
    'x_build_consolidation_plan__mutmut_92': x_build_consolidation_plan__mutmut_92, 
    'x_build_consolidation_plan__mutmut_93': x_build_consolidation_plan__mutmut_93, 
    'x_build_consolidation_plan__mutmut_94': x_build_consolidation_plan__mutmut_94, 
    'x_build_consolidation_plan__mutmut_95': x_build_consolidation_plan__mutmut_95, 
    'x_build_consolidation_plan__mutmut_96': x_build_consolidation_plan__mutmut_96, 
    'x_build_consolidation_plan__mutmut_97': x_build_consolidation_plan__mutmut_97, 
    'x_build_consolidation_plan__mutmut_98': x_build_consolidation_plan__mutmut_98, 
    'x_build_consolidation_plan__mutmut_99': x_build_consolidation_plan__mutmut_99, 
    'x_build_consolidation_plan__mutmut_100': x_build_consolidation_plan__mutmut_100, 
    'x_build_consolidation_plan__mutmut_101': x_build_consolidation_plan__mutmut_101, 
    'x_build_consolidation_plan__mutmut_102': x_build_consolidation_plan__mutmut_102, 
    'x_build_consolidation_plan__mutmut_103': x_build_consolidation_plan__mutmut_103, 
    'x_build_consolidation_plan__mutmut_104': x_build_consolidation_plan__mutmut_104, 
    'x_build_consolidation_plan__mutmut_105': x_build_consolidation_plan__mutmut_105, 
    'x_build_consolidation_plan__mutmut_106': x_build_consolidation_plan__mutmut_106, 
    'x_build_consolidation_plan__mutmut_107': x_build_consolidation_plan__mutmut_107, 
    'x_build_consolidation_plan__mutmut_108': x_build_consolidation_plan__mutmut_108, 
    'x_build_consolidation_plan__mutmut_109': x_build_consolidation_plan__mutmut_109, 
    'x_build_consolidation_plan__mutmut_110': x_build_consolidation_plan__mutmut_110, 
    'x_build_consolidation_plan__mutmut_111': x_build_consolidation_plan__mutmut_111, 
    'x_build_consolidation_plan__mutmut_112': x_build_consolidation_plan__mutmut_112, 
    'x_build_consolidation_plan__mutmut_113': x_build_consolidation_plan__mutmut_113, 
    'x_build_consolidation_plan__mutmut_114': x_build_consolidation_plan__mutmut_114, 
    'x_build_consolidation_plan__mutmut_115': x_build_consolidation_plan__mutmut_115, 
    'x_build_consolidation_plan__mutmut_116': x_build_consolidation_plan__mutmut_116, 
    'x_build_consolidation_plan__mutmut_117': x_build_consolidation_plan__mutmut_117, 
    'x_build_consolidation_plan__mutmut_118': x_build_consolidation_plan__mutmut_118, 
    'x_build_consolidation_plan__mutmut_119': x_build_consolidation_plan__mutmut_119, 
    'x_build_consolidation_plan__mutmut_120': x_build_consolidation_plan__mutmut_120, 
    'x_build_consolidation_plan__mutmut_121': x_build_consolidation_plan__mutmut_121, 
    'x_build_consolidation_plan__mutmut_122': x_build_consolidation_plan__mutmut_122, 
    'x_build_consolidation_plan__mutmut_123': x_build_consolidation_plan__mutmut_123, 
    'x_build_consolidation_plan__mutmut_124': x_build_consolidation_plan__mutmut_124, 
    'x_build_consolidation_plan__mutmut_125': x_build_consolidation_plan__mutmut_125, 
    'x_build_consolidation_plan__mutmut_126': x_build_consolidation_plan__mutmut_126, 
    'x_build_consolidation_plan__mutmut_127': x_build_consolidation_plan__mutmut_127, 
    'x_build_consolidation_plan__mutmut_128': x_build_consolidation_plan__mutmut_128, 
    'x_build_consolidation_plan__mutmut_129': x_build_consolidation_plan__mutmut_129, 
    'x_build_consolidation_plan__mutmut_130': x_build_consolidation_plan__mutmut_130, 
    'x_build_consolidation_plan__mutmut_131': x_build_consolidation_plan__mutmut_131, 
    'x_build_consolidation_plan__mutmut_132': x_build_consolidation_plan__mutmut_132, 
    'x_build_consolidation_plan__mutmut_133': x_build_consolidation_plan__mutmut_133, 
    'x_build_consolidation_plan__mutmut_134': x_build_consolidation_plan__mutmut_134, 
    'x_build_consolidation_plan__mutmut_135': x_build_consolidation_plan__mutmut_135
}

def build_consolidation_plan(*args, **kwargs):
    result = _mutmut_trampoline(x_build_consolidation_plan__mutmut_orig, x_build_consolidation_plan__mutmut_mutants, args, kwargs)
    return result 

build_consolidation_plan.__signature__ = _mutmut_signature(x_build_consolidation_plan__mutmut_orig)
x_build_consolidation_plan__mutmut_orig.__name__ = 'x_build_consolidation_plan'
