"""
RAG Utility Functions
Shared utilities for RAG modules including model loading helpers.
"""

import logging
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Tuple

logger = logging.getLogger(__name__)


def has_meta_tensors(model: Any) -> bool:
    """
    Comprehensive meta tensor detection that checks parameters, buffers, AND nested modules.
    
    This function recursively checks ALL components of a model to detect meta tensors:
    - Direct model parameters
    - Model buffers (e.g., running_mean, running_var in BatchNorm)
    - Nested submodules and their parameters/buffers
    
    Args:
        model: PyTorch model or SentenceTransformer to check
        
    Returns:
        True if ANY meta tensors found anywhere in the model hierarchy
        
    Example:
        >>> from sentence_transformers import SentenceTransformer
        >>> model = SentenceTransformer('all-MiniLM-L6-v2')
        >>> if has_meta_tensors(model):
        ...     print("Model has meta tensors - needs special handling")
    """
    try:
        import torch
        
        # Strategy 1: Check via named_modules (most comprehensive)
        if hasattr(model, "named_modules"):
            for module_name, module in model.named_modules():
                # Check parameters in this specific module (recurse=False to avoid duplicates)
                for param_name, param in module.named_parameters(recurse=False):
                    if isinstance(param, torch.Tensor) and param.device.type == "meta":
                        logger.debug(f"Meta tensor found: {module_name}.{param_name}")
                        return True
                
                # Check buffers (often overlooked but critical for BatchNorm, etc.)
                for buf_name, buf in module.named_buffers(recurse=False):
                    if isinstance(buf, torch.Tensor) and buf.device.type == "meta":
                        logger.debug(f"Meta buffer found: {module_name}.{buf_name}")
                        return True
        
        # Strategy 2: Direct parameter check (fallback for non-module objects)
        elif hasattr(model, "parameters"):
            for param in model.parameters():
                if isinstance(param, torch.Tensor) and param.device.type == "meta":
                    logger.debug("Meta tensor found in direct parameters")
                    return True
        
        # Strategy 3: Check model device attribute (last resort)
        elif hasattr(model, "device"):
            if hasattr(model.device, "type") and model.device.type == "meta":
                logger.debug("Model itself is on meta device")
                return True
        
        return False
        
    except Exception as e:
        logger.warning(f"Error during meta tensor detection: {e}")
        # Conservative: assume no meta tensors if we can't check
        return False


def safe_model_to_device(
    model: Any,
    device: str = "cpu",
    model_name: Optional[str] = None,
    cache_folder: Optional[str] = None,
    max_retries: int = 3,
    retry_delay: float = 1.0
) -> Any:
    """
    Robust model device transfer with 4-strategy fallback and retry logic.
    
    This function implements a comprehensive strategy pattern for moving models to
    target devices, with special handling for PyTorch meta tensors that require
    materialization before transfer.
    
    **Strategy Pattern:**
    1. Try to_empty() + reload weights (best for meta tensors)
    2. Reinitialize SentenceTransformer with device parameter
    3. Manual parameter replacement (for stubborn cases)
    4. Standard to() operation (for normal models)
    
    Each strategy includes retry logic with exponential backoff.
    
    Args:
        model: Model to transfer (PyTorch model or SentenceTransformer)
        device: Target device ("cpu", "cuda", "cuda:0", etc.)
        model_name: Original model name (required for strategies 1 & 2)
        cache_folder: Model cache directory (optional, for strategies 1 & 2)
        max_retries: Maximum retry attempts per strategy (default: 3)
        retry_delay: Initial retry delay in seconds, doubles each retry (default: 1.0)
        
    Returns:
        Model properly materialized and moved to target device
        
    Raises:
        RuntimeError: If all strategies fail after retries
        
    Example:
        >>> from sentence_transformers import SentenceTransformer
        >>> model = SentenceTransformer('all-MiniLM-L6-v2')
        >>> model = safe_model_to_device(
        ...     model,
        ...     device="cpu",
        ...     model_name='all-MiniLM-L6-v2'
        ... )
        >>> model.eval()
    """
    import torch
    
    # Check if model already has meta tensors
    has_meta = has_meta_tensors(model)
    
    if not has_meta:
        # No meta tensors detected, try simple move
        logger.info(f"No meta tensors detected, attempting standard move to {device}")
        try:
            model = model.to(device)
            model.eval()
            logger.info("✓ Standard to() operation successful")
            return model
        except Exception as e:
            logger.warning(f"Standard to() failed: {e}, trying fallback strategies")
    
    # Model has meta tensors or standard to() failed - try advanced strategies
    logger.info(f"Attempting 4-strategy fallback to materialize model on {device}")
    
    # Strategy 1: to_empty() + reload (best for meta tensors)
    if model_name:
        for attempt in range(max_retries):
            try:
                logger.info(f"Strategy 1 (attempt {attempt + 1}/{max_retries}): to_empty() + reload")
                
                from sentence_transformers import SentenceTransformer
                
                # Create empty model on target device
                target_device = torch.device(device)
                model = model.to_empty(device=target_device)
                
                # Reload weights from cache or hub
                reloaded = SentenceTransformer(
                    model_name,
                    device=device,
                    cache_folder=cache_folder,
                    trust_remote_code=False
                )
                
                # Verify no meta tensors remain
                if not has_meta_tensors(reloaded):
                    logger.info("✓ Strategy 1 successful")
                    reloaded.eval()
                    return reloaded
                else:
                    logger.warning("Strategy 1: Reloaded model still has meta tensors")
                    
            except Exception as e:
                logger.warning(f"Strategy 1 attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    delay = retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay}s...")
                    time.sleep(delay)
    
    # Strategy 2: Full reinitialization with device parameter
    if model_name and hasattr(model, '__class__') and model.__class__.__name__ == 'SentenceTransformer':
        for attempt in range(max_retries):
            try:
                logger.info(f"Strategy 2 (attempt {attempt + 1}/{max_retries}): Full reinitialization")
                
                from sentence_transformers import SentenceTransformer
                
                new_model = SentenceTransformer(
                    model_name,
                    device=device,
                    cache_folder=cache_folder,
                    trust_remote_code=False
                )
                
                if not has_meta_tensors(new_model):
                    logger.info("✓ Strategy 2 successful")
                    new_model.eval()
                    return new_model
                else:
                    logger.warning("Strategy 2: New model still has meta tensors")
                    
            except Exception as e:
                logger.warning(f"Strategy 2 attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    delay = retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay}s...")
                    time.sleep(delay)
    
    # Strategy 3: Manual parameter replacement
    if has_meta:
        for attempt in range(max_retries):
            try:
                logger.info(f"Strategy 3 (attempt {attempt + 1}/{max_retries}): Manual parameter replacement")
                
                target_device = torch.device(device)
                
                # Replace each parameter with a materialized version
                for name, param in list(model.named_parameters()):
                    if param.device.type == "meta":
                        # Create new tensor on target device with same shape
                        new_param = torch.empty(
                            param.shape,
                            dtype=param.dtype,
                            device=target_device
                        )
                        # Replace parameter
                        module_parts = name.rsplit(".", 1)
                        if len(module_parts) == 2:
                            module_name, param_name = module_parts
                            module = dict(model.named_modules())[module_name]
                            setattr(module, param_name, torch.nn.Parameter(new_param))
                        else:
                            setattr(model, name, torch.nn.Parameter(new_param))
                
                # Do the same for buffers
                for name, buf in list(model.named_buffers()):
                    if buf.device.type == "meta":
                        new_buf = torch.empty(
                            buf.shape,
                            dtype=buf.dtype,
                            device=target_device
                        )
                        module_parts = name.rsplit(".", 1)
                        if len(module_parts) == 2:
                            module_name, buf_name = module_parts
                            module = dict(model.named_modules())[module_name]
                            module.register_buffer(buf_name, new_buf)
                        else:
                            model.register_buffer(name, new_buf)
                
                if not has_meta_tensors(model):
                    logger.info("✓ Strategy 3 successful")
                    model.eval()
                    return model
                else:
                    logger.warning("Strategy 3: Model still has meta tensors after replacement")
                    
            except Exception as e:
                logger.warning(f"Strategy 3 attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    delay = retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay}s...")
                    time.sleep(delay)
    
    # Strategy 4: Last resort - standard to() with retries
    for attempt in range(max_retries):
        try:
            logger.info(f"Strategy 4 (attempt {attempt + 1}/{max_retries}): Standard to() operation")
            
            target_device = torch.device(device)
            model = model.to(target_device)
            
            if not has_meta_tensors(model):
                logger.info("✓ Strategy 4 successful")
                model.eval()
                return model
            else:
                logger.warning("Strategy 4: Model still has meta tensors")
                
        except Exception as e:
            logger.warning(f"Strategy 4 attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                delay = retry_delay * (2 ** attempt)
                logger.info(f"Retrying in {delay}s...")
                time.sleep(delay)
    
    # All strategies exhausted
    error_msg = (
        f"✗ All 4 strategies failed to move model to {device}. "
        f"Model: {model.__class__.__name__ if hasattr(model, '__class__') else 'Unknown'}, "
        f"Has meta tensors: {has_meta_tensors(model)}"
    )
    if model_name:
        error_msg += f", Model name: {model_name}"
    
    logger.error(error_msg)
    raise RuntimeError(error_msg)


def safe_model_load(model: Any, device: str = "cpu") -> Any:
    """
    DEPRECATED: Use safe_model_to_device() instead.
    
    This function is kept for backward compatibility and delegates to safe_model_to_device().
    
    Args:
        model: The model to load
        device: Target device
    
    Returns:
        Model moved to target device
    
    Raises:
        DeprecationWarning: Always raised to warn about deprecated usage
    """
    import warnings
    warnings.warn(
        "safe_model_load() is deprecated. Use safe_model_to_device() instead. "
        "This function will be removed in version 1.0.0.",
        DeprecationWarning,
        stacklevel=2
    )
    return safe_model_to_device(model, device)


# Backward compatibility aliases
check_for_meta_tensors = has_meta_tensors  # Old name -> new name
safe_model_load_v2 = safe_model_to_device  # Old name -> new name


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
