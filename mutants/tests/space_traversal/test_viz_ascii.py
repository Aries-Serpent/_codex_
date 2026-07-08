"""Tests for ASCII visualization (v1.5.2)."""

from __future__ import annotations


def test_sparkline_basic():
    """Test basic sparkline generation."""
    from scripts.space_traversal.viz_ascii import sparkline

    values = [0.0, 0.25, 0.5, 0.75, 1.0]
    spark = sparkline(values)

    assert len(spark) == 5, "Spark must not be empty"
    # First should be lowest, last should be highest
    assert spark[0] == " ", "Condition must be true"
    assert spark[-1] == "█", "Condition must be true"


def test_sparkline_empty():
    """Test sparkline with empty values."""
    from scripts.space_traversal.viz_ascii import sparkline

    assert sparkline([]) == "—", "Condition must be true"


def test_sparkline_constant():
    """Test sparkline with constant values."""
    from scripts.space_traversal.viz_ascii import sparkline

    spark = sparkline([0.5, 0.5, 0.5, 0.5])
    # All values same, should use middle block
    assert len(spark) == 4, "Spark must not be empty"
    assert all(c == "▄" for c in spark), "c is not valid"


def test_sparkline_width_limit():
    """Test sparkline respects width limit."""
    from scripts.space_traversal.viz_ascii import sparkline

    values = list(range(100))
    spark = sparkline(values, width=20)
    assert len(spark) == 20, "Spark must not be empty"


def test_bar_chart_basic():
    """Test basic bar chart generation."""
    from scripts.space_traversal.viz_ascii import bar_chart

    data = {"High": 0.9, "Medium": 0.6, "Low": 0.3}
    chart = bar_chart(data, width=20)

    lines = chart.split("\n")
    assert len(lines) == 3, "Lines must not be empty"

    # Check that High has more filled chars than Low
    assert lines[0].count("█") > lines[2].count("█"), "Value must be greater than zero"


def test_bar_chart_empty():
    """Test bar chart with empty data."""
    from scripts.space_traversal.viz_ascii import bar_chart

    assert bar_chart({}) == "", "Condition must be true"


def test_bar_chart_show_values():
    """Test bar chart with/without values."""
    from scripts.space_traversal.viz_ascii import bar_chart

    data = {"Test": 0.75}

    with_values = bar_chart(data, show_values=True)
    assert "0.75" in with_values, "Value must be initialized"

    without_values = bar_chart(data, show_values=False)
    assert "0.75" not in without_values, "Value must be initialized"


def test_trend_indicator():
    """Test trend indicator emojis."""
    from scripts.space_traversal.viz_ascii import trend_indicator

    assert trend_indicator(0.85, 0.80) == "📈"  # Improving
    assert trend_indicator(0.75, 0.80) == "📉"  # Declining
    assert trend_indicator(0.80, 0.80) == "➡️"  # Stable
    assert trend_indicator(0.81, 0.80) == "➡️"  # Within threshold


def test_score_badge():
    """Test score badge generation."""
    from scripts.space_traversal.viz_ascii import score_badge

    assert "🟢" in score_badge(0.95), "Condition must be true"
    assert "🟢" in score_badge(0.96), "Condition must be true"
    assert "🟡" in score_badge(0.85), "Condition must be true"
    assert "🟡" in score_badge(0.90), "Condition must be true"
    assert "🟠" in score_badge(0.70), "Condition must be true"
    assert "🟠" in score_badge(0.80), "Condition must be true"
    assert "🔴" in score_badge(0.60), "Condition must be true"
    assert "🔴" in score_badge(0.50), "Condition must be true"


def test_mini_bar():
    """Test mini bar generation."""
    from scripts.space_traversal.viz_ascii import mini_bar

    bar = mini_bar(0.5, width=10)
    assert len(bar) == 10, "Bar must not be empty"
    assert bar.count("█") == 5, "Count must be greater than zero"
    assert bar.count("░") == 5, "Count must be greater than zero"

    full = mini_bar(1.0, width=10)
    assert full.count("█") == 10, "Count must be greater than zero"

    empty = mini_bar(0.0, width=10)
    assert empty.count("░") == 10, "Count must be greater than zero"


def test_progress_bar():
    """Test progress bar generation."""
    from scripts.space_traversal.viz_ascii import progress_bar

    bar = progress_bar(0.75, width=20, show_percent=True)
    assert "75.0%" in bar, "Condition must be true"
    assert "█" in bar, "Condition must be true"
    assert "░" in bar, "Condition must be true"


def test_capability_dashboard():
    """Test full capability dashboard generation."""
    from scripts.space_traversal.viz_ascii import capability_dashboard

    trend_data = [
        {"score": 0.85, "timestamp": 1234567890},
        {"score": 0.80, "timestamp": 1234567800},
        {"score": 0.78, "timestamp": 1234567700},
    ]

    components = {
        "functionality": 1.0,
        "consistency": 0.9,
        "tests": 0.8,
        "safeguards": 0.7,
        "documentation": 0.6,
    }

    dashboard = capability_dashboard(
        capability_id="checkpointing",
        current_score=0.85,
        trend_data=trend_data,
        components=components,
    )

    assert "checkpointing" in dashboard, "Condition must be true"
    assert "Score:" in dashboard, "Condition must be true"
    assert "Trend:" in dashboard, "Condition must be true"
    assert "Components:" in dashboard, "Condition must be true"
    assert "functionality" in dashboard, "Condition must be true"


def test_summary_table():
    """Test summary table generation."""
    from scripts.space_traversal.viz_ascii import summary_table

    capabilities = [
        {"id": "cap1", "score": 0.85},
        {"id": "cap2", "score": 0.75},
        {"id": "cap3", "score": 0.65},
    ]

    table = summary_table(capabilities, show_trend=False)
    lines = table.split("\n")

    # Header + separator + 3 data rows
    assert len(lines) == 5, "Lines must not be empty"
    assert "cap1" in table, "Condition must be true"
    assert "0.85" in table, "Condition must be true"


def test_regression_alert_empty():
    """Test regression alert with no regressions."""
    from scripts.space_traversal.viz_ascii import regression_alert

    alert = regression_alert([])
    assert "No regressions detected" in alert, "Condition must be true"


def test_regression_alert_with_regressions():
    """Test regression alert with regressions."""
    from scripts.space_traversal.viz_ascii import regression_alert

    regressions = [
        {"capability_id": "cap1", "delta": -0.1, "severity": "high"},
        {"capability_id": "cap2", "delta": -0.05, "severity": "medium"},
    ]

    alert = regression_alert(regressions)
    assert "REGRESSIONS DETECTED" in alert, "Condition must be true"
    assert "cap1" in alert, "Condition must be true"
    assert "🔴" in alert, "Condition must be true"
