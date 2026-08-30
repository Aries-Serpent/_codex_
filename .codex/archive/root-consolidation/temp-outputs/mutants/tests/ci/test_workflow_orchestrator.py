"""
Tests for Workflow Orchestrator.

Tests the telemetry-driven workflow orchestration logic.
"""

# Import the module to test
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "ci"))

from workflow_orchestrator import WorkflowOrchestrator


class TestWorkflowOrchestrator:
    """Test suite for WorkflowOrchestrator class."""

    @pytest.fixture
    def sample_telemetry(self):
        """Create sample telemetry data."""
        return {
            "generated_at": "2024-01-01T00:00:00Z",
            "repository": "test-owner/test-repo",
            "branch": "main",
            "days_analyzed": 7,
            "summary": {
                "total_runs": 100,
                "failed_runs": 15,
                "failure_rate": 0.15,
            },
            "pattern_distribution": {
                "auto-fix": 5,
                "coverage-timeout": 3,
                "test-infrastructure": 2,
                "unknown": 5,
            },
            "failed_runs": [],
        }

    @pytest.fixture
    def orchestrator_small(self, sample_telemetry):
        """Create orchestrator for small PR."""
        return WorkflowOrchestrator(
            pr_size="small",
            telemetry_data=sample_telemetry,
            changed_files=["src/module.py", "tests/test_module.py"],
        )

    @pytest.fixture
    def orchestrator_large(self, sample_telemetry):
        """Create orchestrator for large PR."""
        return WorkflowOrchestrator(
            pr_size="large",
            telemetry_data=sample_telemetry,
            changed_files=[f"file{i}.py" for i in range(200)],
        )

    def test_initialization(self, orchestrator_small):
        """Test orchestrator initialization."""
        assert orchestrator_small.pr_size == "small", "pr_size is not valid"
        assert "pattern_distribution" in orchestrator_small.telemetry, "Condition must be true"
        assert len(orchestrator_small.changed_files) == 2, "Collection must not be empty"

    def test_analyze_patterns(self, orchestrator_small):
        """Test pattern analysis from telemetry."""
        patterns = orchestrator_small.analyze_patterns()

        assert "auto-fix" in patterns, "Condition must be true"
        assert patterns["auto-fix"] == 5, "Condition must be true"
        assert patterns["coverage-timeout"] == 3, "Condition must be true"
        assert patterns["test-infrastructure"] == 2, "Condition must be true"

    def test_should_run_workflow_always(self, orchestrator_small):
        """Test workflow with 'always' trigger."""
        assert orchestrator_small.should_run_workflow("smoke-tests", "always") is True

    def test_should_run_workflow_small_pr(self, orchestrator_small):
        """Test workflow with size-based trigger on small PR."""
        assert orchestrator_small.should_run_workflow("unit-tests", "small") is True
        assert orchestrator_small.should_run_workflow("unit-tests", "small|medium") is True

    def test_should_run_workflow_large_pr(self, orchestrator_large):
        """Test workflow with size-based trigger on large PR."""
        assert orchestrator_large.should_run_workflow("unit-tests", "small") is False
        assert orchestrator_large.should_run_workflow("unit-tests", "small|medium") is False

    def test_should_run_workflow_manual(self, orchestrator_small):
        """Test workflow with manual trigger."""
        assert orchestrator_small.should_run_workflow("slow-tests", "manual") is False

    def test_get_pattern_workflows(self, orchestrator_small):
        """Test getting workflows based on patterns."""
        patterns = {"auto-fix": 5, "coverage-timeout": 3}
        workflows = orchestrator_small.get_pattern_workflows(patterns)

        assert "auto-fix-validation" in workflows, "Condition must be true"
        assert "coverage-with-timeout" in workflows, "Condition must be true"

    def test_analyze_changed_files_python(self, orchestrator_small):
        """Test file analysis with Python files."""
        workflows = orchestrator_small.analyze_changed_files()

        assert "python-tests" in workflows, "Condition must be true"
        assert "type-checking" in workflows, "Condition must be true"
        assert "linting" in workflows, "Condition must be true"

    def test_analyze_changed_files_yaml(self):
        """Test file analysis with YAML files."""
        orchestrator = WorkflowOrchestrator(
            pr_size="small",
            telemetry_data={},
            changed_files=[".github/workflows/test.yml"],
        )

        workflows = orchestrator.analyze_changed_files()
        assert "yaml-validation" in workflows, "Condition must be true"

    def test_analyze_changed_files_docker(self):
        """Test file analysis with Docker files."""
        orchestrator = WorkflowOrchestrator(
            pr_size="small",
            telemetry_data={},
            changed_files=["Dockerfile", ".dockerignore"],
        )

        workflows = orchestrator.analyze_changed_files()
        assert "container-build" in workflows, "Condition must be true"

    def test_analyze_changed_files_docs(self):
        """Test file analysis with documentation files."""
        orchestrator = WorkflowOrchestrator(
            pr_size="small",
            telemetry_data={},
            changed_files=["docs/README.md", "CHANGELOG.md"],
        )

        workflows = orchestrator.analyze_changed_files()
        assert "docs-build" in workflows, "Condition must be true"

    def test_generate_plan_small_pr(self, orchestrator_small):
        """Test plan generation for small PR."""
        plan = orchestrator_small.generate_plan()

        # Check structure
        assert "workflows_to_run" in plan, "Condition must be true"
        assert "workflows_to_skip" in plan, "Condition must be true"
        assert "reasons" in plan, "Condition must be true"
        assert "patterns_detected" in plan, "Condition must be true"

        # Critical workflows should always run
        assert "smoke-tests" in plan["workflows_to_run"], "Condition must be true"
        assert "pr-size-analyzer" in plan["workflows_to_run"], "Condition must be true"
        assert "security-scan" in plan["workflows_to_run"], "Condition must be true"

        # Standard workflows for small PR
        assert "unit-tests" in plan["workflows_to_run"], "Condition must be true"

        # Comprehensive workflows for small PR
        assert "integration-tests" in plan["workflows_to_run"], "Condition must be true"

    def test_generate_plan_large_pr(self, orchestrator_large):
        """Test plan generation for large PR."""
        plan = orchestrator_large.generate_plan()

        # Critical workflows should always run
        assert "smoke-tests" in plan["workflows_to_run"], "Condition must be true"

        # Standard workflows should be skipped for large PR
        assert "unit-tests" in plan["workflows_to_skip"], "Condition must be true"

        # Comprehensive workflows should be skipped
        assert "integration-tests" in plan["workflows_to_skip"], "Condition must be true"

    def test_generate_plan_with_patterns(self, orchestrator_small):
        """Test plan includes pattern-based workflows."""
        plan = orchestrator_small.generate_plan()

        # Pattern-based workflows should be added
        assert "auto-fix-validation" in plan["workflows_to_run"], "Condition must be true"
        assert "coverage-with-timeout" in plan["workflows_to_run"], "Condition must be true"

    def test_generate_plan_with_file_workflows(self, orchestrator_small):
        """Test plan includes file-based workflows."""
        plan = orchestrator_small.generate_plan()

        # File-based workflows should be added
        assert "python-tests" in plan["workflows_to_run"], "Condition must be true"
        assert "type-checking" in plan["workflows_to_run"], "Condition must be true"

    def test_estimate_duration(self, orchestrator_small):
        """Test duration estimation."""
        _ = orchestrator_small.generate_plan()  # Generate plan first
        duration = orchestrator_small.estimate_duration()

        assert "total_minutes" in duration, "Condition must be true"
        assert "total_hours" in duration, "Condition must be true"
        assert "workflow_durations" in duration, "Condition must be true"

        assert duration["total_minutes"] > 0, "Value must be greater than zero"
        assert duration["total_hours"] > 0, "Value must be greater than zero"

    def test_workflow_reasons(self, orchestrator_small):
        """Test that all workflows have reasons."""
        plan = orchestrator_small.generate_plan()

        for workflow in plan["workflows_to_run"]:
            assert workflow in plan["reasons"], "w is not valid"
            assert len(plan["reasons"][workflow]) > 0, "Collection must not be empty"

    def test_empty_telemetry(self):
        """Test orchestrator with empty telemetry."""
        orchestrator = WorkflowOrchestrator(pr_size="small", telemetry_data={}, changed_files=[])

        plan = orchestrator.generate_plan()

        # Should still have critical workflows
        assert len(plan["workflows_to_run"]) > 0, "Collection must not be empty"

    def test_workflow_categories_exist(self, orchestrator_small):
        """Test that workflow categories are defined."""
        assert "critical" in WorkflowOrchestrator.WORKFLOW_CATEGORIES, "Condition must be true"
        assert "standard" in WorkflowOrchestrator.WORKFLOW_CATEGORIES, "Condition must be true"
        assert "comprehensive" in WorkflowOrchestrator.WORKFLOW_CATEGORIES, "Condition must be true"
        assert "on-demand" in WorkflowOrchestrator.WORKFLOW_CATEGORIES, "Condition must be true"

    def test_pattern_workflows_mapping(self):
        """Test pattern to workflow mapping exists."""
        assert "auto-fix" in WorkflowOrchestrator.PATTERN_WORKFLOWS, "Condition must be true"
        assert "test-infrastructure" in WorkflowOrchestrator.PATTERN_WORKFLOWS, "Condition must be true"
        assert "coverage-timeout" in WorkflowOrchestrator.PATTERN_WORKFLOWS, "Condition must be true"

    def test_no_duplicate_workflows(self, orchestrator_small):
        """Test that plan doesn't contain duplicate workflows."""
        plan = orchestrator_small.generate_plan()

        workflows_to_run = plan["workflows_to_run"]
        unique_workflows = set(workflows_to_run)

        assert len(workflows_to_run) == len(unique_workflows), "Workflows_to_run must not be empty"
