#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(".github/workflows")
RAW_SETUP_PATTERN = re.compile(r"uses:\s*actions/setup-python@v[0-9]+", re.IGNORECASE)
EXCLUDED_PARTS = {"archived", "_archived", "examples", "ci-templates"}


def iter_workflow_files():
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.suffix not in {".yml", ".yaml"}:
            continue
        name = path.name
        if name.endswith(".disabled") or name.endswith(".template") or ".disabled" in name:
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        yield path


def main() -> int:
    offenders = []
    for path in iter_workflow_files():
        text = path.read_text(encoding="utf-8")
        if RAW_SETUP_PATTERN.search(text):
            offenders.append(path)

    if offenders:
        for path in offenders:
            print(f"{path}: raw actions/setup-python usage is forbidden in active workflows")
        return 1

    print("OK: no active workflow uses raw actions/setup-python.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
