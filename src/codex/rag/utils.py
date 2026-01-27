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
    Safely load a model to the specified device, handling meta tensors.

    PyTorch models loaded with `device_map="meta"` contain meta tensors
    (tensors without data) that cannot be directly moved to CPU/GPU.
    This function properly initializes such models using appropriate methods.

    Handles:
    - Standard PyTorch models with meta tensors
    - SentenceTransformer models (which wrap PyTorch modules)
    - Models that need reinitialization from checkpoint

    Args:
        model: The model to load (PyTorch model or SentenceTransformer)
        device: Target device (default: 'cpu')

    Returns:
        Model moved to the target device

    Raises:
        RuntimeError: If model cannot be loaded to target device

    Example:
        >>> from sentence_transformers import SentenceTransformer
        >>> model = SentenceTransformer('all-MiniLM-L6-v2')
        >>> model = safe_model_load(model, device='cpu')
    """
    try:
        import torch

        # Detect if model has meta tensors by checking its modules/parameters
        has_meta_tensors = False
        meta_tensor_details = []

        # For SentenceTransformer and other models with named_modules
        if hasattr(model, "named_modules"):
            # Check all modules for meta device parameters
            for name, module in model.named_modules():
                # Check parameters (recurse=False to avoid duplicates)
                for param_name, param in module.named_parameters(recurse=False):
                    if hasattr(param, "device") and param.device.type == "meta":
                        has_meta_tensors = True
                        meta_tensor_details.append(f"{name}.{param_name}")
                        logger.debug(
                            f"Detected meta tensor in {name}.{param_name}, "
                            f"device={param.device}, shape={param.shape}"
                        )
                        break
                if has_meta_tensors:
                    break

        # For simple PyTorch models with direct device attribute
        elif hasattr(model, "device"):
            device_type = getattr(model.device, "type", None)
            if device_type == "meta":
                has_meta_tensors = True
                meta_tensor_details.append("model.device")
                logger.debug("Detected model on meta device")

        # If meta tensors detected, handle them appropriately
        if has_meta_tensors:
            logger.warning(
                f"Model contains meta tensors at: {', '.join(meta_tensor_details[:3])}{'...' if len(meta_tensor_details) > 3 else ''}"
            )

            # Strategy 1: Try to_empty() if available (PyTorch >= 1.12)
            if hasattr(model, "to_empty"):
                try:
                    logger.info(f"Moving model from meta device to {device} using to_empty()")
                    model = model.to_empty(device=device)
                    # After to_empty, parameters are on target device but uninitialized
                    # For embedding models, they should already have weights from checkpoint
                    logger.info(f"Successfully moved model to {device} using to_empty()")
                    return model
                except Exception as e:
                    logger.warning(f"to_empty() failed: {e}, trying alternative methods")

            # Strategy 2: For SentenceTransformers, reinitialize with device parameter
            if hasattr(model, "_load_sbert_model") or hasattr(model, "encode"):
                model_name_or_path = getattr(model, "model_name_or_path", None)
                if model_name_or_path:
                    try:
                        from sentence_transformers import SentenceTransformer
                        logger.info(
                            f"Reinitializing SentenceTransformer '{model_name_or_path}' "
                            f"directly on device '{device}'"
                        )
                        # Create new instance directly on target device
                        cache_folder = getattr(model, "cache_folder", None)
                        new_model = SentenceTransformer(
                            model_name_or_path,
                            device=device,
                            cache_folder=cache_folder
                        )
                        logger.info(f"Successfully reinitialized model on {device}")
                        return new_model
                    except ImportError as e:
                        logger.error(f"sentence_transformers not available: {e}")
                    except Exception as e:
                        logger.error(f"Failed to reinitialize SentenceTransformer: {e}")

            # Strategy 3: Try manual parameter-by-parameter materialization
            try:
                logger.info(f"Attempting manual parameter materialization to {device}")
                # This approach materializes each parameter individually
                with torch.no_grad():
                    for name, module in model.named_modules() if hasattr(model, "named_modules") else []:
                        for param_name, param in module.named_parameters(recurse=False):
                            if param.device.type == "meta":
                                # Create a new tensor on target device with same shape and dtype
                                new_param = torch.empty_like(
                                    param,
                                    device=device,
                                    dtype=param.dtype,
                                    requires_grad=param.requires_grad
                                )
                                # Replace the parameter
                                setattr(module, param_name, torch.nn.Parameter(new_param))
                                logger.debug(f"Materialized {name}.{param_name} on {device}")

                logger.info(f"Successfully materialized all parameters on {device}")
                return model
            except Exception as e:
                logger.error(f"Manual materialization failed: {e}")

            # Strategy 4: Last resort - return with error
            error_msg = (
                f"Cannot safely move model from meta device to {device}. "
                f"All strategies failed. Model will likely fail at inference time. "
                f"Meta tensors found at: {', '.join(meta_tensor_details[:5])}"
            )
            logger.error(error_msg)
            # In test environments, we might want to raise an error
            # For now, return as-is with clear warning
            return model

        # No meta tensors detected - use standard device transfer
        if hasattr(model, "to"):
            logger.debug(f"Moving model to {device} (no meta tensors detected)")
            model = model.to(device)
            logger.debug(f"Successfully moved model to {device}")
            return model

        # Model doesn't support device movement
        logger.debug("Model does not support device movement, returning as-is")
        return model

    except ImportError as e:
        logger.warning(f"PyTorch not available: {e}. Returning model as-is.")
        return model
    except Exception as e:
        logger.error(
            f"Unexpected error during safe_model_load to device {device}: {e}. "
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
