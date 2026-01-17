"""
Ollama Embedding Provider

Provides embeddings using Ollama server (local LLM runtime).
"""

import logging
from typing import List, Optional, Union
import numpy as np

logger = logging.getLogger(__name__)

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests not installed")


class OllamaEmbeddingProvider:
    """
    Embedding provider using Ollama local server.
    
    Ollama is a local LLM runtime that provides embedding support through
    its REST API. This provider connects to a running Ollama instance.
    
    Supported models:
    - nomic-embed-text (recommended)
    - mxbai-embed-large
    - all-minilm
    - llama2 (with embeddings)
    
    Example:
        >>> provider = OllamaEmbeddingProvider(model_name='nomic-embed-text')
        >>> embeddings = provider.encode(['Hello world', 'Test document'])
        >>> print(embeddings.shape)
        (2, 768)
    """
    
    def __init__(
        self,
        model_name: str = "nomic-embed-text",
        host: str = "http://localhost",
        port: int = 11434,
        timeout: int = 30,
        dimension: int = 768,
    ):
        """
        Initialize Ollama embedding provider.
        
        Args:
            model_name: Name of Ollama model to use
            host: Ollama server host
            port: Ollama server port
            timeout: Request timeout in seconds
            dimension: Expected embedding dimension
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests not installed. Run: pip install requests")
            
        self.model_name = model_name
        self.host = host
        self.port = port
        self.base_url = f"{host}:{port}"
        self.timeout = timeout
        self.dimension = dimension
        
        # Configure session with retries
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        
        # Check if server is running
        if not self._check_health():
            logger.warning(f"Ollama server not reachable at {self.base_url}")
            logger.warning("Start Ollama with: ollama serve")
    
    def _check_health(self) -> bool:
        """Check if Ollama server is running."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Health check failed: {e}")
            return False
    
    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        show_progress: bool = False,
    ) -> np.ndarray:
        """
        Generate embeddings for texts using Ollama.
        
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
                response = self.session.post(
                    f"{self.base_url}/api/embeddings",
                    json={
                        "model": self.model_name,
                        "prompt": text
                    },
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    embedding = data.get('embedding', [])
                    embeddings.append(embedding)
                else:
                    logger.error(f"Ollama request failed: {response.status_code}")
                    embeddings.append([0.0] * self.dimension)
                    
            except Exception as e:
                logger.error(f"Error encoding text: {e}")
                embeddings.append([0.0] * self.dimension)
        
        return np.array(embeddings, dtype=np.float32)
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.dimension
    
    def __repr__(self) -> str:
        return f"OllamaEmbeddingProvider(model={self.model_name}, host={self.base_url})"
