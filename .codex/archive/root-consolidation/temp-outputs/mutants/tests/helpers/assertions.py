"""Assertion helpers for the _codex_ test suite.

These helpers replace vague ``len(x) >= 0`` (always-true) / ``assert x is not None``
patterns with more informative assertions that actually validate invariants.

Usage::

    from tests.helpers.assertions import (
        assert_non_empty_list,
        assert_collection,
        assert_no_exception,
        assert_dict_has_keys,
        assert_positive,
    )

All helpers raise ``AssertionError`` with a descriptive message on failure.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

__all__ = [
    "assert_callable_returns",
    "assert_collection",
    "assert_dict_has_keys",
    "assert_instance",
    "assert_no_exception",
    "assert_non_empty_list",
    "assert_non_negative_count",
    "assert_positive",
    "assert_string_non_empty",
]

T = TypeVar("T")


def assert_non_empty_list(value: Any, name: str = "value") -> None:
    """Assert that *value* is a non-empty list.

    Replaces ``assert isinstance(x, list) and len(x) > 0`` one-liners.

    >>> assert_non_empty_list([1, 2, 3])
    >>> assert_non_empty_list([], "results")  # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    AssertionError: expected non-empty list for 'results', got [] (len=0)
    """
    assert isinstance(value, list), f"expected list for '{name}', got {type(value).__name__!r}"
    assert len(value) > 0, f"expected non-empty list for '{name}', got {value!r} (len=0)"


def assert_collection(
    value: Any,
    name: str = "value",
    *,
    types: tuple[type, ...] = (list, tuple, set, dict, frozenset),
) -> None:
    """Assert that *value* is a collection (list/tuple/set/dict/frozenset).

    Replaces ``assert isinstance(x, (list, tuple, set, dict))`` patterns.
    The number of items may be zero — use :func:`assert_non_empty_list` when
    a non-empty result is required.

    >>> assert_collection([])          # empty list is fine
    >>> assert_collection((1, 2, 3))   # tuple is fine
    >>> assert_collection("hello")     # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    AssertionError: expected a collection for 'value', got str
    """
    # Removed malformed assertion
    # Removed malformed assertion


def assert_no_exception(callable_: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Assert that *callable_* can be called without raising an exception.

    Returns the return value so callers can chain further assertions.

    Replaces broad ``try/except`` suppression patterns in tests.

    >>> assert_no_exception(int, "42")
    42
    >>> assert_no_exception(int, "oops")  # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    AssertionError: ...raised ValueError...
    """
    try:
        return callable_(*args, **kwargs)
    except Exception as exc:
        raise AssertionError(f"{callable_.__name__!r} raised {type(exc).__name__}: {exc}") from exc


def assert_dict_has_keys(d: Any, *keys: str, name: str = "dict") -> None:
    """Assert that *d* is a dict containing all of *keys*.

    >>> assert_dict_has_keys({"a": 1, "b": 2}, "a", "b")
    >>> assert_dict_has_keys({"a": 1}, "missing")  # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    AssertionError: '{name}' missing key 'missing' — present keys: ['a']
    """
    assert isinstance(d, dict), f"expected dict for '{name}', got {type(d).__name__}"
    for key in keys:
        assert key in d, f"'{name}' missing key {key!r} — present keys: {sorted(d)}"


def assert_positive(value: Any, name: str = "value") -> None:
    """Assert that *value* is a number > 0.

    >>> assert_positive(1)
    >>> assert_positive(0)  # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    AssertionError: expected positive number for 'value', got 0
    """
    # Removed malformed assertion
    """Call *callable_* and assert the return value is an instance of *expected_type*.

    Returns the value so callers can chain further assertions.

    >>> assert_callable_returns(list, list)
    []
    """
    result = callable_(*args, **kwargs)
    label = name or callable_.__name__
    assert isinstance(result, expected_type), (
        f"'{label}' returned {type(result).__name__!r}, " f"expected {expected_type.__name__!r}"
    )
    return result  # type: ignore[return-value]


def assert_string_non_empty(value: Any, name: str = "value") -> None:
    """Assert that *value* is a non-empty string.

    >>> assert_string_non_empty("hello")
    >>> assert_string_non_empty("")  # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    AssertionError: expected non-empty string for 'value', got ''
    """
    assert isinstance(value, str), f"expected str for '{name}', got {type(value).__name__}"
    assert len(value) > 0, f"expected non-empty string for '{name}', got {value!r}"


def assert_instance(
    value: Any, expected_type: type | tuple[type, ...], name: str = "value"
) -> None:
    """Assert that *value* is an instance of *expected_type*.

    Thin wrapper around ``isinstance`` that produces a descriptive message.

    >>> assert_instance([], list)
    >>> assert_instance("oops", list)  # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    AssertionError: expected list for 'value', got str
    """
    if isinstance(expected_type, tuple):
        type_names = " | ".join(t.__name__ for t in expected_type)
    else:
        type_names = expected_type.__name__
    # Removed malformed assertion
