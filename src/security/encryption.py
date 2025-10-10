"""Lightweight authenticated encryption utilities for configuration secrets."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os

from .core import SecurityError


def derive_key(secret: str) -> bytes:
    return hashlib.sha256(secret.encode("utf-8")).digest()


def _keystream(key: bytes, nonce: bytes, length: int) -> bytes:
    stream = b""
    counter = 0
    while len(stream) < length:
        counter_bytes = counter.to_bytes(4, "big")
        stream += hashlib.sha256(key + nonce + counter_bytes).digest()
        counter += 1
    return stream[:length]


def encrypt_message(key: bytes, plaintext: str) -> str:
    if not plaintext:
        raise SecurityError("plaintext must be non-empty")
    nonce = os.urandom(16)
    data = plaintext.encode("utf-8")
    keystream = _keystream(key, nonce, len(data))
    ciphertext = bytes(a ^ b for a, b in zip(data, keystream, strict=True))
    mac = hmac.new(key, nonce + ciphertext, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(nonce + ciphertext + mac).decode("utf-8")


def decrypt_message(key: bytes, token: str) -> str:
    raw = base64.urlsafe_b64decode(token.encode("utf-8"))
    if len(raw) < 16 + hashlib.sha256().digest_size:
        raise SecurityError("token too short")
    nonce = raw[:16]
    mac_start = len(raw) - hashlib.sha256().digest_size
    ciphertext = raw[16:mac_start]
    mac = raw[mac_start:]
    expected_mac = hmac.new(key, nonce + ciphertext, hashlib.sha256).digest()
    if not hmac.compare_digest(mac, expected_mac):
        raise SecurityError("invalid authentication tag")
    keystream = _keystream(key, nonce, len(ciphertext))
    plaintext = bytes(a ^ b for a, b in zip(ciphertext, keystream, strict=True))
    return plaintext.decode("utf-8")
