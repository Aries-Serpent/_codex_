"""
CI/CD Workflow Refactoring Utility

Refactors GitHub Actions workflows to add workflow_dispatch triggers
for manual gating while keeping them in active .github/workflows/ directory.

Part of Phase 4: CI/CD Pipeline Refactoring

Note: Logging is configured using the standard logging module. For production use,
ensure logging is properly configured via logging.basicConfig() or a logging
configuration file before using this module.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Repository root
REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"


class WorkflowRefactorer:
    """
    Utility to refactor GitHub Actions workflows.

    Adds workflow_dispatch triggers and ensures runs-on: [self-hosted, linux]
    tags for cost control and compliance.
    """

    def __init__(self, workflows_dir: Optional[Path] = None):
        """
        Initialize workflow refactorer.

        Args:
            workflows_dir: Path to workflows directory
        """
        self.workflows_dir = workflows_dir or WORKFLOWS_DIR

        if not self.workflows_dir.exists():
            raise ValueError(f"Workflows directory not found: {self.workflows_dir}")

        logger.info(f"WorkflowRefactorer initialized: {self.workflows_dir}")

    def list_workflows(self) -> list[Path]:
        """
        List all workflow files.

        Returns:
            List of workflow file paths
        """
        workflows: list[Any] = []
        for ext in ["*.yml", "*.yaml"]:
            workflows.extend(self.workflows_dir.glob(ext))
            workflows.extend(self.workflows_dir.glob(f"**/{ext}"))

        return sorted(workflows)

    def add_workflow_dispatch(self, workflow_path: Path) -> bool:
        """
        Add workflow_dispatch trigger to workflow if not present.

        Args:
            workflow_path: Path to workflow file

        Returns:
            True if modified, False if already present
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False

        # Read workflow
        with open(workflow_path) as f:
            content = f.read()

        # Check if workflow_dispatch already exists
        if "workflow_dispatch" in content:
            logger.info(f"workflow_dispatch already present: {workflow_path.name}")
            return False

        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            type(e).__name__
            logger.error(f"Failed to parse {workflow_path.name}: <ERROR_TYPE>")
            return False

        if not isinstance(data, dict) or "on" not in data:
            logger.warning(f"Invalid workflow structure: {workflow_path.name}")
            return False

        # Add workflow_dispatch
        if isinstance(data["on"], dict):
            data["on"]["workflow_dispatch"] = None
        elif isinstance(data["on"], list):
            data["on"].append("workflow_dispatch")
        elif isinstance(data["on"], str):
            data["on"] = [data["on"], "workflow_dispatch"]
        else:
            logger.warning(f"Unknown 'on' type: {workflow_path.name}")
            return False

        # Write back
        with open(workflow_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

        logger.info(f"Added workflow_dispatch: {workflow_path.name}")
        return True

    def ensure_self_hosted_runner(self, workflow_path: Path) -> dict[str, Any]:
        """
        Ensure all jobs use [self-hosted, linux] runner.

        Args:
            workflow_path: Path to workflow file

        Returns:
            Dictionary with modification stats
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return {"modified": False, "error": "PyYAML not installed"}

        # Read workflow
        with open(workflow_path) as f:
            content = f.read()

        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            type(e).__name__
            logger.error(f"Failed to parse {workflow_path.name}: <ERROR_TYPE>")
            return {"modified": False, "error": str(e)}

        if not isinstance(data, dict) or "jobs" not in data:
            return {"modified": False, "reason": "No jobs found"}

        modified = False
        jobs_updated = []

        # Process each job
        for job_name, job_config in data["jobs"].items():
            if not isinstance(job_config, dict):
                continue

            runs_on = job_config.get("runs-on")

            # Check if already using self-hosted, linux
            if isinstance(runs_on, list):
                if "self-hosted" in runs_on and "linux" in runs_on:
                    continue  # Already correct
                # Update to [self-hosted, linux]
                job_config["runs-on"] = ["self-hosted", "linux"]
                modified = True
                jobs_updated.append(job_name)

            elif isinstance(runs_on, str):
                if runs_on not in ["self-hosted", "[self-hosted, linux]"]:
                    # Replace with [self-hosted, linux]
                    job_config["runs-on"] = ["self-hosted", "linux"]
                    modified = True
                    jobs_updated.append(job_name)

        if modified:
            # Write back
            with open(workflow_path, "w") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)

            logger.info(f"Updated runs-on for {workflow_path.name}: {', '.join(jobs_updated)}")

        return {
            "modified": modified,
            "jobs_updated": jobs_updated,
            "total_jobs": len(data["jobs"]),
        }

    def add_codex_digest_step(self, workflow_path: Path) -> bool:
        """
        Add codex_digest step to workflow if not present.

        Args:
            workflow_path: Path to workflow file

        Returns:
            True if modified, False otherwise
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return False

        # Read workflow
        with open(workflow_path) as f:
            content = f.read()

        # Check if codex_digest already present
        if "codex_digest" in content or "codex-digest" in content:
            logger.info(f"codex_digest already present: {workflow_path.name}")
            return False

        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            type(e).__name__
            logger.error(f"Failed to parse {workflow_path.name}: <ERROR_TYPE>")
            return False

        if not isinstance(data, dict) or "jobs" not in data:
            return False

        # Add codex_digest step to first job
        modified = False
        for job_name, job_config in data["jobs"].items():
            if not isinstance(job_config, dict) or "steps" not in job_config:
                continue

            # Add step
            digest_step = {
                "name": "Generate context digest",
                "run": "python -m codex_digest --output context_summary.md",
                "if": "always()",
            }

            job_config["steps"].append(digest_step)
            modified = True
            logger.info(f"Added codex_digest step to {job_name} in {workflow_path.name}")
            break  # Only add to first job

        if modified:
            # Write back
            with open(workflow_path, "w") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)

        return modified

    def refactor_all_workflows(
        self,
        add_dispatch: bool = True,
        ensure_self_hosted: bool = True,
        add_digest: bool = False,
    ) -> dict[str, Any]:
        """
        Refactor all workflows in directory.

        Args:
            add_dispatch: Add workflow_dispatch triggers
            ensure_self_hosted: Ensure self-hosted, linux runners
            add_digest: Add codex_digest steps

        Returns:
            Summary of changes
        """
        workflows = self.list_workflows()

        results: dict[str, Any] = {
            "total_workflows": len(workflows),
            "dispatch_added": 0,
            "runner_updated": 0,
            "digest_added": 0,
            "errors": [],
        }

        for workflow_path in workflows:
            try:
                if add_dispatch and self.add_workflow_dispatch(workflow_path):
                    results["dispatch_added"] += 1

                if ensure_self_hosted:
                    runner_result = self.ensure_self_hosted_runner(workflow_path)
                    if runner_result.get("modified"):
                        results["runner_updated"] += 1

                if add_digest and self.add_codex_digest_step(workflow_path):
                    results["digest_added"] += 1

            except (IOError, OSError) as e:
                type(e).__name__
                logger.error(f"Error processing {workflow_path.name}: <ERROR_TYPE>")
                results["errors"].append({"workflow": workflow_path.name, "error": str(e)})

        return results

    def validate_workflow(self, workflow_path: Path) -> dict[str, Any]:
        """
        Validate workflow file.

        Args:
            workflow_path: Path to workflow file

        Returns:
            Validation results
        """
        try:
            import yaml
        except ImportError:
            return {"valid": False, "error": "PyYAML not installed"}

        try:
            with open(workflow_path) as f:
                data = yaml.safe_load(f)

            # Basic validation
            if not isinstance(data, dict):
                return {"valid": False, "error": "Not a valid YAML dict"}

            if "on" not in data:
                return {"valid": False, "error": "Missing 'on' trigger"}

            if "jobs" not in data:
                return {"valid": False, "error": "Missing 'jobs' section"}

            # Check for workflow_dispatch
            has_dispatch = False
            if isinstance(data["on"], dict) or isinstance(data["on"], list):
                has_dispatch = "workflow_dispatch" in data["on"]

            # Check runner tags
            jobs_with_self_hosted = 0
            total_jobs = len(data["jobs"])

            for job_config in data["jobs"].values():
                if isinstance(job_config, dict):
                    runs_on = job_config.get("runs-on", [])
                    if isinstance(runs_on, list):
                        if "self-hosted" in runs_on and "linux" in runs_on:
                            jobs_with_self_hosted += 1

            return {
                "valid": True,
                "has_workflow_dispatch": has_dispatch,
                "total_jobs": total_jobs,
                "jobs_with_self_hosted": jobs_with_self_hosted,
                "compliance": jobs_with_self_hosted == total_jobs,
            }

        except Exception as e:
            return {"valid": False, "error": str(e)}


def refactor_workflows(
    add_dispatch: bool = True, ensure_self_hosted: bool = True, add_digest: bool = False
) -> dict[str, Any]:
    """
    Convenience function to refactor all workflows.

    Args:
        add_dispatch: Add workflow_dispatch triggers
        ensure_self_hosted: Ensure self-hosted, linux runners
        add_digest: Add codex_digest steps

    Returns:
        Summary of changes
    """
    refactorer = WorkflowRefactorer()
    return refactorer.refactor_all_workflows(
        add_dispatch=add_dispatch,
        ensure_self_hosted=ensure_self_hosted,
        add_digest=add_digest,
    )


if __name__ == "__main__":
    # Run refactoring when executed as script
    import json

    print("🔧 CI/CD Workflow Refactoring Utility\n")
    print("Scanning workflows...\n")

    results = refactor_workflows(
        add_dispatch=False,  # Dry run mode for safety
        ensure_self_hosted=False,
        add_digest=False,
    )

    print("Results:")
    print(json.dumps(results, indent=2))
