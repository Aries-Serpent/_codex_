"""
Cross-platform path utilities for _codex_.

Ensures filename compatibility across Windows, Linux, and macOS.
"""
from datetime import datetime, timezone
from typing import Optional
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


def x_windows_safe_timestamp__mutmut_orig(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_1(
    dt: Optional[datetime] = None,
    fmt: str = "XXisoXX",
    include_seconds: bool = True
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
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_2(
    dt: Optional[datetime] = None,
    fmt: str = "ISO",
    include_seconds: bool = True
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
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_3(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = False
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
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_4(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    if dt is not None:
        dt = datetime.now(timezone.utc)
    
    if fmt == "iso":
        # ISO-8601-ish but with hyphens: YYYY-MM-DDTHH-MM-SSZ
        base = dt.strftime("%Y-%m-%dT%H-%M")
        suffix = f"-{dt.strftime('%S')}Z" if include_seconds else "Z"
        return base + suffix
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_5(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
        dt = None
    
    if fmt == "iso":
        # ISO-8601-ish but with hyphens: YYYY-MM-DDTHH-MM-SSZ
        base = dt.strftime("%Y-%m-%dT%H-%M")
        suffix = f"-{dt.strftime('%S')}Z" if include_seconds else "Z"
        return base + suffix
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_6(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
        dt = datetime.now(None)
    
    if fmt == "iso":
        # ISO-8601-ish but with hyphens: YYYY-MM-DDTHH-MM-SSZ
        base = dt.strftime("%Y-%m-%dT%H-%M")
        suffix = f"-{dt.strftime('%S')}Z" if include_seconds else "Z"
        return base + suffix
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_7(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    if fmt != "iso":
        # ISO-8601-ish but with hyphens: YYYY-MM-DDTHH-MM-SSZ
        base = dt.strftime("%Y-%m-%dT%H-%M")
        suffix = f"-{dt.strftime('%S')}Z" if include_seconds else "Z"
        return base + suffix
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_8(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    if fmt == "XXisoXX":
        # ISO-8601-ish but with hyphens: YYYY-MM-DDTHH-MM-SSZ
        base = dt.strftime("%Y-%m-%dT%H-%M")
        suffix = f"-{dt.strftime('%S')}Z" if include_seconds else "Z"
        return base + suffix
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_9(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    if fmt == "ISO":
        # ISO-8601-ish but with hyphens: YYYY-MM-DDTHH-MM-SSZ
        base = dt.strftime("%Y-%m-%dT%H-%M")
        suffix = f"-{dt.strftime('%S')}Z" if include_seconds else "Z"
        return base + suffix
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_10(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
        base = None
        suffix = f"-{dt.strftime('%S')}Z" if include_seconds else "Z"
        return base + suffix
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_11(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
        base = dt.strftime(None)
        suffix = f"-{dt.strftime('%S')}Z" if include_seconds else "Z"
        return base + suffix
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_12(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
        base = dt.strftime("XX%Y-%m-%dT%H-%MXX")
        suffix = f"-{dt.strftime('%S')}Z" if include_seconds else "Z"
        return base + suffix
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_13(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
        base = dt.strftime("%y-%m-%dt%h-%m")
        suffix = f"-{dt.strftime('%S')}Z" if include_seconds else "Z"
        return base + suffix
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_14(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
        base = dt.strftime("%Y-%M-%DT%H-%M")
        suffix = f"-{dt.strftime('%S')}Z" if include_seconds else "Z"
        return base + suffix
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_15(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
        suffix = None
        return base + suffix
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_16(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
        suffix = f"-{dt.strftime(None)}Z" if include_seconds else "Z"
        return base + suffix
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_17(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
        suffix = f"-{dt.strftime('XX%SXX')}Z" if include_seconds else "Z"
        return base + suffix
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_18(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
        suffix = f"-{dt.strftime('%s')}Z" if include_seconds else "Z"
        return base + suffix
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_19(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
        suffix = f"-{dt.strftime('%S')}Z" if include_seconds else "XXZXX"
        return base + suffix
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_20(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
        suffix = f"-{dt.strftime('%S')}Z" if include_seconds else "z"
        return base + suffix
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_21(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
        return base - suffix
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_22(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    elif fmt != "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_23(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    elif fmt == "XXcompactXX":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_24(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    elif fmt == "COMPACT":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_25(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime(None)
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_26(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("XX%Y%m%d_%H%M%SXX")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_27(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%y%m%d_%h%m%s")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_28(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%M%D_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_29(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime(None)
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_30(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("XX%Y%m%d_%H%MXX")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_31(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%y%m%d_%h%m")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_32(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%M%D_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_33(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt != "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_34(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "XXreadableXX":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_35(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "READABLE":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_36(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = None
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_37(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime(None)
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_38(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("XX%Y-%m-%d-%H-%MXX")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_39(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%y-%m-%d-%h-%m")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_40(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%M-%D-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_41(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = None
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_42(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime(None)}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_43(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('XX%SXX')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_44(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%s')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_45(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "XX-UTCXX"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_46(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-utc"
        return base + suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_47(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base - suffix
    
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'iso', 'compact', or 'readable'")


def x_windows_safe_timestamp__mutmut_48(
    dt: Optional[datetime] = None,
    fmt: str = "iso",
    include_seconds: bool = True
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
    
    elif fmt == "compact":
        # Compact format: YYYYMMDD_HHMMSS
        if include_seconds:
            return dt.strftime("%Y%m%d_%H%M%S")
        return dt.strftime("%Y%m%d_%H%M")
    
    elif fmt == "readable":
        # Human-readable: YYYY-MM-DD-HH-MM-SS-UTC
        base = dt.strftime("%Y-%m-%d-%H-%M")
        suffix = f"-{dt.strftime('%S')}-UTC" if include_seconds else "-UTC"
        return base + suffix
    
    else:
        raise ValueError(None)

x_windows_safe_timestamp__mutmut_mutants : ClassVar[MutantDict] = {
'x_windows_safe_timestamp__mutmut_1': x_windows_safe_timestamp__mutmut_1, 
    'x_windows_safe_timestamp__mutmut_2': x_windows_safe_timestamp__mutmut_2, 
    'x_windows_safe_timestamp__mutmut_3': x_windows_safe_timestamp__mutmut_3, 
    'x_windows_safe_timestamp__mutmut_4': x_windows_safe_timestamp__mutmut_4, 
    'x_windows_safe_timestamp__mutmut_5': x_windows_safe_timestamp__mutmut_5, 
    'x_windows_safe_timestamp__mutmut_6': x_windows_safe_timestamp__mutmut_6, 
    'x_windows_safe_timestamp__mutmut_7': x_windows_safe_timestamp__mutmut_7, 
    'x_windows_safe_timestamp__mutmut_8': x_windows_safe_timestamp__mutmut_8, 
    'x_windows_safe_timestamp__mutmut_9': x_windows_safe_timestamp__mutmut_9, 
    'x_windows_safe_timestamp__mutmut_10': x_windows_safe_timestamp__mutmut_10, 
    'x_windows_safe_timestamp__mutmut_11': x_windows_safe_timestamp__mutmut_11, 
    'x_windows_safe_timestamp__mutmut_12': x_windows_safe_timestamp__mutmut_12, 
    'x_windows_safe_timestamp__mutmut_13': x_windows_safe_timestamp__mutmut_13, 
    'x_windows_safe_timestamp__mutmut_14': x_windows_safe_timestamp__mutmut_14, 
    'x_windows_safe_timestamp__mutmut_15': x_windows_safe_timestamp__mutmut_15, 
    'x_windows_safe_timestamp__mutmut_16': x_windows_safe_timestamp__mutmut_16, 
    'x_windows_safe_timestamp__mutmut_17': x_windows_safe_timestamp__mutmut_17, 
    'x_windows_safe_timestamp__mutmut_18': x_windows_safe_timestamp__mutmut_18, 
    'x_windows_safe_timestamp__mutmut_19': x_windows_safe_timestamp__mutmut_19, 
    'x_windows_safe_timestamp__mutmut_20': x_windows_safe_timestamp__mutmut_20, 
    'x_windows_safe_timestamp__mutmut_21': x_windows_safe_timestamp__mutmut_21, 
    'x_windows_safe_timestamp__mutmut_22': x_windows_safe_timestamp__mutmut_22, 
    'x_windows_safe_timestamp__mutmut_23': x_windows_safe_timestamp__mutmut_23, 
    'x_windows_safe_timestamp__mutmut_24': x_windows_safe_timestamp__mutmut_24, 
    'x_windows_safe_timestamp__mutmut_25': x_windows_safe_timestamp__mutmut_25, 
    'x_windows_safe_timestamp__mutmut_26': x_windows_safe_timestamp__mutmut_26, 
    'x_windows_safe_timestamp__mutmut_27': x_windows_safe_timestamp__mutmut_27, 
    'x_windows_safe_timestamp__mutmut_28': x_windows_safe_timestamp__mutmut_28, 
    'x_windows_safe_timestamp__mutmut_29': x_windows_safe_timestamp__mutmut_29, 
    'x_windows_safe_timestamp__mutmut_30': x_windows_safe_timestamp__mutmut_30, 
    'x_windows_safe_timestamp__mutmut_31': x_windows_safe_timestamp__mutmut_31, 
    'x_windows_safe_timestamp__mutmut_32': x_windows_safe_timestamp__mutmut_32, 
    'x_windows_safe_timestamp__mutmut_33': x_windows_safe_timestamp__mutmut_33, 
    'x_windows_safe_timestamp__mutmut_34': x_windows_safe_timestamp__mutmut_34, 
    'x_windows_safe_timestamp__mutmut_35': x_windows_safe_timestamp__mutmut_35, 
    'x_windows_safe_timestamp__mutmut_36': x_windows_safe_timestamp__mutmut_36, 
    'x_windows_safe_timestamp__mutmut_37': x_windows_safe_timestamp__mutmut_37, 
    'x_windows_safe_timestamp__mutmut_38': x_windows_safe_timestamp__mutmut_38, 
    'x_windows_safe_timestamp__mutmut_39': x_windows_safe_timestamp__mutmut_39, 
    'x_windows_safe_timestamp__mutmut_40': x_windows_safe_timestamp__mutmut_40, 
    'x_windows_safe_timestamp__mutmut_41': x_windows_safe_timestamp__mutmut_41, 
    'x_windows_safe_timestamp__mutmut_42': x_windows_safe_timestamp__mutmut_42, 
    'x_windows_safe_timestamp__mutmut_43': x_windows_safe_timestamp__mutmut_43, 
    'x_windows_safe_timestamp__mutmut_44': x_windows_safe_timestamp__mutmut_44, 
    'x_windows_safe_timestamp__mutmut_45': x_windows_safe_timestamp__mutmut_45, 
    'x_windows_safe_timestamp__mutmut_46': x_windows_safe_timestamp__mutmut_46, 
    'x_windows_safe_timestamp__mutmut_47': x_windows_safe_timestamp__mutmut_47, 
    'x_windows_safe_timestamp__mutmut_48': x_windows_safe_timestamp__mutmut_48
}

def windows_safe_timestamp(*args, **kwargs):
    result = _mutmut_trampoline(x_windows_safe_timestamp__mutmut_orig, x_windows_safe_timestamp__mutmut_mutants, args, kwargs)
    return result 

windows_safe_timestamp.__signature__ = _mutmut_signature(x_windows_safe_timestamp__mutmut_orig)
x_windows_safe_timestamp__mutmut_orig.__name__ = 'x_windows_safe_timestamp'


def x_sanitize_filename__mutmut_orig(filename: str) -> str:
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
    sanitized = re.sub(illegal_chars, '_', filename)
    
    # Replace multiple underscores with single
    sanitized = re.sub(r'_+', '_', sanitized)
    
    return sanitized


def x_sanitize_filename__mutmut_1(filename: str) -> str:
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
    illegal_chars = None
    sanitized = re.sub(illegal_chars, '_', filename)
    
    # Replace multiple underscores with single
    sanitized = re.sub(r'_+', '_', sanitized)
    
    return sanitized


def x_sanitize_filename__mutmut_2(filename: str) -> str:
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
    illegal_chars = r'XX[<>:"/\\|?*]XX'
    sanitized = re.sub(illegal_chars, '_', filename)
    
    # Replace multiple underscores with single
    sanitized = re.sub(r'_+', '_', sanitized)
    
    return sanitized


def x_sanitize_filename__mutmut_3(filename: str) -> str:
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
    sanitized = None
    
    # Replace multiple underscores with single
    sanitized = re.sub(r'_+', '_', sanitized)
    
    return sanitized


def x_sanitize_filename__mutmut_4(filename: str) -> str:
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
    sanitized = re.sub(None, '_', filename)
    
    # Replace multiple underscores with single
    sanitized = re.sub(r'_+', '_', sanitized)
    
    return sanitized


def x_sanitize_filename__mutmut_5(filename: str) -> str:
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
    sanitized = re.sub(illegal_chars, None, filename)
    
    # Replace multiple underscores with single
    sanitized = re.sub(r'_+', '_', sanitized)
    
    return sanitized


def x_sanitize_filename__mutmut_6(filename: str) -> str:
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
    sanitized = re.sub(illegal_chars, '_', None)
    
    # Replace multiple underscores with single
    sanitized = re.sub(r'_+', '_', sanitized)
    
    return sanitized


def x_sanitize_filename__mutmut_7(filename: str) -> str:
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
    sanitized = re.sub('_', filename)
    
    # Replace multiple underscores with single
    sanitized = re.sub(r'_+', '_', sanitized)
    
    return sanitized


def x_sanitize_filename__mutmut_8(filename: str) -> str:
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
    sanitized = re.sub(illegal_chars, filename)
    
    # Replace multiple underscores with single
    sanitized = re.sub(r'_+', '_', sanitized)
    
    return sanitized


def x_sanitize_filename__mutmut_9(filename: str) -> str:
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
    sanitized = re.sub(illegal_chars, '_', )
    
    # Replace multiple underscores with single
    sanitized = re.sub(r'_+', '_', sanitized)
    
    return sanitized


def x_sanitize_filename__mutmut_10(filename: str) -> str:
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
    sanitized = re.sub(illegal_chars, 'XX_XX', filename)
    
    # Replace multiple underscores with single
    sanitized = re.sub(r'_+', '_', sanitized)
    
    return sanitized


def x_sanitize_filename__mutmut_11(filename: str) -> str:
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
    sanitized = re.sub(illegal_chars, '_', filename)
    
    # Replace multiple underscores with single
    sanitized = None
    
    return sanitized


def x_sanitize_filename__mutmut_12(filename: str) -> str:
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
    sanitized = re.sub(illegal_chars, '_', filename)
    
    # Replace multiple underscores with single
    sanitized = re.sub(None, '_', sanitized)
    
    return sanitized


def x_sanitize_filename__mutmut_13(filename: str) -> str:
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
    sanitized = re.sub(illegal_chars, '_', filename)
    
    # Replace multiple underscores with single
    sanitized = re.sub(r'_+', None, sanitized)
    
    return sanitized


def x_sanitize_filename__mutmut_14(filename: str) -> str:
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
    sanitized = re.sub(illegal_chars, '_', filename)
    
    # Replace multiple underscores with single
    sanitized = re.sub(r'_+', '_', None)
    
    return sanitized


def x_sanitize_filename__mutmut_15(filename: str) -> str:
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
    sanitized = re.sub(illegal_chars, '_', filename)
    
    # Replace multiple underscores with single
    sanitized = re.sub('_', sanitized)
    
    return sanitized


def x_sanitize_filename__mutmut_16(filename: str) -> str:
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
    sanitized = re.sub(illegal_chars, '_', filename)
    
    # Replace multiple underscores with single
    sanitized = re.sub(r'_+', sanitized)
    
    return sanitized


def x_sanitize_filename__mutmut_17(filename: str) -> str:
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
    sanitized = re.sub(illegal_chars, '_', filename)
    
    # Replace multiple underscores with single
    sanitized = re.sub(r'_+', '_', )
    
    return sanitized


def x_sanitize_filename__mutmut_18(filename: str) -> str:
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
    sanitized = re.sub(illegal_chars, '_', filename)
    
    # Replace multiple underscores with single
    sanitized = re.sub(r'XX_+XX', '_', sanitized)
    
    return sanitized


def x_sanitize_filename__mutmut_19(filename: str) -> str:
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
    sanitized = re.sub(illegal_chars, '_', filename)
    
    # Replace multiple underscores with single
    sanitized = re.sub(r'_+', 'XX_XX', sanitized)
    
    return sanitized

x_sanitize_filename__mutmut_mutants : ClassVar[MutantDict] = {
'x_sanitize_filename__mutmut_1': x_sanitize_filename__mutmut_1, 
    'x_sanitize_filename__mutmut_2': x_sanitize_filename__mutmut_2, 
    'x_sanitize_filename__mutmut_3': x_sanitize_filename__mutmut_3, 
    'x_sanitize_filename__mutmut_4': x_sanitize_filename__mutmut_4, 
    'x_sanitize_filename__mutmut_5': x_sanitize_filename__mutmut_5, 
    'x_sanitize_filename__mutmut_6': x_sanitize_filename__mutmut_6, 
    'x_sanitize_filename__mutmut_7': x_sanitize_filename__mutmut_7, 
    'x_sanitize_filename__mutmut_8': x_sanitize_filename__mutmut_8, 
    'x_sanitize_filename__mutmut_9': x_sanitize_filename__mutmut_9, 
    'x_sanitize_filename__mutmut_10': x_sanitize_filename__mutmut_10, 
    'x_sanitize_filename__mutmut_11': x_sanitize_filename__mutmut_11, 
    'x_sanitize_filename__mutmut_12': x_sanitize_filename__mutmut_12, 
    'x_sanitize_filename__mutmut_13': x_sanitize_filename__mutmut_13, 
    'x_sanitize_filename__mutmut_14': x_sanitize_filename__mutmut_14, 
    'x_sanitize_filename__mutmut_15': x_sanitize_filename__mutmut_15, 
    'x_sanitize_filename__mutmut_16': x_sanitize_filename__mutmut_16, 
    'x_sanitize_filename__mutmut_17': x_sanitize_filename__mutmut_17, 
    'x_sanitize_filename__mutmut_18': x_sanitize_filename__mutmut_18, 
    'x_sanitize_filename__mutmut_19': x_sanitize_filename__mutmut_19
}

def sanitize_filename(*args, **kwargs):
    result = _mutmut_trampoline(x_sanitize_filename__mutmut_orig, x_sanitize_filename__mutmut_mutants, args, kwargs)
    return result 

sanitize_filename.__signature__ = _mutmut_signature(x_sanitize_filename__mutmut_orig)
x_sanitize_filename__mutmut_orig.__name__ = 'x_sanitize_filename'
