"""
Distributed Cache Module

Provides distributed caching for production scale:
- Redis integration for shared cache
- Fallback to local cache when Redis unavailable
- Cache synchronization across instances
- Configurable backends
"""

import hashlib
import json
import logging
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from .query_cache import QueryCache, QueryCacheConfig

logger = logging.getLogger(__name__)


class CacheBackend(Enum):
    """Available cache backends."""
    
    MEMORY = "memory"  # In-memory only
    REDIS = "redis"  # Redis distributed cache
    HYBRID = "hybrid"  # Memory + Redis (write-through)


@dataclass
class DistributedCacheConfig:
    """Configuration for distributed cache."""
    
    backend: CacheBackend = CacheBackend.MEMORY
    
    # Memory cache settings
    memory_max_size: int = 1000
    memory_ttl: float = 300.0
    
    # Redis settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_key_prefix: str = "rag:cache:"
    redis_ttl: int = 3600  # 1 hour
    redis_socket_timeout: float = 5.0
    redis_connection_pool_size: int = 10
    
    # Hybrid settings
    write_through: bool = True  # Write to both caches
    read_through: bool = True  # Check both caches on read
    
    # Serialization
    compress: bool = True
    compression_threshold: int = 1024  # Compress if larger than 1KB


class BaseCacheBackend(ABC):
    """Base class for cache backends."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    def put(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Put value in cache."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all entries."""
        pass
    
    @abstractmethod
    def contains(self, key: str) -> bool:
        """Check if key exists."""
        pass


class MemoryCacheBackend(BaseCacheBackend):
    """In-memory cache backend using QueryCache."""
    
    def __init__(self, config: DistributedCacheConfig):
        self.config = config
        self._cache = QueryCache(QueryCacheConfig(
            max_size=config.memory_max_size,
            default_ttl=config.memory_ttl,
        ))
    
    def get(self, key: str) -> Optional[Any]:
        return self._cache.get(key)
    
    def put(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        ttl_float = float(ttl) if ttl else None
        self._cache.put(key, value, ttl_float)
        return True
    
    def delete(self, key: str) -> bool:
        return self._cache.delete(key)
    
    def clear(self) -> None:
        self._cache.clear()
    
    def contains(self, key: str) -> bool:
        return self._cache.contains(key)
    
    def get_stats(self) -> dict[str, Any]:
        return self._cache.get_stats().to_dict()


class RedisCacheBackend(BaseCacheBackend):
    """Redis distributed cache backend."""
    
    def __init__(self, config: DistributedCacheConfig):
        self.config = config
        self._client = None
        self._connected = False
        self._lock = threading.Lock()
    
    def _get_client(self):
        """Get Redis client with lazy initialization."""
        if self._client is not None:
            return self._client if self._connected else None
        
        with self._lock:
            if self._client is not None:
                return self._client if self._connected else None
            
            try:
                import redis
                
                self._client = redis.Redis(
                    host=self.config.redis_host,
                    port=self.config.redis_port,
                    db=self.config.redis_db,
                    password=self.config.redis_password,
                    socket_timeout=self.config.redis_socket_timeout,
                    decode_responses=False,  # We handle encoding ourselves
                )
                
                # Test connection
                self._client.ping()
                self._connected = True
                logger.info(
                    f"Connected to Redis at {self.config.redis_host}:{self.config.redis_port}"
                )
                return self._client
                
            except ImportError:
                logger.warning(
                    "redis package not installed. Install with: pip install redis"
                )
                self._connected = False
                return None
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}")
                self._connected = False
                return None
    
    def _make_key(self, key: str) -> str:
        """Generate full Redis key with prefix."""
        return f"{self.config.redis_key_prefix}{key}"
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize value for Redis storage."""
        data = json.dumps(value).encode()
        
        if self.config.compress and len(data) > self.config.compression_threshold:
            import zlib
            data = zlib.compress(data)
            # Prefix with marker to indicate compression
            data = b"Z" + data
        else:
            data = b"J" + data
        
        return data
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize value from Redis."""
        if not data:
            return None
        
        marker = data[0:1]
        payload = data[1:]
        
        if marker == b"Z":
            import zlib
            payload = zlib.decompress(payload)
        
        return json.loads(payload.decode())
    
    def get(self, key: str) -> Optional[Any]:
        client = self._get_client()
        if not client:
            return None
        
        try:
            data = client.get(self._make_key(key))
            if data is None:
                return None
            return self._deserialize(data)
        except Exception as e:
            logger.warning(f"Redis get error: {e}")
            return None
    
    def put(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        client = self._get_client()
        if not client:
            return False
        
        try:
            ttl = ttl or self.config.redis_ttl
            data = self._serialize(value)
            client.setex(self._make_key(key), ttl, data)
            return True
        except Exception as e:
            logger.warning(f"Redis put error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        client = self._get_client()
        if not client:
            return False
        
        try:
            result = client.delete(self._make_key(key))
            return result > 0
        except Exception as e:
            logger.warning(f"Redis delete error: {e}")
            return False
    
    def clear(self) -> None:
        client = self._get_client()
        if not client:
            return
        
        try:
            # Delete all keys with our prefix
            pattern = f"{self.config.redis_key_prefix}*"
            cursor = 0
            while True:
                cursor, keys = client.scan(cursor, match=pattern, count=100)
                if keys:
                    client.delete(*keys)
                if cursor == 0:
                    break
            logger.debug("Redis cache cleared")
        except Exception as e:
            logger.warning(f"Redis clear error: {e}")
    
    def contains(self, key: str) -> bool:
        client = self._get_client()
        if not client:
            return False
        
        try:
            return bool(client.exists(self._make_key(key)))
        except Exception as e:
            logger.warning(f"Redis contains error: {e}")
            return False
    
    def get_stats(self) -> dict[str, Any]:
        client = self._get_client()
        if not client:
            return {"connected": False}
        
        try:
            info = client.info("stats")
            return {
                "connected": True,
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
            }
        except Exception as e:
            return {"connected": False, "error": str(e)}


class DistributedCache:
    """
    Production-grade distributed cache.
    
    Features:
    - Multiple backend support (Memory, Redis, Hybrid)
    - Automatic fallback when Redis unavailable
    - Write-through and read-through caching
    - Compression for large values
    
    Example:
        # Memory-only cache
        cache = DistributedCache(DistributedCacheConfig(backend=CacheBackend.MEMORY))
        
        # Redis cache with fallback
        cache = DistributedCache(DistributedCacheConfig(
            backend=CacheBackend.HYBRID,
            redis_host="localhost",
        ))
        
        cache.put("key1", {"data": "value"})
        result = cache.get("key1")
    """
    
    def __init__(self, config: Optional[DistributedCacheConfig] = None):
        """Initialize distributed cache."""
        self.config = config or DistributedCacheConfig()
        
        # Initialize backends
        self._memory_backend = MemoryCacheBackend(self.config)
        
        if self.config.backend in (CacheBackend.REDIS, CacheBackend.HYBRID):
            self._redis_backend = RedisCacheBackend(self.config)
        else:
            self._redis_backend = None
        
        logger.info(f"DistributedCache initialized with backend: {self.config.backend.value}")
    
    def _generate_key(self, query: Any) -> str:
        """Generate cache key from query."""
        if isinstance(query, str):
            data = query.encode()
        else:
            data = json.dumps(query, sort_keys=True).encode()
        return hashlib.sha256(data).hexdigest()[:16]
    
    def get(self, query: Any) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            query: Cache key (string or object)
            
        Returns:
            Cached value or None
        """
        key = self._generate_key(query)
        
        if self.config.backend == CacheBackend.MEMORY:
            return self._memory_backend.get(key)
        
        if self.config.backend == CacheBackend.REDIS:
            return self._redis_backend.get(key)
        
        # Hybrid: check memory first, then Redis
        result = self._memory_backend.get(key)
        if result is not None:
            return result
        
        if self.config.read_through and self._redis_backend:
            result = self._redis_backend.get(key)
            if result is not None:
                # Populate memory cache
                self._memory_backend.put(key, result)
            return result
        
        return None
    
    def put(
        self,
        query: Any,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Put value in cache.
        
        Args:
            query: Cache key (string or object)
            value: Value to cache
            ttl: Optional TTL in seconds
            
        Returns:
            True if stored successfully
        """
        key = self._generate_key(query)
        
        if self.config.backend == CacheBackend.MEMORY:
            return self._memory_backend.put(key, value, ttl)
        
        if self.config.backend == CacheBackend.REDIS:
            return self._redis_backend.put(key, value, ttl)
        
        # Hybrid: write to both
        memory_ok = self._memory_backend.put(key, value, ttl)
        
        if self.config.write_through and self._redis_backend:
            redis_ok = self._redis_backend.put(key, value, ttl)
            return memory_ok and redis_ok
        
        return memory_ok
    
    def delete(self, query: Any) -> bool:
        """Delete value from cache."""
        key = self._generate_key(query)
        
        if self.config.backend == CacheBackend.MEMORY:
            return self._memory_backend.delete(key)
        
        if self.config.backend == CacheBackend.REDIS:
            return self._redis_backend.delete(key)
        
        # Hybrid: delete from both
        memory_ok = self._memory_backend.delete(key)
        redis_ok = True
        if self._redis_backend:
            redis_ok = self._redis_backend.delete(key)
        return memory_ok or redis_ok
    
    def clear(self) -> None:
        """Clear all entries from cache."""
        self._memory_backend.clear()
        if self._redis_backend:
            self._redis_backend.clear()
    
    def contains(self, query: Any) -> bool:
        """Check if key exists in cache."""
        key = self._generate_key(query)
        
        if self.config.backend == CacheBackend.MEMORY:
            return self._memory_backend.contains(key)
        
        if self.config.backend == CacheBackend.REDIS:
            return self._redis_backend.contains(key)
        
        # Hybrid: check both
        return (
            self._memory_backend.contains(key) or
            (self._redis_backend and self._redis_backend.contains(key))
        )
    
    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        stats = {
            "backend": self.config.backend.value,
            "memory": self._memory_backend.get_stats(),
        }
        
        if self._redis_backend:
            stats["redis"] = self._redis_backend.get_stats()
        
        return stats
    
    def warm(self, entries: dict[Any, Any], ttl: Optional[int] = None) -> int:
        """
        Warm the cache with pre-computed entries.
        
        Args:
            entries: Dictionary of query -> value mappings
            ttl: Optional TTL for all entries
            
        Returns:
            Number of entries added
        """
        count = 0
        for query, value in entries.items():
            if self.put(query, value, ttl):
                count += 1
        
        logger.info(f"Cache warmed with {count} entries")
        return count
    
    def __contains__(self, query: Any) -> bool:
        """Check if query is in cache."""
        return self.contains(query)
