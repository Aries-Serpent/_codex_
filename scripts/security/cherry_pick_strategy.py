#!/usr/bin/env python3
"""
Cherry Pick Strategy

Purpose:
    Main execution script

Usage:
    python scripts/security/cherry_pick_strategy.py [options]

    Examples:
    $ python scripts/security/cherry_pick_strategy.py --help

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

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], check: bool = True) -> tuple[int, str, str]:
    """Run a shell command and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=Path(__file__).resolve().parent.parent.parent,
    )

    if check and result.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}", file=sys.stderr)  # codeql[py/clear-text-logging-sensitive-data]
        print(f"STDERR: {result.stderr}", file=sys.stderr)  # codeql[py/clear-text-logging-sensitive-data]

    return result.returncode, result.stdout, result.stderr


def main():
    """Main entry point for cherry-pick strategy."""
    print("=" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print("CHERRY-PICK STRATEGY: Apply Ideal Versions to Clean Branch")  # codeql[py/clear-text-logging-sensitive-data]
    print("=" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    print("Current PR commits (from base bb92fab):")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]
    print("  1. 8475802 - Initial plan")  # codeql[py/clear-text-logging-sensitive-data]
    print("  2. 723f131 - Main revert (2,515 fixes, 1,009 files) ⭐ KEY COMMIT")  # codeql[py/clear-text-logging-sensitive-data]
    print("  3. 6725607 - Revert summary documentation")  # codeql[py/clear-text-logging-sensitive-data]
    print("  4. 4413e30 - Merge conflict resolution tools")  # codeql[py/clear-text-logging-sensitive-data]
    print("  5. 5f018a8 - Merge conflict resolution documentation")  # codeql[py/clear-text-logging-sensitive-data]
    print("  6. 163827f - Merge execution guide")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    print("=" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print("RECOMMENDED APPROACH: Cherry-Pick to Clean Branch")  # codeql[py/clear-text-logging-sensitive-data]
    print("=" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    print("This approach creates a clean branch without conflicts:")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]
    print("Step 1: Create fresh branch from target base")  # codeql[py/clear-text-logging-sensitive-data]
    print("-------")  # codeql[py/clear-text-logging-sensitive-data]
    print("  git fetch origin")  # codeql[py/clear-text-logging-sensitive-data]
    print("  git checkout -b copilot/sub-pr-2713-clean origin/0D_base_")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    print("Step 2: Cherry-pick the key commits")  # codeql[py/clear-text-logging-sensitive-data]
    print("-------")  # codeql[py/clear-text-logging-sensitive-data]
    print("  # Cherry-pick the main revert (most important)")  # codeql[py/clear-text-logging-sensitive-data]
    print("  git cherry-pick 723f131")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]
    print("  # Cherry-pick documentation commits")  # codeql[py/clear-text-logging-sensitive-data]
    print("  git cherry-pick 6725607")  # codeql[py/clear-text-logging-sensitive-data]
    print("  git cherry-pick 4413e30")  # codeql[py/clear-text-logging-sensitive-data]
    print("  git cherry-pick 5f018a8")  # codeql[py/clear-text-logging-sensitive-data]
    print("  git cherry-pick 163827f")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    print("Step 3: Push the clean branch")  # codeql[py/clear-text-logging-sensitive-data]
    print("-------")  # codeql[py/clear-text-logging-sensitive-data]
    print("  git push origin copilot/sub-pr-2713-clean")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    print("Step 4: Update PR to use clean branch")  # codeql[py/clear-text-logging-sensitive-data]
    print("-------")  # codeql[py/clear-text-logging-sensitive-data]
    print("  # On GitHub, change the PR base or create new PR from clean branch")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    print("=" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print("ALTERNATIVE: Cherry-Pick Specific Files")  # codeql[py/clear-text-logging-sensitive-data]
    print("=" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    print("If you want to cherry-pick specific file versions:")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]
    print("Method 1: Copy files from specific commit")  # codeql[py/clear-text-logging-sensitive-data]
    print("----------")  # codeql[py/clear-text-logging-sensitive-data]
    print("  # Get file from our corrected commit")  # codeql[py/clear-text-logging-sensitive-data]
    print("  git show 723f131:.codex/AI_AGENT_UTILITIES_REGISTRY.md > file.md")  # codeql[py/clear-text-logging-sensitive-data]
    print("  cp file.md .codex/AI_AGENT_UTILITIES_REGISTRY.md")  # codeql[py/clear-text-logging-sensitive-data]
    print("  git add .codex/AI_AGENT_UTILITIES_REGISTRY.md")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    print("Method 2: Checkout files from commit")  # codeql[py/clear-text-logging-sensitive-data]
    print("----------")  # codeql[py/clear-text-logging-sensitive-data]
    print("  # Checkout file as it was in commit 723f131")  # codeql[py/clear-text-logging-sensitive-data]
    print("  git checkout 723f131 -- .codex/AI_AGENT_UTILITIES_REGISTRY.md")  # codeql[py/clear-text-logging-sensitive-data]
    print("  git add .codex/AI_AGENT_UTILITIES_REGISTRY.md")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    print("Method 3: Bulk checkout from commit")  # codeql[py/clear-text-logging-sensitive-data]
    print("----------")  # codeql[py/clear-text-logging-sensitive-data]
    print("  # Get list of all files from the main revert commit")  # codeql[py/clear-text-logging-sensitive-data]
    print("  git diff --name-only bb92fab 723f131 > files_to_update.txt")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]
    print("  # Checkout each file from that commit")  # codeql[py/clear-text-logging-sensitive-data]
    print("  while IFS= read -r file; do")  # codeql[py/clear-text-logging-sensitive-data]
    print("      git checkout 723f131 -- \"$file\"")  # codeql[py/clear-text-logging-sensitive-data]
    print("  done < files_to_update.txt")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]
    print("  # Stage all updated files")  # codeql[py/clear-text-logging-sensitive-data]
    print("  git add -A")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    print("=" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print("WHAT GETS PRESERVED")  # codeql[py/clear-text-logging-sensitive-data]
    print("=" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]
    print("The key commit (723f131) contains:")  # codeql[py/clear-text-logging-sensitive-data]
    print("  ✓ 2,274 timestamp fixes (years restored)")  # codeql[py/clear-text-logging-sensitive-data]
    print("  ✓ 237 'may' word fixes")  # codeql[py/clear-text-logging-sensitive-data]
    print("  ✓ 4 'May' month fixes")  # codeql[py/clear-text-logging-sensitive-data]
    print("  ✓ Total: 2,515 corrections across 1,009 files")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    print("Cherry-picking this commit ensures all corrections are applied")  # codeql[py/clear-text-logging-sensitive-data]
    print("to a clean base without merge conflicts.")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    print("=" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print("EXECUTION GUIDE")  # codeql[py/clear-text-logging-sensitive-data]
    print("=" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]
    print("Choose one approach:")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]
    print("A) CLEANEST - New branch with cherry-picks")  # codeql[py/clear-text-logging-sensitive-data]
    print("   Best for: Avoiding all conflicts")  # codeql[py/clear-text-logging-sensitive-data]
    print("   Time: 5-10 minutes")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]
    print("B) QUICK - Checkout files from ideal commit")  # codeql[py/clear-text-logging-sensitive-data]
    print("   Best for: Updating existing branch")  # codeql[py/clear-text-logging-sensitive-data]
    print("   Time: 2-5 minutes")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]
    print("C) CURRENT - Use merge with strategy (from previous guides)")  # codeql[py/clear-text-logging-sensitive-data]
    print("   Best for: If base branch is available")  # codeql[py/clear-text-logging-sensitive-data]
    print("   Time: 2-5 minutes")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    return 0


if __name__ == "__main__":
    sys.exit(main())
