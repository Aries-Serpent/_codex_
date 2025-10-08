from __future__ import annotations

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
    assert roundtrip["schema"] == schema_v2.SCHEMA_ID
    assert roundtrip["run"]["id"] == "run-1"

    upgraded = schema_v2.upgrade_from_v1(
        {
            "meta": {"id": "legacy", "created_at": "yesterday"},
            "weights": {"format": "pt", "bytes": 1},
        }
    )
    assert upgraded["schema"] == schema_v2.SCHEMA_ID
    assert upgraded["run"]["id"] == "legacy"


def test_checkpoint_compat_emits_warning(monkeypatch) -> None:
    monkeypatch.setattr(compat, "_warned", False)
    calls = {}

    def fake_save(out_dir, **kwargs):
        calls["args"] = (out_dir, kwargs)
        return out_dir

    monkeypatch.setattr(
        compat, "_core", type("Core", (), {"save_checkpoint": staticmethod(fake_save)})()
    )

    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        compat.save_checkpoint("/tmp/ckpt", state={}, meta={})
    assert calls
    assert any("deprecated" in str(w.message) for w in captured)
