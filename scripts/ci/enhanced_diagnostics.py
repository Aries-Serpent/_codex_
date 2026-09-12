#!/usr/bin/env python3
"""Structured wrapper around auto_fix_common_issues.py for campaign workflows."""

from __future__ import annotations

import argparse
import json
import signal
import threading
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterator

from scripts.ci.auto_fix_common_issues import CommonIssueFixer

DEFAULT_TIMEOUT_SECONDS = 120.0


class _DiagnosticsTimeout(BaseException):
    """Internal hard-stop signal that broad pattern exception handlers cannot swallow."""


@contextmanager
def _bounded_execution(timeout_seconds: float | None) -> Iterator[None]:
    """Bound a diagnostics sweep when POSIX interval timers are available."""
    if (
        timeout_seconds is None
        or timeout_seconds <= 0
        or not hasattr(signal, "SIGALRM")
        or threading.current_thread() is not threading.main_thread()
    ):
        yield
        return

    previous_handler = signal.getsignal(signal.SIGALRM)
    previous_timer = signal.getitimer(signal.ITIMER_REAL)

    def _raise_timeout(_signum: int, _frame: object) -> None:
        raise _DiagnosticsTimeout

    signal.signal(signal.SIGALRM, _raise_timeout)
    signal.setitimer(signal.ITIMER_REAL, timeout_seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, *previous_timer)
        signal.signal(signal.SIGALRM, previous_handler)


def _utc_timestamp() -> str:
    """Return a UTC timestamp using the repository-standard format."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_enhanced_diagnostics(
    repo_root: Path,
    pattern: int | None = None,
    pattern_name: str | None = None,
    output_path: Path | None = None,
    timeout_seconds: float | None = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Run detection-only diagnostics and enrich the JSON payload."""

    fixer = CommonIssueFixer(repo_root=repo_root, check_only=True)
    timed_out = False
    try:
        with _bounded_execution(timeout_seconds):
            if pattern is not None:
                fixer.run_all_patterns(pattern_num=pattern)
            elif pattern_name:
                fixer.run_all_patterns(pattern_name=pattern_name)
            else:
                fixer.run_all_patterns()
    except _DiagnosticsTimeout:
        timed_out = True

    report = fixer.generate_json_report()
    issues = report.get("issues", [])
    errors = sum(1 for issue in issues if issue.get("severity") == "error")
    warnings = sum(1 for issue in issues if issue.get("severity") == "warning")
    report["generated_at"] = _utc_timestamp()
    report["summary"] = {
        "errors": errors,
        "warnings": warnings,
        "blocking_patterns": sorted(
            {
                issue.get("pattern_name", "unknown")
                for issue in issues
                if issue.get("severity") == "error"
            }
        ),
    }
    report["recommended_command"] = (
        "python scripts/ci/bulk_remediation_orchestrator.py"
        if report.get("auto_fixable", 0) > 0
        else "No blocking auto-fixable issues remain."
    )
    report["diagnostics_complete"] = not timed_out
    if timed_out:
        report["status"] = "timed_out"
        report["timeout_seconds"] = timeout_seconds
        report["next_steps"] = [
            f"Diagnostics stopped after {timeout_seconds:g} seconds.",
            "Retry with --pattern/--pattern-name to narrow the scan.",
        ]

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    return report


def main() -> None:
    """CLI entry point."""

    parser = argparse.ArgumentParser(description="Run enhanced CI diagnostics")
    parser.add_argument("--repo-root", default=".", help="Repository root to scan")
    parser.add_argument("--pattern", type=int, default=None, help="Pattern number to scan")
    parser.add_argument(
        "--pattern-name",
        default=None,
        help="Pattern-name substring to scan when --pattern is not supplied",
    )
    parser.add_argument("--output", default=None, help="Optional JSON output path")
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"Maximum scan duration (default: {DEFAULT_TIMEOUT_SECONDS:g})",
    )
    args = parser.parse_args()

    report = run_enhanced_diagnostics(
        repo_root=Path(args.repo_root).resolve(),
        pattern=args.pattern,
        pattern_name=args.pattern_name,
        output_path=Path(args.output).resolve() if args.output else None,
        timeout_seconds=args.timeout_seconds,
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
