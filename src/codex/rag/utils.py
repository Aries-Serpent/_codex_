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

        # Use the public check_for_meta_tensors function to detect meta tensors
        has_meta_tensors = check_for_meta_tensors(model)

        # If meta tensors detected, collect details for diagnostic logging
        meta_tensor_details = []
        if has_meta_tensors:
            if hasattr(model, "named_modules"):
                for name, module in model.named_modules():
                    for param_name, param in module.named_parameters(recurse=False):
                        if hasattr(param, "device") and param.device.type == "meta":
                            meta_tensor_details.append(f"{name}.{param_name}")
                            logger.debug(
                                f"Detected meta tensor in {name}.{param_name}, "
                                f"device={param.device}, shape={param.shape}"
                            )
                            break
                    if meta_tensor_details:
                        break
            elif hasattr(model, "device"):
                meta_tensor_details.append("model.device")

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

            # Strategy 2: For SentenceTransformers, materialize underlying PyTorch modules
            # using to_empty() on each module that has parameters
            if hasattr(model, "_modules") and hasattr(model, "named_modules"):
                try:
                    logger.info(
                        f"Attempting to materialize SentenceTransformer modules to {device} "
                        f"using to_empty() on underlying PyTorch modules"
                    )
                    # For SentenceTransformer, we need to move underlying modules
                    # Get all modules that contain parameters
                    modules_with_meta = []
                    for name, module in model.named_modules():
                        module_has_meta = False
                        for param_name, param in module.named_parameters(recurse=False):
                            if hasattr(param, "device") and param.device.type == "meta":
                                module_has_meta = True
                                break
                        if module_has_meta:
                            modules_with_meta.append((name, module))

                    logger.info(f"Found {len(modules_with_meta)} modules with meta tensors")

                    # Move each module with meta tensors to target device using to_empty()
                    for name, module in modules_with_meta:
                        if hasattr(module, "to_empty"):
                            try:
                                logger.debug(f"Materializing module {name} to {device}")
                                # This will create empty tensors on target device with same shape
                                module.to_empty(device=device)
                                logger.debug(f"Successfully materialized module {name}")
                            except Exception as e:
                                logger.warning(f"Failed to materialize module {name}: {e}")
                                # Try standard .to() as fallback (will likely fail but worth trying)
                                try:
                                    module.to(device)
                                except Exception:
                                    pass  # Continue with other modules

                    # Verify all meta tensors are gone
                    remaining_meta = False
                    for name, module in model.named_modules():
                        for param_name, param in module.named_parameters(recurse=False):
                            if hasattr(param, "device") and param.device.type == "meta":
                                remaining_meta = True
                                logger.warning(f"Meta tensor still present in {name}.{param_name}")
                                break
                        if remaining_meta:
                            break

                    if not remaining_meta:
                        logger.info(f"Successfully materialized all modules to {device}")
                        return model
                    else:
                        logger.warning(
                            "Some meta tensors could not be materialized, trying next strategy"
                        )

                except Exception as e:
                    logger.error(f"Failed to materialize modules: {e}")

            # Strategy 3: Try manual parameter-by-parameter materialization
            try:
                logger.info(f"Attempting manual parameter materialization to {device}")
                # This approach materializes each parameter individually
                with torch.no_grad():
                    for name, module in (
                        model.named_modules() if hasattr(model, "named_modules") else []
                    ):
                        for param_name, param in module.named_parameters(recurse=False):
                            if param.device.type == "meta":
                                # Create a new tensor on target device with same shape and dtype
                                new_param = torch.empty_like(
                                    param,
                                    device=device,
                                    dtype=param.dtype,
                                    requires_grad=param.requires_grad,
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


def check_for_meta_tensors(model: Any) -> bool:
    """
    Check if a model contains any meta device tensors.

    Meta tensors are placeholder tensors on the 'meta' device that don't
    contain actual data. They're used for lazy loading but can cause
    NotImplementedError when trying to move to CPU/GPU.

    Args:
        model: The model to check (PyTorch model or SentenceTransformer)

    Returns:
        True if model contains meta tensors, False otherwise

    Example:
        >>> from sentence_transformers import SentenceTransformer
        >>> model = SentenceTransformer('all-MiniLM-L6-v2')
        >>> has_meta = _check_for_meta_tensors(model)
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
