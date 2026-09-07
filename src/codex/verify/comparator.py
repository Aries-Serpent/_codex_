"""Compatibility wrapper for the legacy ``codex.verify.comparator`` import path."""

from aries_serpent_core.verify.comparator import (  # noqa: F401
    DEFAULT_FLAKINESS_RUNS,
    DEFAULT_TIMEOUT,
    ComparisonDetail,
    ComparisonMode,
    ComparisonResult,
    _coerce_mode,
    _compare_outputs,
    _hash_output,
    _normalize_output,
    _run_script,
    compare,
    generate_tests,
)

__all__ = [
    "DEFAULT_FLAKINESS_RUNS",
    "DEFAULT_TIMEOUT",
    "ComparisonDetail",
    "ComparisonMode",
    "ComparisonResult",
    "_coerce_mode",
    "_compare_outputs",
    "_hash_output",
    "_normalize_output",
    "_run_script",
    "compare",
    "generate_tests",
]
