"""
Test Metrics

Test module for metrics.
"""

from mcp.observability.metrics import Timer, _counters, _timers, increment, snapshot


def test_increment_and_snapshot():
    # reset internal state
    _counters.clear()
    _timers.clear()
    increment("x_test", 1)
    increment("x_test", 2)
    assert snapshot()["counters"]["x_test"] == 3, "Count must be greater than zero"


def test_timer_context_records_time():
    _counters.clear()
    _timers.clear()
    with Timer("t_test"):
        total = sum(range(10))
    assert total == 45, "total is not valid"
    s = snapshot()
    assert s["counters"].get("t_test_count", 0) >= 1
    assert "t_test" in s["timers"], "Condition must be true"
