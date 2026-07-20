"""Registry for RAG API implementations.

This module provides a registry system for managing multiple RAG API
implementations, allowing dynamic registration and retrieval of RAG APIs.
"""

from __future__ import annotations

import logging
from typing import Any, Type

from .base import BaseRagAPI

logger = logging.getLogger(__name__)


class RagAPIRegistry:
    """Registry for managing RAG API implementations.

    Provides a centralized registry for registering, retrieving, and
    instantiating RAG API implementations. Supports multiple implementations
    with different names and configurations.

    Attributes:
        _registry: Dictionary mapping API names to implementation classes
        _instances: Dictionary mapping API names to singleton instances
    """

    _registry: dict[str, Type[BaseRagAPI]] = {}
    _instances: dict[str, BaseRagAPI] = {}

    @classmethod
    def register(
        cls,
        name: str,
        api_class: Type[BaseRagAPI],
        force: bool = False,
    ) -> None:
        """Register a RAG API implementation.

        Args:
            name: Name to register the API under
            api_class: Class implementing BaseRagAPI
            force: If True, overwrite existing registration (default: False)

        Raises:
            ValueError: If name is already registered and force is False
        """
        if name in cls._registry and not force:
            raise ValueError(
                f"RAG API '{name}' is already registered. Use force=True to override."
            )

        if not issubclass(api_class, BaseRagAPI):
            raise TypeError(
                f"API class must inherit from BaseRagAPI, got {api_class.__name__}"
            )

        cls._registry[name] = api_class
        logger.debug(f"Registered RAG API: {name} -> {api_class.__name__}")

    @classmethod
    def get(
        cls,
        name: str,
        config: dict[str, Any] | None = None,
        singleton: bool = True,
    ) -> BaseRagAPI:
        """Retrieve or instantiate a RAG API.

        Args:
            name: Name of the RAG API to retrieve
            config: Optional configuration dictionary to pass to the API
            singleton: If True, return cached instance (default: True)

        Returns:
            Instance of the requested RAG API

        Raises:
            KeyError: If the API name is not registered
        """
        if name not in cls._registry:
            raise KeyError(f"RAG API '{name}' is not registered")

        if singleton and name in cls._instances:
            logger.debug(f"Returning cached instance of RAG API: {name}")
            return cls._instances[name]

        api_class = cls._registry[name]
        instance = api_class(name=name, config=config)

        if singleton:
            cls._instances[name] = instance
            logger.debug(f"Created and cached singleton instance: {name}")

        logger.debug(f"Retrieved RAG API: {name}")
        return instance

    @classmethod
    def list_registered(cls) -> list[str]:
        """List all registered RAG API names.

        Returns:
            List of registered API names
        """
        return list(cls._registry.keys())

    @classmethod
    def unregister(cls, name: str) -> None:
        """Unregister a RAG API implementation.

        Args:
            name: Name of the API to unregister

        Raises:
            KeyError: If the API name is not registered
        """
        if name not in cls._registry:
            raise KeyError(f"RAG API '{name}' is not registered")

        del cls._registry[name]
        if name in cls._instances:
            del cls._instances[name]

        logger.debug(f"Unregistered RAG API: {name}")

    @classmethod
    def clear(cls) -> None:
        """Clear all registered APIs and cached instances.

        Useful for testing and cleanup.
        """
        cls._registry.clear()
        cls._instances.clear()
        logger.debug("Cleared all RAG API registrations")
