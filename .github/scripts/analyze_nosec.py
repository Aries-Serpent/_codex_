#!/usr/bin/env python3
"""
Comprehensive nosec suppression audit script.
Analyzes all # nosec comments in the codebase and generates a detailed report.
"""
import re
import sys
from collections import defaultdict
from pathlib import Path


def parse_nosec_comments(root_dir: Path) -> dict[str, list[tuple[int, str, str, bool]]]:
    """
    Parse all nosec comments from Python files.

    Returns:
        Dict mapping file paths to list of (line_num, rule_id, justification, has_justification)
    """
    nosec_pattern = re.compile(r'#\s*nosec\s*([B\d,\s]*)(.*)?')
    results = defaultdict(list)

    for py_file in root_dir.rglob('*.py'):
        # Skip certain directories
        if any(exc in str(py_file) for exc in ['.venv', '.git', '__pycache__', 'node_modules']):
            continue

        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                for lineno, line in enumerate(f, 1):
                    if match := nosec_pattern.search(line):
                        rule_ids = match.group(1).strip()
                        justification = match.group(2).strip()
                        has_justification = bool(justification)
                        results[str(py_file.relative_to(root_dir))].append(
                            (lineno, rule_ids or 'all', justification, has_justification)
                        )
        except Exception as e:
            print(f"Error reading {py_file}: {e}", file=sys.stderr)

    return results


def generate_report(nosec_data: dict[str, list[tuple[int, str, str, bool]]]) -> str:
    """Generate comprehensive audit report."""
    total_nosec = sum(len(v) for v in nosec_data.values())
    files_with_nosec = len(nosec_data)

    # Count by justification status
    with_justification = sum(
        1 for items in nosec_data.values()
        for item in items if item[3]
    )
    without_justification = total_nosec - with_justification

    # Count by rule
    rule_counts = defaultdict(int)
    for items in nosec_data.values():
        for _, rule_id, _, _ in items:
            for rule in rule_id.split(','):
                rule_counts[rule.strip()] += 1

    report = []
    report.append("=" * 80)
    report.append("NOSEC SUPPRESSION AUDIT REPORT")
    report.append("=" * 80)
    report.append("")
    report.append("EXECUTIVE SUMMARY")
    report.append("-" * 80)
    report.append(f"Total nosec comments: {total_nosec}")
    report.append(f"Files with nosec: {files_with_nosec}")
    report.append(f"With justification: {with_justification} ({with_justification/total_nosec*100:.1f}%)")
    report.append(f"Without justification: {without_justification} ({without_justification/total_nosec*100:.1f}%)")
    report.append("")

    report.append("SUPPRESSIONS BY RULE")
    report.append("-" * 80)
    for rule, count in sorted(rule_counts.items(), key=lambda x: x[1], reverse=True):
        report.append(f"  {rule:10s}: {count:3d} occurrences")
    report.append("")

    report.append("FILES WITHOUT JUSTIFICATION")
    report.append("-" * 80)
    found_unjustified = False
    for filepath, items in sorted(nosec_data.items()):
        unjustified = [(lineno, rule, just) for lineno, rule, just, has_just in items if not has_just]
        if unjustified:
            found_unjustified = True
            report.append(f"\n{filepath}:")
            for lineno, rule, _ in unjustified:
                report.append(f"  Line {lineno}: Rule {rule} - NO JUSTIFICATION")

    if not found_unjustified:
        report.append("✅ ALL nosec comments have justifications!")
    report.append("")

    report.append("DETAILED INVENTORY (First 50 entries)")
    report.append("-" * 80)
    count = 0
    for filepath, items in sorted(nosec_data.items()):
        for lineno, rule, justification, has_just in items:
            if count >= 50:
                report.append(f"\n... and {total_nosec - 50} more entries")
                break
            status = "✅" if has_just else "❌"
            report.append(f"{status} {filepath}:{lineno}")
            report.append(f"   Rule: {rule}")
            report.append(f"   Justification: {justification if justification else '(NONE)'}")
            report.append("")
            count += 1
        if count >= 50:
            break

    report.append("=" * 80)
    report.append("RECOMMENDATIONS")
    report.append("=" * 80)
    if without_justification > 0:
        report.append(f"⚠️  Found {without_justification} nosec comment(s) without justification")
        report.append("   Action: Add justification comments explaining why suppression is needed")
        report.append("   Format: # nosec B101 - Justification here")
    else:
        report.append("✅ All nosec comments properly justified")

    report.append("")
    justification_rate = (with_justification / total_nosec * 100) if total_nosec > 0 else 0
    report.append(f"Current justification rate: {justification_rate:.1f}%")
    report.append("Target justification rate: 100%")
    report.append("")
    report.append("=" * 80)

    return "\n".join(report)


if __name__ == '__main__':
    root = Path.cwd()
    if len(sys.argv) > 1:
        root = Path(sys.argv[1])

    print(f"Scanning {root} for nosec comments...", file=sys.stderr)
    nosec_data = parse_nosec_comments(root)

    if not nosec_data:
        print("No nosec comments found.", file=sys.stderr)
        sys.exit(0)

    report = generate_report(nosec_data)
    print(report)

    # Exit with error if any unjustified
    total = sum(len(v) for v in nosec_data.values())
    justified = sum(1 for items in nosec_data.values() for item in items if item[3])
    sys.exit(0 if justified == total else 1)
