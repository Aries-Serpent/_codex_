#!/usr/bin/env python3
"""Validation orchestration CLI.

This helper wraps :mod:`scripts.run_validation` to provide richer CLI ergonomics
for developers as well as a machine-readable JSON summary that can be consumed
by CI systems or local tooling.
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_validation.sh"
DEFAULT_OUTPUT = ROOT / "validation_summary.json"
LOG_PATH = ROOT / "validation.log"
REPORT_PATH = ROOT / "report.xml"
COVERAGE_PATH = ROOT / "coverage.xml"


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Codex validation orchestrator")
    parser.add_argument(
        "--mode",
        choices=["fast", "full"],
        default="fast",
        help="Validation mode to run (fast skips heavy deps)",
    )
    parser.add_argument("--files", help="Comma-separated test files to run", default=None)
    parser.add_argument("--pytest-args", help="Additional pytest arguments", default=None)
    parser.add_argument(
        "--last-failed",
        action="store_true",
        help="Re-run only the tests that failed in the previous session",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Path to write the JSON summary (default: %(default)s)",
    )
    parser.add_argument(
        "--no-run",
        action="store_true",
        help="Only gather existing artifacts without executing the runner",
    )
    parser.add_argument("--verbose", action="store_true", help="Echo the JSON summary to stdout")
    return parser.parse_args(argv)


def run_validation(
    mode: str, files: Optional[str], pytest_args: Optional[str], last_failed: bool
) -> int:
    if not RUNNER.exists():
        raise FileNotFoundError(f"Validation runner missing at {RUNNER}")

    cmd = [str(RUNNER), f"--{mode}"]
    if files:
        cmd.append(f"--files={files}")

    passthrough: List[str] = []
    if pytest_args:
        passthrough.extend(shlex.split(pytest_args))
    if last_failed:
        passthrough.append("--lf")

    env = os.environ.copy()
    env["VALIDATE_MODE"] = mode
    existing_extra = env.get("PYTEST_EXTRA", "").strip()
    if passthrough:
        combined = " ".join(passthrough)
        env["PYTEST_EXTRA"] = f"{existing_extra} {combined}".strip()
    elif existing_extra:
        env["PYTEST_EXTRA"] = existing_extra

    print("Running:", " ".join(cmd + passthrough))
    result = subprocess.run(cmd + passthrough, env=env)
    return result.returncode


def safe_float(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_junit(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:  # pragma: no cover - defensive
        return {"error": f"Unable to parse JUnit XML: {exc}"}

    root = tree.getroot()
    suites = []
    if root.tag == "testsuite":
        suites = [root]
    else:
        suites = list(root.findall(".//testsuite"))

    summary = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0, "time": 0.0}
    for suite in suites:
        summary["tests"] += int(suite.attrib.get("tests", 0))
        summary["failures"] += int(suite.attrib.get("failures", 0))
        summary["errors"] += int(suite.attrib.get("errors", 0))
        summary["skipped"] += int(suite.attrib.get("skipped", 0))
        summary["time"] += float(suite.attrib.get("time", 0.0))
    return summary


def parse_coverage(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:  # pragma: no cover - defensive
        return {"error": f"Unable to parse coverage XML: {exc}"}

    root = tree.getroot()
    summary: Dict[str, Any] = {
        "line_rate": safe_float(root.attrib.get("line-rate")),
        "branch_rate": safe_float(root.attrib.get("branch-rate")),
        "timestamp": root.attrib.get("timestamp"),
        "version": root.attrib.get("version"),
    }
    if summary["line_rate"] is not None:
        summary["line_percent"] = round(summary["line_rate"] * 100, 2)
    if summary["branch_rate"] is not None:
        summary["branch_percent"] = round(summary["branch_rate"] * 100, 2)
    return summary


def gather_summary(
    mode: str, files: Optional[str], rc: int, pytest_args: Optional[str], last_failed: bool
) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "mode": mode,
        "files": files.split(",") if files else [],
        "return_code": rc,
        "status": "passed" if rc == 0 else "failed",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "artifacts": {
            "log": str(LOG_PATH) if LOG_PATH.exists() else None,
            "junit": str(REPORT_PATH) if REPORT_PATH.exists() else None,
            "coverage": str(COVERAGE_PATH) if COVERAGE_PATH.exists() else None,
        },
        "pytest": {
            "extra_args": pytest_args,
            "last_failed": last_failed,
        },
    }

    junit_stats = parse_junit(REPORT_PATH)
    if junit_stats:
        summary["junit_stats"] = junit_stats

    coverage_stats = parse_coverage(COVERAGE_PATH)
    if coverage_stats:
        summary["coverage_stats"] = coverage_stats

    if LOG_PATH.exists():
        try:
            summary["log_tail"] = LOG_PATH.read_text().splitlines()[-20:]
        except OSError:
            summary["log_tail"] = None

    return summary


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    rc = 0
    if not args.no_run:
        rc = run_validation(args.mode, args.files, args.pytest_args, args.last_failed)

    summary = gather_summary(args.mode, args.files, rc, args.pytest_args, args.last_failed)
    output_path = Path(args.output)
    payload = json.dumps(summary, indent=2, sort_keys=True) + "\n"
    try:
        output_path.write_text(payload)
        if output_path.resolve() != DEFAULT_OUTPUT:
            DEFAULT_OUTPUT.write_text(payload)
    except OSError as exc:
        print(f"Unable to write summary to {output_path}: {exc}", file=sys.stderr)
        return rc or 1

    if args.verbose:
        print(json.dumps(summary, indent=2, sort_keys=True))

    if rc != 0:
        print(f"Validation failed with exit code {rc}. See {output_path}")
    else:
        print(f"Validation succeeded. Summary written to {output_path}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
