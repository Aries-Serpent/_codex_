"""
Scalability and Performance Optimization Module

Provides utilities for:
- Load balancing and request distribution
- Caching strategies
- Resource pooling
- Performance monitoring
- Auto-scaling triggers
"""

from __future__ import annotations

import hashlib
import logging
import threading
import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

__all__ = [
    "CircuitBreaker",
    "LRUCache",
    "LoadBalancer",
    "PerformanceMonitor",
    "RateLimiter",
    "ResourcePool",
    "cached",
    "rate_limited",
]


class LRUCache:
    """Thread-safe LRU cache implementation."""

    def __init__(self, max_size: int = 1000, ttl_seconds: float = 300):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: dict[str, tuple] = {}  # key -> (value, timestamp)
        self._access_order: list[str] = []
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self._lock:
            if key in self._cache:
                value, timestamp = self._cache[key]
                if time.time() - timestamp < self.ttl_seconds:
                    self._hits += 1
                    # Move to end (most recently used)
                    self._access_order.remove(key)
                    self._access_order.append(key)
                    return value
                # Expired
                del self._cache[key]
                self._access_order.remove(key)
            self._misses += 1
            return None

    def set(self, key: str, value: Any) -> None:
        """set value in cache."""
        with self._lock:
            if key in self._cache:
                self._access_order.remove(key)
            elif len(self._cache) >= self.max_size:
                # Evict least recently used
                lru_key = self._access_order.pop(0)
                del self._cache[lru_key]

            self._cache[key] = (value, time.time())
            self._access_order.append(key)

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()

    @property
    def hit_rate(self) -> float:
        """Get cache hit rate."""
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0

    @property
    def stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": self.hit_rate,
            }


def cached(cache: LRUCache, key_func: Callable[..., str] | None = None):
    """Decorator for caching function results."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            if key_func is not None:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = hashlib.sha256(f"{func.__name__}:{args}:{kwargs}".encode()).hexdigest()

            result = cache.get(cache_key)
            if result is not None:
                return result

            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            return result

        return wrapper

    return decorator


class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(
        self,
        rate: float,  # tokens per second
        burst: int = 10,  # max burst size
    ):
        self.rate = rate
        self.burst = burst
        self._tokens = burst
        self._last_update = time.time()
        self._lock = threading.Lock()

    def acquire(self, tokens: int = 1) -> bool:
        """Try to acquire tokens. Returns True if successful."""
        with self._lock:
            now = time.time()
            elapsed = now - self._last_update
            self._tokens = min(self.burst, self._tokens + elapsed * self.rate)  # type: ignore[assignment]
            self._last_update = now

            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            return False

    def wait_for_token(self, timeout: float | None = None) -> bool:
        """Wait for a token to become available."""
        start = time.time()
        while True:
            if self.acquire():
                return True
            if timeout and (time.time() - start) > timeout:
                return False
            time.sleep(0.01)


def rate_limited(limiter: RateLimiter):
    """Decorator for rate limiting function calls."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            if not limiter.acquire():
                raise RuntimeError("Rate limit exceeded")
            return func(*args, **kwargs)

        return wrapper

    return decorator


class CircuitBreaker:
    """Circuit breaker for fault tolerance."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_requests: int = 3,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_requests = half_open_requests

        self._failures = 0
        self._successes = 0
        self._state = "closed"  # closed, open, half-open
        self._last_failure_time: Optional[float] = None
        self._lock = threading.Lock()

    @property
    def state(self) -> str:
        """Get current circuit state."""
        with self._lock:
            if self._state == "open":
                if time.time() - self._last_failure_time > self.recovery_timeout:  # type: ignore[operator]
                    self._state = "half-open"
                    self._successes = 0
            return self._state

    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        state = self.state
        return state in ("closed", "half-open")

    def record_success(self) -> None:
        """Record a successful execution."""
        with self._lock:
            if self._state == "half-open":
                self._successes += 1
                if self._successes >= self.half_open_requests:
                    self._state = "closed"
                    self._failures = 0
            else:
                self._failures = max(0, self._failures - 1)

    def record_failure(self) -> None:
        """Record a failed execution."""
        with self._lock:
            self._failures += 1
            self._last_failure_time = time.time()

            if self._state == "half-open" or self._failures >= self.failure_threshold:
                self._state = "open"

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """Use as a decorator."""

        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            if not self.can_execute():
                raise RuntimeError(f"Circuit breaker is {self.state}")

            try:
                result = func(*args, **kwargs)
                self.record_success()
                return result
            except (ValueError, TypeError, RuntimeError):
                logger.warning("Exception occurred", exc_info=True)
                self.record_failure()
                raise

        return wrapper


@dataclass
class Endpoint:
    """Represents a backend endpoint for load balancing."""

    url: str
    weight: float = 1.0
    healthy: bool = True
    current_connections: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    avg_latency_ms: float = 0.0


class LoadBalancer:
    """Simple load balancer with multiple strategies."""

    def __init__(
        self,
        endpoints: list[Endpoint],
        strategy: str = "round_robin",
    ):
        self.endpoints = endpoints
        self.strategy = strategy
        self._current_index = 0
        self._lock = threading.Lock()

    def get_endpoint(self) -> Optional[Endpoint]:
        """Get next endpoint based on strategy."""
        healthy = [e for e in self.endpoints if e.healthy]
        if not healthy:
            return None

        if self.strategy == "round_robin":
            return self._round_robin(healthy)
        if self.strategy == "least_connections":
            return self._least_connections(healthy)
        if self.strategy == "weighted":
            return self._weighted(healthy)
        return healthy[0]

    def _round_robin(self, endpoints: list[Endpoint]) -> Endpoint:
        with self._lock:
            endpoint = endpoints[self._current_index % len(endpoints)]
            self._current_index += 1
            return endpoint

    def _least_connections(self, endpoints: list[Endpoint]) -> Endpoint:
        return min(endpoints, key=lambda e: e.current_connections)

    def _weighted(self, endpoints: list[Endpoint]) -> Endpoint:
        from secrets import SystemRandom

        total_weight = sum(e.weight for e in endpoints)
        r = SystemRandom().uniform(0, total_weight)

        cumulative = 0
        for endpoint in endpoints:
            cumulative += endpoint.weight  # type: ignore[assignment]
            if r <= cumulative:
                return endpoint
        return endpoints[-1]

    def mark_unhealthy(self, endpoint: Endpoint) -> None:
        """Mark an endpoint as unhealthy."""
        endpoint.healthy = False

    def mark_healthy(self, endpoint: Endpoint) -> None:
        """Mark an endpoint as healthy."""
        endpoint.healthy = True


class ResourcePool:
    """Generic resource pool for connection/object pooling."""

    def __init__(
        self,
        factory: Callable[[], T],
        max_size: int = 10,
        min_size: int = 2,
    ):
        self.factory = factory
        self.max_size = max_size
        self.min_size = min_size

        self._pool: list[T] = []
        self._in_use: int = 0
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)

        # Pre-populate pool
        for _ in range(min_size):
            self._pool.append(factory())

    def acquire(self, timeout: float | None = None) -> Optional[T]:
        """Acquire a resource from the pool."""
        with self._condition:
            start = time.time()

            while True:
                if self._pool:
                    resource = self._pool.pop()
                    self._in_use += 1
                    return resource  # type: ignore[return-value]

                if self._in_use < self.max_size:
                    resource = self.factory()
                    self._in_use += 1
                    return resource  # type: ignore[return-value]

                if timeout:
                    remaining = timeout - (time.time() - start)
                    if remaining <= 0:
                        return None
                    self._condition.wait(remaining)
                else:
                    self._condition.wait()

    def release(self, resource: T) -> None:
        """Return a resource to the pool."""
        with self._condition:
            self._pool.append(resource)  # type: ignore[arg-type]
            self._in_use -= 1
            self._condition.notify()

    @property
    def stats(self) -> dict[str, int]:
        """Get pool statistics."""
        with self._lock:
            return {
                "available": len(self._pool),
                "in_use": self._in_use,
                "max_size": self.max_size,
            }


@dataclass
class MetricPoint:
    """A single metric measurement."""

    name: str
    value: float
    timestamp: float = field(default_factory=time.time)
    tags: dict[str, str] = field(default_factory=dict)


class PerformanceMonitor:
    """Performance monitoring and metrics collection."""

    def __init__(self):
        self._metrics: dict[str, list[MetricPoint]] = defaultdict(list)
        self._lock = threading.Lock()

    def record(self, name: str, value: float, tags: dict[str, str] | None = None) -> None:
        """Record a metric value."""
        with self._lock:
            point = MetricPoint(name=name, value=value, tags=tags or {})
            self._metrics[name].append(point)

            # Keep last 1000 points per metric
            if len(self._metrics[name]) > 1000:
                self._metrics[name] = self._metrics[name][-1000:]

    def get_average(self, name: str, window_seconds: float = 60) -> Optional[float]:
        """Get average value over time window."""
        with self._lock:
            points = self._metrics.get(name, [])
            cutoff = time.time() - window_seconds
            recent = [p.value for p in points if p.timestamp > cutoff]
            return sum(recent) / len(recent) if recent else None

    def get_percentile(
        self, name: str, percentile: float, window_seconds: float = 60
    ) -> Optional[float]:
        """Get percentile value over time window."""
        with self._lock:
            points = self._metrics.get(name, [])
            cutoff = time.time() - window_seconds
            recent = sorted(p.value for p in points if p.timestamp > cutoff)
            if not recent:
                return None
            idx = int(len(recent) * percentile / 100)
            return recent[min(idx, len(recent) - 1)]

    def get_summary(self) -> dict[str, dict[str, Any]]:
        """Get summary of all metrics."""
        with self._lock:
            summary = {}
            for name, points in self._metrics.items():
                if not points:
                    continue
                values = [p.value for p in points[-100:]]
                summary[name] = {
                    "count": len(points),
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                }
            return summary

    def timed(self, name: str):
        """Decorator for timing function execution."""

        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            def wrapper(*args, **kwargs) -> T:
                start = time.time()
                try:
                    return func(*args, **kwargs)
                finally:
                    elapsed_ms = (time.time() - start) * 1000
                    self.record(f"{name}_latency_ms", elapsed_ms)

            return wrapper

        return decorator
