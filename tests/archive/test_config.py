from __future__ import annotations

from pathlib import Path

import pytest

from codex.archive import config as archive_config


def test_archive_app_config_defaults(tmp_path: Path) -> None:
    cfg = archive_config.ArchiveAppConfig.load(env={})
    assert cfg.backend.backend == "sqlite"
    assert cfg.backend.url.endswith(".codex/archive.sqlite")
    assert cfg.logging.level == "info"
    assert cfg.retry.max_attempts == 5
    assert cfg.batch.concurrent == 4
    assert cfg.performance.enabled is True


def test_archive_app_config_env_overrides() -> None:
    env = {
        "CODEX_ARCHIVE_BACKEND": "postgres",
        "CODEX_ARCHIVE_URL": "postgresql://user:***@localhost/archive",
        "CODEX_ARCHIVE_LOG_LEVEL": "debug",
        "CODEX_ARCHIVE_RETRY_ATTEMPTS": "2",
        "CODEX_ARCHIVE_BATCH_CONCURRENT": "8",
        "CODEX_ARCHIVE_PERF_ENABLED": "0",
    }
    cfg = archive_config.ArchiveAppConfig.load(env=env)
    assert cfg.backend.backend == "postgres"
    assert cfg.backend.url.startswith("postgresql://")
    assert cfg.logging.level == "debug"
    assert cfg.retry.max_attempts == 2
    assert cfg.batch.concurrent == 8
    assert cfg.performance.enabled is False


def test_archive_app_config_file_precedence(tmp_path: Path) -> None:
    config_path = tmp_path / "archive.toml"
    config_path.write_text(
        """
        [backend]
        backend = "mariadb"
        url = "mariadb://example/db"

        [retry]
        max_attempts = 9
        initial_delay = 0.5
        """
    )

    cfg = archive_config.ArchiveAppConfig.load(
        config_file=config_path,
        env={"CODEX_ARCHIVE_BACKEND": "postgres"},
    )

    assert cfg.backend.backend == "postgres"
    assert cfg.backend.url == "mariadb://example/db"
    assert cfg.retry.max_attempts == 9
    assert cfg.retry.initial_delay == pytest.approx(0.5)


def test_backend_config_rejects_unknown_backend() -> None:
    with pytest.raises(ValueError):
        archive_config.BackendConfig(backend="dynamodb", url="dynamo://example")


def test_retry_settings_to_retry_config_roundtrip() -> None:
    settings = archive_config.RetrySettings(enabled=True, max_attempts=3, seed=123)
    retry_cfg = settings.to_retry_config()
    assert retry_cfg.max_attempts == 3
    assert retry_cfg.enabled is True
    assert retry_cfg.seed == 123
