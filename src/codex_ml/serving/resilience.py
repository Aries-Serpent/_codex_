"""
Resilience patterns for ML serving

Provides fault-tolerance and graceful degradation:
- Retry logic with exponential backoff
- Circuit breaker pattern
- Graceful degradation with fallback
- Health-based routing
"""
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional
from threading import Lock

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
    """
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout: float = 60.0
    half_open_max_calls: int = 3


class CircuitBreaker:
    """Circuit breaker pattern implementation
    
    Prevents cascading failures by stopping requests to a failing service
    and allowing time for recovery.
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Service failing, requests rejected immediately
    - HALF_OPEN: Testing recovery, limited requests allowed
    
    Attributes:
        config: Circuit breaker configuration
        state: Current circuit state
        failure_count: Consecutive failures
        success_count: Consecutive successes (in half-open)
        last_failure_time: Time of last failure
        half_open_calls: Number of calls in half-open state
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
        
        logger.info(
            f"CircuitBreaker initialized: threshold={self.config.failure_threshold}, "
            f"timeout={self.config.timeout}s"
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
            # Check if we should allow the call
            if not self._should_allow_request():
                raise Exception(f"Circuit breaker is {self.state.value}, request rejected")
            
            # Track half-open calls
            if self.state == CircuitState.HALF_OPEN:
                self.half_open_calls += 1
        
        # Execute function
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _should_allow_request(self) -> bool:
        """Check if request should be allowed"""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # Check if timeout expired
            if self.last_failure_time and \
               (time.time() - self.last_failure_time) >= self.config.timeout:
                logger.info("Circuit breaker timeout expired, entering half-open state")
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
                return True
            return False
        
        if self.state == CircuitState.HALF_OPEN:
            # Allow limited requests in half-open
            return self.half_open_calls < self.config.half_open_max_calls
        
        return False
    
    def _on_success(self) -> None:
        """Handle successful call"""
        with self.lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                logger.debug(f"Circuit breaker success: {self.success_count}/{self.config.success_threshold}")
                
                if self.success_count >= self.config.success_threshold:
                    logger.info("Circuit breaker closing after successful recovery")
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    self.success_count = 0
                    self.half_open_calls = 0
            else:
                # Reset failure count on success in closed state
                self.failure_count = 0
    
    def _on_failure(self) -> None:
        """Handle failed call"""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.state == CircuitState.HALF_OPEN:
                logger.warning("Circuit breaker failure in half-open, reopening")
                self.state = CircuitState.OPEN
                self.success_count = 0
                self.half_open_calls = 0
            elif self.state == CircuitState.CLOSED:
                logger.debug(f"Circuit breaker failure: {self.failure_count}/{self.config.failure_threshold}")
                
                if self.failure_count >= self.config.failure_threshold:
                    logger.warning(f"Circuit breaker opening after {self.failure_count} failures")
                    self.state = CircuitState.OPEN
    
    def reset(self) -> None:
        """Manually reset circuit breaker to closed state"""
        with self.lock:
            logger.info("Circuit breaker manually reset")
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.half_open_calls = 0
            self.last_failure_time = None
    
    def get_state(self) -> dict:
        """Get current circuit breaker state"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
        }


def retry_with_backoff(
    func: Callable[..., Any],
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,),
    *args,
    **kwargs
) -> Any:
    """Retry function with exponential backoff
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        backoff_factor: Multiplier for delay on each retry
        exceptions: Tuple of exceptions to catch and retry
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
    
    raise last_exception


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
        **kwargs
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
        except Exception as e:
            logger.warning(f"Primary function failed: {e}, attempting fallback")
            
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
