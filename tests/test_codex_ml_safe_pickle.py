from __future__ import annotations

import hashlib
import hmac
import os
import pickle
from pathlib import Path

import pytest

from codex_ml.utils import safe_pickle as safe_pickle_module


def test_safe_pickle_dump_writes_versioned_signature_header(tmp_path: Path) -> None:
    payload = {"value": 7}
    key = b"k" * 32
    pickle_path = tmp_path / "signed.pkl"

    safe_pickle_module.safe_pickle_dump(payload, str(pickle_path), add_signature=True, secret_key=key)

    raw = pickle_path.read_bytes()
    assert raw.startswith(safe_pickle_module.SIGNED_PICKLE_MAGIC)
    assert raw[len(safe_pickle_module.SIGNED_PICKLE_MAGIC)] == safe_pickle_module.SIGNED_PICKLE_VERSION
    assert (
        raw[len(safe_pickle_module.SIGNED_PICKLE_MAGIC) + 1]
        == safe_pickle_module.SIGNED_PICKLE_ALGO_SHA256
    )
    assert (
        safe_pickle_module.safe_pickle_load(
            str(pickle_path), verify_signature=True, secret_key=key, use_restricted_unpickler=False
        )
        == payload
    )


def test_safe_pickle_load_supports_legacy_signature_format(tmp_path: Path) -> None:
    payload = {"legacy": True}
    key = b"z" * 32
    pickled = pickle.dumps(payload)
    legacy_signed = pickled + hmac.new(key, pickled, hashlib.sha256).digest()
    pickle_path = tmp_path / "legacy.pkl"
    pickle_path.write_bytes(legacy_signed)

    loaded = safe_pickle_module.safe_pickle_load(
        str(pickle_path), verify_signature=True, secret_key=key, use_restricted_unpickler=False
    )

    assert loaded == payload


def test_get_secret_key_creates_private_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("PICKLE_SECRET_KEY", raising=False)

    key = safe_pickle_module._get_secret_key()
    key_path = tmp_path / ".codex" / "pickle.key"

    assert key_path.read_bytes() == key
    assert os.stat(key_path).st_mode & 0o777 == 0o600
