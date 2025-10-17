"""Tests for archive configuration management."""
from __future__ import annotations

from pathlib import Path

import pytest

from codex.archive.config import (
    ArchiveConfig,
    BackendConfig,
    BatchConfig,
    LoggingConfig,
    PerformanceConfig,
    RetryConfig,
)


class TestConfigFromEnvironment:
    """Test configuration loading from environment variables."""

    def test_from_env_defaults(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("CODEX_ARCHIVE_BACKEND", raising=False)
        monkeypatch.delenv("CODEX_ARCHIVE_URL", raising=False)
        config = ArchiveConfig.from_env()
        assert config.backend.type == "sqlite"
        assert config.backend.url == "sqlite:///./.codex/archive.sqlite"
        assert config.logging.level == "info"
        assert config.retry.enabled is False

    def test_from_env_custom_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CODEX_ARCHIVE_BACKEND", "postgres")
        monkeypatch.setenv("CODEX_ARCHIVE_URL", "postgres://localhost/archive")
        monkeypatch.setenv("CODEX_ARCHIVE_LOG_LEVEL", "debug")
        monkeypatch.setenv("CODEX_ARCHIVE_RETRY_ENABLED", "true")
        config = ArchiveConfig.from_env()
        assert config.backend.type == "postgres"
        assert config.backend.url == "postgres://localhost/archive"
        assert config.logging.level == "debug"
        assert config.retry.enabled is True

    def test_from_env_retry_settings(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CODEX_ARCHIVE_RETRY_ENABLED", "true")
        monkeypatch.setenv("CODEX_ARCHIVE_RETRY_MAX", "5")
        monkeypatch.setenv("CODEX_ARCHIVE_RETRY_INITIAL", "2.0")
        monkeypatch.setenv("CODEX_ARCHIVE_RETRY_MAX_DELAY", "64.0")
        config = ArchiveConfig.from_env()
        assert config.retry.max_attempts == 5
        assert config.retry.initial_delay == 2.0
        assert config.retry.max_delay == 64.0


class TestConfigFromFile:
    """Test configuration loading from TOML file."""

    def test_from_file_valid(self, tmp_path: Path) -> None:
        config_file = tmp_path / "archive.toml"
        config_file.write_text(
            """
[backend]
type = "postgres"
url = "postgres://localhost/archive"
[logging]
level = "debug"
format = "json"
[retry]
enabled = true
max_attempts = 5
"""
        )
        config = ArchiveConfig.from_file(config_file)
        assert config.backend.type == "postgres"
        assert config.logging.level == "debug"
        assert config.retry.enabled is True
        assert config.retry.max_attempts == 5

    def test_from_file_not_found(self, tmp_path: Path) -> None:
        config_file = tmp_path / "missing.toml"
        with pytest.raises(FileNotFoundError):
            ArchiveConfig.from_file(config_file)

    def test_from_file_partial_config(self, tmp_path: Path) -> None:
        config_file = tmp_path / "archive.toml"
        config_file.write_text(
            """
[backend]
type = "sqlite"
"""
        )
        config = ArchiveConfig.from_file(config_file)
        assert config.backend.type == "sqlite"
        assert config.logging.level == "info"
        assert config.retry.enabled is False


class TestConfigLoad:
    """Test configuration load precedence."""

    def test_load_file_precedence(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CODEX_ARCHIVE_BACKEND", "sqlite")
        config_file = tmp_path / "archive.toml"
        config_file.write_text(
            """
[backend]
type = "postgres"
"""
        )
        config = ArchiveConfig.load(config_file=str(config_file))
        assert config.backend.type == "postgres"

    def test_load_env_when_no_file(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CODEX_ARCHIVE_BACKEND", "mariadb")
        config = ArchiveConfig.load()
        assert config.backend.type == "mariadb"

    def test_load_default_location(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        config_dir = tmp_path / ".codex"
        config_dir.mkdir()
        config_file = config_dir / "archive.toml"
        config_file.write_text(
            """
[backend]
type = "postgres"
"""
        )
        config = ArchiveConfig.load()
        assert config.backend.type == "postgres"


class TestConfigValidation:
    """Test configuration dataclasses."""

    def test_backend_type_valid(self) -> None:
        assert BackendConfig(type="sqlite").type == "sqlite"
        assert BackendConfig(type="postgres").type == "postgres"

    def test_logging_level_valid(self) -> None:
        for level in ("debug", "info", "warn", "error"):
            assert LoggingConfig(level=level).level == level

    def test_to_dict(self) -> None:
        config = ArchiveConfig()
        config_dict = config.to_dict()
        assert config_dict["backend"]["type"] == "sqlite"
        assert config_dict["logging"]["level"] == "info"
        assert config_dict["retry"]["enabled"] is False

    def test_custom_section_initialisation(self) -> None:
        config = ArchiveConfig(
            backend=BackendConfig(type="postgres", url="postgres://example/archive"),
            logging=LoggingConfig(level="warn", format="text"),
            retry=RetryConfig(enabled=True, max_attempts=5),
            batch=BatchConfig(max_concurrent=7, timeout_per_item=120, continue_on_error=True),
            performance=PerformanceConfig(enable_metrics=False, track_decompression=False),
        )
        assert config.backend.url == "postgres://example/archive"
        assert config.logging.format == "text"
        assert config.retry.max_attempts == 5
        assert config.batch.continue_on_error is True
        assert config.performance.enable_metrics is False
