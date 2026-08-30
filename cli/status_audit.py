#!/usr/bin/env python
"""
Codex Status Update Audit Report Generator

Purpose:
- Traverse the repository codebase
- Run capability audit
- Generate comprehensive status update audit report
- Provide a single command interface for status audits

Usage:
    codex-status-audit [--output OUTPUT] [--baseline BASELINE]
    codex-status-audit --generate  # Generate JSON status update

This command orchestrates:
1. Repository capability audit (via audit_runner.py)
2. Status update report generation (via generate_status_update.py)
3. Optional baseline comparison for delta tracking
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


def _run_command(cmd: list[str], description: str) -> int:
    """Run a command and return its exit code.

    Output streams in real-time (not buffered) for better user experience
    and to avoid memory issues with large outputs.
    """
    print(f"[INFO] {description}...")
    try:
        result = subprocess.run(cmd, text=True)
        return result.returncode
    except Exception as e:
        print(f"[ERROR] Failed to run {description}: {e}", file=sys.stderr)
        return 1


def main(argv: list[str] | None = None) -> int:
    """Main entry point for status audit command."""
    parser = argparse.ArgumentParser(
        description="Generate a comprehensive Codex status update audit report"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output directory for reports (default: .codex/reports/)",
        default=".codex/reports",
    )
    parser.add_argument(
        "--generate",
        "-g",
        action="store_true",
        help="Generate JSON status update report using the new schema-based tool",
    )
    parser.add_argument(
        "--baseline",
        "-b",
        help="Path to baseline capabilities_scored.json for delta comparison",
        default="",
    )
    parser.add_argument(
        "--artifacts",
        help="Artifacts directory (default: audit_artifacts/)",
        default="audit_artifacts",
    )
    parser.add_argument(
        "--skip-audit",
        action="store_true",
        help="Skip running the audit pipeline (use existing artifacts)",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick mode: only run essential stages",
    )

    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[1]

    # If --generate flag is set, use the new JSON-based tool
    if args.generate:
        print("=" * 70)
        print("Generating JSON Status Update Report (Schema-based)")
        print("=" * 70)
        print()

        status_generator = repo_root / "tools" / "generate_status_update.py"
        if not status_generator.exists():
            print(f"[ERROR] Status generator not found: {status_generator}", file=sys.stderr)
            return 1

        return _run_command([sys.executable, str(status_generator)], "Generate JSON status update")

    # Original audit pipeline workflow
    audit_runner = repo_root / "scripts" / "space_traversal" / "audit_runner.py"
    status_reporter = repo_root / "scripts" / "space_traversal" / "status_update_report.py"

    # Ensure scripts exist
    if not audit_runner.exists():
        print(f"[ERROR] Audit runner not found: {audit_runner}", file=sys.stderr)
        return 1

    if not status_reporter.exists():
        print(f"[ERROR] Status reporter not found: {status_reporter}", file=sys.stderr)
        return 1

    print("=" * 70)
    print("Codex Status Update Audit Report Generator")
    print("=" * 70)
    print()

    artifacts_dir = Path(args.artifacts)

    # Step 1: Run audit pipeline (unless skipped)
    if not args.skip_audit:
        print("[STEP 1/2] Running capability audit pipeline")
        print(f"           Artifacts will be saved to: {artifacts_dir}/")
        print()

        audit_cmd = [
            sys.executable,
            str(audit_runner),
            "run",
            "--artifacts-dir",
            str(artifacts_dir),
        ]
        rc = _run_command(audit_cmd, "Capability audit")

        if rc != 0:
            print(f"[WARN] Audit pipeline returned exit code {rc}", file=sys.stderr)
            # Continue anyway as artifacts may still be usable
    else:
        print("[STEP 1/2] Skipping audit pipeline (using existing artifacts)")
        print()

        # Validate required artifacts before attempting report generation
        required_artifacts = [artifacts_dir / "capabilities_scored.json"]
        missing = [p for p in required_artifacts if not p.exists()]
        if missing:
            print(
                "[ERROR] Missing required audit artifacts when --skip-audit is used:\n"
                + "\n".join(f" - {p}" for p in missing),
                file=sys.stderr,
            )
            return 2

    # Step 2: Generate status update report
    print("[STEP 2/2] Generating status update report")
    print(f"           Report will be saved to: {args.output}/")
    print()

    status_cmd = [
        sys.executable,
        str(status_reporter),
        "--artifacts",
        str(artifacts_dir),
        "--reports",
        args.output,
    ]

    if args.baseline:
        status_cmd.extend(["--base", args.baseline])
        print(f"           Using baseline: {args.baseline}")
        print()

    rc = _run_command(status_cmd, "Status update report")

    if rc != 0:
        print(f"[ERROR] Status report generation failed with exit code {rc}", file=sys.stderr)
        return rc

    print()
    print("=" * 70)
    print("[SUCCESS] Status audit complete!")
    print("=" * 70)
    print()
    print(f"Artifacts directory: {args.artifacts}/")
    print(f"Reports directory:   {args.output}/")
    print()

    # List recent reports
    reports_dir = Path(args.output)
    if reports_dir.exists():
        recent_reports = sorted(reports_dir.glob("codex_status_update_*.md"), reverse=True)[:3]
        if recent_reports:
            print("Recent reports:")
            for report in recent_reports:
                mtime = report.stat().st_mtime
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
                print(f"  - {report.name} ({timestamp})")
            print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
