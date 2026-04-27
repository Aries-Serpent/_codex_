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
"""Cloud events integration for multi-cloud support."""

__all__ = [
    "Event",
    "EventType",
    "EventPublisher",
    "EventSubscriber",
    "EventBus",
]

from .base import Event, EventBus, EventPublisher, EventSubscriber, EventType

__all__ += [
    "AzureEventPublisher",
    "AWSEventPublisher",
    "TrainingEventEmitter",
    "get_optional_event_publishers",
]

try:
    from .azure_events import AzureEventPublisher
except ImportError as e:
    logger.debug(f"ImportError: {e}")
    logger.warning(f"ImportError: {e}", exc_info=True)
    AzureEventPublisher = None  # type: ignore[assignment,misc]

try:
    from .aws_events import AWSEventPublisher
except ImportError as e:
    logger.debug(f"ImportError: {e}")
    logger.warning(f"ImportError: {e}", exc_info=True)
    AWSEventPublisher = None  # type: ignore[assignment,misc]


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
