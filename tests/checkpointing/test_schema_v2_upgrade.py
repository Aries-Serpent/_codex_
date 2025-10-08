from __future__ import annotations

from codex_ml.checkpointing.schema_v2 import digest, is_v2, upgrade_from_v1, validate_manifest


def test_upgrade_from_v1_minimal():
    v1 = {
        "meta": {"id": "x", "created_at": "2025-10-07T00:00:00Z"},
        "weights": {"format": "pt", "bytes": 3},
    }
    v2 = upgrade_from_v1(v1)
    assert is_v2(v2)
    validate_manifest(v2)
    _ = digest(v2)
