"""Enhanced security tests for mutation testing - Phase 63.

These tests are designed to kill mutants in security-critical paths.
Each test validates specific security boundary conditions.
"""

import hashlib
import html
import re
import time
from unittest.mock import MagicMock, patch


# ============================================================================
# Security Functions Under Test (Inline for Mutation Testing)
# ============================================================================


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS and injection attacks."""
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    if not text:
        return ""
    # HTML escape
    sanitized = html.escape(text)
    # Remove potential script tags
    sanitized = re.sub(r"<script[^>]*>.*?</script>", "", sanitized, flags=re.IGNORECASE | re.DOTALL)
    # Remove SQL injection patterns
    sanitized = re.sub(r"(--|;|'|\"|\b(OR|AND|DROP|DELETE|INSERT|UPDATE|SELECT)\b)", "", sanitized, flags=re.IGNORECASE)
    # Remove path traversal
    sanitized = sanitized.replace("..", "").replace("~", "")
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
        "admin": {"documents": ["read", "write", "delete"], "config": ["read", "write"], "users": ["read", "write", "delete"]},
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
        assert sanitize_input("") == ""
    
    def test_sanitize_normal_text_unchanged(self):
        """Normal text should pass through with only HTML escaping."""
        result = sanitize_input("Hello World")
        assert result == "Hello World"
    
    def test_sanitize_html_script_tags_removed(self):
        """Script tags must be removed completely."""
        result = sanitize_input("<script>alert('xss')</script>hello")
        assert "<script>" not in result
        assert "alert" not in result
        assert "hello" in result
    
    def test_sanitize_html_entities_escaped(self):
        """HTML special chars must be escaped."""
        result = sanitize_input("<div>test</div>")
        assert "&lt;" in result
        assert "&gt;" in result
        assert "<div>" not in result
    
    def test_sanitize_sql_injection_patterns_removed(self):
        """SQL injection patterns must be removed."""
        result = sanitize_input("'; DROP TABLE users; --")
        assert "DROP" not in result
        assert "--" not in result
        assert ";" not in result
    
    def test_sanitize_path_traversal_removed(self):
        """Path traversal attempts must be removed."""
        result = sanitize_input("../../etc/passwd")
        assert ".." not in result
        assert result == "etc/passwd"
    
    def test_sanitize_tilde_removed(self):
        """Tilde must be removed to prevent home directory access."""
        result = sanitize_input("~/sensitive/file")
        assert "~" not in result
    
    def test_sanitize_type_error_on_non_string(self):
        """Non-string input must raise TypeError."""
        try:
            sanitize_input(123)
            assert False, "Should raise TypeError"
        except TypeError as e:
            assert "string" in str(e).lower()
    
    def test_sanitize_strips_whitespace(self):
        """Result should be stripped of leading/trailing whitespace."""
        result = sanitize_input("  test  ")
        assert result == "test"
    
    def test_sanitize_case_insensitive_sql(self):
        """SQL keywords removal should be case insensitive."""
        result = sanitize_input("SELECT * FROM users")
        assert "SELECT" not in result
        assert "select" not in sanitize_input("select * from users")


class TestHashDocumentIdMutationKilling:
    """Tests designed to kill mutants in hash_document_id function."""
    
    def test_hash_produces_hex_string(self):
        """Hash should produce 64 character hex string."""
        result = hash_document_id("test_doc")
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)
    
    def test_hash_is_deterministic(self):
        """Same input should always produce same hash."""
        hash1 = hash_document_id("doc123", "salt1")
        hash2 = hash_document_id("doc123", "salt1")
        assert hash1 == hash2
    
    def test_hash_different_salt_different_result(self):
        """Different salt should produce different hash."""
        hash1 = hash_document_id("doc123", "salt1")
        hash2 = hash_document_id("doc123", "salt2")
        assert hash1 != hash2
    
    def test_hash_different_doc_different_result(self):
        """Different document ID should produce different hash."""
        hash1 = hash_document_id("doc1")
        hash2 = hash_document_id("doc2")
        assert hash1 != hash2
    
    def test_hash_empty_doc_raises_error(self):
        """Empty document ID should raise ValueError."""
        try:
            hash_document_id("")
            assert False, "Should raise ValueError"
        except ValueError as e:
            assert "empty" in str(e).lower()


class TestValidateConfigMutationKilling:
    """Tests designed to kill mutants in validate_config function."""
    
    def test_config_missing_model_name_error(self):
        """Missing model_name should produce error."""
        errors, _ = validate_config({})
        assert any("model_name" in e for e in errors)
    
    def test_config_model_name_wrong_type_error(self):
        """Non-string model_name should produce error."""
        errors, _ = validate_config({"model_name": 123})
        assert any("string" in e for e in errors)
    
    def test_config_model_name_too_short_error(self):
        """model_name less than 3 chars should produce error."""
        errors, _ = validate_config({"model_name": "ab"})
        assert any("short" in e for e in errors)
    
    def test_config_valid_model_name_no_error(self):
        """Valid model_name should not produce error."""
        errors, _ = validate_config({"model_name": "valid_model"})
        assert not errors
    
    def test_config_dimension_wrong_type_error(self):
        """Non-integer dimension should produce error."""
        errors, _ = validate_config({"model_name": "test", "dimension": "256"})
        assert any("integer" in e for e in errors)
    
    def test_config_dimension_too_small_error(self):
        """Dimension < 64 should produce error."""
        errors, _ = validate_config({"model_name": "test", "dimension": 32})
        assert any("small" in e for e in errors)
    
    def test_config_dimension_too_large_warning(self):
        """Dimension > 4096 should produce warning."""
        _, warnings = validate_config({"model_name": "test", "dimension": 8192})
        assert any("large" in w for w in warnings)
    
    def test_config_remote_models_warning(self):
        """allow_remote_models=True should produce warning."""
        _, warnings = validate_config({"model_name": "test", "allow_remote_models": True})
        assert any("remote" in w.lower() for w in warnings)


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
        assert is_limited is False
        assert remaining == 5
        assert reset == 0
    
    def test_at_limit_is_limited(self):
        """At limit should be limited."""
        is_limited, remaining, reset = rate_limit_check(10, 60, 10)
        assert is_limited is True
        assert remaining == 0
        assert reset == 60
    
    def test_over_limit_is_limited(self):
        """Over limit should be limited."""
        is_limited, remaining, reset = rate_limit_check(15, 60, 10)
        assert is_limited is True
        assert remaining == 0
    
    def test_remaining_calculated_correctly(self):
        """Remaining requests should be calculated correctly."""
        _, remaining, _ = rate_limit_check(7, 60, 10)
        assert remaining == 3
    
    def test_invalid_negative_count_raises(self):
        """Negative request count should raise error."""
        try:
            rate_limit_check(-1, 60, 10)
            assert False, "Should raise ValueError"
        except ValueError:
            pass
    
    def test_invalid_zero_window_raises(self):
        """Zero window should raise error."""
        try:
            rate_limit_check(5, 0, 10)
            assert False, "Should raise ValueError"
        except ValueError:
            pass
    
    def test_invalid_zero_max_raises(self):
        """Zero max requests should raise error."""
        try:
            rate_limit_check(5, 60, 0)
            assert False, "Should raise ValueError"
        except ValueError:
            pass
