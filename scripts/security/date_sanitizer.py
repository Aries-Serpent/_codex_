#!/usr/bin/env python3
"""
Date Sanitizer

Purpose:
    Main execution script

Usage:
    python scripts/security/date_sanitizer.py [options]
    
    Examples:
    $ python scripts/security/date_sanitizer.py --help

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


"""
Date Sanitization Policy Enforcer

This module provides smart date pattern detection and replacement for documentation.
It distinguishes between:
1. Actual timestamps/version dates (PRESERVED): "2026-01-05", "v1.2.3 (2026-01-05)", "Released: 2026-01-05"
2. Calendar-based planning terminology (SANITIZED): "Q1 2026", "January 2026", "Phase 1 (Q2 2026)"

The goal is to remove specific calendar commitments while preserving technical timestamps
that are part of version history, release dates, or actual event logs.
"""
from __future__ import annotations

import re
from typing import NamedTuple


# Configuration constants
CONTEXT_WINDOW_CHARS = 80  # Maximum characters to look back for context detection
ISO_DATE_LOOKAHEAD_CHARS = 20  # Characters to look ahead for ISO time component
ISO_DATE_LOOKBACK_CHARS = 50  # Characters to look back for technical markers


class ReplacementRule(NamedTuple):
    """A date replacement rule with pattern and conditions."""

    pattern: str
    replacement: str
    description: str
    preserve_if_preceded_by: list[str] | None = None


# Patterns that indicate a date should be preserved (technical/historical contexts)
PRESERVE_CONTEXTS = [
    r"version\s*:?\s*",
    r"v\d+\.\d+\.\d+\s*\(",  # Version number followed by date in parens
    r"released?\s*:?\s*",
    r"updated?\s*:?\s*",
    r"created?\s*:?\s*",
    r"published?\s*:?\s*",
    r"committed?\s*:?\s*",
    r"timestamp\s*:?\s*",
    r"date\s*:?\s*",
    r"aiohttp\s+\d+\.\d+\.\d+.*released\s+",  # Package version releases
    r"@\d{4}-\d{2}-\d{2}",  # Email-style timestamp
    r"session\s+(date|id|completed?)\s*:?\s*",
    r"\*\*date\*\*\s*:?\s*",  # Markdown bold date labels
    r"\*\*created\*\*\s*:?\s*",
    r"\*\*updated\*\*\s*:?\s*",
    r"\*\*session.*?\*\*\s*:?\s*",
    r"completion\s+date\s*:?\s*",
    r"achievement\s+date\s*:?\s*",
    r"report\s+generated\s*:?\s*",
    r"last\s+updated?\s*:?\s*",
    r"generated\s*:?\s*",
    r"prompt\s+created\s*:?\s*",
]

# Patterns for planning terminology that should be replaced
# Order matters - more specific patterns should come first
PLANNING_PATTERNS = [
    # Phase/Cycle with nested quarter in parentheses (most specific)
    ReplacementRule(
        pattern=r"\((Phase|Cycle)\s+\d+\s*\(Q[1-4]\s*20\d{2}\)\)",
        replacement=r"(\1 [n] (Current Cycle))",
        description="Nested phase/cycle with quarter (e.g., '(Phase 2 (Q2 2026))')",
    ),
    # Phase/Cycle with quarter in parentheses
    ReplacementRule(
        pattern=r"\b(Phase|Cycle)\s+\d+\s*\(Q[1-4]\s*20\d{2}\)",
        replacement=r"\1 [n] (Current Cycle)",
        description="Phase/Cycle with quarter (e.g., 'Phase 2 (Q2 2026)')",
    ),
    # "through" or "by" with quarters
    ReplacementRule(
        pattern=r"\bthrough\s+(Phase|Cycle)\s+\d+\s+Q[1-4]\s*20\d{2}\b",
        replacement=r"through \1 [n] Current Cycle",
        description="Planning horizons with quarters",
    ),
    ReplacementRule(
        pattern=r"\bby\s+Q[1-4]\s+20\d{2}\b",
        replacement="by Current Cycle Q[n]",
        description="Deadlines with quarters",
    ),
    # Quarter-based planning (general)
    ReplacementRule(
        pattern=r"\bQ[1-4]\s+20\d{2}\b",
        replacement="Current Cycle Q[n]",
        description="Quarter references (e.g., 'Q1 2026' -> 'Current Cycle Q[n]')",
    ),
    # Month names with years
    ReplacementRule(
        pattern=r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+20\d{2}\b",
        replacement="Current Cycle [Month]",
        description="Month names with years in planning contexts",
    ),
]


def _is_preserved_context(text: str, match_start: int) -> bool:
    """
    Check if a date match occurs in a context where it should be preserved.

    Args:
        text: Full text being analyzed
        match_start: Start position of the date match

    Returns:
        True if the date should be preserved, False if it can be sanitized
    """
    # Look at text before the match
    # First, check the immediate context (same line, up to CONTEXT_WINDOW_CHARS back or previous newline)
    line_start = text.rfind('\n', max(0, match_start - CONTEXT_WINDOW_CHARS), match_start)
    if line_start == -1:
        line_start = max(0, match_start - CONTEXT_WINDOW_CHARS)
    else:
        line_start += 1  # Skip the newline itself
    
    preceding_text = text[line_start:match_start]

    # Check if any preservation pattern matches the preceding context on the same line
    for preserve_pattern in PRESERVE_CONTEXTS:
        if re.search(preserve_pattern, preceding_text, re.IGNORECASE):
            return True

    return False


def _is_iso_date(text: str, match_start: int, match_end: int) -> bool:
    """
    Check if a date is in ISO format (YYYY-MM-DD) which should typically be preserved.

    Args:
        text: Full text being analyzed
        match_start: Start position of the match
        match_end: End position of the match

    Returns:
        True if this appears to be an ISO date that should be preserved
    """
    # Extract the matched text
    matched = text[match_start:match_end]

    # ISO date pattern: YYYY-MM-DD
    iso_pattern = r"^\d{4}-\d{2}-\d{2}$"
    if re.match(iso_pattern, matched):
        # Check if it's in a timestamp context (with time component)
        look_ahead = text[match_end : match_end + ISO_DATE_LOOKAHEAD_CHARS]
        if re.match(r"^[T\s]\d{2}:\d{2}", look_ahead):
            return True

        # Check if it's preceded by technical markers
        look_back = text[max(0, match_start - ISO_DATE_LOOKBACK_CHARS) : match_start]
        technical_markers = [
            r"version",
            r"release",
            r"v\d+\.\d+",
            r"aiohttp",
            r"@",
            r"date:",
            r"timestamp",
            r"session",
        ]
        for marker in technical_markers:
            if re.search(marker, look_back, re.IGNORECASE):
                return True

    return False


def sanitize_planning_dates(text: str, preserve_iso_dates: bool = True) -> tuple[str, list[str]]:
    """
    Sanitize planning terminology while preserving technical timestamps.

    Args:
        text: Text to sanitize
        preserve_iso_dates: If True, preserve all ISO-format dates (YYYY-MM-DD)

    Returns:
        Tuple of (sanitized_text, list of replacements made)
    """
    sanitized = text
    replacements_made = []

    for rule in PLANNING_PATTERNS:
        # Find all matches
        matches = list(re.finditer(rule.pattern, sanitized, re.IGNORECASE))

        # Process matches in reverse order to maintain indices
        for match in reversed(matches):
            match_start = match.start()
            match_end = match.end()

            # Check if this match should be preserved
            if _is_preserved_context(sanitized, match_start):
                continue

            # Check if it's an ISO date that should be preserved
            if preserve_iso_dates and _is_iso_date(sanitized, match_start, match_end):
                continue

            # Perform the replacement
            original = match.group(0)
            # If the replacement contains backreferences, use re.sub
            if r"\1" in rule.replacement or r"\2" in rule.replacement:
                new_text = re.sub(rule.pattern, rule.replacement, original, flags=re.IGNORECASE)
            else:
                new_text = rule.replacement

            sanitized = sanitized[:match_start] + new_text + sanitized[match_end:]
            replacements_made.append(f"{rule.description}: '{original}' -> '{new_text}'")

    return sanitized, replacements_made


def main():
    """CLI interface for testing the date sanitizer."""
    import sys

    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = sys.stdin.read()

    sanitized, replacements = sanitize_planning_dates(content)

    if replacements:
        print("# Replacements made:", file=sys.stderr)
        for repl in replacements:
            print(f"  - {repl}", file=sys.stderr)
        print("", file=sys.stderr)

    print(sanitized, end="")


if __name__ == "__main__":
    main()
