"""Utility helpers for the Codex archival workflow."""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

import datetime as _dt
import hashlib
import json
import os
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

try:  # pragma: no cover - optional dependency
    import zstandard as _zstd  # type: ignore
except Exception:  # pragma: no cover - best-effort fallback
    _zstd = None

import zlib

ISO_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
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


def x_utcnow__mutmut_orig() -> str:
    """Return a UTC timestamp truncated to seconds."""

    return _dt.datetime.now(_dt.UTC).replace(microsecond=0).strftime(ISO_FORMAT)


def x_utcnow__mutmut_1() -> str:
    """Return a UTC timestamp truncated to seconds."""

    return _dt.datetime.now(_dt.UTC).replace(microsecond=0).strftime(None)


def x_utcnow__mutmut_2() -> str:
    """Return a UTC timestamp truncated to seconds."""

    return _dt.datetime.now(_dt.UTC).replace(microsecond=None).strftime(ISO_FORMAT)


def x_utcnow__mutmut_3() -> str:
    """Return a UTC timestamp truncated to seconds."""

    return _dt.datetime.now(None).replace(microsecond=0).strftime(ISO_FORMAT)


def x_utcnow__mutmut_4() -> str:
    """Return a UTC timestamp truncated to seconds."""

    return _dt.datetime.now(_dt.UTC).replace(microsecond=1).strftime(ISO_FORMAT)

x_utcnow__mutmut_mutants : ClassVar[MutantDict] = {
'x_utcnow__mutmut_1': x_utcnow__mutmut_1, 
    'x_utcnow__mutmut_2': x_utcnow__mutmut_2, 
    'x_utcnow__mutmut_3': x_utcnow__mutmut_3, 
    'x_utcnow__mutmut_4': x_utcnow__mutmut_4
}

def utcnow(*args, **kwargs):
    result = _mutmut_trampoline(x_utcnow__mutmut_orig, x_utcnow__mutmut_mutants, args, kwargs)
    return result 

utcnow.__signature__ = _mutmut_signature(x_utcnow__mutmut_orig)
x_utcnow__mutmut_orig.__name__ = 'x_utcnow'


def utcnow_iso() -> str:
    """Return a UTC timestamp (alias for compatibility)."""

    return utcnow()


def x_sha256_hex__mutmut_orig(data: bytes) -> str:
    """Return the SHA-256 hex digest for *data*."""

    digest = hashlib.sha256()
    digest.update(data)
    return digest.hexdigest()


def x_sha256_hex__mutmut_1(data: bytes) -> str:
    """Return the SHA-256 hex digest for *data*."""

    digest = None
    digest.update(data)
    return digest.hexdigest()


def x_sha256_hex__mutmut_2(data: bytes) -> str:
    """Return the SHA-256 hex digest for *data*."""

    digest = hashlib.sha256()
    digest.update(None)
    return digest.hexdigest()

x_sha256_hex__mutmut_mutants : ClassVar[MutantDict] = {
'x_sha256_hex__mutmut_1': x_sha256_hex__mutmut_1, 
    'x_sha256_hex__mutmut_2': x_sha256_hex__mutmut_2
}

def sha256_hex(*args, **kwargs):
    result = _mutmut_trampoline(x_sha256_hex__mutmut_orig, x_sha256_hex__mutmut_mutants, args, kwargs)
    return result 

sha256_hex.__signature__ = _mutmut_signature(x_sha256_hex__mutmut_orig)
x_sha256_hex__mutmut_orig.__name__ = 'x_sha256_hex'


def x_sha256_bytes__mutmut_orig(data: bytes) -> str:
    """Return the SHA-256 hex digest for *data* (alias helper)."""

    return hashlib.sha256(data).hexdigest()


def x_sha256_bytes__mutmut_1(data: bytes) -> str:
    """Return the SHA-256 hex digest for *data* (alias helper)."""

    return hashlib.sha256(None).hexdigest()

x_sha256_bytes__mutmut_mutants : ClassVar[MutantDict] = {
'x_sha256_bytes__mutmut_1': x_sha256_bytes__mutmut_1
}

def sha256_bytes(*args, **kwargs):
    result = _mutmut_trampoline(x_sha256_bytes__mutmut_orig, x_sha256_bytes__mutmut_mutants, args, kwargs)
    return result 

sha256_bytes.__signature__ = _mutmut_signature(x_sha256_bytes__mutmut_orig)
x_sha256_bytes__mutmut_orig.__name__ = 'x_sha256_bytes'


def x_sha256_file__mutmut_orig(path: Path) -> str:
    """Return the SHA-256 hex digest for the contents of *path* if it exists."""

    if not path.exists():
        return ""
    return sha256_bytes(path.read_bytes())


def x_sha256_file__mutmut_1(path: Path) -> str:
    """Return the SHA-256 hex digest for the contents of *path* if it exists."""

    if path.exists():
        return ""
    return sha256_bytes(path.read_bytes())


def x_sha256_file__mutmut_2(path: Path) -> str:
    """Return the SHA-256 hex digest for the contents of *path* if it exists."""

    if not path.exists():
        return "XXXX"
    return sha256_bytes(path.read_bytes())


def x_sha256_file__mutmut_3(path: Path) -> str:
    """Return the SHA-256 hex digest for the contents of *path* if it exists."""

    if not path.exists():
        return ""
    return sha256_bytes(None)

x_sha256_file__mutmut_mutants : ClassVar[MutantDict] = {
'x_sha256_file__mutmut_1': x_sha256_file__mutmut_1, 
    'x_sha256_file__mutmut_2': x_sha256_file__mutmut_2, 
    'x_sha256_file__mutmut_3': x_sha256_file__mutmut_3
}

def sha256_file(*args, **kwargs):
    result = _mutmut_trampoline(x_sha256_file__mutmut_orig, x_sha256_file__mutmut_mutants, args, kwargs)
    return result 

sha256_file.__signature__ = _mutmut_signature(x_sha256_file__mutmut_orig)
x_sha256_file__mutmut_orig.__name__ = 'x_sha256_file'


def x_zstd_compress__mutmut_orig(data: bytes, level: int = 9) -> bytes:
    """Compress *data* using zstandard if available, otherwise zlib."""

    if _zstd is not None:  # pragma: no branch - fast path
        compressor = _zstd.ZstdCompressor(level=level)
        return compressor.compress(data)
    # Fallback to deterministic zlib compression for environments without zstd.
    return zlib.compress(data, level)


def x_zstd_compress__mutmut_1(data: bytes, level: int = 10) -> bytes:
    """Compress *data* using zstandard if available, otherwise zlib."""

    if _zstd is not None:  # pragma: no branch - fast path
        compressor = _zstd.ZstdCompressor(level=level)
        return compressor.compress(data)
    # Fallback to deterministic zlib compression for environments without zstd.
    return zlib.compress(data, level)


def x_zstd_compress__mutmut_2(data: bytes, level: int = 9) -> bytes:
    """Compress *data* using zstandard if available, otherwise zlib."""

    if _zstd is None:  # pragma: no branch - fast path
        compressor = _zstd.ZstdCompressor(level=level)
        return compressor.compress(data)
    # Fallback to deterministic zlib compression for environments without zstd.
    return zlib.compress(data, level)


def x_zstd_compress__mutmut_3(data: bytes, level: int = 9) -> bytes:
    """Compress *data* using zstandard if available, otherwise zlib."""

    if _zstd is not None:  # pragma: no branch - fast path
        compressor = None
        return compressor.compress(data)
    # Fallback to deterministic zlib compression for environments without zstd.
    return zlib.compress(data, level)


def x_zstd_compress__mutmut_4(data: bytes, level: int = 9) -> bytes:
    """Compress *data* using zstandard if available, otherwise zlib."""

    if _zstd is not None:  # pragma: no branch - fast path
        compressor = _zstd.ZstdCompressor(level=None)
        return compressor.compress(data)
    # Fallback to deterministic zlib compression for environments without zstd.
    return zlib.compress(data, level)


def x_zstd_compress__mutmut_5(data: bytes, level: int = 9) -> bytes:
    """Compress *data* using zstandard if available, otherwise zlib."""

    if _zstd is not None:  # pragma: no branch - fast path
        compressor = _zstd.ZstdCompressor(level=level)
        return compressor.compress(None)
    # Fallback to deterministic zlib compression for environments without zstd.
    return zlib.compress(data, level)


def x_zstd_compress__mutmut_6(data: bytes, level: int = 9) -> bytes:
    """Compress *data* using zstandard if available, otherwise zlib."""

    if _zstd is not None:  # pragma: no branch - fast path
        compressor = _zstd.ZstdCompressor(level=level)
        return compressor.compress(data)
    # Fallback to deterministic zlib compression for environments without zstd.
    return zlib.compress(None, level)


def x_zstd_compress__mutmut_7(data: bytes, level: int = 9) -> bytes:
    """Compress *data* using zstandard if available, otherwise zlib."""

    if _zstd is not None:  # pragma: no branch - fast path
        compressor = _zstd.ZstdCompressor(level=level)
        return compressor.compress(data)
    # Fallback to deterministic zlib compression for environments without zstd.
    return zlib.compress(data, None)


def x_zstd_compress__mutmut_8(data: bytes, level: int = 9) -> bytes:
    """Compress *data* using zstandard if available, otherwise zlib."""

    if _zstd is not None:  # pragma: no branch - fast path
        compressor = _zstd.ZstdCompressor(level=level)
        return compressor.compress(data)
    # Fallback to deterministic zlib compression for environments without zstd.
    return zlib.compress(level)


def x_zstd_compress__mutmut_9(data: bytes, level: int = 9) -> bytes:
    """Compress *data* using zstandard if available, otherwise zlib."""

    if _zstd is not None:  # pragma: no branch - fast path
        compressor = _zstd.ZstdCompressor(level=level)
        return compressor.compress(data)
    # Fallback to deterministic zlib compression for environments without zstd.
    return zlib.compress(data, )

x_zstd_compress__mutmut_mutants : ClassVar[MutantDict] = {
'x_zstd_compress__mutmut_1': x_zstd_compress__mutmut_1, 
    'x_zstd_compress__mutmut_2': x_zstd_compress__mutmut_2, 
    'x_zstd_compress__mutmut_3': x_zstd_compress__mutmut_3, 
    'x_zstd_compress__mutmut_4': x_zstd_compress__mutmut_4, 
    'x_zstd_compress__mutmut_5': x_zstd_compress__mutmut_5, 
    'x_zstd_compress__mutmut_6': x_zstd_compress__mutmut_6, 
    'x_zstd_compress__mutmut_7': x_zstd_compress__mutmut_7, 
    'x_zstd_compress__mutmut_8': x_zstd_compress__mutmut_8, 
    'x_zstd_compress__mutmut_9': x_zstd_compress__mutmut_9
}

def zstd_compress(*args, **kwargs):
    result = _mutmut_trampoline(x_zstd_compress__mutmut_orig, x_zstd_compress__mutmut_mutants, args, kwargs)
    return result 

zstd_compress.__signature__ = _mutmut_signature(x_zstd_compress__mutmut_orig)
x_zstd_compress__mutmut_orig.__name__ = 'x_zstd_compress'


def x_zlib_compress__mutmut_orig(data: bytes, level: int = 9) -> bytes:
    """Explicit zlib compression helper used by legacy APIs."""

    return zlib.compress(data, level)


def x_zlib_compress__mutmut_1(data: bytes, level: int = 10) -> bytes:
    """Explicit zlib compression helper used by legacy APIs."""

    return zlib.compress(data, level)


def x_zlib_compress__mutmut_2(data: bytes, level: int = 9) -> bytes:
    """Explicit zlib compression helper used by legacy APIs."""

    return zlib.compress(None, level)


def x_zlib_compress__mutmut_3(data: bytes, level: int = 9) -> bytes:
    """Explicit zlib compression helper used by legacy APIs."""

    return zlib.compress(data, None)


def x_zlib_compress__mutmut_4(data: bytes, level: int = 9) -> bytes:
    """Explicit zlib compression helper used by legacy APIs."""

    return zlib.compress(level)


def x_zlib_compress__mutmut_5(data: bytes, level: int = 9) -> bytes:
    """Explicit zlib compression helper used by legacy APIs."""

    return zlib.compress(data, )

x_zlib_compress__mutmut_mutants : ClassVar[MutantDict] = {
'x_zlib_compress__mutmut_1': x_zlib_compress__mutmut_1, 
    'x_zlib_compress__mutmut_2': x_zlib_compress__mutmut_2, 
    'x_zlib_compress__mutmut_3': x_zlib_compress__mutmut_3, 
    'x_zlib_compress__mutmut_4': x_zlib_compress__mutmut_4, 
    'x_zlib_compress__mutmut_5': x_zlib_compress__mutmut_5
}

def zlib_compress(*args, **kwargs):
    result = _mutmut_trampoline(x_zlib_compress__mutmut_orig, x_zlib_compress__mutmut_mutants, args, kwargs)
    return result 

zlib_compress.__signature__ = _mutmut_signature(x_zlib_compress__mutmut_orig)
x_zlib_compress__mutmut_orig.__name__ = 'x_zlib_compress'


def x_zstd_decompress__mutmut_orig(data: bytes) -> bytes:
    """Inverse operation for :func:`zstd_compress`."""

    if _zstd is not None:  # pragma: no branch - fast path
        decompressor = _zstd.ZstdDecompressor()
        return decompressor.decompress(data)
    return zlib.decompress(data)


def x_zstd_decompress__mutmut_1(data: bytes) -> bytes:
    """Inverse operation for :func:`zstd_compress`."""

    if _zstd is None:  # pragma: no branch - fast path
        decompressor = _zstd.ZstdDecompressor()
        return decompressor.decompress(data)
    return zlib.decompress(data)


def x_zstd_decompress__mutmut_2(data: bytes) -> bytes:
    """Inverse operation for :func:`zstd_compress`."""

    if _zstd is not None:  # pragma: no branch - fast path
        decompressor = None
        return decompressor.decompress(data)
    return zlib.decompress(data)


def x_zstd_decompress__mutmut_3(data: bytes) -> bytes:
    """Inverse operation for :func:`zstd_compress`."""

    if _zstd is not None:  # pragma: no branch - fast path
        decompressor = _zstd.ZstdDecompressor()
        return decompressor.decompress(None)
    return zlib.decompress(data)


def x_zstd_decompress__mutmut_4(data: bytes) -> bytes:
    """Inverse operation for :func:`zstd_compress`."""

    if _zstd is not None:  # pragma: no branch - fast path
        decompressor = _zstd.ZstdDecompressor()
        return decompressor.decompress(data)
    return zlib.decompress(None)

x_zstd_decompress__mutmut_mutants : ClassVar[MutantDict] = {
'x_zstd_decompress__mutmut_1': x_zstd_decompress__mutmut_1, 
    'x_zstd_decompress__mutmut_2': x_zstd_decompress__mutmut_2, 
    'x_zstd_decompress__mutmut_3': x_zstd_decompress__mutmut_3, 
    'x_zstd_decompress__mutmut_4': x_zstd_decompress__mutmut_4
}

def zstd_decompress(*args, **kwargs):
    result = _mutmut_trampoline(x_zstd_decompress__mutmut_orig, x_zstd_decompress__mutmut_mutants, args, kwargs)
    return result 

zstd_decompress.__signature__ = _mutmut_signature(x_zstd_decompress__mutmut_orig)
x_zstd_decompress__mutmut_orig.__name__ = 'x_zstd_decompress'


def x_decompress_payload__mutmut_orig(data: bytes, codec: str) -> bytes:
    """Decompress *data* using the explicit *codec* identifier."""

    if codec == "zstd":
        if _zstd is None:
            raise RuntimeError("zstandard codec requested but python-zstandard is not available")
        decompressor = _zstd.ZstdDecompressor()
        return decompressor.decompress(data)
    if codec == "zlib":
        return zlib.decompress(data)
    raise ValueError(f"Unsupported compression codec: {codec}")


def x_decompress_payload__mutmut_1(data: bytes, codec: str) -> bytes:
    """Decompress *data* using the explicit *codec* identifier."""

    if codec != "zstd":
        if _zstd is None:
            raise RuntimeError("zstandard codec requested but python-zstandard is not available")
        decompressor = _zstd.ZstdDecompressor()
        return decompressor.decompress(data)
    if codec == "zlib":
        return zlib.decompress(data)
    raise ValueError(f"Unsupported compression codec: {codec}")


def x_decompress_payload__mutmut_2(data: bytes, codec: str) -> bytes:
    """Decompress *data* using the explicit *codec* identifier."""

    if codec == "XXzstdXX":
        if _zstd is None:
            raise RuntimeError("zstandard codec requested but python-zstandard is not available")
        decompressor = _zstd.ZstdDecompressor()
        return decompressor.decompress(data)
    if codec == "zlib":
        return zlib.decompress(data)
    raise ValueError(f"Unsupported compression codec: {codec}")


def x_decompress_payload__mutmut_3(data: bytes, codec: str) -> bytes:
    """Decompress *data* using the explicit *codec* identifier."""

    if codec == "ZSTD":
        if _zstd is None:
            raise RuntimeError("zstandard codec requested but python-zstandard is not available")
        decompressor = _zstd.ZstdDecompressor()
        return decompressor.decompress(data)
    if codec == "zlib":
        return zlib.decompress(data)
    raise ValueError(f"Unsupported compression codec: {codec}")


def x_decompress_payload__mutmut_4(data: bytes, codec: str) -> bytes:
    """Decompress *data* using the explicit *codec* identifier."""

    if codec == "zstd":
        if _zstd is not None:
            raise RuntimeError("zstandard codec requested but python-zstandard is not available")
        decompressor = _zstd.ZstdDecompressor()
        return decompressor.decompress(data)
    if codec == "zlib":
        return zlib.decompress(data)
    raise ValueError(f"Unsupported compression codec: {codec}")


def x_decompress_payload__mutmut_5(data: bytes, codec: str) -> bytes:
    """Decompress *data* using the explicit *codec* identifier."""

    if codec == "zstd":
        if _zstd is None:
            raise RuntimeError(None)
        decompressor = _zstd.ZstdDecompressor()
        return decompressor.decompress(data)
    if codec == "zlib":
        return zlib.decompress(data)
    raise ValueError(f"Unsupported compression codec: {codec}")


def x_decompress_payload__mutmut_6(data: bytes, codec: str) -> bytes:
    """Decompress *data* using the explicit *codec* identifier."""

    if codec == "zstd":
        if _zstd is None:
            raise RuntimeError("XXzstandard codec requested but python-zstandard is not availableXX")
        decompressor = _zstd.ZstdDecompressor()
        return decompressor.decompress(data)
    if codec == "zlib":
        return zlib.decompress(data)
    raise ValueError(f"Unsupported compression codec: {codec}")


def x_decompress_payload__mutmut_7(data: bytes, codec: str) -> bytes:
    """Decompress *data* using the explicit *codec* identifier."""

    if codec == "zstd":
        if _zstd is None:
            raise RuntimeError("ZSTANDARD CODEC REQUESTED BUT PYTHON-ZSTANDARD IS NOT AVAILABLE")
        decompressor = _zstd.ZstdDecompressor()
        return decompressor.decompress(data)
    if codec == "zlib":
        return zlib.decompress(data)
    raise ValueError(f"Unsupported compression codec: {codec}")


def x_decompress_payload__mutmut_8(data: bytes, codec: str) -> bytes:
    """Decompress *data* using the explicit *codec* identifier."""

    if codec == "zstd":
        if _zstd is None:
            raise RuntimeError("zstandard codec requested but python-zstandard is not available")
        decompressor = None
        return decompressor.decompress(data)
    if codec == "zlib":
        return zlib.decompress(data)
    raise ValueError(f"Unsupported compression codec: {codec}")


def x_decompress_payload__mutmut_9(data: bytes, codec: str) -> bytes:
    """Decompress *data* using the explicit *codec* identifier."""

    if codec == "zstd":
        if _zstd is None:
            raise RuntimeError("zstandard codec requested but python-zstandard is not available")
        decompressor = _zstd.ZstdDecompressor()
        return decompressor.decompress(None)
    if codec == "zlib":
        return zlib.decompress(data)
    raise ValueError(f"Unsupported compression codec: {codec}")


def x_decompress_payload__mutmut_10(data: bytes, codec: str) -> bytes:
    """Decompress *data* using the explicit *codec* identifier."""

    if codec == "zstd":
        if _zstd is None:
            raise RuntimeError("zstandard codec requested but python-zstandard is not available")
        decompressor = _zstd.ZstdDecompressor()
        return decompressor.decompress(data)
    if codec != "zlib":
        return zlib.decompress(data)
    raise ValueError(f"Unsupported compression codec: {codec}")


def x_decompress_payload__mutmut_11(data: bytes, codec: str) -> bytes:
    """Decompress *data* using the explicit *codec* identifier."""

    if codec == "zstd":
        if _zstd is None:
            raise RuntimeError("zstandard codec requested but python-zstandard is not available")
        decompressor = _zstd.ZstdDecompressor()
        return decompressor.decompress(data)
    if codec == "XXzlibXX":
        return zlib.decompress(data)
    raise ValueError(f"Unsupported compression codec: {codec}")


def x_decompress_payload__mutmut_12(data: bytes, codec: str) -> bytes:
    """Decompress *data* using the explicit *codec* identifier."""

    if codec == "zstd":
        if _zstd is None:
            raise RuntimeError("zstandard codec requested but python-zstandard is not available")
        decompressor = _zstd.ZstdDecompressor()
        return decompressor.decompress(data)
    if codec == "ZLIB":
        return zlib.decompress(data)
    raise ValueError(f"Unsupported compression codec: {codec}")


def x_decompress_payload__mutmut_13(data: bytes, codec: str) -> bytes:
    """Decompress *data* using the explicit *codec* identifier."""

    if codec == "zstd":
        if _zstd is None:
            raise RuntimeError("zstandard codec requested but python-zstandard is not available")
        decompressor = _zstd.ZstdDecompressor()
        return decompressor.decompress(data)
    if codec == "zlib":
        return zlib.decompress(None)
    raise ValueError(f"Unsupported compression codec: {codec}")


def x_decompress_payload__mutmut_14(data: bytes, codec: str) -> bytes:
    """Decompress *data* using the explicit *codec* identifier."""

    if codec == "zstd":
        if _zstd is None:
            raise RuntimeError("zstandard codec requested but python-zstandard is not available")
        decompressor = _zstd.ZstdDecompressor()
        return decompressor.decompress(data)
    if codec == "zlib":
        return zlib.decompress(data)
    raise ValueError(None)

x_decompress_payload__mutmut_mutants : ClassVar[MutantDict] = {
'x_decompress_payload__mutmut_1': x_decompress_payload__mutmut_1, 
    'x_decompress_payload__mutmut_2': x_decompress_payload__mutmut_2, 
    'x_decompress_payload__mutmut_3': x_decompress_payload__mutmut_3, 
    'x_decompress_payload__mutmut_4': x_decompress_payload__mutmut_4, 
    'x_decompress_payload__mutmut_5': x_decompress_payload__mutmut_5, 
    'x_decompress_payload__mutmut_6': x_decompress_payload__mutmut_6, 
    'x_decompress_payload__mutmut_7': x_decompress_payload__mutmut_7, 
    'x_decompress_payload__mutmut_8': x_decompress_payload__mutmut_8, 
    'x_decompress_payload__mutmut_9': x_decompress_payload__mutmut_9, 
    'x_decompress_payload__mutmut_10': x_decompress_payload__mutmut_10, 
    'x_decompress_payload__mutmut_11': x_decompress_payload__mutmut_11, 
    'x_decompress_payload__mutmut_12': x_decompress_payload__mutmut_12, 
    'x_decompress_payload__mutmut_13': x_decompress_payload__mutmut_13, 
    'x_decompress_payload__mutmut_14': x_decompress_payload__mutmut_14
}

def decompress_payload(*args, **kwargs):
    result = _mutmut_trampoline(x_decompress_payload__mutmut_orig, x_decompress_payload__mutmut_mutants, args, kwargs)
    return result 

decompress_payload.__signature__ = _mutmut_signature(x_decompress_payload__mutmut_orig)
x_decompress_payload__mutmut_orig.__name__ = 'x_decompress_payload'


def x_compression_codec__mutmut_orig() -> str:
    """Return the codec identifier used by :func:`zstd_compress`."""

    return "zstd" if _zstd is not None else "zlib"


def x_compression_codec__mutmut_1() -> str:
    """Return the codec identifier used by :func:`zstd_compress`."""

    return "XXzstdXX" if _zstd is not None else "zlib"


def x_compression_codec__mutmut_2() -> str:
    """Return the codec identifier used by :func:`zstd_compress`."""

    return "ZSTD" if _zstd is not None else "zlib"


def x_compression_codec__mutmut_3() -> str:
    """Return the codec identifier used by :func:`zstd_compress`."""

    return "zstd" if _zstd is None else "zlib"


def x_compression_codec__mutmut_4() -> str:
    """Return the codec identifier used by :func:`zstd_compress`."""

    return "zstd" if _zstd is not None else "XXzlibXX"


def x_compression_codec__mutmut_5() -> str:
    """Return the codec identifier used by :func:`zstd_compress`."""

    return "zstd" if _zstd is not None else "ZLIB"

x_compression_codec__mutmut_mutants : ClassVar[MutantDict] = {
'x_compression_codec__mutmut_1': x_compression_codec__mutmut_1, 
    'x_compression_codec__mutmut_2': x_compression_codec__mutmut_2, 
    'x_compression_codec__mutmut_3': x_compression_codec__mutmut_3, 
    'x_compression_codec__mutmut_4': x_compression_codec__mutmut_4, 
    'x_compression_codec__mutmut_5': x_compression_codec__mutmut_5
}

def compression_codec(*args, **kwargs):
    result = _mutmut_trampoline(x_compression_codec__mutmut_orig, x_compression_codec__mutmut_mutants, args, kwargs)
    return result 

compression_codec.__signature__ = _mutmut_signature(x_compression_codec__mutmut_orig)
x_compression_codec__mutmut_orig.__name__ = 'x_compression_codec'


def x_ensure_directory__mutmut_orig(path: Path) -> None:
    """Ensure *path* exists, creating parent directories as needed."""

    path.mkdir(parents=True, exist_ok=True)


def x_ensure_directory__mutmut_1(path: Path) -> None:
    """Ensure *path* exists, creating parent directories as needed."""

    path.mkdir(parents=None, exist_ok=True)


def x_ensure_directory__mutmut_2(path: Path) -> None:
    """Ensure *path* exists, creating parent directories as needed."""

    path.mkdir(parents=True, exist_ok=None)


def x_ensure_directory__mutmut_3(path: Path) -> None:
    """Ensure *path* exists, creating parent directories as needed."""

    path.mkdir(exist_ok=True)


def x_ensure_directory__mutmut_4(path: Path) -> None:
    """Ensure *path* exists, creating parent directories as needed."""

    path.mkdir(parents=True, )


def x_ensure_directory__mutmut_5(path: Path) -> None:
    """Ensure *path* exists, creating parent directories as needed."""

    path.mkdir(parents=False, exist_ok=True)


def x_ensure_directory__mutmut_6(path: Path) -> None:
    """Ensure *path* exists, creating parent directories as needed."""

    path.mkdir(parents=True, exist_ok=False)

x_ensure_directory__mutmut_mutants : ClassVar[MutantDict] = {
'x_ensure_directory__mutmut_1': x_ensure_directory__mutmut_1, 
    'x_ensure_directory__mutmut_2': x_ensure_directory__mutmut_2, 
    'x_ensure_directory__mutmut_3': x_ensure_directory__mutmut_3, 
    'x_ensure_directory__mutmut_4': x_ensure_directory__mutmut_4, 
    'x_ensure_directory__mutmut_5': x_ensure_directory__mutmut_5, 
    'x_ensure_directory__mutmut_6': x_ensure_directory__mutmut_6
}

def ensure_directory(*args, **kwargs):
    result = _mutmut_trampoline(x_ensure_directory__mutmut_orig, x_ensure_directory__mutmut_mutants, args, kwargs)
    return result 

ensure_directory.__signature__ = _mutmut_signature(x_ensure_directory__mutmut_orig)
x_ensure_directory__mutmut_orig.__name__ = 'x_ensure_directory'


def x_json_dumps_sorted__mutmut_orig(payload: dict[str, Any]) -> str:
    """Serialise *payload* with sorted keys for reproducibility."""

    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def x_json_dumps_sorted__mutmut_1(payload: dict[str, Any]) -> str:
    """Serialise *payload* with sorted keys for reproducibility."""

    return json.dumps(None, sort_keys=True, separators=(",", ":"))


def x_json_dumps_sorted__mutmut_2(payload: dict[str, Any]) -> str:
    """Serialise *payload* with sorted keys for reproducibility."""

    return json.dumps(payload, sort_keys=None, separators=(",", ":"))


def x_json_dumps_sorted__mutmut_3(payload: dict[str, Any]) -> str:
    """Serialise *payload* with sorted keys for reproducibility."""

    return json.dumps(payload, sort_keys=True, separators=None)


def x_json_dumps_sorted__mutmut_4(payload: dict[str, Any]) -> str:
    """Serialise *payload* with sorted keys for reproducibility."""

    return json.dumps(sort_keys=True, separators=(",", ":"))


def x_json_dumps_sorted__mutmut_5(payload: dict[str, Any]) -> str:
    """Serialise *payload* with sorted keys for reproducibility."""

    return json.dumps(payload, separators=(",", ":"))


def x_json_dumps_sorted__mutmut_6(payload: dict[str, Any]) -> str:
    """Serialise *payload* with sorted keys for reproducibility."""

    return json.dumps(payload, sort_keys=True, )


def x_json_dumps_sorted__mutmut_7(payload: dict[str, Any]) -> str:
    """Serialise *payload* with sorted keys for reproducibility."""

    return json.dumps(payload, sort_keys=False, separators=(",", ":"))


def x_json_dumps_sorted__mutmut_8(payload: dict[str, Any]) -> str:
    """Serialise *payload* with sorted keys for reproducibility."""

    return json.dumps(payload, sort_keys=True, separators=("XX,XX", ":"))


def x_json_dumps_sorted__mutmut_9(payload: dict[str, Any]) -> str:
    """Serialise *payload* with sorted keys for reproducibility."""

    return json.dumps(payload, sort_keys=True, separators=(",", "XX:XX"))

x_json_dumps_sorted__mutmut_mutants : ClassVar[MutantDict] = {
'x_json_dumps_sorted__mutmut_1': x_json_dumps_sorted__mutmut_1, 
    'x_json_dumps_sorted__mutmut_2': x_json_dumps_sorted__mutmut_2, 
    'x_json_dumps_sorted__mutmut_3': x_json_dumps_sorted__mutmut_3, 
    'x_json_dumps_sorted__mutmut_4': x_json_dumps_sorted__mutmut_4, 
    'x_json_dumps_sorted__mutmut_5': x_json_dumps_sorted__mutmut_5, 
    'x_json_dumps_sorted__mutmut_6': x_json_dumps_sorted__mutmut_6, 
    'x_json_dumps_sorted__mutmut_7': x_json_dumps_sorted__mutmut_7, 
    'x_json_dumps_sorted__mutmut_8': x_json_dumps_sorted__mutmut_8, 
    'x_json_dumps_sorted__mutmut_9': x_json_dumps_sorted__mutmut_9
}

def json_dumps_sorted(*args, **kwargs):
    result = _mutmut_trampoline(x_json_dumps_sorted__mutmut_orig, x_json_dumps_sorted__mutmut_mutants, args, kwargs)
    return result 

json_dumps_sorted.__signature__ = _mutmut_signature(x_json_dumps_sorted__mutmut_orig)
x_json_dumps_sorted__mutmut_orig.__name__ = 'x_json_dumps_sorted'


def x_evidence_file__mutmut_orig() -> Path:
    """Return the evidence file location, creating directories if necessary."""

    base = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    ensure_directory(base)
    return base / "archive_ops.jsonl"


def x_evidence_file__mutmut_1() -> Path:
    """Return the evidence file location, creating directories if necessary."""

    base = None
    ensure_directory(base)
    return base / "archive_ops.jsonl"


def x_evidence_file__mutmut_2() -> Path:
    """Return the evidence file location, creating directories if necessary."""

    base = Path(None)
    ensure_directory(base)
    return base / "archive_ops.jsonl"


def x_evidence_file__mutmut_3() -> Path:
    """Return the evidence file location, creating directories if necessary."""

    base = Path(os.getenv(None, ".codex/evidence"))
    ensure_directory(base)
    return base / "archive_ops.jsonl"


def x_evidence_file__mutmut_4() -> Path:
    """Return the evidence file location, creating directories if necessary."""

    base = Path(os.getenv("CODEX_EVIDENCE_DIR", None))
    ensure_directory(base)
    return base / "archive_ops.jsonl"


def x_evidence_file__mutmut_5() -> Path:
    """Return the evidence file location, creating directories if necessary."""

    base = Path(os.getenv(".codex/evidence"))
    ensure_directory(base)
    return base / "archive_ops.jsonl"


def x_evidence_file__mutmut_6() -> Path:
    """Return the evidence file location, creating directories if necessary."""

    base = Path(os.getenv("CODEX_EVIDENCE_DIR", ))
    ensure_directory(base)
    return base / "archive_ops.jsonl"


def x_evidence_file__mutmut_7() -> Path:
    """Return the evidence file location, creating directories if necessary."""

    base = Path(os.getenv("XXCODEX_EVIDENCE_DIRXX", ".codex/evidence"))
    ensure_directory(base)
    return base / "archive_ops.jsonl"


def x_evidence_file__mutmut_8() -> Path:
    """Return the evidence file location, creating directories if necessary."""

    base = Path(os.getenv("codex_evidence_dir", ".codex/evidence"))
    ensure_directory(base)
    return base / "archive_ops.jsonl"


def x_evidence_file__mutmut_9() -> Path:
    """Return the evidence file location, creating directories if necessary."""

    base = Path(os.getenv("CODEX_EVIDENCE_DIR", "XX.codex/evidenceXX"))
    ensure_directory(base)
    return base / "archive_ops.jsonl"


def x_evidence_file__mutmut_10() -> Path:
    """Return the evidence file location, creating directories if necessary."""

    base = Path(os.getenv("CODEX_EVIDENCE_DIR", ".CODEX/EVIDENCE"))
    ensure_directory(base)
    return base / "archive_ops.jsonl"


def x_evidence_file__mutmut_11() -> Path:
    """Return the evidence file location, creating directories if necessary."""

    base = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    ensure_directory(None)
    return base / "archive_ops.jsonl"


def x_evidence_file__mutmut_12() -> Path:
    """Return the evidence file location, creating directories if necessary."""

    base = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    ensure_directory(base)
    return base * "archive_ops.jsonl"


def x_evidence_file__mutmut_13() -> Path:
    """Return the evidence file location, creating directories if necessary."""

    base = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    ensure_directory(base)
    return base / "XXarchive_ops.jsonlXX"


def x_evidence_file__mutmut_14() -> Path:
    """Return the evidence file location, creating directories if necessary."""

    base = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    ensure_directory(base)
    return base / "ARCHIVE_OPS.JSONL"

x_evidence_file__mutmut_mutants : ClassVar[MutantDict] = {
'x_evidence_file__mutmut_1': x_evidence_file__mutmut_1, 
    'x_evidence_file__mutmut_2': x_evidence_file__mutmut_2, 
    'x_evidence_file__mutmut_3': x_evidence_file__mutmut_3, 
    'x_evidence_file__mutmut_4': x_evidence_file__mutmut_4, 
    'x_evidence_file__mutmut_5': x_evidence_file__mutmut_5, 
    'x_evidence_file__mutmut_6': x_evidence_file__mutmut_6, 
    'x_evidence_file__mutmut_7': x_evidence_file__mutmut_7, 
    'x_evidence_file__mutmut_8': x_evidence_file__mutmut_8, 
    'x_evidence_file__mutmut_9': x_evidence_file__mutmut_9, 
    'x_evidence_file__mutmut_10': x_evidence_file__mutmut_10, 
    'x_evidence_file__mutmut_11': x_evidence_file__mutmut_11, 
    'x_evidence_file__mutmut_12': x_evidence_file__mutmut_12, 
    'x_evidence_file__mutmut_13': x_evidence_file__mutmut_13, 
    'x_evidence_file__mutmut_14': x_evidence_file__mutmut_14
}

def evidence_file(*args, **kwargs):
    result = _mutmut_trampoline(x_evidence_file__mutmut_orig, x_evidence_file__mutmut_mutants, args, kwargs)
    return result 

evidence_file.__signature__ = _mutmut_signature(x_evidence_file__mutmut_orig)
x_evidence_file__mutmut_orig.__name__ = 'x_evidence_file'


def x_append_evidence__mutmut_orig(record: dict[str, Any]) -> None:
    """Append a JSON record to the evidence log."""

    record = dict(record)
    record.setdefault("ts", utcnow())
    path = evidence_file()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json_dumps_sorted(record) + "\n")


def x_append_evidence__mutmut_1(record: dict[str, Any]) -> None:
    """Append a JSON record to the evidence log."""

    record = None
    record.setdefault("ts", utcnow())
    path = evidence_file()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json_dumps_sorted(record) + "\n")


def x_append_evidence__mutmut_2(record: dict[str, Any]) -> None:
    """Append a JSON record to the evidence log."""

    record = dict(None)
    record.setdefault("ts", utcnow())
    path = evidence_file()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json_dumps_sorted(record) + "\n")


def x_append_evidence__mutmut_3(record: dict[str, Any]) -> None:
    """Append a JSON record to the evidence log."""

    record = dict(record)
    record.setdefault(None, utcnow())
    path = evidence_file()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json_dumps_sorted(record) + "\n")


def x_append_evidence__mutmut_4(record: dict[str, Any]) -> None:
    """Append a JSON record to the evidence log."""

    record = dict(record)
    record.setdefault("ts", None)
    path = evidence_file()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json_dumps_sorted(record) + "\n")


def x_append_evidence__mutmut_5(record: dict[str, Any]) -> None:
    """Append a JSON record to the evidence log."""

    record = dict(record)
    record.setdefault(utcnow())
    path = evidence_file()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json_dumps_sorted(record) + "\n")


def x_append_evidence__mutmut_6(record: dict[str, Any]) -> None:
    """Append a JSON record to the evidence log."""

    record = dict(record)
    record.setdefault("ts", )
    path = evidence_file()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json_dumps_sorted(record) + "\n")


def x_append_evidence__mutmut_7(record: dict[str, Any]) -> None:
    """Append a JSON record to the evidence log."""

    record = dict(record)
    record.setdefault("XXtsXX", utcnow())
    path = evidence_file()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json_dumps_sorted(record) + "\n")


def x_append_evidence__mutmut_8(record: dict[str, Any]) -> None:
    """Append a JSON record to the evidence log."""

    record = dict(record)
    record.setdefault("TS", utcnow())
    path = evidence_file()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json_dumps_sorted(record) + "\n")


def x_append_evidence__mutmut_9(record: dict[str, Any]) -> None:
    """Append a JSON record to the evidence log."""

    record = dict(record)
    record.setdefault("ts", utcnow())
    path = None
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json_dumps_sorted(record) + "\n")


def x_append_evidence__mutmut_10(record: dict[str, Any]) -> None:
    """Append a JSON record to the evidence log."""

    record = dict(record)
    record.setdefault("ts", utcnow())
    path = evidence_file()
    with path.open(None, encoding="utf-8") as handle:
        handle.write(json_dumps_sorted(record) + "\n")


def x_append_evidence__mutmut_11(record: dict[str, Any]) -> None:
    """Append a JSON record to the evidence log."""

    record = dict(record)
    record.setdefault("ts", utcnow())
    path = evidence_file()
    with path.open("a", encoding=None) as handle:
        handle.write(json_dumps_sorted(record) + "\n")


def x_append_evidence__mutmut_12(record: dict[str, Any]) -> None:
    """Append a JSON record to the evidence log."""

    record = dict(record)
    record.setdefault("ts", utcnow())
    path = evidence_file()
    with path.open(encoding="utf-8") as handle:
        handle.write(json_dumps_sorted(record) + "\n")


def x_append_evidence__mutmut_13(record: dict[str, Any]) -> None:
    """Append a JSON record to the evidence log."""

    record = dict(record)
    record.setdefault("ts", utcnow())
    path = evidence_file()
    with path.open("a", ) as handle:
        handle.write(json_dumps_sorted(record) + "\n")


def x_append_evidence__mutmut_14(record: dict[str, Any]) -> None:
    """Append a JSON record to the evidence log."""

    record = dict(record)
    record.setdefault("ts", utcnow())
    path = evidence_file()
    with path.open("XXaXX", encoding="utf-8") as handle:
        handle.write(json_dumps_sorted(record) + "\n")


def x_append_evidence__mutmut_15(record: dict[str, Any]) -> None:
    """Append a JSON record to the evidence log."""

    record = dict(record)
    record.setdefault("ts", utcnow())
    path = evidence_file()
    with path.open("A", encoding="utf-8") as handle:
        handle.write(json_dumps_sorted(record) + "\n")


def x_append_evidence__mutmut_16(record: dict[str, Any]) -> None:
    """Append a JSON record to the evidence log."""

    record = dict(record)
    record.setdefault("ts", utcnow())
    path = evidence_file()
    with path.open("a", encoding="XXutf-8XX") as handle:
        handle.write(json_dumps_sorted(record) + "\n")


def x_append_evidence__mutmut_17(record: dict[str, Any]) -> None:
    """Append a JSON record to the evidence log."""

    record = dict(record)
    record.setdefault("ts", utcnow())
    path = evidence_file()
    with path.open("a", encoding="UTF-8") as handle:
        handle.write(json_dumps_sorted(record) + "\n")


def x_append_evidence__mutmut_18(record: dict[str, Any]) -> None:
    """Append a JSON record to the evidence log."""

    record = dict(record)
    record.setdefault("ts", utcnow())
    path = evidence_file()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(None)


def x_append_evidence__mutmut_19(record: dict[str, Any]) -> None:
    """Append a JSON record to the evidence log."""

    record = dict(record)
    record.setdefault("ts", utcnow())
    path = evidence_file()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json_dumps_sorted(record) - "\n")


def x_append_evidence__mutmut_20(record: dict[str, Any]) -> None:
    """Append a JSON record to the evidence log."""

    record = dict(record)
    record.setdefault("ts", utcnow())
    path = evidence_file()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json_dumps_sorted(None) + "\n")


def x_append_evidence__mutmut_21(record: dict[str, Any]) -> None:
    """Append a JSON record to the evidence log."""

    record = dict(record)
    record.setdefault("ts", utcnow())
    path = evidence_file()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json_dumps_sorted(record) + "XX\nXX")

x_append_evidence__mutmut_mutants : ClassVar[MutantDict] = {
'x_append_evidence__mutmut_1': x_append_evidence__mutmut_1, 
    'x_append_evidence__mutmut_2': x_append_evidence__mutmut_2, 
    'x_append_evidence__mutmut_3': x_append_evidence__mutmut_3, 
    'x_append_evidence__mutmut_4': x_append_evidence__mutmut_4, 
    'x_append_evidence__mutmut_5': x_append_evidence__mutmut_5, 
    'x_append_evidence__mutmut_6': x_append_evidence__mutmut_6, 
    'x_append_evidence__mutmut_7': x_append_evidence__mutmut_7, 
    'x_append_evidence__mutmut_8': x_append_evidence__mutmut_8, 
    'x_append_evidence__mutmut_9': x_append_evidence__mutmut_9, 
    'x_append_evidence__mutmut_10': x_append_evidence__mutmut_10, 
    'x_append_evidence__mutmut_11': x_append_evidence__mutmut_11, 
    'x_append_evidence__mutmut_12': x_append_evidence__mutmut_12, 
    'x_append_evidence__mutmut_13': x_append_evidence__mutmut_13, 
    'x_append_evidence__mutmut_14': x_append_evidence__mutmut_14, 
    'x_append_evidence__mutmut_15': x_append_evidence__mutmut_15, 
    'x_append_evidence__mutmut_16': x_append_evidence__mutmut_16, 
    'x_append_evidence__mutmut_17': x_append_evidence__mutmut_17, 
    'x_append_evidence__mutmut_18': x_append_evidence__mutmut_18, 
    'x_append_evidence__mutmut_19': x_append_evidence__mutmut_19, 
    'x_append_evidence__mutmut_20': x_append_evidence__mutmut_20, 
    'x_append_evidence__mutmut_21': x_append_evidence__mutmut_21
}

def append_evidence(*args, **kwargs):
    result = _mutmut_trampoline(x_append_evidence__mutmut_orig, x_append_evidence__mutmut_mutants, args, kwargs)
    return result 

append_evidence.__signature__ = _mutmut_signature(x_append_evidence__mutmut_orig)
x_append_evidence__mutmut_orig.__name__ = 'x_append_evidence'


def x_redact_url_credentials__mutmut_orig(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=True)
        return url

    if not parsed.username and not parsed.password:
        return url

    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    suffix = parsed.netloc.split("@")[-1] if parsed.netloc else ""
    if suffix and suffix != hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "***"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_1(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if url:
        return ""

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=True)
        return url

    if not parsed.username and not parsed.password:
        return url

    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    suffix = parsed.netloc.split("@")[-1] if parsed.netloc else ""
    if suffix and suffix != hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "***"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_2(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return "XXXX"

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=True)
        return url

    if not parsed.username and not parsed.password:
        return url

    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    suffix = parsed.netloc.split("@")[-1] if parsed.netloc else ""
    if suffix and suffix != hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "***"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_3(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = None
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=True)
        return url

    if not parsed.username and not parsed.password:
        return url

    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    suffix = parsed.netloc.split("@")[-1] if parsed.netloc else ""
    if suffix and suffix != hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "***"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_4(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = urlsplit(None)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=True)
        return url

    if not parsed.username and not parsed.password:
        return url

    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    suffix = parsed.netloc.split("@")[-1] if parsed.netloc else ""
    if suffix and suffix != hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "***"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_5(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(None)
        logger.warning(f"ValueError: {e}", exc_info=True)
        return url

    if not parsed.username and not parsed.password:
        return url

    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    suffix = parsed.netloc.split("@")[-1] if parsed.netloc else ""
    if suffix and suffix != hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "***"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_6(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(None, exc_info=True)
        return url

    if not parsed.username and not parsed.password:
        return url

    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    suffix = parsed.netloc.split("@")[-1] if parsed.netloc else ""
    if suffix and suffix != hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "***"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_7(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=None)
        return url

    if not parsed.username and not parsed.password:
        return url

    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    suffix = parsed.netloc.split("@")[-1] if parsed.netloc else ""
    if suffix and suffix != hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "***"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_8(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(exc_info=True)
        return url

    if not parsed.username and not parsed.password:
        return url

    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    suffix = parsed.netloc.split("@")[-1] if parsed.netloc else ""
    if suffix and suffix != hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "***"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_9(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", )
        return url

    if not parsed.username and not parsed.password:
        return url

    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    suffix = parsed.netloc.split("@")[-1] if parsed.netloc else ""
    if suffix and suffix != hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "***"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_10(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=False)
        return url

    if not parsed.username and not parsed.password:
        return url

    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    suffix = parsed.netloc.split("@")[-1] if parsed.netloc else ""
    if suffix and suffix != hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "***"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_11(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=True)
        return url

    if not parsed.username or not parsed.password:
        return url

    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    suffix = parsed.netloc.split("@")[-1] if parsed.netloc else ""
    if suffix and suffix != hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "***"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_12(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=True)
        return url

    if parsed.username and not parsed.password:
        return url

    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    suffix = parsed.netloc.split("@")[-1] if parsed.netloc else ""
    if suffix and suffix != hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "***"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_13(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=True)
        return url

    if not parsed.username and parsed.password:
        return url

    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    suffix = parsed.netloc.split("@")[-1] if parsed.netloc else ""
    if suffix and suffix != hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "***"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_14(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=True)
        return url

    if not parsed.username and not parsed.password:
        return url

    hostname = None
    port = f":{parsed.port}" if parsed.port else ""
    suffix = parsed.netloc.split("@")[-1] if parsed.netloc else ""
    if suffix and suffix != hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "***"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_15(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=True)
        return url

    if not parsed.username and not parsed.password:
        return url

    hostname = parsed.hostname and ""
    port = f":{parsed.port}" if parsed.port else ""
    suffix = parsed.netloc.split("@")[-1] if parsed.netloc else ""
    if suffix and suffix != hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "***"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_16(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=True)
        return url

    if not parsed.username and not parsed.password:
        return url

    hostname = parsed.hostname or "XXXX"
    port = f":{parsed.port}" if parsed.port else ""
    suffix = parsed.netloc.split("@")[-1] if parsed.netloc else ""
    if suffix and suffix != hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "***"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_17(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=True)
        return url

    if not parsed.username and not parsed.password:
        return url

    hostname = parsed.hostname or ""
    port = None
    suffix = parsed.netloc.split("@")[-1] if parsed.netloc else ""
    if suffix and suffix != hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "***"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_18(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=True)
        return url

    if not parsed.username and not parsed.password:
        return url

    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else "XXXX"
    suffix = parsed.netloc.split("@")[-1] if parsed.netloc else ""
    if suffix and suffix != hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "***"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_19(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=True)
        return url

    if not parsed.username and not parsed.password:
        return url

    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    suffix = None
    if suffix and suffix != hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "***"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_20(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=True)
        return url

    if not parsed.username and not parsed.password:
        return url

    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    suffix = parsed.netloc.split(None)[-1] if parsed.netloc else ""
    if suffix and suffix != hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "***"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_21(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=True)
        return url

    if not parsed.username and not parsed.password:
        return url

    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    suffix = parsed.netloc.split("XX@XX")[-1] if parsed.netloc else ""
    if suffix and suffix != hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "***"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_22(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=True)
        return url

    if not parsed.username and not parsed.password:
        return url

    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    suffix = parsed.netloc.split("@")[+1] if parsed.netloc else ""
    if suffix and suffix != hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "***"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_23(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=True)
        return url

    if not parsed.username and not parsed.password:
        return url

    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    suffix = parsed.netloc.split("@")[-2] if parsed.netloc else ""
    if suffix and suffix != hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "***"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_24(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=True)
        return url

    if not parsed.username and not parsed.password:
        return url

    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    suffix = parsed.netloc.split("@")[-1] if parsed.netloc else "XXXX"
    if suffix and suffix != hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "***"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_25(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=True)
        return url

    if not parsed.username and not parsed.password:
        return url

    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    suffix = parsed.netloc.split("@")[-1] if parsed.netloc else ""
    if suffix or suffix != hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "***"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_26(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=True)
        return url

    if not parsed.username and not parsed.password:
        return url

    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    suffix = parsed.netloc.split("@")[-1] if parsed.netloc else ""
    if suffix and suffix == hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "***"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_27(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=True)
        return url

    if not parsed.username and not parsed.password:
        return url

    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    suffix = parsed.netloc.split("@")[-1] if parsed.netloc else ""
    if suffix and suffix != hostname - port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "***"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_28(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=True)
        return url

    if not parsed.username and not parsed.password:
        return url

    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    suffix = parsed.netloc.split("@")[-1] if parsed.netloc else ""
    if suffix and suffix != hostname + port:
        netloc = None
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "***"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_29(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=True)
        return url

    if not parsed.username and not parsed.password:
        return url

    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    suffix = parsed.netloc.split("@")[-1] if parsed.netloc else ""
    if suffix and suffix != hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = None
    else:
        netloc = "***"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_30(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=True)
        return url

    if not parsed.username and not parsed.password:
        return url

    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    suffix = parsed.netloc.split("@")[-1] if parsed.netloc else ""
    if suffix and suffix != hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = None

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_31(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=True)
        return url

    if not parsed.username and not parsed.password:
        return url

    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    suffix = parsed.netloc.split("@")[-1] if parsed.netloc else ""
    if suffix and suffix != hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "XX***XX"

    return parsed._replace(netloc=netloc).geturl()


def x_redact_url_credentials__mutmut_32(url: str | None) -> str:
    """Return *url* with credentials removed while preserving structure."""

    if not url:
        return ""

    try:
        parsed = urlsplit(url)
    except ValueError as e:
        logger.debug(f"ValueError: {e}")
        logger.warning(f"ValueError: {e}", exc_info=True)
        return url

    if not parsed.username and not parsed.password:
        return url

    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    suffix = parsed.netloc.split("@")[-1] if parsed.netloc else ""
    if suffix and suffix != hostname + port:
        netloc = f"***@{suffix}"
    elif hostname:
        netloc = f"***@{hostname}{port}"
    else:
        netloc = "***"

    return parsed._replace(netloc=None).geturl()

x_redact_url_credentials__mutmut_mutants : ClassVar[MutantDict] = {
'x_redact_url_credentials__mutmut_1': x_redact_url_credentials__mutmut_1, 
    'x_redact_url_credentials__mutmut_2': x_redact_url_credentials__mutmut_2, 
    'x_redact_url_credentials__mutmut_3': x_redact_url_credentials__mutmut_3, 
    'x_redact_url_credentials__mutmut_4': x_redact_url_credentials__mutmut_4, 
    'x_redact_url_credentials__mutmut_5': x_redact_url_credentials__mutmut_5, 
    'x_redact_url_credentials__mutmut_6': x_redact_url_credentials__mutmut_6, 
    'x_redact_url_credentials__mutmut_7': x_redact_url_credentials__mutmut_7, 
    'x_redact_url_credentials__mutmut_8': x_redact_url_credentials__mutmut_8, 
    'x_redact_url_credentials__mutmut_9': x_redact_url_credentials__mutmut_9, 
    'x_redact_url_credentials__mutmut_10': x_redact_url_credentials__mutmut_10, 
    'x_redact_url_credentials__mutmut_11': x_redact_url_credentials__mutmut_11, 
    'x_redact_url_credentials__mutmut_12': x_redact_url_credentials__mutmut_12, 
    'x_redact_url_credentials__mutmut_13': x_redact_url_credentials__mutmut_13, 
    'x_redact_url_credentials__mutmut_14': x_redact_url_credentials__mutmut_14, 
    'x_redact_url_credentials__mutmut_15': x_redact_url_credentials__mutmut_15, 
    'x_redact_url_credentials__mutmut_16': x_redact_url_credentials__mutmut_16, 
    'x_redact_url_credentials__mutmut_17': x_redact_url_credentials__mutmut_17, 
    'x_redact_url_credentials__mutmut_18': x_redact_url_credentials__mutmut_18, 
    'x_redact_url_credentials__mutmut_19': x_redact_url_credentials__mutmut_19, 
    'x_redact_url_credentials__mutmut_20': x_redact_url_credentials__mutmut_20, 
    'x_redact_url_credentials__mutmut_21': x_redact_url_credentials__mutmut_21, 
    'x_redact_url_credentials__mutmut_22': x_redact_url_credentials__mutmut_22, 
    'x_redact_url_credentials__mutmut_23': x_redact_url_credentials__mutmut_23, 
    'x_redact_url_credentials__mutmut_24': x_redact_url_credentials__mutmut_24, 
    'x_redact_url_credentials__mutmut_25': x_redact_url_credentials__mutmut_25, 
    'x_redact_url_credentials__mutmut_26': x_redact_url_credentials__mutmut_26, 
    'x_redact_url_credentials__mutmut_27': x_redact_url_credentials__mutmut_27, 
    'x_redact_url_credentials__mutmut_28': x_redact_url_credentials__mutmut_28, 
    'x_redact_url_credentials__mutmut_29': x_redact_url_credentials__mutmut_29, 
    'x_redact_url_credentials__mutmut_30': x_redact_url_credentials__mutmut_30, 
    'x_redact_url_credentials__mutmut_31': x_redact_url_credentials__mutmut_31, 
    'x_redact_url_credentials__mutmut_32': x_redact_url_credentials__mutmut_32
}

def redact_url_credentials(*args, **kwargs):
    result = _mutmut_trampoline(x_redact_url_credentials__mutmut_orig, x_redact_url_credentials__mutmut_mutants, args, kwargs)
    return result 

redact_url_credentials.__signature__ = _mutmut_signature(x_redact_url_credentials__mutmut_orig)
x_redact_url_credentials__mutmut_orig.__name__ = 'x_redact_url_credentials'


_URI_CREDENTIAL_RE = re.compile(r"(?P<scheme>[a-zA-Z][a-zA-Z0-9+.-]*://)(?P<secret>[^@\s]+)@")


def x_redact_text_credentials__mutmut_orig(text: str | None) -> str:
    """Redact credentials embedded in any URLs present within *text*."""

    if text is None:
        return ""

    return _URI_CREDENTIAL_RE.sub(lambda match: f"{match.group('scheme')}***@", text)


def x_redact_text_credentials__mutmut_1(text: str | None) -> str:
    """Redact credentials embedded in any URLs present within *text*."""

    if text is not None:
        return ""

    return _URI_CREDENTIAL_RE.sub(lambda match: f"{match.group('scheme')}***@", text)


def x_redact_text_credentials__mutmut_2(text: str | None) -> str:
    """Redact credentials embedded in any URLs present within *text*."""

    if text is None:
        return "XXXX"

    return _URI_CREDENTIAL_RE.sub(lambda match: f"{match.group('scheme')}***@", text)


def x_redact_text_credentials__mutmut_3(text: str | None) -> str:
    """Redact credentials embedded in any URLs present within *text*."""

    if text is None:
        return ""

    return _URI_CREDENTIAL_RE.sub(None, text)


def x_redact_text_credentials__mutmut_4(text: str | None) -> str:
    """Redact credentials embedded in any URLs present within *text*."""

    if text is None:
        return ""

    return _URI_CREDENTIAL_RE.sub(lambda match: f"{match.group('scheme')}***@", None)


def x_redact_text_credentials__mutmut_5(text: str | None) -> str:
    """Redact credentials embedded in any URLs present within *text*."""

    if text is None:
        return ""

    return _URI_CREDENTIAL_RE.sub(text)


def x_redact_text_credentials__mutmut_6(text: str | None) -> str:
    """Redact credentials embedded in any URLs present within *text*."""

    if text is None:
        return ""

    return _URI_CREDENTIAL_RE.sub(lambda match: f"{match.group('scheme')}***@", )


def x_redact_text_credentials__mutmut_7(text: str | None) -> str:
    """Redact credentials embedded in any URLs present within *text*."""

    if text is None:
        return ""

    return _URI_CREDENTIAL_RE.sub(lambda match: None, text)


def x_redact_text_credentials__mutmut_8(text: str | None) -> str:
    """Redact credentials embedded in any URLs present within *text*."""

    if text is None:
        return ""

    return _URI_CREDENTIAL_RE.sub(lambda match: f"{match.group(None)}***@", text)


def x_redact_text_credentials__mutmut_9(text: str | None) -> str:
    """Redact credentials embedded in any URLs present within *text*."""

    if text is None:
        return ""

    return _URI_CREDENTIAL_RE.sub(lambda match: f"{match.group('XXschemeXX')}***@", text)


def x_redact_text_credentials__mutmut_10(text: str | None) -> str:
    """Redact credentials embedded in any URLs present within *text*."""

    if text is None:
        return ""

    return _URI_CREDENTIAL_RE.sub(lambda match: f"{match.group('SCHEME')}***@", text)

x_redact_text_credentials__mutmut_mutants : ClassVar[MutantDict] = {
'x_redact_text_credentials__mutmut_1': x_redact_text_credentials__mutmut_1, 
    'x_redact_text_credentials__mutmut_2': x_redact_text_credentials__mutmut_2, 
    'x_redact_text_credentials__mutmut_3': x_redact_text_credentials__mutmut_3, 
    'x_redact_text_credentials__mutmut_4': x_redact_text_credentials__mutmut_4, 
    'x_redact_text_credentials__mutmut_5': x_redact_text_credentials__mutmut_5, 
    'x_redact_text_credentials__mutmut_6': x_redact_text_credentials__mutmut_6, 
    'x_redact_text_credentials__mutmut_7': x_redact_text_credentials__mutmut_7, 
    'x_redact_text_credentials__mutmut_8': x_redact_text_credentials__mutmut_8, 
    'x_redact_text_credentials__mutmut_9': x_redact_text_credentials__mutmut_9, 
    'x_redact_text_credentials__mutmut_10': x_redact_text_credentials__mutmut_10
}

def redact_text_credentials(*args, **kwargs):
    result = _mutmut_trampoline(x_redact_text_credentials__mutmut_orig, x_redact_text_credentials__mutmut_mutants, args, kwargs)
    return result 

redact_text_credentials.__signature__ = _mutmut_signature(x_redact_text_credentials__mutmut_orig)
x_redact_text_credentials__mutmut_orig.__name__ = 'x_redact_text_credentials'


def x_chunked__mutmut_orig(iterable: Iterable[Any], *, size: int) -> Iterable[list[Any]]:
    """Yield items from *iterable* in fixed-size chunks."""

    chunk: list[Any] = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) >= size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def x_chunked__mutmut_1(iterable: Iterable[Any], *, size: int) -> Iterable[list[Any]]:
    """Yield items from *iterable* in fixed-size chunks."""

    chunk: list[Any] = None
    for item in iterable:
        chunk.append(item)
        if len(chunk) >= size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def x_chunked__mutmut_2(iterable: Iterable[Any], *, size: int) -> Iterable[list[Any]]:
    """Yield items from *iterable* in fixed-size chunks."""

    chunk: list[Any] = []
    for item in iterable:
        chunk.append(None)
        if len(chunk) >= size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def x_chunked__mutmut_3(iterable: Iterable[Any], *, size: int) -> Iterable[list[Any]]:
    """Yield items from *iterable* in fixed-size chunks."""

    chunk: list[Any] = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) > size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def x_chunked__mutmut_4(iterable: Iterable[Any], *, size: int) -> Iterable[list[Any]]:
    """Yield items from *iterable* in fixed-size chunks."""

    chunk: list[Any] = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) >= size:
            yield chunk
            chunk = None
    if chunk:
        yield chunk

x_chunked__mutmut_mutants : ClassVar[MutantDict] = {
'x_chunked__mutmut_1': x_chunked__mutmut_1, 
    'x_chunked__mutmut_2': x_chunked__mutmut_2, 
    'x_chunked__mutmut_3': x_chunked__mutmut_3, 
    'x_chunked__mutmut_4': x_chunked__mutmut_4
}

def chunked(*args, **kwargs):
    result = _mutmut_trampoline(x_chunked__mutmut_orig, x_chunked__mutmut_mutants, args, kwargs)
    return result 

chunked.__signature__ = _mutmut_signature(x_chunked__mutmut_orig)
x_chunked__mutmut_orig.__name__ = 'x_chunked'
