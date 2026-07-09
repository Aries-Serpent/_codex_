"""
P016: Context Manager Utilities

Consolidates 673 occurrences of context manager patterns.

Example:
    # Instead of: with open(file) as f: ...
    with cleanup_on_exit(resource, cleanup_fn):
        use_resource()
"""

from contextlib import contextmanager
from typing import Any, Callable, List, TypeVar

__all__ = [
    "cleanup_on_exit",
    "ResourceContext",
    "MultiContext",
]

T = TypeVar("T")


@contextmanager
def cleanup_on_exit(resource: Any, cleanup_fn: Callable[[Any], None]):
    """
    Context manager that calls cleanup function on exit.

    Args:
        resource: Resource to manage
        cleanup_fn: Function to call on exit

    Example:
        >>> with cleanup_on_exit(conn, conn.close):
        ...     use_connection()
    """
    try:
        yield resource
    finally:
        cleanup_fn(resource)


class ResourceContext:
    """Base class for resource context managers."""

    def __enter__(self) -> "ResourceContext":
        """Enter context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context and cleanup."""
        self.cleanup()

    def cleanup(self) -> None:
        """Override to implement cleanup logic."""
        pass


class MultiContext:
    """Context manager for multiple resources."""

    def __init__(self, *contexts: Any):
        self.contexts = contexts
        self.entered = []

    def __enter__(self) -> List[Any]:
        """Enter all contexts."""
        self.entered = []
        for ctx in self.contexts:
            self.entered.append(ctx.__enter__())
        return self.entered

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit all contexts in reverse order."""
        for ctx in reversed(self.contexts):
            try:
                ctx.__exit__(exc_type, exc_val, exc_tb)
            except Exception:
                pass
