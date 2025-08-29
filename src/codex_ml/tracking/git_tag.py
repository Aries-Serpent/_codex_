# BEGIN: CODEX_GIT_TAG
"""Helpers for discovering Git metadata.

Currently only exposes :func:`current_commit` which returns the hash of the
current ``HEAD`` commit using ``git rev-parse``.  The function returns ``None``
when the command fails (for example when ``git`` is not installed or the
directory is not a repository).
"""
from __future__ import annotations

import subprocess


def _decode(out: bytes | str) -> str:
    """Return *out* as a decoded string."""
    if isinstance(out, bytes):
        try:
            return out.decode()
        except Exception:
            return out.decode("utf-8", errors="replace")
    return str(out)


def current_commit() -> str | None:
    """Return the current ``HEAD`` commit hash or ``None`` on error."""
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"])
        return _decode(out).strip()
    except Exception:
        return None


# END: CODEX_GIT_TAG
