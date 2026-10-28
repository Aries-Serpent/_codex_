"""Regression coverage for Chronicle's SQLite-backed analysis and recommendations."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aries_serpent_core.logging.chronicle_analytics import ChronicleAnalytics
from aries_serpent_core.logging.session_database import SessionDatabase


@pytest.fixture
def database(tmp_path: Path) -> SessionDatabase:
    """Create an isolated session database with tool outcome data."""
    db = SessionDatabase(str(tmp_path / "sessions.db"))
    with db.get_connection() as connection:
        connection.execute("CREATE TABLE tool_calls (tool_name TEXT, success INTEGER)")
        connection.executemany(
            "INSERT INTO tool_calls VALUES (?, ?)",
            [("view", 1), ("view", 0), ("bash", 1)],
        )
        connection.commit()
    return db


def _add_sessions(database: SessionDatabase, dates: list[str]) -> None:
    """Seed deterministic session history using the production database schema."""
    with database.get_connection() as connection:
        connection.executemany(
            "INSERT INTO sessions (session_id, created_at, status, agent_name) "
            "VALUES (?, ?, ?, ?)",
            [
                (f"session-{index}", date, "complete" if index % 2 else "failed", f"agent-{index}")
                for index, date in enumerate(dates)
            ],
        )
        connection.commit()


def test_analysis_reports_real_session_and_tool_outcomes(database: SessionDatabase) -> None:
    """Reports must agree with stored outcomes rather than infer missing credits."""
    _add_sessions(
        database,
        ["2026-01-01T10:00:00Z", "2026-01-04T11:00:00Z", "2026-01-04T12:00:00Z"],
    )
    analytics = ChronicleAnalytics(database)
    report = analytics.analyze_patterns()

    assert [session["id"] for session in analytics.sessions] == [
        "session-2",
        "session-1",
        "session-0",
    ]
    assert report["frequency"]["total_sessions"] == 3
    assert report["frequency"]["date_range"] == "2026-01-01 to 2026-01-04"
    assert report["frequency"]["avg_sessions_per_day"] == 0.75
    assert report["tools"]["top_tools"] == {"view": 2, "bash": 1}
    assert report["tools"]["tool_success_rates"]["view"]["success_rate"] == 50.0
    assert report["performance"]["successful"] == 1
    assert report["performance"]["failed"] == 2
    assert report["performance"]["success_rate"] == 33.3
    assert report["agents"]["total_agents_used"] == 3
    assert report["time_patterns"]["peak_hours"] == {12: 1, 11: 1, 10: 1}
    assert report["status_distribution"] == {"failed": 2, "complete": 1}

    exported = json.loads(analytics.export_json())
    assert exported["timestamp"].endswith("Z")
    assert exported["patterns"]["performance"] == report["performance"]
    summary = analytics.generate_summary()
    assert "**Total Sessions**: 3" in summary
    assert "**Success Rate**: 33.3%" in summary
    assert "**Top Tools**: view, bash" in summary
    assert "**Top Agents**:" in summary
    assert "**Peak Hours**:" in summary


def test_empty_history_has_explicit_empty_metrics(database: SessionDatabase) -> None:
    """An empty history is not reported as successful measured activity."""
    analytics = ChronicleAnalytics(database)
    report = analytics.analyze_patterns()
    assert report["frequency"] == {}
    assert report["performance"] == {}
    assert report["insights"] == []
    assert analytics._analyze_frequency() == {}
    assert analytics._analyze_trends() == {"trend": "insufficient_data"}
    assert "**Total Sessions**: 0" in analytics.generate_summary()


@pytest.mark.parametrize(
    ("dates", "expected"),
    [
        (["2026-01-04", "2026-01-04", "2026-01-01", "2026-01-03"], "increasing"),
        (["2026-01-03", "2026-01-04", "2026-01-01", "2026-01-01"], "decreasing"),
        (["2026-01-04", "2026-01-04", "2026-01-01", "2026-01-01"], "stable"),
    ],
)
def test_trends_compare_session_density(
    database: SessionDatabase, dates: list[str], expected: str
) -> None:
    """Trend direction reflects recent versus older sessions per day."""
    _add_sessions(database, [f"{date}T12:00:00Z" for date in dates])
    assert ChronicleAnalytics(database).analyze_patterns()["trends"]["trend"] == expected


@pytest.mark.parametrize(
    ("patterns", "titles"),
    [
        (
            {
                "frequency": {"avg_sessions_per_day": 6},
                "tools": {
                    "top_tools": {"bash": 5},
                    "tool_success_rates": {"bash": {"success_rate": 40}},
                },
                "agents": {"total_agents_used": 2, "top_agents": {"agent": 2}},
                "time_patterns": {"peak_hours": {12: 3}},
                "performance": {"success_rate": 95},
                "trends": {"trend": "increasing"},
            },
            {
                "High Session Activity Detected",
                "Low Success Rate for bash",
                "Multi-Agent Delegation",
                "Peak Activity Hours",
                "Excellent Success Rate",
                "Increasing Session Activity",
            },
        ),
        (
            {
                "frequency": {"avg_sessions_per_day": 0.5},
                "performance": {"success_rate": 30},
                "trends": {"trend": "decreasing"},
            },
            {
                "Low Session Frequency",
                "Session Success Rate Below 50%",
                "Decreasing Session Frequency",
                "Use Specialized Agents",
            },
        ),
        (
            {
                "frequency": {"avg_sessions_per_day": 2},
                "performance": {"success_rate": 75},
                "agents": {"top_agents": {"agent": 1}},
            },
            set(),
        ),
    ],
)
def test_recommendations_follow_measured_patterns(
    database: SessionDatabase,
    patterns: dict,
    titles: set[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Tip strategies include only recommendations supported by their inputs."""
    analytics = ChronicleAnalytics(database)
    monkeypatch.setattr(analytics, "analyze_patterns", lambda: patterns)
    assert {tip["title"] for tip in analytics.generate_tips()} == titles
    if not titles:
        assert "No specific tips at this time" in analytics.generate_summary()


def test_unavailable_session_schema_is_logged(
    database: SessionDatabase, caplog: pytest.LogCaptureFixture
) -> None:
    """Missing session storage remains observable instead of causing a SQL crash."""
    with database.get_connection() as connection:
        connection.execute("DROP TABLE sessions")
        connection.commit()
    analytics = ChronicleAnalytics(database)
    assert analytics.sessions == []
    assert "Failed to load chronicle sessions" in caplog.text


def test_missing_tool_table_is_logged(
    database: SessionDatabase, caplog: pytest.LogCaptureFixture
) -> None:
    """Missing tool metrics are explicit and do not prevent session analysis."""
    _add_sessions(database, ["2026-01-01T12:00:00Z"])
    with database.get_connection() as connection:
        connection.execute("DROP TABLE tool_calls")
        connection.commit()
    report = ChronicleAnalytics(database).analyze_patterns()
    assert report["tools"] == {"top_tools": {}, "tool_success_rates": {}}
    assert "Failed to analyze chronicle tool usage" in caplog.text
