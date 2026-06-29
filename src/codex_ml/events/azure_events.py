"""Azure Event Grid integration."""

from __future__ import annotations

import logging
import os
from typing import Optional

from .base import Event, EventPublisher

logger = logging.getLogger(__name__)

__all__ = ["AzureEventPublisher"]

try:
    from azure.core.credentials import AzureKeyCredential
    from azure.eventgrid import EventGridEvent, EventGridPublisherClient

    _HAS_AZURE = True
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
    _HAS_AZURE = False
    logger.warning("azure-eventgrid not installed. Azure Event Grid support disabled.")


class AzureEventPublisher(EventPublisher):
    """Azure Event Grid publisher."""

    def __init__(
        self,
        topic_endpoint: Optional[str] = None,
        topic_key: Optional[str] = None,
    ):
        """Initialize Azure Event Grid publisher.

        Args:
            topic_endpoint: Event Grid topic endpoint (or AZURE_EVENT_GRID_ENDPOINT env var)
            topic_key: Event Grid access key (or AZURE_EVENT_GRID_KEY env var)
        """
        if not _HAS_AZURE:
            raise ImportError(
                "azure-eventgrid package required for Azure Event Grid support. "
                "Install with: pip install azure-eventgrid"
            )

        self.topic_endpoint = topic_endpoint or os.getenv("AZURE_EVENT_GRID_ENDPOINT")
        self.topic_key = topic_key or os.getenv("AZURE_EVENT_GRID_KEY")

        if not self.topic_endpoint or not self.topic_key:
            logger.warning(
                "Azure Event Grid not configured. set AZURE_EVENT_GRID_ENDPOINT "
                "and AZURE_EVENT_GRID_KEY environment variables."
            )
            self.client = None
        else:
            self.client = self._create_client()

    def _create_client(self) -> EventGridPublisherClient:
        """Create Event Grid client.

        Returns:
            Event Grid publisher client
        """
        credential = AzureKeyCredential(self.topic_key)
        return EventGridPublisherClient(self.topic_endpoint, credential)

    def publish(self, event: Event) -> bool:
        """Publish event to Azure Event Grid.

        Args:
            event: Event to publish

        Returns:
            True if successful
        """
        if not self.client:
            logger.warning("Azure Event Grid not configured. Event not published.")
            return False

        try:
            # Convert to EventGridEvent
            eg_event = EventGridEvent(
                subject=event.source,
                event_type=event.event_type.value,
                data=event.data,
                data_version="1.0",
                id=event.event_id,
                event_time=event.timestamp,
            )

            self.client.send([eg_event])
            logger.info(f"Published event to Azure Event Grid: {event.event_id}")
            return True

        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.error("Failed to publish to Azure Event Grid: <ERROR_TYPE>")
            return False

    def publish_batch(self, events: list[Event]) -> bool:
        """Publish batch of events to Azure Event Grid.

        Args:
            events: Events to publish

        Returns:
            True if successful
        """
        if not self.client:
            logger.warning("Azure Event Grid not configured. Events not published.")
            return False

        try:
            # Convert to EventGridEvents
            eg_events = [
                EventGridEvent(
                    subject=event.source,
                    event_type=event.event_type.value,
                    data=event.data,
                    data_version="1.0",
                    id=event.event_id,
                    event_time=event.timestamp,
                )
                for event in events
            ]

            self.client.send(eg_events)
            logger.info(f"Published {len(events)} events to Azure Event Grid")
            return True

        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.error("Failed to publish batch to Azure Event Grid: <ERROR_TYPE>")
            return False
