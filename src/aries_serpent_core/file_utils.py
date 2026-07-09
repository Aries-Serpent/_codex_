"""
Safe file reading utilities with proper error handling and logging.

Based on REPO_ADMIN_IMPLEMENTATION_DECISIONS.md Section 4.2.2:
- Use errors="replace" instead of errors="ignore"
- Log warnings when encoding errors are encountered
- Provide visibility into file reading issues
"""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def read_text_safe(
    path: Path,
    encoding: str = "utf-8",
    max_bytes: Optional[int] = None,
    errors: str = "replace",
) -> str:
    """Read text file with proper error handling and logging.

    Args:
        path: File path to read
        encoding: Text encoding (default: utf-8)
        max_bytes: Optional limit on bytes to read
        errors: Error handling strategy (default: replace)
            - "replace": Replace invalid bytes with � (U+FFFD)
            - "strict": Raise UnicodeDecodeError
            - "ignore": Silently skip (not recommended)
            - "surrogateescape": Preserve invalid bytes

    Returns:
        File content as string

    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If file isn't readable
        UnicodeDecodeError: If errors="strict" and invalid encoding

    Logs:
        WARNING: If decode errors encountered with errors="replace"
        ERROR: If file read fails for other reasons

    Examples:
        >>> content = read_text_safe(Path("myfile.py"))
        >>> content = read_text_safe(Path("data.txt"), max_bytes=1000)
        >>> content = read_text_safe(Path("config.yaml"), errors="strict")
    """
    try:
        # Read file content
        if max_bytes is not None:
            # Read limited bytes
            raw_bytes = path.read_bytes()[:max_bytes]
            content = raw_bytes.decode(encoding=encoding, errors=errors)
        else:
            # Read full file
            content = path.read_text(encoding=encoding, errors=errors)

        # Check if replacement character was used
        if errors == "replace" and "�" in content:
            replacement_count = content.count("�")
            logger.warning(
                f"Encoding errors in {path}: "
                f"{replacement_count} invalid {encoding} byte(s) replaced with U+FFFD. "
                f"Original file may contain binary data or use different encoding."
            )

        return content

    except UnicodeDecodeError as e:
        type(e).__name__
        logger.debug("UnicodeDecodeError: <ERROR_TYPE>")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise

    except FileNotFoundError as e:
        type(e).__name__
        logger.debug("FileNotFoundError: <ERROR_TYPE>")
        logger.warning("FileNotFoundError: <ERROR_TYPE>", exc_info=True)
        logger.error(f"File not found: {path}")
        raise

    except PermissionError as e:
        type(e).__name__
        logger.debug("PermissionError: <ERROR_TYPE>")
        logger.warning("PermissionError: <ERROR_TYPE>", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise

    except (IOError, OSError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: <ERROR_TYPE>")
        raise


def read_text_safe_fallback(
    path: Path,
    encodings: list[str] | None = None,
    max_bytes: Optional[int] = None,
) -> tuple[str, str]:
    """Try multiple encodings in order until one succeeds.

    Args:
        path: File path to read
        encodings: List of encodings to try (default: utf-8, latin-1, cp1252)
        max_bytes: Optional limit on bytes to read

    Returns:
        Tuple of (content, successful_encoding)

    Raises:
        UnicodeDecodeError: If all encodings fail

    Examples:
        >>> content, enc = read_text_safe_fallback(Path("unknown.txt"))
        >>> logger.info(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]

    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict",  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding

        except UnicodeDecodeError as e:
            type(e).__name__
            logger.debug("UnicodeDecodeError: <ERROR_TYPE>")
            logger.warning("UnicodeDecodeError: <ERROR_TYPE>", exc_info=True)
            continue

    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


# Migration helpers for existing code
def migrate_from_ignore(path: Path, **kwargs) -> str:
    """Drop-in replacement for path.read_text(errors="ignore").

    This function logs a deprecation warning and uses read_text_safe.

    Example migration:
        # OLD:
        txt = path.read_text(encoding="utf-8", errors="ignore")

        # NEW:
        from codex.file_utils import read_text_safe
        txt = read_text_safe(path)
    """
    logger.warning(
        f"Using deprecated errors='ignore' pattern for {path}. "
        f"Migrating to read_text_safe with errors='replace'. "
        f"Update code to use read_text_safe directly."
    )
    return read_text_safe(path, **kwargs)
