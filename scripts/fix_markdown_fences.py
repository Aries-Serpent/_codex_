#!/usr/bin/env python3
"""
Normalize Markdown code fences across the repo:
 - Opening fences without an info string -> use ```text
 - Closing fences never include a language
 - If a fenced block's body contains triple backticks, upgrade the OUTER fence to four backticks
Idempotent; safe to run multiple times.
"""

from __future__ import annotations

import re
from pathlib import Path

OPEN_BARE = re.compile(r"(?m)^```(?![`\w])")
CLOSE_WITH_LANG = re.compile(r"(?m)^```[A-Za-z0-9_+-]+\s*$")
BLOCK_RE = re.compile(r"(?s)(```+)([^`\n]*)\n(.*?)\n```+\s*")


def _normalize_block(match: re.Match[str]) -> str:
    fence, info, body = match.groups()
    info = info.strip() or "text"
    inner_fence = "````" if "```" in body else fence
    body = body.replace("\r\n", "\n")
    return f"{inner_fence} {info}\n{body}\n{inner_fence}"


def normalize_markdown(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    text = OPEN_BARE.sub("```text", text)
    text = CLOSE_WITH_LANG.sub("```", text)
    text = BLOCK_RE.sub(_normalize_block, text)
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def iter_markdown_files(root: Path) -> list[Path]:
    return [p for p in root.rglob("*.md") if p.is_file()]


def main() -> int:
    root = Path.cwd()
    changed = 0
    for md in iter_markdown_files(root):
        try:
            if normalize_markdown(md):
                print(f"normalized {md}")
                changed += 1
        except Exception as exc:  # pragma: no cover - best effort script
            print(f"warning: failed to normalize {md}: {exc}")
    print(f"markdown normalization complete: {changed} files updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
