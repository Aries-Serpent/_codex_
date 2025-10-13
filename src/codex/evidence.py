"""Shared helpers for writing append-only evidence artifacts."""

from __future__ import annotations

import json
import os
import platform
import subprocess
from collections.abc import Mapping
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

__all__ = [
    "append_evidence",
    "evidence_dir",
    "evidence_metadata",
    "utc_now",
]


def evidence_dir() -> Path:
    """Return the configured evidence directory, creating it if necessary."""

    base = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence")).resolve()
    base.mkdir(parents=True, exist_ok=True)
    return base


@lru_cache(maxsize=1)
def evidence_metadata() -> dict[str, str]:
    """Capture metadata that should be attached to every evidence record."""

    return {
        "commit": _git_commit_sha(),
        "python": platform.python_version(),
        "os": platform.platform(),
    }


def utc_now() -> str:
    """Return an ISO 8601 timestamp in UTC without microseconds."""

    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def append_evidence(filename: str, payload: Mapping[str, Any]) -> None:
    """Append ``payload`` to ``filename`` in the evidence directory."""

    record = {"meta": evidence_metadata(), **dict(payload)}
    out_path = evidence_dir() / filename
    with out_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=(",", ":")) + "\n")


def _git_commit_sha() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        return "unknown"
