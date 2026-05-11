"""Vector stores package"""

try:
    from .faiss_store import FAISSStore

    _FAISS_AVAILABLE = True  # noqa: F841
except ImportError:  # pragma: no cover - faiss-cpu not installed in minimal envs
    FAISSStore = None  # type: ignore[assignment,misc]
    _FAISS_AVAILABLE = False  # noqa: F841
from .pgvector_store import PGVectorStore
from .weaviate_store import WeaviateStore

__all__ = [
    "FAISSStore",
    "PGVectorStore",
    "WeaviateStore",
]
