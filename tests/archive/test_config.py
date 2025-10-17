"""Tests for archive configuration management."""

from __future__ import annotations

from pathlib import Path

import pytest

from codex.archive.config import ArchiveConfig, BackendConfig, LoggingConfig


class TestConfigFromEnvironment:
    """Test configuration loading from environment variables."""

    def test_from_env_defaults(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("CODEX_ARCHIVE_BACKEND", raising=False)
        monkeypatch.delenv("CODEX_ARCHIVE_URL", raising=False)
        monkeypatch.delenv("CODEX_ARCHIVE_LOG_LEVEL", raising=False)
        config = ArchiveConfig.from_env()
        assert config.backend.type == "sqlite"
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
    """Test configuration load with precedence."""

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
        codex_dir = tmp_path / ".codex"
        codex_dir.mkdir()
        config_file = codex_dir / "archive.toml"
        config_file.write_text(
            """
[backend]
type = "postgres"
"""
        )
        config = ArchiveConfig.load()
        assert config.backend.type == "postgres"


class TestConfigValidation:
    """Test configuration validation."""

    def test_backend_type_valid(self) -> None:
        config = BackendConfig(type="sqlite")
        assert config.type == "sqlite"
        config = BackendConfig(type="postgres")
        assert config.type == "postgres"

    def test_logging_level_valid(self) -> None:
        for level in ["debug", "info", "warn", "error"]:
            config = LoggingConfig(level=level)  # type: ignore[arg-type]
            assert config.level == level

    def test_to_dict(self) -> None:
        config = ArchiveConfig()
        config_dict = config.to_dict()
        assert config_dict["backend"]["type"] == "sqlite"
        assert config_dict["logging"]["level"] == "info"
        assert config_dict["retry"]["enabled"] is False

    def test_to_json(self) -> None:
        config = ArchiveConfig()
        payload = config.to_json()
        assert "backend" in payload
        assert "retry" in payload
