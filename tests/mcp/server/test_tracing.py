"""Tests for mcp.server.tracing — init_tracing, ensure_request_id, drift_span."""

from __future__ import annotations

import importlib
import uuid
from unittest.mock import MagicMock, patch

import pytest

from mcp.server.tracing import (
    drift_span,
    ensure_request_id,
    init_tracing,
    record_drift_event,
)


# ---------------------------------------------------------------------------
# init_tracing
# ---------------------------------------------------------------------------


def test_init_tracing_no_op_when_no_endpoint(monkeypatch: pytest.MonkeyPatch):
    """Should silently no-op when OTEL_EXPORTER_OTLP_ENDPOINT is not set."""
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)
    # Should not raise
    init_tracing("test-service")


def test_init_tracing_no_op_when_opentelemetry_unavailable(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    with patch("importlib.util.find_spec", return_value=None):
        init_tracing("svc")  # Should not raise


def test_init_tracing_default_service_name(monkeypatch: pytest.MonkeyPatch):
    """Default service name is 'mcp'."""
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)
    init_tracing()  # Should use default "mcp"


# ---------------------------------------------------------------------------
# ensure_request_id
# ---------------------------------------------------------------------------


def _make_mock_request(x_request_id: str | None = None):
    """Create a minimal mock Starlette request."""
    req = MagicMock()
    headers: dict = {}
    if x_request_id is not None:
        headers["x-request-id"] = x_request_id
    req.headers = headers
    req.state = MagicMock()
    return req


def test_ensure_request_id_uses_existing_header():
    req = _make_mock_request("my-request-id")
    rid = ensure_request_id(req)
    assert rid == "my-request-id"
    assert req.state.request_id == "my-request-id"


def test_ensure_request_id_generates_uuid_when_missing():
    req = _make_mock_request()
    rid = ensure_request_id(req)
    # Should be a valid UUID
    parsed = uuid.UUID(rid)
    assert str(parsed) == rid
    assert req.state.request_id == rid


def test_ensure_request_id_generates_unique_ids():
    req1 = _make_mock_request()
    req2 = _make_mock_request()
    rid1 = ensure_request_id(req1)
    rid2 = ensure_request_id(req2)
    assert rid1 != rid2


def test_ensure_request_id_empty_header_generates_new():
    """Empty x-request-id header is treated as missing — generate new UUID."""
    req = _make_mock_request("")
    rid = ensure_request_id(req)
    # Empty string is falsy — should generate UUID
    assert len(rid) > 0


# ---------------------------------------------------------------------------
# drift_span (context manager) — no-op when OTel is unavailable
# ---------------------------------------------------------------------------


def test_drift_span_noop_when_otel_missing():
    """drift_span is a no-op context manager when opentelemetry is unavailable."""
    with patch("importlib.util.find_spec", return_value=None):
        with drift_span(drift_type="data_drift", features=["f1", "f2"]) as span:
            assert span is None


def test_drift_span_noop_yields_none_by_default():
    """Without OTel, drift_span should yield None and not raise."""
    with patch("importlib.util.find_spec", return_value=None):
        result_holder = []
        with drift_span() as span:
            result_holder.append(span)
    assert result_holder[0] is None


def test_drift_span_all_params_noop():
    with patch("importlib.util.find_spec", return_value=None):
        with drift_span(
            tracer_name="test.tracer",
            span_name="test.span",
            drift_type="model_drift",
            features=["age", "income"],
            magnitude=0.5,
            is_critical=True,
            p_value=0.01,
            detector="KSDrift",
            extra_attrs={"custom": "value"},
        ) as span:
            assert span is None


def test_drift_span_import_error_yields_none():
    """If opentelemetry is found but trace module fails, yield None."""
    with patch("importlib.util.find_spec", return_value=MagicMock()):
        with patch("importlib.import_module", side_effect=ImportError("no otel")):
            with drift_span() as span:
                assert span is None


# ---------------------------------------------------------------------------
# record_drift_event — no-op when OTel unavailable
# ---------------------------------------------------------------------------


def test_record_drift_event_noop_when_otel_missing():
    with patch("importlib.util.find_spec", return_value=None):
        # Should not raise
        record_drift_event(
            drift_type="data_drift",
            features=["f1"],
            magnitude=0.3,
        )


def test_record_drift_event_all_params_noop():
    with patch("importlib.util.find_spec", return_value=None):
        record_drift_event(
            drift_type="config_drift",
            features=["param_a", "param_b"],
            magnitude=0.7,
            is_critical=True,
            p_value=0.001,
            detector="PSIDrift",
            extra_attrs={"env": "prod"},
        )


def test_record_drift_event_empty_features_noop():
    with patch("importlib.util.find_spec", return_value=None):
        record_drift_event(drift_type="data_drift", features=[])


def test_record_drift_event_import_error_suppressed():
    with patch("importlib.util.find_spec", return_value=MagicMock()):
        with patch("importlib.import_module", side_effect=Exception("oops")):
            # Should not raise
            record_drift_event(drift_type="data_drift", features=["x"])
