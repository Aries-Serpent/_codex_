from typing import List


MCP_VERSIONS: List[str] = ["1.0"]
"""
List of MCP protocol versions this server can support.
"""


def negotiate_version(client_versions: List[str]) -> str:
    """
    Given a list of version strings supported by the client, return a chosen version string that is supported by both.
    If no common version, raise an exception (VersionMismatch).
    """
    # Use numeric comparison if versions are numbers, else lexicographic
    supported = set(MCP_VERSIONS)
    for ver in sorted(client_versions, reverse=True):
        if ver in supported:
            return ver
    raise Exception("No compatible MCP version found")
