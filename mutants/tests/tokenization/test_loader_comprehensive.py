"""
Test Tokenizer Loader Module

Comprehensive tests for src/tokenization/loader.py covering:
- Special token defaults and fallbacks
- File-based tokenizer loading
- Remote model loading
- Offline loading behavior
- Config validation and error handling
"""

import json
from unittest.mock import MagicMock, patch

import pytest


def test_ensure_special_tokens_pad_fallback():
    """Test: Special Token Defaults - Verify pad_token fallback logic."""
    from src.tokenization.loader import _ensure_special_tokens

    # Create mock tokenizer with no special tokens
    mock_tokenizer = MagicMock()
    mock_tokenizer.pad_token = None
    mock_tokenizer.eos_token = "[EOS]"
    mock_tokenizer.unk_token = "[UNK]"
    mock_tokenizer.pad_token_id = None

    # Call _ensure_special_tokens
    result = _ensure_special_tokens(mock_tokenizer)

    # Verify pad_token falls back to eos_token
    assert result.pad_token == "[EOS]", "Result must not be empty"

    # Verify add_special_tokens was called
    result.add_special_tokens.assert_called_once()
    call_args = result.add_special_tokens.call_args[0][0]
    assert "pad_token" in call_args, "Condition must be true"


def test_ensure_special_tokens_eos_fallback():
    """Test: Special Token Defaults - Verify eos_token fallback logic."""
    from src.tokenization.loader import _ensure_special_tokens

    # Create mock tokenizer with pad but no eos
    mock_tokenizer = MagicMock()
    mock_tokenizer.pad_token = "[PAD]"
    mock_tokenizer.eos_token = None
    mock_tokenizer.pad_token_id = 0

    # Call _ensure_special_tokens
    result = _ensure_special_tokens(mock_tokenizer)

    # Verify eos_token falls back to pad_token
    assert result.eos_token == "[PAD]", "Result must not be empty"

    # Verify result is the same tokenizer
    assert result is mock_tokenizer, "Result must not be empty"


def test_ensure_special_tokens_default_pad():
    """Test: Special Token Defaults - Verify default [PAD] when no tokens exist."""
    from src.tokenization.loader import _ensure_special_tokens

    # Create mock tokenizer with no special tokens at all
    mock_tokenizer = MagicMock()
    mock_tokenizer.pad_token = None
    mock_tokenizer.eos_token = None
    mock_tokenizer.unk_token = None
    mock_tokenizer.pad_token_id = None

    # Call _ensure_special_tokens
    result = _ensure_special_tokens(mock_tokenizer)

    # Verify pad_token gets default [PAD]
    assert result.pad_token == "[PAD]", "Result must not be empty"
    assert result.eos_token == "[PAD]", "Result must not be empty"


def test_load_from_file_basic(tmp_path):
    """Test: Load from File Path - Verify tokenizer loading from JSON file."""
    from src.tokenization.loader import _load_from_file

    # Create a mock tokenizer JSON file
    tokenizer_file = tmp_path / "tokenizer.json"
    tokenizer_data = {
        "version": "1.0",
        "model": {"type": "BPE", "vocab": {}, "merges": []},
    }
    tokenizer_file.write_text(json.dumps(tokenizer_data), encoding="utf-8")

    # Mock the Tokenizer.from_file and PreTrainedTokenizerFast
    with patch("src.tokenization.loader.Tokenizer") as mock_tokenizer_cls:
        with patch("src.tokenization.loader.PreTrainedTokenizerFast") as mock_fast_cls:
            # Setup mocks
            mock_tok_obj = MagicMock()
            mock_tokenizer_cls.from_file.return_value = mock_tok_obj

            mock_fast = MagicMock()
            mock_fast.pad_token = "[PAD]"
            mock_fast.eos_token = "[EOS]"
            mock_fast.pad_token_id = 0
            mock_fast_cls.return_value = mock_fast

            # Call _load_from_file
            result = _load_from_file(tokenizer_file)

            # Verify Tokenizer.from_file was called with correct path
            mock_tokenizer_cls.from_file.assert_called_once_with(str(tokenizer_file))

            # Verify PreTrainedTokenizerFast was instantiated
            mock_fast_cls.assert_called_once_with(tokenizer_object=mock_tok_obj)

            # Verify model_max_length was set
            assert result.model_max_length == 512, "Result must not be empty"


def test_load_from_file_special_tokens_configured(tmp_path):
    """Test: Load from File - Verify special tokens are configured correctly."""
    from src.tokenization.loader import _load_from_file

    tokenizer_file = tmp_path / "tokenizer.json"
    tokenizer_file.write_text('{"version": "1.0"}', encoding="utf-8")

    with patch("src.tokenization.loader.Tokenizer") as mock_tokenizer_cls:
        with patch("src.tokenization.loader.PreTrainedTokenizerFast") as mock_fast_cls:
            mock_tok_obj = MagicMock()
            mock_tokenizer_cls.from_file.return_value = mock_tok_obj

            # Create mock with no special tokens initially
            mock_fast = MagicMock()
            mock_fast.pad_token = None
            mock_fast.eos_token = None
            mock_fast.unk_token = "[UNK]"
            mock_fast.pad_token_id = None
            mock_fast_cls.return_value = mock_fast

            # Call _load_from_file
            result = _load_from_file(tokenizer_file)

            # Verify special tokens were configured
            # After _ensure_special_tokens, pad_token should be set
            assert result.add_special_tokens.called, "Result must not be empty"


def test_load_from_model_name_remote(tmp_path):
    """Test: Load from Model Name (Remote) - Verify loading with allow_remote=True."""
    from src.tokenization.loader import _load_from_model_name

    model_name = "bert-base-uncased"
    cache_dir = tmp_path / "cache"

    # Mock the load_from_pretrained function (from codex_ml.utils.hf_pinning)
    with patch("codex_ml.utils.hf_pinning.load_from_pretrained") as mock_load:
        # Setup mock tokenizer
        mock_tokenizer = MagicMock()
        mock_tokenizer.pad_token = "[PAD]"
        mock_tokenizer.eos_token = "[SEP]"
        mock_tokenizer.pad_token_id = 0
        mock_load.return_value = mock_tokenizer

        # Call with allow_remote=True
        _load_from_model_name(model_name, cache_dir, allow_remote=True)

        # Verify load_from_pretrained was called with correct arguments
        mock_load.assert_called_once()
        call_kwargs = mock_load.call_args[1]
        assert call_kwargs["cache_dir"] == str(cache_dir), "Condition must be true"
        assert call_kwargs["local_files_only"] is False, "Condition must be true"


def test_load_from_model_name_offline(tmp_path):
    """Test: Load from Model Name (Offline) - Verify local_files_only=True."""
    from src.tokenization.loader import _load_from_model_name

    model_name = "gpt2"
    cache_dir = tmp_path / "cache"

    with patch("codex_ml.utils.hf_pinning.load_from_pretrained") as mock_load:
        mock_tokenizer = MagicMock()
        mock_tokenizer.pad_token = "<|endoftext|>"
        mock_tokenizer.eos_token = "<|endoftext|>"
        mock_tokenizer.pad_token_id = 50256
        mock_load.return_value = mock_tokenizer

        # Call with allow_remote=False
        _load_from_model_name(model_name, cache_dir, allow_remote=False)

        # Verify local_files_only=True when allow_remote=False
        call_kwargs = mock_load.call_args[1]
        assert call_kwargs["local_files_only"] is True, "Condition must be true"


def test_load_from_model_name_with_cache_dir(tmp_path):
    """Test: Load from Model Name - Verify cache_dir is used correctly."""
    from src.tokenization.loader import _load_from_model_name

    model_name = "distilbert-base-uncased"
    cache_dir = tmp_path / "custom_cache"

    with patch("codex_ml.utils.hf_pinning.load_from_pretrained") as mock_load:
        mock_tokenizer = MagicMock()
        mock_tokenizer.pad_token = "[PAD]"
        mock_tokenizer.eos_token = "[SEP]"
        mock_tokenizer.pad_token_id = 0
        mock_load.return_value = mock_tokenizer

        _load_from_model_name(model_name, cache_dir, allow_remote=True)

        # Verify cache_dir was passed as string
        call_kwargs = mock_load.call_args[1]
        assert call_kwargs["cache_dir"] == str(cache_dir), "Condition must be true"


def test_load_tokenizer_with_tokenizer_file(tmp_path):
    """Test: Config Validation - Load with tokenizer_file config."""
    from src.tokenization.loader import load_tokenizer

    # Create mock tokenizer file
    tokenizer_file = tmp_path / "tokenizer.json"
    tokenizer_file.write_text('{"version": "1.0"}', encoding="utf-8")

    config = {"tokenizer_file": str(tokenizer_file)}

    with patch("src.tokenization.loader._load_from_file") as mock_load_file:
        mock_tokenizer = MagicMock()
        mock_load_file.return_value = mock_tokenizer

        result = load_tokenizer(config)

        # Verify _load_from_file was called
        mock_load_file.assert_called_once()
        assert result is mock_tokenizer, "Result must not be empty"


def test_load_tokenizer_with_model_name(tmp_path):
    """Test: Config Validation - Load with model_name config."""
    from src.tokenization.loader import load_tokenizer

    config = {"model_name": "gpt2"}
    cache_dir = tmp_path / "cache"

    with patch("src.tokenization.loader._load_from_model_name") as mock_load_model:
        mock_tokenizer = MagicMock()
        mock_load_model.return_value = mock_tokenizer

        load_tokenizer(config, cache_dir=cache_dir, allow_remote=False)

        # Verify _load_from_model_name was called with correct args
        mock_load_model.assert_called_once()
        call_args = mock_load_model.call_args[0]
        assert call_args[0] == "gpt2", "Condition must be true"
        assert call_args[2] is False, "Condition must be true"


def test_load_tokenizer_missing_file_error():
    """Test: Config Validation Errors - FileNotFoundError for missing file."""
    from src.tokenization.loader import load_tokenizer

    config = {"tokenizer_file": "/nonexistent/path/tokenizer.json"}

    # Verify FileNotFoundError is raised with correct message
    with pytest.raises(FileNotFoundError, match="tokenizer file not found"):
        load_tokenizer(config)


def test_load_tokenizer_missing_config_error():
    """Test: Config Validation Errors - ValueError for missing config keys."""
    from src.tokenization.loader import load_tokenizer

    # Empty config should raise ValueError
    config = {}

    with pytest.raises(ValueError, match="must provide 'model_name_or_path' or 'tokenizer_file'"):
        load_tokenizer(config)


def test_load_tokenizer_with_vocab_file_alias(tmp_path):
    """Test: Config Validation - Accept vocab_file as alias for tokenizer_file."""
    from src.tokenization.loader import load_tokenizer

    vocab_file = tmp_path / "vocab.json"
    vocab_file.write_text('{"version": "1.0"}', encoding="utf-8")

    config = {"vocab_file": str(vocab_file)}

    with patch("src.tokenization.loader._load_from_file") as mock_load_file:
        mock_tokenizer = MagicMock()
        mock_load_file.return_value = mock_tokenizer

        load_tokenizer(config)

        # Verify _load_from_file was called (vocab_file is recognized)
        mock_load_file.assert_called_once()


def test_load_tokenizer_with_model_name_or_path_alias():
    """Test: Config Validation - Accept model_name_or_path alias."""
    from src.tokenization.loader import load_tokenizer

    config = {"model_name_or_path": "bert-base-uncased"}

    with patch("src.tokenization.loader._load_from_model_name") as mock_load_model:
        mock_tokenizer = MagicMock()
        mock_load_model.return_value = mock_tokenizer

        load_tokenizer(config)

        # Verify model name was recognized
        mock_load_model.assert_called_once()
        call_args = mock_load_model.call_args[0]
        assert call_args[0] == "bert-base-uncased", "Condition must be true"


def test_load_tokenizer_cache_dir_creation(tmp_path):
    """Test: Cache Directory - Verify cache_dir is created if missing."""
    from src.tokenization.loader import load_tokenizer

    cache_dir = tmp_path / "new_cache" / "nested"
    config = {"model_name": "gpt2"}

    with patch("src.tokenization.loader._load_from_model_name") as mock_load_model:
        mock_tokenizer = MagicMock()
        mock_load_model.return_value = mock_tokenizer

        load_tokenizer(config, cache_dir=cache_dir)

        # Verify cache directory was created
        assert cache_dir.exists(), "Condition must be true"


def test_load_tokenizer_none_config():
    """Test: Config Validation - Handle None config gracefully."""
    from src.tokenization.loader import load_tokenizer

    # None config should be treated as empty dict
    with pytest.raises(ValueError, match="must provide"):
        load_tokenizer(None)


def test_load_tokenizer_prefers_file_over_model():
    """Test: Config Priority - tokenizer_file takes precedence over model_name."""
    from src.tokenization.loader import load_tokenizer

    # When both are provided, file should be used
    with patch("src.tokenization.loader._load_from_file") as mock_load_file:
        with patch("src.tokenization.loader._load_from_model_name") as mock_load_model:
            # Create a temporary file
            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                f.write('{"version": "1.0"}')
                temp_file = f.name

            try:
                config = {"tokenizer_file": temp_file, "model_name": "gpt2"}

                mock_tokenizer = MagicMock()
                mock_load_file.return_value = mock_tokenizer

                load_tokenizer(config)

                # Verify file loader was called, not model loader
                mock_load_file.assert_called_once()
                mock_load_model.assert_not_called()
            finally:
                # Cleanup temp file
                import os

                os.unlink(temp_file)
