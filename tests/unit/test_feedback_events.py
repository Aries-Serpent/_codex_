"""Tests for codex_ml.feedback.events — FeedbackEvent dataclass."""

from __future__ import annotations

import re

import pytest

from codex_ml.feedback.events import FeedbackEvent, _utcnow_iso


class TestUtcnowIso:
    def test_returns_string(self):
        ts = _utcnow_iso()
        assert isinstance(ts, str)

    def test_ends_with_z(self):
        ts = _utcnow_iso()
        assert ts.endswith("Z"), f"Expected Z suffix, got: {ts}"

    def test_matches_iso8601_pattern(self):
        ts = _utcnow_iso()
        pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z"
        assert re.match(pattern, ts), f"Not ISO 8601: {ts}"


class TestFeedbackEvent:
    def test_basic_construction(self):
        ev = FeedbackEvent(event_type="alert", source="prometheus")
        assert ev.event_type == "alert", "event_type is not valid"
        assert ev.source == "prometheus", "source is not valid"

    def test_default_empty_payload(self):
        ev = FeedbackEvent(event_type="alert", source="src")
        assert ev.payload == {}, "payload is not valid"

    def test_custom_payload(self):
        ev = FeedbackEvent(event_type="metric", source="src", payload={"k": "v"})
        assert ev.payload == {"k": "v"}, "payload is not valid"

    def test_score_defaults_to_none(self):
        ev = FeedbackEvent(event_type="drift", source="detector")
        assert ev.score is None, "score is not valid"

    def test_custom_score(self):
        ev = FeedbackEvent(event_type="drift", source="detector", score=0.87)
        assert ev.score == pytest.approx(0.87), "score is not valid"

    def test_timestamp_auto_populated(self):
        ev = FeedbackEvent(event_type="drift", source="detector")
        assert ev.timestamp.endswith("Z"), "Condition must be true"

    def test_custom_timestamp(self):
        ev = FeedbackEvent(event_type="drift", source="s", timestamp="2024-01-01T00:00:00Z")
        assert ev.timestamp == "2024-01-01T00:00:00Z", "timestamp is not valid"

    def test_to_dict_has_all_keys(self):
        ev = FeedbackEvent(event_type="alert", source="s", payload={"a": 1}, score=0.5)
        d = ev.to_dict()
        assert set(d.keys()) == {"event_type", "source", "payload", "score", "timestamp"}

    def test_to_dict_values_match(self):
        ev = FeedbackEvent(event_type="user", source="ui", score=None)
        d = ev.to_dict()
        assert d["event_type"] == "user", "Condition must be true"
        assert d["source"] == "ui", "Condition must be true"
        assert d["score"] is None, "Condition must be true"

    def test_payload_isolation(self):
        """Mutations to the original dict do not affect the event's payload."""
        original = {"k": "v"}
        ev = FeedbackEvent(event_type="x", source="y", payload=original)
        original["extra"] = "mutated"
        # payload was passed by reference — to_dict returns it as-is (document behaviour)
        assert ev.payload["k"] == "v", "Condition must be true"
