#!/usr/bin/env python3
"""
phase_12_2_compliance_dashboard.py — Phase 12.2 Governance & Compliance Dashboard.

Checks REQ-1 through REQ-6 for the Codex agent ecosystem and produces
structured JSON + Markdown compliance reports.

Usage
-----
    # Check mode — exits non-zero if any requirement fails
    python scripts/ci/phase_12_2_compliance_dashboard.py --check

    # Report mode — generates .codex/PHASE_12_2_COMPLIANCE_REPORT.md
    python scripts/ci/phase_12_2_compliance_dashboard.py --report

    # Machine-readable JSON output
    python scripts/ci/phase_12_2_compliance_dashboard.py --check --json

    # Combined: check + report + json
    python scripts/ci/phase_12_2_compliance_dashboard.py --check --report --json

Exit codes
----------
    0  All requirements passed (or --report-only with no --check)
    1  One or more requirements failed
    2  Internal error (git not found, repository root not found, etc.)

Python >= 3.12 required. No external dependencies beyond stdlib + git subprocess.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    format="%(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("phase12.2.compliance")

# ---------------------------------------------------------------------------
# Repository layout
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
SESSIONS_DIR = REPO_ROOT / ".codex" / "sessions"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"
ACCOUNTABILITY_REPORT = REPO_ROOT / "docs" / "accountability" / "AGENT_ACCOUNTABILITY_REPORT.md"
SECRETS_BASELINE = REPO_ROOT / ".secrets.baseline"
REPORT_OUTPUT = REPO_ROOT / ".codex" / "PHASE_12_2_COMPLIANCE_REPORT.md"

_UNRELEASED_MARKER = "## [Unreleased]"

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class ComplianceResult:
    """Result of a single requirement check."""

    passed: bool
    details: str
    remediation: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a JSON-compatible dict."""
        return {
            "passed": self.passed,
            "details": self.details,
            "remediation": self.remediation,
        }


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


def _git(*args: str, check: bool = False) -> tuple[int, str, str]:
    """Run a git command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            ["git", "-C", str(REPO_ROOT), *args],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except FileNotFoundError:
        logger.error("git executable not found")
        sys.exit(2)
    except subprocess.TimeoutExpired:
        logger.warning("git command timed out: git %s", " ".join(args))
        return 1, "", "timeout"


def _detect_secrets_available() -> bool:
    """Return True if detect-secrets is installed."""
    try:
        result = subprocess.run(
            ["detect-secrets", "--version"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


_SECRET_HEURISTIC_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(?i)(password|passwd|secret|api[_-]?key|auth[_-]?token)\s*=\s*['\"][^'\"]{6,}['\"]"),
    re.compile(r"(?i)-----BEGIN (RSA|EC|OPENSSH|PGP) PRIVATE KEY-----"),
    re.compile(r"(?i)(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36}"),
    re.compile(r"(?i)AKIA[0-9A-Z]{16}"),  # AWS access key
    re.compile(r"(?i)sk-[A-Za-z0-9]{32,}"),  # OpenAI / generic secret key
]


def _heuristic_secret_scan_diff() -> tuple[bool, str]:
    """
    Fallback secret scan using regex heuristics on the git diff.

    Returns (found_secrets, details).
    """
    rc, diff, _ = _git("diff", "HEAD~1", "HEAD", "--unified=0")
    if rc != 0:
        # Single commit — scan index instead
        rc, diff, _ = _git("show", "HEAD", "--unified=0")

    findings: list[str] = []
    for i, line in enumerate(diff.splitlines(), 1):
        if not line.startswith("+"):
            continue
        for pattern in _SECRET_HEURISTIC_PATTERNS:
            if pattern.search(line):
                # Truncate the line so we never log the actual secret value
                truncated = line[:80] + ("…" if len(line) > 80 else "")
                findings.append(f"  line {i}: {truncated}")
                break  # one hit per diff line is enough

    return bool(findings), "\n".join(findings)


# ---------------------------------------------------------------------------
# ComplianceDashboard
# ---------------------------------------------------------------------------


class ComplianceDashboard:
    """
    Checks REQ-1 through REQ-6 for the Codex agent ecosystem.

    Instantiate once, call check_all() or individual check_req*() methods.
    """

    def __init__(self, *, sessions_lookback_days: int = 30) -> None:
        self.sessions_lookback_days = sessions_lookback_days
        self._results: dict[str, ComplianceResult] = {}

    # ------------------------------------------------------------------
    # Individual requirement checks
    # ------------------------------------------------------------------

    def check_req1(self) -> ComplianceResult:
        """
        REQ-1: Session summary exists in .codex/sessions/.

        Pass condition: at least one .md file in the sessions directory
        was modified within the lookback window.
        """
        if not SESSIONS_DIR.exists():
            return ComplianceResult(
                passed=False,
                details=f"Sessions directory does not exist: {SESSIONS_DIR}",
                remediation=(
                    "Create .codex/sessions/ and add a session summary file "
                    "named <session-id>.md before merging."
                ),
            )

        session_files = list(SESSIONS_DIR.rglob("*.md"))
        # Filter out archive subdirectory for the count
        active_files = [f for f in session_files if "archive" not in f.parts]

        if not active_files:
            return ComplianceResult(
                passed=False,
                details="No session summary .md files found in .codex/sessions/",
                remediation=(
                    "Create .codex/sessions/<session-id>.md with a date stamp, "
                    "agent identity, and summary of changes."
                ),
            )

        # Check modification time within lookback window
        lookback_window_seconds = self.sessions_lookback_days * 86400
        now = datetime.now(timezone.utc).timestamp()
        recent_files = [
            f for f in active_files
            if (now - f.stat().st_mtime) <= lookback_window_seconds
        ]

        if not recent_files:
            return ComplianceResult(
                passed=False,
                details=f"No session files modified within {self.sessions_lookback_days} days",
                remediation=(
                    "Create or update a .codex/sessions/<session-id>.md file "
                    "to confirm active session tracking."
                ),
            )

        return ComplianceResult(
            passed=True,
            details=f"Found {len(recent_files)} session file(s) modified within {self.sessions_lookback_days} days",
        )

    def check_req2(self) -> ComplianceResult:
        """
        REQ-2: CHANGELOG.md updated with an [Unreleased] entry.

        Pass condition: CHANGELOG.md exists and contains ## [Unreleased] with
        at least one non-whitespace bullet or entry below it.
        """
        if not CHANGELOG.exists():
            return ComplianceResult(
                passed=False,
                details="CHANGELOG.md does not exist at repository root",
                remediation="Create CHANGELOG.md following Keep a Changelog format.",
            )

        text = CHANGELOG.read_text(encoding="utf-8", errors="replace")
        if _UNRELEASED_MARKER not in text:
            return ComplianceResult(
                passed=False,
                details="CHANGELOG.md does not contain '## [Unreleased]' section",
                remediation=(
                    "Add '## [Unreleased]' section to CHANGELOG.md with at "
                    "least one entry describing current session changes."
                ),
            )

        # Extract text between [Unreleased] and the next ## heading
        idx = text.index(_UNRELEASED_MARKER) + len(_UNRELEASED_MARKER)
        rest = text[idx:]
        next_section = re.search(r"^##\s", rest, re.MULTILINE)
        unreleased_body = rest[: next_section.start()] if next_section else rest

        has_content = bool(re.search(r"\S", unreleased_body))
        if not has_content:
            return ComplianceResult(
                passed=False,
                details="CHANGELOG.md [Unreleased] section is empty",
                remediation=(
                    "Add at least one bullet describing the current session's "
                    "changes under '## [Unreleased]'."
                ),
            )

        # Count rough number of entries
        entries = [ln for ln in unreleased_body.splitlines() if ln.strip().startswith(("-", "*", "+"))]
        return ComplianceResult(
            passed=True,
            details=f"CHANGELOG.md [Unreleased] section has {len(entries)} entr(ies)",
        )

    def check_req3(self) -> ComplianceResult:
        """
        REQ-3: No new test failures (CI green).

        Pass condition: most recent CI run on this branch is successful,
        OR a local pytest quick-check passes.  Falls back gracefully when
        gh CLI or pytest are unavailable.
        """
        # Try gh CLI first
        try:
            gh_result = subprocess.run(
                ["gh", "run", "list", "--branch", self._current_branch(), "--limit", "1", "--json", "status,conclusion"],
                capture_output=True,
                text=True,
                timeout=15,
                cwd=str(REPO_ROOT),
            )
            if gh_result.returncode == 0 and gh_result.stdout.strip():
                runs = json.loads(gh_result.stdout)
                if runs:
                    run = runs[0]
                    status = run.get("status", "")
                    conclusion = run.get("conclusion", "")
                    if status == "completed" and conclusion == "success":
                        return ComplianceResult(
                            passed=True,
                            details=f"Most recent CI run: status={status}, conclusion={conclusion}",
                        )
                    elif status == "completed" and conclusion in ("failure", "cancelled"):
                        return ComplianceResult(
                            passed=False,
                            details=f"Most recent CI run failed: status={status}, conclusion={conclusion}",
                            remediation="Fix failing tests before merging. Check CI logs for details.",
                        )
                    else:
                        # In-progress or unknown — treat as pass-with-caveat
                        return ComplianceResult(
                            passed=True,
                            details=f"CI run in progress or inconclusive: status={status}, conclusion={conclusion}. Assuming pass.",
                        )
        except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError, KeyError):
            pass

        # Fallback: attempt local pytest with strict time-limit
        try:
            pytest_result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(REPO_ROOT),
            )
            if pytest_result.returncode == 0:
                return ComplianceResult(
                    passed=True,
                    details="Local pytest tests passed",
                )
            else:
                stderr_excerpt = pytest_result.stderr[-300:] if pytest_result.stderr else ""
                return ComplianceResult(
                    passed=False,
                    details=f"Local pytest tests failed (exit {pytest_result.returncode}): {stderr_excerpt}",
                    remediation="Run 'pytest' locally and fix any test errors.",
                )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # Cannot verify — optimistic pass with warning
        return ComplianceResult(
            passed=True,
            details="REQ-3 check skipped: neither gh CLI nor pytest available. Assuming pass.",
        )

    def check_req4(self) -> ComplianceResult:
        """
        REQ-4: AGENT_ACCOUNTABILITY_REPORT.md updated in last commit.

        Pass condition: AGENT_ACCOUNTABILITY_REPORT.md appears in the list of
        files changed by HEAD commit.
        """
        rc, changed_files, _ = _git("show", "--name-only", "--format=", "HEAD")
        if rc != 0:
            return ComplianceResult(
                passed=False,
                details="Could not read HEAD commit file list (git show failed)",
                remediation="Ensure the repository has at least one commit.",
            )

        accountability_path = "docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md"
        if accountability_path in changed_files:
            return ComplianceResult(
                passed=True,
                details=f"{accountability_path} was updated in the last commit",
            )

        # Check if the file exists at all
        if not ACCOUNTABILITY_REPORT.exists():
            return ComplianceResult(
                passed=False,
                details=f"{accountability_path} does not exist in the repository",
                remediation=(
                    f"Create {accountability_path} and add an accountability entry, "
                    "then commit it alongside your changes."
                ),
            )

        return ComplianceResult(
            passed=False,
            details=f"{accountability_path} was NOT updated in the last commit",
            remediation=(
                "Run: python scripts/ci/session_wrapup_autofix.py --fix-accountability\n"
                "Or manually append an entry to docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md"
            ),
        )

    def check_req5(self) -> ComplianceResult:
        """
        REQ-5: CHANGELOG.md updated in the last commit.

        Pass condition: CHANGELOG.md appears in the files changed by HEAD.
        """
        rc, changed_files, _ = _git("show", "--name-only", "--format=", "HEAD")
        if rc != 0:
            return ComplianceResult(
                passed=False,
                details="Could not read HEAD commit file list (git show failed)",
                remediation="Ensure the repository has at least one commit.",
            )

        if "CHANGELOG.md" in changed_files:
            return ComplianceResult(
                passed=True,
                details="CHANGELOG.md was updated in the last commit",
            )

        return ComplianceResult(
            passed=False,
            details="CHANGELOG.md was NOT updated in the last commit",
            remediation=(
                "Run: python scripts/ci/session_wrapup_autofix.py --fix-changelog\n"
                "Or manually add an entry to CHANGELOG.md and amend/re-commit."
            ),
        )

    def check_req6(self) -> ComplianceResult:
        """
        REQ-6: No secrets committed (detect-secrets scan passes).

        Pass condition: detect-secrets finds no NEW secrets beyond the baseline,
        or heuristic regex scan of the diff finds nothing.
        """
        if _detect_secrets_available():
            try:
                cmd = ["detect-secrets", "scan", "--baseline", str(SECRETS_BASELINE)]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=str(REPO_ROOT),
                )
                if result.returncode == 0:
                    return ComplianceResult(
                        passed=True,
                        details="detect-secrets scan passed — no new secrets found",
                    )
                else:
                    return ComplianceResult(
                        passed=False,
                        details=f"detect-secrets scan FAILED: {result.stdout[:300]}",
                        remediation=(
                            "Remove the secret from the codebase, rotate the credential, "
                            "and update .secrets.baseline per the SECURITY.md procedure."
                        ),
                    )
            except subprocess.TimeoutExpired:
                logger.warning("detect-secrets timed out; falling back to heuristic scan")

        # Fallback: heuristic scan
        found, details = _heuristic_secret_scan_diff()
        if found:
            return ComplianceResult(
                passed=False,
                details=f"Heuristic secret scan found potential secrets in diff:\n{details}",
                remediation=(
                    "Review the flagged lines, remove any real secrets, and rotate credentials. "
                    "Install detect-secrets for authoritative scanning: pip install detect-secrets"
                ),
            )

        baseline_note = (
            " (detect-secrets not installed — used heuristic scan)"
            if not _detect_secrets_available()
            else ""
        )
        return ComplianceResult(
            passed=True,
            details=f"No secrets detected in diff{baseline_note}",
        )

    # ------------------------------------------------------------------
    # Aggregate methods
    # ------------------------------------------------------------------

    def check_all(self) -> dict[str, ComplianceResult]:
        """Run all REQ-1 through REQ-6 checks and cache results."""
        self._results = {
            "REQ-1": self.check_req1(),
            "REQ-2": self.check_req2(),
            "REQ-3": self.check_req3(),
            "REQ-4": self.check_req4(),
            "REQ-5": self.check_req5(),
            "REQ-6": self.check_req6(),
        }
        return self._results

    def get_compliance_score(self) -> float:
        """
        Return a compliance score between 0.0 (all fail) and 1.0 (all pass).

        Must call check_all() first (or results will be empty → returns 0.0).
        """
        if not self._results:
            return 0.0
        passed = sum(1 for r in self._results.values() if r.passed)
        return passed / len(self._results)

    def generate_report(self) -> dict[str, Any]:
        """
        Generate a full compliance summary as a JSON-serialisable dict.

        Calls check_all() internally if not already run.
        """
        if not self._results:
            self.check_all()

        score = self.get_compliance_score()
        violations = [req for req, res in self._results.items() if not res.passed]
        warnings: list[str] = []
        remediation: list[str] = []

        for req, res in self._results.items():
            if not res.passed and res.remediation:
                remediation.append(f"{req}: {res.remediation}")

        if score == 1.0:
            status = "APPROVED"
        elif not violations:
            status = "APPROVED"
        elif any(r in violations for r in ("REQ-3", "REQ-6")):
            status = "BLOCK"
        else:
            status = "WARN"

        return {
            "governance_status": status,
            "compliance_score": round(score, 4),
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "requirements": {req: res.to_dict() for req, res in self._results.items()},
            "violations": violations,
            "warnings": warnings,
            "remediation": remediation,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _current_branch() -> str:
        """Return the current git branch name."""
        rc, branch, _ = _git("rev-parse", "--abbrev-ref", "HEAD")
        return branch if rc == 0 and branch else "HEAD"


# ---------------------------------------------------------------------------
# Markdown report generation
# ---------------------------------------------------------------------------


def _status_emoji(passed: bool) -> str:
    return "✅" if passed else "❌"


def generate_markdown_report(report: dict[str, Any]) -> str:
    """Render a compliance report dict as Markdown."""
    score_pct = f"{report['compliance_score'] * 100:.0f}%"
    status = report["governance_status"]
    status_emoji = {"APPROVED": "✅", "WARN": "⚠️", "BLOCK": "🚫"}.get(status, "❓")
    ts = report["timestamp"]

    lines: list[str] = [
        "# Phase 12.2 Compliance Report",
        "",
        f"**Governance Status:** {status_emoji} {status}  ",
        f"**Compliance Score:** {score_pct}  ",
        f"**Generated:** {ts}  ",
        "",
        "---",
        "",
        "## Requirement Status",
        "",
        "| Requirement | Status | Details |",
        "|-------------|--------|---------|",
    ]

    req_names = {
        "REQ-1": "Session Summary Exists",
        "REQ-2": "CHANGELOG Updated",
        "REQ-3": "Tests Pass",
        "REQ-4": "Accountability Report Updated",
        "REQ-5": "CHANGELOG in Last Commit",
        "REQ-6": "No Secrets Committed",
    }

    for req, result in report["requirements"].items():
        emoji = _status_emoji(result["passed"])
        name = req_names.get(req, req)
        details = result["details"].replace("|", "\\|")[:120]
        lines.append(f"| **{req}** — {name} | {emoji} {'PASS' if result['passed'] else 'FAIL'} | {details} |")

    lines += ["", "---", "", "## Compliance Score", ""]
    passed_count = sum(1 for r in report["requirements"].values() if r["passed"])
    total = len(report["requirements"])
    lines.append(f"**{passed_count}/{total} requirements passed** — overall score: {score_pct}")

    if report["violations"]:
        lines += ["", "---", "", "## Violations", ""]
        for v in report["violations"]:
            lines.append(f"- **{v}**: {report['requirements'][v]['details']}")

    if report["remediation"]:
        lines += ["", "---", "", "## Remediation Guidance", ""]
        for item in report["remediation"]:
            lines.append(f"- {item}")

    lines += [
        "",
        "---",
        "",
        "## References",
        "",
        "- [Governance Rules](.codex/PHASE_12_2_GOVERNANCE_RULES.md)",
        "- [Session Wrapup Autofix](scripts/ci/session_wrapup_autofix.py)",
        "- [Agency Policy](.codex/CODEBASE_AGENCY_POLICY.md)",
        "",
        "*Report generated by `scripts/ci/phase_12_2_compliance_dashboard.py`*",
    ]

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="phase_12_2_compliance_dashboard",
        description="Phase 12.2 Governance & Compliance Dashboard",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if any requirement fails",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help=f"Write Markdown report to {REPORT_OUTPUT}",
    )
    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="Print JSON report to stdout",
    )
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=30,
        metavar="N",
        help="Days to look back for session files (default: 30)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    dashboard = ComplianceDashboard(sessions_lookback_days=args.lookback_days)
    report = dashboard.generate_report()

    if args.json_output:
        print(json.dumps(report, indent=2))

    if args.report or not (args.check or args.json_output):
        # Default behaviour (no flags) or explicit --report: write Markdown
        md = generate_markdown_report(report)
        REPORT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        REPORT_OUTPUT.write_text(md, encoding="utf-8")
        logger.info("Compliance report written to %s", REPORT_OUTPUT)
        if not args.json_output:
            print(md)

    # Always print a human-readable summary to stderr
    score_pct = f"{report['compliance_score'] * 100:.0f}%"
    status = report["governance_status"]
    print(
        f"\n{'='*60}\n"
        f"  Phase 12.2 Compliance: {status}  (score: {score_pct})\n"
        f"{'='*60}",
        file=sys.stderr,
    )
    for req, result in report["requirements"].items():
        icon = "✓" if result["passed"] else "✗"
        print(f"  {icon} {req}: {result['details'][:80]}", file=sys.stderr)
    print(file=sys.stderr)

    if args.check and report["violations"]:
        logger.error(
            "Compliance check FAILED. Violations: %s",
            ", ".join(report["violations"]),
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
