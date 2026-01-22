#!/usr/bin/env python3
"""
Workflow Error Pattern Analyzer

Analyzes GitHub Actions workflow logs to detect recurring error patterns,
categorize failures, and provide actionable insights for CI/CD improvement.

Usage:
    python analyze_workflow_errors.py --logs <log_file>
    python analyze_workflow_errors.py --run-id <run_id>
    python analyze_workflow_errors.py --analyze-trends --days 7

Features:
    - Parse workflow logs for common error patterns
    - Categorize errors by type (import, syntax, test, timeout, etc.)
    - Detect recurring patterns across multiple runs
    - Generate actionable remediation suggestions
    - Track error trends over time

Author: Cognitive Brain Team
Created: 2026-01-22
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# =============================================================================
# Error Pattern Definitions
# =============================================================================

ERROR_PATTERNS = {
    "import_error": {
        "patterns": [
            r"ModuleNotFoundError:\s*No module named ['\"]?(\w+)['\"]?",
            r"ImportError:\s*cannot import name ['\"]?(\w+)['\"]?",
            r"NameError:\s*name ['\"]?(\w+)['\"]? is not defined",
        ],
        "severity": "high",
        "category": "dependency",
        "remediation": "Add missing import statement or install missing package",
    },
    "syntax_error": {
        "patterns": [
            r"SyntaxError:\s*(.+)",
            r"yaml\.scanner\.ScannerError:\s*(.+)",
            r"IndentationError:\s*(.+)",
        ],
        "severity": "high",
        "category": "code_quality",
        "remediation": "Fix syntax error in the indicated file and line",
    },
    "test_failure": {
        "patterns": [
            r"FAILED\s+(\S+::\S+)",
            r"AssertionError:\s*(.+)",
            r"pytest\.fail\((.+)\)",
            r"E\s+AssertionError:\s*(.+)",
        ],
        "severity": "medium",
        "category": "testing",
        "remediation": "Review test assertions and expected values",
    },
    "timeout_error": {
        "patterns": [
            r"TimeoutError:\s*(.+)",
            r"Timeout\s*\((.+)\)",
            r"timed out after (\d+) seconds",
            r"TIMEOUT",
        ],
        "severity": "medium",
        "category": "performance",
        "remediation": "Increase timeout or optimize slow operations",
    },
    "permission_error": {
        "patterns": [
            r"PermissionError:\s*(.+)",
            r"403 Forbidden",
            r"Permission denied",
            r"Resource not accessible by integration",
        ],
        "severity": "high",
        "category": "security",
        "remediation": "Update workflow permissions or token scopes",
    },
    "dependency_conflict": {
        "patterns": [
            r"pip resolver found incompatible requirements",
            r"version conflict:\s*(.+)",
            r"ResolutionImpossible",
            r"incompatible versions",
        ],
        "severity": "high",
        "category": "dependency",
        "remediation": "Update version pins to compatible ranges",
    },
    "type_error": {
        "patterns": [
            r"TypeError:\s*(.+)",
            r"AttributeError:\s*(.+)",
        ],
        "severity": "medium",
        "category": "code_quality",
        "remediation": "Check type annotations and object attributes",
    },
    "file_not_found": {
        "patterns": [
            r"FileNotFoundError:\s*(.+)",
            r"No such file or directory:\s*['\"]?(.+)['\"]?",
            r"ENOENT",
        ],
        "severity": "medium",
        "category": "configuration",
        "remediation": "Verify file paths and ensure files exist",
    },
    "network_error": {
        "patterns": [
            r"ConnectionError:\s*(.+)",
            r"ConnectionRefusedError",
            r"HTTPError:\s*(.+)",
            r"urllib\.error\.URLError",
        ],
        "severity": "low",
        "category": "infrastructure",
        "remediation": "Check network connectivity or mock external services",
    },
    "memory_error": {
        "patterns": [
            r"MemoryError",
            r"OutOfMemoryError",
            r"SIGKILL",
            r"Killed",
        ],
        "severity": "high",
        "category": "performance",
        "remediation": "Reduce memory usage or increase available memory",
    },
}


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class ErrorMatch:
    """Represents a matched error pattern."""

    error_type: str
    pattern: str
    match: str
    severity: str
    category: str
    remediation: str
    line_number: int | None = None
    context: str = ""


@dataclass
class AnalysisResult:
    """Result of analyzing workflow logs."""

    total_errors: int = 0
    errors_by_type: dict[str, list[ErrorMatch]] = field(default_factory=dict)
    errors_by_severity: dict[str, int] = field(
        default_factory=lambda: {"high": 0, "medium": 0, "low": 0}
    )
    errors_by_category: dict[str, int] = field(default_factory=dict)
    recurring_patterns: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    analyzed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_errors": self.total_errors,
            "errors_by_type": {k: [asdict(e) for e in v] for k, v in self.errors_by_type.items()},
            "errors_by_severity": self.errors_by_severity,
            "errors_by_category": self.errors_by_category,
            "recurring_patterns": self.recurring_patterns,
            "recommendations": self.recommendations,
            "analyzed_at": self.analyzed_at,
        }


# =============================================================================
# Analysis Functions
# =============================================================================


def analyze_log_content(log_content: str) -> AnalysisResult:
    """
    Analyze log content for error patterns.

    Args:
        log_content: Raw log text to analyze

    Returns:
        AnalysisResult with categorized errors and recommendations
    """
    result = AnalysisResult()
    lines = log_content.split("\n")

    for error_type, config in ERROR_PATTERNS.items():
        matches = []
        for pattern in config["patterns"]:
            for line_num, line in enumerate(lines, 1):
                for match in re.finditer(pattern, line, re.IGNORECASE):
                    error_match = ErrorMatch(
                        error_type=error_type,
                        pattern=pattern,
                        match=match.group(0),
                        severity=config["severity"],
                        category=config["category"],
                        remediation=config["remediation"],
                        line_number=line_num,
                        context=line.strip()[:200],
                    )
                    matches.append(error_match)

        if matches:
            result.errors_by_type[error_type] = matches
            result.total_errors += len(matches)
            result.errors_by_severity[config["severity"]] += len(matches)
            result.errors_by_category[config["category"]] = result.errors_by_category.get(
                config["category"], 0
            ) + len(matches)

    # Generate recommendations based on findings
    result.recommendations = _generate_recommendations(result)

    return result


def find_recurring_patterns(logs: list[str]) -> list[dict[str, Any]]:
    """
    Find error patterns that occur across multiple log files.

    Args:
        logs: List of log contents to analyze

    Returns:
        List of recurring patterns with occurrence counts
    """
    all_errors: Counter[str] = Counter()
    error_details: dict[str, dict[str, Any]] = {}

    for log in logs:
        analysis = analyze_log_content(log)
        for error_type, matches in analysis.errors_by_type.items():
            for match in matches:
                # Create a normalized key for the error
                key = f"{error_type}:{match.match[:100]}"
                all_errors[key] += 1
                if key not in error_details:
                    error_details[key] = {
                        "type": error_type,
                        "sample": match.match,
                        "remediation": match.remediation,
                        "severity": match.severity,
                    }

    # Filter to recurring patterns (2+ occurrences)
    recurring = []
    for key, count in all_errors.most_common():
        if count >= 2:
            details = error_details[key]
            details["occurrences"] = count
            recurring.append(details)

    return recurring


def _generate_recommendations(result: AnalysisResult) -> list[str]:
    """Generate actionable recommendations based on analysis."""
    recommendations = []

    # Priority recommendations based on severity
    if result.errors_by_severity["high"] > 0:
        recommendations.append(
            f"⚠️ HIGH PRIORITY: {result.errors_by_severity['high']} high-severity errors found. Address immediately."
        )

    # Category-specific recommendations
    if "dependency" in result.errors_by_category:
        recommendations.append(
            "📦 Dependency issues detected. Run `pip check` and review requirements.txt/pyproject.toml."
        )

    if "code_quality" in result.errors_by_category:
        recommendations.append(
            "🔍 Code quality issues found. Run `ruff check` and `black --check` before committing."
        )

    if "testing" in result.errors_by_category:
        recommendations.append(
            "🧪 Test failures detected. Review test assertions and expected values."
        )

    if "performance" in result.errors_by_category:
        recommendations.append(
            "⏱️ Performance issues found. Consider increasing timeouts or optimizing slow operations."
        )

    if "security" in result.errors_by_category:
        recommendations.append(
            "🔒 Security/permission issues detected. Review workflow permissions and token scopes."
        )

    # Add remediation for most common error type
    if result.errors_by_type:
        most_common = max(result.errors_by_type.items(), key=lambda x: len(x[1]))
        if most_common[1]:
            recommendations.append(
                f"📋 Most common error type: {most_common[0]} ({len(most_common[1])} occurrences). "
                f"Remediation: {most_common[1][0].remediation}"
            )

    return recommendations


# =============================================================================
# Output Functions
# =============================================================================


def print_summary(result: AnalysisResult) -> None:
    """Print a human-readable summary of the analysis."""
    print("\n" + "=" * 60)
    print("WORKFLOW ERROR ANALYSIS REPORT")
    print("=" * 60)
    print(f"Analyzed at: {result.analyzed_at}")
    print(f"Total errors found: {result.total_errors}")
    print()

    print("Errors by Severity:")
    for severity, count in result.errors_by_severity.items():
        if count > 0:
            print(f"  {severity.upper()}: {count}")

    print("\nErrors by Category:")
    for category, count in sorted(result.errors_by_category.items(), key=lambda x: -x[1]):
        print(f"  {category}: {count}")

    print("\nErrors by Type:")
    for error_type, matches in sorted(result.errors_by_type.items(), key=lambda x: -len(x[1])):
        print(f"\n  {error_type} ({len(matches)} occurrences):")
        # Show first 3 examples
        for match in matches[:3]:
            print(f"    - Line {match.line_number}: {match.context[:80]}...")

    print("\n" + "-" * 60)
    print("RECOMMENDATIONS:")
    print("-" * 60)
    for rec in result.recommendations:
        print(f"  {rec}")

    print("\n" + "=" * 60)


def save_report(result: AnalysisResult, output_path: Path) -> None:
    """Save analysis report to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    print(f"Report saved to: {output_path}")


# =============================================================================
# Main Entry Point
# =============================================================================


def main() -> int:
    """Main entry point for the analyzer."""
    parser = argparse.ArgumentParser(
        description="Analyze GitHub Actions workflow logs for error patterns"
    )
    parser.add_argument(
        "--logs",
        type=Path,
        help="Path to log file or directory containing log files",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".codex/reports/error_analysis.json"),
        help="Output path for JSON report",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text", "both"],
        default="both",
        help="Output format",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    if not args.logs:
        # Read from stdin if no file specified
        print("Reading from stdin...")
        log_content = sys.stdin.read()
    elif args.logs.is_file():
        log_content = args.logs.read_text(encoding="utf-8")
    elif args.logs.is_dir():
        # Analyze multiple log files
        log_files = list(args.logs.glob("**/*.log")) + list(args.logs.glob("**/*.txt"))
        if not log_files:
            print(f"No log files found in {args.logs}")
            return 1
        log_content = "\n\n".join(f.read_text(encoding="utf-8") for f in log_files)
        print(f"Analyzing {len(log_files)} log files...")
    else:
        print(f"Error: {args.logs} not found")
        return 1

    # Analyze the logs
    result = analyze_log_content(log_content)

    # Output results
    if args.format in ("text", "both"):
        print_summary(result)

    if args.format in ("json", "both"):
        save_report(result, args.output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
