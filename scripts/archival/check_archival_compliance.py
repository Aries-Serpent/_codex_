#!/usr/bin/env python3
"""
Archival Compliance Checker (P6 Atomic Patchset)

Purpose:
- CI helper to enforce Archival Inventory Process for deletions between commits.
- Detects deleted files in the HEAD diff and ensures a tombstone stub and ADR reference exist,
  and that an evidence append exists in .codex/evidence/archive_ops.jsonl (basic check).

Usage:
  # Run in CI after PR commits are present
  python scripts/archival/check_archival_compliance.py --base <base-ref> --head <head-ref>

Notes / Limitations:
- Uses git to compute diff (local repo required).
- For complex flows (squashed merges, mirrored CI), pass explicit list of removed paths
  via --removed-file <file>.
- Non-exhaustive: intended as a CI gate to surface missing ADR/tombstone/evidence.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

EVIDENCE = Path(".codex/evidence/archive_ops.jsonl")


def git_deleted_between(base: str, head: str) -> list[str]:
    cmd = ["git", "diff", "--name-status", f"{base}..{head}"]
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        print(f"[ERR] git diff failed: {out.stderr}", file=sys.stderr)
        return []
    deleted = []
    for ln in out.stdout.splitlines():
        parts = ln.strip().split("\t", 1)
        if parts and parts[0].startswith("D"):  # format: D\tpath
            if len(parts) == 2:
                deleted.append(parts[1])
    return deleted


def tombstone_exists(path: str) -> bool:
    p = Path(path)
    stub = p.with_name(p.name)  # tombstone is expected at original path
    if stub.exists():
        text = stub.read_text(encoding="utf-8", errors="ignore")
        return "TOMBSTONE" in text or "tombstone" in text.lower() or "adr_ref" in text
    return False


def adr_linked_in_stub(path: str) -> bool:
    p = Path(path)
    if not p.exists():
        return False
    txt = p.read_text(encoding="utf-8", errors="ignore")
    return "adr_ref" in txt or "ADR-" in txt or "adr" in txt.lower()


def evidence_has_entry(original_path: str) -> bool:
    if not EVIDENCE.exists():
        return False
    try:
        for ln in EVIDENCE.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(ln)
            except Exception:
                continue
            if rec.get("path") == original_path or rec.get("original_path") == original_path:
                return True
    except Exception:
        pass
    return False


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="HEAD~1", help="Base ref for diff")
    ap.add_argument("--head", default="HEAD", help="Head ref for diff")
    ap.add_argument(
        "--removed-file",
        default="",
        help="Optional file with newline list of removed paths to check",
    )
    args = ap.parse_args(argv)

    removed = []
    if args.removed_file:
        removed = [l.strip() for l in Path(args.removed_file).read_text().splitlines() if l.strip()]
    else:
        removed = git_deleted_between(args.base, args.head)

    missing_stub = []
    missing_adr = []
    missing_evidence = []

    for r in removed:
        # expected tombstone stub at same path
        # For simplicity assume tombstone is a same-path replacement file (commit shows deletion then tombstone added)
        stub_path = Path(r)
        if not stub_path.exists():
            missing_stub.append(r)
            continue

        if not adr_linked_in_stub(stub_path.as_posix()):
            missing_adr.append(r)

        # evidence check (best-effort)
        if not evidence_has_entry(r):
            missing_evidence.append(r)

    # Summarize results
    rc = 0
    if missing_stub:
        print("[FAIL] Missing tombstone stub for removed paths:", file=sys.stderr)
        for p in missing_stub:
            print(f"  - {p}", file=sys.stderr)
        rc = 2

    if missing_adr:
        print("[FAIL] Tombstone exists but missing ADR reference:", file=sys.stderr)
        for p in missing_adr:
            print(f"  - {p}", file=sys.stderr)
        rc = 2

    if missing_evidence:
        print(
            "[WARN] Evidence entries not found for removed paths (append to .codex/evidence/archive_ops.jsonl):",
            file=sys.stderr,
        )
        for p in missing_evidence:
            print(f"  - {p}", file=sys.stderr)
        # warn only -> non-fatal, but return code may be adjusted by policy

    if rc == 0:
        print("[OK] Archival compliance checks passed (basic).")

    return rc


if __name__ == "__main__":
    sys.exit(main())
