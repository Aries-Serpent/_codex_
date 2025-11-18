"""MCP version negotiation helpers with checksum safeguards."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .errors import OfflineOnly, ValidationError
from .safeguards import compute_secure_checksum


MCP_VERSIONS: List[str] = ["1.0"]


@dataclass(frozen=True)
class VersionMetadata:
    """Metadata describing version compatibility and safeguards."""

    version: str
    status: str
    offline_supported: bool
    checksum: str


VERSION_COMPATIBILITY_MATRIX: Dict[str, VersionMetadata] = {
    version: VersionMetadata(
        version=version,
        status="stable",
        offline_supported=True,
        checksum=compute_secure_checksum(f"{version}:stable"),
    )
    for version in MCP_VERSIONS
}


def negotiate_version(
    client_versions: List[str],
    *,
    offline: bool = False,
    required_checksum: str | None = None,
) -> str:
    """Return a negotiated version ensuring checksum and offline invariants."""

    supported = set(MCP_VERSIONS)
    for version in sorted(client_versions, reverse=True):
        if version not in supported:
            continue
        metadata = VERSION_COMPATIBILITY_MATRIX[version]
        if offline and not metadata.offline_supported:
            raise OfflineOnly(
                f"Version {version} is not approved for offline execution",
                context={"offline": True},
            )
        if required_checksum and metadata.checksum != required_checksum:
            raise ValidationError(
                "Version checksum mismatch", context={"expected": required_checksum}
            )
        return version
    raise ValidationError("No compatible MCP version found")


def version_matrix_checksum() -> str:
    """Return a checksum representing the entire compatibility matrix."""

    payload = "|".join(
        f"{meta.version}:{meta.status}:{meta.offline_supported}:{meta.checksum}"
        for meta in VERSION_COMPATIBILITY_MATRIX.values()
    )
    return compute_secure_checksum(payload)
