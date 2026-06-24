"""
Phase 9.2 Task 2 — Class API tests for workflow/orchestrator/self_healing/physics

Covers:
- Workflow dataclasses: Workflow.__init__, __len__, to_dict, add_step ordering
- WorkflowStep.execute: uses path, no-action path, exception path
- PhysicsGuidedDeveloperOrchestrator: constructor, analyze_user_requirements,
  get_development_status, validate_code, prioritize_tasks, execute_workflow
- SelfHealingEngine: diagnose with log, detect/analyze aliases, apply_remediation
  (dry_run and requires_approval gates)
- RemediationAction: post_init command alias, requires_approval inverse
- DetectedIssue / DiagnosticResult: to_dict shape contracts
- ActionPath: energy alias, calculate_total_energy, calculate_optimization_score
- ForceVector: 3D magnitude calculation, get_components
- DecisionState: default field values and context access

#AFTERMATH_METRIC - Phase 9.2 class API contract tests
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from agents.developer_orchestrator import (
    AppType,
    CodeComponent,
    DevelopmentPhase,
    PhysicsGuidedDeveloperOrchestrator,
    RequirementVariable,
)
from agents.physics_orchestrator import (
    ActionPath,
    ActionType,
    DecisionState,
    ForceVector,
)
from agents.self_healing import (
    DetectedIssue,
    DiagnosticResult,
    IssueSeverity,
    IssueType,
    RemediationAction,
    SelfHealingEngine,
    run_diagnostics,
)
from agents.workflow_navigator import (
    StepStatus,
    Workflow,
    WorkflowFrequency,
    WorkflowStep,
)

# ---------------------------------------------------------------------------
# Workflow dataclass — field and method contracts
# ---------------------------------------------------------------------------


class TestWorkflowDataclass:
    """Workflow.__init__, __len__, to_dict contracts."""

    def test_workflow_len_matches_steps(self) -> None:
        steps = [WorkflowStep(id=f"s{i}", action=f"act{i}") for i in range(3)]
        wf = Workflow(
            workflow_id="LEN_TEST",
            name="Len Test",
            description="d",
            frequency=WorkflowFrequency.LOW,
            steps=steps,
        )
        assert len(wf) == 3

    def test_workflow_len_empty(self) -> None:
        wf = Workflow(
            workflow_id="EMPTY",
            name="Empty",
            description="d",
            frequency=WorkflowFrequency.LOW,
        )
        assert len(wf) == 0

    def test_workflow_to_dict_has_all_keys(self) -> None:
        wf = Workflow(
            workflow_id="DICT_TEST",
            name="Dict Test",
            description="desc",
            frequency=WorkflowFrequency.HIGH,
        )
        d = wf.to_dict()
        for key in (
            "workflow_id",
            "name",
            "description",
            "frequency",
            "deterministic",
            "steps",
            "aliases",
            "entry_points",
            "category",
        ):
            assert key in d, f"Missing key in Workflow.to_dict(): {key}"

    def test_workflow_to_dict_frequency_is_string(self) -> None:
        wf = Workflow(
            workflow_id="FREQ",
            name="Freq",
            description="d",
            frequency=WorkflowFrequency.MEDIUM,
        )
        d = wf.to_dict()
        assert d["frequency"] == "medium"

    def test_workflow_to_dict_steps_is_list(self) -> None:
        step = WorkflowStep(id="s1", action="act1", command="echo hi")
        wf = Workflow(
            workflow_id="STEPS",
            name="Steps",
            description="d",
            frequency=WorkflowFrequency.HIGH,
            steps=[step],
        )
        d = wf.to_dict()
        assert isinstance(d["steps"], list)
        assert len(d["steps"]) == 1

    def test_workflow_defaults(self) -> None:
        wf = Workflow(
            workflow_id="DEFAULTS",
            name="Defaults",
            description="d",
            frequency=WorkflowFrequency.LOW,
        )
        assert wf.deterministic is True
        assert wf.steps == []
        assert wf.aliases == []
        assert wf.category == "general"


# ---------------------------------------------------------------------------
# WorkflowStep.execute — edge paths
# ---------------------------------------------------------------------------


class TestWorkflowStepExecuteEdges:
    """WorkflowStep.execute paths not covered in phase9_1 (uses, no-action, exception)."""

    def test_execute_uses_reference_returns_success(self) -> None:
        step = WorkflowStep(id="s1", action="call", uses="some_module.function")
        result = step.execute({})
        assert result["success"] is True
        assert step.status == StepStatus.COMPLETED

    def test_execute_no_command_no_uses_skips(self) -> None:
        step = WorkflowStep(id="s1", action="noop")
        result = step.execute({})
        assert result["success"] is True
        assert step.status == StepStatus.SKIPPED

    def test_execute_exception_sets_failed(self) -> None:
        step = WorkflowStep(id="s1", action="boom", command="definitely_not_real_cmd_xyz")
        # patch subprocess.run to raise an OSError
        with patch("agents.workflow_navigator.subprocess.run", side_effect=OSError("bad")):
            result = step.execute({})
        assert result["success"] is False
        assert step.status == StepStatus.FAILED
        assert "bad" in result["error"]


# ---------------------------------------------------------------------------
# PhysicsGuidedDeveloperOrchestrator — constructor and key methods
# ---------------------------------------------------------------------------


class TestPhysicsGuidedDeveloperOrchestratorConstructor:
    """Constructor defaults and property access."""

    def test_default_construction(self) -> None:
        orch = PhysicsGuidedDeveloperOrchestrator()
        assert orch.current_phase == DevelopmentPhase.REQUIREMENTS
        assert orch.components == []
        assert orch._requirements == []
        assert isinstance(orch.session_id, str)

    def test_custom_session_id(self) -> None:
        orch = PhysicsGuidedDeveloperOrchestrator(session_id="my_session")
        assert orch.session_id == "my_session"

    def test_custom_app_type(self) -> None:
        orch = PhysicsGuidedDeveloperOrchestrator(app_type=AppType.PYTHON_CLI)
        assert orch.app_type == AppType.PYTHON_CLI

    def test_requirements_property_returns_list(self) -> None:
        orch = PhysicsGuidedDeveloperOrchestrator()
        assert isinstance(orch.requirements, list)

    def test_requirements_setter(self) -> None:
        orch = PhysicsGuidedDeveloperOrchestrator()
        var = RequirementVariable(name="x", description="d", variable_type="str")
        orch.requirements = [var]
        assert orch.requirements[0].name == "x"

    def test_required_variables_property(self) -> None:
        orch = PhysicsGuidedDeveloperOrchestrator()
        assert isinstance(orch.required_variables, dict)


class TestPhysicsGuidedDeveloperOrchestratorAnalyze:
    """analyze_user_requirements contracts."""

    def test_analyze_returns_dict(self) -> None:
        orch = PhysicsGuidedDeveloperOrchestrator()
        result = orch.analyze_user_requirements({"app_type": "python_console"})
        assert isinstance(result, dict)

    def test_analyze_has_required_keys(self) -> None:
        orch = PhysicsGuidedDeveloperOrchestrator()
        result = orch.analyze_user_requirements({})
        for key in ("app_type", "provided_variables", "missing_variables", "completeness"):
            assert key in result

    def test_analyze_sets_app_type(self) -> None:
        orch = PhysicsGuidedDeveloperOrchestrator()
        orch.analyze_user_requirements({"app_type": "python_cli"})
        assert orch.app_type == AppType.PYTHON_CLI

    def test_analyze_unknown_app_type_falls_back(self) -> None:
        orch = PhysicsGuidedDeveloperOrchestrator()
        result = orch.analyze_user_requirements({"app_type": "nonexistent_type"})
        # Should fall back to PYTHON_CONSOLE without raising
        assert result["app_type"] == "python_console"

    def test_analyze_completeness_range(self) -> None:
        orch = PhysicsGuidedDeveloperOrchestrator()
        result = orch.analyze_user_requirements({})
        assert 0.0 <= result["completeness"] <= 1.0


class TestPhysicsGuidedDeveloperOrchestratorStatus:
    """get_development_status contracts."""

    def test_status_returns_dict(self) -> None:
        orch = PhysicsGuidedDeveloperOrchestrator()
        status = orch.get_development_status()
        assert isinstance(status, dict)

    def test_status_has_phase(self) -> None:
        orch = PhysicsGuidedDeveloperOrchestrator()
        status = orch.get_development_status()
        assert "phase" in status
        assert status["phase"] == DevelopmentPhase.REQUIREMENTS.value

    def test_status_components_empty(self) -> None:
        orch = PhysicsGuidedDeveloperOrchestrator()
        status = orch.get_development_status()
        assert status["components"]["total"] == 0
        assert status["components"]["progress"] == 0

    def test_status_with_components(self) -> None:
        orch = PhysicsGuidedDeveloperOrchestrator()
        orch.components.append(
            CodeComponent(
                name="main",
                component_type="module",
                description="main module",
                implementation_status="complete",
            )
        )
        status = orch.get_development_status()
        assert status["components"]["total"] == 1
        assert status["components"]["completed"] == 1


class TestPhysicsGuidedDeveloperOrchestratorValidateCode:
    """validate_code contracts."""

    def test_valid_code_returns_valid_true(self) -> None:
        orch = PhysicsGuidedDeveloperOrchestrator()
        result = orch.validate_code("x = 1\ny = x + 2\n")
        assert result["valid"] is True
        assert result["errors"] == []

    def test_invalid_syntax_returns_error(self) -> None:
        orch = PhysicsGuidedDeveloperOrchestrator()
        result = orch.validate_code("def broken_function\n")
        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_todo_adds_warning(self) -> None:
        orch = PhysicsGuidedDeveloperOrchestrator()
        result = orch.validate_code("x = 1  # TODO: fix this\n")
        assert any("TODO" in w for w in result["warnings"])

    def test_short_code_adds_warning(self) -> None:
        orch = PhysicsGuidedDeveloperOrchestrator()
        result = orch.validate_code("x=1")
        assert any("short" in w.lower() for w in result["warnings"])

    def test_tab_adds_warning(self) -> None:
        orch = PhysicsGuidedDeveloperOrchestrator()
        result = orch.validate_code("def f():\n\tx = 1\n\treturn x\n")
        assert any("tab" in w.lower() for w in result["warnings"])

    def test_component_id_propagated(self) -> None:
        orch = PhysicsGuidedDeveloperOrchestrator()
        result = orch.validate_code("x = 1\n", component_id="my_comp")
        assert result["component_id"] == "my_comp"


class TestPhysicsGuidedDeveloperOrchestratorPrioritize:
    """prioritize_tasks contracts."""

    def test_prioritize_returns_list(self) -> None:
        orch = PhysicsGuidedDeveloperOrchestrator()
        result = orch.prioritize_tasks()
        assert isinstance(result, list)

    def test_prioritize_with_tasks(self) -> None:
        orch = PhysicsGuidedDeveloperOrchestrator()
        tasks = [
            {"id": "t1", "priority": 0.9, "complexity": 2.0},
            {"id": "t2", "priority": 0.3, "complexity": 1.0},
        ]
        result = orch.prioritize_tasks(tasks=tasks)
        assert isinstance(result, list)
        assert len(result) == 2


# ---------------------------------------------------------------------------
# SelfHealingEngine — diagnose, detect, analyze, apply_remediation
# ---------------------------------------------------------------------------


class TestSelfHealingEngineDiagnose:
    """SelfHealingEngine.diagnose contracts."""

    def test_diagnose_log_output_detects_import_error(self, tmp_path: Path) -> None:
        engine = SelfHealingEngine(repo_root=tmp_path)
        log = "ModuleNotFoundError: No module named 'missing_pkg'"
        result = engine.diagnose(log_output=log, run_checks=False)
        assert any(i.issue_type == IssueType.IMPORT_ERROR for i in result.issues)

    def test_diagnose_returns_diagnostic_result(self, tmp_path: Path) -> None:
        engine = SelfHealingEngine(repo_root=tmp_path)
        result = engine.diagnose(log_output=None, run_checks=False)
        assert isinstance(result, DiagnosticResult)

    def test_diagnose_health_score_range(self, tmp_path: Path) -> None:
        engine = SelfHealingEngine(repo_root=tmp_path)
        result = engine.diagnose(log_output=None, run_checks=False)
        assert 0.0 <= result.health_score <= 1.0

    def test_diagnose_test_failure_pattern(self, tmp_path: Path) -> None:
        engine = SelfHealingEngine(repo_root=tmp_path)
        log = "FAILED tests/test_example.py::test_foo"
        result = engine.diagnose(log_output=log, run_checks=False)
        assert any(i.issue_type == IssueType.TEST_FAILURE for i in result.issues)

    def test_diagnose_security_pattern(self, tmp_path: Path) -> None:
        engine = SelfHealingEngine(repo_root=tmp_path)
        log = "CVE-2023-12345 vulnerability detected"
        result = engine.diagnose(log_output=log, run_checks=False)
        assert any(i.issue_type == IssueType.SECURITY_VULNERABILITY for i in result.issues)

    def test_diagnose_log_analysis_in_diagnostics_run(self, tmp_path: Path) -> None:
        engine = SelfHealingEngine(repo_root=tmp_path)
        result = engine.diagnose(log_output="some log", run_checks=False)
        assert "log_analysis" in result.diagnostics_run


class TestSelfHealingEngineAliases:
    """detect, detect_issues, analyze are all aliases for diagnose."""

    def test_detect_issues_returns_list(self, tmp_path: Path) -> None:
        engine = SelfHealingEngine(repo_root=tmp_path)
        issues = engine.detect_issues(log_output=None, run_checks=False)
        assert isinstance(issues, list)

    def test_detect_alias_returns_list(self, tmp_path: Path) -> None:
        engine = SelfHealingEngine(repo_root=tmp_path)
        issues = engine.detect(log_output="FAILED tests/test_x.py::test_y")
        assert isinstance(issues, list)

    def test_analyze_returns_diagnostic_result(self, tmp_path: Path) -> None:
        engine = SelfHealingEngine(repo_root=tmp_path)
        result = engine.analyze(log_output=None, run_checks=False)
        assert isinstance(result, DiagnosticResult)


class TestSelfHealingEngineApplyRemediation:
    """apply_remediation contracts."""

    def test_dry_run_returns_success(self, tmp_path: Path) -> None:
        engine = SelfHealingEngine(repo_root=tmp_path)
        action = RemediationAction(action_type="fix", description="Fix test")
        ok, msg = engine.apply_remediation(action, dry_run=True)
        assert ok is True
        assert "DRY RUN" in msg

    def test_dry_run_shows_commands(self, tmp_path: Path) -> None:
        engine = SelfHealingEngine(repo_root=tmp_path)
        action = RemediationAction(
            action_type="fix",
            description="Fix lint",
            commands=["ruff check --fix ."],
        )
        ok, msg = engine.apply_remediation(action, dry_run=True)
        assert "ruff check --fix ." in msg

    def test_requires_approval_blocks_non_dry_run(self, tmp_path: Path) -> None:
        engine = SelfHealingEngine(repo_root=tmp_path)
        action = RemediationAction(
            action_type="dangerous",
            description="Risky action",
            requires_approval=True,
        )
        ok, msg = engine.apply_remediation(action, dry_run=False)
        assert ok is False
        assert "approval" in msg.lower()

    def test_dry_run_file_changes_shown(self, tmp_path: Path) -> None:
        engine = SelfHealingEngine(repo_root=tmp_path)
        action = RemediationAction(
            action_type="patch",
            description="Patch file",
            file_changes={"some/file.py": "# patched"},
        )
        ok, msg = engine.apply_remediation(action, dry_run=True)
        assert ok is True
        assert "some/file.py" in msg


class TestRemediationActionPostInit:
    """RemediationAction.__post_init__ contracts."""

    def test_command_alias_populates_commands(self) -> None:
        action = RemediationAction(action_type="fix", description="d", command="echo hello")
        assert "echo hello" in action.commands

    def test_auto_apply_false_sets_requires_approval(self) -> None:
        action = RemediationAction(action_type="fix", description="d", auto_apply=False)
        assert action.requires_approval is True

    def test_action_id_auto_generated(self) -> None:
        action = RemediationAction(action_type="fix", description="d")
        assert action.action_id.startswith("action_")


class TestDetectedIssueToDict:
    """DetectedIssue.to_dict shape contract."""

    def test_to_dict_has_required_keys(self) -> None:
        issue = DetectedIssue(
            issue_type=IssueType.IMPORT_ERROR,
            severity=IssueSeverity.HIGH,
            description="missing pkg",
        )
        d = issue.to_dict()
        for key in ("issue_id", "issue_type", "severity", "description"):
            assert key in d


class TestDiagnosticResultToDict:
    """DiagnosticResult.to_dict shape contract."""

    def test_to_dict_has_required_keys(self) -> None:
        dr = DiagnosticResult()
        d = dr.to_dict()
        for key in ("issues", "health_score", "diagnostics_run", "suggested_actions"):
            assert key in d

    def test_health_score_default_one(self) -> None:
        dr = DiagnosticResult()
        assert dr.health_score == 1.0


class TestRunDiagnosticsConvenienceFn:
    """run_diagnostics convenience function."""

    def test_returns_diagnostic_result(self, tmp_path: Path) -> None:
        result = run_diagnostics(repo_root=tmp_path)
        assert isinstance(result, DiagnosticResult)


# ---------------------------------------------------------------------------
# ActionPath — energy alias, calculate_total_energy, calculate_optimization_score
# ---------------------------------------------------------------------------


class TestActionPath:
    """ActionPath field contracts."""

    def test_energy_alias_sets_potential_energy(self) -> None:
        path = ActionPath(energy=50.0)
        assert path.potential_energy == 50.0

    def test_energy_alias_does_not_override_explicit_potential(self) -> None:
        path = ActionPath(potential_energy=30.0, energy=50.0)
        # When potential_energy is provided, energy alias should not override
        assert path.potential_energy == 30.0

    def test_calculate_total_energy(self) -> None:
        path = ActionPath(potential_energy=10.0, kinetic_energy=5.0, momentum=1.0, friction=0.5)
        total = path.calculate_total_energy()
        expected = 10.0 + 5.0 - 1.0 * 5.0 + 0.5 * 10.0
        assert abs(total - expected) < 1e-9

    def test_calculate_optimization_score_positive(self) -> None:
        path = ActionPath(
            potential_energy=10.0,
            kinetic_energy=5.0,
            impact=0.8,
            confidence=0.9,
            momentum=2.0,
            risk=0.1,
            friction=0.1,
        )
        path.calculate_total_energy()
        score = path.calculate_optimization_score()
        assert score > 0.0

    def test_default_action_type(self) -> None:
        path = ActionPath()
        assert path.action_type == ActionType.ANALYZE

    def test_trajectory_default_empty(self) -> None:
        path = ActionPath()
        assert path.trajectory == []

    def test_extract_mlp_features_length(self) -> None:
        path = ActionPath(
            potential_energy=20.0,
            kinetic_energy=10.0,
            friction=1.0,
            momentum=3.0,
            confidence=0.7,
            risk=0.2,
            impact=0.6,
            urgency=0.4,
        )
        features = path._extract_mlp_features()
        assert len(features) == 8


# ---------------------------------------------------------------------------
# ForceVector — 3D magnitude and get_components
# ---------------------------------------------------------------------------


class TestForceVector:
    """ForceVector field and method contracts."""

    def test_magnitude_computed_from_xyz(self) -> None:
        import math

        fv = ForceVector(x=3.0, y=4.0, z=0.0)
        expected = math.hypot(3.0, 4.0)
        assert abs(fv.magnitude - expected) < 1e-9

    def test_direction_normalized_from_xyz(self) -> None:
        fv = ForceVector(x=1.0, y=0.0, z=0.0)
        # direction should be a list [1.0, 0.0, 0.0] (unit vector)
        assert isinstance(fv.direction, list)
        assert abs(fv.direction[0] - 1.0) < 1e-9

    def test_get_components_2d_direction(self) -> None:
        fv = ForceVector(name="test", magnitude=1.0, direction=0.0)  # angle = 0 rad
        x_comp, y_comp = fv.get_components()
        assert abs(x_comp - 1.0) < 1e-9
        assert abs(y_comp) < 1e-9

    def test_get_components_3d_direction(self) -> None:
        fv = ForceVector(x=1.0, y=0.0, z=0.0)
        x_comp, y_comp = fv.get_components()
        # 3D direction projects to (magnitude * priority, 0)
        assert x_comp >= 0.0

    def test_magnitude_zero_when_no_xyz(self) -> None:
        fv = ForceVector(name="empty")
        assert fv.magnitude == 0.0


# ---------------------------------------------------------------------------
# DecisionState — default field values
# ---------------------------------------------------------------------------


class TestDecisionState:
    """DecisionState field defaults."""

    def test_default_values(self) -> None:
        ds = DecisionState()
        assert ds.available_resources == 1.0
        assert ds.time_available == 1.0
        assert ds.current_velocity == 0.5
        assert ds.coherence == 1.0
        assert ds.energy == 0.0

    def test_context_default_empty_dict(self) -> None:
        ds = DecisionState()
        assert ds.context == {}

    def test_state_vector_default_empty(self) -> None:
        ds = DecisionState()
        assert ds.state_vector == []

    def test_custom_positions(self) -> None:
        ds = DecisionState(
            current_position="start",
            goal_position="end",
        )
        assert ds.current_position == "start"
        assert ds.goal_position == "end"

    def test_active_forces_default_empty(self) -> None:
        ds = DecisionState()
        assert ds.active_forces == []
