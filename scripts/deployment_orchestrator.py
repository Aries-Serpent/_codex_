#!/usr/bin/env python3
"""
Autonomous Deployment Orchestration Script for PR #2207

This script implements the 5-phase autonomous deployment workflow:
1. Pre-Deployment Verification
2. Merge Execution
3. Post-Merge Validation
4. Health Check & Validation
5. Notification & Documentation

Usage:
    python scripts/deployment_orchestrator.py --pr-number 2207 --dry-run
    python scripts/deployment_orchestrator.py --pr-number 2207 --execute

Author: Copilot Agent
Version: 1.0.0
"""

import argparse
import json
import logging
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class PhaseStatus(Enum):
    """Deployment phase status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class DeploymentPhase(Enum):
    """Deployment phases enumeration."""
    PHASE_1_PRE_DEPLOYMENT = "Phase 1: Pre-Deployment Verification"
    PHASE_2_MERGE = "Phase 2: Merge Execution"
    PHASE_3_POST_MERGE = "Phase 3: Post-Merge Validation"
    PHASE_4_HEALTH_CHECK = "Phase 4: Health Check & Validation"
    PHASE_5_NOTIFICATION = "Phase 5: Notification & Documentation"


@dataclass
class PhaseResult:
    """Result of a deployment phase."""
    phase: DeploymentPhase
    status: PhaseStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    details: Dict = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate phase duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


@dataclass
class DeploymentManifest:
    """Deployment execution manifest."""
    pr_number: int
    source_branch: str
    target_branch: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: PhaseStatus = PhaseStatus.PENDING
    phase_results: List[PhaseResult] = field(default_factory=list)
    merge_commit_sha: Optional[str] = None
    workflow_run_id: Optional[str] = None
    coverage_percentage: Optional[float] = None
    
    def to_dict(self) -> Dict:
        """Convert manifest to dictionary."""
        return {
            "pr_number": self.pr_number,
            "source_branch": self.source_branch,
            "target_branch": self.target_branch,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status.value,
            "phase_results": [
                {
                    "phase": result.phase.value,
                    "status": result.status.value,
                    "start_time": result.start_time.isoformat() if result.start_time else None,
                    "end_time": result.end_time.isoformat() if result.end_time else None,
                    "duration_seconds": result.duration_seconds,
                    "details": result.details,
                    "errors": result.errors,
                }
                for result in self.phase_results
            ],
            "merge_commit_sha": self.merge_commit_sha,
            "workflow_run_id": self.workflow_run_id,
            "coverage_percentage": self.coverage_percentage,
        }


class DeploymentOrchestrator:
    """Main orchestrator for autonomous deployment."""
    
    def __init__(self, pr_number: int, dry_run: bool = False, output_dir: Optional[Path] = None):
        """
        Initialize deployment orchestrator.
        
        Args:
            pr_number: Pull request number to deploy
            dry_run: If True, simulate without executing actual deployment
            output_dir: Directory for deployment artifacts
        """
        self.pr_number = pr_number
        self.dry_run = dry_run
        self.output_dir = output_dir or Path(".codex/deployments")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up logging
        self.logger = self._setup_logging()
        
        # Initialize manifest
        self.manifest = DeploymentManifest(
            pr_number=pr_number,
            source_branch="",  # Will be detected
            target_branch="main",
            started_at=datetime.now(timezone.utc),
        )
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler
        log_file = self.output_dir / f"deployment_{self.pr_number}_{int(time.time())}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def run_command(self, cmd: List[str], check: bool = True) -> Tuple[int, str, str]:
        """
        Run shell command and return results.
        
        Args:
            cmd: Command to run as list of strings
            check: If True, raise exception on non-zero exit code
            
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        self.logger.debug(f"Running command: {' '.join(cmd)}")
        
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would execute: {' '.join(cmd)}")
            return (0, f"[DRY RUN] Command: {' '.join(cmd)}", "")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=check,
            )
            return (result.returncode, result.stdout, result.stderr)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {e}")
            return (e.returncode, e.stdout, e.stderr)
    
    def phase_1_pre_deployment_verification(self) -> PhaseResult:
        """
        Phase 1: Pre-Deployment Verification
        
        Tasks:
        1. Validate workflow YAML syntax
        2. Run security pre-flight check
        3. Verify merge state
        4. Confirm all status checks passing
        5. Generate pre-check report
        """
        phase = DeploymentPhase.PHASE_1_PRE_DEPLOYMENT
        result = PhaseResult(phase=phase, status=PhaseStatus.IN_PROGRESS)
        result.start_time = datetime.now(timezone.utc)
        
        self.logger.info(f"Starting {phase.value}")
        
        try:
            # Task 1: Validate workflow YAML syntax
            self.logger.info("Task 1.1: Validating workflow YAML syntax")
            workflow_file = Path(".github/workflows/post-merge-validation-optimized.yml")
            
            if workflow_file.exists():
                exit_code, stdout, stderr = self.run_command([
                    "yamllint", "-c", ".yamllint.yml", str(workflow_file)
                ], check=False)
                
                if exit_code == 0:
                    result.details["yaml_validation"] = "PASS"
                    self.logger.info("✓ YAML validation passed")
                else:
                    result.details["yaml_validation"] = "FAIL"
                    result.errors.append(f"YAML validation failed: {stderr}")
                    self.logger.warning(f"YAML validation issues: {stderr}")
            else:
                result.details["yaml_validation"] = "SKIPPED"
                self.logger.warning(f"Workflow file not found: {workflow_file}")
            
            # Task 2: Run security pre-flight check
            self.logger.info("Task 1.2: Running security pre-flight check")
            exit_code, stdout, stderr = self.run_command([
                "bandit", "-r", "src/", "--severity-level=HIGH", "-f", "json"
            ], check=False)
            
            if exit_code == 0 or "No issues identified" in stdout:
                result.details["security_scan"] = "PASS"
                result.details["security_issues"] = 0
                self.logger.info("✓ Security scan passed - no HIGH/CRITICAL issues")
            else:
                try:
                    bandit_data = json.loads(stdout) if stdout else {}
                    issues = len(bandit_data.get("results", []))
                    result.details["security_scan"] = "ISSUES_FOUND"
                    result.details["security_issues"] = issues
                    if issues > 0:
                        result.errors.append(f"Security scan found {issues} HIGH/CRITICAL issues")
                        self.logger.warning(f"Security scan found {issues} issues")
                except json.JSONDecodeError:
                    result.details["security_scan"] = "ERROR"
                    self.logger.error("Failed to parse bandit output")
            
            # Task 3: Verify merge state (requires gh CLI with auth)
            self.logger.info("Task 1.3: Verifying PR merge state")
            # Note: This would require GH_TOKEN to be set in environment
            # For now, we'll mark as skipped in dry-run or without token
            if self.dry_run or not self._check_gh_auth():
                result.details["merge_state"] = "SKIPPED"
                self.logger.info("PR merge state check skipped (requires GH_TOKEN)")
            else:
                exit_code, stdout, stderr = self.run_command([
                    "gh", "pr", "view", str(self.pr_number),
                    "--json", "mergeable,mergeStateStatus,state"
                ], check=False)
                
                if exit_code == 0:
                    try:
                        pr_data = json.loads(stdout)
                        result.details["pr_state"] = pr_data.get("state")
                        result.details["mergeable"] = pr_data.get("mergeable")
                        result.details["merge_state_status"] = pr_data.get("mergeStateStatus")
                        
                        if pr_data.get("mergeable") == "MERGEABLE":
                            result.details["merge_state"] = "PASS"
                            self.logger.info("✓ PR is mergeable")
                        else:
                            result.details["merge_state"] = "FAIL"
                            result.errors.append(f"PR not mergeable: {pr_data}")
                            self.logger.warning(f"PR not mergeable: {pr_data}")
                    except json.JSONDecodeError:
                        result.details["merge_state"] = "ERROR"
                        result.errors.append("Failed to parse PR data")
                else:
                    result.details["merge_state"] = "ERROR"
                    result.errors.append(f"Failed to get PR info: {stderr}")
            
            # Task 4: Confirm status checks (also requires gh CLI)
            self.logger.info("Task 1.4: Confirming status checks")
            if self.dry_run or not self._check_gh_auth():
                result.details["status_checks"] = "SKIPPED"
                self.logger.info("Status checks verification skipped (requires GH_TOKEN)")
            else:
                exit_code, stdout, stderr = self.run_command([
                    "gh", "pr", "view", str(self.pr_number),
                    "--json", "statusCheckRollup"
                ], check=False)
                
                if exit_code == 0:
                    try:
                        pr_data = json.loads(stdout)
                        checks = pr_data.get("statusCheckRollup", [])
                        failed_checks = [
                            c for c in checks 
                            if c.get("conclusion") not in ["SUCCESS", "NEUTRAL", "SKIPPED", None]
                        ]
                        
                        result.details["total_checks"] = len(checks)
                        result.details["failed_checks"] = len(failed_checks)
                        
                        if len(failed_checks) == 0:
                            result.details["status_checks"] = "PASS"
                            self.logger.info(f"✓ All {len(checks)} status checks passed")
                        else:
                            result.details["status_checks"] = "FAIL"
                            result.errors.append(f"{len(failed_checks)} status checks failed")
                            self.logger.warning(f"{len(failed_checks)} status checks failed")
                    except json.JSONDecodeError:
                        result.details["status_checks"] = "ERROR"
                        result.errors.append("Failed to parse status checks")
                else:
                    result.details["status_checks"] = "ERROR"
                    result.errors.append(f"Failed to get status checks: {stderr}")
            
            # Task 5: Generate pre-check report
            self.logger.info("Task 1.5: Generating pre-check report")
            report_file = self.output_dir / f"pre_check_report_{self.pr_number}.json"
            with open(report_file, "w") as f:
                json.dump(result.details, f, indent=2)
            result.details["report_file"] = str(report_file)
            self.logger.info(f"✓ Pre-check report generated: {report_file}")
            
            # Determine overall phase status
            if result.errors:
                result.status = PhaseStatus.FAILED
                self.logger.error(f"{phase.value} FAILED with {len(result.errors)} errors")
            else:
                result.status = PhaseStatus.SUCCESS
                self.logger.info(f"✓ {phase.value} COMPLETED SUCCESSFULLY")
            
        except Exception as e:
            result.status = PhaseStatus.FAILED
            result.errors.append(f"Phase exception: {str(e)}")
            self.logger.exception(f"{phase.value} failed with exception")
        
        result.end_time = datetime.now(timezone.utc)
        return result
    
    def phase_2_merge_execution(self) -> PhaseResult:
        """
        Phase 2: Merge Execution
        
        Tasks:
        1. Execute merge
        2. Log merge commit SHA
        3. Verify main branch updated
        4. Confirm PR marked as merged
        """
        phase = DeploymentPhase.PHASE_2_MERGE
        result = PhaseResult(phase=phase, status=PhaseStatus.IN_PROGRESS)
        result.start_time = datetime.now(timezone.utc)
        
        self.logger.info(f"Starting {phase.value}")
        
        try:
            if self.dry_run or not self._check_gh_auth():
                result.status = PhaseStatus.SKIPPED
                result.details["reason"] = "Dry run or missing GH_TOKEN"
                self.logger.info(f"{phase.value} SKIPPED - dry run or missing authentication")
            else:
                # Task 1: Execute merge
                self.logger.info("Task 2.1: Executing PR merge")
                exit_code, stdout, stderr = self.run_command([
                    "gh", "pr", "merge", str(self.pr_number), "--merge"
                ], check=False)
                
                if exit_code == 0:
                    result.details["merge_executed"] = "SUCCESS"
                    self.logger.info("✓ PR merge executed successfully")
                    
                    # Task 2: Log merge commit SHA
                    time.sleep(2)  # Give GitHub time to update
                    exit_code, stdout, stderr = self.run_command([
                        "gh", "pr", "view", str(self.pr_number),
                        "--json", "mergeCommit"
                    ], check=False)
                    
                    if exit_code == 0:
                        try:
                            pr_data = json.loads(stdout)
                            merge_sha = pr_data.get("mergeCommit", {}).get("oid")
                            self.manifest.merge_commit_sha = merge_sha
                            result.details["merge_commit_sha"] = merge_sha
                            self.logger.info(f"✓ Merge commit SHA: {merge_sha}")
                        except json.JSONDecodeError:
                            result.errors.append("Failed to get merge commit SHA")
                    
                    result.status = PhaseStatus.SUCCESS
                    self.logger.info(f"✓ {phase.value} COMPLETED SUCCESSFULLY")
                else:
                    result.status = PhaseStatus.FAILED
                    result.errors.append(f"Merge failed: {stderr}")
                    self.logger.error(f"Merge failed: {stderr}")
        
        except Exception as e:
            result.status = PhaseStatus.FAILED
            result.errors.append(f"Phase exception: {str(e)}")
            self.logger.exception(f"{phase.value} failed with exception")
        
        result.end_time = datetime.now(timezone.utc)
        return result
    
    def phase_3_post_merge_validation(self) -> PhaseResult:
        """
        Phase 3: Post-Merge Validation

        Tasks:
        1. Trigger post-merge validation workflow
        2. Monitor all jobs in real-time
        3. Collect test results, coverage metrics
        4. Report progress
        5. Aggregate final results
        """
        phase = DeploymentPhase.PHASE_3_POST_MERGE
        result = PhaseResult(phase=phase, status=PhaseStatus.IN_PROGRESS)
        result.start_time = datetime.now(timezone.utc)
        
        self.logger.info(f"Starting {phase.value}")
        
        try:
            if self.dry_run or not self._check_gh_auth():
                result.status = PhaseStatus.SKIPPED
                result.details["reason"] = "Dry run or missing GH_TOKEN"
                self.logger.info(f"{phase.value} SKIPPED - dry run or missing authentication")
            else:
                # Workflow should auto-trigger on merge to main
                # Monitor for workflow run
                self.logger.info("Waiting for post-merge workflow to trigger...")
                time.sleep(10)  # Give GitHub time to trigger workflow

                # Get latest workflow run
                exit_code, stdout, stderr = self.run_command([
                    "gh", "run", "list",
                    "--workflow=post-merge-validation-optimized.yml",
                    "--branch=main",
                    "--limit=1",
                    "--json", "databaseId,status,conclusion"
                ], check=False)

                if exit_code == 0:
                    try:
                        runs = json.loads(stdout)
                        if runs:
                            workflow_summary = runs[0]
                            run_id = workflow_summary.get("databaseId")
                            if run_id is None:
                                raise RuntimeError("Workflow run missing databaseId")
                            self.manifest.workflow_run_id = str(run_id)
                            result.details["workflow_run_id"] = run_id
                            result.details["workflow_status"] = workflow_summary.get("status")
                            result.details["workflow_conclusion"] = workflow_summary.get("conclusion")
                            self.logger.info(f"✓ Workflow run ID: {run_id}")

                            summary_status = workflow_summary.get("status")
                            summary_conclusion = workflow_summary.get("conclusion")
                            result.details["workflow_status"] = summary_status
                            result.details["workflow_conclusion"] = summary_conclusion

                            should_monitor = summary_status != "completed" or summary_conclusion is None
                            if should_monitor:
                                result.status = PhaseStatus.IN_PROGRESS
                                result.details["monitoring"] = (
                                    "Workflow monitoring required - run still in progress"
                                )
                                self.logger.info(
                                    "Workflow run %s is still in progress (status=%s); awaiting completion",
                                    run_id,
                                    summary_status,
                                )

                            try:
                                workflow_details = self._ensure_workflow_completion(
                                    run_id=run_id,
                                    initial_status=summary_status,
                                    initial_conclusion=summary_conclusion,
                                )
                            except TimeoutError as timeout_err:
                                result.status = PhaseStatus.FAILED
                                timeout_message = str(timeout_err)
                                result.errors.append(timeout_message)
                                result.details["timeout"] = True
                                self.logger.error(timeout_message)
                            except Exception as monitor_err:  # pylint: disable=broad-except
                                if should_monitor:
                                    result.status = PhaseStatus.IN_PROGRESS
                                    result.details.setdefault(
                                        "monitoring_error",
                                        str(monitor_err),
                                    )
                                    self.logger.info(
                                        "Workflow run %s monitoring deferred: %s",
                                        run_id,
                                        monitor_err,
                                    )
                                else:
                                    result.status = PhaseStatus.FAILED
                                    error_message = f"Failed to monitor workflow run {run_id}: {monitor_err}"
                                    result.errors.append(error_message)
                                    self.logger.error(error_message)
                            else:
                                result.details.update({
                                    "workflow_status": workflow_details.get("status"),
                                    "workflow_conclusion": workflow_details.get("conclusion"),
                                })
                                result.details["monitoring"] = "Workflow monitored until completion"

                                jobs = workflow_details.get("jobs") or []
                                if jobs:
                                    result.details["jobs"] = [
                                        {
                                            "name": job.get("name"),
                                            "status": job.get("status"),
                                            "conclusion": job.get("conclusion"),
                                        }
                                        for job in jobs
                                    ]

                                if (
                                    workflow_details.get("status") == "completed"
                                    and workflow_details.get("conclusion") == "success"
                                ):
                                    result.status = PhaseStatus.SUCCESS
                                    self.logger.info("✓ Post-merge validation workflow completed successfully")
                                else:
                                    result.status = PhaseStatus.FAILED
                                    conclusion = workflow_details.get("conclusion") or "unknown"
                                    result.errors.append(
                                        f"Workflow concluded with status={workflow_details.get('status')} conclusion={conclusion}"
                                    )

                                    failed_jobs = [
                                        job for job in (result.details.get("jobs") or [])
                                        if job.get("conclusion") not in (None, "success")
                                    ]
                                    if failed_jobs:
                                        result.details["failed_jobs"] = failed_jobs
                                    self.logger.error(
                                        "Post-merge validation workflow did not succeed; conclusion=%s",
                                        conclusion,
                                    )
                        else:
                            result.errors.append("No workflow run found")
                            result.status = PhaseStatus.FAILED
                    except json.JSONDecodeError:
                        result.errors.append("Failed to parse workflow data")
                        result.status = PhaseStatus.FAILED
                else:
                    result.errors.append(f"Failed to get workflow runs: {stderr}")
                    result.status = PhaseStatus.FAILED
        
        except Exception as e:
            result.status = PhaseStatus.FAILED
            result.errors.append(f"Phase exception: {str(e)}")
            self.logger.exception(f"{phase.value} failed with exception")
        
        result.end_time = datetime.now(timezone.utc)
        return result

    def _ensure_workflow_completion(
        self,
        run_id: int,
        initial_status: Optional[str] = None,
        initial_conclusion: Optional[str] = None,
        timeout_seconds: int = 1800,
        poll_interval_seconds: int = 30,
    ) -> Dict[str, Optional[object]]:
        """Poll the GitHub workflow run until completion or timeout."""

        if initial_status == "completed" and initial_conclusion is not None:
            return {
                "status": initial_status,
                "conclusion": initial_conclusion,
                "jobs": [],
            }

        deadline = datetime.now(timezone.utc) + timedelta(seconds=timeout_seconds)
        last_status: Optional[str] = initial_status

        while datetime.now(timezone.utc) < deadline:
            exit_code, stdout, stderr = self.run_command([
                "gh",
                "run",
                "view",
                str(run_id),
                "--json",
                "status,conclusion,jobs",
            ], check=False)

            if exit_code != 0:
                raise RuntimeError(f"Failed to view workflow run {run_id}: {stderr}")

            try:
                run_data = json.loads(stdout)
            except json.JSONDecodeError as decode_error:
                raise RuntimeError("Failed to parse workflow run details") from decode_error

            status = run_data.get("status")
            conclusion = run_data.get("conclusion")

            if status == "completed":
                return {
                    "status": status,
                    "conclusion": conclusion,
                    "jobs": run_data.get("jobs") or [],
                }

            if status != last_status:
                self.logger.info(
                    "Workflow run %s status changed to %s; waiting for completion...",
                    run_id,
                    status,
                )
                last_status = status

            time.sleep(poll_interval_seconds)

        raise TimeoutError(
            f"Workflow run {run_id} did not complete within {timeout_seconds} seconds"
        )
    
    def phase_4_health_check(self) -> PhaseResult:
        """
        Phase 4: Health Check & Validation
        
        Tasks:
        1. Verify main branch state
        2. Confirm all workflow artifacts present
        3. Validate no regressions
        4. Generate health check report
        5. Recommend production readiness
        """
        phase = DeploymentPhase.PHASE_4_HEALTH_CHECK
        result = PhaseResult(phase=phase, status=PhaseStatus.IN_PROGRESS)
        result.start_time = datetime.now(timezone.utc)
        
        self.logger.info(f"Starting {phase.value}")
        
        try:
            # Task 1: Verify main branch state
            self.logger.info("Task 4.1: Verifying main branch state")
            exit_code, stdout, stderr = self.run_command([
                "git", "rev-parse", "HEAD"
            ], check=False)
            
            if exit_code == 0:
                current_sha = stdout.strip()
                result.details["current_sha"] = current_sha
                self.logger.info(f"✓ Current HEAD: {current_sha}")
            
            # Task 2: Check for critical files
            self.logger.info("Task 4.2: Checking critical files")
            critical_files = [
                ".github/coverage_threshold.txt",
                ".github/workflows/post-merge-validation-optimized.yml",
                ".bandit.yaml",
            ]
            
            missing_files = []
            for file_path in critical_files:
                if not Path(file_path).exists():
                    missing_files.append(file_path)
            
            result.details["critical_files_check"] = {
                "total": len(critical_files),
                "missing": missing_files,
            }
            
            if missing_files:
                result.errors.append(f"Missing critical files: {missing_files}")
                self.logger.warning(f"Missing files: {missing_files}")
            else:
                self.logger.info("✓ All critical files present")
            
            # Task 3: Generate health check report
            self.logger.info("Task 4.3: Generating health check report")
            health_report = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "pr_number": self.pr_number,
                "merge_commit_sha": self.manifest.merge_commit_sha,
                "critical_files": result.details["critical_files_check"],
                "status": "HEALTHY" if not result.errors else "ISSUES_FOUND",
            }
            
            report_file = self.output_dir / f"health_check_report_{self.pr_number}.json"
            with open(report_file, "w") as f:
                json.dump(health_report, f, indent=2)
            
            result.details["health_report_file"] = str(report_file)
            self.logger.info(f"✓ Health check report generated: {report_file}")
            
            # Determine phase status
            if result.errors:
                result.status = PhaseStatus.FAILED
            else:
                result.status = PhaseStatus.SUCCESS
                self.logger.info(f"✓ {phase.value} COMPLETED SUCCESSFULLY")
        
        except Exception as e:
            result.status = PhaseStatus.FAILED
            result.errors.append(f"Phase exception: {str(e)}")
            self.logger.exception(f"{phase.value} failed with exception")
        
        result.end_time = datetime.now(timezone.utc)
        return result
    
    def phase_5_notification(self) -> PhaseResult:
        """
        Phase 5: Notification & Documentation

        Tasks:
        1. Create comprehensive deployment summary
        2. Generate release notes
        3. Archive deployment manifest
        4. Create follow-up tracking issues
        """
        phase = DeploymentPhase.PHASE_5_NOTIFICATION
        result = PhaseResult(phase=phase, status=PhaseStatus.IN_PROGRESS)
        result.start_time = datetime.now(timezone.utc)
        
        self.logger.info(f"Starting {phase.value}")
        
        try:
            # Task 1: Create deployment summary
            self.logger.info("Task 5.1: Creating deployment summary")
            summary = self._generate_deployment_summary()
            
            summary_file = self.output_dir / f"deployment_summary_{self.pr_number}.md"
            with open(summary_file, "w") as f:
                f.write(summary)
            
            result.details["summary_file"] = str(summary_file)
            self.logger.info(f"✓ Deployment summary created: {summary_file}")
            
            # Task 2: Archive deployment manifest
            self.logger.info("Task 5.2: Archiving deployment manifest")
            manifest_file = self.output_dir / f"deployment_manifest_{self.pr_number}.json"
            
            self.manifest.completed_at = datetime.now(timezone.utc)
            
            # Determine overall deployment status
            self.manifest.status = self._determine_overall_status()

            with open(manifest_file, "w") as f:
                json.dump(self.manifest.to_dict(), f, indent=2)

            result.details["manifest_file"] = str(manifest_file)
            self.logger.info(f"✓ Deployment manifest archived: {manifest_file}")

            result.status = PhaseStatus.SUCCESS
            if self.manifest.status == PhaseStatus.SUCCESS:
                self.logger.info(f"✓ {phase.value} COMPLETED SUCCESSFULLY")
            else:
                self.logger.info(
                    "✓ %s COMPLETED WITH OVERALL STATUS: %s",
                    phase.value,
                    self.manifest.status.value.upper(),
                )

        except Exception as e:
            result.status = PhaseStatus.FAILED
            result.errors.append(f"Phase exception: {str(e)}")
            self.logger.exception(f"{phase.value} failed with exception")
        
        result.end_time = datetime.now(timezone.utc)
        return result
    
    def _check_gh_auth(self) -> bool:
        """Check if GitHub CLI is authenticated."""
        exit_code, stdout, stderr = self.run_command(
            ["gh", "auth", "status"], check=False
        )
        return exit_code == 0

    def _determine_overall_status(self) -> PhaseStatus:
        """Aggregate phase results to determine overall deployment status."""
        statuses = [result.status for result in self.manifest.phase_results]

        if not statuses:
            return PhaseStatus.PENDING

        if any(status == PhaseStatus.FAILED for status in statuses):
            return PhaseStatus.FAILED

        if any(status == PhaseStatus.IN_PROGRESS for status in statuses):
            return PhaseStatus.IN_PROGRESS

        if any(status == PhaseStatus.SKIPPED for status in statuses):
            return PhaseStatus.SKIPPED

        return PhaseStatus.SUCCESS
    
    def _generate_deployment_summary(self) -> str:
        """Generate markdown deployment summary."""
        lines = [
            f"# Deployment Summary: PR #{self.pr_number}",
            "",
            f"**Started**: {self.manifest.started_at.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Completed**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Status**: {self.manifest.status.value.upper()}",
            "",
            "## Phase Results",
            "",
        ]
        
        for phase_result in self.manifest.phase_results:
            status_icon = "✓" if phase_result.status == PhaseStatus.SUCCESS else "✗"
            duration = f"{phase_result.duration_seconds:.1f}s" if phase_result.duration_seconds else "N/A"
            
            lines.append(f"### {status_icon} {phase_result.phase.value}")
            lines.append(f"- **Status**: {phase_result.status.value}")
            lines.append(f"- **Duration**: {duration}")
            
            if phase_result.errors:
                lines.append("- **Errors**:")
                for error in phase_result.errors:
                    lines.append(f"  - {error}")
            
            if phase_result.details:
                lines.append("- **Details**:")
                for key, value in phase_result.details.items():
                    lines.append(f"  - {key}: {value}")
            
            lines.append("")
        
        if self.manifest.merge_commit_sha:
            lines.append(f"## Merge Information")
            lines.append(f"- **Merge Commit SHA**: `{self.manifest.merge_commit_sha}`")
            lines.append("")
        
        return "\n".join(lines)
    
    def execute(self) -> bool:
        """
        Execute full deployment orchestration.
        
        Returns:
            True if deployment successful, False otherwise
        """
        self.logger.info("=" * 80)
        self.logger.info(f"DEPLOYMENT ORCHESTRATION STARTED FOR PR #{self.pr_number}")
        self.logger.info(f"Dry Run: {self.dry_run}")
        self.logger.info("=" * 80)
        
        try:
            # Execute each phase in sequence
            phases = [
                self.phase_1_pre_deployment_verification,
                self.phase_2_merge_execution,
                self.phase_3_post_merge_validation,
                self.phase_4_health_check,
                self.phase_5_notification,
            ]
            
            for phase_func in phases:
                result = phase_func()
                self.manifest.phase_results.append(result)

                # Check if we should halt on failure
                if result.status == PhaseStatus.FAILED:
                    self.logger.error(f"Phase failed: {result.phase.value}")
                    self.logger.error("DEPLOYMENT HALTED DUE TO PHASE FAILURE")

                    # Still run notification phase to document failure
                    if phase_func != self.phase_5_notification:
                        notification_result = self.phase_5_notification()
                        self.manifest.phase_results.append(notification_result)

                    self.manifest.status = self._determine_overall_status()
                    return False

                # Halt orchestration when a phase is still running
                if result.status == PhaseStatus.IN_PROGRESS:
                    self.logger.warning(
                        "%s still in progress; halting orchestration until completion",
                        result.phase.value,
                    )
                    self.manifest.status = self._determine_overall_status()
                    self.logger.info("=" * 80)
                    self.logger.info(
                        "DEPLOYMENT ORCHESTRATION PAUSED - AWAITING %s",
                        result.phase.value,
                    )
                    self.logger.info("=" * 80)
                    return False

                # Halt non-dry-run executions when a phase is skipped unexpectedly
                if result.status == PhaseStatus.SKIPPED and not self.dry_run:
                    self.logger.warning(
                        "%s reported SKIPPED; manual intervention required before continuing",
                        result.phase.value,
                    )
                    self.manifest.status = self._determine_overall_status()
                    self.logger.info("=" * 80)
                    self.logger.info(
                        "DEPLOYMENT ORCHESTRATION HALTED DUE TO SKIPPED PHASE",
                    )
                    self.logger.info("=" * 80)
                    return False

            overall_status = self._determine_overall_status()
            self.manifest.status = overall_status

            self.logger.info("=" * 80)
            if overall_status == PhaseStatus.SUCCESS:
                self.logger.info("DEPLOYMENT ORCHESTRATION COMPLETED SUCCESSFULLY")
                self.logger.info("=" * 80)
                return True

            if overall_status == PhaseStatus.SKIPPED and self.dry_run:
                self.logger.info("DEPLOYMENT ORCHESTRATION DRY RUN COMPLETED (PHASES SKIPPED)")
                self.logger.info("=" * 80)
                return True

            self.logger.warning(
                "DEPLOYMENT ORCHESTRATION COMPLETED WITH STATUS: %s",
                overall_status.value.upper(),
            )
            self.logger.info("=" * 80)
            return False
        
        except Exception as e:
            self.logger.exception("DEPLOYMENT ORCHESTRATION FAILED WITH EXCEPTION")
            
            # Try to run notification phase
            try:
                notification_result = self.phase_5_notification()
                self.manifest.phase_results.append(notification_result)
            except Exception:
                self.logger.exception("Failed to run notification phase")
            
            return False


def main():
    """Main entry point for deployment orchestrator."""
    parser = argparse.ArgumentParser(
        description="Autonomous Deployment Orchestration for PR #2207"
    )
    parser.add_argument(
        "--pr-number",
        type=int,
        required=True,
        help="Pull request number to deploy"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate deployment without executing actual operations"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for deployment artifacts (default: .codex/deployments)"
    )
    
    args = parser.parse_args()
    
    orchestrator = DeploymentOrchestrator(
        pr_number=args.pr_number,
        dry_run=args.dry_run,
        output_dir=args.output_dir,
    )
    
    success = orchestrator.execute()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
