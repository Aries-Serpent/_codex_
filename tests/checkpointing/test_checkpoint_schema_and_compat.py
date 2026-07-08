"""
Test Checkpoint Schema And Compat

Test module for checkpoint schema and compat.
"""

from __future__ import annotations

import os
import tempfile
import warnings

from codex_ml.checkpointing import compat, schema_v2


def test_schema_v2_roundtrip() -> None:
    manifest = {
        "schema": schema_v2.SCHEMA_ID,
        "run": {
            "id": "run-1",
            "created_at": "2025-10-07T00:00:00Z",
            "framework": "pytorch",
        },
        "weights": {"format": "pt", "bytes": 123},
        "optimizer": {"name": "adam", "bytes": 42},
        "notes": "integration test",
    }
    schema_v2.validate_manifest(manifest)
    obj = schema_v2.from_dict(manifest)
    roundtrip = schema_v2.to_dict(obj)
    assert roundtrip["schema"] == schema_v2.SCHEMA_ID, "Condition must be true"
    assert roundtrip["run"]["id"] == "run-1", "Condition must be true"

    upgraded = schema_v2.upgrade_from_v1(
        {
            "meta": {"id": "legacy", "created_at": "yesterday"},
            "weights": {"format": "pt", "bytes": 1},
        }
    )
    assert upgraded["schema"] == schema_v2.SCHEMA_ID, "Condition must be true"
    assert upgraded["run"]["id"] == "legacy", "Condition must be true"


def test_checkpoint_compat_emits_warning(monkeypatch) -> None:
    # Clear the lru_cache on _warn_save_checkpoint_deprecated so the warning is emitted
    compat._warn_save_checkpoint_deprecated.cache_clear()
    
    calls = {}

    def fake_save(out_dir, **kwargs):
        calls["args"] = (out_dir, kwargs)
        return out_dir

    monkeypatch.setattr(
        compat, "_core", type("Core", (), {"save_checkpoint": staticmethod(fake_save)})()
    )

    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        compat.save_checkpoint(os.path.join(tempfile.gettempdir(), "ckpt"), state={}, meta={})
    assert calls, "calls is not valid"
    assert any("deprecated" in str(w.message) for w in captured), "Condition must be true"
