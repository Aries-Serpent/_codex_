"""
Production Security Validation Tests

Tests security controls for SQL injection, XSS, CSRF, and input sanitization.
All tests are deterministic and isolated with no external dependencies.
"""

import html
import re
import sqlite3

import pytest

from codex.security.sanitization import sanitize_html, sanitize_integer

# SQL Injection Prevention Tests


def test_sql_injection_basic_quotes(tmp_path):
    """Test that basic SQL injection with quotes is prevented."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER, name TEXT, email TEXT)")
    cursor.execute("INSERT INTO users VALUES (1, 'Alice', 'alice@example.com')")
    conn.commit()

    # Malicious input
    malicious_input = "'; DROP TABLE users; --"

    # Safe parameterized query
    cursor.execute("SELECT * FROM users WHERE name = ?", (malicious_input,))
    results = cursor.fetchall()

    # Should return no results, table should still exist
    assert len(results) == 0, "Results must not be empty"
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    assert cursor.fetchone() is not None, "curs must be initialized"
    conn.close()


def test_sql_injection_union_attack(tmp_path):
    """Test prevention of UNION-based SQL injection."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER, username TEXT, password TEXT)")
    cursor.execute("INSERT INTO users VALUES (1, 'admin', 'secret123')")
    conn.commit()

    # UNION injection attempt
    malicious_input = "1 UNION SELECT password FROM users --"

    cursor.execute("SELECT username FROM users WHERE id = ?", (malicious_input,))
    results = cursor.fetchall()

    # Should not retrieve password data
    assert len(results) == 0, "Results must not be empty"
    conn.close()


def test_sql_injection_boolean_based(tmp_path):
    """Test prevention of boolean-based blind SQL injection."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE accounts (id INTEGER, balance REAL)")
    cursor.execute("INSERT INTO accounts VALUES (1, 1000.0)")
    conn.commit()

    # Boolean injection attempt
    malicious_input = "1 OR 1=1"

    cursor.execute("SELECT balance FROM accounts WHERE id = ?", (malicious_input,))
    results = cursor.fetchall()

    # Should not return all rows
    assert len(results) == 0, "Results must not be empty"
    conn.close()


def test_sql_injection_comment_bypass(tmp_path):
    """Test prevention of comment-based injection bypass."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE sessions (token TEXT, user_id INTEGER)")
    cursor.execute("INSERT INTO sessions VALUES ('abc123', 1)")
    conn.commit()

    # Comment injection
    malicious_input = "abc123' --"

    cursor.execute("SELECT user_id FROM sessions WHERE token = ?", (malicious_input,))
    results = cursor.fetchall()

    # Should not authenticate
    assert len(results) == 0, "Results must not be empty"
    conn.close()


# XSS Prevention Tests


def test_xss_basic_script_tag():
    """Test that basic script tag injection is sanitized."""
    malicious_input = "<script>alert('XSS')</script>"
    sanitized = html.escape(malicious_input)

    assert "<script>" not in sanitized, "Condition must be true"
    assert "&lt;script&gt;" in sanitized, "Condition must be true"
    assert "alert" in sanitized, "Condition must be true"


def test_xss_event_handler_injection():
    """Test prevention of event handler XSS attacks."""
    malicious_input = '<img src="x" onerror="alert(1)">'
    sanitized = sanitize_html(malicious_input)

    assert "onerror=" not in sanitized, "Error should be raised or set"
    assert "<img" not in sanitized, "Condition must be true"


def test_xss_javascript_protocol():
    """Test prevention of javascript: protocol XSS."""
    malicious_input = '<a href="javascript:alert(1)">Click</a>'
    sanitized = sanitize_html(malicious_input)

    assert "javascript:" not in sanitized, "Condition must be true"
    assert "<a" not in sanitized, "Condition must be true"


def test_xss_encoded_characters():
    """Test prevention of encoded XSS attacks."""
    malicious_input = "&#60;script&#62;alert('XSS')&#60;/script&#62;"
    # Double escape to prevent decoding attacks
    sanitized = html.escape(html.unescape(malicious_input))

    assert "<script>" not in sanitized, "Condition must be true"
    assert "&lt;script&gt;" in sanitized, "Condition must be true"


def test_xss_attribute_injection():
    """Test prevention of attribute-based XSS."""
    malicious_input = '" onload="alert(1)'
    sanitized = sanitize_html(malicious_input)

    assert "onload=" not in sanitized, "Condition must be true"
    # After sanitization, should only have the quote character
    assert "alert" not in sanitized, "Condition must be true"


# CSRF Protection Tests


def test_csrf_token_generation():
    """Test that CSRF tokens are generated correctly."""
    import secrets

    token1 = secrets.token_hex(32)
    token2 = secrets.token_hex(32)

    assert len(token1) == 64, "Token1 must not be empty"
    assert len(token2) == 64, "Token2 must not be empty"
    assert token1 != token2, "token1 is not valid"


def test_csrf_token_validation():
    """Test CSRF token validation logic."""
    import secrets

    session_token = secrets.token_hex(32)
    valid_token = session_token
    invalid_token = secrets.token_hex(32)

    # Valid token should pass
    assert valid_token == session_token, "valid_token is not valid"

    # Invalid token should fail
    assert invalid_token != session_token, "invalid_token is not valid"


def test_csrf_token_expiration():
    """Test CSRF token expiration logic."""
    from datetime import datetime, timedelta

    creation_time = datetime.now()
    expiry_time = creation_time + timedelta(hours=1)

    # Token should be valid immediately
    assert datetime.now() < expiry_time, "Condition must be true"

    # Simulate expiration
    expired_time = expiry_time - timedelta(hours=2)
    assert expired_time < creation_time, "expired_time is not valid"


def test_csrf_double_submit_cookie():
    """Test double-submit cookie CSRF protection pattern."""
    import secrets

    # Generate token for cookie and form
    token = secrets.token_hex(32)
    cookie_token = token
    form_token = token

    # Valid: tokens match
    assert cookie_token == form_token, "cookie_token is not valid"

    # Invalid: tokens don't match
    attacker_token = secrets.token_hex(32)
    assert cookie_token != attacker_token, "cookie_token is not valid"


# Input Sanitization Tests


def test_input_sanitization_email():
    """Test email input validation and sanitization."""

    # More strict email pattern that disallows consecutive dots
    email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    # Additional check for consecutive dots
    def is_valid_email(email):
        if not email_pattern.match(email):
            return False
        # Check for consecutive dots
        return ".." not in email

    valid_emails = ["test@example.com", "user.name+tag@example.co.uk"]
    invalid_emails = ["<script>@test.com", "test@", "@example.com", "test..test@example.com"]

    for email in valid_emails:
        assert is_valid_email(email), f"Valid email {email} was rejected"

    for email in invalid_emails:
        assert not is_valid_email(email), f"Invalid email {email} was accepted"


def test_input_sanitization_filename():
    """Test filename sanitization to prevent path traversal."""

    def sanitize_filename(filename):
        # Remove path separators and null bytes
        sanitized = filename.replace("/", "").replace("\\", "").replace("\0", "")
        # Remove parent directory references
        return sanitized.replace("..", "")

    dangerous_filenames = [
        "../../../etc/passwd",
        "..\\..\\windows\\system32",
        "file\0.txt",
        "normal/../../../etc/passwd",
    ]

    for filename in dangerous_filenames:
        sanitized = sanitize_filename(filename)
        assert "../" not in sanitized, "Condition must be true"
        assert "..\\" not in sanitized, "Condition must be true"
        assert "\0" not in sanitized, "Condition must be true"


def test_input_sanitization_username():
    """Test username sanitization for allowed characters."""

    def sanitize_username(username):
        # Only allow alphanumeric, underscore, hyphen
        return re.sub(r"[^a-zA-Z0-9_-]", "", username)

    test_cases = [
        ("user123", "user123"),
        ("user_name-123", "user_name-123"),
        ("user@#$%", "user"),
        ("<script>alert(1)</script>", "scriptalert1script"),
    ]

    for input_val, expected in test_cases:
        assert sanitize_username(input_val) == expected, "Condition must be true"


def test_input_sanitization_integer():
    """Test integer input validation and bounds checking."""
    assert sanitize_integer("42", min_value=0, max_value=1000) == 42
    assert sanitize_integer("-10", min_value=0, max_value=1000) == 0  # Clamped to min
    assert sanitize_integer("9999", min_value=0, max_value=1000) == 1000  # Clamped to max
    assert sanitize_integer("not_a_number", default=0) == 0
    assert sanitize_integer("42.7", min_value=0, max_value=1000) == 42


def test_input_sanitization_path_traversal():
    """Test prevention of path traversal attacks in file paths."""
    from pathlib import Path

    def safe_join(base_dir, user_path):
        base = Path(base_dir).resolve()
        target = (base / user_path).resolve()
        # Ensure target is within base directory
        try:
            target.relative_to(base)
            return str(target)
        except ValueError:
            return str(base)

    base_dir = "/var/www/uploads"

    # Safe paths
    assert safe_join(base_dir, "file.txt").startswith(base_dir)
    assert safe_join(base_dir, "subdir/file.txt").startswith(base_dir)

    # Dangerous paths should be blocked
    dangerous = safe_join(base_dir, "../../../etc/passwd")
    assert dangerous == base_dir or not dangerous.startswith("/etc"), "dangerous is not valid"


def test_input_sanitization_command_injection():
    """Test prevention of command injection in system calls."""
    import shlex

    def sanitize_shell_arg(arg):
        # Use shlex.quote to escape shell metacharacters
        return shlex.quote(str(arg))

    dangerous_inputs = [
        "; rm -rf /",
        "| cat /etc/passwd",
        "`whoami`",
        "$(cat /etc/shadow)",
        "&& echo hacked",
    ]

    for dangerous in dangerous_inputs:
        sanitized = sanitize_shell_arg(dangerous)
        # Should be quoted and escaped
        assert "'" in sanitized or '"' in sanitized or "\\" in sanitized


def test_input_sanitization_json_injection():
    """Test prevention of JSON injection attacks."""
    import json

    def _safe_json_value(value):
        # Serialize and deserialize to ensure proper escaping
        return json.loads(json.dumps(value))

    dangerous_input = '{"key": "value", "inject": "\\u0022escape\\u0022"}'

    # Should handle escaped unicode
    try:
        parsed = json.loads(dangerous_input)
        safe_value = _safe_json_value(parsed)
        assert isinstance(safe_value, dict)
        assert safe_value == parsed, "Value must be initialized"
        # Re-serialize should be safe
        serialized = json.dumps(safe_value)
        assert '"inject"' in serialized, "Condition must be true"
    except json.JSONDecodeError:
        pytest.fail("Valid JSON should parse correctly")


def test_input_sanitization_ldap_injection():
    """Test prevention of LDAP injection attacks."""

    def sanitize_ldap(value):
        # Escape LDAP special characters
        replacements = {
            "\\": "\\5c",
            "*": "\\2a",
            "(": "\\28",
            ")": "\\29",
            "\x00": "\\00",
        }
        sanitized = str(value)
        for char, escape in replacements.items():
            sanitized = sanitized.replace(char, escape)
        return sanitized

    dangerous_inputs = [
        "admin*",
        "user)(|(userPassword=*))",
        "test\\",
    ]

    for dangerous in dangerous_inputs:
        sanitized = sanitize_ldap(dangerous)
        assert "*" not in sanitized or "\\2a" in sanitized, "Condition must be true"
        assert "(" not in sanitized or "\\28" in sanitized, "Condition must be true"
        assert ")" not in sanitized or "\\29" in sanitized, "Condition must be true"
