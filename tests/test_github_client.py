"""
Test Github Client

Test module for github client.
"""

import os
from unittest.mock import Mock

import pytest
import requests

import codex_bridge
from codex_bridge import github_client
from codex_bridge.github_client import list_branches


def test_bridge_package_uses_repo_local_implementation():
    """Bridge re-exports must stay pinned to the in-repo module, not a shadowed package."""
    assert codex_bridge.list_branches.__module__ == "codex_bridge.github_client", "__module__ is not valid"


@pytest.mark.parametrize(
    "url",
    [
        "https://localhost/",
        "https://127.0.0.1/",
        "https://example.com/api.github.com",
        "https://api.github.com.example.com/",
        "https://{}:{}@api.github.com/user".format("user", "pass"),
        "https://api.github.com/\r\ninjected",
    ],
)
def test_gh_get_rejects_unsafe_urls_before_transport(monkeypatch, url):
    transport = Mock()
    monkeypatch.setattr(github_client.requests, "get", transport)
    with pytest.raises(ValueError):
        github_client.gh_get(url)
    transport.assert_not_called()


@pytest.mark.parametrize("status_code", [301, 302, 307, 308])
def test_gh_get_does_not_follow_redirects(monkeypatch, status_code):
    response = Mock(status_code=status_code, headers={"Location": "https://127.0.0.1/"})
    transport = Mock(return_value=response)
    monkeypatch.setattr(github_client.requests, "get", transport)
    with pytest.raises(requests.HTTPError, match="redirects are not permitted"):
        github_client.gh_get("https://api.github.com/user")
    assert transport.call_count == 1
    assert transport.call_args.kwargs["allow_redirects"] is False
    response.json.assert_not_called()


def test_get_text_does_not_follow_raw_content_redirects(monkeypatch):
    response = Mock(status_code=302, headers={"Location": "https://127.0.0.1/"})
    transport = Mock(return_value=response)
    metadata = Mock(return_value={"encoding": "base64", "content": "aGVsbG8="})
    monkeypatch.setattr(github_client.requests, "get", transport)
    monkeypatch.setattr(github_client, "gh_get", metadata)
    assert github_client.get_text("owner", "repo", "main", "README.md") == "hello"
    assert transport.call_count == 1
    assert transport.call_args.kwargs["allow_redirects"] is False
    metadata.assert_called_once()


@pytest.mark.network
@pytest.mark.skipif(
    os.getenv("CI") == "true" and not os.getenv("GITHUB_TOKEN"),
    reason="Network test requires GITHUB_TOKEN in CI",
)
def test_list_branches_returns_list():
    """Test list_branches returns a list (requires network and GitHub API access)."""
    out = list_branches()
    assert isinstance(out, list)
