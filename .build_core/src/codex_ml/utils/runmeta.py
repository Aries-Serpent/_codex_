"""Helpers to capture minimal run metadata for checkpoint sidecars."""

from __future__ import annotations

import hashlib
import logging
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def python_version() -> str:
    """Return the current Python interpreter version as a ``'major.minor.patch'`` string."""
    return ".".join(map(str, sys.version_info[:3]))


def _git_rev_parse() -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
            timeout=2,
        )
    except (IOError, OSError):
        logger.warning("Exception occurred", exc_info=True)
        return None
    return out.decode("utf-8").strip()


def _git_read_head(repo: Path) -> str | None:
    head = repo / ".git" / "HEAD"
    if not head.exists():
        return None
    try:
        ref = head.read_text(encoding="utf-8").strip()
    except (IOError, OSError):
        logger.warning("Exception occurred", exc_info=True)
        return None
    if ref.startswith("ref:"):
        _, ref_path = ref.split(":", 1)
        ref_file = repo / ".git" / ref_path.strip()
        if ref_file.exists():
            try:
                return ref_file.read_text(encoding="utf-8").strip()
            except (IOError, OSError):
                logger.warning("Exception occurred", exc_info=True)
                return None
        return None
    return ref or None


def git_sha(repo: str | Path = ".") -> str:
    """Return the current HEAD commit SHA for the repository at *repo*.

    Tries ``git rev-parse HEAD`` first; falls back to reading ``.git/HEAD``
    directly when the ``git`` binary is unavailable.  Returns an empty string
    when the SHA cannot be determined.

    Args:
        repo: Path to the root of the git repository.  Defaults to the
            current working directory.

    Returns:
        40-character hex SHA string, or ``""`` on failure.
    """
    repo_path = Path(repo)
    return _git_rev_parse() or _git_read_head(repo_path) or ""


def _sha256_file(path: Path) -> str | None:
    try:
        hasher = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1 << 16), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (IOError, OSError):
        logger.warning("Exception occurred", exc_info=True)
        return None


_LOCK_CANDIDATES = ("uv.lock", "requirements/lock.txt", "poetry.lock", "Pipfile.lock")


def lock_digest(root: str | Path = ".") -> str:
    """Return the SHA-256 hex digest of the first lock file found under *root*.

    Searches for ``uv.lock``, ``requirements/lock.txt``, ``poetry.lock``, and
    ``Pipfile.lock`` in that order.  Returns an empty string when none are
    found.

    Args:
        root: Repository root directory.  Defaults to the current working
            directory.

    Returns:
        64-character hex SHA-256 digest, or ``""`` when no lock file exists.
    """
    base = Path(root)
    for candidate in _LOCK_CANDIDATES:
        lock_path = base / candidate
        if lock_path.exists():
            digest = _sha256_file(lock_path)
            if digest:
                return digest
    return ""


def collect_run_meta(extra: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Collect minimal reproducibility metadata for a training run.

    Returns a dictionary with at least the following keys:

    * ``"python"`` — interpreter version string (see :func:`python_version`).
    * ``"git"`` — HEAD commit SHA (see :func:`git_sha`), empty if unavailable.
    * ``"lock_sha256"`` — SHA-256 of the first lock file found (see
      :func:`lock_digest`), empty if no lock file exists.

    Additional keys from *extra* are merged in (extra values take precedence).

    Args:
        extra: Optional mapping of additional metadata to include.

    Returns:
        Dictionary of run metadata suitable for JSON serialisation.
    """
    payload: dict[str, Any] = {
        "python": python_version(),
        "git": git_sha(),
        "lock_sha256": lock_digest(),
    }
    if extra:
        payload.update(dict(extra))
    return payload


__all__ = ["collect_run_meta", "git_sha", "lock_digest", "python_version"]
