from __future__ import annotations

import hashlib
import json
from pathlib import Path
from random import Random

from codex_ml.data.registry import MANIFEST_SCHEMA, _DatasetRegistry, get_dataset


def _manifest_path(path: Path) -> Path:
    if path.suffix:
        return path.with_suffix(f"{path.suffix}.manifest.json")
    return path.with_name(path.name + ".manifest.json")


def test_lines_loader_seeded_shuffle(tmp_path: Path) -> None:
    data_file = tmp_path / "dataset.txt"
    values = [f"row-{idx}" for idx in range(10)]
    data_file.write_text("\n".join(values), encoding="utf-8")

    expected = list(values)
    Random(7).shuffle(expected)
    loaded_first = get_dataset("lines", path=str(data_file), seed=7)
    loaded_second = get_dataset("lines", path=str(data_file), seed=7)

    assert loaded_first == expected
    assert loaded_first == loaded_second

    alt_loaded = get_dataset("lines", path=str(data_file), seed=11)
    assert sorted(alt_loaded) == sorted(expected)
    assert alt_loaded != expected


def test_lines_loader_manifest_schema(tmp_path: Path) -> None:
    data_file = tmp_path / "records.txt"
    records = [f"sample-{i}" for i in range(5)]
    data_file.write_text("\n".join(records), encoding="utf-8")

    loaded = get_dataset("lines", path=str(data_file), seed=3, write_manifest=True)
    manifest_file = _manifest_path(data_file)
    assert manifest_file.exists()

    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert manifest["schema"] == MANIFEST_SCHEMA
    assert Path(manifest["source"]) == data_file.resolve()
    assert manifest["num_records"] == len(loaded)
    assert manifest["seed"] == 3
    assert manifest["shuffle"] is True

    source_checksum = hashlib.sha256(data_file.read_bytes()).hexdigest()
    shuffled_checksum = hashlib.sha256("\n".join(loaded).encode("utf-8")).hexdigest()
    assert manifest["source_checksum"] == source_checksum
    assert manifest["shuffled_checksum"] == shuffled_checksum
    assert manifest["checksum"] == shuffled_checksum


def test_lines_loader_checksums_stable_across_runs(tmp_path: Path) -> None:
    data_file = tmp_path / "records.txt"
    records = [f"stable-{i}" for i in range(6)]
    data_file.write_text("\n".join(records), encoding="utf-8")

    manifest_path = tmp_path / "manifest.json"

    first_loaded = get_dataset(
        "lines",
        path=str(data_file),
        seed=17,
        write_manifest=True,
        manifest_path=manifest_path,
    )
    first_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    get_dataset(
        "lines",
        path=str(data_file),
        seed=17,
        write_manifest=True,
        manifest_path=manifest_path,
    )
    second_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    expected_source_checksum = hashlib.sha256(data_file.read_bytes()).hexdigest()
    expected_shuffled_checksum = hashlib.sha256("\n".join(first_loaded).encode("utf-8")).hexdigest()

    assert first_manifest["source_checksum"] == expected_source_checksum
    assert second_manifest["source_checksum"] == expected_source_checksum

    assert first_manifest["shuffled_checksum"] == expected_shuffled_checksum
    assert second_manifest["shuffled_checksum"] == expected_shuffled_checksum

    assert first_manifest["checksum"] == expected_shuffled_checksum
    assert second_manifest["checksum"] == expected_shuffled_checksum


def test_lines_loader_does_not_emit_manifest_by_default(tmp_path: Path) -> None:
    data_file = tmp_path / "records.txt"
    data_file.write_text("example", encoding="utf-8")

    loaded = get_dataset("lines", path=str(data_file), seed=2)
    assert loaded == ["example"]

    assert not _manifest_path(data_file).exists()


def test_dataset_registry_discovers_entry_points(monkeypatch) -> None:
    registry = _DatasetRegistry()

    class DummyEntryPoint:
        def __init__(self, name: str, value):
            self.name = name
            self._value = value

        def load(self):
            return self._value

    loaded: list[str] = []

    def plugin_loader() -> list[str]:
        loaded.append("plugin")
        return loaded

    def fake_entry_points(*, group: str):
        assert group == registry._ENTRY_POINT_GROUP
        return (DummyEntryPoint("plugin-dataset", plugin_loader),)

    monkeypatch.setattr(
        "codex_ml.data.registry.metadata.entry_points",
        fake_entry_points,
    )

    loader = registry.get("plugin-dataset")
    assert callable(loader)
    assert registry.list() == ["plugin-dataset"]
    assert loader() == ["plugin"]
