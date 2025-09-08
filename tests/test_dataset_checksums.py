import json

from codex_ml.utils.repro import record_dataset_checksums


def test_record_dataset_checksums(tmp_path):
    f1 = tmp_path / "a.txt"
    f1.write_text("hello")
    f2 = tmp_path / "b.txt"
    f2.write_text("world")
    out = tmp_path / "checksums.json"
    checksums = record_dataset_checksums([f1, f2], out)
    assert out.exists()
    data = json.loads(out.read_text())
    assert data == checksums
    assert set(data.keys()) == {"a.txt", "b.txt"}
