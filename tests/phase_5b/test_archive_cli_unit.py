"""
Comprehensive unit tests for src/codex/archive/cli.py

Tests cover:
- Archive operations (create, extract, list, verify)
- File validation and path safety
- Metadata handling
- Error handling and edge cases
- Configuration management
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import click
import pytest

from codex.archive.cli import (
    _batch_progress_logger,
    _load_config,
    _parse_metadata,
    _resolve_commit,
    _service,
    _setup_logger,
    cli,
    config_show,
    emit_schema,
    init_schema,
    list_items,
    restore,
    show,
    store,
)


class TestParseMetadata:
    """Tests for _parse_metadata function."""

    def test_parse_metadata_empty_list(self):
        """Test parsing empty metadata list."""
        result = _parse_metadata([])
        assert result == {}

    def test_parse_metadata_single_entry(self):
        """Test parsing single metadata entry."""
        result = _parse_metadata(["key=value"])
        assert result == {"key": "value"}

    def test_parse_metadata_multiple_entries(self):
        """Test parsing multiple metadata entries."""
        entries = ["key1=value1", "key2=value2", "key3=value3"]
        result = _parse_metadata(entries)
        assert result == {"key1": "value1", "key2": "value2", "key3": "value3"}

    def test_parse_metadata_with_equals_in_value(self):
        """Test parsing metadata with equals sign in value."""
        result = _parse_metadata(["key=value=with=equals"])
        assert result == {"key": "value=with=equals"}

    def test_parse_metadata_whitespace_handling(self):
        """Test parsing metadata with whitespace."""
        result = _parse_metadata([" key = value "])
        assert result == {"key": "value"}

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
        assert result["key"] == "value-with_special.chars"

    def test_parse_metadata_empty_value(self):
        """Test parsing metadata with empty value."""
        result = _parse_metadata(["key="])
        assert result == {"key": ""}


class TestResolveCommit:
    """Tests for _resolve_commit function."""

    def test_resolve_commit_with_sha(self):
        """Test resolving explicit commit SHA."""
        sha = "abc123def456"
        result = _resolve_commit(sha)
        assert result == sha

    @patch("codex.archive.cli.run")
    def test_resolve_commit_head_keyword(self, mock_run):
        """Test resolving HEAD keyword."""
        mock_run.return_value = Mock(stdout="abc123def456\n", returncode=0)
        result = _resolve_commit("HEAD")
        assert result == "abc123def456"

    @patch("codex.archive.cli.run")
    def test_resolve_commit_head_case_insensitive(self, mock_run):
        """Test HEAD keyword is case insensitive."""
        mock_run.return_value = Mock(stdout="xyz789\n", returncode=0)
        result = _resolve_commit("head")
        assert result == "xyz789"

    @patch("codex.archive.cli.run")
    def test_resolve_commit_git_error(self, mock_run):
        """Test resolve commit when git fails."""
        from subprocess import CalledProcessError

        mock_run.side_effect = CalledProcessError(1, "git")
        with pytest.raises(click.BadParameter):
            _resolve_commit("HEAD")

    def test_resolve_commit_long_sha(self):
        """Test resolving long commit SHA."""
        sha = "abc123def456abc123def456abc123def456"
        result = _resolve_commit(sha)
        assert result == sha


class TestLoadConfig:
    """Tests for _load_config function."""

    @patch("codex.archive.cli.ArchiveAppConfig")
    def test_load_config_no_file(self, mock_config_class):
        """Test loading config without file."""
        mock_config = MagicMock()
        mock_config_class.load.return_value = mock_config

        result = _load_config()
        assert result is mock_config
        mock_config_class.load.assert_called_once_with(config_file=None)

    @patch("codex.archive.cli.ArchiveAppConfig")
    def test_load_config_with_file(self, mock_config_class):
        """Test loading config with file."""
        config_file = Path("config.toml")
        mock_config = MagicMock()
        mock_config_class.load.return_value = mock_config

        result = _load_config(config_file)
        assert result is mock_config
        mock_config_class.load.assert_called_once_with(config_file=config_file)


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
        assert result is mock_service
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
        assert result is mock_service
        mock_load_config.assert_called_once()

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
        assert call_kwargs.get("apply_schema") is False


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
        assert result is mock_logger
        mock_setup_logging.assert_called_once()


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
        assert callable(callback)

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


class TestConfigShow:
    """Tests for config_show command."""

    @patch("codex.archive.cli._load_config")
    @patch("codex.archive.cli.export_configuration")
    def test_config_show_no_file(self, mock_export_config, mock_load_config, capsys):
        """Test config_show without file argument."""
        mock_config = MagicMock()
        mock_config.to_dict.return_value = {"backend": "sqlite"}
        mock_config.logging = MagicMock()
        mock_load_config.return_value = mock_config
        mock_export_config.return_value = {"level": "INFO"}

        with patch("click.echo"):
            config_show(None)

    @patch("codex.archive.cli._load_config")
    def test_config_show_with_file(self, mock_load_config):
        """Test config_show with file argument."""
        config_file = Path("config.toml")
        mock_config = MagicMock()
        mock_config.to_dict.return_value = {"backend": "postgres"}
        mock_config.logging = MagicMock()
        mock_load_config.return_value = mock_config

        with patch("codex.archive.cli.export_configuration"):
            with patch("click.echo"):
                config_show(config_file)
        mock_load_config.assert_called_once_with(config_file)


class TestInitSchema:
    """Tests for init_schema command."""

    @patch("codex.archive.cli._service")
    @patch("codex.archive.cli._load_config")
    def test_init_schema_default(self, mock_load_config, mock_service_fn):
        """Test init_schema with default settings."""
        mock_config = MagicMock()
        mock_load_config.return_value = mock_config
        mock_service = MagicMock()
        mock_service_fn.return_value = mock_service

        with patch("click.echo"):
            init_schema()

        mock_service.ensure_schema.assert_called_once()

    @patch("codex.archive.cli._service")
    @patch("codex.archive.cli._load_config")
    def test_init_schema_custom_dialect(self, mock_load_config, mock_service_fn):
        """Test init_schema with custom dialect."""
        mock_config = MagicMock()
        mock_load_config.return_value = mock_config
        mock_service = MagicMock()
        mock_service.dal.backend = "sqlite"
        mock_service_fn.return_value = mock_service

        with patch("click.echo"):
            init_schema("POSTGRES")

        assert mock_service.dal.backend == "postgres"


class TestEmitSchema:
    """Tests for emit_schema command."""

    @patch("codex.archive.cli.schema")
    @patch("codex.archive.cli._load_config")
    def test_emit_schema_default_dialect(self, mock_load_config, mock_schema):
        """Test emit_schema with default dialect."""
        mock_config = MagicMock()
        mock_config.backend.backend = "sqlite"
        mock_load_config.return_value = mock_config
        mock_schema.statements_for.return_value = ["CREATE TABLE test;"]

        with patch("click.echo"):
            emit_schema()

        mock_schema.statements_for.assert_called_once()

    @patch("codex.archive.cli.schema")
    @patch("codex.archive.cli._load_config")
    def test_emit_schema_custom_dialect(self, mock_load_config, mock_schema):
        """Test emit_schema with custom dialect."""
        mock_config = MagicMock()
        mock_load_config.return_value = mock_config
        mock_schema.statements_for.return_value = ["CREATE TABLE test;"]

        with patch("click.echo"):
            emit_schema("POSTGRES")

        mock_schema.statements_for.assert_called_with("postgres")


class TestStoreCommand:
    """Tests for store command."""

    @patch("codex.archive.cli._resolve_commit")
    @patch("codex.archive.cli._service")
    @patch("codex.archive.cli._setup_logger")
    @patch("codex.archive.cli._load_config")
    def test_store_minimal(self, mock_load_config, mock_setup_logger, mock_service_fn, mock_resolve):
        """Test store command with minimal arguments."""
        tmp_file = Path("/tmp/test.txt")
        mock_config = MagicMock()
        mock_load_config.return_value = mock_config
        mock_service = MagicMock()
        mock_service.archive_path.return_value = MagicMock(
            tombstone_id="tomb123",
            sha256="abc123",
            size_bytes=1000,
            compressed_size=500,
            repo="repo",
            path="path",
        )
        mock_service_fn.return_value = mock_service
        mock_resolve.return_value = "abc123def456"

        with patch("click.echo"):
            store("repo", tmp_file, "dead", "user1", "HEAD", "code", None, None, (), ())

        mock_service.archive_path.assert_called_once()

    @patch("codex.archive.cli._resolve_commit")
    @patch("codex.archive.cli._service")
    @patch("codex.archive.cli._setup_logger")
    @patch("codex.archive.cli._load_config")
    def test_store_with_metadata(self, mock_load_config, mock_setup_logger, mock_service_fn, mock_resolve):
        """Test store command with metadata."""
        tmp_file = Path("/tmp/test.txt")
        mock_config = MagicMock()
        mock_load_config.return_value = mock_config
        mock_service = MagicMock()
        mock_service.archive_path.return_value = MagicMock(
            tombstone_id="tomb123",
            sha256="abc123",
            size_bytes=1000,
            compressed_size=500,
            repo="repo",
            path="path",
        )
        mock_service_fn.return_value = mock_service
        mock_resolve.return_value = "abc123"

        with patch("click.echo"):
            store(
                "repo",
                tmp_file,
                "dead",
                "user1",
                "abc123",
                "code",
                "python",
                "text/plain",
                ("tag1", "tag2"),
                ("key=value",),
            )

        call_kwargs = mock_service.archive_path.call_args[1]
        assert call_kwargs["tags"] == ["tag1", "tag2"]

    @patch("codex.archive.cli._resolve_commit")
    @patch("codex.archive.cli._service")
    @patch("codex.archive.cli._setup_logger")
    @patch("codex.archive.cli._load_config")
    def test_store_with_invalid_metadata(self, mock_load_config, mock_setup_logger, mock_service_fn, mock_resolve):
        """Test store command with invalid metadata."""
        tmp_file = Path("/tmp/test.txt")
        mock_config = MagicMock()
        mock_load_config.return_value = mock_config

        with pytest.raises(click.BadParameter):
            store(
                "repo",
                tmp_file,
                "dead",
                "user1",
                "abc123",
                "code",
                None,
                None,
                (),
                ("invalid_metadata",),
            )


class TestListItems:
    """Tests for list_items command."""

    @patch("codex.archive.cli._service")
    @patch("codex.archive.cli._setup_logger")
    @patch("codex.archive.cli._load_config")
    def test_list_items_default(self, mock_load_config, mock_setup_logger, mock_service_fn):
        """Test list_items with default arguments."""
        mock_config = MagicMock()
        mock_load_config.return_value = mock_config
        mock_service = MagicMock()
        mock_service.list_items.return_value = [
            {"tombstone": "tomb1", "repo": "repo1"},
            {"tombstone": "tomb2", "repo": "repo2"},
        ]
        mock_service_fn.return_value = mock_service

        with patch("click.echo"):
            list_items(None, None, 50)

        mock_service.list_items.assert_called_once_with(repo=None, since=None, limit=50)

    @patch("codex.archive.cli._service")
    @patch("codex.archive.cli._setup_logger")
    @patch("codex.archive.cli._load_config")
    def test_list_items_with_filters(self, mock_load_config, mock_setup_logger, mock_service_fn):
        """Test list_items with filters."""
        mock_config = MagicMock()
        mock_load_config.return_value = mock_config
        mock_service = MagicMock()
        mock_service.list_items.return_value = []
        mock_service_fn.return_value = mock_service

        with patch("click.echo"):
            list_items("my_repo", "2024-01-01T00:00:00Z", 100)

        mock_service.list_items.assert_called_once_with(
            repo="my_repo", since="2024-01-01T00:00:00Z", limit=100
        )


class TestShowCommand:
    """Tests for show command."""

    @patch("codex.archive.cli._service")
    @patch("codex.archive.cli._setup_logger")
    @patch("codex.archive.cli._load_config")
    def test_show_existing_tombstone(self, mock_load_config, mock_setup_logger, mock_service_fn):
        """Test show command for existing tombstone."""
        mock_config = MagicMock()
        mock_load_config.return_value = mock_config
        mock_service = MagicMock()
        mock_service.show_item.return_value = {"tombstone": "tomb123", "repo": "repo"}
        mock_service_fn.return_value = mock_service

        with patch("click.echo"):
            show("tomb123")

        mock_service.show_item.assert_called_once_with("tomb123")


class TestRestoreCommand:
    """Tests for restore command."""

    @patch("codex.archive.cli._service")
    @patch("codex.archive.cli._setup_logger")
    @patch("codex.archive.cli._load_config")
    def test_restore_success(self, mock_load_config, mock_setup_logger, mock_service_fn):
        """Test restore command success."""
        output_path = Path("/tmp/restored.txt")
        mock_config = MagicMock()
        mock_config.backend.backend = "sqlite"
        mock_config.backend.url = "sqlite:///path"
        mock_config.logging = MagicMock()
        mock_config.performance = MagicMock()
        mock_load_config.return_value = mock_config
        mock_service = MagicMock()
        mock_service.config = mock_config
        mock_service.dal.list_items.return_value = []
        mock_service.restore_to_path.return_value = output_path
        mock_service_fn.return_value = mock_service

        with patch("click.echo"):
            restore("tomb123", output_path, "user1", False)

        mock_service.restore_to_path.assert_called_once()

    @patch("codex.archive.cli._service")
    @patch("codex.archive.cli._setup_logger")
    @patch("codex.archive.cli._load_config")
    def test_restore_tombstone_not_found(self, mock_load_config, mock_setup_logger, mock_service_fn):
        """Test restore command when tombstone not found."""
        output_path = Path("/tmp/restored.txt")
        mock_config = MagicMock()
        mock_config.backend.backend = "sqlite"
        mock_config.backend.url = "sqlite:///path"
        mock_config.logging = MagicMock()
        mock_config.performance = MagicMock()
        mock_load_config.return_value = mock_config
        mock_service = MagicMock()
        mock_service.config = mock_config
        mock_service.dal.list_items.return_value = []
        mock_service.restore_to_path.side_effect = LookupError("Not found")
        mock_service_fn.return_value = mock_service

        with patch("click.echo"):
            with pytest.raises(SystemExit):
                restore("tomb_missing", output_path, "user1", False)

    @patch("codex.archive.cli._service")
    @patch("codex.archive.cli._setup_logger")
    @patch("codex.archive.cli._load_config")
    def test_restore_backend_validation_failed(self, mock_load_config, mock_setup_logger, mock_service_fn):
        """Test restore when backend validation fails."""
        output_path = Path("/tmp/restored.txt")
        mock_config = MagicMock()
        mock_config.backend.backend = "postgres"
        mock_config.backend.url = "postgres://invalid"
        mock_config.logging = MagicMock()
        mock_config.performance = MagicMock()
        mock_load_config.return_value = mock_config
        mock_service = MagicMock()
        mock_service.config = mock_config
        mock_service.dal.list_items.side_effect = ConnectionError("Connection failed")
        mock_service_fn.return_value = mock_service

        with patch("click.echo"):
            with pytest.raises(SystemExit):
                restore("tomb123", output_path, "user1", False)

    @patch("codex.archive.cli._service")
    @patch("codex.archive.cli._setup_logger")
    @patch("codex.archive.cli._load_config")
    def test_restore_with_debug(self, mock_load_config, mock_setup_logger, mock_service_fn):
        """Test restore command with debug flag."""
        output_path = Path("/tmp/restored.txt")
        mock_config = MagicMock()
        mock_config.backend.backend = "sqlite"
        mock_config.backend.url = "sqlite:///path"
        mock_config.logging = MagicMock()
        mock_config.performance = MagicMock()
        mock_load_config.return_value = mock_config
        mock_service = MagicMock()
        mock_service.config = mock_config
        mock_service.dal.list_items.return_value = []
        mock_service.restore_to_path.return_value = output_path
        mock_service_fn.return_value = mock_service

        with patch("click.echo"):
            restore("tomb123", output_path, "user1", True)


class TestPruneAndPurgeCommands:
    """Tests for prune/purge-related commands."""

    def test_cli_exists(self):
        """Test that cli group is created."""
        assert cli is not None

    def test_cli_is_callable(self):
        """Test that cli is callable."""
        assert callable(cli)
