#!/usr/bin/env python3
"""Scan configuration directories for stale root path references."""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET_DIRS = ["configs", "conf", "deploy", ".github/workflows"]
PATTERNS = [
    r"AGENTS\.md",
    r"RUNBOOK\.md",
    r"CHANGELOG_[\w.-]+\.md",
    r"functional_training\.py",
]


def scan() -> int:
    issues: list[str] = []
    for directory in TARGET_DIRS:
        base = REPO_ROOT / directory
        if not base.exists():
            continue
        for file in base.rglob("*"):
            if not file.is_file():
                continue
            try:
                text = file.read_text(encoding="utf-8")
            except Exception:
                continue
            for pat in PATTERNS:
                if re.search(pat, text) and "docs/" not in text:
                    issues.append(f"{file}:{pat}")
    for issue in issues:
        print(issue)
    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(scan())
