"""
Tests for metrics_collector.py and dashboard_generator.py

This module tests the session metrics collection and dashboard generation
for the cognitive brain system.
"""

import json
import sys
from pathlib import Path

# Add scripts/cognitive to path for import
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts' / 'cognitive'))

from dashboard_generator import (
    calculate_health_score,
    format_duration,
    generate_dashboard,
    generate_progress_bar,
    generate_sparkline,
    generate_trend_indicator,
    get_health_status,
)
from metrics_collector import (
    calculate_trends,
    extract_session_metrics,
    generate_ascii_chart,
    load_action_log,
    load_pattern_store,
    parse_timestamp,
)


class TestParseTimestamp:
    """Tests for parse_timestamp function."""

    def test_parses_iso_format(self):
        """Test parsing ISO format timestamp."""
        result = parse_timestamp("2026-02-05T10:00:00Z")
        assert result is not None
        assert result.year == 2026
        assert result.month == 2

    def test_handles_none(self):
        """Test handling of None."""
        result = parse_timestamp(None)
        assert result is None

    def test_handles_empty_string(self):
        """Test handling of empty string."""
        result = parse_timestamp("")
        assert result is None

    def test_handles_invalid_format(self):
        """Test handling of invalid format."""
        result = parse_timestamp("not a timestamp")
        assert result is None


class TestLoadActionLog:
    """Tests for load_action_log function."""

    def test_loads_valid_entries(self, tmp_path):
        """Test loading valid action log entries."""
        log_file = tmp_path / 'action_log.ndjson'
        entries = [
            {'timestamp': '2026-02-05T10:00:00Z', 'action': 'created', 'path': 'src/new.py'},
            {'timestamp': '2026-02-05T10:01:00Z', 'action': 'edited', 'path': 'src/old.py'},
        ]
        log_file.write_text('\n'.join(json.dumps(e) for e in entries))

        result = load_action_log(log_file)

        assert len(result) == 2

    def test_handles_missing_file(self, tmp_path):
        """Test handling of missing file."""
        log_file = tmp_path / 'nonexistent.ndjson'
        result = load_action_log(log_file)
        assert result == []


class TestLoadPatternStore:
    """Tests for load_pattern_store function."""

    def test_loads_valid_store(self, tmp_path):
        """Test loading valid pattern store."""
        store_file = tmp_path / 'pattern_store.json'
        store = {"patterns": {"test": {"success_rate": 0.9}}}
        store_file.write_text(json.dumps(store))

        result = load_pattern_store(store_file)

        assert "patterns" in result

    def test_handles_missing_file(self, tmp_path):
        """Test handling of missing file."""
        store_file = tmp_path / 'nonexistent.json'
        result = load_pattern_store(store_file)

        assert "patterns" in result
        assert result["patterns"] == {}


class TestExtractSessionMetrics:
    """Tests for extract_session_metrics function."""

    def test_extracts_file_metrics(self):
        """Test extraction of file metrics."""
        entries = [
            {'action': 'created', 'path': 'new.py', 'timestamp': '2026-02-05T10:00:00Z'},
            {'action': 'edited', 'path': 'old.py', 'timestamp': '2026-02-05T10:01:00Z'},
        ]
        pattern_store = {"patterns": {}, "learning_log": []}
        commits = []

        result = extract_session_metrics(entries, pattern_store, commits)

        assert result['files']['created'] == 1
        assert result['files']['modified'] == 1
        assert result['files']['total_operations'] == 2

    def test_calculates_pattern_metrics(self):
        """Test extraction of pattern metrics."""
        entries = []
        pattern_store = {
            "patterns": {
                "p1": {"success_rate": 0.9},
                "p2": {"success_rate": 0.8}
            },
            "learning_log": [
                {"patterns_applied": ["p1"], "patterns_learned": ["p3"]}
            ]
        }
        commits = []

        result = extract_session_metrics(entries, pattern_store, commits)

        assert result['patterns']['applied'] == 1
        assert result['patterns']['learned'] == 1
        assert result['patterns']['avg_success_rate'] == 0.85


class TestCalculateTrends:
    """Tests for calculate_trends function."""

    def test_returns_stable_without_previous(self):
        """Test that trends are stable without previous data."""
        current = {"files": {"total_operations": 10}}
        result = calculate_trends(current)

        assert result['files_trend'] == 'stable'

    def test_detects_increasing_trend(self):
        """Test detection of increasing trend."""
        current = {"files": {"total_operations": 20}}
        previous = {"files": {"total_operations": 10}}

        result = calculate_trends(current, previous)

        assert result['files_trend'] == 'increasing'

    def test_detects_decreasing_trend(self):
        """Test detection of decreasing trend."""
        current = {"files": {"total_operations": 5}}
        previous = {"files": {"total_operations": 10}}

        result = calculate_trends(current, previous)

        assert result['files_trend'] == 'decreasing'


class TestGenerateAsciiChart:
    """Tests for generate_ascii_chart function."""

    def test_generates_chart(self):
        """Test chart generation."""
        data = [("A", 10), ("B", 20)]
        result = generate_ascii_chart(data, width=20, title="Test")

        assert "Test" in result
        assert "A" in result
        assert "B" in result


class TestGenerateProgressBar:
    """Tests for generate_progress_bar function."""

    def test_generates_full_bar(self):
        """Test full progress bar."""
        result = generate_progress_bar(100, 100, width=10)
        assert result == "██████████"

    def test_generates_empty_bar(self):
        """Test empty progress bar."""
        result = generate_progress_bar(0, 100, width=10)
        assert result == "░░░░░░░░░░"

    def test_generates_half_bar(self):
        """Test half-filled progress bar."""
        result = generate_progress_bar(50, 100, width=10)
        assert result == "█████░░░░░"


class TestGenerateTrendIndicator:
    """Tests for generate_trend_indicator function."""

    def test_increasing_trend(self):
        """Test increasing trend indicator."""
        result = generate_trend_indicator("increasing")
        assert result == "📈"

    def test_decreasing_trend(self):
        """Test decreasing trend indicator."""
        result = generate_trend_indicator("decreasing")
        assert result == "📉"

    def test_unknown_trend(self):
        """Test unknown trend indicator."""
        result = generate_trend_indicator("unknown")
        assert result == "❓"


class TestGenerateSparkline:
    """Tests for generate_sparkline function."""

    def test_generates_sparkline(self):
        """Test sparkline generation."""
        values = [1, 2, 3, 4, 5]
        result = generate_sparkline(values, width=5)

        assert len(result) == 5
        assert result[0] == "▁"
        assert result[-1] == "█"

    def test_handles_empty_values(self):
        """Test handling of empty values."""
        result = generate_sparkline([], width=5)
        assert result == "▁▁▁▁▁"


class TestFormatDuration:
    """Tests for format_duration function."""

    def test_formats_minutes(self):
        """Test formatting minutes."""
        result = format_duration(45)
        assert result == "45m"

    def test_formats_hours_and_minutes(self):
        """Test formatting hours and minutes."""
        result = format_duration(90)
        assert result == "1h 30m"


class TestCalculateHealthScore:
    """Tests for calculate_health_score function."""

    def test_calculates_score(self):
        """Test health score calculation."""
        metrics = {
            "files": {"total_operations": 10},
            "patterns": {"avg_success_rate": 0.9},
            "commits": {"total": 5},
            "sessions": {"total": 2}
        }

        result = calculate_health_score(metrics)

        assert 0 <= result <= 100
        assert result > 0  # Should have some score

    def test_handles_empty_metrics(self):
        """Test handling of empty metrics."""
        metrics = {}
        result = calculate_health_score(metrics)
        assert result == 0


class TestGetHealthStatus:
    """Tests for get_health_status function."""

    def test_excellent_health(self):
        """Test excellent health status."""
        result = get_health_status(95)
        assert result["label"] == "Excellent"
        assert result["emoji"] == "🌟"

    def test_good_health(self):
        """Test good health status."""
        result = get_health_status(75)
        assert result["label"] == "Good"

    def test_critical_health(self):
        """Test critical health status."""
        result = get_health_status(20)
        assert result["label"] == "Critical"


class TestGenerateDashboard:
    """Tests for generate_dashboard function."""

    def test_generates_dashboard(self):
        """Test dashboard generation."""
        metrics = {
            "period": {"start": "2026-02-05T10:00:00Z", "end": "2026-02-05T12:00:00Z", "duration_minutes": 120},
            "files": {"created": 5, "modified": 10, "total_operations": 15},
            "patterns": {"applied": 3, "learned": 1, "unique_patterns": ["p1", "p2"], "avg_success_rate": 0.9},
            "commits": {"total": 5, "by_copilot": 3},
            "sessions": {"total": 2},
            "trends": {"files_trend": "increasing", "patterns_trend": "stable", "overall_health": "good"},
            "quality": {}
        }

        result = generate_dashboard(metrics)

        assert "Cognitive Brain Dashboard" in result
        assert "Quick Stats" in result
        assert "Health Score" in result
        assert "File Activity" in result

    def test_includes_patterns(self):
        """Test that patterns are included."""
        metrics = {
            "period": {"duration_minutes": 60},
            "files": {"created": 0, "modified": 0, "total_operations": 0},
            "patterns": {"applied": 0, "learned": 0, "unique_patterns": ["test_pattern"], "avg_success_rate": 0.5},
            "commits": {"total": 0, "by_copilot": 0},
            "sessions": {"total": 1},
            "trends": {},
            "quality": {}
        }

        result = generate_dashboard(metrics)

        assert "test_pattern" in result
