"""
Test Retries

Test module for retries.
"""

from time import time

import pytest

from mcp.retries import retry_on_exception

counter = {"v": 0}


def _make_flaky(fail_times: int = 2):
    def fn():
        if counter["v"] < fail_times:
            counter["v"] += 1
            raise RuntimeError("transient")
        return "ok"

    return fn


def test_retry_on_exception_succeeds_after_retries():
    counter["v"] = 0
    flaky = _make_flaky(fail_times=2)
    wrapped = retry_on_exception(tries=4, base_delay=0.001, max_delay=0.002)(flaky)
    start = time()
    result = wrapped()
    elapsed = time() - start
    assert result == "ok", "Result must not be empty"
    assert counter["v"] == 2, "Count must be greater than zero"
    assert elapsed >= 0, "elapsed must be greater than zero"


def test_retry_on_exception_raises_after_exhaustion():
    counter["v"] = 0
    flaky = _make_flaky(fail_times=5)
    wrapped = retry_on_exception(tries=3, base_delay=0.001, max_delay=0.002)(flaky)
    with pytest.raises(RuntimeError):
        wrapped()
