from __future__ import annotations

from codex_ml.checkpointing.schema_v2 import (
    CheckpointManifest,
    RunMeta,
    WeightsMeta,
    canonical_json,
    digest,
    from_dict,
    to_dict,
    validate_manifest,
)


def test_roundtrip_and_digest_stability(tmp_path):
    m = CheckpointManifest(
        run=RunMeta(id="run123", created_at="2025-10-07T12:00:00Z"),
        weights=WeightsMeta(format="pt", bytes=42, dtype="float32", sharded=False),
        notes="unit test",
    )
    d1 = to_dict(m)
    j1 = canonical_json(d1)
    h1 = digest(d1)
    d2 = {
        "weights": {"bytes": 42, "format": "pt", "dtype": "float32", "sharded": False},
        "schema": "codex.checkpoint.v2",
        "notes": "unit test",
        "run": {
            "id": "run123",
            "created_at": "2025-10-07T12:00:00Z",
            "framework": "pytorch",
            "codex_version": None,
        },
        "optimizer": None,
        "scheduler": None,
        "rng": None,
    }
    j2 = canonical_json(d2)
    h2 = digest(d2)
    assert j1 == j2 and h1 == h2
    m2 = from_dict(d2)
    assert to_dict(m2) == d1


def test_validate_manifest_minimum():
    good = {
        "schema": "codex.checkpoint.v2",
        "run": {"id": "r", "created_at": "2025-10-07T00:00:00Z"},
        "weights": {"format": "pt", "bytes": 1},
    }
    validate_manifest(good)
    bad = {"run": {}, "weights": {}}
    try:
        validate_manifest(bad)
    except ValueError as e:
        assert "schema" in str(e)
    else:  # pragma: no cover - defensive
        raise AssertionError("expected ValueError")
