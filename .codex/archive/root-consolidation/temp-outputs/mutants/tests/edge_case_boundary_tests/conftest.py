"""
Pytest configuration and fixtures for edge case and boundary testing.

Provides shared fixtures, parametrization, and test utilities for Phase 7A Wave 3 Lane 3.1.
"""

from unittest.mock import MagicMock

import pytest

# ============================================================================
# AUTHENTICATION FIXTURES
# ============================================================================


@pytest.fixture
def valid_token():
    """Valid JWT token fixture."""
    return "******"


@pytest.fixture
def expired_token():
    """Expired JWT token fixture."""
    return "eyJleHAiOiIxNjAwMDAwMDAwIn0"


@pytest.fixture
def malformed_token():
    """Malformed JWT token fixture."""
    return "not.a.valid.token.at.all"


@pytest.fixture
def mock_mfa_manager():
    """Mock MFA manager fixture."""
    manager = MagicMock()
    manager.verify_mfa_code.return_value = True
    manager.generate_backup_codes.return_value = ["code1", "code2", "code3"]
    manager.verify_backup_code.return_value = True
    return manager


@pytest.fixture
def mock_oauth_provider():
    """Mock OAuth provider fixture."""
    provider = MagicMock()
    provider.exchange_code_for_token.return_value = {
        "access_token": "token",
        "refresh_token": "refresh",
    }
    provider.validate_state.return_value = True
    provider.get_user_info.return_value = {"id": "123", "email": "user@example.com"}
    return provider


# ============================================================================
# AUTHORIZATION FIXTURES
# ============================================================================


@pytest.fixture
def mock_rbac_engine():
    """Mock RBAC authorization engine."""
    engine = MagicMock()
    engine.has_permission.return_value = True
    engine.get_roles.return_value = ["user", "admin"]
    engine.check_role_inheritance.return_value = True
    return engine


@pytest.fixture
def mock_abac_engine():
    """Mock ABAC authorization engine."""
    engine = MagicMock()
    engine.evaluate_policy.return_value = True
    engine.get_attributes.return_value = {"department": "sales", "level": 3}
    engine.check_attribute_conflict.return_value = False
    return engine


# ============================================================================
# DATA VALIDATION FIXTURES
# ============================================================================


@pytest.fixture
def injection_payloads():
    """Common injection attack payloads for boundary testing."""
    return {
        "sql_injection": [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "1' UNION SELECT * FROM users --",
            "admin'--",
            "1' AND 1=1 --",
        ],
        "xss_injection": [
            "<script>alert('xss')</script>",
            "<img src=x onerror='alert(1)'>",
            "javascript:alert('xss')",
            "<svg onload='alert(1)'>",
            "<iframe src='javascript:alert(1)'>",
        ],
        "command_injection": ["; ls -la", "| cat /etc/passwd", "&& whoami", "`id`", "$(whoami)"],
    }


@pytest.fixture
def boundary_values():
    """Common boundary values for testing."""
    return {
        "integers": {
            "min_int": -2147483648,
            "max_int": 2147483647,
            "zero": 0,
            "one": 1,
            "negative_one": -1,
        },
        "strings": {
            "empty": "",
            "whitespace": "   ",
            "newline": "\n",
            "very_long": "x" * 1000000,
            "unicode": "🔐😀中文",
            "special_chars": "!@#$%^&*()",
        },
    }


# ============================================================================
# CRYPTOGRAPHY FIXTURES
# ============================================================================


@pytest.fixture
def key_management_mock():
    """Mock key management system."""
    manager = MagicMock()
    manager.generate_key.return_value = b"0" * 32
    manager.get_key.return_value = b"0" * 32
    manager.rotate_key.return_value = True
    return manager


# ============================================================================
# STATE MANAGEMENT FIXTURES
# ============================================================================


@pytest.fixture
def state_machine_mock():
    """Mock state machine for testing state transitions."""
    fsm = MagicMock()
    fsm.current_state = "idle"
    fsm.valid_states = ["idle", "running", "paused", "completed", "error"]
    fsm.transition.return_value = True
    fsm.rollback.return_value = True
    return fsm


# ============================================================================
# API/NETWORK FIXTURES
# ============================================================================


@pytest.fixture
def http_client_mock():
    """Mock HTTP client for testing network scenarios."""
    client = MagicMock()
    client.get.return_value = MagicMock(status_code=200, json=lambda: {"result": "ok"})
    client.post.return_value = MagicMock(status_code=201, json=lambda: {"id": "123"})
    return client


# ============================================================================
# PARAMETRIZATION FIXTURES
# ============================================================================


@pytest.fixture(
    params=[
        {"status": 200, "data": {"result": "ok"}},
        {"status": 201, "data": {"id": "123"}},
        {"status": 204, "data": None},
        {"status": 400, "error": "Invalid request"},
        {"status": 401, "error": "Unauthorized"},
        {"status": 403, "error": "Forbidden"},
        {"status": 404, "error": "Not found"},
        {"status": 500, "error": "Internal server error"},
    ]
)
def http_status_codes(request):
    """Parametrized HTTP status codes for boundary testing."""
    return request.param


# ============================================================================
# UTILITY FUNCTIONS FOR TESTS
# ============================================================================


def create_mock_request(method="GET", path="/", headers=None, body=None):
    """Create a mock HTTP request."""
    request = MagicMock()
    request.method = method
    request.path = path
    request.headers = headers or {}
    request.body = body
    return request


def create_mock_response(status_code=200, data=None):
    """Create a mock HTTP response."""
    response = MagicMock()
    response.status_code = status_code
    response.data = data
    return response
