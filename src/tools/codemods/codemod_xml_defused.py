#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import sys

TARGETS = (
    "import xml.etree.ElementTree as ET",
    "from xml.etree import ElementTree as ET",
)
REPLACEMENT = "from defusedxml import ElementTree as ET"


def transform(text: str) -> str:
    updated = text
    for target in TARGETS:
        updated = updated.replace(target, REPLACEMENT)
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
    print(f"codemod_xml_defused changed {changed} files")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
