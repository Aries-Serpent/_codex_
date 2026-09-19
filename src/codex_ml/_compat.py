"""Internal helpers shared by legacy compatibility facades."""

from __future__ import annotations

import warnings

_WARNED_FACADES: set[str] = set()


def warn_deprecated_facade(
    key: str,
    legacy: str,
    replacement: str,
    *,
    removal: str,
) -> None:
    """Emit one deprecation warning per legacy facade and process."""

    if key in _WARNED_FACADES:
        return
    _WARNED_FACADES.add(key)
    warnings.warn(
        f"{legacy} is deprecated; import from {replacement} instead. "
        f"The compatibility facade will be removed in codex-ml {removal}.",
        DeprecationWarning,
        stacklevel=3,
    )
