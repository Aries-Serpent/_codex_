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

    Meta tensors are placeholder tensors without actual data, created when
    models are initialized on the 'meta' device. They must be handled specially
    during device transfers.

    Args:
        model: PyTorch model to inspect

    Returns:
        True if any parameter/buffer is on meta device, False otherwise,
        None if model doesn't support parameter inspection
    """
    try:
        # Check if model has parameters method
        if hasattr(model, 'parameters'):
            for param in model.parameters():
                # Use is_meta attribute for direct meta tensor detection (PyTorch 1.10+)
                if hasattr(param, 'is_meta') and param.is_meta:
                    logger.debug(f"Found meta tensor parameter: {param.shape}")
                    return True
                # Fallback: Check device.type for older versions or mock objects
                if hasattr(param, 'device') and hasattr(param.device, 'type'):
                    if param.device.type == 'meta':
                        logger.debug(f"Found meta device parameter via device.type")
                        return True

        # Also check buffers if available
        if hasattr(model, 'buffers'):
            for buffer in model.buffers():
                if hasattr(buffer, 'is_meta') and buffer.is_meta:
                    logger.debug(f"Found meta tensor buffer: {buffer.shape}")
                    return True
                # Fallback: Check device.type
                if hasattr(buffer, 'device') and hasattr(buffer.device, 'type'):
                    if buffer.device.type == 'meta':
                        logger.debug(f"Found meta device buffer via device.type")
                        return True

        # Check named_modules for parameters (for comprehensive detection)
        if hasattr(model, 'named_modules'):
            for _, module in model.named_modules():
                if hasattr(module, 'named_parameters'):
                    for _, param in module.named_parameters():
                        if hasattr(param, 'is_meta') and param.is_meta:
                            logger.debug(f"Found meta tensor in module parameter")
                            return True
                        if hasattr(param, 'device') and hasattr(param.device, 'type'):
                            if param.device.type == 'meta':
                                logger.debug(f"Found meta device in module parameter via device.type")
                                return True

        # Check model's own device attribute
        if hasattr(model, 'device') and hasattr(model.device, 'type'):
            if model.device.type == 'meta':
                logger.debug(f"Found meta device on model itself")
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
    Safely move a model to the specified device, handling meta tensors.

    Meta tensors are placeholder tensors without actual data. When models
    are initialized with meta tensors, they must use .to_empty() instead
    of .to() for device transfers, followed by parameter reinitialization.

    Args:
        model: PyTorch model or SentenceTransformer model
        device: Target device ('cpu', 'cuda', 'mps', etc.)

    Returns:
        Model on the target device

    Raises:
        AttributeError: If model with meta tensors doesn't support to_empty()
        RuntimeError: If model cannot be moved to device
    """
    try:
        import torch

        # Check if model has any meta tensors
        meta_status = has_meta_tensors(model)
        if meta_status is None:
            # Model doesn't support parameter inspection
            logger.debug("Model doesn't support parameter inspection, returning as-is")
            return model

        if meta_status:
            # Model has meta tensors - must use to_empty()
            logger.warning(
                "Detected meta tensor in model. Using to_empty() for device transfer."
            )

            if not hasattr(model, "to_empty"):
                logger.error(
                    "PyTorch version does not support to_empty(). "
                    "Upgrade to PyTorch >= 2.0"
                )
                raise AttributeError("Model does not support to_empty()")

            logger.info(f"Moving model with meta tensors to {device} using to_empty()")

            # First, move to the target device with to_empty()
            model = model.to_empty(device=device)

            # Then reinitialize parameters (if needed)
            # This ensures all parameters have actual data
            # Skip if model doesn't support modules() (e.g., mock objects in tests)
            if hasattr(model, 'modules') and callable(getattr(model, 'modules', None)):
                for module in model.modules():
                    if hasattr(module, 'reset_parameters'):
                        try:
                            module.reset_parameters()
                            logger.debug(f"Reset parameters for {module.__class__.__name__}")
                        except Exception as e:
                            logger.debug(f"Could not reset parameters for {module}: {e}")
            else:
                logger.debug("Model doesn't support modules(), skipping parameter reset")

            logger.info("Successfully moved model with meta tensors to device")
            return model

        else:
            # Standard device transfer for normal tensors
            logger.debug(f"Moving model to {device} using standard .to()")
            if isinstance(model, torch.nn.Module):
                return model.to(device)  # safe-device-placement: internal implementation

            # For SentenceTransformer or other models with .to() method
            if hasattr(model, "to") and callable(getattr(model, "to", None)):
                return model.to(device)  # safe-device-placement: internal implementation

            return model

    except ImportError:
        # PyTorch not available - try fallback .to() method if model has it
        logger.warning("PyTorch not available, attempting fallback .to() method")
        if hasattr(model, "to") and callable(getattr(model, "to", None)):
            return model.to(device)  # safe-device-placement: internal implementation
        # No fallback available
        logger.warning("No device transfer method available, returning model as-is")
        return model
    except AttributeError as e:
        # Re-raise if this is about missing to_empty() (critical error)
        if "to_empty" in str(e):
            raise
        # Otherwise, model doesn't support .to() method - return as-is
        logger.warning(f"Model does not support device transfer: {e}")
        return model
    except Exception as e:
        logger.error(f"Error moving model to device {device}: {e}")
        raise RuntimeError(f"Failed to move model to {device}: {e}") from e


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
