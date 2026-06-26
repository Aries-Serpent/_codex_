"""Enhanced security tests for mutation testing - Phase 63.

These tests are designed to kill mutants in security-critical paths.
Each test validates specific security boundary conditions.
"""

import hashlib
import html
import re

import pytest

# ============================================================================
# Security Functions Under Test (Inline for Mutation Testing)
# ============================================================================


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS and injection attacks.

    Note: This is a demonstration sanitizer for mutation testing purposes.
    Production code should use specialized libraries for each attack type.
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    if not text:
        return ""
    sanitized = text
    # Remove potential script tags BEFORE HTML escaping (order matters)
    # CodeQL py/bad-tag-filter: include optional whitespace before the '>' on the
    # closing tag so that variants like ``</script >`` (with extra spaces) are
    # also stripped — matching browser HTML parsing behaviour.
    sanitized = re.sub(
        r"<script[^>]*>.*?</script(?:\s+[^>]*)?\s*>",
        "",
        sanitized,
        flags=re.IGNORECASE | re.DOTALL,
    )
    # HTML escape remaining content
    sanitized = html.escape(sanitized)
    # Remove SQL injection patterns (demonstration - use parameterized queries in production)
    # Note: Don't remove semicolons as they're used in HTML entities
    sanitized = re.sub(
        r"(--|\b(OR|AND|DROP|DELETE|INSERT|UPDATE|SELECT|UNION|EXEC)\b)",
        "",
        sanitized,
        flags=re.IGNORECASE,
    )
    # Remove path traversal patterns (including encoded variants)
    sanitized = (
        sanitized.replace("..", "").replace("~", "").replace("%2e%2e", "").replace("%2E%2E", "")
    )
    # Remove leading slashes that could result from path traversal removal
    sanitized = sanitized.lstrip("/")
    return sanitized.strip()


def hash_document_id(doc_id: str, salt: str = "codex_default") -> str:
    """Create a secure hash of document ID."""
    if not doc_id:
        raise ValueError("Document ID cannot be empty")
    combined = f"{salt}:{doc_id}"
    return hashlib.sha256(combined.encode()).hexdigest()


def validate_config(config: dict) -> tuple:
    """Validate RAG configuration for security issues."""
    errors = []
    warnings = []

    # Required fields
    if "model_name" not in config:
        errors.append("model_name is required")
    elif not isinstance(config["model_name"], str):
        errors.append("model_name must be a string")
    elif len(config["model_name"]) < 3:
        errors.append("model_name too short")

    # Dimension validation
    if "dimension" in config:
        dim = config["dimension"]
        if not isinstance(dim, int):
            errors.append("dimension must be integer")
        elif dim < 64:
            errors.append("dimension too small (min 64)")
        elif dim > 4096:
            warnings.append("dimension unusually large")

    # Security settings
    if config.get("allow_remote_models", False):
        warnings.append("remote models enabled - security risk")

    return errors, warnings


def check_permissions(user_role: str, resource: str, action: str) -> bool:
    """Check if user has permission for action on resource."""
    permissions = {
        "admin": {
            "documents": ["read", "write", "delete"],
            "config": ["read", "write"],
            "users": ["read", "write", "delete"],
        },
        "user": {"documents": ["read", "write"], "config": ["read"], "users": []},
        "guest": {"documents": ["read"], "config": [], "users": []},
    }

    if user_role not in permissions:
        return False

    user_perms = permissions[user_role]
    if resource not in user_perms:
        return False

    return action in user_perms[resource]


def rate_limit_check(request_count: int, window_seconds: int, max_requests: int) -> tuple:
    """Check if rate limit is exceeded."""
    if request_count < 0 or window_seconds <= 0 or max_requests <= 0:
        raise ValueError("Invalid rate limit parameters")

    is_limited = request_count >= max_requests
    remaining = max(0, max_requests - request_count)
    reset_time = window_seconds if is_limited else 0

    return is_limited, remaining, reset_time


# ============================================================================
# Enhanced Security Tests for Mutation Testing
# ============================================================================


class TestSanitizeInputMutationKilling:
    """Tests designed to kill mutants in sanitize_input function."""

    def test_sanitize_empty_string_returns_empty(self):
        """Empty input should return empty string."""
        assert sanitize_input("") == "", "Condition must be true"

    def test_sanitize_normal_text_unchanged(self):
        """Normal text should pass through with only HTML escaping."""
        result = sanitize_input("Hello World")
        assert result == "Hello World", "Result must not be empty"

    def test_sanitize_html_script_tags_removed(self):
        """Script tags must be removed completely."""
        result = sanitize_input("<script>alert('xss')</script>hello")
        assert "script" not in result.lower(), "Result must not be empty"
        assert "hello" in result, "Result must not be empty"

    def test_sanitize_html_entities_escaped(self):
        """HTML special chars must be escaped after script removal."""
        result = sanitize_input("<div>test</div>")
        assert "&lt;" in result, "Result must not be empty"
        assert "&gt;" in result, "Result must not be empty"
        assert "<div>" not in result, "Result must not be empty"

    def test_sanitize_sql_injection_patterns_removed(self):
        """SQL injection patterns must be removed."""
        result = sanitize_input("test DROP TABLE users --comment")
        assert "DROP" not in result, "Result must not be empty"
        assert "--" not in result, "Result must not be empty"

    def test_sanitize_path_traversal_removed(self):
        """Path traversal attempts must be removed."""
        result = sanitize_input("../../etc/passwd")
        assert ".." not in result, "Result must not be empty"
        assert result == "etc/passwd", "Result must not be empty"

    def test_sanitize_tilde_removed(self):
        """Tilde must be removed to prevent home directory access."""
        result = sanitize_input("~/sensitive/file")
        assert "~" not in result, "Result must not be empty"

    def test_sanitize_type_error_on_non_string(self):
        """Non-string input must raise TypeError."""
        with pytest.raises(TypeError, match="string"):
            sanitize_input(123)

    def test_sanitize_strips_whitespace(self):
        """Result should be stripped of leading/trailing whitespace."""
        result = sanitize_input("  test  ")
        assert result == "test", "Result must not be empty"

    def test_sanitize_case_insensitive_sql(self):
        """SQL keywords removal should be case insensitive."""
        result = sanitize_input("SELECT * FROM users")
        assert "SELECT" not in result, "Result must not be empty"
        assert "select" not in sanitize_input("select * from users"), "Condition must be true"


class TestHashDocumentIdMutationKilling:
    """Tests designed to kill mutants in hash_document_id function."""

    def test_hash_produces_hex_string(self):
        """Hash should produce 64 character hex string."""
        result = hash_document_id("test_doc")
        assert len(result) == 64, "Result must not be empty"
        assert all(c in "0123456789abcdef" for c in result), "Result must not be empty"

    def test_hash_is_deterministic(self):
        """Same input should always produce same hash."""
        hash1 = hash_document_id("doc123", "salt1")
        hash2 = hash_document_id("doc123", "salt1")
        assert hash1 == hash2, "hash1 is not valid"

    def test_hash_different_salt_different_result(self):
        """Different salt should produce different hash."""
        hash1 = hash_document_id("doc123", "salt1")
        hash2 = hash_document_id("doc123", "salt2")
        assert hash1 != hash2, "hash1 is not valid"

    def test_hash_different_doc_different_result(self):
        """Different document ID should produce different hash."""
        hash1 = hash_document_id("doc1")
        hash2 = hash_document_id("doc2")
        assert hash1 != hash2, "hash1 is not valid"

    def test_hash_empty_doc_raises_error(self):
        """Empty document ID should raise ValueError."""
        with pytest.raises(ValueError, match=r"empty|cannot be empty"):
            hash_document_id("")


class TestValidateConfigMutationKilling:
    """Tests designed to kill mutants in validate_config function."""

    def test_config_missing_model_name_error(self):
        """Missing model_name should produce error."""
        errors, _ = validate_config({})
        assert any("model_name" in e for e in errors), "Error should be raised or set"

    def test_config_model_name_wrong_type_error(self):
        """Non-string model_name should produce error."""
        errors, _ = validate_config({"model_name": 123})
        assert any("string" in e for e in errors), "Error should be raised or set"

    def test_config_model_name_too_short_error(self):
        """model_name less than 3 chars should produce error."""
        errors, _ = validate_config({"model_name": "ab"})
        assert any("short" in e for e in errors), "Error should be raised or set"

    def test_config_valid_model_name_no_error(self):
        """Valid model_name should not produce error."""
        errors, _ = validate_config({"model_name": "valid_model"})
        assert not errors, "Error should be raised or set"

    def test_config_dimension_wrong_type_error(self):
        """Non-integer dimension should produce error."""
        errors, _ = validate_config({"model_name": "test", "dimension": "256"})
        assert any("integer" in e for e in errors), "Error should be raised or set"

    def test_config_dimension_too_small_error(self):
        """Dimension < 64 should produce error."""
        errors, _ = validate_config({"model_name": "test", "dimension": 32})
        assert any("small" in e for e in errors), "Error should be raised or set"

    def test_config_dimension_too_large_warning(self):
        """Dimension > 4096 should produce warning."""
        _, warnings = validate_config({"model_name": "test", "dimension": 8192})
        assert any("large" in w for w in warnings), "Condition must be true"

    def test_config_remote_models_warning(self):
        """allow_remote_models=True should produce warning."""
        _, warnings = validate_config({"model_name": "test", "allow_remote_models": True})
        assert any("remote" in w.lower() for w in warnings), "Condition must be true"


class TestCheckPermissionsMutationKilling:
    """Tests designed to kill mutants in check_permissions function."""

    def test_admin_can_delete_documents(self):
        """Admin should be able to delete documents."""
        assert check_permissions("admin", "documents", "delete") is True

    def test_admin_can_write_users(self):
        """Admin should be able to write users."""
        assert check_permissions("admin", "users", "write") is True

    def test_user_cannot_delete_documents(self):
        """User should not be able to delete documents."""
        assert check_permissions("user", "documents", "delete") is False

    def test_user_can_read_config(self):
        """User should be able to read config."""
        assert check_permissions("user", "config", "read") is True

    def test_user_cannot_write_config(self):
        """User should not be able to write config."""
        assert check_permissions("user", "config", "write") is False

    def test_guest_can_only_read_documents(self):
        """Guest should only read documents."""
        assert check_permissions("guest", "documents", "read") is True
        assert check_permissions("guest", "documents", "write") is False

    def test_guest_cannot_access_config(self):
        """Guest should not access config."""
        assert check_permissions("guest", "config", "read") is False

    def test_unknown_role_denied(self):
        """Unknown role should be denied all access."""
        assert check_permissions("hacker", "documents", "read") is False

    def test_unknown_resource_denied(self):
        """Unknown resource should be denied."""
        assert check_permissions("admin", "secrets", "read") is False


class TestRateLimitCheckMutationKilling:
    """Tests designed to kill mutants in rate_limit_check function."""

    def test_under_limit_not_limited(self):
        """Under limit should not be limited."""
        is_limited, remaining, reset = rate_limit_check(5, 60, 10)
        assert is_limited is False, "is_limited is not valid"
        assert remaining == 5, "remaining is not valid"
        assert reset == 0, "reset is not valid"

    def test_at_limit_is_limited(self):
        """At limit should be limited."""
        is_limited, remaining, reset = rate_limit_check(10, 60, 10)
        assert is_limited is True, "is_limited is not valid"
        assert remaining == 0, "remaining is not valid"
        assert reset == 60, "reset is not valid"

    def test_over_limit_is_limited(self):
        """Over limit should be limited."""
        is_limited, remaining, _reset = rate_limit_check(15, 60, 10)
        assert is_limited is True, "is_limited is not valid"
        assert remaining == 0, "remaining is not valid"

    def test_remaining_calculated_correctly(self):
        """Remaining requests should be calculated correctly."""
        _, remaining, _ = rate_limit_check(7, 60, 10)
        assert remaining == 3, "remaining is not valid"

    def test_invalid_negative_count_raises(self):
        """Negative request count should raise error."""
        with pytest.raises(ValueError):
            rate_limit_check(-1, 60, 10)

    def test_invalid_zero_window_raises(self):
        """Zero window should raise error."""
        with pytest.raises(ValueError):
            rate_limit_check(5, 0, 10)

    def test_invalid_zero_max_raises(self):
        """Zero max requests should raise error."""
        with pytest.raises(ValueError):
            rate_limit_check(5, 60, 0)


class TestMutationKillers:
    """Additional tests specifically designed to kill surviving mutations."""

    def test_sql_injection_or_keyword_removed(self):
        """OR keyword should be removed from SQL injection attempts."""
        result = sanitize_input("SELECT * FROM users OR 1=1")
        assert "OR" not in result, "Result must not be empty"
        # Verify the output doesn't contain SQL keywords even fragmented
        assert result.replace("&#39;", "'") != "SELECT * FROM users OR 1=1"

    def test_sql_injection_and_keyword_removed(self):
        """AND keyword should be removed from SQL injection attempts."""
        result = sanitize_input("WHERE id=1 AND password='test'")
        assert "AND" not in result, "Result must not be empty"

    def test_sql_injection_union_keyword_removed(self):
        """UNION keyword should be removed from SQL injection attempts."""
        result = sanitize_input("SELECT * UNION SELECT password FROM users")
        assert "UNION" not in result, "Result must not be empty"

    def test_config_dimension_valid_type_no_error(self):
        """Valid integer dimension should not produce type error."""
        errors, _warnings = validate_config({"model_name": "test", "dimension": 256})
        # Should not have dimension type error
        assert not any("integer" in e for e in errors), "Error should be raised or set"
        # But should be a valid dimension
        assert 64 <= 256 <= 4096, "64 is not valid"

    def test_config_dimension_float_is_error(self):
        """Float dimension should produce error since it's not an int."""
        errors, _ = validate_config({"model_name": "test", "dimension": 256.5})
        assert any("integer" in e for e in errors), "Error should be raised or set"

    def test_config_remote_models_false_no_warning(self):
        """allow_remote_models=False should not produce warning."""
        _, warnings = validate_config({"model_name": "test", "allow_remote_models": False})
        assert not any("remote" in w.lower() for w in warnings), "Condition must be true"

    def test_config_remote_models_not_present_no_warning(self):
        """No allow_remote_models key should not produce warning."""
        _, warnings = validate_config({"model_name": "test"})
        assert not any("remote" in w.lower() for w in warnings), "Condition must be true"

    def test_sanitize_multiple_sql_keywords_all_removed(self):
        """Multiple SQL keywords in one string should all be removed."""
        result = sanitize_input("DROP DATABASE; DELETE FROM users; SELECT * FROM admin")
        assert "DROP" not in result, "Result must not be empty"
        assert "DELETE" not in result, "Result must not be empty"
        assert "SELECT" not in result, "Result must not be empty"

    def test_sanitize_maintains_legitimate_text_structure(self):
        """Legitimate text should maintain word boundaries after sanitization."""
        result = sanitize_input("The database contains user records")
        # Should contain 'contains' (database and user are retained as they're not keywords)
        assert "contains" in result.lower(), "Result must not be empty"

    def test_hash_with_numeric_doc_id(self):
        """Document IDs with numbers should hash consistently."""
        hash1 = hash_document_id("doc123", "salt")
        hash2 = hash_document_id("doc123", "salt")
        # Deterministic
        assert hash1 == hash2, "hash1 is not valid"
        # But different from other IDs
        assert hash1 != hash_document_id("doc124", "salt")
