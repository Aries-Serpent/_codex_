"""Unit tests for Internal Tools API key security helpers."""

from __future__ import annotations

import importlib.util
import sys
import time
from pathlib import Path

# PBKDF2-HMAC-SHA256 with digest_size=32 bytes → 64-character hex string.
_PBKDF2_DIGEST_HEX_LEN = 64


def _load_security_module():
    module_path = Path(__file__).resolve().parents[1] / "app" / "security.py"
    spec = importlib.util.spec_from_file_location("ita_security", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_verify_api_key_accepts_issued_key(tmp_path: Path, monkeypatch) -> None:
    security = _load_security_module()
    try:
        store_path = tmp_path / "api_keys.json"
        pepper = tmp_path / "pepper.bin"
        pepper.write_bytes(b"deterministic-test-pepper-bytes-32b")  # file-path pepper
        monkeypatch.setenv("ITA_API_KEYS_PATH", str(store_path))
        monkeypatch.setenv("ITA_API_KEY_PEPPER", str(pepper))

        store = security.ApiKeyStore(path=store_path)
        issued_key = store.issue_key()

        hashed = security.verify_api_key(issued_key, store=store)
        assert hashed == security.hash_key(issued_key)
    finally:
        sys.modules.pop("ita_security", None)


def test_verify_api_key_migrates_legacy_sha256_hash(tmp_path: Path, monkeypatch) -> None:
    """Verify that bare-SHA256 hashes (pre-0.2) are migrated to PBKDF2 on first auth."""
    security = _load_security_module()
    try:
        store_path = tmp_path / "api_keys.json"
        monkeypatch.setenv("ITA_API_KEYS_PATH", str(store_path))
        monkeypatch.setenv("ITA_API_KEY_PEPPER", "test-pepper")

        legacy_token = "ita_legacy_token"
        legacy_hash = security._legacy_hash_key(legacy_token.encode("utf-8"))
        record = security.ApiKeyRecord(key_hash=legacy_hash, created_at=time.time())
        store = security.ApiKeyStore(path=store_path)
        store._dump([record])

        upgraded_hash = security.verify_api_key(legacy_token, store=store)
        assert upgraded_hash == security.hash_key(legacy_token)
        assert upgraded_hash in store.hashed_keys()
        assert legacy_hash not in store.hashed_keys()
    finally:
        sys.modules.pop("ita_security", None)


def test_verify_api_key_migrates_hmac_sha256_hash(tmp_path: Path, monkeypatch) -> None:
    """Verify that HMAC-SHA256 hashes (0.2.x) are migrated to PBKDF2 on first auth."""
    security = _load_security_module()
    try:
        store_path = tmp_path / "api_keys.json"
        monkeypatch.setenv("ITA_API_KEYS_PATH", str(store_path))
        monkeypatch.setenv("ITA_API_KEY_PEPPER", "test-pepper")

        token = "ita_hmac_sha256_token"
        # Store the token using the intermediate HMAC-SHA256 scheme
        intermediate_hash = security._hmac_sha256_hash_key(token.encode("utf-8"))
        record = security.ApiKeyRecord(key_hash=intermediate_hash, created_at=time.time())
        store = security.ApiKeyStore(path=store_path)
        store._dump([record])

        upgraded_hash = security.verify_api_key(token, store=store)
        # Should now be stored as PBKDF2
        assert upgraded_hash == security.hash_key(token)
        assert upgraded_hash in store.hashed_keys()
        assert intermediate_hash not in store.hashed_keys()
    finally:
        sys.modules.pop("ita_security", None)


def test_verify_api_key_migrates_blake2b_hash(tmp_path: Path, monkeypatch) -> None:
    """Verify that BLAKE2b hashes (0.3.x) are migrated to PBKDF2 on first auth."""
    import warnings

    security = _load_security_module()
    try:
        store_path = tmp_path / "api_keys.json"
        pepper = tmp_path / "pepper.bin"
        pepper.write_bytes(b"deterministic-test-pepper-bytes-32b")
        monkeypatch.setenv("ITA_API_KEYS_PATH", str(store_path))
        monkeypatch.setenv("ITA_API_KEY_PEPPER", str(pepper))

        token = "ita_blake2b_token"
        # Access the private migration helper directly to simulate a 0.3.x stored hash.
        # This is intentional for migration validation: the function is deprecated but
        # must remain callable to verify that verify_api_key() correctly upgrades it.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            blake2b_hash = security._blake2b_hash_key(token.encode("utf-8"))
        record = security.ApiKeyRecord(key_hash=blake2b_hash, created_at=time.time())
        store = security.ApiKeyStore(path=store_path)
        store._dump([record])

        upgraded_hash = security.verify_api_key(token, store=store)
        # Should now be stored as PBKDF2
        assert upgraded_hash == security.hash_key(token)
        assert upgraded_hash in store.hashed_keys()
        assert blake2b_hash not in store.hashed_keys()
    finally:
        sys.modules.pop("ita_security", None)


def test_hash_key_uses_pbkdf2(monkeypatch) -> None:
    """hash_key should produce a PBKDF2-HMAC-SHA256 hex digest (64 hex chars = 32 bytes)."""
    security = _load_security_module()
    try:
        monkeypatch.setenv("ITA_API_KEY_PEPPER", "unit-test-pepper")
        result = security.hash_key("some_api_key")
        # PBKDF2-HMAC-SHA256 produces a 32-byte (64 hex char) digest
        assert isinstance(result, str)
        assert len(result) == _PBKDF2_DIGEST_HEX_LEN
    finally:
        sys.modules.pop("ita_security", None)
