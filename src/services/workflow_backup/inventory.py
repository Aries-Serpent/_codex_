"""Workflow service inventory module."""
from typing import Optional, Dict, Any, List
from .types import WorkflowRun
from .parser import WorkflowParser

class WorkflowInventory:
    """Inventory manager for workflow runs."""
    
    def __init__(self):
        """Initialize the workflow inventory."""
        self.parser = WorkflowParser()
        self._runs: Dict[str, WorkflowRun] = {}
    
    def register_run(self, run_id: str, run_data: Dict[str, Any]) -> WorkflowRun:
        """Register a workflow run in the inventory."""
        run = self.parser.parse_workflow_run(run_data)
        self._runs[run_id] = run
        return run
    
    def get_run(self, run_id: str) -> Optional[WorkflowRun]:
        """Retrieve a workflow run from the inventory."""
        return self._runs.get(run_id)
    
    def list_runs(self) -> List[WorkflowRun]:
        """List all workflow runs in the inventory."""
        return list(self._runs.values())

__all__ = ["WorkflowInventory"]
