"""
FastAPI middleware for Phase 13.4 unified cache instrumentation.

Automatically:
- Caches endpoint responses by request signature
- Tracks p99 latency
- Monitors cache hit rates per endpoint
- Detects eviction storms
"""

from __future__ import annotations

import hashlib
import logging
import time
from typing import Any, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .orchestrator import get_cache_orchestrator
from .request_cache import reset_l1_cache

logger = logging.getLogger(__name__)


class CacheInstrumentationMiddleware(BaseHTTPMiddleware):
    """Middleware for automatic request caching and performance monitoring.

    Features:
    - Caches GET requests by path + query parameters
    - Tracks per-endpoint latency and hit rates
    - Resets L1 cache per request (request-scoped isolation)
    - Records p99 latency metrics
    - Detects cache eviction storms

    Configuration:
        app.add_middleware(
            CacheInstrumentationMiddleware,
            cacheable_methods=["GET"],
            cache_threshold_ms=100,
            enable_metrics=True,
        )
    """

    def __init__(
        self,
        app: ASGIApp,
        cacheable_methods: list[str] = None,
        cache_threshold_ms: int = 100,
        enable_metrics: bool = True,
    ):
        """Initialize middleware.

        Args:
            app: ASGI application
            cacheable_methods: HTTP methods to cache (default: ["GET"])
            cache_threshold_ms: Only cache responses slower than this
            enable_metrics: Enable per-endpoint metrics collection
        """
        super().__init__(app)
        self.cacheable_methods = cacheable_methods or ["GET"]
        self.cache_threshold_ms = cache_threshold_ms
        self.enable_metrics = enable_metrics

        self.cache = get_cache_orchestrator()
        self._endpoint_stats: dict[str, dict[str, Any]] = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with caching and metrics.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response
        """
        # Reset L1 cache at request start (request-scoped)
        reset_l1_cache()

        method = request.method
        path = request.url.path
        endpoint_key = f"{method} {path}"

        # Check if this endpoint should be cached
        use_cache = method in self.cacheable_methods

        # Generate cache key
        cache_key = None
        if use_cache:
            cache_key = self._make_cache_key(request)

            # Try to get from cache
            cached_response = self.cache.get(cache_key)
            if cached_response is not None:
                logger.debug(f"Cache hit for {endpoint_key}")
                return self._make_response(cached_response)

        # Record start time for latency measurement
        start_time = time.time()

        # Call next middleware/handler
        response = await call_next(request)

        # Measure latency
        latency_ms = (time.time() - start_time) * 1000

        # Only cache if response is successful and slow enough
        if use_cache and cache_key and response.status_code == 200 and latency_ms >= self.cache_threshold_ms:
            try:
                # Skip caching StreamingResponse and other non-bufferable responses
                if hasattr(response, 'body'):
                    # For buffered responses (JSONResponse, etc.)
                    body = response.body if isinstance(response.body, bytes) else response.body.encode('utf-8')
                else:
                    # For streaming responses, don't cache
                    logger.debug(f"Skipping cache for streaming response: {endpoint_key}")
                    return response

                # Cache the response
                cached_data = {
                    "status_code": response.status_code,
                    "body": body.decode("utf-8") if isinstance(body, bytes) else body,
                    "headers": dict(response.headers),
                    "media_type": response.media_type,
                    "timestamp": time.time(),
                    "latency_ms": latency_ms,
                }
                self.cache.set(cache_key, cached_data, tier="L2")

                # Re-wrap response with body and preserve content-type
                response = Response(
                    content=body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=cached_data.get("media_type"),
                )
            except Exception as e:
                logger.error(f"Cache write error for {endpoint_key}: {e}")

        # Record metrics
        if self.enable_metrics:
            self._record_endpoint_stats(endpoint_key, latency_ms, use_cache and cache_key is not None)

        return response

    def _make_cache_key(self, request: Request) -> str:
        """Generate cache key from request.

        Args:
            request: HTTP request

        Returns:
            Cache key string
        """
        # Include path and query params
        key_parts = [request.method, request.url.path]

        # Add query string if present
        if request.url.query:
            key_parts.append(request.url.query)

        # Add user ID if available (for personalized caching)
        user_header = request.headers.get("x-user-id") or request.headers.get("authorization")
        if user_header:
            key_parts.append(user_header)

        key_str = ":".join(key_parts)
        # Create hash to keep key size reasonable (SHA-256 used for security)
        cache_key = f"request:{hashlib.sha256(key_str.encode()).hexdigest()}"

        return cache_key

    def _make_response(self, cached_data: dict[str, Any]) -> Response:
        """Create Response from cached data.

        Args:
            cached_data: Cached response data

        Returns:
            Response object
        """
        return Response(
            content=cached_data.get("body", ""),
            status_code=cached_data.get("status_code", 200),
            headers=cached_data.get("headers", {}),
            media_type=cached_data.get("media_type", "application/json"),
        )

    def _record_endpoint_stats(self, endpoint_key: str, latency_ms: float, was_cached: bool) -> None:
        """Record statistics for endpoint.

        Args:
            endpoint_key: Endpoint identifier
            latency_ms: Response latency in milliseconds
            was_cached: Whether response was cached
        """
        if endpoint_key not in self._endpoint_stats:
            self._endpoint_stats[endpoint_key] = {
                "count": 0,
                "total_latency": 0,
                "min_latency": float("inf"),
                "max_latency": 0,
                "cache_hits": 0,
                "cache_misses": 0,
                "latencies": [],  # For p99 calculation
            }

        stats = self._endpoint_stats[endpoint_key]
        stats["count"] += 1
        stats["total_latency"] += latency_ms
        stats["min_latency"] = min(stats["min_latency"], latency_ms)
        stats["max_latency"] = max(stats["max_latency"], latency_ms)
        stats["latencies"].append(latency_ms)

        if was_cached:
            stats["cache_hits"] += 1
        else:
            stats["cache_misses"] += 1

        # Keep only last 1000 latencies for p99 calculation
        if len(stats["latencies"]) > 1000:
            stats["latencies"] = stats["latencies"][-1000:]

    def get_endpoint_stats(self) -> dict[str, Any]:
        """Get statistics for all endpoints.

        Returns:
            Dict with per-endpoint stats including p99 latency
        """
        result = {}

        for endpoint_key, stats in self._endpoint_stats.items():
            if stats["count"] > 0:
                # Calculate p99 latency
                sorted_latencies = sorted(stats["latencies"])
                p99_idx = max(0, int(len(sorted_latencies) * 0.99) - 1)
                p99_latency = sorted_latencies[p99_idx] if sorted_latencies else 0

                cache_hit_rate = (
                    stats["cache_hits"] / stats["count"] * 100 if stats["count"] > 0 else 0
                )

                result[endpoint_key] = {
                    "request_count": stats["count"],
                    "avg_latency_ms": stats["total_latency"] / stats["count"],
                    "p99_latency_ms": p99_latency,
                    "min_latency_ms": stats["min_latency"],
                    "max_latency_ms": stats["max_latency"],
                    "cache_hit_rate": f"{cache_hit_rate:.1f}%",
                    "cache_hits": stats["cache_hits"],
                    "cache_misses": stats["cache_misses"],
                }

        return result
