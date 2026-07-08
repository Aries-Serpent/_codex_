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
from typing import List, Optional

__all__ = [
    "safe_path",
    "path_exists",
    "ensure_path_exists",
    "find_files",
    "get_repo_root",
    "windows_safe_timestamp",
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
        >>> safe_path(os.path.join(tempfile.gettempdir(), 'file.txt'))
        PosixPath(os.path.join(tempfile.gettempdir(), 'file.txt'))
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
            pattern = "*"

        glob_pattern = f"**/{pattern}" if recursive else pattern
        return list(root.glob(glob_pattern))
    except (OSError, ValueError):
        return []


def get_repo_root() -> Path:
    """
    Get the repository root directory.

    Searches upward from current directory for .git directory.
    Falls back to current working directory if not found.

    Returns:
        Path to repository root

    Example:
        >>> repo_root = get_repo_root()
        >>> config_file = repo_root / "pyproject.toml"
    """
    current = Path.cwd()

    # Search upward for .git directory
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent

    # Fallback to current working directory
    return Path.cwd()


def windows_safe_timestamp(fmt: str = "iso") -> str:
    """
    Generate a Windows-safe timestamp for filenames.

    Windows filesystems prohibit these characters in filenames: < > : " / \\ | ? *
    This function generates timestamps without colons (which break filenames).

    Args:
        fmt: Format type - 'iso', 'compact', or 'readable'
             - 'iso': 2026-01-23T14-30-45Z (ISO format with hyphens instead of colons)
             - 'compact': 20260123_143045 (YYYYMMdd_HHmmss)
             - 'readable': 2026-01-23-14-30-45-UTC (human-readable with hyphens)

    Returns:
        Formatted timestamp string safe for Windows filenames

    Example:
        >>> timestamp = windows_safe_timestamp(fmt="compact")
        >>> filename = f"log_{timestamp}.txt"  # log_20260123_143045.txt
    """
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)

    if fmt == "iso":
        # ISO format: 2026-01-23T14-30-45Z (colons replaced with hyphens)
        return now.strftime("%Y-%m-%dT%H-%M-%SZ")
    elif fmt == "compact":
        # Compact format: 20260123_143045
        return now.strftime("%Y%m%d_%H%M%S")
    elif fmt == "readable":
        # Readable format: 2026-01-23-14-30-45-UTC
        return now.strftime("%Y-%m-%d-%H-%M-%S-UTC")
    else:
        # Default to compact if unknown format
        return now.strftime("%Y%m%d_%H%M%S")
