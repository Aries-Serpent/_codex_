"""Vector stores package"""

try:
    from .faiss_store import FAISSStore

    FAISS_AVAILABLE: bool = True
except ImportError:  # pragma: no cover - faiss-cpu not installed in minimal envs
    FAISSStore = None
    FAISS_AVAILABLE = False

try:
    from .pgvector_store import PGVectorStore
except ImportError:  # pragma: no cover - numpy/pgvector deps may be absent
    PGVectorStore = None

try:
    from .weaviate_store import WeaviateStore
except ImportError:  # pragma: no cover - numpy may be absent
    WeaviateStore = None

__all__ = [
    "FAISS_AVAILABLE",
    "FAISSStore",
    "PGVectorStore",
    "WeaviateStore",
]
