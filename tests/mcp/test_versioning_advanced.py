import sys
from pathlib import Path

import pytest

repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

from mcp.errors import OfflineOnly, ValidationError
from mcp.versioning import (
    MCP_VERSIONS,
    VERSION_COMPATIBILITY_MATRIX,
    VersionMetadata,
    negotiate_version,
    version_matrix_checksum,
)


def test_versioning_returns_supported_version():
    chosen = negotiate_version(["1.0", "0.9"])
    assert chosen in MCP_VERSIONS


def test_versioning_prefers_highest_version():
    chosen = negotiate_version(["0.1", MCP_VERSIONS[0]])
    assert chosen == MCP_VERSIONS[0]


def test_versioning_raises_when_no_common_version():
    with pytest.raises(ValidationError):
        negotiate_version(["2.0"])


def test_versioning_offline_requires_supported_flag(monkeypatch):
    meta = VERSION_COMPATIBILITY_MATRIX[MCP_VERSIONS[0]]
    replacement = VersionMetadata(
        version=meta.version,
        status=meta.status,
        offline_supported=False,
        checksum=meta.checksum,
    )
    monkeypatch.setitem(VERSION_COMPATIBILITY_MATRIX, meta.version, replacement)
    with pytest.raises(OfflineOnly):
        negotiate_version([meta.version], offline=True)


def test_versioning_offline_negotiation_succeeds_with_supported_flag():
    chosen = negotiate_version([MCP_VERSIONS[0]], offline=True)
    assert chosen == MCP_VERSIONS[0]


def test_versioning_checksum_matches_matrix():
    checksum = version_matrix_checksum()
    assert isinstance(checksum, str)


def test_versioning_metadata_contains_checksum():
    meta = VERSION_COMPATIBILITY_MATRIX[MCP_VERSIONS[0]]
    assert len(meta.checksum) == 64


def test_versioning_metadata_offline_supported_flag():
    meta = VERSION_COMPATIBILITY_MATRIX[MCP_VERSIONS[0]]
    assert meta.offline_supported is True


def test_versioning_checksum_validation_passes():
    meta = VERSION_COMPATIBILITY_MATRIX[MCP_VERSIONS[0]]
    assert negotiate_version([meta.version], required_checksum=meta.checksum) == meta.version


def test_versioning_checksum_validation_fails_on_mismatch():
    with pytest.raises(ValidationError):
        negotiate_version([MCP_VERSIONS[0]], required_checksum="deadbeef")


def test_versioning_handles_duplicate_versions():
    chosen = negotiate_version([MCP_VERSIONS[0], MCP_VERSIONS[0]])
    assert chosen == MCP_VERSIONS[0]


def test_versioning_matrix_checksum_is_deterministic():
    assert version_matrix_checksum() == version_matrix_checksum()


def test_versioning_metadata_status_is_stable():
    meta = VERSION_COMPATIBILITY_MATRIX[MCP_VERSIONS[0]]
    assert meta.status == "stable"


def test_versioning_matrix_contains_all_versions():
    assert set(VERSION_COMPATIBILITY_MATRIX.keys()) == set(MCP_VERSIONS)


def test_versioning_rejects_empty_client_list():
    with pytest.raises(ValidationError):
        negotiate_version([])


def test_versioning_accepts_exact_match():
    assert negotiate_version([MCP_VERSIONS[0]]) == MCP_VERSIONS[0]
