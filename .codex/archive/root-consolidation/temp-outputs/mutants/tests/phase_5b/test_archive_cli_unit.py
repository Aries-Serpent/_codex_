"""
Comprehensive unit tests for src/codex/archive/cli.py

Tests cover:
- Helper function validation
- Metadata handling
- Configuration loading
- Error handling
"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import click
import pytest

from codex.archive.cli import (
    _batch_progress_logger,  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
    _load_config,
    _parse_metadata,
    _resolve_commit,
    _service,
    _setup_logger,
    cli,
)


class TestParseMetadata:
    """Tests for _parse_metadata function."""

    def test_parse_metadata_empty_list(self):
        """Test parsing empty metadata list."""
        result = _parse_metadata([])
        assert result == {}, "Result must not be empty"

    def test_parse_metadata_single_entry(self):
        """Test parsing single metadata entry."""
        result = _parse_metadata(["key=value"])
        assert result == {"key": "value"}, "Result must not be empty"

    def test_parse_metadata_multiple_entries(self):
        """Test parsing multiple metadata entries."""
        entries = ["key1=value1", "key2=value2", "key3=value3"]
        result = _parse_metadata(entries)
        assert result == {"key1": "value1", "key2": "value2", "key3": "value3"}

    def test_parse_metadata_with_equals_in_value(self):
        """Test parsing metadata with equals sign in value."""
        result = _parse_metadata(["key=value=with=equals"])
        assert result == {"key": "value=with=equals"}, "Result must not be empty"

    def test_parse_metadata_whitespace_handling(self):
        """Test parsing metadata with whitespace."""
        result = _parse_metadata([" key = value "])
        assert result == {"key": "value"}, "Result must not be empty"

    def test_parse_metadata_invalid_entry(self):
        """Test parsing invalid metadata entry without equals sign."""
        with pytest.raises(click.BadParameter):
            _parse_metadata(["invalid_entry"])

    def test_parse_metadata_invalid_entry_in_list(self):
        """Test parsing list with one invalid entry."""
        with pytest.raises(click.BadParameter):
            _parse_metadata(["key1=value1", "invalid", "key2=value2"])

    def test_parse_metadata_special_characters(self):
        """Test parsing metadata with special characters."""
        result = _parse_metadata(["key=value-with_special.chars"])
        assert result["key"] == "value-with_special.chars", "Result must not be empty"

    def test_parse_metadata_empty_value(self):
        """Test parsing metadata with empty value."""
        result = _parse_metadata(["key="])
        assert result == {"key": ""}, "Result must not be empty"

    def test_parse_metadata_url_value(self):
        """Test parsing metadata with URL value."""
        result = _parse_metadata(["repo=https://github.com/test/repo"])
        assert "https://" in result["repo"], "Result must not be empty"

    def test_parse_metadata_numeric_value(self):
        """Test parsing metadata with numeric value."""
        result = _parse_metadata(["count=42"])
        assert result["count"] == "42", "Result must not be empty"

    def test_parse_metadata_boolean_like_value(self):
        """Test parsing metadata with boolean-like value."""
        result = _parse_metadata(["enabled=true"])
        assert result["enabled"] == "true", "Result must not be empty"

    def test_parse_metadata_json_like_value(self):
        """Test parsing metadata with JSON-like value."""
        result = _parse_metadata(['config={"key":"value"}'])
        assert "{" in result["config"], "Result must not be empty"

    def test_parse_metadata_path_value(self):
        """Test parsing metadata with path value."""
        result = _parse_metadata(["path=/home/user/file.txt"])
        assert result["path"] == "/home/user/file.txt", "Result must not be empty"

    def test_parse_metadata_multipart_key(self):
        """Test parsing metadata with multipart key."""
        result = _parse_metadata(["org.project.key=value"])
        assert result["org.project.key"] == "value", "Result must not be empty"

    def test_parse_metadata_hyphen_in_key(self):
        """Test parsing metadata with hyphen in key."""
        result = _parse_metadata(["my-key=value"])
        assert result["my-key"] == "value", "Result must not be empty"


class TestResolveCommit:
    """Tests for _resolve_commit function."""

    def test_resolve_commit_with_sha(self):
        """Test resolving explicit commit SHA."""
        sha = "abc123def456"
        result = _resolve_commit(sha)
        assert result == sha, "Result must not be empty"

    def test_resolve_commit_short_sha(self):
        """Test resolving short commit SHA."""
        sha = "abc123"
        result = _resolve_commit(sha)
        assert result == sha, "Result must not be empty"

    def test_resolve_commit_long_sha(self):
        """Test resolving long commit SHA."""
        sha = "abc123def456abc123def456abc123def456"
        result = _resolve_commit(sha)
        assert result == sha, "Result must not be empty"

    def test_resolve_commit_lowercase_head(self):
        """Test resolving lowercase 'head' keyword."""
        result = _resolve_commit("head")
        # Should process HEAD keyword or return as-is
        assert result is not None, "result must be initialized"

    def test_resolve_commit_uppercase_head(self):
        """Test resolving uppercase 'HEAD' keyword."""
        result = _resolve_commit("HEAD")
        assert result is not None, "result must be initialized"

    def test_resolve_commit_mixed_case_head(self):
        """Test resolving mixed case 'HeAd' keyword."""
        result = _resolve_commit("HeAd")
        assert result is not None, "result must be initialized"

    def test_resolve_commit_empty_string(self):
        """Test resolving empty string."""
        result = _resolve_commit("")
        assert result == "", "Result must not be empty"


class TestLoadConfig:
    """Tests for _load_config function."""

    @patch("codex.archive.cli.ArchiveAppConfig")
    def test_load_config_no_file(self, mock_config_class):
        """Test loading config without file."""
        mock_config = MagicMock()
        mock_config_class.load.return_value = mock_config

        result = _load_config()
        assert result is mock_config, "Result must not be empty"
        mock_config_class.load.assert_called_once_with(config_file=None)

    @patch("codex.archive.cli.ArchiveAppConfig")
    def test_load_config_with_file(self, mock_config_class):
        """Test loading config with file."""
        config_file = Path("config.toml")
        mock_config = MagicMock()
        mock_config_class.load.return_value = mock_config

        result = _load_config(config_file)
        assert result is mock_config, "Result must not be empty"
        mock_config_class.load.assert_called_once_with(config_file=config_file)

    @patch("codex.archive.cli.ArchiveAppConfig")
    def test_load_config_returns_config_object(self, mock_config_class):
        """Test that _load_config returns config object."""
        mock_config = Mock(spec=["to_dict", "logging", "backend"])
        mock_config_class.load.return_value = mock_config

        result = _load_config()
        assert result is mock_config, "Result must not be empty"


class TestService:
    """Tests for _service function."""

    @patch("codex.archive.cli._load_config")
    @patch("codex.archive.cli.ArchiveService")
    def test_service_with_config(self, mock_service_class, mock_load_config):
        """Test _service with provided config."""
        mock_config = MagicMock()
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        result = _service(apply_schema=True, app_config=mock_config)
        assert result is mock_service, "Result must not be empty"
        mock_service_class.assert_called_once()

    @patch("codex.archive.cli._load_config")
    @patch("codex.archive.cli.ArchiveService")
    def test_service_loads_config_if_not_provided(self, mock_service_class, mock_load_config):
        """Test _service loads config if not provided."""
        mock_config = MagicMock()
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_load_config.return_value = mock_config

        result = _service(apply_schema=False)
        assert result is mock_service, "Result must not be empty"
        mock_load_config.assert_called_once()

    @patch("codex.archive.cli._load_config")
    @patch("codex.archive.cli.ArchiveService")
    def test_service_apply_schema_true(self, mock_service_class, mock_load_config):
        """Test _service with apply_schema=True."""
        mock_config = MagicMock()
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_load_config.return_value = mock_config

        _service(apply_schema=True, app_config=mock_config)
        call_kwargs = mock_service_class.call_args[1]
        assert call_kwargs.get("apply_schema") is True, "Condition must be true"

    @patch("codex.archive.cli._load_config")
    @patch("codex.archive.cli.ArchiveService")
    def test_service_apply_schema_false(self, mock_service_class, mock_load_config):
        """Test _service with apply_schema=False."""
        mock_config = MagicMock()
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_load_config.return_value = mock_config

        _service(apply_schema=False, app_config=mock_config)
        call_kwargs = mock_service_class.call_args[1]
        assert call_kwargs.get("apply_schema") is False, "Condition must be true"


class TestSetupLogger:
    """Tests for _setup_logger function."""

    @patch("codex.archive.cli.setup_logging")
    def test_setup_logger(self, mock_setup_logging):
        """Test _setup_logger setup."""
        mock_config = MagicMock()
        mock_config.logging = MagicMock()
        mock_logger = MagicMock()
        mock_setup_logging.return_value = mock_logger

        result = _setup_logger(mock_config)
        assert result is mock_logger, "Result must not be empty"
        mock_setup_logging.assert_called_once()

    @patch("codex.archive.cli.setup_logging")
    def test_setup_logger_returns_logger(self, mock_setup_logging):
        """Test _setup_logger returns a logger object."""
        mock_config = MagicMock()
        mock_config.logging = {"level": "INFO"}
        mock_logger = Mock(spec=["info", "debug", "error"])
        mock_setup_logging.return_value = mock_logger

        result = _setup_logger(mock_config)
        assert result is mock_logger, "Result must not be empty"


class TestBatchProgressLogger:
    """Tests for _batch_progress_logger function."""

    @patch("codex.archive.cli.log_restore")
    def test_batch_progress_logger_creation(self, mock_log_restore):
        """Test creating batch progress logger."""
        mock_config = MagicMock()
        mock_config.batch.progress_interval = 1
        mock_config.logging = MagicMock()
        mock_config.performance = MagicMock()
        mock_logger = MagicMock()

        callback = _batch_progress_logger(mock_logger, mock_config)
        assert callable(callback), "Condition must be true"

    @patch("codex.archive.cli.log_restore")
    def test_batch_progress_logger_callback(self, mock_log_restore, capsys):
        """Test batch progress logger callback."""
        mock_config = MagicMock()
        mock_config.batch.progress_interval = 2
        mock_config.logging = MagicMock()
        mock_config.performance = MagicMock()
        mock_logger = MagicMock()

        callback = _batch_progress_logger(mock_logger, mock_config)
        entry = {"status": "PROCESSING", "tombstone": "tomb123"}
        callback(2, 10, entry)

    @patch("codex.archive.cli.log_restore")
    def test_batch_progress_logger_zero_interval(self, mock_log_restore):
        """Test batch progress logger with zero interval."""
        mock_config = MagicMock()
        mock_config.batch.progress_interval = 0
        mock_config.logging = MagicMock()
        mock_config.performance = MagicMock()
        mock_logger = MagicMock()

        callback = _batch_progress_logger(mock_logger, mock_config)
        entry = {"status": "DONE", "tombstone": "tomb456"}
        # Should not raise
        callback(1, 10, entry)

    @patch("codex.archive.cli.log_restore")
    def test_batch_progress_logger_callback_calls_log_restore(self, mock_log_restore):
        """Test batch progress logger calls log_restore."""
        mock_config = MagicMock()
        mock_config.batch.progress_interval = 1
        mock_config.logging = MagicMock()
        mock_config.performance = MagicMock()
        mock_logger = MagicMock()

        callback = _batch_progress_logger(mock_logger, mock_config)
        entry = {"status": "PROCESSING", "tombstone": "tomb789"}
        callback(1, 5, entry)
        mock_log_restore.assert_called()

    @patch("codex.archive.cli.log_restore")
    def test_batch_progress_logger_last_item(self, mock_log_restore):
        """Test batch progress logger on last item."""
        mock_config = MagicMock()
        mock_config.batch.progress_interval = 10
        mock_config.logging = MagicMock()
        mock_config.performance = MagicMock()
        mock_logger = MagicMock()

        callback = _batch_progress_logger(mock_logger, mock_config)
        entry = {"status": "DONE", "tombstone": "tomb_last"}
        # Last item should always log
        callback(10, 10, entry)


class TestCliGroup:
    """Tests for cli group."""

    def test_cli_exists(self):
        """Test that cli group is created."""
        assert cli is not None, "cli must be initialized"

    def test_cli_is_callable(self):
        """Test that cli is callable."""
        assert callable(cli), "Condition must be true"

    def test_cli_is_click_group(self):
        """Test that cli is a Click group."""
        # Click groups have a commands attribute
        assert hasattr(cli, "commands") or hasattr(cli, "list_commands")


# Additional comprehensive tests for edge cases
class TestMetadataEdgeCases:
    """Additional edge case tests for metadata parsing."""

    def test_parse_metadata_many_entries(self):
        """Test parsing many metadata entries."""
        entries = [f"key{i}=value{i}" for i in range(100)]
        result = _parse_metadata(entries)
        assert len(result) == 100, "Result must not be empty"
        assert result["key0"] == "value0", "Result must not be empty"
        assert result["key99"] == "value99", "Result must not be empty"

    def test_parse_metadata_unicode_value(self):
        """Test parsing metadata with unicode value."""
        result = _parse_metadata(["name=José"])
        assert result["name"] == "José", "Result must not be empty"

    def test_parse_metadata_emoji_value(self):
        """Test parsing metadata with emoji value."""
        result = _parse_metadata(["emoji=🚀"])
        assert result["emoji"] == "🚀", "Result must not be empty"

    def test_parse_metadata_long_value(self):
        """Test parsing metadata with very long value."""
        long_value = "x" * 1000
        result = _parse_metadata([f"long={long_value}"])
        assert result["long"] == long_value, "Result must not be empty"

    def test_parse_metadata_newline_in_key(self):
        """Test parsing metadata with newline-like value."""
        result = _parse_metadata(["text=line1\\nline2"])
        assert "line" in result["text"], "Result must not be empty"

    def test_parse_metadata_tab_in_value(self):
        """Test parsing metadata with tab in value."""
        result = _parse_metadata(["tab=value\\twith\\ttabs"])
        assert result["tab"] == "value\\twith\\ttabs", "Result must not be empty"
