"""Integration tests for multi-backend configuration support."""
from __future__ import annotations

from pathlib import Path

import pytest

from codex.archive.backend import ArchiveBackendConfig, infer_backend
from codex.archive.config import ArchiveConfig as SettingsConfig, BackendConfig


class TestInferBackend:
    """Test backend inference utility."""

    @pytest.mark.parametrize(
        ("url", "expected"),
        [
            ("sqlite:///./.codex/archive.sqlite", "sqlite"),
            ("postgres://user@localhost/db", "postgres"),
            ("mysql://user@localhost/db", "mariadb"),
        ],
    )
    def test_infer_backend(self, url: str, expected: str) -> None:
        assert infer_backend(url) == expected

    def test_infer_backend_unknown(self) -> None:
        with pytest.raises(ValueError):
            infer_backend("unknown://example")


class TestBackendConfig:
    """Test backend configuration dataclass."""

    def test_sqlite_config_valid(self, tmp_path: Path) -> None:
        url = f"sqlite:///{tmp_path}/archive.db"
        config = BackendConfig(type="sqlite", url=url)
        assert config.type == "sqlite"
        assert config.url == url

    def test_postgres_config_valid(self) -> None:
        config = BackendConfig(type="postgres", url="postgres://user:pass@localhost:5432/archive")
        assert config.type == "postgres"
        assert "postgres://" in config.url

    def test_mariadb_config_valid(self) -> None:
        config = BackendConfig(type="mariadb", url="mysql://user:pass@localhost:3306/archive")
        assert config.type == "mariadb"
        assert "mysql://" in config.url


class TestSettingsIntegration:
    """Test integration between settings and backend config."""

    def test_config_loader_supports_all_backends(self, tmp_path: Path) -> None:
        for backend_type in ("sqlite", "postgres", "mariadb"):
            config_file = tmp_path / f"archive_{backend_type}.toml"
            config_file.write_text(
                f"""
[backend]
type = "{backend_type}"
url = "placeholder://localhost/archive"
"""
            )
            config = SettingsConfig.from_file(config_file)
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
        config = SettingsConfig.load(config_file=str(config_file))
        assert config.backend.type == "postgres"

    def test_backend_config_from_settings(self) -> None:
        settings = SettingsConfig(backend=BackendConfig(type="postgres", url="postgres://localhost/db"))
        backend_config = ArchiveBackendConfig.from_settings(settings)
        assert backend_config.backend == "postgres"
        assert backend_config.url == "postgres://localhost/db"
