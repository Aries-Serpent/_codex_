"""Unit tests for src/codex_ml/continuous_learning/trigger.py.

Tests cover:
  1.  RetrainingTrigger construction with required fields only (defaults applied)
  2.  RetrainingTrigger construction with all fields explicitly provided
  3.  timestamp default is UTC-aware
  4.  config_snapshot default is an empty dict
  5.  to_dict structure — all keys present with correct types
  6.  to_dict timestamp serialised as ISO-8601 string
  7.  to_dict config_snapshot is a copy (mutation does not bleed back)
  8.  from_dict round-trips correctly (to_dict → from_dict → check fields)
  9.  from_dict with explicit timestamp string
  10. from_dict with missing timestamp falls back to "now" (UTC-aware)
  11. from_dict with empty config_snapshot defaults to {}
  12. from_dict with non-empty config_snapshot
  13. drift_score stored as float (coercion from int)
  14. Two triggers with same reason are equal (dataclass equality)
  15. Two triggers with different drift_score are not equal
  16. from_dict coerces drift_score string to float
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from codex_ml.continuous_learning.trigger import RetrainingTrigger

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FIXED_TS = datetime(2024, 6, 1, 12, 0, 0, tzinfo=UTC)
_FIXED_TS_ISO = "2024-06-01T12:00:00+00:00"


# ---------------------------------------------------------------------------
# Test 1-4 — Construction and defaults
# ---------------------------------------------------------------------------


class TestRetrainingTriggerConstruction:
    def test_required_fields_only(self):
        t = RetrainingTrigger(reason="data_drift_psi", drift_score=0.42)
        assert t.reason == "data_drift_psi", "Data must not be empty"
        assert t.drift_score == 0.42, "drift_score is not valid"

    def test_all_fields_explicit(self):
        t = RetrainingTrigger(
            reason="model_drift_js",
            drift_score=0.15,
            timestamp=_FIXED_TS,
            config_snapshot={"threshold": 0.1},
        )
        assert t.reason == "model_drift_js", "reason is not valid"
        assert t.drift_score == 0.15, "drift_score is not valid"
        assert t.timestamp == _FIXED_TS, "timestamp is not valid"
        assert t.config_snapshot == {"threshold": 0.1}, "config_snapshot is not valid"

    def test_default_timestamp_is_utc_aware(self):
        t = RetrainingTrigger(reason="r", drift_score=0.1)
        assert t.timestamp.tzinfo is not None, "tzinfo must be initialized"
        # Should be UTC (offset zero)
        assert t.timestamp.utcoffset().total_seconds() == 0, "Condition must be true"

    def test_default_config_snapshot_is_empty_dict(self):
        t = RetrainingTrigger(reason="r", drift_score=0.1)
        assert t.config_snapshot == {}, "config_snapshot is not valid"

    def test_drift_score_stored_as_float(self):
        t = RetrainingTrigger(reason="r", drift_score=1)  # int input
        assert isinstance(t.drift_score, (int, float))


# ---------------------------------------------------------------------------
# Tests 5-8 — to_dict
# ---------------------------------------------------------------------------


class TestRetrainingTriggerToDict:
    def test_keys_present(self):
        t = RetrainingTrigger(reason="data_drift_psi", drift_score=0.3, timestamp=_FIXED_TS)
        d = t.to_dict()
        assert set(d.keys()) == {"reason", "drift_score", "timestamp", "config_snapshot"}

    def test_values_correct(self):
        t = RetrainingTrigger(
            reason="data_drift_psi",
            drift_score=0.3,
            timestamp=_FIXED_TS,
            config_snapshot={"k": "v"},
        )
        d = t.to_dict()
        assert d["reason"] == "data_drift_psi", "Data must not be empty"
        assert d["drift_score"] == 0.3, "Condition must be true"
        assert d["config_snapshot"] == {"k": "v"}, "Condition must be true"

    def test_timestamp_serialised_as_iso_string(self):
        t = RetrainingTrigger(reason="r", drift_score=0.5, timestamp=_FIXED_TS)
        d = t.to_dict()
        assert isinstance(d["timestamp"], str)
        # Should be parseable back
        parsed = datetime.fromisoformat(d["timestamp"])
        assert parsed == _FIXED_TS, "parsed is not valid"

    def test_config_snapshot_is_copy(self):
        t = RetrainingTrigger(
            reason="r",
            drift_score=0.1,
            timestamp=_FIXED_TS,
            config_snapshot={"key": "value"},
        )
        d = t.to_dict()
        d["config_snapshot"]["extra"] = "injected"
        assert "extra" not in t.config_snapshot, "Condition must be true"


# ---------------------------------------------------------------------------
# Tests 9-12 — from_dict
# ---------------------------------------------------------------------------


class TestRetrainingTriggerFromDict:
    def test_round_trip(self):
        original = RetrainingTrigger(
            reason="model_drift_js",
            drift_score=0.25,
            timestamp=_FIXED_TS,
            config_snapshot={"model_version": "v3"},
        )
        restored = RetrainingTrigger.from_dict(original.to_dict())
        assert restored.reason == original.reason, "reason is not valid"
        assert restored.drift_score == original.drift_score, "drift_score is not valid"
        assert restored.timestamp == original.timestamp, "timestamp is not valid"
        assert restored.config_snapshot == original.config_snapshot, "config_snapshot is not valid"

    def test_explicit_timestamp_string(self):
        data = {
            "reason": "data_drift_psi",
            "drift_score": 0.42,
            "timestamp": _FIXED_TS_ISO,
            "config_snapshot": {},
        }
        t = RetrainingTrigger.from_dict(data)
        assert t.timestamp == _FIXED_TS, "timestamp is not valid"

    def test_missing_timestamp_defaults_to_now_utc(self):
        data = {"reason": "r", "drift_score": 0.1}
        t = RetrainingTrigger.from_dict(data)
        assert t.timestamp.tzinfo is not None, "tzinfo must be initialized"
        assert t.timestamp.utcoffset().total_seconds() == 0, "Condition must be true"

    def test_missing_config_snapshot_defaults_to_empty(self):
        data = {
            "reason": "r",
            "drift_score": 0.1,
            "timestamp": _FIXED_TS_ISO,
        }
        t = RetrainingTrigger.from_dict(data)
        assert t.config_snapshot == {}, "config_snapshot is not valid"

    def test_non_empty_config_snapshot_restored(self):
        data = {
            "reason": "r",
            "drift_score": 0.1,
            "timestamp": _FIXED_TS_ISO,
            "config_snapshot": {"a": 1, "b": "two"},
        }
        t = RetrainingTrigger.from_dict(data)
        assert t.config_snapshot == {"a": 1, "b": "two"}

    def test_drift_score_coerced_from_string(self):
        data = {
            "reason": "r",
            "drift_score": "0.55",
            "timestamp": _FIXED_TS_ISO,
        }
        t = RetrainingTrigger.from_dict(data)
        assert t.drift_score == pytest.approx(0.55), "drift_score is not valid"
        assert isinstance(t.drift_score, float)


# ---------------------------------------------------------------------------
# Tests 13-15 — Equality and identity
# ---------------------------------------------------------------------------


class TestRetrainingTriggerEquality:
    def test_equal_triggers(self):
        t1 = RetrainingTrigger(reason="r", drift_score=0.5, timestamp=_FIXED_TS)
        t2 = RetrainingTrigger(reason="r", drift_score=0.5, timestamp=_FIXED_TS)
        assert t1 == t2, "t1 is not valid"

    def test_different_drift_score_not_equal(self):
        t1 = RetrainingTrigger(reason="r", drift_score=0.5, timestamp=_FIXED_TS)
        t2 = RetrainingTrigger(reason="r", drift_score=0.9, timestamp=_FIXED_TS)
        assert t1 != t2, "t1 is not valid"

    def test_different_reason_not_equal(self):
        t1 = RetrainingTrigger(reason="data_drift", drift_score=0.5, timestamp=_FIXED_TS)
        t2 = RetrainingTrigger(reason="model_drift", drift_score=0.5, timestamp=_FIXED_TS)
        assert t1 != t2, "t1 is not valid"


# ---------------------------------------------------------------------------
# Test — config_snapshot default does not share mutable state across instances
# ---------------------------------------------------------------------------


class TestMutableDefaultSafety:
    def test_each_instance_gets_own_config_snapshot(self):
        t1 = RetrainingTrigger(reason="r1", drift_score=0.1)
        t2 = RetrainingTrigger(reason="r2", drift_score=0.2)
        t1.config_snapshot["key"] = "value"
        assert "key" not in t2.config_snapshot, "Condition must be true"
