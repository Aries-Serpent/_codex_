# AI Agent Code Templates

> Version: 1.0.0 | Generated: 2025-12-17
> Purpose: Ready-to-use code templates for AI agents to quickly implement common patterns

## Table of Contents

1. [Module Templates](#module-templates)
2. [Test Templates](#test-templates)
3. [Configuration Templates](#configuration-templates)
4. [CLI Templates](#cli-templates)
5. [Workflow Templates](#workflow-templates)

---

## Module Templates

### TEMPLATE-M001: Basic MCP Capability Module

```python
"""[Module Name] - [Brief description].

This module provides:
- [Feature 1]
- [Feature 2]
- [Feature 3]

Example usage:
    from src.mcp.[module_name] import [ClassName]
    
    instance = [ClassName]()
    result = instance.do_something("input")
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class [ClassName]Config:
    """Configuration for [ClassName].
    
    Attributes:
        setting1: Description of setting1.
        setting2: Description of setting2.
        enabled: Whether the feature is enabled.
    """
    
    setting1: str = "default_value"
    setting2: int = 100
    enabled: bool = True
    options: Dict[str, Any] = field(default_factory=dict)


class [ClassName]:
    """[Brief description of class].
    
    This class handles [describe responsibility].
    
    Attributes:
        config: Configuration instance.
    
    Example:
        >>> obj = [ClassName]()
        >>> obj.do_something("test")
        'Result: test'
    """
    
    def __init__(self, config: Optional[[ClassName]Config] = None) -> None:
        """Initialize [ClassName].
        
        Args:
            config: Optional configuration. Uses defaults if not provided.
        """
        self._config = config or [ClassName]Config()
        self._logger = logging.getLogger(__name__)
        self._initialized = False
        
    def initialize(self) -> None:
        """Initialize the instance.
        
        Call this before using other methods if lazy initialization is needed.
        """
        if self._initialized:
            return
        
        self._logger.info("Initializing [ClassName]")
        # Initialization logic here
        self._initialized = True
    
    def do_something(self, input_value: str) -> str:
        """Perform the main action.
        
        Args:
            input_value: The input to process.
            
        Returns:
            The processed result.
            
        Raises:
            ValueError: If input_value is None or empty.
        """
        if not input_value:
            raise ValueError("input_value cannot be empty")
        
        self._logger.debug("Processing: %s", input_value)
        result = f"Result: {input_value}"
        return result
    
    def process_batch(self, items: List[str]) -> List[str]:
        """Process multiple items.
        
        Args:
            items: List of items to process.
            
        Returns:
            List of processed results.
        """
        return [self.do_something(item) for item in items if item]
    
    @property
    def is_enabled(self) -> bool:
        """Check if the feature is enabled."""
        return self._config.enabled
    
    def __repr__(self) -> str:
        """Return string representation."""
        return f"[ClassName](config={self._config})"


# Module-level convenience functions
_default_instance: Optional[[ClassName]] = None


def get_[class_name]() -> [ClassName]:
    """Get or create the default [ClassName] instance.
    
    Returns:
        The default [ClassName] instance.
    """
    global _default_instance
    if _default_instance is None:
        _default_instance = [ClassName]()
    return _default_instance


def reset_[class_name]() -> None:
    """Reset the default instance (for testing)."""
    global _default_instance
    _default_instance = None
```

### TEMPLATE-M002: Async Service Module

```python
"""[Service Name] - Async service implementation.

This module provides an async service for [description].
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Awaitable

logger = logging.getLogger(__name__)


@dataclass
class [ServiceName]Config:
    """Configuration for [ServiceName]."""
    
    timeout_seconds: float = 30.0
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    max_concurrent: int = 10


class [ServiceName]:
    """Async service for [description].
    
    This service handles [responsibility] with support for:
    - Concurrent operations
    - Automatic retries
    - Timeout handling
    """
    
    def __init__(self, config: Optional[[ServiceName]Config] = None) -> None:
        """Initialize the service.
        
        Args:
            config: Service configuration.
        """
        self._config = config or [ServiceName]Config()
        self._logger = logging.getLogger(__name__)
        self._semaphore = asyncio.Semaphore(self._config.max_concurrent)
        self._running = False
    
    async def start(self) -> None:
        """Start the service."""
        self._running = True
        self._logger.info("[ServiceName] started")
    
    async def stop(self) -> None:
        """Stop the service gracefully."""
        self._running = False
        self._logger.info("[ServiceName] stopped")
    
    async def execute(self, operation: str, params: Dict[str, Any]) -> Any:
        """Execute an operation with retry logic.
        
        Args:
            operation: Operation name.
            params: Operation parameters.
            
        Returns:
            Operation result.
            
        Raises:
            TimeoutError: If operation times out.
            RuntimeError: If max retries exceeded.
        """
        async with self._semaphore:
            for attempt in range(self._config.max_retries):
                try:
                    return await asyncio.wait_for(
                        self._do_execute(operation, params),
                        timeout=self._config.timeout_seconds
                    )
                except asyncio.TimeoutError:
                    self._logger.warning(
                        "Operation %s timed out (attempt %d/%d)",
                        operation, attempt + 1, self._config.max_retries
                    )
                    if attempt == self._config.max_retries - 1:
                        raise
                    await asyncio.sleep(self._config.retry_delay_seconds)
                except Exception as e:
                    self._logger.error(
                        "Operation %s failed: %s (attempt %d/%d)",
                        operation, e, attempt + 1, self._config.max_retries
                    )
                    if attempt == self._config.max_retries - 1:
                        raise RuntimeError(f"Max retries exceeded: {e}")
                    await asyncio.sleep(self._config.retry_delay_seconds)
        
        raise RuntimeError("Unexpected state")
    
    async def _do_execute(
        self, operation: str, params: Dict[str, Any]
    ) -> Any:
        """Internal execution implementation.
        
        Override this in subclasses for custom behavior.
        """
        self._logger.debug("Executing %s with %s", operation, params)
        # Implementation here
        return {"status": "ok", "operation": operation}
    
    async def execute_batch(
        self,
        operations: List[tuple[str, Dict[str, Any]]]
    ) -> List[Any]:
        """Execute multiple operations concurrently.
        
        Args:
            operations: List of (operation, params) tuples.
            
        Returns:
            List of results in same order.
        """
        tasks = [
            self.execute(op, params)
            for op, params in operations
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    @property
    def is_running(self) -> bool:
        """Check if service is running."""
        return self._running
```

### TEMPLATE-M003: State Machine Module

```python
"""[StateMachine Name] - State machine implementation.

Provides state management with validated transitions.
"""

import logging
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class [State]State(Enum):
    """States for [description]."""
    
    INITIAL = auto()
    PENDING = auto()
    ACTIVE = auto()
    PAUSED = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


# Define valid transitions
VALID_TRANSITIONS: Dict[[State]State, Set[[State]State]] = {
    [State]State.INITIAL: {[State]State.PENDING, [State]State.CANCELLED},
    [State]State.PENDING: {[State]State.ACTIVE, [State]State.CANCELLED, [State]State.FAILED},
    [State]State.ACTIVE: {[State]State.PAUSED, [State]State.COMPLETED, [State]State.FAILED},
    [State]State.PAUSED: {[State]State.ACTIVE, [State]State.CANCELLED},
    [State]State.COMPLETED: set(),  # Terminal state
    [State]State.FAILED: {[State]State.INITIAL},  # Can retry
    [State]State.CANCELLED: set(),  # Terminal state
}


class InvalidTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""
    
    def __init__(self, current: [State]State, target: [State]State) -> None:
        self.current = current
        self.target = target
        super().__init__(
            f"Cannot transition from {current.name} to {target.name}"
        )


@dataclass
class StateContext:
    """Context information for state transitions."""
    
    previous_state: Optional[[State]State] = None
    reason: str = ""
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class [State]Machine:
    """State machine for [description].
    
    Manages state transitions with validation and callbacks.
    """
    
    def __init__(self, initial_state: [State]State = [State]State.INITIAL) -> None:
        """Initialize state machine.
        
        Args:
            initial_state: Starting state.
        """
        self._state = initial_state
        self._logger = logging.getLogger(__name__)
        self._on_enter: Dict[[State]State, List[Callable]] = {}
        self._on_exit: Dict[[State]State, List[Callable]] = {}
        self._history: List[StateContext] = []
    
    @property
    def state(self) -> [State]State:
        """Get current state."""
        return self._state
    
    @property
    def is_terminal(self) -> bool:
        """Check if in terminal state."""
        return len(VALID_TRANSITIONS.get(self._state, set())) == 0
    
    def can_transition_to(self, target: [State]State) -> bool:
        """Check if transition is valid.
        
        Args:
            target: Target state.
            
        Returns:
            True if transition is valid.
        """
        return target in VALID_TRANSITIONS.get(self._state, set())
    
    def transition_to(
        self,
        target: [State]State,
        reason: str = "",
        metadata: Optional[Dict] = None
    ) -> None:
        """Transition to a new state.
        
        Args:
            target: Target state.
            reason: Reason for transition.
            metadata: Additional context.
            
        Raises:
            InvalidTransitionError: If transition is not valid.
        """
        if not self.can_transition_to(target):
            raise InvalidTransitionError(self._state, target)
        
        # Create context
        context = StateContext(
            previous_state=self._state,
            reason=reason,
            metadata=metadata or {}
        )
        
        # Run exit callbacks
        for callback in self._on_exit.get(self._state, []):
            callback(context)
        
        # Perform transition
        old_state = self._state
        self._state = target
        self._history.append(context)
        
        self._logger.info(
            "State transition: %s -> %s (reason: %s)",
            old_state.name, target.name, reason
        )
        
        # Run enter callbacks
        for callback in self._on_enter.get(target, []):
            callback(context)
    
    def on_enter(self, state: [State]State, callback: Callable) -> None:
        """Register callback for entering a state.
        
        Args:
            state: State to watch.
            callback: Function to call.
        """
        if state not in self._on_enter:
            self._on_enter[state] = []
        self._on_enter[state].append(callback)
    
    def on_exit(self, state: [State]State, callback: Callable) -> None:
        """Register callback for exiting a state.
        
        Args:
            state: State to watch.
            callback: Function to call.
        """
        if state not in self._on_exit:
            self._on_exit[state] = []
        self._on_exit[state].append(callback)
    
    def get_history(self) -> List[StateContext]:
        """Get state transition history."""
        return list(self._history)
    
    def reset(self) -> None:
        """Reset to initial state."""
        self._state = [State]State.INITIAL
        self._history.clear()
```

---

## Test Templates

### TEMPLATE-T001: Comprehensive Test Suite

```python
"""Tests for [module_name] module.

This test suite covers:
- Initialization and configuration
- Core functionality
- Edge cases and error handling
- Integration scenarios
"""

import pytest
from typing import Any, Dict
from unittest.mock import Mock, patch, AsyncMock

# Import the module under test
from src.mcp.[module_name] import (
    [ClassName],
    [ClassName]Config,
    get_[class_name],
    reset_[class_name],
)


class Test[ClassName]Config:
    """Tests for [ClassName]Config."""
    
    def test_default_values(self):
        """Test that default config values are sensible."""
        config = [ClassName]Config()
        assert config.setting1 == "default_value"
        assert config.setting2 == 100
        assert config.enabled is True
    
    def test_custom_values(self):
        """Test config with custom values."""
        config = [ClassName]Config(
            setting1="custom",
            setting2=200,
            enabled=False
        )
        assert config.setting1 == "custom"
        assert config.setting2 == 200
        assert config.enabled is False


class Test[ClassName]:
    """Tests for [ClassName]."""
    
    @pytest.fixture
    def config(self) -> [ClassName]Config:
        """Create test configuration."""
        return [ClassName]Config(setting1="test")
    
    @pytest.fixture
    def instance(self, config) -> [ClassName]:
        """Create test instance."""
        return [ClassName](config)
    
    @pytest.fixture(autouse=True)
    def reset_global(self):
        """Reset global instance after each test."""
        yield
        reset_[class_name]()
    
    # Initialization tests
    
    def test_init_with_default_config(self):
        """Test initialization with default config."""
        obj = [ClassName]()
        assert obj._config.setting1 == "default_value"
    
    def test_init_with_custom_config(self, config):
        """Test initialization with custom config."""
        obj = [ClassName](config)
        assert obj._config.setting1 == "test"
    
    def test_initialize_sets_flag(self, instance):
        """Test that initialize() sets initialized flag."""
        assert not instance._initialized
        instance.initialize()
        assert instance._initialized
    
    def test_initialize_is_idempotent(self, instance):
        """Test that multiple initialize() calls are safe."""
        instance.initialize()
        instance.initialize()  # Should not raise
        assert instance._initialized
    
    # Core functionality tests
    
    def test_do_something_happy_path(self, instance):
        """Test do_something with valid input."""
        result = instance.do_something("test_input")
        assert result == "Result: test_input"
    
    def test_do_something_with_special_chars(self, instance):
        """Test do_something handles special characters."""
        result = instance.do_something("test@#$%^&*()")
        assert "test@#$%^&*()" in result
    
    def test_do_something_with_unicode(self, instance):
        """Test do_something handles unicode."""
        result = instance.do_something("测试 テスト")
        assert "测试 テスト" in result
    
    # Edge case tests
    
    def test_do_something_empty_string_raises(self, instance):
        """Test do_something raises on empty string."""
        with pytest.raises(ValueError, match="cannot be empty"):
            instance.do_something("")
    
    def test_do_something_none_raises(self, instance):
        """Test do_something raises on None."""
        with pytest.raises(ValueError):
            instance.do_something(None)
    
    def test_do_something_whitespace_only(self, instance):
        """Test do_something with whitespace-only input."""
        # Decide expected behavior and test accordingly
        result = instance.do_something("   ")
        assert "   " in result  # or expect ValueError
    
    # Batch processing tests
    
    def test_process_batch_empty_list(self, instance):
        """Test process_batch with empty list."""
        result = instance.process_batch([])
        assert result == []
    
    def test_process_batch_filters_empty(self, instance):
        """Test process_batch filters empty strings."""
        result = instance.process_batch(["a", "", "b", None, "c"])
        assert len(result) == 3
    
    def test_process_batch_preserves_order(self, instance):
        """Test process_batch preserves input order."""
        result = instance.process_batch(["first", "second", "third"])
        assert "first" in result[0]
        assert "second" in result[1]
        assert "third" in result[2]
    
    # Property tests
    
    def test_is_enabled_default(self, instance):
        """Test is_enabled with default config."""
        assert instance.is_enabled is True
    
    def test_is_enabled_when_disabled(self):
        """Test is_enabled when explicitly disabled."""
        config = [ClassName]Config(enabled=False)
        obj = [ClassName](config)
        assert obj.is_enabled is False
    
    # Module-level function tests
    
    def test_get_returns_singleton(self):
        """Test get_[class_name] returns same instance."""
        obj1 = get_[class_name]()
        obj2 = get_[class_name]()
        assert obj1 is obj2
    
    def test_reset_clears_singleton(self):
        """Test reset clears the singleton."""
        obj1 = get_[class_name]()
        reset_[class_name]()
        obj2 = get_[class_name]()
        assert obj1 is not obj2


class Test[ClassName]Integration:
    """Integration tests for [ClassName]."""
    
    def test_full_workflow(self):
        """Test complete workflow from init to completion."""
        obj = [ClassName]()
        obj.initialize()
        
        # Process items
        results = obj.process_batch(["item1", "item2", "item3"])
        
        # Verify
        assert len(results) == 3
        assert all("Result:" in r for r in results)


# Async test examples (if applicable)
class Test[ClassName]Async:
    """Async tests for [ClassName]."""
    
    @pytest.mark.asyncio
    async def test_async_operation(self):
        """Test async operation."""
        # If your class has async methods
        pass


# Parametrized test examples
class Test[ClassName]Parametrized:
    """Parametrized tests for edge cases."""
    
    @pytest.mark.parametrize("input_value,expected", [
        ("simple", "Result: simple"),
        ("with spaces", "Result: with spaces"),
        ("123", "Result: 123"),
        ("a" * 1000, "Result: " + "a" * 1000),  # Long input
    ])
    def test_do_something_various_inputs(self, input_value, expected):
        """Test do_something with various inputs."""
        obj = [ClassName]()
        result = obj.do_something(input_value)
        assert result == expected
```

### TEMPLATE-T002: Async Test Suite

```python
"""Async tests for [service_name] service."""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch

from src.mcp.[service_name] import [ServiceName], [ServiceName]Config


@pytest.fixture
def config():
    """Test configuration with short timeouts."""
    return [ServiceName]Config(
        timeout_seconds=1.0,
        max_retries=2,
        retry_delay_seconds=0.1,
        max_concurrent=5
    )


@pytest.fixture
def service(config):
    """Create test service."""
    return [ServiceName](config)


class Test[ServiceName]:
    """Tests for [ServiceName]."""
    
    @pytest.mark.asyncio
    async def test_start_stop(self, service):
        """Test service start and stop."""
        assert not service.is_running
        
        await service.start()
        assert service.is_running
        
        await service.stop()
        assert not service.is_running
    
    @pytest.mark.asyncio
    async def test_execute_success(self, service):
        """Test successful execution."""
        await service.start()
        
        result = await service.execute("test_op", {"key": "value"})
        
        assert result["status"] == "ok"
        assert result["operation"] == "test_op"
    
    @pytest.mark.asyncio
    async def test_execute_timeout(self, service):
        """Test execution timeout."""
        await service.start()
        
        # Mock slow operation
        with patch.object(
            service, '_do_execute',
            new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.side_effect = asyncio.sleep(10)
            
            with pytest.raises(asyncio.TimeoutError):
                await service.execute("slow_op", {})
    
    @pytest.mark.asyncio
    async def test_execute_retry_on_failure(self, service):
        """Test retry logic on transient failures."""
        await service.start()
        
        call_count = 0
        
        async def flaky_operation(*args):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise RuntimeError("Transient error")
            return {"status": "ok"}
        
        with patch.object(service, '_do_execute', flaky_operation):
            result = await service.execute("flaky_op", {})
        
        assert call_count == 2
        assert result["status"] == "ok"
    
    @pytest.mark.asyncio
    async def test_execute_batch_concurrent(self, service):
        """Test concurrent batch execution."""
        await service.start()
        
        operations = [
            ("op1", {"id": 1}),
            ("op2", {"id": 2}),
            ("op3", {"id": 3}),
        ]
        
        results = await service.execute_batch(operations)
        
        assert len(results) == 3
        assert all(r["status"] == "ok" for r in results)
    
    @pytest.mark.asyncio
    async def test_concurrency_limit(self, service):
        """Test that concurrency is limited."""
        await service.start()
        
        max_concurrent = 0
        current_concurrent = 0
        
        async def track_concurrency(*args):
            nonlocal max_concurrent, current_concurrent
            current_concurrent += 1
            max_concurrent = max(max_concurrent, current_concurrent)
            await asyncio.sleep(0.1)
            current_concurrent -= 1
            return {"status": "ok"}
        
        with patch.object(service, '_do_execute', track_concurrency):
            operations = [("op", {}) for _ in range(10)]
            await service.execute_batch(operations)
        
        assert max_concurrent <= service._config.max_concurrent
```

---

## Configuration Templates

### TEMPLATE-C001: YAML Configuration Schema

```yaml
# Configuration file template for [component]
# Version: 1.0.0

# Required settings
required:
  name: "component-name"
  version: "1.0"

# Server settings
server:
  host: "localhost"
  port: 8080
  workers: 4
  timeout_seconds: 30

# Authentication
auth:
  enabled: true
  type: "api_key"  # Options: api_key, jwt, oauth2
  # API Key settings
  api_key:
    header: "X-API-Key"
    query_param: "api_key"
  # JWT settings
  jwt:
    secret_env: "JWT_SECRET"
    algorithm: "HS256"
    expiry_minutes: 60

# Rate limiting
rate_limit:
  enabled: true
  requests_per_minute: 60
  burst_size: 10
  by: "ip"  # Options: ip, api_key, user

# Logging
logging:
  level: "INFO"  # Options: DEBUG, INFO, WARNING, ERROR
  format: "json"  # Options: json, text
  output: "stdout"  # Options: stdout, file
  file_path: "/var/log/component.log"

# Metrics
metrics:
  enabled: true
  endpoint: "/metrics"
  include_labels:
    - method
    - status
    - endpoint

# Feature flags
features:
  new_feature: false
  experimental_mode: false
  debug_endpoints: false

# Environment-specific overrides
environments:
  development:
    logging:
      level: "DEBUG"
    features:
      debug_endpoints: true
  
  production:
    server:
      workers: 8
    rate_limit:
      requests_per_minute: 120
```

### TEMPLATE-C002: Python Config Loader

```python
"""Configuration loader for [component].

Loads configuration from YAML files with environment overrides.
"""

import os
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import yaml  # or use ruamel.yaml for comments

logger = logging.getLogger(__name__)


@dataclass
class ServerConfig:
    """Server configuration."""
    host: str = "localhost"
    port: int = 8080
    workers: int = 4
    timeout_seconds: int = 30


@dataclass
class AuthConfig:
    """Authentication configuration."""
    enabled: bool = True
    type: str = "api_key"
    api_key_header: str = "X-API-Key"
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 60


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    enabled: bool = True
    requests_per_minute: int = 60
    burst_size: int = 10
    by: str = "ip"


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "json"
    output: str = "stdout"
    file_path: Optional[str] = None


@dataclass
class [Component]Config:
    """Main configuration container."""
    
    name: str = "component"
    version: str = "1.0"
    server: ServerConfig = field(default_factory=ServerConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    features: Dict[str, bool] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "[Component]Config":
        """Create config from dictionary.
        
        Args:
            data: Configuration dictionary.
            
        Returns:
            Config instance.
        """
        return cls(
            name=data.get("required", {}).get("name", "component"),
            version=data.get("required", {}).get("version", "1.0"),
            server=ServerConfig(**data.get("server", {})),
            auth=AuthConfig(
                enabled=data.get("auth", {}).get("enabled", True),
                type=data.get("auth", {}).get("type", "api_key"),
                api_key_header=data.get("auth", {}).get("api_key", {}).get("header", "X-API-Key"),
            ),
            rate_limit=RateLimitConfig(**data.get("rate_limit", {})),
            logging=LoggingConfig(**data.get("logging", {})),
            features=data.get("features", {}),
        )
    
    @classmethod
    def from_yaml(
        cls,
        path: Path,
        environment: Optional[str] = None
    ) -> "[Component]Config":
        """Load config from YAML file.
        
        Args:
            path: Path to YAML file.
            environment: Optional environment for overrides.
            
        Returns:
            Config instance.
        """
        with open(path) as f:
            data = yaml.safe_load(f)
        
        # Apply environment overrides
        if environment and "environments" in data:
            env_overrides = data["environments"].get(environment, {})
            data = _deep_merge(data, env_overrides)
        
        return cls.from_dict(data)
    
    def validate(self) -> list[str]:
        """Validate configuration.
        
        Returns:
            List of validation errors (empty if valid).
        """
        errors = []
        
        if not self.name:
            errors.append("name is required")
        
        if self.server.port < 1 or self.server.port > 65535:
            errors.append(f"invalid port: {self.server.port}")
        
        if self.server.workers < 1:
            errors.append("workers must be at least 1")
        
        if self.rate_limit.enabled and self.rate_limit.requests_per_minute < 1:
            errors.append("requests_per_minute must be at least 1")
        
        return errors


def _deep_merge(base: Dict, override: Dict) -> Dict:
    """Deep merge two dictionaries."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(
    config_path: Optional[str] = None,
    environment: Optional[str] = None
) -> [Component]Config:
    """Load configuration.
    
    Args:
        config_path: Path to config file. Uses default if not provided.
        environment: Environment name for overrides.
        
    Returns:
        Loaded configuration.
    """
    # Determine config path
    if config_path:
        path = Path(config_path)
    else:
        path = Path("config/config.yaml")
    
    # Determine environment
    if not environment:
        environment = os.environ.get("APP_ENV", "development")
    
    # Load and validate
    if path.exists():
        config = [Component]Config.from_yaml(path, environment)
    else:
        logger.warning("Config file not found, using defaults: %s", path)
        config = [Component]Config()
    
    errors = config.validate()
    if errors:
        raise ValueError(f"Configuration errors: {errors}")
    
    return config
```

---

## CLI Templates

### TEMPLATE-CLI001: CLI Application with Subcommands

```python
"""CLI for [component].

Usage:
    python -m [component].cli [command] [options]

Commands:
    start       Start the service
    stop        Stop the service
    status      Show service status
    config      Configuration management
"""

import argparse
import logging
import sys
from typing import Optional, Sequence

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def cmd_start(args: argparse.Namespace) -> int:
    """Start the service."""
    logger.info("Starting service...")
    logger.info("Host: %s, Port: %d", args.host, args.port)
    
    # Implementation here
    return 0


def cmd_stop(args: argparse.Namespace) -> int:
    """Stop the service."""
    logger.info("Stopping service...")
    
    if args.force:
        logger.warning("Force stop requested")
    
    # Implementation here
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """Show service status."""
    print("Service Status")
    print("-" * 40)
    print(f"Running: {'Yes' if args.verbose else 'No'}")
    
    if args.verbose:
        print(f"Uptime: 1h 23m")
        print(f"Requests: 12,345")
    
    return 0


def cmd_config(args: argparse.Namespace) -> int:
    """Configuration management."""
    if args.config_action == "show":
        print("Current configuration:")
        print("  host: localhost")
        print("  port: 8080")
    elif args.config_action == "validate":
        print("Configuration is valid")
    elif args.config_action == "set":
        print(f"Setting {args.key} = {args.value}")
    
    return 0


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog="[component]",
        description="[Component] CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to configuration file"
    )
    
    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        required=True
    )
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start the service")
    start_parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host to bind to"
    )
    start_parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to listen on"
    )
    start_parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of worker processes"
    )
    start_parser.set_defaults(func=cmd_start)
    
    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop the service")
    stop_parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Force immediate stop"
    )
    stop_parser.set_defaults(func=cmd_stop)
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show service status")
    status_parser.set_defaults(func=cmd_status)
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_subparsers = config_parser.add_subparsers(
        dest="config_action",
        required=True
    )
    
    config_subparsers.add_parser("show", help="Show configuration")
    config_subparsers.add_parser("validate", help="Validate configuration")
    
    set_parser = config_subparsers.add_parser("set", help="Set configuration value")
    set_parser.add_argument("key", help="Configuration key")
    set_parser.add_argument("value", help="Configuration value")
    
    config_parser.set_defaults(func=cmd_config)
    
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Main entry point.
    
    Args:
        argv: Command line arguments.
        
    Returns:
        Exit code.
    """
    parser = create_parser()
    args = parser.parse_args(argv)
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        return args.func(args)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 130
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

---

## Workflow Templates

### TEMPLATE-W001: GitHub Actions Workflow

```yaml
# .github/workflows/[workflow-name].yml
name: [Workflow Name]

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy to'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production

env:
  PYTHON_VERSION: "3.11"
  UV_CACHE_DIR: /tmp/uv-cache

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install UV
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      
      - name: Install dependencies
        run: uv pip install --system ruff black mypy
      
      - name: Run ruff
        run: ruff check .
      
      - name: Run black
        run: black --check .
      
      - name: Run mypy
        run: mypy src/
        continue-on-error: true

  test:
    name: Test
    runs-on: ubuntu-latest
    needs: lint
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Cache UV
        uses: actions/cache@v4
        with:
          path: ${{ env.UV_CACHE_DIR }}
          key: uv-${{ runner.os }}-py${{ matrix.python-version }}-${{ hashFiles('requirements*.txt') }}
          restore-keys: |
            uv-${{ runner.os }}-py${{ matrix.python-version }}-
      
      - name: Install UV and dependencies
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          uv pip install --system -r requirements-test.txt
      
      - name: Run tests
        run: pytest tests/ -v --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: coverage.xml
          fail_ci_if_error: false

  build:
    name: Build
    runs-on: ubuntu-latest
    needs: test
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Build package
        run: |
          pip install build
          python -m build
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
          retention-days: 30
```

---

## Usage Instructions

1. **Copy the relevant template**
2. **Replace placeholders** (marked with `[brackets]`)
3. **Customize** for your specific needs
4. **Verify syntax** with appropriate tools
5. **Add tests** for any new code

## Placeholder Reference

| Placeholder | Replace With | Example |
|-------------|--------------|---------|
| `[ClassName]` | PascalCase class name | `SessionManager` |
| `[class_name]` | snake_case for functions | `session_manager` |
| `[module_name]` | Module file name | `session_manager` |
| `[ServiceName]` | Service class name | `AuthService` |
| `[State]` | State machine prefix | `Task` |
| `[Component]` | Component name | `MCP` |
| `[description]` | Brief description | `Manages user sessions` |
