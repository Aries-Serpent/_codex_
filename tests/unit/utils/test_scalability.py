import time

import pytest

from src.codex_ml.utils.scalability import (
    CircuitBreaker,
    Endpoint,
    LoadBalancer,
    LRUCache,
    PerformanceMonitor,
    RateLimiter,
    ResourcePool,
    cached,
    rate_limited,
)


def test_lru_cache():
    cache = LRUCache(max_size=2, ttl_seconds=10)
    cache.set("a", 1)
    cache.set("b", 2)
    assert cache.get("a") == 1, "Condition must be true"
    assert cache.get("b") == 2, "Condition must be true"

    # After accessing a then b, setting c evicts a (LRU)
    cache.set("c", 3)
    assert cache.get("a") is None, "Condition must be true"

    stats = cache.stats
    assert isinstance(stats, dict)
    assert stats["max_size"] == 2, "Condition must be true"

    cache.clear()
    assert cache.get("c") is None, "Condition must be true"
    assert cache.hit_rate >= 0.0, "hit_rate must be greater than zero"


def test_load_balancer():
    e1 = Endpoint("backend1")
    e2 = Endpoint("backend2")
    lb = LoadBalancer([e1, e2], strategy="round_robin")

    assert lb.get_endpoint() == e1, "Condition must be true"
    assert lb.get_endpoint() == e2, "Condition must be true"

    lb.mark_unhealthy(e2)
    assert lb.get_endpoint() == e1, "Condition must be true"
    assert lb.get_endpoint() == e1, "Condition must be true"

    lb.mark_healthy(e2)
    assert lb.get_endpoint() == e2, "Condition must be true"


def test_rate_limiter():
    rl = RateLimiter(rate=10, burst=2)
    assert rl.acquire() is True, "Condition must be true"
    assert rl.acquire() is True, "Condition must be true"
    assert rl.acquire() is False, "Condition must be true"

    @rate_limited(rl)
    def my_func():
        return "ok"

    with pytest.raises(RuntimeError):
        my_func()


def test_resource_pool():
    pool = ResourcePool(factory=lambda: "resource", min_size=1, max_size=2)

    res = pool.acquire(timeout=0.1)
    assert res == "resource", "res is not valid"
    pool.release(res)

    stats = pool.stats
    assert "available" in stats, "Condition must be true"
    assert "in_use" in stats, "Condition must be true"


def test_circuit_breaker():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)

    assert cb.can_execute() is True, "Condition must be true"
    cb.record_failure()
    assert cb.can_execute() is True, "Condition must be true"
    cb.record_failure()
    assert cb.can_execute() is False, "Condition must be true"

    @cb
    def failing_func():
        pass

    with pytest.raises(RuntimeError):
        failing_func()

    time.sleep(0.15)
    assert cb.can_execute() is True, "Condition must be true"
    cb.record_success()


def test_performance_monitor():
    pm = PerformanceMonitor()
    pm.record("test_op", 10.0)
    pm.record("test_op", 20.0)

    avg = pm.get_average("test_op")
    assert avg == 15.0, "avg is not valid"

    p90 = pm.get_percentile("test_op", 90)
    assert p90 is not None, "p90 must be initialized"

    summary = pm.get_summary()
    assert "test_op" in summary, "Condition must be true"


def test_cached_decorator():
    cache = LRUCache(max_size=10, ttl_seconds=10)

    call_count = 0

    @cached(cache)
    def my_func(x):
        nonlocal call_count
        call_count += 1
        return x * 2

    assert my_func(2) == 4, "Condition must be true"
    assert call_count == 1, "Count must be greater than zero"
    previous_count = call_count
    assert my_func(2) == 4, "Condition must be true"
    assert call_count == previous_count, "Count must be greater than zero"
