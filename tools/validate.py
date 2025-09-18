#!/usr/bin/env python3
"""Validation orchestration CLI.

This helper wraps ``scripts/run_validation.sh`` to provide a richer developer
experience:

* simple command line switching between fast and full validation modes
* optional reruns that target only tests that failed previously
* structured JSON summaries that downstream tooling (or CI) can consume
* minimal parsing of produced artifacts (JUnit + coverage)
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_validation.sh"
LOG_PATH = ROOT / "validation.log"
JUNIT_PATH = ROOT / "validation-junit.xml"
COVERAGE_PATH = ROOT / "coverage.xml"


@dataclass
class JunitStats:
    tests: int
    failures: int
    errors: int
    skipped: int
    duration: float
    failed_cases: list[str]


def _int_attr(node: ET.Element, attr: str) -> int:
    value = node.attrib.get(attr)
    if value is None:
        return 0
    try:
        return int(value)
    except ValueError:
        try:
            return int(float(value))
        except ValueError:
            return 0


def _float_attr(node: ET.Element, attr: str) -> float:
    value = node.attrib.get(attr)
    if value is None:
        return 0.0
    try:
        return float(value)
    except ValueError:
        return 0.0


def parse_junit(path: Path) -> JunitStats | None:
    if not path.exists():
        return None
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        print(
            f"Warning: failed to parse JUnit report at {path}: {exc}",
            file=sys.stderr,
        )
        return None
    root = tree.getroot()
    suites: Iterable[ET.Element]
    if root.tag == "testsuite":
        suites = [root]
    elif root.tag == "testsuites":
        suites = root.findall("testsuite")
    else:
        suites = root

    total_tests = 0
    total_failures = 0
    total_errors = 0
    total_skipped = 0
    total_time = 0.0
    failed_cases: list[str] = []

    for suite in suites:
        total_tests += _int_attr(suite, "tests")
        total_failures += _int_attr(suite, "failures")
        total_errors += _int_attr(suite, "errors")
        total_skipped += _int_attr(suite, "skipped")
        total_time += _float_attr(suite, "time")
        for case in suite.findall("testcase"):
            if case.find("failure") is None and case.find("error") is None:
                continue
            identifier = _case_identifier(case)
            if identifier not in failed_cases:
                failed_cases.append(identifier)

    return JunitStats(
        tests=total_tests,
        failures=total_failures,
        errors=total_errors,
        skipped=total_skipped,
        duration=total_time,
        failed_cases=failed_cases,
    )


def _case_identifier(case: ET.Element) -> str:
    file_path = case.attrib.get("file")
    name = case.attrib.get("name", "")
    classname = case.attrib.get("classname", "")
    if file_path:
        return f"{file_path}::{name}"
    if classname:
        module_selector = classname.replace(".", "::")
        return f"{module_selector}::{name}"
    return name or "<unknown>"


def parse_coverage(path: Path) -> dict[str, float] | None:
    if not path.exists():
        return None
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        print(
            f"Warning: failed to parse coverage report at {path}: {exc}",
            file=sys.stderr,
        )
        return None
    root = tree.getroot()
    return {
        "line_rate": float(root.attrib.get("line-rate", 0.0)),
        "branch_rate": float(root.attrib.get("branch-rate", 0.0)),
    }


def build_command(mode: str, selectors: list[str] | None) -> list[str]:
    cmd = [str(SCRIPT)]
    if mode:
        cmd.append(f"--{mode}")
    if selectors:
        joined = ",".join(selectors)
        cmd.append(f"--files={joined}")
    return cmd


def run_validation(mode: str, selectors: list[str] | None, pytest_opts: str | None) -> int:
    cmd = build_command(mode, selectors)
    env = os.environ.copy()
    if pytest_opts:
        existing = env.get("PYTEST_OPTS")
        env["PYTEST_OPTS"] = f"{existing} {pytest_opts}".strip() if existing else pytest_opts
    start = time.time()
    print("Running:", " ".join(cmd))
    completed = subprocess.run(cmd, cwd=ROOT, env=env)
    duration = time.time() - start
    print(f"Validation finished in {duration:.2f}s with exit code {completed.returncode}")
    return completed.returncode


def gather_summary(
    mode: str, selectors: list[str] | None, pytest_opts: str | None, exit_code: int
) -> dict:
    junit_stats = parse_junit(JUNIT_PATH)
    coverage_stats = parse_coverage(COVERAGE_PATH)
    summary = {
        "mode": mode,
        "selectors": selectors or [],
        "pytest_opts": pytest_opts or "",
        "exit_code": exit_code,
        "artifacts": {
            "log": str(LOG_PATH.relative_to(ROOT)) if LOG_PATH.exists() else None,
            "junit": str(JUNIT_PATH.relative_to(ROOT)) if JUNIT_PATH.exists() else None,
            "coverage": str(COVERAGE_PATH.relative_to(ROOT)) if COVERAGE_PATH.exists() else None,
        },
    }
    if junit_stats:
        summary["junit"] = {
            "tests": junit_stats.tests,
            "failures": junit_stats.failures,
            "errors": junit_stats.errors,
            "skipped": junit_stats.skipped,
            "duration_seconds": round(junit_stats.duration, 3),
            "failed_cases": junit_stats.failed_cases,
        }
    if coverage_stats:
        summary["coverage"] = coverage_stats
    return summary


def _selectors_from_failures() -> list[str]:
    stats = parse_junit(JUNIT_PATH)
    if not stats or not stats.failed_cases:
        return []
    return stats.failed_cases


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Codex validation orchestrator")
    parser.add_argument("--mode", choices=["fast", "full"], help="Validation mode to execute")
    parser.add_argument("--files", nargs="*", help="Explicit pytest targets to run")
    parser.add_argument("--pytest-opts", default=None, help="Additional pytest options to forward")
    parser.add_argument(
        "--rerun-failures",
        action="store_true",
        help="Re-run only failing tests from the last JUnit report",
    )
    parser.add_argument(
        "--output",
        default="validation_summary.json",
        help="Where to write the JSON summary (use - for stdout)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only emit the computed summary without executing validation",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    mode = args.mode or os.environ.get("VALIDATE_MODE", "fast")
    selectors: list[str] | None = None

    if args.files:
        selectors = args.files

    if args.rerun_failures:
        failure_selectors = _selectors_from_failures()
        if not failure_selectors:
            print("No recorded failures found in", JUNIT_PATH)
        else:
            selectors = failure_selectors
            print("Re-running failing tests:")
            for item in selectors:
                print("  -", item)

    pytest_opts = args.pytest_opts
    if args.dry_run:
        summary = gather_summary(mode, selectors, pytest_opts, exit_code=0)
        _write_summary(summary, args.output)
        return 0

    exit_code = run_validation(mode, selectors, pytest_opts)
    summary = gather_summary(mode, selectors, pytest_opts, exit_code)
    _write_summary(summary, args.output)
    if exit_code != 0:
        print("Validation failed; see", summary["artifacts"]["log"])
    else:
        print("Validation succeeded")
    return exit_code


def _write_summary(summary: dict, destination: str) -> None:
    payload = json.dumps(summary, indent=2)
    if destination == "-":
        print(payload)
        return
    output_path = Path(destination)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(payload)
    print("Summary written to", output_path)


if __name__ == "__main__":
    sys.exit(main())
