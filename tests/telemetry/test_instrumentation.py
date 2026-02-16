"""
Test Instrumentation

Test module for instrumentation.
"""

from codex_ml.telemetry import REQUEST_LATENCY, track_time


def dummy():
    pass


def test_track_time_records_histogram():
    wrapped = track_time(REQUEST_LATENCY)(dummy)
    # Prometheus Histogram count is accessed via _value.get() for the count metric
    count_before = REQUEST_LATENCY._value.get() if REQUEST_LATENCY and hasattr(REQUEST_LATENCY, '_value') else 0
    wrapped()
    count_after = REQUEST_LATENCY._value.get() if REQUEST_LATENCY and hasattr(REQUEST_LATENCY, '_value') else 0
    assert count_after == count_before + 1 if REQUEST_LATENCY else True
