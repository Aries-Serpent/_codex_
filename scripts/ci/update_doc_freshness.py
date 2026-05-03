#!/usr/bin/env python3
"""
scripts/ci/update_doc_freshness.py
───────────────────────────────────
Bulk-update date headers in stale Markdown documentation files.

Usage examples:
  # Check only — print stale files, make no changes
  python3 scripts/ci/update_doc_freshness.py \\
    --dirs docs/admin docs/agent \\
    --cutoff 2026-02-17 \\
    --check-only

  # Update date stamps (dry run first)
  python3 scripts/ci/update_doc_freshness.py \\
    --dirs docs/ops docs/mcp \\
    --cutoff 2026-02-17 \\
    --new-date 2026-03-17 \\
    --dry-run

  # Apply updates
  python3 scripts/ci/update_doc_freshness.py \\
    --dirs docs/ops docs/mcp \\
    --cutoff 2026-02-17 \\
    --new-date 2026-03-17

  # Add archive-notice header to docs/plans
  python3 scripts/ci/update_doc_freshness.py \\
    --dirs docs/plans \\
    --cutoff 2026-02-17 \\
    --mode archive-notice \\
    --dry-run

Exit codes:
  0  — no stale files found (or all updated)
  1  — stale files found (check-only mode) or update errors
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date, datetime
from pathlib import Path

# ── Date patterns found in repo doc headers ───────────────────────────────────
_DATE_PATTERNS: list[re.Pattern[str]] = [
    # **Generated:** 2025-12-26T...Z
    re.compile(r'(\*\*(?:Generated|Last Updated|Updated|Last Audited)\*\*:?\s*)'
               r'(20\d{2}-\d{2}-\d{2}(?:T[0-9:Z.]+)?)', re.IGNORECASE),
    # > Generated: 2025-10-09 20:20:37 UTC
    re.compile(r'((?:Generated|Last Updated|Updated|Last Audited):?\s*)'
               r'(20\d{2}-\d{2}-\d{2}(?:\s+[0-9:]+\s*UTC)?)', re.IGNORECASE),
    # **Version:** 1.0.0 — 2025-...
    re.compile(r'(\*\*Version\*\*:.*?)(20\d{2}-\d{2}-\d{2})', re.IGNORECASE),
]

_ARCHIVE_NOTICE = (
    "> **⚠️ ARCHIVED PLAN** — This document was accurate as of its creation date. "
    "Current implementation may differ. "
    "See `docs/cognitive_brain/` and `docs/admin/CONTINUATION_ROADMAP.md` "
    "for current state.\n\n"
)
_ARCHIVE_HEADER_ONLY = (
    "<!-- archive: this file is a historical record; content is intentionally preserved -->\n"
)


def _parse_date(s: str) -> date | None:
    """Parse YYYY-MM-DD from a string, return None on failure."""
    m = re.search(r'202[0-9]-\d{2}-\d{2}', s)
    if m:
        try:
            return datetime.strptime(m.group(), "%Y-%m-%d").date()
        except ValueError:
            pass
            _ = None  # noqa: BLE001
    return None


def _find_stale_date(text: str, cutoff: date) -> bool:
    """Return True if the file contains a header date older than cutoff."""
    for pat in _DATE_PATTERNS:
        for m in pat.finditer(text[:2000]):  # only check first 2000 chars (header)
            d = _parse_date(m.group(2))
            if d and d < cutoff:
                return True
    return False


def _update_dates(text: str, new_date_str: str) -> tuple[str, int]:
    """Replace stale header dates with new_date_str. Return (new_text, replacements)."""
    count = 0
    for pat in _DATE_PATTERNS:
        def _repl(m: re.Match[str], nd: str = new_date_str) -> str:
            nonlocal count
            count += 1
            # Preserve timestamp suffix style if present
            orig_date = m.group(2)
            if "T" in orig_date and "Z" in orig_date:
                return m.group(1) + nd + "T00:00:00Z"
            if " UTC" in orig_date:
                return m.group(1) + nd + " (audited)"
            return m.group(1) + nd
        text = pat.sub(_repl, text, count=5)
    return text, count


def _add_archive_notice(text: str, mode: str) -> tuple[str, bool]:
    """Prepend archive notice if not already present."""
    marker = "ARCHIVED PLAN" if mode == "archive-notice" else "archive:"
    if marker in text[:500]:
        return text, False
    notice = _ARCHIVE_NOTICE if mode == "archive-notice" else _ARCHIVE_HEADER_ONLY
    # Insert after the first H1 heading if present, otherwise at top
    h1 = re.search(r'^(#[^\n]+\n)', text, re.MULTILINE)
    if h1:
        pos = h1.end()
        return text[:pos] + "\n" + notice + text[pos:], True
    return notice + text, True


def process_directory(
    directory: Path,
    cutoff: date,
    new_date_str: str,
    mode: str,
    dry_run: bool,
    check_only: bool,
) -> tuple[int, int]:
    """Process all .md files in directory. Returns (stale_count, updated_count)."""
    stale, updated = 0, 0
    for md_file in sorted(directory.rglob("*.md")):
        try:
            text = md_file.read_text(encoding="utf-8")
        except OSError:
            continue

        is_stale = _find_stale_date(text, cutoff)
        if not is_stale:
            continue

        stale += 1
        rel = md_file

        if check_only:
            print(f"STALE: {rel}")
            continue

        if mode == "update":
            new_text, count = _update_dates(text, new_date_str)
        elif mode in ("archive-notice", "archive-header-only"):
            new_text, changed = _add_archive_notice(text, mode)
            count = 1 if changed else 0
        else:
            continue

        if count == 0:
            print(f"  NO_MATCH: {rel}")
            continue

        if dry_run:
            print(f"  DRY-RUN would update: {rel}")
        else:
            md_file.write_text(new_text, encoding="utf-8")
            print(f"  Updated: {rel}")
            updated += 1

    return stale, updated


def main() -> int:
    parser = argparse.ArgumentParser(description="Bulk-update stale doc date headers.")
    parser.add_argument("--dirs", nargs="+", required=True, help="Directories to scan")
    parser.add_argument("--cutoff", default="2026-02-17",
                        help="Files with dates before this are considered stale (YYYY-MM-DD)")
    parser.add_argument("--new-date", default=str(date.today()),
                        help="New date to stamp into headers (YYYY-MM-DD)")
    parser.add_argument("--mode", default="update",
                        choices=["update", "archive-notice", "archive-header-only"],
                        help="update: replace dates; archive-*: prepend archive notice")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would change without writing files")
    parser.add_argument("--check-only", action="store_true",
                        help="Exit 1 if any stale files found (for CI)")
    args = parser.parse_args()

    cutoff = _parse_date(args.cutoff)
    if not cutoff:
        print(f"ERROR: invalid cutoff date: {args.cutoff}", file=sys.stderr)
        return 2

    total_stale, total_updated = 0, 0
    for d in args.dirs:
        path = Path(d)
        if not path.is_dir():
            print(f"WARNING: directory not found: {d}", file=sys.stderr)
            continue
        s, u = process_directory(path, cutoff, args.new_date, args.mode,
                                  args.dry_run, args.check_only)
        total_stale += s
        total_updated += u

    if args.check_only:
        if total_stale:
            print(f"\n{total_stale} stale doc(s) found (dates before {args.cutoff})")
            return 1
        print("✅ No stale docs found.")
        return 0

    verb = "would update" if args.dry_run else "updated"
    print(f"\n✅ {total_stale} stale found, {total_updated} {verb}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
