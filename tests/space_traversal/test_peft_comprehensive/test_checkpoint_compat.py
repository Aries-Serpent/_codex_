"""
Test Checkpoint Compat

Test module for checkpoint compat.
"""

from codex_ml.utils import checkpoint_core as cc


def test_load_legacy_checkpoint_without_version(tmp_path):
    path = tmp_path / "legacy.pt"
    legacy_payload = {
        "state": {"model_state": {"w": 1}},
        "meta": {
            "schema_version": cc.SCHEMA_VERSION,
            "created_at": 0,
            "git_sha": None,
            "config_hash": None,
            "rng": {},
            "env": {},
            "metric_key": None,
            "metric_value": None,
            "sha256": None,
        },
    }
    digest = cc._digest_payload(legacy_payload).hex()
    legacy_payload["meta"]["sha256"] = digest
    raw = cc._serialize_payload(legacy_payload)
    path.write_bytes(raw)

    state, meta = cc.load_checkpoint(path)

    assert state["model_state"] == {"w": 1}
    assert meta.config_version is None
    assert meta.dataset_version is None
