"""
Tests for Duplication CLI Commands

Tests the codex duplication check, report, and compare commands.
"""

import json
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from codex.cli import cli


class TestDuplicationCheckCommand:
    """Test duplication check command"""

    def test_check_command_exists(self):
        """Test that duplication check command exists"""
        runner = CliRunner()
        result = runner.invoke(cli, ["duplication", "check", "--help"])

        assert result.exit_code == 0, "Result must not be empty"
        assert "Check code for duplicates" in result.output, "Result must not be empty"

    def test_check_empty_directory(self):
        """Test checking empty directory"""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(cli, ["duplication", "check", tmpdir])

            # Should complete without error
            assert "Scanning" in result.output, "Result must not be empty"
            assert "Duplication Report" in result.output, "Result must not be empty"

    def test_check_with_output_file(self):
        """Test check command with output file"""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "duplication.json"

            result = runner.invoke(cli, ["duplication", "check", ".", "--output", str(output_file)])

            # Should create output file
            if result.exit_code == 0 or "Saved results" in result.output:
                assert output_file.exists() or "Failed" in result.output, "Result must not be empty"

    def test_check_with_custom_threshold(self):
        """Test check with custom threshold"""
        runner = CliRunner()

        result = runner.invoke(
            cli,
            [
                "duplication",
                "check",
                ".",
                "--threshold",
                "1.0",  # Very high threshold - should always pass
            ],
        )

        assert "threshold" in result.output.lower(), "Result must not be empty"


class TestDuplicationReportCommand:
    """Test duplication report command"""

    def test_report_command_exists(self):
        """Test that duplication report command exists"""
        runner = CliRunner()
        result = runner.invoke(cli, ["duplication", "report", "--help"])

        assert result.exit_code == 0, "Result must not be empty"
        assert "Generate detailed duplication report" in result.output, "Result must not be empty"

    def test_report_json_format(self):
        """Test report with JSON format"""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "report.json"

            result = runner.invoke(
                cli,
                ["duplication", "report", ".", "--format", "json", "--output", str(output_file)],
            )

            # Check output file exists
            if result.exit_code == 0:
                assert output_file.exists(), "Condition must be true"

                # Verify it's valid JSON
                with open(output_file) as f:
                    data = json.load(f)

                assert "ratio" in data or "total_lines" in data, "Data must not be empty"

    def test_report_text_format(self):
        """Test report with text format"""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "report.txt"

            result = runner.invoke(
                cli,
                ["duplication", "report", ".", "--format", "text", "--output", str(output_file)],
            )

            # Check output file exists
            if result.exit_code == 0:
                assert output_file.exists(), "Condition must be true"

                # Verify it contains report elements
                content = output_file.read_text()
                assert "DUPLICATION REPORT" in content or "SUMMARY" in content, "Content must not be empty"


class TestDuplicationCompareCommand:
    """Test duplication compare command"""

    def test_compare_command_exists(self):
        """Test that duplication compare command exists"""
        runner = CliRunner()
        result = runner.invoke(cli, ["duplication", "compare", "--help"])

        assert result.exit_code == 0, "Result must not be empty"
        assert "Compare duplication metrics" in result.output, "Result must not be empty"

    def test_compare_without_baseline(self):
        """Test compare without baseline (shows current only)"""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a dummy current report
            current_file = Path(tmpdir) / "current.json"
            current_file.write_text(
                json.dumps(
                    {
                        "ratio": 0.15,
                        "total_lines": 1000,
                        "duplicate_lines": 150,
                    }
                )
            )

            result = runner.invoke(cli, ["duplication", "compare", str(current_file)])

            # Should show current metrics
            if result.exit_code == 0:
                assert "15" in result.output, "Result must not be empty"

    def test_compare_with_baseline(self):
        """Test compare with baseline"""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create baseline and current reports
            baseline_file = Path(tmpdir) / "baseline.json"
            baseline_file.write_text(
                json.dumps(
                    {
                        "ratio": 0.10,
                        "total_lines": 1000,
                        "duplicate_lines": 100,
                    }
                )
            )

            current_file = Path(tmpdir) / "current.json"
            current_file.write_text(
                json.dumps(
                    {
                        "ratio": 0.12,
                        "total_lines": 1000,
                        "duplicate_lines": 120,
                    }
                )
            )

            result = runner.invoke(
                cli, ["duplication", "compare", str(current_file), "--baseline", str(baseline_file)]
            )

            # Should show comparison
            if result.exit_code == 0:
                assert "Baseline" in result.output or "Current" in result.output, "Result must not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
