"""Security helpers for the Internal Tools API."""

from __future__ import annotations

import json
import os
import secrets
import time
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Iterable, Optional, Set

from fastapi import HTTPException, status

_KEY_FILE_ENV = "ITA_API_KEYS_PATH"
_SINGLE_KEY_ENV = "ITA_API_KEY"
_ADDITIONAL_KEYS_ENV = "ITA_ADDITIONAL_API_KEYS"
_DEFAULT_RUNTIME_PATH = Path(__file__).resolve().parent.parent / "runtime" / "api_keys.json"


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

    def _load(self) -> Set[ApiKeyRecord]:
        if not self.path.exists():
            return set()
        with self.path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        records = {ApiKeyRecord.from_dict(item) for item in payload.get("keys", [])}
        return records

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

    def hashed_keys(self) -> Set[str]:
        return {record.key_hash for record in self._load()}


def hash_key(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _keys_from_environment() -> Set[str]:
    keys: Set[str] = set()
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

    if hashed_candidate in store.hashed_keys():
        return hashed_candidate

    if candidate in _keys_from_environment():
        return hashed_candidate

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


__all__ = ["ApiKeyStore", "ApiKeyRecord", "hash_key", "verify_api_key"]
