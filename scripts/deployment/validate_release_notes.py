#!/usr/bin/env python3
"""
Release Notes Validation Script

Purpose:
    Validate release notes for completeness and GitHub API compliance.

Usage:
    python scripts/deployment/validate_release_notes.py [file] [options]

Arguments:
    file: Path to release notes file to validate

Exit Codes:
    0: Valid
    1: Validation failed

Author: Codex Team
Last Updated: 2026-06-20
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["validate_release_notes", "main"]

# GitHub release body size limit (65536 bytes)
GITHUB_RELEASE_SIZE_LIMIT = 65536


def validate_release_notes(file_path: Path | str) -> dict[str, Any]:
    """Validate release notes file for completeness and compliance.

    Args:
        file_path: Path to release notes file

    Returns:
        Validation result dictionary
    """
    file_path = Path(file_path)

    result = {
        "valid": True,
        "file": str(file_path),
        "errors": [],
        "warnings": [],
        "size_bytes": 0,
        "sections_found": [],
        "required_sections_present": [],
        "missing_sections": [],
    }

    # Check file exists
    if not file_path.exists():
        result["valid"] = False
        result["errors"].append(f"File not found: {file_path}")
        return result

    # Read file
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        result["valid"] = False
        result["errors"].append(f"Error reading file: {e}")
        return result

    # Check size
    result["size_bytes"] = len(content.encode("utf-8"))
    if result["size_bytes"] > GITHUB_RELEASE_SIZE_LIMIT:
        result["valid"] = False
        result["errors"].append(
            f"Release notes too large: {result['size_bytes']} > {GITHUB_RELEASE_SIZE_LIMIT} bytes"
        )

    # Check for required sections
    required_sections = [
        "Release",
        "Features",
        "Fixes",
        "Security",
        "Assets",
        "Verification",
        "Installation",
    ]

    optional_sections = [
        "Breaking Changes",
        "Known Issues",
        "Upgrade Guide",
    ]

    for section in required_sections + optional_sections:
        if section in content or section.lower() in content.lower():
            result["sections_found"].append(section)

    # Check for required sections
    for section in required_sections:
        found = False
        for found_section in result["sections_found"]:
            if section.lower() in found_section.lower():
                result["required_sections_present"].append(section)
                found = True
                break
        if not found:
            result["missing_sections"].append(section)

    if result["missing_sections"]:
        result["warnings"].append(
            f"Missing recommended sections: {', '.join(result['missing_sections'])}"
        )

    # Check for version info
    if not any(x in content for x in ["Release", "Version", "v0.", "v1.", "[0.", "[1."]):
        result["warnings"].append("No version information detected")

    # Check for date
    if not any(x in content for x in ["Date:", "date:", "2026-", "2025-"]):
        result["warnings"].append("No date information detected")

    # Check for download/installation instructions
    if "pip" not in content.lower() and "docker" not in content.lower():
        result["warnings"].append("No installation instructions found")

    # Check for metadata
    has_version = "version" in content.lower() or "release" in content.lower()
    has_date = any(x in content for x in ["Date:", "date:", "-"]) and (
        "2026" in content or "2025" in content
    )
    has_author = "author" in content.lower() or "contributors" in content.lower()

    result["metadata"] = {
        "has_version": has_version,
        "has_date": has_date,
        "has_author": has_author,
    }

    # Final validation
    if result["errors"]:
        result["valid"] = False

    return result


def print_validation_report(result: dict[str, Any]) -> None:
    """Print validation report in human-readable format.

    Args:
        result: Validation result dictionary
    """
    print(f"\n{'='*60}")
    print("RELEASE NOTES VALIDATION REPORT")
    print(f"{'='*60}\n")

    print(f"File: {result['file']}")
    print(f"Size: {result['size_bytes']} / {GITHUB_RELEASE_SIZE_LIMIT} bytes")
    print(f"Status: {'✅ VALID' if result['valid'] else '❌ INVALID'}\n")

    if result["errors"]:
        print("❌ ERRORS:")
        for error in result["errors"]:
            print(f"  - {error}")
        print()

    if result["warnings"]:
        print("⚠️ WARNINGS:")
        for warning in result["warnings"]:
            print(f"  - {warning}")
        print()

    if result["sections_found"]:
        print(f"✅ SECTIONS FOUND ({len(result['sections_found'])}):")
        for section in result["sections_found"]:
            print(f"  - {section}")
        print()

    print("📋 METADATA:")
    for key, value in result["metadata"].items():
        status = "✅" if value else "❌"
        print(f"  {status} {key.replace('_', ' ')}: {value}")
    print()

    if result["missing_sections"]:
        print(f"⚠️ MISSING SECTIONS ({len(result['missing_sections'])}):")
        for section in result["missing_sections"]:
            print(f"  - {section}")
        print()

    print(f"{'='*60}\n")

    # Return appropriate exit code
    return 0 if result["valid"] else 1


def main(argv: list[str] | None = None) -> int:
    """Main entry point.

    Args:
        argv: Command line arguments

    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description="Validate release notes file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate release notes
  python scripts/deployment/validate_release_notes.py .codex/release-notes.md

  # Output as JSON
  python scripts/deployment/validate_release_notes.py .codex/release-notes.md --json
""",
    )

    parser.add_argument("file", type=Path, help="Path to release notes file")
    parser.add_argument(
        "--json", action="store_true", help="Output validation result as JSON"
    )

    args = parser.parse_args(argv)

    try:
        result = validate_release_notes(args.file)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_validation_report(result)

        return 0 if result["valid"] else 1
    except Exception as e:
        logger.error(f"Error validating release notes: {e}")
        print(f"❌ Validation failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
