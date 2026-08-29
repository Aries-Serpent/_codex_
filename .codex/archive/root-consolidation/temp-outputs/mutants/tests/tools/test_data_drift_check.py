"""Test suite for data drift detection."""

from __future__ import annotations

import json

import pytest

from tools.data_drift_check import drift_score, main


class TestDataDriftCheck:
    """Test data drift detection functionality."""

    def test_drift_score_no_drift(self):
        """Test drift detection with identical distributions."""
        ref = {"hist": {"label": {"A": 0.5, "B": 0.5}}}
        cur = {"hist": {"label": {"A": 0.5, "B": 0.5}}}
        score = drift_score(ref, cur)
        assert score == 0.0, "score is not valid"

    def test_drift_score_with_drift(self):
        """Test drift detection with significant drift."""
        ref = {"hist": {"label": {"A": 0.5, "B": 0.5}}}
        cur = {"hist": {"label": {"A": 0.8, "B": 0.2}}}  # Significant shift
        score = drift_score(ref, cur)
        assert score == 0.3, "score is not valid"

    def test_drift_score_new_labels(self):
        """Test drift detection when new labels appear."""
        ref = {"hist": {"label": {"A": 0.5, "B": 0.5}}}
        cur = {"hist": {"label": {"A": 0.4, "B": 0.4, "C": 0.2}}}
        score = drift_score(ref, cur)
        assert score == 0.2, "score is not valid"

    def test_drift_score_missing_labels(self):
        """Test drift detection when labels disappear."""
        ref = {"hist": {"label": {"A": 0.5, "B": 0.3, "C": 0.2}}}
        cur = {"hist": {"label": {"A": 0.7, "B": 0.3}}}
        score = drift_score(ref, cur)
        assert score == 0.2, "score is not valid"

    def test_drift_score_empty_hist(self):
        """Test drift detection with empty histogram."""
        ref = {"hist": {"label": {}}}
        cur = {"hist": {"label": {}}}
        score = drift_score(ref, cur)
        assert score == 0.0, "score is not valid"

    def test_drift_score_missing_hist(self):
        """Test drift detection with missing histogram."""
        ref = {}
        cur = {}
        score = drift_score(ref, cur)
        assert score == 0.0, "score is not valid"

    def test_main_no_drift(self, tmp_path):
        """Test main function with no drift."""
        ref_file = tmp_path / "ref.json"
        cur_file = tmp_path / "cur.json"

        ref_data = {"hist": {"label": {"A": 0.5, "B": 0.5}}}
        cur_data = {"hist": {"label": {"A": 0.5, "B": 0.5}}}

        ref_file.write_text(json.dumps(ref_data), encoding="utf-8")
        cur_file.write_text(json.dumps(cur_data), encoding="utf-8")

        result = main(["--ref", str(ref_file), "--cur", str(cur_file), "--threshold", "0.2"])
        assert result == 0, "Result must not be empty"

    def test_main_with_drift_exceeds_threshold(self, tmp_path):
        """Test main function when drift exceeds threshold."""
        ref_file = tmp_path / "ref.json"
        cur_file = tmp_path / "cur.json"

        ref_data = {"hist": {"label": {"A": 0.5, "B": 0.5}}}
        cur_data = {"hist": {"label": {"A": 0.9, "B": 0.1}}}

        ref_file.write_text(json.dumps(ref_data), encoding="utf-8")
        cur_file.write_text(json.dumps(cur_data), encoding="utf-8")

        result = main(["--ref", str(ref_file), "--cur", str(cur_file), "--threshold", "0.2"])
        assert result == 1, "Result must not be empty"

    def test_main_custom_threshold(self, tmp_path):
        """Test main function with custom threshold."""
        ref_file = tmp_path / "ref.json"
        cur_file = tmp_path / "cur.json"

        ref_data = {"hist": {"label": {"A": 0.6, "B": 0.4}}}
        cur_data = {"hist": {"label": {"A": 0.7, "B": 0.3}}}

        ref_file.write_text(json.dumps(ref_data), encoding="utf-8")
        cur_file.write_text(json.dumps(cur_data), encoding="utf-8")

        # Drift is 0.1, threshold 0.15 -> should pass
        result = main(["--ref", str(ref_file), "--cur", str(cur_file), "--threshold", "0.15"])
        assert result == 0, "Result must not be empty"

        # Drift is 0.1, threshold 0.05 -> should fail
        result = main(["--ref", str(ref_file), "--cur", str(cur_file), "--threshold", "0.05"])
        assert result == 1, "Result must not be empty"

    def test_drift_score_extreme_values(self):
        """Test drift detection with extreme distribution changes."""
        ref = {"hist": {"label": {"A": 1.0}}}
        cur = {"hist": {"label": {"B": 1.0}}}
        score = drift_score(ref, cur)
        assert score == 1.0, "score is not valid"

    def test_drift_score_many_labels(self):
        """Test drift detection with many labels."""
        ref = {"hist": {"label": {f"L{i}": 0.1 for i in range(10)}}}
        cur = {"hist": {"label": {f"L{i}": 0.15 if i < 5 else 0.05 for i in range(10)}}}
        score = drift_score(ref, cur)
        assert score == 0.05, "score is not valid"

    def test_main_nonexistent_file(self, tmp_path):
        """Test main function with non-existent file."""
        with pytest.raises(FileNotFoundError):
            main(
                [
                    "--ref",
                    str(tmp_path / "nonexistent.json"),
                    "--cur",
                    str(tmp_path / "also_nonexistent.json"),
                ]
            )

    def test_main_invalid_json(self, tmp_path):
        """Test main function with invalid JSON."""
        ref_file = tmp_path / "ref.json"
        cur_file = tmp_path / "cur.json"

        ref_file.write_text("{invalid json", encoding="utf-8")
        cur_file.write_text('{"hist": {"label": {}}}', encoding="utf-8")

        with pytest.raises(json.JSONDecodeError):
            main(["--ref", str(ref_file), "--cur", str(cur_file)])
