"""
Test Checkpoint Compat

Test module for checkpoint compat.
"""

import hashlib

from codex_ml.utils import checkpoint_core as cc


def test_load_legacy_checkpoint_without_version(tmp_path):
    path = tmp_path / "legacy.pt"
    # Create the meta dict for the legacy checkpoint (without config_version, dataset_version)
    meta_dict = {
        "schema_version": cc.SCHEMA_VERSION,
        "created_at": 0,
        "git_sha": None,
        "config_hash": None,
        "rng": {},
        "env": {},
        "metric_key": None,
        "metric_value": None,
        "sha256": None,
    }
    state_dict = {"model_state": {"w": 1}}

    # Compute digest the same way load_checkpoint does for file paths
    # (uses hashlib.sha256 of serialized payload, not _digest_payload)
    digest_meta = dict(meta_dict)
    digest_meta["sha256"] = None
    digest = hashlib.sha256(
        cc._serialize_payload({"state": state_dict, "meta": digest_meta})
    ).hexdigest()

    # Set the digest in the meta and create the final payload
    meta_dict["sha256"] = digest
    legacy_payload = {
        "state": state_dict,
        "meta": meta_dict,
    }
    raw = cc._serialize_payload(legacy_payload)
    path.write_bytes(raw)

    state, meta = cc.load_checkpoint(path)

    assert state["model_state"] == {"w": 1}, "Condition must be true"
    assert meta.config_version is None, "config_version is not valid"
    assert meta.dataset_version is None, "Data must not be empty"
