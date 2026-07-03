import pytest

#             assert required.issubset(, "Condition must be true"
#                 result.keys()
#             ), f"Missing keys for dist={dist}: {required - result.keys()}"
# and report generation functionality.
#     def test_missing_pattern_distribution_key(self, collector):
# """
#             assert required.issubset(, "Condition must be true"
#                 result.keys()
#             ), f"Missing keys for dist={dist}: {required - result.keys()}"
# import sys
#             result = collector.analyze_multi_job_cascade(self._make_report(dist))
#             assert required.issubset(, "Condition must be true"
#                 result.keys()
#             ), f"Missing keys for dist={dist}: {required - result.keys()}"
# 
#             result = collector.analyze_multi_job_cascade(self._make_report(dist))
#             assert required.issubset(, "Condition must be true"
#                 result.keys()
#             ), f"Missing keys for dist={dist}: {required - result.keys()}"
# 
#             result = collector.analyze_multi_job_cascade(self._make_report(dist))
#             assert required.issubset(, "Condition must be true"
#                 result.keys()
#             ), f"Missing keys for dist={dist}: {required - result.keys()}"
#     def collector(self):
#     def collector(self):
#         """Create a TelemetryCollector instance for testing."""
#         return TelemetryCollector(
#             owner="test-owner", repo="test-repo", token="test-token"  # pragma: allowlist secret
#         )
#     @pytest.fixture
#     def mock_workflow_runs(self):
#     def mock_workflow_runs(self):
#         """Create mock workflow run data."""
#         return [
#             {
#                 "id": 1001,
#                 "name": "Auto-Fix Common Issues",
#                 "html_url": "https://github.com/test/test/actions/runs/1001",
#                 "conclusion": "failure",
#                 "created_at": "2024-01-01T00:00:00Z",
#             },
#             {
#                 "id": 1002,
#                 "name": "Coverage Report Generation",
#                 "html_url": "https://github.com/test/test/actions/runs/1002",
#                 "conclusion": "timed_out",
#                 "created_at": "2024-01-01T01:00:00Z",
#             },
#             {
#                 "id": 1003,
#                 "name": "Resilient Test Suite",
#                 "html_url": "https://github.com/test/test/actions/runs/1003",
#                 "conclusion": "success",
#                 "created_at": "2024-01-01T02:00:00Z",
#             },
#         ]
#     @pytest.fixture
#     def mock_jobs(self):
#     def mock_jobs(self):
#         """Create mock job data for individual job collection test."""
#         return [
#             {
#                 "id": 2001,
#                 "name": "auto-fix",
#                 "html_url": "https://github.com/test/test/runs/2001",
#                 "status": "completed",
#                 "conclusion": "failure",
#             }
#         ]
#     @pytest.fixture
#     def mock_jobs_by_run(self):
#     def mock_jobs_by_run(self):
#         """Create mock job data mapped by run ID for report generation."""
#         return {
#             1001: [  # Auto-Fix Common Issues run
#                 {
#                     "id": 2001,
#                     "name": "auto-fix",
#                     "html_url": "https://github.com/test/test/runs/2001",
#                     "status": "completed",
#                     "conclusion": "failure",
#                 }
#             ],
#             1002: [  # Coverage Report Generation run
#                 {
#                     "id": 2002,
#                     "name": "coverage-report",
#                     "html_url": "https://github.com/test/test/runs/2002",
#                     "status": "completed",
#                     "conclusion": "timed_out",
#                 }
#             ],
#         }
#     @pytest.fixture
#     def mock_artifacts(self):
#     def mock_artifacts(self):
#         """Create mock artifact data."""
#         return [
#             {
#                 "id": 3001,
#                 "name": "test-results",
#                 "size_in_bytes": 1024,
#                 "expired": False,
#             }
#         ]
#     def test_initialization(self, collector):
#     def test_initialization(self, collector):
#         """Test TelemetryCollector initialization."""
#         assert collector.owner == "test-owner", "owner is not valid"
#         assert collector.repo == "test-repo", "repo is not valid"
#         assert collector.token == "test-token", "token is not valid"
#         assert collector.base_url == "https://api.github.com", "base_url is not valid"
#         assert "Authorization" in collector.headers, "Condition must be true"
#     def test_pattern_keywords_defined(self, collector):
#     def test_pattern_keywords_defined(self, collector):
#         """Test that all core patterns have keywords defined."""
#         assert len(collector.PATTERN_KEYWORDS) >= 5, "Collection must not be empty"
#         assert "auto-fix" in collector.PATTERN_KEYWORDS, "Condition must be true"
#         assert "test-infrastructure" in collector.PATTERN_KEYWORDS, "Condition must be true"
#         assert "coverage-timeout" in collector.PATTERN_KEYWORDS, "Condition must be true"
#         assert "filesystem-deadlock" in collector.PATTERN_KEYWORDS, "Condition must be true"
#         assert "pre-merge-cascade" in collector.PATTERN_KEYWORDS, "Condition must be true"
#     def test_classify_failure_auto_fix(self, collector):
#     def test_classify_failure_auto_fix(self, collector):
#         """Test classification of auto-fix pattern."""
#         run = {"name": "Auto-Fix Common Issues"}
#         jobs = [{"name": "detect-and-fix"}]
#         pattern = collector.classify_failure(run, jobs)
#         assert pattern == "auto-fix", "pattern is not valid"
#     def test_classify_failure_coverage_timeout(self, collector):
#     def test_classify_failure_coverage_timeout(self, collector):
#         """Test classification of coverage timeout pattern."""
#         run = {"name": "Coverage Report Generation"}
#         jobs = [{"name": "pytest-cov"}]
#         pattern = collector.classify_failure(run, jobs)
#         assert pattern == "coverage-timeout", "pattern is not valid"
#     def test_classify_failure_test_infrastructure(self, collector):
#     def test_classify_failure_test_infrastructure(self, collector):
#         """Test classification of test infrastructure pattern."""
#         run = {"name": "Resilient Validation Suite"}
#         jobs = [{"name": "test-runner"}]
#         pattern = collector.classify_failure(run, jobs)
#         assert pattern == "test-infrastructure", "pattern is not valid"
#     def test_classify_failure_filesystem_deadlock(self, collector):
#     def test_classify_failure_filesystem_deadlock(self, collector):
#         """Test classification of filesystem deadlock pattern."""
#         run = {"name": "Root Organization Validation"}
#         jobs = [{"name": "file-validation"}]
#         pattern = collector.classify_failure(run, jobs)
#         assert pattern == "filesystem-deadlock", "pattern is not valid"
#     def test_classify_failure_pre_merge_cascade(self, collector):
#     def test_classify_failure_pre_merge_cascade(self, collector):
#         """Test classification of pre-merge cascade pattern."""
#         run = {"name": "Pre-Merge Final Checks"}
#         jobs = [{"name": "merge validation"}]
#         pattern = collector.classify_failure(run, jobs)
#         assert pattern == "pre-merge-cascade", "pattern is not valid"
#     def test_classify_failure_unknown(self, collector):
#     def test_classify_failure_unknown(self, collector):
#         """Test classification of unknown pattern."""
#         run = {"name": "Some Random Workflow"}
#         jobs = [{"name": "unknown-job"}]
#         pattern = collector.classify_failure(run, jobs)
#         assert pattern == "unknown", "pattern is not valid"
#     @patch("collect_telemetry.requests.get")
#     def test_collect_workflow_runs(self, mock_get, collector, mock_workflow_runs):
#     def test_collect_workflow_runs(self, mock_get, collector, mock_workflow_runs):
#         """Test workflow run collection."""
#         mock_response = Mock()
#         mock_response.raise_for_status = Mock()
#         mock_response.json.return_value = {"workflow_runs": mock_workflow_runs}
#         mock_get.return_value = mock_response
#         runs = collector.collect_workflow_runs("main", days=7)
# 
#         assert len(runs) == 3, "Runs must not be empty"
#         assert runs[0]["name"] == "Auto-Fix Common Issues", "Condition must be true"
#         mock_get.assert_called_once()
# 
#     @patch("collect_telemetry.requests.get")
#     def test_collect_workflow_runs_pagination(self, mock_get, collector):
#     def test_collect_workflow_runs_pagination(self, mock_get, collector):
#         """Test workflow run collection with pagination."""
#         # First page: 100 results
#         first_page = [{"id": i} for i in range(100)]
#         # Second page: 50 results (last page)
#         second_page = [{"id": i} for i in range(100, 150)]
#         mock_responses = [
#             Mock(
#                 json=Mock(return_value={"workflow_runs": first_page}),
#                 raise_for_status=Mock(),
#             ),
#             Mock(
#                 json=Mock(return_value={"workflow_runs": second_page}),
#                 raise_for_status=Mock(),
#             ),
#         ]
#         mock_get.side_effect = mock_responses
# 
#         runs = collector.collect_workflow_runs("main", days=7, max_pages=10)
# 
#         assert len(runs) == 150, "Runs must not be empty"
#         assert mock_get.call_count == 2, "Count must be greater than zero"
# 
#     @patch("collect_telemetry.requests.get")
#     def test_collect_job_details(self, mock_get, collector, mock_jobs):
#     def test_collect_job_details(self, mock_get, collector, mock_jobs):
#         """Test job details collection."""
#         mock_response = Mock()
#         mock_response.raise_for_status = Mock()
#         mock_response.json.return_value = {"jobs": mock_jobs}
#         mock_get.return_value = mock_response
#         jobs = collector.collect_job_details(1001)
# 
#         assert len(jobs) == 1, "Jobs must not be empty"
#         assert jobs[0]["name"] == "auto-fix", "Condition must be true"
# 
#     @patch("collect_telemetry.requests.get")
#     def test_collect_artifacts(self, mock_get, collector, mock_artifacts):
#     def test_collect_artifacts(self, mock_get, collector, mock_artifacts):
#         """Test artifact collection."""
#         mock_response = Mock()
#         mock_response.raise_for_status = Mock()
#         mock_response.json.return_value = {"artifacts": mock_artifacts}
#         mock_get.return_value = mock_response
#         artifacts = collector.collect_artifacts(1001)
# 
#         assert len(artifacts) == 1, "Artifacts must not be empty"
#         assert artifacts[0]["name"] == "test-results", "Result must not be empty"
# 
#     @patch("collect_telemetry.TelemetryCollector.collect_artifacts")
#     @patch("collect_telemetry.TelemetryCollector.collect_job_details")
#     @patch("collect_telemetry.TelemetryCollector.collect_workflow_runs")
#     def test_generate_report(
#         self,
#         mock_collect_runs,
#         mock_collect_jobs,
#         mock_collect_artifacts,
#         collector,
#         mock_workflow_runs,
#         mock_jobs_by_run,
#         mock_artifacts,
#         tmp_path,
#     ):
#     ):
#         """Test telemetry report generation."""
#         mock_collect_runs.return_value = mock_workflow_runs
#         # Use side_effect to return different jobs for different runs
#         mock_collect_jobs.side_effect = lambda run_id: mock_jobs_by_run.get(run_id, [])
#         mock_collect_artifacts.return_value = mock_artifacts
#         output_file = tmp_path / "test_report.json"
#         report = collector.generate_report("main", days=7, output=str(output_file))
#         # Verify report structure
#         assert "generated_at" in report, "Condition must be true"
#         assert "repository" in report, "Condition must be true"
#         assert report["repository"] == "test-owner/test-repo", "rep is not valid"
#         assert report["branch"] == "main", "rep is not valid"
#         assert report["days_analyzed"] == 7, "rep is not valid"
# 
#         # Verify summary
#         assert report["summary"]["total_runs"] == 3, "rep is not valid"
#         assert report["summary"]["failed_runs"] == 2, "rep is not valid"
#         assert report["summary"]["failure_rate"] > 0, "rep must be greater than zero"
# 
#         # Verify pattern distribution
#         assert "auto-fix" in report["pattern_distribution"], "Condition must be true"
#         # Note: coverage-timeout pattern may or may not be present depending on mock data
#         # The mock data includes a timed_out conclusion which should trigger this pattern
#         assert "coverage-timeout" in report["pattern_distribution"], "Condition must be true"
# 
#         # Verify failed runs
#         assert len(report["failed_runs"]) == 2, "Collection must not be empty"
# 
#         # Verify file was written
#         assert output_file.exists(), "Condition must be true"
#         with open(output_file) as f:
#             saved_report = json.load(f)
#             assert saved_report["repository"] == "test-owner/test-repo", "saved_rep is not valid"
#             assert saved_report["repository"] == "test-owner/test-repo", "saved_rep is not valid"
# 
#     def test_telemetry_report_structure(self, collector):
#     def test_telemetry_report_structure(self, collector):
#         """Test that telemetry report has correct structure."""
#         # Create minimal mock data
#         with patch.object(collector, "collect_workflow_runs", return_value=[]):
#             report = collector.generate_report("main", output=os.path.join(tempfile.gettempdir(), "test.json"))
#         required_keys = [
#         required_keys = [
#             "generated_at",
#             "repository",
#             "branch",
#             "days_analyzed",
#             "summary",
#             "pattern_distribution",
#             "failed_runs",
#         ]
#         for key in required_keys:
#             assert key in report, f"Missing required key: {key}"
#         # Verify summary structure
#         assert "total_runs" in report["summary"], "Condition must be true"
#         assert "failed_runs" in report["summary"], "Condition must be true"
#         assert "failure_rate" in report["summary"], "Condition must be true"
#         for dist in [{}, {"self-healing": 1}, {"unknown": 5, "self-healing": 6}]:
#             result = collector.analyze_multi_job_cascade(self._make_report(dist))
#             assert required.issubset(, "Condition must be true"
#                 result.keys()
#             ), f"Missing keys for dist={dist}: {required - result.keys()}"
# 
#     @pytest.fixture
#     def collector(self):
#         return TelemetryCollector(
#             owner="test-owner", repo="test-repo", token="test-token"
#         )  # pragma: allowlist secret
# 
#     def test_classify_run_rebase_gate(self, collector):
#     def test_classify_run_rebase_gate(self, collector):
#         """--classify-run returns rebase-gate for branch-rebase-gate workflow failures."""
#         # The branch-rebase-gate.yml workflow has run name "🔀 Branch Rebase Gate"
#         # which contains "rebase" — a rebase-gate keyword.
#         run = {"name": "🔀 Branch Rebase Gate", "id": 99}
#         jobs = [{"name": "REQ-10: Branch Rebase Check"}]
#         assert collector.classify_failure(run, jobs) == "rebase-gate"
#     def test_classify_run_auth_delegation(self, collector):
#     def test_classify_run_auth_delegation(self, collector):
#         """--classify-run returns auth-delegation for agent-auth-delegation failures.
#         Note: "Agent Token Delegation" contains "agent token" (auth-delegation keyword)
#         and is therefore classified as auth-delegation, not rebase-gate, even when
#         it fails due to the REQ-10 step.  Both patterns are non-fixable; the
#         self-healing CI correctly escalates in either case.
#         self-healing CI correctly escalates in either case.
#         """
#         run = {"name": "Agent Token Delegation", "id": 99}
#         jobs = [{"name": "🧠 Cognitive Pre-flight Check"}]
#         assert collector.classify_failure(run, jobs) == "auth-delegation"
#     def test_classify_run_unknown_fallback(self, collector):
#     def test_classify_run_unknown_fallback(self, collector):
#         """--classify-run returns 'unknown' when no keywords match."""
#         run = {"name": "Completely Unrecognised Workflow XYZ", "id": 99}
#         jobs = [{"name": "some-job-with-no-matching-keywords"}]
#         assert collector.classify_failure(run, jobs) == "unknown"
#     def test_classify_run_dependency_submission(self, collector):
#     def test_classify_run_dependency_submission(self, collector):
#         """'Automatic Dependency Submission' runs classify as security-scan (S150 fix).
#         Run 23250109072 was a GitHub Advanced Security dependency-graph submission
#         that failed with a transient GitHub API error.  Before S150 it was always
#         classified as 'unknown' because no keyword matched its name.
#         classified as 'unknown' because no keyword matched its name.
#         """
#         run = {"name": "Automatic Dependency Submission (Python)", "id": 23250109072}
#         jobs = [{"name": "submit-pypi"}]
#         assert collector.classify_failure(run, jobs) == "security-scan"
#     def test_classify_run_main_entrypoint_prints_pattern(self, capsys):
#     def test_classify_run_main_entrypoint_prints_pattern(self, capsys):
#         """main() with --classify-run prints the pattern and exits cleanly."""
#         import collect_telemetry as ct_mod
#         mock_run_resp = Mock()
#         mock_run_resp.json.return_value = {
#         mock_run_resp.json.return_value = {
#             "name": "Resilient Validation Suite",
#             "id": 12345,
#         }
#         mock_run_resp.raise_for_status = Mock()
#         mock_jobs_resp = Mock()
#         mock_jobs_resp.json.return_value = {"jobs": [{"name": "pytest resilient validation"}]}
#         mock_jobs_resp.raise_for_status = Mock()
# 
#         with (
#             patch("requests.get", side_effect=[mock_run_resp, mock_jobs_resp]),
#             patch.object(
#                 sys,
#                 sys,
#                 "argv",
#                 [
#                     "collect_telemetry.py",
#                     "--owner",
#                     "test-owner",
#                     "--repo",
#                     "test-repo",
#                     "--token",
#                     "test-tok",
#                     "--classify-run",
#                     "12345",
#                 ],
#             ),
#         ):
#             ct_mod.main()
#         captured = capsys.readouterr()
#         assert captured.out.strip() == "test-infrastructure", "Condition must be true"
# 
#     def test_classify_run_api_error_prints_unknown(self, capsys):
#     def test_classify_run_api_error_prints_unknown(self, capsys):
#         """main() with --classify-run prints 'unknown' when API call fails."""
#         import collect_telemetry as ct_mod
#         with (
#             patch("requests.get", side_effect=Exception("network error")),
#             patch.object(
#                 sys,
#                 sys,
#                 "argv",
#                 [
#                     "collect_telemetry.py",
#                     "--owner",
#                     "test-owner",
#                     "--repo",
#                     "test-repo",
#                     "--token",
#                     "test-tok",
#                     "--classify-run",
#                     "99999",
#                 ],
#             ),
#         ):
#             ct_mod.main()
#         captured = capsys.readouterr()
#         assert "unknown" in captured.out, "Condition must be true"
#             result = collector.analyze_multi_job_cascade(self._make_report(dist))
#             assert required.issubset(, "Condition must be true"
#                 result.keys()
#             ), f"Missing keys for dist={dist}: {required - result.keys()}"
# 
#     @pytest.fixture
#     def collector(self):
#         return TelemetryCollector(
#             owner="test-owner", repo="test-repo", token="test-token"
#         )  # pragma: allowlist secret
# 
#     def _make_report(self, distribution: dict) -> dict:
#     def _make_report(self, distribution: dict) -> dict:
#         """Build a minimal telemetry_data dict with the given pattern_distribution."""
#         return {"pattern_distribution": distribution}
#     def test_no_failures_returns_no_cascade(self, collector):
#         report = self._make_report({})
#         result = collector.analyze_multi_job_cascade(report)
#         assert result["cascade_detected"] is False, "Result must not be empty"
#         assert result["cascade_rate"] == 0.0, "Result must not be empty"
#         assert result["self_healing_count"] == 0, "Result must not be empty"
#         assert result["total_failures"] == 0, "Result must not be empty"
#         assert result["self_healing_count"] == 0, "Result must not be empty"
#         assert result["total_failures"] == 0, "Result must not be empty"
# 
#     def test_missing_pattern_distribution_key(self, collector):
#     def test_missing_pattern_distribution_key(self, collector):
#         """Missing key is treated as empty → no cascade."""
#         result = collector.analyze_multi_job_cascade({})
#         assert result["cascade_detected"] is False, "Result must not be empty"
#         assert result["cascade_rate"] == 0.0, "Result must not be empty"
#     def test_no_cascade_when_self_healing_below_threshold(self, collector):
#         dist = {"self-healing": 5, "unknown": 10, "import-error": 5}
#         result = collector.analyze_multi_job_cascade(self._make_report(dist))
#         assert result["cascade_detected"] is False, "Result must not be empty"
#         assert result["cascade_rate"] == pytest.approx(5 / 20), "Result must not be empty"
#         assert result["self_healing_count"] == 5, "Result must not be empty"
#         assert result["total_failures"] == 20, "Result must not be empty"
#         assert result["self_healing_count"] == 5, "Result must not be empty"
#         assert result["total_failures"] == 20, "Result must not be empty"
# 
#     def test_no_cascade_exactly_at_50_percent(self, collector):
#     def test_no_cascade_exactly_at_50_percent(self, collector):
#         """Exactly 50% is NOT considered a cascade (threshold is > 50%)."""
#         dist = {"self-healing": 5, "unknown": 5}
#         result = collector.analyze_multi_job_cascade(self._make_report(dist))
#         assert result["cascade_detected"] is False, "Result must not be empty"
#         assert result["cascade_rate"] == pytest.approx(0.5), "Result must not be empty"
#     def test_no_cascade_recommended_action_contains_top_pattern(self, collector):
#         dist = {"unknown": 10, "self-healing": 3, "ruff-violation": 2}
#         result = collector.analyze_multi_job_cascade(self._make_report(dist))
#         assert result["cascade_detected"] is False, "Result must not be empty"
#         assert "unknown" in result["recommended_action"], "Result must not be empty"
#         assert "10" in result["recommended_action"], "Result must not be empty"
#         assert "collect_telemetry.py" in result["recommended_action"], "Result must not be empty"
# 
#     def test_cascade_detected_when_self_healing_dominant(self, collector):
#     # ── cascade DETECTED (>50%) ──────────────────────────────────────────────
#     def test_cascade_detected_when_self_healing_dominant(self, collector):
#     def test_cascade_detected_when_self_healing_dominant(self, collector):
#         """S172 reference distribution: 126 self-healing / 133 total."""
#         dist = {
#             "self-healing": 126,
#             "unknown": 2,
#             "embedding-rebuild": 1,
#             "auto-fix": 1,
#             "integration-branch-direct-session": 1,
#             "coverage-timeout": 1,
#             "security-scan": 1,
#         }
#         result = collector.analyze_multi_job_cascade(self._make_report(dist))
#         assert result["cascade_detected"] is True, "Result must not be empty"
#         # cascade_rate is rounded to 4 decimal places in the implementation
#         assert result["cascade_rate"] == pytest.approx(126 / 133, abs=5e-5)
#         assert result["self_healing_count"] == 126, "Result must not be empty"
#         assert result["total_failures"] == 133, "Result must not be empty"
#     def test_cascade_detected_just_above_threshold(self, collector):
#     def test_cascade_detected_just_above_threshold(self, collector):
#         """51% self-healing should trigger cascade."""
#         dist = {"self-healing": 51, "other": 49}
#         result = collector.analyze_multi_job_cascade(self._make_report(dist))
#         assert result["cascade_detected"] is True, "Result must not be empty"
#         assert result["cascade_rate"] == pytest.approx(0.51), "Result must not be empty"
#     def test_cascade_root_cause_mentions_venv_recreation(self, collector):
#     def test_cascade_root_cause_mentions_venv_recreation(self, collector):
#         """Root cause string must reference venv recreation (not 'pip fallback')."""
#         dist = {"self-healing": 100, "unknown": 1}
#         result = collector.analyze_multi_job_cascade(self._make_report(dist))
#         assert result["cascade_detected"] is True, "Result must not be empty"
#         rc = result["root_cause"].lower()
#         assert "venv" in rc, "Condition must be true"
#         assert "python3 -m venv" in result["root_cause"] or "venv_ci" in rc, "Result must not be empty"
#     def test_cascade_recommended_action_mentions_venv_recreation(self, collector):
#         dist = {"self-healing": 100, "unknown": 1}
#         result = collector.analyze_multi_job_cascade(self._make_report(dist))
#         assert result["cascade_detected"] is True, "Result must not be empty"
#         ra = result["recommended_action"]
#         assert "python3 -m venv" in ra, "Condition must be true"
#         assert ".venv_ci/bin/pip" in ra, "Condition must be true"
#         # Must NOT instruct operator to look for a system-pip fallback
#         assert "system pip" not in ra.lower(), "Condition must be true"
#         assert "|| pip" not in ra, "Condition must be true"
# 
#     def test_cascade_100_percent_self_healing(self, collector):
#     def test_cascade_100_percent_self_healing(self, collector):
#         """All failures are self-healing — should still detect cascade."""
#         dist = {"self-healing": 50}
#         result = collector.analyze_multi_job_cascade(self._make_report(dist))
#         assert result["cascade_detected"] is True, "Result must not be empty"
#         assert result["cascade_rate"] == pytest.approx(1.0), "Result must not be empty"
#         assert result["self_healing_count"] == 50, "Result must not be empty"
#         assert result["total_failures"] == 50, "Result must not be empty"
#     def test_result_always_contains_required_keys(self, collector):
#         required = {
# 
#     def test_result_always_contains_required_keys(self, collector):
#         required = {
#             "cascade_detected",
#             "cascade_rate",
#             "self_healing_count",
#             "total_failures",
#             "root_cause",
#             "recommended_action",
#             "pattern_distribution",
#         }
#         for dist in [{}, {"self-healing": 1}, {"unknown": 5, "self-healing": 6}]:
#             result = collector.analyze_multi_job_cascade(self._make_report(dist))
#             assert required.issubset(, "Condition must be true"
#                 result.keys()
#             ), f"Missing keys for dist={dist}: {required - result.keys()}"
#     def test_cascade_rate_rounded_to_4_decimal_places(self, collector):
#         dist = {"self-healing": 2, "unknown": 3}  # 0.4 exactly
#         result = collector.analyze_multi_job_cascade(self._make_report(dist))
#         assert isinstance(result["cascade_rate"], float)
#         # round() to 4 places means no more than 4 decimal digits
#         assert result["cascade_rate"] == round(result["cascade_rate"], 4)


class TestCancelledRunsHandling:
    """Tests for the cancelled-run separation introduced to fix the
    42.7% false-positive CI failure rate (issue #4194).

    Cancelled runs are concurrency-guard no-ops from self-approve, healer, and
    rescue workflows. They must NOT be counted as genuine failures in
    summary.failed_runs or influence failure_rate; instead they are reported
    separately under summary.cancelled_runs.
    """

    @pytest.fixture
    def collector(self):
        return TelemetryCollector(
            owner="test-owner", repo="test-repo", token="test-token"
        )  # pragma: allowlist secret

    def _make_run(self, run_id, name, conclusion):
        return {
            "id": run_id,
            "name": name,
            "html_url": f"https://github.com/test/test/actions/runs/{run_id}",
            "conclusion": conclusion,
            "created_at": "2024-01-01T00:00:00Z",
        }

    @patch("collect_telemetry.TelemetryCollector.collect_artifacts")
    @patch("collect_telemetry.TelemetryCollector.collect_job_details")
    @patch("collect_telemetry.TelemetryCollector.collect_workflow_runs")
    def test_cancelled_excluded_from_failed_runs(
        self, mock_runs, mock_jobs, mock_artifacts, collector, tmp_path
    ):
        """Cancelled runs must not appear in summary.failed_runs or failed_runs list."""
        runs = [
            self._make_run(1, "⚡ Self-Approve Pending Workflow Runs", "cancelled"),
            self._make_run(2, "⚡ Self-Approve Pending Workflow Runs", "cancelled"),
            self._make_run(3, "CI — Optimized", "failure"),
        ]
        mock_runs.return_value = runs
        mock_jobs.return_value = []
        mock_artifacts.return_value = []

        report = collector.generate_report("main", output=str(tmp_path / "r.json"))

        assert report["summary"]["failed_runs"] == 1, "rep is not valid"
        assert len(report["failed_runs"]) == 1, "Collection must not be empty"
        assert report["failed_runs"][0]["run_id"] == 3, "rep is not valid"

    @patch("collect_telemetry.TelemetryCollector.collect_artifacts")
    @patch("collect_telemetry.TelemetryCollector.collect_job_details")
    @patch("collect_telemetry.TelemetryCollector.collect_workflow_runs")
    def test_cancelled_counted_in_cancelled_runs_field(
        self, mock_runs, mock_jobs, mock_artifacts, collector, tmp_path
    ):
        """summary.cancelled_runs must equal the number of cancelled runs."""
        runs = [
            self._make_run(1, "⚡ Self-Approve", "cancelled"),
            self._make_run(2, "Copilot Healer Auto-Poster", "cancelled"),
            self._make_run(3, "CI — Optimized", "success"),
        ]
        mock_runs.return_value = runs
        mock_jobs.return_value = []
        mock_artifacts.return_value = []

        report = collector.generate_report("main", output=str(tmp_path / "r.json"))

        assert report["summary"]["cancelled_runs"] == 2, "rep is not valid"

    @patch("collect_telemetry.TelemetryCollector.collect_artifacts")
    @patch("collect_telemetry.TelemetryCollector.collect_job_details")
    @patch("collect_telemetry.TelemetryCollector.collect_workflow_runs")
    def test_failure_rate_excludes_cancelled(
        self, mock_runs, mock_jobs, mock_artifacts, collector, tmp_path
    ):
        """Failure rate must be computed from genuine failures / total runs only."""
        runs = [
            # 3 cancelled — should NOT count toward failure_rate numerator
            self._make_run(1, "Self-Approve", "cancelled"),
            self._make_run(2, "Self-Approve", "cancelled"),
            self._make_run(3, "Self-Approve", "cancelled"),
            # 1 genuine failure
            self._make_run(4, "CI Tests", "failure"),
            # 1 success
            self._make_run(5, "CI Tests", "success"),
        ]
        mock_runs.return_value = runs
        mock_jobs.return_value = []
        mock_artifacts.return_value = []

        report = collector.generate_report("main", output=str(tmp_path / "r.json"))

        # 1 failure / 5 total = 0.2, NOT 4/5 = 0.8
        assert report["summary"]["failure_rate"] == pytest.approx(1 / 5), "rep is not valid"
        assert report["summary"]["total_runs"] == 5, "rep is not valid"
        assert report["summary"]["failed_runs"] == 1, "rep is not valid"
        assert report["summary"]["cancelled_runs"] == 3, "rep is not valid"

    @patch("collect_telemetry.TelemetryCollector.collect_artifacts")
    @patch("collect_telemetry.TelemetryCollector.collect_job_details")
    @patch("collect_telemetry.TelemetryCollector.collect_workflow_runs")
    def test_timed_out_still_counts_as_failure(
        self, mock_runs, mock_jobs, mock_artifacts, collector, tmp_path
    ):
        """timed_out must still be treated as a genuine failure, not operational overhead."""
        runs = [
            self._make_run(1, "Coverage Suite", "timed_out"),
            self._make_run(2, "Self-Approve", "cancelled"),
        ]
        mock_runs.return_value = runs
        mock_jobs.return_value = []
        mock_artifacts.return_value = []

        report = collector.generate_report("main", output=str(tmp_path / "r.json"))

        assert report["summary"]["failed_runs"] == 1, "rep is not valid"
        assert report["summary"]["cancelled_runs"] == 1, "rep is not valid"


class TestApprovalCascadeClassification:
    """Tests for the approval-cascade pattern bucket added to fix inflated
    'unknown' counts from ⚡ Self-Approve Pending Workflow Runs cancellations.
    """

    @pytest.fixture
    def collector(self):
        return TelemetryCollector(
            owner="test-owner", repo="test-repo", token="test-token"
        )  # pragma: allowlist secret

    def test_self_approve_workflow_classified_as_approval_cascade(self, collector):
        """⚡ Self-Approve Pending Workflow Runs → approval-cascade, not unknown."""
        run = {"name": "⚡ Self-Approve Pending Workflow Runs"}
        jobs = [{"name": "approve-pending", "steps": []}]
        assert collector.classify_failure(run, jobs) == "approval-cascade"

    def test_pending_workflow_in_job_name(self, collector):
        """'pending workflow' keyword in job name triggers approval-cascade."""
        run = {"name": "Some Automation Workflow"}
        jobs = [{"name": "pending workflow check", "steps": []}]
        assert collector.classify_failure(run, jobs) == "approval-cascade"

    def test_flush_queued_runs_classified(self, collector):
        """flush-queued keyword triggers approval-cascade."""
        run = {"name": "Flush Queued Runs"}
        jobs = [{"name": "flush-queued", "steps": []}]
        assert collector.classify_failure(run, jobs) == "approval-cascade"

    def test_approval_cascade_does_not_match_generic_names(self, collector):
        """Unrelated workflow names must NOT match approval-cascade."""
        run = {"name": "CI Tests — Optimized with Caching"}
        jobs = [{"name": "pytest", "steps": []}]
        result = collector.classify_failure(run, jobs)
        assert result != "approval-cascade", "Result must not be empty"

    def test_approval_cascade_bucket_defined_in_pattern_keywords(self, collector):
        """The approval-cascade bucket must exist in PATTERN_KEYWORDS."""
        assert "approval-cascade" in collector.PATTERN_KEYWORDS, "Condition must be true"
        keywords = collector.PATTERN_KEYWORDS["approval-cascade"]
        assert any("self-approve" in kw for kw in keywords), "Condition must be true"
        assert any("pending workflow" in kw or "approve pending" in kw for kw in keywords), "Condition must be true"
