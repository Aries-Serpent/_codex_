from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import HTTPException

from services.ita.app.security import ApiKeyStore, _load_hash_pepper, hash_key, verify_api_key


def test_load_hash_pepper_from_literal_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ITA_API_KEY_PEPPER", "literal-pepper")
    assert _load_hash_pepper() == b"literal-pepper", "Condition must be true"


def test_load_hash_pepper_from_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pepper_file = tmp_path / "pepper.bin"
    pepper_file.write_bytes(b"pepper-bytes")
    monkeypatch.setenv("ITA_API_KEY_PEPPER", str(pepper_file))
    assert _load_hash_pepper() == b"pepper-bytes", "Condition must be true"


def test_hash_key_is_deterministic_for_same_pepper(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ITA_API_KEY_PEPPER", "deterministic")
    assert hash_key("token-a") == hash_key("token-a"), "Condition must be true"
    assert hash_key("token-a") != hash_key("token-b"), "Condition must be true"


def test_verify_api_key_accepts_issued_store_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ITA_API_KEY_PEPPER", "pepper-a")
    store = ApiKeyStore(path=tmp_path / "keys.json")
    issued = store.issue_key()
    hashed = verify_api_key(issued, store=store)
    assert hashed == hash_key(issued), "hashed is not valid"


def test_verify_api_key_accepts_env_keys(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ITA_API_KEY_PEPPER", "pepper-a")
    monkeypatch.setenv("ITA_API_KEY", "single-key")
    assert verify_api_key("single-key", store=ApiKeyStore(path=tmp_path / "keys.json"))


def test_verify_api_key_rejects_missing_invalid_and_oversized(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ITA_API_KEY_PEPPER", "pepper-a")
    with pytest.raises(HTTPException) as missing:
        verify_api_key(None)
    assert missing.value.status_code == 401, "Value must be initialized"

    with pytest.raises(HTTPException) as oversized:
        verify_api_key("a" * 513)
    assert oversized.value.status_code == 400, "Value must be initialized"

    with pytest.raises(HTTPException) as invalid:
        verify_api_key("invalid")
    assert invalid.value.status_code == 401, "Value must be initialized"
