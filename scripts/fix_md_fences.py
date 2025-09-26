#!/usr/bin/env python3
"""
Fix common Markdown fence issues repo-wide:
 - Add a language (default: 'text') to bare ``` fences.
 - Ensure closing fences do NOT include a language.
 - Convert nested fences by upgrading the outer fence when needed.
Usage:
    python scripts/fix_md_fences.py [--write] [paths...]
If --write is omitted, prints a diff-like preview to stdout.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
from typing import Iterable

OPEN_OR_CLOSE_RE = re.compile(r"^(\s*)(`{3,})(.*)$")


def iter_files(paths: list[str]) -> Iterable[pathlib.Path]:
    if not paths:
        paths = ["docs"]
    for p in paths:
        candidate = pathlib.Path(p)
        if candidate.is_dir():
            yield from candidate.rglob("*.md")
        elif candidate.suffix == ".md":
            yield candidate


def fix_content(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    stack: list[tuple[str, str]] = []
    for line in lines:
        match = OPEN_OR_CLOSE_RE.match(line)
        if match:
            indent, raw_ticks, rest = match.groups()
            rest = rest.strip()
            if stack and (
                not rest or rest.lower() == stack[-1][1].lower() or rest.lower() == "text"
            ):
                open_ticks, _ = stack.pop()
                ticks = raw_ticks if len(raw_ticks) >= len(open_ticks) else open_ticks
                out.append(f"{indent}{ticks}")
                continue

            lang = rest.split()[0] if rest else "text"
            ticks = raw_ticks
            if stack and len(ticks) <= len(stack[-1][0]):
                ticks = stack[-1][0] + "`"
            stack.append((ticks, lang))
            out.append(f"{indent}{ticks}{lang}")
            continue
        out.append(line)
    while stack:
        ticks, _ = stack.pop()
        out.append(ticks)
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="apply changes in-place")
    parser.add_argument("paths", nargs="*")
    args = parser.parse_args()

    changed = 0
    for path in iter_files(args.paths):
        text = path.read_text(encoding="utf-8", errors="replace")
        new_text = fix_content(text)
        if new_text != text:
            changed += 1
            if args.write:
                path.write_text(new_text, encoding="utf-8")
                print(f"fixed {path}")
            else:
                sys.stdout.write(f"--- {path}\n+++ {path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
