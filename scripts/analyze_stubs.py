#!/usr/bin/env python3
"""
Analyze Stubs

Purpose:
    Simple stub scanner for generating stub analysis report.

Usage:
    python scripts/analyze_stubs.py [options]

    Examples:
    $ python scripts/analyze_stubs.py --help

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

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def scan_for_stubs(source_dirs):
    """Scan source directories for stubs."""
    stubs = []

    for source_dir in source_dirs:
        if not source_dir.exists():
            continue

        for py_file in source_dir.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                lines = content.split("\n")

                for i, line in enumerate(lines, start=1):
                    line_lower = line.lower()

                    # Check for TODO
                    if "todo" in line_lower and "#" in line:
                        priority = (
                            "P0"
                            if "p0" in line_lower or "critical" in line_lower
                            else "P1" if "p1" in line_lower or "high" in line_lower else "P2"
                        )
                        message = line.split("#", 1)[1].strip()
                        stubs.append((py_file, i, "TODO", message, priority))

                    # Check for FIXME
                    if "fixme" in line_lower and "#" in line:
                        priority = (
                            "P0"
                            if "p0" in line_lower or "critical" in line_lower
                            else "P1"
                        )
                        message = line.split("#", 1)[1].strip()
                        stubs.append((py_file, i, "FIXME", message, priority))

                    # Check for NotImplementedError
                    if "notimplementederror" in line_lower:
                        if "(" in line and ")" in line:
                            message_part = line.split("(", 1)[1].rsplit(")", 1)[0]
                            message = message_part.strip("\"'")
                        else:
                            message = "NotImplementedError"
                        stubs.append((py_file, i, "NotImplementedError", message, "P0"))

            except Exception as e:
                error_type = type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                print(f"Warning: Failed to scan {py_file}: <ERROR_TYPE>")

    return stubs


def generate_report(stubs, output_path):
    """Generate markdown report."""
    # Count by priority
    p0_count = sum(1 for s in stubs if s[4] == "P0")
    p1_count = sum(1 for s in stubs if s[4] == "P1")
    p2_count = sum(1 for s in stubs if s[4] == "P2")

    # Count by type
    todo_count = sum(1 for s in stubs if s[2] == "TODO")
    fixme_count = sum(1 for s in stubs if s[2] == "FIXME")
    notimpl_count = sum(1 for s in stubs if s[2] == "NotImplementedError")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        f.write("# Stub Analysis Report\n\n")
        f.write(f"**Total Stubs**: {len(stubs)}\n\n")

        f.write("## Summary by Priority\n\n")
        f.write(f"- **P0**: {p0_count}\n")
        f.write(f"- **P1**: {p1_count}\n")
        f.write(f"- **P2**: {p2_count}\n")

        f.write("\n## Summary by Type\n\n")
        f.write(f"- **NotImplementedError**: {notimpl_count}\n")
        f.write(f"- **FIXME**: {fixme_count}\n")
        f.write(f"- **TODO**: {todo_count}\n")

        f.write("\n## Detailed List\n\n")

        # Sort by priority
        priority_order = {"P0": 0, "P1": 1, "P2": 2}
        sorted_stubs = sorted(stubs, key=lambda s: (priority_order[s[4]], str(s[0]), s[1]))

        for priority in ["P0", "P1", "P2"]:
            priority_stubs = [s for s in sorted_stubs if s[4] == priority]
            if not priority_stubs:
                continue

            f.write(f"\n### {priority} Priority ({len(priority_stubs)} items)\n\n")

            for file_path, line_num, stub_type, message, _ in priority_stubs:
                f.write(f"**{file_path}:{line_num}** [{stub_type}]\n")
                f.write(f"- Message: {message}\n\n")

    print("\n✓ Stub analysis complete:")
    print(f"  Total stubs: {len(stubs)}")
    print(f"  P0: {p0_count}")
    print(f"  P1: {p1_count}")
    print(f"  P2: {p2_count}")
    print(f"  Report: {output_path}")


if __name__ == "__main__":
    source_dirs = [Path("src"), Path("training")]
    stubs = scan_for_stubs(source_dirs)
    generate_report(stubs, Path(".codex/reports/stub_analysis.md"))
