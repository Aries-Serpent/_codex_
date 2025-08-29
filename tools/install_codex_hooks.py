#!/usr/bin/env python3
from __future__ import annotations

"""
Install a prepare-commit-msg git hook that appends Codex metadata (questions count
and report path) into commit messages. The hook is POSIX shell-based and will try
to use `git interpret-trailers` when available; otherwise it appends plain trailers.

This script is safe to run multiple times and will create the hooks directory if
missing. It prefers to detect the repository top-level via git; if that fails it
falls back to the current working directory.
"""

import os
import stat
import subprocess
from pathlib import Path
from textwrap import dedent
from typing import Optional


def repo_root() -> Path:
    """Return the git repository top-level path or current working directory.

    This function attempts to call `git rev-parse --show-toplevel`. If git is
    not available or the command fails, it falls back to the current working
    directory.
    """
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        root = out.stdout.strip()
        return Path(root or ".").resolve()
    except Exception:
        # Best-effort fallback
        return Path(".").resolve()


def write_hook(path: Path, content: str) -> None:
    """Write hook content to `path` and mark it executable.

    Any required parent directories are created. Errors are raised to surface
    problems to callers.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    try:
        # Set execute bits for owner/group/others in a portable way.
        mode = path.stat().st_mode
        path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except Exception:
        # If chmod fails (e.g., on constrained filesystems), ignore but do not crash.
        pass


def main() -> None:
    root = repo_root()
    hook = root / ".git" / "hooks" / "prepare-commit-msg"

    script = dedent(
        r"""#!/usr/bin/env bash
set -euo pipefail
MSG_FILE="$1"
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
QFILE="$ROOT/Codex_Questions.md"
REPORT="$ROOT/codex_commit_comment.txt"
COUNT=0
if [ -f "$QFILE" ]; then
  COUNT=$(grep -c '^Question for ChatGPT @codex ' "$QFILE" || true)
fi
if git interpret-trailers --help >/dev/null 2>&1; then
  git interpret-trailers --in-place \
    --trailer "Codex-Questions-Count=$COUNT" \
    --trailer "Codex-Report-Path=$REPORT" \
    "$MSG_FILE" || true
else
  {
    echo
    echo "Codex-Questions-Count: $COUNT"
    echo "Codex-Report-Path: $REPORT"
  } >> "$MSG_FILE" || true
fi
exit 0
"""
    )

    try:
        write_hook(hook, script)
        print(f"Installed prepare-commit-msg hook: {hook}")
    except Exception as exc:
        # Surface a helpful message but do not raise; callers/scripts can inspect exit code.
        print(f"Failed to install prepare-commit-msg hook at {hook}: {exc}", flush=True)


if __name__ == "__main__":
    main()
    