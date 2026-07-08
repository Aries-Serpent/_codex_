"""
Test Agents Exceptions Module

Comprehensive unit tests for the shared exception hierarchy.
"""

from __future__ import annotations

import pytest

from agents.exceptions import (
    PACKAGE_NAME,
    AgentConfigError,
    AgentError,
    AgentExecutionError,
    AgentImportError,
    AgentValidationError,
    BoundCheckError,
    CausalityViolationError,
    ContinuityError,
    ConvergenceError,
    EntanglementError,
    GaugeError,
    InvariantViolationError,
    PhysicsError,
    ValidationError,
)


class TestPackageConstant:
    """Tests for PACKAGE_NAME constant."""

    def test_package_name_value(self) -> None:
        assert PACKAGE_NAME == "codex-ml", "PACKAGE_NAME is not valid"

    def test_package_name_is_string(self) -> None:
        assert isinstance(PACKAGE_NAME, str)


class TestAgentError:
    """Tests for base AgentError exception."""

    def test_basic_raise(self) -> None:
        with pytest.raises(AgentError):
            raise AgentError("Test error")

    def test_message(self) -> None:
        error = AgentError("Custom message")
        assert str(error) == "Custom message", "Error should be raised or set"

    def test_inheritance(self) -> None:
        assert issubclass(AgentError, Exception)


class TestAgentImportError:
    """Tests for AgentImportError exception."""

    def test_basic_error(self) -> None:
        error = AgentImportError("numpy")
        assert "numpy" in str(error), "Error should be raised or set"
        assert error.module_name == "numpy", "Error should be raised or set"
        assert error.package_name == "numpy", "Error should be raised or set"

    def test_with_package_name(self) -> None:
        error = AgentImportError("np", package_name="numpy")
        assert error.module_name == "np", "Error should be raised or set"
        assert error.package_name == "numpy", "Error should be raised or set"
        assert "numpy" in str(error), "Error should be raised or set"

    def test_with_extra(self) -> None:
        error = AgentImportError("torch", extra="ml")
        assert "ml" in str(error), "Error should be raised or set"
        assert f"pip install {PACKAGE_NAME}[ml]" in str(error), "Error should be raised or set"
        assert error.extra == "ml", "Error should be raised or set"

    def test_without_extra(self) -> None:
        error = AgentImportError("scipy")
        assert "pip install scipy" in str(error), "Error should be raised or set"

    def test_inheritance(self) -> None:
        assert issubclass(AgentImportError, AgentError)
        assert issubclass(AgentImportError, ImportError)


class TestAgentConfigError:
    """Tests for AgentConfigError exception."""

    def test_basic_raise(self) -> None:
        with pytest.raises(AgentConfigError):
            raise AgentConfigError("Invalid config")

    def test_inheritance(self) -> None:
        assert issubclass(AgentConfigError, AgentError)
        assert issubclass(AgentConfigError, ValueError)


class TestAgentValidationError:
    """Tests for AgentValidationError exception."""

    def test_basic_raise(self) -> None:
        with pytest.raises(AgentValidationError):
            raise AgentValidationError("Validation failed")

    def test_inheritance(self) -> None:
        assert issubclass(AgentValidationError, AgentError)
        assert issubclass(AgentValidationError, ValueError)


class TestAgentExecutionError:
    """Tests for AgentExecutionError exception."""

    def test_basic_raise(self) -> None:
        with pytest.raises(AgentExecutionError):
            raise AgentExecutionError("Execution failed")

    def test_inheritance(self) -> None:
        assert issubclass(AgentExecutionError, AgentError)
        assert issubclass(AgentExecutionError, RuntimeError)


class TestPhysicsExceptions:
    """Tests for physics-specific exceptions."""

    def test_entanglement_error(self) -> None:
        assert issubclass(EntanglementError, AgentError)
        with pytest.raises(EntanglementError):
            raise EntanglementError("Entanglement failed")

    def test_gauge_error(self) -> None:
        assert issubclass(GaugeError, AgentError)
        with pytest.raises(GaugeError):
            raise GaugeError("Gauge symmetry violated")

    def test_continuity_error(self) -> None:
        assert issubclass(ContinuityError, AgentValidationError)
        with pytest.raises(ContinuityError):
            raise ContinuityError("Continuity equation violated")

    def test_bound_check_error(self) -> None:
        assert issubclass(BoundCheckError, AgentValidationError)
        with pytest.raises(BoundCheckError):
            raise BoundCheckError("|j| > c")

    def test_physics_error(self) -> None:
        assert issubclass(PhysicsError, AgentError)
        with pytest.raises(PhysicsError):
            raise PhysicsError("Physics error")

    def test_validation_error_alias(self) -> None:
        assert issubclass(ValidationError, AgentValidationError)
        with pytest.raises(ValidationError):
            raise ValidationError("Validation failed")

    def test_convergence_error(self) -> None:
        assert issubclass(ConvergenceError, PhysicsError)
        with pytest.raises(ConvergenceError):
            raise ConvergenceError("Failed to converge")

    def test_invariant_violation_error(self) -> None:
        assert issubclass(InvariantViolationError, PhysicsError)
        with pytest.raises(InvariantViolationError):
            raise InvariantViolationError("Invariant violated")

    def test_causality_violation_error(self) -> None:
        assert issubclass(CausalityViolationError, PhysicsError)
        with pytest.raises(CausalityViolationError):
            raise CausalityViolationError("v > c")


class TestExceptionHierarchy:
    """Tests for the complete exception hierarchy."""

    def test_all_inherit_from_agent_error(self) -> None:
        exceptions = [
            AgentImportError("test"),
            AgentConfigError("test"),
            AgentValidationError("test"),
            AgentExecutionError("test"),
            EntanglementError("test"),
            GaugeError("test"),
            ContinuityError("test"),
            BoundCheckError("test"),
            PhysicsError("test"),
            ValidationError("test"),
            ConvergenceError("test"),
            InvariantViolationError("test"),
            CausalityViolationError("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, AgentError)

    def test_can_catch_with_base_class(self) -> None:
        """Verify all exceptions can be caught with AgentError."""

        def raise_import_error():
            raise AgentImportError("test")

        def raise_config_error():
            raise AgentConfigError("test")

        def raise_physics_error():
            raise PhysicsError("test")

        for func in [raise_import_error, raise_config_error, raise_physics_error]:
            try:
                func()
            except AgentError:
                _ = None  # Expected
            else:
                pytest.fail(f"{func.__name__} should raise AgentError")
