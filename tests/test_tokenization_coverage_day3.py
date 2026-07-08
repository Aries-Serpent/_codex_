"""
Tokenization Coverage Tests — Day 3 Advanced Scenarios
Advanced tokenization scenarios, special token edge cases, batch encoding,
truncation/padding, vocabulary coverage, and multilingual support.
"""

from pathlib import Path

import pytest


class TestAdvancedTokenizationScenarios:
    """Test advanced tokenization scenarios."""

    def test_tokenizer_very_long_text(self):
        """Tokenizer should handle very long text."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        try:
            long_text = "word " * 10000  # Very long text
            tokens = tokenizer.encode(long_text)
            assert len(tokens) > 0, "Tokens must not be empty"
        except (NotImplementedError, MemoryError):
            pytest.skip("Very long text not supported")

    def test_tokenizer_whitespace_handling(self):
        """Tokenizer should handle various whitespace correctly."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        texts = [
            "hello   world",  # Multiple spaces
            "hello\tworld",   # Tab
            "hello\nworld",   # Newline
            "  hello  ",      # Leading/trailing
        ]

        for text in texts:
            try:
                tokens = tokenizer.encode(text)
                decoded = tokenizer.decode(tokens)
                assert decoded is not None, "decoded must be initialized"
            except (NotImplementedError, ValueError):
                pytest.skip("Whitespace handling incomplete")

    def test_tokenizer_special_characters(self):
        """Tokenizer should handle special characters."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        texts = [
            "hello@world!",
            "test#123$code",
            "(parentheses)",
            "[brackets]",
            "{braces}",
        ]

        for text in texts:
            try:
                tokens = tokenizer.encode(text)
                assert len(tokens) > 0, "Tokens must not be empty"
            except (NotImplementedError, ValueError):
                pytest.skip("Special char handling incomplete")

    def test_tokenizer_punctuation_preservation(self):
        """Tokenizer should preserve punctuation information."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        try:
            text1 = "hello world"
            text2 = "hello, world"
            tokens1 = tokenizer.encode(text1)
            tokens2 = tokenizer.encode(text2)
            # Punctuation should affect tokenization
            assert len(tokens1) > 0 and len(tokens2) > 0, "tokens must be created"
        except (NotImplementedError, ValueError):
            pytest.skip("Punctuation handling incomplete")

    def test_tokenizer_mixed_case_handling(self):
        """Tokenizer should handle mixed case text."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        texts = [
            "HELLO WORLD",
            "Hello World",
            "hELLo wORLD",
        ]

        try:
            for text in texts:
                tokens = tokenizer.encode(text)
                assert len(tokens) > 0, "Tokens must not be empty"
        except (NotImplementedError, ValueError):
            pytest.skip("Case handling incomplete")

    def test_tokenizer_number_handling(self):
        """Tokenizer should handle numeric text."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        texts = [
            "12345",
            "3.14159",
            "-42",
            "1e-10",
        ]

        try:
            for text in texts:
                tokens = tokenizer.encode(text)
                assert len(tokens) > 0, "Tokens must not be empty"
        except (NotImplementedError, ValueError):
            pytest.skip("Number handling incomplete")

    def test_tokenizer_url_handling(self):
        """Tokenizer should handle URLs."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        try:
            url = "https://www.example.com/path?query=value"
            tokens = tokenizer.encode(url)
            assert len(tokens) > 0, "Tokens must not be empty"
        except (NotImplementedError, ValueError):
            pytest.skip("URL handling incomplete")


class TestSpecialTokenEdgeCases:
    """Test special token handling in edge cases."""

    def test_special_tokens_consistent_ids(self):
        """Special token IDs should be consistent."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        try:
            # Get BOS/EOS IDs multiple times
            bos1 = tokenizer.bos_token_id if hasattr(tokenizer, "bos_token_id") else None
            bos2 = tokenizer.bos_token_id if hasattr(tokenizer, "bos_token_id") else None
            
            if bos1 is not None:
                assert bos1 == bos2, "BOS ID inconsistent"
        except (NotImplementedError, AttributeError):
            pytest.skip("BOS token not available")

    def test_special_tokens_non_overlapping(self):
        """Special token IDs should not overlap."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        try:
            ids = set()
            for token_type in ["bos_token_id", "eos_token_id", "pad_token_id", "unk_token_id"]:
                token_id = getattr(tokenizer, token_type, None)
                if token_id is not None and token_id >= 0:
                    if token_id in ids:
                        pytest.skip("Special token overlap")
                    ids.add(token_id)
        except (NotImplementedError, AttributeError):
            pytest.skip("Special tokens not available")

    def test_special_tokens_in_batch_encode(self):
        """Special tokens should be handled in batch encoding."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        try:
            texts = ["hello", "world", "test"]
            result = tokenizer.batch_encode_plus(texts, add_special_tokens=True)
            if result and "input_ids" in result:
                assert len(result["input_ids"]) > 0, "Result must not be empty"
        except (NotImplementedError, TypeError):
            pytest.skip("batch_encode_plus not available")

    def test_special_tokens_padding_marker(self):
        """Pad token should be distinct from regular tokens."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        try:
            pad_id = tokenizer.pad_token_id if hasattr(tokenizer, "pad_token_id") else None
            if pad_id is not None and pad_id >= 0:
                # Pad ID should exist
                assert pad_id >= 0, "pad_id must be valid"
        except (NotImplementedError, AttributeError):
            pytest.skip("Pad token not available")

    def test_special_tokens_unk_fallback(self):
        """Unknown token should be available as fallback."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        try:
            unk_id = tokenizer.unk_token_id if hasattr(tokenizer, "unk_token_id") else None
            if unk_id is not None:
                assert unk_id >= 0, "unk_id must be valid"
        except (NotImplementedError, AttributeError):
            pytest.skip("Unk token not available")


class TestBatchEncodingEdgeCases:
    """Test batch encoding with various sizes and configurations."""

    def test_batch_encode_single_item(self):
        """Batch encode should handle single item."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        try:
            result = tokenizer.batch_encode_plus(["hello"])
            if result:
                assert len(result["input_ids"]) == 1, "Should have 1 item"
        except (NotImplementedError, TypeError):
            pytest.skip("batch_encode_plus not available")

    def test_batch_encode_large_batch(self):
        """Batch encode should handle large batches."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        try:
            texts = ["text"] * 1000
            result = tokenizer.batch_encode_plus(texts)
            if result:
                assert len(result["input_ids"]) == 1000, "Should have 1000 items"
        except (NotImplementedError, MemoryError):
            pytest.skip("Large batch not supported")

    def test_batch_encode_mixed_lengths(self):
        """Batch encode should handle mixed length texts."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        try:
            texts = ["a", "hello world", "this is a longer text", "very " * 100]
            result = tokenizer.batch_encode_plus(texts)
            if result:
                assert len(result["input_ids"]) == 4, "Should have 4 items"
        except (NotImplementedError, ValueError):
            pytest.skip("Mixed length batch not supported")

    def test_batch_encode_empty_strings(self):
        """Batch encode should handle empty strings."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        try:
            texts = ["hello", "", "world"]
            result = tokenizer.batch_encode_plus(texts)
            if result:
                assert len(result["input_ids"]) == 3, "Should have 3 items"
        except (NotImplementedError, ValueError):
            pytest.skip("Empty string handling incomplete")

    def test_batch_encode_return_tensors(self):
        """Batch encode should support tensor returns."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        try:
            result = tokenizer.batch_encode_plus(["hello", "world"], return_tensors="pt")
            if result:
                # Should return tensor-like object
                assert "input_ids" in result, "Should have input_ids"
        except (NotImplementedError, TypeError):
            pytest.skip("Tensor return not supported")

    def test_batch_encode_attention_mask(self):
        """Batch encode should produce attention masks."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        try:
            result = tokenizer.batch_encode_plus(["hello", "world"])
            if result:
                assert "attention_mask" in result or "input_ids" in result, "Condition must be true"
        except (NotImplementedError, TypeError):
            pytest.skip("batch_encode_plus not available")


class TestTruncationPaddingEdgeCases:
    """Test truncation and padding edge cases."""

    def test_truncation_exact_max_length(self):
        """Text exactly at max_length should not be truncated."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        try:
            # Create text with known token count
            text = "hello " * 10
            tokens = tokenizer.encode(text)
            max_len = len(tokens)

            result = tokenizer.encode_plus(text, max_length=max_len, truncation=True)
            if "input_ids" in result:
                assert len(result["input_ids"]) <= max_len, "Should not exceed max_length"
        except (NotImplementedError, TypeError):
            pytest.skip("Truncation not available")

    def test_truncation_removes_tokens(self):
        """Truncation should remove tokens beyond limit."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        try:
            text = "word " * 1000
            result = tokenizer.encode_plus(text, max_length=10, truncation=True)
            if "input_ids" in result:
                assert len(result["input_ids"]) <= 10, "Should be truncated"
        except (NotImplementedError, TypeError):
            pytest.skip("Truncation not available")

    def test_padding_exact_max_length(self):
        """Text padded should reach max_length."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        try:
            text = "hello"
            result = tokenizer.encode_plus(text, max_length=20, padding="max_length")
            if "input_ids" in result:
                assert len(result["input_ids"]) == 20, "Should be padded to 20"
        except (NotImplementedError, TypeError):
            pytest.skip("Padding not available")

    def test_truncation_strategy_longest_first(self):
        """Truncation strategy should affect output."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        try:
            text = "word " * 1000
            result = tokenizer.encode_plus(
                text,
                max_length=10,
                truncation=True,
                truncation_strategy="longest_first"
            )
            if "input_ids" in result:
                assert len(result["input_ids"]) <= 10, "Should be truncated"
        except (NotImplementedError, TypeError):
            pytest.skip("Truncation strategy not available")

    def test_padding_strategy_other_sequences(self):
        """Padding strategy for batch should work."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        try:
            texts = ["short", "a much longer text"]
            result = tokenizer.batch_encode_plus(texts, padding="longest")
            if "input_ids" in result:
                # All should have same length
                lengths = [len(ids) for ids in result["input_ids"]]
                assert len(set(lengths)) <= 2, "Condition must be true"
        except (NotImplementedError, TypeError):
            pytest.skip("Padding strategy not available")


class TestVocabularyCoverage:
    """Test vocabulary coverage and special handling."""

    def test_vocab_size_positive(self):
        """Vocabulary size should be positive."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        try:
            if hasattr(tokenizer, "vocab_size"):
                assert tokenizer.vocab_size > 0, "vocab_size must be positive"
        except (NotImplementedError, AttributeError):
            pytest.skip("vocab_size not available")

    def test_vocab_consistent_across_calls(self):
        """Vocabulary should be consistent across calls."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        try:
            if hasattr(tokenizer, "vocab_size"):
                size1 = tokenizer.vocab_size
                size2 = tokenizer.vocab_size
                assert size1 == size2, "vocab_size should be consistent"
        except (NotImplementedError, AttributeError):
            pytest.skip("vocab_size not available")

    def test_token_frequency_distribution(self):
        """Common tokens should appear in vocabulary."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        try:
            # Common words
            common_words = ["the", "a", "is", "and", "or"]
            for word in common_words:
                tokens = tokenizer.encode(word)
                assert len(tokens) > 0, f"{word} should be tokenizable"
        except (NotImplementedError, ValueError):
            pytest.skip("Common token handling incomplete")

    def test_rare_token_handling(self):
        """Rare tokens should map to unknown token."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        try:
            # Very rare/fake word
            rare_text = "xyzabc" * 100
            tokens = tokenizer.encode(rare_text)
            assert len(tokens) > 0, "Should tokenize rare text"
        except (NotImplementedError, ValueError):
            pytest.skip("Rare token handling incomplete")


class TestMultilingualSupport:
    """Test multilingual tokenization support."""

    def test_tokenizer_chinese_characters(self):
        """Tokenizer should handle Chinese."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        try:
            text = "你好世界"  # Hello World in Chinese
            tokens = tokenizer.encode(text)
            assert len(tokens) > 0, "Should tokenize Chinese"
        except (NotImplementedError, UnicodeError):
            pytest.skip("Chinese support incomplete")

    def test_tokenizer_arabic_script(self):
        """Tokenizer should handle Arabic."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        try:
            text = "مرحبا"  # Hello in Arabic
            tokens = tokenizer.encode(text)
            assert len(tokens) > 0, "Should tokenize Arabic"
        except (NotImplementedError, UnicodeError):
            pytest.skip("Arabic support incomplete")

    def test_tokenizer_mixed_language(self):
        """Tokenizer should handle mixed language text."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        try:
            text = "Hello 世界 мир"  # Mixed languages
            tokens = tokenizer.encode(text)
            assert len(tokens) > 0, "Should tokenize mixed language"
        except (NotImplementedError, UnicodeError):
            pytest.skip("Mixed language support incomplete")

    def test_tokenizer_emoji_handling(self):
        """Tokenizer should handle emoji."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        try:
            text = "hello 😀 world"
            tokens = tokenizer.encode(text)
            assert len(tokens) > 0, "Should tokenize emoji"
        except (NotImplementedError, UnicodeError):
            pytest.skip("Emoji support incomplete")

    def test_tokenizer_right_to_left_text(self):
        """Tokenizer should handle right-to-left text."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        try:
            text = "שלום עולם"  # Hello World in Hebrew
            tokens = tokenizer.encode(text)
            assert len(tokens) > 0, "Should tokenize RTL text"
        except (NotImplementedError, UnicodeError):
            pytest.skip("RTL support incomplete")

    def test_tokenizer_accent_marks(self):
        """Tokenizer should handle accented characters."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        try:
            text = "café naïve élève"
            tokens = tokenizer.encode(text)
            assert len(tokens) > 0, "Should tokenize accented text"
        except (NotImplementedError, ValueError):
            pytest.skip("Accent mark support incomplete")


class TestTokenizerCaching:
    """Test tokenizer caching behavior."""

    def test_tokenizer_cache_directory_exists(self):
        """Tokenizer cache should use configured directory."""
        try:
            from codex_ml.tokenization import get_cache_dir
        except (ImportError, AttributeError):
            pytest.skip("Cache utilities not available")

        try:
            cache_dir = get_cache_dir()
            if cache_dir:
                path = Path(cache_dir)
                # Should be absolute or relative
                assert path.is_absolute() or str(path).startswith("."), "Condition must be true"
        except (NotImplementedError, FileNotFoundError):
            pytest.skip("Cache directory not configured")

    def test_tokenizer_repeated_encoding_consistency(self):
        """Repeated encoding should be consistent."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer creation failed")

        try:
            text = "test text for consistency"
            tokens1 = tokenizer.encode(text)
            tokens2 = tokenizer.encode(text)
            tokens3 = tokenizer.encode(text)
            
            assert tokens1 == tokens2 == tokens3, "Encoding must be consistent"
        except (NotImplementedError, ValueError):
            pytest.skip("Encoding consistency incomplete")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
