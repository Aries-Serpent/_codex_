"""
Test Validator

Test module for validator.
"""

from __future__ import annotations

import json
from pathlib import Path

from codex_ml.data.validator import DatasetValidator


def _write_manifest(tmp_path: Path, **overrides) -> Path:
    manifest = {
        "name": "demo",
        "version": "0.1.0",
        "splits": {"train": 1},
        "checksums": [
            {"path": "train.jsonl", "sha256": "0" * 64},
        ],
        "features": [
            {"name": "text", "dtype": "string"},
        ],
    }
    manifest.update(overrides)
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return manifest_path


def test_validate_manifest_success(tmp_path: Path) -> None:
    manifest_path = _write_manifest(tmp_path)
    (tmp_path / "train.jsonl").write_text("{}\n", encoding="utf-8")
    assert DatasetValidator.validate_manifest(manifest_path), "Data must not be empty"
    assert DatasetValidator.validate_splits(manifest_path), "Data must not be empty"


def test_validate_manifest_failure(tmp_path: Path) -> None:
    manifest_path = _write_manifest(tmp_path, name=123)
    assert not DatasetValidator.validate_manifest(manifest_path), "Data must not be empty"


def test_validate_missing_files(tmp_path: Path) -> None:
    manifest_path = _write_manifest(tmp_path)
    assert not DatasetValidator.validate_splits(manifest_path), "Data must not be empty"
