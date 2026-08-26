"""Compatibility exports for workflow services."""

from src.services.workflow import (
    WorkflowDependency,
    WorkflowInput,
    WorkflowInventory,
    WorkflowJob,
    WorkflowMetadata,
    WorkflowParser,
    WorkflowTrigger,
)

__all__ = [
    "WorkflowDependency",
    "WorkflowInput",
    "WorkflowInventory",
    "WorkflowJob",
    "WorkflowMetadata",
    "WorkflowParser",
    "WorkflowTrigger",
]
