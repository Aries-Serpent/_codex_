# BEGIN: CODEX_GIT_TAG
"""Helpers for discovering Git metadata.

Currently only exposes :func:`current_commit` which returns the hash of the
current ``HEAD`` commit using ``git rev-parse``.  The function returns ``None``
when the command fails (for example when ``git`` is not installed or the
directory is not a repository).
"""
from __future__ import annotations

import subprocess


def current_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


# END: CODEX_GIT_TAG
