#!/usr/bin/env python3
"""
CI Failure Tracking Log Helper

Script to help add entries to .codex/CI_FAILURE_TRACKING_LOG.md

Usage:
    python scripts/ci/log_failure.py --issue 3248 --symptom "Worker crashes" --fix "Added plugin flags"
    python scripts/ci/log_failure.py --interactive
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path


def get_repo_root() -> Path:
    """Find repository root by looking for .git directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    raise RuntimeError("Not in a git repository")


def get_log_file_path() -> Path:
    """Get path to CI failure tracking log."""
    return get_repo_root() / ".codex" / "CI_FAILURE_TRACKING_LOG.md"


def format_entry(
    date: str,
    title: str,
    pr_issue: str,
    workflows: str,
    symptom: str,
    root_cause: str,
    fix_applied: str,
    commit: str,
    prevention: str,
    recurrence: str,
    status: str = "RESOLVED"
) -> str:
    """Format a log entry."""
    return f"""
### [{date}] {title}
- **PR/Issue**: {pr_issue}
- **Affected Workflows**: {workflows}
- **Symptom**:
  ```
  {symptom}
  ```
- **Root Cause**: {root_cause}
- **Fix Applied**: {fix_applied}
- **Commit**: {commit}
- **Prevention**: {prevention}
- **Recurrence**: {recurrence}
- **Status**: {status}
"""


def interactive_mode() -> dict:
    """Interactive mode to collect failure details."""
    print("=== CI Failure Tracking Log Entry ===\n")

    data = {}
    data["date"] = input(f"Date (default: {datetime.now().strftime('%Y-%m-%d')}): ").strip()
    if not data["date"]:
        data["date"] = datetime.now().strftime('%Y-%m-%d')

    data["title"] = input("Issue Title: ").strip()
    data["pr_issue"] = input("PR/Issue Number (e.g., #3248): ").strip()
    data["workflows"] = input("Affected Workflows: ").strip()

    print("\nSymptom (enter multi-line, end with empty line):")
    symptom_lines = []
    while True:
        line = input()
        if not line:
            break
        symptom_lines.append(line)
    data["symptom"] = "\n  ".join(symptom_lines)

    data["root_cause"] = input("\nRoot Cause: ").strip()
    data["fix_applied"] = input("Fix Applied: ").strip()
    data["commit"] = input("Commit Hash: ").strip()
    data["prevention"] = input("Prevention Strategy: ").strip()
    data["recurrence"] = input("Recurrence (e.g., 'First occurrence', '3rd occurrence'): ").strip()
    data["status"] = input("Status (default: RESOLVED): ").strip() or "RESOLVED"

    return data


def add_entry_to_log(entry: str, resolved: bool = True) -> None:
    """Add entry to the log file."""
    log_file = get_log_file_path()

    if not log_file.exists():
        print(f"Error: Log file not found at {log_file}")
        sys.exit(1)

    content = log_file.read_text()

    # Find the appropriate section
    section_marker = "## Resolved Issues" if resolved else "## Active Issues (Unresolved)"

    # Find insertion point (after section header)
    section_start = content.find(section_marker)
    if section_start == -1:
        print(f"Error: Could not find section '{section_marker}' in log file")
        sys.exit(1)

    # Find next line after section header
    insertion_point = content.find("\n", section_start) + 1

    # Insert the entry
    new_content = content[:insertion_point] + entry + content[insertion_point:]

    # Write back
    log_file.write_text(new_content)
    print(f"\n✅ Entry added to {log_file}")
    print(f"   Section: {'Resolved Issues' if resolved else 'Active Issues'}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Add entry to CI failure tracking log")
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Interactive mode to collect all details")
    parser.add_argument("--issue", help="PR/Issue number")
    parser.add_argument("--title", help="Issue title")
    parser.add_argument("--workflows", help="Affected workflows")
    parser.add_argument("--symptom", help="Symptom description")
    parser.add_argument("--root-cause", help="Root cause explanation")
    parser.add_argument("--fix", help="Fix applied")
    parser.add_argument("--commit", help="Commit hash")
    parser.add_argument("--prevention", help="Prevention strategy")
    parser.add_argument("--recurrence", default="First occurrence", help="Recurrence info")
    parser.add_argument("--active", action="store_true", help="Add to Active Issues (not Resolved)")
    parser.add_argument("--date", help="Date (YYYY-MM-DD)")

    args = parser.parse_args()

    if args.interactive:
        data = interactive_mode()
        entry = format_entry(**data)
        add_entry_to_log(entry, resolved=(data["status"] == "RESOLVED"))
    elif args.issue and args.title and args.symptom and args.fix:
        data = {
            "date": args.date or datetime.now().strftime('%Y-%m-%d'),
            "title": args.title,
            "pr_issue": args.issue,
            "workflows": args.workflows or "Unknown",
            "symptom": args.symptom,
            "root_cause": args.root_cause or "To be determined",
            "fix_applied": args.fix,
            "commit": args.commit or "Pending",
            "prevention": args.prevention or "To be determined",
            "recurrence": args.recurrence,
        }
        entry = format_entry(**data)
        add_entry_to_log(entry, resolved=not args.active)
    else:
        parser.print_help()
        print("\nExample:")
        print('  python scripts/ci/log_failure.py --issue "#3248" --title "Worker Crashes" \\')
        print('    --symptom "maximum crashed workers reached" --fix "Added plugin flags" \\')
        print('    --commit "17702636"')
        sys.exit(1)


if __name__ == "__main__":
    main()
