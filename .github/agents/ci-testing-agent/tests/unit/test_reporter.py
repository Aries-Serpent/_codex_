"""Unit tests for ArtifactReporter with mocked file operations."""
import sys
from datetime import datetime
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.reporter import ArtifactReporter


class TestArtifactReporter:
    """Test suite for ArtifactReporter class."""

    @pytest.fixture
    def tmp_workspace(self, tmp_path):
        """Create temporary workspace."""
        return tmp_path

    @pytest.fixture
    def reporter(self, tmp_workspace):
        """Create ArtifactReporter instance."""
        return ArtifactReporter(workspace=tmp_workspace)

    def test_init(self, tmp_workspace):
        """Test ArtifactReporter initialization."""
        reporter = ArtifactReporter(workspace=tmp_workspace)
        assert reporter.workspace == tmp_workspace
        assert reporter.reports_dir.exists()

    def test_report_creates_files(self, reporter, tmp_workspace):
        """Test that report creates JSON and markdown files."""
        result = {
            "status": "success",
            "files_generated": 5,
            "timestamp": datetime.utcnow().isoformat(),
        }

        reporter.report(result)

        # Check JSON report exists
        reports = list(tmp_workspace.glob(".reports/report_*.json"))
        assert len(reports) >= 1

        # Check markdown summary exists
        summaries = list(tmp_workspace.glob(".reports/summary_*.md"))
        assert len(summaries) >= 1

    def test_report_adds_timestamp(self, reporter):
        """Test that report adds timestamp if missing."""
        result = {"status": "success"}

        reporter.report(result)

        # Timestamp should be added
        assert "timestamp" in result

    def test_generate_summary_generate_tests(self, reporter):
        """Test summary generation for test generation task."""
        result = {
            "status": "success",
            "task_type": "generate_tests",
            "files_generated": 3,
            "module": "codex.ingest",
            "threshold": 85,
            "test_files": [
                {"path": "tests/test_a.py", "function": "func_a"},
                {"path": "tests/test_b.py", "function": "func_b"},
            ],
        }

        summary = reporter._generate_summary(result)

        assert "Test Generation Results" in summary
        assert "3" in summary  # Files generated count
        assert "codex.ingest" in summary
        assert "tests/test_a.py" in summary

    def test_generate_summary_validate_coverage(self, reporter):
        """Test summary generation for coverage validation task."""
        result = {
            "status": "success",
            "task_type": "validate_coverage",
            "current_coverage": 87.5,
            "baseline_coverage": 82.0,
            "delta": 5.5,
            "threshold": 85,
            "meets_threshold": True,
            "gaps": [],
        }

        summary = reporter._generate_summary(result)

        assert "Coverage Validation Results" in summary
        assert "87.50%" in summary
        assert "82.00%" in summary
        assert "+5.50%" in summary
        assert "Yes" in summary

    def test_generate_summary_execute_tests(self, reporter):
        """Test summary generation for test execution task."""
        result = {
            "status": "failure",
            "task_type": "execute_tests",
            "returncode": 1,
            "command": "pytest tests/",
            "stdout": "Test output here",
            "stderr": "Error message",
        }

        summary = reporter._generate_summary(result)

        assert "Test Execution Results" in summary
        assert "pytest tests/" in summary
        assert "1" in summary  # Exit code
        assert "Test output here" in summary

    def test_generate_summary_with_error(self, reporter):
        """Test summary generation with error."""
        result = {
            "status": "error",
            "error": "Something went wrong",
        }

        summary = reporter._generate_summary(result)

        assert "Error" in summary
        assert "Something went wrong" in summary

    def test_generate_summary_coverage_gaps(self, reporter):
        """Test summary with coverage gaps."""
        result = {
            "status": "below_threshold",
            "task_type": "validate_coverage",
            "current_coverage": 75.0,
            "baseline_coverage": 70.0,
            "delta": 5.0,
            "threshold": 85,
            "meets_threshold": False,
            "gaps": [
                "Overall coverage 75.00% is 10.00% below target 85%",
                "Module src/module.py: 60.00% coverage",
            ],
        }

        summary = reporter._generate_summary(result)

        assert "Coverage Gaps" in summary
        assert "75.00%" in summary
        assert "10.00% below" in summary

    def test_status_emoji(self, reporter):
        """Test status emoji mapping."""
        assert reporter._status_emoji("success") == "✅"
        assert reporter._status_emoji("failure") == "❌"
        assert reporter._status_emoji("error") == "🔥"
        assert reporter._status_emoji("timeout") == "⏱️"
        assert reporter._status_emoji("below_threshold") == "⚠️"
        assert reporter._status_emoji("unknown") == "❓"

    def test_upload_artifact(self, reporter, tmp_workspace, capsys):
        """Test artifact upload placeholder."""
        artifact_file = tmp_workspace / "test.json"
        artifact_file.write_text("{}")

        result = reporter.upload_artifact(artifact_file, "test-artifact")

        assert result is True
        captured = capsys.readouterr()
        assert "Artifact ready" in captured.out

    def test_create_pr_comment(self, reporter, capsys):
        """Test PR comment creation placeholder."""
        result = reporter.create_pr_comment(123, "Test comment")

        assert result is True
        captured = capsys.readouterr()
        assert "PR comment ready" in captured.out
        assert "#123" in captured.out

    def test_update_commit_status(self, reporter, capsys):
        """Test commit status update placeholder."""
        result = reporter.update_commit_status(
            "abc123", "success", "Tests passed"
        )

        assert result is True
        captured = capsys.readouterr()
        assert "Commit status" in captured.out
        assert "abc123" in captured.out

    def test_summary_truncates_long_output(self, reporter):
        """Test that summary truncates very long output."""
        long_output = "X" * 2000
        result = {
            "status": "success",
            "task_type": "execute_tests",
            "returncode": 0,
            "command": "pytest",
            "stdout": long_output,
        }

        summary = reporter._generate_summary(result)

        # Should be truncated
        assert "truncated" in summary
        assert len(summary) < len(long_output) + 500
