"""
Tests for Telemetry Collection Script.

Tests GitHub Actions telemetry collection, pattern classification,
and report generation functionality.
"""

import json

# Import the module to test
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "ci"))

from collect_telemetry import TelemetryCollector


class TestTelemetryCollector:
    """Test suite for TelemetryCollector class."""

    @pytest.fixture
    def collector(self):
        """Create a TelemetryCollector instance for testing."""
        return TelemetryCollector(
            owner="test-owner", repo="test-repo", token="test-token"
        )

    @pytest.fixture
    def mock_workflow_runs(self):
        """Create mock workflow run data."""
        return [
            {
                "id": 1001,
                "name": "Auto-Fix Common Issues",
                "html_url": "https://github.com/test/test/actions/runs/1001",
                "conclusion": "failure",
                "created_at": "2024-01-01T00:00:00Z",
            },
            {
                "id": 1002,
                "name": "Coverage Report Generation",
                "html_url": "https://github.com/test/test/actions/runs/1002",
                "conclusion": "timed_out",
                "created_at": "2024-01-01T01:00:00Z",
            },
            {
                "id": 1003,
                "name": "Resilient Test Suite",
                "html_url": "https://github.com/test/test/actions/runs/1003",
                "conclusion": "success",
                "created_at": "2024-01-01T02:00:00Z",
            },
        ]

    @pytest.fixture
    def mock_jobs(self):
        """Create mock job data for individual job collection test."""
        return [
            {
                "id": 2001,
                "name": "auto-fix",
                "html_url": "https://github.com/test/test/runs/2001",
                "status": "completed",
                "conclusion": "failure",
            }
        ]

    @pytest.fixture
    def mock_jobs_by_run(self):
        """Create mock job data mapped by run ID for report generation."""
        return {
            1001: [  # Auto-Fix Common Issues run
                {
                    "id": 2001,
                    "name": "auto-fix",
                    "html_url": "https://github.com/test/test/runs/2001",
                    "status": "completed",
                    "conclusion": "failure",
                }
            ],
            1002: [  # Coverage Report Generation run
                {
                    "id": 2002,
                    "name": "coverage-report",
                    "html_url": "https://github.com/test/test/runs/2002",
                    "status": "completed",
                    "conclusion": "timed_out",
                }
            ],
        }

    @pytest.fixture
    def mock_artifacts(self):
        """Create mock artifact data."""
        return [
            {
                "id": 3001,
                "name": "test-results",
                "size_in_bytes": 1024,
                "expired": False,
            }
        ]

    def test_initialization(self, collector):
        """Test TelemetryCollector initialization."""
        assert collector.owner == "test-owner"
        assert collector.repo == "test-repo"
        assert collector.token == "test-token"
        assert collector.base_url == "https://api.github.com"
        assert "Authorization" in collector.headers

    def test_pattern_keywords_defined(self, collector):
        """Test that all core patterns have keywords defined."""
        assert len(collector.PATTERN_KEYWORDS) >= 5
        assert "auto-fix" in collector.PATTERN_KEYWORDS
        assert "test-infrastructure" in collector.PATTERN_KEYWORDS
        assert "coverage-timeout" in collector.PATTERN_KEYWORDS
        assert "filesystem-deadlock" in collector.PATTERN_KEYWORDS
        assert "pre-merge-cascade" in collector.PATTERN_KEYWORDS

    def test_classify_failure_auto_fix(self, collector):
        """Test classification of auto-fix pattern."""
        run = {"name": "Auto-Fix Common Issues"}
        jobs = [{"name": "detect-and-fix"}]
        pattern = collector.classify_failure(run, jobs)
        assert pattern == "auto-fix"

    def test_classify_failure_coverage_timeout(self, collector):
        """Test classification of coverage timeout pattern."""
        run = {"name": "Coverage Report Generation"}
        jobs = [{"name": "pytest-cov"}]
        pattern = collector.classify_failure(run, jobs)
        assert pattern == "coverage-timeout"

    def test_classify_failure_test_infrastructure(self, collector):
        """Test classification of test infrastructure pattern."""
        run = {"name": "Resilient Validation Suite"}
        jobs = [{"name": "test-runner"}]
        pattern = collector.classify_failure(run, jobs)
        assert pattern == "test-infrastructure"

    def test_classify_failure_filesystem_deadlock(self, collector):
        """Test classification of filesystem deadlock pattern."""
        run = {"name": "Root Organization Validation"}
        jobs = [{"name": "file-validation"}]
        pattern = collector.classify_failure(run, jobs)
        assert pattern == "filesystem-deadlock"

    def test_classify_failure_pre_merge_cascade(self, collector):
        """Test classification of pre-merge cascade pattern."""
        run = {"name": "Pre-Merge Final Checks"}
        jobs = [{"name": "merge validation"}]
        pattern = collector.classify_failure(run, jobs)
        assert pattern == "pre-merge-cascade"

    def test_classify_failure_unknown(self, collector):
        """Test classification of unknown pattern."""
        run = {"name": "Some Random Workflow"}
        jobs = [{"name": "unknown-job"}]
        pattern = collector.classify_failure(run, jobs)
        assert pattern == "unknown"

    @patch("collect_telemetry.requests.get")
    def test_collect_workflow_runs(self, mock_get, collector, mock_workflow_runs):
        """Test workflow run collection."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {"workflow_runs": mock_workflow_runs}
        mock_get.return_value = mock_response

        runs = collector.collect_workflow_runs("main", days=7)

        assert len(runs) == 3
        assert runs[0]["name"] == "Auto-Fix Common Issues"
        mock_get.assert_called_once()

    @patch("collect_telemetry.requests.get")
    def test_collect_workflow_runs_pagination(self, mock_get, collector):
        """Test workflow run collection with pagination."""
        # First page: 100 results
        first_page = [{"id": i} for i in range(100)]
        # Second page: 50 results (last page)
        second_page = [{"id": i} for i in range(100, 150)]

        mock_responses = [
            Mock(
                json=Mock(return_value={"workflow_runs": first_page}),
                raise_for_status=Mock(),
            ),
            Mock(
                json=Mock(return_value={"workflow_runs": second_page}),
                raise_for_status=Mock(),
            ),
        ]
        mock_get.side_effect = mock_responses

        runs = collector.collect_workflow_runs("main", days=7, max_pages=10)

        assert len(runs) == 150
        assert mock_get.call_count == 2

    @patch("collect_telemetry.requests.get")
    def test_collect_job_details(self, mock_get, collector, mock_jobs):
        """Test job details collection."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {"jobs": mock_jobs}
        mock_get.return_value = mock_response

        jobs = collector.collect_job_details(1001)

        assert len(jobs) == 1
        assert jobs[0]["name"] == "auto-fix"

    @patch("collect_telemetry.requests.get")
    def test_collect_artifacts(self, mock_get, collector, mock_artifacts):
        """Test artifact collection."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {"artifacts": mock_artifacts}
        mock_get.return_value = mock_response

        artifacts = collector.collect_artifacts(1001)

        assert len(artifacts) == 1
        assert artifacts[0]["name"] == "test-results"

    @patch("collect_telemetry.TelemetryCollector.collect_artifacts")
    @patch("collect_telemetry.TelemetryCollector.collect_job_details")
    @patch("collect_telemetry.TelemetryCollector.collect_workflow_runs")
    def test_generate_report(
        self,
        mock_collect_runs,
        mock_collect_jobs,
        mock_collect_artifacts,
        collector,
        mock_workflow_runs,
        mock_jobs_by_run,
        mock_artifacts,
        tmp_path,
    ):
        """Test telemetry report generation."""
        mock_collect_runs.return_value = mock_workflow_runs
        # Use side_effect to return different jobs for different runs
        mock_collect_jobs.side_effect = lambda run_id: mock_jobs_by_run.get(run_id, [])
        mock_collect_artifacts.return_value = mock_artifacts

        output_file = tmp_path / "test_report.json"
        report = collector.generate_report("main", days=7, output=str(output_file))

        # Verify report structure
        assert "generated_at" in report
        assert "repository" in report
        assert report["repository"] == "test-owner/test-repo"
        assert report["branch"] == "main"
        assert report["days_analyzed"] == 7

        # Verify summary
        assert report["summary"]["total_runs"] == 3
        assert report["summary"]["failed_runs"] == 2  # failure + timed_out
        assert report["summary"]["failure_rate"] > 0

        # Verify pattern distribution
        assert "auto-fix" in report["pattern_distribution"]
        # Note: coverage-timeout pattern may or may not be present depending on mock data
        # The mock data includes a timed_out conclusion which should trigger this pattern
        assert "coverage-timeout" in report["pattern_distribution"]

        # Verify failed runs
        assert len(report["failed_runs"]) == 2

        # Verify file was written
        assert output_file.exists()
        with open(output_file) as f:
            saved_report = json.load(f)
            assert saved_report["repository"] == "test-owner/test-repo"

    def test_telemetry_report_structure(self, collector):
        """Test that telemetry report has correct structure."""
        # Create minimal mock data
        with patch.object(
            collector, "collect_workflow_runs", return_value=[]
        ):
            report = collector.generate_report("main", output="/tmp/test.json")

        required_keys = [
            "generated_at",
            "repository",
            "branch",
            "days_analyzed",
            "summary",
            "pattern_distribution",
            "failed_runs",
        ]

        for key in required_keys:
            assert key in report, f"Missing required key: {key}"

        # Verify summary structure
        assert "total_runs" in report["summary"]
        assert "failed_runs" in report["summary"]
        assert "failure_rate" in report["summary"]


class TestClassifyRunCLI:
    """Tests for --classify-run CLI flag added in S150."""

    @pytest.fixture
    def collector(self):
        return TelemetryCollector(owner="test-owner", repo="test-repo", token="test-token")

    def test_classify_run_rebase_gate(self, collector):
        """--classify-run returns rebase-gate for branch-rebase-gate workflow failures."""
        # The branch-rebase-gate.yml workflow has run name "🔀 Branch Rebase Gate"
        # which contains "rebase" — a rebase-gate keyword.
        run = {"name": "🔀 Branch Rebase Gate", "id": 99}
        jobs = [{"name": "REQ-10: Branch Rebase Check"}]
        assert collector.classify_failure(run, jobs) == "rebase-gate"

    def test_classify_run_auth_delegation(self, collector):
        """--classify-run returns auth-delegation for agent-auth-delegation failures.

        Note: "Agent Token Delegation" contains "agent token" (auth-delegation keyword)
        and is therefore classified as auth-delegation, not rebase-gate, even when
        it fails due to the REQ-10 step.  Both patterns are non-fixable; the
        self-healing CI correctly escalates in either case.
        """
        run = {"name": "Agent Token Delegation", "id": 99}
        jobs = [{"name": "🧠 Cognitive Pre-flight Check"}]
        assert collector.classify_failure(run, jobs) == "auth-delegation"

    def test_classify_run_unknown_fallback(self, collector):
        """--classify-run returns 'unknown' when no keywords match."""
        run = {"name": "Completely Unrecognised Workflow XYZ", "id": 99}
        jobs = [{"name": "some-job-with-no-matching-keywords"}]
        assert collector.classify_failure(run, jobs) == "unknown"

    def test_classify_run_dependency_submission(self, collector):
        """'Automatic Dependency Submission' runs classify as security-scan (S150 fix).

        Run 23250109072 was a GitHub Advanced Security dependency-graph submission
        that failed with a transient GitHub API error.  Before S150 it was always
        classified as 'unknown' because no keyword matched its name.
        """
        run = {"name": "Automatic Dependency Submission (Python)", "id": 23250109072}
        jobs = [{"name": "submit-pypi"}]
        assert collector.classify_failure(run, jobs) == "security-scan"

    def test_classify_run_main_entrypoint_prints_pattern(self, capsys):
        """main() with --classify-run prints the pattern and exits cleanly."""
        import sys as _sys

        import collect_telemetry as ct_mod

        mock_run_resp = Mock()
        mock_run_resp.json.return_value = {
            "name": "Resilient Validation Suite",
            "id": 12345,
        }
        mock_run_resp.raise_for_status = Mock()

        mock_jobs_resp = Mock()
        mock_jobs_resp.json.return_value = {
            "jobs": [{"name": "pytest resilient validation"}]
        }
        mock_jobs_resp.raise_for_status = Mock()

        with (
            patch("requests.get", side_effect=[mock_run_resp, mock_jobs_resp]),
            patch.object(_sys, "argv", [
                "collect_telemetry.py",
                "--owner", "test-owner",
                "--repo", "test-repo",
                "--token", "test-tok",
                "--classify-run", "12345",
            ]),
        ):
            ct_mod.main()

        captured = capsys.readouterr()
        assert captured.out.strip() == "test-infrastructure"

    def test_classify_run_api_error_prints_unknown(self, capsys):
        """main() with --classify-run prints 'unknown' when API call fails."""
        import sys as _sys

        import collect_telemetry as ct_mod

        with (
            patch("requests.get", side_effect=Exception("network error")),
            patch.object(_sys, "argv", [
                "collect_telemetry.py",
                "--owner", "test-owner",
                "--repo", "test-repo",
                "--token", "test-tok",
                "--classify-run", "99999",
            ]),
        ):
            ct_mod.main()

        captured = capsys.readouterr()
        assert "unknown" in captured.out
