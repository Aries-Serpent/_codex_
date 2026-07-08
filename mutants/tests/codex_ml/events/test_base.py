"""
Test Events Base Module

Comprehensive unit tests for the event system base classes.
Tests EventType, Event, EventPublisher, EventSubscriber, and EventBus.
"""

from __future__ import annotations

import json
from datetime import datetime

import pytest

import codex_ml.events as events_module
from codex_ml.events.base import (
    Event,
    EventBus,
    EventPublisher,
    EventSubscriber,
    EventType,
)


class TestEventType:
    """Tests for EventType enum."""

    def test_model_training_events(self) -> None:
        assert EventType.MODEL_TRAINING_STARTED.value == "model.training.started", "Value must be initialized"
        assert EventType.MODEL_TRAINING_COMPLETED.value == "model.training.completed", "Value must be initialized"
        assert EventType.MODEL_TRAINING_FAILED.value == "model.training.failed", "Value must be initialized"

    def test_model_lifecycle_events(self) -> None:
        assert EventType.MODEL_REGISTERED.value == "model.registered", "Value must be initialized"
        assert EventType.MODEL_DEPLOYED.value == "model.deployed", "Value must be initialized"
        assert EventType.MODEL_RETIRED.value == "model.retired", "Value must be initialized"

    def test_monitoring_events(self) -> None:
        assert EventType.DRIFT_DETECTED.value == "drift.detected", "Value must be initialized"
        assert EventType.DATASET_UPDATED.value == "dataset.updated", "Data must not be empty"

    def test_pipeline_events(self) -> None:
        assert EventType.PIPELINE_STARTED.value == "pipeline.started", "Value must be initialized"
        assert EventType.PIPELINE_COMPLETED.value == "pipeline.completed", "Value must be initialized"
        assert EventType.PIPELINE_FAILED.value == "pipeline.failed", "Value must be initialized"

    def test_enum_iteration(self) -> None:
        # Verify all event types can be iterated
        event_types = list(EventType)
        assert len(event_types) == 11, "Event_types must not be empty"


class TestOptionalEventPublishers:
    """Tests for optional cloud event publisher exports."""

    def test_returns_provider_map_with_current_values(self) -> None:
        publishers = events_module.get_optional_event_publishers()

        monkeypatch.setattr(events_module, "AzureEventPublisher", None)
        monkeypatch.setattr(events_module, "AWSEventPublisher", None)

        class AzurePublisher(EventPublisher):
            pass

        class AWSPublisher(EventPublisher):
            pass

        monkeypatch.setattr(events_module, "AzureEventPublisher", AzurePublisher)
        monkeypatch.setattr(events_module, "AWSEventPublisher", AWSPublisher)

        event = Event(
            event_type=EventType.MODEL_TRAINING_STARTED,
            source="test_source",
            data={"model_id": "123"},
        )

        assert event.event_type == EventType.MODEL_TRAINING_STARTED, "event_type is not valid"
        assert event.source == "test_source", "source is not valid"
        assert event.data == {"model_id": "123"}, "Data must not be empty"
        assert event.event_id is not None, "event_id must be initialized"
        assert event.timestamp is not None, "timestamp must be initialized"
        assert event.metadata == {}, "Data must not be empty"

    def test_auto_generated_fields(self) -> None:
        event = Event(
            event_type=EventType.MODEL_DEPLOYED,
            source="deployer",
            data={},
        )

        # event_id should be a valid UUID string
        assert len(event.event_id) == 36, "Collection must not be empty"
        assert "-" in event.event_id, "Condition must be true"

        # timestamp should be ISO format
        datetime.fromisoformat(event.timestamp)

    def test_custom_metadata(self) -> None:
        event = Event(
            event_type=EventType.DRIFT_DETECTED,
            source="monitor",
            data={"drift_score": 0.95},
            metadata={"severity": "high", "alert": True},
        )

        assert event.metadata["severity"] == "high", "Data must not be empty"
        assert event.metadata["alert"] is True, "Data must not be empty"

    def test_to_dict(self) -> None:
        event = Event(
            event_type=EventType.PIPELINE_COMPLETED,
            source="pipeline_runner",
            data={"duration_seconds": 120},
        )

        result = event.to_dict()

        assert isinstance(result, dict)
        assert result["event_type"] == "pipeline.completed", "Result must not be empty"
        assert result["source"] == "pipeline_runner", "Result must not be empty"
        assert result["data"] == {"duration_seconds": 120}, "Result must not be empty"
        assert "event_id" in result, "Result must not be empty"
        assert "timestamp" in result, "Result must not be empty"

    def test_to_json(self) -> None:
        event = Event(
            event_type=EventType.MODEL_REGISTERED,
            source="registry",
            data={"version": "1.0.0"},
        )

        json_str = event.to_json()

        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed["event_type"] == "model.registered", "Condition must be true"
        assert parsed["source"] == "registry", "Condition must be true"

    def test_event_uniqueness(self) -> None:
        event1 = Event(
            event_type=EventType.MODEL_TRAINING_STARTED,
            source="trainer",
            data={},
        )
        event2 = Event(
            event_type=EventType.MODEL_TRAINING_STARTED,
            source="trainer",
            data={},
        )

        # Each event should have unique ID
        assert event1.event_id != event2.event_id, "event_id is not valid"


class TestEventBus:
    """Tests for EventBus class."""

    def test_publish_single_event(self) -> None:
        bus = EventBus()
        event = Event(
            event_type=EventType.MODEL_TRAINING_STARTED,
            source="trainer",
            data={"model": "test"},
        )

        result = bus.publish(event)

        assert result is True, "Result must not be empty"
        assert len(bus.event_history) == 1, "Collection must not be empty"
        assert bus.event_history[0] == event, "Condition must be true"

    def test_publish_batch(self) -> None:
        bus = EventBus()
        events = [
            Event(event_type=EventType.PIPELINE_STARTED, source="pipeline", data={}),
            Event(event_type=EventType.MODEL_TRAINING_STARTED, source="trainer", data={}),
            Event(event_type=EventType.PIPELINE_COMPLETED, source="pipeline", data={}),
        ]

        result = bus.publish_batch(events)

        assert result is True, "Result must not be empty"
        assert len(bus.event_history) == 3, "Collection must not be empty"

    def test_subscribe_and_receive(self) -> None:
        bus = EventBus()
        received_events: list[Event] = []

        def callback(event: Event) -> None:
            received_events.append(event)

        bus.subscribe(EventType.MODEL_TRAINING_COMPLETED, callback)

        event = Event(
            event_type=EventType.MODEL_TRAINING_COMPLETED,
            source="trainer",
            data={"accuracy": 0.95},
        )
        bus.publish(event)

        assert len(received_events) == 1, "Received_events must not be empty"
        assert received_events[0] == event, "Condition must be true"

    def test_subscribe_different_event_types(self) -> None:
        bus = EventBus()
        training_events: list[Event] = []
        deployment_events: list[Event] = []

        bus.subscribe(EventType.MODEL_TRAINING_COMPLETED, training_events.append)
        bus.subscribe(EventType.MODEL_DEPLOYED, deployment_events.append)

        bus.publish(
            Event(
                event_type=EventType.MODEL_TRAINING_COMPLETED,
                source="trainer",
                data={},
            )
        )
        bus.publish(
            Event(
                event_type=EventType.MODEL_DEPLOYED,
                source="deployer",
                data={},
            )
        )

        assert len(training_events) == 1, "Training_events must not be empty"
        assert len(deployment_events) == 1, "Deployment_events must not be empty"

    def test_unsubscribe(self) -> None:
        bus = EventBus()
        received_events: list[Event] = []

        bus.subscribe(EventType.DRIFT_DETECTED, received_events.append)
        bus.unsubscribe(EventType.DRIFT_DETECTED)

        bus.publish(
            Event(
                event_type=EventType.DRIFT_DETECTED,
                source="monitor",
                data={},
            )
        )

        assert len(received_events) == 0, "Received_events must not be empty"

    def test_get_history_all(self) -> None:
        bus = EventBus()
        bus.publish(Event(event_type=EventType.MODEL_REGISTERED, source="s", data={}))
        bus.publish(Event(event_type=EventType.MODEL_DEPLOYED, source="s", data={}))

        history = bus.get_history()

        assert len(history) == 2, "History must not be empty"

    def test_get_history_filtered(self) -> None:
        bus = EventBus()
        bus.publish(Event(event_type=EventType.MODEL_REGISTERED, source="s", data={}))
        bus.publish(Event(event_type=EventType.MODEL_DEPLOYED, source="s", data={}))
        bus.publish(Event(event_type=EventType.MODEL_DEPLOYED, source="s", data={}))

        history = bus.get_history(EventType.MODEL_DEPLOYED)

        assert len(history) == 2, "History must not be empty"
        assert all(e.event_type == EventType.MODEL_DEPLOYED for e in history), "event_type is not valid"

    def test_clear_history(self) -> None:
        bus = EventBus()
        bus.publish(Event(event_type=EventType.MODEL_RETIRED, source="s", data={}))
        assert len(bus.event_history) == 1, "Collection must not be empty"

        bus.clear_history()

        assert len(bus.event_history) == 0, "Collection must not be empty"

    def test_callback_exception_handling(self) -> None:
        bus = EventBus()

        def failing_callback(event: Event) -> None:
            raise ValueError("Test error")

        bus.subscribe(EventType.PIPELINE_FAILED, failing_callback)

        # Should not raise, exception is logged
        event = Event(event_type=EventType.PIPELINE_FAILED, source="s", data={})
        result = bus.publish(event)

        assert result is True, "Result must not be empty"
        assert len(bus.event_history) == 1, "Collection must not be empty"

    def test_multiple_subscribers_same_event(self) -> None:
        bus = EventBus()
        received1: list[Event] = []
        received2: list[Event] = []

        bus.subscribe(EventType.DATASET_UPDATED, received1.append)
        bus.subscribe(EventType.DATASET_UPDATED, received2.append)

        bus.publish(Event(event_type=EventType.DATASET_UPDATED, source="s", data={}))

        # Both subscribers should receive the event
        assert len(received1) == 1, "Received1 must not be empty"
        assert len(received2) == 1, "Received2 must not be empty"


class TestAbstractClasses:
    """Tests for abstract class definitions."""

    def test_event_publisher_is_abstract(self) -> None:
        # EventPublisher has abstract methods
        with pytest.raises(TypeError):
            EventPublisher()  # type: ignore[abstract]

    def test_event_subscriber_is_abstract(self) -> None:
        # EventSubscriber has abstract methods
        with pytest.raises(TypeError):
            EventSubscriber()  # type: ignore[abstract]

    def test_event_bus_is_concrete(self) -> None:
        # EventBus implements both interfaces
        bus = EventBus()
        assert isinstance(bus, EventPublisher)
        assert isinstance(bus, EventSubscriber)


class TestEventBusIntegration:
    """Integration tests for EventBus."""

    def test_ml_training_workflow(self) -> None:
        """Simulate a complete ML training workflow."""
        bus = EventBus()
        workflow_events: list[Event] = []

        # Subscribe to all training events
        for event_type in [
            EventType.MODEL_TRAINING_STARTED,
            EventType.MODEL_TRAINING_COMPLETED,
            EventType.MODEL_REGISTERED,
        ]:
            bus.subscribe(event_type, workflow_events.append)

        # Simulate training workflow
        bus.publish(
            Event(
                event_type=EventType.MODEL_TRAINING_STARTED,
                source="trainer",
                data={"model_name": "my_model", "epochs": 10},
            )
        )

        bus.publish(
            Event(
                event_type=EventType.MODEL_TRAINING_COMPLETED,
                source="trainer",
                data={"final_accuracy": 0.92, "duration": 3600},
            )
        )

        bus.publish(
            Event(
                event_type=EventType.MODEL_REGISTERED,
                source="registry",
                data={"model_version": "1.0.0"},
            )
        )

        assert len(workflow_events) == 3, "Workflow_events must not be empty"
        assert workflow_events[0].event_type == EventType.MODEL_TRAINING_STARTED, "event_type is not valid"
        assert workflow_events[1].event_type == EventType.MODEL_TRAINING_COMPLETED, "event_type is not valid"
        assert workflow_events[2].event_type == EventType.MODEL_REGISTERED, "event_type is not valid"
