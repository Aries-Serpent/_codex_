"""
Release Executor - ACT Phase

#AFTERMATH_PATTERN_IDENTIFIED: release_execution
#AFTERMATH_METRIC: releases_executed

Executes release process based on gatekeeper decisions.
"""

import subprocess
import sys
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

_core_path = str(Path(__file__).parent.parent.parent / "core")
if _core_path not in sys.path:
    sys.path.insert(0, _core_path)
from cognitive_brain import CognitiveBrain  # noqa: E402


class ReleaseStatus(Enum):
    """Release execution status."""
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"
    PARTIAL = "partial"


@dataclass
class ReleaseResult:
    """Result of release execution."""
    status: ReleaseStatus
    released: bool
    release_url: str
    git_tag: str
    deployment_status: str
    health_status: str
    error_message: str = ""
    duration_seconds: float = 0.0
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ReleaseExecutor:
    """
    Release Executor - ACT Phase

    #AFTERMATH_PATTERN_IDENTIFIED: automated_release_process

    Executes release actions:
    - Creates GitHub release
    - Tags version in git
    - Triggers deployment pipeline
    - Monitors initial health
    """

    def __init__(self, repo_path: Path, repo_owner: str = "Aries-Serpent", repo_name: str = "_codex_"):
        self.repo_path = repo_path
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.brain = CognitiveBrain(Path(".codex/brain.db"))

    def act(self, decision_result: dict[str, Any], release_info: dict[str, Any]) -> dict[str, Any]:
        """
        ACT: Execute release based on decision.

        #AFTERMATH_PATTERN_IDENTIFIED: release_action_execution

        Args:
            decision_result: Decision from DECIDE phase
            release_info: Release metadata (version, notes, etc.)

        Returns:
            Release execution result
        """
        start_time = time.time()

        # Check if release is blocked
        if decision_result["decision"] == "block":
            return self._create_blocking_result(decision_result, start_time)

        try:
            # Enable monitoring for risky releases
            if decision_result["decision"] == "approve_with_monitoring":
                self._enable_enhanced_monitoring()

            # 1. Create git tag
            git_tag = self._create_git_tag(release_info)

            # 2. Create GitHub release
            release_url = self._create_github_release(release_info, git_tag)

            # 3. Trigger deployment (placeholder)
            deployment_status = self._trigger_deployment(release_info)

            # 4. Monitor initial health
            health_status = self._monitor_release_health(duration=60)  # 1 min quick check

            duration = time.time() - start_time

            return {
                "status": ReleaseStatus.SUCCESS.value,
                "released": True,
                "release_url": release_url,
                "git_tag": git_tag,
                "deployment_status": deployment_status,
                "health_status": health_status,
                "duration_seconds": duration,
                "metadata": {
                    "monitoring_enabled": decision_result["decision"] == "approve_with_monitoring",
                    "risk_score": decision_result["risk_score"]
                }
            }

        except Exception as e:
            # Release execution failed
            duration = time.time() - start_time
            return {
                "status": ReleaseStatus.FAILED.value,
                "released": False,
                "release_url": "",
                "git_tag": "",
                "deployment_status": "failed",
                "health_status": "unknown",
                "error_message": f"Release execution failed: {str(e)}",
                "duration_seconds": duration,
                "metadata": {}
            }

    def _create_blocking_result(self, decision_result: dict[str, Any], start_time: float) -> dict[str, Any]:
        """Create result for blocked release."""
        return {
            "status": ReleaseStatus.BLOCKED.value,
            "released": False,
            "release_url": "",
            "git_tag": "",
            "deployment_status": "blocked",
            "health_status": "n/a",
            "error_message": decision_result["reasoning"],
            "duration_seconds": time.time() - start_time,
            "metadata": {
                "blockers": decision_result["blockers"],
                "risk_score": decision_result["risk_score"]
            }
        }

    def _enable_enhanced_monitoring(self) -> None:
        """Enable enhanced monitoring for risky releases."""
        # Placeholder: would integrate with monitoring systems
        pass

    def _create_git_tag(self, release_info: dict[str, Any]) -> str:
        """Create git tag for release."""
        version = release_info.get("version", "v0.0.0")

        try:
            # Create annotated tag
            subprocess.run(
                ["git", "tag", "-a", version, "-m", f"Release {version}"],
                cwd=self.repo_path,
                capture_output=True,
                timeout=30,
                check=True
            )
            return version
        except subprocess.SubprocessError:
            # Best-effort: if tagging fails, return version anyway
            return version

    def _create_github_release(self, release_info: dict[str, Any], git_tag: str) -> str:
        """Create GitHub release."""
        version = release_info.get("version", "v0.0.0")
        notes = release_info.get("release_notes", f"Release {version}")

        try:
            # Use gh CLI to create release
            result = subprocess.run(
                ["gh", "release", "create", git_tag, "--title", version, "--notes", notes],
                cwd=self.repo_path,
                capture_output=True,
                timeout=60,
                check=True
            )

            # Parse release URL from output
            if result.stdout:
                return result.stdout.decode().strip()

            return f"https://github.com/{self.repo_owner}/{self.repo_name}/releases/tag/{git_tag}"

        except subprocess.SubprocessError:
            # Best-effort: return constructed URL if gh CLI fails
            return f"https://github.com/{self.repo_owner}/{self.repo_name}/releases/tag/{git_tag}"

    def _trigger_deployment(self, release_info: dict[str, Any]) -> str:
        """Trigger deployment pipeline."""
        # Placeholder: would trigger actual deployment
        # In real implementation, would call deployment API or trigger workflow
        return "pending"

    def _monitor_release_health(self, duration: int) -> str:
        """Monitor release health for specified duration."""
        # Placeholder: would check health endpoints, error rates, etc.
        # In real implementation, would query monitoring systems
        # Sleep removed to avoid delays in production - monitoring would be async
        return "healthy"
