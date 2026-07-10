"""
Semantic Assertion Utilities for Phase 5 Track 3 Test Coverage Maximization.

This module provides high-level semantic assertion helpers that replace bare
assertTrue/assertEqual with meaningful, diagnostic assertions that include
context about what was tested and why the assertion matters.

Usage:
    from tests.conftest_semantic_assertions import (
        assert_valid_numeric_type,
        assert_boundary_condition,
        assert_collection_not_empty,
        assert_error_message_contains
    )
"""

from __future__ import annotations

import sys
import math
from typing import Any, Callable, Iterable, Optional, Type, Union


# ============================================================================
# NUMERIC ASSERTIONS
# ============================================================================


def assert_valid_numeric_type(
    value: Any,
    expected_type: Type[Union[int, float]],
    *,
    context: str = "",
    allow_none: bool = False,
) -> None:
    """
    Assert value is of valid numeric type with diagnostic context.

    Args:
        value: Value to check
        expected_type: Expected type (int or float)
        context: Optional context string describing what this numeric value represents
        allow_none: Whether None is acceptable

    Raises:
        AssertionError: If type check fails with diagnostic information

    Example:
        >>> assert_valid_numeric_type(42, int, context="user_id")
        >>> assert_valid_numeric_type(3.14, float, context="learning_rate")
    """
    if value is None:
        if allow_none:
            return
        raise AssertionError(
            f"Expected {expected_type.__name__} for {context}, got None (null value)"
        )

    if not isinstance(value, expected_type):
        raise AssertionError(
            f"Type mismatch for {context}: expected {expected_type.__name__}, "
            f"got {type(value).__name__} (value={value!r})"
        )


def assert_numeric_in_range(
    value: float,
    min_value: float = float("-inf"),
    max_value: float = float("inf"),
    *,
    context: str = "",
    inclusive: bool = True,
) -> None:
    """
    Assert numeric value is within specified range.

    Args:
        value: Value to check
        min_value: Minimum acceptable value (default: negative infinity)
        max_value: Maximum acceptable value (default: positive infinity)
        context: Optional context describing what this range represents
        inclusive: Whether range bounds are inclusive (default: True)

    Raises:
        AssertionError: If value is outside range with diagnostic information

    Example:
        >>> assert_numeric_in_range(0.85, 0.0, 1.0, context="confidence_score")
        >>> assert_numeric_in_range(learning_rate, 1e-5, 0.1, context="learning_rate")
    """
    comparison_str = "<=" if inclusive else "<"
    comparison_op = (lambda a, b: a <= b) if inclusive else (lambda a, b: a < b)

    if not (min_value <= value <= max_value if inclusive else (min_value < value < max_value)):
        raise AssertionError(
            f"Value out of range for {context}: {min_value} {comparison_str} {value} "
            f"{comparison_str} {max_value} (violated at value={value})"
        )


def assert_positive(value: float, *, context: str = "") -> None:
    """
    Assert value is strictly positive (> 0).

    Args:
        value: Value to check
        context: Optional context describing what this value represents

    Raises:
        AssertionError: If value is not positive

    Example:
        >>> assert_positive(loss, context="training_loss")
    """
    if value <= 0:
        raise AssertionError(
            f"Value must be positive for {context}: got {value} (≤ 0)"
        )


def assert_non_negative(value: float, *, context: str = "") -> None:
    """
    Assert value is non-negative (>= 0).

    Args:
        value: Value to check
        context: Optional context describing what this value represents

    Raises:
        AssertionError: If value is negative

    Example:
        >>> assert_non_negative(accuracy, context="model_accuracy")
    """
    if value < 0:
        raise AssertionError(
            f"Value must be non-negative for {context}: got {value} (< 0)"
        )


def assert_floats_approximately_equal(
    actual: float,
    expected: float,
    *,
    tolerance: float = 1e-7,
    relative: bool = False,
    context: str = "",
) -> None:
    """
    Assert two floats are approximately equal with diagnostic precision info.

    Args:
        actual: Actual value
        expected: Expected value
        tolerance: Absolute or relative tolerance
        relative: Whether tolerance is relative (percentage) or absolute
        context: Optional context describing what's being compared

    Raises:
        AssertionError: If values differ beyond tolerance with precision info

    Example:
        >>> assert_floats_approximately_equal(
        ...     math.sin(math.pi), 0.0,
        ...     tolerance=1e-10, context="sin(π) should be ~0"
        ... )
    """
    if relative:
        # Relative tolerance: |a - b| / max(|a|, |b|)
        denominator = max(abs(actual), abs(expected), 1.0)
        diff_pct = abs(actual - expected) / denominator
        if diff_pct > tolerance:
            raise AssertionError(
                f"Float mismatch for {context}: {actual} vs {expected} "
                f"(relative diff {diff_pct:.2%} > tolerance {tolerance:.2%})"
            )
    else:
        # Absolute tolerance
        diff = abs(actual - expected)
        if diff > tolerance:
            raise AssertionError(
                f"Float mismatch for {context}: {actual} vs {expected} "
                f"(absolute diff {diff} > tolerance {tolerance})"
            )


# ============================================================================
# COLLECTION ASSERTIONS
# ============================================================================


def assert_collection_not_empty(
    collection: Iterable,
    *,
    context: str = "",
    collection_type: str = "collection",
) -> None:
    """
    Assert collection is not empty with type information.

    Args:
        collection: Collection to check
        context: Optional context describing what the collection contains
        collection_type: Human-readable type name (list, dict, set, etc.)

    Raises:
        AssertionError: If collection is empty

    Example:
        >>> assert_collection_not_empty(results, context="query_results", collection_type="list")
    """
    if isinstance(collection, (list, tuple, set, frozenset)):
        is_empty = len(collection) == 0
    elif isinstance(collection, dict):
        is_empty = len(collection) == 0
    else:
        # Try to convert to list for iteration check
        try:
            is_empty = not any(True for _ in collection)
        except TypeError:
            raise AssertionError(
                f"Cannot determine if {collection_type} is empty for {context}: "
                f"object is not iterable"
            )

    if is_empty:
        raise AssertionError(
            f"Expected non-empty {collection_type} for {context}, "
            f"but {collection_type} is empty"
        )


def assert_collection_length(
    collection: Iterable,
    expected_length: int,
    *,
    context: str = "",
    comparison: str = "==",
) -> None:
    """
    Assert collection has expected length with comparison operator.

    Args:
        collection: Collection to check
        expected_length: Expected length
        context: Optional context describing the collection
        comparison: Comparison operator ("==", ">=", "<=", ">", "<")

    Raises:
        AssertionError: If length check fails

    Example:
        >>> assert_collection_length(results, 10, context="page_results", comparison="==")
        >>> assert_collection_length(errors, 0, context="validation_errors", comparison="==")
    """
    try:
        actual_length = len(collection)
    except TypeError:
        raise AssertionError(
            f"Cannot determine length of {context}: object has no len()"
        )

    operators = {
        "==": lambda a, b: a == b,
        ">=": lambda a, b: a >= b,
        "<=": lambda a, b: a <= b,
        ">": lambda a, b: a > b,
        "<": lambda a, b: a < b,
    }

    if comparison not in operators:
        raise ValueError(
            f"Invalid comparison operator: {comparison}. "
            f"Must be one of: {', '.join(operators.keys())}"
        )

    if not operators[comparison](actual_length, expected_length):
        raise AssertionError(
            f"Length mismatch for {context}: expected {comparison} {expected_length}, "
            f"got {actual_length} (collection has {actual_length} items)"
        )


def assert_all_elements_satisfy(
    collection: Iterable,
    predicate: Callable[[Any], bool],
    *,
    context: str = "",
    predicate_name: str = "condition",
) -> None:
    """
    Assert all elements in collection satisfy predicate with diagnostic info.

    Args:
        collection: Collection to check
        predicate: Function returning True for valid elements
        context: Optional context describing the collection
        predicate_name: Human-readable name of the condition

    Raises:
        AssertionError: If any element fails predicate with failing element info

    Example:
        >>> assert_all_elements_satisfy(
        ...     results,
        ...     lambda x: x > 0,
        ...     context="test_scores",
        ...     predicate_name="positive score"
        ... )
    """
    for i, element in enumerate(collection):
        if not predicate(element):
            raise AssertionError(
                f"Not all elements satisfy {predicate_name} for {context}: "
                f"element at index {i} failed (value={element!r})"
            )


# ============================================================================
# TYPE AND VALUE ASSERTIONS
# ============================================================================


def assert_not_none(value: Any, *, context: str = "") -> None:
    """
    Assert value is not None with context.

    Args:
        value: Value to check
        context: Optional context describing what should not be None

    Raises:
        AssertionError: If value is None

    Example:
        >>> assert_not_none(result, context="database_query_result")
    """
    if value is None:
        raise AssertionError(f"Expected non-None value for {context}, got None")


def assert_instance_of(
    value: Any,
    expected_type: Type,
    *,
    context: str = "",
) -> None:
    """
    Assert value is instance of expected type.

    Args:
        value: Value to check
        expected_type: Expected type
        context: Optional context describing what's being checked

    Raises:
        AssertionError: If type check fails

    Example:
        >>> assert_instance_of(result, dict, context="API_response")
    """
    if not isinstance(value, expected_type):
        raise AssertionError(
            f"Type mismatch for {context}: expected {expected_type.__name__}, "
            f"got {type(value).__name__} (value={value!r})"
        )


def assert_string_not_empty(value: str, *, context: str = "") -> None:
    """
    Assert string is not empty and contains meaningful content.

    Args:
        value: String to check
        context: Optional context describing what the string represents

    Raises:
        AssertionError: If string is empty or None

    Example:
        >>> assert_string_not_empty(error_message, context="error_message")
    """
    if not isinstance(value, str):
        raise AssertionError(
            f"Expected string for {context}, got {type(value).__name__}"
        )
    if not value or not value.strip():
        raise AssertionError(
            f"Expected non-empty string for {context}, "
            f"got empty or whitespace-only string"
        )


# ============================================================================
# ERROR AND EXCEPTION ASSERTIONS
# ============================================================================


def assert_error_message_contains(
    exception: Exception,
    expected_phrases: Union[str, list[str]],
    *,
    context: str = "",
    case_sensitive: bool = False,
) -> None:
    """
    Assert exception message contains expected phrase(s).

    Args:
        exception: Exception to check
        expected_phrases: String or list of strings that should appear in message
        context: Optional context describing what error was expected
        case_sensitive: Whether to match case-sensitively

    Raises:
        AssertionError: If expected phrase(s) not found in exception message

    Example:
        >>> try:
        ...     function_that_should_fail()
        ... except ValueError as e:
        ...     assert_error_message_contains(
        ...         e, ["invalid", "value"],
        ...         context="invalid input validation"
        ...     )
    """
    if isinstance(expected_phrases, str):
        expected_phrases = [expected_phrases]

    message = str(exception)
    if not case_sensitive:
        message = message.lower()
        expected_phrases = [p.lower() for p in expected_phrases]

    for phrase in expected_phrases:
        if phrase not in message:
            raise AssertionError(
                f"Exception message for {context} does not contain '{phrase}': "
                f"got '{message}'"
            )


def assert_exception_raised(
    callable_obj: Callable,
    expected_exception: Type[Exception],
    *,
    context: str = "",
    expected_message: Optional[str] = None,
) -> Exception:
    """
    Assert that calling callable raises expected exception.

    Args:
        callable_obj: Callable that should raise
        expected_exception: Expected exception type
        context: Optional context describing what should fail
        expected_message: Optional expected message substring

    Returns:
        The raised exception

    Raises:
        AssertionError: If no exception raised or wrong type

    Example:
        >>> exc = assert_exception_raised(
        ...     lambda: int("not_a_number"),
        ...     ValueError,
        ...     context="string to int conversion"
        ... )
    """
    try:
        result = callable_obj()
        raise AssertionError(
            f"Expected {expected_exception.__name__} to be raised for {context}, "
            f"but no exception was raised (got {result!r})"
        )
    except expected_exception as e:
        if expected_message and expected_message not in str(e):
            raise AssertionError(
                f"Exception for {context} has wrong message. "
                f"Expected substring '{expected_message}', "
                f"got '{str(e)}'"
            )
        return e
    except Exception as e:
        raise AssertionError(
            f"Expected {expected_exception.__name__} for {context}, "
            f"but got {type(e).__name__}: {str(e)}"
        )


# ============================================================================
# BOUNDARY CONDITION ASSERTIONS
# ============================================================================


def assert_boundary_condition(
    actual: Any,
    boundary_value: Any,
    comparison: Callable[[Any, Any], bool],
    *,
    context: str = "",
    boundary_name: str = "boundary",
) -> None:
    """
    Assert value satisfies boundary condition with diagnostic info.

    Args:
        actual: Actual value
        boundary_value: Boundary value to compare against
        comparison: Binary predicate function (e.g., lambda a, b: a > b)
        context: Optional context describing the boundary test
        boundary_name: Human-readable name of the boundary

    Raises:
        AssertionError: If boundary condition not satisfied

    Example:
        >>> assert_boundary_condition(
        ...     actual_count, max_limit,
        ...     lambda a, b: a <= b,
        ...     context="query_results",
        ...     boundary_name="maximum result limit"
        ... )
    """
    if not comparison(actual, boundary_value):
        raise AssertionError(
            f"Boundary condition '{boundary_name}' failed for {context}: "
            f"actual={actual}, boundary={boundary_value}"
        )


def assert_zero_boundary(
    value: Union[int, float],
    expected_is_zero: bool = False,
    *,
    context: str = "",
) -> None:
    """
    Assert value is or is not zero (zero boundary condition).

    Args:
        value: Value to check
        expected_is_zero: Whether value should be zero
        context: Optional context describing what's being checked

    Raises:
        AssertionError: If zero boundary not satisfied

    Example:
        >>> assert_zero_boundary(result, expected_is_zero=True, context="division_by_zero_result")
    """
    is_zero = value == 0
    if is_zero != expected_is_zero:
        if expected_is_zero:
            raise AssertionError(
                f"Expected zero for {context}, got {value} (non-zero)"
            )
        else:
            raise AssertionError(
                f"Expected non-zero for {context}, got {value} (zero)"
            )


# ============================================================================
# MATHEMATICAL ASSERTIONS
# ============================================================================


def assert_nan_detection(value: float, expected_nan: bool = True, *, context: str = "") -> None:
    """
    Assert value is or is not NaN.

    Args:
        value: Float value to check
        expected_nan: Whether value should be NaN
        context: Optional context describing what's being checked

    Raises:
        AssertionError: If NaN check fails

    Example:
        >>> assert_nan_detection(result, expected_nan=False, context="computation_result")
    """
    is_nan = math.isnan(value) if isinstance(value, float) else False
    if is_nan != expected_nan:
        if expected_nan:
            raise AssertionError(
                f"Expected NaN for {context}, got {value} (valid number)"
            )
        else:
            raise AssertionError(
                f"Expected non-NaN for {context}, got NaN"
            )


def assert_infinity_detection(
    value: float,
    expected_inf: bool = False,
    *,
    positive_only: bool = True,
    context: str = "",
) -> None:
    """
    Assert value is or is not infinity.

    Args:
        value: Float value to check
        expected_inf: Whether value should be infinity
        positive_only: If True, only check for positive infinity; if False, check for any infinity
        context: Optional context describing what's being checked

    Raises:
        AssertionError: If infinity check fails

    Example:
        >>> assert_infinity_detection(result, expected_inf=False, context="division_result")
    """
    if isinstance(value, float):
        if positive_only:
            is_inf = math.isinf(value) and value > 0
        else:
            is_inf = math.isinf(value)
    else:
        is_inf = False

    if is_inf != expected_inf:
        if expected_inf:
            raise AssertionError(
                f"Expected infinity for {context}, got {value}"
            )
        else:
            raise AssertionError(
                f"Expected finite value for {context}, got infinity"
            )


# ============================================================================
# STATE AND TRANSITION ASSERTIONS
# ============================================================================


def assert_state_transition_valid(
    current_state: str,
    next_state: str,
    valid_transitions: dict[str, list[str]],
    *,
    context: str = "",
) -> None:
    """
    Assert state transition is valid according to state machine rules.

    Args:
        current_state: Current state
        next_state: Proposed next state
        valid_transitions: Dict mapping states to list of valid next states
        context: Optional context describing the state machine

    Raises:
        AssertionError: If transition is invalid

    Example:
        >>> valid_transitions = {
        ...     "pending": ["running", "cancelled"],
        ...     "running": ["completed", "failed"],
        ...     "completed": [],
        ... }
        >>> assert_state_transition_valid(
        ...     "pending", "running", valid_transitions,
        ...     context="task_lifecycle"
        ... )
    """
    if current_state not in valid_transitions:
        raise AssertionError(
            f"Unknown current state '{current_state}' for {context}"
        )

    if next_state not in valid_transitions[current_state]:
        raise AssertionError(
            f"Invalid state transition for {context}: "
            f"'{current_state}' → '{next_state}' not allowed "
            f"(valid: {valid_transitions[current_state]})"
        )


# ============================================================================
# PERFORMANCE/RESOURCE ASSERTIONS
# ============================================================================


def assert_execution_time_within_bounds(
    actual_time: float,
    max_time: float,
    *,
    context: str = "",
    unit: str = "seconds",
) -> None:
    """
    Assert execution time is within acceptable bounds.

    Args:
        actual_time: Actual execution time
        max_time: Maximum acceptable time
        context: Optional context describing what was timed
        unit: Time unit (seconds, ms, etc.)

    Raises:
        AssertionError: If execution time exceeds limit

    Example:
        >>> import time
        >>> start = time.time()
        >>> operation()
        >>> elapsed = time.time() - start
        >>> assert_execution_time_within_bounds(
        ...     elapsed, 1.0, context="database_query", unit="seconds"
        ... )
    """
    if actual_time > max_time:
        raise AssertionError(
            f"Execution time exceeded limit for {context}: "
            f"{actual_time:.3f}{unit} > {max_time:.3f}{unit}"
        )


def assert_memory_efficient(
    object_size: int,
    max_size_bytes: int,
    *,
    context: str = "",
) -> None:
    """
    Assert object size is within acceptable memory bounds.

    Args:
        object_size: Size of object in bytes
        max_size_bytes: Maximum acceptable size in bytes
        context: Optional context describing the object

    Raises:
        AssertionError: If object exceeds size limit

    Example:
        >>> import sys
        >>> data = list(range(1000))
        >>> size = sys.getsizeof(data)
        >>> assert_memory_efficient(size, 1024*1024, context="cached_data")
    """
    if object_size > max_size_bytes:
        mb_size = object_size / (1024 * 1024)
        mb_limit = max_size_bytes / (1024 * 1024)
        raise AssertionError(
            f"Memory usage exceeded limit for {context}: "
            f"{mb_size:.2f}MB > {mb_limit:.2f}MB"
        )
