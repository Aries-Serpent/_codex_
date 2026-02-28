"""Vector stores package"""

try:
    from .faiss_store import FAISSStore

    _FAISS_AVAILABLE = True
except ImportError:  # pragma: no cover - faiss-cpu not installed in minimal envs
    FAISSStore = None  # type: ignore[assignment,misc]
    _FAISS_AVAILABLE = False
from .pgvector_store import PGVectorStore
from .weaviate_store import WeaviateStore

__all__ = [
    "FAISSStore",
    "PGVectorStore",
    "WeaviateStore",
]
