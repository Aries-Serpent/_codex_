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
from importlib import util
from pathlib import Path
from typing import Any, Callable, Dict
import inspect
import logging
import sys

logger = logging.getLogger(__name__)

# Lazy imports to avoid hard dependencies
_LOADERS: Dict[str, Callable] = {}
_CORE_MODULE_NAME = "codex_ml.data._core_loaders"
_CORE_MODULE_PATH = Path(__file__).resolve().parent.parent / "loaders.py"

if _CORE_MODULE_NAME in sys.modules:
    _core = sys.modules[_CORE_MODULE_NAME]
else:
    spec = util.spec_from_file_location(_CORE_MODULE_NAME, _CORE_MODULE_PATH)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError(f"Unable to load core loaders from {_CORE_MODULE_PATH}")
    _core = util.module_from_spec(spec)
    sys.modules[_CORE_MODULE_NAME] = _core
    spec.loader.exec_module(_core)

# Re-export helpers from the core loader module for compatibility with
# ``from codex_ml.data.loaders import ...`` call sites.
stream_paths = _core.stream_paths
iter_jsonl = _core.iter_jsonl
iter_txt = _core.iter_txt
collect_stats = _core.collect_stats
split_indices = _core.split_indices
load_jsonl = _core.load_jsonl
load_csv = _core.load_csv
compute_file_checksum = _core.compute_file_checksum
Sample = _core.Sample


def _resolve_loader(loader_entry: Callable) -> Callable:
    """Resolve lazy loader factories into actual loader callables."""

    if not callable(loader_entry):
        raise TypeError("Registered loader must be callable")

    try:
        signature = inspect.signature(loader_entry)
    except (TypeError, ValueError):
        # Built-in or C-level callables without signature support
        return loader_entry

    if len(signature.parameters) == 0:
        resolved = loader_entry()
        if not callable(resolved):
            raise TypeError("Lazy loader factory must return a callable")
        return resolved

    return loader_entry


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
    loader_fn = _resolve_loader(_LOADERS[ext])

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
    "load_dataset",
    "register_loader",
    "stream_paths",
    "iter_jsonl",
    "iter_txt",
    "collect_stats",
    "split_indices",
    "load_jsonl",
    "load_csv",
    "compute_file_checksum",
    "Sample",
]


__all__ = [
    'load_dataset',
    'register_loader',
    'load_parquet',
    'load_arrow',
    'load_hdf5',
]
