"""
Semantic search for Copilot sessions via embeddings.

Uses Faiss for vector indexing and sentence-transformers for embeddings.
sentence-transformers is optional; falls back to mock embeddings if unavailable.

Usage:
    embeddings = SessionEmbeddings()
    embeddings.add_session("S293", "Query filtering", ["P-001"], ["database"])
    similar = embeddings.find_similar("S293", k=5)
    embeddings.save_index()

Storage:
    .codex/session_embeddings.faiss - Faiss index (binary)
    .codex/session_embeddings_metadata.json - Metadata (JSON)
"""

from __future__ import annotations

import json
import logging
import threading
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

# Optional imports with graceful fallback
try:
    import faiss

    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False
    logger.warning("faiss not available; SessionEmbeddings will use mock vectors")

try:
    from sentence_transformers import SentenceTransformer

    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    logger.warning("sentence-transformers not available; using mock embeddings")


class SessionEmbeddings:
    """Generate and manage session embeddings for semantic search.

    Attributes:
        embeddings_path: Path to save/load Faiss index
        metadata_path: Path to save/load metadata JSON
        dimension: Embedding dimension (384 for all-MiniLM-L6-v2)
        _embeddings: Faiss index (IndexFlatL2)
        _metadata: Dict mapping session_id -> index metadata
        _model: sentence-transformers model (lazy-loaded)
        _lock: Threading lock for thread-safe access
    """

    DIMENSION = 384
    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    VERSION = "1.0"

    def __init__(
        self,
        embeddings_path: str = ".codex/session_embeddings.faiss",
        metadata_path: str = ".codex/session_embeddings_metadata.json",
    ):
        """Initialize embeddings module.

        Args:
            embeddings_path: Path to Faiss index file
            metadata_path: Path to metadata JSON file
        """
        self.embeddings_path = Path(embeddings_path)
        self.metadata_path = Path(metadata_path)
        self._embeddings = None
        self._metadata: dict[str, Any] = {}
        self._model = None
        self._lock = threading.RLock()

        # Load existing index if available
        self._load_index()

    def _load_model(self) -> None:
        """Load sentence-transformers model.

        Falls back to mock embeddings if model unavailable.
        Model is cached for reuse.
        """
        if self._model is not None:
            return

        if HAS_SENTENCE_TRANSFORMERS:
            try:
                self._model = SentenceTransformer(self.MODEL_NAME)
                logger.info(f"Loaded model: {self.MODEL_NAME}")
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.warning("Failed to load model: <ERROR_TYPE>; using mock embeddings")
                self._model = None
        else:
            logger.info("Using mock embeddings (sentence-transformers not available)")

    def _normalize_text(self, text: str) -> str:
        """Normalize text for embedding.

        Args:
            text: Raw text

        Returns:
            Normalized text (lowercase, whitespace trimmed)
        """
        if not isinstance(text, str):
            text = str(text)
        return text.lower().strip()

    def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (384-dim, dtype=float32)

        Raises:
            ValueError: If embedding dimension mismatches expected
        """
        text = self._normalize_text(text)

        if not text:
            raise ValueError("Cannot embed empty text")

        if self._model is None:
            # Mock embedding (deterministic based on text)
            np.random.seed(hash(text) % 2**31)
            embedding = np.random.randn(self.DIMENSION).astype(np.float32)
        else:
            # Real embedding
            try:
                embedding = self._model.encode(text, convert_to_numpy=True)
            except (ValueError, TypeError) as e:
                type(e).__name__
                logger.error(f"Embedding failed for '{text[:50]}': <ERROR_TYPE>")
                raise

        embedding = embedding.astype(np.float32)
        if embedding.shape[0] != self.DIMENSION:
            raise ValueError(
                f"Dimension mismatch: got {embedding.shape[0]}, expected {self.DIMENSION}"
            )

        return embedding

    def _create_index(self) -> None:
        """Create new Faiss index."""
        if HAS_FAISS:
            self._embeddings = faiss.IndexFlatL2(self.DIMENSION)
        else:
            # Mock index using numpy
            self._embeddings = []  # type: ignore[assignment]

    def _load_index(self) -> None:
        """Load embeddings from disk or create new."""
        with self._lock:
            if self.embeddings_path.exists() and self.metadata_path.exists():
                try:
                    self._load_from_disk()
                except (IOError, OSError) as e:
                    type(e).__name__
                    logger.warning("Failed to load index: <ERROR_TYPE>; creating new index")
                    self._create_index()
                    self._metadata = {}
            else:
                self._create_index()
                self._metadata = {}

    def _load_from_disk(self) -> None:
        """Load Faiss index and metadata from disk."""
        # Load metadata
        if not self.metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {self.metadata_path}")

        with open(self.metadata_path, "r") as f:
            data = json.load(f)
            self._metadata = data.get("sessions", {})

        # Load Faiss index
        if HAS_FAISS:
            if self.embeddings_path.exists():
                self._embeddings = faiss.read_index(str(self.embeddings_path))
            else:
                self._create_index()
        else:
            # For testing without Faiss: reconstruct embeddings from disk
            self._embeddings = []  # type: ignore[assignment]
            if self.embeddings_path.exists():
                # Try to load pickled embeddings as fallback
                import pickle

                try:
                    with open(self.embeddings_path, "rb") as f:
                        self._embeddings = pickle.load(
                            f
                        )  # nosec B301 - trusted data only  # nosemgrep: semgrep.unsafe-pickle-load
                except (IOError, OSError):
                    self._embeddings = []  # type: ignore[assignment]

    def save_index(self) -> None:
        """Save embeddings to disk.

        Saves both Faiss index and metadata JSON atomically.
        Also saves embeddings as pickle if Faiss unavailable.
        """
        with self._lock:
            # Ensure directories exist
            self.embeddings_path.parent.mkdir(parents=True, exist_ok=True)
            self.metadata_path.parent.mkdir(parents=True, exist_ok=True)

            # Save Faiss index (or pickle as fallback)
            if self._embeddings is not None:
                if HAS_FAISS:
                    faiss.write_index(self._embeddings, str(self.embeddings_path))
                else:
                    # Save embeddings as pickle for fallback
                    import pickle

                    with open(self.embeddings_path, "wb") as f:
                        pickle.dump(self._embeddings, f)

            # Save metadata
            metadata_dict = {
                "version": self.VERSION,
                "model": self.MODEL_NAME,
                "dimension": self.DIMENSION,
                "total_sessions": len(self._metadata),
                "sessions": self._metadata,
            }

            # Atomic write (temp + rename)
            temp_path = self.metadata_path.with_suffix(".tmp")
            with open(temp_path, "w") as f:
                json.dump(metadata_dict, f, indent=2)
            temp_path.replace(self.metadata_path)

            logger.info(f"Saved index: {len(self._metadata)} sessions to {self.metadata_path}")

    def add_session(
        self,
        session_id: str,
        summary: str,
        patterns: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> bool:
        """Add session to embeddings index.

        Args:
            session_id: Unique session identifier
            summary: Session summary text
            patterns: List of pattern IDs (optional)
            tags: List of tags (optional)

        Returns:
            True if added successfully, False if error

        Side Effects:
            Updates self._embeddings and self._metadata
        """
        with self._lock:
            try:
                if not session_id or not summary:
                    logger.warning(f"Skipping invalid session: {session_id}")
                    return False

                # Combine text
                patterns = patterns or []
                tags = tags or []
                combined_text = f"{summary} {' '.join(patterns)} {' '.join(tags)}"

                # Generate embedding
                embedding = self._generate_embedding(combined_text)

                # Add to index
                if HAS_FAISS:
                    self._embeddings.add(np.array([embedding]))  # type: ignore[attr-defined]
                else:
                    self._embeddings.append(embedding)  # type: ignore[attr-defined]

                # Update metadata
                index = len(self._metadata)
                self._metadata[session_id] = {
                    "index": index,
                    "summary": summary,
                    "patterns": patterns,
                    "tags": tags,
                }

                logger.debug(f"Added session {session_id} (index {index})")
                return True

            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.error(f"Failed to add session {session_id}: <ERROR_TYPE>")
                return False

    def find_similar(self, session_id: str, k: int = 5) -> list[tuple[str, float]]:
        """Find k sessions most similar to given session.

        Args:
            session_id: Reference session ID
            k: Number of results to return

        Returns:
            List of (session_id, similarity_score) tuples
            Score is normalized to [0, 1] (0 = identical, 1 = completely different)
        """
        with self._lock:
            if session_id not in self._metadata:
                logger.warning(f"Session not found: {session_id}")
                return []

            index = self._metadata[session_id]["index"]

            # Get embedding
            if HAS_FAISS:
                embedding = self._embeddings.reconstruct(index)  # type: ignore[attr-defined]
            else:
                embedding = self._embeddings[index]  # type: ignore[index]

            return self._search(embedding, k, exclude_index=index)

    def find_similar_text(self, query_text: str, k: int = 5) -> list[tuple[str, float]]:
        """Find k sessions similar to query text.

        Args:
            query_text: Query text
            k: Number of results to return

        Returns:
            List of (session_id, similarity_score) tuples
        """
        with self._lock:
            try:
                embedding = self._generate_embedding(query_text)
                return self._search(embedding, k)
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.error("Failed to search: <ERROR_TYPE>")
                return []

    def _search(
        self, query_embedding: np.ndarray, k: int, exclude_index: int | None = None
    ) -> list[tuple[str, float]]:
        """Internal search implementation.

        Args:
            query_embedding: Query vector
            k: Number of results
            exclude_index: Index to exclude (optional, for find_similar)

        Returns:
            List of (session_id, similarity_score) tuples
        """
        if len(self._metadata) == 0:
            return []

        # Ensure k doesn't exceed available sessions
        k = min(k, len(self._metadata))

        # Perform search
        if HAS_FAISS:
            distances, indices = self._embeddings.search(  # type: ignore[attr-defined]
                np.array([query_embedding]), k + (1 if exclude_index is not None else 0)
            )
            distances = distances[0]
            indices = indices[0]
        else:
            # Mock search using numpy
            embeddings_array = np.array(self._embeddings, dtype=np.float32)
            distances = np.linalg.norm(embeddings_array - query_embedding, axis=1)
            indices = np.argsort(distances)

        # Build results
        results = []
        reverse_metadata = {v["index"]: k for k, v in self._metadata.items()}

        for idx, dist in zip(indices, distances):
            if exclude_index is not None and idx == exclude_index:
                continue

            if idx in reverse_metadata:
                session_id = reverse_metadata[idx]
                # Normalize L2 distance to [0, 1]
                # L2 distance ranges from 0 (identical) to ~sqrt(2*dim) (opposite)
                score = float(np.clip(dist / (2 * self.DIMENSION) ** 0.5, 0, 1))
                results.append((session_id, score))

            if len(results) >= k:
                break

        return results

    def get_metadata(self, session_id: str) -> dict[str, Any]:
        """Get metadata for a session.

        Args:
            session_id: Session ID

        Returns:
            Metadata dict or empty dict if not found
        """
        with self._lock:
            return self._metadata.get(session_id, {})

    def list_sessions(self) -> list[str]:
        """List all session IDs in index.

        Returns:
            List of session IDs
        """
        with self._lock:
            return list(self._metadata.keys())

    def rebuild_index(self) -> bool:
        """Rebuild entire index from metadata.

        Useful for maintenance after corruptions.
        Returns True if successful, False otherwise.
        """
        with self._lock:
            try:
                # Save old metadata
                old_metadata = self._metadata.copy()

                # Create new index
                self._create_index()
                self._metadata = {}

                # Re-add all sessions
                for session_id, meta in old_metadata.items():
                    self.add_session(
                        session_id,
                        meta.get("summary", ""),
                        meta.get("patterns", []),
                        meta.get("tags", []),
                    )

                logger.info(f"Rebuilt index with {len(self._metadata)} sessions")
                return True

            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.error("Rebuild failed: <ERROR_TYPE>")
                self._metadata = old_metadata
                return False

    def get_stats(self) -> dict[str, Any]:
        """Get index statistics.

        Returns:
            Dict with stats (sessions_count, dimension, model, etc.)
        """
        with self._lock:
            return {
                "total_sessions": len(self._metadata),
                "dimension": self.DIMENSION,
                "model": self.MODEL_NAME,
                "has_faiss": HAS_FAISS,
                "has_model": HAS_SENTENCE_TRANSFORMERS,
                "embeddings_path": str(self.embeddings_path),
                "metadata_path": str(self.metadata_path),
            }
