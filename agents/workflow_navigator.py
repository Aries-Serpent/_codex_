"""
Workflow Navigator for AI Assistants/Agents

Provides tokenized logical workflows for deterministic navigation and execution
of common repository operations.
"""

import json
import logging
logger = logging.getLogger(__name__)
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


class WorkflowFrequency(Enum):
    """How often a workflow is typically used"""

    HIGH = "high"  # Daily/multiple per day
    MEDIUM = "medium"  # Weekly
    LOW = "low"  # Monthly


class StepStatus(Enum):
    """Status of a workflow step"""

    PENDING = "pending"
    RUNNING = "running"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


@dataclass
class WorkflowStep:
    """A single step in a workflow"""

    id: str
    action: str
    command: Optional[str] = None
    uses: Optional[str] = None  # Reference to another workflow or function
    outputs: List[str] = field(default_factory=list)
    optional: bool = False
    status: StepStatus = StepStatus.PENDING

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute this step"""
        self.status = StepStatus.RUNNING

        try:
            if self.command:
                # Execute shell command with safety: split command into list
                import shlex

                cmd_list = shlex.split(self.command)
                result = subprocess.run(
                    cmd_list, capture_output=True, text=True, cwd=context.get("working_dir", ".")
                )

                if result.returncode != 0 and not self.optional:
                    self.status = StepStatus.FAILED
                    return {"success": False, "error": result.stderr, "stdout": result.stdout}

                self.status = StepStatus.COMPLETED
                return {"success": True, "stdout": result.stdout, "stderr": result.stderr}

            elif self.uses:
                # Call another workflow or function
                # This would be implemented to dynamically import and call
                self.status = StepStatus.COMPLETED
                return {"success": True, "message": f"Would execute: {self.uses}"}

            else:
                self.status = StepStatus.SKIPPED
                return {"success": True, "message": "No action defined"}

        except Exception as e:
            logger.debug(f"Exception: {e}")
            self.status = StepStatus.FAILED
            return {"success": False, "error": str(e)}


@dataclass
class Workflow:
    """A complete workflow definition"""

    workflow_id: str
    name: str
    description: str
    frequency: WorkflowFrequency
    deterministic: bool = True
    steps: List[WorkflowStep] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)
    entry_points: List[str] = field(default_factory=list)
    category: str = "general"

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "frequency": self.frequency.value,
            "deterministic": self.deterministic,
            "steps": [
                {
                    "id": step.id,
                    "action": step.action,
                    "command": step.command,
                    "uses": step.uses,
                    "outputs": step.outputs,
                    "optional": step.optional,
                }
                for step in self.steps
            ],
            "aliases": self.aliases,
            "entry_points": self.entry_points,
            "category": self.category,
        }


class WorkflowNavigator:
    """
    Navigate and execute tokenized workflows for AI Agents

    Provides deterministic, repeatable paths through common operations.
    """

    def __init__(self, workspace_dir: Path = None):
        self.workspace_dir = workspace_dir or Path.cwd()
        self.workflows: Dict[str, Workflow] = {}
        self.workflow_state_dir = self.workspace_dir / ".codex" / "workflows" / "state"
        self.workflow_state_dir.mkdir(parents=True, exist_ok=True)

        # Stateful navigation attributes
        self.current_workflow_id: Optional[str] = None
        self.current_step_index: int = 0

        # Initialize default workflows
        self._register_default_workflows()

    def _create_dynamic_workflow(self, workflow_type: str, **kwargs) -> Workflow:
        """
        Factory method for creating common workflow templates.

        Centralizes dynamic workflow creation logic to reduce duplication.

        Args:
            workflow_type: Type of workflow to create ('test_coverage', 'self_heal', 'audit_coverage', 'test_run')
            **kwargs: Additional parameters for workflow customization

        Returns:
            Workflow instance based on the specified type
        """
        if workflow_type == "test_coverage":
            return Workflow(
                workflow_id="TEST_COVERAGE_DYNAMIC",
                name="Improve Test Coverage",
                description="Dynamically generated workflow to identify and fill test coverage gaps",
                frequency=WorkflowFrequency.HIGH,
                steps=[
                    WorkflowStep(
                        id="identify_gaps",
                        action="Identify uncovered code paths",
                        command="pytest --cov-report=term-missing",
                    ),
                    WorkflowStep(
                        id="add_tests",
                        action="Add tests for uncovered code",
                    ),
                ],
            )
        elif workflow_type == "self_heal":
            return Workflow(
                workflow_id="SELF_HEAL_DYNAMIC",
                name="Self-Healing Issue Resolution",
                description="Dynamically generated workflow to categorize, prioritize, and resolve open issues",
                frequency=WorkflowFrequency.MEDIUM,
                steps=[
                    WorkflowStep(
                        id="categorize_issues",
                        action="Categorize open issues by type and severity",
                    ),
                    WorkflowStep(
                        id="prioritize",
                        action="Prioritize using physics-inspired scoring",
                    ),
                    WorkflowStep(
                        id="resolve",
                        action="Apply automated fixes where possible",
                    ),
                ],
            )
        elif workflow_type == "audit_coverage":
            return Workflow(
                workflow_id="AUDIT_COVERAGE_DYNAMIC",
                name="Audit Coverage Analysis",
                description="Dynamically generated workflow to audit code coverage and identify gaps",
                frequency=WorkflowFrequency.HIGH,
                steps=[
                    WorkflowStep(
                        id="run_coverage",
                        action="Run coverage analysis",
                        command="pytest --cov=. --cov-report=json",
                    ),
                    WorkflowStep(
                        id="analyze_gaps",
                        action="Analyze coverage gaps and prioritize",
                    ),
                    WorkflowStep(
                        id="report",
                        action="Generate audit report",
                    ),
                ],
            )
        elif workflow_type == "test_run":
            return Workflow(
                workflow_id="TEST_RUN_DYNAMIC",
                name="Test Execution",
                description="Dynamically generated workflow to execute tests",
                frequency=WorkflowFrequency.HIGH,
                steps=[
                    WorkflowStep(
                        id="setup",
                        action="Setup test environment",
                    ),
                    WorkflowStep(id="run_tests", action="Execute test suite", command="pytest -v"),
                    WorkflowStep(
                        id="report_results",
                        action="Report test results",
                    ),
                ],
            )
        else:
            raise ValueError(f"Unknown workflow type: {workflow_type}")

    def _register_default_workflows(self):
        """Register the default tokenized workflows"""

        # AUDIT_EXEC - Audit Execution
        audit_exec = Workflow(
            workflow_id="AUDIT_EXEC",
            name="Audit Execution",
            description="Run complete audit pipeline with visualization",
            frequency=WorkflowFrequency.HIGH,
            category="quality_assurance",
            steps=[
                WorkflowStep(
                    id="prepare",
                    action="validate_environment",
                    command="python -m scripts.space_traversal.audit_runner --check",
                    optional=True,
                ),
                WorkflowStep(
                    id="execute",
                    action="run_audit",
                    command="python -m scripts.space_traversal.audit_runner run",
                    outputs=["audit_report.md", "audit_results.json"],
                ),
                WorkflowStep(
                    id="store",
                    action="store_trends",
                    command="python -m scripts.space_traversal.audit_runner store-trend",
                    optional=True,
                ),
                WorkflowStep(
                    id="visualize",
                    action="generate_dashboard",
                    command="python -m scripts.space_traversal.audit_runner dashboard",
                    outputs=["audit_dashboard.html"],
                    optional=True,
                ),
            ],
            aliases=["audit", "check", "validate", "quality"],
            entry_points=["Run audit pipeline", "Check code quality", "Validate capabilities"],
        )
        self.register_workflow(audit_exec)

        # PHYS_DECIDE - Physics-Inspired Decision Making
        phys_decide = Workflow(
            workflow_id="PHYS_DECIDE",
            name="Physics-Inspired Decision",
            description="Make decisions using physics-inspired optimization",
            frequency=WorkflowFrequency.HIGH,
            category="decision_making",
            steps=[
                WorkflowStep(
                    id="assess", action="gather_state", uses="physics_orchestrator.assess_situation"
                ),
                WorkflowStep(
                    id="deliberate",
                    action="calculate_paths",
                    uses="physics_orchestrator.deliberate_paths",
                    outputs=["ranked_paths", "energy_calculations"],
                ),
                WorkflowStep(
                    id="optimize",
                    action="select_optimal",
                    uses="physics_orchestrator.optimize_path",
                ),
                WorkflowStep(id="act", action="execute_decision", uses="physics_orchestrator.act"),
                WorkflowStep(
                    id="reflect", action="store_reasoning", uses="mental_mapping.record_outcome"
                ),
            ],
            aliases=["decide", "choose", "evaluate", "optimize"],
            entry_points=["Make decision", "Evaluate options", "Choose path", "Optimize choice"],
        )
        self.register_workflow(phys_decide)

        # DOC_GEN - Documentation Generation
        doc_gen = Workflow(
            workflow_id="DOC_GEN",
            name="Documentation Generation",
            description="Generate comprehensive documentation and wiki",
            frequency=WorkflowFrequency.MEDIUM,
            category="deployment",
            steps=[
                WorkflowStep(
                    id="generate_wiki",
                    action="create_wiki_bundle",
                    command="python -m scripts.space_traversal.audit_runner wiki",
                    outputs=["wiki_bundle.zip"],
                    optional=True,
                ),
                WorkflowStep(
                    id="generate_docs_hub",
                    action="create_docs_hub",
                    command="python -m scripts.space_traversal.audit_runner docs-hub",
                    outputs=["docs_hub.html"],
                    optional=True,
                ),
                WorkflowStep(
                    id="generate_api_docs",
                    action="create_api_collection",
                    command="python -m scripts.space_traversal.viz_api_collection",
                    outputs=["api_collection.html"],
                    optional=True,
                ),
            ],
            aliases=["docs", "wiki", "documentation"],
            entry_points=["Generate documentation", "Update wiki", "Create API docs"],
        )
        self.register_workflow(doc_gen)

        # REPO_ORG - Repository Organization
        repo_org = Workflow(
            workflow_id="REPO_ORG",
            name="Repository Organization",
            description="Organize and archive repository files",
            frequency=WorkflowFrequency.LOW,
            category="maintenance",
            steps=[
                WorkflowStep(
                    id="analyze",
                    action="analyze_structure",
                    command="python scripts/organize_repository.py --dry-run",
                ),
                WorkflowStep(
                    id="archive",
                    action="archive_files",
                    command="python scripts/organize_repository.py",
                    outputs=["archive_directory", "index_json", "index_markdown"],
                ),
                WorkflowStep(
                    id="validate", action="verify_archive", uses="archive_validator.check_integrity"
                ),
            ],
            aliases=["organize", "cleanup", "archive"],
            entry_points=["Organize repository", "Archive old files", "Clean up root"],
        )
        self.register_workflow(repo_org)

    def register_workflow(self, workflow: Workflow) -> None:
        """Register a new workflow"""
        self.workflows[workflow.workflow_id] = workflow

        # Also register by aliases
        for alias in workflow.aliases:
            self.workflows[alias.upper()] = workflow

    def get_workflow(self, identifier: str) -> Optional[Workflow]:
        """
        Get workflow by ID or alias.

        Args:
            identifier: Workflow ID or alias

        Returns:
            Workflow object if found, None otherwise
        """
        return self.workflows.get(identifier.upper())

    def create_workflow(self, identifier: str, steps: List[WorkflowStep], **kwargs) -> str:
        """
        Create and register a new workflow with the given steps.

        Args:
            identifier: Workflow ID
            steps: List of workflow steps
            **kwargs: Additional workflow parameters (name, description, frequency, etc.)

        Returns:
            The workflow_id of the created workflow (uppercase)
        """
        workflow_id_upper = identifier.upper()
        workflow = Workflow(
            workflow_id=workflow_id_upper,
            name=kwargs.get("name", identifier.replace("_", " ").title()),
            description=kwargs.get(
                "description", f"Dynamically created workflow: {workflow_id_upper}"
            ),
            frequency=kwargs.get("frequency", WorkflowFrequency.MEDIUM),
            steps=steps,
            category=kwargs.get("category", "general"),
        )
        self.register_workflow(workflow)
        return workflow.workflow_id

    def current_step(self) -> Optional[WorkflowStep]:
        """Get the current step in the active workflow."""
        if not self.current_workflow_id:
            return None

        workflow = self.workflows.get(self.current_workflow_id)
        if not workflow or not workflow.steps:
            return None

        if 0 <= self.current_step_index < len(workflow.steps):
            return workflow.steps[self.current_step_index]

        return None

    def next_step(self) -> Optional[WorkflowStep]:
        """Advance to and return the next step in the workflow."""
        if not self.current_workflow_id:
            return None

        workflow = self.workflows.get(self.current_workflow_id)
        if not workflow or not workflow.steps:
            return None

        next_index = self.current_step_index + 1
        if next_index < len(workflow.steps):
            self.current_step_index = next_index
            return workflow.steps[self.current_step_index]

        return None

    def previous_step(self) -> Optional[WorkflowStep]:
        """Go back to and return the previous step in the workflow."""
        if not self.current_workflow_id:
            return None

        workflow = self.workflows.get(self.current_workflow_id)
        if not workflow or not workflow.steps:
            return None

        prev_index = self.current_step_index - 1
        if prev_index >= 0:
            self.current_step_index = prev_index
            return workflow.steps[self.current_step_index]

        return None

    def navigate_to(self, step_index: int = None, step_id: str = None) -> bool:
        """
        Navigate to a specific step by index or ID.

        Args:
            step_index: The index of the step to navigate to
            step_id: The ID of the step to navigate to

        Returns:
            True if navigation successful, False otherwise
        """
        if not self.current_workflow_id:
            return False

        workflow = self.workflows.get(self.current_workflow_id)
        if not workflow or not workflow.steps:
            return False

        if step_index is not None:
            if 0 <= step_index < len(workflow.steps):
                self.current_step_index = step_index
                return True
            return False

        if step_id is not None:
            for i, step in enumerate(workflow.steps):
                if step.id == step_id:
                    self.current_step_index = i
                    return True
            return False

        return False

    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get the status of a workflow.

        Args:
            workflow_id: The ID of the workflow

        Returns:
            Dictionary with workflow status information
        """
        workflow = self.workflows.get(workflow_id.upper())
        if not workflow:
            return {"exists": False, "error": "Workflow not found"}

        completed_steps = sum(1 for step in workflow.steps if step.status == StepStatus.COMPLETED)
        failed_steps = sum(1 for step in workflow.steps if step.status == StepStatus.FAILED)
        pending_steps = sum(1 for step in workflow.steps if step.status == StepStatus.PENDING)

        return {
            "exists": True,
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "total_steps": len(workflow.steps),
            "completed_steps": completed_steps,
            "failed_steps": failed_steps,
            "pending_steps": pending_steps,
            "current_index": (
                self.current_step_index if self.current_workflow_id == workflow_id.upper() else None
            ),
        }

    def suggest_next_action(self) -> Optional[str]:
        """
        Suggest the next action based on current workflow state.

        Returns:
            String suggestion or None if no workflow active
        """
        if not self.current_workflow_id:
            return None

        current = self.current_step()
        if current:
            return f"Execute: {current.action}"

        workflow = self.workflows.get(self.current_workflow_id)
        if workflow and workflow.steps:
            if self.current_step_index >= len(workflow.steps):
                return "Workflow completed"
            else:
                return f"Start workflow: {workflow.name}"

        return None

    def find_workflow(self, description: str) -> Optional[Workflow]:
        """Find workflow by natural language description"""
        description_lower = description.lower()

        # Check entry points
        for workflow in self.workflows.values():
            for entry_point in workflow.entry_points:
                if entry_point.lower() in description_lower:
                    return workflow

        # Check descriptions
        for workflow in self.workflows.values():
            if workflow.description.lower() in description_lower:
                return workflow

        return None

    def execute(
        self, identifier: str, context: Dict[str, Any] = None, dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a workflow by ID, alias, or description

        Returns execution result with status and outputs
        """
        # Try to get workflow directly
        workflow = self.get_workflow(identifier)

        # If not found, try natural language search
        if not workflow:
            workflow = self.find_workflow(identifier)

        if not workflow:
            return {"success": False, "error": f"Workflow not found: {identifier}"}

        print(f"\n{'='*60}")
        print(f"EXECUTING WORKFLOW: {workflow.name}")
        print(f"{'='*60}")
        print(f"Description: {workflow.description}")
        print(f"Frequency: {workflow.frequency.value}")
        print(f"Steps: {len(workflow.steps)}")

        if dry_run:
            print("\n[DRY RUN MODE - No commands will be executed]")
            for i, step in enumerate(workflow.steps, 1):
                print(f"\n{i}. {step.action}")
                if step.command:
                    print(f"   Command: {step.command}")
                if step.uses:
                    print(f"   Uses: {step.uses}")
                if step.outputs:
                    print(f"   Outputs: {', '.join(step.outputs)}")
            return {"success": True, "dry_run": True}

        # Execute workflow
        context = context or {}
        context["working_dir"] = str(self.workspace_dir)

        results = []
        for i, step in enumerate(workflow.steps, 1):
            print(f"\n[Step {i}/{len(workflow.steps)}] {step.action}")

            result = step.execute(context)
            results.append(
                {
                    "step_id": step.id,
                    "action": step.action,
                    "status": step.status.value,
                    "result": result,
                }
            )

            if not result["success"] and not step.optional:
                print(f"  ✗ Failed: {result.get('error', 'Unknown error')}")
                print(f"\n{'='*60}")
                print(f"WORKFLOW FAILED at step: {step.action}")
                print(f"{'='*60}")

                # Save failure state
                self._save_workflow_state(workflow, results, success=False)

                return {
                    "success": False,
                    "workflow_id": workflow.workflow_id,
                    "failed_step": step.id,
                    "error": result.get("error"),
                    "results": results,
                }
            elif result["success"]:
                print(f"  ✓ Completed")
            else:
                print(f"  ⊘ Skipped (optional)")

        print(f"\n{'='*60}")
        print(f"WORKFLOW COMPLETED: {workflow.name}")
        print(f"{'='*60}")

        # Save success state
        self._save_workflow_state(workflow, results, success=True)

        return {"success": True, "workflow_id": workflow.workflow_id, "results": results}

    def execute_chain(
        self, workflow_ids: List[str], context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute multiple workflows in sequence"""
        print(f"\n{'#'*60}")
        print(f"EXECUTING WORKFLOW CHAIN")
        print(f"{'#'*60}")
        print(f"Workflows: {' → '.join(workflow_ids)}")

        context = context or {}
        chain_results = []

        for workflow_id in workflow_ids:
            result = self.execute(workflow_id, context=context)
            chain_results.append(result)

            if not result["success"]:
                print(f"\n{'#'*60}")
                print(f"CHAIN ABORTED at: {workflow_id}")
                print(f"{'#'*60}")

                return {"success": False, "aborted_at": workflow_id, "chain_results": chain_results}

            # Pass outputs to next workflow in chain
            if "results" in result:
                for step_result in result["results"]:
                    context.update(step_result.get("result", {}))

        print(f"\n{'#'*60}")
        print(f"WORKFLOW CHAIN COMPLETED")
        print(f"{'#'*60}")

        return {"success": True, "chain_results": chain_results}

    def list_workflows(
        self, frequency: Optional[WorkflowFrequency] = None, category: Optional[str] = None
    ) -> List[Workflow]:
        """List available workflows with optional filtering"""
        # Get unique workflows (remove duplicates from aliases)
        unique_workflows = {}
        for workflow in self.workflows.values():
            unique_workflows[workflow.workflow_id] = workflow

        workflows = list(unique_workflows.values())

        if frequency:
            workflows = [w for w in workflows if w.frequency == frequency]

        if category:
            workflows = [w for w in workflows if w.category == category]

        return workflows

    def _save_workflow_state(self, workflow: Workflow, results: List[Dict], success: bool) -> None:
        """Save workflow execution state"""
        timestamp = datetime.now().isoformat()

        state = {
            "timestamp": timestamp,
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "success": success,
            "results": results,
        }

        # Save to file
        filename = f"{workflow.workflow_id}_{timestamp.replace(':', '-')}.json"
        filepath = self.workflow_state_dir / filename

        with open(filepath, "w") as f:
            json.dump(state, f, indent=2)

        # Update current symlink
        current_path = self.workflow_state_dir / "current.json"
        if current_path.exists() or current_path.is_symlink():
            current_path.unlink()

        try:
            current_path.symlink_to(filename)
        except OSError as e:
            logger.debug(f"OSError: {e}")
            logger.warning(f"OSError: {e}", exc_info=True)
            # On Windows, symlinks may fail, so just copy
            shutil.copy(filepath, current_path)

    def get_workflow_suggestions(self, current_state: Dict[str, Any]) -> List[Workflow]:
        """
        Suggest workflows based on current state

        Uses simple heuristics, but could integrate with physics orchestrator
        """
        suggestions = []

        # If recent commit, suggest audit
        if current_state.get("recent_commits"):
            audit_workflow = self.get_workflow("AUDIT_EXEC")
            if audit_workflow:
                suggestions.append(audit_workflow)

        # If low test coverage, suggest testing workflows
        if current_state.get("test_coverage", 100) < 70:
            test_workflow = self.get_workflow("TEST_COVERAGE")
            if test_workflow:
                suggestions.append(test_workflow)
            else:
                # Create a dynamic test improvement workflow using factory
                test_workflow = self._create_dynamic_workflow("test_coverage")
                suggestions.append(test_workflow)

        # If many unresolved issues, suggest self-healing
        if current_state.get("open_issues", 0) > 10:
            heal_workflow = self.get_workflow("SELF_HEAL")
            if heal_workflow:
                suggestions.append(heal_workflow)
            else:
                # Create a dynamic self-healing workflow using factory
                heal_workflow = self._create_dynamic_workflow("self_heal")
                suggestions.append(heal_workflow)

        return suggestions


# Example usage
if __name__ == "__main__":
    navigator = WorkflowNavigator()

    print("=" * 60)
    print("WORKFLOW NAVIGATOR DEMONSTRATION")
    print("=" * 60)

    # List all workflows
    print("\nAvailable Workflows:")
    for workflow in navigator.list_workflows():
        print(f"  {workflow.workflow_id:15s} - {workflow.name} ({workflow.frequency.value})")

    # Execute workflow in dry-run mode
    print("\n" + "=" * 60)
    print("DRY RUN: Audit Execution Workflow")
    print("=" * 60)
    result = navigator.execute("audit", dry_run=True)

    # Find workflow by description
    print("\n" + "=" * 60)
    print("FINDING WORKFLOW BY DESCRIPTION")
    print("=" * 60)
    workflow = navigator.find_workflow("Run audit pipeline")
    if workflow:
        print(f"Found: {workflow.name}")
        print(f"ID: {workflow.workflow_id}")
        print(f"Aliases: {', '.join(workflow.aliases)}")
