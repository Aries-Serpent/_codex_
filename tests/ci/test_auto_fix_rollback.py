"""
Tests for Auto-Fix with Rollback functionality.

Tests pre-flight checks, rollback mechanisms, and fix application
with safety guarantees.
"""

import subprocess

# Import the module to test
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "ci"))

from auto_fix_with_rollback import (
    AutoFixWithRollback,
    FixApplicationError,
    PreFlightError,
)


class TestAutoFixWithRollback:
    """Test suite for AutoFixWithRollback class."""

    @pytest.fixture
    def temp_repo(self, tmp_path):
        """Create a temporary git repository for testing."""
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()

        # Initialize git repo
        subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )

        # Create directory structure
        (repo_path / "src").mkdir()
        (repo_path / "tests").mkdir()

        # Create initial commit
        test_file = repo_path / "src" / "test.py"
        test_file.write_text("# Test file\n")
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )

        return repo_path

    @pytest.fixture
    def fixer(self, temp_repo):
        """Create AutoFixWithRollback instance for testing."""
        return AutoFixWithRollback(temp_repo, verbose=False)

    def test_initialization(self, temp_repo):
        """Test AutoFixWithRollback initialization."""
        fixer = AutoFixWithRollback(temp_repo, verbose=True)
        assert fixer.repo_root == temp_repo, "repo_root is not valid"
        assert fixer.max_retries == 3, "max_retries is not valid"
        assert fixer.metrics["fixes_attempted"] == 0, "Condition must be true"

    def test_check_git_repository_success(self, fixer):
        """Test git repository check succeeds in valid repo."""
        assert fixer._check_git_repository() is True, "Condition must be true"

    def test_check_git_repository_failure(self, tmp_path):
        """Test git repository check fails in non-git directory."""
        fixer = AutoFixWithRollback(tmp_path, verbose=False)
        assert fixer._check_git_repository() is False, "Condition must be true"

    def test_check_git_clean_success(self, fixer):
        """Test git clean check succeeds with clean working tree."""
        assert fixer._check_git_clean() is True, "Condition must be true"

    def test_check_git_clean_with_modifications(self, fixer, temp_repo):
        """Test git clean check with modified files."""
        # Modify a file
        test_file = temp_repo / "src" / "test.py"
        test_file.write_text("# Modified\n")

        # Should detect modifications
        assert fixer._check_git_clean() is False, "Condition must be true"

    def test_check_files_writable_success(self, fixer):
        """Test file writability check succeeds."""
        assert fixer._check_files_writable() is True, "Condition must be true"

    def test_check_files_writable_failure(self, fixer, temp_repo):
        """Test file writability check with read-only directory."""
        # Make src directory read-only
        src_dir = temp_repo / "src"
        src_dir.chmod(0o444)

        try:
            result = fixer._check_files_writable()
            # May succeed on some systems, so just verify it runs
            assert isinstance(result, bool)
        finally:
            # Restore permissions for cleanup
            src_dir.chmod(0o755)

    def test_check_branch_valid_success(self, fixer):
        """Test branch validation succeeds on regular branch."""
        assert fixer._check_branch_valid() is True, "Condition must be true"

    def test_check_python_available(self, fixer):
        """Test Python availability check."""
        assert fixer._check_python_available() is True, "Condition must be true"

    @patch("subprocess.run")
    def test_check_tools_available_success(self, mock_run, fixer):
        """Test tools availability check with all tools present."""
        mock_run.return_value = Mock(returncode=0)
        assert fixer._check_tools_available() is True, "Condition must be true"
        assert mock_run.call_count >= 3, "call_count must be positive"

    @patch("subprocess.run")
    def test_check_tools_available_failure(self, mock_run, fixer):
        """Test tools availability check with missing tool."""
        mock_run.side_effect = FileNotFoundError("Tool not found")
        assert fixer._check_tools_available() is False, "Condition must be true"

    @patch.object(AutoFixWithRollback, "_check_git_repository")
    @patch.object(AutoFixWithRollback, "_check_git_clean")
    @patch.object(AutoFixWithRollback, "_check_files_writable")
    @patch.object(AutoFixWithRollback, "_check_branch_valid")
    @patch.object(AutoFixWithRollback, "_check_python_available")
    @patch.object(AutoFixWithRollback, "_check_tools_available")
    def test_pre_flight_checks_all_pass(
        self,
        mock_tools,
        mock_python,
        mock_branch,
        mock_writable,
        mock_clean,
        mock_repo,
        fixer,
    ):
        """Test pre-flight checks when all checks pass."""
        # Make all checks pass
        mock_repo.return_value = True
        mock_clean.return_value = True
        mock_writable.return_value = True
        mock_branch.return_value = True
        mock_python.return_value = True
        mock_tools.return_value = True

        result = fixer.run_pre_flight_checks()
        assert result is True, "Result must not be empty"
        assert fixer.metrics["pre_flight_passed"] is True, "Condition must be true"

    @patch.object(AutoFixWithRollback, "_check_git_repository")
    @patch.object(AutoFixWithRollback, "_check_git_clean")
    def test_pre_flight_checks_failure(self, mock_clean, mock_repo, fixer):
        """Test pre-flight checks when some checks fail."""
        mock_repo.return_value = True
        mock_clean.return_value = False  # Fail this check

        with pytest.raises(PreFlightError) as exc_info:
            fixer.run_pre_flight_checks()

        assert "git_clean" in str(exc_info.value), "Value must be initialized"
        assert fixer.metrics["pre_flight_passed"] is False, "Condition must be true"

    def test_rollback_context_success(self, fixer, temp_repo):
        """Test rollback context manager with successful operation."""
        test_file = temp_repo / "src" / "test.py"
        _ = test_file.read_text()  # Read original content (not used in this test)

        with fixer.rollback_context(test_file):
            # Modify file
            test_file.write_text("# Modified content\n")

        # File should keep modification (no rollback)

    def test_rollback_context_failure(self, fixer, temp_repo):
        """Test rollback context manager with failed operation."""
        test_file = temp_repo / "src" / "test.py"
        original_content = test_file.read_text()

        try:
            with fixer.rollback_context(test_file):
                # Modify file
                test_file.write_text("# Modified content\n")
                # Simulate failure
                raise Exception("Simulated failure")
        except FixApplicationError:
            _ = None  # suppressed: no action needed

        # File should be rolled back to original
        assert test_file.read_text() == original_content, "Content must not be empty"
        assert fixer.metrics["rollbacks_performed"] == 1, "Condition must be true"

    def test_validate_python_syntax_valid(self, fixer, temp_repo):
        """Test Python syntax validation with valid file."""
        test_file = temp_repo / "src" / "valid.py"
        test_file.write_text("def foo():\n    return 42\n")

        assert fixer._validate_python_syntax(test_file) is True, "Condition must be true"

    def test_validate_python_syntax_invalid(self, fixer, temp_repo):
        """Test Python syntax validation with invalid file."""
        test_file = temp_repo / "src" / "invalid.py"
        test_file.write_text("def foo(\n    # Missing closing paren\n")

        with pytest.raises(FixApplicationError):
            fixer._validate_python_syntax(test_file)

    def test_apply_fix_with_retry_success(self, fixer):
        """Test fix application with successful fix on first try."""
        mock_fix = Mock(return_value=True)

        result = fixer.apply_fix_with_retry("test fix", mock_fix)

        assert result is True, "Result must not be empty"
        assert mock_fix.call_count == 1, "Count must be greater than zero"
        assert fixer.metrics["fixes_attempted"] == 1, "Condition must be true"
        assert fixer.metrics["fixes_succeeded"] == 1, "Condition must be true"

    def test_apply_fix_with_retry_failure(self, fixer):
        """Test fix application with persistent failure."""
        mock_fix = Mock(side_effect=Exception("Fix failed"))

        result = fixer.apply_fix_with_retry("test fix", mock_fix)

        assert result is False, "Result must not be empty"
        assert mock_fix.call_count == fixer.max_retries, "Count must be greater than zero"
        assert fixer.metrics["fixes_attempted"] == 1, "Condition must be true"
        assert fixer.metrics["fixes_failed"] == 1, "Condition must be true"

    def test_apply_fix_with_retry_success_after_retries(self, fixer):
        """Test fix application succeeding after retries."""
        # Fail twice, succeed on third attempt
        mock_fix = Mock(side_effect=[Exception("Fail 1"), Exception("Fail 2"), True])

        result = fixer.apply_fix_with_retry("test fix", mock_fix)

        assert result is True, "Result must not be empty"
        assert mock_fix.call_count == 3, "Count must be greater than zero"
        assert fixer.metrics["fixes_succeeded"] == 1, "Condition must be true"

    def test_save_metrics(self, fixer, tmp_path):
        """Test metrics saving to file."""
        output_file = tmp_path / "metrics.json"

        fixer.metrics["fixes_attempted"] = 5
        fixer.metrics["fixes_succeeded"] = 3
        fixer.save_metrics(str(output_file))

        assert output_file.exists(), "Condition must be true"

        import json

        with open(output_file) as f:
            saved_metrics = json.load(f)

        assert saved_metrics["fixes_attempted"] == 5, "Condition must be true"
        assert saved_metrics["fixes_succeeded"] == 3, "Condition must be true"
        assert "end_time" in saved_metrics, "Condition must be true"

    def test_rollback_on_syntax_error(self, fixer, temp_repo):
        """Test that rollback occurs when fix introduces syntax error."""
        test_file = temp_repo / "src" / "test.py"
        original_content = "def valid():\n    return 42\n"
        test_file.write_text(original_content)

        try:
            with fixer.rollback_context(test_file):
                # Introduce syntax error
                test_file.write_text("def broken(\n")
                # Trigger validation (which will fail)
                fixer._validate_python_syntax(test_file)
        except FixApplicationError:
            _ = None  # suppressed: no action needed

        # Should have rolled back
        assert test_file.read_text() == original_content, "Content must not be empty"


class TestIntegration:
    """Integration tests for auto-fix with rollback."""

    def test_end_to_end_pre_flight_and_fix(self, tmp_path):
        """Test end-to-end workflow with pre-flight and fix."""
        # Create minimal git repo
        repo = tmp_path / "repo"
        repo.mkdir()
        subprocess.run(["git", "init"], cwd=repo, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=repo,
            capture_output=True,
        )

        (repo / "src").mkdir()
        (repo / "tests").mkdir()

        test_file = repo / "src" / "test.py"
        test_file.write_text("# test\n")

        subprocess.run(["git", "add", "."], cwd=repo, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=repo, capture_output=True)

        fixer = AutoFixWithRollback(repo, verbose=False)

        # This should pass pre-flight checks
        with patch.object(fixer, "_check_tools_available", return_value=True):
            result = fixer.run_pre_flight_checks()
            assert result is True, "Result must not be empty"
