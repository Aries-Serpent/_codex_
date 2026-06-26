"""
Test Checkpoint Core Io

Test module for checkpoint core io.
"""

from __future__ import annotations

import pickle
import types

import pytest

from codex_ml.utils import checkpoint_core


def test_save_and_load_roundtrip(tmp_path) -> None:
    ckpt_dir = tmp_path / "epoch-0"
    payload = {
        "model_state": {"w": [1, 2]},
        "optimizer_state": {"beta": 0.9},
    }
    metadata = {"metrics": {"loss": 0.25}}
    state_path, _meta = checkpoint_core.save_checkpoint(
        ckpt_dir,
        payload=payload,
        metadata=metadata,
        include_rng=False,
    )
    assert state_path.exists(), "Condition must be true"

    loaded_state, loaded_meta = checkpoint_core.load_checkpoint(ckpt_dir)
    assert loaded_state["model_state"] == payload["model_state"], "Condition must be true"
    assert loaded_state["optimizer_state"] == payload["optimizer_state"], "Condition must be true"
    assert loaded_meta.schema_version == checkpoint_core.SCHEMA_VERSION, "schema_version is not valid"
    assert loaded_meta.rng == {}, "rng is not valid"


def test_deserialize_payload_prefers_weights_only_torch_load(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = {"state": {"epoch": 1}, "meta": {"schema_version": checkpoint_core.SCHEMA_VERSION}}
    raw = checkpoint_core.trusted_pickle_dumps(payload)
    captured: dict[str, object] = {}

    def fake_load(source, **kwargs):  # type: ignore[no-untyped-def]
        captured["source_type"] = type(source).__name__
        captured["kwargs"] = dict(kwargs)
        return payload

    monkeypatch.setattr(
        checkpoint_core,
        "torch",
        types.SimpleNamespace(load=fake_load, __version__="2.2.0"),
    )

    assert checkpoint_core._deserialize_payload(raw) == payload, "checkpoint_c is not valid"
    assert captured["source_type"] == "BytesIO", "Condition must be true"
    assert captured["kwargs"] == {"map_location": "cpu", "weights_only": True}


def test_deserialize_payload_fallback_rejects_unsafe_pickle(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_runtime_error(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        raise RuntimeError("invalid checkpoint payload")

    monkeypatch.setattr(
        checkpoint_core,
        "torch",
        types.SimpleNamespace(load=raise_runtime_error, __version__="2.2.0"),
    )

    evil_payload = b"cposix\nsystem\np0\n(Vecho evil\np1\ntp2\nRp3\n."

    with pytest.raises(pickle.UnpicklingError, match="Class posix.system not in whitelist"):
        checkpoint_core._deserialize_payload(evil_payload)
