"""Tests for codex.rag.analytics.metrics_db — MetricsDatabase and QueryMetric."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from codex.rag.analytics.metrics_db import MetricsDatabase, QueryMetric

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _now_ts() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _make_metric(
    query: str = "test query",
    index_name: str = "idx1",
    tenant_id: str = "tenant1",
    top_k: int = 5,
    latency_ms: float = 12.5,
    cache_hit: bool = False,
    num_results: int = 5,
    avg_score: float = 0.85,
) -> QueryMetric:
    return QueryMetric(
        timestamp=_now_ts(),
        query=query,
        index_name=index_name,
        tenant_id=tenant_id,
        top_k=top_k,
        latency_ms=latency_ms,
        cache_hit=cache_hit,
        num_results=num_results,
        avg_score=avg_score,
    )


@pytest.fixture
def db(tmp_path: Path) -> MetricsDatabase:
    return MetricsDatabase(db_path=tmp_path / "test_metrics.db")


# ---------------------------------------------------------------------------
# QueryMetric dataclass
# ---------------------------------------------------------------------------


def test_query_metric_fields():
    m = _make_metric()
    assert m.query == "test query"
    assert m.index_name == "idx1"
    assert m.tenant_id == "tenant1"
    assert m.top_k == 5
    assert m.latency_ms == pytest.approx(12.5)
    assert m.cache_hit is False
    assert m.num_results == 5
    assert m.avg_score == pytest.approx(0.85)


def test_query_metric_cache_hit_true():
    m = _make_metric(cache_hit=True)
    assert m.cache_hit is True


# ---------------------------------------------------------------------------
# MetricsDatabase — initialisation
# ---------------------------------------------------------------------------


def test_db_creates_file(tmp_path: Path):
    db_path = tmp_path / "metrics.db"
    MetricsDatabase(db_path=db_path)
    assert db_path.exists()


def test_db_creates_parent_dirs(tmp_path: Path):
    db_path = tmp_path / "nested" / "path" / "metrics.db"
    MetricsDatabase(db_path=db_path)
    assert db_path.exists()


# ---------------------------------------------------------------------------
# MetricsDatabase — log_query and get_stats
# ---------------------------------------------------------------------------


def test_get_stats_empty_db(db: MetricsDatabase):
    stats = db.get_stats()
    assert stats["total_queries"] == 0


def test_log_query_increments_count(db: MetricsDatabase):
    db.log_query(_make_metric())
    stats = db.get_stats()
    assert stats["total_queries"] == 1


def test_log_multiple_queries(db: MetricsDatabase):
    for _ in range(5):
        db.log_query(_make_metric())
    stats = db.get_stats()
    assert stats["total_queries"] == 5


def test_get_stats_avg_latency(db: MetricsDatabase):
    db.log_query(_make_metric(latency_ms=10.0))
    db.log_query(_make_metric(latency_ms=20.0))
    stats = db.get_stats()
    assert stats["avg_latency_ms"] == pytest.approx(15.0)


def test_get_stats_cache_hit_rate_zero(db: MetricsDatabase):
    db.log_query(_make_metric(cache_hit=False))
    db.log_query(_make_metric(cache_hit=False))
    stats = db.get_stats()
    assert stats["cache_hit_rate"] == pytest.approx(0.0)


def test_get_stats_cache_hit_rate_100(db: MetricsDatabase):
    db.log_query(_make_metric(cache_hit=True))
    db.log_query(_make_metric(cache_hit=True))
    stats = db.get_stats()
    assert stats["cache_hit_rate"] == pytest.approx(100.0)


def test_get_stats_filter_by_index_name(db: MetricsDatabase):
    db.log_query(_make_metric(index_name="idx1"))
    db.log_query(_make_metric(index_name="idx2"))
    stats = db.get_stats(index_name="idx1")
    assert stats["total_queries"] == 1


def test_get_stats_unknown_index_returns_zero(db: MetricsDatabase):
    db.log_query(_make_metric(index_name="idx1"))
    stats = db.get_stats(index_name="nonexistent")
    assert stats["total_queries"] == 0


# ---------------------------------------------------------------------------
# MetricsDatabase — get_percentiles
# ---------------------------------------------------------------------------


def test_get_percentiles_empty_db(db: MetricsDatabase):
    percs = db.get_percentiles()
    assert percs == {"p50": 0.0, "p95": 0.0, "p99": 0.0}


def test_get_percentiles_single_entry(db: MetricsDatabase):
    db.log_query(_make_metric(latency_ms=50.0))
    percs = db.get_percentiles()
    assert percs["p50"] == pytest.approx(50.0)


def test_get_percentiles_multiple_entries(db: MetricsDatabase):
    for i in range(1, 101):
        db.log_query(_make_metric(latency_ms=float(i)))
    percs = db.get_percentiles()
    # p50 should be around the median
    assert 40.0 <= percs["p50"] <= 60.0
    assert percs["p95"] >= percs["p50"]
    assert percs["p99"] >= percs["p95"]


def test_get_percentiles_filter_by_index(db: MetricsDatabase):
    db.log_query(_make_metric(index_name="idx1", latency_ms=5.0))
    db.log_query(_make_metric(index_name="idx2", latency_ms=500.0))
    percs = db.get_percentiles(index_name="idx1")
    assert percs["p50"] == pytest.approx(5.0)
