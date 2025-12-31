"""Unit tests for SandboxExecutor with mocked subprocess calls."""
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.executor import SandboxExecutor


class TestSandboxExecutor:
    """Test suite for SandboxExecutor class."""

    @pytest.fixture
    def tmp_workspace(self, tmp_path):
        """Create temporary workspace."""
        return tmp_path

    @pytest.fixture
    def executor(self, tmp_workspace):
        """Create SandboxExecutor instance."""
        return SandboxExecutor(workspace=tmp_workspace, timeout=60)

    def test_init(self, tmp_workspace):
        """Test SandboxExecutor initialization."""
        executor = SandboxExecutor(workspace=tmp_workspace, timeout=120)
        assert executor.workspace == tmp_workspace
        assert executor.timeout == 120

    @patch("subprocess.run")
    def test_execute_success(self, mock_run, executor):
        """Test successful command execution."""
        # Mock successful subprocess
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Test output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        task = {"command": "pytest", "args": ["tests/"]}

        result = executor.execute(task)

        assert result["status"] == "success"
        assert result["returncode"] == 0
        assert result["stdout"] == "Test output"
        assert "pytest" in result["command"]

    @patch("subprocess.run")
    def test_execute_failure(self, mock_run, executor):
        """Test command execution with failure."""
        # Mock failed subprocess
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error occurred"
        mock_run.return_value = mock_result

        task = {"command": "pytest", "args": ["tests/"]}

        result = executor.execute(task)

        assert result["status"] == "failure"
        assert result["returncode"] == 1
        assert result["stderr"] == "Error occurred"

    @patch("subprocess.run")
    def test_execute_timeout(self, mock_run, executor):
        """Test command execution timeout."""
        import subprocess

        # Mock timeout
        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd=["pytest"], timeout=60, output=b"", stderr=b""
        )

        task = {"command": "pytest", "args": ["tests/"]}

        result = executor.execute(task)

        assert result["status"] == "timeout"
        assert result["returncode"] == -1
        assert "timed out" in result["error"].lower()

    @patch("subprocess.run")
    def test_execute_command_not_found(self, mock_run, executor):
        """Test execution when command not found."""
        # Mock FileNotFoundError
        mock_run.side_effect = FileNotFoundError("Command not found")

        task = {"command": "nonexistent_command"}

        result = executor.execute(task)

        assert result["status"] == "error"
        assert result["returncode"] == -1
        assert "not found" in result["error"].lower()

    @patch("subprocess.run")
    def test_execute_with_env(self, mock_run, executor):
        """Test execution with environment variables."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        task = {
            "command": "pytest",
            "args": [],
            "env": {"TEST_VAR": "value"},
        }

        result = executor.execute(task)

        # Verify env was passed
        call_kwargs = mock_run.call_args[1]
        assert "TEST_VAR" in call_kwargs["env"]
        assert call_kwargs["env"]["TEST_VAR"] == "value"

    @patch("subprocess.run")
    def test_execute_parallel(self, mock_run, executor):
        """Test parallel execution of multiple tasks."""
        # Mock successful executions
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Success"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        tasks = [
            {"command": "pytest", "args": ["tests/unit/"]},
            {"command": "pytest", "args": ["tests/integration/"]},
        ]

        results = executor.execute_parallel(tasks, max_workers=2)

        assert len(results) == 2
        for result in results:
            assert result["status"] == "success"

    def test_validate_command_allowed(self, executor):
        """Test command validation for allowed commands."""
        assert executor.validate_command("pytest") is True
        assert executor.validate_command("python") is True
        assert executor.validate_command("coverage") is True

    def test_validate_command_disallowed(self, executor):
        """Test command validation for disallowed commands."""
        assert executor.validate_command("rm") is False
        assert executor.validate_command("curl") is False
        assert executor.validate_command("wget") is False

    @patch("subprocess.run")
    def test_execute_with_validation(self, mock_run, executor):
        """Test execution with command validation."""
        # Test allowed command
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        task = {"command": "pytest"}
        result = executor.execute_with_validation(task)
        assert result["status"] == "success"

        # Test disallowed command
        task = {"command": "rm"}
        result = executor.execute_with_validation(task)
        assert result["status"] == "error"
        assert "not allowed" in result["error"].lower()

    @patch("subprocess.run")
    def test_execute_custom_timeout(self, mock_run, executor):
        """Test execution with custom timeout."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        task = {"command": "pytest", "timeout": 120}

        result = executor.execute(task)

        # Verify timeout was passed
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["timeout"] == 120
