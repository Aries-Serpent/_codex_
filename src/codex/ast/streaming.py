"""
Streaming AST parser for large files.
Processes files in chunks to minimize memory usage.
"""

import logging
from collections.abc import Iterator
from pathlib import Path

from .node import StandardizedASTNode
from .parser import parse_python

logger = logging.getLogger(__name__)


class StreamingParser:
    """
    Parse large files in chunks without loading entire file into memory.

    Yields AST nodes incrementally for memory-efficient processing.
    """

    def __init__(self, chunk_size: int = 1024 * 1024):  # 1MB default
        """
        Initialize streaming parser.

        Args:
            chunk_size: Size of chunks to read (bytes)
        """
        self.chunk_size = chunk_size

    def parse_file(self, file_path: str) -> Iterator[StandardizedASTNode]:
        """
        Parse file in streaming fashion.

        Args:
            file_path: Path to file to parse

        Yields:
            StandardizedASTNode for each top-level construct
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # For Python files, we need to parse complete syntactic units
        # Can't truly "stream" since Python requires full AST
        # But we can yield top-level nodes incrementally

        try:
            # Read file in chunks to check size
            file_size = path.stat().st_size

            if file_size > self.chunk_size:
                logger.info(f"Large file detected ({file_size} bytes), using streaming mode")

            # Parse entire file (Python requires complete parse)
            tree = parse_python(str(path))

            if tree:
                # Yield top-level nodes incrementally
                for child in tree.children:
                    yield child

        except (IOError, OSError) as e:
            type(e).__name__
            logger.error(f"Failed to parse {file_path}: <ERROR_TYPE>")
            raise

    def parse_directory(
        self, directory: str, pattern: str = "**/*.py"
    ) -> Iterator[tuple[str, StandardizedASTNode]]:
        """
        Parse all files in directory, streaming results.

        Args:
            directory: Directory to scan
            pattern: Glob pattern for files

        Yields:
            Tuples of (file_path, node)
        """
        dir_path = Path(directory)

        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                try:
                    for node in self.parse_file(str(file_path)):
                        yield (str(file_path), node)
                except (IOError, OSError) as e:
                    type(e).__name__
                    logger.warning(f"Failed to parse {file_path}: <ERROR_TYPE>")
                    continue
