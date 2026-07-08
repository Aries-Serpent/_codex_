"""
Comprehensive Edge Case Tests for Phase 7A WAVE 2

Tests for edge cases and boundary conditions.

Categories:
- Very large payloads
- Empty request bodies
- Null values in optional fields
- Unicode/special characters
- Concurrent requests
- Rapid sequential requests # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
- Timeout handling
- Resource exhaustion
"""

import concurrent.futures

import pytest

pytest.importorskip("fastapi")
from fastapi import FastAPI
from fastapi.testclient import TestClient

from codex.api.auth_routes import create_auth_router
from codex.auth.authenticator import Authenticator
from codex.auth.token_manager import TokenManager
from codex.auth.user_store import UserStore

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def auth_components():
    """Create fresh authentication components."""
    store = UserStore()
    tokens = TokenManager(secret_key="test-secret-phase7a")
    auth = Authenticator(user_store=store, token_manager=tokens)
    return store, tokens, auth


@pytest.fixture
def test_client(auth_components):
    """Create FastAPI test client with auth router."""
    _, _, auth = auth_components
    app = FastAPI()
    router = create_auth_router(authenticator=auth)
    app.include_router(router)
    return TestClient(app)


# ---------------------------------------------------------------------------
# Large Payload Tests
# ---------------------------------------------------------------------------


class TestLargePayloads:
    """Tests for handling large payloads."""

    def test_very_large_username(self, test_client):
        """Very large username should be handled."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "a" * 10000,
                "email": "large@example.com",
                "password": "SecurePass123!",
            },
        )
        # Should reject or handle gracefully
        assert response.status_code in [400, 413, 422]

    def test_very_large_password(self, test_client):
        """Very large password."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "largepass",
                "email": "largepass@example.com",
                "password": "P" + "a" * 10000 + "1!",
            },
        )
        assert response.status_code in [201, 400, 413, 422]

    def test_very_long_email(self, test_client):
        """Very long email address."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "longemail",
                "email": "a" * 1000 + "@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code in [400, 413, 422]

    def test_large_json_payload(self, test_client):
        """Large JSON payload."""
        roles = [f"role{i}" for i in range(1000)]
        response = test_client.post(
            "/auth/register",
            json={
                "username": "manyrolesuser",
                "email": "roles@example.com",
                "password": "SecurePass123!",
                "roles": roles,
            },
        )
        assert response.status_code in [201, 400, 413, 422]

    def test_deeply_nested_payload(self, test_client):
        """Deeply nested JSON payload."""
        nested = {"key": "value"}
        for _ in range(100):
            nested = {"nested": nested}
        response = test_client.post(
            "/auth/register",
            json={
                "username": "deepnest",
                "email": "nested@example.com",
                "password": "SecurePass123!",
                "metadata": nested,
            },
        )
        assert response.status_code in [201, 400, 413, 422]

    def test_many_extra_fields(self, test_client):
        """Many extra fields in payload."""
        payload = {
            "username": "manyfields",
            "email": "manyfields@example.com",
            "password": "SecurePass123!",
        }
        # Add 1000 extra fields
        for i in range(1000):
            payload[f"extra_{i}"] = f"value_{i}"
        response = test_client.post("/auth/register", json=payload)
        assert response.status_code in [201, 400, 413, 422]


# ---------------------------------------------------------------------------
# Empty/Null Request Tests
# ---------------------------------------------------------------------------


class TestEmptyAndNullRequests:
    """Tests for empty and null requests."""

    def test_empty_json_object(self, test_client):
        """Empty JSON object should fail validation."""
        response = test_client.post("/auth/register", json={})
        assert response.status_code == 422, "Response must not be empty"

    def test_all_null_fields(self, test_client):
        """All null fields should fail."""
        response = test_client.post(
            "/auth/register", json={"username": None, "email": None, "password": None}
        )
        assert response.status_code == 422, "Response must not be empty"

    def test_null_optional_field(self, test_client):
        """Null optional field should be handled."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "test",
                "email": "test@example.com",
                "password": "SecurePass123!",
                "roles": None,
            },
        )
        # Should accept or reject gracefully
        assert response.status_code in [201, 400, 422]

    def test_empty_array_roles(self, test_client):
        """Empty array for roles."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "emptyroles",
                "email": "empty@example.com",
                "password": "SecurePass123!",
                "roles": [],
            },
        )
        # Should accept or reject
        assert response.status_code in [201, 400, 422]

    def test_empty_string_fields(self, test_client):
        """Empty string fields."""
        response = test_client.post(
            "/auth/register", json={"username": "", "email": "", "password": ""}
        )
        assert response.status_code in [400, 422]


# ---------------------------------------------------------------------------
# Unicode and Special Characters Tests
# ---------------------------------------------------------------------------


class TestUnicodeAndSpecialCharacters:
    """Tests for unicode and special character handling."""

    def test_username_with_emoji(self, test_client):
        """Username with emoji characters."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "user😀😀😀",
                "email": "emoji@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code in [201, 400, 422]

    def test_username_with_cyrillic(self, test_client):
        """Username with Cyrillic characters."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "пользователь",
                "email": "cyrillic@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code in [201, 400, 422]

    def test_username_with_chinese(self, test_client):
        """Username with Chinese characters."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "用户名",
                "email": "chinese@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code in [201, 400, 422]

    def test_username_with_arabic(self, test_client):
        """Username with Arabic characters."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "المستخدم",
                "email": "arabic@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code in [201, 400, 422]

    def test_username_with_mixed_scripts(self, test_client):
        """Username with mixed scripts."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "user用户пользователь",
                "email": "mixed@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code in [201, 400, 422]

    def test_password_with_emoji(self, test_client):
        """Password with emoji."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "emojipass",
                "email": "emojipass@example.com",
                "password": "Pass😀123!",
            },
        )
        assert response.status_code in [201, 400, 422]

    def test_email_with_unicode(self, test_client):
        """Email with unicode (IDN)."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "unicodeemail",
                "email": "user@例え.jp",
                "password": "SecurePass123!",
            },
        )
        # Most systems don't support unicode in email
        assert response.status_code in [201, 400, 422]

    def test_username_with_combining_marks(self, test_client):
        """Username with combining diacritical marks."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "e\u0301\u0302\u0303",  # e with multiple combining marks
                "email": "combining@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code in [201, 400, 422]

    def test_zero_width_characters(self, test_client):
        """Zero-width characters in username."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "user\u200b\u200c\u200d",  # Zero-width space, joiner, non-joiner
                "email": "zerowidth@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code in [201, 400, 422]


# ---------------------------------------------------------------------------
# Concurrent Request Tests
# ---------------------------------------------------------------------------


class TestConcurrentRequests:
    """Tests for handling concurrent requests."""

    def test_concurrent_registrations_same_user(self, test_client):
        """Concurrent registration attempts for same user."""

        def register_user():
            return test_client.post(
                "/auth/register",
                json={
                    "username": "concurrent",
                    "email": f"concurrent{hash(id())}@example.com",
                    "password": "SecurePass123!",
                },
            )

        # Make multiple concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(register_user) for _ in range(5)]
            results = [f.result() for f in futures]

        # At least one should succeed, others might fail with conflict
        status_codes = [r.status_code for r in results]
        assert any(code == 201 for code in status_codes), "code is not valid"
        # Others should be 400 (conflict) or 201 (if emails differ)
        assert all(code in [201, 400] for code in status_codes)

    def test_concurrent_logins(self, test_client):
        """Concurrent login attempts."""
        # Register a user first
        test_client.post(
            "/auth/register",
            json={
                "username": "conclogin",
                "email": "conclogin@example.com",
                "password": "SecurePass123!",
            },
        )

        def login_user():
            return test_client.post(
                "/auth/login", json={"username": "conclogin", "password": "SecurePass123!"}
            )

        # Make multiple concurrent login requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(login_user) for _ in range(5)]
            results = [f.result() for f in futures]

        # All should succeed
        status_codes = [r.status_code for r in results]
        assert all(code == 200 for code in status_codes), "code is not valid"

    def test_concurrent_mixed_operations(self, test_client):
        """Concurrent mixed operations (register, login, etc)."""

        def operation(op_type):
            if op_type == "register":
                return test_client.post(
                    "/auth/register",
                    json={
                        "username": f"mixed{op_type}",
                        "email": f"mixed{op_type}{hash(id())}@example.com",
                        "password": "SecurePass123!",
                    },
                )
            else:  # login
                return test_client.post(
                    "/auth/login", json={"username": "nonexistent", "password": "wrong"}
                )

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(operation, "register"),
                executor.submit(operation, "login"),
                executor.submit(operation, "register"),
                executor.submit(operation, "login"),
                executor.submit(operation, "register"),
            ]
            results = [f.result() for f in futures]

        # All should complete without errors
        status_codes = [r.status_code for r in results]
        assert all(code in [200, 201, 400] for code in status_codes)


# ---------------------------------------------------------------------------
# Rapid Sequential Request Tests
# ---------------------------------------------------------------------------


class TestRapidSequentialRequests:
    """Tests for rapid sequential requests."""

    def test_many_rapid_registrations(self, test_client):
        """Many rapid registration requests."""
        responses = []
        for i in range(20):
            response = test_client.post(
                "/auth/register",
                json={
                    "username": f"rapid{i}",
                    "email": f"rapid{i}@example.com",
                    "password": "SecurePass123!",
                },
            )
            responses.append(response)

        # Most should succeed
        success_count = sum(1 for r in responses if r.status_code == 201)
        assert success_count >= 15, "success_count must be positive"

    def test_many_rapid_logins(self, test_client):
        """Many rapid login attempts."""
        # Register a user
        test_client.post(
            "/auth/register",
            json={
                "username": "rapidlogin",
                "email": "rapidlogin@example.com",
                "password": "SecurePass123!",
            },
        )

        # Make many rapid logins
        responses = []
        for _ in range(20):
            response = test_client.post(
                "/auth/login", json={"username": "rapidlogin", "password": "SecurePass123!"}
            )
            responses.append(response)

        # Most should succeed
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count >= 15, "success_count must be positive"

    def test_rapid_invalid_requests(self, test_client):
        """Rapid invalid requests."""
        responses = []
        for i in range(20):
            response = test_client.post(
                "/auth/login", json={"username": f"invalid{i}", "password": "wrong"}
            )
            responses.append(response)

        # All should fail with 400
        assert all(r.status_code == 400 for r in responses), "Response must not be empty"


# ---------------------------------------------------------------------------
# Resource Exhaustion Tests
# ---------------------------------------------------------------------------


class TestResourceExhaustion:
    """Tests for resource exhaustion scenarios."""

    def test_many_users_registered(self, test_client):
        """Register many users."""
        for i in range(50):
            response = test_client.post(
                "/auth/register",
                json={
                    "username": f"bulk{i}",
                    "email": f"bulk{i}@example.com",
                    "password": "SecurePass123!",
                },
            )
            assert response.status_code in [201, 400]

    def test_large_array_in_request(self, test_client):
        """Large array in request."""
        large_array = list(range(10000))
        response = test_client.post(
            "/auth/register",
            json={
                "username": "largearray",
                "email": "largearray@example.com",
                "password": "SecurePass123!",
                "items": large_array,
            },
        )
        assert response.status_code in [201, 400, 413, 422]

    def test_large_nested_object(self, test_client):
        """Large nested object."""
        nested = {}
        for i in range(5000):
            nested[f"key{i}"] = {"value": f"value{i}", "nested": {"deeper": i}}
        response = test_client.post(
            "/auth/register",
            json={
                "username": "nestedobj",
                "email": "nested@example.com",
                "password": "SecurePass123!",
                "data": nested,
            },
        )
        assert response.status_code in [201, 400, 413, 422]


# ---------------------------------------------------------------------------
# Boundary Condition Tests
# ---------------------------------------------------------------------------


class TestBoundaryConditions:
    """Tests for boundary conditions."""

    def test_exactly_max_length_username(self, test_client):
        """Username exactly at max length."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "a" * 255,
                "email": "maxlen@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code in [201, 400, 422]

    def test_one_over_max_length_username(self, test_client):
        """Username one character over max."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "a" * 256,
                "email": "overmax@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code in [400, 422]

    def test_single_character_username(self, test_client):
        """Single character username."""
        response = test_client.post(
            "/auth/register",
            json={"username": "a", "email": "single@example.com", "password": "SecurePass123!"},
        )
        assert response.status_code in [201, 400, 422]

    def test_numeric_only_username(self, test_client):
        """Numeric only username."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "123456789",
                "email": "numeric@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code in [201, 400]


# ---------------------------------------------------------------------------
# State Persistence Tests
# ---------------------------------------------------------------------------


class TestStatePersistence:
    """Tests for state persistence across requests."""

    def test_user_persists_after_registration(self, test_client):
        """User should persist after registration."""
        response1 = test_client.post(
            "/auth/register",
            json={
                "username": "persist",
                "email": "persist@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response1.status_code == 201, "Response must not be empty"

        # Try to register again
        response2 = test_client.post(
            "/auth/register",
            json={
                "username": "persist",
                "email": "persist2@example.com",
                "password": "SecurePass123!",
            },
        )
        # Should fail - user exists
        assert response2.status_code == 400, "Response must not be empty"

    def test_can_login_after_registration(self, test_client):
        """Should be able to login after registration."""
        test_client.post(
            "/auth/register",
            json={
                "username": "loginafter",
                "email": "loginafter@example.com",
                "password": "SecurePass123!",
            },
        )

        response = test_client.post(
            "/auth/login", json={"username": "loginafter", "password": "SecurePass123!"}
        )
        assert response.status_code == 200, "Response must not be empty"

    def test_wrong_password_fails_login(self, test_client):
        """Wrong password should fail login."""
        test_client.post(
            "/auth/register",
            json={
                "username": "wrongpass",
                "email": "wrongpass@example.com",
                "password": "SecurePass123!",
            },
        )

        response = test_client.post(
            "/auth/login", json={"username": "wrongpass", "password": "WrongPassword123!"}
        )
        assert response.status_code == 400, "Response must not be empty"
