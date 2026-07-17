"""Workflow service parser module."""
from typing import Optional, Dict, Any, List
from .types import WorkflowRun, WorkflowJobExecution, WorkflowStep

class WorkflowParser:
    """Parser for workflow configurations and runs."""
    
    def __init__(self):
        """Initialize the workflow parser."""
        pass
    
    def parse_workflow_run(self, data: Dict[str, Any]) -> WorkflowRun:
        """Parse workflow run data."""
        return WorkflowRun(
            id=data.get("id", ""),
            name=data.get("name", ""),
            status=data.get("status", ""),
            conclusion=data.get("conclusion"),
        )
    
    def parse_job_execution(self, data: Dict[str, Any]) -> WorkflowJobExecution:
        """Parse job execution data."""
        return WorkflowJobExecution(
            id=data.get("id", ""),
            name=data.get("name", ""),
            status=data.get("status", ""),
            conclusion=data.get("conclusion"),
        )

__all__ = ["WorkflowParser"]
