"""Unit tests for the codex_ml.feedback package (Gap 39).

Covers:
 1. FeedbackEvent construction defaults
 2. FeedbackCollector.record + get_recent pagination
 3. FeedbackCollector.aggregate stats
 4. FeedbackLoop.on_alert ingestion (dict + FeedbackEvent)
 5. FeedbackLoop.on_drift ingestion (dict + FeedbackEvent)
 6. FeedbackLoop.should_adapt threshold logic
 7. JSONL file sink
 8. Collector max_memory ring-buffer
"""

from __future__ import annotations

import json
import pathlib

import pytest

from codex_ml.feedback import FeedbackCollector, FeedbackEvent, FeedbackLoop

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def collector() -> FeedbackCollector:
    return FeedbackCollector()


@pytest.fixture()
def loop(collector: FeedbackCollector) -> FeedbackLoop:
    return FeedbackLoop(collector=collector, adapt_threshold=3, adapt_window=10)


# ---------------------------------------------------------------------------
# 1. FeedbackEvent construction
# ---------------------------------------------------------------------------


class TestFeedbackEvent:
    def test_defaults_populated(self) -> None:
        ev = FeedbackEvent(event_type="metric", source="prometheus")
        assert ev.event_type == "metric", "event_type is not valid"
        assert ev.source == "prometheus", "source is not valid"
        assert ev.payload == {}, "payload is not valid"
        assert ev.score is None, "score is not valid"
        # timestamp should be a non-empty ISO string
        assert isinstance(ev.timestamp, str)
        assert len(ev.timestamp) > 10, "Collection must not be empty"
        assert "T" in ev.timestamp, "Condition must be true"

    def test_to_dict_roundtrip(self) -> None:
        ev = FeedbackEvent(
            event_type="alert",
            source="pagerduty",
            payload={"title": "high CPU"},
            score=0.9,
            timestamp="2025-01-01T00:00:00Z",
        )
        d = ev.to_dict()
        assert d["event_type"] == "alert", "Condition must be true"
        assert d["source"] == "pagerduty", "Condition must be true"
        assert d["payload"] == {"title": "high CPU"}, "Condition must be true"
        assert d["score"] == pytest.approx(0.9), "Condition must be true"
        assert d["timestamp"] == "2025-01-01T00:00:00Z", "Condition must be true"

    def test_json_serialisable(self) -> None:
        ev = FeedbackEvent(event_type="drift", source="detector", score=0.3)
        raw = json.dumps(ev.to_dict())
        parsed = json.loads(raw)
        assert parsed["event_type"] == "drift", "Condition must be true"


# ---------------------------------------------------------------------------
# 2. FeedbackCollector — record and get_recent
# ---------------------------------------------------------------------------


class TestFeedbackCollectorRecordAndGetRecent:
    def test_record_increases_length(self, collector: FeedbackCollector) -> None:
        assert len(collector) == 0, "Collector must not be empty"
        collector.record(FeedbackEvent(event_type="metric", source="x"))
        assert len(collector) == 1, "Collector must not be empty"

    def test_get_recent_returns_all_when_fewer_than_n(self, collector: FeedbackCollector) -> None:
        for i in range(5):
            collector.record(FeedbackEvent(event_type="metric", source=f"s{i}"))
        result = collector.get_recent(n=100)
        assert len(result) == 5, "Result must not be empty"

    def test_get_recent_pagination_returns_last_n(self, collector: FeedbackCollector) -> None:
        for i in range(20):
            collector.record(FeedbackEvent(event_type="metric", source=f"s{i}", payload={"i": i}))
        result = collector.get_recent(n=5)
        assert len(result) == 5, "Result must not be empty"
        # Last event should have i=19
        assert result[-1].payload["i"] == 19, "Result must not be empty"
        # First of the returned slice should have i=15
        assert result[0].payload["i"] == 15, "Result must not be empty"

    def test_get_recent_order_newest_last(self, collector: FeedbackCollector) -> None:
        for i in range(10):
            collector.record(FeedbackEvent(event_type="x", source="s", payload={"i": i}))
        result = collector.get_recent(n=10)
        indices = [r.payload["i"] for r in result]
        assert indices == list(range(10)), "indices is not valid"


# ---------------------------------------------------------------------------
# 3. FeedbackCollector — aggregate
# ---------------------------------------------------------------------------


class TestFeedbackCollectorAggregate:
    def test_empty_aggregate(self, collector: FeedbackCollector) -> None:
        stats = collector.aggregate()
        assert stats["total"] == 0, "Condition must be true"
        assert stats["counts_by_type"] == {}, "Count must be greater than zero"
        assert stats["avg_score"] is None, "Condition must be true"

    def test_counts_by_type(self, collector: FeedbackCollector) -> None:
        collector.record(FeedbackEvent(event_type="alert", source="a"))
        collector.record(FeedbackEvent(event_type="alert", source="b"))
        collector.record(FeedbackEvent(event_type="drift", source="c"))
        stats = collector.aggregate()
        assert stats["counts_by_type"]["alert"] == 2, "Count must be greater than zero"
        assert stats["counts_by_type"]["drift"] == 1, "Count must be greater than zero"
        assert stats["total"] == 3, "Condition must be true"

    def test_avg_score_computed(self, collector: FeedbackCollector) -> None:
        collector.record(FeedbackEvent(event_type="alert", source="a", score=0.4))
        collector.record(FeedbackEvent(event_type="alert", source="b", score=0.8))
        # One event without a score — should not affect average
        collector.record(FeedbackEvent(event_type="metric", source="c"))
        stats = collector.aggregate()
        assert stats["avg_score"] == pytest.approx(0.6), "Condition must be true"

    def test_avg_score_none_when_no_scores(self, collector: FeedbackCollector) -> None:
        collector.record(FeedbackEvent(event_type="metric", source="x"))
        stats = collector.aggregate()
        assert stats["avg_score"] is None, "Condition must be true"


# ---------------------------------------------------------------------------
# 4. FeedbackLoop — on_alert
# ---------------------------------------------------------------------------


class TestFeedbackLoopOnAlert:
    def test_on_alert_dict_creates_alert_event(self, loop: FeedbackLoop) -> None:
        loop.on_alert({"severity": "critical", "source": "prometheus", "msg": "CPU"})
        recent = loop.collector.get_recent(n=1)
        assert len(recent) == 1, "Recent must not be empty"
        ev = recent[0]
        assert ev.event_type == "alert", "event_type is not valid"
        assert ev.source == "prometheus", "source is not valid"
        assert ev.score == pytest.approx(1.0), "score is not valid"

    def test_on_alert_warning_score(self, loop: FeedbackLoop) -> None:
        loop.on_alert({"severity": "warning", "source": "grafana"})
        ev = loop.collector.get_recent(n=1)[0]
        assert ev.score == pytest.approx(0.5), "score is not valid"

    def test_on_alert_passthrough_feedback_event(self, loop: FeedbackLoop) -> None:
        original = FeedbackEvent(event_type="alert", source="custom", score=0.7, payload={"k": "v"})
        loop.on_alert(original)
        recent = loop.collector.get_recent(n=1)
        assert recent[0] is original, "Condition must be true"

    def test_on_alert_unknown_object(self, loop: FeedbackLoop) -> None:
        class FakeAlert:
            severity = "info"
            source = "infra"

        loop.on_alert(FakeAlert())
        ev = loop.collector.get_recent(n=1)[0]
        assert ev.event_type == "alert", "event_type is not valid"
        assert ev.score == pytest.approx(0.0), "score is not valid"


# ---------------------------------------------------------------------------
# 5. FeedbackLoop — on_drift
# ---------------------------------------------------------------------------


class TestFeedbackLoopOnDrift:
    def test_on_drift_dict_creates_drift_event(self, loop: FeedbackLoop) -> None:
        loop.on_drift({"drift_score": 0.85, "source": "data_drift_detector"})
        ev = loop.collector.get_recent(n=1)[0]
        assert ev.event_type == "drift", "event_type is not valid"
        assert ev.score == pytest.approx(0.85), "score is not valid"
        assert ev.source == "data_drift_detector", "Data must not be empty"

    def test_on_drift_passthrough_feedback_event(self, loop: FeedbackLoop) -> None:
        original = FeedbackEvent(event_type="drift", source="detector")
        loop.on_drift(original)
        assert loop.collector.get_recent(n=1)[0] is original, "Condition must be true"

    def test_on_drift_no_score_when_missing(self, loop: FeedbackLoop) -> None:
        loop.on_drift({"source": "model_drift_detector"})
        ev = loop.collector.get_recent(n=1)[0]
        assert ev.score is None, "score is not valid"

    def test_on_drift_arbitrary_object(self, loop: FeedbackLoop) -> None:
        class DriftResult:
            drift_score = 0.42
            source = "feature_store"

        loop.on_drift(DriftResult())
        ev = loop.collector.get_recent(n=1)[0]
        assert ev.event_type == "drift", "event_type is not valid"
        assert ev.score == pytest.approx(0.42), "score is not valid"


# ---------------------------------------------------------------------------
# 6. FeedbackLoop — should_adapt threshold logic
# ---------------------------------------------------------------------------


class TestFeedbackLoopShouldAdapt:
    def test_no_events_returns_false(self, loop: FeedbackLoop) -> None:
        assert loop.should_adapt() is False, "Condition must be true"

    def test_below_threshold_returns_false(self, loop: FeedbackLoop) -> None:
        # threshold=3, so ≤3 alerts → False
        for _ in range(3):
            loop.on_alert({"severity": "critical", "source": "prom"})
        assert loop.should_adapt() is False, "Condition must be true"

    def test_above_threshold_returns_true(self, loop: FeedbackLoop) -> None:
        # 4 alerts > threshold of 3 → True
        for _ in range(4):
            loop.on_alert({"severity": "critical", "source": "prom"})
        assert loop.should_adapt() is True, "Condition must be true"

    def test_mixed_types_only_alert_counts(self, loop: FeedbackLoop) -> None:
        # 2 alerts + 3 drifts in window of 10 — alert count (2) ≤ threshold (3)
        for _ in range(2):
            loop.on_alert({"severity": "warning", "source": "prom"})
        for _ in range(3):
            loop.on_drift({"drift_score": 0.5, "source": "detector"})
        assert loop.should_adapt() is False, "Condition must be true"

    def test_window_limits_lookback(self) -> None:
        # window=5, threshold=2: put 4 old alerts then 5 new non-alert events
        small_loop = FeedbackLoop(adapt_threshold=2, adapt_window=5)
        for _ in range(4):
            small_loop.on_alert({"severity": "critical", "source": "prom"})
        # Fill window with non-alert events to push old alerts out
        for _ in range(5):
            small_loop.on_drift({"drift_score": 0.1, "source": "d"})
        # Only the last 5 events are inspected → 0 alerts → False
        assert small_loop.should_adapt() is False, "Condition must be true"

    def test_custom_threshold(self) -> None:
        tight_loop = FeedbackLoop(adapt_threshold=1, adapt_window=5)
        tight_loop.on_alert({"severity": "warning", "source": "x"})
        tight_loop.on_alert({"severity": "warning", "source": "x"})
        # 2 alerts > threshold 1 → True
        assert tight_loop.should_adapt() is True, "Condition must be true"


# ---------------------------------------------------------------------------
# 7. JSONL file sink
# ---------------------------------------------------------------------------


class TestFeedbackCollectorJSONLSink:
    def test_sink_writes_jsonl(self, tmp_path: pathlib.Path) -> None:
        sink = tmp_path / "events.jsonl"
        col = FeedbackCollector(sink_path=sink)
        col.record(FeedbackEvent(event_type="alert", source="s1", score=1.0))
        col.record(FeedbackEvent(event_type="drift", source="s2"))
        lines = sink.read_text().splitlines()
        assert len(lines) == 2, "Lines must not be empty"
        first = json.loads(lines[0])
        assert first["event_type"] == "alert", "Condition must be true"
        assert first["score"] == pytest.approx(1.0), "Condition must be true"
        second = json.loads(lines[1])
        assert second["event_type"] == "drift", "Condition must be true"


# ---------------------------------------------------------------------------
# 8. Ring-buffer max_memory
# ---------------------------------------------------------------------------


class TestFeedbackCollectorMaxMemory:
    def test_max_memory_drops_oldest(self) -> None:
        col = FeedbackCollector(max_memory=5)
        for i in range(10):
            col.record(FeedbackEvent(event_type="x", source="s", payload={"i": i}))
        assert len(col) == 5, "Col must not be empty"
        # Oldest (i=0..4) should be gone; newest (i=5..9) retained
        indices = [ev.payload["i"] for ev in col.get_recent(n=100)]
        assert indices == [5, 6, 7, 8, 9]
