"""GitHub API Client for Copilot Workflow Agent.

This module provides a typed, async-friendly wrapper around the GitHub REST API
for workflow operations including triggering, monitoring, and artifact retrieval.
"""

from .client import GitHubClient
from .exceptions import (
    AuthenticationError,
    GitHubAPIError,
    NotFoundError,
    RateLimitError,
    WorkflowTriggerError,
)
from .types import (
    ArtifactInfo,
    RunConclusion,
    RunStatus,
    WorkflowInfo,
    WorkflowJob,
    WorkflowRun,
)

__all__ = [
    "ArtifactInfo",
    "AuthenticationError",
    "GitHubAPIError",
    "GitHubClient",
    "NotFoundError",
    "RateLimitError",
    "RunConclusion",
    "RunStatus",
    "WorkflowInfo",
    "WorkflowJob",
    "WorkflowRun",
    "WorkflowTriggerError",
]
