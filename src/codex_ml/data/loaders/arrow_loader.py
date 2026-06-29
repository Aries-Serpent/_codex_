"""
Apache Arrow IPC Dataset Loader v1.0.0
Zero-copy data sharing via Arrow's IPC format

Features:
- Memory-mapped file access
- Zero-copy deserialization
- Batch iteration support
- Schema validation
- Efficient for inter-process data sharing

Author: mbaetiong
Generated: 2025-11-19 04:02:05
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

try:
    import pyarrow as pa
    import pyarrow.ipc as ipc

    ARROW_AVAILABLE = True
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
    ARROW_AVAILABLE = False
    logger.warning("PyArrow not installed. Install: pip install pyarrow")


class ArrowLoader:
    """
    Efficient Arrow IPC file loader

    Arrow IPC format benefits:
    - Zero-copy reads via memory mapping
    - Language-agnostic format
    - Preserves schema metadata
    - Efficient for columnar data

    Examples:
        >>> loader = ArrowLoader("dataset.arrow")
        >>> data = loader.load()
        >>>
        >>> # Stream large files
        >>> for batch in loader.load_batched():
        >>>     process(batch)
    """

    def __init__(self, file_path: Path):
        """
        Initialize Arrow IPC loader

        Args:
            file_path: Path to .arrow file
        """
        if not ARROW_AVAILABLE:
            raise ImportError(
                "PyArrow required for Arrow support.\nInstall: pip install pyarrow>=10.0.0"
            )

        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Arrow file not found: {file_path}")

        # Validate file by opening
        try:
            with pa.memory_map(str(self.file_path), "r") as source:
                with ipc.open_file(source) as reader:
                    self.schema = reader.schema
                    self.num_batches = reader.num_record_batches
        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            raise ValueError(f"Invalid Arrow IPC file: {e}") from e

    def load(self) -> list[dict[str, Any]]:
        """
        Load entire Arrow file into memory

        Returns:
            list of dict records
        """
        logger.info(f"Loading Arrow IPC: {self.file_path}")

        with pa.memory_map(str(self.file_path), "r") as source:
            with ipc.open_file(source) as reader:
                table = reader.read_all()

        # Convert to list of dicts
        records = []
        for batch in table.to_batches():
            df = batch.to_pandas()
            records.extend(df.to_dict("records"))

        logger.info(f"Loaded {len(records)} records from Arrow")
        return records

    def load_batched(self) -> Iterator[list[dict[str, Any]]]:
        """
        Stream Arrow file in record batches

        Yields:
            Batches of dict records
        """
        logger.info("Streaming Arrow IPC in batches")

        with pa.memory_map(str(self.file_path), "r") as source:
            with ipc.open_file(source) as reader:
                for i in range(reader.num_record_batches):
                    batch = reader.get_batch(i)
                    df = batch.to_pandas()
                    yield df.to_dict("records")

    def get_schema(self) -> None:
        """
        Get Arrow schema

        Returns:
            PyArrow Schema object
        """
        return self.schema

    def get_metadata(self) -> dict[str, Any]:
        """
        Extract Arrow file metadata

        Returns:
            Metadata dictionary
        """
        with pa.memory_map(str(self.file_path), "r") as source:
            with ipc.open_file(source) as reader:
                return {
                    "num_batches": reader.num_record_batches,
                    "schema": str(self.schema),
                    "field_names": self.schema.names,
                    "field_types": [str(f.type) for f in self.schema],
                    "file_size_bytes": self.file_path.stat().st_size,
                }


def load_arrow(file_path: Path, batch_size: Optional[int] = None):
    """
    Convenience function to load Arrow IPC dataset

    Args:
        file_path: Path to .arrow file
        batch_size: If set, return batched generator

    Returns:
        list of dicts or generator of batches

    Examples:
        >>> # Load all
        >>> data = load_arrow("dataset.arrow")
        >>>
        >>> # Stream batches
        >>> for batch in load_arrow("large.arrow", batch_size=True):
        >>>     process(batch)
    """
    loader = ArrowLoader(file_path)

    if batch_size:
        return loader.load_batched()
    return loader.load()
