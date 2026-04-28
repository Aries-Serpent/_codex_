#!/usr/bin/env python3
"""
Run Capability Audit

Purpose:
    Runs capability_audit

Usage:
    python scripts/run_capability_audit.py [options]

    Examples:
    $ python scripts/run_capability_audit.py --help

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


from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from codex_ml.detectors.capability_detectors import run_capability_audit

WARN_THRESHOLD = 0.85


def print_table(result: dict, threshold: float = 0.99) -> None:
    """Print audit results as a formatted table."""
    print("=" * 80)
    print("CAPABILITY AUDIT REPORT")
    print("=" * 80)
    print()

    # Summary
    total_score = result["total_score"]
    status = "✅ PASS" if total_score >= threshold else "❌ FAIL"
    print(f"Overall Score: {total_score * 100:.2f}% {status}")
    print(f"Target Threshold: {threshold * 100:.0f}%")
    print(f"Capabilities: {len(result['by_capability'])}")
    print()

    # Capability table
    print("-" * 80)
    print(f"{'Capability':<25} {'Score':<12} {'Status':<10} {'Checks':<20}")
    print("-" * 80)

    for detail in result["details"]:
        name = detail["name"]
        score = detail["score"] * 100
        warn_cutoff = WARN_THRESHOLD * 100
        status = "✅" if score >= threshold * 100 else "⚠️" if score >= warn_cutoff else "❌"
        checks = detail.get("details", {}).get("checks", {})
        passed = sum(1 for v in checks.values() if v and v != 0)
        total = len(checks)
        print(f"{name:<25} {score:>6.1f}%     {status:<10} {passed}/{total}")

    print("-" * 80)
    print()

    # Recommendations
    failing = [d["name"] for d in result["details"] if d["score"] < threshold]
    if failing:
        print("⚠️  Capabilities below threshold:")
        for cap in failing:
            print(f"   - {cap}")
        print()
        print("Recommendations:")
        print("   1. Add more comprehensive tests")
        print("   2. Ensure detector checks are passing")
        print("   3. Review capability implementation")
    else:
        print("✅ All capabilities meet the threshold!")


def write_markdown_matrix(result: dict, threshold: float, path: Path) -> None:
    """Write a markdown capability matrix for quick inspection."""
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Capability Audit Matrix",
        "",
        f"- Overall Score: {result['total_score'] * 100:.2f}%",
        f"- Threshold: {threshold * 100:.0f}%",
        "",
        "| Capability | Score | Status | Checks Passed |",
        "|---|---|---|---|",
    ]

    for detail in result["details"]:
        checks = detail.get("details", {}).get("checks", {})
        passed = sum(1 for v in checks.values() if v and v != 0)
        total = len(checks)
        status = (
            "PASS"
            if detail["score"] >= threshold
            else "WARN" if detail["score"] >= WARN_THRESHOLD else "FAIL"
        )
        lines.append(
            f"| {detail['name']} | {detail['score'] * 100:.2f}% | {status} | {passed}/{total} |"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    """Run the capability audit."""
    parser = argparse.ArgumentParser(description="Run capability audit")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.99,
        help="Target threshold for passing (default: 0.99)",
    )
    parser.add_argument(
        "--fail-under",
        type=float,
        default=WARN_THRESHOLD,
        help=f"Fail if score is below this threshold (default: {WARN_THRESHOLD})",
    )
    parser.add_argument(
        "--output",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)",
    )
    parser.add_argument(
        "--save",
        type=str,
        help="Save results to file",
    )
    parser.add_argument(
        "--matrix-out",
        type=str,
        default="audit_artifacts/capability_matrix.md",
        help="Path to write markdown capability matrix (default: audit_artifacts/capability_matrix.md)",
    )
    args = parser.parse_args()

    # Run audit
    result = run_capability_audit()

    # Output results
    if args.output == "json":
        output = json.dumps(result, indent=2)
        print(output)
    else:
        print_table(result, args.threshold)

    # Save if requested
    if args.save:
        with open(args.save, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Results saved to {args.save}")

    # Write markdown matrix for easy viewing
    write_markdown_matrix(result, args.threshold, Path(args.matrix_out))
    print(f"Matrix report written to {args.matrix_out}")

    # Check fail-under threshold
    if result["total_score"] < args.fail_under:
        print(
            f"\n❌ FAILED: Score {result['total_score'] * 100:.2f}% is below {args.fail_under * 100:.0f}%"
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
