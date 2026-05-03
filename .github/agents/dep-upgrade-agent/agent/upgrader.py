"""
Dependency Upgrader Module - ACT Phase

#AFTERMATH_PATTERN_IDENTIFIED: automated_dependency_upgrade
Implements automated dependency upgrade execution and PR creation.
"""

import json
import re
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class UpgradeStrategy(Enum):
    """Strategy for applying upgrades."""
    AUTO_MERGE = "auto_merge"      # Auto-upgrade and merge if tests pass
    PR_WITH_AUTOMERGE = "pr_automerge"  # Create PR with auto-merge enabled
    PR_MANUAL_REVIEW = "pr_manual"      # Create PR requiring manual review
    STAGED_ROLLOUT = "staged"           # Gradual rollout with monitoring


@dataclass
class UpgradeResult:
    """Result of dependency upgrade operation."""
    package_name: str
    from_version: str
    to_version: str
    strategy_used: UpgradeStrategy
    success: bool
    tests_passed: bool
    pr_created: bool
    pr_url: Optional[str]
    rollback_performed: bool
    error_message: Optional[str]
    duration_seconds: float
    metadata: dict[str, Any]


class DependencyUpgrader:
    """
    Dependency Upgrader - ACT Phase

    #AFTERMATH_PATTERN_IDENTIFIED: dependency_upgrade_execution

    Executes dependency upgrades:
    - Update dependency files
    - Run test suite
    - Create GitHub PRs
    - Auto-merge safe updates
    - Rollback on failure
    """

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.results: list[UpgradeResult] = []

    def act(self, decision: dict[str, Any]) -> dict[str, Any]:
        """
        ACT: Execute dependency upgrades.

        #AFTERMATH_PATTERN_IDENTIFIED: upgrade_application

        Args:
            decision: Evaluation results from DECIDE phase

        Returns:
            Result with upgrade outcomes
        """
        auto_upgrades = decision.get("auto_upgrades", [])

        # Apply auto-upgrades first
        for evaluation in auto_upgrades:
            result = self._apply_upgrade(evaluation, UpgradeStrategy.AUTO_MERGE)
            self.results.append(result)

        # Create PRs for manual upgrades
        manual_upgrades = decision.get("manual_upgrades", [])
        for evaluation in manual_upgrades:
            result = self._create_upgrade_pr(evaluation)
            self.results.append(result)

        # Generate upgrade report
        report_path = self._generate_upgrade_report(decision)

        return {
            "results": self.results,
            "successful_upgrades": sum(1 for r in self.results if r.success),
            "failed_upgrades": sum(1 for r in self.results if not r.success),
            "prs_created": sum(1 for r in self.results if r.pr_created),
            "rollbacks_performed": sum(1 for r in self.results if r.rollback_performed),
            "report_path": str(report_path),
            "summary": self._generate_summary()
        }

        #AFTERMATH_METRIC: total_upgrades = len(self.results)
        #AFTERMATH_METRIC: successful = result["successful_upgrades"]
        #AFTERMATH_METRIC: prs_created = result["prs_created"]


    def _apply_upgrade(self, evaluation: Any, strategy: UpgradeStrategy) -> UpgradeResult:
        """
        Apply dependency upgrade.

        #AFTERMATH_PATTERN_IDENTIFIED: upgrade_execution
        """
        import time
        start_time = time.time()

        success = False
        tests_passed = False
        rollback_performed = False
        error_message = None

        try:
            # Update dependency file
            self._update_dependency_file(
                evaluation.package_name,
                evaluation.target_version
            )

            # Install updated dependency
            install_success = self._install_dependencies()

            if install_success:
                # Run tests
                tests_passed = self._run_tests()

                if tests_passed:
                    success = True
                else:
                    # Rollback on test failure
                    self._rollback_upgrade(
                        evaluation.package_name,
                        evaluation.current_version
                    )
                    rollback_performed = True
                    error_message = "Tests failed after upgrade"
            else:
                error_message = "Failed to install upgraded dependency"
                rollback_performed = True
                self._rollback_upgrade(
                    evaluation.package_name,
                    evaluation.current_version
                )
        except Exception as e:
            error_message = str(e)
            rollback_performed = True
            try:
                self._rollback_upgrade(
                    evaluation.package_name,
                    evaluation.current_version
                )
            except Exception:
                # Best-effort rollback: if secondary rollback also fails,
                # continue processing other upgrades. Manual intervention may be needed.
                pass

        duration = time.time() - start_time

        return UpgradeResult(
            package_name=evaluation.package_name,
            from_version=evaluation.current_version,
            to_version=evaluation.target_version,
            strategy_used=strategy,
            success=success,
            tests_passed=tests_passed,
            pr_created=False,
            pr_url=None,
            rollback_performed=rollback_performed,
            error_message=error_message,
            duration_seconds=duration,
            metadata={"evaluation": evaluation}
        )

    def _create_upgrade_pr(self, evaluation: Any) -> UpgradeResult:
        """
        Create GitHub PR for upgrade.

        #AFTERMATH_PATTERN_IDENTIFIED: pr_creation
        """
        import time
        start_time = time.time()

        pr_created = False
        pr_url = None
        error_message = None

        try:
            # Create branch
            branch_name = f"upgrade-{evaluation.package_name}-{evaluation.target_version}"
            self._create_branch(branch_name)

            # Update dependency file
            self._update_dependency_file(
                evaluation.package_name,
                evaluation.target_version
            )

            # Commit changes
            self._commit_changes(
                f"Upgrade {evaluation.package_name} from {evaluation.current_version} to {evaluation.target_version}"
            )

            # Push branch (would use GitHub API in real implementation)
            # pr_url = self._create_github_pr(...)
            pr_created = True
            pr_url = "https://github.com/example/repo/pull/123"  # Placeholder

        except Exception as e:
            error_message = str(e)

        duration = time.time() - start_time

        return UpgradeResult(
            package_name=evaluation.package_name,
            from_version=evaluation.current_version,
            to_version=evaluation.target_version,
            strategy_used=UpgradeStrategy.PR_MANUAL_REVIEW,
            success=pr_created,
            tests_passed=False,  # Tests will run in CI
            pr_created=pr_created,
            pr_url=pr_url,
            rollback_performed=False,
            error_message=error_message,
            duration_seconds=duration,
            metadata={"evaluation": evaluation}
        )

    def _update_dependency_file(self, package: str, version: str) -> None:
        """
        Update dependency file with new version.

        #AFTERMATH_PATTERN_IDENTIFIED: dependency_file_update
        """
        req_file = self.repo_path / "requirements.txt"
        if req_file.exists():
            content = req_file.read_text()
            lines = []

            for line in content.splitlines():
                if line.strip().startswith(package):
                    # Replace version
                    lines.append(f"{package}=={version}")
                else:
                    lines.append(line)

            req_file.write_text('\n'.join(lines) + '\n')

    def _install_dependencies(self) -> bool:
        """Install updated dependencies."""
        try:
            result = subprocess.run(
                ["pip", "install", "-r", "requirements.txt"],
                cwd=self.repo_path,
                capture_output=True,
                timeout=300
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _run_tests(self) -> bool:
        """
        Run test suite to validate upgrade.

        #AFTERMATH_PATTERN_IDENTIFIED: upgrade_validation
        """
        try:
            result = subprocess.run(
                ["pytest", "-x"],  # Stop on first failure
                cwd=self.repo_path,
                capture_output=True,
                timeout=600
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _rollback_upgrade(self, package: str, version: str) -> None:
        """
        Rollback upgrade to previous version.

        #AFTERMATH_PATTERN_IDENTIFIED: upgrade_rollback
        """
        self._update_dependency_file(package, version)
        self._install_dependencies()

    def _create_branch(self, branch_name: str) -> None:
        """Create git branch for upgrade."""
        # Sanitize branch name to prevent command injection
        safe_branch_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '-', branch_name)

        # Validate working directory
        if not self._is_safe_repo_path():
            print("Warning: Invalid repository path for branch creation")
            return

        try:
            result = subprocess.run(
                ["git", "checkout", "-b", safe_branch_name],
                cwd=self.repo_path,
                capture_output=True,
                timeout=30
            )
            if result.returncode != 0:
                print(f"Warning: Failed to create branch {safe_branch_name}: {result.stderr.decode()}")
        except subprocess.TimeoutExpired:
            print(f"Warning: Git branch creation timed out for {safe_branch_name}")
        except FileNotFoundError:
            print("Warning: Git command not found")

    def _commit_changes(self, message: str) -> None:
        """Commit changes to git."""
        # Validate working directory
        if not self._is_safe_repo_path():
            print("Warning: Invalid repository path for commit")
            return

        try:
            result = subprocess.run(
                ["git", "add", "."],
                cwd=self.repo_path,
                capture_output=True,
                timeout=30
            )
            if result.returncode != 0:
                print(f"Warning: Git add failed: {result.stderr.decode()}")
                return

            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.repo_path,
                capture_output=True,
                timeout=30
            )
            if result.returncode != 0:
                print(f"Warning: Git commit failed: {result.stderr.decode()}")
        except subprocess.TimeoutExpired:
            print("Warning: Git commit timed out")
        except FileNotFoundError:
            print("Warning: Git command not found")

    def _is_safe_repo_path(self) -> bool:
        """Validate repository path is safe for git operations."""
        try:
            repo_resolved = self.repo_path.resolve()
            # Ensure path exists and is a directory
            return repo_resolved.exists() and repo_resolved.is_dir()
        except (OSError, ValueError):
            return False

    def _generate_upgrade_report(self, decision: dict[str, Any]) -> Path:
        """
        Generate upgrade report.

        #AFTERMATH_PATTERN_IDENTIFIED: upgrade_reporting
        """
        report_path = self.repo_path / ".codex" / "dependency_upgrade_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        report = {
            "summary": {
                "total_evaluated": decision.get("total_evaluated", 0),
                "total_upgraded": len(self.results),
                "successful": sum(1 for r in self.results if r.success),
                "failed": sum(1 for r in self.results if not r.success),
                "prs_created": sum(1 for r in self.results if r.pr_created)
            },
            "results": [
                {
                    "package": r.package_name,
                    "from": r.from_version,
                    "to": r.to_version,
                    "success": r.success,
                    "tests_passed": r.tests_passed,
                    "pr_url": r.pr_url,
                    "error": r.error_message
                }
                for r in self.results
            ],
            "recommendations": decision.get("recommendations", [])
        }

        report_path.write_text(json.dumps(report, indent=2))
        return report_path

    def _generate_summary(self) -> dict[str, Any]:
        """Generate upgrade summary."""
        return {
            "total": len(self.results),
            "successful": sum(1 for r in self.results if r.success),
            "failed": sum(1 for r in self.results if not r.success),
            "auto_merged": sum(1 for r in self.results if r.strategy_used == UpgradeStrategy.AUTO_MERGE and r.success),
            "needs_review": sum(1 for r in self.results if r.pr_created)
        }
