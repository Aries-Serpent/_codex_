#!/usr/bin/env python3
"""Normalize Markdown code fences to satisfy validate-fences."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

LANG_DEFAULT = "text"


def _iter_targets(args: list[str]) -> list[Path]:
    if args:
        return [Path(a) for a in args]
    try:
        proc = subprocess.run(["git", "ls-files"], capture_output=True, check=True, text=True)
    except Exception:
        return []
    files: list[Path] = []
    for line in proc.stdout.splitlines():
        path = Path(line.strip())
        if path.suffix.lower() in {".md", ".mdx"}:
            files.append(path)
    return files


def _split_fence(line: str) -> tuple[str, str]:
    if not line:
        return "", ""
    fence_char = line[0]
    count = 0
    for ch in line:
        if ch == fence_char:
            count += 1
        else:
            break
    return fence_char * count, line[count:]


def fix(path: Path) -> None:
    if path.suffix.lower() not in {".md", ".mdx"}:
        return
    if not path.exists():
        return
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines()
    updated: list[str] = []
    inside = False
    fence_char = "`"
    fence_len = 3
    for line in lines:
        stripped = line.lstrip()
        prefix_len = len(line) - len(stripped)
        prefix = line[:prefix_len]
        if stripped.startswith("```") or stripped.startswith("~~~"):
            fence, remainder = _split_fence(stripped)
            if not inside:
                info = remainder.strip()
                if info:
                    updated.append(prefix + fence + remainder)
                else:
                    updated.append(f"{prefix}{fence} {LANG_DEFAULT}")
                inside = True
                fence_char = fence[0]
                fence_len = len(fence)
            else:
                updated.append(f"{prefix}{fence_char * fence_len}")
                inside = False
        else:
            updated.append(line)
    if inside:
        return
    new_text = "\n".join(updated)
    if original.endswith("\n"):
        new_text += "\n"
    if new_text != original:
        path.write_text(new_text, encoding="utf-8")


def main() -> int:
    targets = _iter_targets(sys.argv[1:])
    for target in targets:
        fix(target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
