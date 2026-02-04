#!/usr/bin/env python3
"""
CI Failure Diagnosis Tool

Analyzes CI workflow logs to identify common failure patterns and suggest fixes.

Usage:
    python diagnose_ci_failure.py <run_id>
    python diagnose_ci_failure.py --log-file /path/to/log.txt
"""

import json
import re
import sys
from pathlib import Path
from typing import Any


# NOTE: `auto_fix` values are human-readable suggestions and are not dynamically
# formatted. They describe the remediation action for operators to take manually.
ERROR_PATTERNS: dict[str, dict[str, Any]] = {
    "missing_dependency": {
        "pattern": r"ModuleNotFoundError: No module named ['\"]([^'\"]+)['\"]",
        "diagnosis": "Missing Python dependency",
        "auto_fix": "Install the missing module with pip (e.g., pip install <module>)",
        "priority": "high",
    },
    "sarif_upload": {
        "pattern": r"(SARIF upload.*fail|sarif.*error|Error: Unable to upload)",
        "diagnosis": "SARIF upload configuration issue",
        "auto_fix": "Check SARIF file format and GitHub token permissions",
        "priority": "high",
    },
    "coverage_threshold": {
        "pattern": r"coverage.*below.*threshold|FAILED.*coverage|fail-under",
        "diagnosis": "Test coverage below minimum threshold",
        "auto_fix": "Add tests for uncovered code paths",
        "priority": "medium",
    },
    "syntax_error": {
        "pattern": r"SyntaxError:|invalid syntax|unexpected token",
        "diagnosis": "Syntax error detected",
        "auto_fix": "Review code for syntax issues",
        "priority": "high",
    },
    "linting_error": {
        "pattern": r"(ruff|black|isort|pylint).*error|linting.*fail",
        "diagnosis": "Code formatting/linting violations",
        "auto_fix": "Run: ruff check --fix && black . && isort .",
        "priority": "low",
    },
    "test_failure": {
        "pattern": r"FAILED.*test_|AssertionError|pytest.*failed",
        "diagnosis": "Unit test assertion failed",
        "auto_fix": "Review test expectations and implementation",
        "priority": "high",
    },
    "import_error": {
        "pattern": r"ImportError:|cannot import name",
        "diagnosis": "Import error - module or name not found",
        "auto_fix": "Check module installation and import paths",
        "priority": "high",
    },
    "type_error": {
        "pattern": r"TypeError:|type.*mismatch",
        "diagnosis": "Type error in code",
        "auto_fix": "Review type annotations and function signatures",
        "priority": "high",
    },
    "permission_denied": {
        "pattern": r"PermissionError:|Permission denied|EACCES",
        "diagnosis": "Permission denied error",
        "auto_fix": "Check file/directory permissions",
        "priority": "high",
    },
    "timeout": {
        "pattern": r"timeout|timed out|TimeoutError",
        "diagnosis": "Operation timed out",
        "auto_fix": "Increase timeout or optimize slow operations",
        "priority": "medium",
    },
    "shell_syntax": {
        "pattern": r"syntax error near unexpected token|bad substitution",
        "diagnosis": "Shell script syntax error",
        "auto_fix": "Review shell script for syntax issues, especially special characters",
        "priority": "high",
    },
}


def diagnose_log(log_content: str) -> list[dict[str, Any]]:
    """Diagnose CI failure from log content."""
    findings = []

    for error_type, config in ERROR_PATTERNS.items():
        matches = re.findall(config["pattern"], log_content, re.IGNORECASE)
        if matches:
            # Extract unique matches (limit to first 5)
            unique_matches = list(set(matches[:10]))[:5]
            findings.append(
                {
                    "type": error_type,
                    "diagnosis": config["diagnosis"],
                    "auto_fix": config["auto_fix"],
                    "priority": config["priority"],
                    "matches": unique_matches,
                    "count": len(matches),
                }
            )

    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    findings.sort(key=lambda x: priority_order.get(x["priority"], 3))

    return findings


def diagnose_log_file(log_file: Path) -> list[dict[str, Any]]:
    """Diagnose CI failure from log file."""
    with open(log_file, encoding="utf-8", errors="replace") as f:
        log_content = f.read()
    return diagnose_log(log_content)


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: diagnose_ci_failure.py <run_id> or --log-file <path>"}))
        sys.exit(1)

    if sys.argv[1] == "--log-file":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Missing log file path"}))
            sys.exit(1)
        log_file = Path(sys.argv[2])
        if not log_file.exists():
            print(json.dumps({"error": f"Log file not found: {log_file}"}))
            sys.exit(1)
        findings = diagnose_log_file(log_file)
    else:
        run_id = sys.argv[1]
        log_file = Path(f".codex/logs/run_{run_id}.log")

        if not log_file.exists():
            print(json.dumps({"error": f"Log file not found: {log_file}"}))
            sys.exit(1)

        findings = diagnose_log_file(log_file)

    print(json.dumps(findings, indent=2))


if __name__ == "__main__":
    main()
