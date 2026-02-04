"""Service workflow tests for GitHub exceptions and types (Phase 24)."""

import pytest

from src.services.github.exceptions import (
    GitHubAPIError,
    RateLimitError,
    AuthenticationError,
)
from src.services.github.types import Repository, Issue, PullRequest


@pytest.mark.integration
def test_github_api_error_construction():
    """Test GitHubAPIError construction."""
    error = GitHubAPIError("API error", status_code=500)
    assert "API error" in str(error)
    assert error.status_code == 500


@pytest.mark.integration
def test_rate_limit_error_construction():
    """Test RateLimitError construction."""
    error = RateLimitError("Rate limit exceeded", reset_at=1234567890)
    assert "Rate limit" in str(error)
    assert error.reset_at == 1234567890


@pytest.mark.integration
def test_authentication_error_construction():
    """Test AuthenticationError construction."""
    error = AuthenticationError("Invalid token")
    assert "Invalid token" in str(error)


@pytest.mark.integration
def test_repository_type_construction():
    """Test Repository type construction."""
    repo = Repository(
        id=123,
        name="test-repo",
        owner="test-owner",
        url="https://github.com/test-owner/test-repo",
    )
    assert repo.id == 123
    assert repo.name == "test-repo"
    assert repo.owner == "test-owner"


@pytest.mark.integration
def test_issue_type_construction():
    """Test Issue type construction."""
    issue = Issue(
        id=456,
        number=1,
        title="Test issue",
        state="open",
        url="https://github.com/owner/repo/issues/1",
    )
    assert issue.id == 456
    assert issue.number == 1
    assert issue.state == "open"


@pytest.mark.integration
def test_pull_request_type_construction():
    """Test PullRequest type construction."""
    pr = PullRequest(
        id=789,
        number=2,
        title="Test PR",
        state="open",
        url="https://github.com/owner/repo/pull/2",
        base_ref="main",
        head_ref="feature",
    )
    assert pr.id == 789
    assert pr.number == 2
    assert pr.base_ref == "main"
    assert pr.head_ref == "feature"
