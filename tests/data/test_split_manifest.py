import json
from pathlib import Path

from codex_ml.data.split_utils import split_dataset


def test_split_dataset_writes_checksum_manifest(tmp_path: Path) -> None:
    source = tmp_path / "dataset.jsonl"
    rows = [{"text": f"row-{idx}"} for idx in range(30)]
    source.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
    result = split_dataset(source, seed=0)
    manifest = source.parent / "split_checksums.json"
    assert manifest.exists()
    checksums = json.loads(manifest.read_text(encoding="utf-8"))
    names = set(checksums.keys())
    assert result.train.name in names
    assert result.val.name in names
    assert result.test.name in names
