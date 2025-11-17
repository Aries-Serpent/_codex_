"""
Vector Store Factory and Registry Pattern
Provides centralized management and creation of vector stores
"""
from typing import Dict, Type, Optional, Any
from enum import Enum
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


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
    
    _stores: Dict[str, Type] = {}
    
    @classmethod
    def register(cls, store_type: str, store_class: Type) -> None:
        """Register a vector store implementation"""
        if store_type in cls._stores:
            logger.warning(f"Overwriting existing store type: {store_type}")
        cls._stores[store_type] = store_class
        logger.info(f"Registered vector store: {store_type}")
    
    @classmethod
    def get(cls, store_type: str) -> Optional[Type]:
        """Get a registered vector store class"""
        return cls._stores.get(store_type)
    
    @classmethod
    def list_types(cls) -> list:
        """List all registered store types"""
        return list(cls._stores.keys())


class VectorStoreFactory:
    """
    Factory for creating vector store instances.
    Supports multiple backends with unified interface.
    """
    
    @staticmethod
    def create(
        store_type: str,
        index_name: str,
        dimension: int,
        **kwargs
    ) -> Any:
        """
        Create a vector store instance.
        
        Args:
            store_type: Type of vector store ("faiss", "chromadb", etc.)
            index_name: Name for the index
            dimension: Embedding dimension
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
                f"Unknown vector store type: {store_type}. "
                f"Available types: {available}"
            )
        
        logger.info(f"Creating {store_type} vector store: {index_name}")
        
        # Create instance with validation
        try:
            instance = store_class(
                index_name=index_name,
                dimension=dimension,
                **kwargs
            )
            logger.info(f"Successfully created {store_type} store")
            return instance
        except Exception as e:
            logger.error(f"Failed to create {store_type} store: {e}")
            raise
    
    @staticmethod
    def create_from_config(config: Dict[str, Any]) -> Any:
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
            k: v for k, v in config.items()
            if k not in ["type", "index_name", "dimension"]
        }
        
        return VectorStoreFactory.create(
            store_type=store_type,
            index_name=index_name,
            dimension=dimension,
            **other_params
        )


# Auto-register FAISS store
try:
    from codex.retrieval.stores.faiss_store import FAISSVectorStore
    VectorStoreRegistry.register("faiss", FAISSVectorStore)
except ImportError:
    logger.warning("FAISS store not available for registration")


def get_default_store(dimension: int, index_name: str = "default") -> Any:
    """
    Get a default vector store instance (FAISS).
    
    Args:
        dimension: Embedding dimension
        index_name: Index name (default: "default")
        
    Returns:
        Vector store instance
    """
    return VectorStoreFactory.create(
        store_type="faiss",
        index_name=index_name,
        dimension=dimension
    )


if __name__ == "__main__":
    # Example usage
    print("Registered vector stores:", VectorStoreRegistry.list_types())
    
    # Create FAISS store via factory
    store = VectorStoreFactory.create(
        store_type="faiss",
        index_name="example",
        dimension=768
    )
    print(f"Created store: {store}")
    
    # Create from config
    config = {
        "type": "faiss",
        "index_name": "config_example",
        "dimension": 384
    }
    store2 = VectorStoreFactory.create_from_config(config)
    print(f"Created from config: {store2}")
