"""Tests for src/codex/cognitive/objective_analyzer.py — Phase 2 gap-fill.

Covers MetricType, TrendDirection, AlertSeverity, MetricValue, MetricThreshold,
MetricAlert, TrendAnalysis, MetricStore, TrendAnalyzer, and AnomalyDetector.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from codex.cognitive.objective_analyzer import (
    AlertSeverity,
    AnomalyDetector,
    MetricStore,
    MetricThreshold,
    MetricType,
    MetricValue,
    TrendAnalyzer,
    TrendDirection,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_metric(
    value: float,
    metric_type: MetricType = MetricType.COVERAGE,
    offset_days: float = 0.0,
) -> MetricValue:
    """Factory for MetricValue with a UTC timestamp."""
    ts = datetime.now(timezone.utc) - timedelta(days=offset_days)
    return MetricValue(metric_type=metric_type, value=value, timestamp=ts)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class TestEnums:
    def test_metric_types(self) -> None:
        assert MetricType.COVERAGE.value == "coverage"
        assert MetricType.SECURITY.value == "security"
        assert MetricType.CI_CD.value == "ci_cd"

    def test_trend_directions(self) -> None:
        assert TrendDirection.IMPROVING.value == "improving"
        assert TrendDirection.DEGRADING.value == "degrading"
        assert TrendDirection.STABLE.value == "stable"

    def test_alert_severities(self) -> None:
        assert AlertSeverity.INFO.value == "info"
        assert AlertSeverity.WARNING.value == "warning"
        assert AlertSeverity.CRITICAL.value == "critical"


# ---------------------------------------------------------------------------
# MetricValue
# ---------------------------------------------------------------------------


class TestMetricValue:
    def test_to_dict_roundtrip(self) -> None:
        now = datetime.now(timezone.utc)
        mv = MetricValue(
            metric_type=MetricType.COVERAGE,
            value=82.5,
            timestamp=now,
            context={"source": "pytest"},
        )
        d = mv.to_dict()
        assert d["metric_type"] == "coverage"
        assert d["value"] == 82.5
        assert d["context"] == {"source": "pytest"}

        # Round-trip via from_dict
        mv2 = MetricValue.from_dict(d)
        assert mv2.metric_type == MetricType.COVERAGE
        assert mv2.value == pytest.approx(82.5)
        assert mv2.context == {"source": "pytest"}

    def test_default_context_empty(self) -> None:
        mv = _make_metric(75.0)
        assert mv.context == {}


# ---------------------------------------------------------------------------
# MetricThreshold
# ---------------------------------------------------------------------------


class TestMetricThreshold:
    @pytest.fixture()
    def gte_threshold(self) -> MetricThreshold:
        return MetricThreshold(
            metric_type=MetricType.COVERAGE,
            target=80.0,
            warning_threshold=70.0,
            critical_threshold=60.0,
            comparison="gte",
        )

    @pytest.fixture()
    def lte_threshold(self) -> MetricThreshold:
        return MetricThreshold(
            metric_type=MetricType.SECURITY,
            target=0.0,
            warning_threshold=3.0,
            critical_threshold=10.0,
            comparison="lte",
        )

    def test_gte_above_target_ok(self, gte_threshold: MetricThreshold) -> None:
        ok, severity = gte_threshold.check_value(85.0)
        assert ok is True
        assert severity is None

    def test_gte_at_target_ok(self, gte_threshold: MetricThreshold) -> None:
        ok, severity = gte_threshold.check_value(80.0)
        assert ok is True

    def test_gte_warning_zone(self, gte_threshold: MetricThreshold) -> None:
        ok, severity = gte_threshold.check_value(72.0)
        assert ok is False
        assert severity == AlertSeverity.WARNING

    def test_gte_critical_zone(self, gte_threshold: MetricThreshold) -> None:
        ok, severity = gte_threshold.check_value(55.0)
        assert ok is False
        assert severity == AlertSeverity.CRITICAL

    def test_lte_at_or_below_target_ok(self, lte_threshold: MetricThreshold) -> None:
        ok, severity = lte_threshold.check_value(0.0)
        assert ok is True
        assert severity is None

    def test_lte_warning_zone(self, lte_threshold: MetricThreshold) -> None:
        ok, severity = lte_threshold.check_value(2.0)
        assert ok is False
        assert severity == AlertSeverity.WARNING

    def test_lte_critical_zone(self, lte_threshold: MetricThreshold) -> None:
        ok, severity = lte_threshold.check_value(15.0)
        assert ok is False
        assert severity == AlertSeverity.CRITICAL


# ---------------------------------------------------------------------------
# MetricStore
# ---------------------------------------------------------------------------


class TestMetricStore:
    @pytest.fixture()
    def store(self, tmp_path: Path) -> MetricStore:
        return MetricStore(store_path=tmp_path / "metrics.json")

    def test_add_and_get_latest(self, store: MetricStore) -> None:
        mv = _make_metric(80.0, MetricType.COVERAGE)
        store.add_metric(mv)
        latest = store.get_latest(MetricType.COVERAGE)
        assert latest is not None
        assert latest.value == pytest.approx(80.0)

    def test_get_latest_empty_store(self, store: MetricStore) -> None:
        assert store.get_latest(MetricType.COVERAGE) is None

    def test_get_metrics_within_period(self, store: MetricStore) -> None:
        old = _make_metric(60.0, MetricType.COVERAGE, offset_days=40)
        recent = _make_metric(80.0, MetricType.COVERAGE, offset_days=2)
        store.add_metric(old)
        store.add_metric(recent)
        # Default 30-day window should include recent but not old
        metrics_30 = store.get_metrics(MetricType.COVERAGE, days=30)
        assert any(m.value == pytest.approx(80.0) for m in metrics_30)
        assert all(m.value != pytest.approx(60.0) for m in metrics_30)

    def test_add_multiple_types(self, store: MetricStore) -> None:
        store.add_metric(_make_metric(90.0, MetricType.CI_CD))
        store.add_metric(_make_metric(2.0, MetricType.SECURITY))
        assert store.get_latest(MetricType.CI_CD) is not None
        assert store.get_latest(MetricType.SECURITY) is not None

    def test_persistence(self, tmp_path: Path) -> None:
        path = tmp_path / "metrics.json"
        store1 = MetricStore(store_path=path)
        store1.add_metric(_make_metric(77.0, MetricType.COVERAGE))
        store1._save()

        store2 = MetricStore(store_path=path)
        assert store2.get_latest(MetricType.COVERAGE) is not None


# ---------------------------------------------------------------------------
# TrendAnalyzer
# ---------------------------------------------------------------------------


class TestTrendAnalyzer:
    @pytest.fixture()
    def analyzer(self) -> TrendAnalyzer:
        return TrendAnalyzer(min_data_points=3)

    def _make_series(
        self, values: list[float], spacing_days: float = 1.0
    ) -> list[MetricValue]:
        base = datetime.now(timezone.utc)
        return [
            MetricValue(
                metric_type=MetricType.COVERAGE,
                value=v,
                timestamp=base - timedelta(days=(len(values) - i - 1) * spacing_days),
            )
            for i, v in enumerate(values)
        ]

    def test_too_few_points_returns_none(self, analyzer: TrendAnalyzer) -> None:
        metrics = self._make_series([70.0, 75.0])  # only 2 — below min 3
        result = analyzer.analyze(metrics)
        assert result is None

    def test_improving_trend(self, analyzer: TrendAnalyzer) -> None:
        metrics = self._make_series([60.0, 70.0, 80.0, 85.0])
        result = analyzer.analyze(metrics)
        assert result is not None
        assert result.direction == TrendDirection.IMPROVING
        assert result.slope > 0

    def test_degrading_trend(self, analyzer: TrendAnalyzer) -> None:
        metrics = self._make_series([85.0, 75.0, 65.0, 55.0])
        result = analyzer.analyze(metrics)
        assert result is not None
        assert result.direction == TrendDirection.DEGRADING
        assert result.slope < 0

    def test_stable_trend(self, analyzer: TrendAnalyzer) -> None:
        metrics = self._make_series([80.0, 80.0, 80.0, 80.0])
        result = analyzer.analyze(metrics)
        assert result is not None
        assert result.direction == TrendDirection.STABLE

    def test_result_fields_populated(self, analyzer: TrendAnalyzer) -> None:
        metrics = self._make_series([70.0, 75.0, 80.0])
        result = analyzer.analyze(metrics)
        assert result is not None
        assert result.data_points == 3
        assert result.start_value == pytest.approx(70.0)
        assert result.end_value == pytest.approx(80.0)
        assert isinstance(result.r_squared, float)

    def test_to_dict(self, analyzer: TrendAnalyzer) -> None:
        metrics = self._make_series([70.0, 75.0, 80.0])
        result = analyzer.analyze(metrics)
        assert result is not None
        d = result.to_dict()
        assert "direction" in d
        assert "slope" in d
        assert "data_points" in d


# ---------------------------------------------------------------------------
# AnomalyDetector
# ---------------------------------------------------------------------------


class TestAnomalyDetector:
    @pytest.fixture()
    def detector(self) -> AnomalyDetector:
        return AnomalyDetector(z_threshold=2.0)

    def _make_series_with_spike(self) -> list[MetricValue]:
        base_ts = datetime.now(timezone.utc)
        # Series: 9 normal values around 80, one extreme outlier (200)
        values = [80.0] * 9 + [200.0]
        return [
            MetricValue(
                metric_type=MetricType.COVERAGE,
                value=v,
                timestamp=base_ts - timedelta(hours=len(values) - i),
            )
            for i, v in enumerate(values)
        ]

    def test_detects_spike(self, detector: AnomalyDetector) -> None:
        metrics = self._make_series_with_spike()
        anomalies = detector.detect(metrics)
        assert len(anomalies) >= 1
        assert any(m.value == pytest.approx(200.0) for m in anomalies)

    def test_no_anomaly_uniform_series(self, detector: AnomalyDetector) -> None:
        base_ts = datetime.now(timezone.utc)
        metrics = [
            MetricValue(
                metric_type=MetricType.COVERAGE,
                value=80.0,
                timestamp=base_ts - timedelta(hours=i),
            )
            for i in range(10)
        ]
        anomalies = detector.detect(metrics)
        assert anomalies == []

    def test_empty_short_series(self, detector: AnomalyDetector) -> None:
        base_ts = datetime.now(timezone.utc)
        metrics = [
            MetricValue(
                metric_type=MetricType.COVERAGE,
                value=80.0,
                timestamp=base_ts,
            )
        ]
        # Fewer than 3 points → no anomalies
        assert detector.detect(metrics) == []

    def test_returns_metric_values(self, detector: AnomalyDetector) -> None:
        metrics = self._make_series_with_spike()
        anomalies = detector.detect(metrics)
        for a in anomalies:
            assert isinstance(a, MetricValue)
