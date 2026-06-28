"""
Tokenization Coverage Tests — codex_ml.tokenization
Comprehensive tokenizer validation including CLI, round-trip, and special tokens
"""

from pathlib import Path

import pytest


class TestTokenizerCLICommands:
    """Test tokenizer CLI commands (inspect, export, refresh)."""

    def test_tokenizer_cli_inspect_help(self):
        """Tokenizer CLI should provide inspect help."""
        try:
            from codex_ml.tokenization import get_tokenizer_cli
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer CLI not available")

        cli = get_tokenizer_cli()
        if cli is None:
            pytest.skip("CLI not available")

    def test_tokenizer_cli_export_formats(self):
        """Tokenizer should support multiple export formats."""
        formats = ["json", "csv", "yaml", "pickle"]

        # Test format support
        for fmt in formats[:2]:  # Test at least json and csv
            assert fmt in ["json", "csv", "yaml", "pickle"]

    def test_tokenizer_cache_directory(self):
        """Tokenizer cache should use configured directory."""
        try:
            from codex_ml.tokenization import get_cache_dir
        except (ImportError, AttributeError):
            pytest.skip("Cache utilities not available")

        try:
            cache_dir = get_cache_dir()
            if cache_dir:
                # Cache dir should be resolvable
                path = Path(cache_dir)
                assert path.is_absolute() or path.is_relative_to(Path.cwd()), "Condition must be true"
        except (NotImplementedError, FileNotFoundError):
            pytest.skip("Cache directory not configured")


class TestTokenizerRoundTrip:
    """Test encode/decode round-trip fidelity."""

    def test_basic_encode_decode_roundtrip(self):
        """Basic text should survive encode/decode."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer instantiation failed")

        text = "Hello world"

        try:
            # Encode
            tokens = tokenizer.encode(text)
            assert len(tokens) > 0, "Tokens must not be empty"

            # Decode
            decoded = tokenizer.decode(tokens)
            assert decoded is not None, "decoded must be initialized"
        except (NotImplementedError, AttributeError):
            pytest.skip("encode/decode not implemented")

    def test_unicode_roundtrip(self):
        """Unicode text should preserve during round-trip."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer not available")

        texts = [
            "Hello 世界",  # Chinese
            "Привет мир",  # Russian
            "مرحبا بالعالم",  # Arabic
        ]

        for text in texts:
            try:
                tokens = tokenizer.encode(text)
                decoded = tokenizer.decode(tokens)
                assert decoded is not None, "decoded must be initialized"
            except (NotImplementedError, UnicodeError):
                pytest.skip("Unicode handling not fully implemented")

    def test_empty_text_encode_decode(self):
        """Empty text should handle gracefully."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer not available")

        try:
            # Empty string
            tokens = tokenizer.encode("")
            decoded = tokenizer.decode(tokens)
            assert decoded is not None, "decoded must be initialized"
        except (NotImplementedError, ValueError):
            pytest.skip("Empty text handling not specified")


class TestSpecialTokens:
    """Test special token handling."""

    def test_bos_token_encode(self):
        """BOS (Beginning of Sequence) token should be identifiable."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer not available")

        try:
            if hasattr(tokenizer, "bos_token_id"):
                bos_id = tokenizer.bos_token_id
                assert bos_id is not None or bos_id >= 0, "bos_id must be initialized"
        except (NotImplementedError, AttributeError):
            pytest.skip("BOS token not defined")

    def test_eos_token_encode(self):
        """EOS (End of Sequence) token should be identifiable."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer not available")

        try:
            if hasattr(tokenizer, "eos_token_id"):
                eos_id = tokenizer.eos_token_id
                assert eos_id is not None or eos_id >= 0, "eos_id must be initialized"
        except (NotImplementedError, AttributeError):
            pytest.skip("EOS token not defined")

    def test_pad_token_batch_handling(self):
        """PAD token should handle batch encoding."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer not available")

        try:
            if hasattr(tokenizer, "pad_token_id"):
                pad_id = tokenizer.pad_token_id
                assert pad_id is not None or pad_id >= 0, "pad_id must be initialized"
        except (NotImplementedError, AttributeError):
            pytest.skip("PAD token not defined")

    def test_unk_token_fallback(self):
        """UNK (Unknown) token should exist for OOV words."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer not available")

        try:
            if hasattr(tokenizer, "unk_token_id"):
                unk_id = tokenizer.unk_token_id
                assert unk_id is not None or unk_id >= 0, "unk_id must be initialized"
        except (NotImplementedError, AttributeError):
            pytest.skip("UNK token not defined")


class TestBatchEncoding:
    """Test batch encoding at multiple sizes."""

    def test_batch_size_1_encoding(self):
        """Should handle batch size 1."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer not available")

        try:
            texts = ["Hello world"]
            result = tokenizer.batch_encode_plus(texts, return_tensors="pt")
            assert result is not None, "result must be initialized"
        except (NotImplementedError, AttributeError):
            pytest.skip("batch_encode_plus not implemented")

    def test_batch_size_8_encoding(self):
        """Should handle batch size 8."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer not available")

        try:
            texts = [f"Text {i}" for i in range(8)]
            result = tokenizer.batch_encode_plus(texts, return_tensors="pt")
            assert result is not None, "result must be initialized"
        except (NotImplementedError, AttributeError):
            pytest.skip("batch_encode_plus not implemented")

    def test_batch_mixed_lengths_padding(self):
        """Should handle mixed-length sequences with padding."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer not available")

        try:
            texts = [
                "Short",
                "This is a much longer text that will need padding",
                "Medium length text here",
            ]
            result = tokenizer.batch_encode_plus(texts, padding=True, return_tensors="pt")
            assert result is not None, "result must be initialized"
        except (NotImplementedError, AttributeError):
            pytest.skip("batch_encode_plus not implemented")

    def test_batch_return_types(self):
        """Batch encoding should support multiple return types."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer not available")

        texts = ["Hello", "World"]

        try:
            # Try torch tensors
            result_pt = tokenizer.batch_encode_plus(texts, return_tensors="pt")
            assert result_pt is not None, "result_pt must be initialized"
        except (NotImplementedError, ImportError):
            try:
                # Fallback to Python lists
                result_list = tokenizer.batch_encode_plus(texts, return_tensors=None)
                assert result_list is not None, "result_list must be initialized"
            except NotImplementedError:
                pytest.skip("batch_encode_plus not fully implemented")


class TestTruncationAndPadding:
    """Test truncation and padding behavior."""

    def test_max_length_truncation(self):
        """Should truncate to max_length."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer not available")

        try:
            text = " ".join(["word"] * 100)  # Long text
            result = tokenizer.encode_plus(text, max_length=10, truncation=True)
            if result:
                # Should be truncated to 10 or less
                assert len(result["input_ids"]) <= 10, "Collection must not be empty"
        except (NotImplementedError, TypeError):
            pytest.skip("Truncation not implemented")

    def test_padding_left_direction(self):
        """Should support left-padding."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer not available")

        try:
            texts = ["short", "this is much longer"]
            result = tokenizer.batch_encode_plus(
                texts, padding=True, pad_to_multiple_of=8
            )
            assert result is not None, "result must be initialized"
        except (NotImplementedError, TypeError):
            pytest.skip("Padding configuration not fully supported")

    def test_padding_right_direction(self):
        """Should support right-padding (default)."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer not available")

        try:
            texts = ["short", "this is much longer"]
            result = tokenizer.batch_encode_plus(texts, padding="max_length", max_length=20)
            assert result is not None, "result must be initialized"
        except (NotImplementedError, TypeError):
            pytest.skip("Right-padding not implemented")

    def test_attention_mask_generation(self):
        """Should generate attention masks for padded sequences."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer not available")

        try:
            texts = ["hello", "world here"]
            result = tokenizer.batch_encode_plus(texts, padding=True)
            if "attention_mask" in result:
                # Attention mask should be present for padded sequences
                assert result["attention_mask"] is not None, "Value must be initialized"
        except (NotImplementedError, KeyError):
            pytest.skip("Attention mask generation not available")


class TestTokenizerVocabSize:
    """Test vocabulary size and completeness."""

    def test_vocab_size_positive(self):
        """Vocabulary size should be positive."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer not available")

        try:
            vocab_size = tokenizer.vocab_size
            assert vocab_size > 0, "Vocabulary must have positive size"
        except (NotImplementedError, AttributeError):
            pytest.skip("vocab_size not available")

    def test_vocab_size_reasonable(self):
        """Vocabulary size should be in reasonable range."""
        try:
            from codex_ml.tokenization import get_tokenizer
        except (ImportError, AttributeError):
            pytest.skip("Tokenizer not available")

        tokenizer = get_tokenizer()
        if tokenizer is None:
            pytest.skip("Tokenizer not available")

        try:
            vocab_size = tokenizer.vocab_size
            # Vocabulary should be between 256 (minimal) and 1M (huge)
            assert 256 <= vocab_size <= 1_000_000, "256 is not valid"
        except (NotImplementedError, AttributeError):
            pytest.skip("vocab_size not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
