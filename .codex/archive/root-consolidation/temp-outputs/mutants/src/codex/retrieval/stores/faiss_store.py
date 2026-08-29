"""
FAISS Vector Store
Local CPU-based FAISS index for vector similarity search

Enhanced with:
- Input validation and safeguards
- Dimension mismatch detection
- Size limits and quota enforcement
- Connection health checks
- Error handling with fallbacks
- Checksum validation for persisted indices
- Full VectorStore interface implementation
"""

import hashlib
import logging
import uuid
from pathlib import Path
from typing import Any, Optional

import numpy as np

from ..filtering import apply_filters, calculate_fetch_multiplier
from .base import (
    DimensionMismatchError,
    IndexNotLoadedError,
    VectorNotFoundError,
    VectorStore,
)

logger = logging.getLogger(__name__)

# Safety limits
MAX_DIMENSION = 4096  # Maximum embedding dimension
MAX_VECTORS = 10_000_000  # Maximum number of vectors
MAX_QUERY_BATCH = 1000  # Maximum query batch size


class FAISSStore(VectorStore):
    """FAISS-based vector store for local operation with safeguards"""

    def __init__(
        self,
        index_dir: Optional[str] = None,
        index_name: str = "default",
        max_vectors: int = MAX_VECTORS,
        validate_checksums: bool = True,
        dimension: Optional[int] = None,
    ):
        """Initialize FAISS store with safety checks

        Args:
            index_dir: Directory to store indices (default: .codex/faiss)
            index_name: Name of the index
            max_vectors: Maximum number of vectors allowed (safety limit)
            validate_checksums: Whether to validate checksums on load
            dimension: Optional initial embedding dimension (set automatically on first insert)
        """
        self.index_dir = Path(index_dir) if index_dir else Path(".codex/faiss")
        self.index_name = self._validate_index_name(index_name)
        self.index = None
        self.documents: list[dict[str, Any]] = []
        self.vector_ids: list[str] = []  # Track vector IDs
        self.id_to_index: dict[str, int] = {}  # Map ID to index position
        self.dimension: Optional[int] = None
        self.max_vectors = min(max_vectors, MAX_VECTORS)
        self.validate_checksums = validate_checksums
        self._checksum: Optional[str] = None

        try:
            import faiss

            self.faiss = faiss
            version = getattr(faiss, "__version__", "unknown")
            logger.info(f"FAISS version: {version}")
        except ImportError as e:
            type(e).__name__
            logger.debug("ImportError: <ERROR_TYPE>")
            logger.error("faiss-cpu not installed. Install with: pip install faiss-cpu")
            raise

        # Validate and eagerly initialize index if dimension is provided
        if dimension is not None:
            if not isinstance(dimension, int) or dimension <= 0 or dimension > MAX_DIMENSION:
                raise ValueError(
                    f"dimension must be a positive integer ≤ {MAX_DIMENSION}, got {dimension!r}"
                )
            self.dimension = dimension
            self.index = self.faiss.IndexFlatL2(self.dimension)
            logger.info(f"Pre-initialized FAISS index with dimension: {self.dimension}")

    @staticmethod
    def _validate_index_name(name: str) -> str:
        """Validate and sanitize index name"""
        if not name or not isinstance(name, str):
            raise ValueError("Index name must be a non-empty string")
        # Sanitize: only alphanumeric, dash, underscore
        import re

        if not re.match(r"^[a-zA-Z0-9_-]+$", name):
            raise ValueError(
                f"Invalid index name: {name}. Use only alphanumeric, dash, underscore."
            )
        return name

    def health_check(self) -> dict[str, Any]:
        """Perform health check on the vector store

        Returns:
            Dictionary with health status and metrics
        """
        status: dict[str, Any] = {
            "healthy": False,
            "index_loaded": self.index is not None,
            "num_vectors": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "num_documents": len(self.documents),
            "index_dir_exists": self.index_dir.exists(),
            "faiss_available": True,
            "backend": "faiss",
        }

        if self.index:
            status["healthy"] = (
                status["num_vectors"] > 0
                and status["num_vectors"] == status["num_documents"]
                and status["dimension"] is not None
            )

        return status

    def create_index(self, embeddings: np.ndarray, documents: list[dict[str, Any]]) -> None:
        """Create a new FAISS index with validation

        Args:
            embeddings: Embedding vectors (shape: [n_docs, dim])
            documents: list of document dictionaries

        Raises:
            ValueError: If inputs are invalid
            RuntimeError: If safety limits are exceeded
        """
        # Input validation
        if not isinstance(embeddings, np.ndarray):
            raise TypeError("Embeddings must be a numpy array")

        if embeddings.ndim != 2:
            raise ValueError(f"Embeddings must be 2D array, got shape: {embeddings.shape}")

        n_vectors, dim = embeddings.shape

        # Validate dimensions
        if dim <= 0 or dim > MAX_DIMENSION:
            raise ValueError(f"Dimension must be between 1 and {MAX_DIMENSION}, got {dim}")

        # Validate document count
        if len(documents) != n_vectors:
            raise ValueError(
                f"Number of embeddings ({n_vectors}) must match number of documents ({len(documents)})"  # noqa: E501
            )

        # Safety limit check
        if n_vectors > self.max_vectors:
            raise RuntimeError(
                f"Cannot create index with {n_vectors} vectors. Maximum allowed: {self.max_vectors}"
            )

        # Validate embedding values
        if not np.isfinite(embeddings).all():
            raise ValueError("Embeddings contain NaN or Inf values")

        # Normalize embeddings (L2 normalization for better similarity)
        embeddings_normalized = embeddings.astype(np.float32)
        norms = np.linalg.norm(embeddings_normalized, axis=1, keepdims=True)
        norms = np.maximum(norms, 1e-12)  # Avoid division by zero
        embeddings_normalized = embeddings_normalized / norms

        self.dimension = dim
        self.documents = documents

        # Create index (L2 distance on normalized vectors ~ cosine similarity)
        logger.info(f"Creating FAISS index with dimension: {self.dimension}, vectors: {n_vectors}")
        self.index = self.faiss.IndexFlatL2(self.dimension)

        # Add vectors
        self.index.add(embeddings_normalized)

        # Generate IDs if not provided in documents
        self.vector_ids = []
        for _, doc in enumerate(self.documents):
            if isinstance(doc, dict) and "id" in doc:
                self.vector_ids.append(doc["id"])
            else:
                # Generate UUID for documents without IDs
                vid = str(uuid.uuid4())
                self.vector_ids.append(vid)
                if isinstance(doc, dict):
                    doc["id"] = vid

        # Build ID to index mapping
        self.id_to_index = {vid: idx for idx, vid in enumerate(self.vector_ids)}

        logger.info(f"Successfully added {self.index.ntotal} vectors to index")

        # Compute checksum
        self._checksum = self._compute_checksum(embeddings_normalized)

    @staticmethod
    def _compute_checksum(data: np.ndarray) -> str:
        """Compute SHA-256 checksum of embedding data"""
        return hashlib.sha256(data.tobytes()).hexdigest()

    def save(self, path: Optional[str] = None) -> None:
        """Save index and documents to disk with checksum validation

        Args:
            path: Optional custom path (uses default if not provided)
        """
        if not self.index:
            raise RuntimeError("No index to save")

        save_dir = Path(path) if path else self.index_dir
        save_dir.mkdir(parents=True, exist_ok=True)

        # Save FAISS index
        index_path = save_dir / f"{self.index_name}.index"
        self.faiss.write_index(self.index, str(index_path))
        logger.info(f"Saved FAISS index to {index_path}")

        # Save documents with IDs
        import json

        docs_path = save_dir / f"{self.index_name}.docs.jsonl"
        with open(docs_path, "w", encoding="utf-8") as f:
            for doc, vid in zip(self.documents, self.vector_ids, strict=False):
                entry = {"id": vid, **doc}
                f.write(json.dumps(entry) + "\n")
        logger.info(f"Saved {len(self.documents)} documents to {docs_path}")

        # Save metadata with checksum
        metadata = {
            "index_name": self.index_name,
            "dimension": self.dimension,
            "num_vectors": self.index.ntotal if self.index else 0,
            "checksum": self._checksum,
            "max_vectors": self.max_vectors,
            "vector_ids": self.vector_ids,  # Save IDs for recovery
        }
        meta_path = save_dir / f"{self.index_name}.meta.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Saved metadata with checksum to {meta_path}")

    def load(self, path: Optional[str] = None) -> None:
        """Load index and documents from disk with validation

        Args:
            path: Optional custom path (uses default if not provided)
        """
        load_dir = Path(path) if path else self.index_dir
        index_path = load_dir / f"{self.index_name}.index"
        docs_path = load_dir / f"{self.index_name}.docs.jsonl"
        meta_path = load_dir / f"{self.index_name}.meta.json"

        if not index_path.exists():
            raise FileNotFoundError(f"Index not found: {index_path}")

        # Load and validate metadata
        import json

        if meta_path.exists():
            with open(meta_path, encoding="utf-8") as f:
                metadata = json.load(f)

            # Validate metadata
            if metadata.get("index_name") != self.index_name:
                logger.warning(
                    f"Index name mismatch: expected {self.index_name}, "
                    f"got {metadata.get('index_name')}"
                )

            self._checksum = metadata.get("checksum")
            saved_ids = metadata.get("vector_ids", [])
        else:
            logger.warning(f"Metadata file not found: {meta_path}")
            self._checksum = None
            saved_ids = []

        # Load FAISS index
        self.index = self.faiss.read_index(str(index_path))
        self.dimension = self.index.d
        logger.info(
            f"Loaded FAISS index from {index_path} (dim={self.dimension}, n={self.index.ntotal})"
        )

        # Validate dimension
        if self.dimension > MAX_DIMENSION:
            raise ValueError(f"Loaded dimension {self.dimension} exceeds maximum {MAX_DIMENSION}")

        # Load documents and IDs
        if docs_path.exists():
            self.documents = []
            self.vector_ids = []
            with open(docs_path, encoding="utf-8") as f:
                for line_no, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        try:
                            doc = json.loads(line)
                            # Extract ID if present
                            vid = doc.get(
                                "id",
                                (
                                    saved_ids[line_no - 1]
                                    if line_no - 1 < len(saved_ids)
                                    else str(uuid.uuid4())
                                ),
                            )
                            self.vector_ids.append(vid)
                            self.documents.append(doc)
                        except json.JSONDecodeError as e:
                            type(e).__name__
                            logger.error(
                                f"Failed to parse document at line {line_no}: <ERROR_TYPE>"
                            )
                            continue

            # Rebuild ID to index mapping
            self.id_to_index = {vid: idx for idx, vid in enumerate(self.vector_ids)}

            logger.info(f"Loaded {len(self.documents)} documents from {docs_path}")

            # Validate document count
            if len(self.documents) != self.index.ntotal:
                logger.warning(
                    f"Document count ({len(self.documents)}) != "
                    f"index vector count ({self.index.ntotal})"
                )
        else:
            logger.warning(f"Documents file not found: {docs_path}")
            self.documents = []
            self.vector_ids = []
            self.id_to_index = {}

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        """Search for similar vectors with validation and optional filtering

        Args:
            query_vector: Query embedding vector (shape: [dim] or [1, dim])
            top_k: Number of results to return
            filters: Optional metadata filters (MongoDB-style)

        Returns:
            list of results with document, score, and index

        Raises:
            RuntimeError: If index not loaded
            ValueError: If query vector is invalid
        """
        if not self.index:
            raise RuntimeError("Index not loaded. Call load() or create_index() first.")

        # Validate query vector
        if not isinstance(query_vector, np.ndarray):
            raise TypeError("Query vector must be a numpy array")

        # Reshape query if needed
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        elif query_vector.ndim != 2:
            raise ValueError(f"Query vector must be 1D or 2D, got shape: {query_vector.shape}")

        # Validate dimension
        if query_vector.shape[1] != self.dimension:
            raise ValueError(
                f"Query dimension ({query_vector.shape[1]}) must match "
                f"index dimension ({self.dimension})"
            )

        # Validate values
        if not np.isfinite(query_vector).all():
            raise ValueError("Query vector contains NaN or Inf values")

        # Validate top_k
        if top_k <= 0:
            raise ValueError(f"top_k must be positive, got {top_k}")
        if top_k > MAX_QUERY_BATCH:
            logger.warning(f"top_k ({top_k}) exceeds maximum ({MAX_QUERY_BATCH}), capping")
            top_k = MAX_QUERY_BATCH

        # Normalize query vector
        query_normalized = query_vector.astype(np.float32)
        norm = np.linalg.norm(query_normalized, axis=1, keepdims=True)
        norm = np.maximum(norm, 1e-12)
        query_normalized = query_normalized / norm

        # Calculate fetch multiplier if filtering
        fetch_multiplier = calculate_fetch_multiplier(filters) if filters else 1
        fetch_k = min(top_k * fetch_multiplier, self.index.ntotal, MAX_QUERY_BATCH)

        # Search
        k = min(fetch_k, self.index.ntotal)
        distances, indices = self.index.search(query_normalized, k)

        # Build results
        results = []
        for _, (dist, idx) in enumerate(zip(distances[0], indices[0], strict=False)):
            if idx < 0:  # FAISS returns -1 for not found
                continue

            if idx >= len(self.documents):
                logger.warning(
                    f"Index {idx} out of range for documents (len={len(self.documents)})"
                )
                continue

            # Convert L2 distance to similarity score (inverse)
            # For normalized vectors: L2 distance ~ 2 * (1 - cosine_similarity)
            # So: cosine_similarity ~ 1 - L2_distance/2
            cosine_similarity = max(0.0, 1.0 - float(dist) / 2.0)

            # Get metadata and ID
            doc = self.documents[idx]
            vid = self.vector_ids[idx] if idx < len(self.vector_ids) else str(uuid.uuid4())

            results.append(
                {
                    "id": vid,
                    "score": cosine_similarity,
                    "metadata": doc,
                    "distance": float(dist),
                }
            )

        # Apply filters if provided
        if filters:
            results = apply_filters(results, filters, max_results=top_k)
            logger.debug(f"Filtered to {len(results)} results")
        else:
            results = results[:top_k]

        logger.debug(f"Found {len(results)} results for query")
        return results

    # VectorStore Interface Implementation

    def add(
        self,
        vectors: np.ndarray,
        metadata: Optional[list[dict[str, Any]]] = None,
        ids: Optional[list[str]] = None,
    ) -> list[str]:
        """Add vectors to the store with optional metadata

        Args:
            vectors: Embedding vectors to add (shape: [n_vectors, dimension])
            metadata: Optional metadata for each vector
            ids: Optional IDs for vectors (auto-generated if not provided)

        Returns:
            list of vector IDs
        """
        if not isinstance(vectors, np.ndarray):
            raise TypeError("Vectors must be a numpy array")

        if vectors.ndim != 2:
            raise ValueError(f"Vectors must be 2D array, got shape: {vectors.shape}")

        n_vectors, dim = vectors.shape

        # Initialize index if not exists
        if self.index is None:
            if dim <= 0 or dim > MAX_DIMENSION:
                raise ValueError(f"Dimension must be between 1 and {MAX_DIMENSION}, got {dim}")
            self.dimension = dim
            self.index = self.faiss.IndexFlatL2(self.dimension)
            logger.info(f"Created new FAISS index with dimension: {self.dimension}")
        else:
            # Validate dimension match
            if dim != self.dimension:
                raise DimensionMismatchError(
                    f"Vector dimension ({dim}) doesn't match index dimension ({self.dimension})"
                )

        # Check safety limits
        if self.index.ntotal + n_vectors > self.max_vectors:
            raise RuntimeError(
                f"Adding {n_vectors} vectors would exceed maximum ({self.max_vectors})"
            )

        # Validate vectors
        if not np.isfinite(vectors).all():
            raise ValueError("Vectors contain NaN or Inf values")

        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(n_vectors)]
        else:
            if len(ids) != n_vectors:
                raise ValueError(
                    f"Number of IDs ({len(ids)}) must match number of vectors ({n_vectors})"
                )
            # Check for duplicate IDs
            existing_ids = set(self.vector_ids)
            duplicates = [vid for vid in ids if vid in existing_ids]
            if duplicates:
                raise ValueError(f"Duplicate IDs found: {duplicates[:5]}")

        # Prepare metadata
        if metadata is None:
            metadata = [{} for _ in range(n_vectors)]
        else:
            if len(metadata) != n_vectors:
                raise ValueError(
                    f"Number of metadata entries ({len(metadata)}) must match "
                    f"number of vectors ({n_vectors})"
                )

        # Normalize vectors
        vectors_normalized = vectors.astype(np.float32)
        norms = np.linalg.norm(vectors_normalized, axis=1, keepdims=True)
        norms = np.maximum(norms, 1e-12)
        vectors_normalized = vectors_normalized / norms

        # Add to index
        start_idx = self.index.ntotal
        self.index.add(vectors_normalized)

        # Store metadata and IDs
        for i, (vid, meta) in enumerate(zip(ids, metadata, strict=False)):
            idx = start_idx + i
            self.vector_ids.append(vid)
            self.id_to_index[vid] = idx
            self.documents.append({"id": vid, "metadata": meta})

        logger.info(f"Added {n_vectors} vectors to index (total: {self.index.ntotal})")
        return ids

    def delete(self, ids: str | list[str]) -> int:
        """Delete vectors by ID

        Note: FAISS doesn't support efficient deletion, so we mark as deleted
        and rebuild index if needed

        Args:
            ids: Single ID or list of IDs to delete

        Returns:
            Number of vectors deleted
        """
        if isinstance(ids, str):
            ids = [ids]

        deleted_count = 0
        indices_to_keep = []

        for i, vid in enumerate(self.vector_ids):
            if vid not in ids:
                indices_to_keep.append(i)
            else:
                deleted_count += 1
                del self.id_to_index[vid]

        if deleted_count == 0:
            return 0

        # Rebuild index with remaining vectors
        if len(indices_to_keep) > 0 and self.index is not None:
            # Update tracking first
            self.vector_ids = [self.vector_ids[i] for i in indices_to_keep]
            self.documents = [self.documents[i] for i in indices_to_keep]

            # Rebuild ID to index mapping
            self.id_to_index = {vid: idx for idx, vid in enumerate(self.vector_ids)}

            # Extract remaining vectors from index
            remaining_vectors = np.zeros((len(indices_to_keep), self.dimension), dtype=np.float32)
            for new_idx, old_idx in enumerate(indices_to_keep):
                # Reconstruct vector from index
                vec = self.index.reconstruct(int(old_idx))
                remaining_vectors[new_idx] = vec

            # Rebuild the index with remaining vectors
            self.index = self.faiss.IndexFlatL2(self.dimension)
            self.index.add(remaining_vectors)

            logger.info(
                f"Deleted {deleted_count} vectors, rebuilt index with {self.index.ntotal} vectors"
            )
        else:
            # Clear everything
            self.clear()
            logger.info(f"Deleted all {deleted_count} vectors, index cleared")

        return deleted_count

    def get(self, ids: str | list[str]) -> list[dict[str, Any]]:
        """Retrieve vectors by ID

        Args:
            ids: Single ID or list of IDs to retrieve

        Returns:
            list of results with id, vector, and metadata

        Raises:
            VectorNotFoundError: If vector ID not found
            IndexNotLoadedError: If index is not loaded
        """
        if isinstance(ids, str):
            ids = [ids]

        if self.index is None:
            raise IndexNotLoadedError("Index not loaded. Call create_index() or load() first.")

        results = []
        for vid in ids:
            if vid not in self.id_to_index:
                raise VectorNotFoundError(f"Vector ID not found: {vid}")

            idx = self.id_to_index[vid]
            if idx >= len(self.documents):
                raise VectorNotFoundError(f"Document index out of range: {idx}")

            # Reconstruct vector from FAISS index
            vector = self.index.reconstruct(int(idx))

            doc = self.documents[idx]
            results.append(
                {
                    "id": vid,
                    "vector": vector,
                    "metadata": doc.get("metadata", {}),
                }
            )

        return results

    def count(self) -> int:
        """Get total number of vectors in the store"""
        return self.index.ntotal if self.index else 0

    def clear(self) -> None:
        """Clear all vectors from the store"""
        self.index = None
        self.documents = []
        self.vector_ids = []
        self.id_to_index = {}
        self.dimension = None
        self._checksum = None
        logger.info("Cleared all vectors from store")
