"""
Test Github Client

Test module for github client.
"""

import os

import pytest

import codex_bridge
from codex_bridge.github_client import list_branches


def test_bridge_package_uses_repo_local_implementation():
    """Bridge re-exports must stay pinned to the in-repo module, not a shadowed package."""
    assert codex_bridge.list_branches.__module__ == "codex_bridge.github_client"


@pytest.mark.network
@pytest.mark.skipif(
    os.getenv("CI") == "true" and not os.getenv("GITHUB_TOKEN"),
    reason="Network test requires GITHUB_TOKEN in CI",
)
def test_list_branches_returns_list():
    """Test list_branches returns a list (requires network and GitHub API access)."""
    out = list_branches()
    assert isinstance(out, list)
