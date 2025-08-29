#!/usr/bin/env python3
from __future__ import annotations
import os
import stat
import subprocess
from pathlib import Path
from textwrap import dedent


def repo_root() -> Path:
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    return Path(out.stdout.strip() or ".").resolve()


def write_hook(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)


def main() -> None:
    root = repo_root()
    hook = root / ".git" / "hooks" / "prepare-commit-msg"
    script = dedent(r"""#!/usr/bin/env bash
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
""")
    write_hook(hook, script)
    print(f"Installed prepare-commit-msg hook: {hook}")


if __name__ == "__main__":
    main()
