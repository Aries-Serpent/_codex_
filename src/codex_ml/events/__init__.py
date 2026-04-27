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

__all__ += ["AzureEventPublisher", "AWSEventPublisher", "TrainingEventEmitter"]

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

# Keep optional publisher exports in an explicit registry so the module-level
# symbols are concretely referenced even when cloud-specific deps are absent.
OPTIONAL_EVENT_PUBLISHERS = {
    "azure": AzureEventPublisher,
    "aws": AWSEventPublisher,
}
