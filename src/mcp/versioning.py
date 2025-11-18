"""MCP protocol versioning support.

This module provides version negotiation for MCP (Model Context Protocol).
The server and client use this to agree on a compatible protocol version.
"""

from __future__ import annotations

from typing import List


# Supported MCP protocol versions in preference order (highest to lowest)
MCP_VERSIONS: List[str] = ["1.0"]


def negotiate_version(client_versions: List[str]) -> str:
    """Negotiate MCP protocol version between client and server.
    
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
    if not client_versions:
        raise ValueError("Client must provide at least one supported version")
    
    # Find the first version in our preference order that the client also supports
    for server_version in MCP_VERSIONS:
        if server_version in client_versions:
            return server_version
    
    # No common version found
    raise ValueError(
        f"No compatible MCP version found. "
        f"Server supports: {MCP_VERSIONS}, Client supports: {client_versions}"
    )


__all__ = ["MCP_VERSIONS", "negotiate_version"]
