"""Tests for batch restore operations."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from codex.archive.batch import BatchItem, BatchManifest, BatchRestore
from codex.archive.config import ArchiveConfig as SettingsConfig, BackendConfig
from codex.archive.service import ArchiveService


def _service_for_tmp(tmp_path: Path) -> ArchiveService:
    db_path = tmp_path / ".codex" / "archive.sqlite"
    settings = SettingsConfig(backend=BackendConfig(type="sqlite", url=f"sqlite:///{db_path}"))
    return ArchiveService(apply_schema=True, settings=settings)


class TestBatchManifestJson:
    """Test JSON manifest loading."""

    def test_load_valid_manifest(self, tmp_path: Path) -> None:
        manifest_file = tmp_path / "manifest.json"
        manifest_file.write_text(
            json.dumps(
                {
                    "items": [
                        {"tombstone": "uuid-1", "output": "/tmp/file1.txt"},
                        {"tombstone": "uuid-2", "output": "/tmp/file2.txt"},
                    ]
                }
            )
        )
        items = BatchManifest.load_json(manifest_file)
        assert len(items) == 2
        assert items[0].tombstone == "uuid-1"
        assert items[1].output == "/tmp/file2.txt"

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
    """Test batch restore orchestration."""

    def test_batch_restore_all_success(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        service = _service_for_tmp(tmp_path)
        test_file = tmp_path / "example.txt"
        test_file.write_text("payload")
        archive_result = service.archive_path(
            repo="test",
            path=test_file,
            reason="dead",
            archived_by="tester",
            commit_sha="abc123",
        )
        items = [BatchItem(tombstone=archive_result.tombstone_id, output=str(tmp_path / "out.txt"))]
        batch = BatchRestore(service, continue_on_error=False)
        results = batch.restore(items, actor="tester")
        assert len(results) == 1
        assert results[0].status == "success"
        assert Path(results[0].item.output).exists()

    def test_batch_restore_with_errors(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        service = _service_for_tmp(tmp_path)
        items = [BatchItem(tombstone="missing", output=str(tmp_path / "out.txt"))]
        batch = BatchRestore(service, continue_on_error=True)
        results = batch.restore(items, actor="tester")
        assert len(results) == 1
        assert results[0].status == "failed"
        assert results[0].error is not None

    def test_batch_restore_save_results(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        service = _service_for_tmp(tmp_path)
        items = [BatchItem(tombstone="uuid-1", output=str(tmp_path / "out1.txt"))]
        batch = BatchRestore(service, continue_on_error=True)
        batch.restore(items, actor="tester")
        results_file = tmp_path / "results.json"
        batch.save_results(results_file)
        data = json.loads(results_file.read_text())
        assert data["summary"]["total"] == 1
        assert "items" in data

    def test_batch_restore_progress_callback(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        service = _service_for_tmp(tmp_path)
        items = [BatchItem(tombstone=f"uuid-{idx}", output=str(tmp_path / f"out{idx}.txt")) for idx in range(3)]
        progress_calls: list[tuple[int, int]] = []

        def progress(current: int, total: int) -> None:
            progress_calls.append((current, total))

        batch = BatchRestore(service, continue_on_error=True)
        batch.restore(items, actor="tester", progress_callback=progress)
        assert len(progress_calls) == 3
        assert progress_calls[-1] == (3, 3)
