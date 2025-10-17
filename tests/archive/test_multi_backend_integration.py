from __future__ import annotations

import pytest

from codex.archive import config as archive_config


def test_backend_config_to_archive_config() -> None:
    backend = archive_config.BackendConfig(backend="postgres", url="postgresql://user@localhost/db")
    archive_backend = backend.to_archive_config()
    assert archive_backend.backend == "postgres"
    assert archive_backend.url.startswith("postgresql://")


def test_backend_config_rejects_empty_url() -> None:
    with pytest.raises(ValueError):
        archive_config.BackendConfig(backend="sqlite", url="")


def test_archive_config_loads_postgres_env() -> None:
    env = {
        "CODEX_ARCHIVE_URL": "postgresql://user@localhost/db",
        "CODEX_ARCHIVE_BACKEND": "postgres",
    }
    cfg = archive_config.ArchiveAppConfig.load(env=env)
    assert cfg.backend.backend == "postgres"


def test_archive_config_loads_mariadb_env() -> None:
    env = {"CODEX_ARCHIVE_BACKEND": "mariadb", "CODEX_ARCHIVE_URL": "mariadb://example/db"}
    cfg = archive_config.ArchiveAppConfig.load(env=env)
    assert cfg.backend.backend == "mariadb"
    assert cfg.backend.url == "mariadb://example/db"


def test_archive_config_batch_results_path_serialisation(tmp_path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
        [batch]
        results_path = "results.json"
        """
    )
    cfg = archive_config.ArchiveAppConfig.load(config_file=config_path, env={})
    serialized = cfg.to_dict()
    assert serialized["batch"]["results_path"].endswith("results.json")
