"""
Session-based caching utilities for Codex processing optimization.

Purpose:
  Reduce file I/O overhead by caching frequently accessed files
  and memoizing search results during a session.

References:
  - Analysis finding: 24+ duplicate file reads per session
  - Unix principle: Cache results, avoid redundant I/O

Classes:
  - FileCache: Mtime-aware file content cache
  - SearchCache: Memoization decorator for search operations
"""

from __future__ import annotations

import hashlib
import logging
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class FileCache:
    """Mtime-aware file content cache for session optimization.

    Usage:
        cache = FileCache()
        cache.add("scripts/survey.sh")
        content = cache.get("scripts/survey.sh")  # Returns cached content
        cache.invalidate_if_modified("scripts/survey.sh")  # Refresh if changed
    """

    def __init__(self) -> None:
        """Initialize file cache."""
        self._file_contents: dict[str, str] = {}
        self._file_mtimes: dict[str, float] = {}
        self._file_shas: dict[str, str] = {}
        logger.info("FileCache initialized")

    def add(self, file_path: str) -> bool:
        """Add file to cache. Returns True if successful, False if file not found."""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()

            stat = path.stat()
            sha = hashlib.sha256(content.encode()).hexdigest()

            self._file_contents[file_path] = content
            self._file_mtimes[file_path] = stat.st_mtime
            self._file_shas[file_path] = sha

            logger.debug(f"Cached file ({len(content)} bytes): {file_path}")
            return True
        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.error(f"Failed to cache file {file_path}: <ERROR_TYPE>")
            return False

    def get(self, file_path: str, auto_refresh: bool = True) -> Optional[str]:
        """Retrieve cached content. If auto_refresh, validates mtime first."""
        if auto_refresh:
            self.invalidate_if_modified(file_path)

        if file_path not in self._file_contents:
            logger.warning(f"Cache miss: {file_path} (not cached)")
            return None

        logger.debug(f"Cache hit: {file_path}")
        return self._file_contents[file_path]

    def invalidate_if_modified(self, file_path: str) -> bool:
        """Check if file modified since caching. Refresh if needed. Returns True if refreshed."""
        if file_path not in self._file_mtimes:
            return False

        path = Path(file_path)
        if not path.exists():
            logger.warning(f"Cached file no longer exists: {file_path}")
            self.clear(file_path)
            return False

        current_mtime = path.stat().st_mtime
        if current_mtime != self._file_mtimes[file_path]:
            logger.info(f"File modified, refreshing cache: {file_path}")
            self.clear(file_path)
            return self.add(file_path)

        return False

    def get_sha(self, file_path: str) -> Optional[str]:
        """Retrieve cached SHA256 hash of file."""
        return self._file_shas.get(file_path)

    def clear(self, file_path: str) -> None:
        """Remove file from cache."""
        self._file_contents.pop(file_path, None)
        self._file_mtimes.pop(file_path, None)
        self._file_shas.pop(file_path, None)
        logger.debug(f"Cleared cache: {file_path}")

    def clear_all(self) -> None:
        """Clear entire cache."""
        self._file_contents.clear()
        self._file_mtimes.clear()
        self._file_shas.clear()
        logger.info("Cache cleared (all files)")

    def stats(self) -> dict[str, Any]:
        """Return cache statistics."""
        return {
            "cached_files": len(self._file_contents),
            "total_size_bytes": sum(len(c) for c in self._file_contents.values()),
            "files": list(self._file_contents.keys()),
        }


class SearchCache:
    """Memoization decorator for search operations.

    Usage:
        cache = SearchCache()

        @cache.memoize
        def find_files(pattern, scope):
            # SECURE: Use shell=False and properly quoted arguments
            result = subprocess.run(
                ['find', scope, '-name', pattern],
                capture_output=True,
                text=True,
                shell=False,
                timeout=30
            )
            return result.stdout

        result1 = find_files('*.py', '/src')  # Executes search
        result2 = find_files('*.py', '/src')  # Returns cached result
    """

    def __init__(self) -> None:
        """Initialize search cache."""
        self._cache: dict[str, Any] = {}
        logger.info("SearchCache initialized")

    def _validate_path_arg(self, path_str: str, arg_name: str = "path") -> str:
        """Validate path argument to prevent command injection.

        Parameters:
            path_str: Path to validate
            arg_name: Name of argument for error messages

        Returns:
            Validated path string

        Raises:
            ValueError: If path contains suspicious patterns
        """
        if not path_str:
            raise ValueError(f"{arg_name} cannot be empty")
        if ".." in path_str:
            raise ValueError(f"{arg_name} cannot contain '..' (path traversal)")
        if any(c in path_str for c in [";", "|", "&", "$", "`", "\n", "\r"]):
            raise ValueError(f"{arg_name} contains shell metacharacters")
        return path_str

    def _validate_pattern_arg(self, pattern: str) -> str:
        """Validate glob pattern argument to prevent command injection.

        Parameters:
            pattern: Glob pattern to validate

        Returns:
            Validated pattern string

        Raises:
            ValueError: If pattern contains suspicious sequences
        """
        if not pattern:
            raise ValueError("pattern cannot be empty")
        if any(c in pattern for c in [";", "|", "&", "$", "`", "\n", "\r", "'"]):
            raise ValueError("pattern contains forbidden characters")
        return pattern

    def memoize(self, func: Callable) -> Callable:
        """Decorator to memoize function results."""

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            key = f"{func.__name__}:{args!s}:{kwargs!s}"
            if key in self._cache:
                logger.debug(f"Search cache hit: {func.__name__}")
                return self._cache[key]

            result = func(*args, **kwargs)
            self._cache[key] = result
            logger.debug(f"Search cached: {func.__name__}")
            return result

        return wrapper

    def clear(self) -> None:
        """Clear search cache."""
        self._cache.clear()
        logger.info("Search cache cleared")
