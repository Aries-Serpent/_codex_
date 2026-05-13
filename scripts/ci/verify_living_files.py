#!/usr/bin/env python3
"""verify_living_files.py — living-file staleness enforcement.

Checks that the 5 required living files for a PR are present and
non-empty.  In ``--strict`` mode (used in CI and before every final
commit) exits with status 1 if any file is stale or missing.

Living files:
  1. CHANGELOG.md
  2. docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md
  3. docs/plans/PR{N}_whats_next.md
  4. docs/sessions/PR{N}_session_diagram.md
  5. .github/copilot-prompts/active/PR-{N}-followup.md
"""

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

DEFAULT_PR_NUMBER = 4425

# Minimum byte size to consider a file non-stale (not just a header stub)
MIN_SIZE_BYTES = 200


def _resolve_pr_number(cli_pr_number: int | None) -> int:
    if cli_pr_number is not None:
        if cli_pr_number <= 0:
            raise SystemExit(
                f"error: --pr-number must be a positive integer, got {cli_pr_number}\n"
                "usage: verify_living_files.py [--pr-number N] [--strict]"
            )
        return cli_pr_number
    env_pr = os.environ.get("PR_NUMBER")
    if env_pr and env_pr.isdigit():
        return int(env_pr)
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if event_path and Path(event_path).exists():
        try:
            with open(event_path, encoding="utf-8") as f:
                payload = json.load(f)
            pr_num = payload.get("pull_request", {}).get("number")
            if isinstance(pr_num, int):
                return pr_num
        except (OSError, json.JSONDecodeError) as exc:
            print(
                f"⚠️  Could not read PR number from GITHUB_EVENT_PATH '{event_path}': {exc}",
                file=sys.stderr,
            )
    return DEFAULT_PR_NUMBER


def _living_files(pr_number: int) -> list[str]:
    return [
        "CHANGELOG.md",
        "docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md",
        f"docs/plans/PR{pr_number}_whats_next.md",
        f"docs/sessions/PR{pr_number}_session_diagram.md",
        f".github/copilot-prompts/active/PR-{pr_number}-followup.md",
    ]


def check_living_files(pr_number: int) -> bool:
    """Return True if all living files are present and non-stale."""
    all_ok = True
    for rel_path in _living_files(pr_number):
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
        description="Verify that all required living files for a PR are present and non-stale."
    )
    parser.add_argument(
        "--pr-number",
        type=int,
        help=f"PR number to validate (default: auto-detect, fallback {DEFAULT_PR_NUMBER}).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with status 1 if any living file is stale or missing.",
    )
    args = parser.parse_args()

    pr_number = _resolve_pr_number(args.pr_number)
    print("=" * 60)
    print(f"🔍 verify_living_files — PR #{pr_number} living-file check")
    print("=" * 60)

    ok = check_living_files(pr_number)

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
