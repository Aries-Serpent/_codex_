"""
Evidence Module

This module provides functionality for evidence.

Usage:
    from codex.evidence import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)
"""Shared helpers for writing append-only evidence artifacts."""


import json
import os
import platform
import subprocess
from collections.abc import Mapping
from datetime import datetime, UTC
from functools import lru_cache
from pathlib import Path
from typing import Any

__all__ = [
    "append_evidence",
    "evidence_dir",
    "evidence_metadata",
    "utc_now",
]
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


def x_evidence_dir__mutmut_orig() -> Path:
    """Return the configured evidence directory, creating it if necessary."""

    base = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence")).resolve()
    base.mkdir(parents=True, exist_ok=True)
    return base


def x_evidence_dir__mutmut_1() -> Path:
    """Return the configured evidence directory, creating it if necessary."""

    base = None
    base.mkdir(parents=True, exist_ok=True)
    return base


def x_evidence_dir__mutmut_2() -> Path:
    """Return the configured evidence directory, creating it if necessary."""

    base = Path(None).resolve()
    base.mkdir(parents=True, exist_ok=True)
    return base


def x_evidence_dir__mutmut_3() -> Path:
    """Return the configured evidence directory, creating it if necessary."""

    base = Path(os.getenv(None, ".codex/evidence")).resolve()
    base.mkdir(parents=True, exist_ok=True)
    return base


def x_evidence_dir__mutmut_4() -> Path:
    """Return the configured evidence directory, creating it if necessary."""

    base = Path(os.getenv("CODEX_EVIDENCE_DIR", None)).resolve()
    base.mkdir(parents=True, exist_ok=True)
    return base


def x_evidence_dir__mutmut_5() -> Path:
    """Return the configured evidence directory, creating it if necessary."""

    base = Path(os.getenv(".codex/evidence")).resolve()
    base.mkdir(parents=True, exist_ok=True)
    return base


def x_evidence_dir__mutmut_6() -> Path:
    """Return the configured evidence directory, creating it if necessary."""

    base = Path(os.getenv("CODEX_EVIDENCE_DIR", )).resolve()
    base.mkdir(parents=True, exist_ok=True)
    return base


def x_evidence_dir__mutmut_7() -> Path:
    """Return the configured evidence directory, creating it if necessary."""

    base = Path(os.getenv("XXCODEX_EVIDENCE_DIRXX", ".codex/evidence")).resolve()
    base.mkdir(parents=True, exist_ok=True)
    return base


def x_evidence_dir__mutmut_8() -> Path:
    """Return the configured evidence directory, creating it if necessary."""

    base = Path(os.getenv("codex_evidence_dir", ".codex/evidence")).resolve()
    base.mkdir(parents=True, exist_ok=True)
    return base


def x_evidence_dir__mutmut_9() -> Path:
    """Return the configured evidence directory, creating it if necessary."""

    base = Path(os.getenv("CODEX_EVIDENCE_DIR", "XX.codex/evidenceXX")).resolve()
    base.mkdir(parents=True, exist_ok=True)
    return base


def x_evidence_dir__mutmut_10() -> Path:
    """Return the configured evidence directory, creating it if necessary."""

    base = Path(os.getenv("CODEX_EVIDENCE_DIR", ".CODEX/EVIDENCE")).resolve()
    base.mkdir(parents=True, exist_ok=True)
    return base


def x_evidence_dir__mutmut_11() -> Path:
    """Return the configured evidence directory, creating it if necessary."""

    base = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence")).resolve()
    base.mkdir(parents=None, exist_ok=True)
    return base


def x_evidence_dir__mutmut_12() -> Path:
    """Return the configured evidence directory, creating it if necessary."""

    base = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence")).resolve()
    base.mkdir(parents=True, exist_ok=None)
    return base


def x_evidence_dir__mutmut_13() -> Path:
    """Return the configured evidence directory, creating it if necessary."""

    base = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence")).resolve()
    base.mkdir(exist_ok=True)
    return base


def x_evidence_dir__mutmut_14() -> Path:
    """Return the configured evidence directory, creating it if necessary."""

    base = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence")).resolve()
    base.mkdir(parents=True, )
    return base


def x_evidence_dir__mutmut_15() -> Path:
    """Return the configured evidence directory, creating it if necessary."""

    base = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence")).resolve()
    base.mkdir(parents=False, exist_ok=True)
    return base


def x_evidence_dir__mutmut_16() -> Path:
    """Return the configured evidence directory, creating it if necessary."""

    base = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence")).resolve()
    base.mkdir(parents=True, exist_ok=False)
    return base

x_evidence_dir__mutmut_mutants : ClassVar[MutantDict] = {
'x_evidence_dir__mutmut_1': x_evidence_dir__mutmut_1, 
    'x_evidence_dir__mutmut_2': x_evidence_dir__mutmut_2, 
    'x_evidence_dir__mutmut_3': x_evidence_dir__mutmut_3, 
    'x_evidence_dir__mutmut_4': x_evidence_dir__mutmut_4, 
    'x_evidence_dir__mutmut_5': x_evidence_dir__mutmut_5, 
    'x_evidence_dir__mutmut_6': x_evidence_dir__mutmut_6, 
    'x_evidence_dir__mutmut_7': x_evidence_dir__mutmut_7, 
    'x_evidence_dir__mutmut_8': x_evidence_dir__mutmut_8, 
    'x_evidence_dir__mutmut_9': x_evidence_dir__mutmut_9, 
    'x_evidence_dir__mutmut_10': x_evidence_dir__mutmut_10, 
    'x_evidence_dir__mutmut_11': x_evidence_dir__mutmut_11, 
    'x_evidence_dir__mutmut_12': x_evidence_dir__mutmut_12, 
    'x_evidence_dir__mutmut_13': x_evidence_dir__mutmut_13, 
    'x_evidence_dir__mutmut_14': x_evidence_dir__mutmut_14, 
    'x_evidence_dir__mutmut_15': x_evidence_dir__mutmut_15, 
    'x_evidence_dir__mutmut_16': x_evidence_dir__mutmut_16
}

def evidence_dir(*args, **kwargs):
    result = _mutmut_trampoline(x_evidence_dir__mutmut_orig, x_evidence_dir__mutmut_mutants, args, kwargs)
    return result 

evidence_dir.__signature__ = _mutmut_signature(x_evidence_dir__mutmut_orig)
x_evidence_dir__mutmut_orig.__name__ = 'x_evidence_dir'


@lru_cache(maxsize=1)
def evidence_metadata() -> dict[str, str]:
    """Capture metadata that should be attached to every evidence record."""

    return {
        "commit": _git_commit_sha(),
        "python": platform.python_version(),
        "os": platform.platform(),
    }


def x_utc_now__mutmut_orig() -> str:
    """Return an ISO 8601 timestamp in UTC without microseconds."""

    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def x_utc_now__mutmut_1() -> str:
    """Return an ISO 8601 timestamp in UTC without microseconds."""

    return datetime.now(UTC).strftime(None)


def x_utc_now__mutmut_2() -> str:
    """Return an ISO 8601 timestamp in UTC without microseconds."""

    return datetime.now(None).strftime("%Y-%m-%dT%H:%M:%SZ")


def x_utc_now__mutmut_3() -> str:
    """Return an ISO 8601 timestamp in UTC without microseconds."""

    return datetime.now(UTC).strftime("XX%Y-%m-%dT%H:%M:%SZXX")


def x_utc_now__mutmut_4() -> str:
    """Return an ISO 8601 timestamp in UTC without microseconds."""

    return datetime.now(UTC).strftime("%y-%m-%dt%h:%m:%sz")


def x_utc_now__mutmut_5() -> str:
    """Return an ISO 8601 timestamp in UTC without microseconds."""

    return datetime.now(UTC).strftime("%Y-%M-%DT%H:%M:%SZ")

x_utc_now__mutmut_mutants : ClassVar[MutantDict] = {
'x_utc_now__mutmut_1': x_utc_now__mutmut_1, 
    'x_utc_now__mutmut_2': x_utc_now__mutmut_2, 
    'x_utc_now__mutmut_3': x_utc_now__mutmut_3, 
    'x_utc_now__mutmut_4': x_utc_now__mutmut_4, 
    'x_utc_now__mutmut_5': x_utc_now__mutmut_5
}

def utc_now(*args, **kwargs):
    result = _mutmut_trampoline(x_utc_now__mutmut_orig, x_utc_now__mutmut_mutants, args, kwargs)
    return result 

utc_now.__signature__ = _mutmut_signature(x_utc_now__mutmut_orig)
x_utc_now__mutmut_orig.__name__ = 'x_utc_now'


def x_append_evidence__mutmut_orig(filename: str, payload: Mapping[str, Any]) -> None:
    """Append ``payload`` to ``filename`` in the evidence directory."""

    record = {"meta": evidence_metadata(), **dict(payload)}
    out_path = evidence_dir() / filename
    with out_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=(",", ":")) + "\n")


def x_append_evidence__mutmut_1(filename: str, payload: Mapping[str, Any]) -> None:
    """Append ``payload`` to ``filename`` in the evidence directory."""

    record = None
    out_path = evidence_dir() / filename
    with out_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=(",", ":")) + "\n")


def x_append_evidence__mutmut_2(filename: str, payload: Mapping[str, Any]) -> None:
    """Append ``payload`` to ``filename`` in the evidence directory."""

    record = {"XXmetaXX": evidence_metadata(), **dict(payload)}
    out_path = evidence_dir() / filename
    with out_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=(",", ":")) + "\n")


def x_append_evidence__mutmut_3(filename: str, payload: Mapping[str, Any]) -> None:
    """Append ``payload`` to ``filename`` in the evidence directory."""

    record = {"META": evidence_metadata(), **dict(payload)}
    out_path = evidence_dir() / filename
    with out_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=(",", ":")) + "\n")


def x_append_evidence__mutmut_4(filename: str, payload: Mapping[str, Any]) -> None:
    """Append ``payload`` to ``filename`` in the evidence directory."""

    record = {"meta": evidence_metadata(), **dict(None)}
    out_path = evidence_dir() / filename
    with out_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=(",", ":")) + "\n")


def x_append_evidence__mutmut_5(filename: str, payload: Mapping[str, Any]) -> None:
    """Append ``payload`` to ``filename`` in the evidence directory."""

    record = {"meta": evidence_metadata(), **dict(payload)}
    out_path = None
    with out_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=(",", ":")) + "\n")


def x_append_evidence__mutmut_6(filename: str, payload: Mapping[str, Any]) -> None:
    """Append ``payload`` to ``filename`` in the evidence directory."""

    record = {"meta": evidence_metadata(), **dict(payload)}
    out_path = evidence_dir() * filename
    with out_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=(",", ":")) + "\n")


def x_append_evidence__mutmut_7(filename: str, payload: Mapping[str, Any]) -> None:
    """Append ``payload`` to ``filename`` in the evidence directory."""

    record = {"meta": evidence_metadata(), **dict(payload)}
    out_path = evidence_dir() / filename
    with out_path.open(None, encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=(",", ":")) + "\n")


def x_append_evidence__mutmut_8(filename: str, payload: Mapping[str, Any]) -> None:
    """Append ``payload`` to ``filename`` in the evidence directory."""

    record = {"meta": evidence_metadata(), **dict(payload)}
    out_path = evidence_dir() / filename
    with out_path.open("a", encoding=None) as handle:
        handle.write(json.dumps(record, separators=(",", ":")) + "\n")


def x_append_evidence__mutmut_9(filename: str, payload: Mapping[str, Any]) -> None:
    """Append ``payload`` to ``filename`` in the evidence directory."""

    record = {"meta": evidence_metadata(), **dict(payload)}
    out_path = evidence_dir() / filename
    with out_path.open(encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=(",", ":")) + "\n")


def x_append_evidence__mutmut_10(filename: str, payload: Mapping[str, Any]) -> None:
    """Append ``payload`` to ``filename`` in the evidence directory."""

    record = {"meta": evidence_metadata(), **dict(payload)}
    out_path = evidence_dir() / filename
    with out_path.open("a", ) as handle:
        handle.write(json.dumps(record, separators=(",", ":")) + "\n")


def x_append_evidence__mutmut_11(filename: str, payload: Mapping[str, Any]) -> None:
    """Append ``payload`` to ``filename`` in the evidence directory."""

    record = {"meta": evidence_metadata(), **dict(payload)}
    out_path = evidence_dir() / filename
    with out_path.open("XXaXX", encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=(",", ":")) + "\n")


def x_append_evidence__mutmut_12(filename: str, payload: Mapping[str, Any]) -> None:
    """Append ``payload`` to ``filename`` in the evidence directory."""

    record = {"meta": evidence_metadata(), **dict(payload)}
    out_path = evidence_dir() / filename
    with out_path.open("A", encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=(",", ":")) + "\n")


def x_append_evidence__mutmut_13(filename: str, payload: Mapping[str, Any]) -> None:
    """Append ``payload`` to ``filename`` in the evidence directory."""

    record = {"meta": evidence_metadata(), **dict(payload)}
    out_path = evidence_dir() / filename
    with out_path.open("a", encoding="XXutf-8XX") as handle:
        handle.write(json.dumps(record, separators=(",", ":")) + "\n")


def x_append_evidence__mutmut_14(filename: str, payload: Mapping[str, Any]) -> None:
    """Append ``payload`` to ``filename`` in the evidence directory."""

    record = {"meta": evidence_metadata(), **dict(payload)}
    out_path = evidence_dir() / filename
    with out_path.open("a", encoding="UTF-8") as handle:
        handle.write(json.dumps(record, separators=(",", ":")) + "\n")


def x_append_evidence__mutmut_15(filename: str, payload: Mapping[str, Any]) -> None:
    """Append ``payload`` to ``filename`` in the evidence directory."""

    record = {"meta": evidence_metadata(), **dict(payload)}
    out_path = evidence_dir() / filename
    with out_path.open("a", encoding="utf-8") as handle:
        handle.write(None)


def x_append_evidence__mutmut_16(filename: str, payload: Mapping[str, Any]) -> None:
    """Append ``payload`` to ``filename`` in the evidence directory."""

    record = {"meta": evidence_metadata(), **dict(payload)}
    out_path = evidence_dir() / filename
    with out_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=(",", ":")) - "\n")


def x_append_evidence__mutmut_17(filename: str, payload: Mapping[str, Any]) -> None:
    """Append ``payload`` to ``filename`` in the evidence directory."""

    record = {"meta": evidence_metadata(), **dict(payload)}
    out_path = evidence_dir() / filename
    with out_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(None, separators=(",", ":")) + "\n")


def x_append_evidence__mutmut_18(filename: str, payload: Mapping[str, Any]) -> None:
    """Append ``payload`` to ``filename`` in the evidence directory."""

    record = {"meta": evidence_metadata(), **dict(payload)}
    out_path = evidence_dir() / filename
    with out_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=None) + "\n")


def x_append_evidence__mutmut_19(filename: str, payload: Mapping[str, Any]) -> None:
    """Append ``payload`` to ``filename`` in the evidence directory."""

    record = {"meta": evidence_metadata(), **dict(payload)}
    out_path = evidence_dir() / filename
    with out_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(separators=(",", ":")) + "\n")


def x_append_evidence__mutmut_20(filename: str, payload: Mapping[str, Any]) -> None:
    """Append ``payload`` to ``filename`` in the evidence directory."""

    record = {"meta": evidence_metadata(), **dict(payload)}
    out_path = evidence_dir() / filename
    with out_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ) + "\n")


def x_append_evidence__mutmut_21(filename: str, payload: Mapping[str, Any]) -> None:
    """Append ``payload`` to ``filename`` in the evidence directory."""

    record = {"meta": evidence_metadata(), **dict(payload)}
    out_path = evidence_dir() / filename
    with out_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=("XX,XX", ":")) + "\n")


def x_append_evidence__mutmut_22(filename: str, payload: Mapping[str, Any]) -> None:
    """Append ``payload`` to ``filename`` in the evidence directory."""

    record = {"meta": evidence_metadata(), **dict(payload)}
    out_path = evidence_dir() / filename
    with out_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=(",", "XX:XX")) + "\n")


def x_append_evidence__mutmut_23(filename: str, payload: Mapping[str, Any]) -> None:
    """Append ``payload`` to ``filename`` in the evidence directory."""

    record = {"meta": evidence_metadata(), **dict(payload)}
    out_path = evidence_dir() / filename
    with out_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=(",", ":")) + "XX\nXX")

x_append_evidence__mutmut_mutants : ClassVar[MutantDict] = {
'x_append_evidence__mutmut_1': x_append_evidence__mutmut_1, 
    'x_append_evidence__mutmut_2': x_append_evidence__mutmut_2, 
    'x_append_evidence__mutmut_3': x_append_evidence__mutmut_3, 
    'x_append_evidence__mutmut_4': x_append_evidence__mutmut_4, 
    'x_append_evidence__mutmut_5': x_append_evidence__mutmut_5, 
    'x_append_evidence__mutmut_6': x_append_evidence__mutmut_6, 
    'x_append_evidence__mutmut_7': x_append_evidence__mutmut_7, 
    'x_append_evidence__mutmut_8': x_append_evidence__mutmut_8, 
    'x_append_evidence__mutmut_9': x_append_evidence__mutmut_9, 
    'x_append_evidence__mutmut_10': x_append_evidence__mutmut_10, 
    'x_append_evidence__mutmut_11': x_append_evidence__mutmut_11, 
    'x_append_evidence__mutmut_12': x_append_evidence__mutmut_12, 
    'x_append_evidence__mutmut_13': x_append_evidence__mutmut_13, 
    'x_append_evidence__mutmut_14': x_append_evidence__mutmut_14, 
    'x_append_evidence__mutmut_15': x_append_evidence__mutmut_15, 
    'x_append_evidence__mutmut_16': x_append_evidence__mutmut_16, 
    'x_append_evidence__mutmut_17': x_append_evidence__mutmut_17, 
    'x_append_evidence__mutmut_18': x_append_evidence__mutmut_18, 
    'x_append_evidence__mutmut_19': x_append_evidence__mutmut_19, 
    'x_append_evidence__mutmut_20': x_append_evidence__mutmut_20, 
    'x_append_evidence__mutmut_21': x_append_evidence__mutmut_21, 
    'x_append_evidence__mutmut_22': x_append_evidence__mutmut_22, 
    'x_append_evidence__mutmut_23': x_append_evidence__mutmut_23
}

def append_evidence(*args, **kwargs):
    result = _mutmut_trampoline(x_append_evidence__mutmut_orig, x_append_evidence__mutmut_mutants, args, kwargs)
    return result 

append_evidence.__signature__ = _mutmut_signature(x_append_evidence__mutmut_orig)
x_append_evidence__mutmut_orig.__name__ = 'x_append_evidence'


def x__git_commit_sha__mutmut_orig() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return "unknown"


def x__git_commit_sha__mutmut_1() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode(None)
            .strip()
        )
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return "unknown"


def x__git_commit_sha__mutmut_2() -> str:
    try:
        return (
            subprocess.check_output(None, stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return "unknown"


def x__git_commit_sha__mutmut_3() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=None)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return "unknown"


def x__git_commit_sha__mutmut_4() -> str:
    try:
        return (
            subprocess.check_output(stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return "unknown"


def x__git_commit_sha__mutmut_5() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], )
            .decode("utf-8")
            .strip()
        )
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return "unknown"


def x__git_commit_sha__mutmut_6() -> str:
    try:
        return (
            subprocess.check_output(["XXgitXX", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return "unknown"


def x__git_commit_sha__mutmut_7() -> str:
    try:
        return (
            subprocess.check_output(["GIT", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return "unknown"


def x__git_commit_sha__mutmut_8() -> str:
    try:
        return (
            subprocess.check_output(["git", "XXrev-parseXX", "HEAD"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return "unknown"


def x__git_commit_sha__mutmut_9() -> str:
    try:
        return (
            subprocess.check_output(["git", "REV-PARSE", "HEAD"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return "unknown"


def x__git_commit_sha__mutmut_10() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "XXHEADXX"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return "unknown"


def x__git_commit_sha__mutmut_11() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "head"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return "unknown"


def x__git_commit_sha__mutmut_12() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode("XXutf-8XX")
            .strip()
        )
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return "unknown"


def x__git_commit_sha__mutmut_13() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode("UTF-8")
            .strip()
        )
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return "unknown"


def x__git_commit_sha__mutmut_14() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        logger.warning(None, exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return "unknown"


def x__git_commit_sha__mutmut_15() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        logger.warning("Exception occurred", exc_info=None)
        logger.warning("Exception occurred", exc_info=True)
        return "unknown"


def x__git_commit_sha__mutmut_16() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        logger.warning(exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return "unknown"


def x__git_commit_sha__mutmut_17() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        logger.warning("Exception occurred", )
        logger.warning("Exception occurred", exc_info=True)
        return "unknown"


def x__git_commit_sha__mutmut_18() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        logger.warning("XXException occurredXX", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return "unknown"


def x__git_commit_sha__mutmut_19() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        logger.warning("exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return "unknown"


def x__git_commit_sha__mutmut_20() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        logger.warning("EXCEPTION OCCURRED", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return "unknown"


def x__git_commit_sha__mutmut_21() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        logger.warning("Exception occurred", exc_info=False)
        logger.warning("Exception occurred", exc_info=True)
        return "unknown"


def x__git_commit_sha__mutmut_22() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning(None, exc_info=True)
        return "unknown"


def x__git_commit_sha__mutmut_23() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=None)
        return "unknown"


def x__git_commit_sha__mutmut_24() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning(exc_info=True)
        return "unknown"


def x__git_commit_sha__mutmut_25() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", )
        return "unknown"


def x__git_commit_sha__mutmut_26() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("XXException occurredXX", exc_info=True)
        return "unknown"


def x__git_commit_sha__mutmut_27() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("exception occurred", exc_info=True)
        return "unknown"


def x__git_commit_sha__mutmut_28() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("EXCEPTION OCCURRED", exc_info=True)
        return "unknown"


def x__git_commit_sha__mutmut_29() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=False)
        return "unknown"


def x__git_commit_sha__mutmut_30() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return "XXunknownXX"


def x__git_commit_sha__mutmut_31() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return "UNKNOWN"

x__git_commit_sha__mutmut_mutants : ClassVar[MutantDict] = {
'x__git_commit_sha__mutmut_1': x__git_commit_sha__mutmut_1, 
    'x__git_commit_sha__mutmut_2': x__git_commit_sha__mutmut_2, 
    'x__git_commit_sha__mutmut_3': x__git_commit_sha__mutmut_3, 
    'x__git_commit_sha__mutmut_4': x__git_commit_sha__mutmut_4, 
    'x__git_commit_sha__mutmut_5': x__git_commit_sha__mutmut_5, 
    'x__git_commit_sha__mutmut_6': x__git_commit_sha__mutmut_6, 
    'x__git_commit_sha__mutmut_7': x__git_commit_sha__mutmut_7, 
    'x__git_commit_sha__mutmut_8': x__git_commit_sha__mutmut_8, 
    'x__git_commit_sha__mutmut_9': x__git_commit_sha__mutmut_9, 
    'x__git_commit_sha__mutmut_10': x__git_commit_sha__mutmut_10, 
    'x__git_commit_sha__mutmut_11': x__git_commit_sha__mutmut_11, 
    'x__git_commit_sha__mutmut_12': x__git_commit_sha__mutmut_12, 
    'x__git_commit_sha__mutmut_13': x__git_commit_sha__mutmut_13, 
    'x__git_commit_sha__mutmut_14': x__git_commit_sha__mutmut_14, 
    'x__git_commit_sha__mutmut_15': x__git_commit_sha__mutmut_15, 
    'x__git_commit_sha__mutmut_16': x__git_commit_sha__mutmut_16, 
    'x__git_commit_sha__mutmut_17': x__git_commit_sha__mutmut_17, 
    'x__git_commit_sha__mutmut_18': x__git_commit_sha__mutmut_18, 
    'x__git_commit_sha__mutmut_19': x__git_commit_sha__mutmut_19, 
    'x__git_commit_sha__mutmut_20': x__git_commit_sha__mutmut_20, 
    'x__git_commit_sha__mutmut_21': x__git_commit_sha__mutmut_21, 
    'x__git_commit_sha__mutmut_22': x__git_commit_sha__mutmut_22, 
    'x__git_commit_sha__mutmut_23': x__git_commit_sha__mutmut_23, 
    'x__git_commit_sha__mutmut_24': x__git_commit_sha__mutmut_24, 
    'x__git_commit_sha__mutmut_25': x__git_commit_sha__mutmut_25, 
    'x__git_commit_sha__mutmut_26': x__git_commit_sha__mutmut_26, 
    'x__git_commit_sha__mutmut_27': x__git_commit_sha__mutmut_27, 
    'x__git_commit_sha__mutmut_28': x__git_commit_sha__mutmut_28, 
    'x__git_commit_sha__mutmut_29': x__git_commit_sha__mutmut_29, 
    'x__git_commit_sha__mutmut_30': x__git_commit_sha__mutmut_30, 
    'x__git_commit_sha__mutmut_31': x__git_commit_sha__mutmut_31
}

def _git_commit_sha(*args, **kwargs):
    result = _mutmut_trampoline(x__git_commit_sha__mutmut_orig, x__git_commit_sha__mutmut_mutants, args, kwargs)
    return result 

_git_commit_sha.__signature__ = _mutmut_signature(x__git_commit_sha__mutmut_orig)
x__git_commit_sha__mutmut_orig.__name__ = 'x__git_commit_sha'
