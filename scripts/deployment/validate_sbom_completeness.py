#!/usr/bin/env python3
"""
SBOM Completeness Validation Script

Purpose:
    Validate SBOM files for completeness, accuracy, and compliance with standards.

Usage:
    python scripts/deployment/validate_sbom_completeness.py [sbom_files...] [options]

Arguments:
    sbom_files: Path(s) to SBOM file(s) to validate

Exit Codes:
    0: All SBOMs valid
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

__all__ = ["validate_sbom", "main"]


def validate_sbom(file_path: Path | str) -> dict[str, Any]:
    """Validate a single SBOM file.

    Args:
        file_path: Path to SBOM file

    Returns:
        Validation result dictionary
    """
    file_path = Path(file_path)

    result = {
        "valid": True,
        "file": str(file_path),
        "errors": [],
        "warnings": [],
        "format": "unknown",
        "component_count": 0,
        "has_duplicates": False,
        "version_info": None,
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

    # Detect format
    if file_path.suffix.lower() == ".json":
        try:
            data = json.loads(content)
            result["format"] = "JSON"

            # Validate CycloneDX structure
            if "bomFormat" in data and data["bomFormat"] == "CycloneDX":
                result["format"] = "CycloneDX JSON"
                result["version_info"] = data.get("specVersion", "unknown")

                # Count components
                components = data.get("components", [])
                result["component_count"] = len(components)

                if result["component_count"] == 0:
                    result["warnings"].append("No components found in SBOM")

                # Check for duplicates
                component_names = [c.get("name") for c in components]
                if len(component_names) != len(set(component_names)):
                    result["has_duplicates"] = True
                    result["warnings"].append("Duplicate components detected")

                # Validate component structure
                for i, comp in enumerate(components):
                    if "name" not in comp:
                        result["errors"].append(
                            f"Component {i} missing required field: name"
                        )
                    if "version" not in comp:
                        result["warnings"].append(
                            f"Component {i} ({comp.get('name')}) missing version"
                        )

                # Check for metadata
                if "metadata" not in data:
                    result["warnings"].append("Missing metadata section")

            elif "packages" in data:
                result["format"] = "SPDX JSON"
                result["component_count"] = len(data.get("packages", []))

            else:
                result["warnings"].append("Unknown JSON SBOM format")

        except json.JSONDecodeError as e:
            result["valid"] = False
            result["errors"].append(f"Invalid JSON: {e}")

    elif file_path.suffix.lower() in [".txt", ".text"]:
        result["format"] = "Text"
        # Count lines as components (rough estimate)
        lines = content.strip().split("\n")
        result["component_count"] = max(0, len(lines) - 5)  # Subtract header lines

    else:
        result["warnings"].append(f"Unknown file format: {file_path.suffix}")

    # Final validation
    if result["errors"]:
        result["valid"] = False

    return result


def validate_multiple_sboms(file_paths: list[Path | str]) -> dict[str, Any]:
    """Validate multiple SBOM files.

    Args:
        file_paths: List of paths to SBOM files

    Returns:
        Aggregated validation result
    """
    results = {
        "total": len(file_paths),
        "valid": 0,
        "invalid": 0,
        "warnings": 0,
        "total_components": 0,
        "details": [],
    }

    for file_path in file_paths:
        result = validate_sbom(file_path)
        results["details"].append(result)

        if result["valid"]:
            results["valid"] += 1
        else:
            results["invalid"] += 1

        if result["warnings"]:
            results["warnings"] += len(result["warnings"])

        results["total_components"] += result["component_count"]

    return results


def print_validation_report(result: dict[str, Any]) -> None:
    """Print validation report.

    Args:
        result: Validation result dictionary
    """
    print(f"\n{'='*60}")
    print("SBOM VALIDATION REPORT")
    print(f"{'='*60}\n")

    if "total" in result:
        # Multiple SBOMs
        print(f"Total Files: {result['total']}")
        print(f"Valid: {result['valid']} | Invalid: {result['invalid']}")
        print(f"Total Components: {result['total_components']}")
        print(f"Warnings: {result['warnings']}\n")

        for detail in result["details"]:
            status = "✅" if detail["valid"] else "❌"
            print(f"{status} {detail['file']}")
            print(f"   Format: {detail['format']}")
            print(f"   Components: {detail['component_count']}")

            if detail["errors"]:
                for error in detail["errors"]:
                    print(f"   ❌ {error}")

            if detail["warnings"]:
                for warning in detail["warnings"]:
                    print(f"   ⚠️ {warning}")

    else:
        # Single SBOM
        print(f"File: {result['file']}")
        print(f"Status: {'✅ VALID' if result['valid'] else '❌ INVALID'}")
        print(f"Format: {result['format']}")
        print(f"Components: {result['component_count']}")
        print(f"Version: {result['version_info'] or 'N/A'}\n")

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

    print(f"{'='*60}\n")


def main(argv: list[str] | None = None) -> int:
    """Main entry point.

    Args:
        argv: Command line arguments

    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description="Validate SBOM file completeness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate single SBOM
  python scripts/deployment/validate_sbom_completeness.py sbom.json

  # Validate multiple SBOMs
  python scripts/deployment/validate_sbom_completeness.py sbom-*.json

  # Output as JSON
  python scripts/deployment/validate_sbom_completeness.py sbom.json --json
""",
    )

    parser.add_argument("files", nargs="+", type=Path, help="Path(s) to SBOM file(s)")
    parser.add_argument(
        "--json", action="store_true", help="Output validation result as JSON"
    )

    args = parser.parse_args(argv)

    try:
        if len(args.files) == 1:
            result = validate_sbom(args.files[0])
        else:
            result = validate_multiple_sboms(args.files)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_validation_report(result)

        # Determine exit code
        if "total" in result:
            return 0 if result["invalid"] == 0 else 1
        else:
            return 0 if result["valid"] else 1

    except Exception as e:
        logger.error(f"Error validating SBOM: {e}")
        print(f"❌ Validation failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
