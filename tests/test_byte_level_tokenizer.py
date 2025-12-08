"""
Tests for byte-level tokenizer.

Ensures:
- Encode-decode roundtrip preserves text
- Padding works correctly
- Truncation limits length
- Deterministic behavior
- Batch operations work
"""

import pytest
from codex_ml.tokenization.base import ByteLevelTokenizer, TokenizerConfig


class TestByteLevelTokenizer:
    """Tests for byte-level tokenizer."""
    
    def test_encode_decode_roundtrip(self):
        """Encode-decode should preserve text."""
        tokenizer = ByteLevelTokenizer()
        text = "Hello, world! 🌍"
        ids = tokenizer.encode(text, add_special_tokens=False)
        decoded = tokenizer.decode(ids)
        assert decoded == text
    
    def test_encode_decode_with_eos(self):
        """Test roundtrip with EOS token."""
        tokenizer = ByteLevelTokenizer()
        text = "Hello, world!"
        ids = tokenizer.encode(text, add_special_tokens=True)
        
        # Should include EOS token
        assert tokenizer.eos_token_id in ids
        
        # Decode should skip EOS
        decoded = tokenizer.decode(ids, skip_special_tokens=True)
        assert decoded == text
    
    def test_padding_to_max_length(self):
        """Padding should reach max_length."""
        tokenizer = ByteLevelTokenizer(max_length=50)
        text = "short"
        ids = tokenizer.encode(text)
        
        assert len(ids) == 50
        # Check that padding tokens exist
        assert tokenizer.pad_token_id in ids
    
    def test_truncation(self):
        """Truncation should limit length."""
        tokenizer = ByteLevelTokenizer(max_length=10, truncation=True)
        long_text = "A" * 100
        ids = tokenizer.encode(long_text)
        
        assert len(ids) == 10
    
    def test_no_padding_when_disabled(self):
        """No padding when padding != max_length."""
        tokenizer = ByteLevelTokenizer(max_length=50, padding="longest")
        text = "short"
        ids = tokenizer.encode(text)
        
        # Should not pad to max_length
        assert len(ids) < 50
    
    def test_determinism(self):
        """Same input should produce same output."""
        tokenizer = ByteLevelTokenizer(max_length=100)
        text = "Deterministic test"
        
        ids1 = tokenizer.encode(text)
        ids2 = tokenizer.encode(text)
        
        assert ids1 == ids2
    
    def test_batch_operations(self):
        """Batch encode/decode should work."""
        tokenizer = ByteLevelTokenizer(max_length=20)
        texts = ["Hello", "World", "Test"]
        
        batch_ids = tokenizer.batch_encode(texts)
        assert len(batch_ids) == 3
        
        decoded = tokenizer.batch_decode(batch_ids)
        assert decoded == texts
    
    def test_vocab_size(self):
        """Vocab size should be 256 bytes + 3 special tokens."""
        tokenizer = ByteLevelTokenizer()
        assert tokenizer.vocab_size == 259
    
    def test_special_token_ids(self):
        """Special tokens should have reserved IDs."""
        tokenizer = ByteLevelTokenizer()
        
        assert tokenizer.pad_token_id == 0
        assert tokenizer.eos_token_id == 1
        assert tokenizer.unk_token_id == 2
    
    def test_custom_special_tokens(self):
        """Custom special token IDs should work."""
        tokenizer = ByteLevelTokenizer(
            pad_token_id=10,
            eos_token_id=11,
            unk_token_id=12,
        )
        
        assert tokenizer.pad_token_id == 10
        assert tokenizer.eos_token_id == 11
        assert tokenizer.unk_token_id == 12
    
    def test_empty_string(self):
        """Empty string should encode/decode correctly."""
        tokenizer = ByteLevelTokenizer()
        
        ids = tokenizer.encode("", add_special_tokens=False)
        assert len(ids) == 0
        
        decoded = tokenizer.decode(ids)
        assert decoded == ""
    
    def test_unicode_handling(self):
        """Unicode characters should be handled correctly."""
        tokenizer = ByteLevelTokenizer()
        
        texts = [
            "Hello 世界",
            "Emoji: 😀🎉",
            "Math: ∑∫∂",
            "Cyrillic: Привет",
        ]
        
        for text in texts:
            ids = tokenizer.encode(text, add_special_tokens=False)
            decoded = tokenizer.decode(ids)
            assert decoded == text
    
    def test_legacy_compatibility(self):
        """Legacy tokenize_example should work."""
        tokenizer = ByteLevelTokenizer()
        text = "Test"
        
        ids = tokenizer.tokenize_example(text)
        assert isinstance(ids, list)
        assert all(isinstance(i, int) for i in ids)
    
    def test_decode_skip_special_tokens_false(self):
        """Test decode without skipping special tokens."""
        tokenizer = ByteLevelTokenizer()
        text = "Test"
        
        ids = tokenizer.encode(text, add_special_tokens=True)
        decoded = tokenizer.decode(ids, skip_special_tokens=False)
        
        # Decoded text will contain replacement characters for special tokens
        assert isinstance(decoded, str)
    
    def test_batch_with_different_lengths(self):
        """Batch operations with varying lengths."""
        tokenizer = ByteLevelTokenizer(max_length=30)
        
        texts = ["a", "medium text", "much longer text"]
        batch_ids = tokenizer.batch_encode(texts)
        
        # All should be padded to same length
        assert all(len(ids) == 30 for ids in batch_ids)
        
        decoded = tokenizer.batch_decode(batch_ids)
        assert decoded == texts


class TestTokenizerConfig:
    """Test tokenizer configuration."""
    
    def test_config_defaults(self):
        """Test default configuration values."""
        config = TokenizerConfig()
        
        assert config.pad_token_id == 0
        assert config.eos_token_id == 1
        assert config.unk_token_id == 2
        assert config.max_length is None
        assert config.padding == "max_length"
        assert config.truncation is True
    
    def test_config_custom_values(self):
        """Test custom configuration values."""
        config = TokenizerConfig(
            pad_token_id=5,
            max_length=128,
            truncation=False,
        )
        
        assert config.pad_token_id == 5
        assert config.max_length == 128
        assert config.truncation is False


class TestLegacyFunction:
    """Test legacy tokenize_example function."""
    
    def test_legacy_function(self):
        """Legacy function should work for backward compatibility."""
        from codex_ml.tokenization.base import tokenize_example
        
        ids = tokenize_example("Hello")
        assert isinstance(ids, list)
        assert len(ids) > 0
        assert all(isinstance(i, int) for i in ids)
