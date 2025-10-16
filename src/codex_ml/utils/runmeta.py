"""Helpers to capture minimal run metadata for checkpoint sidecars."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any


def python_version() -> str:
    return ".".join(map(str, sys.version_info[:3]))


def _git_rev_parse() -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
            timeout=2,
        )
    except Exception:
        return None
    return out.decode("utf-8").strip()


def _git_read_head(repo: Path) -> str | None:
    head = repo / ".git" / "HEAD"
    if not head.exists():
        return None
    try:
        ref = head.read_text(encoding="utf-8").strip()
    except Exception:
        return None
    if ref.startswith("ref:"):
        _, ref_path = ref.split(":", 1)
        ref_file = repo / ".git" / ref_path.strip()
        if ref_file.exists():
            try:
                return ref_file.read_text(encoding="utf-8").strip()
            except Exception:
                return None
        return None
    return ref or None


def git_sha(repo: str | Path = ".") -> str:
    repo_path = Path(repo)
    return _git_rev_parse() or _git_read_head(repo_path) or ""


def _sha256_file(path: Path) -> str | None:
    try:
        hasher = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1 << 16), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None


_LOCK_CANDIDATES = ("uv.lock", "requirements.lock", "poetry.lock", "Pipfile.lock")


def lock_digest(root: str | Path = ".") -> str:
    base = Path(root)
    for candidate in _LOCK_CANDIDATES:
        lock_path = base / candidate
        if lock_path.exists():
            digest = _sha256_file(lock_path)
            if digest:
                return digest
    return ""


def collect_run_meta(extra: Mapping[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "python": python_version(),
        "git": git_sha(),
        "lock_sha256": lock_digest(),
    }
    if extra:
        payload.update(dict(extra))
    return payload


__all__ = ["python_version", "git_sha", "lock_digest", "collect_run_meta"]
