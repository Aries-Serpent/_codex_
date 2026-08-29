"""MCP tool for fetching GitHub Actions logs.

Provides Model Context Protocol (MCP) tool interface for fetching logs
from GitHub Actions workflows, jobs, and check runs.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class FetchCheckRunLogsInput(BaseModel):
    """Input schema for fetch_check_run_logs tool."""

    owner: str = Field(..., description="Repository owner (e.g., 'Aries-Serpent')")
    repo: str = Field(..., description="Repository name (e.g., '_codex_')")
    check_run_id: int = Field(..., description="Check run ID to fetch logs for")


class FetchJobLogsInput(BaseModel):
    """Input schema for fetch_job_logs tool."""

    owner: str = Field(..., description="Repository owner (e.g., 'Aries-Serpent')")
    repo: str = Field(..., description="Repository name (e.g., '_codex_')")
    job_id: int = Field(..., description="Job ID to fetch logs for")


class ListCheckRunsInput(BaseModel):
    """Input schema for list_check_runs tool."""

    owner: str = Field(..., description="Repository owner (e.g., 'Aries-Serpent')")
    repo: str = Field(..., description="Repository name (e.g., '_codex_')")
    ref: str = Field(..., description="Git reference (commit SHA, branch, or tag)")
    status: Optional[str] = Field(
        None, description="Filter by status (queued, in_progress, completed)"
    )
    check_name: Optional[str] = Field(None, description="Filter by check run name")


def _get_github_client():
    """Get GitHub client instance."""
    from services.github.client import GitHubClientSync

    return GitHubClientSync()


def fetch_check_run_logs(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.

    This MCP tool fetches logs from a specific GitHub Actions check run by ID.

    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID

    Returns:
        Dictionary containing check run details and logs.

    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)

        # Get client
        client = _get_github_client()

        # Fetch check run details
        check_run = client.get_check_run(input_data.owner, input_data.repo, input_data.check_run_id)

        # Fetch logs
        logs = client.get_check_run_logs(input_data.owner, input_data.repo, input_data.check_run_id)

        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": (
                    check_run.completed_at.isoformat() if check_run.completed_at else None
                ),
            },
            "logs": logs,
        }

    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        logger.error("Failed to fetch check run logs: <ERROR_TYPE>", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def fetch_job_logs(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.

    This MCP tool fetches logs from a specific GitHub Actions job by ID.

    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID

    Returns:
        Dictionary containing job logs.

    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)

        # Get client
        client = _get_github_client()

        # Fetch logs
        logs = client.get_job_logs(input_data.owner, input_data.repo, input_data.job_id)

        return {
            "success": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }

    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        logger.error("Failed to fetch job logs: <ERROR_TYPE>", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def list_check_runs(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.

    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).

    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter

    Returns:
        Dictionary containing list of check runs.

    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",  # pragma: allowlist secret
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)

        # Get client
        client = _get_github_client()

        # Fetch check runs (pass status as string; client accepts both str and enum)
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=input_data.status,
        )

        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]

        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }

    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        logger.error("Failed to list check runs: <ERROR_TYPE>", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


# MCP tool registry metadata
GITHUB_LOGS_TOOLS = {
    "fetch_check_run_logs": {
        "function": fetch_check_run_logs,
        "schema": FetchCheckRunLogsInput.schema(),
        "description": "Fetch logs from a GitHub Actions check run by ID",
        "name": "fetch_check_run_logs",
    },
    "fetch_job_logs": {
        "function": fetch_job_logs,
        "schema": FetchJobLogsInput.schema(),
        "description": "Fetch logs from a GitHub Actions workflow job by ID",
        "name": "fetch_job_logs",
    },
    "list_check_runs": {
        "function": list_check_runs,
        "schema": ListCheckRunsInput.schema(),
        "description": "List check runs for a git reference (commit, branch, or tag)",
        "name": "list_check_runs",
    },
}
