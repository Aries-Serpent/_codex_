"""
Detect Module

This module provides functionality for detect.

Usage:
    from archive.detect import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

from dataclasses import dataclass
from pathlib import Path

_EXT_TO_MIME = {
    ".py": "text/x-python",
    ".md": "text/markdown",
    ".txt": "text/plain",
    ".json": "application/json",
    ".csv": "text/csv",
    ".yml": "text/yaml",
    ".yaml": "text/yaml",
    ".sql": "application/sql",
    ".js": "application/javascript",
    ".ts": "application/typescript",
    ".sh": "text/x-shellscript",
}

_EXT_TO_LANG = {
    ".py": "python",
    ".md": "markdown",
    ".txt": "text",
    ".json": "json",
    ".csv": "csv",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".sql": "sql",
    ".js": "javascript",
    ".ts": "typescript",
    ".sh": "shell",
}
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
class FileMeta:
    path: str
    size_bytes: int
    mtime_epoch: float
    mime: str
    lang: str
    sloc: int


def x__sloc_of_bytes__mutmut_orig(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_1(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = None
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_2(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode(None, "ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_3(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", None)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_4(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_5(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", )
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_6(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("XXutf-8XX", "ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_7(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("UTF-8", "ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_8(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "XXignoreXX")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_9(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "IGNORE")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_10(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning(None, exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_11(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=None)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_12(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning(exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_13(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning("Exception occurred", )
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_14(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning("XXException occurredXX", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_15(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning("exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_16(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning("EXCEPTION OCCURRED", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_17(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=False)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_18(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning(None, exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_19(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=None)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_20(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning(exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_21(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", )
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_22(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("XXException occurredXX", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_23(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_24(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("EXCEPTION OCCURRED", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_25(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=False)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_26(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return 1
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_27(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = None
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_28(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 1
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_29(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = None
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_30(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_31(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            break
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_32(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") and s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_33(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith(None) or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_34(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("XX#XX") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_35(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith(None):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_36(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("XX//XX"):
            continue
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_37(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            break
        sloc += 1
    return sloc


def x__sloc_of_bytes__mutmut_38(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc = 1
    return sloc


def x__sloc_of_bytes__mutmut_39(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc -= 1
    return sloc


def x__sloc_of_bytes__mutmut_40(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 2
    return sloc

x__sloc_of_bytes__mutmut_mutants : ClassVar[MutantDict] = {
'x__sloc_of_bytes__mutmut_1': x__sloc_of_bytes__mutmut_1, 
    'x__sloc_of_bytes__mutmut_2': x__sloc_of_bytes__mutmut_2, 
    'x__sloc_of_bytes__mutmut_3': x__sloc_of_bytes__mutmut_3, 
    'x__sloc_of_bytes__mutmut_4': x__sloc_of_bytes__mutmut_4, 
    'x__sloc_of_bytes__mutmut_5': x__sloc_of_bytes__mutmut_5, 
    'x__sloc_of_bytes__mutmut_6': x__sloc_of_bytes__mutmut_6, 
    'x__sloc_of_bytes__mutmut_7': x__sloc_of_bytes__mutmut_7, 
    'x__sloc_of_bytes__mutmut_8': x__sloc_of_bytes__mutmut_8, 
    'x__sloc_of_bytes__mutmut_9': x__sloc_of_bytes__mutmut_9, 
    'x__sloc_of_bytes__mutmut_10': x__sloc_of_bytes__mutmut_10, 
    'x__sloc_of_bytes__mutmut_11': x__sloc_of_bytes__mutmut_11, 
    'x__sloc_of_bytes__mutmut_12': x__sloc_of_bytes__mutmut_12, 
    'x__sloc_of_bytes__mutmut_13': x__sloc_of_bytes__mutmut_13, 
    'x__sloc_of_bytes__mutmut_14': x__sloc_of_bytes__mutmut_14, 
    'x__sloc_of_bytes__mutmut_15': x__sloc_of_bytes__mutmut_15, 
    'x__sloc_of_bytes__mutmut_16': x__sloc_of_bytes__mutmut_16, 
    'x__sloc_of_bytes__mutmut_17': x__sloc_of_bytes__mutmut_17, 
    'x__sloc_of_bytes__mutmut_18': x__sloc_of_bytes__mutmut_18, 
    'x__sloc_of_bytes__mutmut_19': x__sloc_of_bytes__mutmut_19, 
    'x__sloc_of_bytes__mutmut_20': x__sloc_of_bytes__mutmut_20, 
    'x__sloc_of_bytes__mutmut_21': x__sloc_of_bytes__mutmut_21, 
    'x__sloc_of_bytes__mutmut_22': x__sloc_of_bytes__mutmut_22, 
    'x__sloc_of_bytes__mutmut_23': x__sloc_of_bytes__mutmut_23, 
    'x__sloc_of_bytes__mutmut_24': x__sloc_of_bytes__mutmut_24, 
    'x__sloc_of_bytes__mutmut_25': x__sloc_of_bytes__mutmut_25, 
    'x__sloc_of_bytes__mutmut_26': x__sloc_of_bytes__mutmut_26, 
    'x__sloc_of_bytes__mutmut_27': x__sloc_of_bytes__mutmut_27, 
    'x__sloc_of_bytes__mutmut_28': x__sloc_of_bytes__mutmut_28, 
    'x__sloc_of_bytes__mutmut_29': x__sloc_of_bytes__mutmut_29, 
    'x__sloc_of_bytes__mutmut_30': x__sloc_of_bytes__mutmut_30, 
    'x__sloc_of_bytes__mutmut_31': x__sloc_of_bytes__mutmut_31, 
    'x__sloc_of_bytes__mutmut_32': x__sloc_of_bytes__mutmut_32, 
    'x__sloc_of_bytes__mutmut_33': x__sloc_of_bytes__mutmut_33, 
    'x__sloc_of_bytes__mutmut_34': x__sloc_of_bytes__mutmut_34, 
    'x__sloc_of_bytes__mutmut_35': x__sloc_of_bytes__mutmut_35, 
    'x__sloc_of_bytes__mutmut_36': x__sloc_of_bytes__mutmut_36, 
    'x__sloc_of_bytes__mutmut_37': x__sloc_of_bytes__mutmut_37, 
    'x__sloc_of_bytes__mutmut_38': x__sloc_of_bytes__mutmut_38, 
    'x__sloc_of_bytes__mutmut_39': x__sloc_of_bytes__mutmut_39, 
    'x__sloc_of_bytes__mutmut_40': x__sloc_of_bytes__mutmut_40
}

def _sloc_of_bytes(*args, **kwargs):
    result = _mutmut_trampoline(x__sloc_of_bytes__mutmut_orig, x__sloc_of_bytes__mutmut_mutants, args, kwargs)
    return result 

_sloc_of_bytes.__signature__ = _mutmut_signature(x__sloc_of_bytes__mutmut_orig)
x__sloc_of_bytes__mutmut_orig.__name__ = 'x__sloc_of_bytes'


def x_detect_mime_lang__mutmut_orig(p: Path) -> tuple[str, str]:
    ext = p.suffix.lower()
    return _EXT_TO_MIME.get(ext, "application/octet-stream"), _EXT_TO_LANG.get(ext, "binary")


def x_detect_mime_lang__mutmut_1(p: Path) -> tuple[str, str]:
    ext = None
    return _EXT_TO_MIME.get(ext, "application/octet-stream"), _EXT_TO_LANG.get(ext, "binary")


def x_detect_mime_lang__mutmut_2(p: Path) -> tuple[str, str]:
    ext = p.suffix.upper()
    return _EXT_TO_MIME.get(ext, "application/octet-stream"), _EXT_TO_LANG.get(ext, "binary")


def x_detect_mime_lang__mutmut_3(p: Path) -> tuple[str, str]:
    ext = p.suffix.lower()
    return _EXT_TO_MIME.get(None, "application/octet-stream"), _EXT_TO_LANG.get(ext, "binary")


def x_detect_mime_lang__mutmut_4(p: Path) -> tuple[str, str]:
    ext = p.suffix.lower()
    return _EXT_TO_MIME.get(ext, None), _EXT_TO_LANG.get(ext, "binary")


def x_detect_mime_lang__mutmut_5(p: Path) -> tuple[str, str]:
    ext = p.suffix.lower()
    return _EXT_TO_MIME.get("application/octet-stream"), _EXT_TO_LANG.get(ext, "binary")


def x_detect_mime_lang__mutmut_6(p: Path) -> tuple[str, str]:
    ext = p.suffix.lower()
    return _EXT_TO_MIME.get(ext, ), _EXT_TO_LANG.get(ext, "binary")


def x_detect_mime_lang__mutmut_7(p: Path) -> tuple[str, str]:
    ext = p.suffix.lower()
    return _EXT_TO_MIME.get(ext, "XXapplication/octet-streamXX"), _EXT_TO_LANG.get(ext, "binary")


def x_detect_mime_lang__mutmut_8(p: Path) -> tuple[str, str]:
    ext = p.suffix.lower()
    return _EXT_TO_MIME.get(ext, "APPLICATION/OCTET-STREAM"), _EXT_TO_LANG.get(ext, "binary")


def x_detect_mime_lang__mutmut_9(p: Path) -> tuple[str, str]:
    ext = p.suffix.lower()
    return _EXT_TO_MIME.get(ext, "application/octet-stream"), _EXT_TO_LANG.get(None, "binary")


def x_detect_mime_lang__mutmut_10(p: Path) -> tuple[str, str]:
    ext = p.suffix.lower()
    return _EXT_TO_MIME.get(ext, "application/octet-stream"), _EXT_TO_LANG.get(ext, None)


def x_detect_mime_lang__mutmut_11(p: Path) -> tuple[str, str]:
    ext = p.suffix.lower()
    return _EXT_TO_MIME.get(ext, "application/octet-stream"), _EXT_TO_LANG.get("binary")


def x_detect_mime_lang__mutmut_12(p: Path) -> tuple[str, str]:
    ext = p.suffix.lower()
    return _EXT_TO_MIME.get(ext, "application/octet-stream"), _EXT_TO_LANG.get(ext, )


def x_detect_mime_lang__mutmut_13(p: Path) -> tuple[str, str]:
    ext = p.suffix.lower()
    return _EXT_TO_MIME.get(ext, "application/octet-stream"), _EXT_TO_LANG.get(ext, "XXbinaryXX")


def x_detect_mime_lang__mutmut_14(p: Path) -> tuple[str, str]:
    ext = p.suffix.lower()
    return _EXT_TO_MIME.get(ext, "application/octet-stream"), _EXT_TO_LANG.get(ext, "BINARY")

x_detect_mime_lang__mutmut_mutants : ClassVar[MutantDict] = {
'x_detect_mime_lang__mutmut_1': x_detect_mime_lang__mutmut_1, 
    'x_detect_mime_lang__mutmut_2': x_detect_mime_lang__mutmut_2, 
    'x_detect_mime_lang__mutmut_3': x_detect_mime_lang__mutmut_3, 
    'x_detect_mime_lang__mutmut_4': x_detect_mime_lang__mutmut_4, 
    'x_detect_mime_lang__mutmut_5': x_detect_mime_lang__mutmut_5, 
    'x_detect_mime_lang__mutmut_6': x_detect_mime_lang__mutmut_6, 
    'x_detect_mime_lang__mutmut_7': x_detect_mime_lang__mutmut_7, 
    'x_detect_mime_lang__mutmut_8': x_detect_mime_lang__mutmut_8, 
    'x_detect_mime_lang__mutmut_9': x_detect_mime_lang__mutmut_9, 
    'x_detect_mime_lang__mutmut_10': x_detect_mime_lang__mutmut_10, 
    'x_detect_mime_lang__mutmut_11': x_detect_mime_lang__mutmut_11, 
    'x_detect_mime_lang__mutmut_12': x_detect_mime_lang__mutmut_12, 
    'x_detect_mime_lang__mutmut_13': x_detect_mime_lang__mutmut_13, 
    'x_detect_mime_lang__mutmut_14': x_detect_mime_lang__mutmut_14
}

def detect_mime_lang(*args, **kwargs):
    result = _mutmut_trampoline(x_detect_mime_lang__mutmut_orig, x_detect_mime_lang__mutmut_mutants, args, kwargs)
    return result 

detect_mime_lang.__signature__ = _mutmut_signature(x_detect_mime_lang__mutmut_orig)
x_detect_mime_lang__mutmut_orig.__name__ = 'x_detect_mime_lang'


def x_stat_file__mutmut_orig(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_1(p: Path) -> FileMeta:
    st = None
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_2(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = None
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_3(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(None)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_4(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = None
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_5(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning(None, exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_6(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("Exception occurred", exc_info=None)
        logger.warning("Exception occurred", exc_info=True)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_7(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning(exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_8(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("Exception occurred", )
        logger.warning("Exception occurred", exc_info=True)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_9(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("XXException occurredXX", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_10(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_11(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("EXCEPTION OCCURRED", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_12(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("Exception occurred", exc_info=False)
        logger.warning("Exception occurred", exc_info=True)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_13(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning(None, exc_info=True)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_14(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=None)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_15(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning(exc_info=True)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_16(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", )
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_17(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("XXException occurredXX", exc_info=True)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_18(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("exception occurred", exc_info=True)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_19(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("EXCEPTION OCCURRED", exc_info=True)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_20(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=False)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_21(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        b = None
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_22(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        b = b"XXXX"
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_23(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        b = b""
    return FileMeta(
        path=None,
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_24(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=None,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_25(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=None,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_26(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=None,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_27(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=None,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_28(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        sloc=None,
    )


def x_stat_file__mutmut_29(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        b = b""
    return FileMeta(
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_30(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_31(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_32(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_33(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        sloc=_sloc_of_bytes(b),
    )


def x_stat_file__mutmut_34(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        )


def x_stat_file__mutmut_35(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(None),
    )

x_stat_file__mutmut_mutants : ClassVar[MutantDict] = {
'x_stat_file__mutmut_1': x_stat_file__mutmut_1, 
    'x_stat_file__mutmut_2': x_stat_file__mutmut_2, 
    'x_stat_file__mutmut_3': x_stat_file__mutmut_3, 
    'x_stat_file__mutmut_4': x_stat_file__mutmut_4, 
    'x_stat_file__mutmut_5': x_stat_file__mutmut_5, 
    'x_stat_file__mutmut_6': x_stat_file__mutmut_6, 
    'x_stat_file__mutmut_7': x_stat_file__mutmut_7, 
    'x_stat_file__mutmut_8': x_stat_file__mutmut_8, 
    'x_stat_file__mutmut_9': x_stat_file__mutmut_9, 
    'x_stat_file__mutmut_10': x_stat_file__mutmut_10, 
    'x_stat_file__mutmut_11': x_stat_file__mutmut_11, 
    'x_stat_file__mutmut_12': x_stat_file__mutmut_12, 
    'x_stat_file__mutmut_13': x_stat_file__mutmut_13, 
    'x_stat_file__mutmut_14': x_stat_file__mutmut_14, 
    'x_stat_file__mutmut_15': x_stat_file__mutmut_15, 
    'x_stat_file__mutmut_16': x_stat_file__mutmut_16, 
    'x_stat_file__mutmut_17': x_stat_file__mutmut_17, 
    'x_stat_file__mutmut_18': x_stat_file__mutmut_18, 
    'x_stat_file__mutmut_19': x_stat_file__mutmut_19, 
    'x_stat_file__mutmut_20': x_stat_file__mutmut_20, 
    'x_stat_file__mutmut_21': x_stat_file__mutmut_21, 
    'x_stat_file__mutmut_22': x_stat_file__mutmut_22, 
    'x_stat_file__mutmut_23': x_stat_file__mutmut_23, 
    'x_stat_file__mutmut_24': x_stat_file__mutmut_24, 
    'x_stat_file__mutmut_25': x_stat_file__mutmut_25, 
    'x_stat_file__mutmut_26': x_stat_file__mutmut_26, 
    'x_stat_file__mutmut_27': x_stat_file__mutmut_27, 
    'x_stat_file__mutmut_28': x_stat_file__mutmut_28, 
    'x_stat_file__mutmut_29': x_stat_file__mutmut_29, 
    'x_stat_file__mutmut_30': x_stat_file__mutmut_30, 
    'x_stat_file__mutmut_31': x_stat_file__mutmut_31, 
    'x_stat_file__mutmut_32': x_stat_file__mutmut_32, 
    'x_stat_file__mutmut_33': x_stat_file__mutmut_33, 
    'x_stat_file__mutmut_34': x_stat_file__mutmut_34, 
    'x_stat_file__mutmut_35': x_stat_file__mutmut_35
}

def stat_file(*args, **kwargs):
    result = _mutmut_trampoline(x_stat_file__mutmut_orig, x_stat_file__mutmut_mutants, args, kwargs)
    return result 

stat_file.__signature__ = _mutmut_signature(x_stat_file__mutmut_orig)
x_stat_file__mutmut_orig.__name__ = 'x_stat_file'
