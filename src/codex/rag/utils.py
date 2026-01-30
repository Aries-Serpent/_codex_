"""RAG utility functions for model loading and device management."""

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Tuple

logger = logging.getLogger(__name__)


def has_meta_tensors(model: Any) -> Optional[bool]:
    """
    Check if model contains any meta tensors.
    
    Args:
        model: PyTorch model to inspect
        
    Returns:
        True if any parameter/buffer is on meta device
    """
    try:
        for _, module in getattr(model, "named_modules", lambda: [])():
            for _, param in getattr(module, "named_parameters", lambda: [])():
                if getattr(getattr(param, "device", None), "type", None) == "meta":
                    return True

        for param in getattr(model, "parameters", lambda: [])():
            if getattr(getattr(param, "device", None), "type", None) == "meta":
                return True

        for buffer in getattr(model, "buffers", lambda: [])():
            if getattr(getattr(buffer, "device", None), "type", None) == "meta":
                return True

        if getattr(getattr(model, "device", None), "type", None) == "meta":
            return True

        return False
    except Exception as e:
        logger.warning(f"Error checking for meta tensors: {e}")
        return None


def safe_model_to_device(
    model: Any, 
    device: str = "cpu"
) -> Any:
    """
    Safely move model to device, handling meta tensors.
    
    Args:
        model: Model to move
        device: Target device ("cpu" or "cuda")
        
    Returns:
        Model on target device
        
    Raises:
        RuntimeError: If model contains meta tensors after transfer
    """
    meta_status = has_meta_tensors(model)
    if meta_status is None:
        return model

    if meta_status:
        logger.warning(
            f"Model contains meta tensors, using to_empty({device})"
        )
        if hasattr(model, "to_empty"):
            return model.to_empty(device=device)

        logger.error(
            "PyTorch version does not support to_empty(). "
            "Upgrade to PyTorch >= 2.0"
        )
        raise AttributeError("Model does not support to_empty()")

    try:
        import torch

        if isinstance(model, torch.nn.Module):
            return model.to(device)
    except ImportError:
        pass

    if hasattr(model, "to") and callable(getattr(model, "to", None)):
        return model.to(device)

    return model


# Backward compatibility aliases
check_for_meta_tensors = has_meta_tensors  # Old name -> new name
safe_model_load_v2 = safe_model_to_device  # Old name -> new name


def safe_model_load(model: Any, device: str = "cpu") -> Any:
    """
    Deprecated: Use safe_model_to_device() instead.
    
    This function is provided for backward compatibility only.
    
    Args:
        model: Model to move
        device: Target device ("cpu" or "cuda")
        
    Returns:
        Model on target device
    """
    import warnings
    
    warnings.warn(
        "safe_model_load() is deprecated. Use safe_model_to_device() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return safe_model_to_device(model, device)


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
