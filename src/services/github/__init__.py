"""GitHub API Client for Copilot Workflow Agent.

This module provides a typed, async-friendly wrapper around the GitHub REST API
for workflow operations including triggering, monitoring, and artifact retrieval.
"""

import logging

from .client import GitHubClient

logger = logging.getLogger(__name__)
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
