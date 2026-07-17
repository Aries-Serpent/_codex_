"""
Shared fixtures for self-healing infrastructure tests.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import pytest


class ServiceState(Enum):
    """Service state enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    RECOVERING = "recovering"
    FAILED = "failed"


class RecoveryAction(Enum):
    """Recovery action types."""
    RESTART = "restart"
    FAILOVER = "failover"
    CACHE_REBUILD = "cache_rebuild"
    STATE_SYNC = "state_sync"
    CONNECTION_RESET = "connection_reset"
    RETRY = "retry"
    ROLLBACK = "rollback"
    GRACEFUL_DEGRADE = "graceful_degrade"


@dataclass
class HealthCheckResult:
    """Health check result."""
    check_name: str
    status: ServiceState
    timestamp: datetime
    metrics: Dict[str, Any]
    error_message: Optional[str] = None
    recovery_attempted: bool = False


@dataclass
class RecoveryProcedure:
    """Recovery procedure."""
    id: str
    action: RecoveryAction
    target_service: str
    state_before: ServiceState
    state_after: ServiceState
    start_time: datetime
    end_time: Optional[datetime] = None
    success: bool = False
    error_message: Optional[str] = None
    audit_log: List[str] = None
    rollback_available: bool = False

    def __post_init__(self):
        if self.audit_log is None:
            self.audit_log = []


class MockService:
    """Mock service for testing."""

    def __init__(self, name: str, initial_state: ServiceState = ServiceState.HEALTHY):
        self.name = name
        self.state = initial_state
        self.health_checks: List[HealthCheckResult] = []
        self.recovery_history: List[RecoveryProcedure] = []
        self.failure_count = 0
        self.restart_count = 0
        self.metrics = {
            "uptime": 100.0,
            "latency_ms": 50.0,
            "error_rate": 0.0,
            "requests_per_sec": 1000.0
        }

    def get_health(self) -> HealthCheckResult:
        """Get current health status."""
        result = HealthCheckResult(
            check_name=f"{self.name}_health",
            status=self.state,
            timestamp=datetime.now(),
            metrics=self.metrics.copy()
        )
        self.health_checks.append(result)
        return result

    def inject_failure(self, failure_type: str = "generic"):
        """Simulate service failure."""
        self.failure_count += 1
        self.state = ServiceState.UNHEALTHY
        self.metrics["error_rate"] = min(1.0, 0.1 * self.failure_count)
        self.metrics["uptime"] = max(0.0, 100.0 - 10 * self.failure_count)

    def restart(self) -> bool:
        """Restart service."""
        self.restart_count += 1
        self.state = ServiceState.RECOVERING
        self.failure_count = 0
        self.metrics["error_rate"] = 0.0
        self.metrics["uptime"] = 100.0
        self.state = ServiceState.HEALTHY
        return True

    def reset_connection_pool(self) -> bool:
        """Reset connection pool."""
        self.metrics["error_rate"] = 0.0
        self.state = ServiceState.HEALTHY
        return True

    def sync_state(self) -> bool:
        """Sync state with primary."""
        self.state = ServiceState.HEALTHY
        return True


class MockDatabase:
    """Mock database for testing."""

    def __init__(self, name: str = "primary"):
        self.name = name
        self.state = ServiceState.HEALTHY
        self.connected = True
        self.failover_count = 0
        self.data = {}
        self.replication_lag_ms = 0.0

    def check_connection(self) -> bool:
        """Check database connection."""
        return self.connected

    def failover_to_replica(self) -> bool:
        """Failover to replica."""
        if not self.connected:
            self.connected = True
            self.failover_count += 1
            self.state = ServiceState.HEALTHY
            return True
        return False

    def sync_replicas(self) -> bool:
        """Sync all replicas."""
        self.replication_lag_ms = 0.0
        return True

    def read_data(self, key: str) -> Optional[Any]:
        """Read data from database."""
        return self.data.get(key)

    def write_data(self, key: str, value: Any) -> bool:
        """Write data to database."""
        if self.connected:
            self.data[key] = value
            return True
        return False


class MockCache:
    """Mock cache for testing."""

    def __init__(self, name: str = "redis"):
        self.name = name
        self.state = ServiceState.HEALTHY
        self.cache = {}
        self.hit_count = 0
        self.miss_count = 0
        self.invalidation_count = 0

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self.cache:
            self.hit_count += 1
            return self.cache[key]
        self.miss_count += 1
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        self.cache[key] = value
        return True

    def invalidate(self, pattern: str = "*") -> int:
        """Invalidate cache entries."""
        self.invalidation_count += 1
        if pattern == "*":
            count = len(self.cache)
            self.cache.clear()
            return count
        return 0

    def rebuild(self) -> bool:
        """Rebuild cache."""
        self.cache.clear()
        self.invalidation_count = 0
        self.hit_count = 0
        self.miss_count = 0
        return True


class CircuitBreaker:
    """Circuit breaker for resilience."""

    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.state = "closed"
        self.failure_count = 0
        self.last_failure_time = None
        self.open_time = None

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half_open"
            else:
                raise Exception("Circuit breaker is open")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt reset."""
        if self.open_time is None:
            return False
        elapsed = (datetime.now() - self.open_time).total_seconds()
        return elapsed >= self.timeout_seconds

    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        self.state = "closed"

    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            self.open_time = datetime.now()


class ExponentialBackoffRetry:
    """Exponential backoff retry logic."""

    def __init__(self, max_retries: int = 3, initial_delay_ms: int = 100, max_delay_ms: int = 10000):
        self.max_retries = max_retries
        self.initial_delay_ms = initial_delay_ms
        self.max_delay_ms = max_delay_ms
        self.retry_count = 0
        self.total_delay_ms = 0

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with exponential backoff retry."""
        self.retry_count = 0
        self.total_delay_ms = 0
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                self.retry_count = attempt + 1  # Count total retry attempts
                if attempt < self.max_retries:
                    delay_ms = min(
                        self.initial_delay_ms * (2 ** attempt),
                        self.max_delay_ms
                    )
                    self.total_delay_ms += delay_ms

        if last_exception:
            raise last_exception
        raise Exception("Unknown error during retry")


class StateManager:
    """Service state manager."""

    def __init__(self):
        self.state_snapshots: List[Dict[str, Any]] = []
        self.recovery_checkpoints: List[Dict[str, Any]] = []
        self.current_state = {}

    def save_state(self, service_name: str, state_data: Dict[str, Any]) -> bool:
        """Save service state snapshot."""
        snapshot = {
            "service": service_name,
            "timestamp": datetime.now().isoformat(),
            "state": state_data.copy()
        }
        self.state_snapshots.append(snapshot)
        self.current_state[service_name] = state_data.copy()
        return True

    def restore_state(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Restore service state from latest snapshot."""
        if service_name in self.current_state:
            return self.current_state[service_name].copy()
        
        # Find latest snapshot for this service
        for snapshot in reversed(self.state_snapshots):
            if snapshot["service"] == service_name:
                return snapshot["state"].copy()
        return None

    def create_checkpoint(self, checkpoint_name: str, state_data: Dict[str, Any]) -> bool:
        """Create recovery checkpoint."""
        checkpoint = {
            "name": checkpoint_name,
            "timestamp": datetime.now().isoformat(),
            "state": state_data.copy()
        }
        self.recovery_checkpoints.append(checkpoint)
        return True

    def verify_consistency(self, service_name: str, expected_state: Dict[str, Any]) -> bool:
        """Verify state consistency."""
        current = self.current_state.get(service_name, {})
        for key, expected_value in expected_state.items():
            if current.get(key) != expected_value:
                return False
        return True


# ============================================================================
# Pytest Fixtures
# ============================================================================

@pytest.fixture
def mock_service():
    """Fixture for mock service."""
    return MockService("test_service")


@pytest.fixture
def mock_database():
    """Fixture for mock database."""
    return MockDatabase("primary")


@pytest.fixture
def mock_cache():
    """Fixture for mock cache."""
    return MockCache("redis")


@pytest.fixture
def circuit_breaker():
    """Fixture for circuit breaker."""
    return CircuitBreaker(failure_threshold=3, timeout_seconds=5)


@pytest.fixture
def retry_policy():
    """Fixture for exponential backoff retry."""
    return ExponentialBackoffRetry(max_retries=3, initial_delay_ms=100)


@pytest.fixture
def state_manager():
    """Fixture for state manager."""
    return StateManager()


@pytest.fixture
def recovery_context(mock_service, mock_database, mock_cache, state_manager):
    """Fixture for recovery context with all components."""
    return {
        "service": mock_service,
        "database": mock_database,
        "cache": mock_cache,
        "state_manager": state_manager,
        "timestamp": datetime.now()
    }


@pytest.fixture(autouse=True)
def reset_asyncio_loop():
    """Reset asyncio loop between tests."""
    yield
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.stop()
    except RuntimeError:
        pass
