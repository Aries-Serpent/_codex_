"""
Vector Store Factory and Registry Pattern
Provides centralized management and creation of vector stores
"""

from enum import Enum
from typing import Any, Optional

from codex.logging.structured_logger import logger


class VectorStoreType(Enum):
    """Supported vector store types"""

    FAISS = "faiss"
    CHROMADB = "chromadb"
    PINECONE = "pinecone"
    WEAVIATE = "weaviate"


class VectorStoreRegistry:
    """
    Registry for vector store implementations.
    Allows registration and retrieval of vector store classes.
    """

    _stores: dict[str, type] = {}

    @classmethod
    def register(cls, store_type: str, store_class: type) -> None:
        """Register a vector store implementation"""
        if store_type in cls._stores:
            logger.warning(f"Overwriting existing store type: {store_type}")
        cls._stores[store_type] = store_class
        logger.info(f"Registered vector store: {store_type}")

    @classmethod
    def get(cls, store_type: str) -> Optional[type]:
        """Get a registered vector store class"""
        return cls._stores.get(store_type)

    @classmethod
    def list_types(cls) -> list[Any]:
        """list all registered store types"""
        return list(cls._stores.keys())


class VectorStoreFactory:
    """
    Factory for creating vector store instances.
    Supports multiple backends with unified interface.
    """

    @staticmethod
    def create(store_type: str, index_name: str, dimension: Optional[int] = None, **kwargs) -> Any:
        """
        Create a vector store instance.

        Args:
            store_type: Type of vector store ("faiss", "chromadb", etc.)
            index_name: Name for the index
            dimension: Embedding dimension (optional, store-specific)
            **kwargs: Additional store-specific parameters

        Returns:
            Vector store instance

        Raises:
            ValueError: If store type not registered
        """
        store_class = VectorStoreRegistry.get(store_type)

        if store_class is None:
            available = VectorStoreRegistry.list_types()
            raise ValueError(
                f"Unknown vector store type: {store_type}. Available types: {available}"
            )

        logger.info(f"Creating {store_type} vector store: {index_name}")

        # Create instance with validation
        # For FAISS: only pass index_name and kwargs (dimension not in constructor)
        # For other stores: may need dimension in constructor
        try:
            if store_type == "faiss":
                # FAISSStore constructor: (index_dir, index_name, max_vectors, validate_checksums)
                # Dimension is set when create_index() is called
                # Strip dimension from kwargs as it's not a constructor parameter
                sanitized_kwargs = {k: v for k, v in kwargs.items() if k != "dimension"}
                instance = store_class(index_name=index_name, **sanitized_kwargs)
            else:
                # Other stores may require dimension
                instance = store_class(index_name=index_name, dimension=dimension, **kwargs)
            logger.info(f"Successfully created {store_type} store")
            return instance
        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.error(f"Failed to create {store_type} store: <ERROR_TYPE>")
            raise

    @staticmethod
    def create_from_config(config: dict[str, Any]) -> Any:
        """
        Create vector store from configuration dictionary.

        Args:
            config: Configuration with keys:
                - type: Store type
                - index_name: Index name
                - dimension: Embedding dimension
                - Other store-specific params

        Returns:
            Vector store instance
        """
        store_type = config.get("type")
        if not store_type:
            raise ValueError("Config must specify 'type'")

        index_name = config.get("index_name", "default")
        dimension = config.get("dimension")

        if dimension is None:
            raise ValueError("Config must specify 'dimension'")

        # Extract other params
        other_params = {
            k: v for k, v in config.items() if k not in ["type", "index_name", "dimension"]
        }

        return VectorStoreFactory.create(
            store_type=store_type,
            index_name=index_name,
            dimension=dimension,
            **other_params,
        )


# Auto-register FAISS store
try:
    from codex.retrieval.stores.faiss_store import FAISSStore

    VectorStoreRegistry.register("faiss", FAISSStore)
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
    logger.warning("FAISS store not available for registration")

# Auto-register Pinecone store
try:
    from codex.retrieval.stores.pinecone_store import PineconeStore

    VectorStoreRegistry.register("pinecone", PineconeStore)
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
    logger.warning("Pinecone store not available for registration")

# Auto-register Weaviate store
try:
    from codex.retrieval.stores.weaviate_store import WeaviateStore

    VectorStoreRegistry.register("weaviate", WeaviateStore)
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
    logger.warning("Weaviate store not available for registration")

# Auto-register PGVector store
try:
    from codex.retrieval.stores.pgvector_store import PGVectorStore

    VectorStoreRegistry.register("pgvector", PGVectorStore)
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
    logger.warning("PGVector store not available for registration")


def get_default_store(dimension: int, index_name: str = "default") -> Any:
    """
    Get a default vector store instance (FAISS).

    Args:
        dimension: Embedding dimension
        index_name: Index name (default: "default")

    Returns:
        Vector store instance
    """
    return VectorStoreFactory.create(store_type="faiss", index_name=index_name, dimension=dimension)


def auto_detect_store() -> str:
    """
    Auto-detect the best available vector store backend.

    Returns:
        Store type string (e.g., "faiss", "pinecone")

    Priority:
    1. FAISS (always available, local)
    2. PGVector (if PostgreSQL available)
    3. Pinecone (if API key configured)
    4. Weaviate (if URL configured)
    """
    import os

    # Always prefer FAISS for local/offline mode
    if "faiss" in VectorStoreRegistry.list_types():
        logger.info("Auto-detected: FAISS (local/offline)")
        return "faiss"

    # Check for PGVector configuration
    if "pgvector" in VectorStoreRegistry.list_types():
        pg_conn = os.getenv("PGVECTOR_CONNECTION_STRING")
        if pg_conn:
            logger.info("Auto-detected: PGVector (PostgreSQL)")
            return "pgvector"

    # Check for Pinecone configuration
    if "pinecone" in VectorStoreRegistry.list_types():
        pinecone_key = os.getenv("PINECONE_API_KEY")
        if pinecone_key:
            logger.info("Auto-detected: Pinecone (cloud)")
            return "pinecone"

    # Check for Weaviate configuration
    if "weaviate" in VectorStoreRegistry.list_types():
        weaviate_url = os.getenv("WEAVIATE_URL")
        if weaviate_url:
            logger.info("Auto-detected: Weaviate (cloud/self-hosted)")
            return "weaviate"

    # Fallback to first available
    available = VectorStoreRegistry.list_types()
    if available:
        fallback = available[0]
        logger.warning(f"No preferred backend detected, falling back to: {fallback}")
        return fallback

    raise RuntimeError(
        "No vector store backends available. Install faiss-cpu or configure a cloud provider."
    )


def create_auto_store(
    index_name: str = "default", dimension: Optional[int] = None, **kwargs
) -> Any:
    """
    Create a vector store with auto-detected backend.

    Args:
        index_name: Index name
        dimension: Embedding dimension
        **kwargs: Additional store-specific parameters

    Returns:
        Vector store instance
    """
    store_type = auto_detect_store()
    return VectorStoreFactory.create(
        store_type=store_type, index_name=index_name, dimension=dimension, **kwargs
    )


if __name__ == "__main__":
    # Example usage
    logger.info("Registered vector stores:", VectorStoreRegistry.list_types())

    # Create FAISS store via factory
    store = VectorStoreFactory.create(store_type="faiss", index_name="example", dimension=768)
    logger.info(f"Created store: {store}")

    # Create from config
    config = {"type": "faiss", "index_name": "config_example", "dimension": 384}
    store2 = VectorStoreFactory.create_from_config(config)
    logger.info(f"Created from config: {store2}")
