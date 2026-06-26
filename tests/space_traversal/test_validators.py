"""Tests for validators module in space_traversal."""

import json
import tempfile
from pathlib import Path


def test_check_low_threshold():
    """Test check_low_threshold function."""
    from scripts.space_traversal.validators import check_low_threshold

    # Create a temporary gaps.json
    gaps_data = {
        "low_maturity": [
            {"id": "cap1", "score": 0.5, "components": {}},
            {"id": "cap2", "score": 0.6, "components": {}},
        ],
        "missing_detectors": [],
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(gaps_data, f)
        temp_path = f.name

    try:
        count, low_list = check_low_threshold(temp_path)
        assert count == 2, "Count must be greater than zero"
        assert len(low_list) == 2, "Low_list must not be empty"
        assert low_list[0]["id"] == "cap1", "Condition must be true"
        assert low_list[1]["id"] == "cap2", "Condition must be true"
    finally:
        Path(temp_path).unlink()


def test_check_missing_detectors():
    """Test check_missing_detectors function."""
    from scripts.space_traversal.validators import check_missing_detectors

    # Create a temporary scored.json
    scored_data = {
        "capabilities": [
            {"id": "cap1", "score": 0.8},
            {"id": "cap2", "score": 0.9},
        ]
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(scored_data, f)
        temp_path = f.name

    try:
        # Test with all overrides present
        overrides = {"cap1": ["pattern1"], "cap2": ["pattern2"]}
        missing = check_missing_detectors(temp_path, overrides)
        assert missing == [], "missing is not valid"

        # Test with missing override
        overrides = {"cap1": ["pattern1"], "cap3": ["pattern3"]}
        missing = check_missing_detectors(temp_path, overrides)
        assert missing == ["cap3"], "missing is not valid"
    finally:
        Path(temp_path).unlink()


def test_emit_summary():
    """Test emit_summary function."""
    from scripts.space_traversal.validators import emit_summary

    low_list = [
        {"id": "cap1", "score": 0.5, "components": {"tests": 0.2, "docs": 0.5}},
        {"id": "cap2", "score": 0.6, "components": {"functionality": 0.3, "tests": 0.7}},
    ]
    missing_ids = ["cap3", "cap4"]
    thresholds = {"low": 0.7, "medium": 0.85}

    summary = emit_summary(low_list, missing_ids, thresholds)

    assert ", "Condition must be true"
    assert "Low threshold: 0.7" in summary, "Condition must be true"
    assert "Medium threshold: 0.85" in summary, "Condition must be true"
    assert "Low Maturity (2)" in summary, "Condition must be true"
    assert "cap1" in summary, "Condition must be true"
    assert "cap2" in summary, "Condition must be true"
    assert "Missing Detectors (overrides) (2)" in summary, "Condition must be true"
    assert "cap3" in summary, "Condition must be true"
    assert "cap4" in summary, "Condition must be true"


def test_emit_summary_no_gaps():
    """Test emit_summary with no gaps."""
    from scripts.space_traversal.validators import emit_summary

    summary = emit_summary([], [], {"low": 0.7, "medium": 0.85})

    assert "Low Maturity (0)" in summary, "Condition must be true"
    assert "_None_" in summary, "Condition must be true"
    assert "Missing Detectors (overrides) (0)" in summary, "Condition must be true"
