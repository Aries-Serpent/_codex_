"""
GitHub Guru Agent — Main Orchestrator

Implements the ASSESS → DELIBERATE → OPTIMIZE → ACT → REFLECT cycle.
Entry point for all 10 capabilities.

SAFE_MODE=true: Read-only GitHub operations only.
OFFLINE_MODE=true: No external network calls (when GITHUB_TOKEN absent).
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

try:
    from .analyzers import IssueAnalyzer, PRAnalyzer, WorkflowAnalyzer
except ImportError:
    from analyzers import IssueAnalyzer, PRAnalyzer, WorkflowAnalyzer
try:
    from .github_client import GitHubAPIClient
except ImportError:
    from github_client import GitHubAPIClient
try:
    from .hygiene import HygieneReport, RepoHygiene
except ImportError:
    from hygiene import HygieneReport, RepoHygiene
try:
    from .learning import LearningEngine
except ImportError:
    from learning import LearningEngine
try:
    from .metrics import MetricsCollector
except ImportError:
    from metrics import MetricsCollector
try:
    from .patterns import PatternMatch
except ImportError:
    from patterns import PatternMatch
try:
    from .triage import IssueTriage, TriageResult
except ImportError:
    from triage import IssueTriage, TriageResult

logger = logging.getLogger(__name__)

__all__ = ["GitHubGuruAgent", "SweepReport"]


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

class ReviewResult:
    """Result from PR analysis capability."""
    def __init__(self, pr_number: int, summary_md: str, health_score: float,
                 pattern_matches: list[PatternMatch], signals: list[str],
                 routing_suggestions: list[str]) -> None:
        self.pr_number = pr_number
        self.summary_md = summary_md
        self.health_score = health_score
        self.pattern_matches = pattern_matches
        self.signals = signals
        self.routing_suggestions = routing_suggestions

    def __repr__(self) -> str:
        return f"<ReviewResult pr={self.pr_number} score={self.health_score:.0f}>"


class SweepReport:
    """Full daily sweep report across all capabilities."""
    def __init__(self) -> None:
        self.session_id: str = ""
        self.pr_results: list[ReviewResult] = []
        self.triage_results: list[TriageResult] = []
        self.workflow_summary_md: str = ""
        self.hygiene_report: Optional[HygieneReport] = None
        self.branch_governance_md: str = ""
        self.contributor_summary_md: str = ""
        self.dependency_drift_md: str = ""
        self.stale_resources_md: str = ""
        self.label_compliance: dict[str, Any] = {}
        self.navigation_hint_md: str = ""
        self.started_at: datetime = datetime.now(tz=timezone.utc)
        self.finished_at: Optional[datetime] = None
        self.total_issues_found: int = 0

    @property
    def summary_md(self) -> str:
        sections = [
            "# 🤖 GitHub Guru Agent — Daily Sweep Report",
            f"**Session**: `{self.session_id}`",
            f"**Started**: {self.started_at.strftime('%Y-%m-%d %H:%M UTC')}",
            "",
            "## 📊 PR Analysis",
            f"- PRs analyzed: {len(self.pr_results)}",
            *(f"  - {r.summary_md}" for r in self.pr_results if r.health_score < 80),
            "",
            "## 🔎 Issue Triage",
            f"- Issues triaged: {len(self.triage_results)}",
            "",
            "## ⚙️ Workflow Health",
            self.workflow_summary_md or "No workflow data.",
            "",
            "## 🏥 Repository Hygiene",
            (self.hygiene_report.summary_md if self.hygiene_report else "No hygiene data."),
            "",
            "## 📦 Dependency Drift",
            self.dependency_drift_md or "No drift detected.",
            "",
            "## 🏷️ Label Compliance",
            f"Score: {self.label_compliance.get('compliance_score', 100):.0f}/100",
        ]
        return "\n".join(sections)


# ---------------------------------------------------------------------------
# Main Agent
# ---------------------------------------------------------------------------

class GitHubGuruAgent:
    """
    GitHub Guru Agent — main orchestrator.

    Capabilities (C-01 through C-10):
      C-01  pr_analysis
      C-02  issue_triage
      C-03  workflow_health_monitoring
      C-04  branch_governance
      C-05  contributor_intelligence
      C-06  repository_hygiene_reporting
      C-07  codebase_navigation_guidance
      C-08  dependency_drift_detection
      C-09  stale_resource_detection
      C-10  label_taxonomy_enforcement
    """

    VERSION = "1.1.0"

    def __init__(
        self,
        owner: str,
        repo: str,
        token: Optional[str] = None,
        safe_mode: bool = True,
        repo_root: Optional[Path] = None,
        session_id: Optional[str] = None,
    ) -> None:
        self.owner = owner
        self.repo = repo
        self.safe_mode = safe_mode
        self.session_id = session_id or f"guru-{uuid.uuid4().hex[:8]}"
        self.repo_root = repo_root or Path.cwd()

        self.client = GitHubAPIClient(
            owner=owner,
            repo=repo,
            token=token,
            safe_mode=safe_mode,
        )

        self._pr_analyzer = PRAnalyzer(self.client)
        self._issue_analyzer = IssueAnalyzer(self.client)
        self._workflow_analyzer = WorkflowAnalyzer(self.client)
        self._triage = IssueTriage(self.client)
        self._hygiene = RepoHygiene(self.client, repo_root=self.repo_root)
        self._metrics = MetricsCollector(self.session_id)
        self._learning = LearningEngine(self.session_id)

        logger.info(
            "GitHubGuruAgent v%s — session=%s owner=%s repo=%s safe=%s",
            self.VERSION, self.session_id, owner, repo, safe_mode,
        )

    # -----------------------------------------------------------------------
    # C-01: pr_analysis
    # -----------------------------------------------------------------------

    def pr_analysis(self, pr_number: int) -> ReviewResult:
        """C-01: Analyze a single PR for health, size, staleness, and patterns."""
        self._metrics.start_capability("pr_analysis")
        try:
            result = self._pr_analyzer.analyze(pr_number)
            self._metrics.record_pr_analyzed()
            self._metrics.record_patterns_matched(len(result.pattern_matches))
            self._metrics.end_capability(
                "pr_analysis",
                success=True,
                output_summary=f"PR#{pr_number} score={result.health_score:.0f}",
            )
            return ReviewResult(
                pr_number=pr_number,
                summary_md=result.summary_md,
                health_score=result.health_score,
                pattern_matches=result.pattern_matches,
                signals=result.signals,
                routing_suggestions=result.routing_suggestions,
            )
        except Exception as exc:
            self._metrics.end_capability("pr_analysis", success=False, error=str(exc))
            raise

    # -----------------------------------------------------------------------
    # C-02: issue_triage
    # -----------------------------------------------------------------------

    def issue_triage(self, issue_number: int) -> TriageResult:
        """C-02: Triage an issue — suggest labels, priority, and routing."""
        self._metrics.start_capability("issue_triage")
        try:
            result = self._triage.triage(issue_number)
            self._metrics.record_issue_triaged()
            self._metrics.end_capability(
                "issue_triage",
                success=True,
                output_summary=f"Issue#{issue_number} priority={result.analysis.suggested_priority}",
            )
            return result
        except Exception as exc:
            self._metrics.end_capability("issue_triage", success=False, error=str(exc))
            raise

    # -----------------------------------------------------------------------
    # C-03: workflow_health_monitoring
    # -----------------------------------------------------------------------

    def workflow_health_monitoring(self, lookback_runs: int = 20) -> str:
        """C-03: Analyze recent workflow runs; return Markdown health report."""
        self._metrics.start_capability("workflow_health_monitoring")
        try:
            result = self._workflow_analyzer.analyze(lookback_runs)
            self._metrics.record_workflow_checked()
            self._metrics.record_patterns_matched(len(result.pattern_matches))
            self._metrics.end_capability(
                "workflow_health_monitoring",
                success=True,
                output_summary=f"health={result.health_score:.0f} failure_rate={result.failure_rate:.0%}",
            )
            if result.is_degraded:
                self._learning.record_lesson(
                    capability="workflow_health_monitoring",
                    observation=f"Workflow health degraded: score={result.health_score:.0f}",
                    hypothesis="Repeated failures or high failure rate detected",
                    action_taken="Flagged degraded workflows for remediation",
                    outcome=f"Degraded: {', '.join(result.degraded_workflows)}",
                    confidence=0.9,
                    tags=["workflow", "degraded"],
                )
            return result.summary_md
        except Exception as exc:
            self._metrics.end_capability("workflow_health_monitoring", success=False, error=str(exc))
            raise

    # -----------------------------------------------------------------------
    # C-04: branch_governance
    # -----------------------------------------------------------------------

    def branch_governance(self, stale_days: int = 30) -> str:
        """C-04: Identify stale branches and naming convention violations."""
        self._metrics.start_capability("branch_governance")
        try:
            issues = self._hygiene._check_stale_branches()
            stale = [i for i in issues if i.category == "stale_branch"]
            lines = [
                f"**Branch Governance Report** — {len(stale)} stale branch(es) found",
            ]
            for issue in stale:
                lines.append(f"- `{issue.context.get('branch')}` — {issue.description}")
            if not stale:
                lines.append("✅ All branches are active or have open PRs.")
            summary = "\n".join(lines)
            self._metrics.end_capability(
                "branch_governance",
                success=True,
                output_summary=f"{len(stale)} stale branches",
            )
            return summary
        except Exception as exc:
            self._metrics.end_capability("branch_governance", success=False, error=str(exc))
            raise

    # -----------------------------------------------------------------------
    # C-05: contributor_intelligence
    # -----------------------------------------------------------------------

    def contributor_intelligence(self, lookback_commits: int = 50) -> str:
        """C-05: Surface contributor patterns, ownership gaps, review bottlenecks."""
        self._metrics.start_capability("contributor_intelligence")
        try:
            resp = self.client.list_commits(per_page=min(lookback_commits, 100))
            if not resp.ok or not isinstance(resp.data, list):
                return "Unable to fetch commit history."

            # Tally commits per author
            author_counts: dict[str, int] = {}
            for commit in resp.data:
                author = (
                    (commit.get("commit") or {})
                    .get("author", {})
                    .get("name", "unknown")
                )
                author_counts[author] = author_counts.get(author, 0) + 1

            # Build table
            lines = [
                "**Contributor Intelligence Report**",
                "",
                "| Author | Commits |",
                "|--------|---------|",
            ]
            for author, count in sorted(author_counts.items(), key=lambda x: -x[1])[:10]:
                lines.append(f"| {author} | {count} |")

            # Ownership gap heuristic
            if len(author_counts) <= 1:
                lines.append("\n⚠️ **Bus factor = 1**: Only one contributor detected.")

            codeowners_issues = self._hygiene._check_contributor_gaps()
            for issue in codeowners_issues:
                lines.append(f"\n⚠️ {issue.description}")

            summary = "\n".join(lines)
            self._metrics.end_capability(
                "contributor_intelligence",
                success=True,
                output_summary=f"{len(author_counts)} contributors",
            )
            return summary
        except Exception as exc:
            self._metrics.end_capability("contributor_intelligence", success=False, error=str(exc))
            raise

    # -----------------------------------------------------------------------
    # C-06: repository_hygiene_reporting
    # -----------------------------------------------------------------------

    def repository_hygiene_reporting(self) -> HygieneReport:
        """C-06: Full repository hygiene check — orphaned files, dep drift, gaps."""
        self._metrics.start_capability("repository_hygiene_reporting")
        try:
            report = self._hygiene.run_all_checks()
            self._metrics.record_hygiene_issues(len(report.issues))
            self._metrics.end_capability(
                "repository_hygiene_reporting",
                success=True,
                output_summary=f"score={report.hygiene_score:.0f} issues={len(report.issues)}",
            )
            return report
        except Exception as exc:
            self._metrics.end_capability("repository_hygiene_reporting", success=False, error=str(exc))
            raise

    # -----------------------------------------------------------------------
    # C-07: codebase_navigation_guidance
    # -----------------------------------------------------------------------

    def codebase_navigation_guidance(self, query: str = "") -> str:
        """C-07: Return navigation hints based on AGENTS.md and repo structure."""
        self._metrics.start_capability("codebase_navigation_guidance")
        try:
            hint_lines = [
                "**Codebase Navigation Guidance**",
                f"Query: `{query}`" if query else "",
                "",
            ]

            # Surface relevant agent based on query keywords
            keyword_map = {
                "test": ["ci-testing-agent", "autonomous-test-healer-agent", "test-coverage-monitor"],
                "security": ["security-alert-verification-agent", "code-scanning-remediation-agent"],
                "coverage": ["coverage-roadmap-agent", "test-coverage-monitor"],
                "docs": ["documentation-quality-agent", "doc-freshness-checker"],
                "dependency": ["dependency-conflict-agent", "dependency-vulnerability-scanner"],
                "ci": ["ci-testing-agent", "ci-parameter-mismatch-healer"],
                "workflow": ["workflow-ci-fixer", "codebase-health-guardian"],
                "rag": ["rag-index-manager", "rag-meta-tensor-regression-agent"],
            }

            matched_agents: list[str] = []
            q_lower = query.lower()
            for keyword, agents in keyword_map.items():
                if keyword in q_lower:
                    matched_agents.extend(agents)

            if matched_agents:
                hint_lines.append("**Relevant agents for your query:**")
                for agent in matched_agents[:5]:
                    hint_lines.append(f"- `.github/agents/{agent}.md`")
            else:
                hint_lines.append("**Key navigation points:**")
                hint_lines.append("- `AGENTS.md` — agent index")
                hint_lines.append("- `.github/agents/AGENT_REGISTRY.md` — full registry")
                hint_lines.append("- `.codex/TECH_DEBT_REGISTRY.md` — tech debt")
                hint_lines.append("- `.codex/plans/AGENTIC_SESSION_METHODOLOGY.md` — session protocol")

            summary = "\n".join(line for line in hint_lines if line is not None)
            self._metrics.end_capability("codebase_navigation_guidance", success=True, output_summary=query)
            return summary
        except Exception as exc:
            self._metrics.end_capability("codebase_navigation_guidance", success=False, error=str(exc))
            raise

    # -----------------------------------------------------------------------
    # C-08: dependency_drift_detection
    # -----------------------------------------------------------------------

    def dependency_drift_detection(self) -> str:
        """C-08: Detect outdated/unpinned dependencies in requirements files."""
        self._metrics.start_capability("dependency_drift_detection")
        try:
            issues = self._hygiene._check_dependency_drift()
            lines = [f"**Dependency Drift Report** — {len(issues)} issue(s) found"]
            for issue in issues[:20]:  # cap output
                lines.append(f"- {issue.description}")
                lines.append(f"  *Remediation*: {issue.remediation}")
            if not issues:
                lines.append("✅ All detected dependencies are pinned.")
            summary = "\n".join(lines)
            self._metrics.end_capability(
                "dependency_drift_detection",
                success=True,
                output_summary=f"{len(issues)} unpinned deps",
            )
            return summary
        except Exception as exc:
            self._metrics.end_capability("dependency_drift_detection", success=False, error=str(exc))
            raise

    # -----------------------------------------------------------------------
    # C-09: stale_resource_detection
    # -----------------------------------------------------------------------

    def stale_resource_detection(
        self,
        pr_stale_days: int = 14,
        branch_stale_days: int = 30,
    ) -> str:
        """C-09: Detect stale PRs, issues, and branches."""
        self._metrics.start_capability("stale_resource_detection")
        try:
            lines = ["**Stale Resource Report**", ""]

            # Stale PRs
            pr_resp = self.client.list_pull_requests(state="open", per_page=50)
            stale_prs: list[str] = []
            if pr_resp.ok and isinstance(pr_resp.data, list):
                from datetime import timedelta
                cutoff = datetime.now(tz=timezone.utc) - timedelta(days=pr_stale_days)
                for pr in pr_resp.data:
                    updated = pr.get("updated_at", "")
                    if updated:
                        try:
                            ts = datetime.fromisoformat(updated.rstrip("Z")).replace(tzinfo=timezone.utc)
                            if ts < cutoff:
                                stale_prs.append(f"PR #{pr.get('number')} — {pr.get('title', '')[:50]}")
                        except ValueError:
                            logger.debug("Skipping PR with unparseable timestamp: %r", updated)

            lines.append(f"**Stale PRs** (inactive >{pr_stale_days}d): {len(stale_prs)}")
            for pr in stale_prs[:5]:
                lines.append(f"  - {pr}")

            # Stale branches
            branch_issues = self._hygiene._check_stale_branches()
            stale_branches = [i.context.get("branch", "") for i in branch_issues]
            lines.append(f"\n**Stale Branches** (inactive >{branch_stale_days}d): {len(stale_branches)}")
            for br in stale_branches[:5]:
                lines.append(f"  - `{br}`")

            if not stale_prs and not stale_branches:
                lines.append("✅ No stale resources detected.")

            summary = "\n".join(lines)
            self._metrics.end_capability(
                "stale_resource_detection",
                success=True,
                output_summary=f"{len(stale_prs)} stale PRs, {len(stale_branches)} stale branches",
            )
            return summary
        except Exception as exc:
            self._metrics.end_capability("stale_resource_detection", success=False, error=str(exc))
            raise

    # -----------------------------------------------------------------------
    # C-10: label_taxonomy_enforcement
    # -----------------------------------------------------------------------

    def label_taxonomy_enforcement(self) -> dict[str, Any]:
        """C-10: Check that all repo labels match the taxonomy in triage.py."""
        self._metrics.start_capability("label_taxonomy_enforcement")
        try:
            resp = self.client.list_labels()
            repo_labels: list[str] = []
            if resp.ok and isinstance(resp.data, list):
                repo_labels = [lbl.get("name", "") for lbl in resp.data]

            result = self._triage.check_label_compliance(repo_labels)
            self._metrics.end_capability(
                "label_taxonomy_enforcement",
                success=True,
                output_summary=f"score={result.get('compliance_score', 0):.0f}",
            )
            return result
        except Exception as exc:
            self._metrics.end_capability("label_taxonomy_enforcement", success=False, error=str(exc))
            raise

    # -----------------------------------------------------------------------
    # Daily sweep & event handler
    # -----------------------------------------------------------------------

    def run_daily_sweep(self) -> SweepReport:
        """Run all capabilities for a full daily health sweep."""
        report = SweepReport()
        report.session_id = self.session_id

        # C-03: Workflow health
        report.workflow_summary_md = self.workflow_health_monitoring()

        # C-04: Branch governance
        report.branch_governance_md = self.branch_governance()

        # C-06: Repository hygiene
        report.hygiene_report = self.repository_hygiene_reporting()

        # C-08: Dependency drift
        report.dependency_drift_md = self.dependency_drift_detection()

        # C-09: Stale resources
        report.stale_resources_md = self.stale_resource_detection()

        # C-10: Label taxonomy
        report.label_compliance = self.label_taxonomy_enforcement()

        # C-05: Contributor intelligence
        report.contributor_summary_md = self.contributor_intelligence()

        report.finished_at = datetime.now(tz=timezone.utc)
        report.total_issues_found = (
            len(report.pr_results) +
            len(report.triage_results) +
            (len(report.hygiene_report.issues) if report.hygiene_report else 0)
        )

        # Finalize metrics and learning
        self._metrics.finalize()
        self._learning.finalize()

        return report

    def handle_event(self, event: dict[str, Any]) -> dict[str, Any]:
        """
        Route a GitHub webhook event to the appropriate capability.

        Args:
            event: GitHub webhook payload dict with 'event_type' key.

        Returns:
            Dict with 'capability', 'result_md', and 'success'.
        """
        event_type = event.get("event_type", "workflow_dispatch")
        entity_id = event.get("entity_id")

        try:
            if event_type == "pull_request" and entity_id:
                result = self.pr_analysis(int(entity_id))
                return {"capability": "pr_analysis", "result_md": result.summary_md, "success": True}

            if event_type == "issues" and entity_id:
                result = self.issue_triage(int(entity_id))
                return {"capability": "issue_triage", "result_md": result.summary_md, "success": True}

            if event_type in ("schedule", "workflow_dispatch"):
                report = self.run_daily_sweep()
                return {"capability": "daily_sweep", "result_md": report.summary_md, "success": True}

            return {
                "capability": "unknown",
                "result_md": f"Unhandled event type: {event_type}",
                "success": False,
            }
        except Exception as exc:
            logger.error("handle_event failed for %s: %s", event_type, exc)
            return {"capability": event_type, "result_md": str(exc), "success": False}
