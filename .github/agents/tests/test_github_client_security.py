import sys
from pathlib import Path
from urllib.parse import urlunsplit

import pytest

AGENTS_DIR = Path(__file__).resolve().parents[1]
if str(AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(AGENTS_DIR))

from codex_reviewer.github_client import GitHubAPIClient, GitHubConfig  # noqa: E402


@pytest.fixture
def client() -> GitHubAPIClient:
    return GitHubAPIClient(GitHubConfig(token="test-token", base_url="https://api.github.com"))


def test_build_api_url_accepts_valid_repo(client):
    url = client._build_github_api_url("owner/repo", "pulls/42/reviews")
    assert url == "https://api.github.com/repos/owner/repo/pulls/42/reviews"


def test_build_api_url_rejects_malformed_repo(client):
    with pytest.raises(ValueError):
        client._build_github_api_url("https://evil.example/repo", "pulls/42")

    with pytest.raises(ValueError):
        client._build_github_api_url("owner/../repo", "pulls/42")


def test_validated_request_url_rejects_non_github_hosts(client):
    with pytest.raises(ValueError, match="host mismatch"):
        client._validated_request_url("https://github.com/repos/owner/repo/pulls/42")

    creds_url = urlunsplit(("https", "user:pass@api.github.com", "/repos/owner/repo/pulls/42", "", ""))
    with pytest.raises(ValueError, match="embedded credentials"):
        client._validated_request_url(creds_url)

    with pytest.raises(ValueError, match="query parameters"):
        client._validated_request_url("https://api.github.com/repos/owner/repo/pulls/42?foo=bar")
