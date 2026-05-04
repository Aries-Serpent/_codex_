"""Unit tests for Internal Tools API key security helpers."""

from __future__ import annotations

import importlib.util
import sys
import time
from pathlib import Path


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
    store_path = tmp_path / "api_keys.json"
    pepper = tmp_path / "pepper.bin"
    monkeypatch.setenv("ITA_API_KEYS_PATH", str(store_path))
    monkeypatch.setenv("ITA_API_KEY_PEPPER", str(pepper))

    store = security.ApiKeyStore(path=store_path)
    issued_key = store.issue_key()

    hashed = security.verify_api_key(issued_key, store=store)
    assert hashed == security.hash_key(issued_key)


def test_verify_api_key_migrates_legacy_hash(tmp_path: Path, monkeypatch) -> None:
    security = _load_security_module()
    store_path = tmp_path / "api_keys.json"
    monkeypatch.setenv("ITA_API_KEYS_PATH", str(store_path))
    monkeypatch.setenv("ITA_API_KEY_PEPPER", "test-pepper")

    legacy_token = "ita_legacy_token"
    legacy_hash = security._legacy_hash_key(legacy_token)
    record = security.ApiKeyRecord(key_hash=legacy_hash, created_at=time.time())
    store = security.ApiKeyStore(path=store_path)
    store._dump([record])

    upgraded_hash = security.verify_api_key(legacy_token, store=store)
    assert upgraded_hash == security.hash_key(legacy_token)
    assert upgraded_hash in store.hashed_keys()
    assert legacy_hash not in store.hashed_keys()
