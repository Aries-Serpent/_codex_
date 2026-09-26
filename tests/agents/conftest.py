"""
Agent Test Harness Fixtures and Configuration
==============================================

Provides comprehensive pytest fixtures for agent testing:
- Agent initialization and mocking
- Database setup and teardown
- Common test helpers
- Agent context builders
"""

import json
import os
import sqlite3
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Generator, List
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add agents module to path
AGENTS_MODULE_PATH = Path(__file__).parent.parent.parent / "agents"
if str(AGENTS_MODULE_PATH) not in sys.path:
    sys.path.insert(0, str(AGENTS_MODULE_PATH))


# ============================================================================
# DATABASE FIXTURES
# ============================================================================


@pytest.fixture
def temp_db() -> Generator[str, None, None]:
    """Provide a temporary in-memory SQLite database."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        # Initialize with schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Basic schema for agent testing
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS agent_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                agent_type TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                result TEXT,
                error TEXT,
                metadata TEXT
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS agent_states (
                agent_id TEXT PRIMARY KEY,
                state TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS test_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                agent_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data TEXT
            )
            """
        )

        conn.commit()
        conn.close()

        yield db_path

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


@pytest.fixture
def db_connection(temp_db: str) -> Generator[sqlite3.Connection, None, None]:
    """Provide a database connection for tests."""
    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# ============================================================================
# MOCK FIXTURES
# ============================================================================


@pytest.fixture
def mock_env() -> Generator[Dict[str, str], None, None]:
    """Mock environment variables for agent testing."""
    env = {
        "COPILOT_AGENT_ID": "test-agent-001",
        "COPILOT_SESSION_ID": "test-session-001",
        "GITHUB_TOKEN": "ghp_test_token_123456789",
        "GITHUB_OWNER": "test-owner",
        "GITHUB_REPO": "test-repo",
        "LOG_LEVEL": "DEBUG",
        "AGENT_MODE": "test",
    }

    with patch.dict(os.environ, env, clear=False):
        yield env


@pytest.fixture
def mock_github_api() -> Mock:
    """Mock GitHub API client."""
    mock_api = MagicMock()
    mock_api.get_user.return_value = {"login": "test-user", "id": 123}
    mock_api.list_pull_requests.return_value = []
    mock_api.get_pull_request.return_value = {
        "number": 1,
        "title": "Test PR",
        "body": "Test PR description",
        "state": "open",
    }
    mock_api.list_issues.return_value = []
    mock_api.get_issue.return_value = {
        "number": 1,
        "title": "Test Issue",
        "body": "Test issue description",
        "state": "open",
    }
    return mock_api


@pytest.fixture
def mock_logger() -> Mock:
    """Mock logger for agent tests."""
    logger = MagicMock()
    logger.debug = MagicMock()
    logger.info = MagicMock()
    logger.warning = MagicMock()
    logger.error = MagicMock()
    logger.critical = MagicMock()
    return logger


# ============================================================================
# AGENT CONTEXT BUILDERS
# ============================================================================


@pytest.fixture
def agent_context_builder():
    """Builder for creating agent execution contexts."""

    class AgentContextBuilder:
        def __init__(self):
            self.context = {
                "agent_id": "test-agent",
                "agent_type": "test",
                "session_id": "test-session",
                "user_id": "test-user",
                "timestamp": "2024-01-01T00:00:00Z",
                "metadata": {},
                "inputs": {},
                "config": {},
            }

        def with_agent_id(self, agent_id: str) -> "AgentContextBuilder":
            self.context["agent_id"] = agent_id
            return self

        def with_agent_type(self, agent_type: str) -> "AgentContextBuilder":
            self.context["agent_type"] = agent_type
            return self

        def with_session_id(self, session_id: str) -> "AgentContextBuilder":
            self.context["session_id"] = session_id
            return self

        def with_input(self, key: str, value: Any) -> "AgentContextBuilder":
            self.context["inputs"][key] = value
            return self

        def with_config(self, key: str, value: Any) -> "AgentContextBuilder":
            self.context["config"][key] = value
            return self

        def with_metadata(self, key: str, value: Any) -> "AgentContextBuilder":
            self.context["metadata"][key] = value
            return self

        def build(self) -> Dict[str, Any]:
            return self.context.copy()

    return AgentContextBuilder()


@pytest.fixture
def execution_context_builder():
    """Builder for execution test contexts."""

    class ExecutionContextBuilder:
        def __init__(self):
            self.execution = {
                "status": "pending",
                "started_at": None,
                "completed_at": None,
                "duration_ms": 0,
                "result": None,
                "error": None,
                "logs": [],
                "metrics": {},
            }

        def with_status(self, status: str) -> "ExecutionContextBuilder":
            self.execution["status"] = status
            return self

        def with_result(self, result: Any) -> "ExecutionContextBuilder":
            self.execution["result"] = result
            return self

        def with_error(self, error: str) -> "ExecutionContextBuilder":
            self.execution["error"] = error
            return self

        def with_log(self, log: str) -> "ExecutionContextBuilder":
            self.execution["logs"].append(log)
            return self

        def with_metric(self, key: str, value: Any) -> "ExecutionContextBuilder":
            self.execution["metrics"][key] = value
            return self

        def build(self) -> Dict[str, Any]:
            return self.execution.copy()

    return ExecutionContextBuilder()


# ============================================================================
# SAMPLE DATA FIXTURES
# ============================================================================


@pytest.fixture
def sample_agent_config() -> Dict[str, Any]:
    """Provide sample agent configuration."""
    return {
        "id": "test-agent-001",
        "name": "Test Agent",
        "version": "1.0.0",
        "type": "test",
        "status": "active",
        "maturity": "beta",
        "autonomy": "E",
        "category": "testing",
        "capabilities": ["test_execution", "error_handling"],
        "config": {
            "timeout": 30,
            "retries": 3,
            "log_level": "DEBUG",
            "enable_metrics": True,
        },
    }


@pytest.fixture
def sample_test_inputs() -> Dict[str, Any]:
    """Provide sample test inputs for agents."""
    return {
        "simple": {"input": "test"},
        "complex": {
            "data": [1, 2, 3, 4, 5],
            "options": {"verbose": True, "filter": "active"},
        },
        "edge_case": {
            "empty_list": [],
            "null_value": None,
            "large_string": "x" * 10000,
        },
        "error_case": {
            "invalid_type": object(),
            "circular_ref": None,  # Will be set to self in test
        },
    }


@pytest.fixture
def sample_agent_outputs() -> Dict[str, Any]:
    """Provide sample agent outputs for validation."""
    return {
        "success": {
            "status": "success",
            "data": {"result": "test result"},
            "metadata": {"execution_time_ms": 100},
        },
        "partial": {
            "status": "partial",
            "data": {"completed": 5, "failed": 2},
            "warnings": ["Some items could not be processed"],
        },
        "error": {
            "status": "error",
            "error": "Test error message",
            "code": "TEST_ERROR_001",
        },
    }


# ============================================================================
# COMMON TEST HELPERS
# ============================================================================


@pytest.fixture
def assert_valid_json():
    """Helper to validate JSON outputs."""

    def _assert_valid_json(data: str) -> Dict[str, Any]:
        try:
            parsed = json.loads(data)
            assert isinstance(parsed, (dict, list)), "JSON must be object or array"
            return parsed
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON: {e}")

    return _assert_valid_json


@pytest.fixture
def assert_valid_agent_output():
    """Helper to validate agent output format."""

    def _assert_valid_output(output: Dict[str, Any]) -> None:
        # Required fields
        assert "status" in output, "Output must have 'status' field"
        assert output["status"] in [
            "success",
            "partial",
            "error",
        ], "Status must be success, partial, or error"

        # Status-specific validation
        if output["status"] == "error":
            assert "error" in output, "Error status must have 'error' field"
        elif output["status"] in ["success", "partial"]:
            assert "data" in output, f"{output['status']} status must have 'data' field"

    return _assert_valid_output


@pytest.fixture
def measure_execution_time():
    """Helper to measure and assert execution time."""
    import time

    class ExecutionTimer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.duration_ms = 0

        def __enter__(self):
            self.start_time = time.time()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.end_time = time.time()
            self.duration_ms = (self.end_time - self.start_time) * 1000

        def assert_under(self, max_ms: float) -> None:
            assert (
                self.duration_ms < max_ms
            ), f"Execution took {self.duration_ms}ms, expected < {max_ms}ms"

        def assert_over(self, min_ms: float) -> None:
            assert (
                self.duration_ms >= min_ms
            ), f"Execution took {self.duration_ms}ms, expected >= {min_ms}ms"

    return ExecutionTimer


@pytest.fixture
def assert_callback_called():
    """Helper to verify callbacks are called with expected args."""

    def _assert_callback(mock_func, expected_args: List[Any], expected_kwargs: Dict[str, Any] = None) -> None:
        if expected_kwargs is None:
            expected_kwargs = {}

        mock_func.assert_called_once_with(*expected_args, **expected_kwargs)

    return _assert_callback


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers",
        "agent: mark test as an agent test",
    )
    config.addinivalue_line(
        "markers",
        "integration: mark test as an integration test",
    )
    config.addinivalue_line(
        "markers",
        "control_flow: mark test as control flow test",
    )
    config.addinivalue_line(
        "markers",
        "quality: mark test as quality test",
    )
    config.addinivalue_line(
        "markers",
        "regression: mark test as regression test",
    )
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow",
    )
    config.addinivalue_line(
        "markers",
        "requires_auth: mark test as requiring authentication",
    )


# ============================================================================
# SCOPE AND CLEANUP
# ============================================================================


@pytest.fixture(scope="session")
def test_artifacts_dir() -> Generator[Path, None, None]:
    """Provide a directory for test artifacts."""
    artifacts_dir = Path(tempfile.mkdtemp(prefix="agent_tests_"))
    try:
        yield artifacts_dir
    finally:
        import shutil

        shutil.rmtree(artifacts_dir, ignore_errors=True)
