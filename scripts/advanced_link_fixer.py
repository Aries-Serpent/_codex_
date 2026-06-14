#!/usr/bin/env python3
"""Advanced link fixer for documentation."""

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

REPORT_FILE = Path.cwd() / ".codex" / "phase6_link_audit_complete.json"


def find_file_by_name(target_name: str) -> List[Path]:
    """Find files by name pattern."""
    results = []
    target_lower = target_name.lower()

    for md_file in Path(".").rglob("*.md"):
        if md_file.name.lower() == target_lower:
            results.append(md_file)
        elif md_file.name.lower().endswith(target_lower):
            results.append(md_file)

    return results


def extract_filename(broken_url: str) -> str:
    """Extract filename from a broken URL."""
    return Path(broken_url).name.split("#")[0]


def fix_by_filename_matching(
    file_path: Path, old_url: str, filename: str
) -> str:
    """Fix by matching filename in repository."""
    matches = find_file_by_name(filename)
    if not matches:
        return ""

    best_match = matches[0]

    try:
        rel_path = best_match.relative_to(file_path.parent)
        return str(rel_path)
    except ValueError:
        try:
            parts = best_match.parts
            source_parts = file_path.parent.parts
            common = 0
            for i, (p, s) in enumerate(zip(parts, source_parts)):
                if p == s:
                    common = i + 1
                else:
                    break

            if common > 0:
                up_count = len(source_parts) - common
                down_parts = parts[common:]
                rel_path = "/".join([".."] * up_count + list(down_parts))
                return rel_path
        except Exception:
            pass

    return ""


def fix_archive_references(file_path: Path, old_url: str) -> str:
    """Fix references to archived files."""
    if ".codex/archive" in old_url or "archive/" in old_url:
        return ""

    if "archive" in str(file_path):
        filename = extract_filename(old_url)
        return fix_by_filename_matching(file_path, old_url, filename)

    return ""


def fix_relative_path_errors(file_path: Path, old_url: str) -> str:
    """Fix relative path errors."""
    if old_url.startswith("/"):
        return old_url[1:]

    if old_url.startswith("./"):
        return old_url[2:]

    return ""


def fix_malformed_urls(old_url: str) -> str:
    """Fix malformed URLs."""
    if old_url.startswith("..") and not old_url.startswith("../../"):
        return old_url

    return ""


def apply_advanced_fixes() -> Dict[str, Any]:
    """Apply advanced fixes."""
    if not REPORT_FILE.exists():
        print(f"Report not found: {REPORT_FILE}")
        return {}

    with open(REPORT_FILE, "r", encoding="utf-8") as f:
        report = json.load(f)

    fixed_count = 0
    fix_details: List[Dict[str, Any]] = []

    for issue in report.get("medium_confidence_issues", []):
        file_path = Path(issue["file"])
        old_url = issue["url"]

        if not file_path.exists():
            continue

        new_url = ""

        new_url = fix_relative_path_errors(file_path, old_url)
        if not new_url:
            new_url = fix_archive_references(file_path, old_url)
        if not new_url:
            filename = extract_filename(old_url)
            new_url = fix_by_filename_matching(file_path, old_url, filename)

        if not new_url or new_url == old_url:
            continue

        try:
            content = file_path.read_text(encoding="utf-8")

            pattern = f"]({re.escape(old_url)})"
            if pattern not in content:
                content_with_quotes = f'"{old_url}"'
                if content_with_quotes in content:
                    content = content.replace(content_with_quotes, f'"{new_url}"')
                else:
                    continue

            else:
                content = content.replace(pattern, f"]({new_url})")

            file_path.write_text(content, encoding="utf-8")
            fixed_count += 1
            fix_details.append(
                {
                    "file": str(file_path),
                    "old_url": old_url,
                    "new_url": new_url,
                    "fix_type": "advanced",
                }
            )

        except Exception as e:
            print(f"Warning: Failed to fix {file_path}: {e}")

    return {"fixed_count": fixed_count, "fixes": fix_details}


def main() -> int:
    """Main entry point."""
    print("Applying advanced link fixes...")
    results = apply_advanced_fixes()
    fixed_count = results.get("fixed_count", 0)
    print(f"Applied {fixed_count} advanced fixes")

    if fixed_count > 0:
        fixes = results.get("fixes", [])
        print("\nSample fixes applied:")
        for fix in fixes[:10]:
            print(f"  {fix['file'].split('/')[-1]}: {fix['old_url']} -> {fix['new_url']}")
        if len(fixes) > 10:
            print(f"  ... and {len(fixes) - 10} more")

    return 0


if __name__ == "__main__":
    sys.exit(main())
