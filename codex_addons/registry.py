"""
General-purpose factory registry with stable ordering.

Provides a consistent API for registering and resolving components
across the codex_addons plugin system.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Generic, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class Registry(Generic[T]):
    """Generic factory registry with stable ordering and idempotent registration.

    Example:
        >>> registry = Registry(kind="metrics")
        >>> @registry.register("accuracy")
        ... def my_accuracy(preds, labels):
        ...     return sum(p == l for p, l in zip(preds, labels)) / len(labels)
        >>>
        >>> # List registered names (stable order)
        >>> registry.list()
        ['accuracy']
        >>>
        >>> # Get registered function
        >>> fn = registry.get("accuracy")
    """

    def __init__(self, kind: str):
        """Initialize a new registry.

        Args:
            kind: Registry kind/category (e.g., 'metrics', 'models')
        """
        self.kind = kind
        self._registry: dict[str, T] = {}
        self._registration_order: list[str] = []
        logger.debug(f"Created registry for '{kind}'")

    def register(self, name: str, item: T | None = None) -> Callable[[T], T]:
        """Register an item in the registry (idempotent).

        Can be used as a decorator or called directly.

        Args:
            name: Name to register under
            item: Item to register (optional if used as decorator)

        Returns:
            The registered item (for decorator use)

        Example:
            >>> registry = Registry(kind="test")
            >>> @registry.register("my_func")
            ... def my_func():
            ...     pass
            >>>
            >>> # Or direct registration
            >>> registry.register("other_func", lambda: 42)
        """

        def _register(obj: T) -> T:
            if name in self._registry:
                if self._registry[name] is obj:
                    # Idempotent: same object, same name - no-op
                    logger.debug(
                        f"Registry '{self.kind}': '{name}' already registered (idempotent)"
                    )
                else:
                    # Re-registration with different object - warn but allow
                    logger.warning(
                        f"Registry '{self.kind}': re-registering '{name}' "
                        f"(was {self._registry[name]}, now {obj})"
                    )
                    # Update order to maintain most recent
                    if name in self._registration_order:
                        self._registration_order.remove(name)
                    self._registration_order.append(name)
            else:
                # New registration
                self._registration_order.append(name)
                logger.debug(f"Registry '{self.kind}': registered '{name}'")

            self._registry[name] = obj
            return obj

        if item is not None:
            # Direct call: register(name, item)
            return _register(item)
        # Decorator: @register(name)
        return _register

    def get(self, name: str, default: T | None = None) -> T | None:
        """Get a registered item by name.

        Args:
            name: Name to look up
            default: Default value if not found

        Returns:
            The registered item, or default if not found
        """
        return self._registry.get(name, default)

    def list(self) -> list[str]:
        """List all registered names in stable order.

        Names are returned in registration order (stable across runs).

        Returns:
            List of registered names
        """
        # Return a copy in registration order (stable, deterministic)
        return sorted(self._registration_order)

    def names(self) -> list[str]:
        """Alias for list() - returns registered names in stable order.

        Returns:
            List of registered names
        """
        return self.list()

    def items(self) -> list[tuple[str, T]]:
        """Get all registered items as (name, item) pairs in stable order.

        Returns:
            List of (name, item) tuples in stable order
        """
        return [(name, self._registry[name]) for name in self.list()]

    def __contains__(self, name: str) -> bool:
        """Check if a name is registered.

        Args:
            name: Name to check

        Returns:
            True if name is registered
        """
        return name in self._registry

    def __len__(self) -> int:
        """Get number of registered items.

        Returns:
            Number of registered items
        """
        return len(self._registry)

    def __repr__(self) -> str:
        """String representation of registry.

        Returns:
            String representation showing kind and count
        """
        return f"Registry(kind='{self.kind}', count={len(self)})"


def create_registry(kind: str) -> Registry:
    """Factory function to create a new registry.

    Args:
        kind: Registry kind/category

    Returns:
        New Registry instance

    Example:
        >>> metrics_registry = create_registry("metrics")
        >>> metrics_registry.register("accuracy", my_accuracy_fn)
    """
    return Registry(kind=kind)
