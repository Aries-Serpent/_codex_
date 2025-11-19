"""
Dataset Loader Registry v1.0.0
Unified interface for all data loading backends

Supports:
- JSONL (line-delimited JSON)
- CSV/TSV (delimiter-separated)
- Parquet (Apache Parquet columnar)
- Arrow (Arrow IPC zero-copy)
- HDF5 (hierarchical scientific data)
- HuggingFace Datasets

Author: mbaetiong
Generated: 2025-11-19 04:02:05
"""
from pathlib import Path
from typing import Any, Callable, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Lazy imports to avoid hard dependencies
_LOADERS: Dict[str, Callable] = {}


def register_loader(extensions: list, loader_fn: Callable):
    """
    Register a loader function for file extensions
    
    Args:
        extensions: List of file extensions (e.g., ['.jsonl', '.json'])
        loader_fn: Function that takes (path, **kwargs) and returns data
    """
    for ext in extensions:
        _LOADERS[ext.lower()] = loader_fn
        logger.debug(f"Registered loader for {ext}")


def load_dataset(file_path, **kwargs) -> Any:
    """
    Automatically load dataset based on file extension
    
    Args:
        file_path: Path to dataset file
        **kwargs: Passed to specific loader
    
    Returns:
        Loaded dataset (format depends on file type)
    
    Raises:
        ValueError: If file extension not supported
    
    Examples:
        >>> # Automatic format detection
        >>> data = load_dataset("train.jsonl")
        >>> data = load_dataset("embeddings.parquet")
        >>> data = load_dataset("features.h5", dataset_path="/train/features")
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {path}")
    
    ext = path.suffix.lower()
    
    if ext not in _LOADERS:
        raise ValueError(
            f"Unsupported file extension: {ext}\n"
            f"Supported: {list(_LOADERS.keys())}"
        )
    
    logger.info(f"Loading dataset: {path} (format: {ext})")
    loader_fn = _LOADERS[ext]
    
    return loader_fn(path, **kwargs)


# Register built-in loaders
def _lazy_load_parquet():
    from .parquet_loader import load_parquet
    return load_parquet


def _lazy_load_arrow():
    from .arrow_loader import load_arrow
    return load_arrow


def _lazy_load_hdf5():
    from .hdf5_loader import load_hdf5
    return load_hdf5


# Register extensions
register_loader(['.parquet'], _lazy_load_parquet)
register_loader(['.arrow', '.ipc'], _lazy_load_arrow)
register_loader(['.h5', '.hdf5'], _lazy_load_hdf5)


__all__ = [
    'load_dataset',
    'register_loader',
    'load_parquet',
    'load_arrow',
    'load_hdf5',
]
