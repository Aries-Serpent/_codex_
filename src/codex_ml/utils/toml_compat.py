"""
toml_compat: small helper to abstract tomllib (Py>=3.11) vs tomli (Py<3.11).

Usage:
    from codex_ml.utils.toml_compat import load, loads

Notes:
- tomllib requires binary mode for load(); this wrapper handles it.
- Fallback to tomli if tomllib is unavailable.
"""

from __future__ import annotations

import logging
from typing import IO, Any

logger = logging.getLogger(__name__)

try:
    import tomllib as _toml  # Python >=3.11

    _BINARY_REQUIRED = True
except (IOError, OSError):  # pragma: no cover
    import tomli as _toml  # type: ignore

    _BINARY_REQUIRED = False


def load(fp: IO[bytes] | IO[str]) -> Any:
    """Parse a TOML file-like object and return the decoded data as a dict.

    Wraps ``tomllib.load`` (Python ≥ 3.11) or ``tomli.load`` transparently.
    The caller must open the file in **binary** mode when ``tomllib`` is used
    (Python ≥ 3.11); text-mode objects work with ``tomli``.

    Args:
        fp: A readable binary or text file-like object containing TOML data.

    Returns:
        Parsed TOML data as a :class:`dict`.
    """
    if _BINARY_REQUIRED:
        # Ensure binary mode for tomllib
        if hasattr(fp, "read") and isinstance(getattr(fp, "read", None), object):
            return _toml.load(fp)  # type: ignore[arg-type]
    return _toml.load(fp)  # type: ignore[arg-type]


def loads(s: str | bytes) -> Any:
    """Parse a TOML string or bytes object and return the decoded data as a dict.

    Accepts both ``str`` and ``bytes``; bytes are decoded as UTF-8 before
    parsing.

    Args:
        s: TOML-encoded string or UTF-8 bytes.

    Returns:
        Parsed TOML data as a :class:`dict`.
    """
    if isinstance(s, bytes):
        return _toml.loads(s.decode("utf-8"))
    return _toml.loads(s)
