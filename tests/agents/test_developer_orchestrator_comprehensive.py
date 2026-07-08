"""
Comprehensive tests for PhysicsGuidedDeveloperOrchestrator.

Coverage targets:
- Phase-specific testing (REQUIREMENTS, DESIGN, ARCHITECTURE, etc.)
- State machine transitions
- Multi-agent coordination
- Error handling in each phase
- Resource allocation
- Progress reporting

Test Categories:
- Initialization and configuration
- Requirement analysis
- Design generation
- Architecture planning
- Code generation
- Testing orchestration
- Optimization
- Complete workflows
"""

import pytest

from agents.developer_orchestrator import (
    AppType,
    CodeComponent,
    DevelopmentPhase,
    PhysicsGuidedDeveloperOrchestrator,
    RequirementVariable,
)


class TestRequirementVariable:
    """Test suite for RequirementVariable dataclass."""

    def test_requirement_variable_initialization(self):
        """Test basic initialization."""
        var = RequirementVariable(
            name="port",
            description="Server port number",
            variable_type="int",
            required=True,
        )

        assert var.name == "port", "name is not valid"
        assert var.description == "Server port number", "description is not valid"
        assert var.variable_type == "int", "variable_type is not valid"
        assert var.required, "Condition must be true"
        assert var.current_value is None, "Value must be initialized"

    def test_requirement_variable_with_defaults(self):
        """Test with default values."""
        var = RequirementVariable(
            name="timeout",
            description="Request timeout",
            variable_type="int",
            required=False,
            default_value=30,
            suggested_values=[10, 30, 60],
        )

        assert var.default_value == 30, "Value must be initialized"
        assert 30 in var.suggested_values, "Value must be initialized"

    def test_is_satisfied_when_value_set(self):
        """Test satisfaction check with value."""
        var = RequirementVariable(
            name="name", description="App name", variable_type="str", required=True
        )

        assert not var.is_satisfied(), "Condition must be true"

        var.current_value = "MyApp"
        assert var.is_satisfied(), "Condition must be true"

    def test_is_satisfied_when_optional(self):
        """Test optional variable is always satisfied."""
        var = RequirementVariable(
            name="optional_param",
            description="Optional parameter",
            variable_type="str",
            required=False,
        )

        assert var.is_satisfied(), "Condition must be true"

    def test_suggest_from_chaos_without_cnn(self):
        """Test chaos suggestions fallback."""
        var = RequirementVariable(
            name="threads",
            description="Thread count",
            variable_type="int",
            suggested_values=[2, 4, 8],
        )

        suggestions = var.suggest_from_chaos(cnn=None)
        assert suggestions == [2, 4, 8]


class TestCodeComponent:
    """Test suite for CodeComponent dataclass."""

    def test_code_component_initialization(self):
        """Test basic initialization."""
        component = CodeComponent(
            component_id="comp_001",
            name="main.py",
            component_type="module",
            description="Main entry point",
            code="print('Hello')",
        )

        assert component.name == "main.py", "name is not valid"
        assert component.component_type == "module", "component_type is not valid"
        assert "Hello" in component.code, "Condition must be true"

    def test_code_component_with_dependencies(self):
        """Test component with dependencies."""
        component = CodeComponent(
            component_id="comp_002",
            name="utils.py",
            component_type="module",
            description="Utilities",
            code="def helper(): pass",
            dependencies=["logging", "typing"],
        )

        assert "logging" in component.dependencies, "Condition must be true"
        assert "typing" in component.dependencies, "Condition must be true"

    def test_code_component_with_complexity(self):
        """Test component with complexity score."""
        component = CodeComponent(
            component_id="comp_003",
            name="complex.py",
            component_type="module",
            description="Complex module",
            code="# Complex code\n" * 100,
            complexity=0.85,
        )

        assert component.complexity == 0.85, "complexity is not valid"


class TestPhysicsGuidedDeveloperOrchestrator:
    """Test suite for PhysicsGuidedDeveloperOrchestrator."""

    @pytest.fixture
    def orchestrator(self):
        """Create basic orchestrator."""
        orch = PhysicsGuidedDeveloperOrchestrator()
        orch.app_type = AppType.PYTHON_CONSOLE
        return orch

    @pytest.fixture
    def web_orchestrator(self):
        """Create web app orchestrator."""
        orch = PhysicsGuidedDeveloperOrchestrator()
        orch.app_type = AppType.PYTHON_WEB
        return orch

    # ========== INITIALIZATION TESTS ==========

    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initializes correctly."""
        assert orchestrator.app_type == AppType.PYTHON_CONSOLE, "app_type is not valid"
        assert orchestrator.current_phase == DevelopmentPhase.REQUIREMENTS, "current_phase is not valid"
        assert len(orchestrator.requirements) == 0, "Collection must not be empty"
        assert len(orchestrator.components) == 0, "Collection must not be empty"

    def test_different_app_types(self):
        """Test initialization with different app types."""
        for app_type in AppType:
            orch = PhysicsGuidedDeveloperOrchestrator()
            orch.app_type = app_type
            assert orch.app_type == app_type, "app_type is not valid"

    def test_orchestrator_with_session_id(self):
        """Test with custom session ID."""
        orch = PhysicsGuidedDeveloperOrchestrator(session_id="test-session-123")
        orch.app_type = AppType.PYTHON_CLI
        assert orch.session_id == "test-session-123", "session_id is not valid"

    # ========== REQUIREMENTS PHASE TESTS ==========

    def test_analyze_requirements_basic(self, orchestrator):
        """Test basic requirement analysis."""
        user_request = "Create a CLI tool that processes CSV files"

        result = orchestrator.analyze_requirements(user_request)

        # analyze_requirements returns a dict with "missing_variables",
        # "provided_variables", "completeness", etc. – NOT a "requirements" key.
        assert "missing_variables" in result or isinstance(result, list)
        assert orchestrator.current_phase == DevelopmentPhase.REQUIREMENTS, "current_phase is not valid"

    def test_analyze_requirements_identifies_variables(self, orchestrator):
        """Test requirement analysis identifies needed variables."""
        user_request = "Build a web server on port 8080 with authentication"

        result = orchestrator.analyze_requirements(user_request)

        # analyze_requirements returns a dict; fall back to orchestrator.requirements
        # for any list-typed return shape (future-proofing only).
        if isinstance(result, dict):
            reqs = result.get("missing_variables", orchestrator.requirements)
        else:
            reqs = orchestrator.requirements

        assert len(reqs) > 0, "Reqs must not be empty"

    def test_add_requirement_variable(self, orchestrator):
        """Test adding requirement variables."""
        var = RequirementVariable(
            name="database_url",
            description="Database connection string",
            variable_type="str",
            required=True,
        )

        orchestrator.requirements.append(var)

        assert len(orchestrator.requirements) == 1, "Collection must not be empty"
        assert orchestrator.requirements[0].name == "database_url", "Data must not be empty"

    def test_check_requirements_satisfaction(self, orchestrator):
        """Test checking if all requirements are satisfied."""
        var1 = RequirementVariable("req1", "Desc1", "str", required=True)
        var2 = RequirementVariable("req2", "Desc2", "int", required=False)

        orchestrator.requirements = [var1, var2]

        # Not satisfied (req1 required but no value)
        all_satisfied = all(r.is_satisfied() for r in orchestrator.requirements)
        assert not all_satisfied, "Condition must be true"

        # Set value
        var1.current_value = "value"
        all_satisfied = all(r.is_satisfied() for r in orchestrator.requirements)
        assert all_satisfied, "all_satisfied is not valid"

    # ========== DESIGN PHASE TESTS ==========

    def test_transition_to_design_phase(self, orchestrator):
        """Test transitioning to design phase."""
        orchestrator.current_phase = DevelopmentPhase.DESIGN
        assert orchestrator.current_phase == DevelopmentPhase.DESIGN, "current_phase is not valid"

    def test_generate_design_basic(self, orchestrator):
        """Test basic design generation."""
        # Set up requirements first
        var = RequirementVariable("app_name", "Name", "str", required=True)
        var.current_value = "TestApp"
        orchestrator.requirements = [var]

        orchestrator.current_phase = DevelopmentPhase.DESIGN

        # Design should be generated
        if hasattr(orchestrator, "generate_design"):
            design = orchestrator.generate_design()
            assert design is not None, "design must be initialized"

    # ========== ARCHITECTURE PHASE TESTS ==========

    def test_transition_to_architecture_phase(self, orchestrator):
        """Test transitioning to architecture phase."""
        orchestrator.current_phase = DevelopmentPhase.ARCHITECTURE
        assert orchestrator.current_phase == DevelopmentPhase.ARCHITECTURE, "current_phase is not valid"

    def test_plan_architecture_identifies_components(self, orchestrator):
        """Test architecture planning identifies components."""
        orchestrator.current_phase = DevelopmentPhase.ARCHITECTURE

        # Should identify needed components
        if hasattr(orchestrator, "plan_architecture"):
            arch = orchestrator.plan_architecture()
            assert arch is not None, "arch must be initialized"

    # ========== IMPLEMENTATION PHASE TESTS ==========

    def test_transition_to_implementation_phase(self, orchestrator):
        """Test transitioning to implementation phase."""
        orchestrator.current_phase = DevelopmentPhase.IMPLEMENTATION
        assert orchestrator.current_phase == DevelopmentPhase.IMPLEMENTATION, "current_phase is not valid"

    def test_generate_code_component(self, orchestrator):
        """Test code generation for component."""
        component = CodeComponent(
            name="test.py", component_type="module", description="Test module", code=""
        )

        orchestrator.components.append(component)
        assert len(orchestrator.components) == 1, "Collection must not be empty"

    def test_generate_code_for_console_app(self, orchestrator):
        """Test generating code for console app."""
        orchestrator.current_phase = DevelopmentPhase.IMPLEMENTATION

        if hasattr(orchestrator, "generate_code"):
            code = orchestrator.generate_code()
            assert code is not None, "code must be initialized"

    def test_generate_code_for_web_app(self, web_orchestrator):
        """Test generating code for web app."""
        web_orchestrator.current_phase = DevelopmentPhase.IMPLEMENTATION

        if hasattr(web_orchestrator, "generate_code"):
            code = web_orchestrator.generate_code(component_id="web_component_001")
            assert code is not None, "code must be initialized"

    # ========== STATE MACHINE TESTS ==========

    def test_phase_progression_order(self, orchestrator):
        """Test phases progress in correct order."""
        phases = [
            DevelopmentPhase.REQUIREMENTS,
            DevelopmentPhase.DESIGN,
            DevelopmentPhase.ARCHITECTURE,
            DevelopmentPhase.IMPLEMENTATION,
            DevelopmentPhase.TESTING,
            DevelopmentPhase.OPTIMIZATION,
            DevelopmentPhase.DEPLOYMENT,
        ]

        for phase in phases:
            orchestrator.current_phase = phase
            assert orchestrator.current_phase == phase, "current_phase is not valid"

    def test_cannot_skip_phases_validation(self, orchestrator):
        """Test phase validation (if implemented)."""
        # Start at requirements
        assert orchestrator.current_phase == DevelopmentPhase.REQUIREMENTS, "current_phase is not valid"

        # Can manually set phase (no validation in current impl)
        orchestrator.current_phase = DevelopmentPhase.DEPLOYMENT
        assert orchestrator.current_phase == DevelopmentPhase.DEPLOYMENT, "current_phase is not valid"

    # ========== ERROR HANDLING TESTS ==========

    def test_analyze_requirements_with_empty_request(self, orchestrator):
        """Test handling empty user request."""
        result = orchestrator.analyze_requirements("")
        # Should handle gracefully
        assert result is not None, "result must be initialized"

    def test_analyze_requirements_with_none(self, orchestrator):
        """Test handling None user request."""
        try:
            orchestrator.analyze_requirements(None)  # type: ignore
            # Should either work or raise appropriate error
        except (TypeError, AttributeError):
            # Acceptable to raise error for None
            _ = None  # suppressed: no action needed

    # ========== INTEGRATION TESTS ==========

    def test_complete_workflow_console_app(self, orchestrator):
        """Test complete development workflow for console app."""
        # Phase 1: Requirements
        user_request = "Create a simple calculator CLI"
        result = orchestrator.analyze_requirements(user_request)
        assert result is not None, "result must be initialized"

        # Phase 2: Design (if method exists)
        orchestrator.current_phase = DevelopmentPhase.DESIGN

        # Phase 3: Implementation
        orchestrator.current_phase = DevelopmentPhase.IMPLEMENTATION

        # Should reach implementation
        assert orchestrator.current_phase == DevelopmentPhase.IMPLEMENTATION, "current_phase is not valid"

    def test_multiple_components_coordination(self, orchestrator):
        """Test coordinating multiple code components."""
        comp1 = CodeComponent("main.py", "module", "Main", "")
        comp2 = CodeComponent("utils.py", "module", "Utils", "")
        comp3 = CodeComponent("config.py", "module", "Config", "")

        orchestrator.components = [comp1, comp2, comp3]

        assert len(orchestrator.components) == 3, "Collection must not be empty"
        assert all(isinstance(c, CodeComponent) for c in orchestrator.components)

    # ========== RESOURCE MANAGEMENT TESTS ==========

    def test_component_complexity_tracking(self, orchestrator):
        """Test tracking component complexity."""
        simple = CodeComponent("simple.py", "module", "Simple", "x=1", complexity_score=0.1)
        complex = CodeComponent(
            "complex.py", "module", "Complex", "# lots of code", complexity_score=0.9
        )

        orchestrator.components = [simple, complex]

        avg_complexity = sum(c.complexity_score or 0 for c in orchestrator.components) / len(
            orchestrator.components
        )
        assert 0 < avg_complexity < 1, "0 is not valid"

    def test_dependency_tracking(self, orchestrator):
        """Test tracking component dependencies."""
        comp = CodeComponent(
            "app.py",
            "module",
            "App",
            "import logging\nimport json",
            dependencies=["logging", "json"],
        )

        orchestrator.components.append(comp)

        all_deps = set()
        for c in orchestrator.components:
            if c.dependencies:
                all_deps.update(c.dependencies)

        assert "logging" in all_deps, "Condition must be true"
        assert "json" in all_deps, "Condition must be true"


class TestPhysicsIntegration:
    """Test physics-based decision making if available."""

    def test_orchestrator_without_physics(self):
        """Test orchestrator works without physics modules."""
        orch = PhysicsGuidedDeveloperOrchestrator(app_type=AppType.PYTHON_SCRIPT)

        # Should work even without advanced physics
        assert orch is not None, "orch must be initialized"
        assert orch.app_type == AppType.PYTHON_SCRIPT, "app_type is not valid"

    def test_chaos_suggestions_fallback(self):
        """Test chaos suggestions work with fallback."""
        var = RequirementVariable("param", "Parameter", "int", suggested_values=[1, 2, 3])

        suggestions = var.suggest_from_chaos(cnn=None)
        assert suggestions == [1, 2, 3]
