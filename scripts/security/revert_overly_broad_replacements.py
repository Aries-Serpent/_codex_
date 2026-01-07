#!/usr/bin/env python3
"""
Revert Overly Broad Date and Word Replacements

This script fixes two types of incorrect replacements:
1. Timestamps where years were removed: "2026-01-05" -> "Current Cycle-01-05" (INCORRECT)
2. Words "may"/"May" changed to "phase"/"Phase 5": "may be" -> "phase be" (INCORRECT)

The script restores:
- Year portions in timestamps (e.g., "Current Cycle-01-05" -> "2026-01-05")
- "may"/"May" words (e.g., "Phase 5 need" -> "May need", "Phase 5 14, Current Cycle" -> "May 14, 2026")
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import NamedTuple


class FixStats(NamedTuple):
    """Statistics for fixes applied."""

    files_processed: int
    timestamp_fixes: int
    may_word_fixes: int
    may_month_fixes: int


def infer_year_from_month_day(month: str, day: str) -> str:
    """
    Infer the year based on month and day.
    
    For dates in the archive/historical/sessions context:
    - Dates from January are likely 2026
    - Dates from December are likely 2025
    - Other months need context
    """
    month_num = int(month)
    day_num = int(day)
    
    # January dates are 2026
    if month_num == 1:
        return "2026"
    # December dates are 2025
    elif month_num == 12:
        return "2025"
    # For other months, default to 2025 (most common in the archive)
    else:
        return "2025"


def fix_timestamps(content: str, filepath: Path) -> tuple[str, int]:
    """
    Fix timestamps where years were incorrectly removed.
    
    Patterns to fix:
    - "Current Cycle-01-05" -> "2026-01-05"
    - "Previous Cycle-12-27" -> "2025-12-27"
    - "Current Cycle-01-06T05:30:00Z" -> "2026-01-06T05:30:00Z"
    """
    fixes = 0
    
    # Pattern 1: Current Cycle-MM-DD or Current Cycle-MM-DDT... (should be 2026-MM-DD)
    # Use lookahead to handle both regular dates and ISO timestamps
    pattern1 = r'\bCurrent Cycle-(\d{2})-(\d{2})(?=[T\s\)]|$)'
    
    def replace_current(match):
        nonlocal fixes
        month, day = match.groups()
        fixes += 1
        year = infer_year_from_month_day(month, day)
        return f'{year}-{month}-{day}'
    
    content = re.sub(pattern1, replace_current, content)
    
    # Pattern 2: Previous Cycle-MM-DD or Previous Cycle-MM-DDT... (should be 2025-MM-DD or 2024-MM-DD)
    pattern2 = r'\bPrevious Cycle-(\d{2})-(\d{2})(?=[T\s\)]|$)'
    
    def replace_previous(match):
        nonlocal fixes
        month, day = match.groups()
        fixes += 1
        year = infer_year_from_month_day(month, day)
        # For "Previous Cycle", it's typically one year back
        if year == "2026":
            year = "2025"
        elif year == "2025":
            year = "2024"
        return f'{year}-{month}-{day}'
    
    content = re.sub(pattern2, replace_previous, content)
    
    return content, fixes


def fix_may_word_replacements(content: str) -> tuple[str, int]:
    """
    Fix incorrect "may" -> "phase"/"Phase 5" replacements.
    
    Patterns to fix:
    - "Phase 5 need" -> "May need"
    - "Phase 5 have" -> "may have"  
    - "Phase 5 fail" -> "may fail"
    - "Phase 5 be" -> "may be"
    - "Phase 5 not" -> "may not"
    - "Phase 5 require" -> "may require"
    - "Phase 5 exceed" -> "may exceed"
    - "Phase 5 show" -> "may show"
    - "Phase 5 flag" -> "may flag"
    
    Context: These are auxiliary verb constructions where "may" indicates possibility.
    """
    fixes = 0
    
    # Words that follow "may" as an auxiliary verb
    auxiliary_verbs = [
        'be', 'have', 'need', 'fail', 'not', 'require', 'exceed', 
        'show', 'flag', 'contain', 'miss', 'match', 'take', 'behave',
        'become', 'benefit',
    ]
    
    # Build pattern for "Phase 5 + verb"
    pattern = r'\bPhase 5 (' + '|'.join(auxiliary_verbs) + r')\b'
    
    def replace_phase5(match):
        nonlocal fixes
        verb = match.group(1)
        fixes += 1
        # Lowercase "may" for auxiliary verb usage
        return f'may {verb}'
    
    content = re.sub(pattern, replace_phase5, content, flags=re.IGNORECASE)
    
    return content, fixes


def fix_may_month_replacements(content: str) -> tuple[str, int]:
    """
    Fix incorrect "May" (month) -> "Phase 5" replacements.
    
    Patterns to fix:
    - "Phase 5 14, Current Cycle" -> "May 14, 2026"
    - "by Phase 5 14, 2026" -> "by May 14, 2026"
    - "Phase 5 the PDA Loop" -> "May the PDA Loop"
    """
    fixes = 0
    
    # Pattern 1: "Phase 5 DD, Current Cycle" -> "May DD, 2026"
    pattern1 = r'\bPhase 5 (\d{1,2}), Current Cycle\b'
    
    def replace_month_current(match):
        nonlocal fixes
        day = match.group(1)
        fixes += 1
        return f'May {day}, 2026'
    
    content = re.sub(pattern1, replace_month_current, content)
    
    # Pattern 2: "Phase 5 DD, 20XX" -> "May DD, 20XX"
    pattern2 = r'\bPhase 5 (\d{1,2}), (20\d{2})\b'
    
    def replace_month_year(match):
        nonlocal fixes
        day, year = match.groups()
        fixes += 1
        return f'May {day}, {year}'
    
    content = re.sub(pattern2, replace_month_year, content)
    
    # Pattern 3: "Phase 5 the" (as in "May the force be with you")
    pattern3 = r'\bPhase 5 the\b'
    
    def replace_may_the(match):
        nonlocal fixes
        fixes += 1
        return 'May the'
    
    content = re.sub(pattern3, replace_may_the, content)
    
    return content, fixes


def process_file(filepath: Path) -> tuple[bool, int, int, int]:
    """
    Process a single file and fix incorrect replacements.
    
    Returns:
        (changed, timestamp_fixes, may_word_fixes, may_month_fixes)
    """
    try:
        content = filepath.read_text(encoding='utf-8')
        original_content = content
        
        # Apply fixes
        content, ts_fixes = fix_timestamps(content, filepath)
        content, word_fixes = fix_may_word_replacements(content)
        content, month_fixes = fix_may_month_replacements(content)
        
        # Write back if changed
        if content != original_content:
            filepath.write_text(content, encoding='utf-8')
            return True, ts_fixes, word_fixes, month_fixes
        
        return False, 0, 0, 0
        
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
        return False, 0, 0, 0


def main():
    """Main entry point."""
    # Find all markdown files in the repository (excluding node_modules, .git, etc.)
    repo_root = Path(__file__).resolve().parent.parent.parent
    
    if not repo_root.exists():
        print(f"Error: {repo_root} not found", file=sys.stderr)
        sys.exit(1)
    
    # Find all .md files, excluding certain directories
    exclude_dirs = {'.git', 'node_modules', 'dist', 'build', '__pycache__', '.pytest_cache', '.mypy_cache'}
    md_files = []
    for md_file in repo_root.rglob("*.md"):
        # Skip if any parent is in exclude_dirs
        if not any(part in exclude_dirs for part in md_file.parts):
            md_files.append(md_file)
    
    print(f"Found {len(md_files)} markdown files to process")
    print("=" * 60)
    
    stats = FixStats(0, 0, 0, 0)
    changed_files = []
    
    for filepath in md_files:
        changed, ts_fixes, word_fixes, month_fixes = process_file(filepath)
        if changed:
            stats = FixStats(
                stats.files_processed + 1,
                stats.timestamp_fixes + ts_fixes,
                stats.may_word_fixes + word_fixes,
                stats.may_month_fixes + month_fixes,
            )
            changed_files.append(filepath.relative_to(repo_root))
            print(f"✓ {filepath.relative_to(repo_root)}")
            if ts_fixes:
                print(f"  - Fixed {ts_fixes} timestamp(s)")
            if word_fixes:
                print(f"  - Fixed {word_fixes} 'may' word(s)")
            if month_fixes:
                print(f"  - Fixed {month_fixes} 'May' month reference(s)")
    
    print()
    print("=" * 60)
    print("Summary:")
    print(f"  Files processed:      {stats.files_processed}")
    print(f"  Timestamp fixes:      {stats.timestamp_fixes}")
    print(f"  'may' word fixes:     {stats.may_word_fixes}")
    print(f"  'May' month fixes:    {stats.may_month_fixes}")
    print(f"  Total fixes:          {stats.timestamp_fixes + stats.may_word_fixes + stats.may_month_fixes}")
    
    if stats.files_processed == 0:
        print("\n✓ No files needed fixing")
    else:
        print(f"\n✓ Successfully fixed {stats.files_processed} files")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
