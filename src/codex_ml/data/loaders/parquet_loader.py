"""
Parquet Dataset Loader v1.0.0
Production-ready Apache Parquet file handling with streaming support

Features:
- Column selection optimization
- Batched loading for large files
- Memory-efficient streaming
- Metadata extraction
- Compression support (snappy, gzip, lz4)

Author: mbaetiong
Generated: 2025-11-19 04:02:05
"""

from __future__ import annotations

import importlib.util
import logging
from collections.abc import Iterator
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

try:
    import pyarrow.parquet as pq

    PARQUET_AVAILABLE = importlib.util.find_spec("pandas") is not None
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
    PARQUET_AVAILABLE = False
    logger.warning("PyArrow not installed. Install: pip install pyarrow")


class ParquetLoader:
    """
    Efficient Parquet file loader with streaming capabilities

    Examples:
        >>> loader = ParquetLoader("dataset.parquet", columns=["text", "label"])
        >>> data = loader.load()
        >>>
        >>> # Streaming for large files
        >>> for batch in loader.load_batched(batch_size=10000):
        >>>     process(batch)
    """

    def __init__(
        self,
        file_path: Path,
        columns: Optional[list[str]] = None,
        use_threads: bool = True,
    ):
        """
        Initialize Parquet loader

        Args:
            file_path: Path to .parquet file
            columns: Columns to load (None = all)
            use_threads: Enable multi-threaded reading
        """
        if not PARQUET_AVAILABLE:
            raise ImportError(
                "PyArrow required for Parquet support.\nInstall: pip install pyarrow>=10.0.0"
            )

        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Parquet file not found: {file_path}")

        self.columns = columns
        self.use_threads = use_threads

        # Validate file
        try:
            self.parquet_file = pq.ParquetFile(self.file_path)
            self.metadata = self.parquet_file.metadata
        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            raise ValueError(f"Invalid Parquet file: {e}") from e

    def load(self) -> list[dict[str, Any]]:
        """
        Load entire Parquet file into memory

        Returns:
            list of dictionaries (records)
        """
        logger.info(f"Loading Parquet: {self.file_path}")

        # Read with optimizations
        table = pq.read_table(
            self.file_path,
            columns=self.columns,
            use_threads=self.use_threads,
            memory_map=True,  # Memory-map for efficiency
        )

        # Convert to pandas then dict records
        df = table.to_pandas()
        records = df.to_dict("records")

        logger.info(f"Loaded {len(records)} records from Parquet")
        return records

    def load_batched(self, batch_size: int = 10000) -> Iterator[list[dict[str, Any]]]:
        """
        Stream Parquet file in batches (memory efficient)

        Args:
            batch_size: Records per batch

        Yields:
            Batches of dict records
        """
        logger.info(f"Streaming Parquet in batches of {batch_size}")

        for batch in self.parquet_file.iter_batches(batch_size=batch_size):
            df = batch.to_pandas()

            # Filter columns if specified
            if self.columns:
                df = df[self.columns]

            yield df.to_dict("records")

    def get_metadata(self) -> dict[str, Any]:
        """
        Extract Parquet file metadata

        Returns:
            Metadata dictionary
        """
        return {
            "num_rows": self.metadata.num_rows,
            "num_columns": self.metadata.num_columns,
            "num_row_groups": self.metadata.num_row_groups,
            "format_version": self.metadata.format_version,
            "created_by": self.metadata.created_by,
            "schema": self.parquet_file.schema.to_arrow_schema(),
            "file_size_bytes": self.file_path.stat().st_size,
        }

    def get_column_stats(self) -> dict[str, dict[str, Any]]:
        """
        Get statistics for each column

        Returns:
            Column name -> stats dictionary
        """
        stats = {}

        for i in range(self.metadata.num_columns):
            col_meta = self.metadata.row_group(0).column(i)
            col_name = self.parquet_file.schema[i].name

            stats[col_name] = {
                "total_compressed_size": col_meta.total_compressed_size,
                "total_uncompressed_size": col_meta.total_uncompressed_size,
                "compression": col_meta.compression,
            }

        return stats


def load_parquet(
    file_path: Path,
    columns: Optional[list[str]] = None,
    batch_size: Optional[int] = None,
    use_threads: bool = True,
):
    """
    Convenience function to load Parquet dataset

    Args:
        file_path: Path to .parquet file
        columns: Columns to load (None = all)
        batch_size: If set, return batched generator
        use_threads: Enable multi-threaded reading

    Returns:
        list of dicts or generator of batches

    Examples:
        >>> # Load all at once
        >>> data = load_parquet("dataset.parquet")
        >>>
        >>> # Stream in batches
        >>> for batch in load_parquet("large.parquet", batch_size=5000):
        >>>     process(batch)
        >>>
        >>> # Load specific columns only
        >>> data = load_parquet("dataset.parquet", columns=["text", "label"])
    """
    loader = ParquetLoader(file_path, columns, use_threads)

    if batch_size:
        return loader.load_batched(batch_size)
    return loader.load()
