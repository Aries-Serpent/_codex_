"""Smoke tests for :mod:`mcp.versioning`."""

from __future__ import annotations

import pytest

from mcp.versioning import MCP_VERSIONS, negotiate_version


def test_negotiate_version_picks_highest():
    assert negotiate_version(["0.9", "1.0"]) == MCP_VERSIONS[0]


def test_negotiate_version_no_overlap():
    with pytest.raises(ValueError):
        negotiate_version(["0.5", "0.6"])


def test_negotiate_requires_client_versions():
    with pytest.raises(ValueError):
        negotiate_version([])
