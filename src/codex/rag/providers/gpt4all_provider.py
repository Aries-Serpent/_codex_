"""
GPT4All Embedding Provider

Provides embeddings using GPT4All local runtime.
"""

import logging
from typing import List, Optional, Union
import numpy as np

logger = logging.getLogger(__name__)

try:
    from gpt4all import Embed4All
    GPT4ALL_AVAILABLE = True
except ImportError:
    GPT4ALL_AVAILABLE = False
    logger.debug("gpt4all not installed")


class GPT4AllEmbeddingProvider:
    """
    Embedding provider using GPT4All local runtime.
    
    GPT4All provides easy-to-use Python bindings for running local LLMs
    with bundled quantized models. This provider uses Embed4All for embeddings.
    
    Supported models:
    - nomic-embed-text-v1.5 (recommended, 768d)
    - all-MiniLM-L6-v2 (384d)
    - GPT4All bundled embedding models
    
    Example:
        >>> provider = GPT4AllEmbeddingProvider(model_name='nomic-embed-text-v1.5')
        >>> embeddings = provider.encode(['Hello world', 'Test document'])
        >>> print(embeddings.shape)
        (2, 768)
    """
    
    def __init__(
        self,
        model_name: str = "nomic-embed-text-v1.5",
        dimension: Optional[int] = None,
    ):
        """
        Initialize GPT4All embedding provider.
        
        Args:
            model_name: Name of GPT4All embedding model
            dimension: Expected embedding dimension (auto-detected if None)
        """
        if not GPT4ALL_AVAILABLE:
            raise ImportError(
                "gpt4all not installed. "
                "Install with: pip install gpt4all"
            )
        
        self.model_name = model_name
        
        try:
            self.embedder = Embed4All()
            logger.info(f"Initialized GPT4All embedder")
            
            # Auto-detect dimension
            if dimension is None:
                test_embedding = self.embedder.embed("test")
                self.dimension = len(test_embedding)
                logger.debug(f"Detected embedding dimension: {self.dimension}")
            else:
                self.dimension = dimension
                
        except Exception as e:
            logger.error(f"Failed to initialize GPT4All: {e}")
            raise
    
    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        show_progress: bool = False,
    ) -> np.ndarray:
        """
        Generate embeddings for texts using GPT4All.
        
        Args:
            texts: Single text or list of texts to embed
            batch_size: Batch size for processing
            show_progress: Show progress bar (not implemented)
            
        Returns:
            numpy array of embeddings with shape (n, dimension)
        """
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = []
        for text in texts:
            try:
                embedding = self.embedder.embed(text)
                embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Error encoding text: {e}")
                embeddings.append([0.0] * self.dimension)
        
        return np.array(embeddings, dtype=np.float32)
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.dimension
    
    def __repr__(self) -> str:
        return f"GPT4AllEmbeddingProvider(model={self.model_name}, dim={self.dimension})"
    
    def __del__(self):
        """Cleanup embedder on deletion."""
        if hasattr(self, 'embedder'):
            del self.embedder
