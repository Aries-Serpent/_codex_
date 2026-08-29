"""Training pipeline event integration."""

from __future__ import annotations

import logging
import os
from typing import Any, Optional

from codex_ml.events.base import Event, EventBus, EventPublisher, EventType

logger = logging.getLogger(__name__)

__all__ = ["TrainingEventEmitter"]


class TrainingEventEmitter:
    """Emit training lifecycle events."""

    def __init__(self, publisher: Optional[EventPublisher] = None):
        """Initialize training event emitter.

        Args:
            publisher: Event publisher (auto-detect if None)
        """
        self.publisher = publisher or self._create_publisher()

    def _create_publisher(self) -> EventPublisher:
        """Create event publisher based on environment.

        Returns:
            Event publisher instance
        """
        # Try Azure Event Grid first
        if os.getenv("AZURE_EVENT_GRID_ENDPOINT"):
            try:
                from codex_ml.events.azure_events import AzureEventPublisher

                logger.info("Using Azure Event Grid publisher")
                return AzureEventPublisher()
            except ImportError as e:
                type(e).__name__
                logger.debug("ImportError: <ERROR_TYPE>")
                logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
                logger.warning("Azure Event Grid configured but package not installed")

        # Try AWS EventBridge
        if os.getenv("AWS_EVENT_BUS_NAME"):
            try:
                from codex_ml.events.aws_events import AWSEventPublisher

                logger.info("Using AWS EventBridge publisher")
                return AWSEventPublisher()
            except ImportError as e:
                type(e).__name__
                logger.debug("ImportError: <ERROR_TYPE>")
                logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
                logger.warning("AWS EventBridge configured but package not installed")

        # Fallback to local EventBus
        logger.info("Using local EventBus (no cloud events configured)")
        return EventBus()

    def emit_training_started(
        self,
        model_name: str,
        config: dict[str, Any],
    ) -> bool:
        """Emit training started event.

        Args:
            model_name: Model name
            config: Training configuration

        Returns:
            True if successful
        """
        event = Event(
            event_type=EventType.MODEL_TRAINING_STARTED,
            source=f"codex-ml/training/{model_name}",
            data={
                "model_name": model_name,
                "config": config,
            },
        )
        return self.publisher.publish(event)

    def emit_training_completed(
        self,
        model_name: str,
        metrics: dict[str, Any],
    ) -> bool:
        """Emit training completed event.

        Args:
            model_name: Model name
            metrics: Training metrics

        Returns:
            True if successful
        """
        event = Event(
            event_type=EventType.MODEL_TRAINING_COMPLETED,
            source=f"codex-ml/training/{model_name}",
            data={
                "model_name": model_name,
                "metrics": metrics,
            },
        )
        return self.publisher.publish(event)

    def emit_training_failed(
        self,
        model_name: str,
        error: str,
    ) -> bool:
        """Emit training failed event.

        Args:
            model_name: Model name
            error: Error message

        Returns:
            True if successful
        """
        event = Event(
            event_type=EventType.MODEL_TRAINING_FAILED,
            source=f"codex-ml/training/{model_name}",
            data={
                "model_name": model_name,
                "error": error,
            },
        )
        return self.publisher.publish(event)

    def emit_drift_detected(
        self,
        drift_type: str,
        score: float,
        threshold: float,
    ) -> bool:
        """Emit drift detected event.

        Args:
            drift_type: Type of drift
            score: Drift score
            threshold: Drift threshold

        Returns:
            True if successful
        """
        event = Event(
            event_type=EventType.DRIFT_DETECTED,
            source="codex-ml/monitoring/drift",
            data={
                "drift_type": drift_type,
                "score": score,
                "threshold": threshold,
            },
        )
        return self.publisher.publish(event)

    def emit_model_deployed(
        self,
        model_name: str,
        version: str,
        environment: str = "production",
    ) -> bool:
        """Emit model deployed event.

        Args:
            model_name: Model name
            version: Model version
            environment: Deployment environment

        Returns:
            True if successful
        """
        event = Event(
            event_type=EventType.MODEL_DEPLOYED,
            source=f"codex-ml/deployment/{model_name}",
            data={
                "model_name": model_name,
                "version": version,
                "environment": environment,
            },
        )
        return self.publisher.publish(event)
