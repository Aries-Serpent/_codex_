"""
Resilience patterns for ML serving

Provides fault-tolerance and graceful degradation:
- Retry logic with exponential backoff
- Circuit breaker pattern with advanced features
- Per-model circuit breakers
- Graceful degradation with fallback
- Health-based routing
"""

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from threading import Lock
from typing import Any, Optional

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker

    Attributes:
        failure_threshold: Number of failures before opening circuit
        success_threshold: Number of successes to close circuit from half-open
        timeout: Seconds to wait before entering half-open state
        half_open_max_calls: Max calls to allow in half-open state
        use_exponential_backoff: Enable exponential backoff for recovery
        initial_backoff: Initial backoff time in seconds
        max_backoff: Maximum backoff time in seconds
        backoff_multiplier: Multiplier for exponential backoff
        enable_health_probe: Enable health probing in half-open state
        health_probe_func: Optional health check function
        persist_state: Enable state persistence across restarts
        state_file: File path for state persistence
    """

    failure_threshold: int = 5
    success_threshold: int = 2
    timeout: float = 60.0
    half_open_max_calls: int = 3
    use_exponential_backoff: bool = True
    initial_backoff: float = 1.0
    max_backoff: float = 300.0
    backoff_multiplier: float = 2.0
    enable_health_probe: bool = True
    health_probe_func: Optional[Callable[[], bool]] = None
    persist_state: bool = False
    state_file: Optional[str] = None


class CircuitBreaker:
    """Circuit breaker pattern implementation with advanced features

    Prevents cascading failures by stopping requests to a failing service
    and allowing time for recovery.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Service failing, requests rejected immediately
    - HALF_OPEN: Testing recovery, limited requests allowed

    Features:
    - Exponential backoff for recovery attempts
    - Health probing before allowing traffic
    - State persistence across restarts
    - Per-endpoint metrics

    Attributes:
        config: Circuit breaker configuration
        state: Current circuit state
        failure_count: Consecutive failures
        success_count: Consecutive successes (in half-open)
        last_failure_time: Time of last failure
        half_open_calls: Number of calls in half-open state
        current_backoff: Current backoff time
        consecutive_failures: Total consecutive failures for backoff calculation
        metrics: Performance and state metrics
    """

    def __init__(self, config: Optional[CircuitBreakerConfig] = None):
        """Initialize circuit breaker

        Args:
            config: Configuration, uses defaults if None
        """
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.half_open_calls = 0
        self.lock = Lock()

        # Enhanced features
        self.current_backoff = self.config.initial_backoff
        self.consecutive_failures = 0
        self.metrics: dict[str, Any] = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "rejected_calls": 0,
            "state_transitions": 0,
            "last_state_change": None,
        }

        # Load persisted state if enabled
        if self.config.persist_state and self.config.state_file:
            self._load_state()

        logger.info(
            f"CircuitBreaker initialized: threshold={self.config.failure_threshold}, "
            f"timeout={self.config.timeout}s, exponential_backoff={self.config.use_exponential_backoff}"  # noqa: E501
        )

    def call(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection

        Args:
            func: Function to call
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Function result

        Raises:
            Exception: If circuit is open or function fails
        """
        with self.lock:
            self.metrics["total_calls"] += 1

            # Check if we should allow the call
            if not self._should_allow_request():
                self.metrics["rejected_calls"] += 1
                raise Exception(f"Circuit breaker is {self.state.value}, request rejected")

            # Perform health probe if enabled and in half-open state
            if (
                self.state == CircuitState.HALF_OPEN
                and self.config.enable_health_probe
                and self.config.health_probe_func
            ):
                try:
                    if not self.config.health_probe_func():
                        logger.warning("Health probe failed, keeping circuit open")
                        raise Exception("Health probe failed")
                except (IOError, OSError) as e:
                    type(e).__name__
                    logger.debug("Exception: <ERROR_TYPE>")
                    logger.warning("Health probe error: <ERROR_TYPE>")
                    self._on_failure()
                    raise

            # Track half-open calls
            if self.state == CircuitState.HALF_OPEN:
                self.half_open_calls += 1

        # Execute function
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except (ConnectionError, TimeoutError):
            self._on_failure()
            raise

    def _should_allow_request(self) -> bool:
        """Check if request should be allowed"""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            # Calculate timeout with exponential backoff if enabled
            timeout = self.config.timeout
            if self.config.use_exponential_backoff:
                timeout = min(self.current_backoff, self.config.max_backoff)

            # Check if timeout expired
            if self.last_failure_time and (time.time() - self.last_failure_time) >= timeout:
                logger.info(
                    f"Circuit breaker timeout expired ({timeout:.1f}s), entering half-open state"
                )
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
                self._record_state_change()
                return True
            return False

        if self.state == CircuitState.HALF_OPEN:
            # Allow limited requests in half-open
            return self.half_open_calls < self.config.half_open_max_calls

        return False

    def _on_success(self) -> None:
        """Handle successful call"""
        with self.lock:
            self.metrics["successful_calls"] += 1

            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                logger.debug(
                    f"Circuit breaker success: {self.success_count}/{self.config.success_threshold}"
                )

                if self.success_count >= self.config.success_threshold:
                    logger.info("Circuit breaker closing after successful recovery")
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    self.success_count = 0
                    self.half_open_calls = 0
                    self.consecutive_failures = 0
                    self.current_backoff = self.config.initial_backoff
                    self._record_state_change()

                    # Persist state if enabled
                    if self.config.persist_state:
                        self._save_state()
            else:
                # Reset failure count on success in closed state
                self.failure_count = 0
                self.consecutive_failures = 0

    def _on_failure(self) -> None:
        """Handle failed call"""
        with self.lock:
            self.metrics["failed_calls"] += 1
            self.failure_count += 1
            self.consecutive_failures += 1
            self.last_failure_time = time.time()

            if self.state == CircuitState.HALF_OPEN:
                logger.warning("Circuit breaker failure in half-open, reopening")
                self.state = CircuitState.OPEN
                self.success_count = 0
                self.half_open_calls = 0

                # Increase backoff on failure in half-open
                if self.config.use_exponential_backoff:
                    self.current_backoff = min(
                        self.current_backoff * self.config.backoff_multiplier,
                        self.config.max_backoff,
                    )
                    logger.info(f"Backoff increased to {self.current_backoff:.1f}s")

                self._record_state_change()

                # Persist state if enabled
                if self.config.persist_state:
                    self._save_state()

            elif self.state == CircuitState.CLOSED:
                logger.debug(
                    f"Circuit breaker failure: {self.failure_count}/{self.config.failure_threshold}"
                )

                if self.failure_count >= self.config.failure_threshold:
                    logger.warning(f"Circuit breaker opening after {self.failure_count} failures")
                    self.state = CircuitState.OPEN

                    # Initialize backoff
                    if self.config.use_exponential_backoff:
                        self.current_backoff = self.config.initial_backoff

                    self._record_state_change()

                    # Persist state if enabled
                    if self.config.persist_state:
                        self._save_state()

    def reset(self) -> None:
        """Manually reset circuit breaker to closed state"""
        with self.lock:
            logger.info("Circuit breaker manually reset")
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.half_open_calls = 0
            self.last_failure_time = None
            self.consecutive_failures = 0
            self.current_backoff = self.config.initial_backoff
            self._record_state_change()

            # Persist state if enabled
            if self.config.persist_state:
                self._save_state()

    def get_state(self) -> dict[str, Any]:
        """Get current circuit breaker state"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
            "current_backoff": self.current_backoff,
            "consecutive_failures": self.consecutive_failures,
            "metrics": self.metrics.copy(),
        }

    def get_metrics(self) -> dict[str, Any]:
        """Get detailed metrics"""
        with self.lock:
            return {
                **self.metrics.copy(),
                "state": self.state.value,
                "current_backoff": self.current_backoff,
                "uptime_ratio": self._calculate_uptime_ratio(),
            }

    def _record_state_change(self) -> None:
        """Record state transition"""
        self.metrics["state_transitions"] += 1
        self.metrics["last_state_change"] = time.time()
        logger.info(f"Circuit breaker state changed to {self.state.value}")

    def _calculate_uptime_ratio(self) -> float:
        """Calculate uptime ratio (successful / total calls)"""
        total = self.metrics["total_calls"]
        if total == 0:
            return 1.0
        return self.metrics["successful_calls"] / total

    def _save_state(self) -> None:
        """Persist circuit breaker state to file"""
        if not self.config.state_file:
            return

        try:
            import json
            from pathlib import Path

            state_data = {
                "state": self.state.value,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "last_failure_time": self.last_failure_time,
                "consecutive_failures": self.consecutive_failures,
                "current_backoff": self.current_backoff,
                "metrics": self.metrics,
                "saved_at": time.time(),
            }

            state_file = Path(self.config.state_file)
            state_file.parent.mkdir(parents=True, exist_ok=True)

            with open(state_file, "w") as f:
                json.dump(state_data, f, indent=2)

            logger.debug(f"Circuit breaker state saved to {state_file}")
        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.warning("Failed to save circuit breaker state: <ERROR_TYPE>")

    def _load_state(self) -> None:
        """Load persisted circuit breaker state from file"""
        if not self.config.state_file:
            return

        try:
            import json
            from pathlib import Path

            state_file = Path(self.config.state_file)
            if not state_file.exists():
                logger.debug("No persisted state found, starting fresh")
                return

            with open(state_file) as f:
                state_data = json.load(f)

            # Restore state
            self.state = CircuitState(state_data["state"])
            self.failure_count = state_data["failure_count"]
            self.success_count = state_data["success_count"]
            self.last_failure_time = state_data.get("last_failure_time")
            self.consecutive_failures = state_data.get("consecutive_failures", 0)
            self.current_backoff = state_data.get("current_backoff", self.config.initial_backoff)
            self.metrics = state_data.get("metrics", self.metrics)

            logger.info(
                f"Circuit breaker state loaded: {self.state.value}, failures={self.failure_count}"
            )
        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.warning("Failed to load circuit breaker state: <ERROR_TYPE>, starting fresh")


def retry_with_backoff(
    func: Callable[..., Any],
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    exceptions: tuple[Any, ...] = (Exception,),
    *args,
    **kwargs,
) -> Any:
    """Retry function with exponential backoff

    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        backoff_factor: Multiplier for delay on each retry
        exceptions: tuple of exceptions to catch and retry
        *args: Positional arguments for function
        **kwargs: Keyword arguments for function

    Returns:
        Function result

    Raises:
        Exception: If all retries exhausted
    """
    delay = initial_delay
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return func(*args, **kwargs)
        except exceptions as e:
            last_exception = e

            if attempt < max_retries:
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                    f"Retrying in {delay:.2f}s..."
                )
                time.sleep(delay)
                delay = min(delay * backoff_factor, max_delay)
            else:
                logger.error(f"All {max_retries + 1} attempts failed")

    # Guard against None (defensive programming)
    if last_exception is not None:
        raise last_exception
    raise RuntimeError(
        f"Retry exhausted with no captured exception context (max_retries={max_retries})"
    )


class FallbackHandler:
    """Handle fallback strategies for graceful degradation

    Provides fallback mechanisms when primary operations fail.

    Attributes:
        fallback_func: Fallback function to call on primary failure
        use_cache: Whether to use cached results as fallback
        cache: Optional cache for fallback results
    """

    def __init__(
        self,
        fallback_func: Optional[Callable] = None,
        use_cache: bool = True,
        cache: Optional[Any] = None,
    ):
        """Initialize fallback handler

        Args:
            fallback_func: Function to call when primary fails
            use_cache: Whether to use cache as fallback
            cache: Cache instance for fallback
        """
        self.fallback_func = fallback_func
        self.use_cache = use_cache
        self.cache = cache

        logger.info(f"FallbackHandler initialized: use_cache={use_cache}")

    def call_with_fallback(
        self,
        func: Callable[..., Any],
        fallback_key: Optional[Any] = None,
        *args,
        **kwargs,
    ) -> Any:
        """Call function with fallback on failure

        Args:
            func: Primary function to call
            fallback_key: Key for cache lookup (if use_cache=True)
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Result from primary or fallback
        """
        try:
            return func(*args, **kwargs)
        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.warning("Primary function failed: <ERROR_TYPE>, attempting fallback")

            # Try cache fallback
            if self.use_cache and self.cache and fallback_key:
                cached_result = self.cache.get(fallback_key)
                if cached_result is not None:
                    logger.info("Using cached result as fallback")
                    return cached_result

            # Try custom fallback function
            if self.fallback_func:
                logger.info("Using custom fallback function")
                return self.fallback_func(*args, **kwargs)

            # No fallback available
            logger.error("No fallback available, re-raising exception")
            raise


class PerModelCircuitBreaker:
    """Manage circuit breakers per model

    Provides isolated circuit breakers for each model to prevent
    failures in one model from affecting others.

    Attributes:
        default_config: Default configuration for new circuit breakers
        breakers: Dictionary of model_name -> CircuitBreaker
        lock: Thread lock for breaker management
    """

    def __init__(self, default_config: Optional[CircuitBreakerConfig] = None):
        """Initialize per-model circuit breaker manager

        Args:
            default_config: Default config for new breakers
        """
        self.default_config = default_config or CircuitBreakerConfig()
        self.breakers: dict[str, CircuitBreaker] = {}
        self.lock = Lock()

        logger.info("PerModelCircuitBreaker manager initialized")

    def get_breaker(self, model_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for model

        Args:
            model_name: Model identifier

        Returns:
            Circuit breaker for the model
        """
        with self.lock:
            if model_name not in self.breakers:
                # Create circuit breaker with state file per model
                config = CircuitBreakerConfig(
                    **{
                        **self.default_config.__dict__,
                        "state_file": (
                            f"{self.default_config.state_file}_{model_name}.json"
                            if self.default_config.state_file
                            else None
                        ),
                    }
                )
                self.breakers[model_name] = CircuitBreaker(config)
                logger.info(f"Created circuit breaker for model: {model_name}")

            return self.breakers[model_name]

    def call(self, model_name: str, func: Callable[..., Any], *args, **kwargs) -> Any:
        """Execute function with model-specific circuit breaker

        Args:
            model_name: Model identifier
            func: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result
        """
        breaker = self.get_breaker(model_name)
        return breaker.call(func, *args, **kwargs)

    def get_all_states(self) -> dict[str, dict[str, Any]]:
        """Get states of all circuit breakers

        Returns:
            Dictionary of model_name -> state
        """
        with self.lock:
            return {name: breaker.get_state() for name, breaker in self.breakers.items()}

    def get_all_metrics(self) -> dict[str, dict[str, Any]]:
        """Get metrics from all circuit breakers

        Returns:
            Dictionary of model_name -> metrics
        """
        with self.lock:
            return {name: breaker.get_metrics() for name, breaker in self.breakers.items()}

    def reset_all(self) -> None:
        """Reset all circuit breakers"""
        with self.lock:
            for breaker in self.breakers.values():
                breaker.reset()
            logger.info("All circuit breakers reset")

    def reset_model(self, model_name: str) -> None:
        """Reset circuit breaker for specific model

        Args:
            model_name: Model identifier
        """
        breaker = self.get_breaker(model_name)
        breaker.reset()
        logger.info(f"Circuit breaker reset for model: {model_name}")
