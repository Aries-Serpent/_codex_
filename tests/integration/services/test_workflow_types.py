"""Service workflow tests for workflow metadata models (Phase 24)."""

import pytest

from src.services.workflow.types import WorkflowRun, WorkflowJob, WorkflowStep


@pytest.mark.integration
def test_workflow_run_construction():
    """Test WorkflowRun construction."""
    run = WorkflowRun(
        id=123,
        workflow_id=456,
        status="completed",
        conclusion="success",
        url="https://github.com/owner/repo/actions/runs/123",
    )
    assert run.id == 123
    assert run.workflow_id == 456
    assert run.status == "completed"
    assert run.conclusion == "success"


@pytest.mark.integration
def test_workflow_job_construction():
    """Test WorkflowJob construction."""
    job = WorkflowJob(
        id=789,
        run_id=123,
        name="test-job",
        status="completed",
        conclusion="success",
        started_at="2024-01-01T00:00:00Z",
        completed_at="2024-01-01T00:05:00Z",
    )
    assert job.id == 789
    assert job.run_id == 123
    assert job.name == "test-job"


@pytest.mark.integration
def test_workflow_step_construction():
    """Test WorkflowStep construction."""
    step = WorkflowStep(
        name="test-step",
        status="completed",
        conclusion="success",
        number=1,
    )
    assert step.name == "test-step"
    assert step.status == "completed"
    assert step.number == 1


@pytest.mark.integration
def test_workflow_job_if_condition():
    """Test WorkflowJob if-condition handling."""
    job = WorkflowJob(
        id=100,
        run_id=200,
        name="conditional-job",
        status="skipped",
        conclusion="skipped",
        if_condition={"expression": "github.event_name == 'push'"},
    )
    assert job.if_condition is not None
    assert "expression" in job.if_condition
