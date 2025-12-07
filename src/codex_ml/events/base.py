"""Event system base classes and abstractions."""

from __future__ import annotations

import json
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

__all__ = [
    "EventType",
    "Event",
    "EventPublisher",
    "EventSubscriber",
    "EventBus",
]


class EventType(str, Enum):
    """Event types for ML lifecycle."""

    MODEL_TRAINING_STARTED = "model.training.started"
    MODEL_TRAINING_COMPLETED = "model.training.completed"
    MODEL_TRAINING_FAILED = "model.training.failed"
    MODEL_REGISTERED = "model.registered"
    MODEL_DEPLOYED = "model.deployed"
    MODEL_RETIRED = "model.retired"
    DRIFT_DETECTED = "drift.detected"
    DATASET_UPDATED = "dataset.updated"
    PIPELINE_STARTED = "pipeline.started"
    PIPELINE_COMPLETED = "pipeline.completed"
    PIPELINE_FAILED = "pipeline.failed"


@dataclass
class Event:
    """Event data structure.

    Attributes:
        event_type: Type of event
        source: Event source identifier
        data: Event payload
        event_id: Unique event identifier
        timestamp: Event timestamp
        metadata: Additional metadata
    """

    event_type: EventType
    source: str
    data: Dict[str, Any]
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        result = asdict(self)
        result["event_type"] = self.event_type.value
        return result

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


class EventPublisher(ABC):
    """Abstract event publisher."""

    @abstractmethod
    def publish(self, event: Event) -> bool:
        """Publish a single event.

        Args:
            event: Event to publish

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def publish_batch(self, events: List[Event]) -> bool:
        """Publish multiple events.

        Args:
            events: Events to publish

        Returns:
            True if successful
        """
        pass


class EventSubscriber(ABC):
    """Abstract event subscriber."""

    @abstractmethod
    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]):
        """Subscribe to events.

        Args:
            event_type: Event type to subscribe to
            callback: Callback function
        """
        pass

    @abstractmethod
    def unsubscribe(self, event_type: EventType):
        """Unsubscribe from events.

        Args:
            event_type: Event type to unsubscribe from
        """
        pass


class EventBus(EventPublisher, EventSubscriber):
    """Local in-memory event bus for testing and development."""

    def __init__(self):
        """Initialize event bus."""
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.event_history: List[Event] = []

    def publish(self, event: Event) -> bool:
        """Publish event to local subscribers.

        Args:
            event: Event to publish

        Returns:
            True if successful
        """
        self.event_history.append(event)

        callbacks = self.subscribers.get(event.event_type, [])
        for callback in callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in event callback: {e}")

        logger.info(f"Published event: {event.event_type.value} (id={event.event_id})")
        return True

    def publish_batch(self, events: List[Event]) -> bool:
        """Publish multiple events.

        Args:
            events: Events to publish

        Returns:
            True if successful
        """
        for event in events:
            self.publish(event)
        return True

    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]):
        """Subscribe to event type.

        Args:
            event_type: Event type
            callback: Callback function
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        logger.info(f"Subscribed to {event_type.value}")

    def unsubscribe(self, event_type: EventType):
        """Unsubscribe from event type.

        Args:
            event_type: Event type
        """
        if event_type in self.subscribers:
            del self.subscribers[event_type]
            logger.info(f"Unsubscribed from {event_type.value}")

    def get_history(self, event_type: Optional[EventType] = None) -> List[Event]:
        """Get event history.

        Args:
            event_type: Filter by event type (optional)

        Returns:
            List of events
        """
        if event_type:
            return [e for e in self.event_history if e.event_type == event_type]
        return self.event_history

    def clear_history(self):
        """Clear event history."""
        self.event_history.clear()
