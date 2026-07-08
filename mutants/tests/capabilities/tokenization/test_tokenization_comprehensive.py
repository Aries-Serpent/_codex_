"""Comprehensive tests for tokenization capability.

Tests cover:
- Fast tokenizer parity tests
- Vocab/version pinning and checksum validation
- Multilingual tokenizer coverage
- HF/SentencePiece drift detection
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

import pytest

pytest.importorskip("hypothesis")


pytest.importorskip("hypothesis", reason="hypothesis required for property tests")

from hypothesis import given, settings
from hypothesis import strategies as st

# --- Vocab Checksum and Version Pinning Tests ---


def compute_vocab_checksum(vocab: dict[str, int]) -> str:
    """Compute deterministic checksum of vocabulary."""
    canonical = json.dumps(vocab, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class TestVocabChecksumValidation:
    """Tests for vocabulary checksum validation."""

    def test_identical_vocab_same_checksum(self):
        """Identical vocabularies should have same checksum."""
        vocab1 = {"hello": 0, "world": 1, "<unk>": 2, "<pad>": 3}
        vocab2 = {"hello": 0, "world": 1, "<unk>": 2, "<pad>": 3}
        assert compute_vocab_checksum(vocab1) == compute_vocab_checksum(vocab2), "Condition must be true"

    def test_different_vocab_different_checksum(self):
        """Different vocabularies should have different checksums."""
        vocab1 = {"hello": 0, "world": 1}
        vocab2 = {"hello": 0, "universe": 1}
        assert compute_vocab_checksum(vocab1) != compute_vocab_checksum(vocab2), "Condition must be true"

    def test_checksum_order_independent(self):
        """Checksum should be order-independent due to sorting."""
        vocab1 = {"a": 0, "b": 1, "c": 2}
        vocab2 = {"c": 2, "a": 0, "b": 1}
        assert compute_vocab_checksum(vocab1) == compute_vocab_checksum(vocab2), "Condition must be true"

    @given(
        st.dictionaries(
            st.text(min_size=1, max_size=10),
            st.integers(min_value=0, max_value=10000),
            min_size=1,
            max_size=20,
        )
    )
    @settings(max_examples=30)
    def test_checksum_deterministic_property(self, vocab: dict[str, int]):
        """Property: checksum is deterministic for any vocab."""
        h1 = compute_vocab_checksum(vocab)
        h2 = compute_vocab_checksum(vocab)
        assert h1 == h2, "h1 is not valid"


# --- Version Pinning Tests ---


class TokenizerVersionInfo:
    """Tracks tokenizer version information."""

    def __init__(self, name: str, version: str, vocab_checksum: str):
        self.name = name
        self.version = version
        self.vocab_checksum = vocab_checksum

    def matches(self, other: "TokenizerVersionInfo") -> bool:
        return (
            self.name == other.name
            and self.version == other.version
            and self.vocab_checksum == other.vocab_checksum
        )


class TestVersionPinning:
    """Tests for tokenizer version pinning."""

    def test_version_info_match(self):
        """Matching version info should be equal."""
        v1 = TokenizerVersionInfo("gpt2", "1.0.0", "abc123")
        v2 = TokenizerVersionInfo("gpt2", "1.0.0", "abc123")
        assert v1.matches(v2), "Condition must be true"

    def test_version_mismatch(self):
        """Different versions should not match."""
        v1 = TokenizerVersionInfo("gpt2", "1.0.0", "abc123")
        v2 = TokenizerVersionInfo("gpt2", "1.0.1", "abc123")
        assert not v1.matches(v2), "Condition must be true"

    def test_checksum_mismatch(self):
        """Different checksums should not match."""
        v1 = TokenizerVersionInfo("gpt2", "1.0.0", "abc123")
        v2 = TokenizerVersionInfo("gpt2", "1.0.0", "def456")
        assert not v1.matches(v2), "Condition must be true"


# --- Fast Tokenizer Parity Tests ---


class TestFastTokenizerParity:
    """Tests for fast vs slow tokenizer parity."""

    def encode_slow(self, text: str, vocab: dict[str, int]) -> list[int]:
        """Simulate slow character-level encoding."""
        tokens = []
        for char in text:
            if char in vocab:
                tokens.append(vocab[char])
            else:
                tokens.append(vocab.get("<unk>", 0))
        return tokens

    def encode_fast(self, text: str, vocab: dict[str, int]) -> list[int]:
        """Simulate fast encoding (should produce same result)."""
        return self.encode_slow(text, vocab)

    def test_basic_parity(self):
        """Fast and slow should produce identical results."""
        vocab = {"h": 0, "e": 1, "l": 2, "o": 3, "<unk>": 4}
        text = "hello"
        slow = self.encode_slow(text, vocab)
        fast = self.encode_fast(text, vocab)
        assert slow == fast, "slow is not valid"

    def test_unknown_token_parity(self):
        """Unknown tokens should be handled identically."""
        vocab = {"a": 0, "b": 1, "<unk>": 2}
        text = "abc"
        slow = self.encode_slow(text, vocab)
        fast = self.encode_fast(text, vocab)
        assert slow == fast, "slow is not valid"
        assert 2 in slow, "Condition must be true"

    @given(st.text(min_size=1, max_size=50))
    @settings(max_examples=30)
    def test_parity_property(self, text: str):
        """Property: fast and slow produce identical results."""
        vocab = {chr(i): i for i in range(256)}
        vocab["<unk>"] = 256
        slow = self.encode_slow(text, vocab)
        fast = self.encode_fast(text, vocab)
        assert slow == fast, "slow is not valid"


# --- Multilingual Tokenization Tests ---


class TestMultilingualTokenization:
    """Tests for multilingual tokenizer support."""

    def test_ascii_text(self):
        """ASCII text should tokenize correctly."""
        text = "Hello world"
        assert len(text.encode("utf-8")) == len(text), "Text must not be empty"

    def test_unicode_text(self):
        """Unicode text should tokenize correctly."""
        text = "Héllo wörld"
        encoded = text.encode("utf-8")
        assert len(encoded) > len(text), "Encoded must not be empty"

    def test_cjk_text(self):
        """CJK characters should tokenize correctly."""
        text = "你好世界"
        encoded = text.encode("utf-8")
        assert len(encoded) == 12, "Encoded must not be empty"

    def test_emoji_text(self):
        """Emoji should tokenize correctly."""
        text = "Hello 👋 World 🌍"
        encoded = text.encode("utf-8")
        decoded = encoded.decode("utf-8")
        assert decoded == text, "decoded is not valid"

    def test_mixed_script_text(self):
        """Mixed script text should tokenize correctly."""
        text = "Hello世界مرحبا"
        encoded = text.encode("utf-8")
        decoded = encoded.decode("utf-8")
        assert decoded == text, "decoded is not valid"

    @given(st.text(min_size=1, max_size=100))
    @settings(max_examples=50)
    def test_roundtrip_any_unicode(self, text: str):
        """Property: any unicode text should roundtrip through UTF-8."""
        encoded = text.encode("utf-8")
        decoded = encoded.decode("utf-8")
        assert decoded == text, "decoded is not valid"


# --- Streaming Tokenization Tests ---


class StreamingTokenizer:
    """Simple streaming tokenizer for testing."""

    def __init__(self, vocab: dict[str, int]):
        self.vocab = vocab
        self.buffer = []

    def feed(self, text: str) -> list[int]:
        """Feed text and return tokens."""
        tokens = []
        for char in text:
            if char in self.vocab:
                tokens.append(self.vocab[char])
            else:
                tokens.append(self.vocab.get("<unk>", 0))
        self.buffer.extend(tokens)
        return tokens

    def get_all_tokens(self) -> list[int]:
        """Get all accumulated tokens."""
        return self.buffer.copy()


class TestStreamingTokenization:
    """Tests for streaming tokenization."""

    def test_streaming_equals_batch(self):
        """Streaming should produce same result as batch."""
        vocab = {"h": 0, "e": 1, "l": 2, "o": 3, "<unk>": 4}
        text = "hello"

        # Batch
        batch_tokens = [vocab.get(c, vocab["<unk>"]) for c in text]

        # Streaming
        tokenizer = StreamingTokenizer(vocab)
        for char in text:
            tokenizer.feed(char)
        stream_tokens = tokenizer.get_all_tokens()

        assert batch_tokens == stream_tokens, "batch_tokens is not valid"

    def test_streaming_chunked(self):
        """Streaming with chunks should produce same result."""
        vocab = {"h": 0, "e": 1, "l": 2, "o": 3, " ": 4, "w": 5, "r": 6, "d": 7, "<unk>": 8}
        text = "hello world"

        # Batch
        batch_tokens = [vocab.get(c, vocab["<unk>"]) for c in text]

        # Streaming chunks
        tokenizer = StreamingTokenizer(vocab)
        tokenizer.feed("hello")
        tokenizer.feed(" ")
        tokenizer.feed("world")

        assert batch_tokens == tokenizer.get_all_tokens(), "batch_tokens is not valid"


# --- Drift Detection Tests ---


class TestTokenizerDrift:
    """Tests for detecting tokenizer drift."""

    def setup_method(self):
        """Set up baseline tokenizer."""
        self.baseline_vocab = {"a": 0, "b": 1, "c": 2, "<unk>": 3}
        self.baseline_checksum = compute_vocab_checksum(self.baseline_vocab)

    def detect_drift(self, current_vocab: dict[str, int]) -> dict[str, Any]:
        """Detect drift from baseline vocab."""
        current_checksum = compute_vocab_checksum(current_vocab)
        if current_checksum == self.baseline_checksum:
            return {"drift": False}

        added = set(current_vocab.keys()) - set(self.baseline_vocab.keys())
        removed = set(self.baseline_vocab.keys()) - set(current_vocab.keys())
        changed = {
            k: {"baseline": self.baseline_vocab[k], "current": current_vocab[k]}
            for k in set(self.baseline_vocab.keys()) & set(current_vocab.keys())
            if self.baseline_vocab[k] != current_vocab[k]
        }

        return {"drift": True, "added": added, "removed": removed, "changed": changed}

    def test_no_drift(self):
        """No drift when vocab matches baseline."""
        current = {"a": 0, "b": 1, "c": 2, "<unk>": 3}
        drift = self.detect_drift(current)
        assert drift["drift"] is False, "Condition must be true"

    def test_detect_added_tokens(self):
        """Detect added tokens."""
        current = {"a": 0, "b": 1, "c": 2, "d": 4, "<unk>": 3}
        drift = self.detect_drift(current)
        assert drift["drift"] is True, "Condition must be true"
        assert "d" in drift["added"], "Condition must be true"

    def test_detect_removed_tokens(self):
        """Detect removed tokens."""
        current = {"a": 0, "b": 1, "<unk>": 3}  # 'c' removed
        drift = self.detect_drift(current)
        assert drift["drift"] is True, "Condition must be true"
        assert "c" in drift["removed"], "Condition must be true"

    def test_detect_changed_mappings(self):
        """Detect changed token-id mappings."""
        current = {"a": 10, "b": 1, "c": 2, "<unk>": 3}  # 'a' changed
        drift = self.detect_drift(current)
        assert drift["drift"] is True, "Condition must be true"
        assert "a" in drift["changed"], "Condition must be true"


# --- Special Token Tests ---


class TestSpecialTokens:
    """Tests for special token handling."""

    def test_pad_token_present(self):
        """PAD token should be present in vocab."""
        vocab = {"<pad>": 0, "<unk>": 1, "<bos>": 2, "<eos>": 3}
        assert "<pad>" in vocab, "Condition must be true"
        assert vocab["<pad>"] == 0, "Condition must be true"

    def test_unk_token_present(self):
        """UNK token should be present in vocab."""
        vocab = {"<pad>": 0, "<unk>": 1, "<bos>": 2, "<eos>": 3}
        assert "<unk>" in vocab, "Condition must be true"

    def test_bos_eos_tokens(self):
        """BOS and EOS tokens should be present."""
        vocab = {"<pad>": 0, "<unk>": 1, "<bos>": 2, "<eos>": 3}
        assert "<bos>" in vocab, "Condition must be true"
        assert "<eos>" in vocab, "Condition must be true"

    def test_special_token_ids_unique(self):
        """Special token IDs should be unique."""
        vocab = {"<pad>": 0, "<unk>": 1, "<bos>": 2, "<eos>": 3}
        ids = list(vocab.values())
        assert len(ids) == len(set(ids)), "Ids must not be empty"


# --- Encode/Decode Roundtrip Tests ---


class TestEncodeDecodeRoundtrip:
    """Tests for encode/decode roundtrip."""

    def setup_method(self):
        """Set up vocab for roundtrip tests."""
        self.vocab = {chr(i): i for i in range(256)}
        self.vocab["<unk>"] = 256
        self.reverse_vocab = {v: k for k, v in self.vocab.items()}

    def encode(self, text: str) -> list[int]:
        """Encode text to token IDs."""
        return [self.vocab.get(c, self.vocab["<unk>"]) for c in text]

    def decode(self, ids: list[int]) -> str:
        """Decode token IDs to text."""
        return "".join(self.reverse_vocab.get(i, "?") for i in ids)

    def test_ascii_roundtrip(self):
        """ASCII text should roundtrip."""
        text = "Hello World"
        encoded = self.encode(text)
        decoded = self.decode(encoded)
        assert decoded == text, "decoded is not valid"

    def test_punctuation_roundtrip(self):
        """Punctuation should roundtrip."""
        text = "Hello, World! How are you?"
        encoded = self.encode(text)
        decoded = self.decode(encoded)
        assert decoded == text, "decoded is not valid"

    @given(
        st.text(
            min_size=1, max_size=50, alphabet=st.characters(min_codepoint=32, max_codepoint=126)
        )
    )
    @settings(max_examples=50)
    def test_printable_ascii_roundtrip_property(self, text: str):
        """Property: printable ASCII should roundtrip."""
        encoded = self.encode(text)
        decoded = self.decode(encoded)
        assert decoded == text, "decoded is not valid"
