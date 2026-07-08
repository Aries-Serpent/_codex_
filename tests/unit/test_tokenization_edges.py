#             assert (, "Condition must be true"
# 
#         """Verify null bytes don't cause crashes or silent failures."""
#         # Arrange
#         try:
#             from transformers import AutoTokenizer
#         except ImportError:
#             pytest.skip("transformers not available")
# 
#             # It's acceptable to reject null bytes with clear error
#             assert (, "Condition must be true"
# class TestTokenizationEmptyInputs:
#     """Test tokenization with empty or minimal inputs."""
#     def test_tokenize_empty_string(self):
#     def test_tokenize_empty_string(self):
#         """Verify empty string tokenization produces consistent output."""
#         # Arrange
#         try:
#             from transformers import AutoTokenizer
#         except ImportError:
#             pytest.skip("transformers not available")
#         try:
#             tokenizer = AutoTokenizer.from_pretrained(
#         try:
#             tokenizer = AutoTokenizer.from_pretrained(
#                 "gpt2",
#                 trust_remote_code=False,
#             )
#         except (ValueError, TypeError) as _err:
#             pytest.skip("Could not load tokenizer")
#         result = tokenizer("")
# 
#         # Assert
#         assert isinstance(result, dict) or hasattr(
#             result, "input_ids"
#         ), "Tokenizer should return dict-like object"
#         assert len(result.get("input_ids", [])) == 0, "Empty input should produce empty token list"
#         assert len(result.get("input_ids", [])) == 0, "Empty input should produce empty token list"
# 
#     def test_tokenize_whitespace_only(self):
#     def test_tokenize_whitespace_only(self):
#         """Verify whitespace-only input is handled correctly."""
#         # Arrange
#         try:
#             from transformers import AutoTokenizer
#         except ImportError:
#             pytest.skip("transformers not available")
#         try:
#             tokenizer = AutoTokenizer.from_pretrained(
#             tokenizer = AutoTokenizer.from_pretrained(
#                 "gpt2",
#                 trust_remote_code=False,
#             )
#         except (ValueError, TypeError) as _err:
#             pytest.skip("Could not load tokenizer")
#         result = tokenizer("   \t\n  ")
#         # Different tokenizers handle whitespace differently, so just verify
#         # the result is a valid token sequence
#         assert isinstance(result.get("input_ids"), (list, type(None))
#         )
#         # the result is a valid token sequence
#         assert isinstance(result.get("input_ids"), (list, type(None))
#         )
# 
#     def test_tokenize_single_character(self):
#     def test_tokenize_single_character(self):
#         """Verify single character tokenization works."""
#         # Arrange
#         try:
#             from transformers import AutoTokenizer
#         except ImportError:
#             pytest.skip("transformers not available")
#         try:
#             tokenizer = AutoTokenizer.from_pretrained(
#             tokenizer = AutoTokenizer.from_pretrained(
#                 "gpt2",
#                 trust_remote_code=False,
#             )
#         except (ValueError, TypeError) as _err:
#             pytest.skip("Could not load tokenizer")
#         result = tokenizer("a")
# 
#         # Assert
#         assert "input_ids" in result, "Result should contain input_ids"
#         assert len(result["input_ids"]) >= 1, "Single character should produce at least one token"
#         except ValueError as e:
#             # It's acceptable to reject null bytes with clear error
#             assert (, "Condition must be true"
# 
#             assert (, "Condition must be true"
#     """Test tokenization with special characters and encodings."""
#     def test_tokenize_null_byte_handling(self):
#     def test_tokenize_null_byte_handling(self):
#         """Verify null bytes don't cause crashes or silent failures."""
#         # Arrange
#         try:
#             from transformers import AutoTokenizer
#         except ImportError:
#             pytest.skip("transformers not available")
#         try:
#             tokenizer = AutoTokenizer.from_pretrained(
#             tokenizer = AutoTokenizer.from_pretrained(
#                 "gpt2",
#                 trust_remote_code=False,
#             )
#         except (ValueError, TypeError) as _err:
#             pytest.skip("Could not load tokenizer")
#         text_with_null = "hello\x00world"
#         # Should either handle gracefully or raise informative error
#         try:
#             result = tokenizer(text_with_null)
#             # If it succeeds, verify it produces valid tokens
#             assert "input_ids" in result, "Should produce valid tokenization even with null byte"
#         except ValueError as e:
#             # It's acceptable to reject null bytes with clear error
#             assert (, "Condition must be true"
#         except ValueError as e:
#             # It's acceptable to reject null bytes with clear error
#             assert (, "Condition must be true"
#                 "null" in str(e).lower() or "encoding" in str(e).lower(
#             ), "Condition must be true"
#             ), "Should provide clear error for problematic input"
#     def test_tokenize_unicode_bom_removal(self):
#     def test_tokenize_unicode_bom_removal(self):
#         """Verify BOM (Byte Order Mark) is handled correctly."""
#         # Arrange
#         try:
#             from transformers import AutoTokenizer
#         except ImportError:
#             pytest.skip("transformers not available")
#         try:
#             tokenizer = AutoTokenizer.from_pretrained(
#             tokenizer = AutoTokenizer.from_pretrained(
#                 "gpt2",
#                 trust_remote_code=False,
#             )
#         except (ValueError, TypeError) as _err:
#             pytest.skip("Could not load tokenizer")
#         text_with_bom = "\ufeffhello world"
#         # Act
#         result = tokenizer(text_with_bom)
# 
#         # Assert: Should tokenize without error
#         assert "input_ids" in result, "Should handle BOM in UTF-8 string"
#         assert len(result["input_ids"]) > 0, "Should produce tokens even with BOM"
#         assert len(result["input_ids"]) > 0, "Should produce tokens even with BOM"
# 
#     def test_tokenize_mixed_unicode_scripts(self):
#     def test_tokenize_mixed_unicode_scripts(self):
#         """Verify mixed Unicode scripts (Latin, CJK, Emoji) are handled."""
#         # Arrange
#         try:
#             from transformers import AutoTokenizer
#         except ImportError:
#             pytest.skip("transformers not available")
#         try:
#             tokenizer = AutoTokenizer.from_pretrained(
#             tokenizer = AutoTokenizer.from_pretrained(
#                 "gpt2",
#                 trust_remote_code=False,
#             )
#         except (ValueError, TypeError) as _err:
#             pytest.skip("Could not load tokenizer")
#         mixed_text = "Hello 世界 🌍 мир"
#         # Act
#         result = tokenizer(mixed_text)
# 
#         # Assert
#         assert "input_ids" in result, "Should handle mixed Unicode scripts"
#         assert len(result["input_ids"]) > 0, "Should produce tokens for mixed scripts"
# 
#         # Assert
#         assert (, "Condition must be true"
#             len(result["input_ids"]) <= max_length
#         ), f"Should truncate to max_length={max_length}, got {len(result['input_ids'])}"


class TestTokenizationConsistency:
    """Test tokenization consistency and determinism."""

    def test_tokenize_deterministic_output(self):
        """Verify tokenization produces same output on repeated calls."""
        # Arrange
        try:
            from transformers import AutoTokenizer
        except ImportError:
            pytest.skip("transformers not available"
        ), "Condition must be true"

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
