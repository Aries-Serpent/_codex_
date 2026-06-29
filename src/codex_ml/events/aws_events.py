"""AWS EventBridge integration."""

from __future__ import annotations

import logging
import os
from typing import Optional

from .base import Event, EventPublisher

logger = logging.getLogger(__name__)

__all__ = ["AWSEventPublisher"]

try:
    import boto3

    _HAS_BOTO3 = True
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
    _HAS_BOTO3 = False
    logger.warning("boto3 not installed. AWS EventBridge support disabled.")


class AWSEventPublisher(EventPublisher):
    """AWS EventBridge publisher."""

    def __init__(
        self,
        event_bus_name: Optional[str] = None,
        region_name: Optional[str] = None,
    ):
        """Initialize AWS EventBridge publisher.

        Args:
            event_bus_name: EventBridge bus name (or AWS_EVENT_BUS_NAME env var)
            region_name: AWS region (or AWS_REGION env var)
        """
        if not _HAS_BOTO3:
            raise ImportError(
                "boto3 package required for AWS EventBridge support. "
                "Install with: pip install boto3"
            )

        self.event_bus_name = event_bus_name or os.getenv("AWS_EVENT_BUS_NAME", "default")
        self.region_name = region_name or os.getenv("AWS_REGION", "us-east-1")

        try:
            self.client = boto3.client("events", region_name=self.region_name)
            logger.info(f"AWS EventBridge client initialized (region={self.region_name})")
        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.warning("Failed to initialize AWS EventBridge client: <ERROR_TYPE>")
            self.client = None

    def publish(self, event: Event) -> bool:
        """Publish event to AWS EventBridge.

        Args:
            event: Event to publish

        Returns:
            True if successful
        """
        if not self.client:
            logger.warning("AWS EventBridge not configured. Event not published.")
            return False

        try:
            response = self.client.put_events(
                Entries=[
                    {
                        "Source": event.source,
                        "DetailType": event.event_type.value,
                        "Detail": event.to_json(),
                        "EventBusName": self.event_bus_name,
                    }
                ]
            )

            # Check for failures
            if response.get("FailedEntryCount", 0) > 0:
                logger.error(f"Failed to publish event: {response['Entries']}")
                return False

            logger.info(f"Published event to AWS EventBridge: {event.event_id}")
            return True

        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.error("Failed to publish to AWS EventBridge: <ERROR_TYPE>")
            return False

    def publish_batch(self, events: list[Event]) -> bool:
        """Publish batch of events to AWS EventBridge.

        Args:
            events: Events to publish (max 10 per batch)

        Returns:
            True if all successful
        """
        if not self.client:
            logger.warning("AWS EventBridge not configured. Events not published.")
            return False

        # AWS EventBridge max 10 events per request
        batch_size = 10
        all_success = True

        for i in range(0, len(events), batch_size):
            batch = events[i : i + batch_size]

            try:
                entries = [
                    {
                        "Source": event.source,
                        "DetailType": event.event_type.value,
                        "Detail": event.to_json(),
                        "EventBusName": self.event_bus_name,
                    }
                    for event in batch
                ]

                response = self.client.put_events(Entries=entries)

                # Check for failures
                failed_count = response.get("FailedEntryCount", 0)
                if failed_count > 0:
                    logger.error(f"Failed to publish {failed_count} events in batch")
                    all_success = False
                else:
                    logger.info(f"Published {len(batch)} events to AWS EventBridge")

            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                logger.error("Failed to publish batch to AWS EventBridge: <ERROR_TYPE>")
                all_success = False

        return all_success
