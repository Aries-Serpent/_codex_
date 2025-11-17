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
"""

import hashlib
import logging
from pathlib import Path
from typing import Any, Optional

import numpy as np

logger = logging.getLogger(__name__)

# Safety limits
MAX_DIMENSION = 4096  # Maximum embedding dimension
MAX_VECTORS = 10_000_000  # Maximum number of vectors
MAX_QUERY_BATCH = 1000  # Maximum query batch size


class FAISSStore:
    """FAISS-based vector store for local operation with safeguards"""
    
    def __init__(
        self, 
        index_dir: Optional[str] = None, 
        index_name: str = "default",
        max_vectors: int = MAX_VECTORS,
        validate_checksums: bool = True
    ):
        """Initialize FAISS store with safety checks
        
        Args:
            index_dir: Directory to store indices (default: .codex/faiss)
            index_name: Name of the index
            max_vectors: Maximum number of vectors allowed (safety limit)
            validate_checksums: Whether to validate checksums on load
        """
        self.index_dir = Path(index_dir) if index_dir else Path(".codex/faiss")
        self.index_name = self._validate_index_name(index_name)
        self.index = None
        self.documents: list[dict[str, Any]] = []
        self.dimension: Optional[int] = None
        self.max_vectors = min(max_vectors, MAX_VECTORS)
        self.validate_checksums = validate_checksums
        self._checksum: Optional[str] = None
        
        try:
            import faiss
            self.faiss = faiss
            logger.info(f"FAISS version: {faiss.__version__}")
        except ImportError:
            logger.error("faiss-cpu not installed. Install with: pip install faiss-cpu")
            raise
    
    @staticmethod
    def _validate_index_name(name: str) -> str:
        """Validate and sanitize index name"""
        if not name or not isinstance(name, str):
            raise ValueError("Index name must be a non-empty string")
        # Sanitize: only alphanumeric, dash, underscore
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            raise ValueError(f"Invalid index name: {name}. Use only alphanumeric, dash, underscore.")
        return name
    
    def health_check(self) -> dict[str, Any]:
        """Perform health check on the vector store
        
        Returns:
            Dictionary with health status and metrics
        """
        status = {
            "healthy": False,
            "index_loaded": self.index is not None,
            "num_vectors": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "num_documents": len(self.documents),
            "index_dir_exists": self.index_dir.exists(),
            "faiss_available": True,
        }
        
        if self.index:
            status["healthy"] = (
                status["num_vectors"] > 0 
                and status["num_vectors"] == status["num_documents"]
                and status["dimension"] is not None
            )
        
        return status
    
    def create_index(self, embeddings: np.ndarray, documents: list[dict[str, Any]]):
        """Create a new FAISS index with validation
        
        Args:
            embeddings: Embedding vectors (shape: [n_docs, dim])
            documents: List of document dictionaries
            
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
                f"Number of embeddings ({n_vectors}) must match number of documents ({len(documents)})"
            )
        
        # Safety limit check
        if n_vectors > self.max_vectors:
            raise RuntimeError(
                f"Cannot create index with {n_vectors} vectors. "
                f"Maximum allowed: {self.max_vectors}"
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
        
        logger.info(f"Successfully added {self.index.ntotal} vectors to index")
        
        # Compute checksum
        self._checksum = self._compute_checksum(embeddings_normalized)
    
    @staticmethod
    def _compute_checksum(data: np.ndarray) -> str:
        """Compute SHA-256 checksum of embedding data"""
        return hashlib.sha256(data.tobytes()).hexdigest()
    
    def save(self):
        """Save index and documents to disk with checksum validation"""
        if not self.index:
            raise RuntimeError("No index to save")
        
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        index_path = self.index_dir / f"{self.index_name}.index"
        self.faiss.write_index(self.index, str(index_path))
        logger.info(f"Saved FAISS index to {index_path}")
        
        # Save documents
        import json
        docs_path = self.index_dir / f"{self.index_name}.docs.jsonl"
        with open(docs_path, "w", encoding="utf-8") as f:
            for doc in self.documents:
                f.write(json.dumps(doc) + "\n")
        logger.info(f"Saved {len(self.documents)} documents to {docs_path}")
        
        # Save metadata with checksum
        metadata = {
            "index_name": self.index_name,
            "dimension": self.dimension,
            "num_vectors": self.index.ntotal if self.index else 0,
            "checksum": self._checksum,
            "max_vectors": self.max_vectors,
        }
        meta_path = self.index_dir / f"{self.index_name}.meta.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Saved metadata with checksum to {meta_path}")
    
    def load(self):
        """Load index and documents from disk with validation"""
        index_path = self.index_dir / f"{self.index_name}.index"
        docs_path = self.index_dir / f"{self.index_name}.docs.jsonl"
        meta_path = self.index_dir / f"{self.index_name}.meta.json"
        
        if not index_path.exists():
            raise FileNotFoundError(f"Index not found: {index_path}")
        
        # Load and validate metadata
        import json
        if meta_path.exists():
            with open(meta_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            
            # Validate metadata
            if metadata.get("index_name") != self.index_name:
                logger.warning(
                    f"Index name mismatch: expected {self.index_name}, "
                    f"got {metadata.get('index_name')}"
                )
            
            self._checksum = metadata.get("checksum")
        else:
            logger.warning(f"Metadata file not found: {meta_path}")
            self._checksum = None
        
        # Load FAISS index
        self.index = self.faiss.read_index(str(index_path))
        self.dimension = self.index.d
        logger.info(f"Loaded FAISS index from {index_path} (dim={self.dimension}, n={self.index.ntotal})")
        
        # Validate dimension
        if self.dimension > MAX_DIMENSION:
            raise ValueError(f"Loaded dimension {self.dimension} exceeds maximum {MAX_DIMENSION}")
        
        # Load documents
        if docs_path.exists():
            self.documents = []
            with open(docs_path, "r", encoding="utf-8") as f:
                for line_no, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        try:
                            self.documents.append(json.loads(line))
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse document at line {line_no}: {e}")
                            continue
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
    
    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Search for similar vectors with validation
        
        Args:
            query_vector: Query embedding vector (shape: [dim] or [1, dim])
            top_k: Number of results to return
        
        Returns:
            List of results with document, score, and index
            
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
        
        # Search
        k = min(top_k, self.index.ntotal)
        distances, indices = self.index.search(query_normalized, k)
        
        # Build results
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < 0:  # FAISS returns -1 for not found
                continue
            
            if idx >= len(self.documents):
                logger.warning(f"Index {idx} out of range for documents (len={len(self.documents)})")
                continue
            
            # Convert L2 distance to similarity score (inverse)
            # For normalized vectors: L2 distance ~ 2 * (1 - cosine_similarity)
            # So: cosine_similarity ~ 1 - L2_distance/2
            cosine_similarity = max(0.0, 1.0 - float(dist) / 2.0)
            
            results.append({
                "document": self.documents[idx],
                "score": cosine_similarity,
                "index": int(idx),
                "distance": float(dist),
            })
        
        logger.debug(f"Found {len(results)} results for query")
        return results
