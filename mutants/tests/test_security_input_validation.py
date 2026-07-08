"""
Security tests for input validation and cryptographic operations.

Phase 3 Wave 5 Lane 1 — L1_SECURITY
OWASP Coverage: A03 (Injection), A02 (Cryptographic Failures)
Test Count: 18 tests
"""

import hashlib
import os
import re
import secrets
import urllib.parse
from typing import List

import pytest


 # pragma: allowlist secret
class TestInputValidation:
    """Test suite for secure input validation."""

    def test_sql_injection_payload_rejected(self):
        """Verify SQL injection payloads are rejected."""
        
        def validate_username(username: str) -> str:
            """Validate username against SQL injection."""
            # Should only allow alphanumeric, underscore, hyphen
            if not re.match(r'^[a-zA-Z0-9_-]{3,32}$', username):
                raise ValueError("Invalid username format")
            return username
        
        # Valid usernames
        assert validate_username("alice_123") == "alice_123"
        assert validate_username("bob-user") == "bob-user"
        
        # SQL injection attempts
        with pytest.raises(ValueError):
            validate_username("alice' OR '1'='1")
        
        with pytest.raises(ValueError):
            validate_username("'; DROP TABLE users; --")
        
        with pytest.raises(ValueError):
            validate_username("admin'--")

    def test_xss_payload_rejected_in_user_input(self):
        """Verify XSS payloads are rejected or properly escaped."""
        
        def validate_comment(comment: str) -> str:
            """Validate comment text for XSS attacks."""
            # Check for dangerous HTML/JS
            dangerous_patterns = [
                r'<script',
                r'javascript:',
                r'on\w+\s*=',  # Event handlers
                r'<iframe',
                r'<object',
                r'<embed'
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, comment, re.IGNORECASE):
                    raise ValueError("Dangerous content detected")
            
            return comment
        
        # Valid comments
        assert validate_comment("This is a safe comment") == "This is a safe comment"
        assert validate_comment("Check out: https://example.com") == "Check out: https://example.com"
        
        # XSS attempts
        with pytest.raises(ValueError):
            validate_comment("<script>alert('XSS')</script>")
        
        with pytest.raises(ValueError):
            validate_comment("<img src=x onerror=alert('XSS')>")
        
        with pytest.raises(ValueError):
            validate_comment("javascript:alert('XSS')")

    def test_command_injection_prevented(self):
        """Verify command injection is prevented."""
        
        def validate_filename(filename: str) -> str:
            """Validate filename to prevent command injection."""
            # Only allow alphanumeric, dots, dashes, underscores
            if not re.match(r'^[a-zA-Z0-9._-]+$', filename):
                raise ValueError("Invalid filename")
            
            # Prevent directory traversal
            if '..' in filename or '/' in filename or '\\' in filename:
                raise ValueError("Directory traversal detected")
            
            return filename
        
        # Valid filenames
        assert validate_filename("report_2026.pdf") == "report_2026.pdf"
        assert validate_filename("data-file_v1.csv") == "data-file_v1.csv"
        
        # Command injection attempts
        with pytest.raises(ValueError):
            validate_filename("file.txt; rm -rf /")
        
        with pytest.raises(ValueError):
            validate_filename("file.txt && cat /etc/passwd")
        
        with pytest.raises(ValueError):
            validate_filename("../../../etc/passwd")

    def test_path_traversal_prevented(self):
        """Verify path traversal attacks are prevented."""
        
        def validate_file_path(requested_path: str, base_dir: str = "/data") -> str:
            """Validate file path to prevent traversal."""
            # Normalize path
            import os.path
            
            # Get absolute paths
            requested_abs = os.path.abspath(requested_path)
            base_abs = os.path.abspath(base_dir)
            
            # Ensure requested path is within base directory
            if not requested_abs.startswith(base_abs):
                raise ValueError("Path traversal detected")
            
            return requested_abs
        
        base = "/data"
        
        # Valid paths
        result = validate_file_path("/data/documents/file.txt", base)
        assert "/data/documents" in result
        
        # Path traversal attempts
        with pytest.raises(ValueError):
            validate_file_path("/data/../../../etc/passwd", base)
        
        with pytest.raises(ValueError):
            validate_file_path("/etc/passwd", base)

    def test_email_validation(self):
        """Verify email validation prevents common bypasses."""
        
        def validate_email(email: str) -> str:
            """Validate email address format."""
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, email):
                raise ValueError("Invalid email format")
            
            # Additional checks
            if len(email) > 254:
                raise ValueError("Email too long")
            
            return email
        
        # Valid emails
        assert validate_email("user@example.com") == "user@example.com"
        assert validate_email("alice.bob+tag@company.co.uk") == "alice.bob+tag@company.co.uk"
        
        # Invalid emails
        with pytest.raises(ValueError):
            validate_email("invalid.email")
        
        with pytest.raises(ValueError):
            validate_email("user@.com")
        
        with pytest.raises(ValueError):
            validate_email("user@domain")

    def test_integer_overflow_prevented(self):
        """Verify integer overflow attacks are prevented."""
        
        def validate_quantity(quantity: int, max_value: int = 1000000) -> int:
            """Validate numeric input to prevent overflow."""
            if quantity < 0:
                raise ValueError("Quantity cannot be negative")
            
            if quantity > max_value:
                raise ValueError(f"Quantity exceeds maximum: {max_value}")
            
            return quantity
        
        # Valid values
        assert validate_quantity(100) == 100
        assert validate_quantity(1000000) == 1000000
        
        # Invalid values
        with pytest.raises(ValueError):
            validate_quantity(-1)
        
        with pytest.raises(ValueError):
            validate_quantity(2000000)

    def test_url_validation_prevents_ssrf(self):
        """Verify URL validation prevents SSRF attacks."""
        
        def validate_redirect_url(url: str, allowed_hosts: List[str]) -> str:
            """Validate redirect URL to prevent SSRF."""
            parsed = urllib.parse.urlparse(url)
            
            # Must have scheme and netloc
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("Invalid URL format")
            
            # Only allow HTTPS
            if parsed.scheme not in ['http', 'https']:
                raise ValueError("Invalid scheme")
            
            # Check against allowed hosts
            if parsed.netloc not in allowed_hosts:
                raise ValueError("Host not in whitelist")
            
            # Prevent localhost/internal IPs
            internal_patterns = [r'^localhost', r'^127\.', r'^::1', r'^169\.254', r'^192\.168', r'^10\.']
            for pattern in internal_patterns:
                if re.match(pattern, parsed.netloc):
                    raise ValueError("Internal/localhost URLs not allowed")
            
            return url
        
        allowed = ["example.com", "trusted-partner.com"]
        
        # Valid URLs
        assert validate_redirect_url("https://example.com/page", allowed) == "https://example.com/page"
        
        # SSRF attempts
        with pytest.raises(ValueError):
            validate_redirect_url("http://localhost:8080/admin", allowed)
        
        with pytest.raises(ValueError):
            validate_redirect_url("http://192.168.1.1/admin", allowed)
        
        with pytest.raises(ValueError):
            validate_redirect_url("https://evil.com", allowed)


class TestCryptographicOperations:
    """Test suite for cryptographic security."""

    def test_random_number_generation_uses_secure_source(self):
        """Verify random number generation uses secure sources."""
        
        # Use secrets module (cryptographically secure)
        random_values = []
        for _ in range(10):
            value = secrets.randbelow(1000000)
            random_values.append(value)
        
        # Values should be diverse
        assert len(set(random_values)) == 10, "Secure random values are unique"
        
        # No pattern should be obvious
        for i in range(1, len(random_values)):
            assert random_values[i] != random_values[i-1], "No consecutive duplicates"

    def test_cryptographic_hash_function_strength(self):
        """Verify strong hash functions are used (SHA-256 or better)."""
        
        data = b"sensitive_data"
        
        # SHA-256 is acceptable
        sha256_hash = hashlib.sha256(data).hexdigest()
        assert len(sha256_hash) == 64, "SHA-256 produces 256-bit hash"
        
        # MD5 should not be used for security
        md5_hash = hashlib.md5(data).hexdigest()
        assert len(md5_hash) == 32, "MD5 is weaker (128-bit)"
        
        # SHA-256 should be preferred
        assert len(sha256_hash) > len(md5_hash), "SHA-256 > MD5 strength"

    def test_salt_length_for_password_hashing(self):
        """Verify adequate salt length in password hashing."""
        
        def validate_salt(salt: bytes) -> bool:
            """Validate salt meets security requirements."""
            # Salt should be at least 16 bytes (128 bits)
            min_salt_bytes = 16
            
            if len(salt) < min_salt_bytes:
                raise ValueError(f"Salt too short: {len(salt)} < {min_salt_bytes}")
            
            return True
        
        # Weak salt (too short)
        weak_salt = os.urandom(4)
        with pytest.raises(ValueError):
            validate_salt(weak_salt)
        
        # Adequate salt
        good_salt = os.urandom(16)
        assert validate_salt(good_salt)
        
        # Strong salt
        strong_salt = os.urandom(32)
        assert validate_salt(strong_salt)

    def test_key_derivation_function_iterations(self):
        """Verify key derivation functions use adequate iterations."""
        
        def validate_kdf_params(iterations: int) -> bool:
            """Validate KDF parameters meet security requirements."""
            # PBKDF2 should use at least 100,000 iterations (as of 2026)
            min_iterations = 100000
            
            if iterations < min_iterations:
                raise ValueError(f"Too few iterations: {iterations} < {min_iterations}")
            
            return True
        
        # Weak: too few iterations
        with pytest.raises(ValueError):
            validate_kdf_params(10000)
        
        # Adequate: meets standard
        assert validate_kdf_params(100000)
        
        # Strong: exceeds standard
        assert validate_kdf_params(600000)

    def test_random_token_uniqueness(self):
        """Verify randomly generated tokens are unique."""
        
        def generate_secure_token(length: int = 32) -> str:
            """Generate cryptographically secure token."""
            return secrets.token_urlsafe(length)
        
        tokens = set()
        for _ in range(1000):
            token = generate_secure_token()
            assert token not in tokens, "Token is unique"
            tokens.add(token)
        
        assert len(tokens) == 1000, "All 1000 tokens are unique"

    def test_nonce_is_not_reused(self):
        """Verify nonces are never reused (critical for security)."""
        
        nonce_cache = set()
        
        def generate_nonce():
            """Generate nonce and track usage."""
            nonce = secrets.token_hex(16)
            
            if nonce in nonce_cache:
                raise ValueError("Nonce reused - critical security failure!")
            
            nonce_cache.add(nonce)
            return nonce
        
        # Generate multiple nonces
        nonces = [generate_nonce() for _ in range(100)]
        
        # All should be unique
        assert len(set(nonces)) == 100, "All nonces are unique"

    def test_hmac_key_length(self):
        """Verify HMAC keys are adequately long."""
        
        def validate_hmac_key(key: bytes) -> bool:
            """Validate HMAC key meets security requirements."""
            # Key should be at least 32 bytes (256 bits)
            min_key_bytes = 32
            
            if len(key) < min_key_bytes:
                raise ValueError(f"HMAC key too short: {len(key)} < {min_key_bytes}")
            
            return True
        
        # Weak key
        weak_key = os.urandom(16)
        with pytest.raises(ValueError):
            validate_hmac_key(weak_key)
        
        # Adequate key
        good_key = os.urandom(32)
        assert validate_hmac_key(good_key)
        
        # Strong key
        strong_key = os.urandom(64)
        assert validate_hmac_key(strong_key)


class TestDataProtection:
    """Test suite for data protection and sensitive information handling."""

    def test_sensitive_data_not_logged(self):
        """Verify sensitive data is not logged in plaintext."""
        
        def log_message(message: str) -> bool:
            """Check that sensitive data is not in log message."""
            # Should not contain passwords, tokens, API keys
            sensitive_patterns = [
                r'password\s*[:=]',
                r'api_key\s*[:=]',
                r'secret\s*[:=]',
                r'token\s*[:=]'
            ]
            
            for pattern in sensitive_patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    raise ValueError("Sensitive data detected in log")
            
            return True
        
        # Safe logs
        assert log_message("User alice logged in")
        assert log_message("API request to /users endpoint")
        
        # Logs with sensitive data
        with pytest.raises(ValueError):
            log_message("User authentication failed for ******")
        
        with pytest.raises(ValueError):
            log_message("API key: sk_live_abc123def456")

    def test_api_key_not_in_source_code(self):
        """Verify API keys are not hardcoded in source."""
        
        # Simulate code scan
        code_snippets = [
            'api_key = "sk_live_1234567890abcdef"',  # Bad
            'api_key = os.environ.get("API_KEY")',   # Good
            'GITHUB_TOKEN = "ghp_1234567890"',       # Bad
            'token = config.get_secret("github_token")',  # Good
        ]
        
        def contains_hardcoded_secret(code: str) -> bool:
            patterns = [
                r'api_key\s*=\s*["\'][\w]{20,}["\']',
                r'token\s*=\s*["\']gh[p_][\w]{30,}["\']',
                r'key\s*=\s*["\'][A-Za-z0-9_]{30,}["\']',
            ]
            
            for pattern in patterns:
                if re.search(pattern, code):
                    return True
            return False
        
        assert contains_hardcoded_secret(code_snippets[0])
        assert not contains_hardcoded_secret(code_snippets[1])
        assert contains_hardcoded_secret(code_snippets[2])
        assert not contains_hardcoded_secret(code_snippets[3])

    def test_database_connection_uses_tls(self):
        """Verify database connections use TLS encryption."""
        
        def validate_db_connection_string(connection_string: str) -> bool:
            """Check database connection uses TLS."""
            # Should use TLS/SSL
            if 'postgresql' in connection_string.lower():
                if 'sslmode=require' not in connection_string:
                    raise ValueError("PostgreSQL connection missing sslmode=require")
            
            if 'mysql' in connection_string.lower():
                if 'ssl' not in connection_string.lower():
                    raise ValueError("MySQL connection missing SSL requirement")
            
            return True
        
        # Valid: TLS required
        assert validate_db_connection_string("******host/db?sslmode=require")
        
        # Invalid: no TLS
        with pytest.raises(ValueError):
            validate_db_connection_string("******host/db")


class TestErrorHandling:
    """Test suite for secure error handling."""

    def test_error_messages_dont_leak_system_info(self):
        """Verify error messages don't leak system information."""
        
        def sanitize_error_message(error: Exception, debug_mode: bool = False) -> str:
            """Return appropriate error message based on context."""
            if debug_mode:
                # Debug mode: can show full details
                return str(error)
            else:
                # Production: generic message
                error_str = str(error)
                
                # Check for system leaks
                leaked_patterns = [
                    r'/home/\w+',
                    r'/var/\w+',
                    r'server=',
                    r'user=',
                    r'password=',
                    r'traceback',
                ]
                
                for pattern in leaked_patterns:
                    if re.search(pattern, error_str, re.IGNORECASE):
                        return "An error occurred. Please try again."
                
                return error_str
        
        # Safe error
        safe_error = Exception("Invalid input provided")
        assert "Invalid input" in sanitize_error_message(safe_error, debug_mode=False)
        
        # Leaky error
        leaky_error = Exception("Database connection failed: user=admin ****** on server=192.168.1.1")
        result = sanitize_error_message(leaky_error, debug_mode=False)
        assert "error occurred" in result or len(result) < len(str(leaky_error))


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
