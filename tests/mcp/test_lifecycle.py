"""Comprehensive tests for src/mcp/lifecycle.py module."""

import pytest


class TestServerState:
    """Tests for ServerState enum."""

    def test_server_state_import(self):
        """Test that ServerState can be imported."""
        try:
            from src.mcp.lifecycle import ServerState

            assert ServerState is not None, "ServerState must be initialized"
        except ImportError:
            pytest.skip("Module not available")

    def test_server_state_values(self):
        """Test all ServerState enum values."""
        try:
            from src.mcp.lifecycle import ServerState

            assert ServerState.UNINITIALIZED.value == "uninitialized", "Value must be initialized"
            assert ServerState.INITIALIZING.value == "initializing", "Value must be initialized"
            assert ServerState.READY.value == "ready", "Value must be initialized"
            assert ServerState.RUNNING.value == "running", "Value must be initialized"
            assert ServerState.DRAINING.value == "draining", "Value must be initialized"
            assert ServerState.STOPPING.value == "stopping", "Value must be initialized"
            assert ServerState.STOPPED.value == "stopped", "Value must be initialized"
            assert ServerState.ERROR.value == "error", "Value must be initialized"
        except ImportError:
            pytest.skip("Module not available")

    def test_valid_transitions_defined(self):
        """Test that VALID_TRANSITIONS dict is defined."""
        try:
            from src.mcp.lifecycle import VALID_TRANSITIONS, ServerState

            assert isinstance(VALID_TRANSITIONS, dict)
            assert ServerState.UNINITIALIZED in VALID_TRANSITIONS, "Condition must be true"
        except ImportError:
            pytest.skip("Module not available")


class TestInvalidStateTransition:
    """Tests for InvalidStateTransition exception."""

    def test_exception_creation(self):
        """Test creating InvalidStateTransition exception."""
        try:
            from src.mcp.lifecycle import InvalidStateTransition, ServerState

            exc = InvalidStateTransition(ServerState.STOPPED, ServerState.RUNNING)
            assert exc.current == ServerState.STOPPED, "current is not valid"
            assert exc.target == ServerState.RUNNING, "target is not valid"
        except ImportError:
            pytest.skip("Module not available")

    def test_exception_message(self):
        """Test exception message format."""
        try:
            from src.mcp.lifecycle import InvalidStateTransition, ServerState

            exc = InvalidStateTransition(ServerState.STOPPED, ServerState.RUNNING)
            assert "stopped" in str(exc), "Condition must be true"
            assert "running" in str(exc), "Condition must be true"
        except ImportError:
            pytest.skip("Module not available")


class TestHealthStatus:
    """Tests for HealthStatus dataclass."""

    def test_health_status_creation(self):
        """Test creating HealthStatus."""
        try:
            from src.mcp.lifecycle import HealthStatus

            status = HealthStatus(healthy=True, message="OK")
            assert status.healthy is True, "healthy is not valid"
            assert status.message == "OK", "message is not valid"
        except ImportError:
            pytest.skip("Module not available")

    def test_health_status_defaults(self):
        """Test HealthStatus default values."""
        try:
            from src.mcp.lifecycle import HealthStatus

            status = HealthStatus(healthy=False)
            assert status.message == "", "message is not valid"
            assert isinstance(status.details, dict)
            assert isinstance(status.timestamp, float)
        except ImportError:
            pytest.skip("Module not available")

    def test_health_status_with_details(self):
        """Test HealthStatus with details."""
        try:
            from src.mcp.lifecycle import HealthStatus

            details = {"cpu": 50, "memory": 75}
            status = HealthStatus(healthy=True, details=details)
            assert status.details == details, "details is not valid"
        except ImportError:
            pytest.skip("Module not available")


class TestLifecycleConfig:
    """Tests for LifecycleConfig dataclass."""

    def test_config_creation(self):
        """Test creating LifecycleConfig."""
        try:
            from src.mcp.lifecycle import LifecycleConfig

            config = LifecycleConfig()
            assert config is not None, "config must be initialized"
        except ImportError:
            pytest.skip("Module not available")

    def test_config_defaults(self):
        """Test LifecycleConfig default values."""
        try:
            from src.mcp.lifecycle import LifecycleConfig

            config = LifecycleConfig()
            assert config.shutdown_timeout_seconds == 30.0, "shutdown_timeout_seconds is not valid"
            assert config.health_check_interval_seconds == 10.0, "health_check_interval_seconds is not valid"
            assert config.drain_timeout_seconds == 60.0, "drain_timeout_seconds is not valid"
            assert config.max_concurrent_requests == 100, "max_concurrent_requests is not valid"
        except ImportError:
            pytest.skip("Module not available")

    def test_config_custom_values(self):
        """Test LifecycleConfig with custom values."""
        try:
            from src.mcp.lifecycle import LifecycleConfig

            config = LifecycleConfig(shutdown_timeout_seconds=60.0, max_concurrent_requests=200)
            assert config.shutdown_timeout_seconds == 60.0, "shutdown_timeout_seconds is not valid"
            assert config.max_concurrent_requests == 200, "max_concurrent_requests is not valid"
        except ImportError:
            pytest.skip("Module not available")


class TestLifecycleManager:
    """Tests for LifecycleManager class."""

    def test_manager_creation(self):
        """Test creating LifecycleManager."""
        try:
            from src.mcp.lifecycle import LifecycleManager

            manager = LifecycleManager()
            assert manager is not None, "manager must be initialized"
        except ImportError:
            pytest.skip("Module not available")

    def test_manager_with_config(self):
        """Test creating LifecycleManager with config."""
        try:
            from src.mcp.lifecycle import LifecycleConfig, LifecycleManager

            config = LifecycleConfig(shutdown_timeout_seconds=45.0)
            manager = LifecycleManager(config=config)
            assert manager is not None, "manager must be initialized"
        except ImportError:
            pytest.skip("Module not available")

    def test_manager_initial_state(self):
        """Test LifecycleManager initial state."""
        try:
            from src.mcp.lifecycle import LifecycleManager, ServerState

            manager = LifecycleManager()
            # Access internal state (for testing)
            assert manager._state == ServerState.UNINITIALIZED, "_state is not valid"
        except ImportError:
            pytest.skip("Module not available")

    def test_manager_has_health_checks(self):
        """Test LifecycleManager has health checks list."""
        try:
            from src.mcp.lifecycle import LifecycleManager

            manager = LifecycleManager()
            assert isinstance(manager._health_checks, list)
        except ImportError:
            pytest.skip("Module not available")

    def test_manager_has_startup_hooks(self):
        """Test LifecycleManager has startup hooks list."""
        try:
            from src.mcp.lifecycle import LifecycleManager

            manager = LifecycleManager()
            assert isinstance(manager._startup_hooks, list)
        except ImportError:
            pytest.skip("Module not available")


class TestStateTransitions:
    """Tests for valid state transitions."""

    def test_uninitialized_can_initialize(self):
        """Test UNINITIALIZED can transition to INITIALIZING."""
        try:
            from src.mcp.lifecycle import VALID_TRANSITIONS, ServerState

            assert ServerState.INITIALIZING in VALID_TRANSITIONS[ServerState.UNINITIALIZED], "Condition must be true"
        except ImportError:
            pytest.skip("Module not available")

    def test_initializing_can_become_ready(self):
        """Test INITIALIZING can transition to READY."""
        try:
            from src.mcp.lifecycle import VALID_TRANSITIONS, ServerState

            assert ServerState.READY in VALID_TRANSITIONS[ServerState.INITIALIZING], "Condition must be true"
        except ImportError:
            pytest.skip("Module not available")

    def test_ready_can_run(self):
        """Test READY can transition to RUNNING."""
        try:
            from src.mcp.lifecycle import VALID_TRANSITIONS, ServerState

            assert ServerState.RUNNING in VALID_TRANSITIONS[ServerState.READY], "Condition must be true"
        except ImportError:
            pytest.skip("Module not available")

    def test_running_can_drain(self):
        """Test RUNNING can transition to DRAINING."""
        try:
            from src.mcp.lifecycle import VALID_TRANSITIONS, ServerState

            assert ServerState.DRAINING in VALID_TRANSITIONS[ServerState.RUNNING], "Condition must be true"
        except ImportError:
            pytest.skip("Module not available")

    def test_draining_can_stop(self):
        """Test DRAINING can transition to STOPPING."""
        try:
            from src.mcp.lifecycle import VALID_TRANSITIONS, ServerState

            assert ServerState.STOPPING in VALID_TRANSITIONS[ServerState.DRAINING], "Condition must be true"
        except ImportError:
            pytest.skip("Module not available")

    def test_stopping_becomes_stopped(self):
        """Test STOPPING can transition to STOPPED."""
        try:
            from src.mcp.lifecycle import VALID_TRANSITIONS, ServerState

            assert ServerState.STOPPED in VALID_TRANSITIONS[ServerState.STOPPING], "Condition must be true"
        except ImportError:
            pytest.skip("Module not available")

    def test_stopped_can_reinitialize(self):
        """Test STOPPED can transition to INITIALIZING."""
        try:
            from src.mcp.lifecycle import VALID_TRANSITIONS, ServerState

            assert ServerState.INITIALIZING in VALID_TRANSITIONS[ServerState.STOPPED], "Condition must be true"
        except ImportError:
            pytest.skip("Module not available")

    def test_error_recovery(self):
        """Test ERROR can transition to STOPPING or INITIALIZING."""
        try:
            from src.mcp.lifecycle import VALID_TRANSITIONS, ServerState

            assert ServerState.STOPPING in VALID_TRANSITIONS[ServerState.ERROR], "Error should be raised or set"
            assert ServerState.INITIALIZING in VALID_TRANSITIONS[ServerState.ERROR], "Error should be raised or set"
        except ImportError:
            pytest.skip("Module not available")
