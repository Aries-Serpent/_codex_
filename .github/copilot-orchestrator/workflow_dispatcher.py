"""
GitHub Actions Workflow Dispatcher for Copilot Agent.

Enables GitHub Copilot to trigger, monitor, and orchestrate GitHub Actions workflows
while continuing other tasks in parallel.

Author: mbaetiong
Generated: 2025-12-21
"""

from __future__ import annotations

import asyncio
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

logger = logging.getLogger(__name__)


class WorkflowPriority(Enum):
    """Priority levels for workflow execution."""
    CRITICAL = 1  # Security, production fixes
    HIGH = 2      # Build failures, test runs
    MEDIUM = 3    # Code analysis, documentation
    LOW = 4       # Cleanup, optimization


@dataclass
class WorkflowJob:
    """Represents a triggered workflow job."""
    job_id: str
    workflow_name: str
    run_id: Optional[int] = None
    status: str = "pending"
    triggered_at: datetime = field(default_factory=datetime.now)
    estimated_duration: timedelta = timedelta(minutes=5)
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    artifacts: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class CopilotWorkflowOrchestrator:
    """Orchestrates GitHub Actions workflows for Copilot Agent."""

    def __init__(
        self,
        github_token: Optional[str] = None,
        repo_owner: Optional[str] = None,
        repo_name: Optional[str] = None,
    ):
        """Initialize workflow orchestrator.

        Args:
            github_token: GitHub API token
            repo_owner: Repository owner
            repo_name: Repository name
        """
        # GAP-041: Respect AGENT_KILL_SWITCH at startup
        if os.environ.get("AGENT_KILL_SWITCH", "0") == "1":
            raise RuntimeError(
                "AGENT_KILL_SWITCH=1 — CopilotWorkflowOrchestrator startup aborted"
            )
        # GAP-038: Fail fast when aiohttp is unavailable so callers get a clear error
        if not HAS_AIOHTTP:
            raise ImportError(
                "aiohttp is required for CopilotWorkflowOrchestrator. "
                "Install with: pip install 'aiohttp>=3.9'"
            )
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN", "")
        self.repo_owner = repo_owner or os.environ.get("GITHUB_REPOSITORY", "").split("/")[0]
        self.repo_name = repo_name or os.environ.get("GITHUB_REPOSITORY", "").split("/")[1] if "/" in os.environ.get("GITHUB_REPOSITORY", "") else ""
        self.active_jobs: dict[str, WorkflowJob] = {}
        self.monitoring_tasks: dict[str, asyncio.Task] = {}
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry."""
        if HAS_AIOHTTP:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"token {self.github_token}",
                    "Accept": "application/vnd.github.v3+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                }
            )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def trigger_workflow(
        self,
        workflow_name: str,
        inputs: Optional[dict[str, Any]] = None,
        priority: WorkflowPriority = WorkflowPriority.MEDIUM,
        wait_for_completion: bool = False,
        ref: str = "main",
    ) -> WorkflowJob:
        """Trigger a GitHub Actions workflow with tracking.

        Args:
            workflow_name: Name of the workflow file (e.g., 'ci.yml')
            inputs: Input parameters for the workflow
            priority: Priority level for the workflow
            wait_for_completion: Whether to wait for workflow to complete
            ref: Git ref to run workflow on

        Returns:
            WorkflowJob object with tracking information
        """
        if not HAS_AIOHTTP:
            logger.error("aiohttp not available - cannot trigger workflows")
            return self._create_error_job(workflow_name, "aiohttp not available")

        if not self.github_token:
            logger.error("No GitHub token - cannot trigger workflows")
            return self._create_error_job(workflow_name, "No GitHub token")

        # Create job tracking object
        job = WorkflowJob(
            job_id=str(uuid.uuid4()),
            workflow_name=workflow_name,
            inputs=inputs or {},
            metadata={
                "priority": priority.name,
                "wait_for_completion": wait_for_completion,
                "ref": ref,
            },
        )

        # Add to active jobs
        self.active_jobs[job.job_id] = job

        # Dispatch workflow
        dispatch_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/actions/workflows/{workflow_name}/dispatches"

        payload = {
            "ref": ref,
            "inputs": {
                **(inputs or {}),
                "copilot_job_id": job.job_id,
                "copilot_triggered": "true",
            },
        }

        try:
            async with self.session.post(dispatch_url, json=payload) as response:
                if response.status == 204:
                    job.status = "triggered"
                    logger.info(f"✅ Triggered workflow {workflow_name} (Job ID: {job.job_id})")

                    # Start monitoring task
                    monitor_task = asyncio.create_task(self._monitor_workflow(job))
                    self.monitoring_tasks[job.job_id] = monitor_task

                    if wait_for_completion:
                        await monitor_task
                else:
                    job.status = "failed_to_trigger"
                    error_data = await response.json() if response.status != 404 else {"message": "Workflow not found"}
                    job.metadata["error"] = error_data
                    logger.error(f"❌ Failed to trigger workflow {workflow_name}: {response.status} - {error_data}")
        except Exception as e:
            job.status = "failed_to_trigger"
            job.metadata["error"] = str(e)
            logger.error(f"❌ Exception triggering workflow {workflow_name}: {e}")

        return job

    def _create_error_job(self, workflow_name: str, error: str) -> WorkflowJob:
        """Create a job object representing an error state."""
        return WorkflowJob(
            job_id=str(uuid.uuid4()),
            workflow_name=workflow_name,
            status="error",
            metadata={"error": error},
        )

    async def _monitor_workflow(self, job: WorkflowJob):
        """Monitor workflow execution status."""
        # Initial delay to allow workflow to start
        await asyncio.sleep(5)

        runs_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/actions/runs"

        max_attempts = 180  # 15 minutes with 5s intervals
        attempt = 0

        while attempt < max_attempts:
            try:
                async with self.session.get(runs_url, params={"per_page": 10}) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Find our workflow run
                        for run in data.get("workflow_runs", []):
                            # Match by workflow name and recent trigger time
                            run_created = datetime.fromisoformat(run["created_at"].replace("Z", "+00:00"))
                            time_diff = abs((run_created - job.triggered_at).total_seconds())

                            if (run["name"] == job.workflow_name.replace(".yml", "").replace(".yaml", "") and
                                time_diff < 60):  # Within 60 seconds

                                job.run_id = run["id"]
                                job.status = run["status"]

                                # Update metadata
                                job.metadata.update({
                                    "run_url": run["html_url"],
                                    "head_sha": run["head_sha"],
                                    "conclusion": run.get("conclusion"),
                                    "updated_at": run["updated_at"],
                                })

                                # Check if completed
                                if run["status"] == "completed":
                                    logger.info(f"✅ Workflow {job.workflow_name} completed: {run.get('conclusion')}")
                                    job.metadata["completed_at"] = datetime.now().isoformat()
                                    job.metadata["duration"] = str(datetime.now() - job.triggered_at)
                                    return

                # Intelligent backoff
                await asyncio.sleep(self._calculate_backoff(attempt))
                attempt += 1

            except Exception as e:
                job.metadata["monitoring_error"] = str(e)
                logger.warning(f"Error monitoring workflow: {e}")
                await asyncio.sleep(5)
                attempt += 1

        # Timeout
        job.status = "monitoring_timeout"
        logger.warning(f"⏰ Monitoring timeout for workflow {job.workflow_name}")

        # Cleanup
        if job.job_id in self.monitoring_tasks:
            del self.monitoring_tasks[job.job_id]

    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate intelligent backoff interval."""
        if attempt < 10:
            return 2  # First 10 attempts: 2 seconds
        if attempt < 30:
            return 5  # Next 20 attempts: 5 seconds
        return 10  # Remaining: 10 seconds

    async def get_job_status(self, job_id: str) -> dict[str, Any]:
        """Get current status of a job."""
        if job_id not in self.active_jobs:
            return {"error": "Job not found"}

        job = self.active_jobs[job_id]

        return {
            "job_id": job.job_id,
            "workflow": job.workflow_name,
            "status": job.status,
            "run_id": job.run_id,
            "triggered_at": job.triggered_at.isoformat(),
            "progress": self._calculate_progress(job),
            "outputs": job.outputs,
            "artifacts": job.artifacts,
            "metadata": job.metadata,
        }

    def _calculate_progress(self, job: WorkflowJob) -> float:
        """Calculate estimated progress percentage."""
        if job.status == "completed":
            return 100.0
        if job.status in ("pending", "error", "failed_to_trigger"):
            return 0.0
        elapsed = datetime.now() - job.triggered_at
        progress = (elapsed.total_seconds() / job.estimated_duration.total_seconds()) * 100
        return min(progress, 95.0)  # Cap at 95% until actually complete

    def get_active_jobs(self) -> list[dict[str, Any]]:
        """Get list of all active jobs."""
        return [
            {
                "job_id": job.job_id,
                "workflow": job.workflow_name,
                "status": job.status,
                "progress": self._calculate_progress(job),
            }
            for job in self.active_jobs.values()
            if job.status not in ("completed", "error", "failed_to_trigger")
        ]


async def main():
    """Example usage of workflow orchestrator."""
    import sys

    logging.basicConfig(level=logging.INFO)

    orchestrator = CopilotWorkflowOrchestrator()

    if not orchestrator.github_token:
        print("❌ No GitHub token available. Set GITHUB_TOKEN environment variable.")
        sys.exit(1)

    print(f"🚀 Workflow Orchestrator for {orchestrator.repo_owner}/{orchestrator.repo_name}")
    print()

    async with orchestrator:
        # Example: Trigger a workflow
        job = await orchestrator.trigger_workflow(
            workflow_name="ci.yml",
            inputs={"test_suite": "unit"},
            priority=WorkflowPriority.HIGH,
            wait_for_completion=False,
        )

        print(f"Job ID: {job.job_id}")
        print(f"Status: {job.status}")

        # Monitor progress
        for i in range(10):
            await asyncio.sleep(2)
            status = await orchestrator.get_job_status(job.job_id)
            print(f"Progress: {status['progress']:.0f}% - Status: {status['status']}")
            if status['status'] == 'completed':
                break


if __name__ == "__main__":
    asyncio.run(main())
