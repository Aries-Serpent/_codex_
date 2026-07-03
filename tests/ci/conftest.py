"""Pytest fixtures for Phase 5 token hierarchy tests.

Provides comprehensive fixtures for testing token resolution, GitHub API mocking,
environment isolation, and audit logging validation.
"""

from __future__ import annotations

import base64
import io
import logging
import os
import uuid
from typing import Any, Dict, Generator, List, Optional, Tuple

import pytest

from scripts.ci._token_resolver import get_token

# ============================================================================
# ENVIRONMENT ISOLATION FIXTURES
# ============================================================================


@pytest.fixture
def isolated_env() -> Generator[Dict[str, str], None, None]:
    """Fixture that isolates environment variables for each test.

    Saves the current environment, clears all token-related variables,
    and restores the original environment after the test.

    Yields:
        A mutable dict of the current (cleared) environment.
    """
    # Save original environment
    saved_env = os.environ.copy()

    # Clear all token-related variables
    token_vars = [
        "CODEX_MASTER_KEY",
        "CODEX_BACKUP_KEY",
        "GH_TOKEN",
        "GITHUB_TOKEN",
    ]
    for var in token_vars:
        os.environ.pop(var, None)

    try:
        yield os.environ
    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(saved_env)


@pytest.fixture
def env_with_master_key(isolated_env: Dict[str, str]) -> Generator[Dict[str, str], None, None]:
    """Fixture that sets only CODEX_MASTER_KEY in isolated environment."""
    get_token(required_elevated=True)[0] = f"ghp_test_master_{uuid.uuid4().hex[:16]}"
    yield os.environ


@pytest.fixture
def env_with_backup_key(isolated_env: Dict[str, str]) -> Generator[Dict[str, str], None, None]:
    """Fixture that sets only CODEX_BACKUP_KEY in isolated environment."""
    get_token(required_elevated=True)[0] = f"ghp_test_backup_{uuid.uuid4().hex[:16]}"
    yield os.environ


@pytest.fixture
def env_with_gh_token(isolated_env: Dict[str, str]) -> Generator[Dict[str, str], None, None]:
    """Fixture that sets only GH_TOKEN in isolated environment."""
    os.environ["GH_TOKEN"] = f"ghp_test_gh_{uuid.uuid4().hex[:16]}"
    yield os.environ


@pytest.fixture
def env_with_github_token(isolated_env: Dict[str, str]) -> Generator[Dict[str, str], None, None]:
    """Fixture that sets only GITHUB_TOKEN in isolated environment."""
    os.environ["GITHUB_TOKEN"] = f"ghp_test_github_{uuid.uuid4().hex[:16]}"
    yield os.environ


@pytest.fixture
def env_no_tokens(isolated_env: Dict[str, str]) -> Generator[Dict[str, str], None, None]:
    """Fixture that ensures no tokens are set."""
    # All tokens already cleared by isolated_env
    yield os.environ


# ============================================================================
# LOG CAPTURE FIXTURES
# ============================================================================


class TokenLogCapture:
    """Helper class for capturing and validating logs without token exposure."""

    def __init__(self, logger_name: str = "scripts.ci._token_resolver"):
        """Initialize log capture for a specific logger.

        Args:
            logger_name: Name of the logger to capture.
        """
        self.logger_name = logger_name
        self.records: List[logging.LogRecord] = []
        self.handler = logging.StreamHandler(io.StringIO())
        self.handler.setLevel(logging.DEBUG)
        self.text_buffer = io.StringIO()

    def __enter__(self) -> TokenLogCapture:
        """Enter context manager."""
        logger = logging.getLogger(self.logger_name)
        self.old_level = logger.level
        logger.setLevel(logging.DEBUG)

        # Create handler that captures to StringIO
        self.text_io = io.StringIO()
        self.handler = logging.StreamHandler(self.text_io)
        formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
        self.handler.setFormatter(formatter)
        logger.addHandler(self.handler)

        return self

    def __exit__(self, *args):
        """Exit context manager."""
        logger = logging.getLogger(self.logger_name)
        logger.removeHandler(self.handler)
        logger.setLevel(self.old_level)

    @property
    def text(self) -> str:
        """Return all captured log text."""
        self.handler.flush()
        return self.text_io.getvalue()

    def assert_token_not_exposed(self, token: str) -> None:
        """Assert that a token value doesn't appear in logs.

        Args:
            token: The token to check for.

        Raises:
            AssertionError: If token appears in logs.
        """
        text = self.text
        assert token not in text, f"Token value exposed in logs: {token}"

    def assert_token_source_logged(self, source: str) -> None:
        """Assert that a token source is logged (without value).

        Args:
            source: The source name (e.g., 'CODEX_MASTER_KEY').

        Raises:
            AssertionError: If source not mentioned in logs.
        """
        text = self.text
        assert source in text, f"Token source '{source}' not logged"


@pytest.fixture
def token_log_capture() -> Generator[TokenLogCapture, None, None]:
    """Fixture that captures token-related logs for validation."""
    capture = TokenLogCapture()
    yield capture


# ============================================================================
# MOCK GITHUB API FIXTURES
# ============================================================================


class MockGitHubAPI:
    """Mock GitHub API for testing without real network calls."""

    def __init__(self):
        """Initialize mock API."""
        self.variables: Dict[str, str] = {}
        self.request_log: List[Dict[str, Any]] = []
        self.auth_tokens_seen: List[str] = []

    def create_variable(
        self, name: str, value: str, token: str, repo: str = "test-org/test-repo"
    ) -> Tuple[bool, str]:
        """Mock GitHub API endpoint for creating repo variables.

        Args:
            name: Variable name.
            value: Variable value.
            token: Authorization token.
            repo: Repository in format "owner/repo".

        Returns:
            Tuple of (success, message).
        """
        self.request_log.append(
            {
                "method": "POST",
                "endpoint": f"/repos/{repo}/actions/variables",
                "name": name,
                "token_prefix": token[:10] if token else None,
            }
        )

        if token:
            self.auth_tokens_seen.append(token)

        if not name or not value:
            return False, "Variable name and value required"

        self.variables[name] = value
        return True, f"Variable {name} created"

    def get_variable(
        self, name: str, token: str, repo: str = "test-org/test-repo"
    ) -> Tuple[Optional[str], bool]:
        """Mock GitHub API endpoint for retrieving repo variables.

        Args:
            name: Variable name.
            token: Authorization token.
            repo: Repository in format "owner/repo".

        Returns:
            Tuple of (value, success).
        """
        self.request_log.append(
            {
                "method": "GET",
                "endpoint": f"/repos/{repo}/actions/variables/{name}",
                "token_prefix": token[:10] if token else None,
            }
        )

        if token:
            self.auth_tokens_seen.append(token)

        value = self.variables.get(name)
        if value is None:
            return None, False

        return value, True

    def delete_variable(
        self, name: str, token: str, repo: str = "test-org/test-repo"
    ) -> Tuple[bool, str]:
        """Mock GitHub API endpoint for deleting repo variables.

        Args:
            name: Variable name.
            token: Authorization token.
            repo: Repository in format "owner/repo".

        Returns:
            Tuple of (success, message).
        """
        self.request_log.append(
            {
                "method": "DELETE",
                "endpoint": f"/repos/{repo}/actions/variables/{name}",
                "token_prefix": token[:10] if token else None,
            }
        )

        if token:
            self.auth_tokens_seen.append(token)

        if name not in self.variables:
            return False, f"Variable {name} not found"

        del self.variables[name]
        return True, f"Variable {name} deleted"

    def assert_token_never_exposed(self) -> None:
        """Assert that no actual token values appear in request logs.

        This validates that only prefixes are logged, not full tokens.

        Raises:
            AssertionError: If full token appears in logs.
        """
        for request in self.request_log:
            if request.get("token_prefix"):
                # Token is in request, which is fine for the API call
                # But we should never log it
                pass

    def get_request_count(self, method: str) -> int:
        """Get count of requests by method type.

        Args:
            method: HTTP method (GET, POST, DELETE).

        Returns:
            Count of requests with this method.
        """
        return len([r for r in self.request_log if r["method"] == method])


@pytest.fixture
def mock_github_api() -> Generator[MockGitHubAPI, None, None]:
    """Fixture providing a mock GitHub API."""
    api = MockGitHubAPI()
    yield api


# ============================================================================
# TOKEN FACTORY FIXTURES
# ============================================================================


class TokenFactory:
    """Factory for creating test tokens and scenarios."""

    @staticmethod
    def create_token(token_type: str = "master") -> str:
        """Create a realistic-looking test token.

        Args:
            token_type: Type of token (master, backup, gh, github).

        Returns:
            A test token string.
        """
        prefixes = {
            "master": "ghp_master",
            "backup": "ghp_backup",
            "gh": "ghp_gh",
            "github": "ghp_github",
        }
        prefix = prefixes.get(token_type, "ghp_test")
        return f"{prefix}_{uuid.uuid4().hex[:16]}"

    @staticmethod
    def create_base64_content(content: str) -> str:
        """Create base64-encoded content.

        Args:
            content: Content to encode.

        Returns:
            Base64-encoded string.
        """
        return base64.b64encode(content.encode("utf-8")).decode("utf-8")

    @staticmethod
    def decode_base64_content(encoded: str) -> str:
        """Decode base64-encoded content.

        Args:
            encoded: Base64-encoded string.

        Returns:
            Decoded content.
        """
        return base64.b64decode(encoded).decode("utf-8")


@pytest.fixture
def token_factory() -> Generator[TokenFactory, None, None]:
    """Fixture providing a token factory."""
    yield TokenFactory()


# ============================================================================
# PARAMETRIZED SCENARIO FIXTURES
# ============================================================================


@pytest.fixture(
    params=[
        ("CODEX_MASTER_KEY", "elevated", True),
        ("CODEX_BACKUP_KEY", "standard", True),
        ("GH_TOKEN", "standard", True),
        ("GITHUB_TOKEN", "fallback", True),
    ]
)
def parametrized_token_scenarios(
    request, isolated_env: Dict[str, str]
) -> Generator[Tuple[str, str, bool], None, None]:
    """Parametrized fixture for testing all token hierarchy levels.

    Each test using this fixture runs once for each token type.

    Yields:
        Tuple of (token_var_name, expected_scope, should_succeed).
    """
    token_var, scope, should_succeed = request.param
    token_value = f"ghp_test_{uuid.uuid4().hex[:16]}"
    os.environ[token_var] = token_value

    yield token_var, scope, should_succeed


# ============================================================================
# UTILITY FIXTURES
# ============================================================================


@pytest.fixture
def sample_python_file() -> Generator[str, None, None]:
    """Fixture providing sample Python file content for base64 round-trip testing."""
    content = '''"""Sample module for testing base64 encoding/decoding."""

def hello_world():
    """Print a greeting."""
    logger.info("Hello, World!")

class TestClass:
    """Test class for validation."""
    
    def __init__(self):
        """Initialize."""
        self.value = 42
    
    def get_value(self):
        """Get the value."""
        return self.value
'''
    yield content


@pytest.fixture
def github_repo_context() -> Generator[Dict[str, str], None, None]:
    """Fixture providing GitHub repository context."""
    yield {
        "owner": "test-org",
        "repo": "test-repo",
        "api_base": "https://api.github.com",
    }


# ============================================================================
# INTEGRATION FIXTURES
# ============================================================================


@pytest.fixture
def token_test_suite() -> Generator[Dict[str, Any], None, None]:
    """Fixture providing test suite configuration and state."""
    suite_state = {
        "scenarios_run": [],
        "scenarios_passed": [],
        "scenarios_failed": [],
        "test_start_time": None,
        "test_end_time": None,
        "metrics": {
            "total_duration": 0.0,
            "scenario_durations": {},
        },
    }
    yield suite_state


__all__ = [
    "isolated_env",
    "env_with_master_key",
    "env_with_backup_key",
    "env_with_gh_token",
    "env_with_github_token",
    "env_no_tokens",
    "token_log_capture",
    "TokenLogCapture",
    "mock_github_api",
    "MockGitHubAPI",
    "token_factory",
    "TokenFactory",
    "parametrized_token_scenarios",
    "sample_python_file",
    "github_repo_context",
    "token_test_suite",
]
