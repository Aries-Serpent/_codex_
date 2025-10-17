"""Tests for batch restore operations."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from codex.archive import config as archive_config
from codex.archive.batch import BatchItem, BatchManifest, BatchRestore
from codex.archive.service import ArchiveService

SettingsArchiveConfig = archive_config.ArchiveConfig
BackendConfig = archive_config.BackendConfig


class TestBatchManifestJson:
    def test_load_valid_manifest(self, tmp_path: Path) -> None:
        manifest_file = tmp_path / "manifest.json"
        manifest_file.write_text(
            json.dumps(
                {
                    "items": [
                        {
                            "tombstone": "uuid-1",
                            "output": (tmp_path / "file1.txt").as_posix(),
                        },
                        {
                            "tombstone": "uuid-2",
                            "output": (tmp_path / "file2.txt").as_posix(),
                        },
                    ]
                }
            )
        )
        items = BatchManifest.load_json(manifest_file)
        assert len(items) == 2
        assert items[0].tombstone == "uuid-1"
        assert items[1].output == (tmp_path / "file2.txt").as_posix()

    def test_load_missing_manifest(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            BatchManifest.load_json(tmp_path / "missing.json")

    def test_load_invalid_manifest_format(self, tmp_path: Path) -> None:
        manifest_file = tmp_path / "manifest.json"
        manifest_file.write_text(json.dumps({"wrong_key": []}))
        with pytest.raises(ValueError):
            BatchManifest.load_json(manifest_file)

    def test_load_manifest_missing_fields(self, tmp_path: Path) -> None:
        manifest_file = tmp_path / "manifest.json"
        manifest_file.write_text(json.dumps({"items": [{"tombstone": "uuid-1"}]}))
        with pytest.raises(ValueError):
            BatchManifest.load_json(manifest_file)


class TestBatchRestore:
    def _service(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> ArchiveService:
        db_path = tmp_path / ".codex" / "archive.sqlite"
        monkeypatch.setenv("CODEX_ARCHIVE_URL", f"sqlite:///{db_path.as_posix()}")
        monkeypatch.chdir(tmp_path)
        settings = SettingsArchiveConfig(
            backend=BackendConfig(type="sqlite", url=f"sqlite:///{db_path.as_posix()}")
        )
        return ArchiveService(settings, apply_schema=True)

    def test_batch_restore_all_success(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        service = self._service(tmp_path, monkeypatch)
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content", encoding="utf-8")
        archive_result = service.archive_path(
            repo="test",
            path=test_file,
            reason="dead",
            archived_by="test",
            commit_sha="abc123",
        )
        items = [
            BatchItem(
                tombstone=archive_result.tombstone_id,
                output=str(tmp_path / "out1.txt"),
            )
        ]
        batch = BatchRestore(service, continue_on_error=False)
        results = batch.restore(items, actor="test-user")
        assert len(results) == 1
        assert results[0].status == "success"
        assert Path(results[0].item.output).exists()

    def test_batch_restore_with_errors(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        service = self._service(tmp_path, monkeypatch)
        items = [BatchItem(tombstone="invalid-uuid", output=str(tmp_path / "out.txt"))]
        batch = BatchRestore(service, continue_on_error=True)
        results = batch.restore(items, actor="test-user")
        assert len(results) == 1
        assert results[0].status == "failed"
        assert results[0].error is not None

    def test_batch_restore_save_results(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        service = self._service(tmp_path, monkeypatch)
        items = [
            BatchItem(tombstone="uuid-1", output=str(tmp_path / "out1.txt")),
            BatchItem(tombstone="uuid-2", output=str(tmp_path / "out2.txt")),
        ]
        batch = BatchRestore(service, continue_on_error=True)
        batch.restore(items, actor="test-user")
        results_file = tmp_path / "results.json"
        batch.save_results(results_file)
        assert results_file.exists()
        results_data = json.loads(results_file.read_text())
        assert results_data["summary"]["total"] == 2
        assert results_data["summary"]["failed"] == 2

    def test_batch_restore_progress_callback(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        service = self._service(tmp_path, monkeypatch)
        items = [
            BatchItem(tombstone=f"uuid-{i}", output=str(tmp_path / f"out{i}.txt")) for i in range(3)
        ]
        progress_calls: list[tuple[int, int]] = []

        def progress_callback(current: int, total: int) -> None:
            progress_calls.append((current, total))

        batch = BatchRestore(service, continue_on_error=True)
        batch.restore(items, actor="test", progress_callback=progress_callback)
        assert len(progress_calls) == 3
        assert progress_calls[-1] == (3, 3)
