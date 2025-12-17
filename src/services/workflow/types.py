"""Type definitions for workflow metadata and configuration."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from pydantic import BaseModel, Field, field_validator


class TriggerType(str, Enum):
    """GitHub Actions trigger types."""

    WORKFLOW_DISPATCH = "workflow_dispatch"
    PUSH = "push"
    PULL_REQUEST = "pull_request"
    SCHEDULE = "schedule"
    WORKFLOW_CALL = "workflow_call"
    WORKFLOW_RUN = "workflow_run"
    REPOSITORY_DISPATCH = "repository_dispatch"
    RELEASE = "release"
    CREATE = "create"
    DELETE = "delete"
    FORK = "fork"
    ISSUES = "issues"
    ISSUE_COMMENT = "issue_comment"
    PULL_REQUEST_TARGET = "pull_request_target"
    PULL_REQUEST_REVIEW = "pull_request_review"
    PULL_REQUEST_REVIEW_COMMENT = "pull_request_review_comment"
    REGISTRY_PACKAGE = "registry_package"
    WATCH = "watch"
    OTHER = "other"


class InputType(str, Enum):
    """Workflow input types."""

    STRING = "string"
    CHOICE = "choice"
    BOOLEAN = "boolean"
    ENVIRONMENT = "environment"
    NUMBER = "number"


class WorkflowInput(BaseModel):
    """Workflow input definition."""

    name: str = Field(..., description="Input name")
    description: Optional[str] = Field(None, description="Input description")
    required: bool = Field(False, description="Whether input is required")
    type: InputType = Field(InputType.STRING, description="Input type")
    default: Optional[Union[str, bool, int]] = Field(None, description="Default value")
    options: Optional[List[str]] = Field(None, description="Choice options")

    class Config:
        frozen = True


class WorkflowTrigger(BaseModel):
    """Workflow trigger configuration."""

    type: TriggerType = Field(..., description="Trigger type")
    branches: Optional[List[str]] = Field(None, description="Branch filters")
    paths: Optional[List[str]] = Field(None, description="Path filters")
    types: Optional[List[str]] = Field(None, description="Activity types")
    schedule_cron: Optional[List[str]] = Field(None, description="Cron schedules")
    workflows: Optional[List[str]] = Field(None, description="Workflow dependencies")

    class Config:
        frozen = True


class WorkflowJob(BaseModel):
    """Workflow job definition."""

    id: str = Field(..., description="Job ID")
    name: Optional[str] = Field(None, description="Job display name")
    runs_on: Union[str, List[str]] = Field(..., description="Runner labels")
    needs: Optional[List[str]] = Field(None, description="Job dependencies")
    if_condition: Optional[str] = Field(None, alias="if", description="Conditional expression")
    steps: int = Field(0, description="Number of steps")
    timeout_minutes: Optional[int] = Field(None, description="Job timeout")
    uses: Optional[str] = Field(None, description="Reusable workflow reference")

    class Config:
        frozen = True
        populate_by_name = True


class WorkflowDependency(BaseModel):
    """Workflow dependency relationship."""

    source: str = Field(..., description="Source workflow name")
    target: str = Field(..., description="Target workflow name")
    trigger_type: TriggerType = Field(..., description="How dependency is triggered")
    required: bool = Field(True, description="Whether dependency is required")

    class Config:
        frozen = True


class WorkflowMetadata(BaseModel):
    """Complete workflow metadata."""

    name: str = Field(..., description="Workflow name")
    file_path: Path = Field(..., description="Path to workflow file")
    triggers: List[WorkflowTrigger] = Field(
        default_factory=list, description="Trigger configurations"
    )
    inputs: Dict[str, WorkflowInput] = Field(default_factory=dict, description="Workflow inputs")
    jobs: Dict[str, WorkflowJob] = Field(default_factory=dict, description="Job definitions")
    dependencies: List[WorkflowDependency] = Field(
        default_factory=list, description="Workflow dependencies"
    )
    permissions: Dict[str, str] = Field(default_factory=dict, description="Permission settings")
    env: Dict[str, Union[str, int, bool]] = Field(
        default_factory=dict, description="Environment variables"
    )
    concurrency: Optional[Dict[str, Any]] = Field(None, description="Concurrency settings")
    is_reusable: bool = Field(False, description="Whether workflow is reusable")
    is_triggerable: bool = Field(False, description="Whether workflow can be manually triggered")
    last_modified: Optional[datetime] = Field(None, description="Last modification time")

    @field_validator("file_path", mode="before")
    @classmethod
    def convert_path(cls, v: Any) -> Path:
        """Convert string paths to Path objects."""
        if isinstance(v, str):
            return Path(v)
        return v

    @property
    def filename(self) -> str:
        """Get workflow filename."""
        return self.file_path.name

    @property
    def has_workflow_dispatch(self) -> bool:
        """Check if workflow has workflow_dispatch trigger."""
        return any(t.type == TriggerType.WORKFLOW_DISPATCH for t in self.triggers)

    @property
    def trigger_types(self) -> Set[TriggerType]:
        """Get all trigger types."""
        return {t.type for t in self.triggers}

    @property
    def job_ids(self) -> List[str]:
        """Get all job IDs."""
        return list(self.jobs.keys())

    class Config:
        frozen = False  # Allow mutations for caching
        arbitrary_types_allowed = True


class InventoryStats(BaseModel):
    """Statistics about workflow inventory."""

    total_workflows: int = Field(0, description="Total number of workflows")
    triggerable_workflows: int = Field(0, description="Manually triggerable workflows")
    reusable_workflows: int = Field(0, description="Reusable workflows")
    total_jobs: int = Field(0, description="Total number of jobs")
    total_triggers: int = Field(0, description="Total number of triggers")
    trigger_type_counts: Dict[str, int] = Field(
        default_factory=dict, description="Count by trigger type"
    )
    dependency_count: int = Field(0, description="Number of workflow dependencies")

    class Config:
        frozen = True
