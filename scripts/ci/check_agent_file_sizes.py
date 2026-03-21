#!/usr/bin/env python3
"""
check_agent_file_sizes.py — Enforce the 30,000-character limit on custom agent files.

GitHub Copilot custom agent definition files in .github/agents/ MUST NOT exceed
30,000 characters.  If they do, the custom agent silently does NOT work.

Usage
-----
    # Check all top-level agent files (default):
    python scripts/ci/check_agent_file_sizes.py

    # Check specific files:
    python scripts/ci/check_agent_file_sizes.py .github/agents/my-agent.md

    # Check with custom limit:
    python scripts/ci/check_agent_file_sizes.py --limit 28000

    # Check only registered agents (from AGENT_REGISTRY.yaml):
    python scripts/ci/check_agent_file_sizes.py --registered-only

Exit codes
----------
    0  All files within limit
    1  One or more files exceed the limit

Integration
-----------
Add to pre-commit hooks or CI:

    # .pre-commit-config.yaml
    - repo: local
      hooks:
        - id: check-agent-file-sizes
          name: Check agent file sizes (30k limit)
          entry: python scripts/ci/check_agent_file_sizes.py
          language: python
          pass_filenames: false
          always_run: true

    # GitHub Actions (in any workflow):
    - name: Check agent file sizes
      run: python scripts/ci/check_agent_file_sizes.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
AGENT_REGISTRY = AGENTS_DIR / "AGENT_REGISTRY.yaml"

# Hard limit — GitHub Copilot custom agents silently fail above this.
DEFAULT_LIMIT = 30_000

# Warning threshold — flag files approaching the limit.
WARN_THRESHOLD = 0.83  # 83% = 24,900 chars


def get_registered_agent_ids() -> set[str]:
    """Parse AGENT_REGISTRY.yaml for registered agent IDs."""
    ids: set[str] = set()
    if not AGENT_REGISTRY.exists():
        return ids
    for line in AGENT_REGISTRY.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("- id:"):
            agent_id = stripped.split("- id:", 1)[1].strip()
            if agent_id:
                ids.add(agent_id)
    return ids


def get_agent_files(registered_only: bool = False) -> list[Path]:
    """Return the list of agent .md/.yml files to check."""
    if not AGENTS_DIR.exists():
        return []

    candidates = list(AGENTS_DIR.glob("*.md")) + list(AGENTS_DIR.glob("*.yml"))

    if not registered_only:
        return [f for f in candidates if f.name != "AGENT_REGISTRY.yaml"]

    # Registered only: match by stem against registry IDs
    ids = get_registered_agent_ids()
    result = []
    for f in candidates:
        stem = f.stem
        # Strip common suffixes like .agent from stem
        bare = stem.replace(".agent", "")
        if bare in ids or stem in ids:
            result.append(f)
    return result


def check_files(
    files: list[Path],
    limit: int = DEFAULT_LIMIT,
) -> tuple[list[tuple[Path, int]], list[tuple[Path, int]]]:
    """Return (over_limit, near_limit) lists of (path, size) tuples."""
    over_limit: list[tuple[Path, int]] = []
    near_limit: list[tuple[Path, int]] = []
    warn_chars = int(limit * WARN_THRESHOLD)

    for f in sorted(files):
        try:
            size = len(f.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        if size > limit:
            over_limit.append((f, size))
        elif size > warn_chars:
            near_limit.append((f, size))

    return over_limit, near_limit


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Enforce 30,000-character limit on GitHub Copilot custom agent files."
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Specific files to check (default: all top-level .md/.yml in .github/agents/)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        metavar="N",
        help=f"Character limit (default: {DEFAULT_LIMIT})",
    )
    parser.add_argument(
        "--registered-only",
        action="store_true",
        help="Only check files registered in AGENT_REGISTRY.yaml",
    )
    args = parser.parse_args(argv)

    if args.files:
        files = [Path(f) for f in args.files if Path(f).exists()]
    else:
        files = get_agent_files(registered_only=args.registered_only)

    if not files:
        print("ℹ  No agent files to check.")
        return 0

    over_limit, near_limit = check_files(files, limit=args.limit)

    if near_limit:
        print(f"⚠️  {len(near_limit)} agent file(s) approaching {args.limit:,}-char limit:")
        for path, size in sorted(near_limit, key=lambda x: -x[1]):
            pct = size * 100 // args.limit
            rel = path.relative_to(REPO_ROOT)
            print(f"   {pct:3d}%  {size:6,} chars  {rel}")

    if over_limit:
        print(f"\n❌ {len(over_limit)} agent file(s) EXCEED the {args.limit:,}-char limit:")
        print("   (These agents silently DO NOT WORK in GitHub Copilot)\n")
        for path, size in sorted(over_limit, key=lambda x: -x[1]):
            pct = size * 100 // args.limit
            rel = path.relative_to(REPO_ROOT)
            excess = size - args.limit
            print(f"   {pct:3d}%  {size:6,} chars  (+{excess:,} over limit)  {rel}")
        print(
            "\nFix: trim the file to under "
            f"{args.limit:,} chars, or move it out of .github/agents/\n"
            "     if it is not a registered custom agent definition."
        )
        return 1

    ok_count = len(files) - len(near_limit)
    print(
        f"✅ All {len(files)} agent file(s) within {args.limit:,}-char limit "
        f"({ok_count} OK, {len(near_limit)} near limit)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
