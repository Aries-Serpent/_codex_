"""Print auto-fixable issues from an autofix JSON report.

Used by pre-merge-validation.yml to surface actionable items without
embedding a Python heredoc (which breaks YAML block-scalar parsing).
"""

import json
import sys

REPORT_PATH = "/tmp/autofix_report.json"


def main() -> None:
    try:
        with open(REPORT_PATH, "r", encoding="utf-8") as f:
            report = json.load(f)
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to read {REPORT_PATH}: {exc}")
        sys.exit(0)

    raw_issues = report.get("issues", []) or []
    issues = [
        item
        for item in raw_issues
        if isinstance(item, dict) and item.get("auto_fix_available")
    ]

    if issues:
        print("Auto-fixable issues:")
        for issue in issues:
            pattern = issue.get("pattern_name", "unknown-pattern")
            file_path = issue.get("file", "unknown-file")
            line = issue.get("line", "?")
            message = issue.get("message", "")
            print(f"  [{pattern}] {file_path}:{line} - {message}")
    else:
        print("Run: python scripts/ci/auto_fix_common_issues.py --check-only for details")


if __name__ == "__main__":
    main()
