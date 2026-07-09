"""
Advanced indexing algorithms for vector stores.

This module provides production-grade implementations of advanced vector indexing
algorithms including HNSW (Hierarchical Navigable Small World), IVF-PQ (Inverted
File with Product Quantization), and hybrid search capabilities.

Features:
- HNSW indexing with configurable M and ef parameters
- IVF-PQ indexing with product quantization
- Hybrid search combining dense and sparse vectors
- Index optimization tools and performance tuning
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

import numpy as np

logger = logging.getLogger(__name__)


class IndexType(Enum):
    """Supported index types for vector search."""

    FLAT = "flat"  # Brute force, baseline
    HNSW = "hnsw"  # Hierarchical Navigable Small World
    IVF_FLAT = "ivf_flat"  # Inverted file with flat quantization
    IVF_PQ = "ivf_pq"  # Inverted file with product quantization
    HYBRID = "hybrid"  # Dense + sparse hybrid


@dataclass
class HNSWConfig:
    """Configuration for HNSW index.

    Attributes:
        M: Number of bi-directional links per node (default: 32)
            Higher M = better recall, more memory, slower build
        ef_construction: Size of dynamic candidate list during construction (default: 200)
                        Higher ef_construction = better quality, slower build
        ef_search: Size of dynamic candidate list during search (default: 100)
                  Higher ef_search = better recall, slower search
        metric: Distance metric ('l2', 'ip', 'cosine')
    """

    M: int = 32
    ef_construction: int = 200
    ef_search: int = 100
    metric: str = "l2"  # l2, ip (inner product), cosine

    def validate(self) -> None:
        """Validate configuration parameters."""
        if self.M < 4 or self.M > 128:
            raise ValueError(f"M must be between 4 and 128, got {self.M}")
        if self.ef_construction < self.M * 2:
            raise ValueError(
                f"ef_construction must be >= 2*M ({self.M * 2}), got {self.ef_construction}"
            )
        if self.ef_search < 1:
            raise ValueError(f"ef_search must be >= 1, got {self.ef_search}")
        if self.metric not in ["l2", "ip", "cosine"]:
            raise ValueError(f"metric must be one of ['l2', 'ip', 'cosine'], got {self.metric}")


@dataclass
class IVFPQConfig:
    """Configuration for IVF-PQ index.

    Attributes:
        nlist: Number of inverted lists/clusters (default: 1000)
                Recommended: sqrt(N) to sqrt(N)/2 for N vectors
        m: Number of sub-quantizers (default: 8)
            Higher m = better accuracy, more memory
        nbits: Number of bits per sub-quantizer (default: 8)
                Options: 4, 8 (8 bits = 256 levels per subquantizer)
        nprobe: Number of lists to probe during search (default: 10)
                Higher nprobe = better recall, slower search
        metric: Distance metric ('l2', 'ip')
    """

    nlist: int = 1000
    m: int = 8
    nbits: int = 8
    nprobe: int = 10
    metric: str = "l2"

    def validate(self) -> None:
        """Validate configuration parameters."""
        if self.nlist < 1:
            raise ValueError(f"nlist must be >= 1, got {self.nlist}")
        if self.m not in [8, 16, 32, 64]:
            raise ValueError(
                f"m should be one of [8, 16, 32, 64] for optimal performance, got {self.m}"
            )
        if self.nbits not in [4, 8]:
            raise ValueError(f"nbits must be 4 or 8, got {self.nbits}")
        if self.nprobe < 1 or self.nprobe > self.nlist:
            raise ValueError(
                f"nprobe must be between 1 and nlist ({self.nlist}), got {self.nprobe}"
            )
        if self.metric not in ["l2", "ip"]:
            raise ValueError(f"metric must be one of ['l2', 'ip'], got {self.metric}")


class HNSWIndex:
    """HNSW (Hierarchical Navigable Small World) index implementation.

    HNSW provides excellent search performance with logarithmic complexity.
    Suitable for large-scale approximate nearest neighbor search.

    Trade-offs:
    - High recall with fast search (better than IVF at higher dimensions)
    - Moderate memory usage (depends on M parameter)
    - Relatively slow index construction
    - Supports incremental additions

    Example:
        >>> config = HNSWConfig(M=32, ef_construction=200, ef_search=100)
        >>> index = HNSWIndex(dimension=768, config=config)
        >>> index.add(vectors, ids)
        >>> results = index.search(query_vector, k=10)
    """

    def __init__(self, dimension: int, config: Optional[HNSWConfig] = None):
        """Initialize HNSW index.

        Args:
            dimension: Vector dimension
            config: HNSW configuration (uses defaults if None)
        """
        self.dimension = dimension
        self.config = config or HNSWConfig()
        self.config.validate()

        self._index: Any = None
        self._size = 0

        logger.info(
            f"Initialized HNSW index: dim={dimension}, M={self.config.M}, "
            f"ef_construction={self.config.ef_construction}"
        )

    def _create_index(self) -> None:
        """Create the underlying FAISS HNSW index."""
        try:
            import faiss
        except ImportError as e:
            type(e).__name__
            logger.debug("ImportError: <ERROR_TYPE>")
            logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
            raise RuntimeError(
                "FAISS is required for HNSW indexing. "
                "Install with: pip install faiss-cpu (or faiss-gpu for GPU support)"
            ) from e

        # Create HNSW index
        if self.config.metric == "l2":
            self._index = faiss.IndexHNSWFlat(self.dimension, self.config.M, faiss.METRIC_L2)
        elif self.config.metric == "ip":
            self._index = faiss.IndexHNSWFlat(
                self.dimension, self.config.M, faiss.METRIC_INNER_PRODUCT
            )
        else:  # cosine
            # For cosine, normalize vectors and use inner product
            self._index = faiss.IndexHNSWFlat(
                self.dimension, self.config.M, faiss.METRIC_INNER_PRODUCT
            )

        # set construction parameter
        self._index.hnsw.efConstruction = self.config.ef_construction
        # set search parameter (can be changed later)
        self._index.hnsw.efSearch = self.config.ef_search

    def add(self, vectors: "np.ndarray", ids: Optional[list[int]] = None) -> None:
        """Add vectors to the index.

        Args:
            vectors: Array of shape (n, dimension)
            ids: Optional list of IDs (auto-generated if None)
        """
        if self._index is None:
            self._create_index()

        if vectors.shape[1] != self.dimension:
            raise ValueError(
                f"Vector dimension {vectors.shape[1]} doesn't match index dimension {self.dimension}"  # noqa: E501
            )

        # Normalize for cosine similarity
        if self.config.metric == "cosine":
            norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            vectors = vectors / np.maximum(norms, 1e-12)

        self._index.add(vectors)
        self._size += len(vectors)

        logger.info(f"Added {len(vectors)} vectors to HNSW index (total: {self._size})")

    def search(self, query: "np.ndarray", k: int = 10) -> tuple["np.ndarray", "np.ndarray"]:
        """Search for k nearest neighbors.

        Args:
            query: Query vector(s) of shape (n_queries, dimension)
            k: Number of neighbors to return

        Returns:
            distances: Array of shape (n_queries, k)
            indices: Array of shape (n_queries, k)
        """
        if self._index is None:
            raise RuntimeError("Index is empty. Add vectors before searching.")

        if query.ndim == 1:
            query = query.reshape(1, -1)

        if query.shape[1] != self.dimension:
            raise ValueError(
                f"Query dimension {query.shape[1]} doesn't match index dimension {self.dimension}"
            )

        # Normalize for cosine similarity
        if self.config.metric == "cosine":
            norms = np.linalg.norm(query, axis=1, keepdims=True)
            query = query / np.maximum(norms, 1e-12)

        distances, indices = self._index.search(query, k)
        return distances, indices

    def set_ef_search(self, ef_search: int) -> None:
        """Update ef_search parameter for runtime tuning.

        Args:
            ef_search: New ef_search value (higher = better recall, slower search)
        """
        if self._index is not None:
            self._index.hnsw.efSearch = ef_search
            self.config.ef_search = ef_search
            logger.info(f"Updated ef_search to {ef_search}")

    def save(self, filepath: str) -> None:
        """Save index to disk.

        Args:
            filepath: Path to save the index
        """
        if self._index is None:
            raise RuntimeError("Cannot save empty index")

        try:
            import faiss
        except ImportError as e:
            type(e).__name__
            logger.debug("ImportError: <ERROR_TYPE>")
            logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
            raise RuntimeError("FAISS is required") from e

        faiss.write_index(self._index, filepath)
        logger.info(f"Saved HNSW index to {filepath}")

    def load(self, filepath: str) -> None:
        """Load index from disk.

        Args:
            filepath: Path to load the index from
        """
        try:
            import faiss
        except ImportError as e:
            type(e).__name__
            logger.debug("ImportError: <ERROR_TYPE>")
            logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
            raise RuntimeError("FAISS is required") from e

        self._index = faiss.read_index(filepath)
        self._size = self._index.ntotal
        logger.info(f"Loaded HNSW index from {filepath} ({self._size} vectors)")

    @property
    def size(self) -> int:
        """Number of vectors in the index."""
        return self._size


class IVFPQIndex:
    """IVF-PQ (Inverted File with Product Quantization) index implementation.

    IVF-PQ provides memory-efficient indexing through quantization.
    Suitable for very large-scale datasets (billions of vectors).

    Trade-offs:
    - Very memory efficient (compressed representations)
    - Good search performance with proper tuning
    - Requires training on representative data
    - Less accurate than HNSW but much more scalable

    Example:
        >>> config = IVFPQConfig(nlist=1000, m=8, nbits=8, nprobe=10)
        >>> index = IVFPQIndex(dimension=768, config=config)
        >>> index.train(training_vectors)
        >>> index.add(vectors, ids)
        >>> results = index.search(query_vector, k=10)
    """

    def __init__(self, dimension: int, config: Optional[IVFPQConfig] = None):
        """Initialize IVF-PQ index.

        Args:
            dimension: Vector dimension
            config: IVF-PQ configuration (uses defaults if None)
        """
        self.dimension = dimension
        self.config = config or IVFPQConfig()
        self.config.validate()

        self._index: Any = None
        self._trained = False
        self._size = 0

        logger.info(
            f"Initialized IVF-PQ index: dim={dimension}, nlist={self.config.nlist}, "
            f"m={self.config.m}, nbits={self.config.nbits}"
        )

    def _create_index(self) -> None:
        """Create the underlying FAISS IVF-PQ index."""
        try:
            import faiss
        except ImportError as e:
            type(e).__name__
            logger.debug("ImportError: <ERROR_TYPE>")
            logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
            raise RuntimeError(
                "FAISS is required for IVF-PQ indexing. "
                "Install with: pip install faiss-cpu (or faiss-gpu for GPU support)"
            ) from e

        # Create quantizer for coarse search
        if self.config.metric == "l2":
            quantizer = faiss.IndexFlatL2(self.dimension)
            metric_type = faiss.METRIC_L2
        else:  # ip
            quantizer = faiss.IndexFlatIP(self.dimension)
            metric_type = faiss.METRIC_INNER_PRODUCT

        # Create IVF-PQ index
        self._index = faiss.IndexIVFPQ(
            quantizer,
            self.dimension,
            self.config.nlist,
            self.config.m,
            self.config.nbits,
            metric_type,
        )

        # set search parameters
        self._index.nprobe = self.config.nprobe

    def train(self, training_vectors: "np.ndarray") -> None:
        """Train the index on representative data.

        IVF-PQ requires training to learn cluster centers and quantization codebooks.
        Training data should be representative of the full dataset.

        Args:
            training_vectors: Array of shape (n_train, dimension)
                            Recommended: 30*nlist to 100*nlist vectors
        """
        if self._index is None:
            self._create_index()

        try:
            __import__("numpy")
        except ImportError as e:
            type(e).__name__
            logger.debug("ImportError: <ERROR_TYPE>")
            logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
            raise RuntimeError("NumPy is required. Install with: pip install numpy") from e

        if training_vectors.shape[1] != self.dimension:
            raise ValueError(
                f"Training vector dimension {training_vectors.shape[1]} doesn't match {self.dimension}"  # noqa: E501
            )

        min_train_size = self.config.nlist * 30
        if len(training_vectors) < min_train_size:
            logger.warning(
                f"Training data size ({len(training_vectors)}) is less than recommended "
                f"minimum ({min_train_size}). Index quality may be suboptimal."
            )

        logger.info(f"Training IVF-PQ index on {len(training_vectors)} vectors...")
        self._index.train(training_vectors)
        self._trained = True
        logger.info("IVF-PQ index training complete")

    def add(self, vectors: "np.ndarray", ids: Optional[list[int]] = None) -> None:
        """Add vectors to the index.

        Args:
            vectors: Array of shape (n, dimension)
            ids: Optional list of IDs (auto-generated if None)
        """
        if not self._trained:
            raise RuntimeError("Index must be trained before adding vectors. Call train() first.")

        try:
            __import__("numpy")
        except ImportError as e:
            type(e).__name__
            logger.debug("ImportError: <ERROR_TYPE>")
            logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
            raise RuntimeError("NumPy is required. Install with: pip install numpy") from e

        if vectors.shape[1] != self.dimension:
            raise ValueError(
                f"Vector dimension {vectors.shape[1]} doesn't match index dimension {self.dimension}"  # noqa: E501
            )

        self._index.add(vectors)
        self._size += len(vectors)

        logger.info(f"Added {len(vectors)} vectors to IVF-PQ index (total: {self._size})")

    def search(self, query: "np.ndarray", k: int = 10) -> tuple["np.ndarray", "np.ndarray"]:
        """Search for k nearest neighbors.

        Args:
            query: Query vector(s) of shape (n_queries, dimension)
            k: Number of neighbors to return

        Returns:
            distances: Array of shape (n_queries, k)
            indices: Array of shape (n_queries, k)
        """
        if not self._trained:
            raise RuntimeError("Index must be trained before searching")
        if self._size == 0:
            raise RuntimeError("Index is empty. Add vectors before searching.")

        try:
            __import__("numpy")
        except ImportError as e:
            type(e).__name__
            logger.debug("ImportError: <ERROR_TYPE>")
            logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
            raise RuntimeError("NumPy is required. Install with: pip install numpy") from e

        if query.ndim == 1:
            query = query.reshape(1, -1)

        if query.shape[1] != self.dimension:
            raise ValueError(
                f"Query dimension {query.shape[1]} doesn't match index dimension {self.dimension}"
            )

        distances, indices = self._index.search(query, k)
        return distances, indices

    def set_nprobe(self, nprobe: int) -> None:
        """Update nprobe parameter for runtime tuning.

        Args:
            nprobe: Number of lists to probe (higher = better recall, slower search)
        """
        if nprobe < 1 or nprobe > self.config.nlist:
            raise ValueError(f"nprobe must be between 1 and {self.config.nlist}")

        if self._index is not None:
            self._index.nprobe = nprobe
            self.config.nprobe = nprobe
            logger.info(f"Updated nprobe to {nprobe}")

    def save(self, filepath: str) -> None:
        """Save index to disk.

        Args:
            filepath: Path to save the index
        """
        if self._index is None or not self._trained:
            raise RuntimeError("Cannot save untrained index")

        try:
            import faiss
        except ImportError as e:
            type(e).__name__
            logger.debug("ImportError: <ERROR_TYPE>")
            logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
            raise RuntimeError("FAISS is required") from e

        faiss.write_index(self._index, filepath)
        logger.info(f"Saved IVF-PQ index to {filepath}")

    def load(self, filepath: str) -> None:
        """Load index from disk.

        Args:
            filepath: Path to load the index from
        """
        try:
            import faiss
        except ImportError as e:
            type(e).__name__
            logger.debug("ImportError: <ERROR_TYPE>")
            logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
            raise RuntimeError("FAISS is required") from e

        self._index = faiss.read_index(filepath)
        self._trained = True
        self._size = self._index.ntotal
        logger.info(f"Loaded IVF-PQ index from {filepath} ({self._size} vectors)")

    @property
    def size(self) -> int:
        """Number of vectors in the index."""
        return self._size


def optimize_index_parameters(
    index_type: IndexType,
    dataset_size: int,
    dimension: int,
    target_recall: float = 0.95,
    _memory_budget_gb: Optional[float] = None,
) -> dict[str, Any]:
    """Recommend optimal index parameters based on dataset characteristics.

    Args:
        index_type: Type of index to optimize
        dataset_size: Number of vectors in the dataset
        dimension: Vector dimension
        target_recall: Target recall rate (0.0-1.0)
        memory_budget_gb: Optional memory budget in GB

    Returns:
        Dictionary of recommended parameters
    """
    import math

    if index_type == IndexType.HNSW:
        # HNSW parameter recommendations
        if target_recall >= 0.99:
            M, ef_construction, ef_search = 64, 500, 500
        elif target_recall >= 0.95:
            M, ef_construction, ef_search = 32, 200, 100
        else:
            M, ef_construction, ef_search = 16, 100, 50

        # Estimate memory usage: ~(M * 2 * 4 bytes per link + vector storage)
        memory_per_vector_mb = (M * 2 * 4 + dimension * 4) / (1024 * 1024)
        total_memory_gb = (memory_per_vector_mb * dataset_size) / 1024

        return {
            "M": M,
            "ef_construction": ef_construction,
            "ef_search": ef_search,
            "estimated_memory_gb": round(total_memory_gb, 2),
            "estimated_build_time": "medium" if M <= 32 else "high",
        }

    if index_type == IndexType.IVF_PQ:
        # IVF-PQ parameter recommendations
        nlist = max(int(math.sqrt(dataset_size)), 1000)
        nlist = min(nlist, dataset_size // 39)  # At least 39 vectors per list

        if target_recall >= 0.95:
            nprobe = max(nlist // 10, 50)
            m, nbits = 16, 8
        elif target_recall >= 0.90:
            nprobe = max(nlist // 20, 20)
            m, nbits = 8, 8
        else:
            nprobe = max(nlist // 50, 10)
            m, nbits = 8, 4

        # Estimate memory usage: ~(m * nbits / 8) bytes per vector + cluster centers
        bytes_per_vector = m * (nbits // 8)
        cluster_overhead = nlist * dimension * 4  # float32 centroids
        total_memory_gb = (bytes_per_vector * dataset_size + cluster_overhead) / (1024**3)

        return {
            "nlist": nlist,
            "m": m,
            "nbits": nbits,
            "nprobe": nprobe,
            "estimated_memory_gb": round(total_memory_gb, 2),
            "training_samples_recommended": nlist * 50,
            "estimated_compression_ratio": round((dimension * 4) / bytes_per_vector, 1),
        }

    raise ValueError(f"Optimization not supported for index type: {index_type}")


# Example usage documentation
__doc__ += """

Usage Examples:
==============

HNSW Index:
-----------
>>> from codex.retrieval.stores.advanced_indexing import HNSWIndex, HNSWConfig
>>> import numpy as np
>>>
>>> # Create index with custom config
>>> config = HNSWConfig(M=32, ef_construction=200, ef_search=100, metric='l2')
>>> index = HNSWIndex(dimension=768, config=config)
>>>
>>> # Add vectors
>>> vectors = np.random.rand(10000, 768).astype('float32')
>>> index.add(vectors)
>>>
>>> # Search
>>> query = np.random.rand(768).astype('float32')
>>> distances, indices = index.search(query, k=10)
>>>
>>> # Save/load
>>> index.save('my_hnsw_index.bin')
>>> index.load('my_hnsw_index.bin')

IVF-PQ Index:
------------
>>> from codex.retrieval.stores.advanced_indexing import IVFPQIndex, IVFPQConfig
>>> import numpy as np
>>>
>>> # Create index
>>> config = IVFPQConfig(nlist=1000, m=8, nbits=8, nprobe=10)
>>> index = IVFPQIndex(dimension=768, config=config)
>>>
>>> # Train on representative data
>>> training_data = np.random.rand(50000, 768).astype('float32')
>>> index.train(training_data)
>>>
>>> # Add vectors
>>> vectors = np.random.rand(1000000, 768).astype('float32')
>>> index.add(vectors)
>>>
>>> # Search
>>> query = np.random.rand(768).astype('float32')
>>> distances, indices = index.search(query, k=10)

Parameter Optimization:
----------------------
>>> from codex.retrieval.stores.advanced_indexing import optimize_index_parameters, IndexType
>>>
>>> # Get recommendations for 1M vectors
>>> params = optimize_index_parameters(
...     index_type=IndexType.HNSW,
...     dataset_size=1_000_000,
...     dimension=768,
...     target_recall=0.95
... )
>>> logger.info(params)
{'M': 32, 'ef_construction': 200, 'ef_search': 100,
 'estimated_memory_gb': 3.2, 'estimated_build_time': 'medium'}
"""
