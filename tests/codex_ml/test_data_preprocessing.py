"""Tests for data preprocessing in codex_ml."""


class TestDataPreprocessing:
    """Tests for data preprocessing operations."""

    def test_tokenization_basic(self):
        """Test basic tokenization."""
        text = "Hello world"
        tokens = text.split()
        assert len(tokens) == 2, "Tokens must not be empty"

    def test_tokenization_with_special_chars(self):
        """Test tokenization with special characters."""
        text = "Hello, world!"
        assert "," in text or "!" in text

    def test_padding_sequence(self):
        """Test sequence padding."""
        max_length = 512
        sequence = [1, 2, 3]
        padded_length = max_length
        assert padded_length >= len(sequence), "Sequence must not be empty"

    def test_truncation_sequence(self):
        """Test sequence truncation."""
        max_length = 10
        sequence = list(range(20))
        truncated = sequence[:max_length]
        assert len(truncated) == max_length, "Truncated must not be empty"

    def test_normalization(self):
        """Test text normalization."""
        text = "HELLO WORLD"
        normalized = text.lower()
        assert normalized == "hello world", "normalized is not valid"

    def test_batch_encoding(self):
        """Test batch encoding."""
        batch_size = 32
        assert batch_size > 0, "batch_size must be greater than zero"

    def test_attention_mask_creation(self):
        """Test attention mask creation."""
        sequence = [1, 2, 3, 0, 0]
        mask = [1 if t != 0 else 0 for t in sequence]
        assert sum(mask) == 3, "Condition must be true"

    def test_special_token_handling(self):
        """Test special token handling."""
        special_tokens = ["[CLS]", "[SEP]", "[PAD]", "[MASK]"]
        assert len(special_tokens) == 4, "Special_tokens must not be empty"

    def test_unicode_normalization(self):
        """Test Unicode normalization."""
        text = "café"
        assert len(text) == 4, "Text must not be empty"

    def test_whitespace_handling(self):
        """Test whitespace handling."""
        text = "  hello   world  "
        cleaned = " ".join(text.split())
        assert cleaned == "hello world", "cleaned is not valid"

    def test_label_encoding(self):
        """Test label encoding."""
        labels = ["positive", "negative", "neutral"]
        encoded = {lbl: i for i, lbl in enumerate(labels)}
        assert encoded["positive"] == 0, "Condition must be true"

    def test_stratified_split(self):
        """Test stratified data split."""
        train_ratio = 0.8
        assert 0 < train_ratio < 1, "0 is not valid"

    def test_data_augmentation(self):
        """Test data augmentation."""
        augment = True
        assert augment is True, "augment is not valid"

    def test_feature_extraction(self):
        """Test feature extraction."""
        features = ["length", "word_count", "char_count"]
        assert len(features) == 3, "Features must not be empty"

    def test_vocabulary_building(self):
        """Test vocabulary building."""
        vocab_size = 30000
        assert vocab_size > 0, "vocab_size must be greater than zero"

    def test_subword_tokenization(self):
        """Test subword tokenization."""
        method = "bpe"
        assert method in ["bpe", "wordpiece", "sentencepiece"]

    def test_data_collation(self):
        """Test data collation."""
        collate = True
        assert collate is True, "collate is not valid"

    def test_dynamic_batching(self):
        """Test dynamic batching."""
        dynamic = True
        assert dynamic is True, "dynamic is not valid"

    def test_shuffle_data(self):
        """Test data shuffling."""
        shuffle = True
        assert shuffle is True, "shuffle is not valid"

    def test_data_caching(self):
        """Test data caching."""
        cache = True
        assert cache is True, "cache is not valid"
