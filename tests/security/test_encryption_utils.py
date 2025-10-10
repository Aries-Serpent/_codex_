import pytest

from src.security import SecurityError, decrypt_message, derive_key, encrypt_message


def test_encrypt_decrypt_roundtrip() -> None:
    key = derive_key("secret")
    token = encrypt_message(key, "payload")
    assert decrypt_message(key, token) == "payload"


def test_decrypt_rejects_modified_token() -> None:
    key = derive_key("secret")
    token = encrypt_message(key, "payload")
    tampered = token[:-2] + "aa"
    with pytest.raises(SecurityError):
        decrypt_message(key, tampered)
