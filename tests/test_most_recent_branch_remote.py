"""
Test Most Recent Branch Remote

Test module for most recent branch remote.
"""

import os

from codex_bridge.github_client import most_recent_branch


def test_most_recent_branch_returns_string():
    os.environ.setdefault("CODEX_GH_OWNER", "Aries-Serpent")
    os.environ.setdefault("CODEX_GH_REPO", "_codex_")
    name = most_recent_branch()
    assert isinstance(name, str)
    assert name, "name is not valid"
