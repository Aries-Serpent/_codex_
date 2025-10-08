from __future__ import annotations

from codex_ml.checkpointing.schema_v2 import (
    compute_manifest_digest,
    to_canonical_bytes,
    validate_manifest,
)


def test_canonical_digest_is_order_insensitive():
    manifest_a = {
        "run_id": "x",
        "step": 1,
        "epoch": 0,
        "created_utc": 0.0,
        "extra": {"b": 2, "a": 1},
    }
    manifest_b = {
        "created_utc": 0.0,
        "epoch": 0,
        "extra": {"a": 1, "b": 2},
        "run_id": "x",
        "step": 1,
    }
    validate_manifest(manifest_a)
    da = compute_manifest_digest(manifest_a)
    db = compute_manifest_digest(manifest_b)
    assert da == db
    assert to_canonical_bytes(manifest_a) == to_canonical_bytes(manifest_b)
