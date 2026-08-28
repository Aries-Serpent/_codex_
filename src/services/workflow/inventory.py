"""Workflow inventory management.

Scans .github/workflows directory, parses workflow files, and builds
a dependency graph. Supports caching and incremental updates.
"""

import logging
from pathlib import Path
from typing import Optional

from .parser import WorkflowParser
from .types import (
    InventoryStats,
    TriggerType,
    WorkflowDependency,
    WorkflowMetadata,
)

logger = logging.getLogger(__name__)


class WorkflowInventory:
    """Manages inventory of GitHub Actions workflows.

    Features:
    - Scans .github/workflows directory
    - Parses workflow YAML files
    - Builds dependency graph between workflows
    - Caches parsed results
    - Supports incremental updates

    Example:
        ```python
        inventory = WorkflowInventory(".github/workflows")
        inventory.scan()

        print(f"Found {len(inventory.workflows)} workflows")
        print(f"Triggerable: {len(inventory.get_triggerable())}")

        # Get specific workflow
        workflow = inventory.get_workflow("test-suite.yml")
        if workflow:
            print(f"Jobs: {workflow.job_ids}")
        ```
    """

    def __init__(self, workflows_dir: Path | str):
        """Initialize workflow inventory.

        Args:
            workflows_dir: Path to .github/workflows directory.
        """
        self.workflows_dir = Path(workflows_dir)
        self.parser = WorkflowParser()
        self._workflows: dict[str, WorkflowMetadata] = {}
        self._dependencies: list[WorkflowDependency] = []

    @property
    def workflows(self) -> dict[str, WorkflowMetadata]:
        """Get all parsed workflows."""
        return self._workflows

    @property
    def dependencies(self) -> list[WorkflowDependency]:
        """Get all workflow dependencies."""
        return self._dependencies

    def scan(self, force_refresh: bool = False) -> int:
        """Scan workflows directory and parse all workflow files.

        Args:
            force_refresh:  If True, clear cache and reparse everything.

        Returns:
            Number of workflows successfully parsed.
        """
        if force_refresh:
            self._workflows.clear()
            self.parser.clear_cache()

        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return 0

        parsed_count = 0
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        logger.info(f"Scanning {len(workflow_files)} workflow files in {self.workflows_dir}")

        for workflow_file in workflow_files:
            # Skip disabled workflows. GitHub Actions commonly uses a `.disabled`
            # suffix to archive workflows without removing them from the repo.
            if workflow_file.name.endswith(".disabled") or any(
                suffix == ".disabled" for suffix in workflow_file.suffixes
            ):
                logger.debug(f"Skipping disabled workflow:  {workflow_file.name}")
                continue

            try:
                metadata = self.parser.parse_file(workflow_file)
                if metadata:
                    self._workflows[workflow_file.name] = metadata
                    parsed_count += 1
                    logger.debug(f"Parsed workflow:  {workflow_file.name}")
                else:
                    logger.warning(f"Failed to parse workflow: {workflow_file.name}")
            except Exception:
                logger.exception(f"Error parsing workflow: {workflow_file.name}")

        # Build dependency graph
        self._build_dependency_graph()

        logger.info(
            f"Scanned {parsed_count} workflows, found {len(self._dependencies)} dependencies"
        )
        return parsed_count

    def get_workflow(self, filename: str) -> Optional[WorkflowMetadata]:
        """Get workflow metadata by filename.

        Args:
            filename: Workflow filename (e.g., "test-suite.yml")

        Returns:
            Workflow metadata, or None if not found.
        """
        return self._workflows.get(filename)

    def get_triggerable(self) -> list[WorkflowMetadata]:
        """Get all manually triggerable workflows (workflow_dispatch).

        Returns:
            list of workflows with workflow_dispatch trigger.
        """
        return [w for w in self._workflows.values() if w.is_triggerable]

    def get_reusable(self) -> list[WorkflowMetadata]:
        """Get all reusable workflows (workflow_call).

        Returns:
            list of workflows with workflow_call trigger.
        """
        return [w for w in self._workflows.values() if w.is_reusable]

    def get_by_trigger_type(self, trigger_type: TriggerType) -> list[WorkflowMetadata]:
        """Get workflows by trigger type.

        Args:
            trigger_type:  Trigger type to filter by.

        Returns:
            list of workflows with the specified trigger.
        """
        return [w for w in self._workflows.values() if trigger_type in w.trigger_types]

    def get_workflow_dependencies(self, filename: str) -> list[str]:
        """Get workflows that this workflow depends on.

        Args:
            filename:  Workflow filename.

        Returns:
            list of dependency workflow filenames.
        """
        return [dep.target for dep in self._dependencies if dep.source == filename]

    def get_workflow_dependents(self, filename: str) -> list[str]:
        """Get workflows that depend on this workflow.

        Args:
            filename:  Workflow filename.

        Returns:
            list of dependent workflow filenames.
        """
        return [dep.source for dep in self._dependencies if dep.target == filename]

    def get_stats(self) -> InventoryStats:
        """Get inventory statistics.

        Returns:
            Statistics about the workflow inventory.
        """
        trigger_counts: dict[str, int] = {}
        total_jobs = 0
        total_triggers = 0

        for workflow in self._workflows.values():
            total_jobs += len(workflow.jobs)
            total_triggers += len(workflow.triggers)

            for trigger in workflow.triggers:
                trigger_type = trigger.type.value
                trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 1

        return InventoryStats(
            total_workflows=len(self._workflows),
            triggerable_workflows=len(self.get_triggerable()),
            reusable_workflows=len(self.get_reusable()),
            total_jobs=total_jobs,
            total_triggers=total_triggers,
            trigger_type_counts=trigger_counts,
            dependency_count=len(self._dependencies),
        )

    def _build_dependency_graph(self) -> None:
        """Build dependency graph from workflow_run and workflow_call triggers."""
        self._dependencies.clear()

        for filename, workflow in self._workflows.items():
            for trigger in workflow.triggers:
                # workflow_run dependencies
                if trigger.type == TriggerType.WORKFLOW_RUN and trigger.workflows:
                    for dep_workflow in trigger.workflows:
                        # Try to find the actual workflow file
                        dep_filename = self._find_workflow_by_name(dep_workflow)
                        if dep_filename:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_RUN,
                                    required=True,
                                )
                            )

            # Check for workflow_call usage in jobs
            for job in workflow.jobs.values():
                if job.uses:
                    # Extract workflow reference (e.g., "./.github/workflows/reusable.yml")
                    if job.uses.startswith("./"):
                        # Local workflow reference
                        parts = job.uses.split("@")[0]  # Remove @ref if present
                        workflow_path = Path(parts.lstrip("./"))
                        dep_filename = workflow_path.name

                        if dep_filename in self._workflows:
                            self._dependencies.append(
                                WorkflowDependency(
                                    source=filename,
                                    target=dep_filename,
                                    trigger_type=TriggerType.WORKFLOW_CALL,
                                    required=True,
                                )
                            )

    def _find_workflow_by_name(self, workflow_name: str) -> Optional[str]:
        """Find workflow filename by workflow name.

        Args:
            workflow_name: Workflow name (from 'name' field).

        Returns:
            Workflow filename, or None if not found.
        """
        for filename, workflow in self._workflows.items():
            if workflow.name == workflow_name:
                return filename
        return None

    def list_workflows(self) -> list[str]:
        """list all workflow filenames.

        Returns:
            Sorted list of workflow filenames.
        """
        return sorted(self._workflows.keys())

    def refresh_workflow(self, filename: str) -> bool:
        """Refresh a single workflow file.

        Args:
            filename: Workflow filename to refresh.

        Returns:
            True if successfully refreshed, False otherwise.
        """
        workflow_path = self.workflows_dir / filename
        if not workflow_path.exists():
            logger.error(f"Workflow file not found: {workflow_path}")
            return False

        try:
            metadata = self.parser.parse_file(workflow_path, use_cache=False)
            if metadata:
                self._workflows[filename] = metadata
                self._build_dependency_graph()
                logger.info(f"Refreshed workflow: {filename}")
                return True
        except Exception:
            logger.exception(f"Error refreshing workflow: {filename}")

        return False
