#!/usr/bin/env python3
"""
Check Archival Compliance

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/archival/check_archival_compliance.py [options]

    Examples:
    $ python scripts/archival/check_archival_compliance.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


# Evidence path: configurable via env var, defaults to relative path from repo root
EVIDENCE = Path(os.getenv("ARCHIVAL_EVIDENCE_PATH", ".codex/evidence/archive_ops.jsonl"))

# Git diff status prefixes that represent removal-style operations where the original path
# must satisfy tombstone + ADR + evidence requirements.  Git reports renames as "R100"
# (optionally with other scores), so we only look at the first character.
# Note: "C" (copy) is NOT included because copies leave the original file intact.
REMOVAL_STATUS_PREFIXES = {"D", "R"}


@dataclass
class DiffEntry:
    status: str
    path: str
    original_path: str | None = None


@dataclass
class CheckResult:
    missing_stub: list[str]
    missing_adr: list[str]
    missing_evidence: list[str]

    @property
    def return_code(self) -> int:
        if self.missing_stub or self.missing_adr:
            return 2
        return 0


def git_relevant_changes(base: str, head: str) -> list[DiffEntry]:
    cmd = ["git", "diff", "--name-status", f"{base}..{head}"]
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        print(f"[ERR] git diff failed: {out.stderr}", file=sys.stderr)
        raise RuntimeError("git diff failed")
    entries: list[DiffEntry] = []
    for ln in out.stdout.splitlines():
        parts = ln.strip().split("\t")
        if not parts:
            continue
        status = parts[0]
        if status.startswith("D"):
            if len(parts) >= 2:
                entries.append(DiffEntry(status=status, path=parts[1], original_path=parts[1]))
        elif status.startswith("M"):
            if len(parts) >= 2:
                entries.append(DiffEntry(status=status, path=parts[1], original_path=parts[1]))
        elif status.startswith("R"):
            # Rename: original file removed, new file created
            if len(parts) >= 3:
                entries.append(DiffEntry(status=status, path=parts[2], original_path=parts[1]))
        elif status.startswith("C"):
            # Copy: original file remains, new file created (not a removal operation)
            # We track it but won't enforce tombstone requirements
            if len(parts) >= 3:
                entries.append(DiffEntry(status=status, path=parts[2], original_path=parts[1]))
    return entries


def tombstone_exists(path: str) -> bool:
    p = Path(path)
    # Tombstone is expected at original path
    if p.exists():
        text = p.read_text(encoding="utf-8", errors="ignore")
        text_lower = text.lower()
        return "tombstone" in text_lower or "adr_ref" in text_lower
    return False


def adr_linked_in_stub(path: str) -> bool:
    p = Path(path)
    if not p.exists():
        return False
    txt = p.read_text(encoding="utf-8", errors="ignore")
    return "adr_ref" in txt or "ADR-" in txt


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
    except Exception as e:
        logger.debug(f"Exception: {e}")
        # Best-effort: ignore errors reading/parsing evidence file (e.g., file corruption, permission issues)
        print(
            f"[WARN] Could not read or parse evidence file {EVIDENCE} for path '{original_path}': {e}",
            file=sys.stderr,
        )
    return False


def evaluate_entries(diff_entries: list[DiffEntry]) -> CheckResult:
    missing_stub: list[str] = []
    missing_adr: list[str] = []
    missing_evidence: list[str] = []

    for entry in diff_entries:
        original_path = entry.original_path or entry.path
        stub_path = Path(original_path)
        status = entry.status.upper()
        status_prefix = status[:1]

        if status_prefix in REMOVAL_STATUS_PREFIXES and not stub_path.exists():
            # For deletes, renames, and copies we expect a tombstone stub at the original path.
            missing_stub.append(original_path)
            continue

        if status_prefix == "M":
            if not tombstone_exists(stub_path.as_posix()):
                # Standard modification; not a tombstone conversion.
                continue
        elif status_prefix in REMOVAL_STATUS_PREFIXES:
            if not stub_path.exists():
                # Defensive: if the stub disappeared between checks treat it as missing.
                missing_stub.append(original_path)
                continue
        else:
            continue

        if not adr_linked_in_stub(stub_path.as_posix()):
            missing_adr.append(original_path)

        if not evidence_has_entry(original_path):
            missing_evidence.append(original_path)

    return CheckResult(
        missing_stub=missing_stub,
        missing_adr=missing_adr,
        missing_evidence=missing_evidence,
    )


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

    diff_entries: list[DiffEntry] = []
    if args.removed_file:
        diff_entries = []
        for raw_line in Path(args.removed_file).read_text().splitlines():
            line = raw_line.strip()
            if not line:
                continue
            diff_entries.append(DiffEntry(status="D", path=line, original_path=line))
    else:
        try:
            diff_entries = git_relevant_changes(args.base, args.head)
        except RuntimeError as e:
            logger.debug(f"RuntimeError: {e}")
            return 3

    result = evaluate_entries(diff_entries)

    if result.missing_stub:
        print("[FAIL] Missing tombstone stub for removed paths:", file=sys.stderr)
        for p in result.missing_stub:
            print(f"  - {p}", file=sys.stderr)

    if result.missing_adr:
        print("[FAIL] Tombstone exists but missing ADR reference:", file=sys.stderr)
        for p in result.missing_adr:
            print(f"  - {p}", file=sys.stderr)

    if result.missing_evidence:
        print(
            "[WARN] Evidence entries not found for removed paths (append to .codex/evidence/archive_ops.jsonl):",
            file=sys.stderr,
        )
        for p in result.missing_evidence:
            print(f"  - {p}", file=sys.stderr)
        # warn only -> non-fatal, but return code may be adjusted by policy

    if result.return_code == 0:
        print("[OK] Archival compliance checks passed (basic).")

    return result.return_code


if __name__ == "__main__":
    sys.exit(main())
