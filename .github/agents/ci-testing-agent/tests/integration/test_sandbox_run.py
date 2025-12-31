"""Integration tests running agent in sandbox repository."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

# Path to agent CLI
AGENT_CLI = Path(__file__).parent.parent.parent / "cli.py"


class TestSandboxIntegration:
    """Integration tests for complete agent execution."""

    @pytest.fixture
    def sandbox_repo(self, tmp_path):
        """Create a sandbox repository with test structure."""
        repo_dir = tmp_path / "test_repo"
        repo_dir.mkdir()

        # Create src directory with sample module
        src_dir = repo_dir / "src"
        src_dir.mkdir()

        sample_module = src_dir / "sample.py"
        sample_module.write_text(
            """
def add(x, y):
    return x + y

def subtract(x, y):
    return x - y
"""
        )

        # Create manifest
        manifest = repo_dir / "manifest.yaml"
        manifest.write_text(
            """
name: Test Repository
version: 1.0.0
"""
        )

        return repo_dir

    @pytest.mark.skipif(
        not AGENT_CLI.exists(), reason="Agent CLI not found"
    )
    def test_full_agent_execution_generate_tests(self, sandbox_repo):
        """Test complete agent execution for test generation."""
        manifest = sandbox_repo / "manifest.yaml"
        task = json.dumps(
            {
                "type": "generate_tests",
                "module": "sample",
                "threshold": 85,
            }
        )

        # Execute agent
        result = subprocess.run(
            [
                sys.executable,
                str(AGENT_CLI),
                "--manifest",
                str(manifest),
                "--task",
                task,
                "--workspace",
                str(sandbox_repo),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Check execution
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)

        # Should complete (even if no tests generated)
        assert result.returncode in [0, 1]  # Success or expected failure
        assert "CI Testing Agent" in result.stdout

    @pytest.mark.skipif(
        not AGENT_CLI.exists(), reason="Agent CLI not found"
    )
    def test_agent_execution_with_invalid_task(self, sandbox_repo):
        """Test agent execution with invalid task type."""
        manifest = sandbox_repo / "manifest.yaml"
        task = json.dumps({"type": "invalid_task_type"})

        result = subprocess.run(
            [
                sys.executable,
                str(AGENT_CLI),
                "--manifest",
                str(manifest),
                "--task",
                task,
                "--workspace",
                str(sandbox_repo),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should fail with error
        assert result.returncode == 1
        assert "Unknown task type" in result.stderr or "Unknown task type" in result.stdout

    @pytest.mark.skipif(
        not AGENT_CLI.exists(), reason="Agent CLI not found"
    )
    def test_agent_execution_missing_manifest(self, tmp_path):
        """Test agent execution with missing manifest."""
        task = json.dumps({"type": "generate_tests", "module": "sample"})

        result = subprocess.run(
            [
                sys.executable,
                str(AGENT_CLI),
                "--manifest",
                str(tmp_path / "nonexistent.yaml"),
                "--task",
                task,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should fail
        assert result.returncode == 1

    @pytest.mark.skipif(
        not AGENT_CLI.exists(), reason="Agent CLI not found"
    )
    def test_agent_execution_invalid_json(self, sandbox_repo):
        """Test agent execution with invalid JSON task."""
        manifest = sandbox_repo / "manifest.yaml"
        task = "not valid json"

        result = subprocess.run(
            [
                sys.executable,
                str(AGENT_CLI),
                "--manifest",
                str(manifest),
                "--task",
                task,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should fail with JSON error
        assert result.returncode == 1
        assert "JSON" in result.stderr or "JSON" in result.stdout

    @pytest.mark.skipif(
        not AGENT_CLI.exists(), reason="Agent CLI not found"
    )
    def test_agent_creates_reports(self, sandbox_repo):
        """Test that agent creates report files."""
        manifest = sandbox_repo / "manifest.yaml"
        task = json.dumps({"type": "generate_tests", "module": "sample"})

        result = subprocess.run(
            [
                sys.executable,
                str(AGENT_CLI),
                "--manifest",
                str(manifest),
                "--task",
                task,
                "--workspace",
                str(sandbox_repo),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Check reports directory created
        reports_dir = sandbox_repo / ".reports"
        assert reports_dir.exists()

        # Check for report files
        json_reports = list(reports_dir.glob("report_*.json"))
        md_summaries = list(reports_dir.glob("summary_*.md"))

        assert len(json_reports) >= 1 or len(md_summaries) >= 1

    def test_cli_help(self):
        """Test CLI help output."""
        result = subprocess.run(
            [sys.executable, str(AGENT_CLI), "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0
        assert "CI Testing Agent" in result.stdout
        assert "--manifest" in result.stdout
        assert "--task" in result.stdout
        assert "--workspace" in result.stdout
