# Branch Coverage Tests - Phase 14.4
"""
This package contains branch coverage tests for Phase 14.4.

Tests in this package intentionally exercise specific branches with
hard-coded inputs.  To prevent constant-propagation tools (CodeQL,
ruff) from flagging the unused branches as "unreachable code", value
inputs are routed through :func:`branch_input`, which is opaque to
static analysers but a no-op at runtime.
"""

from typing import TypeVar

_T = TypeVar("_T")


def branch_input(value: _T, /) -> _T:
    """Return *value* unchanged.

    Used to opaquify constant test inputs so static-analysis tools do
    not classify the unused branches in branch-coverage scenarios as
    unreachable.  The implementation deliberately routes the value
    through a mutable container so simple value tracking cannot fold
    it back to the original literal.
    """
    _box = [value]
    return _box.pop()


__all__ = ["branch_input"]
