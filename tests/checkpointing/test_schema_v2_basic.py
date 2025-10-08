from __future__ import annotations
import json
from pathlib import Path

from codex_ml.checkpointing.schema_v2 import (
    CANON_SEPARATORS,
    CheckpointMetaV2,
    compute_manifest_digest,
    new_manifest,
    to_canonical_bytes,
    validate_manifest,
)


def test_checkpoint_meta_roundtrip_and_digest(tmp_path: Path):
    meta = CheckpointMetaV2(run_id="run-1", step=10, epoch=1, created_utc=123.0, notes="ok")
    manifest = meta.to_dict()
    canon = to_canonical_bytes(manifest)
    assert canon.decode("utf-8").count(",") == len(manifest) - 1
    digest = compute_manifest_digest(manifest)
    path = tmp_path / "manifest.json"
    path.write_text(
        json.dumps(manifest, separators=CANON_SEPARATORS, sort_keys=True), encoding="utf-8"
    )
    on_disk = json.loads(path.read_text(encoding="utf-8"))
    assert compute_manifest_digest(on_disk) == digest


def test_validate_manifest_reports_missing_fields():
    problems = validate_manifest({})
    assert "missing field" in problems[0]
    good = {"run_id": "r", "step": 1, "epoch": 0, "created_utc": 0.0}
    assert validate_manifest(good) == []


def test_new_manifest_includes_digest(monkeypatch):
    monkeypatch.setattr("codex_ml.checkpointing.schema_v2.time.time", lambda: 100.0)
    manifest = new_manifest("r", 1, 0)
    assert manifest["run_id"] == "r"
    assert manifest["digest"] == compute_manifest_digest(
        {k: v for k, v in manifest.items() if k != "digest"}
    )
