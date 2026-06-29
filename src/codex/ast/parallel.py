"""
Parallel AST parsing for improved performance.
"""

import logging
import threading
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

from .node import StandardizedASTNode
from .parser import parse_python

logger = logging.getLogger(__name__)


class ParallelParser:
    """
    Parse multiple files concurrently using thread pool.

    Provides thread-safe node ID generation and progress tracking.
    """

    def __init__(self, max_workers: Optional[int] = None):
        """
        Initialize parallel parser.

        Args:
            max_workers: Maximum number of worker threads (None = CPU count)
        """
        self.max_workers = max_workers
        self._node_id_counter = 0
        self._lock = threading.Lock()

    def _generate_node_id(self) -> int:
        """Generate thread-safe unique node ID."""
        with self._lock:
            self._node_id_counter += 1
            return self._node_id_counter

    def parse_files(
        self,
        file_paths: list[str],
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse multiple files in parallel.

        Args:
            file_paths: list of file paths to parse
            progress_callback: Optional callback(file_path, completed, total)

        Returns:
            Dictionary mapping file_path to parsed node
        """
        results = {}
        total = len(file_paths)
        completed = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all parse tasks
            future_to_path = {executor.submit(self._parse_file, path): path for path in file_paths}

            # Collect results as they complete
            for future in as_completed(future_to_path):
                file_path = future_to_path[future]

                try:
                    node = future.result()
                    if node:
                        results[file_path] = node
                except (IOError, OSError) as e:
                    type(e).__name__
                    logger.error(f"Failed to parse {file_path}: <ERROR_TYPE>")

                # Update progress
                completed += 1
                if progress_callback:
                    progress_callback(file_path, completed, total)

        return results

    def _parse_file(self, file_path: str) -> Optional[StandardizedASTNode]:
        """Parse a single file (called in worker thread)."""
        try:
            return parse_python(file_path)
        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug(f"Parse error in {file_path}: <ERROR_TYPE>")
            return None

    def parse_directory(
        self,
        directory: str,
        pattern: str = "**/*.py",
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
    ) -> dict[str, StandardizedASTNode]:
        """
        Parse all files in directory in parallel.

        Args:
            directory: Directory to scan
            pattern: Glob pattern for files
            progress_callback: Optional progress callback

        Returns:
            Dictionary mapping file_path to parsed node
        """
        dir_path = Path(directory)
        file_paths = [str(p) for p in dir_path.glob(pattern) if p.is_file()]

        logger.info(f"Parsing {len(file_paths)} files in parallel")
        return self.parse_files(file_paths, progress_callback)
