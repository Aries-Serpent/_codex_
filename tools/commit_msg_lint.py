"""Enforce Conventional Commit messages at commit-msg stage."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Iterable

ALLOWED_TYPES = (
    "build",
    "chore",
    "ci",
    "docs",
    "feat",
    "fix",
    "perf",
    "refactor",
    "revert",
    "style",
    "test",
)

HEADER_RE = re.compile(
    rf"^(?P<type>{'|'.join(ALLOWED_TYPES)})(?:\((?P<scope>[A-Za-z0-9._/-]+)\))?(?P<breaking>!)?: (?P<summary>.+)$"
)

SKIP_SOURCES = {"merge", "squash", "commit"}


def _read_message(path: Path) -> Iterable[str]:
    """Yield non-comment lines from the commit message file."""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            continue
        yield line.rstrip("\n")


def _should_skip(path: Path, source: str | None) -> bool:
    if os.environ.get("CODEX_COMMIT_LINT_SKIP", "0") == "1":
        return True
    if source and source in SKIP_SOURCES:
        return True
    lines = list(_read_message(path))
    if not lines:
        return True
    header = lines[0].strip()
    if not header:
        return False
    lowered = header.lower()
    if lowered.startswith("merge ") or lowered.startswith("revert "):
        return True
    return False


def main(argv: list[str]) -> int:
    if not argv:
        print("commit_msg_lint: expected path to commit message file", file=sys.stderr)
        return 1

    message_path = Path(argv[0])
    source = argv[1] if len(argv) > 1 else None

    if _should_skip(message_path, source):
        return 0

    lines = [line.strip() for line in _read_message(message_path) if line.strip()]
    if not lines:
        print("commit message must start with a Conventional Commit header", file=sys.stderr)
        return 1

    header = lines[0]
    match = HEADER_RE.match(header)
    if not match:
        print(
            "Conventional Commit header expected: <type>(<scope>)?: <summary>.",
            file=sys.stderr,
        )
        print(f"Received: {header}", file=sys.stderr)
        print(
            "Allowed types: "
            + ", ".join(ALLOWED_TYPES)
            + "; scope is optional; use ! for breaking changes.",
            file=sys.stderr,
        )
        return 1

    if len(header) > 72:
        print("Header exceeds 72 characters; please shorten the summary.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
