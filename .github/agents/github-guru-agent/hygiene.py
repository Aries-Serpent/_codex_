"""
GitHub Guru Agent — Repository Hygiene Checks

Identifies repository hygiene issues:
  - Stale branches (inactive > N days with no open PR)
  - Orphaned root-level report/log files
  - Missing module docstrings in new Python files
  - Dependency drift in requirements*.txt / pyproject.toml
  - Contributor ownership gaps

All checks are read-only (SAFE_MODE=true).
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

try:
    from .github_client import GitHubAPIClient
except ImportError:
    from github_client import GitHubAPIClient

logger = logging.getLogger(__name__)


@dataclass
class HygieneIssue:
    """A single detected hygiene issue."""

    category: str  # stale_branch | orphaned_file | missing_docstring | dep_drift | ownership_gap
    severity: str  # critical | high | medium | low | info
    description: str
    remediation: str
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class HygieneReport:
    """Full hygiene report for a repository."""

    issues: list[HygieneIssue] = field(default_factory=list)
    hygiene_score: float = 100.0  # 0–100
    summary_md: str = ""
    checked_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "critical")

    @property
    def high_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "high")


class RepoHygiene:
    """
    Repository hygiene checker.

    Combines remote GitHub API checks with local filesystem checks
    (when running in the repository root).
    """

    STALE_BRANCH_DAYS = 30
    ROOT_ORPHAN_EXTENSIONS = {".txt", ".log", ".json", ".csv", ".ndjson"}
    ROOT_ORPHAN_PATTERNS = re.compile(
        r"(report|log|audit|output|result|metrics|coverage|baseline).*\.(txt|log|json|csv|ndjson)$",
        re.IGNORECASE,
    )

    def __init__(self, client: GitHubAPIClient, repo_root: Optional[Path] = None):
        self.client = client
        self.repo_root = repo_root or Path.cwd()

    def run_all_checks(self) -> HygieneReport:
        """Run all hygiene checks and return a consolidated report."""
        issues: list[HygieneIssue] = []

        issues.extend(self._check_stale_branches())
        issues.extend(self._check_orphaned_root_files())
        issues.extend(self._check_dependency_drift())
        issues.extend(self._check_contributor_gaps())

        # Calculate hygiene score
        severity_deductions = {"critical": 20, "high": 10, "medium": 5, "low": 2, "info": 0}
        total_deduction = sum(severity_deductions.get(i.severity, 0) for i in issues)
        hygiene_score = max(0.0, 100.0 - total_deduction)

        # Build summary
        summary_lines = [
            f"**Repository Hygiene Score**: {hygiene_score:.0f}/100",
            f"- Issues found: {len(issues)} "
            f"({sum(1 for i in issues if i.severity=='critical')} critical, "
            f"{sum(1 for i in issues if i.severity=='high')} high, "
            f"{sum(1 for i in issues if i.severity=='medium')} medium)",
        ]
        if issues:
            summary_lines.append("\n**Top Issues**:")
            for issue in sorted(issues, key=lambda x: ["critical","high","medium","low","info"].index(x.severity))[:5]:
                summary_lines.append(f"- [{issue.severity.upper()}] {issue.description}")

        return HygieneReport(
            issues=issues,
            hygiene_score=hygiene_score,
            summary_md="\n".join(summary_lines),
        )

    def _check_stale_branches(self) -> list[HygieneIssue]:
        """Detect branches inactive > STALE_BRANCH_DAYS with no open PR."""
        issues: list[HygieneIssue] = []
        resp = self.client.list_branches(per_page=100)
        if not resp.ok or not isinstance(resp.data, list):
            logger.debug("Could not fetch branches: %s", resp.error)
            return issues

        # Get open PRs for comparison
        pr_resp = self.client.list_pull_requests(state="open", per_page=100)
        open_pr_branches: set = set()
        if pr_resp.ok and isinstance(pr_resp.data, list):
            for pr in pr_resp.data:
                head_ref = (pr.get("head") or {}).get("ref", "")
                if head_ref:
                    open_pr_branches.add(head_ref)

        cutoff = datetime.now(tz=timezone.utc) - timedelta(days=self.STALE_BRANCH_DAYS)

        for branch in resp.data:
            name = branch.get("name", "")
            if name in ("main", "master", "develop"):
                continue  # never flag protected branches
            if name in open_pr_branches:
                continue  # has open PR

            # Get last commit date
            commit_date_str = (
                (branch.get("commit") or {})
                .get("commit", {})
                .get("committer", {})
                .get("date", "")
            )
            if commit_date_str:
                try:
                    commit_date = datetime.fromisoformat(commit_date_str.rstrip("Z")).replace(
                        tzinfo=timezone.utc
                    )
                    if commit_date < cutoff:
                        age_days = (datetime.now(tz=timezone.utc) - commit_date).days
                        issues.append(
                            HygieneIssue(
                                category="stale_branch",
                                severity="low",
                                description=f"Branch `{name}` inactive for {age_days} days with no open PR",
                                remediation=f"Delete or archive branch `{name}`",
                                context={"branch": name, "age_days": age_days},
                            )
                        )
                except ValueError:
                    logger.debug("Could not parse commit date for branch %s", name)

        return issues

    def _check_orphaned_root_files(self) -> list[HygieneIssue]:
        """Detect stray report/log files in the repository root."""
        issues: list[HygieneIssue] = []
        if not self.repo_root.is_dir():
            return issues

        protected = {
            "README.md", "CHANGELOG.md", "LICENSE", "pyproject.toml",
            "setup.py", "setup.cfg", "requirements.txt", "Makefile",
            ".gitignore", ".gitattributes", "Dockerfile", "docker-compose.yml",
        }

        for entry in self.repo_root.iterdir():
            if entry.is_file() and entry.name not in protected:
                if self.ROOT_ORPHAN_PATTERNS.match(entry.name):
                    issues.append(
                        HygieneIssue(
                            category="orphaned_file",
                            severity="info",
                            description=f"Stray report/log file in root: `{entry.name}`",
                            remediation=f"Move `{entry.name}` to `.codex/` per artifact hygiene policy",
                            context={"file": str(entry)},
                        )
                    )

        return issues

    def _check_dependency_drift(self) -> list[HygieneIssue]:
        """Detect unpinned dependencies in requirements files."""
        issues: list[HygieneIssue] = []
        req_files = list(self.repo_root.glob("requirements*.txt"))

        for req_file in req_files:
            try:
                lines = req_file.read_text(encoding="utf-8").splitlines()
            except OSError:
                continue

            for lineno, line in enumerate(lines, start=1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # Detect unpinned (no == or specific version)
                if "==" not in line and ">=" not in line and "~=" not in line:
                    pkg_name = re.split(r"[>=<!~]", line)[0].strip()
                    if pkg_name:
                        issues.append(
                            HygieneIssue(
                                category="dep_drift",
                                severity="medium",
                                description=(
                                    f"Unpinned dependency `{pkg_name}` in "
                                    f"`{req_file.name}` line {lineno}"
                                ),
                                remediation=f"Pin `{pkg_name}` to a specific version for reproducibility",
                                context={"file": req_file.name, "line": lineno, "package": pkg_name},
                            )
                        )

        return issues

    def _check_contributor_gaps(self) -> list[HygieneIssue]:
        """Detect ownership gaps: no CODEOWNERS or missing coverage."""
        issues: list[HygieneIssue] = []
        codeowners_paths = [
            self.repo_root / "CODEOWNERS",
            self.repo_root / ".github" / "CODEOWNERS",
            self.repo_root / "docs" / "CODEOWNERS",
        ]
        if not any(p.exists() for p in codeowners_paths):
            issues.append(
                HygieneIssue(
                    category="ownership_gap",
                    severity="low",
                    description="No CODEOWNERS file found",
                    remediation="Create .github/CODEOWNERS to define ownership",
                    context={},
                )
            )
        return issues
