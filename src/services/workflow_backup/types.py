"""Workflow service types module."""
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

class WorkflowJobStatus(str, Enum):
    """Workflow job status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class WorkflowStep:
    """Represents a workflow step."""
    name: str
    status: str
    conclusion: Optional[str] = None

@dataclass
class WorkflowJobExecution:
    """Represents a workflow job execution."""
    id: str
    name: str
    status: str
    conclusion: Optional[str] = None
    steps: Optional[List[WorkflowStep]] = None

@dataclass
class WorkflowRun:
    """Represents a workflow run."""
    id: str
    name: str
    status: str
    conclusion: Optional[str] = None
    jobs: Optional[List[WorkflowJobExecution]] = None

__all__ = [
    "WorkflowJobStatus",
    "WorkflowStep",
    "WorkflowJobExecution",
    "WorkflowRun",
]

class InputType:
    """Input type for workflow configuration."""
    def __init__(self, name: str = "default"):
        self.name = name

__all__.append("InputType")

class TriggerType:
    """Trigger type for workflow execution."""
    def __init__(self, name: str = "push"):
        self.name = name

# Update __all__ if needed
if "TriggerType" not in __all__:
    __all__.append("TriggerType")
