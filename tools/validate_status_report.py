#!/usr/bin/env python3
"""
Validate status update reports against the schema.

This script provides basic validation for status update markdown files
to ensure they contain required sections and follow the template structure.

Usage:
    python validate_status_report.py <report_file.md>
    python validate_status_report.py reports/daily/2025-11-02.md
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SUPPORTED_TEMPLATE_VERSIONS = {"v1.1", "v1.2"}
SUPPORTED_TEMPLATE_MAJOR_VERSIONS = {1}
VERSION_REGEX = re.compile(r"^v(?P<major>\d+)(?:\.(?P<minor>\d+))?(?:\.[0-9]+)*$")


COMMON_REQUIRED_SECTIONS = [
    "## Template Version",
    "## 0. Report Metadata",
    "## 1. Executive Summary",
    "## 2. Full Snapshot",
    "### 2.1 Repo Map",
    "### 2.2 Capability Audit",
    "### 2.3 High‑Signal Findings",
    "### 2.4 Tests & Gates Snapshot",
    "### 2.5 Reproducibility Checklist",
    "## 3. Delta From Last Report",
    "## 4. Atomic Patch Diffs",
    "## 5. Automation Data Ingest",
    "## 6. Concise Tokenization Insights",
    "## 7. Secret‑Masking Guidance",
    "## 8. Error Capture Blocks",
    "## 9. Open Questions & Answers",
    "## 10. Decision Log",
    "## 11. Scoring Rubric",
    "## 12. Appendix",
]


VERSION_REQUIRED_SECTIONS: dict[str, list[str]] = {
    "v1.1": [
        "### 2.6 Deferred Items",
    ],
    "v1.2": [
        "### 2.6 Schema Validation Report",
        "### 2.7 Security Input Validation Summary",
        "### 2.8 Audit Integrity Chain",
        "### 2.9 Deferred Items",
    ],
}


def normalise_version_key(version: str | None) -> str:
    """Return the version key used for required sections lookup."""

    if not version:
        return "v1.1"

    lowered = version.lower()
    if lowered in VERSION_REQUIRED_SECTIONS:
        return lowered

    match = VERSION_REGEX.match(version)
    if not match:
        return "v1.1"

    major = match.group("major")
    if major == "1":
        return "v1.2"

    return "v1.1"


def check_required_sections(content: str, version: str | None) -> tuple[list[str], list[str]]:
    """Check if all required sections are present in the report."""

    version_key = normalise_version_key(version)
    required_sections = COMMON_REQUIRED_SECTIONS + VERSION_REQUIRED_SECTIONS.get(
        version_key, VERSION_REQUIRED_SECTIONS["v1.1"]
    )
    
    found = []
    missing = []
    
    for section in required_sections:
        if section in content:
            found.append(section)
        else:
            missing.append(section)
    
    return found, missing


def check_title_format(content: str, is_template: bool = False) -> bool:
    """Check if the title follows the required format."""
    lines = content.split('\n')
    for line in lines[:10]:  # Check first 10 lines
        if line.startswith('# '):
            # For templates, accept the template title
            if is_template and 'Template:' in line and '_codex_' in line:
                return True
            # For reports, require the exact format
            if '📍 `_codex_` : Status Update' in line:
                return True
    return False


def is_supported_template_version(version: str) -> bool:
    """Return True if the template version is recognised by the validator."""

    normalised = version.lower()

    if normalised in SUPPORTED_TEMPLATE_VERSIONS:
        return True

    match = VERSION_REGEX.match(normalised)
    if not match:
        return False

    major = int(match.group("major"))
    return major in SUPPORTED_TEMPLATE_MAJOR_VERSIONS


def check_template_version(content: str) -> tuple[str | None, bool]:
    """Extract the template version and indicate whether it is supported."""

    version_patterns = [
        r"^\s*(?:[-*]\s*)?Template Version Used\s*:\s*(v\d+(?:\.\d+)*)",
        r"^\s*(?:[-*]\s*)?Template\s*:\s*(v\d+(?:\.\d+)*)",
    ]

    # Search both the raw content and a variant with Markdown bold removed so we
    # correctly match headings such as "**Template Version Used**: v1.2".
    search_variants = [content, re.sub(r"\*\*(.*?)\*\*", r"\1", content)]

    for variant in search_variants:
        for pattern in version_patterns:
            match = re.search(pattern, variant, flags=re.IGNORECASE | re.MULTILINE)
            if match:
                version = match.group(1)
                version = version.strip()
                return version, is_supported_template_version(version)

    return None, False


def validate_report(report_path: Path) -> int:
    """Validate a status report file."""
    if not report_path.exists():
        print(f"❌ Error: File not found: {report_path}", file=sys.stderr)
        return 1
    
    content = report_path.read_text(encoding='utf-8')
    is_template = 'template' in report_path.name.lower()
    
    print(f"Validating: {report_path}")
    print("=" * 60)
    
    # Check title format
    has_valid_title = check_title_format(content, is_template=is_template)
    if has_valid_title:
        print("✓ Title format correct")
    else:
        print("✗ Title format incorrect (expected: 📍 `_codex_` : Status Update <date>)")
    
    # Check template version
    version, is_supported = check_template_version(content)
    if version and is_supported:
        print(f"✓ Template version: {version}")
    elif version and not is_supported:
        print(
            f"⚠ Template version detected but not in supported set: {version}. "
            "Update the validator or use a supported template version."
        )
    else:
        print("✗ Template version not found or incorrect")
    
    # Check required sections
    found, missing = check_required_sections(content, version)
    print(f"\n✓ Found {len(found)}/{len(found) + len(missing)} required sections")
    
    if missing:
        print(f"\n✗ Missing sections ({len(missing)}):")
        for section in missing:
            print(f"  - {section}")
    
    # Check for severity/confidence scoring
    has_severity = "Severity:" in content or "Severity (1–5)" in content
    has_confidence = "Confidence:" in content or "Confidence (1–5)" in content
    
    if has_severity and has_confidence:
        print("\n✓ Scoring rubric elements present")
    else:
        print("\n⚠ Warning: Scoring rubric elements may be incomplete")
    
    # Summary
    print("\n" + "=" * 60)
    if not missing and has_valid_title and version and is_supported:
        print("✓ Report validation PASSED")
        return 0
    else:
        print("✗ Report validation FAILED")
        return 1


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate _codex_ status update reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s reports/daily/2025-11-02.md
  %(prog)s --help
        """,
    )
    parser.add_argument(
        "report_file",
        type=Path,
        help="Path to the status report markdown file",
    )
    
    args = parser.parse_args()
    
    return validate_report(args.report_file)


if __name__ == "__main__":
    sys.exit(main())
