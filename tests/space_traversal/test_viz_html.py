"""Tests for HTML visualization (v1.5.2)."""
from __future__ import annotations

from pathlib import Path


def test_generate_dashboard_basic(tmp_path: Path):
    """Test basic dashboard generation."""
    from scripts.space_traversal.viz_html import generate_dashboard

    capabilities = [
        {
            "id": "cap1",
            "score": 0.85,
            "components": {
                "functionality": 1.0,
                "consistency": 0.9,
                "tests": 0.8,
                "safeguards": 0.7,
                "documentation": 0.6,
            },
        },
        {
            "id": "cap2",
            "score": 0.75,
            "components": {
                "functionality": 0.9,
                "consistency": 0.8,
                "tests": 0.7,
                "safeguards": 0.6,
                "documentation": 0.5,
            },
        },
    ]

    trend_data = [
        {"avg_score": 0.80, "date": "2024-01-01"},
        {"avg_score": 0.82, "date": "2024-01-02"},
    ]

    output_path = tmp_path / "dashboard.html"
    generate_dashboard(
        capabilities=capabilities,
        trend_data=trend_data,
        output_path=output_path,
        repo_name="Test Repo",
        version="1.5.2",
    )

    assert output_path.exists()
    content = output_path.read_text()

    # Check essential HTML elements
    assert "<!DOCTYPE html>" in content
    assert "Audit Dashboard" in content
    assert "Test Repo" in content
    assert "cap1" in content
    assert "cap2" in content


def test_generate_dashboard_with_regressions(tmp_path: Path):
    """Test dashboard with regression data."""
    from scripts.space_traversal.viz_html import generate_dashboard

    capabilities = [{"id": "cap1", "score": 0.75, "components": {}}]
    trend_data = []
    regressions = [
        {"capability_id": "cap1", "delta": -0.1, "severity": "high"},
    ]

    output_path = tmp_path / "dashboard.html"
    generate_dashboard(
        capabilities=capabilities,
        trend_data=trend_data,
        output_path=output_path,
        regressions=regressions,
    )

    content = output_path.read_text()
    # Regression count should be shown
    assert ">1<" in content  # Regression count


def test_generate_dashboard_chart_data(tmp_path: Path):
    """Test dashboard chart data JSON."""
    from scripts.space_traversal.viz_html import generate_dashboard

    capabilities = [
        {"id": "high", "score": 0.90, "components": {}},
        {"id": "medium", "score": 0.80, "components": {}},
        {"id": "low", "score": 0.60, "components": {}},
    ]

    trend_data = [
        {"avg_score": 0.75, "timestamp": 1704067200},
        {"avg_score": 0.78, "timestamp": 1704153600},
    ]

    output_path = tmp_path / "dashboard.html"
    generate_dashboard(
        capabilities=capabilities,
        trend_data=trend_data,
        output_path=output_path,
    )

    content = output_path.read_text()

    # Check distribution data (high=1, medium=1, low=1)
    assert "[1, 1, 1]" in content


def test_generate_dashboard_empty_trend(tmp_path: Path):
    """Test dashboard with no trend data."""
    from scripts.space_traversal.viz_html import generate_dashboard

    capabilities = [{"id": "cap1", "score": 0.85, "components": {}}]

    output_path = tmp_path / "dashboard.html"
    generate_dashboard(
        capabilities=capabilities,
        trend_data=[],
        output_path=output_path,
    )

    assert output_path.exists()


def test_generate_capability_detail(tmp_path: Path):
    """Test capability detail page generation."""
    from scripts.space_traversal.viz_html import generate_capability_detail

    capability = {
        "id": "checkpointing",
        "score": 0.85,
        "components": {
            "functionality": 1.0,
            "consistency": 0.9,
            "tests": 0.8,
            "safeguards": 0.7,
            "documentation": 0.6,
        },
    }

    trend_history = [
        {"score": 0.85, "timestamp": 1704153600},
        {"score": 0.80, "timestamp": 1704067200},
        {"score": 0.78, "timestamp": 1703980800},
    ]

    output_path = tmp_path / "checkpointing.html"
    generate_capability_detail(capability, trend_history, output_path)

    assert output_path.exists()
    content = output_path.read_text()

    assert "checkpointing" in content
    assert "0.85" in content
    assert "Components" in content
    assert "Score History" in content


def test_generate_dashboard_creates_directory(tmp_path: Path):
    """Test dashboard creates parent directories."""
    from scripts.space_traversal.viz_html import generate_dashboard

    capabilities = [{"id": "cap1", "score": 0.85, "components": {}}]

    output_path = tmp_path / "nested" / "dir" / "dashboard.html"
    generate_dashboard(
        capabilities=capabilities,
        trend_data=[],
        output_path=output_path,
    )

    assert output_path.exists()
    assert output_path.parent.exists()


def test_html_template_content():
    """Test HTML template contains required elements."""
    from scripts.space_traversal.viz_html import HTML_TEMPLATE

    assert "<html" in HTML_TEMPLATE
    assert "Chart.js" in HTML_TEMPLATE or "chart.js" in HTML_TEMPLATE
    assert "distributionChart" in HTML_TEMPLATE
    assert "trendChart" in HTML_TEMPLATE
    assert "{repo_name}" in HTML_TEMPLATE
    assert "{avg_score" in HTML_TEMPLATE


def test_dashboard_score_classes(tmp_path: Path):
    """Test score class assignment."""
    from scripts.space_traversal.viz_html import generate_dashboard

    # High average
    capabilities_high = [{"id": "cap1", "score": 0.90, "components": {}}]
    output_high = tmp_path / "high.html"
    generate_dashboard(capabilities_high, [], output_high)
    assert 'class="score high"' in output_high.read_text()

    # Medium average
    capabilities_med = [{"id": "cap1", "score": 0.75, "components": {}}]
    output_med = tmp_path / "med.html"
    generate_dashboard(capabilities_med, [], output_med)
    assert 'class="score medium"' in output_med.read_text()

    # Low average
    capabilities_low = [{"id": "cap1", "score": 0.60, "components": {}}]
    output_low = tmp_path / "low.html"
    generate_dashboard(capabilities_low, [], output_low)
    assert 'class="score low"' in output_low.read_text()
