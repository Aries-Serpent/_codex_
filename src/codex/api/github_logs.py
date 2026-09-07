"""FastAPI and compatibility routing for GitHub Actions log access."""

from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/github", tags=["github"])


class CheckRunLogsResponse(BaseModel):
    """Response payload for a check-run log fetch."""

    check_run_id: int
    owner: str
    repo: str
    check_run_name: str
    check_run_status: str
    check_run_conclusion: Optional[str]
    check_run_url: str
    logs: str


class JobLogsResponse(BaseModel):
    """Response payload for fetching workflow job logs."""

    job_id: int
    owner: str
    repo: str
    logs: str


class CheckRunInfo(BaseModel):
    """Check run summary returned by list endpoints."""

    id: int
    name: str
    status: str
    conclusion: Optional[str]
    html_url: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class CheckRunsListResponse(BaseModel):
    """List of check runs for a ref."""

    owner: str
    repo: str
    ref: str
    total_count: int
    check_runs: list[CheckRunInfo]


def _get_github_client():
    """Return the canonical GitHub client with a compatibility fallback."""
    try:
        from src.services.github.client import GitHubClientSync
    except ImportError:
        from services.github.client import GitHubClientSync

    return GitHubClientSync()


@router.get(
    "/check-runs/{check_run_id}/logs",
    response_model=CheckRunLogsResponse,
    summary="Get check run logs",
)
async def get_check_run_logs(
    check_run_id: int = Path(..., description="Check run ID"),
    owner: str = Query(..., description="Repository owner"),
    repo: str = Query(..., description="Repository name"),
):
    """Fetch logs from a GitHub Actions check run by ID."""
    try:
        client = _get_github_client()
        check_run = client.get_check_run(owner, repo, check_run_id)
        logs = client.get_check_run_logs(owner, repo, check_run_id)
        return {
            "check_run_id": check_run_id,
            "owner": owner,
            "repo": repo,
            "check_run_name": check_run.name,
            "check_run_status": str(check_run.status),
            "check_run_conclusion": getattr(check_run, "conclusion", None),
            "check_run_url": check_run.html_url,
            "logs": logs,
        }
    except Exception as exc:  # pragma: no cover - compatibility layer
        logger.exception("Failed to fetch check run logs")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get(
    "/jobs/{job_id}/logs",
    response_model=JobLogsResponse,
    summary="Get job logs",
)
async def get_job_logs(
    job_id: int = Path(..., description="Job ID"),
    owner: str = Query(..., description="Repository owner"),
    repo: str = Query(..., description="Repository name"),
):
    """Fetch logs from a GitHub Actions workflow job by ID."""
    try:
        client = _get_github_client()
        logs = client.get_job_logs(owner, repo, job_id)
        return {
            "job_id": job_id,
            "owner": owner,
            "repo": repo,
            "logs": logs,
        }
    except Exception as exc:  # pragma: no cover - compatibility layer
        logger.exception("Failed to fetch job logs")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/check-runs", response_model=CheckRunsListResponse, summary="List check runs")
async def list_check_runs(
    owner: str = Query(..., description="Repository owner"),
    repo: str = Query(..., description="Repository name"),
    ref: str = Query(..., description="Git reference"),
    status: Optional[str] = Query(None, description="Check run status"),
    check_name: Optional[str] = Query(None, description="Check run name"),
):
    """List check runs for a git reference."""
    try:
        client = _get_github_client()
        check_runs = client.list_check_runs_for_ref(
            owner,
            repo,
            ref,
            check_name=check_name,
            status=status,
        )
        return {
            "owner": owner,
            "repo": repo,
            "ref": ref,
            "total_count": len(check_runs),
            "check_runs": [
                {
                    "id": run.id,
                    "name": run.name,
                    "status": str(run.status),
                    "conclusion": getattr(run, "conclusion", None),
                    "html_url": run.html_url,
                    "started_at": run.started_at.isoformat() if run.started_at else None,
                    "completed_at": run.completed_at.isoformat() if run.completed_at else None,
                }
                for run in check_runs
            ],
        }
    except Exception as exc:  # pragma: no cover - compatibility layer
        logger.exception("Failed to list check runs")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


class GitHubLogsAPI:
    """Minimal compatibility GitHub Actions log client."""

    def __init__(self, token: Optional[str] = None, **kwargs: Any):
        if token is None or token == "":
            raise ValueError("token is required")
        self.token = token
        self._kwargs = kwargs

    def get_logs(self, *, owner: Optional[str] = None, repo: Optional[str] = None, run_id: Optional[int] = None, **kwargs: Any) -> str:
        if repo is None or repo == "":
            raise ValueError("repo is required")
        if run_id is None:
            raise TypeError("run_id is required")
        if run_id < 0:
            raise ValueError("run_id must be non-negative")
        client = _get_github_client()
        return client.get_check_run_logs(owner or "", repo, run_id)

    async def fetch_logs(self, *, owner: Optional[str] = None, repo: Optional[str] = None, run_id: Optional[int] = None, **kwargs: Any) -> str:
        if repo is None or repo == "":
            raise ValueError("repo is required")
        if run_id is None:
            raise TypeError("run_id is required")
        if run_id < 0:
            raise ValueError("run_id must be non-negative")
        return self.get_logs(owner=owner, repo=repo, run_id=run_id, **kwargs)


__all__ = ["GitHubLogsAPI", "router"]

import sys

if __name__.startswith("src."):
    sys.modules.setdefault("codex.api.github_logs", sys.modules[__name__])
else:
    sys.modules.setdefault("src.codex.api.github_logs", sys.modules[__name__])
