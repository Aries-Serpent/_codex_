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
except ImportError:
    AzureEventPublisher = None  # type: ignore

try:
    from .aws_events import AWSEventPublisher
except ImportError:
    AWSEventPublisher = None  # type: ignore
