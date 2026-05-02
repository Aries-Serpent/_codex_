"""
Cross-platform path utilities for _codex_.

Ensures filename compatibility across Windows, Linux, and macOS.
"""

from datetime import datetime, timezone
from typing import Optional


def windows_safe_timestamp(
    dt: Optional[datetime] = None, fmt: str = "iso", include_seconds: bool = True
) -> str:
    """
    Generate Windows-safe timestamp string for use in filenames.

    Replaces colons with hyphens to ensure cross-platform compatibility.

    Args:
        dt: datetime object (defaults to current UTC time)
        fmt: Format style - "iso", "compact", or "readable"
        include_seconds: Include seconds in output (default: True)

    Returns:
        Timestamp string safe for use in filenames on all platforms

    Examples:
        >>> windows_safe_timestamp(fmt="iso")
        '2026-01-21T14-30-45Z'

        >>> windows_safe_timestamp(fmt="compact")
        '20260121_143045'

        >>> windows_safe_timestamp(fmt="readable")
        '2026-01-21-14-30-45-UTC'
    """
    if dt is None:
        dt = datetime.now(timezone.utc)

    if fmt == "iso":
        # ISO-8601-ish but with hyphens: YYYY-MM-DDTHH-MM-SSZ
        base = dt.strftime("%Y-%m-%dT%H-%M")
        suffix = f"-{dt.strftime('%S')}Z" if include_seconds else "Z"
        return base + suffix

    if fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")

    if fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix

    raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for cross-platform compatibility.

    Replaces Windows-illegal characters: < > : " / \\ | ? *

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for Windows, Linux, macOS
    """
    import re

    # Replace illegal characters with underscores
    illegal_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(illegal_chars, "_", filename)

    # Replace multiple underscores with single
    return re.sub(r"_+", "_", sanitized)
