#!/usr/bin/env python3
"""
Batch Scan Integration — programmatic API for Copilot agents.

All applicable agents use this module to invoke ``rvs_preflight.py``
with the correct flags instead of running ``pytest tests/`` directly.
The runner splits the suite into batches and executes them in parallel
so agents see failures fast without waiting for a sequential 70-minute run.

Quick-start
-----------
>>> from scripts.ci.batch_scan_integration import BatchScanRunner
>>> runner = BatchScanRunner()
>>> result = runner.scan(group="quick", changed_only=True)
>>> if not result.ok:
...     for f in result.failures[:5]:
...         print(f)

Agent integration contract
--------------------------
1. Always call ``preview()`` first to confirm scope.
2. Call ``scan(changed_only=True)`` for incremental checks.
3. Call ``scan(group="quick")`` for full pre-commit validation.
4. Inspect ``ScanResult.failures`` and ``ScanResult.report`` for structured output.
5. Never invoke ``pytest tests/`` directly — always go through this API.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Literal, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
_PREFLIGHT = REPO_ROOT / "scripts" / "ci" / "rvs_preflight.py"

Group = Literal["quick", "slow", "integration", "docs", "all"]


@dataclass
class BatchScanResult:
    """Structured result returned by every agent scan."""

    group: str
    ok: bool
    passed: int
    failed: int
    errors: int
    skipped: int
    duration_s: float
    failures: List[str]                    # list of FAILED test node-ids
    batches_run: int
    report_path: Optional[Path] = None     # path to JSON report if requested
    raw: Dict = field(default_factory=dict)

    @property
    def summary_line(self) -> str:
        icon = "✅" if self.ok else "❌"
        return (
            f"{icon} {self.group.upper():12}  "
            f"P:{self.passed}  F:{self.failed}  S:{self.skipped}  "
            f"{self.duration_s:.1f}s  batches:{self.batches_run}"
        )


class BatchScanRunner:
    """Invoke ``rvs_preflight.py`` and return a ``BatchScanResult``.

    Parameters
    ----------
    workers:
        Number of parallel batch processes (default: auto = cpu_count/2).
    batch_size:
        Test files per batch (default 30; increase for fast test suites,
        decrease if workers are resource-constrained).
    """

    def __init__(
        self,
        workers: Optional[int] = None,
        batch_size: int = 30,
    ) -> None:
        self.workers = workers
        self.batch_size = batch_size

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def preview(self, group: Group = "quick") -> str:
        """Return a human-readable list of what *would* run — no execution."""
        out = self._run(group=group, extra_flags=["--preview"], report=None)
        return out.get("stdout", "")

    def scan(
        self,
        group: Group = "quick",
        changed_only: bool = False,
        fail_fast: bool = False,
        report_path: Optional[Path] = None,
    ) -> BatchScanResult:
        """Execute the scan and return a structured result.

        Parameters
        ----------
        group:
            One of ``quick | slow | integration | docs | all``.
            Mirrors the ``matrix.test-group`` from ``resilient_validation.yml``.
        changed_only:
            When ``True``, only tests for files changed since last commit are run.
            Use for fast incremental checks during active development.
        fail_fast:
            Stop all parallel batches on the first batch failure.
        report_path:
            Optional path to write the full JSON report.  When ``None`` a
            temporary file is used and cleaned up after parsing.
        """
        use_tmp = report_path is None
        tmp = tempfile.NamedTemporaryFile(
            prefix="rvs_report_", suffix=".json", delete=False
        ) if use_tmp else None

        actual_report = Path(tmp.name) if tmp else report_path
        if tmp:
            tmp.close()

        try:
            extra: List[str] = []
            if changed_only:
                extra.append("--changed-only")
            if fail_fast:
                extra.append("--fail-fast")

            self._run(
                group=group,
                extra_flags=extra,
                report=actual_report,
            )

            return self._parse_report(actual_report, group, report_path)

        finally:
            if use_tmp and actual_report and actual_report.exists():
                actual_report.unlink(missing_ok=True)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _run(
        self,
        group: Group,
        extra_flags: List[str],
        report: Optional[Path],
    ) -> dict:
        cmd = [
            sys.executable,
            str(_PREFLIGHT),
            "--group", group,
            "--batch-size", str(self.batch_size),
            "--no-color",
        ]
        if self.workers is not None:
            cmd += ["--workers", str(self.workers)]
        if report is not None:
            cmd += ["--report", str(report)]
        cmd.extend(extra_flags)

        proc = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            capture_output=False,   # stream live to terminal
            text=True,
        )
        return {"exit_code": proc.returncode, "stdout": ""}

    @staticmethod
    def _parse_report(
        path: Path,
        group: str,
        report_path: Optional[Path],
    ) -> BatchScanResult:
        if not path.exists():
            # Preflight errored before writing report
            return BatchScanResult(
                group=group, ok=False,
                passed=0, failed=1, errors=0, skipped=0,
                duration_s=0.0, failures=["preflight_error"], batches_run=0,
            )

        data = json.loads(path.read_text())
        groups = data.get("groups", {})

        # For "all" mode aggregate; for a single group just use that key
        keys = list(groups.keys()) if group == "all" else [group]

        passed = sum(groups[k]["passed"] for k in keys if k in groups)
        failed = sum(groups[k]["failed"] for k in keys if k in groups)
        errors = sum(groups[k]["errors"] for k in keys if k in groups)
        skipped = sum(groups[k]["skipped"] for k in keys if k in groups)
        duration = sum(groups[k]["duration_s"] for k in keys if k in groups)
        batches = sum(groups[k]["batches"] for k in keys if k in groups)
        failures = []
        for k in keys:
            if k in groups:
                failures.extend(groups[k].get("failed_tests", []))

        return BatchScanResult(
            group=group,
            ok=data.get("overall_pass", False),
            passed=passed,
            failed=failed,
            errors=errors,
            skipped=skipped,
            duration_s=duration,
            failures=failures,
            batches_run=batches,
            report_path=report_path,
            raw=data,
        )


# ---------------------------------------------------------------------------
# CLI shim — makes ``python -m scripts.ci.batch_scan_integration`` work
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="BatchScanRunner CLI shim")
    p.add_argument("--group", default="quick",
                   choices=["quick", "slow", "integration", "docs", "all"])
    p.add_argument("--changed-only", action="store_true")
    p.add_argument("--fail-fast", action="store_true")
    p.add_argument("--report", metavar="PATH")
    p.add_argument("--workers", type=int)
    p.add_argument("--batch-size", type=int, default=30)
    args = p.parse_args()

    runner = BatchScanRunner(
        workers=args.workers,
        batch_size=args.batch_size,
    )
    result = runner.scan(
        group=args.group,
        changed_only=args.changed_only,
        fail_fast=args.fail_fast,
        report_path=Path(args.report) if args.report else None,
    )
    print(result.summary_line)
    sys.exit(0 if result.ok else 1)
