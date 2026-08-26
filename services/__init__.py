"""Public service exports for the repository.

This compatibility layer exposes the workflow inventory and parser from the
canonical implementation under ``src/services`` so both import paths behave
consistently for app code and tests.
"""

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
