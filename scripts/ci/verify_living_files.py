#!/usr/bin/env python3
"""verify_living_files.py — living-file staleness enforcement.

Checks that the 5 required living files for PR #4425 are present and
non-empty.  In ``--strict`` mode (used in CI and before every final
commit) exits with status 1 if any file is stale or missing.

Living files:
  1. CHANGELOG.md
  2. docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md
  3. docs/plans/PR4425_whats_next.md
  4. docs/sessions/PR4425_session_diagram.md
  5. .github/copilot-prompts/active/PR-4425-followup.md
"""

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

LIVING_FILES = [
    "CHANGELOG.md",
    "docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md",
    "docs/plans/PR4425_whats_next.md",
    "docs/sessions/PR4425_session_diagram.md",
    ".github/copilot-prompts/active/PR-4425-followup.md",
]

# Minimum byte size to consider a file non-stale (not just a header stub)
MIN_SIZE_BYTES = 200


def check_living_files(strict: bool = False) -> bool:
    """Return True if all living files are present and non-stale."""
    all_ok = True
    for rel_path in LIVING_FILES:
        path = REPO_ROOT / rel_path
        if not path.exists():
            print(f"❌ MISSING:  {rel_path}")
            all_ok = False
            continue
        size = path.stat().st_size
        if size < MIN_SIZE_BYTES:
            print(f"⚠️  STALE:    {rel_path}  ({size} bytes — below {MIN_SIZE_BYTES}B threshold)")
            all_ok = False
        else:
            print(f"✅ OK:       {rel_path}  ({size} bytes)")
    return all_ok


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that all living files for PR #4425 are present and non-stale."
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with status 1 if any living file is stale or missing.",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("🔍 verify_living_files — PR #4425 living-file check")
    print("=" * 60)

    ok = check_living_files(strict=args.strict)

    print("=" * 60)
    if ok:
        print("✅ All living files are present and non-stale.")
        return 0
    else:
        msg = "❌ One or more living files are stale or missing."
        if args.strict:
            print(f"{msg}  Exiting with status 1 (--strict mode).")
            return 1
        print(f"{msg}  (Pass --strict to block CI on this.)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
