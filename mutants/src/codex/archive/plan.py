"""
Plan Module

This module provides functionality for plan.

Usage:
    from archive.plan import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

import re
import time
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from fnmatch import fnmatch
from pathlib import Path
from re import Pattern
from typing import Any, Final

from .detect import FileMeta, stat_file
from .score import ScoreInput, archive_score

DEPRECATION_PAT: Final[Pattern[str]] = re.compile(
    r"\b(DEPRECATED|LEGACY|PRUNE_ME)\b", re.IGNORECASE
)
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
class PlanEntry:
    path: str
    reason: str
    age_days: int
    ref_count: int
    coverage: float
    score: float
    commit_sha: str
    mime: str
    lang: str
    tags: list[str]
    size_bytes: int
    sloc: int


def x__has_deprecation_tag__mutmut_orig(p: Path) -> bool:
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return False
    return bool(DEPRECATION_PAT.search(txt))


def x__has_deprecation_tag__mutmut_1(p: Path) -> bool:
    try:
        txt = None
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return False
    return bool(DEPRECATION_PAT.search(txt))


def x__has_deprecation_tag__mutmut_2(p: Path) -> bool:
    try:
        txt = p.read_text(encoding=None, errors="ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return False
    return bool(DEPRECATION_PAT.search(txt))


def x__has_deprecation_tag__mutmut_3(p: Path) -> bool:
    try:
        txt = p.read_text(encoding="utf-8", errors=None)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return False
    return bool(DEPRECATION_PAT.search(txt))


def x__has_deprecation_tag__mutmut_4(p: Path) -> bool:
    try:
        txt = p.read_text(errors="ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return False
    return bool(DEPRECATION_PAT.search(txt))


def x__has_deprecation_tag__mutmut_5(p: Path) -> bool:
    try:
        txt = p.read_text(encoding="utf-8", )
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return False
    return bool(DEPRECATION_PAT.search(txt))


def x__has_deprecation_tag__mutmut_6(p: Path) -> bool:
    try:
        txt = p.read_text(encoding="XXutf-8XX", errors="ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return False
    return bool(DEPRECATION_PAT.search(txt))


def x__has_deprecation_tag__mutmut_7(p: Path) -> bool:
    try:
        txt = p.read_text(encoding="UTF-8", errors="ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return False
    return bool(DEPRECATION_PAT.search(txt))


def x__has_deprecation_tag__mutmut_8(p: Path) -> bool:
    try:
        txt = p.read_text(encoding="utf-8", errors="XXignoreXX")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return False
    return bool(DEPRECATION_PAT.search(txt))


def x__has_deprecation_tag__mutmut_9(p: Path) -> bool:
    try:
        txt = p.read_text(encoding="utf-8", errors="IGNORE")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return False
    return bool(DEPRECATION_PAT.search(txt))


def x__has_deprecation_tag__mutmut_10(p: Path) -> bool:
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        logger.warning(None, exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return False
    return bool(DEPRECATION_PAT.search(txt))


def x__has_deprecation_tag__mutmut_11(p: Path) -> bool:
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=None)
        logger.warning("Exception occurred", exc_info=True)
        return False
    return bool(DEPRECATION_PAT.search(txt))


def x__has_deprecation_tag__mutmut_12(p: Path) -> bool:
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        logger.warning(exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return False
    return bool(DEPRECATION_PAT.search(txt))


def x__has_deprecation_tag__mutmut_13(p: Path) -> bool:
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        logger.warning("Exception occurred", )
        logger.warning("Exception occurred", exc_info=True)
        return False
    return bool(DEPRECATION_PAT.search(txt))


def x__has_deprecation_tag__mutmut_14(p: Path) -> bool:
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        logger.warning("XXException occurredXX", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return False
    return bool(DEPRECATION_PAT.search(txt))


def x__has_deprecation_tag__mutmut_15(p: Path) -> bool:
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        logger.warning("exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return False
    return bool(DEPRECATION_PAT.search(txt))


def x__has_deprecation_tag__mutmut_16(p: Path) -> bool:
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        logger.warning("EXCEPTION OCCURRED", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return False
    return bool(DEPRECATION_PAT.search(txt))


def x__has_deprecation_tag__mutmut_17(p: Path) -> bool:
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=False)
        logger.warning("Exception occurred", exc_info=True)
        return False
    return bool(DEPRECATION_PAT.search(txt))


def x__has_deprecation_tag__mutmut_18(p: Path) -> bool:
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning(None, exc_info=True)
        return False
    return bool(DEPRECATION_PAT.search(txt))


def x__has_deprecation_tag__mutmut_19(p: Path) -> bool:
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=None)
        return False
    return bool(DEPRECATION_PAT.search(txt))


def x__has_deprecation_tag__mutmut_20(p: Path) -> bool:
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning(exc_info=True)
        return False
    return bool(DEPRECATION_PAT.search(txt))


def x__has_deprecation_tag__mutmut_21(p: Path) -> bool:
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", )
        return False
    return bool(DEPRECATION_PAT.search(txt))


def x__has_deprecation_tag__mutmut_22(p: Path) -> bool:
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("XXException occurredXX", exc_info=True)
        return False
    return bool(DEPRECATION_PAT.search(txt))


def x__has_deprecation_tag__mutmut_23(p: Path) -> bool:
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("exception occurred", exc_info=True)
        return False
    return bool(DEPRECATION_PAT.search(txt))


def x__has_deprecation_tag__mutmut_24(p: Path) -> bool:
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("EXCEPTION OCCURRED", exc_info=True)
        return False
    return bool(DEPRECATION_PAT.search(txt))


def x__has_deprecation_tag__mutmut_25(p: Path) -> bool:
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=False)
        return False
    return bool(DEPRECATION_PAT.search(txt))


def x__has_deprecation_tag__mutmut_26(p: Path) -> bool:
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return True
    return bool(DEPRECATION_PAT.search(txt))


def x__has_deprecation_tag__mutmut_27(p: Path) -> bool:
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return False
    return bool(None)


def x__has_deprecation_tag__mutmut_28(p: Path) -> bool:
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return False
    return bool(DEPRECATION_PAT.search(None))

x__has_deprecation_tag__mutmut_mutants : ClassVar[MutantDict] = {
'x__has_deprecation_tag__mutmut_1': x__has_deprecation_tag__mutmut_1, 
    'x__has_deprecation_tag__mutmut_2': x__has_deprecation_tag__mutmut_2, 
    'x__has_deprecation_tag__mutmut_3': x__has_deprecation_tag__mutmut_3, 
    'x__has_deprecation_tag__mutmut_4': x__has_deprecation_tag__mutmut_4, 
    'x__has_deprecation_tag__mutmut_5': x__has_deprecation_tag__mutmut_5, 
    'x__has_deprecation_tag__mutmut_6': x__has_deprecation_tag__mutmut_6, 
    'x__has_deprecation_tag__mutmut_7': x__has_deprecation_tag__mutmut_7, 
    'x__has_deprecation_tag__mutmut_8': x__has_deprecation_tag__mutmut_8, 
    'x__has_deprecation_tag__mutmut_9': x__has_deprecation_tag__mutmut_9, 
    'x__has_deprecation_tag__mutmut_10': x__has_deprecation_tag__mutmut_10, 
    'x__has_deprecation_tag__mutmut_11': x__has_deprecation_tag__mutmut_11, 
    'x__has_deprecation_tag__mutmut_12': x__has_deprecation_tag__mutmut_12, 
    'x__has_deprecation_tag__mutmut_13': x__has_deprecation_tag__mutmut_13, 
    'x__has_deprecation_tag__mutmut_14': x__has_deprecation_tag__mutmut_14, 
    'x__has_deprecation_tag__mutmut_15': x__has_deprecation_tag__mutmut_15, 
    'x__has_deprecation_tag__mutmut_16': x__has_deprecation_tag__mutmut_16, 
    'x__has_deprecation_tag__mutmut_17': x__has_deprecation_tag__mutmut_17, 
    'x__has_deprecation_tag__mutmut_18': x__has_deprecation_tag__mutmut_18, 
    'x__has_deprecation_tag__mutmut_19': x__has_deprecation_tag__mutmut_19, 
    'x__has_deprecation_tag__mutmut_20': x__has_deprecation_tag__mutmut_20, 
    'x__has_deprecation_tag__mutmut_21': x__has_deprecation_tag__mutmut_21, 
    'x__has_deprecation_tag__mutmut_22': x__has_deprecation_tag__mutmut_22, 
    'x__has_deprecation_tag__mutmut_23': x__has_deprecation_tag__mutmut_23, 
    'x__has_deprecation_tag__mutmut_24': x__has_deprecation_tag__mutmut_24, 
    'x__has_deprecation_tag__mutmut_25': x__has_deprecation_tag__mutmut_25, 
    'x__has_deprecation_tag__mutmut_26': x__has_deprecation_tag__mutmut_26, 
    'x__has_deprecation_tag__mutmut_27': x__has_deprecation_tag__mutmut_27, 
    'x__has_deprecation_tag__mutmut_28': x__has_deprecation_tag__mutmut_28
}

def _has_deprecation_tag(*args, **kwargs):
    result = _mutmut_trampoline(x__has_deprecation_tag__mutmut_orig, x__has_deprecation_tag__mutmut_mutants, args, kwargs)
    return result 

_has_deprecation_tag.__signature__ = _mutmut_signature(x__has_deprecation_tag__mutmut_orig)
x__has_deprecation_tag__mutmut_orig.__name__ = 'x__has_deprecation_tag'


def x__in_excludes__mutmut_orig(p: Path, excludes: Iterable[str]) -> bool:
    s = p.as_posix()
    return any(fnmatch(s, pat) for pat in excludes)


def x__in_excludes__mutmut_1(p: Path, excludes: Iterable[str]) -> bool:
    s = None
    return any(fnmatch(s, pat) for pat in excludes)


def x__in_excludes__mutmut_2(p: Path, excludes: Iterable[str]) -> bool:
    s = p.as_posix()
    return any(None)


def x__in_excludes__mutmut_3(p: Path, excludes: Iterable[str]) -> bool:
    s = p.as_posix()
    return any(fnmatch(None, pat) for pat in excludes)


def x__in_excludes__mutmut_4(p: Path, excludes: Iterable[str]) -> bool:
    s = p.as_posix()
    return any(fnmatch(s, None) for pat in excludes)


def x__in_excludes__mutmut_5(p: Path, excludes: Iterable[str]) -> bool:
    s = p.as_posix()
    return any(fnmatch(pat) for pat in excludes)


def x__in_excludes__mutmut_6(p: Path, excludes: Iterable[str]) -> bool:
    s = p.as_posix()
    return any(fnmatch(s, ) for pat in excludes)

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


def x_build_plan__mutmut_orig(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_1(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "XXdeadXX",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_2(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "DEAD",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_3(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = None
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_4(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = None
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_5(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob(None):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_6(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("XX*XX"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_7(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            break
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_8(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(None, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_9(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, None):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_10(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_11(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, ):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_12(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            break
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_13(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = None
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_14(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(None)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_15(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = None
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_16(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int(None)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_17(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) * 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_18(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now + fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_19(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86401)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_20(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = None
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_21(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(None)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_22(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = None
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_23(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=None,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_24(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=None,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_25(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=None,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_26(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=None,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_27(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_28(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_29(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_30(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_31(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=1,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_32(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=1.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_33(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = None
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_34(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(None, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_35(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=None)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_36(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_37(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, )
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_38(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score > 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_39(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 1.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_40(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                None
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_41(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=None,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_42(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=None,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_43(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=None,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_44(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=None,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_45(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=None,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_46(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=None,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_47(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=None,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_48(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=None,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_49(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=None,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_50(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=None,
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_51(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=None,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_52(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=None,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_53(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_54(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_55(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_56(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_57(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_58(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_59(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_60(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_61(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_62(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_63(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_64(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_65(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=1,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_66(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=1.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_67(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["XXauto-planXX"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_68(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["AUTO-PLAN"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_69(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = None
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_70(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(None) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_71(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(None, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_72(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=None)]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_73(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_74(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, )]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_75(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: None)]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_76(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (+e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_77(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"XXgenerated_atXX": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_78(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"GENERATED_AT": int(now), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_79(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(None), "analyze_sha": analyze_sha, "entries": serial}


def x_build_plan__mutmut_80(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "XXanalyze_shaXX": analyze_sha, "entries": serial}


def x_build_plan__mutmut_81(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "ANALYZE_SHA": analyze_sha, "entries": serial}


def x_build_plan__mutmut_82(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "XXentriesXX": serial}


def x_build_plan__mutmut_83(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "ENTRIES": serial}

x_build_plan__mutmut_mutants : ClassVar[MutantDict] = {
'x_build_plan__mutmut_1': x_build_plan__mutmut_1, 
    'x_build_plan__mutmut_2': x_build_plan__mutmut_2, 
    'x_build_plan__mutmut_3': x_build_plan__mutmut_3, 
    'x_build_plan__mutmut_4': x_build_plan__mutmut_4, 
    'x_build_plan__mutmut_5': x_build_plan__mutmut_5, 
    'x_build_plan__mutmut_6': x_build_plan__mutmut_6, 
    'x_build_plan__mutmut_7': x_build_plan__mutmut_7, 
    'x_build_plan__mutmut_8': x_build_plan__mutmut_8, 
    'x_build_plan__mutmut_9': x_build_plan__mutmut_9, 
    'x_build_plan__mutmut_10': x_build_plan__mutmut_10, 
    'x_build_plan__mutmut_11': x_build_plan__mutmut_11, 
    'x_build_plan__mutmut_12': x_build_plan__mutmut_12, 
    'x_build_plan__mutmut_13': x_build_plan__mutmut_13, 
    'x_build_plan__mutmut_14': x_build_plan__mutmut_14, 
    'x_build_plan__mutmut_15': x_build_plan__mutmut_15, 
    'x_build_plan__mutmut_16': x_build_plan__mutmut_16, 
    'x_build_plan__mutmut_17': x_build_plan__mutmut_17, 
    'x_build_plan__mutmut_18': x_build_plan__mutmut_18, 
    'x_build_plan__mutmut_19': x_build_plan__mutmut_19, 
    'x_build_plan__mutmut_20': x_build_plan__mutmut_20, 
    'x_build_plan__mutmut_21': x_build_plan__mutmut_21, 
    'x_build_plan__mutmut_22': x_build_plan__mutmut_22, 
    'x_build_plan__mutmut_23': x_build_plan__mutmut_23, 
    'x_build_plan__mutmut_24': x_build_plan__mutmut_24, 
    'x_build_plan__mutmut_25': x_build_plan__mutmut_25, 
    'x_build_plan__mutmut_26': x_build_plan__mutmut_26, 
    'x_build_plan__mutmut_27': x_build_plan__mutmut_27, 
    'x_build_plan__mutmut_28': x_build_plan__mutmut_28, 
    'x_build_plan__mutmut_29': x_build_plan__mutmut_29, 
    'x_build_plan__mutmut_30': x_build_plan__mutmut_30, 
    'x_build_plan__mutmut_31': x_build_plan__mutmut_31, 
    'x_build_plan__mutmut_32': x_build_plan__mutmut_32, 
    'x_build_plan__mutmut_33': x_build_plan__mutmut_33, 
    'x_build_plan__mutmut_34': x_build_plan__mutmut_34, 
    'x_build_plan__mutmut_35': x_build_plan__mutmut_35, 
    'x_build_plan__mutmut_36': x_build_plan__mutmut_36, 
    'x_build_plan__mutmut_37': x_build_plan__mutmut_37, 
    'x_build_plan__mutmut_38': x_build_plan__mutmut_38, 
    'x_build_plan__mutmut_39': x_build_plan__mutmut_39, 
    'x_build_plan__mutmut_40': x_build_plan__mutmut_40, 
    'x_build_plan__mutmut_41': x_build_plan__mutmut_41, 
    'x_build_plan__mutmut_42': x_build_plan__mutmut_42, 
    'x_build_plan__mutmut_43': x_build_plan__mutmut_43, 
    'x_build_plan__mutmut_44': x_build_plan__mutmut_44, 
    'x_build_plan__mutmut_45': x_build_plan__mutmut_45, 
    'x_build_plan__mutmut_46': x_build_plan__mutmut_46, 
    'x_build_plan__mutmut_47': x_build_plan__mutmut_47, 
    'x_build_plan__mutmut_48': x_build_plan__mutmut_48, 
    'x_build_plan__mutmut_49': x_build_plan__mutmut_49, 
    'x_build_plan__mutmut_50': x_build_plan__mutmut_50, 
    'x_build_plan__mutmut_51': x_build_plan__mutmut_51, 
    'x_build_plan__mutmut_52': x_build_plan__mutmut_52, 
    'x_build_plan__mutmut_53': x_build_plan__mutmut_53, 
    'x_build_plan__mutmut_54': x_build_plan__mutmut_54, 
    'x_build_plan__mutmut_55': x_build_plan__mutmut_55, 
    'x_build_plan__mutmut_56': x_build_plan__mutmut_56, 
    'x_build_plan__mutmut_57': x_build_plan__mutmut_57, 
    'x_build_plan__mutmut_58': x_build_plan__mutmut_58, 
    'x_build_plan__mutmut_59': x_build_plan__mutmut_59, 
    'x_build_plan__mutmut_60': x_build_plan__mutmut_60, 
    'x_build_plan__mutmut_61': x_build_plan__mutmut_61, 
    'x_build_plan__mutmut_62': x_build_plan__mutmut_62, 
    'x_build_plan__mutmut_63': x_build_plan__mutmut_63, 
    'x_build_plan__mutmut_64': x_build_plan__mutmut_64, 
    'x_build_plan__mutmut_65': x_build_plan__mutmut_65, 
    'x_build_plan__mutmut_66': x_build_plan__mutmut_66, 
    'x_build_plan__mutmut_67': x_build_plan__mutmut_67, 
    'x_build_plan__mutmut_68': x_build_plan__mutmut_68, 
    'x_build_plan__mutmut_69': x_build_plan__mutmut_69, 
    'x_build_plan__mutmut_70': x_build_plan__mutmut_70, 
    'x_build_plan__mutmut_71': x_build_plan__mutmut_71, 
    'x_build_plan__mutmut_72': x_build_plan__mutmut_72, 
    'x_build_plan__mutmut_73': x_build_plan__mutmut_73, 
    'x_build_plan__mutmut_74': x_build_plan__mutmut_74, 
    'x_build_plan__mutmut_75': x_build_plan__mutmut_75, 
    'x_build_plan__mutmut_76': x_build_plan__mutmut_76, 
    'x_build_plan__mutmut_77': x_build_plan__mutmut_77, 
    'x_build_plan__mutmut_78': x_build_plan__mutmut_78, 
    'x_build_plan__mutmut_79': x_build_plan__mutmut_79, 
    'x_build_plan__mutmut_80': x_build_plan__mutmut_80, 
    'x_build_plan__mutmut_81': x_build_plan__mutmut_81, 
    'x_build_plan__mutmut_82': x_build_plan__mutmut_82, 
    'x_build_plan__mutmut_83': x_build_plan__mutmut_83
}

def build_plan(*args, **kwargs):
    result = _mutmut_trampoline(x_build_plan__mutmut_orig, x_build_plan__mutmut_mutants, args, kwargs)
    return result 

build_plan.__signature__ = _mutmut_signature(x_build_plan__mutmut_orig)
x_build_plan__mutmut_orig.__name__ = 'x_build_plan'
