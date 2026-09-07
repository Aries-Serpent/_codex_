"""Canonical codex verify compatibility facade."""

from __future__ import annotations

from pathlib import Path

_pkg_root = Path(__file__).resolve().parent
_migrated_root = _pkg_root.parent.parent / "aries_serpent_core" / "verify"

__path__ = [str(_pkg_root)]
if _migrated_root.is_dir():
    __path__.append(str(_migrated_root))

from aries_serpent_core.verify import ComparisonMode, ComparisonResult, compare, generate_tests


def _coerce_mode(mode: ComparisonMode | str | None) -> ComparisonMode | None:
    if mode is None or isinstance(mode, ComparisonMode):
        return mode
    return ComparisonMode(mode.strip().casefold())


def verify_snapshot(
    baseline: str | Path,
    patched: str | Path | None = None,
    **kwargs,
):
    """Compatibility helper for legacy verify_snapshot callers."""
    baseline_path = Path(baseline)
    patched_path = Path(patched) if patched is not None else baseline_path
    mode = kwargs.get("mode")
    if mode is not None:
        kwargs["mode"] = _coerce_mode(mode)
    return compare(baseline_path, patched_path, **kwargs)


__all__ = ["ComparisonMode", "ComparisonResult", "compare", "generate_tests", "verify_snapshot"]
