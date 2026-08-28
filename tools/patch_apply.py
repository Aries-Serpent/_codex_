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
import difflib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_LOG = REPO_ROOT / ".codex" / "generation_audit.jsonl"

BEGIN = re.compile(r"^\*\*\* Begin Patch")
END = re.compile(r"^\*\*\* End Patch")
ADD = re.compile(r"^\*\*\* Add File: (.+)$")
UPDATE = re.compile(r"^\*\*\* Update File: (.+)$")
DELETE = re.compile(r"^\*\*\* Delete File: (.+)$")


def audit(event: str, **details: object) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    payload = {"ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "event": event, **details}
    with AUDIT_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def ensure_repo_path(path_str: str) -> Path:
    candidate = Path(path_str)
    if not candidate.parts:
        raise ValueError("empty path")
    if ".." in candidate.parts:
        raise ValueError(f"path traversal blocked: {path_str}")
    if candidate.is_absolute():
        resolved = candidate.resolve(strict=False)
    else:
        resolved = (REPO_ROOT / candidate).resolve(strict=False)
    repo_root_resolved = REPO_ROOT.resolve()
    try:
        resolved.relative_to(repo_root_resolved)
    except ValueError as exc:
        raise ValueError(f"write outside repository root: {path_str}") from exc
    return resolved


def preview_diff(target: Path, new_content: str) -> str:
    old_content = target.read_text(encoding="utf-8") if target.exists() else ""
    diff = difflib.unified_diff(
        old_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile=str(target.relative_to(REPO_ROOT)) if target.is_relative_to(REPO_ROOT) else str(target),
        tofile=str(target.relative_to(REPO_ROOT)) if target.is_relative_to(REPO_ROOT) else str(target),
        lineterm="",
    )
    lines = list(diff)
    preview = "\n".join(lines[:80])
    if not preview:
        return "(no content change)"
    return preview


def apply_patch_block(lines: list[str], *, preview_only: bool = False) -> None:
    header = lines[0].strip()
    m_add = ADD.match(header)
    m_upd = UPDATE.match(header)
    m_del = DELETE.match(header)

    def validate_path(path_str: str) -> Path:
        try:
            return ensure_repo_path(path_str)
        except ValueError as exc:
            print(f"[ERROR] {exc}", file=sys.stderr)
            raise SystemExit(1) from exc

    if m_add:
        path = validate_path(m_add.group(1))
        content = "\n".join(lines[1:])
        audit("patch_preview", action="add", path=str(path.relative_to(REPO_ROOT)), preview=preview_diff(path, content))
        if preview_only:
            print(f"[PREVIEW] {path}\n{preview_diff(path, content)}")
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        audit("patch_applied", action="add", path=str(path.relative_to(REPO_ROOT)))
        print(f"[ADD] {path}")
    elif m_upd:
        path = validate_path(m_upd.group(1))
        content = "\n".join(lines[1:])
        audit("patch_preview", action="update", path=str(path.relative_to(REPO_ROOT)), preview=preview_diff(path, content))
        if preview_only:
            print(f"[PREVIEW] {path}\n{preview_diff(path, content)}")
            return
        if not path.exists():
            print(f"[WARN] Update target missing; creating {path}")
            path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        audit("patch_applied", action="update", path=str(path.relative_to(REPO_ROOT)))
        print(f"[UPDATE] {path}")
    elif m_del:
        path = validate_path(m_del.group(1))
        if path.exists():
            preview = f"DELETE {path.relative_to(REPO_ROOT)}"
            audit("patch_preview", action="delete", path=str(path.relative_to(REPO_ROOT)), preview=preview)
            if preview_only:
                print(f"[PREVIEW] {preview}")
                return
            path.unlink()
            audit("patch_applied", action="delete", path=str(path.relative_to(REPO_ROOT)))
            print(f"[DELETE] {path}")
        else:
            print(f"[SKIP] Missing file for delete: {path}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--patch-file", required=True)
    ap.add_argument("--preview", action="store_true", help="Show the diff without writing files.")
    args = ap.parse_args(argv)

    try:
        patch_path = ensure_repo_path(str(Path(args.patch_file)))
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2
    if not patch_path.exists():
        print(f"[ERROR] patch file missing: {patch_path}", file=sys.stderr)
        return 2

    text = patch_path.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(text):
        if BEGIN.match(text[i]):
            i += 1
            block = []
            while i < len(text) and not END.match(text[i]):
                block.append(text[i])
                i += 1
            apply_patch_block(block, preview_only=args.preview)
        i += 1

    print("[OK] Patch processing complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
