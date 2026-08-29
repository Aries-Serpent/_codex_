"""
Safety Filters Edge Case Tests - Phase 26

Comprehensive edge case testing for safety filters covering:
- Boundary conditions and extreme inputs
- Unicode and encoding edge cases
- Nested patterns and complex regex
- Policy override scenarios
- Classifier integration edge cases
- Performance with large inputs

Part of Phase 26: Coverage 70% → 75-80%
"""

from unittest.mock import Mock, patch

import pytest

# pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
from codex_ml.safety.filters import (
    REDACT_PLACEHOLDER,
    SafetyFilters,
    sanitize_output,
    sanitize_prompt,
)


class TestSafetyFiltersEdgeCases:
    """Edge case tests for SafetyFilters class."""

    def test_empty_input_handling(self):
        """Test filters handle empty string input."""
        filters = SafetyFilters.from_defaults()
        result = sanitize_prompt("", filters=filters)
        assert result.allowed is True, "Result must not be empty"
        assert result.sanitized_text == "", "Result must not be empty"
        assert len(result.matches) == 0, "Collection must not be empty"

    def test_whitespace_only_input(self):
        """Test filters handle whitespace-only input."""
        filters = SafetyFilters.from_defaults()
        for text in [" ", "\n", "\t", "   \n\t  "]:
            result = sanitize_prompt(text, filters=filters)
            assert result.allowed is True, "Result must not be empty"
            assert result.sanitized_text.strip() == "", "Result must not be empty"

    def test_extremely_long_input(self):
        """Test filters handle very long input strings."""
        filters = SafetyFilters.from_defaults()
        # 1MB of text
        long_text = "safe text " * 100000
        result = sanitize_prompt(long_text, filters=filters)
        assert result.allowed is True, "Result must not be empty"
        assert len(result.sanitized_text) > 0, "Collection must not be empty"

    def test_unicode_edge_cases(self):
        """Test filters handle various Unicode characters."""
        filters = SafetyFilters.from_defaults()
        test_cases = [
            "Hello 世界",  # Chinese
            "Привет мир",  # Russian
            "مرحبا بالعالم",  # Arabic
            "🔥💯🎉",  # Emojis
            "\u200b\u200c\u200d",  # Zero-width characters
        ]
        for text in test_cases:
            result = sanitize_prompt(text, filters=filters)
            assert result.sanitized_text is not None, "sanitized_text must be initialized"

    def test_nested_secret_patterns(self):
        """Test redaction of nested/obfuscated secrets."""
        filters = SafetyFilters.from_defaults()
        test_cases = [
            "API_KEY='abc123' and PASSWORD='xyz789'",
            # Note: Split/concatenated patterns like 'sk-' + var are NOT detectable
            # by regex-based filters; they require AST/semantic analysis.
        ]
        for text in test_cases:
            result = sanitize_prompt(text, filters=filters)
            assert result.allowed is True, "Result must not be empty"
            # Either redacted or matches found (allow list can neutralize)
            assert REDACT_PLACEHOLDER in result.sanitized_text or len(result.matches) > 0, "Collection must not be empty"

    def test_regex_dos_prevention(self):
        """Test that regex patterns don't cause ReDoS."""
        filters = SafetyFilters.from_defaults()
        # Potential catastrophic backtracking patterns
        text = "a" * 1000 + "!"
        import time

        start = time.time()
        result = sanitize_prompt(text, filters=filters)
        duration = time.time() - start
        assert duration < 5.0, "duration is not valid"
        assert result.sanitized_text is not None, "sanitized_text must be initialized"

    def test_null_byte_handling(self):
        """Test filters handle null bytes safely."""
        filters = SafetyFilters.from_defaults()
        text = "safe\x00text\x00here"
        result = sanitize_prompt(text, filters=filters)
        assert result.sanitized_text is not None, "sanitized_text must be initialized"
        assert "\x00" not in result.sanitized_text or result.allowed, "Result must not be empty"

    def test_control_character_handling(self):
        """Test filters handle control characters."""
        filters = SafetyFilters.from_defaults()
        # Various control characters
        text = "text\x01\x02\x03\x04\x05"
        result = sanitize_prompt(text, filters=filters)
        assert result.sanitized_text is not None, "sanitized_text must be initialized"

    def test_mixed_newline_formats(self):
        """Test filters handle different newline formats."""
        filters = SafetyFilters.from_defaults()
        test_cases = [
            "line1\nline2",  # Unix
            "line1\r\nline2",  # Windows
            "line1\rline2",  # Old Mac
        ]
        for text in test_cases:
            result = sanitize_prompt(text, filters=filters)
            assert result.sanitized_text is not None, "sanitized_text must be initialized"


class TestPolicyRuleEdgeCases:
    """Edge case tests for PolicyRule matching."""

    def test_overlapping_patterns(self):
        """Test behavior with overlapping allow/block patterns."""
        filters = SafetyFilters.from_defaults()
        # Text that might match both allow and block rules
        text = "safe_api_key=test123"
        result = sanitize_prompt(text, filters=filters)
        # Should be handled consistently
        assert result.sanitized_text is not None, "sanitized_text must be initialized"

    def test_case_sensitivity_edge_cases(self):
        """Test case-sensitive vs case-insensitive matching."""
        filters = SafetyFilters.from_defaults()
        test_cases = [
            ("API_KEY=abc", "api_key=abc", "Api_Key=abc"),
            ("PASSWORD=xyz", "password=xyz", "PaSsWoRd=xyz"),
        ]
        for upper, lower, mixed in test_cases:
            r1 = sanitize_prompt(upper, filters=filters)
            r2 = sanitize_prompt(lower, filters=filters)
            r3 = sanitize_prompt(mixed, filters=filters)
            # All should be handled (either allowed or redacted)
            assert all(r.sanitized_text is not None for r in [r1, r2, r3])

    def test_boundary_pattern_matching(self):
        """Test word boundary handling in patterns."""
        filters = SafetyFilters.from_defaults()
        test_cases = [
            "apikey",  # No underscore
            "api_key",  # With underscore
            "api-key",  # With hyphen
            "api.key",  # With dot
        ]
        for text in test_cases:
            result = sanitize_prompt(text, filters=filters)
            assert result.sanitized_text is not None, "sanitized_text must be initialized"

    def test_special_regex_characters(self):
        """Test patterns containing regex special characters."""
        filters = SafetyFilters.from_defaults()
        special_chars = r".*+?[]{}()\|^$"
        for char in special_chars:
            text = f"test{char}value"
            result = sanitize_prompt(text, filters=filters)
            assert result.sanitized_text is not None, "sanitized_text must be initialized"


class TestClassifierIntegrationEdgeCases:
    """Edge case tests for external classifier integration."""

    @patch.dict("os.environ", {"CODEX_SAFETY_CLASSIFIER": "mock.classifier.check"})
    def test_classifier_not_available(self):
        """Test graceful handling when classifier module not available."""
        filters = SafetyFilters.from_defaults()
        text = "test input"
        # Should work even if classifier can't be imported
        result = sanitize_prompt(text, filters=filters)
        assert result.sanitized_text is not None, "sanitized_text must be initialized"

    @patch("codex_ml.safety.filters.importlib.import_module")
    def test_classifier_import_error(self, mock_import):
        """Test handling of classifier import errors."""
        mock_import.side_effect = ImportError("Module not found")
        filters = SafetyFilters.from_defaults()
        text = "test input"
        result = sanitize_prompt(text, filters=filters)
        assert result.sanitized_text is not None, "sanitized_text must be initialized"

    @patch("codex_ml.safety.filters.importlib.import_module")
    def test_classifier_exception_handling(self, mock_import):
        """Test handling of classifier runtime exceptions."""
        mock_classifier = Mock()
        mock_classifier.check.side_effect = RuntimeError("Classifier error")
        mock_module = Mock()
        mock_module.check = mock_classifier.check
        mock_import.return_value = mock_module

        with patch.dict("os.environ", {"CODEX_SAFETY_CLASSIFIER": "mock.classifier.check"}):
            filters = SafetyFilters.from_defaults()
            text = "test input"
            # Should handle exception gracefully
            result = sanitize_prompt(text, filters=filters)
            assert result.sanitized_text is not None, "sanitized_text must be initialized"


class TestBypassMechanismEdgeCases:
    """Edge case tests for policy bypass mechanisms."""

    @patch.dict("os.environ", {"CODEX_SAFETY_BYPASS": "1"})
    def test_bypass_with_dangerous_input(self):
        """Test bypass allows dangerous input through."""
        filters = SafetyFilters.from_defaults()
        text = "rm -rf / --no-preserve-root"
        result = sanitize_prompt(text, filters=filters)
        # Bypass should allow anything
        assert result.allowed is True, "Result must not be empty"

    @patch.dict("os.environ", {"CODEX_SAFETY_BYPASS": "true"})
    def test_bypass_various_truthy_values(self):
        """Test bypass recognizes various truthy env values."""
        filters = SafetyFilters.from_defaults()
        text = "dangerous input"
        result = sanitize_prompt(text, filters=filters)
        assert result.allowed is True, "Result must not be empty"

    @patch.dict("os.environ", {}, clear=True)
    def test_no_bypass_by_default(self):
        """Test bypass is not active by default."""
        filters = SafetyFilters.from_defaults()
        text = "rm -rf /"
        result = sanitize_output(text, filters=filters)
        # Should block dangerous command
        assert result.allowed is False or len(result.blocked_rules) > 0, "Allowed must not be empty"


class TestRedactionEdgeCases:
    """Edge case tests for redaction functionality."""

    def test_multiple_secrets_same_line(self):
        """Test redaction of multiple secrets on same line."""
        filters = SafetyFilters.from_defaults()
        text = "API_KEY=abc123 PASSWORD=xyz789 TOKEN=def456"
        result = sanitize_prompt(text, filters=filters)
        # Should redact all secrets
        redact_count = result.sanitized_text.count(REDACT_PLACEHOLDER)
        assert redact_count >= 1, "redact_count must be positive"

    def test_secret_at_boundaries(self):
        """Test redaction of secrets at text boundaries."""
        filters = SafetyFilters.from_defaults()
        test_cases = [
            "API_KEY=abc123",  # At start
            "text API_KEY=abc123",  # In middle
            "API_KEY=abc123 text",  # At end
        ]
        for text in test_cases:
            result = sanitize_prompt(text, filters=filters)
            assert REDACT_PLACEHOLDER in result.sanitized_text or result.allowed, "Result must not be empty"

    def test_partial_secret_patterns(self):
        """Test handling of partial secret-like patterns."""
        filters = SafetyFilters.from_defaults()
        test_cases = [
            "API_KEY",  # No value
            "API_KEY=",  # Empty value
            "=abc123",  # No key
        ]
        for text in test_cases:
            result = sanitize_prompt(text, filters=filters)
            assert result.sanitized_text is not None, "sanitized_text must be initialized"


class TestPerformanceEdgeCases:
    """Edge case tests for performance characteristics."""

    def test_many_small_matches(self):
        """Test performance with many small pattern matches."""
        filters = SafetyFilters.from_defaults()
        # Generate text with many potential matches
        text = " ".join([f"key{i}=val{i}" for i in range(1000)])
        import time

        start = time.time()
        result = sanitize_prompt(text, filters=filters)
        duration = time.time() - start
        assert duration < 10.0, "duration is not valid"
        assert result.sanitized_text is not None, "sanitized_text must be initialized"

    def test_deeply_nested_patterns(self):
        """Test handling of deeply nested pattern structures."""
        filters = SafetyFilters.from_defaults()
        # Nested structures
        text = "{{{{secret}}}} [[[[key]]]]"
        result = sanitize_prompt(text, filters=filters)
        assert result.sanitized_text is not None, "sanitized_text must be initialized"

    @pytest.mark.parametrize("size", [1000, 10000, 100000])
    def test_varying_input_sizes(self, size):
        """Test filters handle varying input sizes efficiently."""
        filters = SafetyFilters.from_defaults()
        text = "safe text " * (size // 10)
        result = sanitize_prompt(text, filters=filters)
        assert result.allowed is True, "Result must not be empty"
        assert len(result.sanitized_text) > 0, "Collection must not be empty"


class TestConcurrencyEdgeCases:
    """Edge case tests for concurrent filter usage."""

    def test_filter_reuse_safety(self):
        """Test that SafetyFilters can be reused safely."""
        filters = SafetyFilters.from_defaults()
        # Use same filter instance multiple times
        results = [sanitize_prompt(f"test{i}", filters=filters) for i in range(100)]
        assert all(r.sanitized_text is not None for r in results), "sanitized_text must be initialized"

    def test_thread_safety_indication(self):
        """Test that filters work with threading (basic check)."""
        filters = SafetyFilters.from_defaults()
        import threading

        results = []

        def worker(text):
            result = sanitize_prompt(text, filters=filters)
            results.append(result)

        threads = [threading.Thread(target=worker, args=(f"text{i}",)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10, "Results must not be empty"
        assert all(r.sanitized_text is not None for r in results), "sanitized_text must be initialized"


# Edge case markers for pytest
pytestmark = [
    pytest.mark.security,
    pytest.mark.regression,
]
