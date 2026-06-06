"""Unit tests for codex_ml.utils.safe_pickle."""

from __future__ import annotations

import os
import pickle
from pathlib import Path

import pytest

from codex_ml.utils.safe_pickle import (
    SIGNED_PICKLE_ALGO_SHA256,
    SIGNED_PICKLE_HEADER,
    SIGNED_PICKLE_HEADER_LEN,
    SIGNED_PICKLE_MAGIC,
    SIGNED_PICKLE_SIGNATURE_LEN,
    SIGNED_PICKLE_VERSION,
    RestrictedUnpickler,
    _build_signed_pickle,
    _split_signed_pickle,
    safe_pickle_dump,
    safe_pickle_load,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_magic_bytes():
    assert SIGNED_PICKLE_MAGIC == b"SPKL"


def test_header_starts_with_magic():
    assert SIGNED_PICKLE_HEADER.startswith(SIGNED_PICKLE_MAGIC)


def test_signature_length():
    assert SIGNED_PICKLE_SIGNATURE_LEN == 32  # SHA-256 digest size


def test_header_version_and_algo():
    assert SIGNED_PICKLE_HEADER[len(SIGNED_PICKLE_MAGIC)] == SIGNED_PICKLE_VERSION
    assert SIGNED_PICKLE_HEADER[len(SIGNED_PICKLE_MAGIC) + 1] == SIGNED_PICKLE_ALGO_SHA256


# ---------------------------------------------------------------------------
# RestrictedUnpickler — allowed classes
# ---------------------------------------------------------------------------


def _roundtrip_restricted(obj: object) -> object:
    data = pickle.dumps(obj)
    import io

    return RestrictedUnpickler(io.BytesIO(data)).load()


def test_restricted_unpickler_allows_int():
    assert _roundtrip_restricted(42) == 42


def test_restricted_unpickler_allows_float():
    assert _roundtrip_restricted(3.14) == pytest.approx(3.14)


def test_restricted_unpickler_allows_str():
    assert _roundtrip_restricted("hello") == "hello"


def test_restricted_unpickler_allows_list():
    assert _roundtrip_restricted([1, 2, 3]) == [1, 2, 3]


def test_restricted_unpickler_allows_dict():
    assert _roundtrip_restricted({"a": 1}) == {"a": 1}


def test_restricted_unpickler_allows_tuple():
    assert _roundtrip_restricted((1, 2)) == (1, 2)


def test_restricted_unpickler_allows_bytes():
    assert _roundtrip_restricted(b"raw") == b"raw"


def test_restricted_unpickler_blocks_unsafe_class():
    import io

    # Craft a minimal pickle that tries to load os.system (not in allowlist)
    # Protocol 2 opcode: GLOBAL opcode (b'c') followed by module\nname\n
    payload = b"\x80\x02cos\nsystem\nq\x00."
    with pytest.raises(pickle.UnpicklingError, match="not in whitelist"):
        RestrictedUnpickler(io.BytesIO(payload)).load()


# ---------------------------------------------------------------------------
# _build_signed_pickle / _split_signed_pickle — round-trip
# ---------------------------------------------------------------------------


_SECRET = b"test_secret_key_32_bytes_padding!"


def test_build_and_split_roundtrip():
    payload = pickle.dumps({"x": 1})
    signed = _build_signed_pickle(payload, _SECRET)
    recovered_payload, sig = _split_signed_pickle(signed)
    assert recovered_payload == payload
    assert len(sig) == SIGNED_PICKLE_SIGNATURE_LEN


def test_build_signed_starts_with_header():
    signed = _build_signed_pickle(b"data", _SECRET)
    assert signed.startswith(SIGNED_PICKLE_HEADER)


def test_split_legacy_format():
    """Files without SPKL magic are treated as legacy: sig appended at end."""
    import hmac
    import hashlib

    payload = b"legacy_data"
    sig = hmac.new(_SECRET, payload, hashlib.sha256).digest()
    legacy = payload + sig
    recovered, recovered_sig = _split_signed_pickle(legacy)
    assert recovered == payload
    assert recovered_sig == sig


def test_split_too_small_legacy_raises():
    with pytest.raises(ValueError, match="too small"):
        _split_signed_pickle(b"tiny")


def test_split_too_small_versioned_raises():
    # Valid header but no room for sig + payload
    data = SIGNED_PICKLE_HEADER + b"short"
    with pytest.raises(ValueError, match="too small"):
        _split_signed_pickle(data)


def test_split_bad_version_raises():
    # Craft a header with wrong version byte
    bad_header = SIGNED_PICKLE_MAGIC + bytes([99, SIGNED_PICKLE_ALGO_SHA256])
    sig_and_payload = b"\x00" * (SIGNED_PICKLE_SIGNATURE_LEN + 4)
    data = bad_header + sig_and_payload
    with pytest.raises(ValueError, match="Unsupported signed pickle version"):
        _split_signed_pickle(data)


def test_split_bad_algo_raises():
    bad_header = SIGNED_PICKLE_MAGIC + bytes([SIGNED_PICKLE_VERSION, 99])
    sig_and_payload = b"\x00" * (SIGNED_PICKLE_SIGNATURE_LEN + 4)
    data = bad_header + sig_and_payload
    with pytest.raises(ValueError, match="Unsupported signed pickle algorithm"):
        _split_signed_pickle(data)


# ---------------------------------------------------------------------------
# safe_pickle_dump / safe_pickle_load — basic usage
# ---------------------------------------------------------------------------


def test_dump_and_load_simple(tmp_path: Path):
    path = str(tmp_path / "test.pkl")
    obj = {"key": "value", "num": 42}
    safe_pickle_dump(obj, path)
    loaded = safe_pickle_load(path)
    assert loaded == obj


def test_dump_and_load_nested(tmp_path: Path):
    path = str(tmp_path / "nested.pkl")
    obj = [1, {"a": [2, 3]}, (4, 5)]
    safe_pickle_dump(obj, path)
    loaded = safe_pickle_load(path)
    assert loaded == obj


def test_dump_creates_parent_dirs(tmp_path: Path):
    path = str(tmp_path / "deep" / "nested" / "file.pkl")
    safe_pickle_dump({"x": 1}, path)
    assert Path(path).exists()


def test_load_file_not_found_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match="Pickle file not found"):
        safe_pickle_load(str(tmp_path / "missing.pkl"))


def test_load_without_restricted_unpickler(tmp_path: Path):
    path = str(tmp_path / "unrestricted.pkl")
    safe_pickle_dump([1, 2, 3], path)
    loaded = safe_pickle_load(path, use_restricted_unpickler=False)
    assert loaded == [1, 2, 3]


# ---------------------------------------------------------------------------
# Signed pickle round-trip (dump + load with HMAC)
# ---------------------------------------------------------------------------


def test_signed_dump_and_load(tmp_path: Path):
    path = str(tmp_path / "signed.pkl")
    obj = {"signed": True, "value": 99}
    safe_pickle_dump(obj, path, add_signature=True, secret_key=_SECRET)
    loaded = safe_pickle_load(path, verify_signature=True, secret_key=_SECRET)
    assert loaded == obj


def test_tampered_signed_pickle_raises(tmp_path: Path):
    path = str(tmp_path / "tampered.pkl")
    obj = {"safe": True}
    safe_pickle_dump(obj, path, add_signature=True, secret_key=_SECRET)
    # Corrupt one byte of the file payload
    raw = Path(path).read_bytes()
    corrupted = bytearray(raw)
    corrupted[-1] ^= 0xFF
    Path(path).write_bytes(bytes(corrupted))
    with pytest.raises(ValueError, match="HMAC signature verification failed"):
        safe_pickle_load(path, verify_signature=True, secret_key=_SECRET)


def test_wrong_key_raises(tmp_path: Path):
    path = str(tmp_path / "wrong_key.pkl")
    safe_pickle_dump({"x": 1}, path, add_signature=True, secret_key=_SECRET)
    with pytest.raises(ValueError, match="HMAC signature verification failed"):
        safe_pickle_load(path, verify_signature=True, secret_key=b"wrong_key_entirely_different!!!!!")


# ---------------------------------------------------------------------------
# Environment variable secret key integration
# ---------------------------------------------------------------------------


def test_dump_load_signed_with_env_key(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PICKLE_SECRET_KEY", "env_secret_key_value")
    path = str(tmp_path / "env_signed.pkl")
    obj = {"env": "key_test"}
    safe_pickle_dump(obj, path, add_signature=True)
    loaded = safe_pickle_load(path, verify_signature=True)
    assert loaded == obj
