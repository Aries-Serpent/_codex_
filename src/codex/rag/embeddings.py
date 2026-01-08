"""
RAG Embeddings Module
Provides embedding provider abstraction with caching layer for expanded context workflows.
"""

import hashlib
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

import numpy as np

logger = logging.getLogger(__name__)


def safe_model_load(model, device: str = "cpu"):
    """
    Safely move model from meta device to target device.
    
    This helper addresses the Torch meta tensor error that occurs when
    loading models in test environments. Models on the 'meta' device
    need to be properly moved to a real device before use.
    
    Args:
        model: The model to load
        device: Target device (default: 'cpu')
    
    Returns:
        Model moved to the target device
    """
    try:
        # Check if model has a device attribute and is on meta device
        if hasattr(model, "device") and str(model.device) == "meta":
            # Use to_empty to move from meta device
            if hasattr(model, "to_empty"):
                return model.to_empty(device=device)
            # Fallback to regular .to() method
            return model.to(device)
        # If not on meta device, just move to target device
        if hasattr(model, "to"):
            return model.to(device)
        return model
    except Exception as e:
        logger.warning(f"Could not safely load model to device {device}: {e}")
        return model


class EmbeddingProvider(Protocol):
    """Protocol for embedding providers."""

    def encode(self, texts: List[str], **kwargs) -> np.ndarray:
        """Encode texts to embeddings."""
        ...

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        ...


class LocalSentenceTransformerProvider:
    """
    Local sentence-transformer embedding provider.

    Uses sentence-transformers library for local embedding generation.
    Fallback to all-MiniLM-L6-v2 model.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        cache_dir: Optional[str] = None,
    ):
        """
        Initialize local embedding provider.

        Args:
            model_name: HuggingFace model name
            cache_dir: Optional cache directory for model weights
        """
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the embedding model."""
        try:
            from sentence_transformers import SentenceTransformer

            logger.info(f"Loading local embedding model: {self.model_name}")
            self.model = SentenceTransformer(
                self.model_name, cache_folder=self.cache_dir
            )
            # Apply safe model loading to handle meta device tensors
            self.model = safe_model_load(self.model, device="cpu")
            logger.info("Local embedding model loaded successfully")
        except ImportError:
            logger.error(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )
            raise
        except Exception as e:
            logger.error(f"Error loading local embedding model: {e}")
            raise

    def encode(
        self, texts: List[str], batch_size: int = 32, show_progress: bool = False
    ) -> np.ndarray:
        """
        Encode texts to embeddings.

        Args:
            texts: List of text strings
            batch_size: Batch size for encoding
            show_progress: Show progress bar

        Returns:
            numpy array of embeddings
        """
        if not self.model:
            raise RuntimeError("Model not loaded")

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
        )

        return embeddings

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        if not self.model:
            raise RuntimeError("Model not loaded")
        return self.model.get_sentence_embedding_dimension()


class OpenAIEmbeddingProvider:
    """
    OpenAI embedding provider.

    Uses OpenAI API for embedding generation (requires OPENAI_API_KEY).
    """

    def __init__(
        self,
        model_name: str = "text-embedding-3-small",
        api_key: Optional[str] = None,
    ):
        """
        Initialize OpenAI embedding provider.

        Args:
            model_name: OpenAI model name
            api_key: Optional API key (defaults to OPENAI_API_KEY env var)
        
        Security Note:
            API keys are stored in memory during operation. Consider using
            key rotation and secure key management practices in production.
        """
        self.model_name = model_name
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. "
                "Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )

        self.client = None
        self._initialize_client()
    
    def __del__(self):
        """Clean up on destruction (clear sensitive data)."""
        if hasattr(self, 'api_key'):
            self.api_key = None

    def _initialize_client(self):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI

            self.client = OpenAI(api_key=self.api_key)
            logger.info(f"Initialized OpenAI client with model: {self.model_name}")
        except ImportError:
            logger.error(
                "openai package not installed. Install with: pip install openai"
            )
            raise

    def encode(self, texts: List[str], batch_size: int = 100, **kwargs) -> np.ndarray:
        """
        Encode texts to embeddings using OpenAI API.

        Args:
            texts: List of text strings
            batch_size: Batch size (OpenAI supports up to 2048)

        Returns:
            numpy array of embeddings
        """
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")

        embeddings = []

        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]

            try:
                response = self.client.embeddings.create(
                    model=self.model_name, input=batch
                )

                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)

            except Exception as e:
                logger.error(f"Error encoding batch {i}-{i+len(batch)}: {e}")
                raise

        return np.array(embeddings)

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        # Model-specific dimensions
        dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        }
        return dimensions.get(self.model_name, 1536)


class CachedEmbeddingProvider:
    """
    Caching layer for embedding providers.

    Caches embeddings per file/chunk with mtime checks for invalidation.
    Stores cache in .codex/embeddings_cache/ with metadata.
    """

    def __init__(
        self,
        provider: EmbeddingProvider,
        cache_dir: str = ".codex/embeddings_cache",
    ):
        """
        Initialize cached embedding provider.

        Args:
            provider: Underlying embedding provider
            cache_dir: Directory for embedding cache
        """
        self.provider = provider
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Stats
        self.cache_hits = 0
        self.cache_misses = 0

        logger.info(f"Initialized embedding cache at {self.cache_dir}")

    def encode(
        self,
        texts: List[str],
        cache_key: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> np.ndarray:
        """
        Encode texts with caching.

        Args:
            texts: List of text strings
            cache_key: Optional cache key (e.g., file path)
            metadata: Optional metadata for cache validation
            **kwargs: Additional arguments for provider

        Returns:
            numpy array of embeddings
        """
        # Generate cache key if not provided
        if not cache_key:
            # Hash all texts together
            combined = "\n".join(texts)
            cache_key = hashlib.sha256(combined.encode()).hexdigest()

        cache_file = self.cache_dir / f"{cache_key}.npz"
        metadata_file = self.cache_dir / f"{cache_key}.meta.json"

        # Check cache
        if cache_file.exists() and metadata_file.exists():
            if self._is_cache_valid(metadata_file, metadata):
                try:
                    # Load from cache
                    data = np.load(cache_file)
                    embeddings = data["embeddings"]
                    self.cache_hits += 1
                    logger.debug(f"Cache hit for key: {cache_key}")
                    return embeddings
                except Exception as e:
                    logger.warning(f"Error loading cache: {e}")

        # Cache miss - generate embeddings
        self.cache_misses += 1
        logger.debug(f"Cache miss for key: {cache_key}")
        embeddings = self.provider.encode(texts, **kwargs)

        # Save to cache
        try:
            np.savez_compressed(cache_file, embeddings=embeddings)

            cache_metadata = {
                "cache_key": cache_key,
                "num_texts": len(texts),
                "embedding_dim": embeddings.shape[1] if len(embeddings) > 0 else 0,
                "created_at": datetime.utcnow().isoformat() + "Z",
                "provider": self.provider.__class__.__name__,
                **(metadata or {}),
            }

            with open(metadata_file, "w") as f:
                json.dump(cache_metadata, f, indent=2)

            logger.debug(f"Saved embeddings to cache: {cache_key}")

        except Exception as e:
            logger.warning(f"Error saving to cache: {e}")

        return embeddings

    def _is_cache_valid(
        self, metadata_file: Path, provided_metadata: Optional[Dict[str, Any]]
    ) -> bool:
        """
        Check if cached embeddings are still valid.

        Args:
            metadata_file: Path to cache metadata file
            provided_metadata: Metadata from current request

        Returns:
            True if cache is valid, False otherwise
        """
        try:
            with open(metadata_file, "r") as f:
                cache_metadata = json.load(f)

            # If file mtime is provided, check if it matches
            if provided_metadata and "file_mtime" in provided_metadata:
                cached_mtime = cache_metadata.get("file_mtime")
                if cached_mtime != provided_metadata["file_mtime"]:
                    logger.debug("Cache invalid: file mtime changed")
                    return False

            # Add more validation rules as needed
            return True

        except Exception as e:
            logger.warning(f"Error validating cache: {e}")
            return False

    def get_dimension(self) -> int:
        """Get embedding dimension from provider."""
        return self.provider.get_dimension()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total if total > 0 else 0.0

        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "total_requests": total,
            "hit_rate": hit_rate,
            "cache_dir": str(self.cache_dir),
        }

    def clear_cache(self):
        """Clear all cached embeddings."""
        import shutil

        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Cleared embedding cache")

        self.cache_hits = 0
        self.cache_misses = 0


def create_embedding_provider(
    provider_type: str = "local",
    model_name: Optional[str] = None,
    use_cache: bool = True,
    cache_dir: str = ".codex/embeddings_cache",
    **kwargs,
) -> EmbeddingProvider:
    """
    Factory function to create embedding providers.

    Args:
        provider_type: Type of provider ('local' or 'openai')
        model_name: Model name (uses defaults if not provided)
        use_cache: Whether to wrap provider with caching layer
        cache_dir: Cache directory
        **kwargs: Additional provider-specific arguments

    Returns:
        Embedding provider (optionally wrapped with caching)
    """
    # Create base provider
    if provider_type == "local":
        model_name = model_name or "sentence-transformers/all-MiniLM-L6-v2"
        provider = LocalSentenceTransformerProvider(model_name=model_name, **kwargs)

    elif provider_type == "openai":
        # Check if API key is available
        if not os.environ.get("OPENAI_API_KEY") and "api_key" not in kwargs:
            logger.error(
                "OpenAI provider requested but OPENAI_API_KEY not found. "
                "Set the environment variable or pass api_key parameter. "
                "Use provider_type='local' for local embeddings instead."
            )
            raise ValueError(
                "OpenAI API key required for provider_type='openai'. "
                "Use provider_type='local' or set OPENAI_API_KEY."
            )
        else:
            model_name = model_name or "text-embedding-3-small"
            provider = OpenAIEmbeddingProvider(model_name=model_name, **kwargs)

    else:
        raise ValueError(f"Unknown provider type: {provider_type}")

    # Wrap with caching if requested
    if use_cache:
        provider = CachedEmbeddingProvider(provider, cache_dir=cache_dir)

    logger.info(f"Created embedding provider: {provider.__class__.__name__}")
    return provider
