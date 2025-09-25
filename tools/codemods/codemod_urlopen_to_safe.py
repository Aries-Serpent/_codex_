#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import re
import sys

IMPORT_PATTERN = re.compile(r"from urllib\.request import ([^\n]+)")


def _rewrite_import(match: re.Match[str]) -> str:
    names = [name.strip() for name in match.group(1).split(",")]
    remaining = [name for name in names if name != "urlopen"]
    if remaining:
        return f"from urllib.request import {', '.join(remaining)}"
    return ""


def transform(text: str) -> str:
    updated = IMPORT_PATTERN.sub(_rewrite_import, text)
    if "urlopen(" in updated:
        updated = updated.replace("urlopen(", "safe_fetch(")
        if "from tools.security.net import" not in updated:
            updated = "from tools.security.net import safe_fetch, safe_request\n" + updated
    return updated


def main(root: str) -> int:
    changed = 0
    for path in pathlib.Path(root).rglob("*.py"):
        if path.is_relative_to(pathlib.Path("tools/codemods")) or path.name == "net.py":
            continue
        original = path.read_text(encoding="utf-8", errors="ignore")
        rewritten = transform(original)
        if rewritten != original:
            path.write_text(rewritten, encoding="utf-8")
            changed += 1
    print(f"codemod_urlopen_to_safe changed {changed} files")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
