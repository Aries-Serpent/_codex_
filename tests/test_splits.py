import hashlib
import json
from pathlib import Path

from codex_ml.data.split import (
    DEFAULT_CHECKSUMS_NAME,
    DEFAULT_MANIFEST_NAME,
    train_val_test_split,
)


def test_train_val_test_split_manifest(tmp_path: Path) -> None:
    data = [f"sample-{i}" for i in range(20)]
    manifest_path = tmp_path / "custom_manifest.json"

    train, val, test = train_val_test_split(
        data,
        val_frac=0.2,
        test_frac=0.2,
        seed=99,
        dataset_id="toy-dataset",
        manifest_path=manifest_path,
        artifact_dir=tmp_path,
    )

    # Sizes add up and splits contain unique entries.
    assert len(train) + len(val) + len(test) == len(data)
    assert len(train) == len(set(train))

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_hash = hashlib.sha256("toy-dataset".encode("utf-8")).hexdigest()
    assert manifest["seed"] == 99
    assert manifest["dataset"]["hashed_id"] == expected_hash
    assert manifest["splits"]["train"]["size"] == len(train)
    assert manifest["splits"]["val"]["size"] == len(val)
    assert manifest["splits"]["test"]["size"] == len(test)

    checksums = json.loads((tmp_path / DEFAULT_CHECKSUMS_NAME).read_text(encoding="utf-8"))
    assert checksums["train"] == manifest["splits"]["train"]["checksum"]
    assert checksums["val"] == manifest["splits"]["val"]["checksum"]
    assert checksums["test"] == manifest["splits"]["test"]["checksum"]


def test_train_val_test_split_reproducible(tmp_path: Path) -> None:
    data = [f"item-{i}" for i in range(15)]
    run_a = tmp_path / "run_a"
    run_b = tmp_path / "run_b"
    run_a.mkdir()
    run_b.mkdir()

    result_a = train_val_test_split(
        data,
        val_frac=0.2,
        test_frac=0.2,
        seed=7,
        dataset_id="toy-dataset",
        artifact_dir=run_a,
    )
    result_b = train_val_test_split(
        data,
        val_frac=0.2,
        test_frac=0.2,
        seed=7,
        dataset_id="toy-dataset",
        artifact_dir=run_b,
    )

    assert result_a == result_b

    manifest_a = json.loads((run_a / DEFAULT_MANIFEST_NAME).read_text(encoding="utf-8"))
    manifest_b = json.loads((run_b / DEFAULT_MANIFEST_NAME).read_text(encoding="utf-8"))
    assert manifest_a == manifest_b

    checksum_a = json.loads((run_a / DEFAULT_CHECKSUMS_NAME).read_text(encoding="utf-8"))
    checksum_b = json.loads((run_b / DEFAULT_CHECKSUMS_NAME).read_text(encoding="utf-8"))
    assert checksum_a == checksum_b
