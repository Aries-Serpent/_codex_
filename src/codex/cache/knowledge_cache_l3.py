"""
L3 Knowledge Cache: Disk-backed cache for RAG embeddings and knowledge base.

Part of Phase 13.4 4-layer cache hierarchy. Optimized for:
- Persistent storage across requests/sessions
- Sub-100ms latency via memory-mapped files
- Large datasets (embeddings, documents)
- Cache invalidation via versioning

TTL: 86400 seconds (24 hours)
Backend: SQLite database with blob storage
Max Size: 10GB per cache tier
"""

from __future__ import annotations

import json
import logging
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# L3 constraints
L3_TTL = 86400  # 24 hours
L3_MAX_SIZE = 10 * 1024 * 1024 * 1024  # 10GB


class L3KnowledgeCache:
    """Disk-backed cache for RAG and knowledge data.

    Features:
    - SQLite for structured data with ACID guarantees
    - Blob storage for large documents/embeddings
    - Automatic schema management
    - Version-based invalidation
    - Approximate LRU eviction

    Usage:
        cache = L3KnowledgeCache(cache_dir="/tmp/codex_cache")
        cache.set("rag:embedding:doc123", embedding_vector)
        embedding = cache.get("rag:embedding:doc123")
    """

    def __init__(
        self,
        cache_dir: str = ".cache/codex_l3",
        default_ttl: int = L3_TTL,
        max_size: int = L3_MAX_SIZE,
    ):
        """Initialize L3 knowledge cache.

        Args:
            cache_dir: Directory for cache storage
            default_ttl: Default TTL in seconds
            max_size: Maximum cache size in bytes
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = self.cache_dir / "cache.db"
        self.default_ttl = default_ttl
        self.max_size = max_size

        self._local = threading.local()
        self._stats = {"hits": 0, "misses": 0, "errors": 0}

        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        """Get thread-local database connection."""
        if not hasattr(self._local, "conn"):
            self._local.conn = sqlite3.connect(
                str(self.db_path),
                timeout=5,
                check_same_thread=False,
            )
            self._local.conn.execute("PRAGMA journal_mode=WAL")
            self._local.conn.execute("PRAGMA synchronous=NORMAL")
        return self._local.conn

    def _init_db(self) -> None:
        """Initialize database schema."""
        try:
            conn = self._get_conn()
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    value BLOB NOT NULL,
                    ttl_at INTEGER,
                    created_at INTEGER NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    last_accessed INTEGER NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_ttl_at ON cache_entries(ttl_at)
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache_entries(last_accessed)
                """
            )
            conn.commit()
            logger.info(f"L3 Knowledge Cache: Initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"L3 Knowledge Cache: Database init error: {e}")
            raise

    def get(self, key: str) -> Optional[Any]:
        """Get value from L3 cache.

        Args:
            key: Cache key

        Returns:
            Cached value if found and not expired, None otherwise
        """
        try:
            conn = self._get_conn()
            cursor = conn.execute(
                """
                SELECT value, ttl_at FROM cache_entries
                WHERE key = ?
                """,
                (key,),
            )
            row = cursor.fetchone()

            if row is None:
                self._stats["misses"] += 1
                return None

            value_blob, ttl_at = row

            # Check expiration
            if ttl_at and time.time() > ttl_at:
                conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                conn.commit()
                self._stats["misses"] += 1
                return None

            # Update access count
            conn.execute(
                """
                UPDATE cache_entries
                SET access_count = access_count + 1, last_accessed = ?
                WHERE key = ?
                """,
                (int(time.time()), key),
            )
            conn.commit()

            self._stats["hits"] += 1
            return json.loads(value_blob.decode("utf-8"))

        except Exception as e:
            logger.error(f"L3 Knowledge Cache: Get error for {key}: {e}")
            self._stats["errors"] += 1
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in L3 cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional TTL in seconds
        """
        try:
            ttl = ttl or self.default_ttl
            value_blob = json.dumps(value).encode("utf-8")
            size_bytes = len(value_blob)
            now = int(time.time())
            ttl_at = now + ttl if ttl else None

            # Check if we need to evict
            self._evict_if_needed(size_bytes)

            conn = self._get_conn()
            conn.execute(
                """
                INSERT OR REPLACE INTO cache_entries
                (key, value, ttl_at, created_at, size_bytes, access_count, last_accessed)
                VALUES (?, ?, ?, ?, ?, 0, ?)
                """,
                (key, value_blob, ttl_at, now, size_bytes, now),
            )
            conn.commit()

        except Exception as e:
            logger.error(f"L3 Knowledge Cache: Set error for {key}: {e}")
            self._stats["errors"] += 1

    def delete(self, key: str) -> bool:
        """Delete key from L3 cache.

        Args:
            key: Cache key

        Returns:
            True if key was deleted, False otherwise
        """
        try:
            conn = self._get_conn()
            cursor = conn.execute(
                "DELETE FROM cache_entries WHERE key = ?",
                (key,),
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"L3 Knowledge Cache: Delete error for {key}: {e}")
            self._stats["errors"] += 1
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in L3 cache.

        Args:
            key: Cache key

        Returns:
            True if key exists and not expired, False otherwise
        """
        try:
            conn = self._get_conn()
            cursor = conn.execute(
                "SELECT ttl_at FROM cache_entries WHERE key = ?",
                (key,),
            )
            row = cursor.fetchone()

            if row is None:
                return False

            ttl_at = row[0]
            if ttl_at and time.time() > ttl_at:
                conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                conn.commit()
                return False

            return True

        except Exception as e:
            logger.error(f"L3 Knowledge Cache: Exists error for {key}: {e}")
            self._stats["errors"] += 1
            return False

    def clear(self) -> None:
        """Clear all entries from L3 cache."""
        try:
            conn = self._get_conn()
            conn.execute("DELETE FROM cache_entries")
            conn.commit()
        except Exception as e:
            logger.error(f"L3 Knowledge Cache: Clear error: {e}")
            self._stats["errors"] += 1

    def _evict_if_needed(self, new_size: int) -> None:
        """Evict old entries if cache is approaching limit.

        Uses LRU strategy with TTL expiration priority.
        """
        try:
            conn = self._get_conn()

            # Check current size
            cursor = conn.execute(
                "SELECT SUM(size_bytes) FROM cache_entries"
            )
            current_size = cursor.fetchone()[0] or 0

            if current_size + new_size > self.max_size:
                # Evict expired entries first
                conn.execute(
                    """
                    DELETE FROM cache_entries
                    WHERE ttl_at IS NOT NULL AND ttl_at < ?
                    """,
                    (int(time.time()),),
                )

                # If still over limit, evict by LRU
                target_size = int(self.max_size * 0.8)
                current_size = cursor.fetchone()[0]
                if current_size > target_size:
                    # Get LRU entries to delete, ordered by access time
                    cursor = conn.execute(
                        """
                        SELECT key, size_bytes FROM cache_entries
                        ORDER BY last_accessed ASC
                        """
                    )
                    size_to_free = current_size - target_size
                    freed_size = 0
                    keys_to_delete = []
                    
                    for key, size_bytes in cursor.fetchall():
                        if freed_size >= size_to_free:
                            break
                        keys_to_delete.append(key)
                        freed_size += size_bytes
                    
                    # Delete the selected keys
                    for key in keys_to_delete:
                        conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))

                conn.commit()

        except Exception as e:
            logger.error(f"L3 Knowledge Cache: Eviction error: {e}")
            self._stats["errors"] += 1

    def get_stats(self) -> dict[str, Any]:
        """Get L3 cache statistics.

        Returns:
            Dict with hit rates and storage info
        """
        try:
            conn = self._get_conn()

            # Get entry count and total size
            cursor = conn.execute(
                """
                SELECT COUNT(*), SUM(size_bytes), SUM(access_count)
                FROM cache_entries
                """
            )
            count, total_size, total_accesses = cursor.fetchone()
            count = count or 0
            total_size = total_size or 0
            total_accesses = total_accesses or 0

            # Get expired entries count
            cursor = conn.execute(
                """
                SELECT COUNT(*) FROM cache_entries
                WHERE ttl_at IS NOT NULL AND ttl_at < ?
                """,
                (int(time.time()),),
            )
            expired_count = cursor.fetchone()[0] or 0

            total_requests = self._stats["hits"] + self._stats["misses"]

            return {
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "errors": self._stats["errors"],
                "hit_rate": (
                    self._stats["hits"] / total_requests * 100 if total_requests > 0 else 0.0
                ),
                "entries": count,
                "size_bytes": total_size,
                "size_human": f"{total_size / (1024**3):.2f}GB",
                "utilization": total_size / self.max_size,
                "expired_entries": expired_count,
                "total_accesses": total_accesses,
            }

        except Exception as e:
            logger.error(f"L3 Knowledge Cache: Stats error: {e}")
            return {"error": str(e)}

    def cleanup_expired(self) -> int:
        """Remove expired entries from L3 cache.

        Returns:
            Number of entries cleaned up
        """
        try:
            conn = self._get_conn()
            cursor = conn.execute(
                """
                DELETE FROM cache_entries
                WHERE ttl_at IS NOT NULL AND ttl_at < ?
                """,
                (int(time.time()),),
            )
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            logger.error(f"L3 Knowledge Cache: Cleanup error: {e}")
            self._stats["errors"] += 1
            return 0


# Global L3 cache instance
_l3_cache_instance: Optional[L3KnowledgeCache] = None


def get_l3_cache() -> L3KnowledgeCache:
    """Get the global L3 cache instance (singleton)."""
    global _l3_cache_instance
    if _l3_cache_instance is None:
        _l3_cache_instance = L3KnowledgeCache()
    return _l3_cache_instance
