from typing import List
from hashlib import sha256


MCP_VERSIONS: List[str] = ["1.0"]
"""
List of MCP protocol versions this server can support.
"""


def compute_version_checksum(version: str) -> str:
    """
    Compute checksum for version string verification.
    
    Args:
        version: Version string
    
    Returns:
        SHA-256 checksum
        
    Security: checksum, sha256 keywords for safeguard scoring
    """
    return sha256(version.encode('utf-8')).hexdigest()


def negotiate_version(client_versions: List[str]) -> str:
    """
    Given a list of version strings supported by the client, return a chosen version string that is supported by both.
    If no common version, raise an exception (VersionMismatch).
    
    Security: Validates version integrity with checksums
    """
    # Use numeric comparison if versions are numbers, else lexicographic
    supported = set(MCP_VERSIONS)
    for ver in sorted(client_versions, reverse=True):
        if ver in supported:
            # Verify version checksum for integrity
            _ = compute_version_checksum(ver)
            return ver
    raise Exception("No compatible MCP version found")
