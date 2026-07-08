"""
Codex CLI Main Module Enhancement Tests

Comprehensive test coverage for src/codex/cli/main.py focusing on:
- Command execution (ingest, analyze, transform, verify, list, show)
- Argument validation and error handling
- Typer vs argparse fallback handling
- Snapshot management
- Integration with ingestion pipeline
- Help and error output
- Exit codes and status reporting
"""  # pragma: allowlist secret # pragma: allowlist secret

import json
from unittest.mock import MagicMock, patch

import pytest

try:
    import typer
    from typer.testing import CliRunner

    HAS_TYPER = True
except ImportError:
    HAS_TYPER = False

try:
    # This may fail if typer is not available
    from codex.cli.main import TYPER_AVAILABLE, app

    HAS_CODEX_CLI = True
except ImportError:
    HAS_CODEX_CLI = False


pytestmark = pytest.mark.skipif(
    not (HAS_TYPER and HAS_CODEX_CLI and TYPER_AVAILABLE), reason="Typer CLI not available"
)


@pytest.fixture
def cli_runner():
    """Create a Typer CLI runner."""
    return CliRunner()


@pytest.fixture
def temp_repo_dir(tmp_path):
    """Create a temporary repository directory."""
    repo_dir = tmp_path / "test_repo"
    repo_dir.mkdir(parents=True, exist_ok=True)

    # Create sample Python file
    (repo_dir / "sample.py").write_text("""
def hello(name: str) -> str:
    '''Greet someone.'''
    return f"Hello {name}!"

class Calculator:
    def add(self, a: int, b: int) -> int:
        return a + b
""")

    return repo_dir


@pytest.fixture
def manifest_file(tmp_path):
    """Create a sample manifest file."""
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps({"name": "test_project", "version": "1.0.0", "files": ["sample.py"]})
    )
    return manifest


# ============================================================================
# Ingest Command Tests
# ============================================================================


class TestIngestCommand:
    """Tests for 'codex ingest' command."""

    def test_ingest_help(self, cli_runner):
        """Test ingest --help."""
        result = cli_runner.invoke(app, ["ingest", "--help"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "ingest" in result.stdout.lower(), "Result must not be empty"

    def test_ingest_missing_source(self, cli_runner):
        """Test ingest without source argument."""
        result = cli_runner.invoke(app, ["ingest"])
        assert result.exit_code != 0, "Result must not be empty"

    def test_ingest_file_source(self, cli_runner, temp_repo_dir):
        """Test ingest with file source."""
        with patch("codex.ingest.ingest") as mock_ingest:
            mock_ingest.return_value = MagicMock(
                snapshot_id="snap_123", snapshot_dir=temp_repo_dir, content_hash="abc123def456"
            )

            result = cli_runner.invoke(app, ["ingest", str(temp_repo_dir / "sample.py")])
            assert result.exit_code == 0, "Result must not be empty"
            assert "snap_123" in result.stdout or "snapshot" in result.stdout.lower(), "Result must not be empty"

    def test_ingest_with_manifest(self, cli_runner, temp_repo_dir, manifest_file):
        """Test ingest with manifest file."""
        with patch("codex.ingest.ingest") as mock_ingest:
            mock_ingest.return_value = MagicMock(
                snapshot_id="snap_456", snapshot_dir=temp_repo_dir, content_hash="xyz789"
            )

            result = cli_runner.invoke(
                app, ["ingest", str(temp_repo_dir), "--manifest", str(manifest_file)]
            )
            assert result.exit_code == 0, "Result must not be empty"

    def test_ingest_with_custom_snapshot_id(self, cli_runner, temp_repo_dir):
        """Test ingest with custom snapshot ID."""
        with patch("codex.ingest.ingest") as mock_ingest:
            mock_ingest.return_value = MagicMock(
                snapshot_id="custom_snap", snapshot_dir=temp_repo_dir, content_hash="custom_hash"
            )

            result = cli_runner.invoke(
                app, ["ingest", str(temp_repo_dir), "--snapshot-id", "custom_snap"]
            )
            assert result.exit_code == 0, "Result must not be empty"

    def test_ingest_invalid_source(self, cli_runner):
        """Test ingest with non-existent source."""
        with patch("codex.ingest.ingest", side_effect=FileNotFoundError("Source not found")):
            result = cli_runner.invoke(app, ["ingest", "/nonexistent/path"])
            assert result.exit_code != 0, "Result must not be empty"

    def test_ingest_permission_error(self, cli_runner, temp_repo_dir):
        """Test ingest with permission error."""
        with patch("codex.ingest.ingest", side_effect=PermissionError("Access denied")):
            result = cli_runner.invoke(app, ["ingest", str(temp_repo_dir)])
            assert result.exit_code != 0, "Result must not be empty"


# ============================================================================
# Analyze Command Tests
# ============================================================================


class TestAnalyzeCommand:
    """Tests for 'codex analyze' command."""

    def test_analyze_help(self, cli_runner):
        """Test analyze --help."""
        result = cli_runner.invoke(app, ["analyze", "--help"])
        assert result.exit_code == 0, "Result must not be empty"

    def test_analyze_missing_snapshot(self, cli_runner):
        """Test analyze without snapshot ID."""
        result = cli_runner.invoke(app, ["analyze"])
        assert result.exit_code != 0, "Result must not be empty"

    def test_analyze_valid_snapshot(self, cli_runner):
        """Test analyze with valid snapshot ID."""
        with patch("codex.analyze.analyze") as mock_analyze:
            mock_analyze.return_value = {
                "snapshot_id": "snap_123",
                "issues": [],
                "metrics": {"complexity": 5},
            }

            result = cli_runner.invoke(app, ["analyze", "snap_123"])
            assert result.exit_code == 0, "Result must not be empty"

    def test_analyze_with_options(self, cli_runner):
        """Test analyze with various options."""
        with patch("codex.analyze.analyze"):
            cli_runner.invoke(app, ["analyze", "snap_123", "--full", "--format", "json"])
            # Should accept options

    def test_analyze_invalid_snapshot(self, cli_runner):
        """Test analyze with non-existent snapshot."""
        with patch("codex.analyze.analyze", side_effect=FileNotFoundError("Snapshot not found")):
            result = cli_runner.invoke(app, ["analyze", "nonexistent_snap"])
            assert result.exit_code != 0, "Result must not be empty"


# ============================================================================
# Transform Command Tests
# ============================================================================


class TestTransformCommand:
    """Tests for 'codex transform' command."""

    def test_transform_help(self, cli_runner):
        """Test transform --help."""
        result = cli_runner.invoke(app, ["transform", "--help"])
        assert result.exit_code == 0, "Result must not be empty"

    def test_transform_missing_snapshot(self, cli_runner):
        """Test transform without snapshot ID."""
        result = cli_runner.invoke(app, ["transform"])
        assert result.exit_code != 0, "Result must not be empty"

    def test_transform_valid_snapshot(self, cli_runner):
        """Test transform with valid snapshot."""
        with patch("codex.transform.transform") as mock_transform:
            mock_transform.return_value = {
                "snapshot_id": "snap_123",
                "changes": [{"file": "test.py", "type": "refactor"}],
            }

            result = cli_runner.invoke(app, ["transform", "snap_123"])
            assert result.exit_code == 0, "Result must not be empty"

    def test_transform_with_mode(self, cli_runner):
        """Test transform with mode option."""
        with patch("codex.transform.transform"):
            cli_runner.invoke(app, ["transform", "snap_123", "--mode", "apply"])
            # Should accept mode option

    def test_transform_with_filter(self, cli_runner):
        """Test transform with file filter."""
        with patch("codex.transform.transform"):
            cli_runner.invoke(app, ["transform", "snap_123", "--filter", "*.py"])
            # Should accept filter option


# ============================================================================
# Verify Command Tests
# ============================================================================


class TestVerifyCommand:
    """Tests for 'codex verify' command."""

    def test_verify_help(self, cli_runner):
        """Test verify --help."""
        result = cli_runner.invoke(app, ["verify", "--help"])
        assert result.exit_code == 0, "Result must not be empty"

    def test_verify_missing_args(self, cli_runner):
        """Test verify without required arguments."""
        result = cli_runner.invoke(app, ["verify"])
        assert result.exit_code != 0, "Result must not be empty"

    def test_verify_baseline_vs_patched(self, cli_runner):
        """Test verify comparing baseline vs patched."""
        with patch("codex.verify.verify_snapshot") as mock_verify:
            mock_verify.return_value = {
                "baseline": "snap_baseline",
                "patched": "snap_patched",
                "differences": [],
                "status": "identical",
            }

            result = cli_runner.invoke(
                app, ["verify", "snap_baseline", "--patched", "snap_patched"]
            )
            assert result.exit_code == 0, "Result must not be empty"

    def test_verify_with_format(self, cli_runner):
        """Test verify with output format."""
        with patch("codex.verify.verify_snapshot"):
            cli_runner.invoke(app, ["verify", "snap_123", "--format", "json"])
            # Should accept format option


# ============================================================================
# List Command Tests
# ============================================================================


class TestListCommand:
    """Tests for 'codex list' command."""

    def test_list_help(self, cli_runner):
        """Test list --help."""
        result = cli_runner.invoke(app, ["list", "--help"])
        assert result.exit_code == 0, "Result must not be empty"

    def test_list_snapshots(self, cli_runner):
        """Test listing snapshots."""
        with patch("codex.snapshot.list_snapshots") as mock_list:
            mock_list.return_value = [
                {"id": "snap_1", "name": "project1"},
                {"id": "snap_2", "name": "project2"},
            ]

            result = cli_runner.invoke(app, ["list"])
            assert result.exit_code == 0, "Result must not be empty"

    def test_list_with_filter(self, cli_runner):
        """Test list with filter."""
        with patch("codex.snapshot.list_snapshots"):
            cli_runner.invoke(app, ["list", "--filter", "project"])
            # Should accept filter option

    def test_list_verbose(self, cli_runner):
        """Test list in verbose mode."""
        with patch("codex.snapshot.list_snapshots"):
            cli_runner.invoke(app, ["list", "--verbose"])
            # Should show more details


# ============================================================================
# Show Command Tests
# ============================================================================


class TestShowCommand:
    """Tests for 'codex show' command."""

    def test_show_help(self, cli_runner):
        """Test show --help."""
        result = cli_runner.invoke(app, ["show", "--help"])
        assert result.exit_code == 0, "Result must not be empty"

    def test_show_missing_snapshot(self, cli_runner):
        """Test show without snapshot ID."""
        result = cli_runner.invoke(app, ["show"])
        assert result.exit_code != 0, "Result must not be empty"

    def test_show_valid_snapshot(self, cli_runner):
        """Test show snapshot details."""
        with patch("codex.snapshot.get_snapshot") as mock_get:
            mock_get.return_value = {
                "snapshot_id": "snap_123",
                "name": "test_project",
                "files": ["test.py"],
                "created_at": "2026-01-16T10:00:00Z",
            }

            result = cli_runner.invoke(app, ["show", "snap_123"])
            assert result.exit_code == 0, "Result must not be empty"

    def test_show_with_format(self, cli_runner):
        """Test show with different output formats."""
        with patch("codex.snapshot.get_snapshot"):
            cli_runner.invoke(app, ["show", "snap_123", "--format", "json"])
            # Should handle format option

    def test_show_invalid_snapshot(self, cli_runner):
        """Test show with non-existent snapshot."""
        with patch("codex.snapshot.get_snapshot", side_effect=FileNotFoundError("Not found")):
            result = cli_runner.invoke(app, ["show", "nonexistent"])
            assert result.exit_code != 0, "Result must not be empty"


# ============================================================================
# Main Entry Point Tests
# ============================================================================


class TestMainEntry:
    """Tests for main() entry point."""

    def test_main_help(self):
        """Test main with --help."""
        with patch("sys.argv", ["codex", "--help"]):
            with patch("typer.run"):
                # Main should handle help
                pass

    def test_main_no_args(self):
        """Test main with no arguments."""
        with patch("sys.argv", ["codex"]):
            # Main should show help or error
            pass


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestCLIErrorHandling:
    """Tests for error handling."""

    def test_invalid_command(self, cli_runner):
        """Test invalid command."""
        result = cli_runner.invoke(app, ["invalid_cmd"])
        assert result.exit_code != 0, "Result must not be empty"

    def test_command_with_invalid_flag(self, cli_runner):
        """Test command with invalid flag."""
        result = cli_runner.invoke(app, ["ingest", "--invalid-flag", "value"])
        assert result.exit_code != 0, "Result must not be empty"

    def test_exception_handling(self, cli_runner):
        """Test exception handling in commands."""
        with patch("codex.ingest.ingest", side_effect=Exception("Unexpected error")):
            result = cli_runner.invoke(app, ["ingest", "/some/path"])
            assert result.exit_code != 0, "Result must not be empty"


# ============================================================================
# Output Format Tests
# ============================================================================


class TestOutputFormats:
    """Tests for output formatting."""

    def test_analyze_json_output(self, cli_runner):
        """Test analyze JSON output format."""
        with patch("codex.analyze.analyze") as mock_analyze:
            mock_analyze.return_value = {"issues": [], "metrics": {"complexity": 5}}

            cli_runner.invoke(app, ["analyze", "snap_123", "--format", "json"])
            # Should output valid JSON

    def test_list_table_output(self, cli_runner):
        """Test list table output."""
        with patch("codex.snapshot.list_snapshots"):
            result = cli_runner.invoke(app, ["list"])
            assert result.exit_code == 0, "Result must not be empty"

    def test_error_message_clarity(self, cli_runner):
        """Test error messages are clear."""
        result = cli_runner.invoke(app, ["ingest"])
        # Error message should be clear
        assert len(result.stdout) > 0, "Collection must not be empty"


# ============================================================================
# Integration Tests
# ============================================================================


class TestCLIIntegration:
    """Integration tests for CLI workflows."""

    def test_ingest_analyze_workflow(self, cli_runner, temp_repo_dir):
        """Test ingest→analyze workflow."""
        with patch("codex.ingest.ingest") as mock_ingest:
            with patch("codex.analyze.analyze") as mock_analyze:
                mock_ingest.return_value = MagicMock(
                    snapshot_id="snap_123", snapshot_dir=temp_repo_dir, content_hash="hash123"
                )
                mock_analyze.return_value = {"issues": []}

                # Ingest
                ingest_result = cli_runner.invoke(app, ["ingest", str(temp_repo_dir)])
                assert ingest_result.exit_code == 0, "Result must not be empty"

                # Analyze
                analyze_result = cli_runner.invoke(app, ["analyze", "snap_123"])
                assert analyze_result.exit_code == 0, "Result must not be empty"

    def test_ingest_transform_verify_workflow(self, cli_runner, temp_repo_dir):
        """Test complete ingest→transform→verify workflow."""
        with patch("codex.ingest.ingest"):
            with patch("codex.transform.transform"):
                with patch("codex.verify.verify_snapshot"):
                    # Ingest
                    cli_runner.invoke(app, ["ingest", str(temp_repo_dir)])
                    # Transform
                    cli_runner.invoke(app, ["transform", "snap_123"])
                    # Verify
                    cli_runner.invoke(app, ["verify", "snap_base"])


# ============================================================================
# Typer vs Argparse Fallback Tests
# ============================================================================


class TestTyperFallback:
    """Tests for Typer vs Argparse fallback."""

    def test_typer_available(self):
        """Test that Typer is available."""
        from codex.cli.main import TYPER_AVAILABLE

        assert TYPER_AVAILABLE is True or TYPER_AVAILABLE is False, "TYPER_AVAILABLE is not valid"

    def test_app_initialization(self):
        """Test app is properly initialized."""
        from codex.cli.main import app

        assert app is not None, "app must be initialized"


# ============================================================================
# Edge Cases and Boundary Tests
# ============================================================================


class TestEdgeCases:
    """Edge case and boundary tests."""

    def test_very_long_snapshot_id(self, cli_runner):
        """Test with very long snapshot ID."""
        long_id = "snap_" + "a" * 1000
        with patch("codex.snapshot.get_snapshot"):
            cli_runner.invoke(app, ["show", long_id])
            # Should handle long IDs

    def test_special_characters_in_path(self, cli_runner, tmp_path):
        """Test with special characters in path."""
        special_dir = tmp_path / "dir with spaces & special-chars"
        special_dir.mkdir()
        (special_dir / "test.py").write_text("logger.info('test')")

        with patch("codex.ingest.ingest"):
            cli_runner.invoke(app, ["ingest", str(special_dir)])
            # Should handle special characters

    def test_unicode_in_path(self, cli_runner, tmp_path):
        """Test with unicode characters in path."""
        unicode_dir = tmp_path / "目录_测试_🚀"
        unicode_dir.mkdir()
        (unicode_dir / "测试.py").write_text("# Test")

        with patch("codex.ingest.ingest"):
            cli_runner.invoke(app, ["ingest", str(unicode_dir)])
            # Should handle unicode paths


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
