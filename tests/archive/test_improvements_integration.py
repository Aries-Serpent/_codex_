"""Integration tests verifying new archive improvements."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from codex.archive.batch import BatchManifest, BatchRestore
from codex.archive.config import ArchiveConfig as SettingsConfig, BackendConfig
from codex.archive.service import ArchiveService


class TestFullIntegration:
    """Integration scenarios covering config, retry, batch, and metrics."""

    def test_config_retry_batch_integration(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        config_dir = tmp_path / ".codex"
        config_dir.mkdir()
        config_file = config_dir / "archive.toml"
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
        settings = SettingsConfig.load()
        assert settings.retry.enabled is True
        assert settings.batch.max_concurrent == 5
        assert settings.performance.enable_metrics is True

        service = ArchiveService(apply_schema=True, settings=settings)
        for idx in range(2):
            test_file = tmp_path / f"file{idx}.txt"
            test_file.write_text(f"content-{idx}")
            service.archive_path(
                repo="repo",
                path=test_file,
                reason="dead",
                archived_by="tester",
                commit_sha="abc123",
            )

        manifest_path = tmp_path / "manifest.json"
        items = [
            {"tombstone": row["tombstone_id"], "output": str(tmp_path / f"out{idx}.txt")}
            for idx, row in enumerate(service.list_items(limit=2))
        ]
        manifest_path.write_text(json.dumps({"items": items}))
        batch_items = BatchManifest.load_json(manifest_path)
        batch = BatchRestore(
            service,
            max_concurrent=settings.batch.max_concurrent,
            continue_on_error=True,
        )
        results = batch.restore(batch_items, actor="tester")
        assert len(results) == len(items)
        assert all(result.status in {"success", "failed"} for result in results)

    def test_performance_metrics_present(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        settings = SettingsConfig(backend=BackendConfig(type="sqlite", url="sqlite:///.codex/archive.sqlite"))
        service = ArchiveService(apply_schema=True, settings=settings)
        test_file = tmp_path / "sample.txt"
        test_file.write_text("content")
        result = service.archive_path(
            repo="repo",
            path=test_file,
            reason="dead",
            archived_by="tester",
            commit_sha="abc123",
        )
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "items": [
                        {
                            "tombstone": result.tombstone_id,
                            "output": str(tmp_path / "out.txt"),
                        }
                    ]
                }
            )
        )
        batch_items = BatchManifest.load_json(manifest_path)
        batch = BatchRestore(service, continue_on_error=True)
        results = batch.restore(batch_items, actor="tester")
        assert results[0].duration_ms > 0

    def test_config_precedence_with_env(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CODEX_ARCHIVE_BACKEND", "mariadb")
        monkeypatch.chdir(tmp_path)
        config_file = tmp_path / "archive.toml"
        config_file.write_text(
            """
[backend]
type = "postgres"
"""
        )
        config = SettingsConfig.load(config_file=str(config_file))
        assert config.backend.type == "postgres"
