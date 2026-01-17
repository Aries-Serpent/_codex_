"""
GPU Utilities for RAG Pipeline

Provides GPU detection, memory management, and automatic CPU/GPU fallback.
"""

import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

def check_cuda_available() -> bool:
    """
    Check if CUDA is available.
    
    Returns:
        True if CUDA is available, False otherwise
    """
    try:
        import torch
        available = torch.cuda.is_available()
        if available:
            logger.info(f"✓ CUDA available: {torch.cuda.get_device_name(0)}")
        return available
    except ImportError:
        logger.debug("PyTorch not installed")
        return False
    except Exception as e:
        logger.debug(f"CUDA check failed: {e}")
        return False


def get_gpu_memory() -> Tuple[int, int]:
    """
    Get GPU memory (free, total) in bytes.
    
    Returns:
        Tuple of (free_memory, total_memory) in bytes
    """
    try:
        import torch
        if torch.cuda.is_available():
            free, total = torch.cuda.mem_get_info()
            logger.debug(f"GPU memory: {free / 1e9:.2f}GB free / {total / 1e9:.2f}GB total")
            return free, total
    except Exception as e:
        logger.debug(f"Could not get GPU memory: {e}")
    return 0, 0


def select_device(prefer_gpu: bool = True) -> str:
    """
    Select best available device (cpu or cuda).
    
    Args:
        prefer_gpu: Prefer GPU if available
        
    Returns:
        Device string ('cpu' or 'cuda')
    """
    if prefer_gpu and check_cuda_available():
        return "cuda"
    return "cpu"


def get_optimal_batch_size(
    embedding_dim: int = 384,
    max_memory_gb: float = 2.0,
    safety_factor: float = 0.8,
) -> int:
    """
    Calculate optimal batch size based on available GPU memory.
    
    Args:
        embedding_dim: Dimension of embeddings
        max_memory_gb: Maximum memory to use in GB
        safety_factor: Safety factor (0-1) to avoid OOM
        
    Returns:
        Optimal batch size
    """
    # Estimate memory per embedding (float32)
    bytes_per_embedding = embedding_dim * 4
    
    # Get available memory
    free_memory, _ = get_gpu_memory()
    if free_memory == 0:
        # Default for CPU
        return 32
    
    # Calculate batch size
    available_memory = free_memory * safety_factor
    max_batch_size = int(available_memory / bytes_per_embedding)
    
    # Clamp to reasonable range
    batch_size = max(8, min(max_batch_size, 512))
    logger.debug(f"Optimal batch size: {batch_size}")
    return batch_size


def try_gpu_index(index, data, device: str = "cuda"):
    """
    Try to move FAISS index to GPU.
    
    Args:
        index: FAISS index
        data: Index data (optional)
        device: Target device
        
    Returns:
        GPU index if successful, original index otherwise
    """
    if device != "cuda" or not check_cuda_available():
        return index
    
    try:
        import faiss
        
        # Check if GPU version is available
        if not hasattr(faiss, 'StandardGpuResources'):
            logger.warning("faiss-gpu not available, using CPU")
            return index
        
        # Create GPU resources
        res = faiss.StandardGpuResources()
        
        # Convert to GPU index
        gpu_index = faiss.index_cpu_to_gpu(res, 0, index)
        logger.info("✓ Index moved to GPU")
        return gpu_index
        
    except Exception as e:
        logger.warning(f"Failed to move index to GPU: {e}")
        logger.info("Continuing with CPU index")
        return index
