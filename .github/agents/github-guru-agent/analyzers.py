"""
GitHub Guru Agent — PR/Issue/Workflow Analyzers

Provides structured analysis for PRs, issues, and GitHub Actions workflows.
Each analyzer returns a typed result with health score and actionable signals.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

try:
    from .github_client import GitHubAPIClient
except ImportError:
    from github_client import GitHubAPIClient
try:
    from .patterns import PatternMatch, match_patterns
except ImportError:
    from patterns import PatternMatch, match_patterns

logger = logging.getLogger(__name__)


# --- Result types ---------------------------------------------------------------

@dataclass
class PRAnalysisResult:
    """Result of PR analysis."""

    pr_number: int
    title: str
    health_score: float  # 0–100
    size_category: str  # xs/s/m/l/xl
    file_count: int
    addition_count: int
    deletion_count: int
    is_stale: bool
    has_failing_checks: bool
    has_merge_conflicts: bool
    reviewer_count: int
    pattern_matches: list[PatternMatch] = field(default_factory=list)
    signals: list[str] = field(default_factory=list)
    routing_suggestions: list[str] = field(default_factory=list)
    summary_md: str = ""

    @property
    def needs_attention(self) -> bool:
        return self.health_score < 60 or bool(self.pattern_matches)


@dataclass
class IssueAnalysisResult:
    """Result of issue analysis."""

    issue_number: int
    title: str
    suggested_labels: list[str] = field(default_factory=list)
    suggested_priority: str = "medium"  # critical/high/medium/low
    routing_agent: Optional[str] = None
    triage_confidence: float = 0.0
    signals: list[str] = field(default_factory=list)
    summary_md: str = ""


@dataclass
class WorkflowHealthResult:
    """Result of workflow health analysis."""

    total_runs: int
    failure_rate: float  # 0–1
    avg_duration_seconds: float
    flaky_jobs: list[str] = field(default_factory=list)
    degraded_workflows: list[str] = field(default_factory=list)
    pattern_matches: list[PatternMatch] = field(default_factory=list)
    health_score: float = 100.0  # 0–100
    summary_md: str = ""

    @property
    def is_degraded(self) -> bool:
        return self.health_score < 70 or self.failure_rate > 0.2


# --- Size thresholds -----------------------------------------------------------

_SIZE_THRESHOLDS = {
    "xs": 10,
    "s": 50,
    "m": 200,
    "l": 500,
    "xl": float("inf"),
}


def _classify_pr_size(changed_lines: int) -> str:
    for label, threshold in _SIZE_THRESHOLDS.items():
        if changed_lines <= threshold:
            return label
    return "xl"


# --- PR Analyzer ---------------------------------------------------------------

class PRAnalyzer:
    """Analyzes pull requests for health, size, staleness, and pattern matches."""

    STALE_DAYS = 7  # PR inactive for this many days is considered stale

    def __init__(self, client: GitHubAPIClient):
        self.client = client

    def analyze(self, pr_number: int) -> PRAnalysisResult:
        """
        Analyze a single pull request.

        Returns:
            PRAnalysisResult with health score and actionable signals.
        """
        pr_resp = self.client.get_pull_request(pr_number)
        if not pr_resp.ok:
            logger.warning("Failed to fetch PR #%d: %s", pr_number, pr_resp.error)
            return PRAnalysisResult(
                pr_number=pr_number,
                title="(fetch failed)",
                health_score=0.0,
                size_category="unknown",
                file_count=0,
                addition_count=0,
                deletion_count=0,
                is_stale=False,
                has_failing_checks=False,
                has_merge_conflicts=False,
                reviewer_count=0,
                signals=[f"API error: {pr_resp.error}"],
            )

        pr = pr_resp.data
        additions = pr.get("additions", 0)
        deletions = pr.get("deletions", 0)
        changed_files = pr.get("changed_files", 0)
        total_lines = additions + deletions
        size_cat = _classify_pr_size(total_lines)

        # Staleness check
        updated_at_str = pr.get("updated_at", "")
        is_stale = False
        if updated_at_str:
            try:
                updated_at = datetime.fromisoformat(updated_at_str.rstrip("Z")).replace(
                    tzinfo=timezone.utc
                )
                is_stale = (datetime.now(tz=timezone.utc) - updated_at) > timedelta(
                    days=self.STALE_DAYS
                )
            except ValueError:
                logger.debug("Could not parse updated_at: %s", updated_at_str)

        # Merge conflict check
        mergeable_state = pr.get("mergeable_state", "")
        has_merge_conflicts = mergeable_state == "dirty"

        # Reviewer count
        reviews_resp = self.client.list_pull_request_reviews(pr_number)
        reviewer_count = 0
        if reviews_resp.ok and isinstance(reviews_resp.data, list):
            seen = set()
            for r in reviews_resp.data:
                login = (r.get("user") or {}).get("login", "")
                if login:
                    seen.add(login)
            reviewer_count = len(seen)

        # CI status
        has_failing_checks = pr.get("mergeable_state") in ("blocked", "unstable")

        # Pattern matching
        context = {
            "pr_size": size_cat,
            "total_lines": total_lines,
            "is_stale": is_stale,
            "has_failing_checks": has_failing_checks,
            "has_merge_conflicts": has_merge_conflicts,
            "reviewer_count": reviewer_count,
        }
        pattern_matches = match_patterns(context)

        # Health score (0–100)
        deductions = 0.0
        signals: list[str] = []
        routing: list[str] = []

        if is_stale:
            deductions += 15
            signals.append("⚠️ PR inactive >7 days")
        if has_merge_conflicts:
            deductions += 25
            signals.append("❌ Merge conflicts detected")
        if has_failing_checks:
            deductions += 20
            signals.append("❌ CI checks failing")
        if reviewer_count == 0:
            deductions += 10
            signals.append("⚠️ No reviewers assigned")
        if size_cat in ("l", "xl"):
            deductions += 10
            signals.append(f"📏 Large PR ({total_lines} lines changed)")

        for match in pattern_matches:
            if match.pattern.routing_agent:
                routing.append(match.pattern.routing_agent)

        health_score = max(0.0, 100.0 - deductions)

        summary_lines = [
            f"**PR #{pr_number}**: {pr.get('title', '')}",
            f"- Health score: **{health_score:.0f}/100**",
            f"- Size: `{size_cat}` ({total_lines} lines, {changed_files} files)",
            f"- Reviewers: {reviewer_count}",
        ]
        if signals:
            summary_lines.append("- Signals: " + "; ".join(signals))
        if routing:
            summary_lines.append("- Route to: " + ", ".join(set(routing)))

        return PRAnalysisResult(
            pr_number=pr_number,
            title=pr.get("title", ""),
            health_score=health_score,
            size_category=size_cat,
            file_count=changed_files,
            addition_count=additions,
            deletion_count=deletions,
            is_stale=is_stale,
            has_failing_checks=has_failing_checks,
            has_merge_conflicts=has_merge_conflicts,
            reviewer_count=reviewer_count,
            pattern_matches=pattern_matches,
            signals=signals,
            routing_suggestions=list(set(routing)),
            summary_md="\n".join(summary_lines),
        )


# --- Issue Analyzer ------------------------------------------------------------

class IssueAnalyzer:
    """Analyzes issues for triage: label suggestions, priority, routing."""

    _PRIORITY_KEYWORDS = {
        "critical": ["crash", "data loss", "security", "vulnerability", "exploit"],
        "high": ["regression", "broken", "failing", "error", "exception", "blocker"],
        "medium": ["slow", "warning", "incorrect", "mismatch", "missing"],
        "low": ["typo", "docs", "improvement", "enhancement", "refactor"],
    }

    _LABEL_PATTERNS = {
        "bug": ["fail", "error", "broken", "crash", "regression", "exception"],
        "documentation": ["docs", "readme", "docstring", "comment", "typo"],
        "enhancement": ["improve", "add", "new feature", "request", "support"],
        "security": ["security", "vulnerability", "exploit", "cve", "injection"],
        "performance": ["slow", "performance", "latency", "memory", "cpu"],
        "ci/cd": ["workflow", "action", "pipeline", "ci", "cd", "build"],
        "test": ["test", "coverage", "flak", "skip", "xfail"],
        "dependencies": ["dependency", "package", "requirements", "pyproject"],
    }

    def __init__(self, client: GitHubAPIClient):
        self.client = client

    def analyze(self, issue_number: int) -> IssueAnalysisResult:
        """Analyze an issue and suggest labels, priority, and routing."""
        resp = self.client.get_issue(issue_number)
        if not resp.ok:
            logger.warning("Failed to fetch issue #%d: %s", issue_number, resp.error)
            return IssueAnalysisResult(
                issue_number=issue_number,
                title="(fetch failed)",
                signals=[f"API error: {resp.error}"],
            )

        issue = resp.data
        title = (issue.get("title") or "").lower()
        body = (issue.get("body") or "").lower()
        combined = f"{title} {body}"

        # Suggest labels
        suggested_labels: list[str] = []
        for label, keywords in self._LABEL_PATTERNS.items():
            if any(kw in combined for kw in keywords):
                suggested_labels.append(label)

        # Determine priority
        priority = "low"
        for p, keywords in self._PRIORITY_KEYWORDS.items():
            if any(kw in combined for kw in keywords):
                priority = p
                break

        # Routing
        routing_map = {
            "ci/cd": "ci-testing-agent",
            "security": "security-alert-verification-agent",
            "dependencies": "dependency-conflict-agent",
            "test": "autonomous-test-healer-agent",
            "documentation": "documentation-quality-agent",
        }
        routing_agent: Optional[str] = None
        for label in suggested_labels:
            if label in routing_map:
                routing_agent = routing_map[label]
                break

        triage_confidence = min(len(suggested_labels) * 0.2, 1.0)

        signals = []
        if not suggested_labels:
            signals.append("⚠️ No matching labels found; manual triage needed")
        signals.append(f"🎯 Suggested priority: **{priority}**")
        if routing_agent:
            signals.append(f"🔀 Route to: `{routing_agent}`")

        summary = (
            f"**Issue #{issue_number}**: {issue.get('title', '')}\n"
            f"- Priority: **{priority}**\n"
            f"- Labels: {', '.join(f'`{lbl}`' for lbl in suggested_labels) or '(none)'}\n"
            f"- Triage confidence: {triage_confidence:.0%}\n"
        )
        if routing_agent:
            summary += f"- Route to: `{routing_agent}`\n"

        return IssueAnalysisResult(
            issue_number=issue_number,
            title=issue.get("title", ""),
            suggested_labels=suggested_labels,
            suggested_priority=priority,
            routing_agent=routing_agent,
            triage_confidence=triage_confidence,
            signals=signals,
            summary_md=summary,
        )


# --- Workflow Analyzer ---------------------------------------------------------

class WorkflowAnalyzer:
    """Analyzes recent GitHub Actions runs for health trends."""

    FAILURE_RATE_THRESHOLD = 0.20  # >20% failure rate = degraded
    DURATION_THRESHOLD_SECONDS = 1800  # >30min = long-running

    def __init__(self, client: GitHubAPIClient):
        self.client = client

    def analyze(self, lookback_runs: int = 20) -> WorkflowHealthResult:
        """
        Analyze recent workflow runs.

        Args:
            lookback_runs: Number of recent runs to inspect.

        Returns:
            WorkflowHealthResult with health score and degraded workflow list.
        """
        resp = self.client.list_workflow_runs(status="completed", per_page=lookback_runs)
        if not resp.ok or not isinstance(resp.data, dict):
            return WorkflowHealthResult(
                total_runs=0,
                failure_rate=0.0,
                avg_duration_seconds=0.0,
                health_score=100.0,
                summary_md="Unable to fetch workflow runs.",
            )

        runs: list[dict[str, Any]] = resp.data.get("workflow_runs", [])
        if not runs:
            return WorkflowHealthResult(
                total_runs=0,
                failure_rate=0.0,
                avg_duration_seconds=0.0,
                health_score=100.0,
                summary_md="No recent workflow runs found.",
            )

        total = len(runs)
        failures = sum(1 for r in runs if r.get("conclusion") == "failure")
        failure_rate = failures / total if total > 0 else 0.0

        # Duration calculation (simplified: created_at to updated_at)
        durations: list[float] = []
        for run in runs:
            ca = run.get("created_at", "")
            ua = run.get("updated_at", "")
            if ca and ua:
                try:
                    t0 = datetime.fromisoformat(ca.rstrip("Z")).replace(tzinfo=timezone.utc)
                    t1 = datetime.fromisoformat(ua.rstrip("Z")).replace(tzinfo=timezone.utc)
                    durations.append((t1 - t0).total_seconds())
                except ValueError:
                    logger.debug("Could not parse run timestamps")

        avg_duration = sum(durations) / len(durations) if durations else 0.0

        # Degraded workflows
        workflow_failures: dict[str, int] = {}
        for run in runs:
            name = run.get("name", "unknown")
            if run.get("conclusion") == "failure":
                workflow_failures[name] = workflow_failures.get(name, 0) + 1

        degraded = [name for name, count in workflow_failures.items() if count >= 3]

        # Long-running jobs (jobs endpoint would be needed; approximate here)
        long_running_jobs: list[str] = []

        # Pattern matching
        context = {
            "failure_rate": failure_rate,
            "degraded_workflow_count": len(degraded),
        }
        if degraded:
            context["conclusion"] = "failure"
            context["run_count"] = max(workflow_failures.values())
            context["same_workflow"] = True
        pattern_matches = match_patterns(context)

        # Health score
        health_score = max(0.0, 100.0 - failure_rate * 100 - len(degraded) * 5)

        summary_lines = [
            f"**Workflow Health**: {health_score:.0f}/100",
            f"- Runs analyzed: {total}",
            f"- Failure rate: {failure_rate:.0%}",
            f"- Avg duration: {avg_duration:.0f}s",
        ]
        if degraded:
            summary_lines.append(f"- ⚠️ Degraded workflows: {', '.join(degraded)}")

        return WorkflowHealthResult(
            total_runs=total,
            failure_rate=failure_rate,
            avg_duration_seconds=avg_duration,
            flaky_jobs=long_running_jobs,
            degraded_workflows=degraded,
            pattern_matches=pattern_matches,
            health_score=health_score,
            summary_md="\n".join(summary_lines),
        )
