"""Unit tests for codex_ml.utils.scalability (Gap 5).

Covers all public APIs:
- LRUCache: get/set/clear, TTL expiry, LRU eviction, hit_rate, stats
- cached decorator: key_func=None and custom key_func, cache hit short-circuits call
- RateLimiter: acquire (success / exhausted), wait_for_token (success / timeout)
- rate_limited decorator: passes-through on token available, raises RuntimeError when exhausted
- CircuitBreaker: initial state, record_success, record_failure, open/close/half-open
  transitions, decorator usage (__call__), RuntimeError when open
- Endpoint: dataclass default values
- LoadBalancer: round_robin, least_connections, weighted, no healthy endpoints,
  mark_healthy/unhealthy, unknown strategy fallback
- ResourcePool: acquire from pre-populated pool, create new resource, release, stats,
  timeout when exhausted
- MetricPoint: dataclass default timestamp/tags
- PerformanceMonitor: record, get_average (windowed), get_percentile, get_summary,
  timed decorator, capped at 1000 points
"""

from __future__ import annotations

import threading
import time

import pytest

from codex_ml.utils.scalability import (
    CircuitBreaker,
    Endpoint,
    LoadBalancer,
    LRUCache,
    MetricPoint,
    PerformanceMonitor,
    RateLimiter,
    ResourcePool,
    cached,
    rate_limited,
)

# ---------------------------------------------------------------------------
# LRUCache
# ---------------------------------------------------------------------------


class TestLRUCache:
    def test_get_miss_returns_none(self):
        cache = LRUCache()
        assert cache.get("missing") is None, "Condition must be true"

    def test_set_and_get(self):
        cache = LRUCache()
        cache.set("k", "v")
        assert cache.get("k") == "v", "Condition must be true"

    def test_get_increments_hits(self):
        cache = LRUCache()
        cache.set("k", 42)
        cache.get("k")
        assert cache._hits == 1, "_hits is not valid"
        assert cache._misses == 0, "_misses is not valid"

    def test_miss_increments_misses(self):
        cache = LRUCache()
        cache.get("no-key")
        assert cache._misses == 1, "_misses is not valid"
        assert cache._hits == 0, "_hits is not valid"

    def test_hit_rate_no_accesses(self):
        cache = LRUCache()
        assert cache.hit_rate == 0.0, "hit_rate is not valid"

    def test_hit_rate_all_hits(self):
        cache = LRUCache()
        cache.set("k", 1)
        cache.get("k")
        cache.get("k")
        assert cache.hit_rate == 1.0, "hit_rate is not valid"

    def test_hit_rate_mixed(self):
        cache = LRUCache()
        cache.set("k", 1)
        cache.get("k")  # hit
        cache.get("x")  # miss
        assert cache.hit_rate == 0.5, "hit_rate is not valid"

    def test_ttl_expiry_returns_none(self):
        cache = LRUCache(ttl_seconds=0.05)
        cache.set("k", "val")
        time.sleep(0.1)
        assert cache.get("k") is None, "Condition must be true"

    def test_ttl_expiry_removes_key(self):
        cache = LRUCache(ttl_seconds=0.05)
        cache.set("k", "val")
        time.sleep(0.1)
        cache.get("k")
        assert "k" not in cache._cache, "Condition must be true"

    def test_lru_eviction(self):
        cache = LRUCache(max_size=2)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.get("a")  # make "a" most recently used
        cache.set("c", 3)  # should evict "b" (LRU)
        assert cache.get("b") is None, "Condition must be true"
        assert cache.get("a") == 1, "Condition must be true"
        assert cache.get("c") == 3, "Condition must be true"

    def test_update_existing_key(self):
        cache = LRUCache()
        cache.set("k", "old")
        cache.set("k", "new")
        assert cache.get("k") == "new", "Condition must be true"

    def test_clear(self):
        cache = LRUCache()
        cache.set("a", 1)
        cache.set("b", 2)
        cache.clear()
        assert len(cache._cache) == 0, "Collection must not be empty"
        assert len(cache._access_order) == 0, "Collection must not be empty"

    def test_stats_structure(self):
        cache = LRUCache(max_size=50)
        cache.set("k", 1)
        cache.get("k")
        cache.get("miss")
        s = cache.stats
        assert s["size"] == 1, "Condition must be true"
        assert s["max_size"] == 50, "Condition must be true"
        assert s["hits"] == 1, "Condition must be true"
        assert s["misses"] == 1, "Condition must be true"
        assert s["hit_rate"] == 0.5, "Condition must be true"

    def test_thread_safety_concurrent_set_get(self):
        cache = LRUCache(max_size=200)
        errors = []

        def worker(i):
            try:
                cache.set(f"k{i}", i)
                cache.get(f"k{i}")
            except Exception as exc:  # pragma: no cover
                errors.append(exc)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert errors == [], "Error should be raised or set"


# ---------------------------------------------------------------------------
# cached decorator
# ---------------------------------------------------------------------------


class TestCachedDecorator:
    def test_caches_result_on_second_call(self):
        cache = LRUCache()
        call_count = 0

        @cached(cache)
        def expensive(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        assert expensive(5) == 10, "Condition must be true"
        assert expensive(5) == 10, "Condition must be true"
        assert call_count == 1, "Count must be greater than zero"

    def test_different_args_separate_cache_entries(self):
        cache = LRUCache()
        call_count = 0

        @cached(cache)
        def fn(x):
            nonlocal call_count
            call_count += 1
            return x

        fn(1)
        fn(2)
        assert call_count == 2, "Count must be greater than zero"

    def test_custom_key_func(self):
        cache = LRUCache()
        call_count = 0

        @cached(cache, key_func=lambda x, y: f"{x}-{y}")
        def add(x, y):
            nonlocal call_count
            call_count += 1
            return x + y

        assert add(1, 2) == 3
        assert add(1, 2) == 3
        assert call_count == 1, "Count must be greater than zero"

    def test_wraps_preserves_function_name(self):
        cache = LRUCache()

        @cached(cache)
        def my_func():
            return 42

        assert my_func.__name__ == "my_func", "__name__ is not valid"

    def test_none_value_is_not_cached(self):
        """A function returning None will miss cache every time (sentinel check)."""
        cache = LRUCache()
        call_count = 0

        @cached(cache)
        def returns_none():
            nonlocal call_count
            call_count += 1
            return None

        returns_none()
        returns_none()
        # None is not stored (cache.get returns None for both hit and miss),
        # so the function is called twice.
        assert call_count == 2, "Count must be greater than zero"


# ---------------------------------------------------------------------------
# RateLimiter
# ---------------------------------------------------------------------------


class TestRateLimiter:
    def test_acquire_within_burst(self):
        limiter = RateLimiter(rate=10, burst=5)
        # Should succeed up to burst size from initial full bucket
        successes = sum(1 for _ in range(5) if limiter.acquire())
        assert successes == 5, "successes is not valid"

    def test_acquire_fails_when_exhausted(self):
        limiter = RateLimiter(rate=0.01, burst=1)
        limiter.acquire()  # drain the single token
        assert limiter.acquire() is False, "Condition must be true"

    def test_acquire_refills_over_time(self):
        limiter = RateLimiter(rate=100, burst=1)
        limiter.acquire()  # drain
        time.sleep(0.05)  # 100 tokens/s -> ~5 tokens added
        assert limiter.acquire() is True, "Condition must be true"

    def test_wait_for_token_succeeds_fast(self):
        limiter = RateLimiter(rate=1000, burst=5)
        result = limiter.wait_for_token(timeout=1.0)
        assert result is True, "Result must not be empty"

    def test_wait_for_token_timeout(self):
        limiter = RateLimiter(rate=0.001, burst=1)
        limiter.acquire()  # drain
        start = time.time()
        result = limiter.wait_for_token(timeout=0.05)
        elapsed = time.time() - start
        assert result is False, "Result must not be empty"
        assert elapsed < 1.0, "elapsed is not valid"

    def test_acquire_multiple_tokens(self):
        limiter = RateLimiter(rate=10, burst=10)
        assert limiter.acquire(tokens=5) is True, "Condition must be true"
        assert limiter.acquire(tokens=5) is True, "Condition must be true"
        assert limiter.acquire(tokens=1) is False, "Condition must be true"


# ---------------------------------------------------------------------------
# rate_limited decorator
# ---------------------------------------------------------------------------


class TestRateLimitedDecorator:
    def test_passes_through_when_token_available(self):
        limiter = RateLimiter(rate=100, burst=10)

        @rate_limited(limiter)
        def fn():
            return "ok"

        assert fn() == "ok", "Condition must be true"

    def test_raises_when_exhausted(self):
        limiter = RateLimiter(rate=0.001, burst=1)
        limiter.acquire()  # drain

        @rate_limited(limiter)
        def fn():
            return "ok"  # pragma: no cover

        with pytest.raises(RuntimeError, match="Rate limit exceeded"):
            fn()

    def test_wraps_preserves_name(self):
        limiter = RateLimiter(rate=100, burst=5)

        @rate_limited(limiter)
        def my_fn():
            pass

        assert my_fn.__name__ == "my_fn", "__name__ is not valid"


# ---------------------------------------------------------------------------
# CircuitBreaker
# ---------------------------------------------------------------------------


class TestCircuitBreaker:
    def test_initial_state_is_closed(self):
        cb = CircuitBreaker()
        assert cb.state == "closed", "state is not valid"

    def test_can_execute_when_closed(self):
        cb = CircuitBreaker()
        assert cb.can_execute() is True, "Condition must be true"

    def test_failures_open_circuit(self):
        cb = CircuitBreaker(failure_threshold=3)
        for _ in range(3):
            cb.record_failure()
        assert cb.state == "open", "state is not valid"

    def test_cannot_execute_when_open(self):
        cb = CircuitBreaker(failure_threshold=1)
        cb.record_failure()
        assert cb.can_execute() is False, "Condition must be true"

    def test_open_transitions_to_half_open_after_timeout(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.05)
        cb.record_failure()
        assert cb.state == "open", "state is not valid"
        time.sleep(0.1)
        assert cb.state == "half-open", "state is not valid"
        assert cb.can_execute() is True, "Condition must be true"

    def test_half_open_closes_after_enough_successes(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.05, half_open_requests=2)
        cb.record_failure()
        time.sleep(0.1)
        cb.state  # trigger half-open
        cb.record_success()
        cb.record_success()
        assert cb.state == "closed", "state is not valid"

    def test_half_open_reopens_on_failure(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.05)
        cb.record_failure()
        time.sleep(0.1)
        cb.state  # trigger half-open transition
        cb.record_failure()
        assert cb._state == "open", "_state is not valid"

    def test_record_success_decrements_failures_in_closed(self):
        cb = CircuitBreaker(failure_threshold=5)
        cb.record_failure()
        cb.record_failure()
        cb.record_success()
        assert cb._failures == 1, "_failures is not valid"

    def test_record_success_clamps_at_zero(self):
        cb = CircuitBreaker()
        cb.record_success()  # no failures to decrement
        assert cb._failures == 0, "_failures is not valid"

    def test_decorator_passes_through(self):
        cb = CircuitBreaker()

        @cb
        def fn():
            return "result"

        assert fn() == "result", "Result must not be empty"

    def test_decorator_records_success(self):
        cb = CircuitBreaker(failure_threshold=5)
        cb._failures = 2

        @cb
        def fn():
            return 1

        fn()
        assert cb._failures == 1, "_failures is not valid"

    def test_decorator_records_failure_and_reraises(self):
        cb = CircuitBreaker(failure_threshold=5)

        @cb
        def failing():
            raise ValueError("circuit_failure")

        with pytest.raises(ValueError, match="circuit_failure"):
            failing()
        assert cb._failures == 1, "_failures is not valid"

    def test_decorator_raises_when_open(self):
        cb = CircuitBreaker(failure_threshold=1)
        cb.record_failure()  # open circuit

        @cb
        def fn():
            return "ok"  # pragma: no cover

        with pytest.raises(RuntimeError, match="Circuit breaker is"):
            fn()

    def test_decorator_preserves_function_name(self):
        cb = CircuitBreaker()

        @cb
        def my_function():
            pass

        assert my_function.__name__ == "my_function", "__name__ is not valid"


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


class TestEndpoint:
    def test_default_values(self):
        ep = Endpoint(url="http://localhost:8080")
        assert ep.weight == 1.0, "weight is not valid"
        assert ep.healthy is True, "healthy is not valid"
        assert ep.current_connections == 0, "current_connections is not valid"
        assert ep.total_requests == 0, "total_requests is not valid"
        assert ep.failed_requests == 0, "failed_requests is not valid"
        assert ep.avg_latency_ms == 0.0, "avg_latency_ms is not valid"

    def test_custom_values(self):
        ep = Endpoint(url="http://host", weight=2.5, healthy=False)
        assert ep.url == "http://host", "url is not valid"
        assert ep.weight == 2.5, "weight is not valid"
        assert ep.healthy is False, "healthy is not valid"


# ---------------------------------------------------------------------------
# LoadBalancer
# ---------------------------------------------------------------------------


class TestLoadBalancer:
    def _make_endpoints(self, n=3):
        return [Endpoint(url=f"http://host{i}") for i in range(n)]

    def test_get_endpoint_round_robin_cycles(self):
        eps = self._make_endpoints(3)
        lb = LoadBalancer(eps, strategy="round_robin")
        urls = [lb.get_endpoint().url for _ in range(6)]
        assert urls[:3] == [e.url for e in eps], "Condition must be true"
        assert urls[3:] == [e.url for e in eps], "Condition must be true"

    def test_get_endpoint_least_connections(self):
        eps = self._make_endpoints(3)
        eps[0].current_connections = 5
        eps[1].current_connections = 2
        eps[2].current_connections = 9
        lb = LoadBalancer(eps, strategy="least_connections")
        assert lb.get_endpoint().url == eps[1].url, "url is not valid"

    def test_get_endpoint_weighted_returns_valid(self):
        eps = self._make_endpoints(3)
        for i, ep in enumerate(eps):
            ep.weight = float(i + 1)
        lb = LoadBalancer(eps, strategy="weighted")
        for _ in range(20):
            result = lb.get_endpoint()
            assert result in eps, "Result must not be empty"

    def test_get_endpoint_no_healthy_returns_none(self):
        eps = self._make_endpoints(2)
        for ep in eps:
            ep.healthy = False
        lb = LoadBalancer(eps)
        assert lb.get_endpoint() is None, "Condition must be true"

    def test_mark_unhealthy(self):
        eps = self._make_endpoints(2)
        lb = LoadBalancer(eps)
        lb.mark_unhealthy(eps[0])
        assert eps[0].healthy is False, "healthy is not valid"
        result = lb.get_endpoint()
        assert result.url == eps[1].url, "Result must not be empty"

    def test_mark_healthy(self):
        eps = self._make_endpoints(1)
        eps[0].healthy = False
        lb = LoadBalancer(eps)
        lb.mark_healthy(eps[0])
        assert lb.get_endpoint().url == eps[0].url, "url is not valid"

    def test_unknown_strategy_returns_first(self):
        eps = self._make_endpoints(3)
        lb = LoadBalancer(eps, strategy="unknown")
        assert lb.get_endpoint().url == eps[0].url, "url is not valid"

    def test_only_healthy_endpoints_used(self):
        eps = self._make_endpoints(3)
        eps[1].healthy = False
        lb = LoadBalancer(eps, strategy="round_robin")
        urls = {lb.get_endpoint().url for _ in range(10)}
        assert eps[1].url not in urls, "Condition must be true"


# ---------------------------------------------------------------------------
# ResourcePool
# ---------------------------------------------------------------------------


class TestResourcePool:
    def _counter_factory(self):
        """Factory that returns incrementing integers."""
        count = [0]

        def factory():
            count[0] += 1
            return count[0]

        return factory

    def test_prepopulates_min_size(self):
        pool = ResourcePool(factory=self._counter_factory(), min_size=3, max_size=10)
        assert len(pool._pool) == 3, "Collection must not be empty"

    def test_acquire_returns_prepopulated_resource(self):
        pool = ResourcePool(factory=lambda: "res", min_size=1, max_size=5)
        r = pool.acquire()
        assert r == "res", "r is not valid"

    def test_acquire_creates_new_when_pool_empty(self):
        call_count = [0]

        def factory():
            call_count[0] += 1
            return object()

        pool = ResourcePool(factory=factory, min_size=0, max_size=5)
        r = pool.acquire()
        assert r is not None, "r must be initialized"
        assert call_count[0] == 1, "Count must be greater than zero"

    def test_release_returns_resource_to_pool(self):
        pool = ResourcePool(factory=lambda: "x", min_size=1, max_size=5)
        r = pool.acquire()
        pool.release(r)
        assert len(pool._pool) == 1, "Collection must not be empty"

    def test_stats(self):
        pool = ResourcePool(factory=lambda: object(), min_size=2, max_size=10)
        r = pool.acquire()
        s = pool.stats
        assert s["in_use"] == 1, "Condition must be true"
        assert s["max_size"] == 10, "Condition must be true"
        pool.release(r)

    def test_acquire_timeout_returns_none_when_exhausted(self):
        """Pool at max capacity with all resources in use: acquire should time out."""
        pool = ResourcePool(factory=lambda: object(), min_size=1, max_size=1)
        r = pool.acquire()  # exhaust the pool
        result = pool.acquire(timeout=0.05)
        assert result is None, "Result must not be empty"
        pool.release(r)

    def test_release_notifies_waiting_acquirer(self):
        """A thread blocking on acquire() should unblock after release()."""
        pool = ResourcePool(factory=lambda: "shared", min_size=1, max_size=1)
        r = pool.acquire()

        acquired = []

        def waiter():
            acquired.append(pool.acquire(timeout=2.0))

        t = threading.Thread(target=waiter)
        t.start()
        time.sleep(0.05)
        pool.release(r)
        t.join(timeout=2.0)
        assert acquired == ["shared"], "acquired is not valid"


# ---------------------------------------------------------------------------
# MetricPoint
# ---------------------------------------------------------------------------


class TestMetricPoint:
    def test_default_tags_is_empty_dict(self):
        mp = MetricPoint(name="latency", value=42.0)
        assert mp.tags == {}, "tags is not valid"

    def test_default_timestamp_is_recent(self):
        before = time.time()
        mp = MetricPoint(name="latency", value=10.0)
        after = time.time()
        assert before <= mp.timestamp <= after, "before is not valid"

    def test_custom_tags(self):
        mp = MetricPoint(name="req", value=1.0, tags={"service": "api"})
        assert mp.tags == {"service": "api"}, "tags is not valid"


# ---------------------------------------------------------------------------
# PerformanceMonitor
# ---------------------------------------------------------------------------


class TestPerformanceMonitor:
    def test_record_and_get_average(self):
        mon = PerformanceMonitor()
        mon.record("latency", 10.0)
        mon.record("latency", 20.0)
        avg = mon.get_average("latency", window_seconds=60)
        assert avg == pytest.approx(15.0), "avg is not valid"

    def test_get_average_returns_none_for_unknown_metric(self):
        mon = PerformanceMonitor()
        assert mon.get_average("nonexistent") is None, "Condition must be true"

    def test_get_average_filters_old_points(self):
        mon = PerformanceMonitor()
        # inject an old point directly
        old_point = MetricPoint(name="req", value=999.0, timestamp=time.time() - 120)
        mon._metrics["req"].append(old_point)
        mon.record("req", 1.0)
        avg = mon.get_average("req", window_seconds=60)
        assert avg == pytest.approx(1.0), "avg is not valid"

    def test_get_percentile_p50(self):
        mon = PerformanceMonitor()
        for v in [1.0, 2.0, 3.0, 4.0, 5.0]:
            mon.record("metric", v)
        p50 = mon.get_percentile("metric", 50, window_seconds=60)
        assert p50 == pytest.approx(3.0), "p50 is not valid"

    def test_get_percentile_p0(self):
        mon = PerformanceMonitor()
        mon.record("metric", 10.0)
        mon.record("metric", 20.0)
        assert mon.get_percentile("metric", 0, window_seconds=60) == pytest.approx(10.0)

    def test_get_percentile_p100(self):
        mon = PerformanceMonitor()
        mon.record("metric", 10.0)
        mon.record("metric", 20.0)
        assert mon.get_percentile("metric", 100, window_seconds=60) == pytest.approx(20.0)

    def test_get_percentile_returns_none_for_unknown(self):
        mon = PerformanceMonitor()
        assert mon.get_percentile("none", 50) is None

    def test_get_summary_structure(self):
        mon = PerformanceMonitor()
        mon.record("latency", 10.0)
        mon.record("latency", 20.0)
        summary = mon.get_summary()
        assert "latency" in summary, "Condition must be true"
        s = summary["latency"]
        assert s["count"] == 2, "Count must be greater than zero"
        assert s["min"] == pytest.approx(10.0), "Condition must be true"
        assert s["max"] == pytest.approx(20.0), "Condition must be true"
        assert s["avg"] == pytest.approx(15.0), "Condition must be true"

    def test_get_summary_empty_returns_empty(self):
        mon = PerformanceMonitor()
        assert mon.get_summary() == {}, "Condition must be true"

    def test_record_caps_at_1000_points(self):
        mon = PerformanceMonitor()
        for i in range(1100):
            mon.record("metric", float(i))
        assert len(mon._metrics["metric"]) == 1000, "Collection must not be empty"

    def test_timed_decorator_records_latency(self):
        mon = PerformanceMonitor()

        @mon.timed("op")
        def fn():
            return "done"

        result = fn()
        assert result == "done", "Result must not be empty"
        avg = mon.get_average("op_latency_ms", window_seconds=60)
        assert avg is not None, "avg must be initialized"
        assert avg >= 0.0, "avg must be greater than zero"

    def test_timed_decorator_records_even_on_exception(self):
        mon = PerformanceMonitor()

        @mon.timed("failing_op")
        def fn():
            raise ValueError("monitor_failure")

        with pytest.raises(ValueError, match="monitor_failure"):
            fn()

        avg = mon.get_average("failing_op_latency_ms", window_seconds=60)
        assert avg is not None, "avg must be initialized"

    def test_timed_decorator_preserves_name(self):
        mon = PerformanceMonitor()

        @mon.timed("x")
        def my_timed_fn():
            pass

        assert my_timed_fn.__name__ == "my_timed_fn", "__name__ is not valid"

    def test_record_with_tags(self):
        mon = PerformanceMonitor()
        mon.record("requests", 1.0, tags={"env": "prod"})
        points = mon._metrics["requests"]
        assert points[0].tags == {"env": "prod"}, "tags is not valid"

    def test_thread_safety_concurrent_record(self):
        mon = PerformanceMonitor()
        errors = []

        def worker(i):
            try:
                for _ in range(20):
                    mon.record("m", float(i))
            except Exception as exc:  # pragma: no cover
                errors.append(exc)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert errors == [], "Error should be raised or set"
