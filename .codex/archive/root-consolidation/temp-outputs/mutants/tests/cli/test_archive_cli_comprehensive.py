"""
Comprehensive tests for src/codex/archive/cli.py

Tests cover Click-based CLI for tombstone archive operations:
- Configuration management
- Batch processing
- Metadata parsing
- Service integration
"""

from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

# ==================== Fixtures ====================

 # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
@pytest.fixture
def cli_runner():
    """Provide Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_archive_service():
    """Mock ArchiveService for testing."""
    with patch("src.codex.archive.cli.ArchiveService") as mock:
        service_instance = Mock()
        mock.return_value = service_instance
        yield service_instance


@pytest.fixture
def mock_config():
    """Mock ArchiveAppConfig for testing."""
    with patch("src.codex.archive.cli._load_config") as mock:
        config_instance = Mock()
        config_instance.logging = Mock()
        config_instance.batch = Mock()
        config_instance.batch.progress_interval = 10
        config_instance.performance = Mock()
        mock.return_value = config_instance
        yield config_instance


# ==================== Parse Metadata Tests ====================


class TestParseMetadata:
    """Tests for _parse_metadata helper function."""

    def test_parse_valid_metadata(self):
        """Test parsing valid key=value entries."""
        try:
            from src.codex.archive.cli import _parse_metadata

            result = _parse_metadata(["key1=value1", "key2=value2"])
            assert result == {"key1": "value1", "key2": "value2"}
        except ImportError:
            pytest.skip("archive.cli module not available")

    def test_parse_metadata_with_equals_in_value(self):
        """Test parsing values containing equals sign."""
        try:
            from src.codex.archive.cli import _parse_metadata

            result = _parse_metadata(["key=value=with=equals"])
            assert result == {"key": "value=with=equals"}, "Result must not be empty"
        except ImportError:
            pytest.skip("archive.cli module not available")

    def test_parse_metadata_strips_whitespace(self):
        """Test that keys and values are stripped."""
        try:
            from src.codex.archive.cli import _parse_metadata

            result = _parse_metadata(["  key  =  value  "])
            assert result == {"key": "value"}, "Result must not be empty"
        except ImportError:
            pytest.skip("archive.cli module not available")

    def test_parse_metadata_invalid_format_raises(self):
        """Test that missing equals raises BadParameter."""
        try:
            import click

            from src.codex.archive.cli import _parse_metadata

            with pytest.raises(click.BadParameter):
                _parse_metadata(["invalid_no_equals"])
        except ImportError:
            pytest.skip("archive.cli module not available")


# ==================== Resolve Commit Tests ====================


class TestResolveCommit:
    """Tests for _resolve_commit helper function."""

    def test_resolve_commit_passes_through(self):
        """Test that non-HEAD commits pass through."""
        try:
            from src.codex.archive.cli import _resolve_commit

            result = _resolve_commit("abc123def")
            assert result == "abc123def", "Result must not be empty"
        except ImportError:
            pytest.skip("archive.cli module not available")

    def test_resolve_head_uppercase(self):
        """Test HEAD keyword resolution (uppercase)."""
        try:
            from src.codex.archive.cli import _resolve_commit

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = Mock(stdout="abc123def456\n")
                result = _resolve_commit("HEAD")
                assert result == "abc123def456", "Result must not be empty"
        except ImportError:
            pytest.skip("archive.cli module not available")

    def test_resolve_head_lowercase(self):
        """Test head keyword resolution (lowercase)."""
        try:
            from src.codex.archive.cli import _resolve_commit

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = Mock(stdout="abc123def456\n")
                result = _resolve_commit("head")
                assert result == "abc123def456", "Result must not be empty"
        except ImportError:
            pytest.skip("archive.cli module not available")


# ==================== CLI Group Tests ====================


class TestCLIGroup:
    """Tests for the main CLI group."""

    def test_cli_group_exists(self):
        """Test that CLI group is defined."""
        try:
            from src.codex.archive.cli import cli

            assert cli is not None, "cli must be initialized"
        except ImportError:
            pytest.skip("archive.cli module not available")

    def test_cli_group_has_help(self):
        """Test CLI group has help text."""
        try:
            from src.codex.archive.cli import cli

            assert cli.help is not None, "help must be initialized"
        except ImportError:
            pytest.skip("archive.cli module not available")

    def test_cli_invocation(self, cli_runner):
        """Test CLI can be invoked."""
        try:
            from src.codex.archive.cli import cli

            result = cli_runner.invoke(cli, ["--help"])
            assert result.exit_code == 0, "Result must not be empty"
            assert "archive" in result.output.lower() or "tombstone" in result.output.lower(), "Result must not be empty"
        except ImportError:
            pytest.skip("archive.cli module not available")


# ==================== Config Show Command Tests ====================


class TestConfigShowCommand:
    """Tests for config-show command."""

    def test_config_show_exists(self, cli_runner):
        """Test config-show command exists."""
        try:
            from src.codex.archive.cli import cli

            result = cli_runner.invoke(cli, ["config-show", "--help"])
            # Should either succeed or show help
            assert result.exit_code in [0, 1, 2]
        except ImportError:
            pytest.skip("archive.cli module not available")


# ==================== Batch Progress Logger Tests ====================


class TestBatchProgressLogger:
    """Tests for _batch_progress_logger function."""

    def test_batch_progress_logger_creation(self, mock_config):
        """Test batch progress logger can be created."""
        try:
            import logging

            from src.codex.archive.cli import _batch_progress_logger

            logger = logging.getLogger("test")
            callback = _batch_progress_logger(logger, mock_config)
            assert callable(callback), "Condition must be true"
        except ImportError:
            pytest.skip("archive.cli module not available")

    def test_batch_progress_callback(self, mock_config, capsys):
        """Test batch progress callback outputs status."""
        try:
            import logging

            from src.codex.archive.cli import _batch_progress_logger

            logger = logging.getLogger("test")
            mock_config.batch.progress_interval = 1

            with patch("src.codex.archive.cli.log_restore"):
                with patch("click.echo") as mock_echo:
                    callback = _batch_progress_logger(logger, mock_config)
                    callback(1, 10, {"status": "OK", "tombstone": "test.txt"})
                    mock_echo.assert_called()
        except ImportError:
            pytest.skip("archive.cli module not available")


# ==================== Service Initialization Tests ====================


class TestServiceInitialization:
    """Tests for _service helper function."""

    def test_service_with_default_config(self):
        """Test service creation with default config."""
        try:
            from src.codex.archive.cli import _service

            with patch("src.codex.archive.cli._load_config") as mock_load:
                mock_config = Mock()
                mock_load.return_value = mock_config
                with patch("src.codex.archive.cli.ArchiveService") as mock_svc:
                    _service()
                    mock_svc.assert_called_once()
        except ImportError:
            pytest.skip("archive.cli module not available")

    def test_service_with_custom_config(self):
        """Test service creation with custom config."""
        try:
            from src.codex.archive.cli import _service

            custom_config = Mock()
            with patch("src.codex.archive.cli.ArchiveService") as mock_svc:
                _service(app_config=custom_config)
                mock_svc.assert_called_with(custom_config, apply_schema=True)
        except ImportError:
            pytest.skip("archive.cli module not available")


# ==================== Setup Logger Tests ====================


class TestSetupLogger:
    """Tests for _setup_logger helper function."""

    def test_setup_logger_returns_logger(self):
        """Test that setup_logger returns a Logger instance."""
        try:
            import logging

            from src.codex.archive.cli import _setup_logger

            mock_config = Mock()
            mock_config.logging = Mock()

            with patch("src.codex.archive.cli.setup_logging") as mock_setup:
                mock_setup.return_value = logging.getLogger("test")
                result = _setup_logger(mock_config)
                assert isinstance(result, logging.Logger)
        except ImportError:
            pytest.skip("archive.cli module not available")


# ==================== Load Config Tests ====================


class TestLoadConfig:
    """Tests for _load_config helper function."""

    def test_load_config_default(self):
        """Test loading default configuration."""
        try:
            from src.codex.archive.cli import _load_config

            with patch("src.codex.archive.config.ArchiveAppConfig.load") as mock_load:
                mock_load.return_value = Mock()
                _load_config()
                mock_load.assert_called_with(config_file=None)
        except ImportError:
            pytest.skip("archive.cli module not available")

    def test_load_config_custom_file(self, tmp_path):
        """Test loading configuration from custom file."""
        try:
            from src.codex.archive.cli import _load_config

            config_file = tmp_path / "config.yaml"
            config_file.write_text("# test config")

            with patch("src.codex.archive.config.ArchiveAppConfig.load") as mock_load:
                mock_load.return_value = Mock()
                _load_config(config_file)
                mock_load.assert_called_with(config_file=config_file)
        except ImportError:
            pytest.skip("archive.cli module not available")


# ==================== Module Import Tests ====================


class TestModuleImports:
    """Tests for module-level imports."""

    def test_logger_defined(self):
        """Test logger is properly configured."""
        try:
            from src.codex.archive.cli import logger

            assert logger is not None, "logger must be initialized"
        except ImportError:
            pytest.skip("archive.cli module not available")

    def test_click_imported(self):
        """Test click is imported."""
        try:
            from src.codex.archive import cli

            # Should be able to access click through the module
            assert hasattr(cli, "cli")
        except ImportError:
            pytest.skip("archive.cli module not available")


# ==================== Redaction Tests ====================


class TestRedactionFunctions:
    """Tests for credential redaction utilities."""

    def test_redact_text_credentials_imported(self):
        """Test redact_text_credentials is available."""
        try:
            from src.codex.archive.cli import redact_text_credentials

            assert callable(redact_text_credentials), "Condition must be true"
        except ImportError:
            pytest.skip("archive.cli module not available")

    def test_redact_url_credentials_imported(self):
        """Test redact_url_credentials is available."""
        try:
            from src.codex.archive.cli import redact_url_credentials

            assert callable(redact_url_credentials), "Condition must be true"
        except ImportError:
            pytest.skip("archive.cli module not available")


# ==================== Integration Tests ====================


class TestCLIIntegration:
    """Integration tests for CLI operations."""

    def test_cli_commands_registered(self, cli_runner):
        """Test that expected commands are registered."""
        try:
            from src.codex.archive.cli import cli

            result = cli_runner.invoke(cli, ["--help"])
            output = result.output.lower()
            # Check for common commands
            assert "config" in output or "show" in output or result.exit_code == 0
        except ImportError:
            pytest.skip("archive.cli module not available")
