"""Security utilities for safe file operations in tests.

This module provides secure wrappers for common file operations that prevent
path traversal and other security vulnerabilities.
"""

from __future__ import annotations

import os
import tarfile
from pathlib import Path
from typing import Optional


def safe_extract_tarfile(
    tar_path: Path,
    extract_to: Path,
    *,
    members: Optional[list] = None,
) -> None:
    """Safely extract tarfile preventing path traversal attacks.

    Security: Validates all paths before extraction to prevent directory traversal
    attacks (e.g., files with names like '../../../etc/passwd').

    Args:
        tar_path: Path to the tarfile to extract
        extract_to: Directory to extract files to
        members: Optional list of specific members to extract (None = all)

    Raises:
        ValueError: If any member path attempts to traverse outside extract directory

    Example:
        >>> safe_extract_tarfile(Path("archive.tar.gz"), Path(os.path.join(tempfile.gettempdir(), "extract")))
    """
    extract_to = extract_to.resolve()

    with tarfile.open(tar_path) as tar:
        # Get members to extract
        to_extract = members if members is not None else tar.getmembers()

        # Validate all paths before extraction
        for member in to_extract:
            # Resolve the extraction path
            member_path = (extract_to / member.name).resolve()

            # Check if path escapes the extraction directory
            try:
                member_path.relative_to(extract_to)
            except ValueError:
                raise ValueError(
                    f"Security: Attempted path traversal in tarfile member: {member.name}"
                )

            # Additional check for absolute paths
            if member.name.startswith("/") or member.name.startswith("\\"):
                raise ValueError(f"Security: Absolute path in tarfile member: {member.name}")

        # Python 3.12+ has built-in filter, use it if available
        if hasattr(tarfile, "data_filter"):
            # Use Python 3.12+ secure filter
            tar.extraction_filter = tarfile.data_filter  # type: ignore

        # Extract (now validated)
        tar.extractall(extract_to, members=to_extract)


def safe_create_file(path: Path, mode: int = 0o600, *, exist_ok: bool = False) -> None:
    """Create file with secure permissions.

    Args:
        path: Path to file to create
        mode: Permission mode (default: 0o600 for secure files)
        exist_ok: If True, don't raise error if file exists

    Security Note: Default changed from 0o644 to 0o600 to prevent world-readable files.
    """
    if path.exists() and not exist_ok:
        raise FileExistsError(f"File already exists: {path}")

    # Create parent directories if needed
    path.parent.mkdir(parents=True, exist_ok=True)

    # Create with secure permissions
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    os.close(fd)
