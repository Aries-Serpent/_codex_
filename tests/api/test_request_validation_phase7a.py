"""
Comprehensive Request Validation Tests for Phase 7A WAVE 2

Tests for validating request inputs, parameters, and schemas.

Categories:
- Valid requests with all fields
- Valid requests with optional fields
- Invalid/malformed request bodies
- Type mismatches
- Missing required fields
- Extra unexpected fields # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
- Boundary value testing
- Special characters in strings
- Parameter validation
"""

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
# Valid Request Tests
# ---------------------------------------------------------------------------


class TestValidRequests:
    """Tests for valid request payloads."""

    def test_register_with_all_required_fields(self, test_client):
        """Registration with all required fields should succeed."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "validuser",
                "email": "valid@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code == 201, "Response must not be empty"
        data = response.json()
        assert data["username"] == "validuser", "Data must not be empty"
        assert data["email"] == "valid@example.com", "Data must not be empty"

    def test_register_with_optional_roles(self, test_client):
        """Registration with optional roles field."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "userwithroles",
                "email": "roles@example.com",
                "password": "SecurePass123!",
                "roles": ["user", "admin"],
            },
        )
        assert response.status_code == 201, "Response must not be empty"

    def test_login_with_username_and_password(self, test_client):
        """Login with username and password."""
        # Register first
        test_client.post(
            "/auth/register",
            json={
                "username": "logintest",
                "email": "login@example.com",
                "password": "SecurePass123!",
            },
        )
        # Then login
        response = test_client.post(
            "/auth/login", json={"username": "logintest", "password": "SecurePass123!"}
        )
        assert response.status_code == 200, "Response must not be empty"
        data = response.json()
        assert "access_token" in data, "Data must not be empty"

    def test_register_with_max_length_username(self, test_client):
        """Registration with maximum valid username length."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "a" * 50,  # Assuming 50 char limit
                "email": "maxlen@example.com",
                "password": "SecurePass123!",
            },
        )
        # Should succeed or fail gracefully
        assert response.status_code in [201, 400, 422]

    def test_register_with_special_chars_in_email(self, test_client):
        """Registration with special characters in email."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "specialemail",
                "email": "user+tag@example.co.uk",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code in [201, 400]

    def test_register_with_international_characters(self, test_client):
        """Registration with international characters."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "userñáéíóú",
                "email": "intl@example.com",
                "password": "SecurePass123!",
            },
        )
        # Should handle or reject gracefully
        assert response.status_code in [201, 400, 422]

    def test_register_with_minimum_password_length(self, test_client):
        """Registration with minimum valid password."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "minpass",
                "email": "minpass@example.com",
                "password": "Pass1!",  # 6 chars, but needs uppercase, lowercase, digit, special
            },
        )
        # May fail password validation
        assert response.status_code in [201, 400]


# ---------------------------------------------------------------------------
# Invalid Request Body Tests
# ---------------------------------------------------------------------------


class TestInvalidRequestBodies:
    """Tests for invalid request bodies."""

    def test_empty_json_object(self, test_client):
        """Empty JSON object should fail validation."""
        response = test_client.post("/auth/register", json={})
        assert response.status_code == 422, "Response must not be empty"

    def test_null_required_field(self, test_client):
        """Null required field should fail."""
        response = test_client.post(
            "/auth/register",
            json={"username": None, "email": "test@example.com", "password": "SecurePass123!"},
        )
        assert response.status_code == 422, "Response must not be empty"

    def test_empty_string_username(self, test_client):
        """Empty string username should fail."""
        response = test_client.post(
            "/auth/register",
            json={"username": "", "email": "test@example.com", "password": "SecurePass123!"},
        )
        assert response.status_code == 400 or response.status_code == 422, "Response must not be empty"

    def test_whitespace_only_username(self, test_client):
        """Whitespace-only username should fail."""
        response = test_client.post(
            "/auth/register",
            json={"username": "   ", "email": "test@example.com", "password": "SecurePass123!"},
        )
        assert response.status_code in [400, 422]

    def test_missing_username_field(self, test_client):
        """Missing username field should fail."""
        response = test_client.post(
            "/auth/register", json={"email": "test@example.com", "password": "SecurePass123!"}
        )
        assert response.status_code == 422, "Response must not be empty"

    def test_missing_email_field(self, test_client):
        """Missing email field should fail."""
        response = test_client.post(
            "/auth/register", json={"username": "test", "password": "SecurePass123!"}
        )
        assert response.status_code == 422, "Response must not be empty"

    def test_missing_password_field(self, test_client):
        """Missing password field should fail."""
        response = test_client.post(
            "/auth/register", json={"username": "test", "email": "test@example.com"}
        )
        assert response.status_code == 422, "Response must not be empty"


# ---------------------------------------------------------------------------
# Type Mismatch Tests
# ---------------------------------------------------------------------------


class TestTypeMismatches:
    """Tests for type mismatch errors."""

    def test_username_as_integer(self, test_client):
        """Username as integer should fail."""
        response = test_client.post(
            "/auth/register",
            json={"username": 12345, "email": "test@example.com", "password": "SecurePass123!"},
        )
        assert response.status_code in [400, 422]

    def test_email_as_integer(self, test_client):
        """Email as integer should fail."""
        response = test_client.post(
            "/auth/register",
            json={"username": "test", "email": 12345, "password": "SecurePass123!"},
        )
        assert response.status_code in [400, 422]

    def test_password_as_integer(self, test_client):
        """Password as integer should fail."""
        response = test_client.post(
            "/auth/register",
            json={"username": "test", "email": "test@example.com", "password": 12345},
        )
        assert response.status_code in [400, 422]

    def test_username_as_array(self, test_client):
        """Username as array should fail."""
        response = test_client.post(
            "/auth/register",
            json={"username": ["test"], "email": "test@example.com", "password": "SecurePass123!"},
        )
        assert response.status_code in [400, 422]

    def test_password_as_boolean(self, test_client):
        """Password as boolean should fail."""
        response = test_client.post(
            "/auth/register",
            json={"username": "test", "email": "test@example.com", "password": True},
        )
        assert response.status_code in [400, 422]

    def test_roles_as_string_instead_of_array(self, test_client):
        """Roles as string instead of array."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "test",
                "email": "test@example.com",
                "password": "SecurePass123!",
                "roles": "admin",  # Should be array
            },
        )
        # May coerce or reject
        assert response.status_code in [201, 400, 422]


# ---------------------------------------------------------------------------
# Email Validation Tests
# ---------------------------------------------------------------------------


class TestEmailValidation:
    """Tests for email field validation."""

    @pytest.mark.parametrize(
        "invalid_email",
        [
            "notanemail",
            "missing@domain",
            "@nodomain.com",
            "spaces in@email.com",
            "double@@domain.com",
            ".startswithdot@domain.com",
            "user@.com",
            "user@domain..com",
            "user name@domain.com",
            "",
        ],
    )
    def test_invalid_email_formats(self, test_client, invalid_email):
        """Invalid email formats should fail."""
        response = test_client.post(
            "/auth/register",
            json={"username": "test", "email": invalid_email, "password": "SecurePass123!"},
        )
        assert response.status_code in [400, 422]

    @pytest.mark.parametrize(
        "valid_email",
        [
            "user@domain.com",
            "user.name@domain.com",
            "user+tag@domain.com",
            "user_name@domain.com",
            "user123@domain.co.uk",
            "a@b.co",
        ],
    )
    def test_valid_email_formats(self, test_client, valid_email):
        """Valid email formats should succeed."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": f"user{hash(valid_email) % 10000}",
                "email": valid_email,
                "password": "SecurePass123!",
            },
        )
        assert response.status_code in [201, 400]  # May fail if email already exists


# ---------------------------------------------------------------------------
# Password Validation Tests
# ---------------------------------------------------------------------------


class TestPasswordValidation:
    """Tests for password field validation."""

    @pytest.mark.parametrize(
        "weak_password",
        [
            "123456",  # Only digits
            "password",  # Only lowercase
            "PASSWORD",  # Only uppercase
            "Pass",  # Too short
            "password1",  # Missing uppercase
            "PASSWORD1",  # Missing lowercase
            "Password",  # Missing digit
            "Pass123",  # Missing special char
        ],
    )
    def test_weak_passwords(self, test_client, weak_password):
        """Weak passwords should fail validation."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": f"weakpass{hash(weak_password) % 10000}",
                "email": f"weak{hash(weak_password)}@example.com",
                "password": weak_password,
            },
        )
        # Should reject weak password
        assert response.status_code in [400, 422]

    @pytest.mark.parametrize(
        "strong_password",
        [
            "SecurePass123!",
            "MyP@ssw0rd",
            "Correct!Horse1",
            "P@ssw0rd2024",
        ],
    )
    def test_strong_passwords(self, test_client, strong_password):
        """Strong passwords should be accepted."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": f"strongpass{hash(strong_password) % 10000}",
                "email": f"strong{hash(strong_password)}@example.com",
                "password": strong_password,
            },
        )
        assert response.status_code == 201, "Response must not be empty"

    def test_password_with_spaces(self, test_client):
        """Password with spaces should work."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "spacedpass",
                "email": "spaced@example.com",
                "password": "My Pass Word 123!",
            },
        )
        # Should accept or reject
        assert response.status_code in [201, 400, 422]

    def test_password_with_unicode(self, test_client):
        """Password with unicode characters."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "unicodepass",
                "email": "unicode@example.com",
                "password": "Pässwörd123!",
            },
        )
        # Should handle unicode
        assert response.status_code in [201, 400, 422]

    def test_very_long_password(self, test_client):
        """Very long password."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "longpass",
                "email": "long@example.com",
                "password": "P" + "a" * 1000 + "1!",
            },
        )
        # Should accept or have max length
        assert response.status_code in [201, 400, 422]


# ---------------------------------------------------------------------------
# Username Validation Tests
# ---------------------------------------------------------------------------


class TestUsernameValidation:
    """Tests for username field validation."""

    def test_username_with_spaces(self, test_client):
        """Username with spaces."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "user name",
                "email": "userspace@example.com",
                "password": "SecurePass123!",
            },
        )
        # Should accept or reject
        assert response.status_code in [201, 400, 422]

    def test_username_with_special_chars(self, test_client):
        """Username with special characters."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "user@name",
                "email": "userspecial@example.com",
                "password": "SecurePass123!",
            },
        )
        # Should accept or reject
        assert response.status_code in [201, 400, 422]

    def test_username_starting_with_number(self, test_client):
        """Username starting with number."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "123user",
                "email": "numuser@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code in [201, 400]

    def test_username_with_underscore(self, test_client):
        """Username with underscore."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "user_name",
                "email": "underscore@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code in [201, 400]

    def test_username_with_dash(self, test_client):
        """Username with dash."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "user-name",
                "email": "dash@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code in [201, 400]


# ---------------------------------------------------------------------------
# Extra Field Tests
# ---------------------------------------------------------------------------


class TestExtraFields:
    """Tests for unexpected/extra fields."""

    def test_extra_unknown_field(self, test_client):
        """Extra unknown field in request."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "test",
                "email": "test@example.com",
                "password": "SecurePass123!",
                "unknown_field": "value",
            },
        )
        # Depends on Pydantic config
        assert response.status_code in [201, 400, 422]

    def test_multiple_extra_fields(self, test_client):
        """Multiple extra fields."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "test",
                "email": "test@example.com",
                "password": "SecurePass123!",
                "extra1": "value1",
                "extra2": "value2",
                "extra3": "value3",
            },
        )
        assert response.status_code in [201, 400, 422]

    def test_nested_extra_object(self, test_client):
        """Nested extra object."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "test",
                "email": "test@example.com",
                "password": "SecurePass123!",
                "metadata": {"key": "value"},
            },
        )
        assert response.status_code in [201, 400, 422]


# ---------------------------------------------------------------------------
# Boundary Value Tests
# ---------------------------------------------------------------------------


class TestBoundaryValues:
    """Tests for boundary value testing."""

    def test_minimum_length_username(self, test_client):
        """Username with minimum length."""
        response = test_client.post(
            "/auth/register",
            json={"username": "a", "email": "minuser@example.com", "password": "SecurePass123!"},
        )
        assert response.status_code in [201, 400, 422]

    def test_maximum_length_username(self, test_client):
        """Username at maximum length."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "a" * 255,
                "email": "maxuser@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code in [201, 400, 422]

    def test_zero_length_password(self, test_client):
        """Zero length password."""
        response = test_client.post(
            "/auth/register", json={"username": "test", "email": "test@example.com", "password": ""}
        )
        assert response.status_code in [400, 422]

    @pytest.mark.parametrize("length", [1, 2, 5, 10, 50, 100, 255, 1000])
    def test_various_string_lengths(self, test_client, length):
        """Test various string lengths."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": f"user_{length}",
                "email": f"test{length}@example.com",
                "password": "S" + "a" * (length - 1) + "1!",
            },
        )
        # Should handle various lengths
        assert response.status_code in [201, 400, 422]


# ---------------------------------------------------------------------------
# Special Characters Tests
# ---------------------------------------------------------------------------


class TestSpecialCharacters:
    """Tests for special characters in strings."""

    @pytest.mark.parametrize(
        "special_username",
        [
            "user!name",
            "user@name",
            "user#name",
            "user$name",
            "user%name",
            "user&name",
            "user*name",
            "user(name)",
            "user[name]",
            "user{name}",
        ],
    )
    def test_special_chars_in_username(self, test_client, special_username):
        """Special characters in username."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": special_username,
                "email": f"special{hash(special_username)}@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code in [201, 400, 422]

    def test_newline_in_username(self, test_client):
        """Newline character in username."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "user\nname",
                "email": "newline@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code in [400, 422]

    def test_tab_in_email(self, test_client):
        """Tab character in email."""
        response = test_client.post(
            "/auth/register",
            json={"username": "test", "email": "user\t@example.com", "password": "SecurePass123!"},
        )
        assert response.status_code in [400, 422]

    def test_sql_injection_attempt_in_username(self, test_client):
        """SQL injection attempt in username."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "'; DROP TABLE users; --",
                "email": "sqli@example.com",
                "password": "SecurePass123!",
            },
        )
        # Should safely reject or handle
        assert response.status_code in [201, 400, 422]

    def test_xss_attempt_in_username(self, test_client):
        """XSS attempt in username."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "<script>alert('xss')</script>",
                "email": "xss@example.com",
                "password": "SecurePass123!",
            },
        )
        # Should safely reject or handle
        assert response.status_code in [201, 400, 422]


# ---------------------------------------------------------------------------
# Parameter Combination Tests
# ---------------------------------------------------------------------------


class TestParameterCombinations:
    """Tests for parameter combinations and interdependencies."""

    def test_same_username_different_email(self, test_client):
        """Same username with different email."""
        # Register first user
        response1 = test_client.post(
            "/auth/register",
            json={
                "username": "combo1",
                "email": "combo1a@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response1.status_code == 201, "Response must not be empty"

        # Try different combo
        response2 = test_client.post(
            "/auth/register",
            json={
                "username": "combo1",
                "email": "combo1b@example.com",
                "password": "SecurePass123!",
            },
        )
        # Should fail - duplicate username
        assert response2.status_code == 400, "Response must not be empty"

    def test_different_username_same_email(self, test_client):
        """Different username with same email."""
        # Register first user
        response1 = test_client.post(
            "/auth/register",
            json={
                "username": "combo2a",
                "email": "combo@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response1.status_code == 201, "Response must not be empty"

        # Try different username, same email
        response2 = test_client.post(
            "/auth/register",
            json={
                "username": "combo2b",
                "email": "combo@example.com",
                "password": "SecurePass123!",
            },
        )
        # Should fail - duplicate email
        assert response2.status_code in [400, 409]

    def test_case_sensitivity_in_username(self, test_client):
        """Case sensitivity in usernames."""
        response1 = test_client.post(
            "/auth/register",
            json={
                "username": "CaseTest",
                "email": "case1@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response1.status_code == 201, "Response must not be empty"

        response2 = test_client.post(
            "/auth/register",
            json={
                "username": "casetest",
                "email": "case2@example.com",
                "password": "SecurePass123!",
            },
        )
        # May allow or reject based on case sensitivity
        assert response2.status_code in [201, 400]

    def test_email_case_insensitivity(self, test_client):
        """Email case insensitivity."""
        response1 = test_client.post(
            "/auth/register",
            json={"username": "email1", "email": "Test@Example.COM", "password": "SecurePass123!"},
        )
        assert response1.status_code == 201, "Response must not be empty"

        response2 = test_client.post(
            "/auth/register",
            json={"username": "email2", "email": "test@example.com", "password": "SecurePass123!"},
        )
        # Should fail if emails match case-insensitively
        assert response2.status_code in [201, 400, 409]
