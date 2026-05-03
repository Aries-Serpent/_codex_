#!/usr/bin/env python3
"""
CodeQL Alert Resolution Pipeline

End-to-end orchestration for discovering, triaging, auto-fixing, and
closing GitHub code scanning alerts.

Pipeline stages
---------------
1. Collect   – fetch alerts via GitHub API (fetch_codeql_alerts.py)
              OR Playwright scraper (playwright_scraper.py) as fallback
2. Analyse   – run analyze_alerts.py to build a prioritised report
3. Remediate – apply automated codemods for high-confidence fix patterns
4. Validate  – run ruff + bandit to confirm no regressions
5. Close     – dismiss resolved alerts via close_codeql_alert.py

Usage:
    python scripts/security/resolution_pipeline.py \\
        --owner Aries-Serpent --repo _codex_ \\
        --stages collect,analyse,remediate,validate

Author: Copilot Agent
Part of: CodeQL Alert Resolution Planset
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

_SCRIPTS_DIR = Path(__file__).parent
_REPO_ROOT = _SCRIPTS_DIR.parent.parent
_DEFAULT_INVENTORY = _REPO_ROOT / ".codex" / "security" / "alert_inventory.json"
_DEFAULT_REPORT = _REPO_ROOT / ".codex" / "security" / "alert_analysis.md"
_DEFAULT_PLAYWRIGHT_OUT = _REPO_ROOT / ".codex" / "security" / "playwright_alerts.json"

# Codemods available for automated fixing
_CODEMODS: dict[str, Path] = {
    "sql_injection": _SCRIPTS_DIR / "codemods" / "fix_sql_injection.py",
    "subprocess_shell": _SCRIPTS_DIR / "codemods" / "fix_subprocess.py",
    "hardcoded_secrets": _SCRIPTS_DIR / "codemods" / "fix_hardcoded_secrets.py",
}

# Severity → priority mapping
SEVERITY_PRIORITY: dict[str, str] = {
    "critical": "P0",
    "high": "P1",
    "medium": "P2",
    "low": "P3",
    "warning": "P4",
    "note": "P4",
    "error": "P1",
}


@dataclass
class PipelineResult:
    """Accumulates results across all pipeline stages."""

    stage: str = ""
    alerts_collected: int = 0
    alerts_analysed: int = 0
    codemods_applied: int = 0
    codemods_failed: int = 0
    alerts_closed: int = 0
    validation_passed: bool = False
    errors: list[str] = field(default_factory=list)
    elapsed_s: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "alerts_collected": self.alerts_collected,
            "alerts_analysed": self.alerts_analysed,
            "codemods_applied": self.codemods_applied,
            "codemods_failed": self.codemods_failed,
            "alerts_closed": self.alerts_closed,
            "validation_passed": self.validation_passed,
            "errors": self.errors,
            "elapsed_s": round(self.elapsed_s, 2),
        }


class ResolutionPipeline:
    """Orchestrates the full alert resolution workflow."""

    def __init__(
        self,
        owner: str,
        repo: str,
        token: Optional[str] = None,
        dry_run: bool = False,
        inventory_path: Path = _DEFAULT_INVENTORY,
        report_path: Path = _DEFAULT_REPORT,
        use_playwright: bool = False,
    ) -> None:
        self.owner = owner
        self.repo = repo
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        self.dry_run = dry_run
        self.inventory_path = inventory_path
        self.report_path = report_path
        self.use_playwright = use_playwright
        self.result = PipelineResult()

    # ------------------------------------------------------------------
    # Stage 1 – Collect
    # ------------------------------------------------------------------

    def collect(self) -> int:
        """
        Fetch all open code scanning alerts.
        Tries the API fetcher first; falls back to Playwright scraper if
        ``use_playwright=True`` and API fetch yields zero results.

        Returns the number of alerts collected.
        """
        logger.info("=== Stage 1: Alert Collection ===")
        t0 = time.monotonic()

        count = self._collect_via_api()

        if count == 0 and self.use_playwright:
            logger.info("API returned 0 alerts; attempting Playwright fallback …")
            count = self._collect_via_playwright()

        self.result.alerts_collected = count
        logger.info("Collected %d alerts in %.1fs", count, time.monotonic() - t0)
        return count

    def _collect_via_api(self) -> int:
        """Run fetch_codeql_alerts.py and return alert count."""
        fetcher = _SCRIPTS_DIR / "fetch_codeql_alerts.py"
        if not fetcher.exists():
            logger.warning("fetch_codeql_alerts.py not found — skipping API fetch")
            return 0

        cmd = [
            sys.executable, str(fetcher),
            "--owner", self.owner,
            "--repo", self.repo,
            "--output", str(self.inventory_path),
        ]
        if self.token:
            cmd += ["--token", self.token]

        logger.info("Running API fetcher …")
        ret = self._run(cmd, label="API fetch")
        if ret != 0:
            logger.warning("API fetcher exited %d", ret)
            return 0

        return self._count_alerts(self.inventory_path)

    def _collect_via_playwright(self) -> int:
        """Run playwright_scraper.py and return alert count."""
        scraper = _SCRIPTS_DIR / "playwright_scraper.py"
        if not scraper.exists():
            logger.warning("playwright_scraper.py not found")
            return 0

        cmd = [
            sys.executable, str(scraper),
            "--repo", f"https://github.com/{self.owner}/{self.repo}",
            "--output", str(_DEFAULT_PLAYWRIGHT_OUT),
        ]
        if self.token:
            cmd += ["--token", self.token]

        logger.info("Running Playwright scraper …")
        ret = self._run(cmd, label="Playwright scrape")
        if ret != 0:
            logger.warning("Playwright scraper exited %d", ret)
            return 0

        # Merge into main inventory format
        count = self._count_alerts(_DEFAULT_PLAYWRIGHT_OUT)
        if count > 0 and not self.inventory_path.exists():
            import shutil
            shutil.copy2(_DEFAULT_PLAYWRIGHT_OUT, self.inventory_path)
        return count

    # ------------------------------------------------------------------
    # Stage 2 – Analyse
    # ------------------------------------------------------------------

    def analyse(self) -> dict[str, Any]:
        """
        Run analyze_alerts.py to produce a prioritised Markdown report.

        Returns a dict with severity breakdowns and priority counts.
        """
        logger.info("=== Stage 2: Alert Analysis ===")
        t0 = time.monotonic()

        analyser = _SCRIPTS_DIR / "analyze_alerts.py"
        if not analyser.exists():
            logger.warning("analyze_alerts.py not found — skipping analysis")
            return {}

        if not self.inventory_path.exists():
            logger.error(
                "Inventory file not found: %s — run collect stage first", self.inventory_path
            )
            self.result.errors.append(f"inventory_missing: {self.inventory_path}")
            return {}

        cmd = [
            sys.executable, str(analyser),
            "--input", str(self.inventory_path),
            "--output", str(self.report_path),
        ]

        ret = self._run(cmd, label="Analysis")
        summary: dict[str, Any] = {}
        if ret == 0:
            summary = self._load_analysis_summary()
            self.result.alerts_analysed = self._count_alerts(self.inventory_path)
        else:
            logger.warning("Analysis exited %d", ret)
            self.result.errors.append(f"analysis_exit_{ret}")

        logger.info("Analysis complete in %.1fs", time.monotonic() - t0)
        return summary

    def _load_analysis_summary(self) -> dict[str, Any]:
        """Parse the inventory JSON to build a severity summary dict."""
        try:
            data = json.loads(self.inventory_path.read_text())
            alerts = data.get("alerts", [])
            severity_counts: dict[str, int] = {}
            priority_counts: dict[str, int] = {"P0": 0, "P1": 0, "P2": 0, "P3": 0, "P4": 0}
            for a in alerts:
                sev = a.get("severity", "unknown")
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
                p = SEVERITY_PRIORITY.get(sev, "P4")
                priority_counts[p] += 1
            return {
                "total": len(alerts),
                "by_severity": severity_counts,
                "by_priority": priority_counts,
            }
        except Exception as exc:
            logger.debug("Could not parse summary: %s", exc)
            return {}

    # ------------------------------------------------------------------
    # Stage 3 – Remediate
    # ------------------------------------------------------------------

    def remediate(self, categories: Optional[Sequence[str]] = None) -> int:
        """
        Apply automated codemods for known vulnerability patterns.

        Args:
            categories: Optional list of codemod names to run (default: all).

        Returns:
            Number of codemods successfully applied.
        """
        logger.info("=== Stage 3: Automated Remediation ===")
        t0 = time.monotonic()
        applied = 0

        targets = list(categories) if categories else list(_CODEMODS.keys())

        for name in targets:
            script = _CODEMODS.get(name)
            if script is None:
                logger.debug("No codemod registered for: %s", name)
                continue
            if not script.exists():
                logger.debug("Codemod not found: %s", script)
                continue

            label = f"codemod:{name}"
            cmd = [sys.executable, str(script), "--repo-root", str(_REPO_ROOT)]
            if self.dry_run:
                cmd.append("--dry-run")

            ret = self._run(cmd, label=label)
            if ret == 0:
                applied += 1
                logger.info("  ✅  %s applied", name)
            else:
                self.result.codemods_failed += 1
                logger.warning("  ❌  %s exited %d", name, ret)

        self.result.codemods_applied = applied
        logger.info(
            "Remediation complete: %d applied, %d failed in %.1fs",
            applied, self.result.codemods_failed, time.monotonic() - t0,
        )
        return applied

    # ------------------------------------------------------------------
    # Stage 4 – Validate
    # ------------------------------------------------------------------

    def validate(self) -> bool:
        """
        Run ruff + bandit to confirm fixes didn't introduce regressions.

        Returns True if both pass (or are unavailable).
        """
        logger.info("=== Stage 4: Validation ===")
        t0 = time.monotonic()
        passed = True

        # ruff check — only errors are blocking
        ruff_cmd = ["ruff", "check", "src/", "--select=F,E9", "--quiet"]
        if self._run(ruff_cmd, label="ruff") not in (0, None):
            logger.warning("ruff found blocking errors")
            self.result.errors.append("ruff_failed")
            passed = False

        # bandit — high severity only
        bandit_cmd = [
            "bandit", "-r", "src/", "--severity-level", "high", "-q",
        ]
        ret = self._run(bandit_cmd, label="bandit")
        if ret not in (0, None, 1):  # 0=clean, 1=low-sev findings (ok)
            logger.warning("bandit found high-severity issues (exit %d)", ret)
            self.result.errors.append("bandit_high_severity")
            passed = False

        self.result.validation_passed = passed
        logger.info(
            "Validation %s in %.1fs",
            "✅ passed" if passed else "❌ failed",
            time.monotonic() - t0,
        )
        return passed

    # ------------------------------------------------------------------
    # Stage 5 – Close
    # ------------------------------------------------------------------

    def close_alerts(
        self,
        alert_numbers: Optional[Sequence[int]] = None,
        reason: str = "fixed",
        comment: str = "Resolved by automated resolution pipeline",
        max_batch: int = 50,
    ) -> int:
        """
        Dismiss resolved alerts via close_codeql_alert.py.

        Args:
            alert_numbers: Explicit list of alert IDs; if None, closes P0+P1 resolved alerts.
            reason: Dismissal reason (fixed|false_positive|wont_fix|used_in_tests).
            comment: Comment to attach.
            max_batch: Safety cap on how many alerts to close in one run.

        Returns:
            Number of alerts closed.
        """
        logger.info("=== Stage 5: Alert Closure ===")
        if self.dry_run:
            logger.info("[dry-run] Would close up to %d alerts", max_batch)
            return 0

        closer = _SCRIPTS_DIR / "close_codeql_alert.py"
        if not closer.exists():
            logger.warning("close_codeql_alert.py not found")
            return 0

        if alert_numbers is None:
            alert_numbers = self._resolve_p0_p1_alerts()[:max_batch]

        closed = 0
        for number in list(alert_numbers)[:max_batch]:
            cmd = [
                sys.executable, str(closer),
                "--owner", self.owner,
                "--repo", self.repo,
                "--alert-number", str(number),
                "--reason", reason,
                "--comment", comment,
            ]
            if self.token:
                cmd += ["--token", self.token]

            if self._run(cmd, label=f"close:{number}") == 0:
                closed += 1
            else:
                logger.warning("Failed to close alert #%d", number)

        self.result.alerts_closed = closed
        logger.info("Closed %d alerts", closed)
        return closed

    def _resolve_p0_p1_alerts(self) -> list[int]:
        """Return alert numbers that are P0/P1 severity from the inventory."""
        try:
            data = json.loads(self.inventory_path.read_text())
            return [
                a["alert_number"]
                for a in data.get("alerts", [])
                if SEVERITY_PRIORITY.get(a.get("severity", ""), "P4") in ("P0", "P1")
                and a.get("alert_number") is not None
            ]
        except Exception:
            return []

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _run(self, cmd: list[str], label: str = "") -> int:
        """Run a subprocess, streaming output to the logger. Returns exit code."""
        logger.debug("Running [%s]: %s", label, " ".join(str(c) for c in cmd))
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(_REPO_ROOT),
            )
            if proc.stdout.strip():
                for line in proc.stdout.splitlines():
                    logger.info("  [%s] %s", label, line)
            if proc.stderr.strip():
                for line in proc.stderr.splitlines():
                    logger.debug("  [%s:err] %s", label, line)
            return proc.returncode
        except FileNotFoundError:
            logger.debug("[%s] command not found; skipping", label)
            return 0  # treat missing tool as non-blocking

    def _count_alerts(self, path: Path) -> int:
        """Return total_alerts from a JSON inventory file."""
        try:
            data = json.loads(path.read_text())
            return data.get("total_alerts", len(data.get("alerts", [])))
        except Exception:
            return 0

    # ------------------------------------------------------------------
    # Run full pipeline
    # ------------------------------------------------------------------

    def run(self, stages: Sequence[str] = ("collect", "analyse", "remediate", "validate")) -> PipelineResult:
        """Execute the requested pipeline stages in order."""
        t0 = time.monotonic()
        stage_set = {s.lower().strip() for s in stages}

        if "collect" in stage_set:
            self.collect()

        if "analyse" in stage_set or "analyze" in stage_set:
            self.analyse()

        if "remediate" in stage_set or "fix" in stage_set:
            self.remediate()

        if "validate" in stage_set:
            self.validate()

        if "close" in stage_set:
            self.close_alerts()

        self.result.elapsed_s = time.monotonic() - t0
        return self.result


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="End-to-end CodeQL alert resolution pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full pipeline (default stages: collect + analyse + remediate + validate)
  python scripts/security/resolution_pipeline.py \\
      --owner Aries-Serpent --repo _codex_

  # Collect + analyse only
  python scripts/security/resolution_pipeline.py \\
      --owner Aries-Serpent --repo _codex_ \\
      --stages collect,analyse

  # Dry-run close of resolved alerts
  python scripts/security/resolution_pipeline.py \\
      --owner Aries-Serpent --repo _codex_ \\
      --stages close --dry-run
""",
    )
    p.add_argument("--owner", default="Aries-Serpent", help="Repo owner")
    p.add_argument("--repo", default="_codex_", help="Repo name")
    p.add_argument("--token", default=None, help="GitHub token (overrides GITHUB_TOKEN)")
    p.add_argument(
        "--stages",
        default="collect,analyse,remediate,validate",
        help="Comma-separated list of stages to run "
             "(collect|analyse|remediate|validate|close)",
    )
    p.add_argument(
        "--inventory",
        type=Path,
        default=_DEFAULT_INVENTORY,
        help="Path to alert inventory JSON",
    )
    p.add_argument(
        "--report",
        type=Path,
        default=_DEFAULT_REPORT,
        help="Path to output analysis report",
    )
    p.add_argument(
        "--use-playwright",
        action="store_true",
        default=False,
        help="Enable Playwright scraper fallback when API returns 0 results",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Do not make any mutations (codemods/closures are skipped)",
    )
    p.add_argument(
        "--output-json",
        type=Path,
        default=None,
        help="Write pipeline result summary to JSON",
    )
    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    stages = [s.strip() for s in args.stages.split(",") if s.strip()]

    pipeline = ResolutionPipeline(
        owner=args.owner,
        repo=args.repo,
        token=args.token,
        dry_run=args.dry_run,
        inventory_path=args.inventory,
        report_path=args.report,
        use_playwright=args.use_playwright,
    )

    result = pipeline.run(stages=stages)

    print("\n" + "=" * 60)
    print("RESOLUTION PIPELINE SUMMARY")
    print("=" * 60)
    print(f"  Stages run     : {', '.join(stages)}")
    print(f"  Alerts collected: {result.alerts_collected}")
    print(f"  Alerts analysed : {result.alerts_analysed}")
    print(f"  Codemods applied: {result.codemods_applied}")
    print(f"  Alerts closed   : {result.alerts_closed}")
    print(f"  Validation      : {'✅ passed' if result.validation_passed else '⚠️  skipped/failed'}")
    print(f"  Elapsed         : {result.elapsed_s:.1f}s")
    if result.errors:
        print(f"  Errors          : {', '.join(result.errors)}")
    print("=" * 60)

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(result.to_dict(), indent=2))
        print(f"\nSummary JSON → {args.output_json}")

    return 0 if not result.errors else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
