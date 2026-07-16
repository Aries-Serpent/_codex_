"""GitHub service exceptions module."""

class GitHubServiceException(Exception):
    """Base exception for GitHub service errors."""
    pass

class GitHubAuthException(GitHubServiceException):
    """GitHub authentication error."""
    pass

class AuthenticationError(GitHubAuthException):
    """GitHub authentication error (alias)."""
    pass

class GitHubAPIException(GitHubServiceException):
    """GitHub API error."""
    pass

class GitHubRateLimitException(GitHubServiceException):
    """GitHub rate limit error."""
    pass

class RateLimitError(GitHubRateLimitException):
    """GitHub rate limit error (alias)."""
    pass

class NotFoundError(GitHubServiceException):
    """GitHub not found error."""
    pass

__all__ = [
    "GitHubServiceException",
    "GitHubAuthException",
    "AuthenticationError",
    "GitHubAPIException",
    "GitHubRateLimitException",
    "RateLimitError",
    "NotFoundError",
]
