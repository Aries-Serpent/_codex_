"""
Embedding Cache Module

Provides caching for embedding vectors with:
- Memory-efficient numpy array storage
- Disk persistence support
- Batch caching operations
"""

import hashlib
import logging
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Union

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingCacheConfig:
    """Configuration for embedding cache."""
    
    max_entries: int = 10000  # Maximum number of embeddings
    enable_disk_cache: bool = False
    disk_cache_path: Optional[str] = None
    default_ttl: float = 3600.0  # 1 hour default TTL
    thread_safe: bool = True
    
    # Memory optimization
    use_float16: bool = False  # Use half precision to save memory


@dataclass
class EmbeddingEntry:
    """A cached embedding entry."""
    
    key: str
    embedding: np.ndarray
    created_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        return self.embedding.shape[0] if self.embedding.ndim == 1 else self.embedding.shape[-1]


class EmbeddingCache:
    """
    Cache for embedding vectors.
    
    Features:
    - Efficient numpy array storage
    - Optional disk persistence
    - Batch operations for bulk caching
    - Memory optimization with float16 option
    
    Example:
        cache = EmbeddingCache(EmbeddingCacheConfig(max_entries=5000))
        
        # Cache embedding
        cache.put("text1", embedding_vector)
        
        # Get embedding
        embedding = cache.get("text1")
        
        # Batch operations
        cache.put_batch(["text1", "text2"], [emb1, emb2])
        embeddings = cache.get_batch(["text1", "text2"])
    """
    
    def __init__(self, config: Optional[EmbeddingCacheConfig] = None):
        """Initialize embedding cache."""
        self.config = config or EmbeddingCacheConfig()
        
        self._cache: dict[str, EmbeddingEntry] = {}
        self._lock = threading.RLock() if self.config.thread_safe else None
        
        # Statistics
        self._hits = 0
        self._misses = 0
        
        # Disk cache path
        if self.config.enable_disk_cache and self.config.disk_cache_path:
            self._disk_path = Path(self.config.disk_cache_path)
            self._disk_path.mkdir(parents=True, exist_ok=True)
        else:
            self._disk_path = None
        
        logger.debug(
            f"EmbeddingCache initialized: max_entries={self.config.max_entries}, "
            f"disk_cache={self.config.enable_disk_cache}"
        )
    
    def _acquire_lock(self):
        """Acquire lock if thread-safe mode is enabled."""
        if self._lock:
            self._lock.acquire()
    
    def _release_lock(self):
        """Release lock if thread-safe mode is enabled."""
        if self._lock:
            self._lock.release()
    
    def _generate_key(self, text: str) -> str:
        """Generate cache key from text."""
        return hashlib.sha256(text.encode()).hexdigest()[:16]
    
    def _convert_embedding(self, embedding: np.ndarray) -> np.ndarray:
        """Convert embedding to configured dtype."""
        if self.config.use_float16:
            return embedding.astype(np.float16)
        return embedding.astype(np.float32)
    
    def _evict_oldest(self) -> None:
        """Evict oldest entries when at capacity."""
        if len(self._cache) < self.config.max_entries:
            return
        
        # Sort by created_at and remove oldest
        sorted_entries = sorted(
            self._cache.items(),
            key=lambda x: x[1].created_at
        )
        
        # Remove oldest 10%
        num_to_remove = max(1, len(sorted_entries) // 10)
        for key, _ in sorted_entries[:num_to_remove]:
            del self._cache[key]
        
        logger.debug(f"Evicted {num_to_remove} oldest entries")
    
    def get(self, text: str) -> Optional[np.ndarray]:
        """
        Get cached embedding for text.
        
        Args:
            text: Text that was embedded
            
        Returns:
            Embedding array or None if not found
        """
        key = self._generate_key(text)
        
        self._acquire_lock()
        try:
            if key not in self._cache:
                self._misses += 1
                
                # Try disk cache
                if self._disk_path:
                    disk_result = self._load_from_disk(key)
                    if disk_result is not None:
                        self._hits += 1
                        self._misses -= 1  # Correct the count
                        return disk_result
                
                return None
            
            entry = self._cache[key]
            
            # Check expiration
            if entry.is_expired:
                del self._cache[key]
                self._misses += 1
                return None
            
            self._hits += 1
            return entry.embedding.copy()  # Return copy to prevent modification
            
        finally:
            self._release_lock()
    
    def put(
        self,
        text: str,
        embedding: np.ndarray,
        ttl: Optional[float] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Store embedding in cache.
        
        Args:
            text: Text that was embedded
            embedding: Embedding vector
            ttl: Optional TTL in seconds
            metadata: Optional metadata
        """
        key = self._generate_key(text)
        ttl = ttl if ttl is not None else self.config.default_ttl
        
        self._acquire_lock()
        try:
            # Evict if at capacity
            self._evict_oldest()
            
            # Convert and store
            now = time.time()
            entry = EmbeddingEntry(
                key=key,
                embedding=self._convert_embedding(embedding),
                created_at=now,
                expires_at=now + ttl if ttl > 0 else None,
                metadata=metadata or {},
            )
            
            self._cache[key] = entry
            
            # Write to disk if enabled
            if self._disk_path:
                self._save_to_disk(key, entry)
            
        finally:
            self._release_lock()
    
    def get_batch(self, texts: list[str]) -> tuple[list[np.ndarray], list[int]]:
        """
        Get cached embeddings for multiple texts.
        
        Args:
            texts: List of texts
            
        Returns:
            Tuple of (found embeddings, indices of found items)
        """
        embeddings = []
        found_indices = []
        
        for i, text in enumerate(texts):
            emb = self.get(text)
            if emb is not None:
                embeddings.append(emb)
                found_indices.append(i)
        
        return embeddings, found_indices
    
    def put_batch(
        self,
        texts: list[str],
        embeddings: list[np.ndarray],
        ttl: Optional[float] = None,
    ) -> None:
        """
        Store multiple embeddings in cache.
        
        Args:
            texts: List of texts
            embeddings: List of embedding vectors
            ttl: Optional TTL for all entries
        """
        for text, embedding in zip(texts, embeddings):
            self.put(text, embedding, ttl)
    
    def contains(self, text: str) -> bool:
        """Check if text is in cache."""
        key = self._generate_key(text)
        
        self._acquire_lock()
        try:
            if key not in self._cache:
                return False
            return not self._cache[key].is_expired
        finally:
            self._release_lock()
    
    def delete(self, text: str) -> bool:
        """Delete embedding from cache."""
        key = self._generate_key(text)
        
        self._acquire_lock()
        try:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
        finally:
            self._release_lock()
    
    def clear(self) -> None:
        """Clear all entries from cache."""
        self._acquire_lock()
        try:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            logger.debug("Embedding cache cleared")
        finally:
            self._release_lock()
    
    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0.0
        
        # Calculate memory usage
        total_memory = sum(
            entry.embedding.nbytes
            for entry in self._cache.values()
        )
        
        return {
            "size": len(self._cache),
            "max_size": self.config.max_entries,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "memory_bytes": total_memory,
            "memory_mb": total_memory / (1024 * 1024),
            "dtype": "float16" if self.config.use_float16 else "float32",
        }
    
    def _save_to_disk(self, key: str, entry: EmbeddingEntry) -> None:
        """Save entry to disk cache."""
        if not self._disk_path:
            return
        
        try:
            file_path = self._disk_path / f"{key}.npy"
            np.save(file_path, entry.embedding)
        except Exception as e:
            logger.warning(f"Failed to save to disk cache: {e}")
    
    def _load_from_disk(self, key: str) -> Optional[np.ndarray]:
        """Load entry from disk cache."""
        if not self._disk_path:
            return None
        
        try:
            file_path = self._disk_path / f"{key}.npy"
            if file_path.exists():
                return np.load(file_path)
        except Exception as e:
            logger.warning(f"Failed to load from disk cache: {e}")
        
        return None
    
    def __len__(self) -> int:
        """Get number of entries in cache."""
        return len(self._cache)
    
    def __contains__(self, text: str) -> bool:
        """Check if text is in cache."""
        return self.contains(text)
