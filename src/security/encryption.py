"""
Security Encryption Utilities (AES-256-GCM with optional dependency)

This module provides authenticated encryption helpers. It prefers the 'cryptography'
package; if unavailable, it raises ImportError and callers/tests should skip.

Usage:
    from src.security.encryption import encrypt, decrypt, generate_key

Notes:
- Offline & deterministic (random nonces per message).
- Avoids adding new hard runtime deps; optional import pattern.
"""
from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from typing import cast

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    _CRYPTO_AVAILABLE = True
except Exception:  # pragma: no cover
    _CRYPTO_AVAILABLE = False


NONCE_SIZE = 12  # AESGCM standard nonce size
KEY_SIZE = 32  # 256-bit
BYTE_TYPES = (bytes, bytearray)


@dataclass(frozen=True)
class EncryptionError(Exception):
    message: str


def _coerce_bytes(value: bytes | bytearray, *, name: str) -> bytes:
    if not isinstance(value, BYTE_TYPES):
        raise EncryptionError(f"{name} must be bytes")
    return bytes(value)


def generate_key() -> bytes:
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    return cast(bytes, AESGCM.generate_key(bit_length=KEY_SIZE * 8))


def encrypt(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Encrypt plaintext using AES-256-GCM. Returns base64-encoded bytes containing nonce+ciphertext.
    Format: base64(nonce || ciphertext)
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    pt = _coerce_bytes(plaintext, name="plaintext")
    key_bytes = _coerce_bytes(key, name="key")
    if len(key_bytes) != KEY_SIZE:
        raise EncryptionError("key must be 32 bytes")

    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key_bytes)
    ct = cast(bytes, aesgcm.encrypt(nonce, pt, aad))
    return base64.b64encode(nonce + ct)


def decrypt(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Decrypt base64-encoded token produced by encrypt(). Returns plaintext bytes.
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    raw = base64.b64decode(token)
    if len(raw) <= NONCE_SIZE:
        raise EncryptionError("ciphertext too short")
    nonce, ct = raw[:NONCE_SIZE], raw[NONCE_SIZE:]
    key_bytes = _coerce_bytes(key, name="key")
    aesgcm = AESGCM(key_bytes)
    return cast(bytes, aesgcm.decrypt(nonce, ct, aad))
