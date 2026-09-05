"""Canonical codex verify compatibility facade."""

from pathlib import Path

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
