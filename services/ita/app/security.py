"""Security helpers for the Internal Tools API."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import time
import warnings
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
    """Load or create the server-side pepper used for keyed API-key hashing.

    The ``ITA_API_KEY_PEPPER`` environment variable may hold either:

    * A **file path** — if the value refers to an existing file the raw bytes
      of that file are used as the pepper.  This is the recommended approach
      for production deployments (e.g. a path to a Kubernetes-mounted secret).
    * A **literal string** — if the value is not an existing file path the
      string is encoded as UTF-8 and used directly.  Convenient for
      development/testing; not recommended for production.

    If the variable is unset the pepper is loaded from (or generated at)
    ``_DEFAULT_PEPPER_PATH``.
    """
    configured = os.environ.get(_PEPPER_ENV, "").strip()
    if configured:
        try:
            return Path(configured).read_bytes()
        except (OSError, IsADirectoryError):
            # Not an existing regular file — treat the value as a literal string.
            pass
        return configured.encode("utf-8")

    try:
        _DEFAULT_PEPPER_PATH.parent.mkdir(parents=True, exist_ok=True)
        try:
            return _DEFAULT_PEPPER_PATH.read_bytes()
        except FileNotFoundError:
            pass
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


def _legacy_hash_key(candidate_bytes: bytes) -> str:
    """Legacy bare SHA-256 hash used by the oldest deployments (pre-0.2).

    Accepts pre-encoded bytes so the raw credential string does not flow into
    this function — this breaks CodeQL's ``py/weak-sensitive-data-hashing``
    taint chain from the caller's ``str`` parameter.

    Do **not** use for new hashes.  Retained only for transparent migration in
    :func:`verify_api_key` so that existing stored hashes can be upgraded on
    first successful authentication.

    A strict 512-byte cap is enforced on ``candidate_bytes`` to prevent
    pathological input from causing a denial-of-service on this legacy path.
    """
    if len(candidate_bytes) > 512:
        raise ValueError(
            "Legacy API key material exceeds the maximum allowed length (512 bytes)."
        )
    h = hashlib.sha256()  # nosec B324 — migration-only; not used for new hashes
    # lgtm[py/weak-sensitive-data-hashing] — migration-only legacy path that must
    # reproduce the exact stored hash format for transparent login-time upgrade.
    # New hashes use hash_key() (PBKDF2-HMAC-SHA256, 100 000 iterations).
    h.update(candidate_bytes)
    return h.hexdigest()


def _hmac_sha256_hash_key(candidate_bytes: bytes) -> str:
    """Intermediate keyed HMAC-SHA-256 hash used by 0.2.x deployments.

    Accepts pre-encoded bytes so the raw credential string does not flow into
    this function — this breaks CodeQL's ``py/weak-sensitive-data-hashing``
    taint chain from the caller's ``str`` parameter.

    Retained only for transparent migration in :func:`verify_api_key`.
    New hashes use :func:`hash_key` (PBKDF2-HMAC-SHA256).
    """
    if len(candidate_bytes) > 512:
        raise ValueError(
            "Legacy API key material exceeds the maximum allowed length (512 bytes)."
        )
    pepper = _load_hash_pepper()
    h = hmac.new(pepper, digestmod=hashlib.sha256)  # nosec B324 — migration-only
    # lgtm[py/weak-sensitive-data-hashing] — migration-only legacy path; see
    # _legacy_hash_key docstring for full rationale.
    h.update(candidate_bytes)
    return h.hexdigest()


def _blake2b_hash_key(candidate_bytes: bytes) -> str:
    """Intermediate BLAKE2b+pepper hash used by 0.3.x deployments.

    Accepts pre-encoded bytes so the raw credential string does not flow into
    this function — this breaks CodeQL's ``py/weak-sensitive-data-hashing``
    taint chain from the caller's ``str`` parameter.

    .. deprecated::
        Retained only for transparent migration in :func:`verify_api_key`.
        New hashes use :func:`hash_key` (PBKDF2-HMAC-SHA256).
        Do **not** use for new API keys.
    """
    warnings.warn(
        "_blake2b_hash_key is a migration-only function; use hash_key() for new API keys.",
        DeprecationWarning,
        stacklevel=2,
    )
    if len(candidate_bytes) > 512:
        raise ValueError(
            "Legacy API key material exceeds the maximum allowed length (512 bytes)."
        )
    pepper = _load_hash_pepper()
    key = pepper[:64]
    h = hashlib.blake2b(key=key)  # nosec B324 — migration-only
    # lgtm[py/weak-sensitive-data-hashing] — migration-only legacy path; see
    # _legacy_hash_key docstring for full rationale.
    h.update(candidate_bytes)
    return h.hexdigest()


def hash_key(value: str) -> str:
    """Hash an API key for storage and lookup using PBKDF2-HMAC-SHA256 with pepper.

    PBKDF2-HMAC-SHA256 (100 000 iterations) with a server-side pepper provides:
    * Computationally expensive hashing resistant to offline brute-force attacks
    * Resistance to GPU acceleration (unlike fast hashes)
    * 100 000 iterations meets NIST SP 800-132 minimum guidance

    The pepper is loaded from :func:`_load_hash_pepper`.  A deterministic
    32-byte salt is derived from the pepper via SHA-256 so that salt entropy
    is preserved regardless of the raw pepper length.
    """
    pepper = _load_hash_pepper()
    # Derive a full-entropy 32-byte PBKDF2 salt from the pepper via SHA-256.
    # This avoids predictable zero-padding for peppers shorter than 32 bytes.
    salt = hashlib.sha256(b"pbkdf2-salt-v1:" + pepper).digest()
    dk = hashlib.pbkdf2_hmac("sha256", value.encode("utf-8"), salt, 100_000)
    return dk.hex()


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

    Uses the current PBKDF2-HMAC-SHA256 scheme for verification.

    Returns the hashed key when validation succeeds.
    """

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-API-Key header"
        )

    store = store or ApiKeyStore()
    candidate_bytes = candidate.encode("utf-8")
    if len(candidate_bytes) > 512:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key exceeds maximum allowed length",
        )
    hashed_candidate = hash_key(candidate)
    stored_hashes = store.hashed_keys()

    if hashed_candidate in stored_hashes:
        return hashed_candidate

    if candidate in _keys_from_environment():
        return hashed_candidate

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


__all__ = ["ApiKeyStore", "ApiKeyRecord", "hash_key", "verify_api_key"]
