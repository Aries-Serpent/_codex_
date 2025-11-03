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


def find_repo_root() -> Path:
    """
    Find repository root by looking for .git directory starting from script location.
    
    This prioritizes the script's location to prevent CWD-based bypass attacks.
    """
    # Start from script location (tools/patch_apply.py -> tools/ -> repo_root/)
    script_path = Path(__file__).resolve()
    current = script_path.parent  # Start at tools/
    
    # Search up from script location for .git directory
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    
    # If no .git found, use script's parent as fallback (tools -> root)
    # This assumes the script is in tools/ subdirectory
    return script_path.parent.parent


def apply_patch_block(lines: list[str], repo_root: Path) -> None:
    header = lines[0].strip()
    m_add = ADD.match(header)
    m_upd = UPDATE.match(header)
    m_del = DELETE.match(header)
    
    if m_add:
        path = Path(m_add.group(1)).resolve()
        if not path.is_relative_to(repo_root):
            print(f"[ERROR] Path outside repository root: {m_add.group(1)}", file=sys.stderr)
            sys.exit(1)
        content = "\n".join(lines[1:])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"[ADD] {path}")
    elif m_upd:
        path = Path(m_upd.group(1)).resolve()
        if not path.is_relative_to(repo_root):
            print(f"[ERROR] Path outside repository root: {m_upd.group(1)}", file=sys.stderr)
            sys.exit(1)
        # naive update: replace file with provided content
        content = "\n".join(lines[1:])
        if not path.exists():
            print(f"[WARN] Update target missing; creating {path}")
            path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"[UPDATE] {path}")
    elif m_del:
        path = Path(m_del.group(1)).resolve()
        if not path.is_relative_to(repo_root):
            print(f"[ERROR] Path outside repository root: {m_del.group(1)}", file=sys.stderr)
            sys.exit(1)
        if path.exists():
            path.unlink()
            print(f"[DELETE] {path}")
        else:
            print(f"[SKIP] Missing file for delete: {path}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--patch-file", required=True)
    args = ap.parse_args(argv)

    repo_root = find_repo_root()
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
            apply_patch_block(block, repo_root)
        i += 1

    print("[OK] Patch processing complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
