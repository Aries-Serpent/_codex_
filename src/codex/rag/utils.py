"""
RAG Utility Functions
Shared utilities for RAG modules including model loading helpers.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Tuple

logger = logging.getLogger(__name__)


def safe_model_load(model: Any, device: str = "cpu") -> Any:
    """
    DEPRECATED: This function is no longer needed and should not be used.
    
    Historical context: This function attempted to fix models that were already
    initialized with meta tensors, which cannot work. PyTorch meta tensors are
    placeholders without data that cannot be copied or moved.
    
    **Correct approach**: Initialize models with explicit device from the start:
    ```python
    import torch
    from sentence_transformers import SentenceTransformer
    
    with torch.device('cpu'):
        model = SentenceTransformer(..., device='cpu', trust_remote_code=False)
    ```
    
    This function is kept for backward compatibility only and will be removed
    in a future version.
    
    Args:
        model: The model (returned unchanged)
        device: Target device (ignored)
    
    Returns:
        Model unchanged (no processing applied)
    
    Raises:
        DeprecationWarning: Always raised to warn about deprecated usage
    """
    import warnings
    warnings.warn(
        "safe_model_load() is deprecated and does not fix meta tensor issues. "
        "Initialize models correctly from the start using: "
        "with torch.device('cpu'): model = SentenceTransformer(..., device='cpu'). "
        "This function will be removed in version 1.0.0.",
        DeprecationWarning,
        stacklevel=2
    )
    return model


def check_for_meta_tensors(model: Any) -> bool:
    """
    Check if a model contains any meta device tensors.
    
    DEPRECATED: This utility function is kept for backward compatibility only.
    For new code, check for meta tensors directly during model initialization.

    Meta tensors are placeholder tensors on the 'meta' device that don't
    contain actual data. They're used for lazy loading but cause errors
    when trying to move to CPU/GPU.
    
    **Best practice**: Prevent meta tensors during initialization instead of
    checking for them after the fact:
    ```python
    with torch.device('cpu'):
        model = SentenceTransformer(..., device='cpu')
    ```

    Args:
        model: The model to check (PyTorch model or SentenceTransformer)

    Returns:
        True if model contains meta tensors, False otherwise

    Example:
        >>> from sentence_transformers import SentenceTransformer
        >>> model = SentenceTransformer('all-MiniLM-L6-v2')
        >>> has_meta = check_for_meta_tensors(model)
        >>> print(f"Model has meta tensors: {has_meta}")
    """
    try:
        # Check if model has modules/parameters to iterate
        if hasattr(model, "named_modules"):
            for name, module in model.named_modules():
                # Check parameters in this module (recurse=False to avoid duplicates)
                for param_name, param in module.named_parameters(recurse=False):
                    if hasattr(param, "device") and param.device.type == "meta":
                        logger.debug(f"Found meta tensor in {name}.{param_name}")
                        return True
                # Also check buffers
                for buf_name, buf in module.named_buffers(recurse=False):
                    if hasattr(buf, "device") and buf.device.type == "meta":
                        logger.debug(f"Found meta tensor in {name}.{buf_name}")
                        return True

        # Check if model itself is on meta device
        elif hasattr(model, "device"):
            device_type = getattr(model.device, "type", None)
            if device_type == "meta":
                logger.debug("Model is on meta device")
                return True

        return False

    except Exception as e:
        logger.debug(f"Error checking for meta tensors: {e}")
        return False


@dataclass
class ProvenanceMetadata:
    """
    Comprehensive provenance tracking for RAG chunks and retrievals.

    Tracks the origin, processing, and retrieval context of text chunks
    to support expanded context workflows (64k-512k tokens) with full
    auditability and traceability.

    Attributes:
        source_file: Original source file path
        line_range: Tuple of (start_line, end_line) in source
        chunk_id: Unique identifier for this chunk
        indexed_at: Timestamp when chunk was indexed
        embedding_model: Model used to generate embeddings
        retrieval_score: Similarity score from retrieval (if applicable)
        char_range: Optional character position range in source
        metadata: Additional custom metadata

    Example:
        >>> prov = ProvenanceMetadata(
        ...     source_file=Path("docs/guide.md"),
        ...     line_range=(10, 25),
        ...     chunk_id="chunk_abc123",
        ...     indexed_at=datetime.now(),
        ...     embedding_model="all-MiniLM-L6-v2",
        ...     retrieval_score=0.85
        ... )
    """

    source_file: Path
    line_range: Tuple[int, int]
    chunk_id: str
    indexed_at: datetime
    embedding_model: str
    retrieval_score: float
    char_range: Optional[Tuple[int, int]] = None
    metadata: Optional[dict] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "source_file": str(self.source_file),
            "line_range": self.line_range,
            "chunk_id": self.chunk_id,
            "indexed_at": self.indexed_at.isoformat(),
            "embedding_model": self.embedding_model,
            "retrieval_score": self.retrieval_score,
            "char_range": self.char_range,
            "metadata": self.metadata or {},
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProvenanceMetadata":
        """Create from dictionary."""
        return cls(
            source_file=Path(data["source_file"]),
            line_range=tuple(data["line_range"]),
            chunk_id=data["chunk_id"],
            indexed_at=datetime.fromisoformat(data["indexed_at"]),
            embedding_model=data["embedding_model"],
            retrieval_score=data["retrieval_score"],
            char_range=tuple(data["char_range"]) if data.get("char_range") else None,
            metadata=data.get("metadata"),
        )
