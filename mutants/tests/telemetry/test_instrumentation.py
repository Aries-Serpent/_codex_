"""
Test Instrumentation

Test module for instrumentation.
"""

from codex_ml.telemetry import REQUEST_LATENCY, track_time


def dummy():
    pass


def _get_histogram_count(histogram):
    """Get observation count using the stable prometheus_client public API."""
    if histogram is None:
        return 0
    for metric_family in histogram.collect():
        for sample in metric_family.samples:
            if sample.name.endswith("_count"):
                return int(sample.value)
    return 0


def test_track_time_records_histogram():
    wrapped = track_time(REQUEST_LATENCY)(dummy)
    count_before = _get_histogram_count(REQUEST_LATENCY)
    wrapped()
    count_after = _get_histogram_count(REQUEST_LATENCY)

    if REQUEST_LATENCY:
        assert count_after == count_before + 1, "Count must be greater than zero"
