"""
L2 Session Cache: Distributed Redis cache for cross-request persistence.

Part of Phase 13.4 4-layer cache hierarchy. Optimized for:
- Sub-100ms latency (Redis + connection pooling)
- Cross-request session persistence
- Distributed cache across multiple instances
- Automatic fallback to local cache if Redis unavailable

TTL: 3600 seconds (1 hour)
Backend: Redis with local LRU fallback
"""

from __future__ import annotations

import base64
import json
import logging
import os
import time
from typing import Any, Optional

logger = logging.getLogger(__name__)

# L2 constraints
L2_TTL = 3600  # 1 hour

# Type tag used by _SafeJSONEncoder to round-trip bytes values.
# The double-underscore prefix/suffix and "codex_b64" namespace make accidental
# collision with real user data extremely unlikely.
_BYTES_TAG = "__codex_cache_bytes_b64__"


class _SafeJSONEncoder(json.JSONEncoder):
    """JSON encoder that safely handles bytes/bytearray by base64-encoding them."""

    def default(self, o: Any) -> Any:
        if isinstance(o, (bytes, bytearray)):
            return {_BYTES_TAG: base64.b64encode(o).decode("ascii")}
        return super().default(o)


def _safe_json_object_hook(obj: dict) -> Any:
    """JSON object hook that restores base64-encoded bytes produced by _SafeJSONEncoder.

    Only decodes dicts that contain exactly the sentinel key to avoid false positives
    on real user dictionaries.
    """
    if len(obj) == 1 and _BYTES_TAG in obj:
        raw = obj[_BYTES_TAG]
        if isinstance(raw, str):
            return base64.b64decode(raw)
    return obj


class L2SessionCache:
    """Distributed session cache backed by Redis with local fallback.

    Features:
    - Redis connection pooling for performance
    - Automatic serialization (JSON with base64 encoding for bytes values)
    - Local LRU fallback cache if Redis unavailable
    - Connection error handling and logging
    - Key pattern scanning for analytics
    - Cross-instance cache coherency via Redis

    Usage:
        cache = L2SessionCache()
        cache.set("session:user123:data", user_data, ttl=3600)
        user_data = cache.get("session:user123:data")
        stats = cache.get_stats()
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        default_ttl: int = L2_TTL,
        enable_local_fallback: bool = True,
        local_max_size: int = 10000,
    ):
        """Initialize L2 session cache.

        Args:
            host: Redis hostname (or env CODEX_REDIS_HOST)
            port: Redis port
            db: Redis database number
            password: Redis password (or env CODEX_REDIS_PASSWORD)
            default_ttl: Default TTL in seconds
            enable_local_fallback: Enable local cache fallback
            local_max_size: Max size of local fallback cache
        """
        self.host = host or os.environ.get("CODEX_REDIS_HOST", "localhost")
        self.port = port
        self.db = db
        self.default_ttl = default_ttl
        self.enable_local_fallback = enable_local_fallback

        self._redis = None
        self._local_cache: dict[str, dict[str, Any]] = {}
        self._local_max_size = local_max_size
        self._local_hits = 0
        self._local_misses = 0
        self._connected = False
        self._stats = {
            "redis_hits": 0,
            "redis_misses": 0,
            "redis_errors": 0,
            "local_hits": 0,
            "local_misses": 0,
        }

        self._connect(password)

    def _connect(self, password: Optional[str] = None) -> None:
        """Try to connect to Redis."""
        try:
            import redis

            kwargs = {
                "host": self.host,
                "port": self.port,
                "db": self.db,
                "decode_responses": False,
                "max_connections": 50,
                "socket_keepalive": True,
                "socket_keepalive_options": {
                    1: 1,  # TCP_KEEPIDLE
                    2: 1,  # TCP_KEEPINTVL
                    3: 3,  # TCP_KEEPCNT
                },
            }
            if password:
                kwargs["password"] = password

            pool = redis.ConnectionPool(**kwargs)
            self._redis = redis.Redis(connection_pool=pool)

            # Test connection
            self._redis.ping()  # type: ignore[attr-defined]
            self._connected = True
            logger.info(
                f"L2 Session Cache: Connected to Redis at {self.host}:{self.port}/{self.db}"
            )

        except ImportError:
            logger.warning(
                "L2 Session Cache: redis package not installed. Install with: pip install redis"
            )
            self._connected = False
        except Exception as e:
            logger.warning(
                f"L2 Session Cache: Failed to connect to Redis: {e}. Using local fallback only."
            )
            self._connected = False

    def _serialize(self, value: Any) -> bytes:
        """Serialize value to bytes using JSON with base64 encoding for bytes/bytearray.

        Supported types: str, int, float, bool, None, list, dict, bytes, bytearray.
        bytes/bytearray are transparently base64-encoded and round-trip correctly.
        """
        try:
            return json.dumps(value, cls=_SafeJSONEncoder).encode("utf-8")
        except (TypeError, ValueError) as exc:
            raise TypeError(
                f"L2SessionCache: value of type {type(value).__name__!r} is not "
                "JSON-serializable. Supported types: str, int, float, bool, None, "
                "list, dict, bytes, bytearray."
            ) from exc

    def _deserialize(self, data: bytes) -> Any:
        """Deserialize bytes to value."""
        try:
            return json.loads(data.decode("utf-8"), object_hook=_safe_json_object_hook)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError(
                f"L2SessionCache: cache data is corrupted or not valid JSON: {exc}"
            ) from exc

    def get(self, key: str) -> Optional[Any]:
        """Get value from L2 cache.

        Args:
            key: Cache key

        Returns:
            Cached value if found and not expired, None otherwise
        """
        # Try Redis first
        if self._connected and self._redis:
            try:
                value = self._redis.get(key)
                if value is not None:
                    self._stats["redis_hits"] += 1
                    # Also store in local fallback
                    if self.enable_local_fallback:
                        self._set_local(key, self._deserialize(value))
                    return self._deserialize(value)
                self._stats["redis_misses"] += 1
            except Exception as e:
                logger.error(f"L2 Session Cache: Redis get error for {key}: {e}")
                self._stats["redis_errors"] += 1

        # Try local fallback
        if self.enable_local_fallback:
            value = self._get_local(key)
            if value is not None:
                self._stats["local_hits"] += 1
                return value
            self._stats["local_misses"] += 1

        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in L2 cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional TTL in seconds
        """
        ttl = ttl or self.default_ttl

        # Store in Redis
        if self._connected and self._redis:
            try:
                serialized = self._serialize(value)
                if ttl:
                    self._redis.setex(key, ttl, serialized)
                else:
                    self._redis.set(key, serialized)
            except Exception as e:
                logger.error(f"L2 Session Cache: Redis set error for {key}: {e}")
                self._stats["redis_errors"] += 1

        # Also store in local fallback
        if self.enable_local_fallback:
            self._set_local(key, value, ttl)

    def delete(self, key: str) -> bool:
        """Delete key from L2 cache.

        Args:
            key: Cache key

        Returns:
            True if key was deleted, False otherwise
        """
        result = False

        # Delete from Redis
        if self._connected and self._redis:
            try:
                result = self._redis.delete(key) > 0
            except Exception as e:
                logger.error(f"L2 Session Cache: Redis delete error for {key}: {e}")
                self._stats["redis_errors"] += 1

        # Delete from local fallback
        if self.enable_local_fallback:
            result = self._delete_local(key) or result

        return result

    def exists(self, key: str) -> bool:
        """Check if key exists in L2 cache.

        Args:
            key: Cache key

        Returns:
            True if key exists, False otherwise
        """
        # Check Redis first
        if self._connected and self._redis:
            try:
                return self._redis.exists(key) > 0
            except Exception as e:
                logger.error(f"L2 Session Cache: Redis exists error for {key}: {e}")
                self._stats["redis_errors"] += 1

        # Check local fallback
        if self.enable_local_fallback:
            return self._exists_local(key)

        return False

    def clear(self) -> None:
        """Clear all entries from L2 cache."""
        # Clear Redis
        if self._connected and self._redis:
            try:
                self._redis.flushdb()
            except Exception as e:
                logger.error(f"L2 Session Cache: Redis clear error: {e}")
                self._stats["redis_errors"] += 1

        # Clear local fallback
        if self.enable_local_fallback:
            self._local_cache.clear()

    def _set_local(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store in local fallback cache."""
        ttl = ttl or self.default_ttl
        ttl_at = time.time() + ttl if ttl else None

        # Evict if needed (simple FIFO for simplicity)
        if len(self._local_cache) >= self._local_max_size:
            # Remove first (oldest) key
            if self._local_cache:
                oldest_key = next(iter(self._local_cache))
                del self._local_cache[oldest_key]

        self._local_cache[key] = {
            "value": value,
            "ttl_at": ttl_at,
            "created_at": time.time(),
        }

    def _get_local(self, key: str) -> Optional[Any]:
        """Get from local fallback cache."""
        if key not in self._local_cache:
            return None

        entry = self._local_cache[key]
        # Check expiration
        if entry["ttl_at"] and time.time() > entry["ttl_at"]:
            del self._local_cache[key]
            return None

        return entry["value"]

    def _exists_local(self, key: str) -> bool:
        """Check if exists in local fallback cache."""
        if key not in self._local_cache:
            return False

        entry = self._local_cache[key]
        if entry["ttl_at"] and time.time() > entry["ttl_at"]:
            del self._local_cache[key]
            return False

        return True

    def _delete_local(self, key: str) -> bool:
        """Delete from local fallback cache."""
        if key in self._local_cache:
            del self._local_cache[key]
            return True
        return False

    def get_stats(self) -> dict[str, Any]:
        """Get L2 cache statistics.

        Returns:
            Dict with hit rates and connection status
        """
        stats = dict(self._stats)

        # Add local cache stats
        if self.enable_local_fallback:
            local_total = self._stats["local_hits"] + self._stats["local_misses"]
            stats["local_cache_stats"] = {
                "size": len(self._local_cache),
                "max_size": self._local_max_size,
                "utilization": len(self._local_cache) / self._local_max_size,
                "hits": self._stats["local_hits"],
                "misses": self._stats["local_misses"],
                "hit_rate": (
                    self._stats["local_hits"] / local_total * 100 if local_total > 0 else 0.0
                ),
            }

        # Add Redis stats
        if self._connected and self._redis:
            try:
                redis_total = self._stats["redis_hits"] + self._stats["redis_misses"]
                info = self._redis.info()
                stats["redis_stats"] = {
                    "connected": True,
                    "hits": self._stats["redis_hits"],
                    "misses": self._stats["redis_misses"],
                    "hit_rate": (
                        self._stats["redis_hits"] / redis_total * 100 if redis_total > 0 else 0.0
                    ),
                    "used_memory": info.get("used_memory"),
                    "used_memory_human": info.get("used_memory_human"),
                    "db_size": self._redis.dbsize(),
                }
            except Exception as e:
                logger.error(f"L2 Session Cache: Error getting Redis info: {e}")
                stats["redis_stats"] = {"connected": False}
        else:
            stats["redis_stats"] = {"connected": False}

        stats["errors"] = self._stats["redis_errors"]

        return stats

    def scan_keys(self, pattern: str = "*", count: int = 100) -> list[str]:
        """Scan for keys matching pattern.

        Args:
            pattern: Key pattern (e.g., 'session:*')
            count: Approximate number of results

        Returns:
            List of matching keys
        """
        keys: list[str] = []

        # Scan Redis
        if self._connected and self._redis:
            try:
                for key in self._redis.scan_iter(match=pattern, count=count):
                    keys.append(key.decode() if isinstance(key, bytes) else key)
            except Exception as e:
                logger.error(f"L2 Session Cache: Redis scan error: {e}")

        return keys


# Global L2 cache instance
_l2_cache_instance: Optional[L2SessionCache] = None


def get_l2_cache() -> L2SessionCache:
    """Get the global L2 cache instance (singleton)."""
    global _l2_cache_instance
    if _l2_cache_instance is None:
        _l2_cache_instance = L2SessionCache()
    return _l2_cache_instance
