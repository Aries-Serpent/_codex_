"""
Test Github Client

Test module for github client.
"""

import os

import pytest

from codex_bridge.github_client import list_branches


@pytest.mark.network
@pytest.mark.skipif(
    os.getenv("CI") == "true" and not os.getenv("GITHUB_TOKEN"),
    reason="Network test requires GITHUB_TOKEN in CI",
)
def test_list_branches_returns_list():
    """Test list_branches returns a list (requires network and GitHub API access)."""
    out = list_branches()
    assert isinstance(out, list)
