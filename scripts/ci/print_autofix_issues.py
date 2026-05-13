"""Print auto-fixable issues from an autofix JSON report.

Used by pre-merge-validation.yml to surface actionable items without
embedding a Python heredoc (which breaks YAML block-scalar parsing).
"""

import argparse
import json
import os
import sys
import tempfile

DEFAULT_REPORT_PATH = os.path.join(tempfile.gettempdir(), "autofix_report.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Print auto-fixable issues from a report")
    parser.add_argument(
        "report",
        nargs="?",
        default=DEFAULT_REPORT_PATH,
        help="Path to the autofix JSON report (default: %(default)s)",
    )
    args = parser.parse_args()

    try:
        with open(args.report, encoding="utf-8") as f:
            report = json.load(f)
    except FileNotFoundError:
        print(f"Report not found: {args.report}")
        sys.exit(0)
    except json.JSONDecodeError as exc:
        print(f"Failed to parse {args.report}: {exc}")
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
