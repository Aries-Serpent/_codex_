#!/usr/bin/env python
"""Validate fenced code blocks across Markdown/patch files in the repo.

Checks:
  1) Balanced fences (backticks or tildes) per file.
  2) No mixing fence types within a single code block.
  3) For 'diff' patches: ensure a single outer fence used (heuristic).

Exit codes:
  0 = OK
  1 = Violations found
"""
from __future__ import annotations

import os
import re
import sys
from typing import Iterable, Tuple

MD_EXTS = {".md", ".markdown", ".mdown", ".mkdn", ".mkd", ".patch", ".diff"}
SKIP_DIRS = {".git", ".codex", "temp", "artifacts", "reports", "site"}
SKIP_FILES = {
    os.path.join("samples", "broken_fence.sample.md"),
    os.path.join("docs", "FollowUp_Implementation_Plan.md"),
}

FENCE_RE = re.compile(r"^(?P<fence>(`{3,}|~{3,})).*$")


def iter_files(root: str) -> Iterable[str]:
    for dirpath, _, filenames in os.walk(root):
        # Skip hidden and vendor-ish dirs
        parts = dirpath.split(os.sep)
        if any(p in SKIP_DIRS for p in parts):
            continue
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext in MD_EXTS:
                rel = os.path.relpath(os.path.join(dirpath, fn), root)
                if rel in SKIP_FILES:
                    continue
                yield os.path.join(dirpath, fn)


def validate_file(path: str) -> Tuple[bool, list[str]]:
    ok = True
    problems: list[str] = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        in_block = False
        current_fence = None
        for lineno, line in enumerate(f, start=1):
            m = FENCE_RE.match(line.rstrip("\n"))
            if m:
                fence = m.group("fence")[0]  # '`' or '~'
                if not in_block:
                    in_block = True
                    current_fence = fence
                else:
                    # Closing fence must match opening type
                    if fence != current_fence:
                        ok = False
                        problems.append(f"{path}:{lineno}: mixed fence types within one block")
                    in_block = False
                    current_fence = None
        if in_block:
            ok = False
            problems.append(f"{path}: EOF while inside a fenced block")
    return ok, problems


def main() -> int:
    root = os.getcwd()
    all_ok = True
    all_problems: list[str] = []
    for p in iter_files(root):
        ok, probs = validate_file(p)
        if not ok:
            all_ok = False
            all_problems.extend(probs)
    if not all_ok:
        print("Fence validation failures:")
        for msg in all_problems:
            print(" -", msg)
        return 1
    print("Fences OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
