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
    Safely move model from meta device to target device.
    
    This helper addresses the Torch meta tensor error that occurs when
    loading models in test environments. Models on the 'meta' device
    need to be properly moved to a real device before use.
    
    Handles both standard PyTorch models and SentenceTransformer models,
    which wrap PyTorch modules internally and require checking the
    underlying modules for meta tensors.
    
    Args:
        model: The model to load (PyTorch model or SentenceTransformer)
        device: Target device (default: 'cpu')
    
    Returns:
        Model moved to the target device
        
    Example:
        >>> from sentence_transformers import SentenceTransformer
        >>> model = SentenceTransformer('all-MiniLM-L6-v2')
        >>> model = safe_model_load(model, device='cpu')
    """
    try:
        # Detect if model has meta tensors by checking its modules/parameters
        has_meta_tensors = False
        
        # For SentenceTransformer and other models with named_modules
        if hasattr(model, "named_modules"):
            # Check all modules for meta device parameters
            for name, module in model.named_modules():
                # Check parameters (recurse=False to avoid duplicates)
                for param_name, param in module.named_parameters(recurse=False):
                    if hasattr(param, "device") and param.device.type == "meta":
                        has_meta_tensors = True
                        logger.debug(
                            f"Detected meta tensor in {name}.{param_name}, "
                            f"will use to_empty() for safe loading"
                        )
                        break
                if has_meta_tensors:
                    break
        
        # For simple PyTorch models with direct device attribute
        elif hasattr(model, "device"):
            device_type = getattr(model.device, "type", None)
            if device_type == "meta":
                has_meta_tensors = True
                logger.debug("Detected model on meta device")
        
        # If meta tensors detected, use to_empty() for safe loading
        if has_meta_tensors:
            if hasattr(model, "to_empty"):
                logger.info(f"Moving model from meta device to {device} using to_empty()")
                return model.to_empty(device=device)
            else:
                # Fallback: try regular to() which may fail
                logger.warning(
                    f"Model has meta tensors but no to_empty() method, "
                    f"attempting regular to({device})"
                )
                return model.to(device)
        
        # No meta tensors, safe to use regular to() method
        if hasattr(model, "to"):
            logger.debug(f"Moving model to {device} (no meta tensors detected)")
            return model.to(device)
        
        # Model doesn't support device movement
        return model
        
    except Exception as e:
        logger.warning(
            f"Could not safely load model to device {device}: {e}. "
            f"Returning model as-is."
        )
        return model


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
