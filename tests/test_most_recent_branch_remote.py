import os

from src.codex_bridge.github_client import most_recent_branch


def test_most_recent_branch_returns_string():
    os.environ.setdefault("CODEX_GH_OWNER", "Aries-Serpent")
    os.environ.setdefault("CODEX_GH_REPO", "_codex_")
    name = most_recent_branch()
    assert isinstance(name, str)
    assert name  # non-empty
