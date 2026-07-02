"""
P008: Extended Path Operations Utilities

Consolidates 2,224 occurrences of path operations.

Example:
    # Instead of: Path(path).exists()
    if path_exists(path):
        ...
    
    # Instead of: os.path.exists(path) or os.path.is_dir(path)
    ensure_path_exists(path)
"""

from pathlib import Path
from typing import Optional, List, Pattern

__all__ = [
    "safe_path",
    "path_exists",
    "ensure_path_exists",
    "find_files",
    "PathError",
]


class PathError(OSError):
    """Raised when path operations fail."""

    pass


def safe_path(path_str: str) -> Path:
    """
    Convert string to safe Path object.

    Args:
        path_str: Path string

    Returns:
        Path object

    Example:
        >>> safe_path('/tmp/file.txt')
        PosixPath('/tmp/file.txt')
    """
    if not path_str:
        raise PathError("Path string cannot be empty")
    return Path(path_str).resolve()


def path_exists(path_str: str) -> bool:
    """
    Check if path exists.

    Args:
        path_str: Path to check

    Returns:
        True if path exists
    """
    try:
        return Path(path_str).exists()
    except (OSError, ValueError):
        return False


def ensure_path_exists(
    path_str: str,
    is_dir: bool = False,
) -> Path:
    """
    Ensure path exists, creating if necessary.

    Args:
        path_str: Path to ensure
        is_dir: If True, treat as directory

    Returns:
        The path

    Raises:
        PathError: If creation fails
    """
    try:
        path = Path(path_str).resolve()

        if is_dir:
            path.mkdir(parents=True, exist_ok=True)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch(exist_ok=True)

        return path
    except OSError as e:
        raise PathError(f"Cannot ensure path {path_str}: {e}") from e


def find_files(
    root_path: str,
    pattern: Optional[str] = None,
    recursive: bool = True,
) -> List[Path]:
    """
    Find files matching pattern.

    Args:
        root_path: Root directory to search
        pattern: Glob pattern (e.g., '*.py')
        recursive: If True, search recursively

    Returns:
        List of matching paths
    """
    try:
        root = Path(root_path)

        if not root.exists():
            return []

        if pattern is None:
            pattern = '*'

        glob_pattern = f"**/{pattern}" if recursive else pattern
        return list(root.glob(glob_pattern))
    except (OSError, ValueError):
        return []
