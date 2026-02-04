"""MCP protocol versioning support.

This module provides version negotiation for MCP (Model Context Protocol).
The server and client use this to agree on a compatible protocol version.

Safeguards implemented:
- Input validation on version lists
- Bounds checking on version string lengths
- Defensive error handling with clear messages
- Deterministic version ordering for reproducibility
- Timeout protection via bounded operations
- Sanitization of version strings
"""

from __future__ import annotations

import logging
import re

# Configure logging for safeguard tracing
logger = logging.getLogger(__name__)

# Supported MCP protocol versions in preference order (highest to lowest)
# Deterministic ordering ensures reproducible version negotiation
MCP_VERSIONS: list[str] = ["1.0"]

# Maximum bounds for version validation (safeguard)
MAX_VERSION_LENGTH = 20
MAX_VERSIONS_COUNT = 100

# Semantic version regex pattern for validation (safeguard)
# Matches simple semantic versions: MAJOR.MINOR or MAJOR.MINOR.PATCH
# Restricted to formats matching MCP_VERSIONS (no pre-release/build metadata)
# Examples: "1.0", "2.1.3"
VERSION_PATTERN = r'^(\d+)\.(\d+)(?:\.(\d+))?$'
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


def x__validate_version_string__mutmut_orig(version: str) -> bool:
    """Validate version string format.

    Safeguard: Validates version strings to prevent injection and ensure
    correct format for secure version negotiation.

    Args:
        version: Version string to validate

    Returns:
        True if valid, False otherwise
    """
    # Bounds check on length (safeguard)
    if not version or len(version) > MAX_VERSION_LENGTH:
        return False

    # Sanitize: Only allow semantic version format (safeguard)
    return bool(re.match(VERSION_PATTERN, version))


def x__validate_version_string__mutmut_1(version: str) -> bool:
    """Validate version string format.

    Safeguard: Validates version strings to prevent injection and ensure
    correct format for secure version negotiation.

    Args:
        version: Version string to validate

    Returns:
        True if valid, False otherwise
    """
    # Bounds check on length (safeguard)
    if not version and len(version) > MAX_VERSION_LENGTH:
        return False

    # Sanitize: Only allow semantic version format (safeguard)
    return bool(re.match(VERSION_PATTERN, version))


def x__validate_version_string__mutmut_2(version: str) -> bool:
    """Validate version string format.

    Safeguard: Validates version strings to prevent injection and ensure
    correct format for secure version negotiation.

    Args:
        version: Version string to validate

    Returns:
        True if valid, False otherwise
    """
    # Bounds check on length (safeguard)
    if version or len(version) > MAX_VERSION_LENGTH:
        return False

    # Sanitize: Only allow semantic version format (safeguard)
    return bool(re.match(VERSION_PATTERN, version))


def x__validate_version_string__mutmut_3(version: str) -> bool:
    """Validate version string format.

    Safeguard: Validates version strings to prevent injection and ensure
    correct format for secure version negotiation.

    Args:
        version: Version string to validate

    Returns:
        True if valid, False otherwise
    """
    # Bounds check on length (safeguard)
    if not version or len(version) >= MAX_VERSION_LENGTH:
        return False

    # Sanitize: Only allow semantic version format (safeguard)
    return bool(re.match(VERSION_PATTERN, version))


def x__validate_version_string__mutmut_4(version: str) -> bool:
    """Validate version string format.

    Safeguard: Validates version strings to prevent injection and ensure
    correct format for secure version negotiation.

    Args:
        version: Version string to validate

    Returns:
        True if valid, False otherwise
    """
    # Bounds check on length (safeguard)
    if not version or len(version) > MAX_VERSION_LENGTH:
        return True

    # Sanitize: Only allow semantic version format (safeguard)
    return bool(re.match(VERSION_PATTERN, version))


def x__validate_version_string__mutmut_5(version: str) -> bool:
    """Validate version string format.

    Safeguard: Validates version strings to prevent injection and ensure
    correct format for secure version negotiation.

    Args:
        version: Version string to validate

    Returns:
        True if valid, False otherwise
    """
    # Bounds check on length (safeguard)
    if not version or len(version) > MAX_VERSION_LENGTH:
        return False

    # Sanitize: Only allow semantic version format (safeguard)
    return bool(None)


def x__validate_version_string__mutmut_6(version: str) -> bool:
    """Validate version string format.

    Safeguard: Validates version strings to prevent injection and ensure
    correct format for secure version negotiation.

    Args:
        version: Version string to validate

    Returns:
        True if valid, False otherwise
    """
    # Bounds check on length (safeguard)
    if not version or len(version) > MAX_VERSION_LENGTH:
        return False

    # Sanitize: Only allow semantic version format (safeguard)
    return bool(re.match(None, version))


def x__validate_version_string__mutmut_7(version: str) -> bool:
    """Validate version string format.

    Safeguard: Validates version strings to prevent injection and ensure
    correct format for secure version negotiation.

    Args:
        version: Version string to validate

    Returns:
        True if valid, False otherwise
    """
    # Bounds check on length (safeguard)
    if not version or len(version) > MAX_VERSION_LENGTH:
        return False

    # Sanitize: Only allow semantic version format (safeguard)
    return bool(re.match(VERSION_PATTERN, None))


def x__validate_version_string__mutmut_8(version: str) -> bool:
    """Validate version string format.

    Safeguard: Validates version strings to prevent injection and ensure
    correct format for secure version negotiation.

    Args:
        version: Version string to validate

    Returns:
        True if valid, False otherwise
    """
    # Bounds check on length (safeguard)
    if not version or len(version) > MAX_VERSION_LENGTH:
        return False

    # Sanitize: Only allow semantic version format (safeguard)
    return bool(re.match(version))


def x__validate_version_string__mutmut_9(version: str) -> bool:
    """Validate version string format.

    Safeguard: Validates version strings to prevent injection and ensure
    correct format for secure version negotiation.

    Args:
        version: Version string to validate

    Returns:
        True if valid, False otherwise
    """
    # Bounds check on length (safeguard)
    if not version or len(version) > MAX_VERSION_LENGTH:
        return False

    # Sanitize: Only allow semantic version format (safeguard)
    return bool(re.match(VERSION_PATTERN, ))

x__validate_version_string__mutmut_mutants : ClassVar[MutantDict] = {
'x__validate_version_string__mutmut_1': x__validate_version_string__mutmut_1, 
    'x__validate_version_string__mutmut_2': x__validate_version_string__mutmut_2, 
    'x__validate_version_string__mutmut_3': x__validate_version_string__mutmut_3, 
    'x__validate_version_string__mutmut_4': x__validate_version_string__mutmut_4, 
    'x__validate_version_string__mutmut_5': x__validate_version_string__mutmut_5, 
    'x__validate_version_string__mutmut_6': x__validate_version_string__mutmut_6, 
    'x__validate_version_string__mutmut_7': x__validate_version_string__mutmut_7, 
    'x__validate_version_string__mutmut_8': x__validate_version_string__mutmut_8, 
    'x__validate_version_string__mutmut_9': x__validate_version_string__mutmut_9
}

def _validate_version_string(*args, **kwargs):
    result = _mutmut_trampoline(x__validate_version_string__mutmut_orig, x__validate_version_string__mutmut_mutants, args, kwargs)
    return result 

_validate_version_string.__signature__ = _mutmut_signature(x__validate_version_string__mutmut_orig)
x__validate_version_string__mutmut_orig.__name__ = 'x__validate_version_string'


def x__sanitize_version_list__mutmut_orig(versions: list[str]) -> list[str]:
    """Sanitize and validate a list of version strings.

    Safeguard: Filters out invalid versions and bounds the list size
    to prevent resource exhaustion attacks.

    Args:
        versions: list of version strings

    Returns:
        Sanitized list of valid versions
    """
    if not isinstance(versions, list):
        logger.warning("Invalid versions type, expected list")
        return []

    # Bounds check on list size (safeguard)
    if len(versions) > MAX_VERSIONS_COUNT:
        logger.warning(f"Version list exceeds maximum: {len(versions)} > {MAX_VERSIONS_COUNT}")
        versions = versions[:MAX_VERSIONS_COUNT]

    # Filter to valid versions only (sanitization safeguard)
    valid_versions = [v for v in versions if isinstance(v, str) and _validate_version_string(v)]

    if len(valid_versions) != len(versions):
        logger.debug(f"Filtered {len(versions) - len(valid_versions)} invalid versions")

    return valid_versions


def x__sanitize_version_list__mutmut_1(versions: list[str]) -> list[str]:
    """Sanitize and validate a list of version strings.

    Safeguard: Filters out invalid versions and bounds the list size
    to prevent resource exhaustion attacks.

    Args:
        versions: list of version strings

    Returns:
        Sanitized list of valid versions
    """
    if isinstance(versions, list):
        logger.warning("Invalid versions type, expected list")
        return []

    # Bounds check on list size (safeguard)
    if len(versions) > MAX_VERSIONS_COUNT:
        logger.warning(f"Version list exceeds maximum: {len(versions)} > {MAX_VERSIONS_COUNT}")
        versions = versions[:MAX_VERSIONS_COUNT]

    # Filter to valid versions only (sanitization safeguard)
    valid_versions = [v for v in versions if isinstance(v, str) and _validate_version_string(v)]

    if len(valid_versions) != len(versions):
        logger.debug(f"Filtered {len(versions) - len(valid_versions)} invalid versions")

    return valid_versions


def x__sanitize_version_list__mutmut_2(versions: list[str]) -> list[str]:
    """Sanitize and validate a list of version strings.

    Safeguard: Filters out invalid versions and bounds the list size
    to prevent resource exhaustion attacks.

    Args:
        versions: list of version strings

    Returns:
        Sanitized list of valid versions
    """
    if not isinstance(versions, list):
        logger.warning(None)
        return []

    # Bounds check on list size (safeguard)
    if len(versions) > MAX_VERSIONS_COUNT:
        logger.warning(f"Version list exceeds maximum: {len(versions)} > {MAX_VERSIONS_COUNT}")
        versions = versions[:MAX_VERSIONS_COUNT]

    # Filter to valid versions only (sanitization safeguard)
    valid_versions = [v for v in versions if isinstance(v, str) and _validate_version_string(v)]

    if len(valid_versions) != len(versions):
        logger.debug(f"Filtered {len(versions) - len(valid_versions)} invalid versions")

    return valid_versions


def x__sanitize_version_list__mutmut_3(versions: list[str]) -> list[str]:
    """Sanitize and validate a list of version strings.

    Safeguard: Filters out invalid versions and bounds the list size
    to prevent resource exhaustion attacks.

    Args:
        versions: list of version strings

    Returns:
        Sanitized list of valid versions
    """
    if not isinstance(versions, list):
        logger.warning("XXInvalid versions type, expected listXX")
        return []

    # Bounds check on list size (safeguard)
    if len(versions) > MAX_VERSIONS_COUNT:
        logger.warning(f"Version list exceeds maximum: {len(versions)} > {MAX_VERSIONS_COUNT}")
        versions = versions[:MAX_VERSIONS_COUNT]

    # Filter to valid versions only (sanitization safeguard)
    valid_versions = [v for v in versions if isinstance(v, str) and _validate_version_string(v)]

    if len(valid_versions) != len(versions):
        logger.debug(f"Filtered {len(versions) - len(valid_versions)} invalid versions")

    return valid_versions


def x__sanitize_version_list__mutmut_4(versions: list[str]) -> list[str]:
    """Sanitize and validate a list of version strings.

    Safeguard: Filters out invalid versions and bounds the list size
    to prevent resource exhaustion attacks.

    Args:
        versions: list of version strings

    Returns:
        Sanitized list of valid versions
    """
    if not isinstance(versions, list):
        logger.warning("invalid versions type, expected list")
        return []

    # Bounds check on list size (safeguard)
    if len(versions) > MAX_VERSIONS_COUNT:
        logger.warning(f"Version list exceeds maximum: {len(versions)} > {MAX_VERSIONS_COUNT}")
        versions = versions[:MAX_VERSIONS_COUNT]

    # Filter to valid versions only (sanitization safeguard)
    valid_versions = [v for v in versions if isinstance(v, str) and _validate_version_string(v)]

    if len(valid_versions) != len(versions):
        logger.debug(f"Filtered {len(versions) - len(valid_versions)} invalid versions")

    return valid_versions


def x__sanitize_version_list__mutmut_5(versions: list[str]) -> list[str]:
    """Sanitize and validate a list of version strings.

    Safeguard: Filters out invalid versions and bounds the list size
    to prevent resource exhaustion attacks.

    Args:
        versions: list of version strings

    Returns:
        Sanitized list of valid versions
    """
    if not isinstance(versions, list):
        logger.warning("INVALID VERSIONS TYPE, EXPECTED LIST")
        return []

    # Bounds check on list size (safeguard)
    if len(versions) > MAX_VERSIONS_COUNT:
        logger.warning(f"Version list exceeds maximum: {len(versions)} > {MAX_VERSIONS_COUNT}")
        versions = versions[:MAX_VERSIONS_COUNT]

    # Filter to valid versions only (sanitization safeguard)
    valid_versions = [v for v in versions if isinstance(v, str) and _validate_version_string(v)]

    if len(valid_versions) != len(versions):
        logger.debug(f"Filtered {len(versions) - len(valid_versions)} invalid versions")

    return valid_versions


def x__sanitize_version_list__mutmut_6(versions: list[str]) -> list[str]:
    """Sanitize and validate a list of version strings.

    Safeguard: Filters out invalid versions and bounds the list size
    to prevent resource exhaustion attacks.

    Args:
        versions: list of version strings

    Returns:
        Sanitized list of valid versions
    """
    if not isinstance(versions, list):
        logger.warning("Invalid versions type, expected list")
        return []

    # Bounds check on list size (safeguard)
    if len(versions) >= MAX_VERSIONS_COUNT:
        logger.warning(f"Version list exceeds maximum: {len(versions)} > {MAX_VERSIONS_COUNT}")
        versions = versions[:MAX_VERSIONS_COUNT]

    # Filter to valid versions only (sanitization safeguard)
    valid_versions = [v for v in versions if isinstance(v, str) and _validate_version_string(v)]

    if len(valid_versions) != len(versions):
        logger.debug(f"Filtered {len(versions) - len(valid_versions)} invalid versions")

    return valid_versions


def x__sanitize_version_list__mutmut_7(versions: list[str]) -> list[str]:
    """Sanitize and validate a list of version strings.

    Safeguard: Filters out invalid versions and bounds the list size
    to prevent resource exhaustion attacks.

    Args:
        versions: list of version strings

    Returns:
        Sanitized list of valid versions
    """
    if not isinstance(versions, list):
        logger.warning("Invalid versions type, expected list")
        return []

    # Bounds check on list size (safeguard)
    if len(versions) > MAX_VERSIONS_COUNT:
        logger.warning(None)
        versions = versions[:MAX_VERSIONS_COUNT]

    # Filter to valid versions only (sanitization safeguard)
    valid_versions = [v for v in versions if isinstance(v, str) and _validate_version_string(v)]

    if len(valid_versions) != len(versions):
        logger.debug(f"Filtered {len(versions) - len(valid_versions)} invalid versions")

    return valid_versions


def x__sanitize_version_list__mutmut_8(versions: list[str]) -> list[str]:
    """Sanitize and validate a list of version strings.

    Safeguard: Filters out invalid versions and bounds the list size
    to prevent resource exhaustion attacks.

    Args:
        versions: list of version strings

    Returns:
        Sanitized list of valid versions
    """
    if not isinstance(versions, list):
        logger.warning("Invalid versions type, expected list")
        return []

    # Bounds check on list size (safeguard)
    if len(versions) > MAX_VERSIONS_COUNT:
        logger.warning(f"Version list exceeds maximum: {len(versions)} > {MAX_VERSIONS_COUNT}")
        versions = None

    # Filter to valid versions only (sanitization safeguard)
    valid_versions = [v for v in versions if isinstance(v, str) and _validate_version_string(v)]

    if len(valid_versions) != len(versions):
        logger.debug(f"Filtered {len(versions) - len(valid_versions)} invalid versions")

    return valid_versions


def x__sanitize_version_list__mutmut_9(versions: list[str]) -> list[str]:
    """Sanitize and validate a list of version strings.

    Safeguard: Filters out invalid versions and bounds the list size
    to prevent resource exhaustion attacks.

    Args:
        versions: list of version strings

    Returns:
        Sanitized list of valid versions
    """
    if not isinstance(versions, list):
        logger.warning("Invalid versions type, expected list")
        return []

    # Bounds check on list size (safeguard)
    if len(versions) > MAX_VERSIONS_COUNT:
        logger.warning(f"Version list exceeds maximum: {len(versions)} > {MAX_VERSIONS_COUNT}")
        versions = versions[:MAX_VERSIONS_COUNT]

    # Filter to valid versions only (sanitization safeguard)
    valid_versions = None

    if len(valid_versions) != len(versions):
        logger.debug(f"Filtered {len(versions) - len(valid_versions)} invalid versions")

    return valid_versions


def x__sanitize_version_list__mutmut_10(versions: list[str]) -> list[str]:
    """Sanitize and validate a list of version strings.

    Safeguard: Filters out invalid versions and bounds the list size
    to prevent resource exhaustion attacks.

    Args:
        versions: list of version strings

    Returns:
        Sanitized list of valid versions
    """
    if not isinstance(versions, list):
        logger.warning("Invalid versions type, expected list")
        return []

    # Bounds check on list size (safeguard)
    if len(versions) > MAX_VERSIONS_COUNT:
        logger.warning(f"Version list exceeds maximum: {len(versions)} > {MAX_VERSIONS_COUNT}")
        versions = versions[:MAX_VERSIONS_COUNT]

    # Filter to valid versions only (sanitization safeguard)
    valid_versions = [v for v in versions if isinstance(v, str) or _validate_version_string(v)]

    if len(valid_versions) != len(versions):
        logger.debug(f"Filtered {len(versions) - len(valid_versions)} invalid versions")

    return valid_versions


def x__sanitize_version_list__mutmut_11(versions: list[str]) -> list[str]:
    """Sanitize and validate a list of version strings.

    Safeguard: Filters out invalid versions and bounds the list size
    to prevent resource exhaustion attacks.

    Args:
        versions: list of version strings

    Returns:
        Sanitized list of valid versions
    """
    if not isinstance(versions, list):
        logger.warning("Invalid versions type, expected list")
        return []

    # Bounds check on list size (safeguard)
    if len(versions) > MAX_VERSIONS_COUNT:
        logger.warning(f"Version list exceeds maximum: {len(versions)} > {MAX_VERSIONS_COUNT}")
        versions = versions[:MAX_VERSIONS_COUNT]

    # Filter to valid versions only (sanitization safeguard)
    valid_versions = [v for v in versions if isinstance(v, str) and _validate_version_string(None)]

    if len(valid_versions) != len(versions):
        logger.debug(f"Filtered {len(versions) - len(valid_versions)} invalid versions")

    return valid_versions


def x__sanitize_version_list__mutmut_12(versions: list[str]) -> list[str]:
    """Sanitize and validate a list of version strings.

    Safeguard: Filters out invalid versions and bounds the list size
    to prevent resource exhaustion attacks.

    Args:
        versions: list of version strings

    Returns:
        Sanitized list of valid versions
    """
    if not isinstance(versions, list):
        logger.warning("Invalid versions type, expected list")
        return []

    # Bounds check on list size (safeguard)
    if len(versions) > MAX_VERSIONS_COUNT:
        logger.warning(f"Version list exceeds maximum: {len(versions)} > {MAX_VERSIONS_COUNT}")
        versions = versions[:MAX_VERSIONS_COUNT]

    # Filter to valid versions only (sanitization safeguard)
    valid_versions = [v for v in versions if isinstance(v, str) and _validate_version_string(v)]

    if len(valid_versions) == len(versions):
        logger.debug(f"Filtered {len(versions) - len(valid_versions)} invalid versions")

    return valid_versions


def x__sanitize_version_list__mutmut_13(versions: list[str]) -> list[str]:
    """Sanitize and validate a list of version strings.

    Safeguard: Filters out invalid versions and bounds the list size
    to prevent resource exhaustion attacks.

    Args:
        versions: list of version strings

    Returns:
        Sanitized list of valid versions
    """
    if not isinstance(versions, list):
        logger.warning("Invalid versions type, expected list")
        return []

    # Bounds check on list size (safeguard)
    if len(versions) > MAX_VERSIONS_COUNT:
        logger.warning(f"Version list exceeds maximum: {len(versions)} > {MAX_VERSIONS_COUNT}")
        versions = versions[:MAX_VERSIONS_COUNT]

    # Filter to valid versions only (sanitization safeguard)
    valid_versions = [v for v in versions if isinstance(v, str) and _validate_version_string(v)]

    if len(valid_versions) != len(versions):
        logger.debug(None)

    return valid_versions


def x__sanitize_version_list__mutmut_14(versions: list[str]) -> list[str]:
    """Sanitize and validate a list of version strings.

    Safeguard: Filters out invalid versions and bounds the list size
    to prevent resource exhaustion attacks.

    Args:
        versions: list of version strings

    Returns:
        Sanitized list of valid versions
    """
    if not isinstance(versions, list):
        logger.warning("Invalid versions type, expected list")
        return []

    # Bounds check on list size (safeguard)
    if len(versions) > MAX_VERSIONS_COUNT:
        logger.warning(f"Version list exceeds maximum: {len(versions)} > {MAX_VERSIONS_COUNT}")
        versions = versions[:MAX_VERSIONS_COUNT]

    # Filter to valid versions only (sanitization safeguard)
    valid_versions = [v for v in versions if isinstance(v, str) and _validate_version_string(v)]

    if len(valid_versions) != len(versions):
        logger.debug(f"Filtered {len(versions) + len(valid_versions)} invalid versions")

    return valid_versions

x__sanitize_version_list__mutmut_mutants : ClassVar[MutantDict] = {
'x__sanitize_version_list__mutmut_1': x__sanitize_version_list__mutmut_1, 
    'x__sanitize_version_list__mutmut_2': x__sanitize_version_list__mutmut_2, 
    'x__sanitize_version_list__mutmut_3': x__sanitize_version_list__mutmut_3, 
    'x__sanitize_version_list__mutmut_4': x__sanitize_version_list__mutmut_4, 
    'x__sanitize_version_list__mutmut_5': x__sanitize_version_list__mutmut_5, 
    'x__sanitize_version_list__mutmut_6': x__sanitize_version_list__mutmut_6, 
    'x__sanitize_version_list__mutmut_7': x__sanitize_version_list__mutmut_7, 
    'x__sanitize_version_list__mutmut_8': x__sanitize_version_list__mutmut_8, 
    'x__sanitize_version_list__mutmut_9': x__sanitize_version_list__mutmut_9, 
    'x__sanitize_version_list__mutmut_10': x__sanitize_version_list__mutmut_10, 
    'x__sanitize_version_list__mutmut_11': x__sanitize_version_list__mutmut_11, 
    'x__sanitize_version_list__mutmut_12': x__sanitize_version_list__mutmut_12, 
    'x__sanitize_version_list__mutmut_13': x__sanitize_version_list__mutmut_13, 
    'x__sanitize_version_list__mutmut_14': x__sanitize_version_list__mutmut_14
}

def _sanitize_version_list(*args, **kwargs):
    result = _mutmut_trampoline(x__sanitize_version_list__mutmut_orig, x__sanitize_version_list__mutmut_mutants, args, kwargs)
    return result 

_sanitize_version_list.__signature__ = _mutmut_signature(x__sanitize_version_list__mutmut_orig)
x__sanitize_version_list__mutmut_orig.__name__ = 'x__sanitize_version_list'


def x_negotiate_version__mutmut_orig(client_versions: list[str]) -> str:
    """Negotiate MCP protocol version between client and server.

    Safeguards implemented:
    - Input validation on client_versions list
    - Bounds checking on list size
    - Version string sanitization
    - Defensive error handling with clear messages
    - Deterministic version preference ordering

    Args:
        client_versions: list of versions supported by the client

    Returns:
        The negotiated version string (highest version supported by both)

    Raises:
        ValueError: If no compatible version is found

    Example:
        >>> negotiate_version(["1.0", "0.9"])
        '1.0'
        >>> negotiate_version(["2.0", "1.0"])
        '1.0'
    """
    # Input validation (safeguard)
    if not client_versions:
        raise ValueError("Client must provide at least one supported version")

    # Sanitize and validate input (safeguard)
    sanitized_versions = _sanitize_version_list(client_versions)

    if not sanitized_versions:
        raise ValueError("No valid version strings provided after sanitization")

    # Find the first version in our preference order that the client also supports
    # Deterministic ordering ensures reproducible results (safeguard)
    for server_version in MCP_VERSIONS:
        if server_version in sanitized_versions:
            logger.debug(f"Negotiated version: {server_version}")
            return server_version

    # No common version found - defensive error handling (safeguard)
    raise ValueError(
        f"No compatible MCP version found. "
        f"Server supports: {MCP_VERSIONS}, Client supports: {sanitized_versions}"
    )


def x_negotiate_version__mutmut_1(client_versions: list[str]) -> str:
    """Negotiate MCP protocol version between client and server.

    Safeguards implemented:
    - Input validation on client_versions list
    - Bounds checking on list size
    - Version string sanitization
    - Defensive error handling with clear messages
    - Deterministic version preference ordering

    Args:
        client_versions: list of versions supported by the client

    Returns:
        The negotiated version string (highest version supported by both)

    Raises:
        ValueError: If no compatible version is found

    Example:
        >>> negotiate_version(["1.0", "0.9"])
        '1.0'
        >>> negotiate_version(["2.0", "1.0"])
        '1.0'
    """
    # Input validation (safeguard)
    if client_versions:
        raise ValueError("Client must provide at least one supported version")

    # Sanitize and validate input (safeguard)
    sanitized_versions = _sanitize_version_list(client_versions)

    if not sanitized_versions:
        raise ValueError("No valid version strings provided after sanitization")

    # Find the first version in our preference order that the client also supports
    # Deterministic ordering ensures reproducible results (safeguard)
    for server_version in MCP_VERSIONS:
        if server_version in sanitized_versions:
            logger.debug(f"Negotiated version: {server_version}")
            return server_version

    # No common version found - defensive error handling (safeguard)
    raise ValueError(
        f"No compatible MCP version found. "
        f"Server supports: {MCP_VERSIONS}, Client supports: {sanitized_versions}"
    )


def x_negotiate_version__mutmut_2(client_versions: list[str]) -> str:
    """Negotiate MCP protocol version between client and server.

    Safeguards implemented:
    - Input validation on client_versions list
    - Bounds checking on list size
    - Version string sanitization
    - Defensive error handling with clear messages
    - Deterministic version preference ordering

    Args:
        client_versions: list of versions supported by the client

    Returns:
        The negotiated version string (highest version supported by both)

    Raises:
        ValueError: If no compatible version is found

    Example:
        >>> negotiate_version(["1.0", "0.9"])
        '1.0'
        >>> negotiate_version(["2.0", "1.0"])
        '1.0'
    """
    # Input validation (safeguard)
    if not client_versions:
        raise ValueError(None)

    # Sanitize and validate input (safeguard)
    sanitized_versions = _sanitize_version_list(client_versions)

    if not sanitized_versions:
        raise ValueError("No valid version strings provided after sanitization")

    # Find the first version in our preference order that the client also supports
    # Deterministic ordering ensures reproducible results (safeguard)
    for server_version in MCP_VERSIONS:
        if server_version in sanitized_versions:
            logger.debug(f"Negotiated version: {server_version}")
            return server_version

    # No common version found - defensive error handling (safeguard)
    raise ValueError(
        f"No compatible MCP version found. "
        f"Server supports: {MCP_VERSIONS}, Client supports: {sanitized_versions}"
    )


def x_negotiate_version__mutmut_3(client_versions: list[str]) -> str:
    """Negotiate MCP protocol version between client and server.

    Safeguards implemented:
    - Input validation on client_versions list
    - Bounds checking on list size
    - Version string sanitization
    - Defensive error handling with clear messages
    - Deterministic version preference ordering

    Args:
        client_versions: list of versions supported by the client

    Returns:
        The negotiated version string (highest version supported by both)

    Raises:
        ValueError: If no compatible version is found

    Example:
        >>> negotiate_version(["1.0", "0.9"])
        '1.0'
        >>> negotiate_version(["2.0", "1.0"])
        '1.0'
    """
    # Input validation (safeguard)
    if not client_versions:
        raise ValueError("XXClient must provide at least one supported versionXX")

    # Sanitize and validate input (safeguard)
    sanitized_versions = _sanitize_version_list(client_versions)

    if not sanitized_versions:
        raise ValueError("No valid version strings provided after sanitization")

    # Find the first version in our preference order that the client also supports
    # Deterministic ordering ensures reproducible results (safeguard)
    for server_version in MCP_VERSIONS:
        if server_version in sanitized_versions:
            logger.debug(f"Negotiated version: {server_version}")
            return server_version

    # No common version found - defensive error handling (safeguard)
    raise ValueError(
        f"No compatible MCP version found. "
        f"Server supports: {MCP_VERSIONS}, Client supports: {sanitized_versions}"
    )


def x_negotiate_version__mutmut_4(client_versions: list[str]) -> str:
    """Negotiate MCP protocol version between client and server.

    Safeguards implemented:
    - Input validation on client_versions list
    - Bounds checking on list size
    - Version string sanitization
    - Defensive error handling with clear messages
    - Deterministic version preference ordering

    Args:
        client_versions: list of versions supported by the client

    Returns:
        The negotiated version string (highest version supported by both)

    Raises:
        ValueError: If no compatible version is found

    Example:
        >>> negotiate_version(["1.0", "0.9"])
        '1.0'
        >>> negotiate_version(["2.0", "1.0"])
        '1.0'
    """
    # Input validation (safeguard)
    if not client_versions:
        raise ValueError("client must provide at least one supported version")

    # Sanitize and validate input (safeguard)
    sanitized_versions = _sanitize_version_list(client_versions)

    if not sanitized_versions:
        raise ValueError("No valid version strings provided after sanitization")

    # Find the first version in our preference order that the client also supports
    # Deterministic ordering ensures reproducible results (safeguard)
    for server_version in MCP_VERSIONS:
        if server_version in sanitized_versions:
            logger.debug(f"Negotiated version: {server_version}")
            return server_version

    # No common version found - defensive error handling (safeguard)
    raise ValueError(
        f"No compatible MCP version found. "
        f"Server supports: {MCP_VERSIONS}, Client supports: {sanitized_versions}"
    )


def x_negotiate_version__mutmut_5(client_versions: list[str]) -> str:
    """Negotiate MCP protocol version between client and server.

    Safeguards implemented:
    - Input validation on client_versions list
    - Bounds checking on list size
    - Version string sanitization
    - Defensive error handling with clear messages
    - Deterministic version preference ordering

    Args:
        client_versions: list of versions supported by the client

    Returns:
        The negotiated version string (highest version supported by both)

    Raises:
        ValueError: If no compatible version is found

    Example:
        >>> negotiate_version(["1.0", "0.9"])
        '1.0'
        >>> negotiate_version(["2.0", "1.0"])
        '1.0'
    """
    # Input validation (safeguard)
    if not client_versions:
        raise ValueError("CLIENT MUST PROVIDE AT LEAST ONE SUPPORTED VERSION")

    # Sanitize and validate input (safeguard)
    sanitized_versions = _sanitize_version_list(client_versions)

    if not sanitized_versions:
        raise ValueError("No valid version strings provided after sanitization")

    # Find the first version in our preference order that the client also supports
    # Deterministic ordering ensures reproducible results (safeguard)
    for server_version in MCP_VERSIONS:
        if server_version in sanitized_versions:
            logger.debug(f"Negotiated version: {server_version}")
            return server_version

    # No common version found - defensive error handling (safeguard)
    raise ValueError(
        f"No compatible MCP version found. "
        f"Server supports: {MCP_VERSIONS}, Client supports: {sanitized_versions}"
    )


def x_negotiate_version__mutmut_6(client_versions: list[str]) -> str:
    """Negotiate MCP protocol version between client and server.

    Safeguards implemented:
    - Input validation on client_versions list
    - Bounds checking on list size
    - Version string sanitization
    - Defensive error handling with clear messages
    - Deterministic version preference ordering

    Args:
        client_versions: list of versions supported by the client

    Returns:
        The negotiated version string (highest version supported by both)

    Raises:
        ValueError: If no compatible version is found

    Example:
        >>> negotiate_version(["1.0", "0.9"])
        '1.0'
        >>> negotiate_version(["2.0", "1.0"])
        '1.0'
    """
    # Input validation (safeguard)
    if not client_versions:
        raise ValueError("Client must provide at least one supported version")

    # Sanitize and validate input (safeguard)
    sanitized_versions = None

    if not sanitized_versions:
        raise ValueError("No valid version strings provided after sanitization")

    # Find the first version in our preference order that the client also supports
    # Deterministic ordering ensures reproducible results (safeguard)
    for server_version in MCP_VERSIONS:
        if server_version in sanitized_versions:
            logger.debug(f"Negotiated version: {server_version}")
            return server_version

    # No common version found - defensive error handling (safeguard)
    raise ValueError(
        f"No compatible MCP version found. "
        f"Server supports: {MCP_VERSIONS}, Client supports: {sanitized_versions}"
    )


def x_negotiate_version__mutmut_7(client_versions: list[str]) -> str:
    """Negotiate MCP protocol version between client and server.

    Safeguards implemented:
    - Input validation on client_versions list
    - Bounds checking on list size
    - Version string sanitization
    - Defensive error handling with clear messages
    - Deterministic version preference ordering

    Args:
        client_versions: list of versions supported by the client

    Returns:
        The negotiated version string (highest version supported by both)

    Raises:
        ValueError: If no compatible version is found

    Example:
        >>> negotiate_version(["1.0", "0.9"])
        '1.0'
        >>> negotiate_version(["2.0", "1.0"])
        '1.0'
    """
    # Input validation (safeguard)
    if not client_versions:
        raise ValueError("Client must provide at least one supported version")

    # Sanitize and validate input (safeguard)
    sanitized_versions = _sanitize_version_list(None)

    if not sanitized_versions:
        raise ValueError("No valid version strings provided after sanitization")

    # Find the first version in our preference order that the client also supports
    # Deterministic ordering ensures reproducible results (safeguard)
    for server_version in MCP_VERSIONS:
        if server_version in sanitized_versions:
            logger.debug(f"Negotiated version: {server_version}")
            return server_version

    # No common version found - defensive error handling (safeguard)
    raise ValueError(
        f"No compatible MCP version found. "
        f"Server supports: {MCP_VERSIONS}, Client supports: {sanitized_versions}"
    )


def x_negotiate_version__mutmut_8(client_versions: list[str]) -> str:
    """Negotiate MCP protocol version between client and server.

    Safeguards implemented:
    - Input validation on client_versions list
    - Bounds checking on list size
    - Version string sanitization
    - Defensive error handling with clear messages
    - Deterministic version preference ordering

    Args:
        client_versions: list of versions supported by the client

    Returns:
        The negotiated version string (highest version supported by both)

    Raises:
        ValueError: If no compatible version is found

    Example:
        >>> negotiate_version(["1.0", "0.9"])
        '1.0'
        >>> negotiate_version(["2.0", "1.0"])
        '1.0'
    """
    # Input validation (safeguard)
    if not client_versions:
        raise ValueError("Client must provide at least one supported version")

    # Sanitize and validate input (safeguard)
    sanitized_versions = _sanitize_version_list(client_versions)

    if sanitized_versions:
        raise ValueError("No valid version strings provided after sanitization")

    # Find the first version in our preference order that the client also supports
    # Deterministic ordering ensures reproducible results (safeguard)
    for server_version in MCP_VERSIONS:
        if server_version in sanitized_versions:
            logger.debug(f"Negotiated version: {server_version}")
            return server_version

    # No common version found - defensive error handling (safeguard)
    raise ValueError(
        f"No compatible MCP version found. "
        f"Server supports: {MCP_VERSIONS}, Client supports: {sanitized_versions}"
    )


def x_negotiate_version__mutmut_9(client_versions: list[str]) -> str:
    """Negotiate MCP protocol version between client and server.

    Safeguards implemented:
    - Input validation on client_versions list
    - Bounds checking on list size
    - Version string sanitization
    - Defensive error handling with clear messages
    - Deterministic version preference ordering

    Args:
        client_versions: list of versions supported by the client

    Returns:
        The negotiated version string (highest version supported by both)

    Raises:
        ValueError: If no compatible version is found

    Example:
        >>> negotiate_version(["1.0", "0.9"])
        '1.0'
        >>> negotiate_version(["2.0", "1.0"])
        '1.0'
    """
    # Input validation (safeguard)
    if not client_versions:
        raise ValueError("Client must provide at least one supported version")

    # Sanitize and validate input (safeguard)
    sanitized_versions = _sanitize_version_list(client_versions)

    if not sanitized_versions:
        raise ValueError(None)

    # Find the first version in our preference order that the client also supports
    # Deterministic ordering ensures reproducible results (safeguard)
    for server_version in MCP_VERSIONS:
        if server_version in sanitized_versions:
            logger.debug(f"Negotiated version: {server_version}")
            return server_version

    # No common version found - defensive error handling (safeguard)
    raise ValueError(
        f"No compatible MCP version found. "
        f"Server supports: {MCP_VERSIONS}, Client supports: {sanitized_versions}"
    )


def x_negotiate_version__mutmut_10(client_versions: list[str]) -> str:
    """Negotiate MCP protocol version between client and server.

    Safeguards implemented:
    - Input validation on client_versions list
    - Bounds checking on list size
    - Version string sanitization
    - Defensive error handling with clear messages
    - Deterministic version preference ordering

    Args:
        client_versions: list of versions supported by the client

    Returns:
        The negotiated version string (highest version supported by both)

    Raises:
        ValueError: If no compatible version is found

    Example:
        >>> negotiate_version(["1.0", "0.9"])
        '1.0'
        >>> negotiate_version(["2.0", "1.0"])
        '1.0'
    """
    # Input validation (safeguard)
    if not client_versions:
        raise ValueError("Client must provide at least one supported version")

    # Sanitize and validate input (safeguard)
    sanitized_versions = _sanitize_version_list(client_versions)

    if not sanitized_versions:
        raise ValueError("XXNo valid version strings provided after sanitizationXX")

    # Find the first version in our preference order that the client also supports
    # Deterministic ordering ensures reproducible results (safeguard)
    for server_version in MCP_VERSIONS:
        if server_version in sanitized_versions:
            logger.debug(f"Negotiated version: {server_version}")
            return server_version

    # No common version found - defensive error handling (safeguard)
    raise ValueError(
        f"No compatible MCP version found. "
        f"Server supports: {MCP_VERSIONS}, Client supports: {sanitized_versions}"
    )


def x_negotiate_version__mutmut_11(client_versions: list[str]) -> str:
    """Negotiate MCP protocol version between client and server.

    Safeguards implemented:
    - Input validation on client_versions list
    - Bounds checking on list size
    - Version string sanitization
    - Defensive error handling with clear messages
    - Deterministic version preference ordering

    Args:
        client_versions: list of versions supported by the client

    Returns:
        The negotiated version string (highest version supported by both)

    Raises:
        ValueError: If no compatible version is found

    Example:
        >>> negotiate_version(["1.0", "0.9"])
        '1.0'
        >>> negotiate_version(["2.0", "1.0"])
        '1.0'
    """
    # Input validation (safeguard)
    if not client_versions:
        raise ValueError("Client must provide at least one supported version")

    # Sanitize and validate input (safeguard)
    sanitized_versions = _sanitize_version_list(client_versions)

    if not sanitized_versions:
        raise ValueError("no valid version strings provided after sanitization")

    # Find the first version in our preference order that the client also supports
    # Deterministic ordering ensures reproducible results (safeguard)
    for server_version in MCP_VERSIONS:
        if server_version in sanitized_versions:
            logger.debug(f"Negotiated version: {server_version}")
            return server_version

    # No common version found - defensive error handling (safeguard)
    raise ValueError(
        f"No compatible MCP version found. "
        f"Server supports: {MCP_VERSIONS}, Client supports: {sanitized_versions}"
    )


def x_negotiate_version__mutmut_12(client_versions: list[str]) -> str:
    """Negotiate MCP protocol version between client and server.

    Safeguards implemented:
    - Input validation on client_versions list
    - Bounds checking on list size
    - Version string sanitization
    - Defensive error handling with clear messages
    - Deterministic version preference ordering

    Args:
        client_versions: list of versions supported by the client

    Returns:
        The negotiated version string (highest version supported by both)

    Raises:
        ValueError: If no compatible version is found

    Example:
        >>> negotiate_version(["1.0", "0.9"])
        '1.0'
        >>> negotiate_version(["2.0", "1.0"])
        '1.0'
    """
    # Input validation (safeguard)
    if not client_versions:
        raise ValueError("Client must provide at least one supported version")

    # Sanitize and validate input (safeguard)
    sanitized_versions = _sanitize_version_list(client_versions)

    if not sanitized_versions:
        raise ValueError("NO VALID VERSION STRINGS PROVIDED AFTER SANITIZATION")

    # Find the first version in our preference order that the client also supports
    # Deterministic ordering ensures reproducible results (safeguard)
    for server_version in MCP_VERSIONS:
        if server_version in sanitized_versions:
            logger.debug(f"Negotiated version: {server_version}")
            return server_version

    # No common version found - defensive error handling (safeguard)
    raise ValueError(
        f"No compatible MCP version found. "
        f"Server supports: {MCP_VERSIONS}, Client supports: {sanitized_versions}"
    )


def x_negotiate_version__mutmut_13(client_versions: list[str]) -> str:
    """Negotiate MCP protocol version between client and server.

    Safeguards implemented:
    - Input validation on client_versions list
    - Bounds checking on list size
    - Version string sanitization
    - Defensive error handling with clear messages
    - Deterministic version preference ordering

    Args:
        client_versions: list of versions supported by the client

    Returns:
        The negotiated version string (highest version supported by both)

    Raises:
        ValueError: If no compatible version is found

    Example:
        >>> negotiate_version(["1.0", "0.9"])
        '1.0'
        >>> negotiate_version(["2.0", "1.0"])
        '1.0'
    """
    # Input validation (safeguard)
    if not client_versions:
        raise ValueError("Client must provide at least one supported version")

    # Sanitize and validate input (safeguard)
    sanitized_versions = _sanitize_version_list(client_versions)

    if not sanitized_versions:
        raise ValueError("No valid version strings provided after sanitization")

    # Find the first version in our preference order that the client also supports
    # Deterministic ordering ensures reproducible results (safeguard)
    for server_version in MCP_VERSIONS:
        if server_version not in sanitized_versions:
            logger.debug(f"Negotiated version: {server_version}")
            return server_version

    # No common version found - defensive error handling (safeguard)
    raise ValueError(
        f"No compatible MCP version found. "
        f"Server supports: {MCP_VERSIONS}, Client supports: {sanitized_versions}"
    )


def x_negotiate_version__mutmut_14(client_versions: list[str]) -> str:
    """Negotiate MCP protocol version between client and server.

    Safeguards implemented:
    - Input validation on client_versions list
    - Bounds checking on list size
    - Version string sanitization
    - Defensive error handling with clear messages
    - Deterministic version preference ordering

    Args:
        client_versions: list of versions supported by the client

    Returns:
        The negotiated version string (highest version supported by both)

    Raises:
        ValueError: If no compatible version is found

    Example:
        >>> negotiate_version(["1.0", "0.9"])
        '1.0'
        >>> negotiate_version(["2.0", "1.0"])
        '1.0'
    """
    # Input validation (safeguard)
    if not client_versions:
        raise ValueError("Client must provide at least one supported version")

    # Sanitize and validate input (safeguard)
    sanitized_versions = _sanitize_version_list(client_versions)

    if not sanitized_versions:
        raise ValueError("No valid version strings provided after sanitization")

    # Find the first version in our preference order that the client also supports
    # Deterministic ordering ensures reproducible results (safeguard)
    for server_version in MCP_VERSIONS:
        if server_version in sanitized_versions:
            logger.debug(None)
            return server_version

    # No common version found - defensive error handling (safeguard)
    raise ValueError(
        f"No compatible MCP version found. "
        f"Server supports: {MCP_VERSIONS}, Client supports: {sanitized_versions}"
    )


def x_negotiate_version__mutmut_15(client_versions: list[str]) -> str:
    """Negotiate MCP protocol version between client and server.

    Safeguards implemented:
    - Input validation on client_versions list
    - Bounds checking on list size
    - Version string sanitization
    - Defensive error handling with clear messages
    - Deterministic version preference ordering

    Args:
        client_versions: list of versions supported by the client

    Returns:
        The negotiated version string (highest version supported by both)

    Raises:
        ValueError: If no compatible version is found

    Example:
        >>> negotiate_version(["1.0", "0.9"])
        '1.0'
        >>> negotiate_version(["2.0", "1.0"])
        '1.0'
    """
    # Input validation (safeguard)
    if not client_versions:
        raise ValueError("Client must provide at least one supported version")

    # Sanitize and validate input (safeguard)
    sanitized_versions = _sanitize_version_list(client_versions)

    if not sanitized_versions:
        raise ValueError("No valid version strings provided after sanitization")

    # Find the first version in our preference order that the client also supports
    # Deterministic ordering ensures reproducible results (safeguard)
    for server_version in MCP_VERSIONS:
        if server_version in sanitized_versions:
            logger.debug(f"Negotiated version: {server_version}")
            return server_version

    # No common version found - defensive error handling (safeguard)
    raise ValueError(
        None
    )

x_negotiate_version__mutmut_mutants : ClassVar[MutantDict] = {
'x_negotiate_version__mutmut_1': x_negotiate_version__mutmut_1, 
    'x_negotiate_version__mutmut_2': x_negotiate_version__mutmut_2, 
    'x_negotiate_version__mutmut_3': x_negotiate_version__mutmut_3, 
    'x_negotiate_version__mutmut_4': x_negotiate_version__mutmut_4, 
    'x_negotiate_version__mutmut_5': x_negotiate_version__mutmut_5, 
    'x_negotiate_version__mutmut_6': x_negotiate_version__mutmut_6, 
    'x_negotiate_version__mutmut_7': x_negotiate_version__mutmut_7, 
    'x_negotiate_version__mutmut_8': x_negotiate_version__mutmut_8, 
    'x_negotiate_version__mutmut_9': x_negotiate_version__mutmut_9, 
    'x_negotiate_version__mutmut_10': x_negotiate_version__mutmut_10, 
    'x_negotiate_version__mutmut_11': x_negotiate_version__mutmut_11, 
    'x_negotiate_version__mutmut_12': x_negotiate_version__mutmut_12, 
    'x_negotiate_version__mutmut_13': x_negotiate_version__mutmut_13, 
    'x_negotiate_version__mutmut_14': x_negotiate_version__mutmut_14, 
    'x_negotiate_version__mutmut_15': x_negotiate_version__mutmut_15
}

def negotiate_version(*args, **kwargs):
    result = _mutmut_trampoline(x_negotiate_version__mutmut_orig, x_negotiate_version__mutmut_mutants, args, kwargs)
    return result 

negotiate_version.__signature__ = _mutmut_signature(x_negotiate_version__mutmut_orig)
x_negotiate_version__mutmut_orig.__name__ = 'x_negotiate_version'


def x_supports_feature__mutmut_orig(feature: str, version: str) -> bool:
    """Check if a feature is supported in the given MCP version.

    Safeguards:
    - Input validation on feature and version
    - Bounded feature lookup
    - Defensive default behavior

    Args:
        feature: Feature name to check
        version: MCP version string

    Returns:
        True if feature is supported, False otherwise
    """
    # Input validation (safeguard)
    if not feature or not isinstance(feature, str):
        return False
    if not version or not _validate_version_string(version):
        return False

    # Feature availability matrix (bounded lookup - safeguard)
    # Maps feature names to list of versions that support them.
    # To add a new feature, add an entry with the feature name as key
    # and a list of version strings where it's available.
    feature_matrix = {
        "basic_tools": ["1.0"],  # Core MCP tool support
        "streaming": ["1.0"],     # Streaming response support
    }

    supported_versions = feature_matrix.get(feature, [])
    return version in supported_versions


def x_supports_feature__mutmut_1(feature: str, version: str) -> bool:
    """Check if a feature is supported in the given MCP version.

    Safeguards:
    - Input validation on feature and version
    - Bounded feature lookup
    - Defensive default behavior

    Args:
        feature: Feature name to check
        version: MCP version string

    Returns:
        True if feature is supported, False otherwise
    """
    # Input validation (safeguard)
    if not feature and not isinstance(feature, str):
        return False
    if not version or not _validate_version_string(version):
        return False

    # Feature availability matrix (bounded lookup - safeguard)
    # Maps feature names to list of versions that support them.
    # To add a new feature, add an entry with the feature name as key
    # and a list of version strings where it's available.
    feature_matrix = {
        "basic_tools": ["1.0"],  # Core MCP tool support
        "streaming": ["1.0"],     # Streaming response support
    }

    supported_versions = feature_matrix.get(feature, [])
    return version in supported_versions


def x_supports_feature__mutmut_2(feature: str, version: str) -> bool:
    """Check if a feature is supported in the given MCP version.

    Safeguards:
    - Input validation on feature and version
    - Bounded feature lookup
    - Defensive default behavior

    Args:
        feature: Feature name to check
        version: MCP version string

    Returns:
        True if feature is supported, False otherwise
    """
    # Input validation (safeguard)
    if feature or not isinstance(feature, str):
        return False
    if not version or not _validate_version_string(version):
        return False

    # Feature availability matrix (bounded lookup - safeguard)
    # Maps feature names to list of versions that support them.
    # To add a new feature, add an entry with the feature name as key
    # and a list of version strings where it's available.
    feature_matrix = {
        "basic_tools": ["1.0"],  # Core MCP tool support
        "streaming": ["1.0"],     # Streaming response support
    }

    supported_versions = feature_matrix.get(feature, [])
    return version in supported_versions


def x_supports_feature__mutmut_3(feature: str, version: str) -> bool:
    """Check if a feature is supported in the given MCP version.

    Safeguards:
    - Input validation on feature and version
    - Bounded feature lookup
    - Defensive default behavior

    Args:
        feature: Feature name to check
        version: MCP version string

    Returns:
        True if feature is supported, False otherwise
    """
    # Input validation (safeguard)
    if not feature or isinstance(feature, str):
        return False
    if not version or not _validate_version_string(version):
        return False

    # Feature availability matrix (bounded lookup - safeguard)
    # Maps feature names to list of versions that support them.
    # To add a new feature, add an entry with the feature name as key
    # and a list of version strings where it's available.
    feature_matrix = {
        "basic_tools": ["1.0"],  # Core MCP tool support
        "streaming": ["1.0"],     # Streaming response support
    }

    supported_versions = feature_matrix.get(feature, [])
    return version in supported_versions


def x_supports_feature__mutmut_4(feature: str, version: str) -> bool:
    """Check if a feature is supported in the given MCP version.

    Safeguards:
    - Input validation on feature and version
    - Bounded feature lookup
    - Defensive default behavior

    Args:
        feature: Feature name to check
        version: MCP version string

    Returns:
        True if feature is supported, False otherwise
    """
    # Input validation (safeguard)
    if not feature or not isinstance(feature, str):
        return True
    if not version or not _validate_version_string(version):
        return False

    # Feature availability matrix (bounded lookup - safeguard)
    # Maps feature names to list of versions that support them.
    # To add a new feature, add an entry with the feature name as key
    # and a list of version strings where it's available.
    feature_matrix = {
        "basic_tools": ["1.0"],  # Core MCP tool support
        "streaming": ["1.0"],     # Streaming response support
    }

    supported_versions = feature_matrix.get(feature, [])
    return version in supported_versions


def x_supports_feature__mutmut_5(feature: str, version: str) -> bool:
    """Check if a feature is supported in the given MCP version.

    Safeguards:
    - Input validation on feature and version
    - Bounded feature lookup
    - Defensive default behavior

    Args:
        feature: Feature name to check
        version: MCP version string

    Returns:
        True if feature is supported, False otherwise
    """
    # Input validation (safeguard)
    if not feature or not isinstance(feature, str):
        return False
    if not version and not _validate_version_string(version):
        return False

    # Feature availability matrix (bounded lookup - safeguard)
    # Maps feature names to list of versions that support them.
    # To add a new feature, add an entry with the feature name as key
    # and a list of version strings where it's available.
    feature_matrix = {
        "basic_tools": ["1.0"],  # Core MCP tool support
        "streaming": ["1.0"],     # Streaming response support
    }

    supported_versions = feature_matrix.get(feature, [])
    return version in supported_versions


def x_supports_feature__mutmut_6(feature: str, version: str) -> bool:
    """Check if a feature is supported in the given MCP version.

    Safeguards:
    - Input validation on feature and version
    - Bounded feature lookup
    - Defensive default behavior

    Args:
        feature: Feature name to check
        version: MCP version string

    Returns:
        True if feature is supported, False otherwise
    """
    # Input validation (safeguard)
    if not feature or not isinstance(feature, str):
        return False
    if version or not _validate_version_string(version):
        return False

    # Feature availability matrix (bounded lookup - safeguard)
    # Maps feature names to list of versions that support them.
    # To add a new feature, add an entry with the feature name as key
    # and a list of version strings where it's available.
    feature_matrix = {
        "basic_tools": ["1.0"],  # Core MCP tool support
        "streaming": ["1.0"],     # Streaming response support
    }

    supported_versions = feature_matrix.get(feature, [])
    return version in supported_versions


def x_supports_feature__mutmut_7(feature: str, version: str) -> bool:
    """Check if a feature is supported in the given MCP version.

    Safeguards:
    - Input validation on feature and version
    - Bounded feature lookup
    - Defensive default behavior

    Args:
        feature: Feature name to check
        version: MCP version string

    Returns:
        True if feature is supported, False otherwise
    """
    # Input validation (safeguard)
    if not feature or not isinstance(feature, str):
        return False
    if not version or _validate_version_string(version):
        return False

    # Feature availability matrix (bounded lookup - safeguard)
    # Maps feature names to list of versions that support them.
    # To add a new feature, add an entry with the feature name as key
    # and a list of version strings where it's available.
    feature_matrix = {
        "basic_tools": ["1.0"],  # Core MCP tool support
        "streaming": ["1.0"],     # Streaming response support
    }

    supported_versions = feature_matrix.get(feature, [])
    return version in supported_versions


def x_supports_feature__mutmut_8(feature: str, version: str) -> bool:
    """Check if a feature is supported in the given MCP version.

    Safeguards:
    - Input validation on feature and version
    - Bounded feature lookup
    - Defensive default behavior

    Args:
        feature: Feature name to check
        version: MCP version string

    Returns:
        True if feature is supported, False otherwise
    """
    # Input validation (safeguard)
    if not feature or not isinstance(feature, str):
        return False
    if not version or not _validate_version_string(None):
        return False

    # Feature availability matrix (bounded lookup - safeguard)
    # Maps feature names to list of versions that support them.
    # To add a new feature, add an entry with the feature name as key
    # and a list of version strings where it's available.
    feature_matrix = {
        "basic_tools": ["1.0"],  # Core MCP tool support
        "streaming": ["1.0"],     # Streaming response support
    }

    supported_versions = feature_matrix.get(feature, [])
    return version in supported_versions


def x_supports_feature__mutmut_9(feature: str, version: str) -> bool:
    """Check if a feature is supported in the given MCP version.

    Safeguards:
    - Input validation on feature and version
    - Bounded feature lookup
    - Defensive default behavior

    Args:
        feature: Feature name to check
        version: MCP version string

    Returns:
        True if feature is supported, False otherwise
    """
    # Input validation (safeguard)
    if not feature or not isinstance(feature, str):
        return False
    if not version or not _validate_version_string(version):
        return True

    # Feature availability matrix (bounded lookup - safeguard)
    # Maps feature names to list of versions that support them.
    # To add a new feature, add an entry with the feature name as key
    # and a list of version strings where it's available.
    feature_matrix = {
        "basic_tools": ["1.0"],  # Core MCP tool support
        "streaming": ["1.0"],     # Streaming response support
    }

    supported_versions = feature_matrix.get(feature, [])
    return version in supported_versions


def x_supports_feature__mutmut_10(feature: str, version: str) -> bool:
    """Check if a feature is supported in the given MCP version.

    Safeguards:
    - Input validation on feature and version
    - Bounded feature lookup
    - Defensive default behavior

    Args:
        feature: Feature name to check
        version: MCP version string

    Returns:
        True if feature is supported, False otherwise
    """
    # Input validation (safeguard)
    if not feature or not isinstance(feature, str):
        return False
    if not version or not _validate_version_string(version):
        return False

    # Feature availability matrix (bounded lookup - safeguard)
    # Maps feature names to list of versions that support them.
    # To add a new feature, add an entry with the feature name as key
    # and a list of version strings where it's available.
    feature_matrix = None

    supported_versions = feature_matrix.get(feature, [])
    return version in supported_versions


def x_supports_feature__mutmut_11(feature: str, version: str) -> bool:
    """Check if a feature is supported in the given MCP version.

    Safeguards:
    - Input validation on feature and version
    - Bounded feature lookup
    - Defensive default behavior

    Args:
        feature: Feature name to check
        version: MCP version string

    Returns:
        True if feature is supported, False otherwise
    """
    # Input validation (safeguard)
    if not feature or not isinstance(feature, str):
        return False
    if not version or not _validate_version_string(version):
        return False

    # Feature availability matrix (bounded lookup - safeguard)
    # Maps feature names to list of versions that support them.
    # To add a new feature, add an entry with the feature name as key
    # and a list of version strings where it's available.
    feature_matrix = {
        "XXbasic_toolsXX": ["1.0"],  # Core MCP tool support
        "streaming": ["1.0"],     # Streaming response support
    }

    supported_versions = feature_matrix.get(feature, [])
    return version in supported_versions


def x_supports_feature__mutmut_12(feature: str, version: str) -> bool:
    """Check if a feature is supported in the given MCP version.

    Safeguards:
    - Input validation on feature and version
    - Bounded feature lookup
    - Defensive default behavior

    Args:
        feature: Feature name to check
        version: MCP version string

    Returns:
        True if feature is supported, False otherwise
    """
    # Input validation (safeguard)
    if not feature or not isinstance(feature, str):
        return False
    if not version or not _validate_version_string(version):
        return False

    # Feature availability matrix (bounded lookup - safeguard)
    # Maps feature names to list of versions that support them.
    # To add a new feature, add an entry with the feature name as key
    # and a list of version strings where it's available.
    feature_matrix = {
        "BASIC_TOOLS": ["1.0"],  # Core MCP tool support
        "streaming": ["1.0"],     # Streaming response support
    }

    supported_versions = feature_matrix.get(feature, [])
    return version in supported_versions


def x_supports_feature__mutmut_13(feature: str, version: str) -> bool:
    """Check if a feature is supported in the given MCP version.

    Safeguards:
    - Input validation on feature and version
    - Bounded feature lookup
    - Defensive default behavior

    Args:
        feature: Feature name to check
        version: MCP version string

    Returns:
        True if feature is supported, False otherwise
    """
    # Input validation (safeguard)
    if not feature or not isinstance(feature, str):
        return False
    if not version or not _validate_version_string(version):
        return False

    # Feature availability matrix (bounded lookup - safeguard)
    # Maps feature names to list of versions that support them.
    # To add a new feature, add an entry with the feature name as key
    # and a list of version strings where it's available.
    feature_matrix = {
        "basic_tools": ["XX1.0XX"],  # Core MCP tool support
        "streaming": ["1.0"],     # Streaming response support
    }

    supported_versions = feature_matrix.get(feature, [])
    return version in supported_versions


def x_supports_feature__mutmut_14(feature: str, version: str) -> bool:
    """Check if a feature is supported in the given MCP version.

    Safeguards:
    - Input validation on feature and version
    - Bounded feature lookup
    - Defensive default behavior

    Args:
        feature: Feature name to check
        version: MCP version string

    Returns:
        True if feature is supported, False otherwise
    """
    # Input validation (safeguard)
    if not feature or not isinstance(feature, str):
        return False
    if not version or not _validate_version_string(version):
        return False

    # Feature availability matrix (bounded lookup - safeguard)
    # Maps feature names to list of versions that support them.
    # To add a new feature, add an entry with the feature name as key
    # and a list of version strings where it's available.
    feature_matrix = {
        "basic_tools": ["1.0"],  # Core MCP tool support
        "XXstreamingXX": ["1.0"],     # Streaming response support
    }

    supported_versions = feature_matrix.get(feature, [])
    return version in supported_versions


def x_supports_feature__mutmut_15(feature: str, version: str) -> bool:
    """Check if a feature is supported in the given MCP version.

    Safeguards:
    - Input validation on feature and version
    - Bounded feature lookup
    - Defensive default behavior

    Args:
        feature: Feature name to check
        version: MCP version string

    Returns:
        True if feature is supported, False otherwise
    """
    # Input validation (safeguard)
    if not feature or not isinstance(feature, str):
        return False
    if not version or not _validate_version_string(version):
        return False

    # Feature availability matrix (bounded lookup - safeguard)
    # Maps feature names to list of versions that support them.
    # To add a new feature, add an entry with the feature name as key
    # and a list of version strings where it's available.
    feature_matrix = {
        "basic_tools": ["1.0"],  # Core MCP tool support
        "STREAMING": ["1.0"],     # Streaming response support
    }

    supported_versions = feature_matrix.get(feature, [])
    return version in supported_versions


def x_supports_feature__mutmut_16(feature: str, version: str) -> bool:
    """Check if a feature is supported in the given MCP version.

    Safeguards:
    - Input validation on feature and version
    - Bounded feature lookup
    - Defensive default behavior

    Args:
        feature: Feature name to check
        version: MCP version string

    Returns:
        True if feature is supported, False otherwise
    """
    # Input validation (safeguard)
    if not feature or not isinstance(feature, str):
        return False
    if not version or not _validate_version_string(version):
        return False

    # Feature availability matrix (bounded lookup - safeguard)
    # Maps feature names to list of versions that support them.
    # To add a new feature, add an entry with the feature name as key
    # and a list of version strings where it's available.
    feature_matrix = {
        "basic_tools": ["1.0"],  # Core MCP tool support
        "streaming": ["XX1.0XX"],     # Streaming response support
    }

    supported_versions = feature_matrix.get(feature, [])
    return version in supported_versions


def x_supports_feature__mutmut_17(feature: str, version: str) -> bool:
    """Check if a feature is supported in the given MCP version.

    Safeguards:
    - Input validation on feature and version
    - Bounded feature lookup
    - Defensive default behavior

    Args:
        feature: Feature name to check
        version: MCP version string

    Returns:
        True if feature is supported, False otherwise
    """
    # Input validation (safeguard)
    if not feature or not isinstance(feature, str):
        return False
    if not version or not _validate_version_string(version):
        return False

    # Feature availability matrix (bounded lookup - safeguard)
    # Maps feature names to list of versions that support them.
    # To add a new feature, add an entry with the feature name as key
    # and a list of version strings where it's available.
    feature_matrix = {
        "basic_tools": ["1.0"],  # Core MCP tool support
        "streaming": ["1.0"],     # Streaming response support
    }

    supported_versions = None
    return version in supported_versions


def x_supports_feature__mutmut_18(feature: str, version: str) -> bool:
    """Check if a feature is supported in the given MCP version.

    Safeguards:
    - Input validation on feature and version
    - Bounded feature lookup
    - Defensive default behavior

    Args:
        feature: Feature name to check
        version: MCP version string

    Returns:
        True if feature is supported, False otherwise
    """
    # Input validation (safeguard)
    if not feature or not isinstance(feature, str):
        return False
    if not version or not _validate_version_string(version):
        return False

    # Feature availability matrix (bounded lookup - safeguard)
    # Maps feature names to list of versions that support them.
    # To add a new feature, add an entry with the feature name as key
    # and a list of version strings where it's available.
    feature_matrix = {
        "basic_tools": ["1.0"],  # Core MCP tool support
        "streaming": ["1.0"],     # Streaming response support
    }

    supported_versions = feature_matrix.get(None, [])
    return version in supported_versions


def x_supports_feature__mutmut_19(feature: str, version: str) -> bool:
    """Check if a feature is supported in the given MCP version.

    Safeguards:
    - Input validation on feature and version
    - Bounded feature lookup
    - Defensive default behavior

    Args:
        feature: Feature name to check
        version: MCP version string

    Returns:
        True if feature is supported, False otherwise
    """
    # Input validation (safeguard)
    if not feature or not isinstance(feature, str):
        return False
    if not version or not _validate_version_string(version):
        return False

    # Feature availability matrix (bounded lookup - safeguard)
    # Maps feature names to list of versions that support them.
    # To add a new feature, add an entry with the feature name as key
    # and a list of version strings where it's available.
    feature_matrix = {
        "basic_tools": ["1.0"],  # Core MCP tool support
        "streaming": ["1.0"],     # Streaming response support
    }

    supported_versions = feature_matrix.get(feature, None)
    return version in supported_versions


def x_supports_feature__mutmut_20(feature: str, version: str) -> bool:
    """Check if a feature is supported in the given MCP version.

    Safeguards:
    - Input validation on feature and version
    - Bounded feature lookup
    - Defensive default behavior

    Args:
        feature: Feature name to check
        version: MCP version string

    Returns:
        True if feature is supported, False otherwise
    """
    # Input validation (safeguard)
    if not feature or not isinstance(feature, str):
        return False
    if not version or not _validate_version_string(version):
        return False

    # Feature availability matrix (bounded lookup - safeguard)
    # Maps feature names to list of versions that support them.
    # To add a new feature, add an entry with the feature name as key
    # and a list of version strings where it's available.
    feature_matrix = {
        "basic_tools": ["1.0"],  # Core MCP tool support
        "streaming": ["1.0"],     # Streaming response support
    }

    supported_versions = feature_matrix.get([])
    return version in supported_versions


def x_supports_feature__mutmut_21(feature: str, version: str) -> bool:
    """Check if a feature is supported in the given MCP version.

    Safeguards:
    - Input validation on feature and version
    - Bounded feature lookup
    - Defensive default behavior

    Args:
        feature: Feature name to check
        version: MCP version string

    Returns:
        True if feature is supported, False otherwise
    """
    # Input validation (safeguard)
    if not feature or not isinstance(feature, str):
        return False
    if not version or not _validate_version_string(version):
        return False

    # Feature availability matrix (bounded lookup - safeguard)
    # Maps feature names to list of versions that support them.
    # To add a new feature, add an entry with the feature name as key
    # and a list of version strings where it's available.
    feature_matrix = {
        "basic_tools": ["1.0"],  # Core MCP tool support
        "streaming": ["1.0"],     # Streaming response support
    }

    supported_versions = feature_matrix.get(feature, )
    return version in supported_versions


def x_supports_feature__mutmut_22(feature: str, version: str) -> bool:
    """Check if a feature is supported in the given MCP version.

    Safeguards:
    - Input validation on feature and version
    - Bounded feature lookup
    - Defensive default behavior

    Args:
        feature: Feature name to check
        version: MCP version string

    Returns:
        True if feature is supported, False otherwise
    """
    # Input validation (safeguard)
    if not feature or not isinstance(feature, str):
        return False
    if not version or not _validate_version_string(version):
        return False

    # Feature availability matrix (bounded lookup - safeguard)
    # Maps feature names to list of versions that support them.
    # To add a new feature, add an entry with the feature name as key
    # and a list of version strings where it's available.
    feature_matrix = {
        "basic_tools": ["1.0"],  # Core MCP tool support
        "streaming": ["1.0"],     # Streaming response support
    }

    supported_versions = feature_matrix.get(feature, [])
    return version not in supported_versions

x_supports_feature__mutmut_mutants : ClassVar[MutantDict] = {
'x_supports_feature__mutmut_1': x_supports_feature__mutmut_1, 
    'x_supports_feature__mutmut_2': x_supports_feature__mutmut_2, 
    'x_supports_feature__mutmut_3': x_supports_feature__mutmut_3, 
    'x_supports_feature__mutmut_4': x_supports_feature__mutmut_4, 
    'x_supports_feature__mutmut_5': x_supports_feature__mutmut_5, 
    'x_supports_feature__mutmut_6': x_supports_feature__mutmut_6, 
    'x_supports_feature__mutmut_7': x_supports_feature__mutmut_7, 
    'x_supports_feature__mutmut_8': x_supports_feature__mutmut_8, 
    'x_supports_feature__mutmut_9': x_supports_feature__mutmut_9, 
    'x_supports_feature__mutmut_10': x_supports_feature__mutmut_10, 
    'x_supports_feature__mutmut_11': x_supports_feature__mutmut_11, 
    'x_supports_feature__mutmut_12': x_supports_feature__mutmut_12, 
    'x_supports_feature__mutmut_13': x_supports_feature__mutmut_13, 
    'x_supports_feature__mutmut_14': x_supports_feature__mutmut_14, 
    'x_supports_feature__mutmut_15': x_supports_feature__mutmut_15, 
    'x_supports_feature__mutmut_16': x_supports_feature__mutmut_16, 
    'x_supports_feature__mutmut_17': x_supports_feature__mutmut_17, 
    'x_supports_feature__mutmut_18': x_supports_feature__mutmut_18, 
    'x_supports_feature__mutmut_19': x_supports_feature__mutmut_19, 
    'x_supports_feature__mutmut_20': x_supports_feature__mutmut_20, 
    'x_supports_feature__mutmut_21': x_supports_feature__mutmut_21, 
    'x_supports_feature__mutmut_22': x_supports_feature__mutmut_22
}

def supports_feature(*args, **kwargs):
    result = _mutmut_trampoline(x_supports_feature__mutmut_orig, x_supports_feature__mutmut_mutants, args, kwargs)
    return result 

supports_feature.__signature__ = _mutmut_signature(x_supports_feature__mutmut_orig)
x_supports_feature__mutmut_orig.__name__ = 'x_supports_feature'


def x_validate_version__mutmut_orig(version: str) -> bool:
    """Validate that a version string is valid and supported.

    Safeguard: Provides external validation entry point with full
    input sanitization and bounds checking.

    Args:
        version: Version string to validate

    Returns:
        True if version is valid and supported
    """
    if not _validate_version_string(version):
        return False
    return version in MCP_VERSIONS


def x_validate_version__mutmut_1(version: str) -> bool:
    """Validate that a version string is valid and supported.

    Safeguard: Provides external validation entry point with full
    input sanitization and bounds checking.

    Args:
        version: Version string to validate

    Returns:
        True if version is valid and supported
    """
    if _validate_version_string(version):
        return False
    return version in MCP_VERSIONS


def x_validate_version__mutmut_2(version: str) -> bool:
    """Validate that a version string is valid and supported.

    Safeguard: Provides external validation entry point with full
    input sanitization and bounds checking.

    Args:
        version: Version string to validate

    Returns:
        True if version is valid and supported
    """
    if not _validate_version_string(None):
        return False
    return version in MCP_VERSIONS


def x_validate_version__mutmut_3(version: str) -> bool:
    """Validate that a version string is valid and supported.

    Safeguard: Provides external validation entry point with full
    input sanitization and bounds checking.

    Args:
        version: Version string to validate

    Returns:
        True if version is valid and supported
    """
    if not _validate_version_string(version):
        return True
    return version in MCP_VERSIONS


def x_validate_version__mutmut_4(version: str) -> bool:
    """Validate that a version string is valid and supported.

    Safeguard: Provides external validation entry point with full
    input sanitization and bounds checking.

    Args:
        version: Version string to validate

    Returns:
        True if version is valid and supported
    """
    if not _validate_version_string(version):
        return False
    return version not in MCP_VERSIONS

x_validate_version__mutmut_mutants : ClassVar[MutantDict] = {
'x_validate_version__mutmut_1': x_validate_version__mutmut_1, 
    'x_validate_version__mutmut_2': x_validate_version__mutmut_2, 
    'x_validate_version__mutmut_3': x_validate_version__mutmut_3, 
    'x_validate_version__mutmut_4': x_validate_version__mutmut_4
}

def validate_version(*args, **kwargs):
    result = _mutmut_trampoline(x_validate_version__mutmut_orig, x_validate_version__mutmut_mutants, args, kwargs)
    return result 

validate_version.__signature__ = _mutmut_signature(x_validate_version__mutmut_orig)
x_validate_version__mutmut_orig.__name__ = 'x_validate_version'


__all__ = [
    "MAX_VERSIONS_COUNT",
    "MCP_VERSIONS",
    "negotiate_version",
    "supports_feature",
    "validate_version",
]
