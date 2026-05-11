"""Vector stores package"""

try:
    from .faiss_store import FAISSStore

except ImportError:  # pragma: no cover - faiss-cpu not installed in minimal envs
    FAISSStore = None  # type: ignore[assignment,misc]
from .pgvector_store import PGVectorStore
from .weaviate_store import WeaviateStore

__all__ = [
    "FAISSStore",
    "PGVectorStore",
    "WeaviateStore",
]
