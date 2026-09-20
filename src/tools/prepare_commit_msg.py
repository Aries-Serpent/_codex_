"""Lightweight prepare-commit-msg helper for Conventional Commits."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ALLOWED_TYPES = {
    "build",
    "chore",
    "ci",
    "docs",
    "feat",
    "fix",
    "perf",
    "refactor",
    "style",
    "test",
}

SKIP_SOURCES = {
    "commit",
    "merge",
    "message",
    "squash",
    "template",
}

DEFAULT_TYPE = "chore"


def _git(cmd: list[str]) -> str:
    result = subprocess.run(
        ["git", *cmd],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _slug_to_summary(slug: str) -> str:
    if not slug:
        return "update"
    parts = re.split(r"[/_-]+", slug)
    words: list[str] = []
    for part in parts:
        if not part:
            continue
        if part.isupper() or any(char.isdigit() for char in part):
            words.append(part)
        else:
            words.append(part.lower())
    summary = " ".join(words).strip()
    return summary or "update"


def _derive_header(branch: str) -> str:
    branch = branch.strip()
    if not branch:
        return f"{DEFAULT_TYPE}: update"
    if branch.startswith("heads/"):
        branch = branch.split("/", 1)[1]
    primary, *rest = branch.split("/")
    commit_type = primary if primary in ALLOWED_TYPES else DEFAULT_TYPE
    summary_slug = "/".join(rest)
    summary = _slug_to_summary(summary_slug)
    return f"{commit_type}: {summary}"


def main(argv: list[str]) -> int:
    if os.environ.get("CODEX_PREPARE_COMMIT_SKIP", "0") == "1":
        return 0
    if not argv:
        return 0

    message_path = Path(argv[0])
    source = argv[1] if len(argv) > 1 else None

    if source and source in SKIP_SOURCES:
        return 0
    if not message_path.exists():
        return 0

    content = message_path.read_text(encoding="utf-8")
    if content.strip():
        return 0

    branch = _git(["symbolic-ref", "--quiet", "HEAD"])
    header = _derive_header(branch)
    message_path.write_text(f"{header}\n\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
