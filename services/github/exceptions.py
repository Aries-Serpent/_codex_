"""GitHub service exceptions module."""

class GitHubServiceException(Exception):
    """Base exception for GitHub service errors."""
    pass

class GitHubAuthException(GitHubServiceException):
    """GitHub authentication error."""
    pass

class GitHubAPIException(GitHubServiceException):
    """GitHub API error."""
    pass

class GitHubRateLimitException(GitHubServiceException):
    """GitHub rate limit error."""
    pass

__all__ = [
    "GitHubServiceException",
    "GitHubAuthException",
    "GitHubAPIException",
    "GitHubRateLimitException",
]
