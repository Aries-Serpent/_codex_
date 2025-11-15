"""
Unit tests for deployment orchestration script.

Tests the 5-phase autonomous deployment workflow for PR #2207.
"""

import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Import the deployment orchestrator module
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from deployment_orchestrator import (
    DeploymentManifest,
    DeploymentOrchestrator,
    DeploymentPhase,
    PhaseResult,
    PhaseStatus,
)


class TestPhaseResult:
    """Test PhaseResult dataclass."""
    
    def test_duration_calculation(self):
        """Test duration calculation between start and end times."""
        result = PhaseResult(
            phase=DeploymentPhase.PHASE_1_PRE_DEPLOYMENT,
            status=PhaseStatus.IN_PROGRESS,
        )
        
        # No times set
        assert result.duration_seconds is None
        
        # Set times
        result.start_time = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        result.end_time = datetime(2025, 1, 1, 12, 0, 5, tzinfo=timezone.utc)
        
        assert result.duration_seconds == 5.0
    
    def test_phase_result_creation(self):
        """Test PhaseResult creation with all fields."""
        result = PhaseResult(
            phase=DeploymentPhase.PHASE_2_MERGE,
            status=PhaseStatus.SUCCESS,
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc),
            details={"test": "value"},
            errors=["error1"],
        )
        
        assert result.phase == DeploymentPhase.PHASE_2_MERGE
        assert result.status == PhaseStatus.SUCCESS
        assert result.details["test"] == "value"
        assert len(result.errors) == 1


class TestDeploymentManifest:
    """Test DeploymentManifest dataclass."""
    
    def test_manifest_creation(self):
        """Test manifest creation with default values."""
        manifest = DeploymentManifest(
            pr_number=2207,
            source_branch="0D_base_",
            target_branch="main",
            started_at=datetime.now(timezone.utc),
        )
        
        assert manifest.pr_number == 2207
        assert manifest.source_branch == "0D_base_"
        assert manifest.target_branch == "main"
        assert manifest.status == PhaseStatus.PENDING
        assert len(manifest.phase_results) == 0
    
    def test_manifest_to_dict(self):
        """Test manifest conversion to dictionary."""
        manifest = DeploymentManifest(
            pr_number=2207,
            source_branch="0D_base_",
            target_branch="main",
            started_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        )
        
        manifest_dict = manifest.to_dict()
        
        assert manifest_dict["pr_number"] == 2207
        assert manifest_dict["source_branch"] == "0D_base_"
        assert manifest_dict["target_branch"] == "main"
        assert manifest_dict["status"] == "pending"
        assert isinstance(manifest_dict["phase_results"], list)


class TestDeploymentOrchestrator:
    """Test DeploymentOrchestrator class."""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def orchestrator(self, temp_output_dir):
        """Create orchestrator instance for testing."""
        return DeploymentOrchestrator(
            pr_number=2207,
            dry_run=True,
            output_dir=temp_output_dir,
        )

    @pytest.fixture
    def live_orchestrator(self, temp_output_dir):
        """Create a non-dry-run orchestrator instance for workflow monitoring tests."""
        return DeploymentOrchestrator(
            pr_number=2207,
            dry_run=False,
            output_dir=temp_output_dir,
        )
    
    def test_orchestrator_initialization(self, orchestrator, temp_output_dir):
        """Test orchestrator initialization."""
        assert orchestrator.pr_number == 2207
        assert orchestrator.dry_run is True
        assert orchestrator.output_dir == temp_output_dir
        assert orchestrator.manifest.pr_number == 2207
        assert orchestrator.manifest.target_branch == "main"
    
    def test_run_command_dry_run(self, orchestrator):
        """Test command execution in dry-run mode."""
        exit_code, stdout, stderr = orchestrator.run_command(["echo", "test"])
        
        assert exit_code == 0
        assert "[DRY RUN]" in stdout
        assert stderr == ""
    
    @patch('subprocess.run')
    def test_run_command_execution(self, mock_run, temp_output_dir):
        """Test actual command execution (non-dry-run)."""
        # Create non-dry-run orchestrator
        orchestrator = DeploymentOrchestrator(
            pr_number=2207,
            dry_run=False,
            output_dir=temp_output_dir,
        )
        
        # Mock successful command
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        exit_code, stdout, stderr = orchestrator.run_command(["echo", "test"])
        
        assert exit_code == 0
        assert stdout == "output"
        mock_run.assert_called_once()
    
    def test_phase_1_pre_deployment_verification(self, orchestrator):
        """Test Phase 1: Pre-Deployment Verification."""
        result = orchestrator.phase_1_pre_deployment_verification()
        
        assert result.phase == DeploymentPhase.PHASE_1_PRE_DEPLOYMENT
        assert result.status in [PhaseStatus.SUCCESS, PhaseStatus.FAILED]
        assert result.start_time is not None
        assert result.end_time is not None
        assert "yaml_validation" in result.details
        assert "security_scan" in result.details
    
    def test_phase_1_generates_report(self, orchestrator, temp_output_dir):
        """Test that Phase 1 generates a pre-check report."""
        orchestrator.phase_1_pre_deployment_verification()
        
        # Check report file was created
        report_file = temp_output_dir / "pre_check_report_2207.json"
        assert report_file.exists()
        
        # Verify report content
        with open(report_file) as f:
            report_data = json.load(f)
        
        assert "yaml_validation" in report_data
        assert "security_scan" in report_data
    
    def test_phase_2_merge_execution_dry_run(self, orchestrator):
        """Test Phase 2: Merge Execution in dry-run mode."""
        result = orchestrator.phase_2_merge_execution()
        
        assert result.phase == DeploymentPhase.PHASE_2_MERGE
        assert result.status == PhaseStatus.SKIPPED
        assert "Dry run" in result.details.get("reason", "")
    
    def test_phase_3_post_merge_validation_dry_run(self, orchestrator):
        """Test Phase 3: Post-Merge Validation in dry-run mode."""
        result = orchestrator.phase_3_post_merge_validation()

        assert result.phase == DeploymentPhase.PHASE_3_POST_MERGE
        assert result.status == PhaseStatus.SKIPPED
        assert "Dry run" in result.details.get("reason", "")

    @patch("scripts.deployment_orchestrator.time.sleep", return_value=None)
    def test_phase_3_post_merge_validation_success(
        self,
        mock_sleep,
        live_orchestrator,
    ):
        """Phase 3 should report success when workflow completes successfully."""

        del mock_sleep  # Unused but required by patch

        with patch.object(live_orchestrator, "_check_gh_auth", return_value=True), \
            patch.object(live_orchestrator, "run_command") as mock_run_cmd, \
            patch.object(
                live_orchestrator,
                "_ensure_workflow_completion",
                return_value={
                    "status": "completed",
                    "conclusion": "success",
                    "jobs": [
                        {"name": "tests", "status": "completed", "conclusion": "success"},
                    ],
                },
            ) as mock_wait:

            mock_run_cmd.return_value = (
                0,
                json.dumps([
                    {
                        "databaseId": 12345,
                        "status": "in_progress",
                        "conclusion": None,
                    }
                ]),
                "",
            )

            result = live_orchestrator.phase_3_post_merge_validation()

        assert result.status == PhaseStatus.SUCCESS
        assert result.details["workflow_run_id"] == 12345
        assert result.details["workflow_conclusion"] == "success"
        assert "failed_jobs" not in result.details
        mock_wait.assert_called_once()
        mock_run_cmd.assert_called_once()

    @patch("scripts.deployment_orchestrator.time.sleep", return_value=None)
    def test_phase_3_post_merge_validation_failure(
        self,
        mock_sleep,
        live_orchestrator,
    ):
        """Phase 3 should record failure when workflow concludes unsuccessfully."""

        del mock_sleep

        with patch.object(live_orchestrator, "_check_gh_auth", return_value=True), \
            patch.object(live_orchestrator, "run_command") as mock_run_cmd, \
            patch.object(
                live_orchestrator,
                "_ensure_workflow_completion",
                return_value={
                    "status": "completed",
                    "conclusion": "failure",
                    "jobs": [
                        {"name": "tests", "status": "completed", "conclusion": "failure"},
                        {"name": "lint", "status": "completed", "conclusion": "success"},
                    ],
                },
            ):

            mock_run_cmd.return_value = (
                0,
                json.dumps([
                    {
                        "databaseId": 999,
                        "status": "in_progress",
                        "conclusion": None,
                    }
                ]),
                "",
            )

            result = live_orchestrator.phase_3_post_merge_validation()

        assert result.status == PhaseStatus.FAILED
        assert result.details["workflow_run_id"] == 999
        assert result.details["workflow_conclusion"] == "failure"
        assert any(job["name"] == "tests" for job in result.details["failed_jobs"])
        assert result.errors

    @patch("scripts.deployment_orchestrator.time.sleep", return_value=None)
    def test_phase_3_post_merge_validation_timeout(
        self,
        mock_sleep,
        live_orchestrator,
    ):
        """Phase 3 should fail with timeout details when monitoring exceeds deadline."""

        del mock_sleep

        with patch.object(live_orchestrator, "_check_gh_auth", return_value=True), \
            patch.object(live_orchestrator, "run_command") as mock_run_cmd, \
            patch.object(
                live_orchestrator,
                "_ensure_workflow_completion",
                side_effect=TimeoutError("Workflow run 111 timed out"),
            ):

            mock_run_cmd.return_value = (
                0,
                json.dumps([
                    {
                        "databaseId": 111,
                        "status": "in_progress",
                        "conclusion": None,
                    }
                ]),
                "",
            )

            result = live_orchestrator.phase_3_post_merge_validation()

        assert result.status == PhaseStatus.FAILED
        assert result.details.get("timeout") is True
        assert any("timed out" in error for error in result.errors)
    
    @patch('subprocess.run')
    def test_phase_3_workflow_completed_success(self, mock_run, temp_output_dir):
        """Test Phase 3 correctly reports success when workflow completes successfully."""
        orchestrator = DeploymentOrchestrator(
            pr_number=2207,
            dry_run=False,
            output_dir=temp_output_dir,
        )
        
        # Mock gh auth status (authenticated)
        mock_auth = Mock()
        mock_auth.returncode = 0
        mock_auth.stdout = ""
        mock_auth.stderr = ""
        
        # Mock gh run list (workflow completed successfully)
        mock_workflow = Mock()
        mock_workflow.returncode = 0
        mock_workflow.stdout = json.dumps([{
            "databaseId": 12345,
            "status": "completed",
            "conclusion": "success"
        }])
        mock_workflow.stderr = ""
        
        mock_run.side_effect = [mock_auth, mock_workflow]
        
        result = orchestrator.phase_3_post_merge_validation()
        
        assert result.status == PhaseStatus.SUCCESS
        assert result.details["workflow_conclusion"] == "success"
        assert result.details["workflow_status"] == "completed"
        assert len(result.errors) == 0
    
    @patch('subprocess.run')
    def test_phase_3_workflow_completed_failure(self, mock_run, temp_output_dir):
        """Test Phase 3 correctly reports failure when workflow fails."""
        orchestrator = DeploymentOrchestrator(
            pr_number=2207,
            dry_run=False,
            output_dir=temp_output_dir,
        )
        
        # Mock gh auth status (authenticated)
        mock_auth = Mock()
        mock_auth.returncode = 0
        mock_auth.stdout = ""
        mock_auth.stderr = ""
        
        # Mock gh run list (workflow completed with failure)
        mock_workflow = Mock()
        mock_workflow.returncode = 0
        mock_workflow.stdout = json.dumps([{
            "databaseId": 12345,
            "status": "completed",
            "conclusion": "failure"
        }])
        mock_workflow.stderr = ""
        
        mock_run.side_effect = [mock_auth, mock_workflow]
        
        result = orchestrator.phase_3_post_merge_validation()
        
        # CRITICAL: Must report FAILED, not SUCCESS
        assert result.status == PhaseStatus.FAILED
        assert result.details["workflow_conclusion"] == "failure"
        assert len(result.errors) > 0
        assert "failure" in result.errors[0]
    
    @patch('subprocess.run')
    def test_phase_3_workflow_in_progress(self, mock_run, temp_output_dir):
        """Test Phase 3 reports IN_PROGRESS when workflow is still running."""
        orchestrator = DeploymentOrchestrator(
            pr_number=2207,
            dry_run=False,
            output_dir=temp_output_dir,
        )
        
        # Mock gh auth status (authenticated)
        mock_auth = Mock()
        mock_auth.returncode = 0
        mock_auth.stdout = ""
        mock_auth.stderr = ""
        
        # Mock gh run list (workflow still in progress)
        mock_workflow = Mock()
        mock_workflow.returncode = 0
        mock_workflow.stdout = json.dumps([{
            "databaseId": 12345,
            "status": "in_progress",
            "conclusion": None
        }])
        mock_workflow.stderr = ""
        
        mock_run.side_effect = [mock_auth, mock_workflow]
        
        result = orchestrator.phase_3_post_merge_validation()
        
        # CRITICAL: Must report IN_PROGRESS, not SUCCESS
        assert result.status == PhaseStatus.IN_PROGRESS
        assert result.details["workflow_status"] == "in_progress"
        assert "monitoring required" in result.details.get("monitoring", "").lower()
    
    @patch('subprocess.run')
    def test_phase_3_workflow_timed_out(self, mock_run, temp_output_dir):
        """Test Phase 3 reports failure when workflow times out."""
        orchestrator = DeploymentOrchestrator(
            pr_number=2207,
            dry_run=False,
            output_dir=temp_output_dir,
        )
        
        # Mock gh auth status (authenticated)
        mock_auth = Mock()
        mock_auth.returncode = 0
        mock_auth.stdout = ""
        mock_auth.stderr = ""
        
        # Mock gh run list (workflow timed out)
        mock_workflow = Mock()
        mock_workflow.returncode = 0
        mock_workflow.stdout = json.dumps([{
            "databaseId": 12345,
            "status": "completed",
            "conclusion": "timed_out"
        }])
        mock_workflow.stderr = ""
        
        mock_run.side_effect = [mock_auth, mock_workflow]
        
        result = orchestrator.phase_3_post_merge_validation()
        
        # CRITICAL: Must report FAILED, not SUCCESS
        assert result.status == PhaseStatus.FAILED
        assert result.details["workflow_conclusion"] == "timed_out"
        assert len(result.errors) > 0
    
    @patch('subprocess.run')
    def test_phase_3_workflow_cancelled(self, mock_run, temp_output_dir):
        """Test Phase 3 reports failure when workflow is cancelled."""
        orchestrator = DeploymentOrchestrator(
            pr_number=2207,
            dry_run=False,
            output_dir=temp_output_dir,
        )
        
        # Mock gh auth status (authenticated)
        mock_auth = Mock()
        mock_auth.returncode = 0
        mock_auth.stdout = ""
        mock_auth.stderr = ""
        
        # Mock gh run list (workflow cancelled)
        mock_workflow = Mock()
        mock_workflow.returncode = 0
        mock_workflow.stdout = json.dumps([{
            "databaseId": 12345,
            "status": "completed",
            "conclusion": "cancelled"
        }])
        mock_workflow.stderr = ""
        
        mock_run.side_effect = [mock_auth, mock_workflow]
        
        result = orchestrator.phase_3_post_merge_validation()
        
        # CRITICAL: Must report FAILED, not SUCCESS
        assert result.status == PhaseStatus.FAILED
        assert result.details["workflow_conclusion"] == "cancelled"
        assert len(result.errors) > 0
    
    
    def test_phase_4_health_check(self, orchestrator, temp_output_dir):
        """Test Phase 4: Health Check & Validation."""
        result = orchestrator.phase_4_health_check()
        
        assert result.phase == DeploymentPhase.PHASE_4_HEALTH_CHECK
        assert result.status in [PhaseStatus.SUCCESS, PhaseStatus.FAILED]
        assert "critical_files_check" in result.details
        
        # Check health report was created
        health_report_file = temp_output_dir / "health_check_report_2207.json"
        assert health_report_file.exists()
    
    def test_phase_5_notification(self, orchestrator, temp_output_dir):
        """Test Phase 5: Notification & Documentation."""
        # Add some phase results first
        orchestrator.manifest.phase_results.append(
            PhaseResult(
                phase=DeploymentPhase.PHASE_1_PRE_DEPLOYMENT,
                status=PhaseStatus.SUCCESS,
                start_time=datetime.now(timezone.utc),
                end_time=datetime.now(timezone.utc),
            )
        )
        
        result = orchestrator.phase_5_notification()
        
        assert result.phase == DeploymentPhase.PHASE_5_NOTIFICATION
        assert result.status == PhaseStatus.SUCCESS
        assert "summary_file" in result.details
        assert "manifest_file" in result.details
        
        # Check files were created
        summary_file = Path(result.details["summary_file"])
        manifest_file = Path(result.details["manifest_file"])
        
        assert summary_file.exists()
        assert manifest_file.exists()
    
    def test_deployment_summary_generation(self, orchestrator):
        """Test deployment summary markdown generation."""
        # Add phase results
        orchestrator.manifest.phase_results = [
            PhaseResult(
                phase=DeploymentPhase.PHASE_1_PRE_DEPLOYMENT,
                status=PhaseStatus.SUCCESS,
                start_time=datetime.now(timezone.utc),
                end_time=datetime.now(timezone.utc),
                details={"test": "value"},
            ),
            PhaseResult(
                phase=DeploymentPhase.PHASE_2_MERGE,
                status=PhaseStatus.SKIPPED,
                start_time=datetime.now(timezone.utc),
                end_time=datetime.now(timezone.utc),
                errors=["Test error"],
            ),
        ]
        
        summary = orchestrator._generate_deployment_summary()
        
        assert "Deployment Summary" in summary
        assert "PR #2207" in summary
        assert "Phase 1: Pre-Deployment Verification" in summary
        assert "Phase 2: Merge Execution" in summary
        assert "Test error" in summary
    
    def test_check_gh_auth(self, orchestrator):
        """Test GitHub CLI authentication check."""
        # In dry-run mode, commands are mocked
        result = orchestrator._check_gh_auth()
        assert isinstance(result, bool)
    
    def test_execute_full_workflow_dry_run(self, orchestrator):
        """Test full workflow execution in dry-run mode."""
        success = orchestrator.execute()
        
        # Should complete successfully in dry-run
        assert isinstance(success, bool)
        
        # Check that all phases were executed
        assert len(orchestrator.manifest.phase_results) >= 5
        
        # Verify notification phase ran
        notification_phases = [
            r for r in orchestrator.manifest.phase_results
            if r.phase == DeploymentPhase.PHASE_5_NOTIFICATION
        ]
        assert len(notification_phases) == 1
    
    def test_execute_creates_artifacts(self, orchestrator, temp_output_dir):
        """Test that execution creates all expected artifacts."""
        orchestrator.execute()
        
        # Check for log file
        log_files = list(temp_output_dir.glob("deployment_2207_*.log"))
        assert len(log_files) > 0
        
        # Check for manifest
        manifest_file = temp_output_dir / "deployment_manifest_2207.json"
        assert manifest_file.exists()
        
        # Check for summary
        summary_file = temp_output_dir / "deployment_summary_2207.md"
        assert summary_file.exists()
    
    def test_error_handling_in_phase(self, orchestrator):
        """Test error handling when a phase encounters an exception."""
        # Mock a method to raise an exception
        original_method = orchestrator.phase_1_pre_deployment_verification
        
        def mock_phase_with_error():
            raise ValueError("Test error")
        
        orchestrator.phase_1_pre_deployment_verification = mock_phase_with_error
        
        # Execute should handle the exception
        try:
            success = orchestrator.execute()
            # Should fail gracefully
            assert success is False
        except Exception:
            pytest.fail("Exception should be caught and handled")
        finally:
            # Restore original method
            orchestrator.phase_1_pre_deployment_verification = original_method
    
    def test_manifest_status_on_failure(self, temp_output_dir):
        """Test that manifest status is set correctly on failure."""
        orchestrator = DeploymentOrchestrator(
            pr_number=2207,
            dry_run=True,
            output_dir=temp_output_dir,
        )
        
        # Add a failed phase result
        failed_result = PhaseResult(
            phase=DeploymentPhase.PHASE_1_PRE_DEPLOYMENT,
            status=PhaseStatus.FAILED,
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc),
            errors=["Test failure"],
        )
        orchestrator.manifest.phase_results.append(failed_result)
        
        # Run notification phase to finalize manifest
        orchestrator.phase_5_notification()
        
        # Check manifest status
        assert orchestrator.manifest.status == PhaseStatus.FAILED


class TestCommandLineInterface:
    """Test command-line interface functionality."""
    
    def test_cli_help_output(self):
        """Test that CLI shows help information."""
        result = subprocess.run(
            ["python", "scripts/deployment_orchestrator.py", "--help"],
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0
        assert "Autonomous Deployment Orchestration" in result.stdout
        assert "--pr-number" in result.stdout
        assert "--dry-run" in result.stdout
    
    def test_cli_requires_pr_number(self):
        """Test that CLI requires --pr-number argument."""
        result = subprocess.run(
            ["python", "scripts/deployment_orchestrator.py"],
            capture_output=True,
            text=True,
        )
        
        assert result.returncode != 0
        assert "required" in result.stderr.lower() or "error" in result.stderr.lower()


class TestPhaseEnum:
    """Test phase enumeration."""
    
    def test_phase_values(self):
        """Test that all phases have correct values."""
        assert "Phase 1" in DeploymentPhase.PHASE_1_PRE_DEPLOYMENT.value
        assert "Phase 2" in DeploymentPhase.PHASE_2_MERGE.value
        assert "Phase 3" in DeploymentPhase.PHASE_3_POST_MERGE.value
        assert "Phase 4" in DeploymentPhase.PHASE_4_HEALTH_CHECK.value
        assert "Phase 5" in DeploymentPhase.PHASE_5_NOTIFICATION.value


class TestPhaseStatusEnum:
    """Test phase status enumeration."""
    
    def test_status_values(self):
        """Test that all status values are defined."""
        assert PhaseStatus.PENDING.value == "pending"
        assert PhaseStatus.IN_PROGRESS.value == "in_progress"
        assert PhaseStatus.SUCCESS.value == "success"
        assert PhaseStatus.FAILED.value == "failed"
        assert PhaseStatus.SKIPPED.value == "skipped"
