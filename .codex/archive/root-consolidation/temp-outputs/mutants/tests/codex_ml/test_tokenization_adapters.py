"""Tests for HuggingFace and SentencePiece tokenization adapters.

These tests validate the tokenizer adapters and skip gracefully when
the required dependencies (transformers, sentencepiece) are not installed.
"""

from __future__ import annotations

import importlib.util

import pytest

# Try to import transformers - skip tests if not available
transformers = pytest.importorskip("transformers", reason="transformers not installed")

# Try to import tokenizers package - skip tests if not available
HAS_TOKENIZERS = importlib.util.find_spec("tokenizers") is not None

# Try to import sentencepiece - skip tests if not available.
# Also verify the module has real functionality (not a stub/type-hint-only package).
# IS_CODEX_STUB=True means the in-repo shim is active rather than the real C extension.
try:
    import sentencepiece as _spm

    HAS_SENTENCEPIECE = hasattr(_spm, "SentencePieceTrainer") and not getattr(
        _spm, "IS_CODEX_STUB", False
    )
except ImportError:
    HAS_SENTENCEPIECE = False


@pytest.mark.skipif(not HAS_TOKENIZERS, reason="requires tokenizers package")
def test_hf_tokenizer_adapter_basic(tmp_path):
    """Test basic HuggingFace tokenizer adapter functionality."""
    from tokenizers import Tokenizer
    from tokenizers.models import WordLevel
    from tokenizers.pre_tokenizers import Whitespace

    from codex_ml.tokenization.hf_adapter import HFTokenizerAdapter

    # Create a simple tokenizer JSON file for testing
    # Build a minimal tokenizer
    tokenizer = Tokenizer(WordLevel(unk_token="<unk>"))
    tokenizer.pre_tokenizer = Whitespace()

    # Add some vocabulary
    vocab = {"<pad>": 0, "<unk>": 1, "</s>": 2, "hello": 3, "world": 4}
    tokenizer_json = tmp_path / "tokenizer.json"

    # Create minimal tokenizer with vocab
    tok = Tokenizer(WordLevel(vocab=vocab, unk_token="<unk>"))
    tok.save(str(tokenizer_json))

    # Test adapter
    adapter = HFTokenizerAdapter(str(tokenizer_json))

    # Basic properties
    assert adapter.vocab_size > 0, "vocab_size must be greater than zero"
    assert adapter.pad_token_id >= 0, "pad_token_id must be greater than zero"
    assert adapter.eos_token_id >= 0, "eos_token_id must be greater than zero"

    # Encode/decode roundtrip
    text = "hello world"
    ids = adapter.encode(text)
    assert isinstance(ids, list)
    assert all(isinstance(i, int) for i in ids)

    decoded = adapter.decode(ids)
    assert isinstance(decoded, str)


@pytest.mark.skipif(not HAS_SENTENCEPIECE, reason="requires sentencepiece")
def test_sentencepiece_adapter_basic(tmp_path):
    """Test basic SentencePiece adapter functionality."""
    from codex_ml.tokenization.sentencepiece_adapter import SentencePieceAdapter

    # Create a small corpus for training
    corpus_file = tmp_path / "corpus.txt"
    corpus_file.write_text("hello world\nhello codex\ntest sentencepiece\n", encoding="utf-8")

    # Train a tiny model
    model_path = tmp_path / "sp_model.model"
    adapter = SentencePieceAdapter(model_path)
    adapter.train_or_load(
        input_path=corpus_file,
        vocab_size=100,
        character_coverage=0.98,
        model_type="unigram",
    )

    # Verify model was created
    assert model_path.exists(), "Condition must be true"

    # Test encode/decode - API contract requires these methods
    text = "hello world"
    ids = adapter.encode(text)
    assert isinstance(ids, (list, tuple))

    decoded = adapter.decode(ids)
    assert isinstance(decoded, str)


@pytest.mark.skipif(not HAS_SENTENCEPIECE, reason="requires sentencepiece")
def test_sentencepiece_adapter_load(tmp_path):
    """Test loading an existing SentencePiece model."""
    from codex_ml.tokenization.sentencepiece_adapter import SentencePieceAdapter

    # Create and train a model
    corpus_file = tmp_path / "corpus.txt"
    corpus_file.write_text("sample text for tokenization\n" * 10, encoding="utf-8")

    model_path = tmp_path / "test.model"
    adapter = SentencePieceAdapter(model_path)
    adapter.train_or_load(corpus_file, vocab_size=100)

    # Load the same model
    adapter2 = SentencePieceAdapter(model_path)
    loaded = adapter2.train_or_load(corpus_file, vocab_size=100)

    # Should load existing model rather than retrain
    assert loaded is not None, "loaded must be initialized"
    assert model_path.exists(), "Condition must be true"
