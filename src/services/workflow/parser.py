"""YAML parser for GitHub Actions workflows.

Handles YAML parsing with edge cases like anchors, aliases, and multi-document files.
Extracts workflow metadata including triggers, inputs, jobs, and dependencies.
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import yaml

from .types import (
    InputType,
    TriggerType,
    WorkflowInput,
    WorkflowJob,
    WorkflowMetadata,
    WorkflowTrigger,
)

logger = logging.getLogger(__name__)


class WorkflowParser:
    """Parser for GitHub Actions workflow YAML files.

    Handles:
    - Standard YAML parsing
    - YAML anchors and aliases
    - Multi-document YAML files
    - Malformed YAML with graceful degradation
    - Extraction of triggers, inputs, jobs, dependencies
    """

    def __init__(self):
        """Initialize the parser."""
        self._cache: dict[Path, WorkflowMetadata] = {}

    def parse_file(self, file_path: Path, use_cache: bool = True) -> Optional[WorkflowMetadata]:
        """Parse a workflow file.

        Args:
            file_path: Path to the workflow YAML file.
            use_cache: Whether to use cached results.

        Returns:
            Parsed workflow metadata, or None if parsing failed.
        """
        if use_cache and file_path in self._cache:
            return self._cache[file_path]

        if not file_path.exists():
            logger.warning(f"Workflow file not found: {file_path}")
            return None

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            metadata = self.parse_content(content, file_path)
            if metadata and use_cache:
                self._cache[file_path] = metadata
            return metadata
        except FileNotFoundError as e:
            type(e).__name__
            logger.debug("FileNotFoundError: <ERROR_TYPE>")
            logger.warning("FileNotFoundError: <ERROR_TYPE>", exc_info=True)
            logger.error(f"Workflow file not found: {file_path}")
            return None
        except PermissionError as e:
            type(e).__name__
            logger.debug("PermissionError: <ERROR_TYPE>")
            logger.warning("PermissionError: <ERROR_TYPE>", exc_info=True)
            logger.error(f"Permission denied reading workflow: {file_path}")
            return None
        except UnicodeDecodeError as e:
            type(e).__name__
            logger.debug("UnicodeDecodeError: <ERROR_TYPE>")
            logger.error(f"Invalid UTF-8 encoding in {file_path}: <ERROR_TYPE>")
            return None
        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.error(f"Failed to parse workflow {file_path}: <ERROR_TYPE>", exc_info=True)
            return None

    def parse(self, content: str, file_path: Optional[Path] = None) -> Optional[WorkflowMetadata]:
        """Parse workflow YAML content (convenience method).

        Args:
            content: YAML content as string.
            file_path: Optional path to the workflow file (for metadata).

        Returns:
            Parsed workflow metadata, or None if parsing failed.

        Raises:
            ValueError: If YAML is invalid and cannot be parsed.
        """
        if file_path is None:
            file_path = Path("workflow.yml")
        try:
            # Parse YAML first to catch YAML errors
            data = yaml.safe_load(content)
            if not data or not isinstance(data, dict):
                raise ValueError("Invalid YAML: must be a dictionary")
            return self.parse_content(content, file_path)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML: {e}") from e

    def parse_content(self, content: str, file_path: Path) -> Optional[WorkflowMetadata]:
        """Parse workflow YAML content.

        Args:
            content: YAML content as string.
            file_path: Path to the workflow file (for metadata).

        Returns:
            Parsed workflow metadata, or None if parsing failed.
        """
        try:
            # Parse YAML with safe loader (supports anchors/aliases)
            data = yaml.safe_load(content)
            if not data or not isinstance(data, dict):
                logger.warning(f"Invalid workflow structure in {file_path}")
                return None

            # Extract basic metadata
            name = data.get("name", file_path.stem)

            # Parse triggers - 'on' is a YAML boolean keyword, so it might be under True
            on_config = data.get("on") or data.get(True) or {}
            triggers = self._parse_triggers(on_config)

            # Parse inputs (for workflow_dispatch)
            inputs = self._parse_inputs(on_config)

            # Parse jobs
            jobs = self._parse_jobs(data.get("jobs", {}))

            # Extract additional metadata
            permissions = data.get("permissions", {})
            if isinstance(permissions, str):
                permissions = {"default": permissions}

            env = data.get("env", {})
            if not isinstance(env, dict):
                env = {}

            concurrency = data.get("concurrency")

            # Determine workflow capabilities
            is_triggerable = any(t.type == TriggerType.WORKFLOW_DISPATCH for t in triggers)
            is_reusable = any(t.type == TriggerType.WORKFLOW_CALL for t in triggers)

            # Get file modification time
            last_modified = None
            if file_path.exists():
                last_modified = datetime.fromtimestamp(file_path.stat().st_mtime, tz=timezone.utc)

            return WorkflowMetadata(
                name=name,
                file_path=file_path,
                triggers=triggers,
                inputs=inputs,
                jobs=jobs,
                dependencies=[],  # Dependencies calculated separately
                permissions=permissions,
                env=env,
                concurrency=concurrency,
                is_reusable=is_reusable,
                is_triggerable=is_triggerable,
                last_modified=last_modified,
            )
        except yaml.YAMLError as e:
            type(e).__name__
            logger.error(f"YAML parsing error in {file_path}: <ERROR_TYPE>")
            logger.debug(f"Problematic content near error: {content[:200]}...")
            return None
        except KeyError as e:
            type(e).__name__
            logger.debug("KeyError: <ERROR_TYPE>")
            logger.error(f"Missing required field in {file_path}: <ERROR_TYPE>")
            return None
        except ValueError as e:
            type(e).__name__
            logger.debug("ValueError: <ERROR_TYPE>")
            logger.error(f"Invalid value in {file_path}: <ERROR_TYPE>")
            return None
        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.error(f"Unexpected error parsing {file_path}: <ERROR_TYPE>", exc_info=True)
            return None

    def _parse_triggers(self, on_config: Any) -> list[WorkflowTrigger]:
        """Parse trigger configuration.

        Args:
            on_config: The 'on' section of the workflow.

        Returns:
            list of parsed triggers.
        """
        triggers: list[WorkflowTrigger] = []

        if not on_config:
            return triggers

        # Handle string format (single trigger)
        if isinstance(on_config, str):
            trigger_type = self._get_trigger_type(on_config)
            triggers.append(
                WorkflowTrigger(
                    type=trigger_type,
                    branches=None,
                    paths=None,
                    types=None,
                    schedule_cron=None,
                    workflows=None,
                )
            )
            return triggers

        # Handle list format
        if isinstance(on_config, list):
            for trigger_name in on_config:
                trigger_type = self._get_trigger_type(trigger_name)
                triggers.append(
                    WorkflowTrigger(
                        type=trigger_type,
                        branches=None,
                        paths=None,
                        types=None,
                        schedule_cron=None,
                        workflows=None,
                    )
                )
            return triggers

        # Handle dict format (with filters)
        if isinstance(on_config, dict):
            for trigger_name, config in on_config.items():
                trigger_type = self._get_trigger_type(trigger_name)

                # Parse trigger config
                branches = None
                paths = None
                types = None
                schedule_cron = None
                workflows = None

                # Schedule trigger - handle list of cron schedules
                if trigger_name == "schedule":
                    if isinstance(config, list):
                        schedule_cron = [
                            item.get("cron")
                            for item in config
                            if isinstance(item, dict) and "cron" in item
                        ]
                    elif isinstance(config, dict) and "cron" in config:
                        schedule_cron = [config["cron"]]
                elif isinstance(config, dict):
                    # Parse other trigger configurations
                    branches = config.get("branches", [])
                    if isinstance(branches, str):
                        branches = [branches]

                    paths = config.get("paths", [])
                    if isinstance(paths, str):
                        paths = [paths]

                    types = config.get("types", [])
                    if isinstance(types, str):
                        types = [types]

                    # Workflow dependencies
                    if trigger_name in ("workflow_run", "workflow_call"):
                        workflows = config.get("workflows", [])
                        if isinstance(workflows, str):
                            workflows = [workflows]

                triggers.append(
                    WorkflowTrigger(
                        type=trigger_type,
                        branches=branches if branches else None,
                        paths=paths if paths else None,
                        types=types if types else None,
                        schedule_cron=(
                            [s for s in schedule_cron if s is not None] if schedule_cron else None
                        ),
                        workflows=workflows,
                    )
                )

        return triggers

    def _parse_inputs(self, on_config: Any) -> dict[str, WorkflowInput]:
        """Parse workflow_dispatch inputs.

        Args:
            on_config: The 'on' section of the workflow.

        Returns:
            Dictionary of input name to WorkflowInput.
        """
        inputs: dict[str, WorkflowInput] = {}

        if not isinstance(on_config, dict):
            return inputs

        workflow_dispatch = on_config.get("workflow_dispatch", {})
        if not isinstance(workflow_dispatch, dict):
            return inputs

        input_defs = workflow_dispatch.get("inputs", {})
        if not isinstance(input_defs, dict):
            return inputs

        for input_name, input_config in input_defs.items():
            if not isinstance(input_config, dict):
                continue

            # Parse input type
            input_type_str = input_config.get("type", "string").lower()
            try:
                input_type = InputType(input_type_str)
            except ValueError as e:
                type(e).__name__
                logger.debug("ValueError: <ERROR_TYPE>")
                logger.warning("ValueError: <ERROR_TYPE>", exc_info=True)
                input_type = InputType.STRING

            # Parse options (for choice type)
            options = input_config.get("options")
            if options and not isinstance(options, list):
                options = None

            # Parse default value
            default = input_config.get("default")

            inputs[input_name] = WorkflowInput(
                name=input_name,
                description=input_config.get("description"),
                required=input_config.get("required", False),
                type=input_type,
                default=default,
                options=options,
            )

        return inputs

    def _parse_jobs(self, jobs_config: dict[str, Any]) -> dict[str, WorkflowJob]:
        """Parse job definitions.

        Args:
            jobs_config: The 'jobs' section of the workflow.

        Returns:
            Dictionary of job ID to WorkflowJob.
        """
        jobs = {}

        if not isinstance(jobs_config, dict):
            return jobs

        for job_id, job_config in jobs_config.items():
            if not isinstance(job_config, dict):
                continue

            # Parse runs-on
            runs_on = job_config.get("runs-on", "ubuntu-latest")

            # Parse needs (job dependencies)
            needs = job_config.get("needs")
            if needs:
                if isinstance(needs, str):
                    needs = [needs]
                elif not isinstance(needs, list):
                    needs = None

            # Count steps
            steps = job_config.get("steps", [])
            step_count = len(steps) if isinstance(steps, list) else 0

            # Parse timeout
            timeout_minutes = job_config.get("timeout-minutes")

            # Check if it's a reusable workflow call
            uses = job_config.get("uses")

            jobs[job_id] = WorkflowJob(
                id=job_id,
                name=job_config.get("name", job_id),
                runs_on=runs_on,
                needs=needs,
                **{"if": job_config.get("if")},  # Use alias directly
                steps=step_count,
                timeout_minutes=timeout_minutes,
                uses=uses,
            )

        return jobs

    def _get_trigger_type(self, trigger_name: str) -> TriggerType:
        """Map trigger name to TriggerType enum.

        Args:
            trigger_name: Trigger name from YAML.

        Returns:
            Corresponding TriggerType.
        """
        trigger_map = {
            "workflow_dispatch": TriggerType.WORKFLOW_DISPATCH,
            "push": TriggerType.PUSH,
            "pull_request": TriggerType.PULL_REQUEST,
            "schedule": TriggerType.SCHEDULE,
            "workflow_call": TriggerType.WORKFLOW_CALL,
            "workflow_run": TriggerType.WORKFLOW_RUN,
            "repository_dispatch": TriggerType.REPOSITORY_DISPATCH,
            "release": TriggerType.RELEASE,
            "create": TriggerType.CREATE,
            "delete": TriggerType.DELETE,
            "fork": TriggerType.FORK,
            "issues": TriggerType.ISSUES,
            "issue_comment": TriggerType.ISSUE_COMMENT,
            "pull_request_target": TriggerType.PULL_REQUEST_TARGET,
            "pull_request_review": TriggerType.PULL_REQUEST_REVIEW,
            "pull_request_review_comment": TriggerType.PULL_REQUEST_REVIEW_COMMENT,
            "registry_package": TriggerType.REGISTRY_PACKAGE,
            "watch": TriggerType.WATCH,
        }
        return trigger_map.get(trigger_name, TriggerType.OTHER)

    def clear_cache(self) -> None:
        """Clear the parser cache."""
        self._cache.clear()
