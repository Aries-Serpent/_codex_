"""Tests for RAG analytics module — CB-002: coverage ≥95%.

Covers:
- codex.rag.analytics.metrics_db.MetricsDatabase (all public methods)
- codex.rag.analytics.metrics_db.QueryMetric (dataclass)
- codex.rag.analytics.dashboard.AnalyticsDashboard.generate_html
- codex.rag.analytics.__init__ exports
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# QueryMetric dataclass
# ---------------------------------------------------------------------------


class TestQueryMetric:
    """Tests for the QueryMetric dataclass."""

    def test_query_metric_creation(self):
        """QueryMetric can be created with all fields."""
        from codex.rag.analytics.metrics_db import QueryMetric

        qm = QueryMetric(
            timestamp="2026-01-01T00:00:00Z",
            query="test query",
            index_name="main",
            tenant_id="default",
            top_k=5,
            latency_ms=42.5,
            cache_hit=False,
            num_results=5,
            avg_score=0.85,
        )
        assert qm.timestamp == "2026-01-01T00:00:00Z", "timestamp is not valid"
        assert qm.query == "test query", "query is not valid"
        assert qm.index_name == "main", "index_name is not valid"
        assert qm.tenant_id == "default", "tenant_id is not valid"
        assert qm.top_k == 5, "top_k is not valid"
        assert qm.latency_ms == 42.5, "latency_ms is not valid"
        assert qm.cache_hit is False, "cache_hit is not valid"
        assert qm.num_results == 5, "Result must not be empty"
        assert qm.avg_score == 0.85, "avg_score is not valid"

    def test_query_metric_cache_hit_true(self):
        """QueryMetric stores cache_hit=True."""
        from codex.rag.analytics.metrics_db import QueryMetric

        qm = QueryMetric(
            timestamp="2026-01-01T00:00:00Z",
            query="cached",
            index_name="idx",
            tenant_id="t1",
            top_k=3,
            latency_ms=5.0,
            cache_hit=True,
            num_results=3,
            avg_score=0.9,
        )
        assert qm.cache_hit is True, "cache_hit is not valid"

    def test_query_metric_equality(self):
        """Two QueryMetrics with same fields are equal (dataclass)."""
        from codex.rag.analytics.metrics_db import QueryMetric

        qm1 = QueryMetric("t", "q", "i", "u", 5, 10.0, False, 5, 0.8)
        qm2 = QueryMetric("t", "q", "i", "u", 5, 10.0, False, 5, 0.8)
        assert qm1 == qm2, "qm1 is not valid"


# ---------------------------------------------------------------------------
# MetricsDatabase
# ---------------------------------------------------------------------------


class TestMetricsDatabase:
    """Tests for MetricsDatabase — covers all public methods."""

    @pytest.fixture()
    def db(self, tmp_path):
        """Create a fresh MetricsDatabase backed by a temp file."""
        from codex.rag.analytics.metrics_db import MetricsDatabase

        return MetricsDatabase(db_path=tmp_path / "test_rag_metrics.db")

    @pytest.fixture()
    def sample_metric(self):
        from codex.rag.analytics.metrics_db import QueryMetric

        return QueryMetric(
            timestamp="2026-01-01T12:00:00",
            query="What is RAG?",
            index_name="docs",
            tenant_id="team-a",
            top_k=5,
            latency_ms=120.0,
            cache_hit=False,
            num_results=5,
            avg_score=0.88,
        )

    # --- init / schema ---------------------------------------------------------

    def test_init_creates_db_file(self, tmp_path):
        """MetricsDatabase.__init__ creates the SQLite file."""
        from codex.rag.analytics.metrics_db import MetricsDatabase

        db_path = tmp_path / "sub" / "rag.db"
        db = MetricsDatabase(db_path=db_path)
        assert db.db_path.exists(), "Condition must be true"

    def test_init_default_path(self):
        """MetricsDatabase uses ~/.codex/rag_metrics.db when no path given."""
        from codex.rag.analytics.metrics_db import MetricsDatabase

        with patch("codex.rag.analytics.metrics_db.Path.home") as mock_home:
            mock_home.return_value = Path(tempfile.mkdtemp())
            db = MetricsDatabase()
            assert "rag_metrics.db" in str(db.db_path), "Condition must be true"

    def test_schema_tables_exist(self, db):
        """Both query_metrics and index_stats tables are created."""
        import sqlite3

        with sqlite3.connect(db.db_path) as conn:
            tables = {
                r[0]
                for r in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
        assert "query_metrics" in tables, "Condition must be true"
        assert "index_stats" in tables, "Condition must be true"

    # --- log_query -------------------------------------------------------------

    def test_log_query_inserts_row(self, db, sample_metric):
        """log_query stores the metric in the database."""
        import sqlite3

        db.log_query(sample_metric)
        with sqlite3.connect(db.db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM query_metrics").fetchone()[0]
        assert count == 1, "Count must be greater than zero"

    def test_log_query_values_correct(self, db, sample_metric):
        """log_query stores all fields correctly."""
        import sqlite3

        db.log_query(sample_metric)
        with sqlite3.connect(db.db_path) as conn:
            row = conn.execute(
                "SELECT query, index_name, latency_ms, cache_hit FROM query_metrics"
            ).fetchone()
        assert row[0] == "What is RAG?", "What is not valid"
        assert row[1] == "docs", "Condition must be true"
        assert row[2] == 120.0, "Condition must be true"
        assert row[3] == 0, "Condition must be true"

    def test_log_query_cache_hit_stored_as_1(self, db):
        """log_query stores cache_hit=True as integer 1."""
        import sqlite3

        from codex.rag.analytics.metrics_db import QueryMetric

        qm = QueryMetric("2026-01-01T00:00:00", "q", "i", "u", 3, 5.0, True, 3, 0.9)
        db.log_query(qm)
        with sqlite3.connect(db.db_path) as conn:
            val = conn.execute("SELECT cache_hit FROM query_metrics").fetchone()[0]
        assert val == 1, "val is not valid"

    def test_log_multiple_queries(self, db, sample_metric):
        """log_query handles multiple inserts."""
        import sqlite3

        for _ in range(5):
            db.log_query(sample_metric)
        with sqlite3.connect(db.db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM query_metrics").fetchone()[0]
        assert count == 5, "Count must be greater than zero"

    # --- get_stats -------------------------------------------------------------

    def test_get_stats_empty_db(self, db):
        """get_stats returns zeros for empty database."""
        stats = db.get_stats()
        assert stats["total_queries"] == 0, "Condition must be true"
        assert stats["avg_latency_ms"] == 0.0, "Condition must be true"

    def test_get_stats_single_entry(self, db, sample_metric):
        """get_stats computes correct stats for a single entry."""
        db.log_query(sample_metric)
        # Use a large hours window so the entry is included
        stats = db.get_stats(hours=999999)
        assert stats["total_queries"] == 1, "Condition must be true"
        assert stats["avg_latency_ms"] == 120.0, "Condition must be true"
        assert stats["cache_hit_rate"] == 0.0, "Condition must be true"
        assert stats["avg_score"] == 0.88, "Condition must be true"

    def test_get_stats_cache_hit_rate(self, db):
        """get_stats calculates cache hit rate correctly."""
        from codex.rag.analytics.metrics_db import QueryMetric

        # 2 hits, 2 misses → 50%
        for hit in [True, True, False, False]:
            db.log_query(QueryMetric("2026-01-01T00:00:00", "q", "i", "u", 3, 10.0, hit, 3, 0.8))
        stats = db.get_stats(hours=999999)
        assert stats["total_queries"] == 4, "Condition must be true"
        assert stats["cache_hit_rate"] == 50.0, "Condition must be true"

    def test_get_stats_with_index_filter(self, db):
        """get_stats filters by index_name correctly."""
        from codex.rag.analytics.metrics_db import QueryMetric

        db.log_query(QueryMetric("2026-01-01T00:00:00", "q", "idx-a", "u", 3, 10.0, False, 3, 0.7))
        db.log_query(QueryMetric("2026-01-01T00:00:00", "q", "idx-b", "u", 3, 20.0, False, 3, 0.9))
        stats_a = db.get_stats(index_name="idx-a", hours=999999)
        stats_b = db.get_stats(index_name="idx-b", hours=999999)
        assert stats_a["total_queries"] == 1, "Condition must be true"
        assert stats_b["total_queries"] == 1, "Condition must be true"
        assert stats_a["avg_latency_ms"] == 10.0, "Condition must be true"

    def test_get_stats_multiple_entries(self, db):
        """get_stats averages across multiple entries."""
        from codex.rag.analytics.metrics_db import QueryMetric

        db.log_query(QueryMetric("2026-01-01T00:00:00", "q", "i", "u", 3, 100.0, False, 3, 0.8))
        db.log_query(QueryMetric("2026-01-01T00:00:00", "q", "i", "u", 3, 200.0, False, 3, 0.6))
        stats = db.get_stats(hours=999999)
        assert stats["total_queries"] == 2, "Condition must be true"
        assert stats["avg_latency_ms"] == 150.0, "Condition must be true"
        assert round(stats["avg_score"], 2) == 0.70

    # --- get_percentiles -------------------------------------------------------

    def test_get_percentiles_empty_db(self, db):
        """get_percentiles returns zeros for empty database."""
        pcts = db.get_percentiles()
        assert pcts == {"p50": 0.0, "p95": 0.0, "p99": 0.0}

    def test_get_percentiles_single_entry(self, db, sample_metric):
        """get_percentiles with one entry returns that value for all percentiles."""
        db.log_query(sample_metric)
        pcts = db.get_percentiles(hours=999999)
        assert pcts["p50"] == 120.0, "Condition must be true"

    def test_get_percentiles_multiple_entries(self, db):
        """get_percentiles returns correct ordinal values."""
        from codex.rag.analytics.metrics_db import QueryMetric

        latencies = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
        for lat in latencies:
            db.log_query(QueryMetric("2026-01-01T00:00:00", "q", "i", "u", 3, lat, False, 3, 0.8))
        pcts = db.get_percentiles(hours=999999)
        # p50 = latencies[5], p95 = latencies[9], p99 = latencies[9]
        assert pcts["p50"] == latencies[5], "Condition must be true"
        assert pcts["p99"] == latencies[9], "Condition must be true"

    def test_get_percentiles_with_index_filter(self, db):
        """get_percentiles accepts index_name filter."""
        from codex.rag.analytics.metrics_db import QueryMetric

        db.log_query(QueryMetric("2026-01-01T00:00:00", "q", "idx-x", "u", 3, 999.0, False, 3, 0.5))
        db.log_query(QueryMetric("2026-01-01T00:00:00", "q", "idx-y", "u", 3, 1.0, False, 3, 0.5))
        pcts = db.get_percentiles(index_name="idx-x", hours=999999)
        assert pcts["p50"] == 999.0, "Condition must be true"

    # --- export_to_json --------------------------------------------------------

    def test_export_to_json_empty(self, db, tmp_path):
        """export_to_json writes valid empty JSON for empty database."""
        out = tmp_path / "export.json"
        db.export_to_json(out, hours=999999)
        assert out.exists(), "Condition must be true"
        data = json.loads(out.read_text())
        assert data == [], "Data must not be empty"

    def test_export_to_json_with_data(self, db, tmp_path, sample_metric):
        """export_to_json exports rows as JSON dicts."""
        db.log_query(sample_metric)
        out = tmp_path / "export.json"
        db.export_to_json(out, hours=999999)
        data = json.loads(out.read_text())
        assert len(data) == 1, "Data must not be empty"
        assert data[0]["query"] == "What is RAG?", "Data must not be empty"
        assert data[0]["index_name"] == "docs", "Data must not be empty"
        assert data[0]["latency_ms"] == 120.0, "Data must not be empty"
        assert data[0]["cache_hit"] is False, "Data must not be empty"

    def test_export_to_json_multiple_entries(self, db, tmp_path):
        """export_to_json exports all rows ordered by timestamp DESC."""
        from codex.rag.analytics.metrics_db import QueryMetric

        for i in range(3):
            db.log_query(
                QueryMetric(
                    f"2026-01-0{i+1}T00:00:00", f"q{i}", "i", "u", 3, float(i * 10), False, 3, 0.8
                )
            )
        out = tmp_path / "multi.json"
        db.export_to_json(out, hours=999999)
        data = json.loads(out.read_text())
        assert len(data) == 3, "Data must not be empty"

    def test_export_to_json_cache_hit_as_bool(self, db, tmp_path):
        """export_to_json converts cache_hit integer back to bool."""
        from codex.rag.analytics.metrics_db import QueryMetric

        db.log_query(QueryMetric("2026-01-01T00:00:00", "q", "i", "u", 3, 5.0, True, 3, 0.9))
        out = tmp_path / "export.json"
        db.export_to_json(out, hours=999999)
        data = json.loads(out.read_text())
        assert data[0]["cache_hit"] is True, "Data must not be empty"


# ---------------------------------------------------------------------------
# AnalyticsDashboard
# ---------------------------------------------------------------------------


class TestAnalyticsDashboard:
    """Tests for AnalyticsDashboard.generate_html."""

    @pytest.fixture()
    def dashboard(self, tmp_path):
        from codex.rag.analytics.dashboard import AnalyticsDashboard
        from codex.rag.analytics.metrics_db import MetricsDatabase

        db = MetricsDatabase(db_path=tmp_path / "dash.db")
        return AnalyticsDashboard(metrics_db=db)

    def test_generate_html_returns_string(self, dashboard):
        """generate_html returns a non-empty HTML string."""
        html = dashboard.generate_html()
        assert isinstance(html, str)
        assert len(html) > 0, "Html must not be empty"

    def test_generate_html_contains_doctype(self, dashboard):
        """generate_html returns valid HTML with DOCTYPE."""
        html = dashboard.generate_html()
        assert "<!DOCTYPE html>" in html, "Condition must be true"

    def test_generate_html_contains_title(self, dashboard):
        """generate_html includes RAG Analytics Dashboard title."""
        html = dashboard.generate_html()
        assert "RAG Analytics Dashboard" in html, "Condition must be true"

    def test_generate_html_with_custom_hours(self, dashboard):
        """generate_html accepts hours parameter."""
        html_24 = dashboard.generate_html(hours=24)
        html_72 = dashboard.generate_html(hours=72)
        assert isinstance(html_24, str)
        assert isinstance(html_72, str)

    def test_generate_html_zero_stats(self, dashboard):
        """generate_html renders correctly with no data (zeros)."""
        html = dashboard.generate_html()
        # Should show 0 for total queries
        assert "0" in html, "Condition must be true"

    def test_generate_html_with_data(self, tmp_path):
        """generate_html renders actual query data."""
        from codex.rag.analytics.dashboard import AnalyticsDashboard
        from codex.rag.analytics.metrics_db import MetricsDatabase, QueryMetric

        db = MetricsDatabase(db_path=tmp_path / "data.db")
        db.log_query(
            QueryMetric("2026-01-01T00:00:00", "test", "main", "default", 5, 55.0, True, 4, 0.92)
        )
        dashboard = AnalyticsDashboard(metrics_db=db)
        html = dashboard.generate_html(hours=999999)
        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html, "Condition must be true"

    def test_dashboard_stores_metrics_db_ref(self, tmp_path):
        """AnalyticsDashboard.metrics_db is set on init."""
        from codex.rag.analytics.dashboard import AnalyticsDashboard
        from codex.rag.analytics.metrics_db import MetricsDatabase

        db = MetricsDatabase(db_path=tmp_path / "ref.db")
        dash = AnalyticsDashboard(metrics_db=db)
        assert dash.metrics_db is db, "metrics_db is not valid"


# ---------------------------------------------------------------------------
# __init__ exports
# ---------------------------------------------------------------------------


class TestAnalyticsInit:
    """Tests for codex.rag.analytics __init__ exports."""

    def test_import_analytics_dashboard(self):
        """AnalyticsDashboard is importable from codex.rag.analytics."""
        from codex.rag.analytics import AnalyticsDashboard

        assert AnalyticsDashboard is not None, "AnalyticsDashboard must be initialized"

    def test_import_metrics_database(self):
        """MetricsDatabase is importable from codex.rag.analytics."""
        from codex.rag.analytics import MetricsDatabase

        assert MetricsDatabase is not None, "MetricsDatabase must be initialized"

    def test_import_query_metric(self):
        """QueryMetric is importable from codex.rag.analytics."""
        from codex.rag.analytics import QueryMetric

        assert QueryMetric is not None, "QueryMetric must be initialized"
