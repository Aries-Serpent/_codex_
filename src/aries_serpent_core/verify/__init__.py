"""
Codex Verify Module

Behavior comparison and test generation for validating transformations.

Components:
- comparator: Compare baseline vs patched behavior
- test_gen: Generate tests from samples
- snapshot: Manage IO snapshots
"""

from __future__ import annotations

from pathlib import Path

from .comparator import ComparisonResult, compare, generate_tests


def verify_snapshot(
    baseline: str | Path,
    patched: str | Path | None = None,
    **kwargs,
):
    """Compatibility wrapper for older codex.verify.verify_snapshot callers."""
    baseline_path = Path(baseline)
    patched_path = Path(patched) if patched is not None else baseline_path
    return compare(baseline_path, patched_path, **kwargs)


__all__ = ["ComparisonResult", "compare", "generate_tests", "verify_snapshot"]
