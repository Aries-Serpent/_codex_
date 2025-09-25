#!/usr/bin/env python3
from __future__ import annotations

import argparse
import pathlib
import re

OPEN_RE = re.compile(r"^(\s*)(```)(\s*)$", re.MULTILINE)
CLOSE_LANG_RE = re.compile(r"^(\s*)(```+)[ \t]+\w+\s*$", re.MULTILINE)


def normalize_fences(text: str) -> str:
    updated = OPEN_RE.sub(r"\1\2text", text)
    updated = CLOSE_LANG_RE.sub(r"\1\2", updated)
    if "```" in updated and updated.count("```") >= 4 and "````" not in updated:
        updated = updated.replace("```", "````", 1).replace("```", "````", 1)
        updated = (
            updated[::-1]
            .replace("```"[::-1], "````"[::-1], 1)
            .replace("```"[::-1], "````"[::-1], 1)[::-1]
        )
    return updated


def iter_markdown_paths(paths: list[str]) -> list[pathlib.Path]:
    collected: list[pathlib.Path] = []
    for raw in paths:
        path = pathlib.Path(raw)
        if path.is_dir():
            collected.extend(sorted(path.rglob("*.md")))
        elif path.suffix.lower() in {".md", ".markdown"}:
            collected.append(path)
    return collected


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", help="Markdown files or directories")
    args = parser.parse_args(argv)

    changed = 0
    for path in iter_markdown_paths(args.paths):
        original = path.read_text(encoding="utf-8", errors="ignore")
        rewritten = normalize_fences(original)
        if rewritten != original:
            path.write_text(rewritten, encoding="utf-8")
            changed += 1
    print(f"normalized {changed} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
