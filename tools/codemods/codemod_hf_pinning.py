#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import re
import sys

PATTERN = re.compile(r"(?P<expr>[A-Za-z_][A-Za-z0-9_\.]*)\.from_pretrained\(")
IMPORT = "from codex_ml.utils.hf_pinning import load_from_pretrained\n"


def transform(text: str) -> str:
    updated = PATTERN.sub(lambda match: f"load_from_pretrained({match.group('expr')}, ", text)
    if (
        updated != text
        and "from codex_ml.utils.hf_pinning import load_from_pretrained" not in updated
    ):
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
    print(f"codemod_hf_pinning changed {changed} files")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
