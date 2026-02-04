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
import logging
logger = logging.getLogger(__name__)

import base64
import os
from typing import cast

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    _CRYPTO_AVAILABLE = True
except Exception:  # pragma: no cover
    _CRYPTO_AVAILABLE = False


NONCE_SIZE = 12  # AESGCM standard nonce size
KEY_SIZE = 32  # 256-bit
BYTE_TYPES = (bytes, bytearray)
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


class EncryptionError(Exception):
    """Exception raised for encryption/decryption errors."""
    
    def xǁEncryptionErrorǁ__init____mutmut_orig(self, message: str):
        self.message = message
        super().__init__(message)
    
    def xǁEncryptionErrorǁ__init____mutmut_1(self, message: str):
        self.message = None
        super().__init__(message)
    
    def xǁEncryptionErrorǁ__init____mutmut_2(self, message: str):
        self.message = message
        super().__init__(None)
    
    xǁEncryptionErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁEncryptionErrorǁ__init____mutmut_1': xǁEncryptionErrorǁ__init____mutmut_1, 
        'xǁEncryptionErrorǁ__init____mutmut_2': xǁEncryptionErrorǁ__init____mutmut_2
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁEncryptionErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁEncryptionErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁEncryptionErrorǁ__init____mutmut_orig)
    xǁEncryptionErrorǁ__init____mutmut_orig.__name__ = 'xǁEncryptionErrorǁ__init__'


def x__coerce_bytes__mutmut_orig(value: bytes | bytearray, *, name: str) -> bytes:
    if not isinstance(value, BYTE_TYPES):
        raise EncryptionError(f"{name} must be bytes")
    return bytes(value)


def x__coerce_bytes__mutmut_1(value: bytes | bytearray, *, name: str) -> bytes:
    if isinstance(value, BYTE_TYPES):
        raise EncryptionError(f"{name} must be bytes")
    return bytes(value)


def x__coerce_bytes__mutmut_2(value: bytes | bytearray, *, name: str) -> bytes:
    if not isinstance(value, BYTE_TYPES):
        raise EncryptionError(None)
    return bytes(value)


def x__coerce_bytes__mutmut_3(value: bytes | bytearray, *, name: str) -> bytes:
    if not isinstance(value, BYTE_TYPES):
        raise EncryptionError(f"{name} must be bytes")
    return bytes(None)

x__coerce_bytes__mutmut_mutants : ClassVar[MutantDict] = {
'x__coerce_bytes__mutmut_1': x__coerce_bytes__mutmut_1, 
    'x__coerce_bytes__mutmut_2': x__coerce_bytes__mutmut_2, 
    'x__coerce_bytes__mutmut_3': x__coerce_bytes__mutmut_3
}

def _coerce_bytes(*args, **kwargs):
    result = _mutmut_trampoline(x__coerce_bytes__mutmut_orig, x__coerce_bytes__mutmut_mutants, args, kwargs)
    return result 

_coerce_bytes.__signature__ = _mutmut_signature(x__coerce_bytes__mutmut_orig)
x__coerce_bytes__mutmut_orig.__name__ = 'x__coerce_bytes'


def x_generate_key__mutmut_orig() -> bytes:
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    return cast(bytes, AESGCM.generate_key(bit_length=KEY_SIZE * 8))


def x_generate_key__mutmut_1() -> bytes:
    if _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    return cast(bytes, AESGCM.generate_key(bit_length=KEY_SIZE * 8))


def x_generate_key__mutmut_2() -> bytes:
    if not _CRYPTO_AVAILABLE:
        raise ImportError(None)
    return cast(bytes, AESGCM.generate_key(bit_length=KEY_SIZE * 8))


def x_generate_key__mutmut_3() -> bytes:
    if not _CRYPTO_AVAILABLE:
        raise ImportError("XXcryptography is not availableXX")
    return cast(bytes, AESGCM.generate_key(bit_length=KEY_SIZE * 8))


def x_generate_key__mutmut_4() -> bytes:
    if not _CRYPTO_AVAILABLE:
        raise ImportError("CRYPTOGRAPHY IS NOT AVAILABLE")
    return cast(bytes, AESGCM.generate_key(bit_length=KEY_SIZE * 8))


def x_generate_key__mutmut_5() -> bytes:
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    return cast(None, AESGCM.generate_key(bit_length=KEY_SIZE * 8))


def x_generate_key__mutmut_6() -> bytes:
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    return cast(bytes, None)


def x_generate_key__mutmut_7() -> bytes:
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    return cast(AESGCM.generate_key(bit_length=KEY_SIZE * 8))


def x_generate_key__mutmut_8() -> bytes:
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    return cast(bytes, )


def x_generate_key__mutmut_9() -> bytes:
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    return cast(bytes, AESGCM.generate_key(bit_length=None))


def x_generate_key__mutmut_10() -> bytes:
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    return cast(bytes, AESGCM.generate_key(bit_length=KEY_SIZE / 8))


def x_generate_key__mutmut_11() -> bytes:
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    return cast(bytes, AESGCM.generate_key(bit_length=KEY_SIZE * 9))

x_generate_key__mutmut_mutants : ClassVar[MutantDict] = {
'x_generate_key__mutmut_1': x_generate_key__mutmut_1, 
    'x_generate_key__mutmut_2': x_generate_key__mutmut_2, 
    'x_generate_key__mutmut_3': x_generate_key__mutmut_3, 
    'x_generate_key__mutmut_4': x_generate_key__mutmut_4, 
    'x_generate_key__mutmut_5': x_generate_key__mutmut_5, 
    'x_generate_key__mutmut_6': x_generate_key__mutmut_6, 
    'x_generate_key__mutmut_7': x_generate_key__mutmut_7, 
    'x_generate_key__mutmut_8': x_generate_key__mutmut_8, 
    'x_generate_key__mutmut_9': x_generate_key__mutmut_9, 
    'x_generate_key__mutmut_10': x_generate_key__mutmut_10, 
    'x_generate_key__mutmut_11': x_generate_key__mutmut_11
}

def generate_key(*args, **kwargs):
    result = _mutmut_trampoline(x_generate_key__mutmut_orig, x_generate_key__mutmut_mutants, args, kwargs)
    return result 

generate_key.__signature__ = _mutmut_signature(x_generate_key__mutmut_orig)
x_generate_key__mutmut_orig.__name__ = 'x_generate_key'


def x_encrypt__mutmut_orig(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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


def x_encrypt__mutmut_1(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Encrypt plaintext using AES-256-GCM. Returns base64-encoded bytes containing nonce+ciphertext.
    Format: base64(nonce || ciphertext)
    """
    if _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    pt = _coerce_bytes(plaintext, name="plaintext")
    key_bytes = _coerce_bytes(key, name="key")
    if len(key_bytes) != KEY_SIZE:
        raise EncryptionError("key must be 32 bytes")

    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key_bytes)
    ct = cast(bytes, aesgcm.encrypt(nonce, pt, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_2(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Encrypt plaintext using AES-256-GCM. Returns base64-encoded bytes containing nonce+ciphertext.
    Format: base64(nonce || ciphertext)
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError(None)
    pt = _coerce_bytes(plaintext, name="plaintext")
    key_bytes = _coerce_bytes(key, name="key")
    if len(key_bytes) != KEY_SIZE:
        raise EncryptionError("key must be 32 bytes")

    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key_bytes)
    ct = cast(bytes, aesgcm.encrypt(nonce, pt, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_3(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Encrypt plaintext using AES-256-GCM. Returns base64-encoded bytes containing nonce+ciphertext.
    Format: base64(nonce || ciphertext)
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("XXcryptography is not availableXX")
    pt = _coerce_bytes(plaintext, name="plaintext")
    key_bytes = _coerce_bytes(key, name="key")
    if len(key_bytes) != KEY_SIZE:
        raise EncryptionError("key must be 32 bytes")

    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key_bytes)
    ct = cast(bytes, aesgcm.encrypt(nonce, pt, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_4(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Encrypt plaintext using AES-256-GCM. Returns base64-encoded bytes containing nonce+ciphertext.
    Format: base64(nonce || ciphertext)
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("CRYPTOGRAPHY IS NOT AVAILABLE")
    pt = _coerce_bytes(plaintext, name="plaintext")
    key_bytes = _coerce_bytes(key, name="key")
    if len(key_bytes) != KEY_SIZE:
        raise EncryptionError("key must be 32 bytes")

    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key_bytes)
    ct = cast(bytes, aesgcm.encrypt(nonce, pt, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_5(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Encrypt plaintext using AES-256-GCM. Returns base64-encoded bytes containing nonce+ciphertext.
    Format: base64(nonce || ciphertext)
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    pt = None
    key_bytes = _coerce_bytes(key, name="key")
    if len(key_bytes) != KEY_SIZE:
        raise EncryptionError("key must be 32 bytes")

    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key_bytes)
    ct = cast(bytes, aesgcm.encrypt(nonce, pt, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_6(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Encrypt plaintext using AES-256-GCM. Returns base64-encoded bytes containing nonce+ciphertext.
    Format: base64(nonce || ciphertext)
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    pt = _coerce_bytes(None, name="plaintext")
    key_bytes = _coerce_bytes(key, name="key")
    if len(key_bytes) != KEY_SIZE:
        raise EncryptionError("key must be 32 bytes")

    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key_bytes)
    ct = cast(bytes, aesgcm.encrypt(nonce, pt, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_7(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Encrypt plaintext using AES-256-GCM. Returns base64-encoded bytes containing nonce+ciphertext.
    Format: base64(nonce || ciphertext)
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    pt = _coerce_bytes(plaintext, name=None)
    key_bytes = _coerce_bytes(key, name="key")
    if len(key_bytes) != KEY_SIZE:
        raise EncryptionError("key must be 32 bytes")

    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key_bytes)
    ct = cast(bytes, aesgcm.encrypt(nonce, pt, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_8(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Encrypt plaintext using AES-256-GCM. Returns base64-encoded bytes containing nonce+ciphertext.
    Format: base64(nonce || ciphertext)
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    pt = _coerce_bytes(name="plaintext")
    key_bytes = _coerce_bytes(key, name="key")
    if len(key_bytes) != KEY_SIZE:
        raise EncryptionError("key must be 32 bytes")

    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key_bytes)
    ct = cast(bytes, aesgcm.encrypt(nonce, pt, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_9(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Encrypt plaintext using AES-256-GCM. Returns base64-encoded bytes containing nonce+ciphertext.
    Format: base64(nonce || ciphertext)
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    pt = _coerce_bytes(plaintext, )
    key_bytes = _coerce_bytes(key, name="key")
    if len(key_bytes) != KEY_SIZE:
        raise EncryptionError("key must be 32 bytes")

    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key_bytes)
    ct = cast(bytes, aesgcm.encrypt(nonce, pt, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_10(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Encrypt plaintext using AES-256-GCM. Returns base64-encoded bytes containing nonce+ciphertext.
    Format: base64(nonce || ciphertext)
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    pt = _coerce_bytes(plaintext, name="XXplaintextXX")
    key_bytes = _coerce_bytes(key, name="key")
    if len(key_bytes) != KEY_SIZE:
        raise EncryptionError("key must be 32 bytes")

    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key_bytes)
    ct = cast(bytes, aesgcm.encrypt(nonce, pt, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_11(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Encrypt plaintext using AES-256-GCM. Returns base64-encoded bytes containing nonce+ciphertext.
    Format: base64(nonce || ciphertext)
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    pt = _coerce_bytes(plaintext, name="PLAINTEXT")
    key_bytes = _coerce_bytes(key, name="key")
    if len(key_bytes) != KEY_SIZE:
        raise EncryptionError("key must be 32 bytes")

    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key_bytes)
    ct = cast(bytes, aesgcm.encrypt(nonce, pt, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_12(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Encrypt plaintext using AES-256-GCM. Returns base64-encoded bytes containing nonce+ciphertext.
    Format: base64(nonce || ciphertext)
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    pt = _coerce_bytes(plaintext, name="plaintext")
    key_bytes = None
    if len(key_bytes) != KEY_SIZE:
        raise EncryptionError("key must be 32 bytes")

    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key_bytes)
    ct = cast(bytes, aesgcm.encrypt(nonce, pt, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_13(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Encrypt plaintext using AES-256-GCM. Returns base64-encoded bytes containing nonce+ciphertext.
    Format: base64(nonce || ciphertext)
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    pt = _coerce_bytes(plaintext, name="plaintext")
    key_bytes = _coerce_bytes(None, name="key")
    if len(key_bytes) != KEY_SIZE:
        raise EncryptionError("key must be 32 bytes")

    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key_bytes)
    ct = cast(bytes, aesgcm.encrypt(nonce, pt, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_14(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Encrypt plaintext using AES-256-GCM. Returns base64-encoded bytes containing nonce+ciphertext.
    Format: base64(nonce || ciphertext)
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    pt = _coerce_bytes(plaintext, name="plaintext")
    key_bytes = _coerce_bytes(key, name=None)
    if len(key_bytes) != KEY_SIZE:
        raise EncryptionError("key must be 32 bytes")

    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key_bytes)
    ct = cast(bytes, aesgcm.encrypt(nonce, pt, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_15(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Encrypt plaintext using AES-256-GCM. Returns base64-encoded bytes containing nonce+ciphertext.
    Format: base64(nonce || ciphertext)
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    pt = _coerce_bytes(plaintext, name="plaintext")
    key_bytes = _coerce_bytes(name="key")
    if len(key_bytes) != KEY_SIZE:
        raise EncryptionError("key must be 32 bytes")

    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key_bytes)
    ct = cast(bytes, aesgcm.encrypt(nonce, pt, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_16(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Encrypt plaintext using AES-256-GCM. Returns base64-encoded bytes containing nonce+ciphertext.
    Format: base64(nonce || ciphertext)
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    pt = _coerce_bytes(plaintext, name="plaintext")
    key_bytes = _coerce_bytes(key, )
    if len(key_bytes) != KEY_SIZE:
        raise EncryptionError("key must be 32 bytes")

    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key_bytes)
    ct = cast(bytes, aesgcm.encrypt(nonce, pt, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_17(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Encrypt plaintext using AES-256-GCM. Returns base64-encoded bytes containing nonce+ciphertext.
    Format: base64(nonce || ciphertext)
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    pt = _coerce_bytes(plaintext, name="plaintext")
    key_bytes = _coerce_bytes(key, name="XXkeyXX")
    if len(key_bytes) != KEY_SIZE:
        raise EncryptionError("key must be 32 bytes")

    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key_bytes)
    ct = cast(bytes, aesgcm.encrypt(nonce, pt, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_18(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Encrypt plaintext using AES-256-GCM. Returns base64-encoded bytes containing nonce+ciphertext.
    Format: base64(nonce || ciphertext)
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    pt = _coerce_bytes(plaintext, name="plaintext")
    key_bytes = _coerce_bytes(key, name="KEY")
    if len(key_bytes) != KEY_SIZE:
        raise EncryptionError("key must be 32 bytes")

    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key_bytes)
    ct = cast(bytes, aesgcm.encrypt(nonce, pt, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_19(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Encrypt plaintext using AES-256-GCM. Returns base64-encoded bytes containing nonce+ciphertext.
    Format: base64(nonce || ciphertext)
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    pt = _coerce_bytes(plaintext, name="plaintext")
    key_bytes = _coerce_bytes(key, name="key")
    if len(key_bytes) == KEY_SIZE:
        raise EncryptionError("key must be 32 bytes")

    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key_bytes)
    ct = cast(bytes, aesgcm.encrypt(nonce, pt, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_20(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Encrypt plaintext using AES-256-GCM. Returns base64-encoded bytes containing nonce+ciphertext.
    Format: base64(nonce || ciphertext)
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    pt = _coerce_bytes(plaintext, name="plaintext")
    key_bytes = _coerce_bytes(key, name="key")
    if len(key_bytes) != KEY_SIZE:
        raise EncryptionError(None)

    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key_bytes)
    ct = cast(bytes, aesgcm.encrypt(nonce, pt, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_21(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Encrypt plaintext using AES-256-GCM. Returns base64-encoded bytes containing nonce+ciphertext.
    Format: base64(nonce || ciphertext)
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    pt = _coerce_bytes(plaintext, name="plaintext")
    key_bytes = _coerce_bytes(key, name="key")
    if len(key_bytes) != KEY_SIZE:
        raise EncryptionError("XXkey must be 32 bytesXX")

    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key_bytes)
    ct = cast(bytes, aesgcm.encrypt(nonce, pt, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_22(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Encrypt plaintext using AES-256-GCM. Returns base64-encoded bytes containing nonce+ciphertext.
    Format: base64(nonce || ciphertext)
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    pt = _coerce_bytes(plaintext, name="plaintext")
    key_bytes = _coerce_bytes(key, name="key")
    if len(key_bytes) != KEY_SIZE:
        raise EncryptionError("KEY MUST BE 32 BYTES")

    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key_bytes)
    ct = cast(bytes, aesgcm.encrypt(nonce, pt, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_23(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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

    nonce = None
    aesgcm = AESGCM(key_bytes)
    ct = cast(bytes, aesgcm.encrypt(nonce, pt, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_24(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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

    nonce = os.urandom(None)
    aesgcm = AESGCM(key_bytes)
    ct = cast(bytes, aesgcm.encrypt(nonce, pt, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_25(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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
    aesgcm = None
    ct = cast(bytes, aesgcm.encrypt(nonce, pt, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_26(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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
    aesgcm = AESGCM(None)
    ct = cast(bytes, aesgcm.encrypt(nonce, pt, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_27(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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
    ct = None
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_28(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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
    ct = cast(None, aesgcm.encrypt(nonce, pt, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_29(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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
    ct = cast(bytes, None)
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_30(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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
    ct = cast(aesgcm.encrypt(nonce, pt, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_31(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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
    ct = cast(bytes, )
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_32(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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
    ct = cast(bytes, aesgcm.encrypt(None, pt, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_33(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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
    ct = cast(bytes, aesgcm.encrypt(nonce, None, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_34(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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
    ct = cast(bytes, aesgcm.encrypt(nonce, pt, None))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_35(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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
    ct = cast(bytes, aesgcm.encrypt(pt, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_36(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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
    ct = cast(bytes, aesgcm.encrypt(nonce, aad))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_37(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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
    ct = cast(bytes, aesgcm.encrypt(nonce, pt, ))
    return base64.b64encode(nonce + ct)


def x_encrypt__mutmut_38(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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
    return base64.b64encode(None)


def x_encrypt__mutmut_39(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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
    return base64.b64encode(nonce - ct)

x_encrypt__mutmut_mutants : ClassVar[MutantDict] = {
'x_encrypt__mutmut_1': x_encrypt__mutmut_1, 
    'x_encrypt__mutmut_2': x_encrypt__mutmut_2, 
    'x_encrypt__mutmut_3': x_encrypt__mutmut_3, 
    'x_encrypt__mutmut_4': x_encrypt__mutmut_4, 
    'x_encrypt__mutmut_5': x_encrypt__mutmut_5, 
    'x_encrypt__mutmut_6': x_encrypt__mutmut_6, 
    'x_encrypt__mutmut_7': x_encrypt__mutmut_7, 
    'x_encrypt__mutmut_8': x_encrypt__mutmut_8, 
    'x_encrypt__mutmut_9': x_encrypt__mutmut_9, 
    'x_encrypt__mutmut_10': x_encrypt__mutmut_10, 
    'x_encrypt__mutmut_11': x_encrypt__mutmut_11, 
    'x_encrypt__mutmut_12': x_encrypt__mutmut_12, 
    'x_encrypt__mutmut_13': x_encrypt__mutmut_13, 
    'x_encrypt__mutmut_14': x_encrypt__mutmut_14, 
    'x_encrypt__mutmut_15': x_encrypt__mutmut_15, 
    'x_encrypt__mutmut_16': x_encrypt__mutmut_16, 
    'x_encrypt__mutmut_17': x_encrypt__mutmut_17, 
    'x_encrypt__mutmut_18': x_encrypt__mutmut_18, 
    'x_encrypt__mutmut_19': x_encrypt__mutmut_19, 
    'x_encrypt__mutmut_20': x_encrypt__mutmut_20, 
    'x_encrypt__mutmut_21': x_encrypt__mutmut_21, 
    'x_encrypt__mutmut_22': x_encrypt__mutmut_22, 
    'x_encrypt__mutmut_23': x_encrypt__mutmut_23, 
    'x_encrypt__mutmut_24': x_encrypt__mutmut_24, 
    'x_encrypt__mutmut_25': x_encrypt__mutmut_25, 
    'x_encrypt__mutmut_26': x_encrypt__mutmut_26, 
    'x_encrypt__mutmut_27': x_encrypt__mutmut_27, 
    'x_encrypt__mutmut_28': x_encrypt__mutmut_28, 
    'x_encrypt__mutmut_29': x_encrypt__mutmut_29, 
    'x_encrypt__mutmut_30': x_encrypt__mutmut_30, 
    'x_encrypt__mutmut_31': x_encrypt__mutmut_31, 
    'x_encrypt__mutmut_32': x_encrypt__mutmut_32, 
    'x_encrypt__mutmut_33': x_encrypt__mutmut_33, 
    'x_encrypt__mutmut_34': x_encrypt__mutmut_34, 
    'x_encrypt__mutmut_35': x_encrypt__mutmut_35, 
    'x_encrypt__mutmut_36': x_encrypt__mutmut_36, 
    'x_encrypt__mutmut_37': x_encrypt__mutmut_37, 
    'x_encrypt__mutmut_38': x_encrypt__mutmut_38, 
    'x_encrypt__mutmut_39': x_encrypt__mutmut_39
}

def encrypt(*args, **kwargs):
    result = _mutmut_trampoline(x_encrypt__mutmut_orig, x_encrypt__mutmut_mutants, args, kwargs)
    return result 

encrypt.__signature__ = _mutmut_signature(x_encrypt__mutmut_orig)
x_encrypt__mutmut_orig.__name__ = 'x_encrypt'


def x_decrypt__mutmut_orig(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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


def x_decrypt__mutmut_1(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Decrypt base64-encoded token produced by encrypt(). Returns plaintext bytes.
    """
    if _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    raw = base64.b64decode(token)
    if len(raw) <= NONCE_SIZE:
        raise EncryptionError("ciphertext too short")
    nonce, ct = raw[:NONCE_SIZE], raw[NONCE_SIZE:]
    key_bytes = _coerce_bytes(key, name="key")
    aesgcm = AESGCM(key_bytes)
    return cast(bytes, aesgcm.decrypt(nonce, ct, aad))


def x_decrypt__mutmut_2(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Decrypt base64-encoded token produced by encrypt(). Returns plaintext bytes.
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError(None)
    raw = base64.b64decode(token)
    if len(raw) <= NONCE_SIZE:
        raise EncryptionError("ciphertext too short")
    nonce, ct = raw[:NONCE_SIZE], raw[NONCE_SIZE:]
    key_bytes = _coerce_bytes(key, name="key")
    aesgcm = AESGCM(key_bytes)
    return cast(bytes, aesgcm.decrypt(nonce, ct, aad))


def x_decrypt__mutmut_3(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Decrypt base64-encoded token produced by encrypt(). Returns plaintext bytes.
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("XXcryptography is not availableXX")
    raw = base64.b64decode(token)
    if len(raw) <= NONCE_SIZE:
        raise EncryptionError("ciphertext too short")
    nonce, ct = raw[:NONCE_SIZE], raw[NONCE_SIZE:]
    key_bytes = _coerce_bytes(key, name="key")
    aesgcm = AESGCM(key_bytes)
    return cast(bytes, aesgcm.decrypt(nonce, ct, aad))


def x_decrypt__mutmut_4(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Decrypt base64-encoded token produced by encrypt(). Returns plaintext bytes.
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("CRYPTOGRAPHY IS NOT AVAILABLE")
    raw = base64.b64decode(token)
    if len(raw) <= NONCE_SIZE:
        raise EncryptionError("ciphertext too short")
    nonce, ct = raw[:NONCE_SIZE], raw[NONCE_SIZE:]
    key_bytes = _coerce_bytes(key, name="key")
    aesgcm = AESGCM(key_bytes)
    return cast(bytes, aesgcm.decrypt(nonce, ct, aad))


def x_decrypt__mutmut_5(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Decrypt base64-encoded token produced by encrypt(). Returns plaintext bytes.
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    raw = None
    if len(raw) <= NONCE_SIZE:
        raise EncryptionError("ciphertext too short")
    nonce, ct = raw[:NONCE_SIZE], raw[NONCE_SIZE:]
    key_bytes = _coerce_bytes(key, name="key")
    aesgcm = AESGCM(key_bytes)
    return cast(bytes, aesgcm.decrypt(nonce, ct, aad))


def x_decrypt__mutmut_6(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Decrypt base64-encoded token produced by encrypt(). Returns plaintext bytes.
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    raw = base64.b64decode(None)
    if len(raw) <= NONCE_SIZE:
        raise EncryptionError("ciphertext too short")
    nonce, ct = raw[:NONCE_SIZE], raw[NONCE_SIZE:]
    key_bytes = _coerce_bytes(key, name="key")
    aesgcm = AESGCM(key_bytes)
    return cast(bytes, aesgcm.decrypt(nonce, ct, aad))


def x_decrypt__mutmut_7(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Decrypt base64-encoded token produced by encrypt(). Returns plaintext bytes.
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    raw = base64.b64decode(token)
    if len(raw) < NONCE_SIZE:
        raise EncryptionError("ciphertext too short")
    nonce, ct = raw[:NONCE_SIZE], raw[NONCE_SIZE:]
    key_bytes = _coerce_bytes(key, name="key")
    aesgcm = AESGCM(key_bytes)
    return cast(bytes, aesgcm.decrypt(nonce, ct, aad))


def x_decrypt__mutmut_8(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Decrypt base64-encoded token produced by encrypt(). Returns plaintext bytes.
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    raw = base64.b64decode(token)
    if len(raw) <= NONCE_SIZE:
        raise EncryptionError(None)
    nonce, ct = raw[:NONCE_SIZE], raw[NONCE_SIZE:]
    key_bytes = _coerce_bytes(key, name="key")
    aesgcm = AESGCM(key_bytes)
    return cast(bytes, aesgcm.decrypt(nonce, ct, aad))


def x_decrypt__mutmut_9(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Decrypt base64-encoded token produced by encrypt(). Returns plaintext bytes.
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    raw = base64.b64decode(token)
    if len(raw) <= NONCE_SIZE:
        raise EncryptionError("XXciphertext too shortXX")
    nonce, ct = raw[:NONCE_SIZE], raw[NONCE_SIZE:]
    key_bytes = _coerce_bytes(key, name="key")
    aesgcm = AESGCM(key_bytes)
    return cast(bytes, aesgcm.decrypt(nonce, ct, aad))


def x_decrypt__mutmut_10(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Decrypt base64-encoded token produced by encrypt(). Returns plaintext bytes.
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    raw = base64.b64decode(token)
    if len(raw) <= NONCE_SIZE:
        raise EncryptionError("CIPHERTEXT TOO SHORT")
    nonce, ct = raw[:NONCE_SIZE], raw[NONCE_SIZE:]
    key_bytes = _coerce_bytes(key, name="key")
    aesgcm = AESGCM(key_bytes)
    return cast(bytes, aesgcm.decrypt(nonce, ct, aad))


def x_decrypt__mutmut_11(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Decrypt base64-encoded token produced by encrypt(). Returns plaintext bytes.
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    raw = base64.b64decode(token)
    if len(raw) <= NONCE_SIZE:
        raise EncryptionError("ciphertext too short")
    nonce, ct = None
    key_bytes = _coerce_bytes(key, name="key")
    aesgcm = AESGCM(key_bytes)
    return cast(bytes, aesgcm.decrypt(nonce, ct, aad))


def x_decrypt__mutmut_12(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Decrypt base64-encoded token produced by encrypt(). Returns plaintext bytes.
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    raw = base64.b64decode(token)
    if len(raw) <= NONCE_SIZE:
        raise EncryptionError("ciphertext too short")
    nonce, ct = raw[:NONCE_SIZE], raw[NONCE_SIZE:]
    key_bytes = None
    aesgcm = AESGCM(key_bytes)
    return cast(bytes, aesgcm.decrypt(nonce, ct, aad))


def x_decrypt__mutmut_13(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Decrypt base64-encoded token produced by encrypt(). Returns plaintext bytes.
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    raw = base64.b64decode(token)
    if len(raw) <= NONCE_SIZE:
        raise EncryptionError("ciphertext too short")
    nonce, ct = raw[:NONCE_SIZE], raw[NONCE_SIZE:]
    key_bytes = _coerce_bytes(None, name="key")
    aesgcm = AESGCM(key_bytes)
    return cast(bytes, aesgcm.decrypt(nonce, ct, aad))


def x_decrypt__mutmut_14(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Decrypt base64-encoded token produced by encrypt(). Returns plaintext bytes.
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    raw = base64.b64decode(token)
    if len(raw) <= NONCE_SIZE:
        raise EncryptionError("ciphertext too short")
    nonce, ct = raw[:NONCE_SIZE], raw[NONCE_SIZE:]
    key_bytes = _coerce_bytes(key, name=None)
    aesgcm = AESGCM(key_bytes)
    return cast(bytes, aesgcm.decrypt(nonce, ct, aad))


def x_decrypt__mutmut_15(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Decrypt base64-encoded token produced by encrypt(). Returns plaintext bytes.
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    raw = base64.b64decode(token)
    if len(raw) <= NONCE_SIZE:
        raise EncryptionError("ciphertext too short")
    nonce, ct = raw[:NONCE_SIZE], raw[NONCE_SIZE:]
    key_bytes = _coerce_bytes(name="key")
    aesgcm = AESGCM(key_bytes)
    return cast(bytes, aesgcm.decrypt(nonce, ct, aad))


def x_decrypt__mutmut_16(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Decrypt base64-encoded token produced by encrypt(). Returns plaintext bytes.
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    raw = base64.b64decode(token)
    if len(raw) <= NONCE_SIZE:
        raise EncryptionError("ciphertext too short")
    nonce, ct = raw[:NONCE_SIZE], raw[NONCE_SIZE:]
    key_bytes = _coerce_bytes(key, )
    aesgcm = AESGCM(key_bytes)
    return cast(bytes, aesgcm.decrypt(nonce, ct, aad))


def x_decrypt__mutmut_17(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Decrypt base64-encoded token produced by encrypt(). Returns plaintext bytes.
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    raw = base64.b64decode(token)
    if len(raw) <= NONCE_SIZE:
        raise EncryptionError("ciphertext too short")
    nonce, ct = raw[:NONCE_SIZE], raw[NONCE_SIZE:]
    key_bytes = _coerce_bytes(key, name="XXkeyXX")
    aesgcm = AESGCM(key_bytes)
    return cast(bytes, aesgcm.decrypt(nonce, ct, aad))


def x_decrypt__mutmut_18(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """
    Decrypt base64-encoded token produced by encrypt(). Returns plaintext bytes.
    """
    if not _CRYPTO_AVAILABLE:
        raise ImportError("cryptography is not available")
    raw = base64.b64decode(token)
    if len(raw) <= NONCE_SIZE:
        raise EncryptionError("ciphertext too short")
    nonce, ct = raw[:NONCE_SIZE], raw[NONCE_SIZE:]
    key_bytes = _coerce_bytes(key, name="KEY")
    aesgcm = AESGCM(key_bytes)
    return cast(bytes, aesgcm.decrypt(nonce, ct, aad))


def x_decrypt__mutmut_19(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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
    aesgcm = None
    return cast(bytes, aesgcm.decrypt(nonce, ct, aad))


def x_decrypt__mutmut_20(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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
    aesgcm = AESGCM(None)
    return cast(bytes, aesgcm.decrypt(nonce, ct, aad))


def x_decrypt__mutmut_21(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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
    return cast(None, aesgcm.decrypt(nonce, ct, aad))


def x_decrypt__mutmut_22(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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
    return cast(bytes, None)


def x_decrypt__mutmut_23(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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
    return cast(aesgcm.decrypt(nonce, ct, aad))


def x_decrypt__mutmut_24(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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
    return cast(bytes, )


def x_decrypt__mutmut_25(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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
    return cast(bytes, aesgcm.decrypt(None, ct, aad))


def x_decrypt__mutmut_26(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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
    return cast(bytes, aesgcm.decrypt(nonce, None, aad))


def x_decrypt__mutmut_27(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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
    return cast(bytes, aesgcm.decrypt(nonce, ct, None))


def x_decrypt__mutmut_28(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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
    return cast(bytes, aesgcm.decrypt(ct, aad))


def x_decrypt__mutmut_29(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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
    return cast(bytes, aesgcm.decrypt(nonce, aad))


def x_decrypt__mutmut_30(token: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
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
    return cast(bytes, aesgcm.decrypt(nonce, ct, ))

x_decrypt__mutmut_mutants : ClassVar[MutantDict] = {
'x_decrypt__mutmut_1': x_decrypt__mutmut_1, 
    'x_decrypt__mutmut_2': x_decrypt__mutmut_2, 
    'x_decrypt__mutmut_3': x_decrypt__mutmut_3, 
    'x_decrypt__mutmut_4': x_decrypt__mutmut_4, 
    'x_decrypt__mutmut_5': x_decrypt__mutmut_5, 
    'x_decrypt__mutmut_6': x_decrypt__mutmut_6, 
    'x_decrypt__mutmut_7': x_decrypt__mutmut_7, 
    'x_decrypt__mutmut_8': x_decrypt__mutmut_8, 
    'x_decrypt__mutmut_9': x_decrypt__mutmut_9, 
    'x_decrypt__mutmut_10': x_decrypt__mutmut_10, 
    'x_decrypt__mutmut_11': x_decrypt__mutmut_11, 
    'x_decrypt__mutmut_12': x_decrypt__mutmut_12, 
    'x_decrypt__mutmut_13': x_decrypt__mutmut_13, 
    'x_decrypt__mutmut_14': x_decrypt__mutmut_14, 
    'x_decrypt__mutmut_15': x_decrypt__mutmut_15, 
    'x_decrypt__mutmut_16': x_decrypt__mutmut_16, 
    'x_decrypt__mutmut_17': x_decrypt__mutmut_17, 
    'x_decrypt__mutmut_18': x_decrypt__mutmut_18, 
    'x_decrypt__mutmut_19': x_decrypt__mutmut_19, 
    'x_decrypt__mutmut_20': x_decrypt__mutmut_20, 
    'x_decrypt__mutmut_21': x_decrypt__mutmut_21, 
    'x_decrypt__mutmut_22': x_decrypt__mutmut_22, 
    'x_decrypt__mutmut_23': x_decrypt__mutmut_23, 
    'x_decrypt__mutmut_24': x_decrypt__mutmut_24, 
    'x_decrypt__mutmut_25': x_decrypt__mutmut_25, 
    'x_decrypt__mutmut_26': x_decrypt__mutmut_26, 
    'x_decrypt__mutmut_27': x_decrypt__mutmut_27, 
    'x_decrypt__mutmut_28': x_decrypt__mutmut_28, 
    'x_decrypt__mutmut_29': x_decrypt__mutmut_29, 
    'x_decrypt__mutmut_30': x_decrypt__mutmut_30
}

def decrypt(*args, **kwargs):
    result = _mutmut_trampoline(x_decrypt__mutmut_orig, x_decrypt__mutmut_mutants, args, kwargs)
    return result 

decrypt.__signature__ = _mutmut_signature(x_decrypt__mutmut_orig)
x_decrypt__mutmut_orig.__name__ = 'x_decrypt'
