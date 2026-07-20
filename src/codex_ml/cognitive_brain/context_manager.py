"""Context management for cognitive brain reasoning operations.

This module provides context storage and retrieval for reasoning engines
and other components that need to maintain state across reasoning operations.
"""

from __future__ import annotations

from typing import Any


class ContextManager:
    """Manages reasoning context for cognitive brain operations.

    Handles storage, retrieval, and lifecycle management of reasoning context.
    Provides mechanisms to persist and query context information during
    reasoning and decision-making processes.

    Attributes:
        _context (dict): Internal storage for context data
        _context_stack (list): Stack for nested context management
    """

    def __init__(self) -> None:
        """Initialize the ContextManager with empty context."""
        self._context: dict[str, Any] = {}
        self._context_stack: list[dict[str, Any]] = []

    def store_context(self, key: str, value: Any) -> None:
        """Store a value in the current reasoning context.

        Args:
            key: Identifier for the context value
            value: The value to store

        Returns:
            None
        """
        self._context[key] = value

    def retrieve_context(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from the current reasoning context.

        Args:
            key: Identifier of the context value
            default: Default value if key is not found

        Returns:
            The stored value or default if not found
        """
        return self._context.get(key, default)

    def clear_context(self) -> None:
        """Clear all context data.

        Removes all stored context, resetting to initial state.

        Returns:
            None
        """
        self._context.clear()
        self._context_stack.clear()

    def push_context(self) -> None:
        """Push current context onto the stack for nested contexts.

        Used for saving context state before entering nested reasoning
        operations.

        Returns:
            None
        """
        self._context_stack.append(self._context.copy())

    def pop_context(self) -> None:
        """Restore context from the stack.

        Restores the previously saved context state. Safe to call even
        if stack is empty (no-op in that case).

        Returns:
            None
        """
        if self._context_stack:
            self._context = self._context_stack.pop()

    def get_all_context(self) -> dict[str, Any]:
        """Get a copy of all current context data.

        Returns:
            Dictionary containing all current context
        """
        return self._context.copy()
