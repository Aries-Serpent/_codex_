#!/usr/bin/env python3
"""
Extract validation errors from status update reports and create error files.

This script validates a status report and creates an error-<report_name>.md file
in the same directory containing all the incomplete or incorrect aspects.
"""
import argparse
import sys
from pathlib import Path

# Import validation functions from the existing script
from validate_status_report import (
    _canonicalise_version,
    check_required_sections,
    check_template_version,
    check_title_format,
)


def collect_validation_errors(report_path: Path) -> tuple[bool, list[str]]:
    """Collect all validation errors for a report."""
    errors = []

    if not report_path.exists():
        errors.append(f"File not found: {report_path}")
        return False, errors

    content = report_path.read_text(encoding="utf-8")
    is_template = "template" in report_path.name.lower()

    # Check title format
    has_valid_title = check_title_format(content, is_template=is_template)
    if not has_valid_title:
        errors.append(
            "Title format incorrect - Expected format: 📍 `_codex_` : Status Update <date>"
        )

    # Check template version
    version, is_supported = check_template_version(content)
    canonical_version = _canonicalise_version(version) if version else None

    if not version:
        errors.append("Template version not found in report")
    elif not is_supported:
        errors.append(f"Template version '{version}' is not supported - Must be one of: v1.1, v1.2")

    # Check required sections
    sections_version = canonical_version if is_supported else None
    found, missing = check_required_sections(content, sections_version)

    if missing:
        errors.append(f"Missing {len(missing)} required sections:")
        for section in missing:
            errors.append(f"  - {section}")

    # Check for severity/confidence scoring
    has_severity = "Severity:" in content or "Severity (1–5)" in content
    has_confidence = "Confidence:" in content or "Confidence (1–5)" in content

    if not (has_severity and has_confidence):
        errors.append("Scoring rubric elements incomplete - Missing severity or confidence markers")

    # Validation passes if no errors
    is_valid = len(errors) == 0

    return is_valid, errors


def create_error_file(report_path: Path, errors: list[str]) -> Path:
    """Create error-*.md file in the same directory as the report."""
    # Get directory and filename
    report_dir = report_path.parent
    report_stem = report_path.stem  # filename without .md

    # Create error filename
    error_filename = f"error-{report_stem}.md"
    error_path = report_dir / error_filename

    # Build error file content
    try:
        rel_path = report_path.relative_to(Path.cwd())
    except ValueError:
        rel_path = report_path

    content_lines = [
        f"# Validation Errors: {report_path.name}",
        "",
        "This file contains validation errors and incomplete aspects detected in the status report.",
        "",
        f"**Report Path:** `{rel_path}`",
        "**Schema:** `docs/templates/status/codex_status_template.schema_v1.2.yaml`",
        "**Validator:** `tools/validate_status_report.py`",
        "",
        "---",
        "",
        "## Validation Errors",
        "",
    ]

    if errors:
        error_num = 1
        for error in errors:
            # Check if this is a sub-item (starts with spaces and dash)
            if error.strip().startswith("-"):
                content_lines.append(error)
            else:
                content_lines.append(f"{error_num}. {error}")
                error_num += 1
    else:
        content_lines.append("_No errors found._")

    content_lines.extend(
        [
            "",
            "---",
            "",
            "## Resolution Steps",
            "",
            "To resolve these validation errors:",
            "",
            "1. Review each error listed above",
            "2. Update the report file to include all required sections and fix formatting issues",
            "3. Ensure the report follows the schema at `docs/templates/status/codex_status_template.schema_v1.2.yaml`",
            "4. Re-run validation: `python tools/validate_status_report.py <report_file>`",
            "5. Delete this error file once all issues are resolved",
            "",
            "---",
            "",
            "## Required Sections Checklist",
            "",
            "For template version v1.2, the following sections are required:",
            "",
            "- [ ] ## Template Version",
            "- [ ] ## 0. Report Metadata",
            "- [ ] ## 1. Executive Summary",
            "- [ ] ## 2. Full Snapshot",
            "- [ ] ### 2.1 Repo Map",
            "- [ ] ### 2.2 Capability Audit",
            "- [ ] ### 2.3 High‑Signal Findings",
            "- [ ] ### 2.4 Tests & Gates Snapshot",
            "- [ ] ### 2.5 Reproducibility Checklist",
            "- [ ] ### 2.6 Schema Validation Report",
            "- [ ] ### 2.7 Security Input Validation Summary",
            "- [ ] ### 2.8 Audit Integrity Chain",
            "- [ ] ### 2.9 Deferred Items",
            "- [ ] ## 3. Delta From Last Report",
            "- [ ] ## 4. Atomic Patch Diffs",
            "- [ ] ## 5. Automation Data Ingest",
            "- [ ] ## 6. Concise Tokenization Insights",
            "- [ ] ## 7. Secret‑Masking Guidance",
            "- [ ] ## 8. Error Capture Blocks",
            "- [ ] ## 9. Open Questions & Answers",
            "- [ ] ## 10. Decision Log",
            "- [ ] ## 11. Scoring Rubric",
            "- [ ] ## 12. Appendix",
            "",
        ]
    )

    # Write to file
    error_path.write_text("\n".join(content_lines), encoding="utf-8")

    return error_path


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Extract validation errors from status reports and create error files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "report_file",
        type=Path,
        help="Path to the status report markdown file",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing error file if present",
    )

    args = parser.parse_args()

    # Validate report and collect errors
    print(f"Validating: {args.report_file}")
    is_valid, errors = collect_validation_errors(args.report_file)

    if is_valid:
        print("✅ Validation PASSED - No errors found")
        print("No error file created.")
        return 0

    # Report has errors - create error file
    print(f"❌ Validation FAILED - {len(errors)} error(s) found")

    # Create error file
    error_file = create_error_file(args.report_file, errors)

    print(f"\n📄 Error file created: {error_file}")
    print("\nReview the error file for details on missing/incorrect aspects.")

    return 1


if __name__ == "__main__":
    sys.exit(main())
