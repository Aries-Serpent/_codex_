"""FastAPI endpoints for fetching GitHub Actions logs.

Provides REST API endpoints to fetch logs from GitHub Actions workflows, jobs, and check runs.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Optional

from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/github", tags=["github"])


class CheckRunStatus(str, Enum):
    """Valid check run status values."""

    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class CheckRunLogsResponse(BaseModel):
    """Response model for check run logs."""

    check_run_id: int
    owner: str
    repo: str
    check_run_name: str
    check_run_status: str
    check_run_conclusion: Optional[str]
    check_run_url: str
    logs: str


class JobLogsResponse(BaseModel):
    """Response model for job logs."""

    job_id: int
    owner: str
    repo: str
    logs: str


class CheckRunInfo(BaseModel):
    """Check run information."""

    id: int
    name: str
    status: CheckRunStatus
    conclusion: Optional[str]
    html_url: str
    started_at: Optional[str]
    completed_at: Optional[str]


class CheckRunsListResponse(BaseModel):
    """Response model for listing check runs."""

    owner: str
    repo: str
    ref: str
    total_count: int
    check_runs: list[CheckRunInfo]


def _get_github_client():
    """Get GitHub client instance."""
    try:
        from services.github.client import GitHubClientSync

        return GitHubClientSync()
    except ImportError as e:
        type(e).__name__
        logger.error("GitHub client not available: <ERROR_TYPE>")
        raise HTTPException(
            status_code=500,
            detail=f"GitHub client not available: {e}. Ensure httpx and pydantic are installed.",
        ) from e


@router.get(
    "/check-runs/{check_run_id}/logs",
    response_model=CheckRunLogsResponse,
    summary="Get check run logs",
    description="Fetch logs from a GitHub Actions check run by ID.",
)
async def get_check_run_logs(
    check_run_id: int = Path(..., description="Check run ID"),
    owner: str = Query(..., description="Repository owner (e.g., 'Aries-Serpent')"),
    repo: str = Query(..., description="Repository name (e.g., '_codex_')"),
):
    """Fetch logs from a GitHub Actions check run.

    Args:
        check_run_id: The check run ID to fetch logs for.
        owner: Repository owner.
        repo: Repository name.

    Returns:
        CheckRunLogsResponse containing check run details and logs.

    Raises:
        HTTPException: If check run not found or logs unavailable.
    """
    try:
        client = _get_github_client()

        # Fetch check run details
        check_run = client.get_check_run(owner, repo, check_run_id)

        # Fetch logs
        logs = client.get_check_run_logs(owner, repo, check_run_id)

        return CheckRunLogsResponse(
            check_run_id=check_run_id,
            owner=owner,
            repo=repo,
            check_run_name=check_run.name,
            check_run_status=check_run.status,
            check_run_conclusion=check_run.conclusion,
            check_run_url=check_run.html_url,
            logs=logs,
        )

    except (ConnectionError, TimeoutError) as e:
        type(e).__name__
        logger.error("Failed to fetch check run logs: <ERROR_TYPE>", exc_info=True)

        # Convert GitHub client exceptions to HTTP exceptions
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e)) from e
        if "rate limit" in str(e).lower():
            raise HTTPException(status_code=429, detail=str(e)) from e
        if "authentication" in str(e).lower():
            raise HTTPException(status_code=401, detail=str(e)) from e
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/jobs/{job_id}/logs",
    response_model=JobLogsResponse,
    summary="Get job logs",
    description="Fetch logs from a GitHub Actions workflow job by ID.",
)
async def get_job_logs(
    job_id: int = Path(..., description="Job ID"),
    owner: str = Query(..., description="Repository owner (e.g., 'Aries-Serpent')"),
    repo: str = Query(..., description="Repository name (e.g., '_codex_')"),
):
    """Fetch logs from a GitHub Actions workflow job.

    Args:
        job_id: The job ID to fetch logs for.
        owner: Repository owner.
        repo: Repository name.

    Returns:
        JobLogsResponse containing job logs.

    Raises:
        HTTPException: If job not found or logs unavailable.
    """
    try:
        client = _get_github_client()

        # Fetch logs
        logs = client.get_job_logs(owner, repo, job_id)

        return JobLogsResponse(
            job_id=job_id,
            owner=owner,
            repo=repo,
            logs=logs,
        )

    except (ConnectionError, TimeoutError) as e:
        type(e).__name__
        logger.error("Failed to fetch job logs: <ERROR_TYPE>", exc_info=True)

        # Convert GitHub client exceptions to HTTP exceptions
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e)) from e
        if "rate limit" in str(e).lower():
            raise HTTPException(status_code=429, detail=str(e)) from e
        if "authentication" in str(e).lower():
            raise HTTPException(status_code=401, detail=str(e)) from e
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/check-runs",
    response_model=CheckRunsListResponse,
    summary="List check runs",
    description="List check runs for a git reference (commit, branch, or tag).",
)
async def list_check_runs(
    owner: str = Query(..., description="Repository owner (e.g., 'Aries-Serpent')"),
    repo: str = Query(..., description="Repository name (e.g., '_codex_')"),
    ref: str = Query(..., description="Git reference (commit SHA, branch, or tag)"),
    status: Optional[CheckRunStatus] = Query(
        None, description="Filter by status (queued, in_progress, completed)"
    ),
    check_name: Optional[str] = Query(None, description="Filter by check run name"),
):
    """List check runs for a git reference.

    Args:
        owner: Repository owner.
        repo: Repository name.
        ref: Git reference (commit SHA, branch, or tag).
        status: Optional status filter.
        check_name: Optional check name filter.

    Returns:
        CheckRunsListResponse containing list of check runs.

    Raises:
        HTTPException: If request fails.
    """
    try:
        client = _get_github_client()

        # Use the locally-defined CheckRunStatus enum (avoids P19 shadow import).
        status_enum = CheckRunStatus(status) if status else None

        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            owner, repo, ref, check_name=check_name, status=status_enum
        )

        # Convert to response format
        check_runs_info = [
            CheckRunInfo(
                id=run.id,
                name=run.name,
                status=run.status,
                conclusion=run.conclusion,
                html_url=run.html_url,
                started_at=run.started_at.isoformat() if run.started_at else None,
                completed_at=run.completed_at.isoformat() if run.completed_at else None,
            )
            for run in check_runs
        ]

        return CheckRunsListResponse(
            owner=owner,
            repo=repo,
            ref=ref,
            total_count=len(check_runs_info),
            check_runs=check_runs_info,
        )

    except (ConnectionError, TimeoutError) as e:
        type(e).__name__
        logger.error("Failed to list check runs: <ERROR_TYPE>", exc_info=True)

        # Convert GitHub client exceptions to HTTP exceptions
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e)) from e
        if "rate limit" in str(e).lower():
            raise HTTPException(status_code=429, detail=str(e)) from e
        if "authentication" in str(e).lower():
            raise HTTPException(status_code=401, detail=str(e)) from e
        raise HTTPException(status_code=500, detail=str(e)) from e
