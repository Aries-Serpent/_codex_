"""
Exceptions Module

This module provides functionality for exceptions.

Usage:
    from github.exceptions import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

import logging

logger = logging.getLogger(__name__)

from typing import Optional  # noqa: E402


class GitHubAPIError(Exception):
    """Base exception for GitHub API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class RateLimitError(GitHubAPIError):
    """Raised when GitHub API rate limit is exceeded."""

    def __init__(
        self,
        message: str = "GitHub API rate limit exceeded",
        reset_at: Optional[int] = None,
        remaining: int = 0,
    ):
        super().__init__(message, status_code=403)
        self.reset_at = reset_at
        self.remaining = remaining


class AuthenticationError(GitHubAPIError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "GitHub authentication failed"):
        super().__init__(message, status_code=401)


class NotFoundError(GitHubAPIError):
    """Raised when a resource is not found."""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            f"{resource} not found: {identifier}",
            status_code=404,
        )
        self.resource = resource
        self.identifier = identifier


class WorkflowTriggerError(GitHubAPIError):
    """Raised when workflow trigger fails."""

    def __init__(
        self,
        workflow: str,
        reason: str,
        status_code: Optional[int] = None,
    ):
        super().__init__(
            f"Failed to trigger workflow '{workflow}': {reason}",
            status_code=status_code,
        )
        self.workflow = workflow
        self.reason = reason


class ValidationError(GitHubAPIError):
    """Raised when request validation fails."""

    def __init__(self, message: str, errors: Optional[list] = None):
        super().__init__(message, status_code=422)
        self.errors = errors or []
