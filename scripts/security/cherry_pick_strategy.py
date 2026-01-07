#!/usr/bin/env python3
"""
Cherry-Pick Strategy for Clean Merge

This script helps cherry-pick the ideal corrected versions from this PR
into a clean branch based on the target (0D_base_), avoiding merge conflicts.

Strategy:
1. Create a new branch from 0D_base_ 
2. Cherry-pick only the commits with actual fixes (not merge commits)
3. This gives a clean history without conflicts
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
        print(f"Command failed: {' '.join(cmd)}", file=sys.stderr)
        print(f"STDERR: {result.stderr}", file=sys.stderr)
    
    return result.returncode, result.stdout, result.stderr


def main():
    """Main entry point for cherry-pick strategy."""
    print("=" * 80)
    print("CHERRY-PICK STRATEGY: Apply Ideal Versions to Clean Branch")
    print("=" * 80)
    print()
    
    print("Current PR commits (from base bb92fab):")
    print()
    print("  1. 8475802 - Initial plan")
    print("  2. 723f131 - Main revert (2,515 fixes, 1,009 files) ⭐ KEY COMMIT")
    print("  3. 6725607 - Revert summary documentation")
    print("  4. 4413e30 - Merge conflict resolution tools")
    print("  5. 5f018a8 - Merge conflict resolution documentation")
    print("  6. 163827f - Merge execution guide")
    print()
    
    print("=" * 80)
    print("RECOMMENDED APPROACH: Cherry-Pick to Clean Branch")
    print("=" * 80)
    print()
    
    print("This approach creates a clean branch without conflicts:")
    print()
    print("Step 1: Create fresh branch from target base")
    print("-------")
    print("  git fetch origin")
    print("  git checkout -b copilot/sub-pr-2713-clean origin/0D_base_")
    print()
    
    print("Step 2: Cherry-pick the key commits")
    print("-------")
    print("  # Cherry-pick the main revert (most important)")
    print("  git cherry-pick 723f131")
    print()
    print("  # Cherry-pick documentation commits")
    print("  git cherry-pick 6725607")
    print("  git cherry-pick 4413e30")
    print("  git cherry-pick 5f018a8")
    print("  git cherry-pick 163827f")
    print()
    
    print("Step 3: Push the clean branch")
    print("-------")
    print("  git push origin copilot/sub-pr-2713-clean")
    print()
    
    print("Step 4: Update PR to use clean branch")
    print("-------")
    print("  # On GitHub, change the PR base or create new PR from clean branch")
    print()
    
    print("=" * 80)
    print("ALTERNATIVE: Cherry-Pick Specific Files")
    print("=" * 80)
    print()
    
    print("If you want to cherry-pick specific file versions:")
    print()
    print("Method 1: Copy files from specific commit")
    print("----------")
    print("  # Get file from our corrected commit")
    print("  git show 723f131:.codex/AI_AGENT_UTILITIES_REGISTRY.md > file.md")
    print("  cp file.md .codex/AI_AGENT_UTILITIES_REGISTRY.md")
    print("  git add .codex/AI_AGENT_UTILITIES_REGISTRY.md")
    print()
    
    print("Method 2: Checkout files from commit")
    print("----------")
    print("  # Checkout file as it was in commit 723f131")
    print("  git checkout 723f131 -- .codex/AI_AGENT_UTILITIES_REGISTRY.md")
    print("  git add .codex/AI_AGENT_UTILITIES_REGISTRY.md")
    print()
    
    print("Method 3: Bulk checkout from commit")
    print("----------")
    print("  # Get list of all files from the main revert commit")
    print("  git diff --name-only bb92fab 723f131 > files_to_update.txt")
    print()
    print("  # Checkout each file from that commit")
    print("  while IFS= read -r file; do")
    print("      git checkout 723f131 -- \"$file\"")
    print("  done < files_to_update.txt")
    print()
    print("  # Stage all updated files")
    print("  git add -A")
    print()
    
    print("=" * 80)
    print("WHAT GETS PRESERVED")
    print("=" * 80)
    print()
    print("The key commit (723f131) contains:")
    print("  ✓ 2,274 timestamp fixes (years restored)")
    print("  ✓ 237 'may' word fixes")
    print("  ✓ 4 'May' month fixes")
    print("  ✓ Total: 2,515 corrections across 1,009 files")
    print()
    
    print("Cherry-picking this commit ensures all corrections are applied")
    print("to a clean base without merge conflicts.")
    print()
    
    print("=" * 80)
    print("EXECUTION GUIDE")
    print("=" * 80)
    print()
    print("Choose one approach:")
    print()
    print("A) CLEANEST - New branch with cherry-picks")
    print("   Best for: Avoiding all conflicts")
    print("   Time: 5-10 minutes")
    print()
    print("B) QUICK - Checkout files from ideal commit")
    print("   Best for: Updating existing branch")
    print("   Time: 2-5 minutes")
    print()
    print("C) CURRENT - Use merge with strategy (from previous guides)")
    print("   Best for: If base branch is available")
    print("   Time: 2-5 minutes")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
