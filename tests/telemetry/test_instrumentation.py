
from codex_ml.telemetry import REQUEST_LATENCY, track_time


def dummy():
    pass


def test_track_time_records_histogram():
    wrapped = track_time(REQUEST_LATENCY)(dummy)
    count_before = REQUEST_LATENCY.count if REQUEST_LATENCY else 0
    wrapped()
    count_after = REQUEST_LATENCY.count if REQUEST_LATENCY else 0
    assert count_after == count_before + 1 if REQUEST_LATENCY else True
