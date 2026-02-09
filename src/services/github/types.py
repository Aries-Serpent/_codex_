"""GitHub API type definitions using Pydantic."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class RunStatus(str, Enum):
    """Workflow run status."""

    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    WAITING = "waiting"
    REQUESTED = "requested"
    PENDING = "pending"


class RunConclusion(str, Enum):
    """Workflow run conclusion."""

    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"
    TIMED_OUT = "timed_out"
    ACTION_REQUIRED = "action_required"
    NEUTRAL = "neutral"
    STALE = "stale"


class WorkflowInfo(BaseModel):
    """Workflow metadata."""

    id: int
    name: str
    path: str
    state: str = "active"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    html_url: Optional[str] = None
    badge_url: Optional[str] = None

    class Config:
        extra = "ignore"


class WorkflowRun(BaseModel):
    """Workflow run information."""

    id: int
    name: Optional[str] = None
    workflow_id: int
    head_branch: Optional[str] = None
    head_sha: str
    run_number: int
    event: str
    status: RunStatus
    conclusion: Optional[RunConclusion] = None
    created_at: datetime
    updated_at: datetime
    html_url: str
    jobs_url: str
    logs_url: str
    artifacts_url: str
    run_attempt: int = 1

    class Config:
        extra = "ignore"

    @property
    def is_completed(self) -> bool:
        """Check if run is completed."""
        return self.status == RunStatus.COMPLETED

    @property
    def is_successful(self) -> bool:
        """Check if run completed successfully."""
        return self.is_completed and self.conclusion == RunConclusion.SUCCESS

    @property
    def is_failed(self) -> bool:
        """Check if run failed."""
        return self.is_completed and self.conclusion in (
            RunConclusion.FAILURE,
            RunConclusion.TIMED_OUT,
            RunConclusion.CANCELLED,
        )


class WorkflowJob(BaseModel):
    """Workflow job information."""

    id: int
    run_id: int
    name: str
    status: RunStatus
    conclusion: Optional[RunConclusion] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    html_url: str
    runner_name: Optional[str] = None
    runner_group_name: Optional[str] = None

    class Config:
        extra = "ignore"

    @property
    def is_completed(self) -> bool:
        """Check if job is completed."""
        return self.status == RunStatus.COMPLETED

    @property
    def duration_seconds(self) -> Optional[float]:
        """Get job duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class ArtifactInfo(BaseModel):
    """Workflow artifact information."""

    id: int
    name: str
    size_in_bytes: int
    archive_download_url: str
    expired: bool = False
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        extra = "ignore"

    @property
    def size_mb(self) -> float:
        """Get size in megabytes."""
        return self.size_in_bytes / (1024 * 1024)


class WorkflowDispatchInput(BaseModel):
    """Input for workflow_dispatch trigger."""

    ref: str = Field(..., description="Git reference (branch/tag) to run on")
    inputs: dict[str, Any] = Field(
        default_factory=dict,
        description="Workflow input parameters",
    )


class RateLimitInfo(BaseModel):
    """GitHub API rate limit information."""

    limit: int
    remaining: int
    reset: datetime
    used: int

    @property
    def is_exceeded(self) -> bool:
        """Check if rate limit is exceeded."""
        return self.remaining == 0

    @property
    def seconds_until_reset(self) -> float:
        """Get seconds until rate limit reset."""
        delta = self.reset - datetime.now(self.reset.tzinfo)
        return max(0, delta.total_seconds())


class ListWorkflowRunsResponse(BaseModel):
    """Response for list workflow runs."""

    total_count: int
    workflow_runs: list[WorkflowRun]

    class Config:
        extra = "ignore"


class ListWorkflowJobsResponse(BaseModel):
    """Response for list workflow jobs."""

    total_count: int
    jobs: list[WorkflowJob]

    class Config:
        extra = "ignore"


class ListArtifactsResponse(BaseModel):
    """Response for list artifacts."""

    total_count: int
    artifacts: list[ArtifactInfo]

    class Config:
        extra = "ignore"


class CheckRunStatus(str, Enum):
    """Check run status."""

    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    WAITING = "waiting"
    REQUESTED = "requested"
    PENDING = "pending"


class CheckRunConclusion(str, Enum):
    """Check run conclusion."""

    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"
    TIMED_OUT = "timed_out"
    ACTION_REQUIRED = "action_required"
    NEUTRAL = "neutral"
    STALE = "stale"


class CheckRun(BaseModel):
    """GitHub Check Run information."""

    id: int
    name: str
    head_sha: str
    status: CheckRunStatus
    conclusion: Optional[CheckRunConclusion] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    html_url: str
    details_url: Optional[str] = None
    external_id: Optional[str] = None
    check_suite_id: Optional[int] = None
    app: Optional[dict[str, Any]] = None

    class Config:
        extra = "ignore"

    @property
    def is_completed(self) -> bool:
        """Check if run is completed."""
        return self.status == CheckRunStatus.COMPLETED

    @property
    def is_successful(self) -> bool:
        """Check if run completed successfully."""
        return self.is_completed and self.conclusion == CheckRunConclusion.SUCCESS

    @property
    def is_failed(self) -> bool:
        """Check if run failed."""
        return self.is_completed and self.conclusion in (
            CheckRunConclusion.FAILURE,
            CheckRunConclusion.TIMED_OUT,
            CheckRunConclusion.CANCELLED,
        )


class ListCheckRunsResponse(BaseModel):
    """Response for list check runs."""

    total_count: int
    check_runs: list[CheckRun]

    class Config:
        extra = "ignore"


# ============================================================================
# Service Integration Types (Phase 24)
# ============================================================================


class Repository(BaseModel):
    """GitHub repository metadata for service integration."""

    id: int
    name: str
    owner: str
    url: str

    class Config:
        extra = "ignore"


class Issue(BaseModel):
    """GitHub issue metadata for service integration."""

    id: int
    number: int
    title: str
    state: str
    url: str

    class Config:
        extra = "ignore"


class PullRequest(BaseModel):
    """GitHub pull request metadata for service integration."""

    id: int
    number: int
    title: str
    state: str
    url: str
    base_ref: str
    head_ref: str

    class Config:
        extra = "ignore"
