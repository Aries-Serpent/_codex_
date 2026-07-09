"""
  Init   Module

This module provides functionality for   init  .

Usage:
    from events.__init__ import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

import logging

logger = logging.getLogger(__name__)

__all__ = [
    "Event",
    "EventBus",
    "EventPublisher",
    "EventSubscriber",
    "EventType",
]

from .base import Event, EventBus, EventPublisher, EventSubscriber, EventType

__all__ += [
    "AWSEventPublisher",
    "AzureEventPublisher",
    "TrainingEventEmitter",
    "get_optional_event_publishers",
]

try:
    from .azure_events import AzureEventPublisher
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
    AzureEventPublisher = None  # type: ignore[misc,assignment]

try:
    from .aws_events import AWSEventPublisher
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
    AWSEventPublisher = None  # type: ignore[misc,assignment]


def get_optional_event_publishers() -> dict[str, type[EventPublisher] | None]:
    """Return a provider-to-publisher map for optional cloud event integrations.

    The returned dictionary maps provider names such as ``"azure"`` and ``"aws"``
    to their corresponding :class:`EventPublisher` subclasses, or ``None`` when
    the provider-specific dependency is unavailable in the current environment.
    """

    return {
        "azure": AzureEventPublisher,
        "aws": AWSEventPublisher,
    }
