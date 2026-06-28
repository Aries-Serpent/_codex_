"""Gap-fill tests for mcp/lifecycle.py module - comprehensive coverage for lifecycle management.

This test suite covers:
- Server state enumeration and transitions
- Lifecycle manager initialization
- Valid and invalid state transitions
- Health checks and status reporting
- Startup and shutdown hooks
- Request tracking and graceful shutdown
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from mcp.lifecycle import (
    VALID_TRANSITIONS,
    HealthStatus,
    InvalidStateTransition,
    LifecycleConfig,
    LifecycleManager,
    ServerState,
    get_lifecycle_manager,
    reset_lifecycle_manager,
)


class TestServerState:
    """Test ServerState enumeration."""

    def test_server_state_values(self):
        """Test that all ServerState values are defined."""
        assert ServerState.UNINITIALIZED.value == "uninitialized", "Value must be initialized"
        assert ServerState.INITIALIZING.value == "initializing", "Value must be initialized"
        assert ServerState.READY.value == "ready", "Value must be initialized"
        assert ServerState.RUNNING.value == "running", "Value must be initialized"
        assert ServerState.DRAINING.value == "draining", "Value must be initialized"
        assert ServerState.STOPPING.value == "stopping", "Value must be initialized"
        assert ServerState.STOPPED.value == "stopped", "Value must be initialized"
        assert ServerState.ERROR.value == "error", "Value must be initialized"

    def test_server_state_enum_members(self):
        """Test that all expected state members exist."""
        states = {
            ServerState.UNINITIALIZED,
            ServerState.INITIALIZING,
            ServerState.READY,
            ServerState.RUNNING,
            ServerState.DRAINING,
            ServerState.STOPPING,
            ServerState.STOPPED,
            ServerState.ERROR,
        }
        assert len(states) == 8, "States must not be empty"


class TestValidTransitions:
    """Test valid state transitions mapping."""

    def test_valid_transitions_structure(self):
        """Test that VALID_TRANSITIONS is properly structured."""
        assert isinstance(VALID_TRANSITIONS, dict)
        for state in ServerState:
            assert state in VALID_TRANSITIONS, "Condition must be true"
            assert isinstance(VALID_TRANSITIONS[state], list)

    def test_uninitialized_transitions(self):
        """Test transitions from UNINITIALIZED state."""
        assert ServerState.INITIALIZING in VALID_TRANSITIONS[ServerState.UNINITIALIZED], "Condition must be true"

    def test_initializing_transitions(self):
        """Test transitions from INITIALIZING state."""
        transitions = VALID_TRANSITIONS[ServerState.INITIALIZING]
        assert ServerState.READY in transitions, "Condition must be true"
        assert ServerState.ERROR in transitions, "Error should be raised or set"

    def test_ready_transitions(self):
        """Test transitions from READY state."""
        transitions = VALID_TRANSITIONS[ServerState.READY]
        assert ServerState.RUNNING in transitions, "Condition must be true"
        assert ServerState.STOPPING in transitions, "Condition must be true"

    def test_running_transitions(self):
        """Test transitions from RUNNING state."""
        transitions = VALID_TRANSITIONS[ServerState.RUNNING]
        assert ServerState.DRAINING in transitions, "Condition must be true"
        assert ServerState.STOPPING in transitions, "Condition must be true"
        assert ServerState.ERROR in transitions, "Error should be raised or set"

    def test_draining_transitions(self):
        """Test transitions from DRAINING state."""
        assert ServerState.STOPPING in VALID_TRANSITIONS[ServerState.DRAINING], "Condition must be true"

    def test_stopping_transitions(self):
        """Test transitions from STOPPING state."""
        assert ServerState.STOPPED in VALID_TRANSITIONS[ServerState.STOPPING], "Condition must be true"

    def test_stopped_transitions(self):
        """Test transitions from STOPPED state."""
        assert ServerState.INITIALIZING in VALID_TRANSITIONS[ServerState.STOPPED], "Condition must be true"

    def test_error_transitions(self):
        """Test transitions from ERROR state."""
        transitions = VALID_TRANSITIONS[ServerState.ERROR]
        assert ServerState.STOPPING in transitions, "Condition must be true"
        assert ServerState.INITIALIZING in transitions, "Condition must be true"


class TestInvalidStateTransition:
    """Test InvalidStateTransition exception."""

    def test_invalid_state_transition_exception(self):
        """Test exception creation and attributes."""
        exc = InvalidStateTransition(ServerState.RUNNING, ServerState.READY)
        assert exc.current == ServerState.RUNNING, "current is not valid"
        assert exc.target == ServerState.READY, "target is not valid"
        assert "running" in str(exc), "Condition must be true"
        assert "ready" in str(exc), "Condition must be true"

    def test_invalid_state_transition_message(self):
        """Test exception message."""
        exc = InvalidStateTransition(ServerState.UNINITIALIZED, ServerState.RUNNING)
        assert "Invalid state transition" in str(exc), "Condition must be true"


class TestHealthStatus:
    """Test HealthStatus dataclass."""

    def test_health_status_creation_healthy(self):
        """Test creating healthy status."""
        status = HealthStatus(healthy=True, message="All good")
        assert status.healthy is True, "healthy is not valid"
        assert status.message == "All good", "message is not valid"
        assert status.details == {}, "details is not valid"
        assert status.timestamp > 0, "timestamp must be greater than zero"

    def test_health_status_creation_unhealthy(self):
        """Test creating unhealthy status."""
        status = HealthStatus(
            healthy=False,
            message="Service unavailable",
            details={"error": "Connection failed"},
        )
        assert status.healthy is False, "healthy is not valid"
        assert status.message == "Service unavailable", "message is not valid"
        assert status.details == {"error": "Connection failed"}, "Error should be raised or set"

    def test_health_status_default_values(self):
        """Test default values for HealthStatus."""
        status = HealthStatus(healthy=True)
        assert status.healthy is True, "healthy is not valid"
        assert status.message == "", "message is not valid"
        assert status.details == {}, "details is not valid"


class TestLifecycleConfig:
    """Test LifecycleConfig dataclass."""

    def test_lifecycle_config_defaults(self):
        """Test default LifecycleConfig values."""
        config = LifecycleConfig()
        assert config.shutdown_timeout_seconds == 30.0, "shutdown_timeout_seconds is not valid"
        assert config.health_check_interval_seconds == 10.0, "health_check_interval_seconds is not valid"
        assert config.drain_timeout_seconds == 60.0, "drain_timeout_seconds is not valid"
        assert config.max_concurrent_requests == 100, "max_concurrent_requests is not valid"

    def test_lifecycle_config_custom(self):
        """Test custom LifecycleConfig values."""
        config = LifecycleConfig(
            shutdown_timeout_seconds=60.0,
            health_check_interval_seconds=5.0,
            drain_timeout_seconds=120.0,
            max_concurrent_requests=200,
        )
        assert config.shutdown_timeout_seconds == 60.0, "shutdown_timeout_seconds is not valid"
        assert config.health_check_interval_seconds == 5.0, "health_check_interval_seconds is not valid"
        assert config.drain_timeout_seconds == 120.0, "drain_timeout_seconds is not valid"
        assert config.max_concurrent_requests == 200, "max_concurrent_requests is not valid"


class TestLifecycleManager:
    """Test LifecycleManager class."""

    def test_lifecycle_manager_initialization(self):
        """Test LifecycleManager initialization."""
        manager = LifecycleManager()
        assert manager.state == ServerState.UNINITIALIZED, "state is not valid"
        assert manager.is_healthy is False, "is_healthy is not valid"
        assert manager.is_accepting_requests is False, "is_accepting_requests is not valid"

    def test_lifecycle_manager_custom_config(self):
        """Test LifecycleManager with custom config."""
        config = LifecycleConfig(shutdown_timeout_seconds=60.0)
        manager = LifecycleManager(config)
        assert manager._config == config, "_config is not valid"
        assert manager._config.shutdown_timeout_seconds == 60.0, "shutdown_timeout_seconds is not valid"

    def test_state_property(self):
        """Test state property."""
        manager = LifecycleManager()
        assert manager.state == ServerState.UNINITIALIZED, "state is not valid"

    def test_is_healthy_property(self):
        """Test is_healthy property."""
        manager = LifecycleManager()
        assert manager.is_healthy is False, "is_healthy is not valid"

        # Mock state to READY
        manager._state = ServerState.READY
        assert manager.is_healthy is True, "is_healthy is not valid"

        # Mock state to RUNNING
        manager._state = ServerState.RUNNING
        assert manager.is_healthy is True, "is_healthy is not valid"

        # Mock state to ERROR
        manager._state = ServerState.ERROR
        assert manager.is_healthy is False, "is_healthy is not valid"

    def test_is_accepting_requests_property(self):
        """Test is_accepting_requests property."""
        manager = LifecycleManager()
        assert manager.is_accepting_requests is False, "is_accepting_requests is not valid"

        manager._state = ServerState.RUNNING
        assert manager.is_accepting_requests is True, "is_accepting_requests is not valid"

        manager._state = ServerState.READY
        assert manager.is_accepting_requests is False, "is_accepting_requests is not valid"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_transition_to_valid(self):
        """Test valid state transition."""
        manager = LifecycleManager()
        await manager.transition_to(ServerState.INITIALIZING)
        assert manager.state == ServerState.INITIALIZING, "state is not valid"

        await manager.transition_to(ServerState.READY)
        assert manager.state == ServerState.READY, "state is not valid"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_transition_to_invalid_raises_error(self):
        """Test invalid state transition raises error."""
        manager = LifecycleManager()
        with pytest.raises(InvalidStateTransition):
            await manager.transition_to(ServerState.RUNNING)

    def test_register_health_check(self):
        """Test registering health check."""
        manager = LifecycleManager()
        check = MagicMock(return_value=HealthStatus(healthy=True))
        manager.register_health_check(check)
        assert check in manager._health_checks, "Condition must be true"

    def test_register_startup_hook(self):
        """Test registering startup hook."""
        manager = LifecycleManager()
        hook = MagicMock()
        manager.register_startup_hook(hook)
        assert hook in manager._startup_hooks, "Condition must be true"

    def test_register_shutdown_hook(self):
        """Test registering shutdown hook."""
        manager = LifecycleManager()
        hook = MagicMock()
        manager.register_shutdown_hook(hook)
        assert hook in manager._shutdown_hooks, "Condition must be true"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_initialize(self):
        """Test server initialization."""
        manager = LifecycleManager()
        startup_hook = AsyncMock()
        manager.register_startup_hook(startup_hook)

        await manager.initialize()

        assert manager.state == ServerState.READY, "state is not valid"
        startup_hook.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_initialize_with_error(self):
        """Test initialization error handling."""
        manager = LifecycleManager()
        startup_hook = MagicMock(side_effect=Exception("Startup failed"))
        manager.register_startup_hook(startup_hook)

        with pytest.raises(Exception, match="Startup failed"):
            await manager.initialize()

        assert manager.state == ServerState.ERROR, "Error should be raised or set"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_start(self):
        """Test starting the server."""
        manager = LifecycleManager()
        manager._state = ServerState.READY

        await manager.start()

        assert manager.state == ServerState.RUNNING, "state is not valid"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_start_from_invalid_state_raises_error(self):
        """Test starting from invalid state raises error."""
        manager = LifecycleManager()
        manager._state = ServerState.UNINITIALIZED

        with pytest.raises(InvalidStateTransition):
            await manager.start()

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_get_health_when_unhealthy(self):
        """Test get_health when server is unhealthy."""
        manager = LifecycleManager()
        manager._state = ServerState.ERROR

        health = manager.get_health()

        assert health.healthy is False, "healthy is not valid"
        assert "error" in health.message.lower(), "Error should be raised or set"
        assert health.details["state"] == "error", "Error should be raised or set"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_get_health_with_checks(self):
        """Test get_health with registered checks."""
        manager = LifecycleManager()
        manager._state = ServerState.READY

        check1 = MagicMock(return_value=HealthStatus(healthy=True, message="Check 1 passed"))
        check2 = MagicMock(return_value=HealthStatus(healthy=False, message="Check 2 failed"))

        manager.register_health_check(check1)
        manager.register_health_check(check2)

        health = manager.get_health()

        assert health.healthy is False, "healthy is not valid"
        assert "Check 2 failed" in health.message, "Condition must be true"
        check1.assert_called_once()
        check2.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_track_request_start(self):
        """Test tracking request start."""
        manager = LifecycleManager()
        manager._state = ServerState.RUNNING

        can_proceed = await manager.track_request_start()

        assert can_proceed is True, "can_proceed is not valid"
        assert manager._active_requests == 1, "_active_requests is not valid"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_track_request_start_when_not_accepting(self):
        """Test tracking request start when not accepting."""
        manager = LifecycleManager()
        manager._state = ServerState.READY

        can_proceed = await manager.track_request_start()

        assert can_proceed is False, "can_proceed is not valid"
        assert manager._active_requests == 0, "_active_requests is not valid"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_track_request_end(self):
        """Test tracking request end."""
        manager = LifecycleManager()
        manager._active_requests = 1

        await manager.track_request_end()

        assert manager._active_requests == 0, "_active_requests is not valid"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_track_request_end_when_zero(self):
        """Test tracking request end when already zero."""
        manager = LifecycleManager()
        manager._active_requests = 0

        await manager.track_request_end()

        assert manager._active_requests == 0, "_active_requests is not valid"


class TestGlobalLifecycleManager:
    """Test global lifecycle manager functions."""

    def test_get_lifecycle_manager_creates_instance(self):
        """Test that get_lifecycle_manager creates an instance."""
        reset_lifecycle_manager()
        manager = get_lifecycle_manager()
        assert isinstance(manager, LifecycleManager)

    def test_get_lifecycle_manager_returns_same_instance(self):
        """Test that get_lifecycle_manager returns the same instance."""
        reset_lifecycle_manager()
        manager1 = get_lifecycle_manager()
        manager2 = get_lifecycle_manager()
        assert manager1 is manager2, "manager1 is not valid"

    def test_reset_lifecycle_manager(self):
        """Test reset_lifecycle_manager clears the instance."""
        reset_lifecycle_manager()
        manager1 = get_lifecycle_manager()
        reset_lifecycle_manager()
        manager2 = get_lifecycle_manager()
        assert manager1 is not manager2, "manager1 is not valid"
