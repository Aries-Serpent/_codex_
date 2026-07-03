#!/usr/bin/env python3
"""
Workflow YAML Trigger Key Remediation Script

This script remediates GitHub Actions workflow files that incorrectly use `true:`
as the trigger configuration key instead of the standard `on:` key.

Usage:
    python scripts/ci/remediate_workflow_triggers.py --dry-run
    python scripts/ci/remediate_workflow_triggers.py --apply
    python scripts/ci/remediate_workflow_triggers.py --validate
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

import yaml

# Target workflows directory
WORKFLOWS_DIR = Path(".github/workflows")

# List of all 40 affected workflows
AFFECTED_WORKFLOWS = [
    "actionlint-audit.yml",
    "agent-registry-validation.yml",
    "api-documentation.yml",
    "auto-approve-workflows.yml",
    "autonomy-phase-ci-matrix.yml",
    "build-agent-env-cache.yml",
    "build-preview-image.yml",
    "ci-checkpoint-validation.yml",
    "ci-health-monitor.yml",
    "ci-pattern-prevention-gate.yml",
    "code-quality-coverage-suite.yml",
    "codeql-analysis.yml",
    "consistency-checks.yml",
    "copilot-agent-checkin.yml",
    "copilot-agent-vars-bootstrap.yml",
    "copilot-setup-validation.yml",
    "dependency-submission.yml",
    "doc-refresh-gate.yml",
    "docker-build-push.yml",
    "forward-sync-autogen.yml",
    "import-linter.yml",
    "ml-lifecycle-gate.yml",
    "mypy-baseline.yml",
    "nox_gates.yml",
    "openvino-phase-c.yml",
    "phase-8-3-perf-monitor.yml",
    "post-accountability-to-discussion.yml",
    "post-ci-status-to-discussion.yml",
    "pre-flight-validation.yml",
    "process-variable-intents.yml",
    "reference-integrity.yml",
    "rust_swarm_ci.yml",
    "sbom.yml",
    "scan-secrets-variables.yml",
    "sync-env-vars.yml",
    "unified-deployment.yml",
    "validate-api-null-handling.yml",
    "validate-code-examples.yml",
    "workflow-expiry-enforcer.yml",
    "workflow-link-validation.yml",
]


def get_file_hash(filepath: Path) -> str:
    """Calculate MD5 hash of file for verification."""
    hash_md5 = hashlib.md5(usedforsecurity=False)
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def find_true_key_line(filepath: Path) -> Tuple[int, bool]:
    """Find line number of `true:` key in workflow file.

    Returns tuple of (line_number, found) where line_number is 1-indexed.
    """
    with open(filepath, "r") as f:
        for i, line in enumerate(f, 1):
            if re.match(r"^true:\s*$", line):
                return i, True
    return -1, False


def validate_yaml(filepath: Path) -> Tuple[bool, str]:
    """Validate YAML syntax of workflow file.

    Returns tuple of (is_valid, message).
    """
    try:
        with open(filepath, "r") as f:
            yaml.safe_load(f)
        return True, "YAML syntax valid"
    except yaml.YAMLError as e:
        return False, f"YAML syntax error: {e}"


def remediate_file(filepath: Path, dry_run: bool = True) -> Tuple[bool, str]:
    """Remediate single workflow file, replacing `true:` with `on:`.

    Returns tuple of (success, message).
    """
    line_num, found = find_true_key_line(filepath)

    if not found:
        # File is already remediated or doesn't have the pattern - treat as success
        return True, "File already has `on:` or `true:` key not found (already remediated)"

    # Read file
    with open(filepath, "r") as f:
        lines = f.readlines()

    # Replace the line (0-indexed)
    target_line_idx = line_num - 1
    original_line = lines[target_line_idx]
    new_line = re.sub(r"^true:", "on:", original_line)

    if not dry_run:
        lines[target_line_idx] = new_line

        # Write file back
        with open(filepath, "w") as f:
            f.writelines(lines)

        # Validate after change
        is_valid, msg = validate_yaml(filepath)
        if not is_valid:
            return False, f"Post-change validation failed: {msg}"

        return True, f"Successfully replaced `true:` with `on:` at line {line_num}"
    else:
        return True, f"[DRY-RUN] Would replace `true:` with `on:` at line {line_num}"


def generate_audit_metadata(output_file: Path = None) -> Dict:
    """Generate comprehensive audit metadata for all affected workflows.

    Returns audit metadata dictionary and optionally writes to file.
    """
    metadata = {
        "campaign": "workflow_trigger_key_remediation",
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "affected_workflows_count": len(AFFECTED_WORKFLOWS),
        "affected_workflows": [],
        "summary": {
            "total_files": 0,
            "found_pattern": 0,
            "missing_files": 0,
            "already_remediated": 0,
        }
    }

    for workflow_name in sorted(AFFECTED_WORKFLOWS):
        filepath = WORKFLOWS_DIR / workflow_name

        if not filepath.exists():
            metadata["affected_workflows"].append({
                "file": workflow_name,
                "status": "NOT_FOUND",
                "path": str(filepath),
            })
            metadata["summary"]["missing_files"] += 1
            continue

        line_num, found = find_true_key_line(filepath)

        if found:
            file_hash = get_file_hash(filepath)
            is_valid, yaml_msg = validate_yaml(filepath)

            metadata["affected_workflows"].append({
                "file": workflow_name,
                "status": "REQUIRES_REMEDIATION",
                "path": str(filepath),
                "true_key_line": line_num,
                "file_hash": file_hash,
                "yaml_valid": is_valid,
                "yaml_message": yaml_msg,
            })
            metadata["summary"]["found_pattern"] += 1
        else:
            # Check if already remediated
            with open(filepath, "r") as f:
                content = f.read()
                if re.search(r"^on:\s*$", content, re.MULTILINE):
                    status = "ALREADY_REMEDIATED"
                    metadata["summary"]["already_remediated"] += 1
                else:
                    status = "NO_PATTERN_FOUND"

            metadata["affected_workflows"].append({
                "file": workflow_name,
                "status": status,
                "path": str(filepath),
            })

        metadata["summary"]["total_files"] += 1

    if output_file:
        with open(output_file, "w") as f:
            json.dump(metadata, f, indent=2)

    return metadata


def main():
    parser = argparse.ArgumentParser(
        description="Remediate GitHub Actions workflow trigger keys"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply remediation changes to all affected workflows"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate all affected workflows"
    )
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Generate audit metadata"
    )
    parser.add_argument(
        "--audit-output",
        type=Path,
        default=Path(".codex/workflow_trigger_audit.json"),
        help="Output path for audit metadata (default: .codex/workflow_trigger_audit.json)"
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        help="Output results as JSON to specified file"
    )

    args = parser.parse_args()

    results = {
        "success": True,
        "phases": {}
    }

    # Phase 1: Generate audit metadata
    if args.audit or args.dry_run or args.apply:
        print("[Phase 1] Generating audit metadata...")
        audit_output = args.audit_output if args.audit else None
        metadata = generate_audit_metadata(audit_output)

        print(f"  Total files analyzed: {metadata['summary']['total_files']}")
        print(f"  Requires remediation: {metadata['summary']['found_pattern']}")
        print(f"  Already remediated: {metadata['summary']['already_remediated']}")
        print(f"  Missing files: {metadata['summary']['missing_files']}")

        results["phases"]["audit"] = metadata["summary"]

        if audit_output:
            print(f"  Audit metadata saved to: {audit_output}")

    # Phase 2: Apply remediation
    if args.apply or args.dry_run:
        print(f"\n[Phase 2] {'[DRY-RUN] Checking' if args.dry_run else 'Applying'} remediation...")

        successful = 0
        failed = 0
        changes = []

        for workflow_name in sorted(AFFECTED_WORKFLOWS):
            filepath = WORKFLOWS_DIR / workflow_name

            if not filepath.exists():
                print(f"  ⚠️  {workflow_name}: File not found")
                failed += 1
                continue

            success, msg = remediate_file(filepath, dry_run=args.dry_run)

            if success:
                print(f"  ✓ {workflow_name}: {msg}")
                successful += 1
                changes.append({
                    "file": workflow_name,
                    "result": msg
                })
            else:
                print(f"  ✗ {workflow_name}: {msg}")
                failed += 1
                results["success"] = False

        results["phases"]["remediation"] = {
            "dry_run": args.dry_run,
            "successful": successful,
            "failed": failed,
            "changes": changes
        }

        print(f"\n  Summary: {successful} successful, {failed} failed")

    # Phase 3: Validate
    if args.validate:
        print("\n[Phase 3] Validating all workflows...")

        valid_count = 0
        invalid_count = 0
        validation_results = []

        for workflow_name in sorted(AFFECTED_WORKFLOWS):
            filepath = WORKFLOWS_DIR / workflow_name

            if not filepath.exists():
                continue

            is_valid, msg = validate_yaml(filepath)

            if is_valid:
                print(f"  ✓ {workflow_name}: {msg}")
                valid_count += 1
            else:
                print(f"  ✗ {workflow_name}: {msg}")
                invalid_count += 1
                results["success"] = False

            validation_results.append({
                "file": workflow_name,
                "valid": is_valid,
                "message": msg
            })

        results["phases"]["validation"] = {
            "valid": valid_count,
            "invalid": invalid_count,
            "results": validation_results
        }

        print(f"\n  Summary: {valid_count} valid, {invalid_count} invalid")

    # Output results
    if args.json_output:
        with open(args.json_output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {args.json_output}")

    return 0 if results["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
