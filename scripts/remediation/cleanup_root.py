#!/usr/bin/env python
"""
import logging
logger = logging.getLogger(__name__)
[Remediation]: Root Directory Sanitation
Purpose: Moves generated report and summary files from the repository root
to a dedicated archive directory to reduce cognitive load and clutter.

Target Pattern: *_REPORT.md, *_SUMMARY.md
Destination: reports/archive/

Flags:
 --dry-run  : Print planned moves without performing them
 --yes      : Confirm execution (required unless --dry-run)
"""
import shutil
import sys
import argparse
from pathlib import Path

# Anchor to repo root based on script location
ROOT = Path(__file__).resolve().parents[2]
ARCHIVE_DIR = ROOT / "reports" / "archive"


def find_root_matches(patterns):
    matches = []
    for pat in patterns:
        for src_file in sorted(ROOT.glob(pat)):
            if src_file.is_file() and src_file.parent == ROOT:
                matches.append(src_file)
    return matches


def main():
    parser = argparse.ArgumentParser(description="Sanitize root by archiving report/summary files.")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be moved, do not change files."
    )
    parser.add_argument(
        "--yes", action="store_true", help="Confirm execution (required unless --dry-run)."
    )
    args = parser.parse_args()

    print(f"[*] Remediation: Root Sanitation")
    print(f"[*] Target Root: {ROOT}")

    if not ROOT.exists():
        print(f"[!] Error: Root path detection failed: {ROOT}", file=sys.stderr)
        sys.exit(1)

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    patterns = ["*_REPORT.md", "*_SUMMARY.md"]
    to_move = find_root_matches(patterns)

    if not to_move:
        print("[+] Root is clean. No files required moving.")
        return

    print(f"[*] Planned moves ({len(to_move)}):")
    for f in to_move:
        print(f"  - {f.name} -> {ARCHIVE_DIR.relative_to(ROOT)}/{f.name}")

    if args.dry_run:
        print("[+] Dry-run complete. No changes made.")
        return

    if not args.yes:
        print("[!] Refusing to proceed without --yes. Run with --dry-run to preview.")
        sys.exit(2)

    moved_count = 0
    errors = 0
    for src_file in to_move:
        dest_file = ARCHIVE_DIR / src_file.name
        try:
            # Overwrite if exists to keep latest at root moved
            if dest_file.exists():
                dest_file.unlink()
            shutil.move(str(src_file), str(dest_file))
            moved_count += 1
        except Exception as e:
            logger.debug(f"Exception: {e}")
            print(f"  [!] Failed to move {src_file.name}: {e}", file=sys.stderr)
            errors += 1

    print(f"[+] Success: Moved {moved_count} files to {ARCHIVE_DIR.relative_to(ROOT)}")
    if errors > 0:
        print(f"[!] Warnings: {errors} files could not be processed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
