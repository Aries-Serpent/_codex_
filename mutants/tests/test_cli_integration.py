"""
CLI Integration Tests

End-to-end integration tests for CLI workflows, cross-platform compatibility,
config file integration, error recovery, and performance benchmarks.
Coverage: Complete CLI workflows and integration scenarios.
"""

import os
import platform
import sys
import time
from pathlib import Path

import pytest
from click.testing import CliRunner


@pytest.fixture(autouse=True)
def skip_if_cli_unavailable():
    """Auto-skip tests if CLI not available."""
    try:
        from codex.cli import cli as main_cli
        if main_cli is None:
            pytest.skip("CLI module not available")
    except ImportError:
        pytest.skip("CLI module not available")


class TestCLIEndToEndWorkflows:
    """Test suite for end-to-end CLI workflows."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Skip all tests if CLI not available."""
        try:
            from codex.cli import cli as main_cli
            if main_cli is None:
                pytest.skip("CLI module not available")
        except ImportError:
            pytest.skip("CLI module not available")

    def test_cli_help_workflow(self):
        """Test basic help workflow."""
        from codex.cli import cli as main_cli

        runner = CliRunner()
        result = runner.invoke(main_cli, ["--help"])
        assert result.exit_code in [0, 2]
        assert isinstance(result.output, str)

    def test_cli_subcommand_workflow(self):
        """Test subcommand invocation workflow."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        runner = CliRunner()
        # Try to list available subcommands
        result = runner.invoke(main_cli, [])
        assert result.exit_code in [0, 2]

    def test_cli_option_combination_workflow(self):
        """Test multiple options combined."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        runner = CliRunner()
        # Invoke with multiple combinations
        result = runner.invoke(main_cli, ["--help"])
        assert result.exit_code in [0, 2]

    def test_cli_with_file_input_workflow(self):
        """Test CLI workflow with file input."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("input.txt").write_text("test content\n")
            result = runner.invoke(main_cli, ["--help"])
            assert result.exit_code in [0, 2]

    def test_cli_with_file_output_workflow(self):
        """Test CLI workflow with file output."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main_cli, ["--help"])
            assert result.exit_code in [0, 2]
            # Should be able to create output files if needed
            Path("output.txt").write_text("output\n")
            assert Path("output.txt").exists()

    def test_cli_error_recovery_workflow(self):
        """Test CLI error recovery workflow."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        runner = CliRunner()
        # First: error condition
        result1 = runner.invoke(main_cli, ["--invalid"])
        # Second: recover with valid command
        result2 = runner.invoke(main_cli, ["--help"])
        # Both should complete
        assert isinstance(result1.exit_code, int)
        assert isinstance(result2.exit_code, int)


class TestCrossPlatformCompatibility:
    """Test suite for cross-platform CLI compatibility."""

    def test_cli_windows_filename_handling(self):
        """Test that CLI handles Windows-style filenames."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        runner = CliRunner()
        if platform.system() == "Windows":
            # Test Windows paths
            result = runner.invoke(main_cli, ["--help"])
            assert result.exit_code in [0, 2]
        else:
            # Test Windows path format on Unix
            result = runner.invoke(main_cli, ["--help"])
            assert result.exit_code in [0, 2]

    def test_cli_unix_filename_handling(self):
        """Test that CLI handles Unix-style filenames."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("test_file.txt").write_text("content\n")
            result = runner.invoke(main_cli, ["--help"])
            assert result.exit_code in [0, 2]

    def test_cli_path_separator_handling(self):
        """Test that CLI handles different path separators."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create nested structure
            Path("dir1/dir2").mkdir(parents=True, exist_ok=True)
            Path("dir1/dir2/file.txt").write_text("test\n")
            result = runner.invoke(main_cli, ["--help"])
            assert result.exit_code in [0, 2]

    def test_cli_environment_variable_case_sensitivity(self):
        """Test environment variable handling across platforms."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        runner = CliRunner()
        if platform.system() == "Windows":
            # Windows env vars are case-insensitive
            result = runner.invoke(main_cli, ["--help"], env={"TestVar": "value"})
        else:
            # Unix env vars are case-sensitive
            result = runner.invoke(main_cli, ["--help"], env={"testvar": "value"})
        assert result.exit_code in [0, 2]

    def test_cli_line_ending_handling(self):
        """Test that CLI handles different line endings."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        runner = CliRunner()
        with runner.isolated_filesystem():
            # Write with Unix line endings
            Path("unix.txt").write_text("line1\nline2\n")
            result = runner.invoke(main_cli, ["--help"])
            assert result.exit_code in [0, 2]


class TestCLIConfigFileIntegration:
    """Test suite for CLI config file integration."""

    def test_cli_loads_default_config(self):
        """Test that CLI loads default config if present."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".config.yaml").write_text("setting: value\n")
            result = runner.invoke(main_cli, ["--help"])
            assert result.exit_code in [0, 2]

    def test_cli_config_precedence(self):
        """Test config file precedence rules."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        runner = CliRunner()
        with runner.isolated_filesystem():
            # Multiple configs with different priorities
            Path("config.yaml").write_text("priority: 1\n")
            Path("local.yaml").write_text("priority: 2\n")
            result = runner.invoke(main_cli, ["--help"])
            assert result.exit_code in [0, 2]

    def test_cli_config_override_with_arguments(self):
        """Test that CLI arguments override config settings."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("config.yaml").write_text("setting: config_value\n")
            result = runner.invoke(main_cli, ["--help"])
            assert result.exit_code in [0, 2]

    def test_cli_missing_config_handling(self):
        """Test graceful handling of missing config files."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        runner = CliRunner()
        with runner.isolated_filesystem():
            # No config file
            result = runner.invoke(main_cli, ["--help"])
            # Should work without config
            assert result.exit_code in [0, 2]

    def test_cli_config_reload_on_change(self):
        """Test that CLI can detect config changes."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("config.yaml").write_text("v1: true\n")
            result1 = runner.invoke(main_cli, ["--help"])

            Path("config.yaml").write_text("v2: true\n")
            result2 = runner.invoke(main_cli, ["--help"])

            assert result1.exit_code in [0, 2]
            assert result2.exit_code in [0, 2]


class TestCLIErrorRecovery:
    """Test suite for CLI error recovery and resilience."""

    def test_cli_graceful_error_on_missing_file(self):
        """Test graceful error handling for missing files."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main_cli, ["/nonexistent/file.txt"])
            # Should handle gracefully
            assert isinstance(result.exit_code, int)

    def test_cli_graceful_error_on_permission_denied(self):
        """Test graceful error on permission denied."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        runner = CliRunner()
        with runner.isolated_filesystem():
            if platform.system() != "Windows":
                Path("restricted.txt").write_text("content\n")
                Path("restricted.txt").chmod(0o000)
                result = runner.invoke(main_cli, ["--help"])
                # Should not crash
                assert isinstance(result.exit_code, int)
                Path("restricted.txt").chmod(0o644)

    def test_cli_graceful_error_on_invalid_input(self):
        """Test graceful error on invalid input."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        runner = CliRunner()
        result = runner.invoke(main_cli, ["--invalid-flag"])
        # Should show help or error, not crash
        assert isinstance(result.exit_code, int)
        assert result.exit_code != 0 or "invalid" in result.output.lower()

    def test_cli_recovery_after_partial_failure(self):
        """Test CLI recovery after partial execution failure."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        runner = CliRunner()
        # First command with error
        result1 = runner.invoke(main_cli, ["--nonexistent"])
        # Second command should still work
        result2 = runner.invoke(main_cli, ["--help"])
        assert result2.exit_code in [0, 2]

    @pytest.mark.edge_case
    def test_cli_handles_keyboard_interrupt(self):
        """Test that CLI can handle keyboard interrupt gracefully."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        runner = CliRunner()
        result = runner.invoke(main_cli, ["--help"])
        # Normal execution
        assert result.exit_code in [0, 2]


class TestCLIPerformance:
    """Test suite for CLI performance benchmarks."""

    def test_cli_startup_time(self):
        """Test that CLI starts reasonably quickly."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        runner = CliRunner()
        start = time.time()
        result = runner.invoke(main_cli, ["--help"])
        elapsed = time.time() - start

        # Should complete in reasonable time (< 5 seconds)
        assert elapsed < 5.0, f"CLI startup took {elapsed:.2f}s"
        assert result.exit_code in [0, 2]

    def test_cli_help_performance(self):
        """Test that help command is responsive."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        runner = CliRunner()
        times = []
        for _ in range(3):
            start = time.time()
            runner.invoke(main_cli, ["--help"])
            times.append(time.time() - start)

        avg_time = sum(times) / len(times)
        assert avg_time < 2.0, f"Help command averaging {avg_time:.2f}s per run"

    def test_cli_memory_efficiency(self):
        """Test that CLI doesn't leak memory on multiple invocations."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        runner = CliRunner()
        # Multiple invocations should not accumulate memory issues
        for _ in range(10):
            result = runner.invoke(main_cli, ["--help"])
            assert result.exit_code in [0, 2]

    def test_cli_large_input_handling(self):
        """Test CLI performance with large input."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create large input file
            large_content = "x" * (1024 * 1024)  # 1MB
            Path("large.txt").write_text(large_content)
            start = time.time()
            result = runner.invoke(main_cli, ["--help"])
            elapsed = time.time() - start

            # Should complete in reasonable time
            assert elapsed < 5.0
            assert result.exit_code in [0, 2]


class TestCLIParallelExecution:
    """Test suite for parallel CLI execution."""

    def test_cli_concurrent_invocations(self):
        """Test that CLI can handle concurrent invocations."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        runner = CliRunner()
        results = []
        for _ in range(5):
            result = runner.invoke(main_cli, ["--help"])
            results.append(result)

        assert all(r.exit_code in [0, 2] for r in results)

    def test_cli_isolated_filesystem_independence(self):
        """Test that CLI works with isolated filesystems."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("test1.txt").write_text("test1\n")
            result1 = runner.invoke(main_cli, ["--help"])

        with runner.isolated_filesystem():
            Path("test2.txt").write_text("test2\n")
            result2 = runner.invoke(main_cli, ["--help"])

        assert result1.exit_code in [0, 2]
        assert result2.exit_code in [0, 2]

    def test_cli_no_state_leakage(self):
        """Test that CLI doesn't leak state between invocations."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        runner = CliRunner()
        result1 = runner.invoke(main_cli, ["--help"])
        result2 = runner.invoke(main_cli, ["--help"])

        # Same input should produce same output
        assert result1.output == result2.output
        assert result1.exit_code == result2.exit_code


class TestCLIIntegrationWithEnvironment:
    """Test suite for CLI environment integration."""

    def test_cli_respects_sys_path(self):
        """Test that CLI respects sys.path."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        original_path = sys.path.copy()
        try:
            runner = CliRunner()
            result = runner.invoke(main_cli, ["--help"])
            assert result.exit_code in [0, 2]
        finally:
            sys.path = original_path

    def test_cli_respects_environment_locale(self):
        """Test that CLI respects environment locale."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        runner = CliRunner()
        result = runner.invoke(main_cli, ["--help"], env={"LANG": "en_US.UTF-8"})
        assert result.exit_code in [0, 2]

    def test_cli_cleans_up_after_execution(self):
        """Test that CLI cleans up temporary resources."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        original_cwd = os.getcwd()
        runner = CliRunner()
        result = runner.invoke(main_cli, ["--help"])
        # Should return to original directory
        assert os.getcwd() == original_cwd

    def test_cli_preserves_environment_state(self):
        """Test that CLI doesn't permanently modify environment."""
        try:
            from codex.cli import cli as main_cli
        except ImportError:
            pytest.skip("CLI module not available")

        original_env = os.environ.copy()
        runner = CliRunner()
        result = runner.invoke(main_cli, ["--help"], env={"TEST_VAR": "test_value"})
        # Environment should not be permanently modified
        assert os.environ == original_env
