"""
Test Dataset Checksums

Test module for dataset checksums.
"""

import json

from codex_ml.utils.repro import record_dataset_checksums


def test_record_dataset_checksums(tmp_path):
    f1 = tmp_path / "a.txt"
    f1.write_text("hello")
    f2 = tmp_path / "b.txt"
    f2.write_text("world")
    out = tmp_path / "checksums.json"
    checksums = record_dataset_checksums([f1, f2], out, dataset_name="sample")
    assert out.exists(), "Condition must be true"
    data = json.loads(out.read_text())
    assert data == checksums, "Data must not be empty"
    assert set(data.keys()) == {"a.txt", "b.txt"}
    sidecar = json.loads(out.with_suffix(out.suffix + ".version.json").read_text())
    assert sidecar["files"] == checksums, "Condition must be true"
    assert sidecar["name"] == "sample", "Condition must be true"
    assert len(sidecar["version"]) == 64, "Collection must not be empty"
