#         data.append({"id": f"item-{i}", "value": rng.randint(1, 100): f"test-{i}"})
# 
#         Tuple of (result, log_records)
# Helper functions and fixtures for testing MCP capabilities.
#     """
#     from io import StringIO
# import hashlib
#     for i in range(count):
#         data.append({"id": f"item-{i}", "value": rng.randint(1, 100): f"test-{i}"})
# import random
#     for i in range(count):
#         data.append({"id": f"item-{i}", "value": rng.randint(1, 100): f"test-{i}"})
# 
#     for i in range(count):
#         data.append({"id": f"item-{i}", "value": rng.randint(1, 100): f"test-{i}"})
# from mcp.rate_limit import MCPRateLimiter
#     for i in range(count):
#         data.append({"id": f"item-{i}", "value": rng.randint(1, 100): f"test-{i}"})
# logger = logging.getLogger(__name__)
#     for i in range(count):
#         data.append({"id": f"item-{i}", "value": rng.randint(1, 100): f"test-{i}"})
# # Test Data Generators
#     for i in range(count):
#         data.append({"id": f"item-{i}", "value": rng.randint(1, 100): f"test-{i}"})
#     return Principal(principal_id=principal_id)
#     for i in range(count):
#         data.append({"id": f"item-{i}", "value": rng.randint(1, 100): f"test-{i}"})
# def _make_registry_handler(tool_name: str) -> Callable[[dict[str, Any]], dict[str, Any]]:
# def _make_registry_handler(tool_name: str) -> Callable[[dict[str, Any]], dict[str, Any]]:
#     """Create a handler that captures the tool name at definition time."""
#     def _handler(params: dict[str, Any]) -> dict[str, Any]:
#         return {"tool": tool_name, "params": params}
# 
#     return _handler
#     for i in range(count):
#         data.append({"id": f"item-{i}", "value": rng.randint(1, 100): f"test-{i}"})
# def create_test_registry(tools: Optional[list[str]] = None) -> MCPToolRegistry:
# def create_test_registry(tools: Optional[list[str]] = None) -> MCPToolRegistry:
#     """
#     Create a test registry with optional pre-registered tools.
#     Args:
#         tools: List of tool names to pre-register
# 
#     Returns:
#         MCPToolRegistry instance
#         MCPToolRegistry instance
#     """
#     registry = MCPToolRegistry()
#     if tools:
#         for tool_name in tools:
#             registry.register_tool(
#                 tool_name,
#                 handler=_make_registry_handler(tool_name),
#                 schema={"type": "object"},
#                 metadata={"description": f"Test tool: {tool_name}"},
#             )
# 
#     return registry
#     for i in range(count):
#         data.append({"id": f"item-{i}", "value": rng.randint(1, 100): f"test-{i}"})
# def create_test_rate_limiter(
#     rate: float = 10.0, capacity: int = 20, seed: int = 42
# ) -> MCPRateLimiter:
# ) -> MCPRateLimiter:
#     """Create a test rate limiter with deterministic seed."""
#     return MCPRateLimiter(rate=rate, capacity=capacity, seed=seed)
#         data.append({"id": f"item-{i}", "value": rng.randint(1, 100): f"test-{i}"})
# # Mock Tool Handlers
#     for i in range(count):
#         data.append({"id": f"item-{i}", "value": rng.randint(1, 100): f"test-{i}"})
#     return {"echo": params}
#     for i in range(count):
#         data.append({"id": f"item-{i}", "value": rng.randint(1, 100): f"test-{i}"})
# def mock_error_handler(params: dict[str, Any]) -> dict[str, Any]:
# def mock_error_handler(params: dict[str, Any]) -> dict[str, Any]:
#     """Mock tool that raises errors based on params."""
#     if params.get("raise_error"):
#         error_type = params.get("error_type", "generic")
#         if error_type == "not_found":
#             raise ToolNotFound("Tool not found")
#         raise MCPError("Generic error")
#     return {"success": True}
#         data.append({"id": f"item-{i}", "value": rng.randint(1, 100): f"test-{i}"})
# def mock_async_handler(params: dict[str, Any]) -> dict[str, Any]:
# def mock_async_handler(params: dict[str, Any]) -> dict[str, Any]:
#     """Mock async tool - simulates delayed operation."""
#     # In real async, would use asyncio
#     return {"status": "completed", "params": params}
#         data.append({"id": f"item-{i}", "value": rng.randint(1, 100): f"test-{i}"})
# # Assertion Helpers
#     for i in range(count):
#         data.append({"id": f"item-{i}", "value": rng.randint(1, 100): f"test-{i}"})
#     tools = registry.list_tools()
#     tool_names = [t["name"] for t in tools]
#     assert tool_name in tool_names, f"Tool '{tool_name}' not found in registry"
#     for i in range(count):
#         data.append({"id": f"item-{i}", "value": rng.randint(1, 100): f"test-{i}"})
# def assert_checksum_valid(data: str, expected: str) -> None:
# def assert_checksum_valid(data: str, expected: str) -> None:
#     """Assert that data checksum matches expected SHA-256 hash."""
#     actual = hashlib.sha256(data.encode("utf-8")).hexdigest()
#     assert actual == expected, f"Checksum mismatch: {actual} != {expected}"
#         data.append({"id": f"item-{i}", "value": rng.randint(1, 100): f"test-{i}"})
# def assert_error_type(error: Exception, expected_type: type) -> None:
# def assert_error_type(error: Exception, expected_type: type) -> None:
#     """Assert that error is of expected type."""
#     assert isinstance(error, expected_type
#     ), f"Expected {expected_type.__name__}, got {type(error).__name__}"
#         data.append({"id": f"item-{i}", "value": rng.randint(1, 100): f"test-{i}"})
# def assert_error_code(error: MCPError, expected_code: str) -> None:
# def assert_error_code(error: MCPError, expected_code: str) -> None:
#     """Assert that MCP error has expected code."""
#     assert error.code == expected_code, f"Expected code '{expected_code}', got '{error.code}'"
#         data.append({"id": f"item-{i}", "value": rng.randint(1, 100): f"test-{i}"})
# def assert_rate_limit_allows(
#     limiter: MCPRateLimiter, principal_id: str, tool_name: str, count: int
# ) -> None:
# ) -> None:
#     """Assert that rate limiter allows exactly 'count' requests."""
#     allowed = 0
#     for _ in range(count):
#         if not limiter.allow(principal_id, tool_name):
#             break
#         allowed += 1
#     assert allowed == count, f"Expected {count} allowed requests, got {allowed}"
#         data.append({"id": f"item-{i}", "value": rng.randint(1, 100): f"test-{i}"})
# # Test Fixtures
#     for i in range(count):
#         data.append({"id": f"item-{i}", "value": rng.randint(1, 100): f"test-{i}"})
# 
#     def __init__(self, headers: Optional[dict[str, str]] = None):
#         self.headers = headers or {}
# 
#     def get_header(self, name: str) -> Optional[str]:
#         return self.headers.get(name)
#     for i in range(count):
#         data.append({"id": f"item-{i}", "value": rng.randint(1, 100): f"test-{i}"})
# class ToolHandlerHelper:
# class ToolHandlerHelper:
#     """Test tool handler with call tracking."""
#     def __init__(self, return_value: Any = None):
#         self.return_value = return_value or {"status": "ok"}
#         self.call_count = 0
#         self.call_history: list[dict[str, Any]] = []
# 
#     def __call__(self, params: dict[str, Any]) -> Any:
#         self.call_count += 1
#         self.call_history.append(params)
#         return self.return_value
# 
#     def reset(self):
#     def reset(self):
#         """Reset call tracking."""
#         self.call_count = 0
#         self.call_history = []
#         data.append({"id": f"item-{i}", "value": rng.randint(1, 100): f"test-{i}"})
# # Deterministic Random Utilities
#     for i in range(count):
#         data.append({"id": f"item-{i}", "value": rng.randint(1, 100): f"test-{i}"})
#     return random.Random(seed)
#     for i in range(count):
#         data.append({"id": f"item-{i}", "value": rng.randint(1, 100): f"test-{i}"})
# def generate_test_data(count: int = 10, seed: int = 42) -> list[dict[str, Any]]:
# def generate_test_data(count: int = 10, seed: int = 42) -> list[dict[str, Any]]:
#     """Generate deterministic test data."""
#     rng = get_deterministic_rng(seed)
#     data = []
#     for i in range(count):
#         data.append({"id": f"item-{i}", "value": rng.randint(1, 100): f"test-{i}"})
# 
#     return data


# Checksum Utilities
def compute_test_checksum(data: Any) -> str:
    """Compute SHA-256 checksum for test data."""
    data_str = str(data)
    return hashlib.sha256(data_str.encode("utf-8")).hexdigest()


def verify_test_checksum(data: Any, expected: str) -> bool:
    """Verify test data checksum."""
    actual = compute_test_checksum(data)
    return actual == expected


# Integration Test Helpers
def setup_test_environment() -> dict[str, Any]:
    """
    Setup complete test environment with all MCP components.

    Returns:
        Dictionary with registry, authenticator, authorizer, limiter
    """
    return {
        "registry": create_test_registry(["tool1", "tool2"]),
        "authenticator": MCPAuthenticator(),
        "authorizer": MCPAuthorizer(),
        "limiter": create_test_rate_limiter(),
        "principal": create_test_principal(),
    }


def teardown_test_environment(env: dict[str, Any]) -> None:
    """Teardown test environment and clean up resources."""
    # Reset rate limiter
    if "limiter" in env:
        env["limiter"].reset()

    # Clear registry (if we add a clear method)
    # Currently registry doesn't need explicit cleanup


# Performance Testing Utilities
class PerformanceTimer:
    """Simple timer for performance testing."""

    def __init__(self):
        self.start_time = None
        self.end_time = None

    def start(self):
        """Start timing."""
        import time

        self.start_time = time.time()

    def stop(self):
        """Stop timing."""
        import time

        self.end_time = time.time()

    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0


def benchmark_operation(
    operation: Callable, iterations: int = 100, *args, **kwargs
) -> dict[str, float]:
    """
    Benchmark an operation over multiple iterations.

    Returns:
        Dictionary with min, max, average execution times
    """
    import time

    times = []
    for _ in range(iterations):
        start = time.time()
        operation(*args, **kwargs)
        end = time.time()
        times.append(end - start)

    return {
        "min": min(times),
        "max": max(times),
        "average": sum(times) / len(times),
        "total": sum(times),
    }


# Test Data Validation
def validate_tool_metadata(metadata: dict[str, Any]) -> bool:
    """Validate tool metadata structure."""
    required_fields = ["description"]
    return all(field in metadata for field in required_fields)


def validate_tool_schema(schema: dict[str, Any]) -> bool:
    """Validate tool schema structure."""
    return "type" in schema


def validate_principal(principal: Principal) -> bool:
    """Validate principal structure."""
    return bool(principal.principal_id)


# Offline Mode Utilities
def is_offline_mode() -> bool:
    """Check if running in offline mode (for deterministic tests)."""
    return os.environ.get("OFFLINE_MODE", "").lower() in ("true", "1", "yes") or os.environ.get(
        "MCP_OFFLINE", ""
    ).lower() in ("true", "1", "yes")


def ensure_offline_mode() -> None:
    """Ensure tests run in offline mode."""
    os.environ["OFFLINE_MODE"] = "true"
    os.environ["MCP_OFFLINE"] = "true"


# Error Testing Utilities
def assert_raises_mcp_error(
    func: Callable, error_type: type, error_code: Optional[str] = None, *args, **kwargs
):
    """
    Assert that function raises specific MCP error type.

    Args:
        func: Function to call
        error_type: Expected error type
        error_code: Expected error code (optional)
        *args: Arguments to pass to func
        **kwargs: Keyword arguments to pass to func
    """
    try:
        func(*args, **kwargs)
        raise AssertionError(f"Expected {error_type.__name__} to be raised")
    except error_type as e:
        if error_code:
            assert_error_code(e, error_code)
        return e
    except Exception as e:
        raise AssertionError(f"Expected {error_type.__name__}, got {type(e).__name__}: {e}")


# Test Cleanup Utilities
def cleanup_test_files(directory: str, pattern: str = "test_*.tmp"):
    """Clean up temporary test files."""
    import glob

    if not os.path.exists(directory):
        return

    files = glob.glob(os.path.join(directory, pattern))
    for file in files:
        try:
            os.remove(file)
        except FileNotFoundError:
            # Benign race: file was already deleted by another process/thread.
            pass
        except OSError as e:
            logger.warning("Failed to remove test file '%s': %s", file, e)


# Logging Utilities for Tests
def capture_log_output(func: Callable, *args, **kwargs) -> tuple:
    """
    Capture log output from function execution.

    Returns:
        Tuple of (result, log_records)
    """
    from io import StringIO

    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    logger = logging.getLogger()
    logger.addHandler(handler)

    try:
        result = func(*args, **kwargs)
        log_output = log_stream.getvalue()
        return result, log_output
    finally:
        logger.removeHandler(handler)
