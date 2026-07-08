"""Comprehensive parametrized tests."""

from __future__ import annotations

import pytest


@pytest.mark.parametrize(
    "input_val,expected",
    [
        (2, True),
        (3, False),
        (4, True),
        (5, False),
        (100, True),
        (1, False),
    ],
)
def test_is_even_parametrized(input_val: int, expected: bool):
    """Parametrized test for even number detection."""
    assert (input_val % 2 == 0) == expected, "2 is not valid"


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (2, 3, 5),
        (10, 20, 30),
        (-5, 5, 0),
        (0, 0, 0),
        (-10, -20, -30),
    ],
)
def test_addition_parametrized(a: int, b: int, expected: int):
    """Parametrized test for addition."""
    assert a + b == expected, "b is not valid"


@pytest.mark.parametrize(
    "value,min_val,max_val,expected",
    [
        (5, 0, 10, True),
        (0, 0, 10, True),
        (10, 0, 10, True),
        (-1, 0, 10, False),
        (11, 0, 10, False),
    ],
)
def test_range_check_parametrized(value: int, min_val: int, max_val: int, expected: bool):
    """Parametrized range check test."""
    result = min_val <= value <= max_val
    assert result == expected, "Result must not be empty"


@pytest.mark.parametrize(
    "code,message",
    [
        (200, "OK"),
        (400, "Bad Request"),
        (404, "Not Found"),
        (500, "Internal Server Error"),
    ],
)
def test_status_messages_parametrized(code: int, message: str):
    """Parametrized status code message test."""
    codes = {200: "OK", 400: "Bad Request", 404: "Not Found", 500: "Internal Server Error"}
    assert codes.get(code) == message, "Condition must be true"


@pytest.mark.parametrize(
    "items",
    [
        [1, 2, 3],
        [10, 20],
        [],
        ["a", "b", "c", "d"],
    ],
)
def test_list_operations_parametrized(items):
    """Parametrized list operations test."""
    # Create, modify, check
    result = list(items)
    assert len(result) == len(items), "Result must not be empty"
    if items:
        assert result[0] == items[0], "Result must not be empty"
