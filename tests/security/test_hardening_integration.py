"""
Phase 3 Team 4 Security Hardening - Integration Tests

Comprehensive security testing for API endpoints, input validation, and OWASP compliance.

Test Categories:
- T1: Input Validation (4 layers)
- T2: API Endpoint Security
- T3: OWASP Top 10 Coverage
- T4: Rate Limiting & DoS Prevention
- T5: CSRF Protection
- T6: Authentication & Authorization

Run with: pytest tests/security/test_hardening_integration.py -v
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

# pragma: allowlist secret
import pytest

# Import validators
try:
    from codex.security.validators import (
        BatchSizeValidator,
        EmailValidator,
        FileSizeValidator,
        FileTypeValidator,
        LearningRateValidator,
        NumericValidator,
        PathValidator,
        StringValidator,
        XSSValidator,
    )
except ImportError as e:
    pytest.skip(f"Security validators not available: {e}", allow_module_level=True)


# ============================================================================
# T1: Input Validation Tests (4 Layers)
# ============================================================================


class TestLayer1StringValidation:
    """Layer 1: String Input Validation."""

    def test_basic_string_validation(self) -> None:
        """Basic string input validation."""
        validator = StringValidator(min_length=1, max_length=100)
        assert validator.validate("hello") == "hello", "validat is not valid"

    def test_sql_injection_prevention(self) -> None:
        """OWASP A01: SQL injection prevention."""
        validator = StringValidator(disallow_chars="';--")
        with pytest.raises(ValueError):
            validator.validate("'; DROP TABLE users; --")

    def test_command_injection_prevention(self) -> None:
        """OWASP A01: Command injection prevention."""
        validator = StringValidator(disallow_chars="|;&$`")
        with pytest.raises(ValueError):
            validator.validate("test | cat /etc/passwd")

    def test_length_based_dos_prevention(self) -> None:
        """OWASP A01: DoS via extremely long strings."""
        validator = StringValidator(min_length=1, max_length=1000)
        with pytest.raises(ValueError, match="too long"):
            validator.validate("x" * 10000)


class TestLayer2NumericValidation:
    """Layer 2: Numeric Input Validation (ML Parameters)."""

    def test_batch_size_oom_prevention(self) -> None:
        """OWASP A01: Batch size DoS / OOM prevention."""
        validator = BatchSizeValidator()
        # Valid batch sizes
        assert validator.validate(32) == 32.0, "validat is not valid"
        assert validator.validate(256) == 256.0, "validat is not valid"
        # Invalid: too large (OOM attack)
        with pytest.raises(ValueError, match="exceeds maximum"):
            validator.validate(100000)

    def test_learning_rate_sanity_check(self) -> None:
        """OWASP A01: Learning rate sanity validation."""
        validator = LearningRateValidator()
        # Valid learning rates
        assert validator.validate(0.001) == 0.001, "validat is not valid"
        assert validator.validate(0.1) == 0.1, "validat is not valid"
        # Invalid: too small or too large
        with pytest.raises(ValueError):
            validator.validate(1e-10)  # Too small
        with pytest.raises(ValueError):
            validator.validate(10.0)  # Too large

    def test_numeric_nan_inf_protection(self) -> None:
        """Prevent NaN and Infinity in numeric parameters."""
        validator = NumericValidator(min_value=0, max_value=100)
        with pytest.raises(ValueError, match=r"cannot be NaN"):
            validator.validate(float("nan"))
        with pytest.raises(ValueError, match=r"cannot be infinity"):
            validator.validate(float("inf"))


class TestLayer3PathValidation:
    """Layer 3: File Path Validation (Path Traversal Prevention)."""

    def test_path_traversal_attack_prevention(self, tmp_path: Path) -> None:
        """OWASP A01: Prevent ../../ path traversal attacks."""
        validator = PathValidator(tmp_path)
        attack_paths = [
            "../../../../etc/passwd",
            "../../../sensitive_file.txt",
            "subdir/../../outside.txt",
        ]
        for attack in attack_paths:
            with pytest.raises(ValueError, match="traversal|escape"):
                validator.validate(attack)

    def test_absolute_path_rejection(self, tmp_path: Path) -> None:
        """Reject absolute paths."""
        validator = PathValidator(tmp_path)
        with pytest.raises(ValueError, match="must be relative"):
            validator.validate("/etc/passwd")

    def test_symlink_escape_prevention(self, tmp_path: Path) -> None:
        """Prevent symlink-based escape attempts."""
        validator = PathValidator(tmp_path)
        # Try to reference a file outside base_dir via symlink
        outside = tmp_path.parent / "outside.txt"
        outside.write_text("secret")
        link = tmp_path / "link.txt"
        try:
            link.symlink_to(outside)
            with pytest.raises(ValueError, match="escape"):
                validator.validate("link.txt")
        except (OSError, NotImplementedError):
            pytest.skip("Symlinks not supported on this platform")


class TestLayer4XSSPrevention:
    """Layer 4: XSS Prevention."""

    def test_html_entity_escaping(self) -> None:
        """OWASP A07: HTML entity escaping."""
        dangerous = "<script>alert('xss')</script>"
        escaped = XSSValidator.escape_html(dangerous)
        assert "&lt;" in escaped, "Condition must be true"
        assert "&gt;" in escaped, "Condition must be true"
        assert "script" in escaped, "Condition must be true"

    def test_xss_pattern_detection(self) -> None:
        """OWASP A07: Detect XSS patterns."""
        xss_payloads = [
            "<img src=x onerror=alert('xss')>",
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>",
        ]
        for payload in xss_payloads:
            patterns = XSSValidator.detect_xss_patterns(payload)
            assert len(patterns) > 0, f"Should detect XSS in: {payload}"

    def test_clean_input_no_false_positives(self) -> None:
        """Clean input should not trigger XSS detection."""
        clean_inputs = [
            "Hello world",
            "user@example.com",
            "This is a normal message",
        ]
        for clean in clean_inputs:
            patterns = XSSValidator.detect_xss_patterns(clean)
            assert len(patterns) == 0, f"False positive for: {clean}"


# ============================================================================
# T2: API Endpoint Security
# ============================================================================


class TestAPIInputValidation:
    """Test API endpoint input validation."""

    def test_email_validation_in_registration(self) -> None:
        """OWASP A02: Validate email in registration."""
        validator = EmailValidator()
        # Valid email
        assert validator.validate("user@example.com") == "user@example.com", "validat is not valid"
        # Invalid email
        with pytest.raises(ValueError):
            validator.validate("notanemail")
        # Email injection attempt
        with pytest.raises(ValueError):
            validator.validate("user@example.com\nBcc: attacker@evil.com")

    def test_username_validation(self) -> None:
        """OWASP A02: Validate username."""
        import re
        validator = StringValidator(
            min_length=3,
            max_length=30,
            pattern=re.compile(r"^[a-zA-Z0-9_-]+$")
        )
        # Valid usernames
        assert validator.validate("user_123") == "user_123", "validat is not valid"
        assert validator.validate("john-doe") == "john-doe", "validat is not valid"
        # Invalid: too short
        with pytest.raises(ValueError):
            validator.validate("ab")
        # Invalid: special characters
        with pytest.raises(ValueError):
            validator.validate("user@admin")


class TestFileUploadValidation:
    """Test file upload validation."""

    def test_file_type_validation(self, tmp_path: Path) -> None:
        """OWASP A04: Validate file types on upload."""
        validator = FileTypeValidator(allowed_extensions={".pdf", ".txt", ".csv"})
        # Valid file type
        valid_file = tmp_path / "report.pdf"
        valid_file.write_text("pdf")
        assert validator.validate(valid_file) == valid_file, "validat is not valid"
        # Invalid: executable
        invalid_file = tmp_path / "malware.exe"
        invalid_file.write_text("exe")
        with pytest.raises(ValueError, match="disallowed"):
            validator.validate(invalid_file)

    def test_file_size_validation(self, tmp_path: Path) -> None:
        """OWASP A01: Prevent file upload DoS via size."""
        validator = FileSizeValidator(max_bytes=1024)  # 1 KB limit
        # Small file
        small_file = tmp_path / "small.txt"
        small_file.write_text("small")
        assert validator.validate(small_file) == small_file, "validat is not valid"
        # Large file
        large_file = tmp_path / "large.txt"
        large_file.write_text("x" * 10000)
        with pytest.raises(ValueError, match="too large"):
            validator.validate(large_file)


# ============================================================================
# T3: OWASP Top 10 Coverage
# ============================================================================


class TestOWASPA01Injection:
    """OWASP A01: Broken Access Control → Injection Prevention."""

    def test_sql_injection_prevention(self) -> None:
        """Prevent SQL injection via input validation."""
        validator = StringValidator(
            max_length=100,
            disallow_chars="';--"
        )
        # Normal query
        assert validator.validate("SELECT * FROM users") == "SELECT * FROM users", "validat is not valid"
        # SQL injection
        with pytest.raises(ValueError):
            validator.validate("'; DROP TABLE users; --")

    def test_command_injection_prevention(self) -> None:
        """Prevent command injection."""
        validator = StringValidator(disallow_chars="|;&$`(){}[]")
        with pytest.raises(ValueError):
            validator.validate("file.txt | cat /etc/passwd")


class TestOWASPA02Auth:
    """OWASP A02: Broken Authentication → Validation."""

    def test_email_validation_prevents_injection(self) -> None:
        """Email validation prevents auth bypass."""
        validator = EmailValidator()
        # Normal email
        assert validator.validate("user@example.com") == "user@example.com", "validat is not valid"
        # Injection attempt with newline
        with pytest.raises(ValueError):
            validator.validate("user@example.com\nAdministrator: yes")


class TestOWASPA03SensitiveData:
    """OWASP A03: Sensitive Data Exposure → No logging."""

    def test_password_not_logged(self) -> None:
        """Ensure passwords are not logged."""
        # Password validator should not expose password in error messages
        validator = StringValidator(min_length=8, max_length=128)
        password = "SuperSecret123!"
        result = validator.validate(password)
        assert result == password, "Result must not be empty"
        # Error messages should not contain password
        try:
            validator.validate("short")
        except ValueError as e:
            assert "short" not in str(e).lower() or "password" not in str(e).lower(), "Condition must be true"


class TestOWASPA05AccessControl:
    """OWASP A05: Broken Access Control → Path traversal."""

    def test_directory_traversal_prevention(self, tmp_path: Path) -> None:
        """Prevent directory traversal attacks."""
        validator = PathValidator(tmp_path)
        attacks = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "subdir/../../outside.txt",
        ]
        for attack in attacks:
            with pytest.raises(ValueError):
                validator.validate(attack)


class TestOWASPA07XSS:
    """OWASP A07: XSS → HTML escaping."""

    def test_stored_xss_prevention(self) -> None:
        """Prevent stored XSS via escaping."""
        dangerous_input = '<img src=x onerror="alert(\'xss\')">'
        escaped = XSSValidator.escape_html(dangerous_input)
        # Ensure tags are escaped
        assert "&lt;" in escaped, "Condition must be true"
        assert "&gt;" in escaped, "Condition must be true"

    def test_reflected_xss_prevention(self) -> None:
        """Detect reflected XSS patterns."""
        patterns = XSSValidator.detect_xss_patterns(
            "?search=<script>alert('xss')</script>"
        )
        assert len(patterns) > 0, "Patterns must not be empty"


# ============================================================================
# T4: Rate Limiting & DoS Prevention
# ============================================================================


class TestRateLimitingProtection:
    """Test rate limiting and DoS prevention."""

    def test_large_batch_size_prevented(self) -> None:
        """Prevent DoS via huge batch sizes."""
        validator = BatchSizeValidator()
        # Normal batch size
        assert validator.validate(128) == 128.0, "validat is not valid"
        # DoS: huge batch size
        with pytest.raises(ValueError):
            validator.validate(1000000)

    def test_string_length_dos_prevented(self) -> None:
        """Prevent DoS via extremely long strings."""
        validator = StringValidator(min_length=1, max_length=1000)
        # Normal string
        assert validator.validate("hello world") == "hello world", "validat is not valid"
        # DoS: gigantic string
        with pytest.raises(ValueError):
            validator.validate("x" * 1000000)


# ============================================================================
# T5: CSRF Protection
# ============================================================================


class TestCSRFProtection:
    """Test CSRF token generation and validation."""

    def test_csrf_token_generation(self) -> None:
        """CSRF tokens can be generated."""
        try:
            from codex.security.middleware import CSRFTokenManager
        except ImportError:
            pytest.skip("Middleware not available")

        manager = CSRFTokenManager()
        token = manager.generate_token()
        assert isinstance(token, str)
        assert len(token) > 20, "Token must not be empty"

    def test_csrf_token_validation(self) -> None:
        """Generated CSRF tokens validate correctly."""
        try:
            from codex.security.middleware import CSRFTokenManager
        except ImportError:
            pytest.skip("Middleware not available")

        manager = CSRFTokenManager()
        token = manager.generate_token()
        assert manager.validate_token(token) is True, "Condition must be true"
        assert manager.validate_token("invalid_token") is False, "Condition must be true"


# ============================================================================
# T6: Authentication & Authorization
# ============================================================================


class TestAuthenticationValidation:
    """Test authentication-related validation."""

    def test_bearer_token_format(self) -> None:
        """OWASP A02: Validate ****** format."""
        try:
            from codex.security.middleware import RequestValidator
        except ImportError:
            pytest.skip("Middleware not available")

        request = Mock()
        # Valid ******
        request.headers = {"Authorization": "******"}
        token = RequestValidator.validate_auth_header(request)
        assert token == "******", "token is not valid"

        # Invalid format
        request.headers = {"Authorization": "Basic dXNlcjpwYXNz"}
        assert RequestValidator.validate_auth_header(request) is None, "RequestValidat is not valid"

    def test_content_type_validation(self) -> None:
        """OWASP A04: Validate content type."""
        try:
            from codex.security.middleware import RequestValidator
        except ImportError:
            pytest.skip("Middleware not available")

        request = Mock()
        # Valid JSON content type
        request.headers = {"content-type": "application/json"}
        assert RequestValidator.validate_json_content_type(request) is True, "Content must not be empty"

        # Invalid content type
        request.headers = {"content-type": "application/x-www-form-urlencoded"}
        assert RequestValidator.validate_json_content_type(request) is False, "Content must not be empty"


# ============================================================================
# Integration Tests
# ============================================================================


class TestSecurityValidationChain:
    """Test complete security validation chain."""

    def test_registration_flow_security(self) -> None:
        """Test complete registration flow with all validators."""
        email_validator = EmailValidator()
        username_validator = StringValidator(
            min_length=3,
            max_length=30,
            disallow_chars="<>&"
        )

        # Valid registration
        email = email_validator.validate("user@example.com")
        username = username_validator.validate("john_doe")
        assert email == "user@example.com", "email is not valid"
        assert username == "john_doe", "username is not valid"

        # Attack attempts
        with pytest.raises(ValueError):
            email_validator.validate("attacker'; DROP TABLE--@example.com")
        with pytest.raises(ValueError):
            username_validator.validate("<script>alert('xss')</script>")

    def test_file_upload_security_chain(self, tmp_path: Path) -> None:
        """Test complete file upload validation chain."""
        path_validator = PathValidator(tmp_path)
        file_type_validator = FileTypeValidator(allowed_extensions={".pdf", ".txt"})
        file_size_validator = FileSizeValidator(max_bytes=5 * 1024 * 1024)

        # Valid upload
        valid_file = tmp_path / "document.pdf"
        valid_file.write_text("PDF content here")
        path = path_validator.validate("document.pdf")
        file_type_validator.validate(path)
        file_size_validator.validate(path)

        # Attack: path traversal
        with pytest.raises(ValueError):
            path_validator.validate("../../../etc/passwd")

        # Attack: executable file
        exe_file = tmp_path / "malware.exe"
        exe_file.write_text("malicious")
        exe_path = tmp_path / "malware.exe"
        with pytest.raises(ValueError):
            file_type_validator.validate(exe_path)


@pytest.fixture
def cleanup_validators():
    """Fixture to cleanup validators after tests."""
    yield
    # Cleanup code here if needed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
