"""Tests for trend comparison (v1.5.1)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_compare_runs_basic(tmp_path: Path):
    """Test basic comparison of two runs."""
    from scripts.space_traversal.trend_compare import compare_runs

    # Create old and new scored files
    old_data = {
        "capabilities": [
            {"id": "cap1", "score": 0.8, "components": {"functionality": 1.0, "tests": 0.6}},
            {"id": "cap2", "score": 0.75, "components": {"functionality": 0.9, "tests": 0.5}},
        ]
    }
    new_data = {
        "capabilities": [
            {"id": "cap1", "score": 0.85, "components": {"functionality": 1.0, "tests": 0.7}},
            {"id": "cap2", "score": 0.68, "components": {"functionality": 0.8, "tests": 0.5}},
        ]
    }

    old_path = tmp_path / "old.json"
    new_path = tmp_path / "new.json"
    old_path.write_text(json.dumps(old_data))
    new_path.write_text(json.dumps(new_data))

    results = compare_runs(old_path, new_path)

    assert len(results) == 2, "Results must not be empty"

    # cap1 improved
    cap1 = next(r for r in results if r.capability_id == "cap1")
    assert cap1.delta == pytest.approx(0.05), "delta is not valid"
    assert not cap1.is_regression, "Condition must be true"

    # cap2 regressed (delta = -0.07, which is < -0.05, so high severity)
    cap2 = next(r for r in results if r.capability_id == "cap2")
    assert cap2.delta == pytest.approx(-0.07), "delta is not valid"
    assert cap2.is_regression, "Condition must be true"
    assert cap2.regression_severity == "high", "regression_severity is not valid"


def test_compare_runs_regression_severity(tmp_path: Path):
    """Test regression severity classification."""
    from scripts.space_traversal.trend_compare import compare_runs

    old_data = {
        "capabilities": [
            {"id": "high_reg", "score": 0.9, "components": {}},
            {"id": "med_reg", "score": 0.9, "components": {}},
            {"id": "low_reg", "score": 0.9, "components": {}},
        ]
    }
    new_data = {
        "capabilities": [
            {"id": "high_reg", "score": 0.84, "components": {}},  # -0.06
            {"id": "med_reg", "score": 0.87, "components": {}},  # -0.03
            {"id": "low_reg", "score": 0.89, "components": {}},  # -0.01 (below threshold)
        ]
    }

    old_path = tmp_path / "old.json"
    new_path = tmp_path / "new.json"
    old_path.write_text(json.dumps(old_data))
    new_path.write_text(json.dumps(new_data))

    results = compare_runs(old_path, new_path, threshold=0.02)

    high_reg = next(r for r in results if r.capability_id == "high_reg")
    assert high_reg.regression_severity == "high", "regression_severity is not valid"

    med_reg = next(r for r in results if r.capability_id == "med_reg")
    assert med_reg.regression_severity == "medium", "regression_severity is not valid"

    low_reg = next(r for r in results if r.capability_id == "low_reg")
    assert not low_reg.is_regression, "Condition must be true"


def test_compare_runs_component_deltas(tmp_path: Path):
    """Test component delta calculation."""
    from scripts.space_traversal.trend_compare import compare_runs

    old_data = {
        "capabilities": [
            {
                "id": "cap1",
                "score": 0.8,
                "components": {
                    "functionality": 1.0,
                    "consistency": 0.8,
                    "tests": 0.7,
                    "safeguards": 0.6,
                    "documentation": 0.9,
                },
            }
        ]
    }
    new_data = {
        "capabilities": [
            {
                "id": "cap1",
                "score": 0.85,
                "components": {
                    "functionality": 1.0,
                    "consistency": 0.9,
                    "tests": 0.8,
                    "safeguards": 0.5,
                    "documentation": 0.9,
                },
            }
        ]
    }

    old_path = tmp_path / "old.json"
    new_path = tmp_path / "new.json"
    old_path.write_text(json.dumps(old_data))
    new_path.write_text(json.dumps(new_data))

    results = compare_runs(old_path, new_path)

    cap1 = results[0]
    assert cap1.component_deltas["functionality"] == pytest.approx(0.0), "Condition must be true"
    assert cap1.component_deltas["consistency"] == pytest.approx(0.1), "Condition must be true"
    assert cap1.component_deltas["tests"] == pytest.approx(0.1), "Condition must be true"
    assert cap1.component_deltas["safeguards"] == pytest.approx(-0.1), "Condition must be true"
    assert cap1.component_deltas["documentation"] == pytest.approx(0.0), "Condition must be true"


def test_compare_runs_new_capability(tmp_path: Path):
    """Test comparison with new capability in newer run."""
    from scripts.space_traversal.trend_compare import compare_runs

    old_data = {"capabilities": [{"id": "cap1", "score": 0.8, "components": {}}]}
    new_data = {
        "capabilities": [
            {"id": "cap1", "score": 0.85, "components": {}},
            {"id": "cap2", "score": 0.7, "components": {}},  # New capability
        ]
    }

    old_path = tmp_path / "old.json"
    new_path = tmp_path / "new.json"
    old_path.write_text(json.dumps(old_data))
    new_path.write_text(json.dumps(new_data))

    results = compare_runs(old_path, new_path)

    assert len(results) == 2, "Results must not be empty"

    cap2 = next(r for r in results if r.capability_id == "cap2")
    assert cap2.old_score == 0, "old_score is not valid"
    assert cap2.new_score == 0.7, "new_score is not valid"


def test_generate_comparison_report(tmp_path: Path):
    """Test comparison report generation."""
    from scripts.space_traversal.trend_compare import (
        ComparisonResult,
        generate_comparison_report,
    )

    results = [
        ComparisonResult(
            capability_id="improving",
            old_score=0.7,
            new_score=0.85,
            delta=0.15,
            old_components={},
            new_components={},
            component_deltas={
                "functionality": 0.1,
                "consistency": 0.05,
                "tests": 0.0,
                "safeguards": 0.0,
                "documentation": 0.0,
            },
            is_regression=False,
            regression_severity=None,
        ),
        ComparisonResult(
            capability_id="regressing",
            old_score=0.9,
            new_score=0.8,
            delta=-0.1,
            old_components={},
            new_components={},
            component_deltas={
                "functionality": 0.0,
                "consistency": -0.05,
                "tests": -0.05,
                "safeguards": 0.0,
                "documentation": 0.0,
            },
            is_regression=True,
            regression_severity="high",
        ),
    ]

    output_path = tmp_path / "comparison.md"
    generate_comparison_report(results, output_path)

    assert output_path.exists(), "Condition must be true"
    content = output_path.read_text()

    assert "Audit Comparison Report" in content, "Content must not be empty"
    assert "improving" in content, "Content must not be empty"
    assert "regressing" in content, "Content must not be empty"
    assert "Regressions" in content, "Content must not be empty"
    assert "Improvements" in content, "Content must not be empty"


def test_get_regression_summary(tmp_path: Path):
    """Test regression summary generation."""
    from scripts.space_traversal.trend_compare import (
        ComparisonResult,
        get_regression_summary,
    )

    results = [
        ComparisonResult(
            capability_id="high_reg",
            old_score=0.9,
            new_score=0.8,
            delta=-0.1,
            old_components={},
            new_components={},
            component_deltas={"tests": -0.15, "functionality": 0.0},
            is_regression=True,
            regression_severity="high",
        ),
        ComparisonResult(
            capability_id="med_reg",
            old_score=0.8,
            new_score=0.75,
            delta=-0.05,
            old_components={},
            new_components={},
            component_deltas={"safeguards": -0.1, "functionality": 0.0},
            is_regression=True,
            regression_severity="medium",
        ),
        ComparisonResult(
            capability_id="improving",
            old_score=0.7,
            new_score=0.8,
            delta=0.1,
            old_components={},
            new_components={},
            component_deltas={},
            is_regression=False,
            regression_severity=None,
        ),
    ]

    summary = get_regression_summary(results)

    assert summary["total_regressions"] == 2, "Condition must be true"
    assert summary["high_severity_count"] == 1, "Count must be greater than zero"
    assert summary["medium_severity_count"] == 1, "Count must be greater than zero"
    assert "high_reg" in summary["high_severity_ids"], "Condition must be true"


def test_comparison_result_dataclass():
    """Test ComparisonResult dataclass."""
    from scripts.space_traversal.trend_compare import ComparisonResult

    result = ComparisonResult(
        capability_id="test_cap",
        old_score=0.8,
        new_score=0.75,
        delta=-0.05,
        old_components={"func": 0.9},
        new_components={"func": 0.85},
        component_deltas={"func": -0.05},
        is_regression=True,
        regression_severity="medium",
    )

    assert result.capability_id == "test_cap", "Result must not be empty"
    assert result.is_regression is True, "Result must not be empty"
    assert result.regression_severity == "medium", "Result must not be empty"
