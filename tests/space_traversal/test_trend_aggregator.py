"""Tests for trend aggregation."""

from __future__ import annotations

import json
import time
from pathlib import Path


def test_aggregate_trends_basic(tmp_path: Path):
    """Test basic trend aggregation."""
    from scripts.space_traversal.trend_aggregator import aggregate_trends

    # Create test data - multiple audit runs
    artifacts_dir = tmp_path / "audit_artifacts"
    artifacts_dir.mkdir()
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()

    # Create two scored capability files
    run1 = {
        "timestamp": time.time() - 86400,  # 1 day ago
        "capabilities": [
            {"id": "cap1", "score": 0.7},
            {"id": "cap2", "score": 0.8},
        ],
    }

    run2 = {
        "timestamp": time.time(),  # now
        "capabilities": [
            {"id": "cap1", "score": 0.75},
            {"id": "cap2", "score": 0.85},
            {"id": "cap3", "score": 0.6},
        ],
    }

    (artifacts_dir / "capabilities_scored_1.json").write_text(json.dumps(run1))
    (artifacts_dir / "capabilities_scored_2.json").write_text(json.dumps(run2))

    # Aggregate
    result = aggregate_trends(artifacts_dir, reports_dir)

    assert result["run_count"] == 2, "Result must not be empty"
    assert result["summary_stats"]["capabilities_tracked"] == 3, "Result must not be empty"
    assert "cap1" in result["capability_trends"], "Result must not be empty"
    assert "cap2" in result["capability_trends"], "Result must not be empty"
    assert "cap3" in result["capability_trends"], "Result must not be empty"

    # Check cap1 trend
    cap1_trend = result["capability_trends"]["cap1"]
    assert len(cap1_trend) == 2, "Cap1_trend must not be empty"
    assert cap1_trend[0]["score"] == 0.7, "Condition must be true"
    assert cap1_trend[1]["score"] == 0.75, "Condition must be true"


def test_aggregate_trends_empty(tmp_path: Path):
    """Test trend aggregation with no data."""
    from scripts.space_traversal.trend_aggregator import aggregate_trends

    artifacts_dir = tmp_path / "audit_artifacts"
    artifacts_dir.mkdir()
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()

    result = aggregate_trends(artifacts_dir, reports_dir)

    assert result["run_count"] == 0, "Result must not be empty"
    assert "error" in result, "Result must not be empty"


def test_aggregate_trends_lookback(tmp_path: Path):
    """Test trend aggregation with lookback filter."""
    from scripts.space_traversal.trend_aggregator import aggregate_trends

    artifacts_dir = tmp_path / "audit_artifacts"
    artifacts_dir.mkdir()
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()

    now = time.time()

    # Create runs at different times
    run1 = {
        "timestamp": now - (10 * 86400),  # 10 days ago
        "capabilities": [{"id": "cap1", "score": 0.5}],
    }

    run2 = {
        "timestamp": now - (5 * 86400),  # 5 days ago
        "capabilities": [{"id": "cap1", "score": 0.6}],
    }

    run3 = {"timestamp": now, "capabilities": [{"id": "cap1", "score": 0.7}]}  # now

    (artifacts_dir / "capabilities_scored_1.json").write_text(json.dumps(run1))
    (artifacts_dir / "capabilities_scored_2.json").write_text(json.dumps(run2))
    (artifacts_dir / "capabilities_scored_3.json").write_text(json.dumps(run3))

    # Only last 7 days
    result = aggregate_trends(artifacts_dir, reports_dir, lookback_days=7)

    assert result["run_count"] == 2, "Result must not be empty"
    cap1_trend = result["capability_trends"]["cap1"]
    assert len(cap1_trend) == 2, "Cap1_trend must not be empty"
    assert cap1_trend[0]["score"] == 0.6, "Condition must be true"


def test_aggregate_trends_manifest_paths(tmp_path: Path):
    """Test trend aggregation with explicit manifest paths."""
    from scripts.space_traversal.trend_aggregator import aggregate_trends

    artifacts_dir = tmp_path / "audit_artifacts"
    artifacts_dir.mkdir()
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()

    # Create external manifest
    external_dir = tmp_path / "external"
    external_dir.mkdir()

    manifest = {"timestamp": time.time(), "capabilities": [{"id": "external_cap", "score": 0.9}]}

    manifest_path = external_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest))

    # Aggregate with explicit path
    result = aggregate_trends(artifacts_dir, reports_dir, manifest_paths=[manifest_path])

    assert result["run_count"] == 1, "Result must not be empty"
    assert "external_cap" in result["capability_trends"], "Result must not be empty"


def test_generate_trend_report(tmp_path: Path):
    """Test trend report generation."""
    from scripts.space_traversal.trend_aggregator import generate_trend_report

    trend_data = {
        "run_count": 3,
        "time_range": {
            "earliest": time.time() - 86400,
            "latest": time.time(),
            "earliest_iso": "2024-01-01T00:00:00",
            "latest_iso": "2024-01-02T00:00:00",
        },
        "summary_stats": {
            "avg_score": 0.75,
            "capabilities_tracked": 5,
            "trending_up": [{"id": "cap1", "delta": 0.1}, {"id": "cap2", "delta": 0.05}],
            "trending_down": [{"id": "cap3", "delta": -0.02}],
            "stable": ["cap4", "cap5"],
        },
        "capability_trends": {},
    }

    output_path = tmp_path / "trend_report.md"
    generate_trend_report(trend_data, output_path)

    assert output_path.exists(), "Condition must be true"
    content = output_path.read_text()
    assert "Capability Audit Trend Report" in content, "Content must not be empty"
    assert "**Runs Analyzed**: 3" in content or "Runs Analyzed: 3" in content, "Content must not be empty"
    assert "cap1" in content, "Content must not be empty"

    # Check JSON was also written
    json_path = tmp_path / "trend_report.json"
    assert json_path.exists(), "Condition must be true"
    json_data = json.loads(json_path.read_text())
    assert json_data["run_count"] == 3, "Data must not be empty"


def test_filter_by_lookback():
    """Test lookback filtering."""
    from scripts.space_traversal.trend_aggregator import _filter_by_lookback

    now = time.time()
    runs = [
        {"timestamp": now - (10 * 86400)},
        {"timestamp": now - (5 * 86400)},
        {"timestamp": now - (1 * 86400)},
        {"timestamp": now},
    ]

    # No filter
    filtered = _filter_by_lookback(runs, None)
    assert len(filtered) == 4, "Filtered must not be empty"

    # Last 7 days
    filtered = _filter_by_lookback(runs, 7)
    assert len(filtered) == 3, "Filtered must not be empty"

    # Last 2 days
    filtered = _filter_by_lookback(runs, 2)
    assert len(filtered) == 2, "Filtered must not be empty"


def test_load_manifest_or_scored(tmp_path: Path):
    """Test loading manifest or scored files."""
    from scripts.space_traversal.trend_aggregator import _load_manifest_or_scored

    # Test with capabilities_scored format
    scored_data = {"generated": time.time(), "capabilities": [{"id": "cap1", "score": 0.8}]}

    scored_file = tmp_path / "capabilities_scored.json"
    scored_file.write_text(json.dumps(scored_data))

    result = _load_manifest_or_scored(scored_file)
    assert result is not None, "result must be initialized"
    assert len(result["capabilities"]) == 1, "Collection must not be empty"
    assert result["capabilities"][0]["id"] == "cap1", "Result must not be empty"

    # Test with ISO timestamp string
    manifest_data = {
        "timestamp": "2024-01-01 12:00:00 UTC",
        "capabilities": [{"id": "cap2", "score": 0.7}],
    }

    manifest_file = tmp_path / "manifest.json"
    manifest_file.write_text(json.dumps(manifest_data))

    result = _load_manifest_or_scored(manifest_file)
    assert result is not None, "result must be initialized"
    assert isinstance(result["timestamp"], (int, float))


def test_trending_detection(tmp_path: Path):
    """Test detection of trending up/down/stable capabilities."""
    from scripts.space_traversal.trend_aggregator import aggregate_trends

    artifacts_dir = tmp_path / "audit_artifacts"
    artifacts_dir.mkdir()
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()

    now = time.time()

    # Create runs showing trends
    run1 = {
        "timestamp": now - 86400,
        "capabilities": [
            {"id": "improving", "score": 0.5},
            {"id": "declining", "score": 0.8},
            {"id": "stable", "score": 0.7},
        ],
    }

    run2 = {
        "timestamp": now,
        "capabilities": [
            {"id": "improving", "score": 0.7},  # +0.2
            {"id": "declining", "score": 0.6},  # -0.2
            {"id": "stable", "score": 0.7},  # 0
        ],
    }

    (artifacts_dir / "capabilities_scored_1.json").write_text(json.dumps(run1))
    (artifacts_dir / "capabilities_scored_2.json").write_text(json.dumps(run2))

    result = aggregate_trends(artifacts_dir, reports_dir)

    stats = result["summary_stats"]

    # Check trending up
    trending_up_ids = [item["id"] for item in stats["trending_up"]]
    assert "improving" in trending_up_ids, "Condition must be true"

    # Check trending down
    trending_down_ids = [item["id"] for item in stats["trending_down"]]
    assert "declining" in trending_down_ids, "Condition must be true"

    # Check stable
    assert "stable" in stats["stable"], "Condition must be true"
