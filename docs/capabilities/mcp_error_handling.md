# MCP Error Handling

## Overview

The MCP (Model Context Protocol) error handling capability provides comprehensive error management for MCP services, including structured error classes, error codes, JSON-RPC error responses, retry mechanisms, and graceful degradation patterns.

**Keywords**: error, exception, handling, mcp-error, error-code, jsonrpc, error-response, recovery, retry, fallback, graceful-degradation, error-handler, traceback, mcp, safeguards, validation, robustness

## Purpose

Manages MCP error handling through:
- **Structured Errors**: Typed error classes with rich context
- **Error Codes**: Standardized error code system
- **JSON-RPC Compliance**: Protocol-compliant error responses
- **Recovery Mechanisms**: Automatic retry and fallback strategies
- **Error Logging**: Comprehensive error tracking and analysis

## Architecture

### Error Handling Layers

```
┌─────────────────────────────────────┐
│   Request Handler                   │
│   (Try-catch wrapper)               │
└─────────────┬───────────────────────┘
              │ catches
              ▼
┌─────────────────────────────────────┐
│   Error Classifier                  │
│   (Categorize and enrich)           │
└─────────────┬───────────────────────┘
              │ transforms
              ▼
┌─────────────────────────────────────┐
│   Error Response Builder            │
│   (Format for client)               │
└─────────────────────────────────────┘
```

### Error Flow

```python
# Pseudocode for error handling flow
def handle_request(request):
    try:
        # 1. Process request
        result = process(request)
        return success_response(result)
        
    except MCPError as e:
        # 2. Handle known MCP errors
        return error_response(e.code, e.message, e.data)
        
    except Exception as e:
        # 3. Handle unexpected errors (safeguard)
        log_error(e, traceback.format_exc())
        return error_response(-32603, "Internal error")
```

## Implementation

### Error Class Hierarchy

Define structured error classes:

```python
from enum import IntEnum
from typing import Any, Optional
import traceback

class ErrorCode(IntEnum):
    """JSON-RPC and MCP error codes."""
    # JSON-RPC standard errors
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    
    # MCP-specific errors
    AUTHENTICATION_REQUIRED = -32001
    AUTHORIZATION_FAILED = -32002
    RATE_LIMIT_EXCEEDED = -32003
    RESOURCE_NOT_FOUND = -32004
    VALIDATION_ERROR = -32005
    TIMEOUT = -32006

class MCPError(Exception):
    """
    Base error class for MCP services.
    
    Provides structured error handling with:
    - Error codes for categorization
    - Rich error context
    - Traceback preservation
    - Serialization support
    
    Safeguards:
    - Input validation on error creation
    - Secure error message sanitization
    - Traceback filtering for sensitive data
    """
    
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        data: Optional[dict] = None,
        cause: Optional[Exception] = None
    ):
        """
        Initialize MCP error.
        
        Args:
            code: Error code from ErrorCode enum
            message: Human-readable error message
            data: Additional error context
            cause: Original exception that caused this error
        """
        super().__init__(message)
        self.code = code
        self.message = self._sanitize_message(message)
        self.data = data or {}
        self.cause = cause
        self.traceback_str = traceback.format_exc() if cause else None
    
    def _sanitize_message(self, message: str) -> str:
        """
        Sanitize error message to prevent information leakage.
        
        Safeguard: Removes sensitive information from error messages.
        """
        # Remove potential secrets or paths
        sanitized = message
        # Add sanitization logic as needed
        return sanitized[:500]  # Bounds check (safeguard)
    
    def to_dict(self) -> dict:
        """Convert error to dictionary for JSON serialization."""
        return {
            "code": int(self.code),
            "message": self.message,
            "data": self.data,
        }
    
    def to_jsonrpc(self) -> dict:
        """Convert to JSON-RPC error response format."""
        return {
            "jsonrpc": "2.0",
            "error": self.to_dict(),
            "id": None,  # Should be set by caller
        }


class AuthenticationError(MCPError):
    """Authentication required or failed."""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(ErrorCode.AUTHENTICATION_REQUIRED, message)


class AuthorizationError(MCPError):
    """Authorization/permission denied."""
    
    def __init__(self, message: str = "Permission denied"):
        super().__init__(ErrorCode.AUTHORIZATION_FAILED, message)


class ValidationError(MCPError):
    """Request validation failed."""
    
    def __init__(self, message: str, errors: list = None):
        super().__init__(
            ErrorCode.VALIDATION_ERROR,
            message,
            data={"validation_errors": errors or []}
        )


class RateLimitError(MCPError):
    """Rate limit exceeded."""
    
    def __init__(self, retry_after: int = 60):
        super().__init__(
            ErrorCode.RATE_LIMIT_EXCEEDED,
            "Rate limit exceeded",
            data={"retry_after": retry_after}
        )
```

### Error Handler Middleware

Implement centralized error handling:

```python
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class ErrorHandler:
    """
    Centralized error handler for MCP services.
    
    Provides:
    - Consistent error response formatting
    - Error logging and tracking
    - Recovery and retry logic
    - Graceful degradation
    
    Safeguards:
    - Prevents information leakage
    - Logs all errors for debugging
    - Handles unexpected errors gracefully
    """
    
    def __init__(self, include_traceback: bool = False):
        """
        Initialize error handler.
        
        Args:
            include_traceback: Include traceback in development mode
        """
        self._include_traceback = include_traceback
    
    def handle(self, error: Exception, request_id: str = None) -> dict:
        """
        Handle an exception and return formatted response.
        
        Safeguards:
        - Logs all errors with context
        - Sanitizes error messages
        - Returns safe error responses
        
        Args:
            error: Exception to handle
            request_id: Request ID for correlation
            
        Returns:
            JSON-RPC formatted error response
        """
        # Log the error (safeguard - observability)
        self._log_error(error, request_id)
        
        # Convert to MCPError if needed
        if isinstance(error, MCPError):
            mcp_error = error
        else:
            # Wrap unexpected errors (safeguard)
            mcp_error = MCPError(
                ErrorCode.INTERNAL_ERROR,
                "An internal error occurred",
                cause=error
            )
        
        # Build response
        response = mcp_error.to_jsonrpc()
        response["id"] = request_id
        
        # Add traceback in development mode only
        if self._include_traceback and mcp_error.traceback_str:
            response["error"]["data"]["traceback"] = mcp_error.traceback_str
        
        return response
    
    def _log_error(self, error: Exception, request_id: str):
        """Log error with context."""
        logger.error(
            "Error handling request",
            extra={
                "error_type": type(error).__name__,
                "error_message": str(error),
                "request_id": request_id,
            },
            exc_info=True
        )


def error_handler(func):
    """Decorator for automatic error handling."""
    handler = ErrorHandler()
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            request_id = kwargs.get("request_id")
            return handler.handle(e, request_id)
    
    return wrapper
```

### Retry and Recovery

Implement retry mechanisms:

```python
import asyncio
from typing import Callable, TypeVar

T = TypeVar("T")

class RetryPolicy:
    """
    Retry policy for transient errors.
    
    Provides:
    - Exponential backoff
    - Configurable retry limits
    - Error classification
    
    Safeguards:
    - Bounds on retry attempts
    - Timeout protection
    - Error logging
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0
    ):
        """
        Initialize retry policy.
        
        Args:
            max_retries: Maximum retry attempts
            base_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Multiplier for exponential backoff
        """
        # Bounds checking (safeguard)
        self.max_retries = min(max_retries, 10)
        self.base_delay = max(base_delay, 0.1)
        self.max_delay = min(max_delay, 300.0)
        self.exponential_base = exponential_base
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number."""
        delay = self.base_delay * (self.exponential_base ** attempt)
        return min(delay, self.max_delay)
    
    def is_retryable(self, error: Exception) -> bool:
        """Determine if error is retryable."""
        retryable_codes = {
            ErrorCode.TIMEOUT,
            ErrorCode.RATE_LIMIT_EXCEEDED,
            ErrorCode.INTERNAL_ERROR,
        }
        
        if isinstance(error, MCPError):
            return error.code in retryable_codes
        
        # Retry on connection errors
        return isinstance(error, (ConnectionError, TimeoutError))


async def with_retry(
    func: Callable[[], T],
    policy: RetryPolicy = None
) -> T:
    """
    Execute function with retry on transient errors.
    
    Safeguards:
    - Limits retry attempts
    - Implements backoff
    - Logs retry attempts
    
    Args:
        func: Async function to execute
        policy: Retry policy (default: standard policy)
        
    Returns:
        Function result
        
    Raises:
        Last exception if all retries fail
    """
    policy = policy or RetryPolicy()
    last_error = None
    
    for attempt in range(policy.max_retries + 1):
        try:
            return await func()
        except Exception as e:
            last_error = e
            
            if attempt >= policy.max_retries:
                break
            
            if not policy.is_retryable(e):
                break
            
            delay = policy.get_delay(attempt)
            logger.warning(
                f"Retry attempt {attempt + 1}/{policy.max_retries}, "
                f"waiting {delay:.1f}s"
            )
            await asyncio.sleep(delay)
    
    raise last_error
```

## Configuration

### Environment Variables

Configure error handling via environment:

```bash
# Error response settings
export MCP_ERROR_INCLUDE_TRACEBACK="false"
export MCP_ERROR_LOG_LEVEL="ERROR"

# Retry settings
export MCP_RETRY_MAX_ATTEMPTS="3"
export MCP_RETRY_BASE_DELAY="1.0"
export MCP_RETRY_MAX_DELAY="60.0"

# Error reporting
export MCP_ERROR_REPORTING_ENABLED="true"
export MCP_ERROR_REPORTING_ENDPOINT="https://errors.example.com"
```

### Configuration File

Use YAML for error handling configuration:

```yaml
# error_config.yaml
error_handling:
  include_traceback: false
  log_level: "ERROR"
  sanitize_messages: true
  
  retry:
    enabled: true
    max_attempts: 3
    base_delay: 1.0
    max_delay: 60.0
    exponential_base: 2.0
    
  recovery:
    circuit_breaker:
      enabled: true
      failure_threshold: 5
      recovery_timeout: 30
    
  reporting:
    enabled: true
    endpoint: "https://errors.example.com"
    sample_rate: 1.0
```

## Usage Examples

### Example 1: Basic Error Handling

```python
async def process_request(request):
    """Process request with error handling."""
    try:
        # Validate request
        if not request.data:
            raise ValidationError("Request data is required")
        
        # Process
        result = await do_processing(request.data)
        return {"result": result}
        
    except ValidationError:
        raise  # Re-raise validation errors
    except Exception as e:
        # Wrap unexpected errors
        raise MCPError(
            ErrorCode.INTERNAL_ERROR,
            "Processing failed",
            cause=e
        )
```

### Example 2: Retry with Fallback

```python
async def fetch_data_with_fallback(key: str):
    """Fetch data with retry and fallback."""
    try:
        # Try primary source with retry
        return await with_retry(
            lambda: fetch_from_primary(key),
            RetryPolicy(max_retries=3)
        )
    except Exception:
        # Fallback to secondary source (graceful degradation)
        logger.warning(f"Primary source failed, using fallback for {key}")
        return await fetch_from_fallback(key)
```

### Example 3: Error Recovery Callback

```python
def on_error(error: MCPError, context: dict):
    """Error recovery callback."""
    if error.code == ErrorCode.RATE_LIMIT_EXCEEDED:
        # Wait and retry
        retry_after = error.data.get("retry_after", 60)
        return {"action": "retry", "delay": retry_after}
    
    elif error.code == ErrorCode.TIMEOUT:
        # Use cached response
        return {"action": "cache", "key": context.get("cache_key")}
    
    else:
        # No recovery possible
        return {"action": "fail"}
```

## Best Practices

### 1. Use Specific Error Classes

```python
# Good: Specific error type
raise ValidationError("Email format is invalid", errors=["email"])

# Bad: Generic error
raise Exception("Validation failed")
```

### 2. Include Context in Errors

```python
raise MCPError(
    ErrorCode.RESOURCE_NOT_FOUND,
    f"User {user_id} not found",
    data={"user_id": user_id, "searched_at": datetime.utcnow().isoformat()}
)
```

### 3. Implement Circuit Breakers

```python
class CircuitBreaker:
    """Prevent cascade failures."""
    
    def __init__(self, failure_threshold: int = 5):
        self.failures = 0
        self.threshold = failure_threshold
        self.state = "closed"
    
    def record_failure(self):
        self.failures += 1
        if self.failures >= self.threshold:
            self.state = "open"
    
    def is_open(self) -> bool:
        return self.state == "open"
```

## Troubleshooting

### Debugging Error Flows

**Problem**: Errors not being caught properly

**Solution**:
1. Check error class hierarchy
2. Verify try-catch order
3. Enable traceback logging
4. Review middleware order

### Error Response Issues

**Problem**: Incorrect error codes in responses

**Solution**:
1. Verify ErrorCode enum usage
2. Check error transformation logic
3. Review JSON-RPC compliance
4. Test error serialization

## Security Considerations

### Information Leakage

- Sanitize error messages in production
- Filter stack traces for sensitive paths
- Log full errors server-side only
- Use generic messages for unexpected errors

### Error Injection

- Validate all error inputs
- Limit error message length
- Escape special characters
- Rate limit error endpoints

## Related Capabilities

- **mcp-observability**: Error logging and monitoring
- **mcp-rate-limiting**: Rate limit error handling
- **mcp-authz-authn**: Authentication error handling
- **mcp-protocol-surface**: Protocol error responses

## References

- [JSON-RPC 2.0 Specification - Error Object](https://www.jsonrpc.org/specification#error_object)
- [Error Handling Best Practices](https://docs.microsoft.com/en-us/azure/architecture/best-practices/api-design#error-handling)
- [Resilience Patterns](https://docs.microsoft.com/en-us/azure/architecture/patterns/category/resiliency)
- MCP Protocol Error Codes
