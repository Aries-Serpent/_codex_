"""Comprehensive test suite for src/services/workflow/types.py.

Tests cover:
- Enum definitions and behavior (TriggerType, InputType)
- Pydantic model instantiation and validation
- Serialization/deserialization (model_dump, model_validate)
- Field validators and constraints
- Type checking and coercion
- Integration scenarios with nested structures
"""

from pathlib import Path

import pytest
from pydantic import ValidationError

from src.services.workflow.types import (
    InputType,
    InventoryStats,
    TriggerType,
    WorkflowDependency,
    WorkflowInput,
    WorkflowJob,
    WorkflowJobExecution,
    WorkflowMetadata,
    WorkflowRun,
    WorkflowStep,
    WorkflowTrigger,
)


class TestEnumTriggerType:
    """Test TriggerType enum definition and behavior."""

    def test_trigger_type_workflow_dispatch(self):
        """Verify WORKFLOW_DISPATCH enum value."""
        assert TriggerType.WORKFLOW_DISPATCH.value == "workflow_dispatch", "Value must be initialized"

    def test_trigger_type_push(self):
        """Verify PUSH enum value."""
        assert TriggerType.PUSH.value == "push", "Value must be initialized"

    def test_trigger_type_pull_request(self):
        """Verify PULL_REQUEST enum value."""
        assert TriggerType.PULL_REQUEST.value == "pull_request", "Value must be initialized"

    def test_trigger_type_schedule(self):
        """Verify SCHEDULE enum value."""
        assert TriggerType.SCHEDULE.value == "schedule", "Value must be initialized"

    def test_trigger_type_workflow_call(self):
        """Verify WORKFLOW_CALL enum value."""
        assert TriggerType.WORKFLOW_CALL.value == "workflow_call", "Value must be initialized"

    def test_trigger_type_workflow_run(self):
        """Verify WORKFLOW_RUN enum value."""
        assert TriggerType.WORKFLOW_RUN.value == "workflow_run", "Value must be initialized"

    def test_trigger_type_repository_dispatch(self):
        """Verify REPOSITORY_DISPATCH enum value."""
        assert TriggerType.REPOSITORY_DISPATCH.value == "repository_dispatch", "Value must be initialized"

    def test_trigger_type_release(self):
        """Verify RELEASE enum value."""
        assert TriggerType.RELEASE.value == "release", "Value must be initialized"

    def test_trigger_type_create(self):
        """Verify CREATE enum value."""
        assert TriggerType.CREATE.value == "create", "Value must be initialized"

    def test_trigger_type_delete(self):
        """Verify DELETE enum value."""
        assert TriggerType.DELETE.value == "delete", "Value must be initialized"

    def test_trigger_type_string_representation(self):
        """Verify string representation of enum values."""
        assert str(TriggerType.PUSH) == "TriggerType.PUSH", "Condition must be true"

    def test_trigger_type_all_members(self):
        """Verify all expected TriggerType members exist."""
        expected_members = {
            "WORKFLOW_DISPATCH",
            "PUSH",
            "PULL_REQUEST",
            "SCHEDULE",
            "WORKFLOW_CALL",
            "WORKFLOW_RUN",
            "REPOSITORY_DISPATCH",
            "RELEASE",
            "CREATE",
            "DELETE",
            "FORK",
            "ISSUES",
            "ISSUE_COMMENT",
            "PULL_REQUEST_TARGET",
            "PULL_REQUEST_REVIEW",
            "PULL_REQUEST_REVIEW_COMMENT",
            "REGISTRY_PACKAGE",
            "WATCH",
            "OTHER",
        }
        assert set(t.name for t in TriggerType) == expected_members, "Condition must be true"

    def test_trigger_type_iteration(self):
        """Verify all TriggerType members can be iterated."""
        members = list(TriggerType)
        assert len(members) == 19, "Members must not be empty"


class TestEnumInputType:
    """Test InputType enum definition and behavior."""

    def test_input_type_string(self):
        """Verify STRING enum value."""
        assert InputType.STRING.value == "string", "Value must be initialized"

    def test_input_type_choice(self):
        """Verify CHOICE enum value."""
        assert InputType.CHOICE.value == "choice", "Value must be initialized"

    def test_input_type_boolean(self):
        """Verify BOOLEAN enum value."""
        assert InputType.BOOLEAN.value == "boolean", "Value must be initialized"

    def test_input_type_environment(self):
        """Verify ENVIRONMENT enum value."""
        assert InputType.ENVIRONMENT.value == "environment", "Value must be initialized"

    def test_input_type_number(self):
        """Verify NUMBER enum value."""
        assert InputType.NUMBER.value == "number", "Value must be initialized"

    def test_input_type_all_members(self):
        """Verify all expected InputType members exist."""
        expected_members = {"STRING", "CHOICE", "BOOLEAN", "ENVIRONMENT", "NUMBER"}
        assert set(t.name for t in InputType) == expected_members, "Condition must be true"

    def test_input_type_iteration(self):
        """Verify all InputType members can be iterated."""
        members = list(InputType)
        assert len(members) == 5, "Members must not be empty"


class TestWorkflowInputCreation:
    """Test WorkflowInput model instantiation."""

    def test_workflow_input_minimal(self):
        """Create WorkflowInput with minimal required fields."""
        inp = WorkflowInput(name="test", type=InputType.STRING)
        assert inp.name == "test", "name is not valid"
        assert inp.type == InputType.STRING, "type is not valid"
        assert inp.required is False, "required is not valid"
        assert inp.default is None, "default is not valid"

    def test_workflow_input_full(self):
        """Create WorkflowInput with all fields specified."""
        inp = WorkflowInput(
            name="test",
            type=InputType.CHOICE,
            required=True,
            default="option1",
        )
        assert inp.name == "test", "name is not valid"
        assert inp.type == InputType.CHOICE, "type is not valid"
        assert inp.required is True, "required is not valid"
        assert inp.default == "option1", "default is not valid"

    def test_workflow_input_frozen_immutable(self):
        """Verify WorkflowInput is immutable."""
        inp = WorkflowInput(name="test", type=InputType.STRING)
        with pytest.raises(Exception):  # FrozenInstanceError or ValidationError
            inp.name = "modified"

    def test_workflow_input_serialization(self):
        """Test WorkflowInput serialization."""
        inp = WorkflowInput(name="test", type=InputType.BOOLEAN, required=True)
        data = inp.model_dump()
        assert data["name"] == "test", "Data must not be empty"
        assert data["type"] == InputType.BOOLEAN, "Data must not be empty"
        assert data["required"] is True, "Data must not be empty"

    def test_workflow_input_deserialization(self):
        """Test WorkflowInput deserialization."""
        data = {
            "name": "test",
            "type": "string",
            "required": False,
            "default": None,
        }
        inp = WorkflowInput.model_validate(data)
        assert inp.name == "test", "name is not valid"
        assert inp.type == InputType.STRING, "type is not valid"

    def test_workflow_input_enum_string_coercion(self):
        """Verify InputType can be coerced from string."""
        inp = WorkflowInput(name="test", type="choice")
        assert inp.type == InputType.CHOICE, "type is not valid"


class TestWorkflowTriggerCreation:
    """Test WorkflowTrigger model instantiation."""

    def test_workflow_trigger_single_branch(self):
        """Create WorkflowTrigger with single branch."""
        trigger = WorkflowTrigger(
            type=TriggerType.PUSH,
            branches=["main"],
        )
        assert trigger.type == TriggerType.PUSH, "type is not valid"
        assert trigger.branches == ["main"], "branches is not valid"

    def test_workflow_trigger_multiple_branches(self):
        """Create WorkflowTrigger with multiple branches."""
        trigger = WorkflowTrigger(
            type=TriggerType.PULL_REQUEST,
            branches=["main", "develop", "staging"],
        )
        assert len(trigger.branches) == 3, "Collection must not be empty"

    def test_workflow_trigger_schedule(self):
        """Create WorkflowTrigger for schedule."""
        trigger = WorkflowTrigger(
            type=TriggerType.SCHEDULE,
            schedule_cron=["0 0 * * *"],
        )
        assert trigger.type == TriggerType.SCHEDULE, "type is not valid"
        assert trigger.schedule_cron == ["0 0 * * *"], "schedule_cron is not valid"

    def test_workflow_trigger_workflow_dispatch(self):
        """Create WorkflowTrigger for workflow_dispatch."""
        trigger = WorkflowTrigger(
            type=TriggerType.WORKFLOW_DISPATCH,
            types=["requested"],
        )
        assert trigger.type == TriggerType.WORKFLOW_DISPATCH, "type is not valid"
        assert trigger.types == ["requested"], "types is not valid"

    def test_workflow_trigger_frozen_immutable(self):
        """Verify WorkflowTrigger is immutable."""
        trigger = WorkflowTrigger(type=TriggerType.PUSH, branches=["main"])
        with pytest.raises(Exception):
            trigger.branches = ["develop"]


class TestWorkflowJobCreation:
    """Test WorkflowJob model instantiation."""

    def test_workflow_job_minimal(self):
        """Create WorkflowJob with minimal required fields."""
        job = WorkflowJob(id="job1", name="test-job", runs_on="ubuntu-latest")
        assert job.id == "job1", "id is not valid"
        assert job.name == "test-job", "name is not valid"
        assert job.runs_on == "ubuntu-latest", "runs_on is not valid"
        assert job.steps == 0, "steps is not valid"

    def test_workflow_job_with_steps(self):
        """Create WorkflowJob with steps count."""
        job = WorkflowJob(
            id="job1",
            name="test-job",
            runs_on="ubuntu-latest",
            steps=3,
        )
        assert job.id == "job1", "id is not valid"
        assert job.steps == 3, "steps is not valid"

    def test_workflow_job_with_if_condition(self):
        """Create WorkflowJob with if_condition."""
        job = WorkflowJob(
            id="job1",
            name="test-job",
            runs_on="ubuntu-latest",
            if_condition="success()",
        )
        assert job.if_condition == "success()", "if_condition is not valid"

    def test_workflow_job_if_condition_alias(self):
        """Verify if_condition field alias works."""
        data = {
            "id": "job1",
            "name": "test-job",
            "runs_on": "ubuntu-latest",
            "if": "failure()",
        }
        job = WorkflowJob.model_validate(data)
        assert job.if_condition == "failure()", "if_condition is not valid"

    def test_workflow_job_multiple_runners(self):
        """Create WorkflowJob with multiple runners."""
        job = WorkflowJob(
            id="job1",
            name="test-job",
            runs_on=["ubuntu-latest", "windows-latest"],
        )
        assert isinstance(job.runs_on, list)
        assert len(job.runs_on) == 2, "Collection must not be empty"

    def test_workflow_job_frozen_immutable(self):
        """Verify WorkflowJob is immutable."""
        job = WorkflowJob(id="job1", name="test-job", runs_on="ubuntu-latest")
        with pytest.raises(Exception):
            job.name = "modified"

    def test_workflow_job_with_timeout(self):
        """Create WorkflowJob with timeout."""
        job = WorkflowJob(
            id="job1",
            name="test-job",
            runs_on="ubuntu-latest",
            timeout_minutes=30,
        )
        assert job.timeout_minutes == 30, "timeout_minutes is not valid"

    def test_workflow_job_with_uses(self):
        """Create WorkflowJob with uses (reusable workflow)."""
        job = WorkflowJob(
            id="job1",
            name="test-job",
            runs_on="ubuntu-latest",
            uses="owner/repo/.github/workflows/reusable.yml@v1",
        )
        assert job.uses == "owner/repo/.github/workflows/reusable.yml@v1", "uses is not valid"


class TestWorkflowMetadataCreation:
    """Test WorkflowMetadata model instantiation."""

    def test_workflow_metadata_minimal(self):
        """Create WorkflowMetadata with minimal fields."""
        meta = WorkflowMetadata(name="test-workflow", file_path="workflow.yml")
        assert meta.name == "test-workflow", "name is not valid"

    def test_workflow_metadata_path_conversion(self):
        """Verify file_path converts to Path object."""
        meta = WorkflowMetadata(name="test-workflow", file_path=".github/workflows/ci.yml")
        assert isinstance(meta.file_path, Path)

    def test_workflow_metadata_path_direct_object(self):
        """Create WorkflowMetadata with Path object."""
        path_obj = Path(".github/workflows/ci.yml")
        meta = WorkflowMetadata(name="test-workflow", file_path=path_obj)
        assert meta.file_path == path_obj, "Object must be initialized"

    def test_workflow_metadata_with_triggers(self):
        """Create WorkflowMetadata with triggers."""
        trigger = WorkflowTrigger(type=TriggerType.PUSH, branches=["main"])
        meta = WorkflowMetadata(
            name="test-workflow",
            file_path="workflow.yml",
            triggers=[trigger],
        )
        assert len(meta.triggers) == 1, "Collection must not be empty"

    def test_workflow_metadata_with_jobs(self):
        """Create WorkflowMetadata with jobs."""
        job = WorkflowJob(id="job1", name="test-job", runs_on="ubuntu-latest")
        meta = WorkflowMetadata(
            name="test-workflow",
            file_path="workflow.yml",
            jobs={"job1": job},
        )
        assert "job1" in meta.jobs, "Condition must be true"

    def test_workflow_metadata_mutable(self):
        """Verify WorkflowMetadata is mutable (not frozen)."""
        meta = WorkflowMetadata(name="test-workflow", file_path="workflow.yml")
        # This should not raise an exception
        meta.name = "modified"
        assert meta.name == "modified", "name is not valid"

    def test_workflow_metadata_computed_property_filename(self):
        """Test computed property filename."""
        meta = WorkflowMetadata(name="test-workflow", file_path=".github/workflows/ci.yml")
        assert meta.filename == "ci.yml", "filename is not valid"

    def test_workflow_metadata_property_has_workflow_dispatch(self):
        """Test has_workflow_dispatch computed property."""
        trigger = WorkflowTrigger(type=TriggerType.WORKFLOW_DISPATCH)
        meta = WorkflowMetadata(
            name="test-workflow",
            file_path="workflow.yml",
            triggers=[trigger],
        )
        assert meta.has_workflow_dispatch is True, "has_workflow_dispatch is not valid"

    def test_workflow_metadata_property_trigger_types(self):
        """Test trigger_types computed property."""
        triggers = [
            WorkflowTrigger(type=TriggerType.PUSH, branches=["main"]),
            WorkflowTrigger(type=TriggerType.PULL_REQUEST, branches=["main"]),
        ]
        meta = WorkflowMetadata(
            name="test-workflow",
            file_path="workflow.yml",
            triggers=triggers,
        )
        assert len(meta.trigger_types) == 2, "Collection must not be empty"

    def test_workflow_metadata_property_job_ids(self):
        """Test job_ids computed property."""
        jobs = {
            "build": WorkflowJob(id="build", name="Build", runs_on="ubuntu-latest"),
            "test": WorkflowJob(id="test", name="Test", runs_on="ubuntu-latest"),
        }
        meta = WorkflowMetadata(
            name="test-workflow",
            file_path="workflow.yml",
            jobs=jobs,
        )
        assert set(meta.job_ids) == {"build", "test"}


class TestWorkflowStepCreation:
    """Test WorkflowStep model instantiation."""

    def test_workflow_step_minimal(self):
        """Create WorkflowStep with required fields."""
        step = WorkflowStep(name="Checkout", status="completed", conclusion="success", number=1)
        assert step.name == "Checkout", "name is not valid"
        assert step.status == "completed", "status is not valid"
        assert step.conclusion == "success", "conclusion is not valid"
        assert step.number == 1, "number is not valid"

    def test_workflow_step_in_progress(self):
        """Create WorkflowStep with in_progress status."""
        step = WorkflowStep(name="Build", status="in_progress", conclusion="neutral", number=2)
        assert step.status == "in_progress", "status is not valid"

    def test_workflow_step_failed(self):
        """Create WorkflowStep with failed status."""
        step = WorkflowStep(name="Test", status="completed", conclusion="failure", number=3)
        assert step.conclusion == "failure", "conclusion is not valid"

    def test_workflow_step_frozen_immutable(self):
        """Verify WorkflowStep is immutable."""
        step = WorkflowStep(name="Checkout", status="completed", conclusion="success", number=1)
        with pytest.raises(Exception):
            step.name = "Modified"


class TestWorkflowDependencyCreation:
    """Test WorkflowDependency model instantiation."""

    def test_workflow_dependency_minimal(self):
        """Create WorkflowDependency with minimal fields."""
        dep = WorkflowDependency(
            source="setup.yml",
            target="ci.yml",
            trigger_type=TriggerType.WORKFLOW_CALL,
        )
        assert dep.source == "setup.yml", "source is not valid"
        assert dep.target == "ci.yml", "target is not valid"
        assert dep.trigger_type == TriggerType.WORKFLOW_CALL, "trigger_type is not valid"

    def test_workflow_dependency_not_required(self):
        """Create WorkflowDependency with required=False."""
        dep = WorkflowDependency(
            source="optional.yml",
            target="main.yml",
            trigger_type=TriggerType.WORKFLOW_RUN,
            required=False,
        )
        assert dep.required is False, "required is not valid"

    def test_workflow_dependency_frozen_immutable(self):
        """Verify WorkflowDependency is immutable."""
        dep = WorkflowDependency(
            source="a.yml",
            target="b.yml",
            trigger_type=TriggerType.PUSH,
        )
        with pytest.raises(Exception):
            dep.source = "modified"


class TestWorkflowRunCreation:
    """Test WorkflowRun model instantiation."""

    def test_workflow_run_minimal(self):
        """Create WorkflowRun with required fields."""
        run = WorkflowRun(
            id=123,
            workflow_id=456,
            status="completed",
            conclusion="success",
            url="https://github.com/repo/actions/runs/123",
        )
        assert run.id == 123, "id is not valid"
        assert run.workflow_id == 456, "workflow_id is not valid"
        assert run.status == "completed", "status is not valid"

    def test_workflow_run_in_progress(self):
        """Create WorkflowRun with in_progress status."""
        run = WorkflowRun(
            id=124,
            workflow_id=456,
            status="in_progress",
            conclusion="",
            url="https://github.com/repo/actions/runs/124",
        )
        assert run.status == "in_progress", "status is not valid"

    def test_workflow_run_frozen_immutable(self):
        """Verify WorkflowRun is immutable."""
        run = WorkflowRun(
            id=123,
            workflow_id=456,
            status="completed",
            conclusion="success",
            url="https://github.com/repo/actions/runs/123",
        )
        with pytest.raises(Exception):
            run.status = "modified"


class TestWorkflowJobExecutionCreation:
    """Test WorkflowJobExecution model instantiation."""

    def test_workflow_job_execution_minimal(self):
        """Create WorkflowJobExecution with required fields."""
        exec_record = WorkflowJobExecution(
            id=1,
            run_id=123,
            name="build",
            status="completed",
            conclusion="success",
        )
        assert exec_record.id == 1, "id is not valid"
        assert exec_record.run_id == 123, "run_id is not valid"
        assert exec_record.name == "build", "name is not valid"

    def test_workflow_job_execution_in_progress(self):
        """Create WorkflowJobExecution with in_progress status."""
        exec_record = WorkflowJobExecution(
            id=2,
            run_id=123,
            name="test",
            status="in_progress",
            conclusion="",
        )
        assert exec_record.status == "in_progress", "status is not valid"

    def test_workflow_job_execution_with_timestamps(self):
        """Create WorkflowJobExecution with timestamps."""
        exec_record = WorkflowJobExecution(
            id=3,
            run_id=123,
            name="deploy",
            status="completed",
            conclusion="success",
            started_at="2024-01-01T12:00:00Z",
            completed_at="2024-01-01T12:30:00Z",
        )
        assert exec_record.started_at is not None, "started_at must be initialized"
        assert exec_record.completed_at is not None, "completed_at must be initialized"

    def test_workflow_job_execution_frozen_immutable(self):
        """Verify WorkflowJobExecution is immutable."""
        exec_record = WorkflowJobExecution(
            id=1,
            run_id=123,
            name="build",
            status="completed",
            conclusion="success",
        )
        with pytest.raises(Exception):
            exec_record.status = "modified"


class TestInventoryStatsCreation:
    """Test InventoryStats model instantiation."""

    def test_inventory_stats_minimal(self):
        """Create InventoryStats with minimal fields."""
        stats = InventoryStats(
            total_workflows=10,
            total_jobs=50,
        )
        assert stats.total_workflows == 10, "total_workflows is not valid"
        assert stats.total_jobs == 50, "total_jobs is not valid"

    def test_inventory_stats_with_all_fields(self):
        """Create InventoryStats with all fields."""
        stats = InventoryStats(
            total_workflows=10,
            triggerable_workflows=8,
            reusable_workflows=2,
            total_jobs=50,
            total_triggers=15,
            trigger_type_counts={"push": 10, "pull_request": 5},
            dependency_count=3,
        )
        assert stats.total_workflows == 10, "total_workflows is not valid"
        assert stats.total_jobs == 50, "total_jobs is not valid"
        assert stats.triggerable_workflows == 8, "triggerable_workflows is not valid"
        assert stats.trigger_type_counts == {"push": 10, "pull_request": 5}


class TestSerialization:
    """Test model serialization and deserialization."""

    def test_workflow_input_model_dump_round_trip(self):
        """Test WorkflowInput serialization round-trip."""
        original = WorkflowInput(name="test", type=InputType.CHOICE, required=True, default="val")
        data = original.model_dump()
        restored = WorkflowInput.model_validate(data)
        assert restored.name == original.name, "name is not valid"
        assert restored.type == original.type, "type is not valid"
        assert restored.required == original.required, "required is not valid"

    def test_workflow_trigger_model_dump_round_trip(self):
        """Test WorkflowTrigger serialization round-trip."""
        original = WorkflowTrigger(
            type=TriggerType.PUSH,
            branches=["main", "develop"],
        )
        data = original.model_dump()
        restored = WorkflowTrigger.model_validate(data)
        assert restored.type == original.type, "type is not valid"
        assert restored.branches == original.branches, "branches is not valid"

    def test_workflow_job_model_dump_exclude_none(self):
        """Test WorkflowJob serialization with exclude_none."""
        job = WorkflowJob(
            id="test-job",
            name="test",
            runs_on="ubuntu-latest",
        )
        data = job.model_dump(exclude_none=True)
        assert "id" in data, "Data must not be empty"
        assert data["id"] == "test-job", "Data must not be empty"

    def test_workflow_metadata_path_serialization(self):
        """Test WorkflowMetadata Path field serialization."""
        meta = WorkflowMetadata(
            name="test",
            file_path=".github/workflows/ci.yml",
        )
        data = meta.model_dump()
        assert isinstance(data["file_path"], (str, Path))

    def test_workflow_metadata_path_deserialization(self):
        """Test WorkflowMetadata Path field deserialization."""
        data = {
            "name": "test",
            "file_path": ".github/workflows/ci.yml",
        }
        meta = WorkflowMetadata.model_validate(data)
        assert isinstance(meta.file_path, Path)


class TestValidation:
    """Test model validation and constraints."""

    def test_workflow_input_required_name(self):
        """Verify name field is required."""
        with pytest.raises(ValidationError):
            WorkflowInput(type=InputType.STRING)

    def test_workflow_input_required_name(self):
        """Verify name field is required."""
        with pytest.raises(ValidationError):
            WorkflowInput(description="test input")

    def test_workflow_trigger_required_type(self):
        """Verify TriggerType is required."""
        with pytest.raises(ValidationError):
            WorkflowTrigger(branches=["main"])

    def test_workflow_job_required_id(self):
        """Verify id field is required."""
        with pytest.raises(ValidationError):
            WorkflowJob(name="test", runs_on="ubuntu-latest")

    def test_workflow_job_required_runs_on(self):
        """Verify runs_on field is required."""
        with pytest.raises(ValidationError):
            WorkflowJob(id="job1", name="test")

    def test_workflow_metadata_required_name(self):
        """Verify name field is required."""
        with pytest.raises(ValidationError):
            WorkflowMetadata(file_path="workflow.yml")

    def test_workflow_metadata_required_file_path(self):
        """Verify file_path field is required."""
        with pytest.raises(ValidationError):
            WorkflowMetadata(name="test")

    def test_workflow_job_required_id(self):
        """Verify id field is required."""
        with pytest.raises(ValidationError):
            WorkflowJob(name="test", runs_on="ubuntu-latest")

    def test_workflow_step_needs_all_fields(self):
        """Verify WorkflowStep needs all required fields."""
        # Missing status
        with pytest.raises(ValidationError):
            WorkflowStep(name="Test", conclusion="success", number=1)

        # Missing conclusion
        with pytest.raises(ValidationError):
            WorkflowStep(name="Test", status="completed", number=1)

        # Missing number
        with pytest.raises(ValidationError):
            WorkflowStep(name="Test", status="completed", conclusion="success")

    def test_input_type_enum_validation(self):
        """Verify InputType enum validation."""
        with pytest.raises(ValidationError):
            WorkflowInput(name="test", type="invalid_type")

    def test_trigger_type_enum_validation(self):
        """Verify TriggerType enum validation."""
        with pytest.raises(ValidationError):
            WorkflowTrigger(type="invalid_trigger")


class TestIntegration:
    """Test integration scenarios with nested structures."""

    def test_complete_workflow_metadata_structure(self):
        """Build complete WorkflowMetadata with all nested components."""
        trigger = WorkflowTrigger(type=TriggerType.PUSH, branches=["main"])
        job = WorkflowJob(id="build", name="build", runs_on="ubuntu-latest", steps=2)
        meta = WorkflowMetadata(
            name="CI",
            file_path=".github/workflows/ci.yml",
            triggers=[trigger],
            jobs={"build": job},
        )

        assert meta.name == "CI", "name is not valid"
        assert len(meta.triggers) == 1, "Collection must not be empty"
        assert len(meta.jobs) == 1, "Collection must not be empty"
        assert meta.filename == "ci.yml", "filename is not valid"
        assert meta.has_workflow_dispatch is False, "has_workflow_dispatch is not valid"

    def test_workflow_with_multiple_triggers(self):
        """Create workflow with multiple trigger types."""
        triggers = [
            WorkflowTrigger(type=TriggerType.PUSH, branches=["main"]),
            WorkflowTrigger(type=TriggerType.PULL_REQUEST, branches=["main"]),
            WorkflowTrigger(type=TriggerType.WORKFLOW_DISPATCH),
        ]
        meta = WorkflowMetadata(
            name="Multi-Trigger",
            file_path="workflow.yml",
            triggers=triggers,
        )
        assert len(meta.triggers) == 3, "Collection must not be empty"
        assert meta.has_workflow_dispatch is True, "has_workflow_dispatch is not valid"

    def test_workflow_with_multiple_jobs(self):
        """Create workflow with multiple jobs."""
        jobs = {
            "lint": WorkflowJob(id="lint", name="Lint", runs_on="ubuntu-latest"),
            "test": WorkflowJob(id="test", name="Test", runs_on="ubuntu-latest"),
            "build": WorkflowJob(id="build", name="Build", runs_on="ubuntu-latest"),
        }
        meta = WorkflowMetadata(
            name="Multi-Job",
            file_path="workflow.yml",
            jobs=jobs,
        )
        assert len(meta.jobs) == 3, "Collection must not be empty"
        assert set(meta.job_ids) == {"lint", "test", "build"}

    def test_workflow_with_job_dependencies(self):
        """Test WorkflowJob with needs field."""
        job = WorkflowJob(
            id="deploy",
            name="deploy",
            runs_on="ubuntu-latest",
            needs=["build", "test"],
        )
        assert job.needs == ["build", "test"]

    def test_workflow_with_multiple_permissions(self):
        """Test WorkflowMetadata with permissions."""
        meta = WorkflowMetadata(
            name="secure-workflow",
            file_path="workflow.yml",
            permissions={"contents": "write", "packages": "write"},
        )
        assert meta.permissions == {"contents": "write", "packages": "write"}

    def test_workflow_with_environment_variables(self):
        """Test WorkflowMetadata with environment variables."""
        meta = WorkflowMetadata(
            name="env-workflow",
            file_path="workflow.yml",
            env={"DEBUG": True, "LOG_LEVEL": "info"},
        )
        assert meta.env == {"DEBUG": True, "LOG_LEVEL": "info"}

    def test_workflow_metadata_empty_jobs(self):
        """Create WorkflowMetadata with empty jobs dict."""
        meta = WorkflowMetadata(
            name="empty",
            file_path="workflow.yml",
            jobs={},
        )
        assert len(meta.jobs) == 0, "Collection must not be empty"
        assert meta.job_ids == [], "job_ids is not valid"

    def test_workflow_metadata_empty_triggers(self):
        """Create WorkflowMetadata with empty triggers list."""
        meta = WorkflowMetadata(
            name="empty",
            file_path="workflow.yml",
            triggers=[],
        )
        assert len(meta.triggers) == 0, "Collection must not be empty"
        assert meta.has_workflow_dispatch is False, "has_workflow_dispatch is not valid"

    def test_complex_workflow_serialization(self):
        """Test serialization of complex nested workflow."""
        triggers = [
            WorkflowTrigger(type=TriggerType.PUSH, branches=["main"]),
            WorkflowTrigger(type=TriggerType.WORKFLOW_DISPATCH),
        ]
        job = WorkflowJob(
            id="test",
            name="test",
            runs_on="ubuntu-latest",
            steps=3,
        )
        meta = WorkflowMetadata(
            name="CI",
            file_path=".github/workflows/ci.yml",
            triggers=triggers,
            jobs={"test": job},
        )

        data = meta.model_dump()
        assert isinstance(data, dict)
        assert "name" in data, "Data must not be empty"
        assert "triggers" in data, "Data must not be empty"
        assert "jobs" in data, "Data must not be empty"

        restored = WorkflowMetadata.model_validate(data)
        assert restored.name == meta.name, "name is not valid"
        assert len(restored.triggers) == len(meta.triggers), "Collection must not be empty"
        assert len(restored.jobs) == len(meta.jobs), "Collection must not be empty"
