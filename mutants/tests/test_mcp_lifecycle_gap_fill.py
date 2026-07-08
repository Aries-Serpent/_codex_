"""Gap-fill tests for MCP lifecycle management.

Tests for src/services/mcp/lifecycle.py to improve module coverage.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from src.services.mcp.lifecycle import LifecycleManager


class TestLifecycleManagerInitialization:
    """Test LifecycleManager initialization."""

    def test_initialization(self):
        """Test basic initialization."""
        manager = LifecycleManager()
        assert manager is not None, "manager must be initialized"
        assert manager.is_healthy() is False, "Condition must be true"
        assert manager.is_ready() is False, "Condition must be true"

    def test_initialization_empty_hooks(self):
        """Test that hooks are initialized as empty lists."""
        manager = LifecycleManager()
        assert hasattr(manager, "_startup_hooks")
        assert hasattr(manager, "_shutdown_hooks")
        assert hasattr(manager, "_health_checks")
        assert hasattr(manager, "_resources")


class TestStartupHookRegistration:
    """Test startup hook registration."""

    def test_register_startup_hook_sync(self):
        """Test registering a synchronous startup hook."""
        manager = LifecycleManager()
        hook = Mock()
        manager.register_startup_hook(hook)
        assert len(manager._startup_hooks) == 1, "Collection must not be empty"

    def test_register_startup_hook_async(self):
        """Test registering an asynchronous startup hook."""
        manager = LifecycleManager()

        async def async_hook():
            pass

        manager.register_startup_hook(async_hook)
        assert len(manager._startup_hooks) == 1, "Collection must not be empty"

    def test_register_startup_hook_multiple(self):
        """Test registering multiple startup hooks."""
        manager = LifecycleManager()
        hook1 = Mock()
        hook2 = Mock()
        manager.register_startup_hook(hook1)
        manager.register_startup_hook(hook2)
        assert len(manager._startup_hooks) == 2, "Collection must not be empty"

    def test_register_startup_hook_raises_on_non_callable(self):
        """Test that registering non-callable raises ValueError."""
        manager = LifecycleManager()
        with pytest.raises(ValueError):
            manager.register_startup_hook("not_callable")

    def test_register_startup_hook_raises_on_none(self):
        """Test that registering None raises ValueError."""
        manager = LifecycleManager()
        with pytest.raises(ValueError):
            manager.register_startup_hook(None)


class TestShutdownHookRegistration:
    """Test shutdown hook registration."""

    def test_register_shutdown_hook_sync(self):
        """Test registering a synchronous shutdown hook."""
        manager = LifecycleManager()
        hook = Mock()
        manager.register_shutdown_hook(hook)
        assert len(manager._shutdown_hooks) == 1, "Collection must not be empty"

    def test_register_shutdown_hook_async(self):
        """Test registering an asynchronous shutdown hook."""
        manager = LifecycleManager()

        async def async_hook():
            pass

        manager.register_shutdown_hook(async_hook)
        assert len(manager._shutdown_hooks) == 1, "Collection must not be empty"

    def test_register_shutdown_hook_multiple(self):
        """Test registering multiple shutdown hooks."""
        manager = LifecycleManager()
        hook1 = Mock()
        hook2 = Mock()
        manager.register_shutdown_hook(hook1)
        manager.register_shutdown_hook(hook2)
        assert len(manager._shutdown_hooks) == 2, "Collection must not be empty"

    def test_register_shutdown_hook_raises_on_non_callable(self):
        """Test that registering non-callable raises ValueError."""
        manager = LifecycleManager()
        with pytest.raises(ValueError):
            manager.register_shutdown_hook(123)


class TestResourceRegistration:
    """Test resource registration."""

    def test_register_resource(self):
        """Test registering a resource."""
        manager = LifecycleManager()
        resource = Mock()
        manager.register_resource("test_resource", resource)
        assert "test_resource" in manager._resources, "Condition must be true"

    def test_register_multiple_resources(self):
        """Test registering multiple resources."""
        manager = LifecycleManager()
        resource1 = Mock()
        resource2 = Mock()
        manager.register_resource("resource1", resource1)
        manager.register_resource("resource2", resource2)
        assert len(manager._resources) == 2, "Collection must not be empty"

    def test_register_resource_raises_on_empty_name(self):
        """Test that empty resource name raises ValueError."""
        manager = LifecycleManager()
        with pytest.raises(ValueError):
            manager.register_resource("", Mock())

    def test_register_resource_raises_on_none_name(self):
        """Test that None resource name raises ValueError."""
        manager = LifecycleManager()
        with pytest.raises(ValueError):
            manager.register_resource(None, Mock())

    def test_register_resource_raises_on_non_string_name(self):
        """Test that non-string resource name raises ValueError."""
        manager = LifecycleManager()
        with pytest.raises(ValueError):
            manager.register_resource(123, Mock())


class TestHealthCheckRegistration:
    """Test health check registration."""

    def test_register_health_check_sync(self):
        """Test registering a synchronous health check."""
        manager = LifecycleManager()
        check = Mock(return_value=True)
        manager.register_health_check(check)
        assert len(manager._health_checks) == 1, "Collection must not be empty"

    def test_register_health_check_async(self):
        """Test registering an asynchronous health check."""
        manager = LifecycleManager()

        async def async_check():
            return True

        manager.register_health_check(async_check)
        assert len(manager._health_checks) == 1, "Collection must not be empty"

    def test_register_health_check_multiple(self):
        """Test registering multiple health checks."""
        manager = LifecycleManager()
        check1 = Mock(return_value=True)
        check2 = Mock(return_value=True)
        manager.register_health_check(check1)
        manager.register_health_check(check2)
        assert len(manager._health_checks) == 2, "Collection must not be empty"

    def test_register_health_check_raises_on_non_callable(self):
        """Test that registering non-callable health check raises ValueError."""
        manager = LifecycleManager()
        with pytest.raises(ValueError):
            manager.register_health_check("not_callable")


class TestStartupExecution:
    """Test startup execution."""

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
    async def test_startup_with_sync_hooks(self):
        """Test startup with synchronous hooks."""
        manager = LifecycleManager()
        hook1 = Mock()
        hook2 = Mock()
        manager.register_startup_hook(hook1)
        manager.register_startup_hook(hook2)

        await manager.startup()

        hook1.assert_called_once()
        hook2.assert_called_once()
        assert manager.is_ready() is True, "Condition must be true"
        assert manager.is_healthy() is True, "Condition must be true"

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
    async def test_startup_with_async_hooks(self):
        """Test startup with asynchronous hooks."""
        manager = LifecycleManager()

        async def async_hook():
            pass

        manager.register_startup_hook(async_hook)
        await manager.startup()

        assert manager.is_ready() is True, "Condition must be true"
        assert manager.is_healthy() is True, "Condition must be true"

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
    async def test_startup_with_mixed_hooks(self):
        """Test startup with mixed sync and async hooks."""
        manager = LifecycleManager()
        sync_hook = Mock()

        async def async_hook():
            pass

        manager.register_startup_hook(sync_hook)
        manager.register_startup_hook(async_hook)

        await manager.startup()

        sync_hook.assert_called_once()
        assert manager.is_ready() is True, "Condition must be true"

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
    async def test_startup_failure_triggers_rollback(self):
        """Test that startup failure triggers rollback."""
        manager = LifecycleManager()
        hook1 = Mock()
        hook2 = Mock(side_effect=RuntimeError("Hook failed"))

        manager.register_startup_hook(hook1)
        manager.register_startup_hook(hook2)

        with pytest.raises(RuntimeError):
            await manager.startup()

        assert manager.is_ready() is False, "Condition must be true"

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
    async def test_startup_no_hooks(self):
        """Test startup with no hooks."""
        manager = LifecycleManager()
        await manager.startup()

        assert manager.is_ready() is True, "Condition must be true"
        assert manager.is_healthy() is True, "Condition must be true"


class TestShutdownExecution:
    """Test shutdown execution."""

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
    async def test_shutdown_with_sync_hooks(self):
        """Test shutdown with synchronous hooks."""
        manager = LifecycleManager()
        hook1 = Mock()
        hook2 = Mock()
        manager.register_shutdown_hook(hook1)
        manager.register_shutdown_hook(hook2)
        manager._is_ready = True
        manager._is_healthy = True

        await manager.shutdown()

        hook1.assert_called_once()
        hook2.assert_called_once()
        assert manager.is_ready() is False, "Condition must be true"
        assert manager.is_healthy() is False, "Condition must be true"

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
    async def test_shutdown_with_async_hooks(self):
        """Test shutdown with asynchronous hooks."""
        manager = LifecycleManager()

        async def async_hook():
            pass

        manager.register_shutdown_hook(async_hook)
        manager._is_ready = True
        manager._is_healthy = True

        await manager.shutdown()

        assert manager.is_ready() is False, "Condition must be true"

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
    async def test_shutdown_hook_exception_doesnt_stop_others(self):
        """Test that exception in one hook doesn't stop others."""
        manager = LifecycleManager()
        hook1 = Mock()
        hook2 = Mock(side_effect=RuntimeError("Hook failed"))
        hook3 = Mock()
        manager.register_shutdown_hook(hook1)
        manager.register_shutdown_hook(hook2)
        manager.register_shutdown_hook(hook3)
        manager._is_ready = True
        manager._is_healthy = True

        await manager.shutdown()

        # All hooks should be attempted
        hook1.assert_called_once()
        hook3.assert_called_once()

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
    async def test_shutdown_no_hooks(self):
        """Test shutdown with no hooks."""
        manager = LifecycleManager()
        manager._is_ready = True
        manager._is_healthy = True

        await manager.shutdown()

        assert manager.is_ready() is False, "Condition must be true"
        assert manager.is_healthy() is False, "Condition must be true"


class TestResourceCleanup:
    """Test resource cleanup."""

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
    async def test_cleanup_with_sync_cleanup_method(self):
        """Test cleanup with synchronous cleanup method."""
        manager = LifecycleManager()
        resource = Mock()
        resource.cleanup = Mock()
        manager.register_resource("test", resource)
        manager._is_ready = True
        manager._is_healthy = True

        await manager.shutdown()

        resource.cleanup.assert_called_once()

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
    async def test_cleanup_with_async_cleanup_method(self):
        """Test cleanup with asynchronous cleanup method."""
        manager = LifecycleManager()
        resource = Mock()
        resource.cleanup = AsyncMock()
        manager.register_resource("test", resource)
        manager._is_ready = True
        manager._is_healthy = True

        await manager.shutdown()

        resource.cleanup.assert_called_once()

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
    async def test_cleanup_with_close_method(self):
        """Test cleanup with close method when cleanup not available."""
        manager = LifecycleManager()
        resource = Mock(spec=["close"])
        resource.close = Mock()
        manager.register_resource("test", resource)
        manager._is_ready = True
        manager._is_healthy = True

        await manager.shutdown()

        resource.close.assert_called_once()

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
    async def test_cleanup_exception_doesnt_stop_others(self):
        """Test that exception in one resource cleanup doesn't stop others."""
        manager = LifecycleManager()
        resource1 = Mock()
        resource1.cleanup = Mock()
        resource2 = Mock()
        resource2.cleanup = Mock(side_effect=RuntimeError("Cleanup failed"))
        resource3 = Mock()
        resource3.cleanup = Mock()

        manager.register_resource("resource1", resource1)
        manager.register_resource("resource2", resource2)
        manager.register_resource("resource3", resource3)
        manager._is_ready = True
        manager._is_healthy = True

        await manager.shutdown()

        resource1.cleanup.assert_called_once()
        resource3.cleanup.assert_called_once()


class TestHealthCheck:
    """Test health check functionality."""

    def test_health_check_sync_all_pass(self):
        """Test health check when all sync checks pass."""
        manager = LifecycleManager()
        check1 = Mock(return_value=True)
        check2 = Mock(return_value=True)
        manager.register_health_check(check1)
        manager.register_health_check(check2)
        manager._is_healthy = True
        manager._is_ready = True

        result = manager.healthz()

        assert result["status"] == "healthy", "Result must not be empty"
        assert result["ready"] is True, "Result must not be empty"
        check1.assert_called_once()
        check2.assert_called_once()

    def test_health_check_sync_one_fails(self):
        """Test health check when one sync check fails."""
        manager = LifecycleManager()
        check1 = Mock(return_value=True)
        check2 = Mock(return_value=False)
        manager.register_health_check(check1)
        manager.register_health_check(check2)
        manager._is_healthy = True
        manager._is_ready = True

        result = manager.healthz()

        assert result["status"] == "unhealthy", "Result must not be empty"

    def test_health_check_sync_exception_handling(self):
        """Test health check handles exceptions gracefully."""
        manager = LifecycleManager()
        check1 = Mock(side_effect=RuntimeError("Check failed"))
        check2 = Mock(return_value=True)
        manager.register_health_check(check1)
        manager.register_health_check(check2)
        manager._is_healthy = True
        manager._is_ready = True

        result = manager.healthz()

        assert result["status"] == "unhealthy", "Result must not be empty"

    def test_health_check_not_healthy_status(self):
        """Test health check when not healthy."""
        manager = LifecycleManager()
        check = Mock(return_value=True)
        manager.register_health_check(check)
        manager._is_healthy = False
        manager._is_ready = False

        result = manager.healthz()

        assert result["status"] == "unhealthy", "Result must not be empty"
        assert result["ready"] is False, "Result must not be empty"

    def test_health_check_resources_count(self):
        """Test health check includes resource count."""
        manager = LifecycleManager()
        manager.register_resource("res1", Mock())
        manager.register_resource("res2", Mock())
        manager._is_healthy = True
        manager._is_ready = True

        result = manager.healthz()

        assert result["resources"] == 2, "Result must not be empty"


class TestStatusMethods:
    """Test status check methods."""

    def test_is_healthy_initial_state(self):
        """Test initial health state is False."""
        manager = LifecycleManager()
        assert manager.is_healthy() is False, "Condition must be true"

    def test_is_ready_initial_state(self):
        """Test initial ready state is False."""
        manager = LifecycleManager()
        assert manager.is_ready() is False, "Condition must be true"

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
    async def test_status_after_startup(self):
        """Test status after successful startup."""
        manager = LifecycleManager()
        await manager.startup()

        assert manager.is_healthy() is True, "Condition must be true"
        assert manager.is_ready() is True, "Condition must be true"

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
    async def test_status_after_shutdown(self):
        """Test status after shutdown."""
        manager = LifecycleManager()
        await manager.startup()
        await manager.shutdown()

        assert manager.is_healthy() is False, "Condition must be true"
        assert manager.is_ready() is False, "Condition must be true"
