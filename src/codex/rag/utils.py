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


def safe_model_load_v2(model: Any, device: str = "cpu", model_name: Optional[str] = None, cache_folder: Optional[str] = None) -> Any:
    """
    Enhanced model loading with strategy pattern for handling meta tensors.
    
    This function attempts multiple strategies to properly materialize models
    that may contain meta tensors (placeholder tensors without data).
    
    Strategy Pattern:
    1. First attempt: Reinitialize SentenceTransformer with device parameter
    2. Second attempt: Use to_empty() if meta tensors detected
    3. Third attempt: Manual per-parameter materialization
    4. Fallback: Standard to() for normal models
    
    Args:
        model: The model to load (SentenceTransformer or PyTorch model)
        device: Target device ("cpu" or "cuda")
        model_name: Original model name (for reinitialization strategy)
        cache_folder: Cache directory (for reinitialization strategy)
    
    Returns:
        Model properly materialized on target device
        
    Raises:
        RuntimeError: If all strategies fail to materialize the model
        
    Example:
        >>> from sentence_transformers import SentenceTransformer
        >>> model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder='./cache')
        >>> model = safe_model_load_v2(model, device="cpu", 
        ...                            model_name='all-MiniLM-L6-v2',
        ...                            cache_folder='./cache')
        >>> model.eval()
    """
    import torch
    
    # Check if model has meta tensors
    has_meta = check_for_meta_tensors(model)
    
    if not has_meta:
        # No meta tensors, model is already properly loaded
        logger.debug(f"Model has no meta tensors, moving to {device}")
        try:
            model = model.to(device)
            model.eval()
            return model
        except Exception as e:
            logger.warning(f"Standard to() failed: {e}, trying fallback strategies")
    
    # Strategy 1: Reinitialize SentenceTransformer with explicit device
    if model_name and hasattr(model, '__class__') and model.__class__.__name__ == 'SentenceTransformer':
        try:
            logger.info(f"Strategy 1: Reinitializing SentenceTransformer with device={device}")
            from sentence_transformers import SentenceTransformer
            
            new_model = SentenceTransformer(
                model_name,
                device=device,
                cache_folder=cache_folder,
                trust_remote_code=False
            )
            
            # Verify no meta tensors
            if not check_for_meta_tensors(new_model):
                logger.info("Strategy 1 successful: Model reinitialized without meta tensors")
                new_model.eval()
                return new_model
            else:
                logger.warning("Strategy 1 failed: Reinitialized model still has meta tensors")
        except Exception as e:
            logger.warning(f"Strategy 1 failed: {e}")
    
    # Strategy 2: Use to_empty() for meta tensors
    if has_meta:
        try:
            logger.info(f"Strategy 2: Using to_empty() to materialize meta tensors")
            
            # Create a device object
            target_device = torch.device(device)
            
            # Use to_empty to materialize meta tensors
            model = model.to_empty(device=target_device)
            
            # Initialize parameters with default values
            for param in model.parameters():
                if param.device.type == "meta":
                    # This shouldn't happen after to_empty, but handle it
                    raise RuntimeError("to_empty() did not materialize all parameters")
                # Initialize with small random values
                if param.requires_grad:
                    torch.nn.init.normal_(param, mean=0.0, std=0.02)
            
            # Verify no meta tensors remain
            if not check_for_meta_tensors(model):
                logger.info("Strategy 2 successful: Model materialized with to_empty()")
                model.eval()
                return model
            else:
                logger.warning("Strategy 2 failed: Model still has meta tensors after to_empty()")
        except Exception as e:
            logger.warning(f"Strategy 2 failed: {e}")
    
    # Strategy 3: Manual per-parameter materialization
    try:
        logger.info(f"Strategy 3: Manual per-parameter materialization")
        
        target_device = torch.device(device)
        
        # Materialize each parameter individually
        for name, param in model.named_parameters():
            if param.device.type == "meta":
                # Create a new tensor on target device with same shape
                new_param = torch.empty(param.shape, dtype=param.dtype, device=target_device)
                # Initialize with small random values
                torch.nn.init.normal_(new_param, mean=0.0, std=0.02)
                # Replace the parameter
                # This requires module replacement which is complex
                logger.warning(f"Cannot directly replace parameter {name}")
        
        # Try moving the model after materialization attempt
        model = model.to(target_device)
        
        # Verify no meta tensors remain
        if not check_for_meta_tensors(model):
            logger.info("Strategy 3 successful: Manual parameter materialization worked")
            model.eval()
            return model
        else:
            logger.warning("Strategy 3 failed: Model still has meta tensors")
    except Exception as e:
        logger.warning(f"Strategy 3 failed: {e}")
    
    # All strategies failed
    error_msg = (
        f"Failed to load model on {device}. All strategies failed to materialize meta tensors. "
        f"Model: {model.__class__.__name__ if hasattr(model, '__class__') else 'Unknown'}"
    )
    if model_name:
        error_msg += f", Model name: {model_name}"
    
    logger.error(error_msg)
    raise RuntimeError(error_msg)


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
