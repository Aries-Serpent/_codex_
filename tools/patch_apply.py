#!/usr/bin/env python3
"""
Apply simplified "*** Begin Patch" blocks from status document to the working directory.

Limitations:
- Supports Add/Update/Delete File markers.
- Does not handle complex renames or binary files.
- Intended for developer-local use; review patches before applying.

Usage:
  python tools/patch_apply.py --patch-file docs/templates/status/patch_example.diff
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


BEGIN = re.compile(r"^\*\*\* Begin Patch")
END = re.compile(r"^\*\*\* End Patch")
ADD = re.compile(r"^\*\*\* Add File: (.+)$")
UPDATE = re.compile(r"^\*\*\* Update File: (.+)$")
DELETE = re.compile(r"^\*\*\* Delete File: (.+)$")


def apply_patch_block(lines: list[str]) -> None:
    header = lines[0].strip()
    m_add = ADD.match(header)
    m_upd = UPDATE.match(header)
    m_del = DELETE.match(header)
    
    # Validate path to prevent directory traversal attacks
    # Allow absolute paths, but block paths with .. components
    def validate_path(path_str: str) -> Path:
        if ".." in Path(path_str).parts:
            print(f"[ERROR] Path traversal detected: {path_str}", file=sys.stderr)
            sys.exit(1)
        return Path(path_str)
    
    if m_add:
        path = validate_path(m_add.group(1))
        content = "\n".join(lines[1:])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"[ADD] {path}")
    elif m_upd:
        path = validate_path(m_upd.group(1))
        # naive update: replace file with provided content
        content = "\n".join(lines[1:])
        if not path.exists():
            print(f"[WARN] Update target missing; creating {path}")
            path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"[UPDATE] {path}")
    elif m_del:
        path = validate_path(m_del.group(1))
        if path.exists():
            path.unlink()
            print(f"[DELETE] {path}")
        else:
            print(f"[SKIP] Missing file for delete: {path}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--patch-file", required=True)
    args = ap.parse_args(argv)

    text = Path(args.patch_file).read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(text):
        if BEGIN.match(text[i]):
            # find header line next
            i += 1
            block = []
            while i < len(text) and not END.match(text[i]):
                block.append(text[i])
                i += 1
            apply_patch_block(block)
        i += 1

    print("[OK] Patch processing complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
