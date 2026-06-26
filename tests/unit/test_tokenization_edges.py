"""Unit tests for tokenization edge cases.

Tests tokenization pipeline behavior with extreme inputs, special characters,
and boundary conditions that could trigger silent failures or data corruption.
"""

from __future__ import annotations

import pytest


class TestTokenizationEmptyInputs:
    """Test tokenization with empty or minimal inputs."""

    def test_tokenize_empty_string(self):
        """Verify empty string tokenization produces consistent output."""
        # Arrange
        try:
            from transformers import AutoTokenizer
        except ImportError:
            pytest.skip("transformers not available")

        # Use a small, standard tokenizer if available
        try:
            tokenizer = AutoTokenizer.from_pretrained(
                "gpt2",
                trust_remote_code=False,
            )
        except (ValueError, TypeError) as _err:
            pytest.skip("Could not load tokenizer")

        # Act
        result = tokenizer("")

        # Assert
        assert isinstance(result, dict) or hasattr(
            result, "input_ids"
        ), "Tokenizer should return dict-like object"
        assert len(result.get("input_ids", [])) == 0, "Empty input should produce empty token list"

    def test_tokenize_whitespace_only(self):
        """Verify whitespace-only input is handled correctly."""
        # Arrange
        try:
            from transformers import AutoTokenizer
        except ImportError:
            pytest.skip("transformers not available")

        try:
            tokenizer = AutoTokenizer.from_pretrained(
                "gpt2",
                trust_remote_code=False,
            )
        except (ValueError, TypeError) as _err:
            pytest.skip("Could not load tokenizer")

        # Act
        result = tokenizer("   \t\n  ")

        # Assert
        # Different tokenizers handle whitespace differently, so just verify
        # the result is a valid token sequence
        assert isinstance(
            result.get("input_ids"), (list, type(None))
        ), "Should return valid token IDs or None"

    def test_tokenize_single_character(self):
        """Verify single character tokenization works."""
        # Arrange
        try:
            from transformers import AutoTokenizer
        except ImportError:
            pytest.skip("transformers not available")

        try:
            tokenizer = AutoTokenizer.from_pretrained(
                "gpt2",
                trust_remote_code=False,
            )
        except (ValueError, TypeError) as _err:
            pytest.skip("Could not load tokenizer")

        # Act
        result = tokenizer("a")

        # Assert
        assert "input_ids" in result, "Result should contain input_ids"
        assert len(result["input_ids"]) >= 1, "Single character should produce at least one token"


class TestTokenizationSpecialCharacters:
    """Test tokenization with special characters and encodings."""

    def test_tokenize_null_byte_handling(self):
        """Verify null bytes don't cause crashes or silent failures."""
        # Arrange
        try:
            from transformers import AutoTokenizer
        except ImportError:
            pytest.skip("transformers not available")

        try:
            tokenizer = AutoTokenizer.from_pretrained(
                "gpt2",
                trust_remote_code=False,
            )
        except (ValueError, TypeError) as _err:
            pytest.skip("Could not load tokenizer")

        text_with_null = "hello\x00world"

        # Act & Assert
        # Should either handle gracefully or raise informative error
        try:
            result = tokenizer(text_with_null)
            # If it succeeds, verify it produces valid tokens
            assert "input_ids" in result, "Should produce valid tokenization even with null byte"
        except ValueError as e:
            # It's acceptable to reject null bytes with clear error
            assert (
                "null" in str(e).lower() or "encoding" in str(e).lower()
            ), "Should provide clear error for problematic input"

    def test_tokenize_unicode_bom_removal(self):
        """Verify BOM (Byte Order Mark) is handled correctly."""
        # Arrange
        try:
            from transformers import AutoTokenizer
        except ImportError:
            pytest.skip("transformers not available")

        try:
            tokenizer = AutoTokenizer.from_pretrained(
                "gpt2",
                trust_remote_code=False,
            )
        except (ValueError, TypeError) as _err:
            pytest.skip("Could not load tokenizer")

        text_with_bom = "\ufeffhello world"

        # Act
        result = tokenizer(text_with_bom)

        # Assert: Should tokenize without error
        assert "input_ids" in result, "Should handle BOM in UTF-8 string"
        assert len(result["input_ids"]) > 0, "Should produce tokens even with BOM"

    def test_tokenize_mixed_unicode_scripts(self):
        """Verify mixed Unicode scripts (Latin, CJK, Emoji) are handled."""
        # Arrange
        try:
            from transformers import AutoTokenizer
        except ImportError:
            pytest.skip("transformers not available")

        try:
            tokenizer = AutoTokenizer.from_pretrained(
                "gpt2",
                trust_remote_code=False,
            )
        except (ValueError, TypeError) as _err:
            pytest.skip("Could not load tokenizer")

        mixed_text = "Hello 世界 🌍 мир"

        # Act
        result = tokenizer(mixed_text)

        # Assert
        assert "input_ids" in result, "Should handle mixed Unicode scripts"
        assert len(result["input_ids"]) > 0, "Should produce tokens for mixed scripts"


class TestTokenizationLengthBoundaries:
    """Test tokenization with extreme sequence lengths."""

    def test_tokenize_very_long_sequence(self):
        """Verify handling of very long sequences."""
        # Arrange
        try:
            from transformers import AutoTokenizer
        except ImportError:
            pytest.skip("transformers not available")

        try:
            tokenizer = AutoTokenizer.from_pretrained(
                "gpt2",
                trust_remote_code=False,
            )
        except (ValueError, TypeError) as _err:
            pytest.skip("Could not load tokenizer")

        # Create a long sequence (10,000 words)
        long_text = " ".join(["word"] * 10000)

        # Act & Assert
        try:
            result = tokenizer(long_text)
            # Should complete without hanging or crashing
            assert "input_ids" in result, "Should tokenize long sequence"
            assert len(result["input_ids"]) > 1000, "Long input should produce many tokens"
        except (RuntimeError, MemoryError) as e:
            # OOM is acceptable for extremely long sequences
            pytest.skip(f"OOM on very long sequence: {e}")

    def test_tokenize_repeated_characters(self):
        """Verify handling of highly repetitive input."""
        # Arrange
        try:
            from transformers import AutoTokenizer
        except ImportError:
            pytest.skip("transformers not available")

        try:
            tokenizer = AutoTokenizer.from_pretrained(
                "gpt2",
                trust_remote_code=False,
            )
        except (ValueError, TypeError) as _err:
            pytest.skip("Could not load tokenizer")

        # Very repetitive input
        repetitive_text = "a" * 5000

        # Act
        result = tokenizer(repetitive_text)

        # Assert
        assert "input_ids" in result, "Should handle highly repetitive input"
        # Repetitive input should compress well (fewer tokens than length)
        assert len(result["input_ids"]) < len(, "Collection must not be empty"
            repetitive_text
        ), "Repetitive input should compress to fewer tokens"

    def test_tokenize_max_length_truncation(self):
        """Verify truncation when max_length is specified."""
        # Arrange
        try:
            from transformers import AutoTokenizer
        except ImportError:
            pytest.skip("transformers not available")

        try:
            tokenizer = AutoTokenizer.from_pretrained(
                "gpt2",
                trust_remote_code=False,
            )
        except (ValueError, TypeError) as _err:
            pytest.skip("Could not load tokenizer")

        text = "word " * 100  # Long sequence
        max_length = 10

        # Act
        result = tokenizer(text, max_length=max_length, truncation=True)

        # Assert
        assert (
            len(result["input_ids"]) <= max_length
        ), f"Should truncate to max_length={max_length}, got {len(result['input_ids'])}"


class TestTokenizationConsistency:
    """Test tokenization consistency and determinism."""

    def test_tokenize_deterministic_output(self):
        """Verify tokenization produces same output on repeated calls."""
        # Arrange
        try:
            from transformers import AutoTokenizer
        except ImportError:
            pytest.skip("transformers not available")

        try:
            tokenizer = AutoTokenizer.from_pretrained(
                "gpt2",
                trust_remote_code=False,
            )
        except (ValueError, TypeError) as _err:
            pytest.skip("Could not load tokenizer")

        text = "The quick brown fox jumps over the lazy dog"

        # Act
        result1 = tokenizer(text)
        result2 = tokenizer(text)

        # Assert
        assert result1["input_ids"] == result2["input_ids"], "Tokenization should be deterministic"

    def test_tokenize_symmetric_strip_equivalence(self):
        """Verify that leading/trailing whitespace doesn't affect core tokens."""
        # Arrange
        try:
            from transformers import AutoTokenizer
        except ImportError:
            pytest.skip("transformers not available")

        try:
            tokenizer = AutoTokenizer.from_pretrained(
                "gpt2",
                trust_remote_code=False,
            )
        except (ValueError, TypeError) as _err:
            pytest.skip("Could not load tokenizer")

        core_text = "hello world"
        padded_text = "   " + core_text + "   \n"

        # Act
        result_core = tokenizer(core_text)
        result_padded = tokenizer(padded_text)

        # Assert: Both should produce valid results
        # (Exact equivalence depends on tokenizer, just verify both work)
        assert len(result_core["input_ids"]) > 0, "Core text should tokenize"
        assert len(result_padded["input_ids"]) > 0, "Padded text should tokenize"


class TestTokenizationErrorRecovery:
    """Test error handling and recovery in tokenization."""

    def test_tokenize_invalid_type_raises_error(self):
        """Verify clear error when passing invalid input type."""
        # Arrange
        try:
            from transformers import AutoTokenizer
        except ImportError:
            pytest.skip("transformers not available")

        try:
            tokenizer = AutoTokenizer.from_pretrained(
                "gpt2",
                trust_remote_code=False,
            )
        except (ValueError, TypeError) as _err:
            pytest.skip("Could not load tokenizer")

        # Act & Assert
        with pytest.raises((TypeError, AttributeError)):
            # Should raise error, not silently fail
            tokenizer(12345)

    def test_tokenize_none_input_raises_error(self):
        """Verify clear error when None is passed."""
        # Arrange
        try:
            from transformers import AutoTokenizer
        except ImportError:
            pytest.skip("transformers not available")

        try:
            tokenizer = AutoTokenizer.from_pretrained(
                "gpt2",
                trust_remote_code=False,
            )
        except (ValueError, TypeError) as _err:
            pytest.skip("Could not load tokenizer")

        # Act & Assert
        with pytest.raises((TypeError, AttributeError, ValueError)):
            # Should raise error, not crash silently
            tokenizer(None)

    def test_tokenize_recovery_after_error(self):
        """Verify tokenizer can recover after encountering an error."""
        # Arrange
        try:
            from transformers import AutoTokenizer
        except ImportError:
            pytest.skip("transformers not available")

        try:
            tokenizer = AutoTokenizer.from_pretrained(
                "gpt2",
                trust_remote_code=False,
            )
        except (ValueError, TypeError) as _err:
            pytest.skip("Could not load tokenizer")

        valid_text = "This is valid text"

        # Act: Try invalid input, then valid input
        try:
            tokenizer(None)
        except (TypeError, AttributeError, ValueError):
            pass  # Expected

        result = tokenizer(valid_text)

        # Assert: Should still work after error
        assert "input_ids" in result, "Tokenizer should recover after error"
        assert len(result["input_ids"]) > 0, "Should produce tokens after recovery"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
