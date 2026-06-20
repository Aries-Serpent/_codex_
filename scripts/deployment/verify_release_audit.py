#!/usr/bin/env python3
"""
Verify Release Audit Script

Purpose:
    Verify the integrity and completeness of release audit artifacts.

Usage:
    python scripts/deployment/verify_release_audit.py <audit_file> [options]

Arguments:
    audit_file: Path to audit file to verify

Exit Codes:
    0: Verification successful
    1: Verification failed

Author: Codex Team
Last Updated: 2026-06-20
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["verify_release_audit", "main"]


def verify_release_audit(audit_file: Path | str) -> dict[str, Any]:
    """Verify a release audit file.

    Args:
        audit_file: Path to audit file

    Returns:
        Verification result dictionary
    """
    audit_file = Path(audit_file)

    result = {
        "valid": True,
        "file": str(audit_file),
        "errors": [],
        "warnings": [],
        "checks": {},
    }

    # Check file exists
    if not audit_file.exists():
        result["valid"] = False
        result["errors"].append(f"Audit file not found: {audit_file}")
        return result

    # Read audit file
    try:
        with open(audit_file, "r", encoding="utf-8") as f:
            audit = json.load(f)
    except json.JSONDecodeError as e:
        result["valid"] = False
        result["errors"].append(f"Invalid JSON in audit file: {e}")
        return result
    except Exception as e:
        result["valid"] = False
        result["errors"].append(f"Error reading audit file: {e}")
        return result

    # Check required fields
    required_fields = [
        "audit_id",
        "release_version",
        "timestamp",
        "status",
        "approvals",
        "artifacts",
        "checksums",
    ]

    for field in required_fields:
        if field not in audit:
            result["errors"].append(f"Missing required field: {field}")
            result["checks"][f"has_{field}"] = False
        else:
            result["checks"][f"has_{field}"] = True

    # Check approval status
    if "approvals" in audit:
        approvals = audit["approvals"]
        approval_status = {
            "editorial_review": approvals.get("editorial_review", {}).get("status"),
            "security_scan": approvals.get("security_scan", {}).get("status"),
            "final_release": approvals.get("final_release", {}).get("status"),
        }
        result["checks"]["approvals"] = approval_status

        # Warn if not all approvals are complete
        if approval_status["editorial_review"] != "approved":
            result["warnings"].append("Editorial review not approved")
        if approval_status["final_release"] != "approved":
            result["warnings"].append("Final release not approved")

    # Check artifact checksums
    if "checksums" in audit:
        checksums = audit["checksums"]
        result["checks"]["artifact_count"] = len(checksums)

        for artifact_path, checksums_dict in checksums.items():
            artifact_file = Path(artifact_path)

            if not artifact_file.exists():
                result["warnings"].append(f"Artifact file not found: {artifact_path}")
                continue

            # Verify SHA256
            try:
                file_sha256 = hashlib.sha256()
                with open(artifact_file, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        file_sha256.update(chunk)

                if file_sha256.hexdigest() == checksums_dict.get("sha256"):
                    result["checks"][f"checksum_ok_{artifact_path}"] = True
                else:
                    result["warnings"].append(
                        f"Checksum mismatch for {artifact_path} (SHA256)"
                    )
                    result["checks"][f"checksum_ok_{artifact_path}"] = False

            except Exception as e:
                result["warnings"].append(f"Error verifying checksum for {artifact_path}: {e}")

    # Check source information
    if "source" in audit:
        source = audit["source"]
        if source.get("commit_sha") == "unknown":
            result["warnings"].append("Source commit SHA not available")
        else:
            result["checks"]["has_commit_sha"] = True

    # Verify metadata
    if "metadata" in audit:
        metadata = audit["metadata"]
        result["checks"]["created_by"] = metadata.get("created_by", "unknown")
        result["checks"]["automation_version"] = metadata.get("automation_version", "unknown")

    # Final validation
    if result["errors"]:
        result["valid"] = False

    return result


def print_verification_report(result: dict[str, Any]) -> None:
    """Print verification report.

    Args:
        result: Verification result dictionary
    """
    print(f"\n{'='*60}")
    print("RELEASE AUDIT VERIFICATION REPORT")
    print(f"{'='*60}\n")

    print(f"File: {result['file']}")
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

    if result["checks"]:
        print("✅ CHECKS:")
        for check_name, check_value in result["checks"].items():
            if isinstance(check_value, bool):
                status = "✅" if check_value else "❌"
                print(f"  {status} {check_name}: {check_value}")
            elif isinstance(check_value, dict):
                print(f"  📋 {check_name}:")
                for key, val in check_value.items():
                    print(f"     - {key}: {val}")
            else:
                print(f"  📊 {check_name}: {check_value}")
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
        description="Verify release audit file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Verify audit file
  python scripts/deployment/verify_release_audit.py .codex/release-audits/0.1.0-audit.json

  # Output as JSON
  python scripts/deployment/verify_release_audit.py 0.1.0-audit.json --json
""",
    )

    parser.add_argument("audit_file", type=Path, help="Path to audit file to verify")
    parser.add_argument(
        "--json", action="store_true", help="Output verification result as JSON"
    )

    args = parser.parse_args(argv)

    try:
        result = verify_release_audit(args.audit_file)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_verification_report(result)

        return 0 if result["valid"] else 1

    except Exception as e:
        logger.error(f"Error verifying audit: {e}")
        print(f"❌ Verification failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
