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
        assert count == 2
        assert len(low_list) == 2
        assert low_list[0]["id"] == "cap1"
        assert low_list[1]["id"] == "cap2"
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
        assert missing == []

        # Test with missing override
        overrides = {"cap1": ["pattern1"], "cap3": ["pattern3"]}
        missing = check_missing_detectors(temp_path, overrides)
        assert missing == ["cap3"]
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

    assert "# Capability Audit — Gate Summary" in summary
    assert "Low threshold: 0.7" in summary
    assert "Medium threshold: 0.85" in summary
    assert "Low Maturity (2)" in summary
    assert "cap1" in summary
    assert "cap2" in summary
    assert "Missing Detectors (overrides) (2)" in summary
    assert "cap3" in summary
    assert "cap4" in summary


def test_emit_summary_no_gaps():
    """Test emit_summary with no gaps."""
    from scripts.space_traversal.validators import emit_summary

    summary = emit_summary([], [], {"low": 0.7, "medium": 0.85})

    assert "Low Maturity (0)" in summary
    assert "_None_" in summary
    assert "Missing Detectors (overrides) (0)" in summary
