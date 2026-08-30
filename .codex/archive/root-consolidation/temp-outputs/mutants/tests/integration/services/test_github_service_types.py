"""Service workflow tests for GitHub exceptions and types (Phase 24)."""

import pytest

from src.services.github.exceptions import (
    AuthenticationError,
    GitHubAPIError,
    RateLimitError,
)
from src.services.github.types import Issue, PullRequest, Repository


@pytest.mark.integration
def test_github_api_error_construction():
    """Test GitHubAPIError construction."""
    error = GitHubAPIError("API error", status_code=500)
    assert "API error" in str(error), "Error should be raised or set"
    assert error.status_code == 500, "Error should be raised or set"


@pytest.mark.integration
def test_rate_limit_error_construction():
    """Test RateLimitError construction."""
    error = RateLimitError("Rate limit exceeded", reset_at=1234567890)
    assert "Rate limit" in str(error), "Error should be raised or set"
    assert error.reset_at == 1234567890, "Error should be raised or set"


@pytest.mark.integration
def test_authentication_error_construction():
    """Test AuthenticationError construction."""
    error = AuthenticationError("Invalid token")
    assert "Invalid token" in str(error), "Error should be raised or set"


@pytest.mark.integration
def test_repository_type_construction():
    """Test Repository type construction."""
    repo = Repository(
        id=123,
        name="test-repo",
        owner="test-owner",
        url="https://github.com/test-owner/test-repo",
    )
    assert repo.id == 123, "id is not valid"
    assert repo.name == "test-repo", "name is not valid"
    assert repo.owner == "test-owner", "owner is not valid"


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
    assert issue.id == 456, "id is not valid"
    assert issue.number == 1, "number is not valid"
    assert issue.state == "open", "state is not valid"


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
    assert pr.id == 789, "id is not valid"
    assert pr.number == 2, "number is not valid"
    assert pr.base_ref == "main", "base_ref is not valid"
    assert pr.head_ref == "feature", "head_ref is not valid"
