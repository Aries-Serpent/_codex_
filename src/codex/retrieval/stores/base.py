"""
Base Vector Store Interface

Defines the abstract interface that all vector store implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import numpy as np


class VectorStore(ABC):
    """Abstract base class for vector stores
    
    All vector store implementations must implement these methods to ensure
    consistent behavior across different backends (FAISS, ChromaDB, Pinecone, etc.).
    """
    
    @abstractmethod
    def add(
        self,
        vectors: np.ndarray,
        metadata: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """Add vectors to the store with optional metadata
        
        Args:
            vectors: Embedding vectors to add (shape: [n_vectors, dimension])
            metadata: Optional metadata for each vector (must match vector count)
            ids: Optional IDs for vectors (auto-generated if not provided)
            
        Returns:
            List of vector IDs (either provided or generated)
            
        Raises:
            ValueError: If inputs are invalid
            RuntimeError: If operation fails
        """
        pass
    
    @abstractmethod
    def search(
        self,
        query_vector: np.ndarray,
        k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors
        
        Args:
            query_vector: Query embedding vector (shape: [dimension] or [1, dimension])
            k: Number of nearest neighbors to return
            filters: Optional metadata filters (e.g., {"category": "tech"})
            
        Returns:
            List of results, each containing:
                - id: Vector ID
                - score: Similarity score (0-1, higher is more similar)
                - metadata: Associated metadata
                - distance: Raw distance metric (optional)
                
        Raises:
            RuntimeError: If index not loaded
            ValueError: If query vector is invalid
        """
        pass
    
    @abstractmethod
    def delete(self, ids: Union[str, List[str]]) -> int:
        """Delete vectors by ID
        
        Args:
            ids: Single ID or list of IDs to delete
            
        Returns:
            Number of vectors actually deleted
            
        Raises:
            ValueError: If IDs are invalid
        """
        pass
    
    @abstractmethod
    def get(self, ids: Union[str, List[str]]) -> List[Dict[str, Any]]:
        """Retrieve vectors by ID
        
        Args:
            ids: Single ID or list of IDs to retrieve
            
        Returns:
            List of results, each containing:
                - id: Vector ID
                - vector: Embedding vector
                - metadata: Associated metadata
                
        Raises:
            ValueError: If IDs are invalid
            KeyError: If ID not found
        """
        pass
    
    @abstractmethod
    def count(self) -> int:
        """Get total number of vectors in the store
        
        Returns:
            Total vector count
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all vectors from the store
        
        Raises:
            RuntimeError: If operation fails
        """
        pass
    
    @abstractmethod
    def save(self, path: Optional[str] = None) -> None:
        """Persist the vector store to disk
        
        Args:
            path: Optional path to save (uses default if not provided)
            
        Raises:
            RuntimeError: If save operation fails
        """
        pass
    
    @abstractmethod
    def load(self, path: Optional[str] = None) -> None:
        """Load the vector store from disk
        
        Args:
            path: Optional path to load from (uses default if not provided)
            
        Raises:
            FileNotFoundError: If path doesn't exist
            RuntimeError: If load operation fails
        """
        pass
    
    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on the vector store
        
        Returns:
            Dictionary with health status and metrics:
                - healthy: Boolean health status
                - index_loaded: Whether index is loaded
                - num_vectors: Total vector count
                - dimension: Vector dimension
                - backend: Store backend type
        """
        pass


class VectorStoreError(Exception):
    """Base exception for vector store errors"""
    pass


class DimensionMismatchError(VectorStoreError):
    """Raised when vector dimensions don't match"""
    pass


class VectorNotFoundError(VectorStoreError):
    """Raised when requested vector ID is not found"""
    pass


class IndexNotLoadedError(VectorStoreError):
    """Raised when operation requires loaded index but it's not loaded"""
    pass
