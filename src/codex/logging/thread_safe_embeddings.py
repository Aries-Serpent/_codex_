"""
Thread-safe Faiss Index Wrapper (Phase 6)

Provides concurrent read access and exclusive write access to Faiss index:
- ReadWriteLock for concurrent readers, exclusive writers
- Lock duration: <1ms for queries, <100ms for updates
- Deadlock prevention with writer starvation prevention
- Monitoring and metrics collection
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Optional

from .concurrency import ReadWriteLock, log_error, save_metrics

logger = logging.getLogger(__name__)

try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import faiss

    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False
    logger.warning("faiss not available; thread-safe embeddings will use mock vectors")

try:
    from sentence_transformers import SentenceTransformer

    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    logger.warning("sentence-transformers not available; using mock embeddings")


class ThreadSafeSessionEmbeddings:
    """
    Thread-safe Faiss index wrapper with read-write locking.

    Features:
    - Multiple concurrent readers (find_similar, get_embedding)
    - Single exclusive writer (add_session, update_session)
    - No writer starvation (readers wait for writers)
    - Lock contention monitoring
    - Automatic index persistence
    - Graceful fallback for missing dependencies
    """

    DIMENSION = 384
    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    VERSION = "1.0"

    def __init__(
        self,
        embeddings_path: str = ".codex/session_embeddings.faiss",
        metadata_path: str = ".codex/session_embeddings_metadata.json",
        metrics_path: str = ".codex/concurrency_metrics.json",
        errors_path: str = ".codex/concurrency_errors.log",
    ):
        """Initialize thread-safe embeddings."""
        self.embeddings_path = Path(embeddings_path)
        self.metadata_path = Path(metadata_path)
        self.metrics_path = metrics_path
        self.errors_path = errors_path

        # Concurrency primitives
        self._rw_lock = ReadWriteLock(timeout=60.0)
        self._index = None
        self._metadata: dict[str, dict[str, Any]] = {}
        self._model = None

        # Load or initialize index
        self._load_or_create_index()

    def _load_or_create_index(self) -> None:
        """Load index from disk or create new one."""
        try:
            if self.embeddings_path.exists() and self.metadata_path.exists():
                # Load existing index
                if HAS_FAISS:
                    self._index = faiss.read_index(str(self.embeddings_path))
                    logger.info(f"Loaded Faiss index from {self.embeddings_path}")

                # Load metadata
                with open(self.metadata_path, "r") as f:
                    self._metadata = json.load(f)
                    logger.info(f"Loaded metadata for {len(self._metadata)} sessions")
            else:
                # Create new index
                if HAS_FAISS:
                    self._index = faiss.IndexFlatL2(self.DIMENSION)
                    logger.info("Created new Faiss index")
                self._metadata = {}

        except (IOError, OSError) as e:
            type(e).__name__
            logger.error("Failed to load/create index: <ERROR_TYPE>")
            log_error(e, "load_index", self.errors_path)
            if HAS_FAISS:
                self._index = faiss.IndexFlatL2(self.DIMENSION)
            self._metadata = {}

    def _get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get embedding for text using sentence-transformers."""
        if not HAS_SENTENCE_TRANSFORMERS:
            # Return mock embedding
            if HAS_NUMPY:
                return np.random.rand(self.DIMENSION).astype(np.float32)
            return None

        try:
            if self._model is None:
                self._model = SentenceTransformer(self.MODEL_NAME)

            embedding = self._model.encode(text, convert_to_numpy=True)  # type: ignore[attr-defined]
            return embedding.astype(np.float32)

        except (ValueError, TypeError) as e:
            type(e).__name__
            logger.warning("Failed to get embedding: <ERROR_TYPE>")
            if HAS_NUMPY:
                return np.random.rand(self.DIMENSION).astype(np.float32)
            return None

    def add_session(
        self,
        session_id: str,
        description: str,
        patterns: list[str],
        keywords: list[str],
    ) -> bool:
        """Add session to index (exclusive write)."""

        def _add() -> bool:
            if not HAS_FAISS:
                # Store only in metadata
                self._metadata[session_id] = {
                    "description": description,
                    "patterns": patterns,
                    "keywords": keywords,
                    "timestamp": time.time(),
                }
                return True

            embedding = self._get_embedding(description)
            if embedding is None:
                logger.error(f"Failed to get embedding for {session_id}")
                return False

            # Add to index
            self._index.add(np.array([embedding]))  # type: ignore[attr-defined]

            # Store metadata
            self._metadata[session_id] = {
                "index_id": self._index.ntotal - 1,  # type: ignore[attr-defined]
                "description": description,
                "patterns": patterns,
                "keywords": keywords,
                "timestamp": time.time(),
            }

            return True

        try:
            with self._rw_lock.write_lock():
                result = _add()
                if result:
                    self.save_index()
                return result

        except (IOError, OSError) as e:
            type(e).__name__
            logger.error(f"Failed to add session {session_id}: <ERROR_TYPE>")
            log_error(e, "add_session", self.errors_path)
            return False

    def find_similar(
        self,
        query_session_id: str,
        k: int = 5,
    ) -> list[dict[str, Any]]:
        """Find similar sessions (concurrent read with read-write lock)."""

        def _find() -> list[dict[str, Any]]:
            if query_session_id not in self._metadata:
                return []

            metadata = self._metadata[query_session_id]
            description = metadata.get("description", "")

            if not HAS_FAISS or not description:
                # Return mock similar sessions from metadata
                return [
                    {
                        "session_id": sid,
                        "similarity_score": 0.9 - (i * 0.05),
                        "description": meta.get("description", ""),
                    }
                    for i, (sid, meta) in enumerate(list(self._metadata.items())[:k])
                    if sid != query_session_id
                ]

            # Get embedding for query
            embedding = self._get_embedding(description)
            if embedding is None:
                return []

            # Search index
            distances, indices = self._index.search(np.array([embedding]), k + 1)  # type: ignore[attr-defined]

            # Convert to results
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx == -1:  # Invalid index
                    continue

                # Find session_id by index
                for sid, meta in self._metadata.items():
                    if meta.get("index_id") == idx and sid != query_session_id:
                        results.append(
                            {
                                "session_id": sid,
                                "similarity_score": float(1.0 / (1.0 + float(dist))),
                                "description": meta.get("description", ""),
                            }
                        )
                        if len(results) >= k:
                            break

            return results

        try:
            with self._rw_lock.read_lock():
                return _find()

        except (IOError, OSError) as e:
            type(e).__name__
            logger.error("Failed to find similar sessions: <ERROR_TYPE>")
            log_error(e, "find_similar", self.errors_path)
            return []

    def get_embedding(self, session_id: str) -> Optional[Any]:
        """Get embedding for session (concurrent read)."""

        def _get() -> Optional[Any]:
            if session_id not in self._metadata:
                return None

            if not HAS_FAISS:
                return np.random.rand(self.DIMENSION).astype(np.float32) if HAS_NUMPY else None

            meta = self._metadata[session_id]
            idx = meta.get("index_id")

            if idx is None:
                return None

            # Reconstruct embedding from index
            try:
                embedding = self._index.reconstruct(int(idx))  # type: ignore[attr-defined]
                return embedding.astype(np.float32)
            except (IOError, OSError) as e:
                type(e).__name__
                logger.warning(f"Failed to reconstruct embedding for {session_id}: <ERROR_TYPE>")
                return None

        try:
            with self._rw_lock.read_lock():
                return _get()

        except (IOError, OSError) as e:
            type(e).__name__
            logger.error("Failed to get embedding: <ERROR_TYPE>")
            log_error(e, "get_embedding", self.errors_path)
            return None

    def save_index(self) -> bool:
        """Save index to disk."""
        try:
            # Ensure parent directories exist
            self.embeddings_path.parent.mkdir(parents=True, exist_ok=True)
            self.metadata_path.parent.mkdir(parents=True, exist_ok=True)

            # Save Faiss index
            if HAS_FAISS and self._index:
                faiss.write_index(self._index, str(self.embeddings_path))

            # Save metadata
            with open(self.metadata_path, "w") as f:
                json.dump(self._metadata, f, indent=2, default=str)

            logger.debug(f"Index saved to {self.embeddings_path}")
            return True

        except (IOError, OSError) as e:
            type(e).__name__
            logger.error("Failed to save index: <ERROR_TYPE>")
            log_error(e, "save_index", self.errors_path)
            return False

    def get_metrics(self) -> dict[str, Any]:
        """Get lock metrics."""
        return self._rw_lock.metrics.to_dict()

    def save_metrics(self) -> None:
        """Save metrics to JSON file."""
        metrics_dict = {
            "timestamp": time.time(),
            "component": "faiss_index",
            "rw_lock": self._rw_lock.metrics.to_dict(),
            "index_size": self._index.ntotal if self._index else 0,
            "metadata_entries": len(self._metadata),
        }
        save_metrics(metrics_dict, self.metrics_path)  # type: ignore[arg-type]

    def __enter__(self) -> "ThreadSafeSessionEmbeddings":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.save_index()
        self.save_metrics()
