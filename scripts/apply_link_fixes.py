#!/usr/bin/env python3
"""Auto-fix broken documentation links with suggestions."""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

REPORT_FILE = Path.cwd() / ".codex" / "phase6_link_audit_complete.json"


def apply_fixes_from_suggestions() -> Dict[str, Any]:
    """Apply fixes to files based on suggestions."""
    if not REPORT_FILE.exists():
        print(f"Report not found: {REPORT_FILE}")
        return {}

    with open(REPORT_FILE, "r", encoding="utf-8") as f:
        report = json.load(f)

    fixed_count = 0
    file_changes: Dict[Path, List[str]] = {}

    for issue in report.get("medium_confidence_issues", []):
        if issue["confidence"] < 0.8:
            continue

        suggestions = issue.get("suggestions", [])
        if not suggestions:
            continue

        file_path = Path(issue["file"])
        old_url = issue["url"]
        best_suggestion = suggestions[0]

        if best_suggestion == old_url:
            continue

        if not file_path.exists():
            continue

        try:
            content = file_path.read_text(encoding="utf-8")

            pattern = f"]({old_url})"
            if pattern not in content:
                continue

            new_content = content.replace(pattern, f"]({best_suggestion})")

            if file_path not in file_changes:
                file_changes[file_path] = []

            file_changes[file_path].append(
                f"Fixed: {old_url} -> {best_suggestion}"
            )

            file_path.write_text(new_content, encoding="utf-8")
            fixed_count += 1

        except Exception as e:
            print(f"Warning: Failed to fix {file_path}: {e}")

    return {"fixed_count": fixed_count, "file_changes": file_changes}


def main() -> int:
    """Main entry point."""
    print("Applying high-confidence fixes from suggestions...")
    results = apply_fixes_from_suggestions()
    fixed_count = results.get("fixed_count", 0)
    print(f"Applied {fixed_count} fixes")

    if fixed_count > 0:
        print("\nFixed files:")
        for file_path, changes in results.get("file_changes", {}).items():
            print(f"  {file_path}:")
            for change in changes[:3]:
                print(f"    - {change}")
            if len(changes) > 3:
                print(f"    ... and {len(changes) - 3} more")

    return 0


if __name__ == "__main__":
    sys.exit(main())
