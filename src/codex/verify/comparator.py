"""Compatibility wrapper for the legacy ``codex.verify.comparator`` import path."""

from aries_serpent_core.verify.comparator import (
    ComparisonDetail,
    ComparisonMode,
    ComparisonResult,
    _coerce_mode,
    _compare_outputs,
    _hash_output,
    _normalize_output,
    compare,
    generate_tests,
)

__all__ = [
    "ComparisonDetail",
    "ComparisonMode",
    "ComparisonResult",
    "_coerce_mode",
    "_compare_outputs",
    "_hash_output",
    "_normalize_output",
    "compare",
    "generate_tests",
]
