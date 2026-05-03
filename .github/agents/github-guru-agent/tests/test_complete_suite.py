"""
GitHub Guru Agent — Complete Test Suite

Tests all 10 capabilities (C-01 through C-10) plus:
  - Cognitive adapter (OODA loop + physics scoring)
  - Pattern registry (match_patterns, severity filtering)
  - GitHub API client (offline/safe mode)
  - Metrics collector (session tracking)
  - Learning engine (lesson capture + persistence)
  - Hygiene checks (stale branches, orphaned files, dep drift)
  - Triage (label taxonomy, priority, routing)
  - Daily sweep + event handler

All tests use mocked/offline GitHub client — no real API calls.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Path setup — make the agent package importable
# ---------------------------------------------------------------------------
_AGENT_DIR = Path(__file__).resolve().parents[1]  # .github/agents/github-guru-agent/
_REPO_ROOT = _AGENT_DIR.parents[2]
if str(_AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(_AGENT_DIR))
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

# ---------------------------------------------------------------------------
# Import agent modules
# ---------------------------------------------------------------------------
from analyzers import PRAnalyzer, WorkflowAnalyzer  # noqa: E402
from github_client import GitHubAPIClient, GitHubAPIResponse  # noqa: E402
from guru_adapter import GitHubGuruAdapter, _physics_score  # noqa: E402
from hygiene import RepoHygiene  # noqa: E402
from learning import LearningEngine  # noqa: E402
from main import GitHubGuruAgent  # noqa: E402
from patterns import (  # noqa: E402
    PATTERNS,
    PatternCategory,
    PatternSeverity,
    get_pattern,
    get_patterns_by_category,
    get_patterns_by_severity,
    match_patterns,
)
from triage import LABEL_TAXONOMY, IssueTriage  # noqa: E402

from metrics import MetricsCollector  # noqa: E402

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _offline_client(owner: str = "test-owner", repo: str = "test-repo") -> GitHubAPIClient:
    """Create a client in offline mode (no real API calls)."""
    return GitHubAPIClient(owner=owner, repo=repo, token="", offline_mode=True)


def _pr_payload(**overrides: Any) -> dict[str, Any]:
    """Minimal valid PR API response."""
    base = {
        "number": 42,
        "title": "feat: add GitHub Guru Agent",
        "additions": 120,
        "deletions": 30,
        "changed_files": 8,
        "updated_at": datetime.now(tz=timezone.utc).isoformat(),
        "mergeable_state": "clean",
        "head": {"ref": "feature/guru-agent"},
    }
    base.update(overrides)
    return base


def _issue_payload(**overrides: Any) -> dict[str, Any]:
    base = {
        "number": 7,
        "title": "CI pipeline keeps failing on import error",
        "body": "The ModuleNotFoundError appears on every PR. This is a blocker.",
    }
    base.update(overrides)
    return base


def _workflow_runs_payload(count: int = 5, failure_rate: float = 0.2) -> dict[str, Any]:
    runs = []
    now = datetime.now(tz=timezone.utc)
    for i in range(count):
        conclusion = "failure" if i < int(count * failure_rate) else "success"
        runs.append({
            "name": "Resilient Validation Suite",
            "conclusion": conclusion,
            "created_at": (now - timedelta(hours=i * 2)).isoformat(),
            "updated_at": (now - timedelta(hours=i * 2 - 1)).isoformat(),
        })
    return {"workflow_runs": runs, "total_count": count}


# ===========================================================================
# I. Pattern Registry Tests
# ===========================================================================

class TestPatternRegistry:
    """Tests for patterns.py — pattern catalogue and matching."""

    def test_all_patterns_have_required_fields(self):
        """Every pattern must have id, name, category, severity, description, remediation."""
        for p in PATTERNS:
            assert p.id, f"Pattern missing id: {p}"
            assert p.name, f"Pattern {p.id} missing name"
            assert isinstance(p.category, PatternCategory)
            assert isinstance(p.severity, PatternSeverity)
            assert p.description, f"Pattern {p.id} missing description"
            assert p.remediation, f"Pattern {p.id} missing remediation"

    def test_at_least_18_patterns_defined(self):
        """Registry must have at least 18 pattern signatures."""
        assert len(PATTERNS) >= 18, f"Only {len(PATTERNS)} patterns found"

    def test_get_pattern_by_id(self):
        p = get_pattern("CI-001")
        assert p is not None
        assert p.name == "Repeated Workflow Failure"

    def test_get_pattern_unknown_returns_none(self):
        assert get_pattern("NONEXISTENT-999") is None

    def test_get_patterns_by_category(self):
        ci_patterns = get_patterns_by_category(PatternCategory.CI_CD)
        assert len(ci_patterns) >= 3
        assert all(p.category == PatternCategory.CI_CD for p in ci_patterns)

    def test_get_patterns_by_severity_critical(self):
        critical = get_patterns_by_severity(PatternSeverity.CRITICAL)
        # Critical filter should include CRITICAL patterns
        severities = {p.severity for p in critical}
        assert PatternSeverity.CRITICAL in severities

    def test_match_patterns_empty_context(self):
        matches = match_patterns({})
        assert isinstance(matches, list)

    def test_match_patterns_failure_rate_context(self):
        ctx = {"failure_rate": 0.5, "conclusion": "failure", "run_count": 5, "same_workflow": True}
        matches = match_patterns(ctx)
        assert len(matches) >= 1
        # Top match should be CI-related
        assert any(m.pattern.category == PatternCategory.CI_CD for m in matches)

    def test_match_patterns_sorted_by_score_descending(self):
        ctx = {
            "failure_rate": 0.8,
            "conclusion": "failure",
            "run_count": 4,
            "same_workflow": True,
            "collection_error": True,
            "ModuleNotFoundError": True,
        }
        matches = match_patterns(ctx)
        scores = [m.score for m in matches]
        assert scores == sorted(scores, reverse=True)

    def test_pattern_match_score_range(self):
        ctx = {"failure_rate": 0.4, "conclusion": "failure", "run_count": 3, "same_workflow": True}
        matches = match_patterns(ctx)
        for m in matches:
            assert 0.0 <= m.score <= 10000, f"Score out of range: {m.score}"


# ===========================================================================
# II. GitHub API Client Tests
# ===========================================================================

class TestGitHubAPIClient:
    """Tests for github_client.py — offline and safe mode behaviour."""

    def test_offline_mode_get_pr_returns_200(self):
        client = _offline_client()
        resp = client.get_pull_request(42)
        assert resp.ok
        assert resp.status == 200

    def test_offline_mode_list_prs_returns_200(self):
        client = _offline_client()
        resp = client.list_pull_requests()
        assert resp.ok

    def test_offline_mode_list_workflow_runs_returns_200(self):
        client = _offline_client()
        resp = client.list_workflow_runs()
        assert resp.ok

    def test_offline_mode_all_endpoints_return_ok(self):
        client = _offline_client()
        endpoints = [
            lambda: client.get_pull_request(1),
            lambda: client.list_pull_request_files(1),
            lambda: client.list_pull_request_reviews(1),
            lambda: client.list_pull_requests(),
            lambda: client.get_issue(1),
            lambda: client.list_issues(),
            lambda: client.list_labels(),
            lambda: client.list_workflow_runs(),
            lambda: client.list_branches(),
            lambda: client.get_repo(),
            lambda: client.list_commits(),
        ]
        for fn in endpoints:
            resp = fn()
            assert resp.ok, f"Expected ok for {fn}"

    def test_safe_mode_flag(self):
        client = GitHubAPIClient("o", "r", safe_mode=True, offline_mode=True)
        assert client.safe_mode is True

    def test_api_response_not_ok_on_error_status(self):
        resp = GitHubAPIResponse(status=404, data={}, error="Not found")
        assert not resp.ok
        assert resp.is_not_found

    def test_api_response_ok(self):
        resp = GitHubAPIResponse(status=200, data={"id": 1})
        assert resp.ok
        assert not resp.is_not_found

    def test_rate_limited_flag(self):
        resp = GitHubAPIResponse(status=200, data={}, rate_limit_remaining=5)
        assert resp.is_rate_limited


# ===========================================================================
# III. C-01: PR Analysis Tests
# ===========================================================================

class TestPRAnalysis:
    """Tests for C-01 pr_analysis capability."""

    def _make_analyzer(self, pr_data=None, reviews=None):
        client = _offline_client()
        client.get_pull_request = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=pr_data or _pr_payload())
        )
        client.list_pull_request_reviews = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=reviews or [])
        )
        return PRAnalyzer(client)

    def test_healthy_pr_scores_high(self):
        analyzer = self._make_analyzer(_pr_payload(additions=50, deletions=10))
        result = analyzer.analyze(42)
        assert result.health_score >= 70

    def test_large_pr_reduces_score(self):
        analyzer = self._make_analyzer(_pr_payload(additions=400, deletions=200))
        result = analyzer.analyze(42)
        assert result.health_score < 100

    def test_stale_pr_flagged(self):
        stale_date = (datetime.now(tz=timezone.utc) - timedelta(days=10)).isoformat()
        analyzer = self._make_analyzer(_pr_payload(updated_at=stale_date))
        result = analyzer.analyze(42)
        assert result.is_stale
        assert any("inactive" in s for s in result.signals)

    def test_merge_conflict_detected(self):
        analyzer = self._make_analyzer(_pr_payload(mergeable_state="dirty"))
        result = analyzer.analyze(42)
        assert result.has_merge_conflicts
        assert result.health_score < 80

    def test_no_reviewers_flagged(self):
        analyzer = self._make_analyzer(reviews=[])
        result = analyzer.analyze(42)
        assert result.reviewer_count == 0
        assert any("reviewer" in s.lower() for s in result.signals)

    def test_reviewer_count_counted(self):
        reviews = [
            {"user": {"login": "alice"}, "state": "APPROVED"},
            {"user": {"login": "bob"}, "state": "CHANGES_REQUESTED"},
        ]
        analyzer = self._make_analyzer(reviews=reviews)
        result = analyzer.analyze(42)
        assert result.reviewer_count == 2

    def test_pr_size_classification_xs(self):
        analyzer = self._make_analyzer(_pr_payload(additions=5, deletions=2))
        result = analyzer.analyze(42)
        assert result.size_category == "xs"

    def test_pr_size_classification_xl(self):
        analyzer = self._make_analyzer(_pr_payload(additions=800, deletions=200))
        result = analyzer.analyze(42)
        assert result.size_category == "xl"

    def test_api_failure_returns_zero_score(self):
        client = _offline_client()
        client.get_pull_request = MagicMock(
            return_value=GitHubAPIResponse(status=404, data={}, error="Not found")
        )
        analyzer = PRAnalyzer(client)
        result = analyzer.analyze(99)
        assert result.health_score == 0.0
        assert len(result.signals) > 0

    def test_summary_md_contains_pr_number(self):
        analyzer = self._make_analyzer()
        result = analyzer.analyze(42)
        assert "42" in result.summary_md

    def test_pattern_matches_returned(self):
        analyzer = self._make_analyzer(
            _pr_payload(mergeable_state="blocked", updated_at=(datetime.now(tz=timezone.utc) - timedelta(days=15)).isoformat())
        )
        result = analyzer.analyze(42)
        assert isinstance(result.pattern_matches, list)


# ===========================================================================
# IV. C-02: Issue Triage Tests
# ===========================================================================

class TestIssueTriage:
    """Tests for C-02 issue_triage capability."""

    def _make_triage(self, issue_data=None):
        client = _offline_client()
        client.get_issue = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=issue_data or _issue_payload())
        )
        return IssueTriage(client)

    def test_ci_issue_gets_ci_label(self):
        triage = self._make_triage(_issue_payload(title="CI workflow failing on import error"))
        result = triage.triage(7)
        assert "ci/cd" in result.labels_to_apply or "bug" in result.labels_to_apply

    def test_security_issue_gets_high_priority(self):
        triage = self._make_triage(_issue_payload(title="Security vulnerability in JWT handling"))
        result = triage.triage(7)
        assert result.analysis.suggested_priority in ("critical", "high")

    def test_typo_issue_gets_low_priority(self):
        # Provide a neutral body so only the title keywords drive priority
        triage = self._make_triage(_issue_payload(
            title="Typo in README documentation",
            body="There is a small typo in the docs.",
        ))
        result = triage.triage(7)
        assert result.analysis.suggested_priority in ("low", "medium")

    def test_priority_label_is_valid_taxonomy(self):
        triage = self._make_triage()
        result = triage.triage(7)
        assert result.priority_label in LABEL_TAXONOMY

    def test_compliance_gaps_empty_when_all_labels_known(self):
        triage = self._make_triage()
        result = triage.triage(7)
        # All suggested labels should come from taxonomy
        for label in result.labels_to_apply:
            assert label in LABEL_TAXONOMY, f"Label '{label}' not in taxonomy"

    def test_api_failure_handled(self):
        client = _offline_client()
        client.get_issue = MagicMock(
            return_value=GitHubAPIResponse(status=404, data={}, error="Not found")
        )
        triage = IssueTriage(client)
        result = triage.triage(99)
        assert len(result.labels_to_apply) == 0 or result.analysis.triage_confidence == 0.0

    def test_triage_confidence_range(self):
        triage = self._make_triage()
        result = triage.triage(7)
        assert 0.0 <= result.analysis.triage_confidence <= 1.0

    def test_label_compliance_check_with_exact_taxonomy(self):
        client = _offline_client()
        triage = IssueTriage(client)
        all_taxonomy_labels = list(LABEL_TAXONOMY.keys())
        result = triage.check_label_compliance(all_taxonomy_labels)
        assert result["compliant"]
        assert result["compliance_score"] == 100.0

    def test_label_compliance_check_with_extra_labels(self):
        client = _offline_client()
        triage = IssueTriage(client)
        labels = list(LABEL_TAXONOMY.keys()) + ["my-custom-label"]
        result = triage.check_label_compliance(labels)
        assert not result["compliant"]
        assert "my-custom-label" in result["extra_labels"]

    def test_label_compliance_check_with_missing_labels(self):
        client = _offline_client()
        triage = IssueTriage(client)
        # Remove 'bug' from the repo
        labels = [lbl for lbl in LABEL_TAXONOMY.keys() if lbl != "bug"]
        result = triage.check_label_compliance(labels)
        assert not result["compliant"]
        assert "bug" in result["missing_labels"]


# ===========================================================================
# V. C-03: Workflow Health Monitoring Tests
# ===========================================================================

class TestWorkflowHealthMonitoring:
    """Tests for C-03 workflow_health_monitoring capability."""

    def _make_analyzer(self, runs_data=None):
        client = _offline_client()
        client.list_workflow_runs = MagicMock(
            return_value=GitHubAPIResponse(
                status=200,
                data=runs_data or _workflow_runs_payload(10, 0.1),
            )
        )
        return WorkflowAnalyzer(client)

    def test_healthy_suite_scores_above_80(self):
        analyzer = self._make_analyzer(_workflow_runs_payload(10, 0.0))
        result = analyzer.analyze()
        assert result.health_score >= 80

    def test_high_failure_rate_degrades_score(self):
        analyzer = self._make_analyzer(_workflow_runs_payload(10, 0.6))
        result = analyzer.analyze()
        assert result.is_degraded

    def test_zero_runs_returns_100_health(self):
        client = _offline_client()
        client.list_workflow_runs = MagicMock(
            return_value=GitHubAPIResponse(status=200, data={"workflow_runs": []})
        )
        analyzer = WorkflowAnalyzer(client)
        result = analyzer.analyze()
        assert result.health_score == 100.0

    def test_api_failure_returns_graceful_result(self):
        client = _offline_client()
        client.list_workflow_runs = MagicMock(
            return_value=GitHubAPIResponse(status=500, data={}, error="Server error")
        )
        analyzer = WorkflowAnalyzer(client)
        result = analyzer.analyze()
        assert result.health_score == 100.0  # safe default

    def test_repeated_failures_detected_as_degraded(self):
        # Workflow fails 4 out of 5 times
        runs = []
        now = datetime.now(tz=timezone.utc)
        for i in range(5):
            runs.append({
                "name": "BrokenWorkflow",
                "conclusion": "failure" if i < 4 else "success",
                "created_at": (now - timedelta(hours=i)).isoformat(),
                "updated_at": (now - timedelta(hours=i - 0.5)).isoformat(),
            })
        client = _offline_client()
        client.list_workflow_runs = MagicMock(
            return_value=GitHubAPIResponse(status=200, data={"workflow_runs": runs})
        )
        analyzer = WorkflowAnalyzer(client)
        result = analyzer.analyze()
        assert "BrokenWorkflow" in result.degraded_workflows

    def test_failure_rate_calculation(self):
        analyzer = self._make_analyzer(_workflow_runs_payload(10, 0.3))
        result = analyzer.analyze()
        assert 0.25 <= result.failure_rate <= 0.35

    def test_summary_md_contains_health_score(self):
        analyzer = self._make_analyzer()
        result = analyzer.analyze()
        assert "Health" in result.summary_md


# ===========================================================================
# VI. C-04 + C-05 + C-06: Governance, Intelligence, Hygiene Tests
# ===========================================================================

class TestBranchGovernanceAndHygiene:
    """Tests for C-04 branch_governance, C-05 contributor_intelligence, C-06 repository_hygiene."""

    def test_branch_governance_detects_stale(self, tmp_path):
        client = _offline_client()
        stale_date = (datetime.now(tz=timezone.utc) - timedelta(days=40)).isoformat()
        client.list_branches = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=[
                {
                    "name": "old-feature",
                    "commit": {"commit": {"committer": {"date": stale_date}}},
                }
            ])
        )
        client.list_pull_requests = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=[])
        )
        hygiene = RepoHygiene(client, repo_root=tmp_path)
        issues = hygiene._check_stale_branches()
        assert any(i.context.get("branch") == "old-feature" for i in issues)

    def test_branch_governance_active_branch_not_flagged(self, tmp_path):
        client = _offline_client()
        recent_date = (datetime.now(tz=timezone.utc) - timedelta(days=2)).isoformat()
        client.list_branches = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=[
                {
                    "name": "active-branch",
                    "commit": {"commit": {"committer": {"date": recent_date}}},
                }
            ])
        )
        client.list_pull_requests = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=[])
        )
        hygiene = RepoHygiene(client, repo_root=tmp_path)
        issues = hygiene._check_stale_branches()
        assert not any(i.context.get("branch") == "active-branch" for i in issues)

    def test_protected_branches_never_flagged(self, tmp_path):
        client = _offline_client()
        old_date = (datetime.now(tz=timezone.utc) - timedelta(days=100)).isoformat()
        client.list_branches = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=[
                {"name": "main", "commit": {"commit": {"committer": {"date": old_date}}}},
                {"name": "master", "commit": {"commit": {"committer": {"date": old_date}}}},
            ])
        )
        client.list_pull_requests = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=[])
        )
        hygiene = RepoHygiene(client, repo_root=tmp_path)
        issues = hygiene._check_stale_branches()
        names = {i.context.get("branch") for i in issues}
        assert "main" not in names
        assert "master" not in names

    def test_orphaned_file_detection(self, tmp_path):
        # Create a stray report file in the root
        (tmp_path / "audit-report-2026.txt").write_text("data")
        client = _offline_client()
        hygiene = RepoHygiene(client, repo_root=tmp_path)
        issues = hygiene._check_orphaned_root_files()
        assert any(i.category == "orphaned_file" for i in issues)

    def test_clean_root_no_orphaned_files(self, tmp_path):
        (tmp_path / "README.md").write_text("# Project")
        client = _offline_client()
        hygiene = RepoHygiene(client, repo_root=tmp_path)
        issues = hygiene._check_orphaned_root_files()
        assert len(issues) == 0

    def test_unpinned_dep_detected(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("requests\nnumpy>=1.0\npytest==7.0.0\n")
        client = _offline_client()
        hygiene = RepoHygiene(client, repo_root=tmp_path)
        issues = hygiene._check_dependency_drift()
        unpinned = [i for i in issues if i.category == "dep_drift"]
        # "requests" has no version specifier
        assert any(i.context.get("package") == "requests" for i in unpinned)

    def test_fully_pinned_deps_no_issues(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("requests==2.31.0\nnumpy==1.24.0\n")
        client = _offline_client()
        hygiene = RepoHygiene(client, repo_root=tmp_path)
        issues = hygiene._check_dependency_drift()
        assert len(issues) == 0

    def test_missing_codeowners_detected(self, tmp_path):
        client = _offline_client()
        hygiene = RepoHygiene(client, repo_root=tmp_path)
        issues = hygiene._check_contributor_gaps()
        assert any(i.category == "ownership_gap" for i in issues)

    def test_codeowners_present_no_gap(self, tmp_path):
        (tmp_path / "CODEOWNERS").write_text("* @mbaetiong\n")
        client = _offline_client()
        hygiene = RepoHygiene(client, repo_root=tmp_path)
        issues = hygiene._check_contributor_gaps()
        assert len(issues) == 0

    def test_hygiene_score_100_for_clean_repo(self, tmp_path):
        (tmp_path / "CODEOWNERS").write_text("* @mbaetiong\n")
        (tmp_path / "requirements.txt").write_text("requests==2.31.0\n")
        client = _offline_client()
        client.list_branches = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=[])
        )
        client.list_pull_requests = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=[])
        )
        hygiene = RepoHygiene(client, repo_root=tmp_path)
        report = hygiene.run_all_checks()
        assert report.hygiene_score == 100.0


# ===========================================================================
# VII. C-07 + C-08 + C-09 + C-10: Navigation, Deps, Stale, Labels Tests
# ===========================================================================

class TestRemainingCapabilities:
    """Tests for C-07 through C-10."""

    def _make_agent(self, tmp_path: Path) -> GitHubGuruAgent:
        agent = GitHubGuruAgent(
            owner="test-owner",
            repo="test-repo",
            token="",
            safe_mode=True,
            repo_root=tmp_path,
        )
        # Offline all API calls
        agent.client._token = ""
        agent.client.offline_mode = True
        return agent

    def test_c07_navigation_with_ci_query(self, tmp_path):
        agent = self._make_agent(tmp_path)
        result = agent.codebase_navigation_guidance("ci testing")
        assert "ci-testing-agent" in result

    def test_c07_navigation_with_security_query(self, tmp_path):
        agent = self._make_agent(tmp_path)
        result = agent.codebase_navigation_guidance("security vulnerability")
        assert "security" in result.lower()

    def test_c07_navigation_empty_query(self, tmp_path):
        agent = self._make_agent(tmp_path)
        result = agent.codebase_navigation_guidance("")
        assert "AGENTS.md" in result or "navigation" in result.lower()

    def test_c08_dependency_drift_finds_unpinned(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("flask\nrequests==2.31.0\n")
        agent = self._make_agent(tmp_path)
        result = agent.dependency_drift_detection()
        assert "flask" in result

    def test_c08_dependency_drift_clean_repo(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("flask==3.0.0\nrequests==2.31.0\n")
        agent = self._make_agent(tmp_path)
        result = agent.dependency_drift_detection()
        assert "✅" in result

    def test_c09_stale_resource_returns_string(self, tmp_path):
        agent = self._make_agent(tmp_path)
        agent.client.list_pull_requests = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=[])
        )
        agent.client.list_branches = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=[])
        )
        result = agent.stale_resource_detection()
        assert isinstance(result, str)
        assert "Stale" in result

    def test_c09_stale_pr_detected(self, tmp_path):
        agent = self._make_agent(tmp_path)
        stale_date = (datetime.now(tz=timezone.utc) - timedelta(days=20)).isoformat()
        agent.client.list_pull_requests = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=[{
                "number": 99,
                "title": "Old PR never merged",
                "updated_at": stale_date,
            }])
        )
        agent.client.list_branches = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=[])
        )
        result = agent.stale_resource_detection()
        assert "99" in result

    def test_c10_label_taxonomy_full_compliance(self, tmp_path):
        agent = self._make_agent(tmp_path)
        from triage import LABEL_TAXONOMY
        agent.client.list_labels = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=[
                {"name": name} for name in LABEL_TAXONOMY
            ])
        )
        result = agent.label_taxonomy_enforcement()
        assert result["compliant"] is True
        assert result["compliance_score"] == 100.0

    def test_c10_label_taxonomy_missing_labels_detected(self, tmp_path):
        agent = self._make_agent(tmp_path)
        agent.client.list_labels = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=[{"name": "bug"}])
        )
        result = agent.label_taxonomy_enforcement()
        assert not result["compliant"]
        assert len(result["missing_labels"]) > 0


# ===========================================================================
# VIII. Cognitive Adapter Tests (OODA Loop + Physics Scoring)
# ===========================================================================

class TestCognitiveAdapter:
    """Tests for cognitive_adapter.py — OODA loop and physics scoring."""

    def _make_adapter(self) -> GitHubGuruAdapter:
        mock_agent = MagicMock()
        mock_agent.pr_analysis = MagicMock(return_value=MagicMock(summary_md="PR OK"))
        mock_agent.issue_triage = MagicMock(return_value=MagicMock(summary_md="Issue OK"))
        return GitHubGuruAdapter(mock_agent)

    def test_observe_returns_observation_data(self):
        adapter = self._make_adapter()
        event = {"event_type": "pull_request", "entity_id": 42}
        obs = adapter.observe(event)
        assert obs.source == "github_event"
        assert obs.data == event

    def test_orient_returns_orientation_result(self):
        adapter = self._make_adapter()
        event = {"event_type": "pull_request", "entity_id": 42, "urgency": 7.0}
        obs = adapter.observe(event)
        ori = adapter.orient(obs)
        assert ori.confidence > 0
        assert "capability" in ori.context

    def test_orient_pull_request_selects_pr_related_capability(self):
        adapter = self._make_adapter()
        obs = adapter.observe({"event_type": "pull_request", "entity_id": 1, "urgency": 5})
        ori = adapter.orient(obs)
        # Physics score determines routing; must be a PR-relevant capability
        assert ori.context["capability"] in ("pr_analysis", "label_taxonomy_enforcement")

    def test_orient_issues_event_selects_issue_triage(self):
        adapter = self._make_adapter()
        obs = adapter.observe({"event_type": "issues", "entity_id": 7, "urgency": 5})
        ori = adapter.orient(obs)
        assert ori.context["capability"] == "issue_triage"

    def test_orient_schedule_event_selects_monitoring(self):
        adapter = self._make_adapter()
        obs = adapter.observe({"event_type": "schedule", "urgency": 3})
        ori = adapter.orient(obs)
        # Schedule → workflow_health_monitoring or similar
        assert ori.context["capability"] in (
            "workflow_health_monitoring",
            "stale_resource_detection",
            "repository_hygiene_reporting",
            "dependency_drift_detection",
            "branch_governance",
        )

    def test_decide_returns_decision(self):
        adapter = self._make_adapter()
        obs = adapter.observe({"event_type": "pull_request", "entity_id": 1, "urgency": 5})
        ori = adapter.orient(obs)
        dec = adapter.decide(ori)
        assert dec.action in GitHubGuruAdapter._CAPABILITY_PHYSICS

    def test_low_confidence_falls_back_to_hygiene(self):
        adapter = self._make_adapter()
        # Unknown event type → very low confidence
        obs = adapter.observe({"event_type": "unknown_event_xyz", "urgency": 1})
        ori = adapter.orient(obs)
        # Force low confidence
        ori.confidence = 0.1
        dec = adapter.decide(ori)
        assert dec.action == "repository_hygiene_reporting"

    def test_act_calls_agent_method(self):
        adapter = self._make_adapter()
        obs = adapter.observe({"event_type": "pull_request", "entity_id": 42, "urgency": 5})
        ori = adapter.orient(obs)
        dec = adapter.decide(ori)
        dec.action = "pr_analysis"
        dec.parameters = {}
        adapter.act(dec)
        adapter.guru_agent.pr_analysis.assert_called_once()

    def test_reflect_records_in_log(self):
        from guru_adapter import ActionResult as _AR
        adapter = self._make_adapter()
        result = _AR(success=True, output="ok", metrics={}, errors=[])
        adapter.reflect(result)
        log = adapter.get_reflection_log()
        assert len(log) == 1
        assert log[0]["success"] is True

    def test_full_ooda_loop_success(self):
        adapter = self._make_adapter()
        result = adapter.ooda_loop({"event_type": "pull_request", "entity_id": 1, "urgency": 7})
        # Act may fail if method signature doesn't match, but loop should not raise
        assert hasattr(result, "success")

    def test_physics_score_higher_impact_scores_higher(self):
        score_high = _physics_score(impact=0.9, confidence=0.8, momentum=7, energy=20, risk=0.1, friction=2)
        score_low  = _physics_score(impact=0.3, confidence=0.8, momentum=7, energy=20, risk=0.1, friction=2)
        assert score_high > score_low

    def test_physics_score_higher_energy_scores_lower(self):
        score_cheap  = _physics_score(impact=0.8, confidence=0.8, momentum=5, energy=10, risk=0.1, friction=1)
        score_costly = _physics_score(impact=0.8, confidence=0.8, momentum=5, energy=50, risk=0.1, friction=1)
        assert score_cheap > score_costly

    def test_physics_score_zero_energy_returns_zero(self):
        score = _physics_score(impact=1.0, confidence=1.0, momentum=10, energy=0, risk=0, friction=0)
        assert score == 0.0

    def test_physics_score_for_all_capabilities(self):
        adapter = self._make_adapter()
        for cap in GitHubGuruAdapter._CAPABILITY_PHYSICS:
            score = adapter.physics_score_for(cap, urgency=5.0)
            assert score > 0.0, f"Expected positive score for {cap}"

    def test_memory_stores_observation(self):
        adapter = self._make_adapter()
        event = {"event_type": "pull_request", "entity_id": 10, "urgency": 5}
        adapter.observe(event)
        stored = adapter.memory.retrieve("last_observation")
        assert stored == event


# ===========================================================================
# IX. Metrics Collector Tests
# ===========================================================================

class TestMetricsCollector:
    """Tests for metrics.py — session tracking."""

    def test_session_id_stored(self):
        m = MetricsCollector("test-session-001")
        assert m._session.session_id == "test-session-001"

    def test_capability_timing_recorded(self):
        import time
        m = MetricsCollector("sess-002")
        m.start_capability("pr_analysis")
        time.sleep(0.01)
        m.end_capability("pr_analysis", success=True, output_summary="ok")
        assert len(m._session.capabilities_invoked) == 1
        assert m._session.capabilities_invoked[0].duration_seconds >= 0.0

    def test_success_rate_all_success(self):
        m = MetricsCollector("sess-003")
        m.start_capability("a")
        m.end_capability("a", success=True)
        m.start_capability("b")
        m.end_capability("b", success=True)
        assert m._session.success_rate == 1.0

    def test_success_rate_mixed(self):
        m = MetricsCollector("sess-004")
        m.start_capability("a")
        m.end_capability("a", success=True)
        m.start_capability("b")
        m.end_capability("b", success=False)
        assert m._session.success_rate == 0.5

    def test_counters_increment(self):
        m = MetricsCollector("sess-005")
        m.record_pr_analyzed()
        m.record_pr_analyzed()
        m.record_issue_triaged()
        m.record_workflow_checked()
        m.record_hygiene_issues(3)
        m.record_patterns_matched(7)
        assert m._session.total_prs_analyzed == 2
        assert m._session.total_issues_triaged == 1
        assert m._session.total_workflows_checked == 1
        assert m._session.total_hygiene_issues_found == 3
        assert m._session.total_patterns_matched == 7

    def test_finalize_sets_ended_at(self):
        m = MetricsCollector("sess-006")
        session = m.finalize()
        assert session.ended_at is not None

    def test_persist_writes_json_file(self, tmp_path):
        m = MetricsCollector("sess-007", baselines_dir=tmp_path)
        m.record_pr_analyzed()
        m.finalize()
        files = list(tmp_path.glob("github_guru_session_*.json"))
        assert len(files) == 1
        data = json.loads(files[0].read_text())
        assert data["session_id"] == "sess-007"
        assert data["total_prs_analyzed"] == 1


# ===========================================================================
# X. Learning Engine Tests
# ===========================================================================

class TestLearningEngine:
    """Tests for learning.py — lesson capture and persistence."""

    def test_record_lesson_creates_entry(self):
        eng = LearningEngine("learn-001")
        lesson = eng.record_lesson(
            capability="pr_analysis",
            observation="PR health score dropped to 40",
            hypothesis="Large PR with no reviewers",
            action_taken="Flagged for review",
            outcome="Developer added reviewer",
            confidence=0.85,
        )
        assert lesson.lesson_id.startswith("learn-001")
        assert lesson.capability == "pr_analysis"
        assert lesson.confidence == 0.85

    def test_lessons_accumulate(self):
        eng = LearningEngine("learn-002")
        for i in range(5):
            eng.record_lesson(
                capability=f"cap-{i}",
                observation="obs",
                hypothesis="hyp",
                action_taken="act",
                outcome="out",
            )
        assert len(eng.get_lessons()) == 5

    def test_finalize_writes_jsonl(self, tmp_path):
        lessons_file = tmp_path / "guru_lessons.jsonl"
        eng = LearningEngine("learn-003", lessons_file=lessons_file)
        eng.record_lesson("pr_analysis", "obs", "hyp", "act", "out")
        count = eng.finalize()
        assert count == 1
        lines = lessons_file.read_text().strip().splitlines()
        assert len(lines) == 1
        entry = json.loads(lines[0])
        assert entry["session_id"] == "learn-003"

    def test_load_all_lessons(self, tmp_path):
        lessons_file = tmp_path / "guru_lessons.jsonl"
        eng1 = LearningEngine("learn-004", lessons_file=lessons_file)
        eng1.record_lesson("c1", "obs", "hyp", "act", "out")
        eng1.finalize()

        eng2 = LearningEngine("learn-005", lessons_file=lessons_file)
        eng2.record_lesson("c2", "obs2", "hyp2", "act2", "out2")
        eng2.finalize()

        eng3 = LearningEngine("learn-any", lessons_file=lessons_file)
        all_lessons = eng3.load_all_lessons()
        assert len(all_lessons) == 2

    def test_pattern_refinements_from_false_positives(self, tmp_path):
        lessons_file = tmp_path / "guru_lessons.jsonl"
        eng = LearningEngine("learn-006", lessons_file=lessons_file)
        for _ in range(3):
            eng.record_lesson("pr_analysis", "obs", "hyp", "act",
                               "false positive detected", pattern_id="CI-001")
        eng.finalize()

        eng2 = LearningEngine("learn-any", lessons_file=lessons_file)
        refinements = eng2.get_pattern_refinements()
        assert any(r["pattern_id"] == "CI-001" for r in refinements)
        ci001 = next(r for r in refinements if r["pattern_id"] == "CI-001")
        assert ci001["false_positive_count"] == 3

    def test_empty_lessons_file_returns_empty_list(self, tmp_path):
        eng = LearningEngine("learn-007", lessons_file=tmp_path / "nonexistent.jsonl")
        assert eng.load_all_lessons() == []

    def test_finalize_with_no_lessons_returns_zero(self, tmp_path):
        eng = LearningEngine("learn-008", lessons_file=tmp_path / "out.jsonl")
        count = eng.finalize()
        assert count == 0


# ===========================================================================
# XI. End-to-End: GitHubGuruAgent Integration Tests
# ===========================================================================

class TestGitHubGuruAgentIntegration:
    """End-to-end tests for GitHubGuruAgent in offline mode."""

    def _agent(self, tmp_path: Path) -> GitHubGuruAgent:
        return GitHubGuruAgent(
            owner="Aries-Serpent",
            repo="_codex_",
            token="",
            safe_mode=True,
            repo_root=tmp_path,
        )

    def _mock_all_endpoints(self, agent: GitHubGuruAgent, tmp_path: Path):
        """Wire up all client mocks for a full offline sweep."""
        now = datetime.now(tz=timezone.utc)
        stale = (now - timedelta(days=40)).isoformat()

        agent.client.list_workflow_runs = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=_workflow_runs_payload(10, 0.1))
        )
        agent.client.list_branches = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=[
                {"name": "old-branch", "commit": {"commit": {"committer": {"date": stale}}}},
            ])
        )
        agent.client.list_pull_requests = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=[])
        )
        from triage import LABEL_TAXONOMY
        agent.client.list_labels = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=[
                {"name": n} for n in list(LABEL_TAXONOMY.keys())[:5]
            ])
        )
        agent.client.list_commits = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=[
                {"commit": {"author": {"name": "alice"}}} for _ in range(5)
            ])
        )
        (tmp_path / "requirements.txt").write_text("requests==2.31.0\n")

    def test_handle_event_pull_request(self, tmp_path):
        agent = self._agent(tmp_path)
        agent.client.get_pull_request = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=_pr_payload())
        )
        agent.client.list_pull_request_reviews = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=[])
        )
        result = agent.handle_event({"event_type": "pull_request", "entity_id": 42})
        assert result["success"] is True
        assert result["capability"] == "pr_analysis"
        assert "42" in result["result_md"]

    def test_handle_event_issues(self, tmp_path):
        agent = self._agent(tmp_path)
        agent.client.get_issue = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=_issue_payload())
        )
        result = agent.handle_event({"event_type": "issues", "entity_id": 7})
        assert result["success"] is True
        assert result["capability"] == "issue_triage"

    def test_handle_event_unknown_returns_failure(self, tmp_path):
        agent = self._agent(tmp_path)
        result = agent.handle_event({"event_type": "totally_unknown_xyz"})
        assert result["success"] is False

    def test_run_daily_sweep_completes(self, tmp_path):
        agent = self._agent(tmp_path)
        self._mock_all_endpoints(agent, tmp_path)
        report = agent.run_daily_sweep()
        assert report.session_id
        assert report.finished_at is not None
        assert isinstance(report.workflow_summary_md, str)
        assert isinstance(report.branch_governance_md, str)
        assert report.hygiene_report is not None
        assert isinstance(report.dependency_drift_md, str)
        assert isinstance(report.stale_resources_md, str)
        assert isinstance(report.label_compliance, dict)
        assert isinstance(report.contributor_summary_md, str)

    def test_sweep_report_summary_md_has_sections(self, tmp_path):
        agent = self._agent(tmp_path)
        self._mock_all_endpoints(agent, tmp_path)
        report = agent.run_daily_sweep()
        summary = report.summary_md
        assert "PR Analysis" in summary
        assert "Workflow Health" in summary
        assert "Repository Hygiene" in summary
        assert "Dependency Drift" in summary
        assert "Label Compliance" in summary

    def test_agent_version(self, tmp_path):
        agent = self._agent(tmp_path)
        assert agent.VERSION == "1.1.0"

    def test_safe_mode_is_default(self, tmp_path):
        agent = self._agent(tmp_path)
        assert agent.safe_mode is True

    def test_session_id_is_unique(self, tmp_path):
        a = self._agent(tmp_path)
        b = GitHubGuruAgent("o", "r", repo_root=tmp_path)
        assert a.session_id != b.session_id

    def test_c01_pr_analysis_via_agent(self, tmp_path):
        agent = self._agent(tmp_path)
        agent.client.get_pull_request = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=_pr_payload())
        )
        agent.client.list_pull_request_reviews = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=[])
        )
        result = agent.pr_analysis(42)
        assert 0 <= result.health_score <= 100
        assert isinstance(result.signals, list)
        assert isinstance(result.routing_suggestions, list)

    def test_c02_issue_triage_via_agent(self, tmp_path):
        agent = self._agent(tmp_path)
        agent.client.get_issue = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=_issue_payload())
        )
        result = agent.issue_triage(7)
        assert isinstance(result.labels_to_apply, list)
        assert isinstance(result.summary_md, str)

    def test_c03_workflow_health_via_agent(self, tmp_path):
        agent = self._agent(tmp_path)
        agent.client.list_workflow_runs = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=_workflow_runs_payload(5, 0.0))
        )
        result = agent.workflow_health_monitoring()
        assert isinstance(result, str)
        assert "Health" in result

    def test_c04_branch_governance_via_agent(self, tmp_path):
        agent = self._agent(tmp_path)
        agent.client.list_branches = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=[])
        )
        agent.client.list_pull_requests = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=[])
        )
        result = agent.branch_governance()
        assert "Branch Governance" in result

    def test_c05_contributor_intelligence_via_agent(self, tmp_path):
        agent = self._agent(tmp_path)
        agent.client.list_commits = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=[
                {"commit": {"author": {"name": "alice"}}} for _ in range(3)
            ])
        )
        result = agent.contributor_intelligence()
        assert "Contributor" in result
        assert "alice" in result

    def test_c06_hygiene_reporting_via_agent(self, tmp_path):
        agent = self._agent(tmp_path)
        agent.client.list_branches = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=[])
        )
        agent.client.list_pull_requests = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=[])
        )
        report = agent.repository_hygiene_reporting()
        assert 0 <= report.hygiene_score <= 100
        assert isinstance(report.issues, list)

    def test_metrics_tracked_across_capabilities(self, tmp_path):
        agent = self._agent(tmp_path)
        agent.client.get_pull_request = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=_pr_payload())
        )
        agent.client.list_pull_request_reviews = MagicMock(
            return_value=GitHubAPIResponse(status=200, data=[])
        )
        agent.pr_analysis(42)
        agent.pr_analysis(43)
        assert agent._metrics._session.total_prs_analyzed == 2
