"""Integration tests verifying config, retry, batch, and perf features."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from codex.archive import config as archive_config, retry as retry_module
from codex.archive.batch import BatchManifest, BatchRestore
from codex.archive.service import ArchiveService

SettingsArchiveConfig = archive_config.ArchiveConfig
BackendConfig = archive_config.BackendConfig
RetryPolicyConfig = retry_module.RetryConfig
retry_with_backoff = retry_module.retry_with_backoff


class TestFullIntegration:
    def test_config_retry_batch_integration(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        config_file = tmp_path / ".codex" / "archive.toml"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        config_file.write_text(
            """
[backend]
type = "sqlite"
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
        settings = SettingsArchiveConfig.load(config_file=str(config_file))
        service = ArchiveService(settings, apply_schema=True)

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
        manifest = tmp_path / "manifest.json"
        manifest.write_text(
            json.dumps(
                {
                    "items": [
                        {
                            "tombstone": item["tombstone_id"],
                            "output": str(tmp_path / f"out{idx}.txt"),
                        }
                        for idx, item in enumerate(items_list[:2])
                    ]
                }
            )
        )
        batch_items = BatchManifest.load_json(manifest)
        batch = BatchRestore(service, max_concurrent=settings.batch.max_concurrent)
        results = batch.restore(batch_items, actor="test")
        assert len(results) >= 1
        assert any(r.status == "success" for r in results)

    def test_performance_metrics_in_batch(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db_path = tmp_path / ".codex" / "archive.sqlite"
        settings = SettingsArchiveConfig(
            backend=BackendConfig(type="sqlite", url=f"sqlite:///{db_path.as_posix()}")
        )
        monkeypatch.chdir(tmp_path)
        service = ArchiveService(settings, apply_schema=True)
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        result = service.archive_path(
            repo="test",
            path=test_file,
            reason="dead",
            archived_by="test",
            commit_sha="abc123",
        )
        manifest = tmp_path / "manifest.json"
        manifest.write_text(
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
        batch_items = BatchManifest.load_json(manifest)
        batch = BatchRestore(service)
        batch_results = batch.restore(batch_items, actor="test")
        assert batch_results[0].duration_ms is not None
        assert batch_results[0].duration_ms >= 0

    def test_config_precedence_full_flow(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("CODEX_ARCHIVE_BACKEND", "sqlite")
        config1 = SettingsArchiveConfig.load()
        assert config1.backend.type == "sqlite"

        config_file = tmp_path / "archive.toml"
        config_file.write_text('[backend]\ntype = "postgres"')
        monkeypatch.setenv("CODEX_ARCHIVE_BACKEND", "mariadb")
        config2 = SettingsArchiveConfig.load(config_file=str(config_file))
        assert config2.backend.type == "postgres"

    def test_retry_decorator_with_service_policy(self) -> None:
        policy = RetryPolicyConfig(max_attempts=2, initial_delay=0.001, jitter=False)

        calls: list[int] = []

        @retry_with_backoff(policy, transient_errors=(RuntimeError,))
        def flaky() -> str:
            calls.append(1)
            if len(calls) < 2:
                raise RuntimeError("boom")
            return "ok"

        assert flaky() == "ok"
        assert len(calls) == 2
