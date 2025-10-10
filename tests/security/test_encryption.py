#!/usr/bin/env python
# Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5
# Purpose: Validate AES-256-GCM encryption utilities if cryptography available.

from __future__ import annotations

import base64

import pytest

try:
    from cryptography.exceptions import InvalidTag  # type: ignore[import-not-found]
except Exception:  # pragma: no cover - cryptography optional
    InvalidTag = Exception  # type: ignore[misc,assignment]

try:
    import src.security.encryption as encryption_mod

    generate_key = encryption_mod.generate_key
    encrypt = encryption_mod.encrypt
    decrypt = encryption_mod.decrypt
    EncryptionError = encryption_mod.EncryptionError
    _CRYPTO_AVAILABLE = getattr(encryption_mod, "_CRYPTO_AVAILABLE", True)
except Exception:
    _CRYPTO_AVAILABLE = False


pytestmark = pytest.mark.skipif(not _CRYPTO_AVAILABLE, reason="cryptography not installed")


def test_encryption_roundtrip_plaintext_bytes():
    key = generate_key()
    pt = b"hello-world"
    token = encrypt(pt, key)
    out = decrypt(token, key)
    assert out == pt


def test_encryption_different_nonces_produce_different_tokens():
    key = generate_key()
    pt = b"A" * 32
    t1 = encrypt(pt, key)
    t2 = encrypt(pt, key)
    assert t1 != t2  # probabilistic, but overwhelmingly likely


def test_encryption_wrong_key_fails():
    key1 = generate_key()
    key2 = generate_key()
    token = encrypt(b"secret", key1)
    with pytest.raises(InvalidTag):
        _ = decrypt(token, key2)


def test_encryption_input_validation():
    key = generate_key()
    with pytest.raises(EncryptionError):
        encrypt("not-bytes", key)  # type: ignore
    with pytest.raises(EncryptionError):
        decrypt(base64.b64encode(b"short"), key)
