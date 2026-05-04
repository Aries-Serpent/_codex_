"""Security helpers for the Internal Tools API."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import time
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, status

_KEY_FILE_ENV = "ITA_API_KEYS_PATH"
_SINGLE_KEY_ENV = "ITA_API_KEY"
_ADDITIONAL_KEYS_ENV = "ITA_ADDITIONAL_API_KEYS"
_PEPPER_ENV = "ITA_API_KEY_PEPPER"
_DEFAULT_RUNTIME_PATH = Path(__file__).resolve().parent.parent / "runtime" / "api_keys.json"
_DEFAULT_PEPPER_PATH = Path(__file__).resolve().parent.parent / "runtime" / "api_key_pepper.bin"


@dataclass(frozen=True, slots=True)
class ApiKeyRecord:
    """A hashed API key and metadata stored on disk."""

    key_hash: str
    created_at: float

    def to_dict(self) -> dict[str, float | str]:
        return {"hash": self.key_hash, "created_at": self.created_at}

    @classmethod
    def from_dict(cls, data: dict[str, float | str]) -> "ApiKeyRecord":
        return cls(key_hash=str(data["hash"]), created_at=float(data["created_at"]))


class ApiKeyStore:
    """Minimal file-backed API key store that keeps only hashed keys."""

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = Path(path or os.environ.get(_KEY_FILE_ENV, _DEFAULT_RUNTIME_PATH))
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> set[ApiKeyRecord]:
        if not self.path.exists():
            return set()
        with self.path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return {ApiKeyRecord.from_dict(item) for item in payload.get("keys", [])}

    def _dump(self, records: Iterable[ApiKeyRecord]) -> None:
        serialized = {
            "keys": [record.to_dict() for record in sorted(records, key=lambda r: r.created_at)]
        }
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(serialized, handle, indent=2)

    def issue_key(self) -> str:
        token = f"ita_{secrets.token_urlsafe(24)}"
        records = self._load()
        record = ApiKeyRecord(key_hash=hash_key(token), created_at=time.time())
        records.add(record)
        self._dump(records)
        return token

    def hashed_keys(self) -> set[str]:
        return {record.key_hash for record in self._load()}

    def upgrade_hash(self, old_hash: str, new_hash: str) -> None:
        """Replace a legacy hash with a stronger hash while preserving metadata."""
        records = self._load()
        upgraded = set()
        changed = False
        for record in records:
            if record.key_hash == old_hash:
                upgraded.add(ApiKeyRecord(key_hash=new_hash, created_at=record.created_at))
                changed = True
            else:
                upgraded.add(record)
        if changed:
            self._dump(upgraded)


def _load_hash_pepper() -> bytes:
    """Load or create the server-side pepper used for keyed API-key hashing."""
    configured = os.environ.get(_PEPPER_ENV, "").strip()
    if configured:
        return configured.encode("utf-8")

    try:
        _DEFAULT_PEPPER_PATH.parent.mkdir(parents=True, exist_ok=True)
        if _DEFAULT_PEPPER_PATH.exists():
            return _DEFAULT_PEPPER_PATH.read_bytes()
        pepper = secrets.token_bytes(32)
        try:
            with _DEFAULT_PEPPER_PATH.open("xb") as handle:
                handle.write(pepper)
            _DEFAULT_PEPPER_PATH.chmod(0o600)
            return pepper
        except FileExistsError:
            # Another process initialized the pepper first; use that value.
            return _DEFAULT_PEPPER_PATH.read_bytes()
    except OSError as exc:
        raise RuntimeError(
            f"Unable to load or initialize API key pepper at {_DEFAULT_PEPPER_PATH}"
        ) from exc


def _legacy_hash_key(value: str) -> str:
    """Legacy non-keyed hash used by older deployments."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hash_key(value: str) -> str:
    """Hash API key for storage and lookup using a keyed digest."""
    pepper = _load_hash_pepper()
    return hmac.new(pepper, value.encode("utf-8"), hashlib.sha256).hexdigest()


def _keys_from_environment() -> set[str]:
    keys: set[str] = set()
    single = os.environ.get(_SINGLE_KEY_ENV)
    if single:
        keys.add(single.strip())
    additional = os.environ.get(_ADDITIONAL_KEYS_ENV)
    if additional:
        keys.update(k.strip() for k in additional.split(",") if k.strip())
    return keys


def verify_api_key(candidate: Optional[str], store: Optional[ApiKeyStore] = None) -> str:
    """Validate the provided API key.

    Returns the hashed key when validation succeeds.
    """

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-API-Key header"
        )

    store = store or ApiKeyStore()
    hashed_candidate = hash_key(candidate)
    legacy_hashed_candidate = _legacy_hash_key(candidate)
    stored_hashes = store.hashed_keys()

    if hashed_candidate in stored_hashes:
        return hashed_candidate

    # Backward compatibility: transparently migrate legacy hashes on successful auth.
    if legacy_hashed_candidate in stored_hashes:
        store.upgrade_hash(legacy_hashed_candidate, hashed_candidate)
        return hashed_candidate

    if candidate in _keys_from_environment():
        return hashed_candidate

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


__all__ = ["ApiKeyStore", "ApiKeyRecord", "hash_key", "verify_api_key"]
