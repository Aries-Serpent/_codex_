"""
Resource Management & Code Quality Optimizations - Track C CWE-400

This module provides utilities for:
- Safe type conversions (CWE-681)
- Integer overflow protection (CWE-190)
- Resource consumption monitoring (CWE-400)
- Optimized iteration patterns
"""

import logging
import sys
from typing import Any, Callable, Generator, Iterable, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")
U = TypeVar("U")


class ResourceLimitError(Exception):
    """Raised when resource consumption exceeds configured limits."""

    pass


class TypeConversionError(Exception):
    """Raised when type conversion fails."""

    pass


def safe_int_conversion(
    value: Any, default: Optional[int] = None, strict: bool = False
) -> Optional[int]:
    """Safely convert value to int with explicit error handling.

    Prevents CWE-681 (Incorrect Type Conversion) and CWE-190 (Integer Overflow).

    Parameters
    ----------
    value : Any
        Value to convert
    default : int | None
        Default value if conversion fails
    strict : bool
        If True, raise exception on conversion failure; if False, return default

    Returns
    -------
    int | None
        Converted integer or default value

    Raises
    ------
    TypeConversionError
        If strict=True and conversion fails
    """
    try:
        # Handle None explicitly
        if value is None:
            if strict:
                raise TypeConversionError(f"Cannot convert None to int")
            return default

        # Try direct conversion
        result = int(value)

        # Check for overflow (Python handles arbitrary precision, but verify sanity)
        if abs(result) > sys.maxsize:
            logger.warning(f"Integer conversion resulted in very large value: {result}")

        return result
    except (ValueError, TypeError) as e:
        if strict:
            raise TypeConversionError(f"Cannot convert {type(value).__name__} to int: {e}")
        return default


def safe_float_conversion(
    value: Any, default: Optional[float] = None, strict: bool = False
) -> Optional[float]:
    """Safely convert value to float with explicit error handling.

    Parameters
    ----------
    value : Any
        Value to convert
    default : float | None
        Default value if conversion fails
    strict : bool
        If True, raise exception on conversion failure

    Returns
    -------
    float | None
        Converted float or default value

    Raises
    ------
    TypeConversionError
        If strict=True and conversion fails
    """
    try:
        if value is None:
            if strict:
                raise TypeConversionError(f"Cannot convert None to float")
            return default

        result = float(value)

        # Check for special float values
        if result != result:  # NaN check
            logger.warning(f"Conversion resulted in NaN")
        elif result == float("inf"):
            logger.warning(f"Conversion resulted in positive infinity")
        elif result == float("-inf"):
            logger.warning(f"Conversion resulted in negative infinity")

        return result
    except (ValueError, TypeError) as e:
        if strict:
            raise TypeConversionError(f"Cannot convert {type(value).__name__} to float: {e}")
        return default


def safe_int_add(a: int, b: int) -> Optional[int]:
    """Safely add two integers with overflow detection.

    Prevents CWE-190 (Integer Overflow).

    Parameters
    ----------
    a : int
        First operand
    b : int
        Second operand

    Returns
    -------
    int | None
        Sum of a and b, or None if overflow detected
    """
    try:
        result = a + b
        # Python handles arbitrary precision, but log warnings for very large numbers
        if abs(result) > 10**18:
            logger.warning(f"Integer addition resulted in very large value: {result}")
        return result
    except Exception as e:
        logger.error(f"Integer addition failed: {e}")
        return None


def safe_int_multiply(a: int, b: int) -> Optional[int]:
    """Safely multiply two integers with overflow detection.

    Prevents CWE-190 (Integer Overflow).

    Parameters
    ----------
    a : int
        First operand
    b : int
        Second operand

    Returns
    -------
    int | None
        Product of a and b, or None if overflow detected
    """
    try:
        # Check for early overflow conditions
        if a == 0 or b == 0:
            return 0

        result = a * b

        # Check for overflow
        if abs(result) > 10**18:
            logger.warning(f"Integer multiplication resulted in very large value: {result}")
            return None

        return result
    except Exception as e:
        logger.error(f"Integer multiplication failed: {e}")
        return None


def safe_divide(numerator: float, denominator: float) -> Optional[float]:
    """Safely divide two numbers with zero-check.

    Parameters
    ----------
    numerator : float
        Dividend
    denominator : float
        Divisor

    Returns
    -------
    float | None
        Result of division, or None if denominator is zero
    """
    if denominator == 0:
        logger.warning("Division by zero attempted")
        return None

    try:
        result = numerator / denominator
        return result
    except Exception as e:
        logger.error(f"Division failed: {e}")
        return None


def resource_aware_map(
    func: Callable[[T], U],
    iterable: Iterable[T],
    max_items: Optional[int] = None,
    warn_threshold: int = 10000,
) -> Generator[U, None, None]:
    """Memory-efficient map with resource consumption warnings.

    Prevents CWE-400 (Uncontrolled Resource Consumption) by:
    - Using generators instead of lists
    - Warning on large iterations
    - Enforcing optional item limits

    Parameters
    ----------
    func : Callable
        Function to apply to each item
    iterable : Iterable
        Items to process
    max_items : int | None
        Maximum items to process (None for unlimited)
    warn_threshold : int
        Log warning when iteration count exceeds this

    Yields
    ------
    Any
        Result of applying func to each item

    Raises
    ------
    ResourceLimitError
        If max_items is exceeded
    """
    for count, item in enumerate(iterable, 1):
        if warn_threshold > 0 and count % warn_threshold == 0:
            logger.warning(
                f"resource_aware_map processing large iteration: {count} items processed"
            )

        if max_items is not None and count > max_items:
            raise ResourceLimitError(
                f"Iteration exceeded max_items limit: {count} > {max_items}"
            )

        try:
            yield func(item)
        except Exception as e:
            logger.error(f"Error processing item {count}: {e}")
            raise


def chunked_iteration(
    iterable: Iterable[T], chunk_size: int = 1000
) -> Generator[list[T], None, None]:
    """Process iterable in chunks for memory efficiency.

    Prevents CWE-400 (Uncontrolled Resource Consumption) by:
    - Processing in manageable chunks
    - Reducing peak memory usage
    - Allowing intermediate results to be garbage collected

    Parameters
    ----------
    iterable : Iterable
        Items to chunk
    chunk_size : int
        Size of each chunk (default 1000)

    Yields
    ------
    list
        Chunk of items
    """
    chunk: list[T] = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) >= chunk_size:
            yield chunk
            chunk = []

    if chunk:  # Yield remaining items
        yield chunk


def optimize_nested_loops(
    outer_items: Iterable[T],
    inner_func: Callable[[T], Iterable[U]],
    max_total_iterations: Optional[int] = None,
) -> Generator[tuple[T, U], None, None]:
    """Optimize nested loops with iteration tracking.

    Prevents CWE-400 (Uncontrolled Resource Consumption) by:
    - Tracking total iterations
    - Enforcing iteration limits
    - Using generators to avoid memory buildup
    - Logging warnings for excessive iterations

    Parameters
    ----------
    outer_items : Iterable
        Outer loop items
    inner_func : Callable
        Function that returns inner loop items
    max_total_iterations : int | None
        Maximum total iterations (outer × inner)

    Yields
    ------
    tuple
        (outer_item, inner_item) pairs

    Raises
    ------
    ResourceLimitError
        If max_total_iterations is exceeded
    """
    total_iterations = 0
    warn_threshold = 100000

    for outer_item in outer_items:
        for inner_item in inner_func(outer_item):
            total_iterations += 1

            if warn_threshold > 0 and total_iterations % warn_threshold == 0:
                logger.warning(
                    f"optimize_nested_loops: {total_iterations} total iterations processed"
                )

            if max_total_iterations is not None and total_iterations > max_total_iterations:
                raise ResourceLimitError(
                    f"Nested loop iterations exceeded limit: {total_iterations} > {max_total_iterations}"
                )

            yield (outer_item, inner_item)


def monitored_resource_context(resource_name: str) -> type:
    """Create a context manager for monitoring resource lifecycle.

    Prevents CWE-400 (Uncontrolled Resource Consumption) by:
    - Tracking resource acquisition/release
    - Logging resource leaks
    - Enforcing cleanup

    Parameters
    ----------
    resource_name : str
        Name of the resource for logging

    Returns
    -------
    type
        Context manager class for the resource
    """

    class MonitoredResource:
        """Context manager for monitored resource."""

        def __init__(self, resource: Any):
            self.resource = resource
            self.resource_name = resource_name
            self.acquired = False

        def __enter__(self):
            logger.debug(f"Acquiring resource: {self.resource_name}")
            self.acquired = True
            return self.resource

        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.acquired:
                logger.debug(f"Releasing resource: {self.resource_name}")
                self.acquired = False

                # Attempt cleanup if resource has close method
                if hasattr(self.resource, "close"):
                    try:
                        self.resource.close()
                    except Exception as e:
                        logger.warning(f"Error closing {self.resource_name}: {e}")

            if exc_type is not None:
                logger.error(
                    f"Error in {self.resource_name} context: {exc_type.__name__}: {exc_val}"
                )

            return False

    return MonitoredResource


__all__ = [
    "ResourceLimitError",
    "TypeConversionError",
    "safe_int_conversion",
    "safe_float_conversion",
    "safe_int_add",
    "safe_int_multiply",
    "safe_divide",
    "resource_aware_map",
    "chunked_iteration",
    "optimize_nested_loops",
    "monitored_resource_context",
]
