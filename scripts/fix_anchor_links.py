#!/usr/bin/env python3
"""Fix broken anchor links in documentation."""

import json
import re
import sys
from pathlib import Path
from typing import Dict

REPORT_FILE = Path.cwd() / ".codex" / "phase6_link_audit_complete.json"


def extract_headings(content: str) -> Dict[str, str]:
    """Extract all headings and their normalized anchors."""
    headings = {}
    heading_pattern = r"^#{1,6}\s+(.+?)(?:\s*\{.*\})?\s*$"
    for line in content.split("\n"):
        match = re.match(heading_pattern, line, re.MULTILINE)
        if match:
            heading = match.group(1).strip()
            # Normalize the heading to an anchor
            anchor = heading.lower()
            anchor = re.sub(r"[^\w\s-]", "", anchor)
            anchor = re.sub(r"[-\s]+", "-", anchor)
            anchor = anchor.strip("-")
            headings[anchor] = heading
    return headings


def find_closest_anchor(target: str, available: Dict[str, str]) -> str:
    """Find the closest matching anchor."""
    target_lower = target.lower()

    # Exact match
    if target_lower in available:
        return target_lower

    # Partial matches
    matches = []
    for anchor in available:
        # Check if target is contained in anchor
        if target_lower in anchor:
            matches.append((len(anchor), anchor))
        # Check if anchor is contained in target
        elif anchor in target_lower:
            matches.append((len(anchor), anchor))

    if matches:
        return sorted(matches)[0][1]

    return ""


def fix_broken_anchors() -> Dict[str, int]:
    """Fix broken anchor links."""
    if not REPORT_FILE.exists():
        print(f"Report not found: {REPORT_FILE}")
        return {}

    with open(REPORT_FILE, "r", encoding="utf-8") as f:
        report = json.load(f)

    fixed_count = 0
    skipped_count = 0

    for issue in report.get("low_confidence_issues", []):
        # Only process anchor issues
        if "anchor" not in issue["error"].lower():
            continue

        file_path = Path(issue["file"])
        old_url = issue["url"]

        if not file_path.exists():
            continue

        # Extract the anchor from the URL
        if "#" not in old_url:
            continue

        file_part, anchor_part = old_url.rsplit("#", 1)

        # If file_part is empty, it's an anchor in the same file
        if not file_part:
            target_file = file_path
        else:
            target_file = file_path.parent / file_part
            if not target_file.exists():
                continue

        try:
            content = target_file.read_text(encoding="utf-8")
            headings = extract_headings(content)

            if not headings:
                continue

            # Try to find the best matching anchor
            best_anchor = find_closest_anchor(anchor_part, headings)

            if not best_anchor or best_anchor == anchor_part:
                skipped_count += 1
                continue

            # Fix the link in the source file
            source_file = Path(issue["file"])
            source_content = source_file.read_text(encoding="utf-8")

            old_pattern = f"]({re.escape(old_url)})"
            new_url = f"{file_part}#{best_anchor}" if file_part else f"#{best_anchor}"
            new_pattern = f"]({new_url})"

            if old_pattern in source_content:
                new_content = source_content.replace(old_pattern, new_pattern)
                source_file.write_text(new_content, encoding="utf-8")
                fixed_count += 1

        except Exception:
            pass

    return {"fixed": fixed_count, "skipped": skipped_count}


def main() -> int:
    """Main entry point."""
    print("Fixing broken anchor links...")
    results = fix_broken_anchors()
    print(f"Fixed: {results.get('fixed', 0)}")
    print(f"Skipped: {results.get('skipped', 0)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
