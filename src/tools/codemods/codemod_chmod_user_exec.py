#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import re
import sys

PATTERN = re.compile(r"os\.chmod\(\s*([^,]+),\s*0o?755\s*\)")
IMPORT = "from tools.security.permissions import add_user_exec\n"


def transform(text: str) -> str:
    updated = PATTERN.sub(r"add_user_exec(\1)", text)
    if updated != text and "from tools.security.permissions import add_user_exec" not in updated:
        updated = IMPORT + updated
    return updated


def main(root: str) -> int:
    changed = 0
    for path in pathlib.Path(root).rglob("*.py"):
        if path.is_relative_to(pathlib.Path("tools/codemods")):
            continue
        original = path.read_text(encoding="utf-8", errors="ignore")
        rewritten = transform(original)
        if rewritten != original:
            path.write_text(rewritten, encoding="utf-8")
            changed += 1
    print(f"codemod_chmod_user_exec changed {changed} files")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
