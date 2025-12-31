"""Unit tests for CoverageValidator with mocked coverage data."""
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.validator import CoverageValidator


class TestCoverageValidator:
    """Test suite for CoverageValidator class."""

    @pytest.fixture
    def tmp_workspace(self, tmp_path):
        """Create temporary workspace."""
        return tmp_path

    @pytest.fixture
    def validator(self, tmp_workspace):
        """Create CoverageValidator instance."""
        return CoverageValidator(workspace=tmp_workspace)

    def test_init(self, tmp_workspace):
        """Test CoverageValidator initialization."""
        validator = CoverageValidator(workspace=tmp_workspace)
        assert validator.workspace == tmp_workspace

    def test_parse_baseline_no_file(self, validator):
        """Test parsing baseline when file doesn't exist."""
        result = validator._parse_baseline("nonexistent.txt")
        assert result["total"] == 0.0

    def test_parse_baseline_valid_file(self, validator, tmp_workspace):
        """Test parsing valid baseline coverage file."""
        baseline_file = tmp_workspace / "baseline.txt"
        baseline_file.write_text("TOTAL    1234    567    78%\n")

        result = validator._parse_baseline("baseline.txt")
        assert result["total"] == 78.0

    def test_compute_delta(self, validator):
        """Test coverage delta computation."""
        baseline = {"total": 75.0}
        current = {"total": 82.5}

        delta = validator._compute_delta(baseline, current)
        assert delta == 7.5

    def test_identify_gaps_above_threshold(self, validator):
        """Test gap identification when above threshold."""
        current = {"total": 90.0, "modules": {}}
        threshold = 85.0

        gaps = validator._identify_gaps(current, threshold)
        assert len(gaps) == 0

    def test_identify_gaps_below_threshold(self, validator):
        """Test gap identification when below threshold."""
        current = {"total": 80.0, "modules": {}}
        threshold = 85.0

        gaps = validator._identify_gaps(current, threshold)
        assert len(gaps) > 0
        assert "80.00%" in gaps[0]
        assert "85" in gaps[0]  # Matches both "85%" and "85.0%"

    def test_identify_gaps_module_specific(self, validator):
        """Test gap identification for specific modules."""
        current = {
            "total": 90.0,
            "modules": {"module_a.py": 95.0, "module_b.py": 70.0},
        }
        threshold = 85.0

        gaps = validator._identify_gaps(current, threshold)
        assert any("module_b.py" in gap for gap in gaps)
        assert not any("module_a.py" in gap for gap in gaps)

    @patch("subprocess.run")
    def test_run_coverage_success(self, mock_run, validator, tmp_workspace):
        """Test running coverage analysis successfully."""
        # Create mock coverage.json
        coverage_data = {
            "totals": {"percent_covered": 85.5},
            "files": {"src/module.py": {"summary": {"percent_covered": 85.5}}},
        }
        coverage_file = tmp_workspace / "coverage.json"
        with open(coverage_file, "w") as f:
            json.dump(coverage_data, f)

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        result = validator._run_coverage([])
        assert result["total"] == 85.5

    @patch("subprocess.run")
    def test_run_coverage_no_json(self, mock_run, validator, tmp_workspace):
        """Test running coverage when JSON not generated."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "TOTAL    100    20    80%\n"
        mock_run.return_value = mock_result

        result = validator._run_coverage([])
        # Should parse from stdout
        assert result["total"] == 80.0

    @patch("subprocess.run")
    def test_run_coverage_timeout(self, mock_run, validator):
        """Test coverage analysis timeout."""
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired(cmd=["pytest"], timeout=300)

        result = validator._run_coverage([])
        assert result["total"] == 0.0

    def test_validate_meets_threshold(self, validator, tmp_workspace):
        """Test validation when coverage meets threshold."""
        # Create baseline
        baseline_file = tmp_workspace / "baseline.txt"
        baseline_file.write_text("TOTAL    100    25    75%\n")

        with patch.object(validator, "_run_coverage") as mock_run:
            mock_run.return_value = {"total": 90.0, "modules": {}}

            task = {"baseline": "baseline.txt", "threshold": 85}
            result = validator.validate(task)

            assert result["status"] == "success"
            assert result["meets_threshold"] is True
            assert result["current_coverage"] == 90.0
            assert result["baseline_coverage"] == 75.0
            assert result["delta"] == 15.0

    def test_validate_below_threshold(self, validator, tmp_workspace):
        """Test validation when coverage below threshold."""
        baseline_file = tmp_workspace / "baseline.txt"
        baseline_file.write_text("TOTAL    100    25    75%\n")

        with patch.object(validator, "_run_coverage") as mock_run:
            mock_run.return_value = {"total": 80.0, "modules": {}}

            task = {"baseline": "baseline.txt", "threshold": 85}
            result = validator.validate(task)

            assert result["status"] == "below_threshold"
            assert result["meets_threshold"] is False
            assert len(result["gaps"]) > 0

    def test_validate_error_handling(self, validator):
        """Test validation error handling."""
        with patch.object(validator, "_run_coverage") as mock_run:
            mock_run.side_effect = Exception("Test error")

            task = {"threshold": 85}
            result = validator.validate(task)

            assert result["status"] == "error"
            assert "error" in result

    @patch("subprocess.run")
    def test_generate_coverage_report(self, mock_run, validator, tmp_workspace):
        """Test coverage report generation."""
        mock_run.return_value = Mock(returncode=0)

        report_path = validator.generate_coverage_report()

        assert "coverage" in str(report_path)
        assert report_path.name == "index.html"
        mock_run.assert_called_once()
