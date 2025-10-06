"""Utilities for establishing deterministic seeds in lightweight training loops."""

from __future__ import annotations

from typing import Optional

from codex_ml.utils.repro import set_seed as _set_seed

_DEFAULT_SEED = 42


def ensure_global_seed(seed: Optional[int] = None, *, deterministic: bool = True) -> int:
    """Resolve ``seed`` to an integer and propagate it via :func:`set_seed`.

    Parameters
    ----------
    seed:
        Optional user-provided seed. When ``None`` a sensible default is used so
        call sites can simply invoke :func:`ensure_global_seed()` to obtain a
        reproducible configuration.
    deterministic:
        Forwarded to :func:`codex_ml.utils.repro.set_seed` to toggle deterministic
        backend behaviour.

    Returns
    -------
    int
        The resolved seed value. Returning the seed makes it trivial for callers
        to persist the decision alongside checkpoints or logs.
    """

    resolved = int(seed) if seed is not None else _DEFAULT_SEED
    _set_seed(resolved, deterministic=deterministic)
    return resolved


__all__ = ["ensure_global_seed"]
