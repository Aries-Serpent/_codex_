import hashlib
import json
from pathlib import Path

from codex_ml.data.registry import load_line_dataset


def test_line_dataset_manifest_includes_source_and_shuffled_checksums(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset.txt"
    dataset.write_text("alpha\nbeta\ngamma\n", encoding="utf-8")

    manifest_path = tmp_path / "dataset.manifest.json"
    lines = load_line_dataset(str(dataset), seed=17, manifest_path=manifest_path)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["source"] == str(dataset.resolve())

    expected_source_checksum = hashlib.sha256(dataset.read_bytes()).hexdigest()
    assert manifest["source_checksum"] == expected_source_checksum

    expected_shuffled_checksum = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()
    assert manifest["shuffled_checksum"] == expected_shuffled_checksum


def test_line_dataset_manifest_is_stable_across_runs(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset.txt"
    dataset.write_text("one\ntwo\nthree\n", encoding="utf-8")

    manifest_path_a = tmp_path / "dataset_a.manifest.json"
    load_line_dataset(str(dataset), seed=5, manifest_path=manifest_path_a)
    manifest_a = json.loads(manifest_path_a.read_text(encoding="utf-8"))

    manifest_path_b = tmp_path / "dataset_b.manifest.json"
    load_line_dataset(str(dataset), seed=5, manifest_path=manifest_path_b)
    manifest_b = json.loads(manifest_path_b.read_text(encoding="utf-8"))

    assert manifest_a == manifest_b
