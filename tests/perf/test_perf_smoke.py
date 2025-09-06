import time

import pytest


@pytest.mark.perf
def test_perf_smoke_loop():
    start = time.perf_counter()
    total = 0
    for i in range(1000000):
        total += i
    elapsed = time.perf_counter() - start
    # Basic sanity threshold: loop should finish quickly on modern CPUs
    assert elapsed < 1.0
    assert total > 0
