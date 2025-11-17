"""
toml_compat: small helper to abstract tomllib (Py>=3.11) vs tomli (Py<3.11).

Usage:
    from codex_ml.utils.toml_compat import load, loads

Notes:
- tomllib requires binary mode for load(); this wrapper handles it.
- Fallback to tomli if tomllib is unavailable.
"""

from __future__ import annotations

from typing import IO, Any

try:
    import tomllib as _toml  # Python >=3.11

    _BINARY_REQUIRED = True
except Exception:  # pragma: no cover
    import tomli as _toml  # type: ignore

    _BINARY_REQUIRED = False


def load(fp: IO[bytes] | IO[str]) -> Any:
    if _BINARY_REQUIRED:
        # Ensure binary mode for tomllib
        if hasattr(fp, "read") and isinstance(getattr(fp, "read", None), object):
            return _toml.load(fp)  # type: ignore[arg-type]
    return _toml.load(fp)  # type: ignore[arg-type]


def loads(s: str | bytes) -> Any:
    if isinstance(s, bytes):
        return _toml.loads(s.decode("utf-8"))
    return _toml.loads(s)
