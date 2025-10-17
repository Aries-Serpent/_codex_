"""Integration tests for multiple archive backends (configuration only)."""

from __future__ import annotations

from pathlib import Path

import pytest

from codex.archive.backend import ArchiveConfig as BackendRuntimeConfig
from codex.archive.config import ArchiveConfig, BackendConfig


class TestSqliteBackend:
    def test_sqlite_config_valid(self, tmp_path: Path) -> None:
        config = BackendConfig(type="sqlite", url=f"sqlite:///{tmp_path}/archive.db")
        assert config.type == "sqlite"
        assert config.url.startswith("sqlite:///")

    def test_sqlite_url_parsing(self) -> None:
        url = "sqlite:///./.codex/archive.sqlite"
        config = BackendConfig(url=url)
        assert config.url == url


class TestPostgresBackendStub:
    def test_postgres_config_valid(self) -> None:
        config = BackendConfig(
            type="postgres",
            url="postgres://user@localhost:5432/archive",
        )
        assert config.type == "postgres"
        assert "localhost" in config.url

    def test_postgres_url_parsing(self) -> None:
        url = "postgres://user@localhost/archive"
        config = BackendConfig(url=url)
        assert config.url == url

    @pytest.mark.skip(reason="Requires PostgreSQL service")
    def test_postgres_connection(self) -> None:
        pass


class TestMariadbBackendStub:
    def test_mariadb_config_valid(self) -> None:
        config = BackendConfig(
            type="mariadb",
            url="mysql://user@localhost:3306/archive",
        )
        assert config.type == "mariadb"
        assert "localhost" in config.url

    def test_mariadb_url_parsing(self) -> None:
        url = "mysql://user@localhost/archive"
        config = BackendConfig(url=url)
        assert config.url == url

    @pytest.mark.skip(reason="Requires MariaDB service")
    def test_mariadb_connection(self) -> None:
        pass


class TestMultiBackendConfig:
    def test_config_loader_supports_all_backends(self, tmp_path: Path) -> None:
        for backend_type in ["sqlite", "postgres", "mariadb"]:
            config_file = tmp_path / f"archive_{backend_type}.toml"
            config_file.write_text(
                f"""
[backend]
type = "{backend_type}"
url = "placeholder://localhost/archive"
"""
            )
            config = ArchiveConfig.from_file(config_file)
            assert config.backend.type == backend_type

    def test_backend_type_precedence(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CODEX_ARCHIVE_BACKEND", "mariadb")
        config_file = tmp_path / "archive.toml"
        config_file.write_text(
            """
[backend]
type = "postgres"
"""
        )
        config = ArchiveConfig.load(config_file=str(config_file))
        assert config.backend.type == "postgres"

    def test_runtime_config_bridge(self) -> None:
        settings = ArchiveConfig()
        runtime = BackendRuntimeConfig.from_settings(settings)
        assert runtime.backend == settings.backend.type
        assert runtime.url == settings.backend.url
