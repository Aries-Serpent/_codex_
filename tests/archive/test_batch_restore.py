from __future__ import annotations

import json
from pathlib import Path

import pytest

from codex.archive import batch
from codex.archive.config import BatchConfig, PerformanceConfig, RetrySettings


class DummyService:
    def __init__(self, failures: set[str] | None = None) -> None:
        self.calls: list[tuple[str, Path, str]] = []
        self.failures = failures or set()

    def restore_to_path(self, tombstone: str, *, output_path: Path, actor: str) -> Path:
        self.calls.append((tombstone, output_path, actor))
        if tombstone in self.failures:
            raise RuntimeError(f"failed: {tombstone}")
        output_path.write_text(f"restored:{tombstone}")
        return output_path


def test_manifest_json_and_csv(tmp_path: Path) -> None:
    manifest_dir = tmp_path / "manifests"
    manifest_dir.mkdir()
    json_manifest = manifest_dir / "batch.json"
    json_manifest.write_text(
        json.dumps(
            {
                "items": [
                    {"tombstone": "a", "output": "fileA.txt"},
                    {"tombstone": "b", "output": "fileB.txt", "actor": "other"},
                ]
            }
        )
    )
    csv_manifest = manifest_dir / "batch.csv"
    csv_manifest.write_text("tombstone,output\na,fileA.txt\n")

    json_items = batch.BatchManifest.from_path(json_manifest, default_actor="actor").items
    csv_items = batch.BatchManifest.from_path(csv_manifest, default_actor="actor").items

    assert len(json_items) == 2
    assert json_items[0].actor == "actor"
    assert csv_items[0].output.name == "fileA.txt"


def test_batch_restore_results(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    manifest_path = tmp_path / "batch.json"
    manifest_path.write_text(
        json.dumps(
            [
                {"tombstone": "ok", "output": "ok.bin"},
                {"tombstone": "fail", "output": "fail.bin"},
            ]
        )
    )

    service = DummyService(failures={"fail"})
    monkeypatch.setattr("codex.archive.retry.time.sleep", lambda _: None)
    runner = batch.BatchRestore(
        service,
        retry_config=RetrySettings(
            max_attempts=2, jitter=0.0, initial_delay=0.0, max_delay=0.0
        ).to_retry_config(),
        batch_config=BatchConfig(progress_interval=1),
        performance_config=PerformanceConfig(enabled=True),
    )

    manifest = batch.BatchManifest.from_path(manifest_path, default_actor="actor")
    result = runner.restore(manifest)

    assert result.total == 2
    assert result.succeeded == 1
    assert result.failed == 1
    assert any(entry["status"] == "FAILED" for entry in result.results)


def test_save_results_persists_summary(tmp_path: Path) -> None:
    service = DummyService()
    runner = batch.BatchRestore(service)
    manifest_path = tmp_path / "batch.json"
    manifest_path.write_text(json.dumps([{"tombstone": "a", "output": "out.bin"}]))
    manifest = batch.BatchManifest.from_path(manifest_path, default_actor="actor")
    result = runner.restore(manifest)

    output_path = tmp_path / "results.json"
    runner.save_results(output_path, result)

    content = json.loads(output_path.read_text())
    assert content["total"] == 1
    assert content["results"][0]["tombstone"] == "a"
