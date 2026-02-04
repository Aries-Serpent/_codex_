"""
Stub Module

This module provides functionality for stub.

Usage:
    from archive.stub import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

from .util import utcnow_iso
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


def x_make_stub_text__mutmut_orig(
    path: str,
    *,
    actor: str,
    reason: str,
    tombstone: str,
    sha256: str,
    commit: str,
) -> str:
    lines = [
        "# TOMBSTONE ARCHIVE STUB — DO NOT DELETE",
        f"# File: {path}",
        f"# ArchivedBy: {actor}",
        f"# Reason: {reason}",
        f"# Tombstone: {tombstone}",
        f"# SHA256: {sha256}",
        f"# ArchivedAt: {utcnow_iso()}",
        f"# Commit: {commit}",
        "#",
        "# To restore:",
        f"#   python -m codex.cli archive restore {tombstone} --out {path}",
        "#",
        "# NOTE: This stub intentionally contains no functional code.",
        "",
    ]
    return "\n".join(lines)


def x_make_stub_text__mutmut_1(
    path: str,
    *,
    actor: str,
    reason: str,
    tombstone: str,
    sha256: str,
    commit: str,
) -> str:
    lines = None
    return "\n".join(lines)


def x_make_stub_text__mutmut_2(
    path: str,
    *,
    actor: str,
    reason: str,
    tombstone: str,
    sha256: str,
    commit: str,
) -> str:
    lines = [
        "XX# TOMBSTONE ARCHIVE STUB — DO NOT DELETEXX",
        f"# File: {path}",
        f"# ArchivedBy: {actor}",
        f"# Reason: {reason}",
        f"# Tombstone: {tombstone}",
        f"# SHA256: {sha256}",
        f"# ArchivedAt: {utcnow_iso()}",
        f"# Commit: {commit}",
        "#",
        "# To restore:",
        f"#   python -m codex.cli archive restore {tombstone} --out {path}",
        "#",
        "# NOTE: This stub intentionally contains no functional code.",
        "",
    ]
    return "\n".join(lines)


def x_make_stub_text__mutmut_3(
    path: str,
    *,
    actor: str,
    reason: str,
    tombstone: str,
    sha256: str,
    commit: str,
) -> str:
    lines = [
        "# tombstone archive stub — do not delete",
        f"# File: {path}",
        f"# ArchivedBy: {actor}",
        f"# Reason: {reason}",
        f"# Tombstone: {tombstone}",
        f"# SHA256: {sha256}",
        f"# ArchivedAt: {utcnow_iso()}",
        f"# Commit: {commit}",
        "#",
        "# To restore:",
        f"#   python -m codex.cli archive restore {tombstone} --out {path}",
        "#",
        "# NOTE: This stub intentionally contains no functional code.",
        "",
    ]
    return "\n".join(lines)


def x_make_stub_text__mutmut_4(
    path: str,
    *,
    actor: str,
    reason: str,
    tombstone: str,
    sha256: str,
    commit: str,
) -> str:
    lines = [
        "# TOMBSTONE ARCHIVE STUB — DO NOT DELETE",
        f"# File: {path}",
        f"# ArchivedBy: {actor}",
        f"# Reason: {reason}",
        f"# Tombstone: {tombstone}",
        f"# SHA256: {sha256}",
        f"# ArchivedAt: {utcnow_iso()}",
        f"# Commit: {commit}",
        "XX#XX",
        "# To restore:",
        f"#   python -m codex.cli archive restore {tombstone} --out {path}",
        "#",
        "# NOTE: This stub intentionally contains no functional code.",
        "",
    ]
    return "\n".join(lines)


def x_make_stub_text__mutmut_5(
    path: str,
    *,
    actor: str,
    reason: str,
    tombstone: str,
    sha256: str,
    commit: str,
) -> str:
    lines = [
        "# TOMBSTONE ARCHIVE STUB — DO NOT DELETE",
        f"# File: {path}",
        f"# ArchivedBy: {actor}",
        f"# Reason: {reason}",
        f"# Tombstone: {tombstone}",
        f"# SHA256: {sha256}",
        f"# ArchivedAt: {utcnow_iso()}",
        f"# Commit: {commit}",
        "#",
        "XX# To restore:XX",
        f"#   python -m codex.cli archive restore {tombstone} --out {path}",
        "#",
        "# NOTE: This stub intentionally contains no functional code.",
        "",
    ]
    return "\n".join(lines)


def x_make_stub_text__mutmut_6(
    path: str,
    *,
    actor: str,
    reason: str,
    tombstone: str,
    sha256: str,
    commit: str,
) -> str:
    lines = [
        "# TOMBSTONE ARCHIVE STUB — DO NOT DELETE",
        f"# File: {path}",
        f"# ArchivedBy: {actor}",
        f"# Reason: {reason}",
        f"# Tombstone: {tombstone}",
        f"# SHA256: {sha256}",
        f"# ArchivedAt: {utcnow_iso()}",
        f"# Commit: {commit}",
        "#",
        "# to restore:",
        f"#   python -m codex.cli archive restore {tombstone} --out {path}",
        "#",
        "# NOTE: This stub intentionally contains no functional code.",
        "",
    ]
    return "\n".join(lines)


def x_make_stub_text__mutmut_7(
    path: str,
    *,
    actor: str,
    reason: str,
    tombstone: str,
    sha256: str,
    commit: str,
) -> str:
    lines = [
        "# TOMBSTONE ARCHIVE STUB — DO NOT DELETE",
        f"# File: {path}",
        f"# ArchivedBy: {actor}",
        f"# Reason: {reason}",
        f"# Tombstone: {tombstone}",
        f"# SHA256: {sha256}",
        f"# ArchivedAt: {utcnow_iso()}",
        f"# Commit: {commit}",
        "#",
        "# TO RESTORE:",
        f"#   python -m codex.cli archive restore {tombstone} --out {path}",
        "#",
        "# NOTE: This stub intentionally contains no functional code.",
        "",
    ]
    return "\n".join(lines)


def x_make_stub_text__mutmut_8(
    path: str,
    *,
    actor: str,
    reason: str,
    tombstone: str,
    sha256: str,
    commit: str,
) -> str:
    lines = [
        "# TOMBSTONE ARCHIVE STUB — DO NOT DELETE",
        f"# File: {path}",
        f"# ArchivedBy: {actor}",
        f"# Reason: {reason}",
        f"# Tombstone: {tombstone}",
        f"# SHA256: {sha256}",
        f"# ArchivedAt: {utcnow_iso()}",
        f"# Commit: {commit}",
        "#",
        "# To restore:",
        f"#   python -m codex.cli archive restore {tombstone} --out {path}",
        "XX#XX",
        "# NOTE: This stub intentionally contains no functional code.",
        "",
    ]
    return "\n".join(lines)


def x_make_stub_text__mutmut_9(
    path: str,
    *,
    actor: str,
    reason: str,
    tombstone: str,
    sha256: str,
    commit: str,
) -> str:
    lines = [
        "# TOMBSTONE ARCHIVE STUB — DO NOT DELETE",
        f"# File: {path}",
        f"# ArchivedBy: {actor}",
        f"# Reason: {reason}",
        f"# Tombstone: {tombstone}",
        f"# SHA256: {sha256}",
        f"# ArchivedAt: {utcnow_iso()}",
        f"# Commit: {commit}",
        "#",
        "# To restore:",
        f"#   python -m codex.cli archive restore {tombstone} --out {path}",
        "#",
        "XX# NOTE: This stub intentionally contains no functional code.XX",
        "",
    ]
    return "\n".join(lines)


def x_make_stub_text__mutmut_10(
    path: str,
    *,
    actor: str,
    reason: str,
    tombstone: str,
    sha256: str,
    commit: str,
) -> str:
    lines = [
        "# TOMBSTONE ARCHIVE STUB — DO NOT DELETE",
        f"# File: {path}",
        f"# ArchivedBy: {actor}",
        f"# Reason: {reason}",
        f"# Tombstone: {tombstone}",
        f"# SHA256: {sha256}",
        f"# ArchivedAt: {utcnow_iso()}",
        f"# Commit: {commit}",
        "#",
        "# To restore:",
        f"#   python -m codex.cli archive restore {tombstone} --out {path}",
        "#",
        "# note: this stub intentionally contains no functional code.",
        "",
    ]
    return "\n".join(lines)


def x_make_stub_text__mutmut_11(
    path: str,
    *,
    actor: str,
    reason: str,
    tombstone: str,
    sha256: str,
    commit: str,
) -> str:
    lines = [
        "# TOMBSTONE ARCHIVE STUB — DO NOT DELETE",
        f"# File: {path}",
        f"# ArchivedBy: {actor}",
        f"# Reason: {reason}",
        f"# Tombstone: {tombstone}",
        f"# SHA256: {sha256}",
        f"# ArchivedAt: {utcnow_iso()}",
        f"# Commit: {commit}",
        "#",
        "# To restore:",
        f"#   python -m codex.cli archive restore {tombstone} --out {path}",
        "#",
        "# NOTE: THIS STUB INTENTIONALLY CONTAINS NO FUNCTIONAL CODE.",
        "",
    ]
    return "\n".join(lines)


def x_make_stub_text__mutmut_12(
    path: str,
    *,
    actor: str,
    reason: str,
    tombstone: str,
    sha256: str,
    commit: str,
) -> str:
    lines = [
        "# TOMBSTONE ARCHIVE STUB — DO NOT DELETE",
        f"# File: {path}",
        f"# ArchivedBy: {actor}",
        f"# Reason: {reason}",
        f"# Tombstone: {tombstone}",
        f"# SHA256: {sha256}",
        f"# ArchivedAt: {utcnow_iso()}",
        f"# Commit: {commit}",
        "#",
        "# To restore:",
        f"#   python -m codex.cli archive restore {tombstone} --out {path}",
        "#",
        "# NOTE: This stub intentionally contains no functional code.",
        "XXXX",
    ]
    return "\n".join(lines)


def x_make_stub_text__mutmut_13(
    path: str,
    *,
    actor: str,
    reason: str,
    tombstone: str,
    sha256: str,
    commit: str,
) -> str:
    lines = [
        "# TOMBSTONE ARCHIVE STUB — DO NOT DELETE",
        f"# File: {path}",
        f"# ArchivedBy: {actor}",
        f"# Reason: {reason}",
        f"# Tombstone: {tombstone}",
        f"# SHA256: {sha256}",
        f"# ArchivedAt: {utcnow_iso()}",
        f"# Commit: {commit}",
        "#",
        "# To restore:",
        f"#   python -m codex.cli archive restore {tombstone} --out {path}",
        "#",
        "# NOTE: This stub intentionally contains no functional code.",
        "",
    ]
    return "\n".join(None)


def x_make_stub_text__mutmut_14(
    path: str,
    *,
    actor: str,
    reason: str,
    tombstone: str,
    sha256: str,
    commit: str,
) -> str:
    lines = [
        "# TOMBSTONE ARCHIVE STUB — DO NOT DELETE",
        f"# File: {path}",
        f"# ArchivedBy: {actor}",
        f"# Reason: {reason}",
        f"# Tombstone: {tombstone}",
        f"# SHA256: {sha256}",
        f"# ArchivedAt: {utcnow_iso()}",
        f"# Commit: {commit}",
        "#",
        "# To restore:",
        f"#   python -m codex.cli archive restore {tombstone} --out {path}",
        "#",
        "# NOTE: This stub intentionally contains no functional code.",
        "",
    ]
    return "XX\nXX".join(lines)

x_make_stub_text__mutmut_mutants : ClassVar[MutantDict] = {
'x_make_stub_text__mutmut_1': x_make_stub_text__mutmut_1, 
    'x_make_stub_text__mutmut_2': x_make_stub_text__mutmut_2, 
    'x_make_stub_text__mutmut_3': x_make_stub_text__mutmut_3, 
    'x_make_stub_text__mutmut_4': x_make_stub_text__mutmut_4, 
    'x_make_stub_text__mutmut_5': x_make_stub_text__mutmut_5, 
    'x_make_stub_text__mutmut_6': x_make_stub_text__mutmut_6, 
    'x_make_stub_text__mutmut_7': x_make_stub_text__mutmut_7, 
    'x_make_stub_text__mutmut_8': x_make_stub_text__mutmut_8, 
    'x_make_stub_text__mutmut_9': x_make_stub_text__mutmut_9, 
    'x_make_stub_text__mutmut_10': x_make_stub_text__mutmut_10, 
    'x_make_stub_text__mutmut_11': x_make_stub_text__mutmut_11, 
    'x_make_stub_text__mutmut_12': x_make_stub_text__mutmut_12, 
    'x_make_stub_text__mutmut_13': x_make_stub_text__mutmut_13, 
    'x_make_stub_text__mutmut_14': x_make_stub_text__mutmut_14
}

def make_stub_text(*args, **kwargs):
    result = _mutmut_trampoline(x_make_stub_text__mutmut_orig, x_make_stub_text__mutmut_mutants, args, kwargs)
    return result 

make_stub_text.__signature__ = _mutmut_signature(x_make_stub_text__mutmut_orig)
x_make_stub_text__mutmut_orig.__name__ = 'x_make_stub_text'
