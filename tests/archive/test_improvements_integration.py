"""Integration tests verifying all improvements work together."""

# ruff: noqa: I001  # import-order handled by isort configuration

from __future__ import annotations

import json
from pathlib import Path

import pytest

from codex.archive.backend import ArchiveConfig as BackendArchiveConfig
from codex.archive.batch import BatchManifest, BatchRestore
from codex.archive.config import ArchiveConfig as RuntimeConfig, BackendConfig
from codex.archive.service import ArchiveService


def _build_service(tmp_path: Path) -> ArchiveService:
    db_path = tmp_path / ".codex" / "archive.sqlite"
    settings = RuntimeConfig(
        backend=BackendConfig(type="sqlite", url=f"sqlite:///{db_path.as_posix()}")
    )
    backend = BackendArchiveConfig(url=settings.backend.url, backend=settings.backend.type)
    return ArchiveService(backend, apply_schema=True, settings=settings)


class TestFullIntegration:
    """Integration tests for all improvements."""

    def test_config_retry_batch_integration(self, tmp_path: Path, monkeypatch) -> None:
        """Config + Retry + Batch should work together."""

        config_file = tmp_path / ".codex" / "archive.toml"
        config_file.parent.mkdir(parents=True)
        config_file.write_text(
            """
[backend]
type = "sqlite"
url = "sqlite:///.codex/archive.sqlite"

[retry]
enabled = true
max_attempts = 2
initial_delay = 0.01

[batch]
max_concurrent = 5
continue_on_error = true

[performance]
enable_metrics = true
"""
        )
        monkeypatch.chdir(tmp_path)
        config = RuntimeConfig.load(config_file=str(config_file))
        backend = BackendArchiveConfig.from_settings(config)
        service = ArchiveService(backend, apply_schema=True, settings=config)

        for i in range(3):
            test_file = tmp_path / f"test{i}.txt"
            test_file.write_text(f"content {i}")
            service.archive_path(
                repo="test",
                path=test_file,
                reason="dead",
                archived_by="test",
                commit_sha="abc123",
            )

        items_list = service.list_items(limit=10)
        batch_items = [
            {
                "tombstone": item.get("tombstone_id"),
                "output": str(tmp_path / f"out{i}.txt"),
            }
            for i, item in enumerate(items_list[:2])
        ]
        manifest = tmp_path / "manifest.json"
        manifest.write_text(json.dumps({"items": batch_items}))

        items = BatchManifest.load_json(manifest)
        batch = BatchRestore(service, max_concurrent=config.batch.max_concurrent)
        results = batch.restore(items, actor="test")
        assert len(results) >= 1
        assert any(result.status == "success" for result in results)

    def test_performance_metrics_in_batch(self, tmp_path: Path, monkeypatch) -> None:
        """Performance metrics should be tracked in batch restores."""

        monkeypatch.chdir(tmp_path)
        service = _build_service(tmp_path)
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        result = service.archive_path(
            repo="test",
            path=test_file,
            reason="dead",
            archived_by="test",
            commit_sha="abc123",
        )
        items = [{"tombstone": result.tombstone_id, "output": str(tmp_path / "out.txt")}]
        manifest = tmp_path / "manifest.json"
        manifest.write_text(json.dumps({"items": items}))
        batch_items = BatchManifest.load_json(manifest)
        batch = BatchRestore(service)
        batch_results = batch.restore(batch_items, actor="test")
        assert batch_results[0].duration_ms is not None
        assert batch_results[0].duration_ms > 0

    def test_config_precedence_full_flow(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Config precedence should be respected in full flow."""

        monkeypatch_env = monkeypatch
        monkeypatch_env.setenv("CODEX_ARCHIVE_BACKEND", "sqlite")
        config1 = RuntimeConfig.load()
        assert config1.backend.type == "sqlite"

        config_file = tmp_path / "archive.toml"
        config_file.write_text("""[backend]\ntype = "sqlite"\n""")
        monkeypatch_env.setenv("CODEX_ARCHIVE_BACKEND", "postgres")
        config2 = RuntimeConfig.load(config_file=str(config_file))
        assert config2.backend.type == "sqlite"
