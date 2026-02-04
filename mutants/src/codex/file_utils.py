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
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


def x_read_text_safe__mutmut_orig(
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_1(
    path: Path,
    encoding: str = "XXutf-8XX",
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_2(
    path: Path,
    encoding: str = "UTF-8",
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_3(
    path: Path,
    encoding: str = "utf-8",
    max_bytes: Optional[int] = None,
    errors: str = "XXreplaceXX",
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_4(
    path: Path,
    encoding: str = "utf-8",
    max_bytes: Optional[int] = None,
    errors: str = "REPLACE",
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_5(
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
        if max_bytes is None:
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_6(
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
            raw_bytes = None
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_7(
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
            content = None
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_8(
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
            content = raw_bytes.decode(encoding=None, errors=errors)
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_9(
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
            content = raw_bytes.decode(encoding=encoding, errors=None)
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_10(
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
            content = raw_bytes.decode(errors=errors)
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_11(
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
            content = raw_bytes.decode(encoding=encoding, )
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_12(
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
            content = None
        
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_13(
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
            content = path.read_text(encoding=None, errors=errors)
        
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_14(
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
            content = path.read_text(encoding=encoding, errors=None)
        
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_15(
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
            content = path.read_text(errors=errors)
        
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_16(
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
            content = path.read_text(encoding=encoding, )
        
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_17(
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
        if errors == "replace" or "�" in content:
            replacement_count = content.count("�")
            logger.warning(
                f"Encoding errors in {path}: "
                f"{replacement_count} invalid {encoding} byte(s) replaced with U+FFFD. "
                f"Original file may contain binary data or use different encoding."
            )
        
        return content
        
    except UnicodeDecodeError as e:
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_18(
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
        if errors != "replace" and "�" in content:
            replacement_count = content.count("�")
            logger.warning(
                f"Encoding errors in {path}: "
                f"{replacement_count} invalid {encoding} byte(s) replaced with U+FFFD. "
                f"Original file may contain binary data or use different encoding."
            )
        
        return content
        
    except UnicodeDecodeError as e:
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_19(
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
        if errors == "XXreplaceXX" and "�" in content:
            replacement_count = content.count("�")
            logger.warning(
                f"Encoding errors in {path}: "
                f"{replacement_count} invalid {encoding} byte(s) replaced with U+FFFD. "
                f"Original file may contain binary data or use different encoding."
            )
        
        return content
        
    except UnicodeDecodeError as e:
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_20(
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
        if errors == "REPLACE" and "�" in content:
            replacement_count = content.count("�")
            logger.warning(
                f"Encoding errors in {path}: "
                f"{replacement_count} invalid {encoding} byte(s) replaced with U+FFFD. "
                f"Original file may contain binary data or use different encoding."
            )
        
        return content
        
    except UnicodeDecodeError as e:
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_21(
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
        if errors == "replace" and "XX�XX" in content:
            replacement_count = content.count("�")
            logger.warning(
                f"Encoding errors in {path}: "
                f"{replacement_count} invalid {encoding} byte(s) replaced with U+FFFD. "
                f"Original file may contain binary data or use different encoding."
            )
        
        return content
        
    except UnicodeDecodeError as e:
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_22(
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
        if errors == "replace" and "�" not in content:
            replacement_count = content.count("�")
            logger.warning(
                f"Encoding errors in {path}: "
                f"{replacement_count} invalid {encoding} byte(s) replaced with U+FFFD. "
                f"Original file may contain binary data or use different encoding."
            )
        
        return content
        
    except UnicodeDecodeError as e:
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_23(
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
            replacement_count = None
            logger.warning(
                f"Encoding errors in {path}: "
                f"{replacement_count} invalid {encoding} byte(s) replaced with U+FFFD. "
                f"Original file may contain binary data or use different encoding."
            )
        
        return content
        
    except UnicodeDecodeError as e:
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_24(
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
            replacement_count = content.count(None)
            logger.warning(
                f"Encoding errors in {path}: "
                f"{replacement_count} invalid {encoding} byte(s) replaced with U+FFFD. "
                f"Original file may contain binary data or use different encoding."
            )
        
        return content
        
    except UnicodeDecodeError as e:
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_25(
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
            replacement_count = content.count("XX�XX")
            logger.warning(
                f"Encoding errors in {path}: "
                f"{replacement_count} invalid {encoding} byte(s) replaced with U+FFFD. "
                f"Original file may contain binary data or use different encoding."
            )
        
        return content
        
    except UnicodeDecodeError as e:
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_26(
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
                None
            )
        
        return content
        
    except UnicodeDecodeError as e:
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_27(
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
        logger.debug(None)
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_28(
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            None
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_29(
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(None)
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_30(
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(None, exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_31(
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=None)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_32(
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_33(
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", )
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_34(
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=False)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_35(
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(None)
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_36(
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(None)
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_37(
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(None, exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_38(
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=None)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_39(
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_40(
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", )
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_41(
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=False)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_42(
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(None)
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_43(
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(None)
        logger.error(f"Unexpected error reading {path}: {type(e).__name__}: {e}")
        raise


def x_read_text_safe__mutmut_44(
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(None)
        raise


def x_read_text_safe__mutmut_45(
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
        logger.debug(f"UnicodeDecodeError: {e}")
        logger.error(
            f"Failed to decode {path} with encoding {encoding}: {e}. "
            f"Try different encoding or use errors='replace'"
        )
        raise
    
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"File not found: {path}")
        raise
    
    except PermissionError as e:
        logger.debug(f"PermissionError: {e}")
        logger.warning(f"PermissionError: {e}", exc_info=True)
        logger.error(f"Permission denied reading {path}")
        raise
    
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Unexpected error reading {path}: {type(None).__name__}: {e}")
        raise

x_read_text_safe__mutmut_mutants : ClassVar[MutantDict] = {
'x_read_text_safe__mutmut_1': x_read_text_safe__mutmut_1, 
    'x_read_text_safe__mutmut_2': x_read_text_safe__mutmut_2, 
    'x_read_text_safe__mutmut_3': x_read_text_safe__mutmut_3, 
    'x_read_text_safe__mutmut_4': x_read_text_safe__mutmut_4, 
    'x_read_text_safe__mutmut_5': x_read_text_safe__mutmut_5, 
    'x_read_text_safe__mutmut_6': x_read_text_safe__mutmut_6, 
    'x_read_text_safe__mutmut_7': x_read_text_safe__mutmut_7, 
    'x_read_text_safe__mutmut_8': x_read_text_safe__mutmut_8, 
    'x_read_text_safe__mutmut_9': x_read_text_safe__mutmut_9, 
    'x_read_text_safe__mutmut_10': x_read_text_safe__mutmut_10, 
    'x_read_text_safe__mutmut_11': x_read_text_safe__mutmut_11, 
    'x_read_text_safe__mutmut_12': x_read_text_safe__mutmut_12, 
    'x_read_text_safe__mutmut_13': x_read_text_safe__mutmut_13, 
    'x_read_text_safe__mutmut_14': x_read_text_safe__mutmut_14, 
    'x_read_text_safe__mutmut_15': x_read_text_safe__mutmut_15, 
    'x_read_text_safe__mutmut_16': x_read_text_safe__mutmut_16, 
    'x_read_text_safe__mutmut_17': x_read_text_safe__mutmut_17, 
    'x_read_text_safe__mutmut_18': x_read_text_safe__mutmut_18, 
    'x_read_text_safe__mutmut_19': x_read_text_safe__mutmut_19, 
    'x_read_text_safe__mutmut_20': x_read_text_safe__mutmut_20, 
    'x_read_text_safe__mutmut_21': x_read_text_safe__mutmut_21, 
    'x_read_text_safe__mutmut_22': x_read_text_safe__mutmut_22, 
    'x_read_text_safe__mutmut_23': x_read_text_safe__mutmut_23, 
    'x_read_text_safe__mutmut_24': x_read_text_safe__mutmut_24, 
    'x_read_text_safe__mutmut_25': x_read_text_safe__mutmut_25, 
    'x_read_text_safe__mutmut_26': x_read_text_safe__mutmut_26, 
    'x_read_text_safe__mutmut_27': x_read_text_safe__mutmut_27, 
    'x_read_text_safe__mutmut_28': x_read_text_safe__mutmut_28, 
    'x_read_text_safe__mutmut_29': x_read_text_safe__mutmut_29, 
    'x_read_text_safe__mutmut_30': x_read_text_safe__mutmut_30, 
    'x_read_text_safe__mutmut_31': x_read_text_safe__mutmut_31, 
    'x_read_text_safe__mutmut_32': x_read_text_safe__mutmut_32, 
    'x_read_text_safe__mutmut_33': x_read_text_safe__mutmut_33, 
    'x_read_text_safe__mutmut_34': x_read_text_safe__mutmut_34, 
    'x_read_text_safe__mutmut_35': x_read_text_safe__mutmut_35, 
    'x_read_text_safe__mutmut_36': x_read_text_safe__mutmut_36, 
    'x_read_text_safe__mutmut_37': x_read_text_safe__mutmut_37, 
    'x_read_text_safe__mutmut_38': x_read_text_safe__mutmut_38, 
    'x_read_text_safe__mutmut_39': x_read_text_safe__mutmut_39, 
    'x_read_text_safe__mutmut_40': x_read_text_safe__mutmut_40, 
    'x_read_text_safe__mutmut_41': x_read_text_safe__mutmut_41, 
    'x_read_text_safe__mutmut_42': x_read_text_safe__mutmut_42, 
    'x_read_text_safe__mutmut_43': x_read_text_safe__mutmut_43, 
    'x_read_text_safe__mutmut_44': x_read_text_safe__mutmut_44, 
    'x_read_text_safe__mutmut_45': x_read_text_safe__mutmut_45
}

def read_text_safe(*args, **kwargs):
    result = _mutmut_trampoline(x_read_text_safe__mutmut_orig, x_read_text_safe__mutmut_mutants, args, kwargs)
    return result 

read_text_safe.__signature__ = _mutmut_signature(x_read_text_safe__mutmut_orig)
x_read_text_safe__mutmut_orig.__name__ = 'x_read_text_safe'


def x_read_text_safe_fallback__mutmut_orig(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_1(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is not None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_2(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = None
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_3(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["XXutf-8XX", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_4(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["UTF-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_5(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "XXlatin-1XX", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_6(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "LATIN-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_7(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "XXcp1252XX", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_8(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "CP1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_9(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "XXutf-16XX"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_10(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "UTF-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_11(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = None
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_12(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                None,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_13(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=None,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_14(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=None,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_15(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors=None  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_16(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_17(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_18(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_19(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_20(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="XXstrictXX"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_21(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="STRICT"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_22(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(None)
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_23(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(None)
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_24(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(None, exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_25(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=None)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_26(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_27(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", )
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_28(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=False)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_29(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            break
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_30(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        None
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_31(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = None
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_32(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(None, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_33(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding=None, max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_34(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=None, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_35(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors=None)
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_36(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_37(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_38(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_39(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, )
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_40(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="XXutf-8XX", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_41(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="UTF-8", max_bytes=max_bytes, errors="replace")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_42(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="XXreplaceXX")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_43(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="REPLACE")
    return content, "utf-8 (with replacements)"


def x_read_text_safe_fallback__mutmut_44(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "XXutf-8 (with replacements)XX"


def x_read_text_safe_fallback__mutmut_45(
    path: Path,
    encodings: list[str] = None,
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
        >>> print(f"Decoded with {enc}")
    """
    if encodings is None:
        encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    
    for encoding in encodings:
        try:
            content = read_text_safe(
                path,
                encoding=encoding,
                max_bytes=max_bytes,
                errors="strict"  # Try strict first
            )
            logger.info(f"Successfully decoded {path} with encoding {encoding}")
            return content, encoding
        
        except UnicodeDecodeError as e:
            logger.debug(f"UnicodeDecodeError: {e}")
            logger.warning(f"UnicodeDecodeError: {e}", exc_info=True)
            continue
    
    # All strict encodings failed, try utf-8 with replace
    logger.warning(
        f"All strict encodings failed for {path}. "
        f"Falling back to utf-8 with errors='replace'"
    )
    content = read_text_safe(path, encoding="utf-8", max_bytes=max_bytes, errors="replace")
    return content, "UTF-8 (WITH REPLACEMENTS)"

x_read_text_safe_fallback__mutmut_mutants : ClassVar[MutantDict] = {
'x_read_text_safe_fallback__mutmut_1': x_read_text_safe_fallback__mutmut_1, 
    'x_read_text_safe_fallback__mutmut_2': x_read_text_safe_fallback__mutmut_2, 
    'x_read_text_safe_fallback__mutmut_3': x_read_text_safe_fallback__mutmut_3, 
    'x_read_text_safe_fallback__mutmut_4': x_read_text_safe_fallback__mutmut_4, 
    'x_read_text_safe_fallback__mutmut_5': x_read_text_safe_fallback__mutmut_5, 
    'x_read_text_safe_fallback__mutmut_6': x_read_text_safe_fallback__mutmut_6, 
    'x_read_text_safe_fallback__mutmut_7': x_read_text_safe_fallback__mutmut_7, 
    'x_read_text_safe_fallback__mutmut_8': x_read_text_safe_fallback__mutmut_8, 
    'x_read_text_safe_fallback__mutmut_9': x_read_text_safe_fallback__mutmut_9, 
    'x_read_text_safe_fallback__mutmut_10': x_read_text_safe_fallback__mutmut_10, 
    'x_read_text_safe_fallback__mutmut_11': x_read_text_safe_fallback__mutmut_11, 
    'x_read_text_safe_fallback__mutmut_12': x_read_text_safe_fallback__mutmut_12, 
    'x_read_text_safe_fallback__mutmut_13': x_read_text_safe_fallback__mutmut_13, 
    'x_read_text_safe_fallback__mutmut_14': x_read_text_safe_fallback__mutmut_14, 
    'x_read_text_safe_fallback__mutmut_15': x_read_text_safe_fallback__mutmut_15, 
    'x_read_text_safe_fallback__mutmut_16': x_read_text_safe_fallback__mutmut_16, 
    'x_read_text_safe_fallback__mutmut_17': x_read_text_safe_fallback__mutmut_17, 
    'x_read_text_safe_fallback__mutmut_18': x_read_text_safe_fallback__mutmut_18, 
    'x_read_text_safe_fallback__mutmut_19': x_read_text_safe_fallback__mutmut_19, 
    'x_read_text_safe_fallback__mutmut_20': x_read_text_safe_fallback__mutmut_20, 
    'x_read_text_safe_fallback__mutmut_21': x_read_text_safe_fallback__mutmut_21, 
    'x_read_text_safe_fallback__mutmut_22': x_read_text_safe_fallback__mutmut_22, 
    'x_read_text_safe_fallback__mutmut_23': x_read_text_safe_fallback__mutmut_23, 
    'x_read_text_safe_fallback__mutmut_24': x_read_text_safe_fallback__mutmut_24, 
    'x_read_text_safe_fallback__mutmut_25': x_read_text_safe_fallback__mutmut_25, 
    'x_read_text_safe_fallback__mutmut_26': x_read_text_safe_fallback__mutmut_26, 
    'x_read_text_safe_fallback__mutmut_27': x_read_text_safe_fallback__mutmut_27, 
    'x_read_text_safe_fallback__mutmut_28': x_read_text_safe_fallback__mutmut_28, 
    'x_read_text_safe_fallback__mutmut_29': x_read_text_safe_fallback__mutmut_29, 
    'x_read_text_safe_fallback__mutmut_30': x_read_text_safe_fallback__mutmut_30, 
    'x_read_text_safe_fallback__mutmut_31': x_read_text_safe_fallback__mutmut_31, 
    'x_read_text_safe_fallback__mutmut_32': x_read_text_safe_fallback__mutmut_32, 
    'x_read_text_safe_fallback__mutmut_33': x_read_text_safe_fallback__mutmut_33, 
    'x_read_text_safe_fallback__mutmut_34': x_read_text_safe_fallback__mutmut_34, 
    'x_read_text_safe_fallback__mutmut_35': x_read_text_safe_fallback__mutmut_35, 
    'x_read_text_safe_fallback__mutmut_36': x_read_text_safe_fallback__mutmut_36, 
    'x_read_text_safe_fallback__mutmut_37': x_read_text_safe_fallback__mutmut_37, 
    'x_read_text_safe_fallback__mutmut_38': x_read_text_safe_fallback__mutmut_38, 
    'x_read_text_safe_fallback__mutmut_39': x_read_text_safe_fallback__mutmut_39, 
    'x_read_text_safe_fallback__mutmut_40': x_read_text_safe_fallback__mutmut_40, 
    'x_read_text_safe_fallback__mutmut_41': x_read_text_safe_fallback__mutmut_41, 
    'x_read_text_safe_fallback__mutmut_42': x_read_text_safe_fallback__mutmut_42, 
    'x_read_text_safe_fallback__mutmut_43': x_read_text_safe_fallback__mutmut_43, 
    'x_read_text_safe_fallback__mutmut_44': x_read_text_safe_fallback__mutmut_44, 
    'x_read_text_safe_fallback__mutmut_45': x_read_text_safe_fallback__mutmut_45
}

def read_text_safe_fallback(*args, **kwargs):
    result = _mutmut_trampoline(x_read_text_safe_fallback__mutmut_orig, x_read_text_safe_fallback__mutmut_mutants, args, kwargs)
    return result 

read_text_safe_fallback.__signature__ = _mutmut_signature(x_read_text_safe_fallback__mutmut_orig)
x_read_text_safe_fallback__mutmut_orig.__name__ = 'x_read_text_safe_fallback'


# Migration helpers for existing code
def x_migrate_from_ignore__mutmut_orig(path: Path, **kwargs) -> str:
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


# Migration helpers for existing code
def x_migrate_from_ignore__mutmut_1(path: Path, **kwargs) -> str:
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
        None
    )
    return read_text_safe(path, **kwargs)


# Migration helpers for existing code
def x_migrate_from_ignore__mutmut_2(path: Path, **kwargs) -> str:
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
    return read_text_safe(None, **kwargs)


# Migration helpers for existing code
def x_migrate_from_ignore__mutmut_3(path: Path, **kwargs) -> str:
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
    return read_text_safe(**kwargs)


# Migration helpers for existing code
def x_migrate_from_ignore__mutmut_4(path: Path, **kwargs) -> str:
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
    return read_text_safe(path, )

x_migrate_from_ignore__mutmut_mutants : ClassVar[MutantDict] = {
'x_migrate_from_ignore__mutmut_1': x_migrate_from_ignore__mutmut_1, 
    'x_migrate_from_ignore__mutmut_2': x_migrate_from_ignore__mutmut_2, 
    'x_migrate_from_ignore__mutmut_3': x_migrate_from_ignore__mutmut_3, 
    'x_migrate_from_ignore__mutmut_4': x_migrate_from_ignore__mutmut_4
}

def migrate_from_ignore(*args, **kwargs):
    result = _mutmut_trampoline(x_migrate_from_ignore__mutmut_orig, x_migrate_from_ignore__mutmut_mutants, args, kwargs)
    return result 

migrate_from_ignore.__signature__ = _mutmut_signature(x_migrate_from_ignore__mutmut_orig)
x_migrate_from_ignore__mutmut_orig.__name__ = 'x_migrate_from_ignore'
