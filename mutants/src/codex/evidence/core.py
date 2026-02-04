"""
Core Module

This module provides functionality for core.

Usage:
    from evidence.core import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import os
import platform
from pathlib import Path
from typing import Any

from codex.archive.util import json_dumps_sorted, utcnow_iso

REQUIRED_FIELDS = ("action", "actor", "tool", "repo", "context")
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


def x_evidence_append__mutmut_orig(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_1(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = None
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_2(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "XXtsXX": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_3(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "TS": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_4(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "XXactionXX": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_5(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "ACTION": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_6(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "XXactorXX": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_7(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "ACTOR": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_8(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor and os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_9(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv(None, "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_10(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", None),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_11(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_12(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", ),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_13(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("XXCODEX_ACTORXX", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_14(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("codex_actor", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_15(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "XXunknownXX"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_16(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "UNKNOWN"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_17(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "XXtoolXX": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_18(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "TOOL": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_19(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "XXrepoXX": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_20(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "REPO": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_21(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "XXcontextXX": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_22(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "CONTEXT": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_23(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context and {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_24(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "XXosXX": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_25(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "OS": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_26(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "XXpythonXX": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_27(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "PYTHON": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_28(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_29(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(None):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_30(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(None)
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_31(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = None
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_32(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(None)
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_33(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv(None, ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_34(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", None))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_35(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv(".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_36(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_37(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("XXCODEX_EVIDENCE_DIRXX", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_38(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("codex_evidence_dir", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_39(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", "XX.codex/evidenceXX"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_40(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".CODEX/EVIDENCE"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_41(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=None, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_42(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=None)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_43(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_44(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, )
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_45(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=False, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_46(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=False)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_47(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open(None, encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_48(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding=None) as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_49(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open(encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_50(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", ) as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_51(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir * "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_52(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "XXarchive_ops.jsonlXX").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_53(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "ARCHIVE_OPS.JSONL").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_54(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("XXaXX", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_55(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("A", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_56(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="XXutf-8XX") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_57(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="UTF-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")


def x_evidence_append__mutmut_58(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(None)


def x_evidence_append__mutmut_59(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) - "\n")


def x_evidence_append__mutmut_60(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(None) + "\n")


def x_evidence_append__mutmut_61(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "XX\nXX")

x_evidence_append__mutmut_mutants : ClassVar[MutantDict] = {
'x_evidence_append__mutmut_1': x_evidence_append__mutmut_1, 
    'x_evidence_append__mutmut_2': x_evidence_append__mutmut_2, 
    'x_evidence_append__mutmut_3': x_evidence_append__mutmut_3, 
    'x_evidence_append__mutmut_4': x_evidence_append__mutmut_4, 
    'x_evidence_append__mutmut_5': x_evidence_append__mutmut_5, 
    'x_evidence_append__mutmut_6': x_evidence_append__mutmut_6, 
    'x_evidence_append__mutmut_7': x_evidence_append__mutmut_7, 
    'x_evidence_append__mutmut_8': x_evidence_append__mutmut_8, 
    'x_evidence_append__mutmut_9': x_evidence_append__mutmut_9, 
    'x_evidence_append__mutmut_10': x_evidence_append__mutmut_10, 
    'x_evidence_append__mutmut_11': x_evidence_append__mutmut_11, 
    'x_evidence_append__mutmut_12': x_evidence_append__mutmut_12, 
    'x_evidence_append__mutmut_13': x_evidence_append__mutmut_13, 
    'x_evidence_append__mutmut_14': x_evidence_append__mutmut_14, 
    'x_evidence_append__mutmut_15': x_evidence_append__mutmut_15, 
    'x_evidence_append__mutmut_16': x_evidence_append__mutmut_16, 
    'x_evidence_append__mutmut_17': x_evidence_append__mutmut_17, 
    'x_evidence_append__mutmut_18': x_evidence_append__mutmut_18, 
    'x_evidence_append__mutmut_19': x_evidence_append__mutmut_19, 
    'x_evidence_append__mutmut_20': x_evidence_append__mutmut_20, 
    'x_evidence_append__mutmut_21': x_evidence_append__mutmut_21, 
    'x_evidence_append__mutmut_22': x_evidence_append__mutmut_22, 
    'x_evidence_append__mutmut_23': x_evidence_append__mutmut_23, 
    'x_evidence_append__mutmut_24': x_evidence_append__mutmut_24, 
    'x_evidence_append__mutmut_25': x_evidence_append__mutmut_25, 
    'x_evidence_append__mutmut_26': x_evidence_append__mutmut_26, 
    'x_evidence_append__mutmut_27': x_evidence_append__mutmut_27, 
    'x_evidence_append__mutmut_28': x_evidence_append__mutmut_28, 
    'x_evidence_append__mutmut_29': x_evidence_append__mutmut_29, 
    'x_evidence_append__mutmut_30': x_evidence_append__mutmut_30, 
    'x_evidence_append__mutmut_31': x_evidence_append__mutmut_31, 
    'x_evidence_append__mutmut_32': x_evidence_append__mutmut_32, 
    'x_evidence_append__mutmut_33': x_evidence_append__mutmut_33, 
    'x_evidence_append__mutmut_34': x_evidence_append__mutmut_34, 
    'x_evidence_append__mutmut_35': x_evidence_append__mutmut_35, 
    'x_evidence_append__mutmut_36': x_evidence_append__mutmut_36, 
    'x_evidence_append__mutmut_37': x_evidence_append__mutmut_37, 
    'x_evidence_append__mutmut_38': x_evidence_append__mutmut_38, 
    'x_evidence_append__mutmut_39': x_evidence_append__mutmut_39, 
    'x_evidence_append__mutmut_40': x_evidence_append__mutmut_40, 
    'x_evidence_append__mutmut_41': x_evidence_append__mutmut_41, 
    'x_evidence_append__mutmut_42': x_evidence_append__mutmut_42, 
    'x_evidence_append__mutmut_43': x_evidence_append__mutmut_43, 
    'x_evidence_append__mutmut_44': x_evidence_append__mutmut_44, 
    'x_evidence_append__mutmut_45': x_evidence_append__mutmut_45, 
    'x_evidence_append__mutmut_46': x_evidence_append__mutmut_46, 
    'x_evidence_append__mutmut_47': x_evidence_append__mutmut_47, 
    'x_evidence_append__mutmut_48': x_evidence_append__mutmut_48, 
    'x_evidence_append__mutmut_49': x_evidence_append__mutmut_49, 
    'x_evidence_append__mutmut_50': x_evidence_append__mutmut_50, 
    'x_evidence_append__mutmut_51': x_evidence_append__mutmut_51, 
    'x_evidence_append__mutmut_52': x_evidence_append__mutmut_52, 
    'x_evidence_append__mutmut_53': x_evidence_append__mutmut_53, 
    'x_evidence_append__mutmut_54': x_evidence_append__mutmut_54, 
    'x_evidence_append__mutmut_55': x_evidence_append__mutmut_55, 
    'x_evidence_append__mutmut_56': x_evidence_append__mutmut_56, 
    'x_evidence_append__mutmut_57': x_evidence_append__mutmut_57, 
    'x_evidence_append__mutmut_58': x_evidence_append__mutmut_58, 
    'x_evidence_append__mutmut_59': x_evidence_append__mutmut_59, 
    'x_evidence_append__mutmut_60': x_evidence_append__mutmut_60, 
    'x_evidence_append__mutmut_61': x_evidence_append__mutmut_61
}

def evidence_append(*args, **kwargs):
    result = _mutmut_trampoline(x_evidence_append__mutmut_orig, x_evidence_append__mutmut_mutants, args, kwargs)
    return result 

evidence_append.__signature__ = _mutmut_signature(x_evidence_append__mutmut_orig)
x_evidence_append__mutmut_orig.__name__ = 'x_evidence_append'
