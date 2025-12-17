"""GitHub API Client for Copilot Workflow Agent.

This module provides a typed, async-friendly wrapper around the GitHub REST API
for workflow operations including triggering, monitoring, and artifact retrieval.
"""

from .client import GitHubClient
from .types import (
    WorkflowInfo,
    WorkflowRun,
    WorkflowJob,
    RunStatus,
    RunConclusion,
    ArtifactInfo,
)
from .exceptions import (
    GitHubAPIError,
    RateLimitError,
    AuthenticationError,
    NotFoundError,
    WorkflowTriggerError,
)

__all__ = [
    "GitHubClient",
    "WorkflowInfo",
    "WorkflowRun",
    "WorkflowJob",
    "RunStatus",
    "RunConclusion",
    "ArtifactInfo",
    "GitHubAPIError",
    "RateLimitError",
    "AuthenticationError",
    "NotFoundError",
    "WorkflowTriggerError",
]
