"""
HDF5 Dataset Loader v1.0.0
Hierarchical Data Format (HDF5) support for scientific datasets

Features:
- Hierarchical group navigation
- Dataset slicing and chunking
- Compression support
- Attribute metadata access
- Memory-efficient streaming

Author: mbaetiong
Generated: 2025-11-19 04:02:05
"""

from __future__ import annotations

import importlib.util
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

try:
    import h5py

    HDF5_AVAILABLE = importlib.util.find_spec("numpy") is not None
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
    HDF5_AVAILABLE = False
    logger.warning("h5py not installed. Install: pip install h5py")


class HDF5Loader:
    """
    HDF5 hierarchical dataset loader

    Common use cases:
    - Scientific datasets
    - Large numerical arrays
    - Embeddings and feature vectors
    - Time-series data

    Examples:
        >>> loader = HDF5Loader("embeddings.h5", dataset_path="/train/embeddings")
        >>> data = loader.load()
        >>>
        >>> # Stream chunks
        >>> for chunk in loader.load_chunked(chunk_size=1000):
        >>>     process(chunk)
    """

    def __init__(self, file_path: Path, dataset_path: str = "/", mode: str = "r"):
        """
        Initialize HDF5 loader

        Args:
            file_path: Path to .h5 or .hdf5 file
            dataset_path: Path within HDF5 hierarchy
            mode: File open mode ('r', 'r+', 'w', 'a')
        """
        if not HDF5_AVAILABLE:
            raise ImportError("h5py required for HDF5 support.\nInstall: pip install h5py>=3.0.0")

        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"HDF5 file not found: {file_path}")

        self.dataset_path = dataset_path
        self.mode = mode

        # Validate file
        try:
            with h5py.File(self.file_path, "r") as f:
                if dataset_path != "/" and dataset_path not in f:
                    raise KeyError(f"Dataset path not found: {dataset_path}")
        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            raise ValueError(f"Invalid HDF5 file: {e}") from e

    def load(self) -> object:
        """
        Load HDF5 dataset into memory

        Returns:
            NumPy array or dict of arrays (for groups)
        """
        logger.info(f"Loading HDF5: {self.file_path}:{self.dataset_path}")

        with h5py.File(self.file_path, self.mode) as f:
            obj = f[self.dataset_path]

            if isinstance(obj, h5py.Dataset):
                # Single dataset
                data = obj[:]
                logger.info(f"Loaded dataset shape: {data.shape}")
                return data
            if isinstance(obj, h5py.Group):
                # Group of datasets
                data = {}
                for key in obj:
                    data[key] = obj[key][:]
                logger.info(f"Loaded group with {len(data)} datasets")
                return data
            raise ValueError(f"Unknown HDF5 object type: {type(obj)}")

    def load_chunked(self, chunk_size: int = 1000):
        """
        Stream HDF5 dataset in chunks

        Args:
            chunk_size: Rows per chunk

        Yields:
            NumPy array chunks
        """
        logger.info(f"Streaming HDF5 in chunks of {chunk_size}")

        with h5py.File(self.file_path, self.mode) as f:
            dataset = f[self.dataset_path]

            if not isinstance(dataset, h5py.Dataset):
                raise ValueError("Chunked loading only for datasets, not groups")

            num_rows = dataset.shape[0]

            for start_idx in range(0, num_rows, chunk_size):
                end_idx = min(start_idx + chunk_size, num_rows)
                yield dataset[start_idx:end_idx]

    def get_metadata(self) -> dict[str, Any]:
        """
        Extract HDF5 metadata

        Returns:
            Metadata dictionary
        """
        with h5py.File(self.file_path, "r") as f:
            obj = f[self.dataset_path]

            if isinstance(obj, h5py.Dataset):
                return {
                    "shape": obj.shape,
                    "dtype": str(obj.dtype),
                    "compression": obj.compression,
                    "chunks": obj.chunks,
                    "attributes": dict(obj.attrs),
                }
            if isinstance(obj, h5py.Group):
                return {
                    "type": "group",
                    "keys": list(obj.keys()),
                    "attributes": dict(obj.attrs),
                }
            return {}

    def list_datasets(self) -> list[str]:
        """
        list all dataset paths in file

        Returns:
            list of dataset paths
        """
        paths = []

        def visitor(name, obj) -> None:
            if isinstance(obj, h5py.Dataset):
                paths.append(name)

        with h5py.File(self.file_path, "r") as f:
            f.visititems(visitor)

        return sorted(paths)


def load_hdf5(file_path: Path, dataset_path: str = "/", chunk_size: Optional[int] = None):
    """
    Convenience function to load HDF5 dataset

    Args:
        file_path: Path to .h5/.hdf5 file
        dataset_path: HDF5 internal path
        chunk_size: If set, return chunked generator

    Returns:
        NumPy array or generator of chunks

    Examples:
        >>> # Load entire dataset
        >>> embeddings = load_hdf5("data.h5", "/embeddings")
        >>>
        >>> # Stream chunks
        >>> for chunk in load_hdf5("large.h5", "/data", chunk_size=5000):
        >>>     process(chunk)
    """
    loader = HDF5Loader(file_path, dataset_path)

    if chunk_size:
        return loader.load_chunked(chunk_size)
    return loader.load()
