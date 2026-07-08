#         assert "PR, "Condition must be true"
#         assert "Phase 1: Pre-Deployment Verification" in summary, "Condition must be true"
#         assert "Phase 2: Merge Execution" in summary, "Condition must be true"
#         assert "Test error" in summary, "Error should be raised or set"
# 
#         assert "Deployment Summary" in summary, "Condition must be true"
#         assert "PR, "Condition must be true"
#         assert "Phase 1: Pre-Deployment Verification" in summary, "Condition must be true"
#         assert "Phase 2: Merge Execution" in summary, "Condition must be true"
#         assert "Test error" in summary, "Error should be raised or set"
# import tempfile
#         assert "Deployment Summary" in summary, "Condition must be true"
#         assert "PR, "Condition must be true"
#         assert "Phase 1: Pre-Deployment Verification" in summary, "Condition must be true"
#         assert "Phase 2: Merge Execution" in summary, "Condition must be true"
#         assert "Test error" in summary, "Error should be raised or set"
# 
#         assert "Deployment Summary" in summary, "Condition must be true"
#         assert "PR, "Condition must be true"
#         assert "Phase 1: Pre-Deployment Verification" in summary, "Condition must be true"
#         assert "Phase 2: Merge Execution" in summary, "Condition must be true"
#         assert "Test error" in summary, "Error should be raised or set"
#     PhaseResult,
#     PhaseStatus,
# )
#         assert "Deployment Summary" in summary, "Condition must be true"
#         assert "PR, "Condition must be true"
#         assert "Phase 1: Pre-Deployment Verification" in summary, "Condition must be true"
#         assert "Phase 2: Merge Execution" in summary, "Condition must be true"
#         assert "Test error" in summary, "Error should be raised or set"
#     def test_duration_calculation(self):
#     def test_duration_calculation(self):
#         """Test duration calculation between start and end times."""
#         result = PhaseResult(
#             phase=DeploymentPhase.PHASE_1_PRE_DEPLOYMENT,
#             status=PhaseStatus.IN_PROGRESS,
#         )
#         assert result.duration_seconds is None, "Result must not be empty"
# 
#         # Set times
#         result.start_time = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
#         result.end_time = datetime(2025, 1, 1, 12, 0, 5, tzinfo=timezone.utc)
#         result.end_time = datetime(2025, 1, 1, 12, 0, 5, tzinfo=timezone.utc)
# 
#         assert result.duration_seconds == 5.0, "Result must not be empty"
# 
#     def test_phase_result_creation(self):
#     def test_phase_result_creation(self):
#         """Test PhaseResult creation with all fields."""
#         result = PhaseResult(
#             phase=DeploymentPhase.PHASE_2_MERGE,
#             status=PhaseStatus.SUCCESS,
#             start_time=datetime.now(timezone.utc),
#             end_time=datetime.now(timezone.utc),
#             details={"test": "value"},
#             errors=["error1"],
#         )
#         assert result.phase == DeploymentPhase.PHASE_2_MERGE, "Result must not be empty"
#         assert result.status == PhaseStatus.SUCCESS, "Result must not be empty"
#         assert result.details["test"] == "value", "Result must not be empty"
#         assert len(result.errors) == 1, "Collection must not be empty"
#         assert "Deployment Summary" in summary, "Condition must be true"
#         assert "PR, "Condition must be true"
#         assert "Phase 1: Pre-Deployment Verification" in summary, "Condition must be true"
#         assert "Phase 2: Merge Execution" in summary, "Condition must be true"
#         assert "Test error" in summary, "Error should be raised or set"
#     def test_manifest_creation(self):
#     def test_manifest_creation(self):
#         """Test manifest creation with default values."""
#         manifest = DeploymentManifest(
#             pr_number=2207,
#             source_branch="0D_base_",
#             target_branch="main",
#             started_at=datetime.now(timezone.utc),
#         )
#         assert manifest.pr_number == 2207, "pr_number is not valid"
#         assert manifest.source_branch == "0D_base_", "source_branch is not valid"
#         assert manifest.target_branch == "main", "target_branch is not valid"
#         assert manifest.status == PhaseStatus.PENDING, "status is not valid"
#         assert len(manifest.phase_results) == 0, "Collection must not be empty"
# 
#     def test_manifest_to_dict(self):
#     def test_manifest_to_dict(self):
#         """Test manifest conversion to dictionary."""
#         manifest = DeploymentManifest(
#             pr_number=2207,
#             source_branch="0D_base_",
#             target_branch="main",
#             started_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
#         )
#         manifest_dict = manifest.to_dict()
# 
#         assert manifest_dict["pr_number"] == 2207, "Condition must be true"
#         assert manifest_dict["source_branch"] == "0D_base_", "Condition must be true"
#         assert manifest_dict["target_branch"] == "main", "Condition must be true"
#         assert manifest_dict["status"] == "pending", "Condition must be true"
#         assert isinstance(manifest_dict["phase_results"], list)
#         assert "Deployment Summary" in summary, "Condition must be true"
#         assert "PR, "Condition must be true"
#         assert "Phase 1: Pre-Deployment Verification" in summary, "Condition must be true"
#         assert "Phase 2: Merge Execution" in summary, "Condition must be true"
#         assert "Test error" in summary, "Error should be raised or set"
#     @pytest.fixture
#     def temp_output_dir(self):
#     def temp_output_dir(self):
#         """Create temporary output directory for tests."""
#         with tempfile.TemporaryDirectory() as tmpdir:
#             yield Path(tmpdir)
#     @pytest.fixture
#     def orchestrator(self, temp_output_dir):
#     def orchestrator(self, temp_output_dir):
#         """Create orchestrator instance for testing."""
#         return DeploymentOrchestrator(
#             pr_number=2207,
#             dry_run=True,
#             output_dir=temp_output_dir,
#         )
#     @pytest.fixture
#     def live_orchestrator(self, temp_output_dir):
#     def live_orchestrator(self, temp_output_dir):
#         """Create a non-dry-run orchestrator instance for workflow monitoring tests."""
#         return DeploymentOrchestrator(
#             pr_number=2207,
#             dry_run=False,
#             output_dir=temp_output_dir,
#         )
#     def test_orchestrator_initialization(self, orchestrator, temp_output_dir):
#     def test_orchestrator_initialization(self, orchestrator, temp_output_dir):
#         """Test orchestrator initialization."""
#         assert orchestrator.pr_number == 2207, "pr_number is not valid"
#         assert orchestrator.dry_run is True, "dry_run is not valid"
#         assert orchestrator.output_dir == temp_output_dir, "output_dir is not valid"
#         assert orchestrator.manifest.pr_number == 2207, "pr_number is not valid"
#         assert orchestrator.manifest.target_branch == "main", "target_branch is not valid"
#     def test_run_command_dry_run(self, orchestrator):
#     def test_run_command_dry_run(self, orchestrator):
#         """Test command execution in dry-run mode."""
#         exit_code, stdout, stderr = orchestrator.run_command(["echo", "test"])
#         assert exit_code == 0, "exit_code is not valid"
#         assert "[DRY RUN]" in stdout, "Condition must be true"
#         assert stderr == "", "stderr is not valid"
# 
#     @patch("subprocess.run")
#     def test_run_command_execution(self, mock_run, temp_output_dir):
#     def test_run_command_execution(self, mock_run, temp_output_dir):
#         """Test actual command execution (non-dry-run)."""
#         # Create non-dry-run orchestrator
#         orchestrator = DeploymentOrchestrator(
#             pr_number=2207,
#             dry_run=False,
#             output_dir=temp_output_dir,
#         )
#         mock_result = Mock()
#         mock_result.returncode = 0
#         mock_result.stdout = "output"
#         mock_result.stderr = ""
#         mock_run.return_value = mock_result
#         mock_run.return_value = mock_result
# 
#         exit_code, stdout, _stderr = orchestrator.run_command(["echo", "test"])
# 
#         assert exit_code == 0, "exit_code is not valid"
#         assert stdout == "output", "stdout is not valid"
#         mock_run.assert_called_once()
# 
#     def test_phase_1_pre_deployment_verification(self, orchestrator):
#     def test_phase_1_pre_deployment_verification(self, orchestrator):
#         """Test Phase 1: Pre-Deployment Verification."""
#         result = orchestrator.phase_1_pre_deployment_verification()
#         assert result.phase == DeploymentPhase.PHASE_1_PRE_DEPLOYMENT, "Result must not be empty"
#         assert result.status in [PhaseStatus.SUCCESS, PhaseStatus.FAILED]
#         assert result.start_time is not None, "start_time must be initialized"
#         assert result.end_time is not None, "end_time must be initialized"
#         assert "yaml_validation" in result.details, "Result must not be empty"
#         assert "security_scan" in result.details, "Result must not be empty"
# 
#     def test_phase_1_generates_report(self, orchestrator, temp_output_dir):
#     def test_phase_1_generates_report(self, orchestrator, temp_output_dir):
#         """Test that Phase 1 generates a pre-check report."""
#         orchestrator.phase_1_pre_deployment_verification()
#         report_file = temp_output_dir / "pre_check_report_2207.json"
#         assert report_file.exists(), "rep is not valid"
# 
#         # Verify report content
#         with open(report_file) as f:
#             report_data = json.load(f)
#             report_data = json.load(f)
# 
#         assert "yaml_validation" in report_data, "Data must not be empty"
#         assert "security_scan" in report_data, "Data must not be empty"
# 
#     def test_phase_2_merge_execution_dry_run(self, orchestrator):
#     def test_phase_2_merge_execution_dry_run(self, orchestrator):
#         """Test Phase 2: Merge Execution in dry-run mode."""
#         result = orchestrator.phase_2_merge_execution()
#         assert result.phase == DeploymentPhase.PHASE_2_MERGE, "Result must not be empty"
#         assert result.status == PhaseStatus.SKIPPED, "Result must not be empty"
#         assert "Dry run" in result.details.get("reason", "")
# 
#     def test_phase_3_post_merge_validation_dry_run(self, orchestrator):
#     def test_phase_3_post_merge_validation_dry_run(self, orchestrator):
#         """Test Phase 3: Post-Merge Validation in dry-run mode."""
#         result = orchestrator.phase_3_post_merge_validation()
#         assert result.phase == DeploymentPhase.PHASE_3_POST_MERGE, "Result must not be empty"
#         assert result.status == PhaseStatus.SKIPPED, "Result must not be empty"
#         assert "Dry run" in result.details.get("reason", "")
# 
#     @patch("scripts.deployment_orchestrator.time.sleep", return_value=None)
#     def test_phase_3_post_merge_validation_success(
#         self,
#         mock_sleep,
#         live_orchestrator,
#     ):
#     ):
#         """Phase 3 should report success when workflow completes successfully."""
#         del mock_sleep  # Unused but required by patch
# 
#         with (
#             patch.object(live_orchestrator, "_check_gh_auth", return_value=True),
#             patch.object(live_orchestrator, "run_command") as mock_run_cmd,
#             patch.object(
#                 live_orchestrator,
#                 live_orchestrator,
#                 "_ensure_workflow_completion",
#                 return_value={
#                     "status": "completed",
#                     "conclusion": "success",
#                     "jobs": [
#                         {"name": "tests", "status": "completed", "conclusion": "success"},
#                     ],
#                 },
#             ) as mock_wait,
#         ):
#             mock_run_cmd.return_value = (
#                 0,
#                 json.dumps(
#                     [
#                         {
#                         {
#                             "databaseId": 12345,
#                             "status": "in_progress",
#                             "conclusion": None,
#                         }
#                     ]
#                 ),
#                 "",
#             )
#             result = live_orchestrator.phase_3_post_merge_validation()
# 
#         assert result.status == PhaseStatus.SUCCESS, "Result must not be empty"
#         assert result.details["workflow_run_id"] == 12345, "Result must not be empty"
#         assert result.details["workflow_conclusion"] == "success", "Result must not be empty"
#         assert "failed_jobs" not in result.details, "Result must not be empty"
#         mock_wait.assert_called_once()
#         mock_run_cmd.assert_called_once()
# 
#     @patch("scripts.deployment_orchestrator.time.sleep", return_value=None)
#     def test_phase_3_post_merge_validation_failure(
#         self,
#         mock_sleep,
#         live_orchestrator,
#     ):
#     ):
#         """Phase 3 should record failure when workflow concludes unsuccessfully."""
#         del mock_sleep
# 
#         with (
#             patch.object(live_orchestrator, "_check_gh_auth", return_value=True),
#             patch.object(live_orchestrator, "run_command") as mock_run_cmd,
#             patch.object(
#                 live_orchestrator,
#                 live_orchestrator,
#                 "_ensure_workflow_completion",
#                 return_value={
#                     "status": "completed",
#                     "conclusion": "failure",
#                     "jobs": [
#                         {"name": "tests", "status": "completed", "conclusion": "failure"},
#                         {"name": "lint", "status": "completed", "conclusion": "success"},
#                     ],
#                 },
#             ),
#         ):
#             mock_run_cmd.return_value = (
#                 0,
#                 json.dumps(
#                     [
#                         {
#                         {
#                             "databaseId": 999,
#                             "status": "in_progress",
#                             "conclusion": None,
#                         }
#                     ]
#                 ),
#                 "",
#             )
#             result = live_orchestrator.phase_3_post_merge_validation()
# 
#         assert result.status == PhaseStatus.FAILED, "Result must not be empty"
#         assert result.details["workflow_run_id"] == 999, "Result must not be empty"
#         assert result.details["workflow_conclusion"] == "failure", "Result must not be empty"
#         assert any(job["name"] == "tests" for job in result.details["failed_jobs"]), "Result must not be empty"
#         assert result.errors, "Result must not be empty"
# 
#     @patch("scripts.deployment_orchestrator.time.sleep", return_value=None)
#     def test_phase_3_post_merge_validation_timeout(
#         self,
#         mock_sleep,
#         live_orchestrator,
#     ):
#     ):
#         """Phase 3 should fail with timeout details when monitoring exceeds deadline."""
#         del mock_sleep
# 
#         with (
#             patch.object(live_orchestrator, "_check_gh_auth", return_value=True),
#             patch.object(live_orchestrator, "run_command") as mock_run_cmd,
#             patch.object(
#                 live_orchestrator,
#                 live_orchestrator,
#                 "_ensure_workflow_completion",
#                 side_effect=TimeoutError("Workflow run 111 timed out"),
#             ),
#         ):
#             mock_run_cmd.return_value = (
#                 0,
#                 json.dumps(
#                     [
#                         {
#                         {
#                             "databaseId": 111,
#                             "status": "in_progress",
#                             "conclusion": None,
#                         }
#                     ]
#                 ),
#                 "",
#             )
#             result = live_orchestrator.phase_3_post_merge_validation()
# 
#         assert result.status == PhaseStatus.FAILED, "Result must not be empty"
#         assert result.details.get("timeout") is True, "Result must not be empty"
#         assert any("timed out" in error for error in result.errors), "Result must not be empty"
# 
#     @patch("subprocess.run")
#     def test_phase_3_workflow_completed_success(self, mock_run, temp_output_dir):
#     def test_phase_3_workflow_completed_success(self, mock_run, temp_output_dir):
#         """Test Phase 3 correctly reports success when workflow completes successfully."""
#         orchestrator = DeploymentOrchestrator(
#             pr_number=2207,
#             dry_run=False,
#             output_dir=temp_output_dir,
#         )
#         mock_auth = Mock()
#         mock_auth.returncode = 0
#         mock_auth.stdout = ""
#         mock_auth.stderr = ""
# 
#         # Mock gh run list (workflow completed successfully)
#         mock_workflow = Mock()
#         mock_workflow.returncode = 0
#         mock_workflow.stdout = json.dumps(
#             [{"databaseId": 12345, "status": "completed", "conclusion": "success"}]
#         )
#         mock_workflow.stderr = ""
#         mock_workflow.stderr = ""
# 
#         mock_run.side_effect = [mock_auth, mock_workflow]
# 
#         result = orchestrator.phase_3_post_merge_validation()
# 
#         assert result.status == PhaseStatus.SUCCESS, "Result must not be empty"
#         assert result.details["workflow_conclusion"] == "success", "Result must not be empty"
#         assert result.details["workflow_status"] == "completed", "Result must not be empty"
#         assert len(result.errors) == 0, "Collection must not be empty"
# 
#     @patch("subprocess.run")
#     def test_phase_3_workflow_completed_failure(self, mock_run, temp_output_dir):
#     def test_phase_3_workflow_completed_failure(self, mock_run, temp_output_dir):
#         """Test Phase 3 correctly reports failure when workflow fails."""
#         orchestrator = DeploymentOrchestrator(
#             pr_number=2207,
#             dry_run=False,
#             output_dir=temp_output_dir,
#         )
#         mock_auth = Mock()
#         mock_auth.returncode = 0
#         mock_auth.stdout = ""
#         mock_auth.stderr = ""
# 
#         # Mock gh run list (workflow completed with failure)
#         mock_workflow = Mock()
#         mock_workflow.returncode = 0
#         mock_workflow.stdout = json.dumps(
#             [{"databaseId": 12345, "status": "completed", "conclusion": "failure"}]
#         )
#         mock_workflow.stderr = ""
#         mock_workflow.stderr = ""
# 
#         mock_run.side_effect = [mock_auth, mock_workflow]
# 
#         result = orchestrator.phase_3_post_merge_validation()
#         # CRITICAL: Must report FAILED, not SUCCESS
#         assert result.status == PhaseStatus.FAILED, "Result must not be empty"
#         assert result.details["workflow_conclusion"] == "failure", "Result must not be empty"
#         assert len(result.errors) > 0, "Collection must not be empty"
#         assert "failure" in result.errors[0], "Result must not be empty"
#         assert "failure" in result.errors[0], "Result must not be empty"
# 
#     @patch("subprocess.run")
#     def test_phase_3_workflow_in_progress(self, mock_run, temp_output_dir):
#     def test_phase_3_workflow_in_progress(self, mock_run, temp_output_dir):
#         """Test Phase 3 reports IN_PROGRESS when workflow is still running."""
#         orchestrator = DeploymentOrchestrator(
#             pr_number=2207,
#             dry_run=False,
#             output_dir=temp_output_dir,
#         )
#         mock_auth = Mock()
#         mock_auth.returncode = 0
#         mock_auth.stdout = ""
#         mock_auth.stderr = ""
# 
#         # Mock gh run list (workflow still in progress)
#         mock_workflow = Mock()
#         mock_workflow.returncode = 0
#         mock_workflow.stdout = json.dumps(
#             [{"databaseId": 12345, "status": "in_progress", "conclusion": None}]
#         )
#         mock_workflow.stderr = ""
#         mock_workflow.stderr = ""
# 
#         mock_run.side_effect = [mock_auth, mock_workflow]
# 
#         result = orchestrator.phase_3_post_merge_validation()
#         # CRITICAL: Must report IN_PROGRESS, not SUCCESS
#         assert result.status == PhaseStatus.IN_PROGRESS, "Result must not be empty"
#         assert result.details["workflow_status"] == "in_progress", "Result must not be empty"
#         assert "monitoring required" in result.details.get("monitoring", "").lower()
#         assert "monitoring required" in result.details.get("monitoring", "").lower()
# 
#     @patch("subprocess.run")
#     def test_phase_3_workflow_timed_out(self, mock_run, temp_output_dir):
#     def test_phase_3_workflow_timed_out(self, mock_run, temp_output_dir):
#         """Test Phase 3 reports failure when workflow times out."""
#         orchestrator = DeploymentOrchestrator(
#             pr_number=2207,
#             dry_run=False,
#             output_dir=temp_output_dir,
#         )
#         mock_auth = Mock()
#         mock_auth.returncode = 0
#         mock_auth.stdout = ""
#         mock_auth.stderr = ""
# 
#         # Mock gh run list (workflow timed out)
#         mock_workflow = Mock()
#         mock_workflow.returncode = 0
#         mock_workflow.stdout = json.dumps(
#             [{"databaseId": 12345, "status": "completed", "conclusion": "timed_out"}]
#         )
#         mock_workflow.stderr = ""
#         mock_workflow.stderr = ""
# 
#         mock_run.side_effect = [mock_auth, mock_workflow]
# 
#         result = orchestrator.phase_3_post_merge_validation()
#         # CRITICAL: Must report FAILED, not SUCCESS
#         assert result.status == PhaseStatus.FAILED, "Result must not be empty"
#         assert result.details["workflow_conclusion"] == "timed_out", "Result must not be empty"
#         assert len(result.errors) > 0, "Collection must not be empty"
#         assert len(result.errors) > 0, "Collection must not be empty"
# 
#     @patch("subprocess.run")
#     def test_phase_3_workflow_cancelled(self, mock_run, temp_output_dir):
#     def test_phase_3_workflow_cancelled(self, mock_run, temp_output_dir):
#         """Test Phase 3 reports failure when workflow is cancelled."""
#         orchestrator = DeploymentOrchestrator(
#             pr_number=2207,
#             dry_run=False,
#             output_dir=temp_output_dir,
#         )
#         mock_auth = Mock()
#         mock_auth.returncode = 0
#         mock_auth.stdout = ""
#         mock_auth.stderr = ""
# 
#         # Mock gh run list (workflow cancelled)
#         mock_workflow = Mock()
#         mock_workflow.returncode = 0
#         mock_workflow.stdout = json.dumps(
#             [{"databaseId": 12345, "status": "completed", "conclusion": "cancelled"}]
#         )
#         mock_workflow.stderr = ""
#         mock_workflow.stderr = ""
# 
#         mock_run.side_effect = [mock_auth, mock_workflow]
# 
#         result = orchestrator.phase_3_post_merge_validation()
#         # CRITICAL: Must report FAILED, not SUCCESS
#         assert result.status == PhaseStatus.FAILED, "Result must not be empty"
#         assert result.details["workflow_conclusion"] == "cancelled", "Result must not be empty"
#         assert len(result.errors) > 0, "Collection must not be empty"
#         assert len(result.errors) > 0, "Collection must not be empty"
# 
#     def test_phase_4_health_check(self, orchestrator, temp_output_dir):
#     def test_phase_4_health_check(self, orchestrator, temp_output_dir):
#         """Test Phase 4: Health Check & Validation."""
#         result = orchestrator.phase_4_health_check()
#         assert result.phase == DeploymentPhase.PHASE_4_HEALTH_CHECK, "Result must not be empty"
#         assert result.status in [PhaseStatus.SUCCESS, PhaseStatus.FAILED]
#         assert "critical_files_check" in result.details, "Result must not be empty"
#         # Check health report was created
#         health_report_file = temp_output_dir / "health_check_report_2207.json"
#         assert health_report_file.exists(), "health_rep is not valid"
#         assert health_report_file.exists(), "health_rep is not valid"
# 
#     def test_phase_5_notification(self, orchestrator, temp_output_dir):
#     def test_phase_5_notification(self, orchestrator, temp_output_dir):
#         """Test Phase 5: Notification & Documentation."""
#         # Add some phase results first
#         orchestrator.manifest.phase_results.append(
#             PhaseResult(
#                 phase=DeploymentPhase.PHASE_1_PRE_DEPLOYMENT,
#                 status=PhaseStatus.SUCCESS,
#                 start_time=datetime.now(timezone.utc),
#                 end_time=datetime.now(timezone.utc),
#             )
#         )
#         result = orchestrator.phase_5_notification()
# 
#         assert result.phase == DeploymentPhase.PHASE_5_NOTIFICATION, "Result must not be empty"
#         assert result.status == PhaseStatus.SUCCESS, "Result must not be empty"
#         assert "summary_file" in result.details, "Result must not be empty"
#         assert "manifest_file" in result.details, "Result must not be empty"
#         # Check files were created
#         summary_file = Path(result.details["summary_file"])
#         manifest_file = Path(result.details["manifest_file"])
#         manifest_file = Path(result.details["manifest_file"])
# 
#         assert summary_file.exists(), "Condition must be true"
#         assert manifest_file.exists(), "Condition must be true"
# 
#     def test_deployment_summary_generation(self, orchestrator):
#     def test_deployment_summary_generation(self, orchestrator):
#         """Test deployment summary markdown generation."""
#         # Add phase results
#         orchestrator.manifest.phase_results = [
#             PhaseResult(
#                 phase=DeploymentPhase.PHASE_1_PRE_DEPLOYMENT,
#                 status=PhaseStatus.SUCCESS,
#                 start_time=datetime.now(timezone.utc),
#                 end_time=datetime.now(timezone.utc),
#                 details={"test": "value"},
#             ),
#             PhaseResult(
#                 phase=DeploymentPhase.PHASE_2_MERGE,
#                 status=PhaseStatus.SKIPPED,
#                 start_time=datetime.now(timezone.utc),
#                 end_time=datetime.now(timezone.utc),
#                 errors=["Test error"],
#             ),
#         ]
#         summary = orchestrator._generate_deployment_summary()
# 
#         assert "Deployment Summary" in summary, "Condition must be true"
#         assert "PR, "Condition must be true"
#         assert "Phase 1: Pre-Deployment Verification" in summary, "Condition must be true"
#         assert "Phase 2: Merge Execution" in summary, "Condition must be true"
#         assert "Test error" in summary, "Error should be raised or set"
# 
#     def test_check_gh_auth(self, orchestrator):
#     def test_check_gh_auth(self, orchestrator):
#         """Test GitHub CLI authentication check."""
#         # In dry-run mode, commands are mocked
#         result = orchestrator._check_gh_auth()
#         assert isinstance(result, bool)
#     def test_execute_full_workflow_dry_run(self, orchestrator):
#     def test_execute_full_workflow_dry_run(self, orchestrator):
#         """Test full workflow execution in dry-run mode."""
#         success = orchestrator.execute()
#         assert isinstance(success, bool)
# 
#         # Check that all phases were executed
#         assert len(orchestrator.manifest.phase_results) >= 5, "Collection must not be empty"
# 
#         # Verify notification phase ran
#         notification_phases = [
#             r
#             for r in orchestrator.manifest.phase_results
#             if r.phase == DeploymentPhase.PHASE_5_NOTIFICATION
#         ]
#         assert len(notification_phases) == 1, "Notification_phases must not be empty"
#         assert len(notification_phases) == 1, "Notification_phases must not be empty"
# 
#     def test_execute_creates_artifacts(self, orchestrator, temp_output_dir):
#     def test_execute_creates_artifacts(self, orchestrator, temp_output_dir):
#         """Test that execution creates all expected artifacts."""
#         orchestrator.execute()
#         log_files = list(temp_output_dir.glob("deployment_2207_*.log"))
#         assert len(log_files) > 0, "Log_files must not be empty"
# 
#         # Check for manifest
#         manifest_file = temp_output_dir / "deployment_manifest_2207.json"
#         assert manifest_file.exists(), "Condition must be true"
# 
#         # Check for summary
#         summary_file = temp_output_dir / "deployment_summary_2207.md"
#         assert summary_file.exists(), "Condition must be true"
#         assert summary_file.exists(), "Condition must be true"
# 
#     def test_execute_halts_when_phase_in_progress(self, live_orchestrator):
#     def test_execute_halts_when_phase_in_progress(self, live_orchestrator):
#         """Ensure orchestrator pauses when a phase reports IN_PROGRESS."""
#         def successful_phase(phase: DeploymentPhase) -> PhaseResult:
#             return PhaseResult(
#                 phase=phase,
#                 status=PhaseStatus.SUCCESS,
#                 start_time=datetime.now(timezone.utc),
#                 end_time=datetime.now(timezone.utc),
#             )
# 
#         def phase1():
#             return successful_phase(DeploymentPhase.PHASE_1_PRE_DEPLOYMENT)
# 
#         def phase2():
#             return successful_phase(DeploymentPhase.PHASE_2_MERGE)
# 
#         def phase3():
#             return PhaseResult(
#                 phase=DeploymentPhase.PHASE_3_POST_MERGE,
#                 status=PhaseStatus.IN_PROGRESS,
#                 start_time=datetime.now(timezone.utc),
#                 end_time=datetime.now(timezone.utc),
#                 details={"reason": "Workflow monitoring still running"},
#             )
# 
#         def fail_phase4():
#             pytest.fail("Phase 4 should not execute while validation is in progress")
# 
#         def fail_phase5():
#             pytest.fail("Phase 5 should not execute while validation is in progress")
# 
#         live_orchestrator.phase_1_pre_deployment_verification = phase1
#         live_orchestrator.phase_2_merge_execution = phase2
#         live_orchestrator.phase_3_post_merge_validation = phase3
#         live_orchestrator.phase_4_health_check = fail_phase4  # type: ignore[assignment]
#         live_orchestrator.phase_5_notification = fail_phase5  # type: ignore[assignment]
# 
#         success = live_orchestrator.execute()
# 
#         assert success is False, "success is not valid"
#         assert live_orchestrator.manifest.status == PhaseStatus.IN_PROGRESS, "status is not valid"
# 
#         executed_phases = [result.phase for result in live_orchestrator.manifest.phase_results]
#         executed_phases = [result.phase for result in live_orchestrator.manifest.phase_results]
#         """Test error handling when a phase encounters an exception."""
#         # Mock a method to raise an exception
#         original_method = orchestrator.phase_1_pre_deployment_verification
#         def mock_phase_with_error():
#             raise ValueError("Test error")
# 
#         orchestrator.phase_1_pre_deployment_verification = mock_phase_with_error
#         # Execute should handle the exception
#         try:
#             success = orchestrator.execute()
#             # Should fail gracefully
#             assert success is False, "success is not valid"
#         except Exception as _err:
#             pytest.fail("Exception should be caught and handled")
#         finally:
#             # Restore original method
#             orchestrator.phase_1_pre_deployment_verification = original_method
#             orchestrator.phase_1_pre_deployment_verification = original_method
# 
#     def test_manifest_status_on_failure(self, temp_output_dir):
#     def test_manifest_status_on_failure(self, temp_output_dir):
#         """Test that manifest status is set correctly on failure."""
#         orchestrator = DeploymentOrchestrator(
#             pr_number=2207,
#             dry_run=True,
#             output_dir=temp_output_dir,
#         )
#         failed_result = PhaseResult(
#             phase=DeploymentPhase.PHASE_1_PRE_DEPLOYMENT,
#             status=PhaseStatus.FAILED,
#             start_time=datetime.now(timezone.utc),
#             end_time=datetime.now(timezone.utc),
#             errors=["Test failure"],
#         )
#         orchestrator.manifest.phase_results.append(failed_result)
# 
#         # Run notification phase to finalize manifest
#         orchestrator.phase_5_notification()
# 
#         # Check manifest status
#         assert orchestrator.manifest.status == PhaseStatus.FAILED, "status is not valid"


class TestCommandLineInterface:
    """Test command-line interface functionality."""

    def test_cli_help_output(self):
        """Test that CLI shows help information."""
        result = subprocess.run(
            ["python", "scripts/deployment_orchestrator.py", "--help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, "Result must not be empty"
        assert "Autonomous Deployment Orchestration" in result.stdout, "Result must not be empty"
        assert "--pr-number" in result.stdout, "Result must not be empty"
        assert "--dry-run" in result.stdout, "Result must not be empty"

    def test_cli_requires_pr_number(self):
        """Test that CLI requires --pr-number argument."""
        result = subprocess.run(
            ["python", "scripts/deployment_orchestrator.py"],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0, "Result must not be empty"
        assert "required" in result.stderr.lower() or "error" in result.stderr.lower(), "Result must not be empty"


class TestPhaseEnum:
    """Test phase enumeration."""

    def test_phase_values(self):
        """Test that all phases have correct values."""
        assert "Phase 1" in DeploymentPhase.PHASE_1_PRE_DEPLOYMENT.value, "Value must be initialized"
        assert "Phase 2" in DeploymentPhase.PHASE_2_MERGE.value, "Value must be initialized"
        assert "Phase 3" in DeploymentPhase.PHASE_3_POST_MERGE.value, "Value must be initialized"
        assert "Phase 4" in DeploymentPhase.PHASE_4_HEALTH_CHECK.value, "Value must be initialized"
        assert "Phase 5" in DeploymentPhase.PHASE_5_NOTIFICATION.value, "Value must be initialized"


class TestPhaseStatusEnum:
    """Test phase status enumeration."""

    def test_status_values(self):
        """Test that all status values are defined."""
        assert PhaseStatus.PENDING.value == "pending", "Value must be initialized"
        assert PhaseStatus.IN_PROGRESS.value == "in_progress", "Value must be initialized"
        assert PhaseStatus.SUCCESS.value == "success", "Value must be initialized"
        assert PhaseStatus.FAILED.value == "failed", "Value must be initialized"
        assert PhaseStatus.SKIPPED.value == "skipped", "Value must be initialized"
