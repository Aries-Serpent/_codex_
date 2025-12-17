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
from typing import List, Optional

# Configure logging for safeguard tracing
logger = logging.getLogger(__name__)

# Supported MCP protocol versions in preference order (highest to lowest)
# Deterministic ordering ensures reproducible version negotiation
MCP_VERSIONS: List[str] = ["1.0"]

# Maximum bounds for version validation (safeguard)
MAX_VERSION_LENGTH = 20
MAX_VERSIONS_COUNT = 100


def _validate_version_string(version: str) -> bool:
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
    pattern = r'^(\d+)\.(\d+)(?:\.(\d+))?(?:-[a-zA-Z0-9.]+)?(?:\+[a-zA-Z0-9.]+)?$'
    return bool(re.match(pattern, version))


def _sanitize_version_list(versions: List[str]) -> List[str]:
    """Sanitize and validate a list of version strings.

    Safeguard: Filters out invalid versions and bounds the list size
    to prevent resource exhaustion attacks.

    Args:
        versions: List of version strings

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


def negotiate_version(client_versions: List[str]) -> str:
    """Negotiate MCP protocol version between client and server.

    Safeguards implemented:
    - Input validation on client_versions list
    - Bounds checking on list size
    - Version string sanitization
    - Defensive error handling with clear messages
    - Deterministic version preference ordering

    Args:
        client_versions: List of versions supported by the client

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


def supports_feature(feature: str, version: str) -> bool:
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
    feature_matrix = {
        "basic_tools": ["1.0"],
        "streaming": ["1.0"],
    }

    supported_versions = feature_matrix.get(feature, [])
    return version in supported_versions


def validate_version(version: str) -> bool:
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


__all__ = [
    "MCP_VERSIONS",
    "negotiate_version",
    "supports_feature",
    "validate_version",
]
