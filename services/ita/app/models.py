"""Pydantic models used by the Internal Tools API."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


class _StrictBaseModel(BaseModel):
    """Base model that forbids unexpected fields."""

    model_config = {
        "extra": "forbid",
        "populate_by_name": True,
    }


class HealthResponse(_StrictBaseModel):
    status: str = Field(default="ok", description="Human friendly status string")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeSearchRequest(_StrictBaseModel):
    query: str = Field(..., min_length=1, description="Full-text query the agent provides")
    top_k: int = Field(5, ge=1, le=20, description="Maximum number of snippets to return")


class KnowledgeSearchResult(_StrictBaseModel):
    snippet: str = Field(..., description="Relevant excerpt to show the agent")
    source: str = Field(..., description="Source of the snippet (URL or document identifier)")
    score: float = Field(..., ge=0, le=1, description="Normalized relevance score (0-1)")


class KnowledgeSearchResponse(_StrictBaseModel):
    results: List[KnowledgeSearchResult]


class RepoHygieneRequest(_StrictBaseModel):
    diff: str = Field(..., description="Unified diff that should be scanned")
    checks: Optional[List[str]] = Field(
        default=None,
        description="Subset of checks to run (lint, format, secrets, license)",
    )

    @field_validator("checks", mode="before")
    @classmethod
    def _ensure_unique_checks(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        if value is None:
            return value
        normalized = [item.lower() for item in value]
        if len(normalized) != len(set(normalized)):
            raise ValueError("Duplicate check entries are not allowed")
        return normalized


class RepoHygieneIssue(_StrictBaseModel):
    type: str = Field(..., description="Short identifier for the issue (e.g. lint)")
    path: str = Field(..., description="File path associated with the issue")
    message: str = Field(..., description="Human-readable description of the issue")
    severity: str = Field(..., pattern="^(info|warn|error)$", description="Severity level")


class RepoHygieneResponse(_StrictBaseModel):
    issues: List[RepoHygieneIssue]


class TestsRunRequest(_StrictBaseModel):
    targets: List[str] = Field(..., min_length=1, description="Test targets to execute")
    timeout_s: int = Field(300, ge=30, le=3600, description="Timeout for the run in seconds")


class TestFailure(_StrictBaseModel):
    name: str
    message: str


class TestsRunSummary(_StrictBaseModel):
    total: int
    passed: int
    failed: int
    duration_s: float


class TestsRunResponse(_StrictBaseModel):
    summary: TestsRunSummary
    failures: List[TestFailure] = Field(default_factory=list)


class GitCreatePullRequestBody(_StrictBaseModel):
    repo: str = Field(..., min_length=1, description="Repository slug (org/repo)")
    title: str
    body: str
    base: str
    head: str
    labels: Optional[List[str]] = None


class GitCreatePullRequestResponse(_StrictBaseModel):
    simulated: bool = Field(..., description="True if the request was simulated (dry run)")
    pr_url: Optional[HttpUrl] = Field(
        default=None,
        description="URL of the created Pull Request when confirm=true",
    )
    message: str = Field(..., description="Status message for the agent")


class RequestContext(_StrictBaseModel):
    request_id: str
    api_key_hash: Optional[str] = None
