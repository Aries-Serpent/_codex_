"""Canonical codex verify compatibility facade."""

from pathlib import Path

from aries_serpent_core.verify import ComparisonResult, compare, generate_tests


def verify_snapshot(
    baseline: str | Path,
    patched: str | Path | None = None,
    **kwargs,
):
    """Compatibility helper for legacy verify_snapshot callers."""
    baseline_path = Path(baseline)
    patched_path = Path(patched) if patched is not None else baseline_path
    return compare(baseline_path, patched_path, **kwargs)


__all__ = ["ComparisonResult", "compare", "generate_tests", "verify_snapshot"]
