"""GitHub API Client implementation.

Provides async-friendly wrapper around GitHub REST API for workflow operations.
Includes retry logic, rate limit handling, and typed responses.
"""

import asyncio
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from .exceptions import (
    AuthenticationError,
    GitHubAPIError,
    NotFoundError,
    RateLimitError,
    WorkflowTriggerError,
)
from .types import (
    ArtifactInfo,
    CheckRun,
    CheckRunStatus,
    ListArtifactsResponse,
    ListCheckRunsResponse,
    ListWorkflowJobsResponse,
    ListWorkflowRunsResponse,
    RateLimitInfo,
    RunStatus,
    WorkflowInfo,
    WorkflowJob,
    WorkflowRun,
)

logger = logging.getLogger(__name__)


class GitHubClient:
    """GitHub API client for workflow operations.

    Provides typed, async-friendly methods for:
    - Listing and triggering workflows
    - Monitoring workflow runs
    - Retrieving job logs and artifacts
    - Rate limit handling with exponential backoff

    Example:
        ```python
        client = GitHubClient()

        # list workflows
        workflows = await client.list_workflows("owner", "repo")

        # Trigger a workflow
        run_id = await client.trigger_workflow(
            "owner", "repo", "ci.yml",
            ref="main",
            inputs={"environment": "staging"}
        )

        # Monitor status
        run = await client.get_workflow_run("owner", "repo", run_id)
        print(f"Status: {run.status}, Conclusion: {run.conclusion}")
        ```
    """

    DEFAULT_BASE_URL = "https://api.github.com"
    DEFAULT_TIMEOUT = 30.0
    MAX_RETRIES = 3
    RETRY_BACKOFF_BASE = 2.0

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ):
        """Initialize GitHub client.

        Args:
            token: GitHub personal access token or app token.
                   Defaults to GITHUB_TOKEN environment variable.
            base_url: GitHub API base URL.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts.
        """
        self.token = token if token is not None else os.environ.get("GITHUB_TOKEN", "")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._rate_limit: Optional[RateLimitInfo] = None

    def _get_headers(self) -> dict[str, str]:
        """Get request headers."""
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _create_client(self) -> httpx.AsyncClient:
        """Create async HTTP client."""
        return httpx.AsyncClient(
            base_url=self.base_url,
            headers=self._get_headers(),
            timeout=self.timeout,
        )

    def _update_rate_limit(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    async def _request(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(response.headers.get("x-ratelimit-reset", 0))
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE**retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(method, path, json, params, retry_count + 1)
                raise GitHubAPIError(f"Request failed: {e}") from e

    async def _get(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make GET request."""
        response = await self._request("GET", path, params=params)
        return response.json()

    async def _post(
        self,
        path: str,
        json: Optional[dict[str, Any]] = None,
    ) -> Optional[dict[str, Any]]:
        """Make POST request."""
        response = await self._request("POST", path, json=json)
        if response.status_code == 204:
            return None
        return response.json()

    # =========================================================================
    # Workflow Operations
    # =========================================================================

    async def list_workflows(
        self,
        owner: str,
        repo: str,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowInfo]:
        """list repository workflows.

        Args:
            owner: Repository owner.
            repo: Repository name.
            per_page: Results per page (max 100).
            page: Page number.

        Returns:
            list of workflow info objects.
        """
        data = await self._get(
            f"/repos/{owner}/{repo}/actions/workflows",
            params={"per_page": per_page, "page": page},
        )
        return [WorkflowInfo(**w) for w in data.get("workflows", [])]

    async def get_workflow(
        self,
        owner: str,
        repo: str,
        workflow_id: int | str,
    ) -> WorkflowInfo:
        """Get workflow by ID or filename.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename (e.g., "ci.yml").

        Returns:
            Workflow info object.
        """
        data = await self._get(f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}")
        return WorkflowInfo(**data)

    async def trigger_workflow(
        self,
        owner: str,
        repo: str,
        workflow_id: int | str,
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json={"ref": ref, "inputs": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(owner, repo, workflow_id, per_page=1)
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            type(e).__name__
            logger.debug("GitHubAPIError: <ERROR_TYPE>")
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                reason=e.message,
                status_code=e.status_code,
            ) from e

    # =========================================================================
    # Workflow Run Operations
    # =========================================================================

    async def list_workflow_runs(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[int | str] = None,
        branch: Optional[str] = None,
        event: Optional[str] = None,
        status: Optional[RunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowRun]:
        """list workflow runs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Filter by workflow ID/filename.
            branch: Filter by branch.
            event: Filter by event type.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if branch:
            params["branch"] = branch
        if event:
            params["event"] = event
        if status:
            params["status"] = status.value if hasattr(status, "value") else str(status)

        if workflow_id:
            path = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            path = f"/repos/{owner}/{repo}/actions/runs"

        data = await self._get(path, params=params)
        response = ListWorkflowRunsResponse(**data)
        return response.workflow_runs

    async def get_workflow_run(
        self,
        owner: str,
        repo: str,
        run_id: int,
    ) -> WorkflowRun:
        """Get workflow run by ID.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.

        Returns:
            Workflow run object.
        """
        data = await self._get(f"/repos/{owner}/{repo}/actions/runs/{run_id}")
        return WorkflowRun(**data)

    async def wait_for_run(
        self,
        owner: str,
        repo: str,
        run_id: int,
        poll_interval: float = 10.0,
        timeout: float = 3600.0,
    ) -> WorkflowRun:
        """Wait for workflow run to complete.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            poll_interval: Seconds between status checks.
            timeout: Maximum wait time in seconds.

        Returns:
            Completed workflow run.

        Raises:
            TimeoutError: If run doesn't complete within timeout.
        """
        start_time = time.time()
        while True:
            run = await self.get_workflow_run(owner, repo, run_id)
            if run.is_completed:
                return run

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(f"Workflow run {run_id} did not complete within {timeout}s")

            await asyncio.sleep(poll_interval)

    async def cancel_workflow_run(
        self,
        owner: str,
        repo: str,
        run_id: int,
    ) -> bool:
        """Cancel a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.

        Returns:
            True if cancellation was accepted.
        """
        try:
            await self._post(f"/repos/{owner}/{repo}/actions/runs/{run_id}/cancel")
            return True
        except GitHubAPIError as e:
            type(e).__name__
            logger.debug("GitHubAPIError: <ERROR_TYPE>")
            logger.warning("GitHubAPIError: <ERROR_TYPE>", exc_info=True)
            return False

    async def rerun_workflow(
        self,
        owner: str,
        repo: str,
        run_id: int,
        enable_debug: bool = False,
    ) -> bool:
        """Re-run a workflow.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            enable_debug: Enable debug logging.

        Returns:
            True if re-run was triggered.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/runs/{run_id}/rerun",
                json={"enable_debug_logging": enable_debug},
            )
            return True
        except GitHubAPIError as e:
            type(e).__name__
            logger.debug("GitHubAPIError: <ERROR_TYPE>")
            logger.warning("GitHubAPIError: <ERROR_TYPE>", exc_info=True)
            return False

    # =========================================================================
    # Job Operations
    # =========================================================================

    async def list_workflow_jobs(
        self,
        owner: str,
        repo: str,
        run_id: int,
        filter_status: Optional[str] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowJob]:
        """list jobs for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            filter_status: Filter by status (latest, all).
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow jobs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if filter_status:
            params["filter"] = filter_status

        data = await self._get(
            f"/repos/{owner}/{repo}/actions/runs/{run_id}/jobs",
            params=params,
        )
        response = ListWorkflowJobsResponse(**data)
        return response.jobs

    async def get_job_logs(
        self,
        owner: str,
        repo: str,
        job_id: int,
    ) -> str:
        """Get job logs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            job_id: Job ID.

        Returns:
            Job logs as string.
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/jobs/{job_id}/logs",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("job logs", str(job_id))

            return response.text

    # =========================================================================
    # Artifact Operations
    # =========================================================================

    async def list_run_artifacts(
        self,
        owner: str,
        repo: str,
        run_id: int,
        per_page: int = 30,
        page: int = 1,
    ) -> list[ArtifactInfo]:
        """list artifacts for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of artifact info objects.
        """
        data = await self._get(
            f"/repos/{owner}/{repo}/actions/runs/{run_id}/artifacts",
            params={"per_page": per_page, "page": page},
        )
        response = ListArtifactsResponse(**data)
        return response.artifacts

    async def download_artifact(
        self,
        owner: str,
        repo: str,
        artifact_id: int,
    ) -> bytes:
        """Download an artifact.

        Args:
            owner: Repository owner.
            repo: Repository name.
            artifact_id: Artifact ID.

        Returns:
            Artifact content as bytes (zip archive).
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("artifact", str(artifact_id))

            if response.status_code >= 400:
                raise GitHubAPIError(
                    message="Failed to download artifact",
                    status_code=response.status_code,
                )

            return response.content

    # =========================================================================
    # Check Run Operations
    # =========================================================================

    async def get_check_run(
        self,
        owner: str,
        repo: str,
        check_run_id: int,
    ) -> CheckRun:
        """Get check run by ID.

        Args:
            owner: Repository owner.
            repo: Repository name.
            check_run_id: Check run ID.

        Returns:
            Check run object.
        """
        data = await self._get(f"/repos/{owner}/{repo}/check-runs/{check_run_id}")
        return CheckRun(**data)

    async def list_check_runs_for_ref(
        self,
        owner: str,
        repo: str,
        ref: str,
        check_name: Optional[str] = None,
        status: Optional[CheckRunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[CheckRun]:
        """List check runs for a git reference.

        Args:
            owner: Repository owner.
            repo: Repository name.
            ref: Git reference (commit SHA, branch, or tag).
            check_name: Filter by check run name.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            List of check runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if check_name:
            params["check_name"] = check_name
        if status:
            params["status"] = status.value if hasattr(status, "value") else str(status)

        data = await self._get(
            f"/repos/{owner}/{repo}/commits/{ref}/check-runs",
            params=params,
        )
        response = ListCheckRunsResponse(**data)
        return response.check_runs

    async def get_check_run_logs(
        self,
        owner: str,
        repo: str,
        check_run_id: int,
    ) -> str:
        """Get check run logs.

        Note: Check runs are associated with GitHub Actions jobs.
        This method fetches the logs for the underlying job.

        Args:
            owner: Repository owner.
            repo: Repository name.
            check_run_id: Check run ID.

        Returns:
            Check run logs as string.

        Raises:
            NotFoundError: If check run or logs not found.
            GitHubAPIError: On other API errors.
        """
        # Check runs don't have a direct logs endpoint, but if it's a GitHub Actions
        # check run, we need to find the associated job
        # For now, we'll try to get logs via the Actions job endpoint
        # The check_run_id is often the same as the job_id for Actions
        try:
            return await self.get_job_logs(owner, repo, check_run_id)
        except NotFoundError as err:
            # If direct job lookup fails, we need to find the job via workflow runs
            # This is a limitation of the GitHub API - check runs don't directly expose logs
            raise NotFoundError(
                "check run logs",
                f"{check_run_id} (note: logs may only be available via associated workflow job)",
            ) from err

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def get_rate_limit(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(core.get("reset", 0), tz=timezone.utc),
            used=core.get("used", 0),
        )

    @property
    def rate_limit(self) -> Optional[RateLimitInfo]:
        """Get cached rate limit info from last request."""
        return self._rate_limit


# Synchronous wrapper for convenience
class GitHubClientSync:
    """Synchronous wrapper for GitHubClient.

    Use when async is not available or not needed.
    """

    def __init__(self, *args: Any, **kwargs: Any):
        self._async_client = GitHubClient(*args, **kwargs)

    def _run(self, coro: Any) -> Any:
        """Run coroutine synchronously."""
        return asyncio.get_event_loop().run_until_complete(coro)

    def list_workflows(self, *args: Any, **kwargs: Any) -> list[WorkflowInfo]:
        return self._run(self._async_client.list_workflows(*args, **kwargs))

    def get_workflow(self, *args: Any, **kwargs: Any) -> WorkflowInfo:
        return self._run(self._async_client.get_workflow(*args, **kwargs))

    def trigger_workflow(self, *args: Any, **kwargs: Any) -> Optional[int]:
        return self._run(self._async_client.trigger_workflow(*args, **kwargs))

    def list_workflow_runs(self, *args: Any, **kwargs: Any) -> list[WorkflowRun]:
        return self._run(self._async_client.list_workflow_runs(*args, **kwargs))

    def get_workflow_run(self, *args: Any, **kwargs: Any) -> WorkflowRun:
        return self._run(self._async_client.get_workflow_run(*args, **kwargs))

    def list_workflow_jobs(self, *args: Any, **kwargs: Any) -> list[WorkflowJob]:
        return self._run(self._async_client.list_workflow_jobs(*args, **kwargs))

    def get_job_logs(self, *args: Any, **kwargs: Any) -> str:
        return self._run(self._async_client.get_job_logs(*args, **kwargs))

    def list_run_artifacts(self, *args: Any, **kwargs: Any) -> list[ArtifactInfo]:
        return self._run(self._async_client.list_run_artifacts(*args, **kwargs))

    def download_artifact(self, *args: Any, **kwargs: Any) -> bytes:
        return self._run(self._async_client.download_artifact(*args, **kwargs))

    def get_check_run(self, *args: Any, **kwargs: Any) -> CheckRun:
        return self._run(self._async_client.get_check_run(*args, **kwargs))

    def list_check_runs_for_ref(self, *args: Any, **kwargs: Any) -> list[CheckRun]:
        return self._run(self._async_client.list_check_runs_for_ref(*args, **kwargs))

    def get_check_run_logs(self, *args: Any, **kwargs: Any) -> str:
        return self._run(self._async_client.get_check_run_logs(*args, **kwargs))

    def get_rate_limit(self, *args: Any, **kwargs: Any) -> RateLimitInfo:
        return self._run(self._async_client.get_rate_limit(*args, **kwargs))
