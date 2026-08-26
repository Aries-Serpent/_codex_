"""
Embedding Builder
Builds embeddings from NDJSON knowledge base
"""

import json
import logging
from typing import Any, Optional

try:
    import numpy as np
except ImportError:  # pragma: no cover - exercised in readiness smoke tests

    class _NumpyFallback:
        ndarray = object

    np = _NumpyFallback()

logger = logging.getLogger(__name__)


class EmbeddingModel:
    """Wrapper for embedding model (sentence-transformers)"""

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        cache_dir: Optional[str] = None,
    ):
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        """Load the embedding model using the shared safe loader."""
        try:
            from aries_serpent_core.rag._model_utils import safe_load_sentence_transformer

            logger.info("Loading embedding model: %s", self.model_name)
            self.model = safe_load_sentence_transformer(self.model_name, self.cache_dir)
            logger.info("Embedding model loaded successfully on CPU")
        except ImportError:
            logger.error(
                "sentence-transformers not installed. Install with: pip install sentence-transformers"
            )
            raise
        except (OSError, ValueError, TypeError, RuntimeError) as e:
            logger.warning(
                "Embedding model '%s' failed to initialize; higher-level code may select a different provider or offline-safe fallback (%s)",
                self.model_name,
                type(e).__name__,
            )
            raise

    def encode(
        self, texts: list[str], batch_size: int = 32, show_progress: bool = False
    ) -> np.ndarray:
        """Encode texts to embeddings

        Args:
            texts: List of text strings to encode
            batch_size: Batch size for encoding
            show_progress: Show progress bar

        Returns:
            Array of embeddings (shape: [len(texts), embedding_dim])
        """
        if not self.model:
            raise RuntimeError("Model not loaded")

        return self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
        )


class KnowledgeBaseLoader:
    """Loads knowledge base from NDJSON format"""

    @staticmethod
    def load_ndjson(file_path: str) -> list[dict[str, Any]]:
        """Load documents from NDJSON file

        Args:
            file_path: Path to NDJSON file

        Returns:
            List of document dictionaries
        """
        documents = []

        with open(file_path, encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    doc = json.loads(line)
                    documents.append(doc)
                except json.JSONDecodeError as e:
                    type(e).__name__
                    logger.warning(f"Error parsing line {line_num} in {file_path}: <ERROR_TYPE>")

        logger.info(f"Loaded {len(documents)} documents from {file_path}")
        return documents

    @staticmethod
    def extract_text(documents: list[dict[str, Any]], text_field: str = "content") -> list[str]:
        """Extract text from documents

        Args:
            documents: List of document dictionaries
            text_field: Field name containing text content

        Returns:
            List of text strings
        """
        texts = []
        for doc in documents:
            text = doc.get(text_field, "")
            if text:
                texts.append(str(text))
            else:
                logger.warning(f"Document missing '{text_field}' field: {doc.get('id', 'unknown')}")
                texts.append("")

        return texts


def build_embeddings(
    ndjson_path: str,
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    cache_dir: Optional[str] = None,
    text_field: str = "content",
    batch_size: int = 32,
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    """Build embeddings from NDJSON knowledge base

    Args:
        ndjson_path: Path to NDJSON file
        model_name: Embedding model name
        cache_dir: Cache directory for model weights
        text_field: Field name containing text content
        batch_size: Batch size for encoding

    Returns:
        Tuple of (embeddings array, documents list)
    """
    # Load documents
    loader = KnowledgeBaseLoader()
    documents = loader.load_ndjson(ndjson_path)

    if not documents:
        raise ValueError(f"No documents loaded from {ndjson_path}")

    # Extract text
    texts = loader.extract_text(documents, text_field)

    # Build embeddings
    model = EmbeddingModel(model_name, cache_dir)
    embeddings = model.encode(texts, batch_size=batch_size, show_progress=True)

    logger.info(f"Built embeddings with shape: {embeddings.shape}")

    return embeddings, documents
