"""
Tests for agents.developer_orchestrator module.

This module contains tests for the PhysicsGuidedDeveloperOrchestrator class
and related classes for physics-inspired software development guidance.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestRequirementVariable:
    """Tests for RequirementVariable dataclass."""

    def test_is_satisfied_with_value(self):
        """Test is_satisfied returns True when current_value is set."""
        from agents.developer_orchestrator import RequirementVariable
        
        var = RequirementVariable(
            name="test_var",
            description="Test variable",
            variable_type="str",
            required=True,
            current_value="some_value"
        )
        assert var.is_satisfied() is True

    def test_is_satisfied_without_value_required(self):
        """Test is_satisfied returns False when required and no value."""
        from agents.developer_orchestrator import RequirementVariable
        
        var = RequirementVariable(
            name="test_var",
            description="Test variable",
            variable_type="str",
            required=True,
            current_value=None
        )
        assert var.is_satisfied() is False

    def test_is_satisfied_without_value_optional(self):
        """Test is_satisfied returns True when optional and no value."""
        from agents.developer_orchestrator import RequirementVariable
        
        var = RequirementVariable(
            name="test_var",
            description="Test variable",
            variable_type="str",
            required=False,
            current_value=None
        )
        assert var.is_satisfied() is True

    def test_suggest_from_chaos_no_physics(self):
        """Test suggest_from_chaos returns suggested_values when no physics."""
        from agents.developer_orchestrator import RequirementVariable
        
        var = RequirementVariable(
            name="test_var",
            description="Test variable",
            variable_type="str",
            suggested_values=["a", "b", "c"]
        )
        result = var.suggest_from_chaos(None)
        assert result == ["a", "b", "c"]

    def test_default_values(self):
        """Test RequirementVariable default values."""
        from agents.developer_orchestrator import RequirementVariable
        
        var = RequirementVariable(
            name="test",
            description="Test",
            variable_type="str"
        )
        assert var.required is True
        assert var.default_value is None
        assert var.suggested_values == []
        assert var.current_value is None


class TestCodeComponent:
    """Tests for CodeComponent dataclass."""

    def test_to_dict(self):
        """Test CodeComponent serialization to dict."""
        from agents.developer_orchestrator import CodeComponent
        
        component = CodeComponent(
            component_id="comp_1",
            name="TestComponent",
            component_type="module",
            description="A test component",
            dependencies=["dep1", "dep2"],
            priority=0.8,
            complexity=1.5,
            implementation_status="in_progress",
            code="print('hello')"
        )
        
        result = component.to_dict()
        
        assert result["component_id"] == "comp_1"
        assert result["name"] == "TestComponent"
        assert result["type"] == "module"
        assert result["description"] == "A test component"
        assert result["dependencies"] == ["dep1", "dep2"]
        assert result["priority"] == 0.8
        assert result["complexity"] == 1.5
        assert result["status"] == "in_progress"
        # Note: 'code' is not included in to_dict

    def test_default_values(self):
        """Test CodeComponent default values."""
        from agents.developer_orchestrator import CodeComponent
        
        component = CodeComponent(
            component_id="comp_1",
            name="Test",
            component_type="function",
            description="Test"
        )
        
        assert component.dependencies == []
        assert component.priority == 0.5
        assert component.complexity == 1.0
        assert component.implementation_status == "pending"
        assert component.code == ""


class TestAppType:
    """Tests for AppType enum."""

    def test_app_type_values(self):
        """Test AppType enum values."""
        from agents.developer_orchestrator import AppType
        
        assert AppType.PYTHON_CONSOLE.value == "python_console"
        assert AppType.PYTHON_CLI.value == "python_cli"
        assert AppType.PYTHON_API.value == "python_api"
        assert AppType.PYTHON_WEB.value == "python_web"
        assert AppType.PYTHON_LIBRARY.value == "python_library"
        assert AppType.PYTHON_SCRIPT.value == "python_script"

    def test_app_type_from_string(self):
        """Test creating AppType from string."""
        from agents.developer_orchestrator import AppType
        
        assert AppType("python_cli") == AppType.PYTHON_CLI


class TestDevelopmentPhase:
    """Tests for DevelopmentPhase enum."""

    def test_phase_values(self):
        """Test DevelopmentPhase enum values."""
        from agents.developer_orchestrator import DevelopmentPhase
        
        assert DevelopmentPhase.REQUIREMENTS.value == "requirements"
        assert DevelopmentPhase.DESIGN.value == "design"
        assert DevelopmentPhase.ARCHITECTURE.value == "architecture"
        assert DevelopmentPhase.IMPLEMENTATION.value == "implementation"
        assert DevelopmentPhase.TESTING.value == "testing"
        assert DevelopmentPhase.OPTIMIZATION.value == "optimization"
        assert DevelopmentPhase.DEPLOYMENT.value == "deployment"
        assert DevelopmentPhase.MAINTENANCE.value == "maintenance"


class TestPhysicsGuidedDeveloperOrchestrator:
    """Tests for PhysicsGuidedDeveloperOrchestrator class."""

    @patch('agents.developer_orchestrator.ADVANCED_PHYSICS', False)
    def test_init_defaults(self):
        """Test orchestrator initialization with defaults."""
        from agents.developer_orchestrator import (
            PhysicsGuidedDeveloperOrchestrator,
            DevelopmentPhase
        )
        
        orchestrator = PhysicsGuidedDeveloperOrchestrator()
        
        assert orchestrator.app_type is None
        assert orchestrator.required_variables == {}
        assert orchestrator.components == {}
        assert orchestrator.current_phase == DevelopmentPhase.REQUIREMENTS
        assert orchestrator.session_id == "dev_orchestrator"
        assert orchestrator.development_history == []
        assert orchestrator.suggestions_cache == {}

    @patch('agents.developer_orchestrator.ADVANCED_PHYSICS', False)
    def test_init_with_session_id(self):
        """Test orchestrator initialization with custom session_id."""
        from agents.developer_orchestrator import PhysicsGuidedDeveloperOrchestrator
        
        orchestrator = PhysicsGuidedDeveloperOrchestrator(session_id="custom_session")
        
        assert orchestrator.session_id == "custom_session"

    @patch('agents.developer_orchestrator.ADVANCED_PHYSICS', False)
    @patch('agents.developer_orchestrator.log_message')
    def test_log_method(self, mock_log):
        """Test _log method calls log_message."""
        from agents.developer_orchestrator import PhysicsGuidedDeveloperOrchestrator
        
        orchestrator = PhysicsGuidedDeveloperOrchestrator(session_id="test_session")
        orchestrator._log("system", "Test message")
        
        mock_log.assert_called_once_with("test_session", "system", "Test message")

    @patch('agents.developer_orchestrator.ADVANCED_PHYSICS', False)
    @patch('agents.developer_orchestrator.log_message')
    def test_analyze_user_requirements_basic(self, mock_log):
        """Test analyzing basic user requirements."""
        from agents.developer_orchestrator import (
            PhysicsGuidedDeveloperOrchestrator,
            AppType
        )
        
        orchestrator = PhysicsGuidedDeveloperOrchestrator()
        requirements = {
            "app_type": "python_console",
            "app_name": "test_app",
            "description": "A test application"
        }
        
        result = orchestrator.analyze_user_requirements(requirements)
        
        assert result["app_type"] == "python_console"
        assert "app_name" in result["provided_variables"]
        assert "description" in result["provided_variables"]
        assert orchestrator.app_type == AppType.PYTHON_CONSOLE

    @patch('agents.developer_orchestrator.ADVANCED_PHYSICS', False)
    @patch('agents.developer_orchestrator.log_message')
    def test_analyze_user_requirements_default_app_type(self, mock_log):
        """Test default app type when not provided."""
        from agents.developer_orchestrator import (
            PhysicsGuidedDeveloperOrchestrator,
            AppType
        )
        
        orchestrator = PhysicsGuidedDeveloperOrchestrator()
        requirements = {}
        
        result = orchestrator.analyze_user_requirements(requirements)
        
        assert result["app_type"] == "python_console"
        assert orchestrator.app_type == AppType.PYTHON_CONSOLE

    @patch('agents.developer_orchestrator.ADVANCED_PHYSICS', False)
    @patch('agents.developer_orchestrator.log_message')
    def test_analyze_user_requirements_invalid_app_type(self, mock_log):
        """Test handling of invalid app type falls back to console."""
        from agents.developer_orchestrator import (
            PhysicsGuidedDeveloperOrchestrator,
            AppType
        )
        
        orchestrator = PhysicsGuidedDeveloperOrchestrator()
        requirements = {"app_type": "invalid_type"}
        
        result = orchestrator.analyze_user_requirements(requirements)
        
        assert orchestrator.app_type == AppType.PYTHON_CONSOLE

    @patch('agents.developer_orchestrator.ADVANCED_PHYSICS', False)
    @patch('agents.developer_orchestrator.log_message')
    def test_analyze_user_requirements_completeness(self, mock_log):
        """Test completeness calculation in analysis."""
        from agents.developer_orchestrator import PhysicsGuidedDeveloperOrchestrator
        
        orchestrator = PhysicsGuidedDeveloperOrchestrator()
        
        # Provide all required variables
        requirements = {
            "app_type": "python_console",
            "app_name": "test_app",
            "description": "A test application",
            "python_version": "3.10"
        }
        
        result = orchestrator.analyze_user_requirements(requirements)
        
        # Completeness should be 1.0 when all variables are provided
        assert result["completeness"] >= 0.0
        assert result["completeness"] <= 1.0

    @patch('agents.developer_orchestrator.ADVANCED_PHYSICS', False)
    def test_define_required_variables_console(self):
        """Test required variables for console app."""
        from agents.developer_orchestrator import (
            PhysicsGuidedDeveloperOrchestrator,
            AppType
        )
        
        orchestrator = PhysicsGuidedDeveloperOrchestrator()
        orchestrator.app_type = AppType.PYTHON_CONSOLE
        orchestrator._define_required_variables()
        
        assert "app_name" in orchestrator.required_variables
        assert "description" in orchestrator.required_variables
        assert "python_version" in orchestrator.required_variables

    @patch('agents.developer_orchestrator.ADVANCED_PHYSICS', False)
    def test_define_required_variables_cli(self):
        """Test required variables for CLI app."""
        from agents.developer_orchestrator import (
            PhysicsGuidedDeveloperOrchestrator,
            AppType
        )
        
        orchestrator = PhysicsGuidedDeveloperOrchestrator()
        orchestrator.app_type = AppType.PYTHON_CLI
        orchestrator._define_required_variables()
        
        assert "cli_framework" in orchestrator.required_variables
        assert "commands" in orchestrator.required_variables
        
        # Check CLI-specific defaults
        cli_framework = orchestrator.required_variables["cli_framework"]
        assert cli_framework.default_value == "argparse"
        assert "click" in cli_framework.suggested_values
        assert "typer" in cli_framework.suggested_values

    @patch('agents.developer_orchestrator.ADVANCED_PHYSICS', False)
    def test_define_required_variables_api(self):
        """Test required variables for API app."""
        from agents.developer_orchestrator import (
            PhysicsGuidedDeveloperOrchestrator,
            AppType
        )
        
        orchestrator = PhysicsGuidedDeveloperOrchestrator()
        orchestrator.app_type = AppType.PYTHON_API
        orchestrator._define_required_variables()
        
        assert "api_framework" in orchestrator.required_variables
        assert "endpoints" in orchestrator.required_variables
        assert "authentication" in orchestrator.required_variables
        
        # Check API-specific defaults
        api_framework = orchestrator.required_variables["api_framework"]
        assert api_framework.default_value == "fastapi"

    @patch('agents.developer_orchestrator.ADVANCED_PHYSICS', False)
    def test_define_required_variables_web(self):
        """Test required variables for web app."""
        from agents.developer_orchestrator import (
            PhysicsGuidedDeveloperOrchestrator,
            AppType
        )
        
        orchestrator = PhysicsGuidedDeveloperOrchestrator()
        orchestrator.app_type = AppType.PYTHON_WEB
        orchestrator._define_required_variables()
        
        assert "web_framework" in orchestrator.required_variables
        assert "routes" in orchestrator.required_variables

    @patch('agents.developer_orchestrator.ADVANCED_PHYSICS', False)
    def test_define_required_variables_library(self):
        """Test required variables for library."""
        from agents.developer_orchestrator import (
            PhysicsGuidedDeveloperOrchestrator,
            AppType
        )
        
        orchestrator = PhysicsGuidedDeveloperOrchestrator()
        orchestrator.app_type = AppType.PYTHON_LIBRARY
        orchestrator._define_required_variables()
        
        assert "modules" in orchestrator.required_variables
        assert "public_api" in orchestrator.required_variables


class TestModuleImports:
    """Tests for module-level imports and availability flags."""

    def test_numpy_availability_flag_exists(self):
        """Test NUMPY_AVAILABLE flag exists."""
        from agents import developer_orchestrator
        
        assert hasattr(developer_orchestrator, 'NUMPY_AVAILABLE')
        assert isinstance(developer_orchestrator.NUMPY_AVAILABLE, bool)

    def test_advanced_physics_flag_exists(self):
        """Test ADVANCED_PHYSICS flag exists."""
        from agents import developer_orchestrator
        
        assert hasattr(developer_orchestrator, 'ADVANCED_PHYSICS')
        assert isinstance(developer_orchestrator.ADVANCED_PHYSICS, bool)

    def test_logging_available_flag_exists(self):
        """Test LOGGING_AVAILABLE flag exists."""
        from agents import developer_orchestrator
        
        assert hasattr(developer_orchestrator, 'LOGGING_AVAILABLE')
        assert isinstance(developer_orchestrator.LOGGING_AVAILABLE, bool)
