"""Integration tests for multiple archive backends (stubs for PostgreSQL/MariaDB)."""

# ruff: noqa: I001  # import-order handled by isort configuration

from __future__ import annotations

from pathlib import Path

import pytest

from codex.archive.backend import ArchiveConfig as BackendArchiveConfig
from codex.archive.config import ArchiveConfig as RuntimeConfig, BackendConfig


class TestSqliteBackend:
    """Test SQLite backend configuration and validation."""

    def test_sqlite_config_valid(self, tmp_path: Path) -> None:
        """SQLite configuration should be valid."""

        config = BackendConfig(type="sqlite", url=f"sqlite:///{tmp_path}/archive.db")
        assert config.type == "sqlite"
        assert config.url.startswith("sqlite:///")

    def test_sqlite_url_parsing(self) -> None:
        """SQLite URL should be parsed correctly."""

        url = "sqlite:///./.codex/archive.sqlite"
        config = BackendConfig(url=url)
        assert config.url == url


class TestPostgresBackendStub:
    """Stub tests for PostgreSQL backend (requires external service)."""

    def test_postgres_config_valid(self) -> None:
        """PostgreSQL configuration should validate."""

        config = BackendConfig(
            type="postgres",
            url="postgres://user:<password>@localhost:5432/archive",
        )
        assert config.type == "postgres"
        assert "localhost" in config.url

    def test_postgres_url_parsing(self) -> None:
        """PostgreSQL URL should be parsed correctly."""

        url = "postgres://user@localhost/archive"
        config = BackendConfig(url=url)
        assert config.url == url

    @pytest.mark.skip(reason="Requires PostgreSQL service")
    def test_postgres_connection(self) -> None:
        """PostgreSQL connection test (requires service)."""

        pass


class TestMariadbBackendStub:
    """Stub tests for MariaDB backend (requires external service)."""

    def test_mariadb_config_valid(self) -> None:
        """MariaDB configuration should validate."""

        config = BackendConfig(
            type="mariadb",
            url="mysql://user:<password>@localhost:3306/archive",
        )
        assert config.type == "mariadb"
        assert "localhost" in config.url

    def test_mariadb_url_parsing(self) -> None:
        """MariaDB URL should be parsed correctly."""

        url = "mysql://user@localhost/archive"
        config = BackendConfig(url=url)
        assert config.url == url

    @pytest.mark.skip(reason="Requires MariaDB service")
    def test_mariadb_connection(self) -> None:
        """MariaDB connection test (requires service)."""

        pass


class TestMultiBackendConfig:
    """Test multi-backend configuration loading."""

    def test_config_loader_supports_all_backends(self, tmp_path: Path) -> None:
        """Config loader should support all backend types."""

        for backend_type in ["sqlite", "postgres", "mariadb"]:
            config_file = tmp_path / f"archive_{backend_type}.toml"
            config_file.write_text(
                f"""
[backend]
type = "{backend_type}"
url = "placeholder://localhost/archive"
"""
            )
            config = RuntimeConfig.from_file(config_file)
            assert config.backend.type == backend_type

    def test_backend_type_precedence(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Backend type should follow precedence: file > env > default."""

        monkeypatch.setenv("CODEX_ARCHIVE_BACKEND", "mariadb")
        config_file = tmp_path / "archive.toml"
        config_file.write_text(
            """
[backend]
type = "postgres"
"""
        )
        config = RuntimeConfig.load(config_file=str(config_file))
        assert config.backend.type == "postgres"

    def test_backend_config_from_settings(self) -> None:
        """Backend config helper should use runtime settings."""

        runtime = RuntimeConfig(backend=BackendConfig(type="sqlite", url="sqlite:///tmp.db"))
        backend_config = BackendArchiveConfig.from_settings(runtime)
        assert backend_config.backend == "sqlite"
        assert backend_config.url == "sqlite:///tmp.db"
