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
        assert EventType.MODEL_TRAINING_STARTED.value == "model.training.started"
        assert EventType.MODEL_TRAINING_COMPLETED.value == "model.training.completed"
        assert EventType.MODEL_TRAINING_FAILED.value == "model.training.failed"

    def test_model_lifecycle_events(self) -> None:
        assert EventType.MODEL_REGISTERED.value == "model.registered"
        assert EventType.MODEL_DEPLOYED.value == "model.deployed"
        assert EventType.MODEL_RETIRED.value == "model.retired"

    def test_monitoring_events(self) -> None:
        assert EventType.DRIFT_DETECTED.value == "drift.detected"
        assert EventType.DATASET_UPDATED.value == "dataset.updated"

    def test_pipeline_events(self) -> None:
        assert EventType.PIPELINE_STARTED.value == "pipeline.started"
        assert EventType.PIPELINE_COMPLETED.value == "pipeline.completed"
        assert EventType.PIPELINE_FAILED.value == "pipeline.failed"

    def test_enum_iteration(self) -> None:
        # Verify all event types can be iterated
        event_types = list(EventType)
        assert len(event_types) == 11


class TestOptionalEventPublishers:
    """Tests for optional cloud event publisher exports."""

    def test_returns_provider_map_with_current_values(self) -> None:
        publishers = events_module.get_optional_event_publishers()

        assert publishers == {
            "azure": events_module.AzureEventPublisher,
            "aws": events_module.AWSEventPublisher,
        }

    def test_returns_none_for_unavailable_publishers(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(events_module, "AzureEventPublisher", None)
        monkeypatch.setattr(events_module, "AWSEventPublisher", None)

        assert events_module.get_optional_event_publishers() == {
            "azure": None,
            "aws": None,
        }

    def test_returns_publisher_classes_when_available(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        class AzurePublisher(EventPublisher):
            pass

        class AWSPublisher(EventPublisher):
            pass

        monkeypatch.setattr(events_module, "AzureEventPublisher", AzurePublisher)
        monkeypatch.setattr(events_module, "AWSEventPublisher", AWSPublisher)

        assert events_module.get_optional_event_publishers() == {
            "azure": AzurePublisher,
            "aws": AWSPublisher,
        }


class TestEvent:
    """Tests for Event dataclass."""

    def test_basic_creation(self) -> None:
        event = Event(
            event_type=EventType.MODEL_TRAINING_STARTED,
            source="test_source",
            data={"model_id": "123"},
        )

        assert event.event_type == EventType.MODEL_TRAINING_STARTED
        assert event.source == "test_source"
        assert event.data == {"model_id": "123"}
        assert event.event_id is not None
        assert event.timestamp is not None
        assert event.metadata == {}

    def test_auto_generated_fields(self) -> None:
        event = Event(
            event_type=EventType.MODEL_DEPLOYED,
            source="deployer",
            data={},
        )

        # event_id should be a valid UUID string
        assert len(event.event_id) == 36
        assert "-" in event.event_id

        # timestamp should be ISO format
        datetime.fromisoformat(event.timestamp)

    def test_custom_metadata(self) -> None:
        event = Event(
            event_type=EventType.DRIFT_DETECTED,
            source="monitor",
            data={"drift_score": 0.95},
            metadata={"severity": "high", "alert": True},
        )

        assert event.metadata["severity"] == "high"
        assert event.metadata["alert"] is True

    def test_to_dict(self) -> None:
        event = Event(
            event_type=EventType.PIPELINE_COMPLETED,
            source="pipeline_runner",
            data={"duration_seconds": 120},
        )

        result = event.to_dict()

        assert isinstance(result, dict)
        assert result["event_type"] == "pipeline.completed"
        assert result["source"] == "pipeline_runner"
        assert result["data"] == {"duration_seconds": 120}
        assert "event_id" in result
        assert "timestamp" in result

    def test_to_json(self) -> None:
        event = Event(
            event_type=EventType.MODEL_REGISTERED,
            source="registry",
            data={"version": "1.0.0"},
        )

        json_str = event.to_json()

        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed["event_type"] == "model.registered"
        assert parsed["source"] == "registry"

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
        assert event1.event_id != event2.event_id


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

        assert result is True
        assert len(bus.event_history) == 1
        assert bus.event_history[0] == event

    def test_publish_batch(self) -> None:
        bus = EventBus()
        events = [
            Event(event_type=EventType.PIPELINE_STARTED, source="pipeline", data={}),
            Event(event_type=EventType.MODEL_TRAINING_STARTED, source="trainer", data={}),
            Event(event_type=EventType.PIPELINE_COMPLETED, source="pipeline", data={}),
        ]

        result = bus.publish_batch(events)

        assert result is True
        assert len(bus.event_history) == 3

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

        assert len(received_events) == 1
        assert received_events[0] == event

    def test_subscribe_different_event_types(self) -> None:
        bus = EventBus()
        training_events: list[Event] = []
        deployment_events: list[Event] = []

        bus.subscribe(EventType.MODEL_TRAINING_COMPLETED, training_events.append)
        bus.subscribe(EventType.MODEL_DEPLOYED, deployment_events.append)

        bus.publish(Event(
            event_type=EventType.MODEL_TRAINING_COMPLETED,
            source="trainer",
            data={},
        ))
        bus.publish(Event(
            event_type=EventType.MODEL_DEPLOYED,
            source="deployer",
            data={},
        ))

        assert len(training_events) == 1
        assert len(deployment_events) == 1

    def test_unsubscribe(self) -> None:
        bus = EventBus()
        received_events: list[Event] = []

        bus.subscribe(EventType.DRIFT_DETECTED, received_events.append)
        bus.unsubscribe(EventType.DRIFT_DETECTED)

        bus.publish(Event(
            event_type=EventType.DRIFT_DETECTED,
            source="monitor",
            data={},
        ))

        assert len(received_events) == 0

    def test_get_history_all(self) -> None:
        bus = EventBus()
        bus.publish(Event(event_type=EventType.MODEL_REGISTERED, source="s", data={}))
        bus.publish(Event(event_type=EventType.MODEL_DEPLOYED, source="s", data={}))

        history = bus.get_history()

        assert len(history) == 2

    def test_get_history_filtered(self) -> None:
        bus = EventBus()
        bus.publish(Event(event_type=EventType.MODEL_REGISTERED, source="s", data={}))
        bus.publish(Event(event_type=EventType.MODEL_DEPLOYED, source="s", data={}))
        bus.publish(Event(event_type=EventType.MODEL_DEPLOYED, source="s", data={}))

        history = bus.get_history(EventType.MODEL_DEPLOYED)

        assert len(history) == 2
        assert all(e.event_type == EventType.MODEL_DEPLOYED for e in history)

    def test_clear_history(self) -> None:
        bus = EventBus()
        bus.publish(Event(event_type=EventType.MODEL_RETIRED, source="s", data={}))
        assert len(bus.event_history) == 1

        bus.clear_history()

        assert len(bus.event_history) == 0

    def test_callback_exception_handling(self) -> None:
        bus = EventBus()

        def failing_callback(event: Event) -> None:
            raise ValueError("Test error")

        bus.subscribe(EventType.PIPELINE_FAILED, failing_callback)

        # Should not raise, exception is logged
        event = Event(event_type=EventType.PIPELINE_FAILED, source="s", data={})
        result = bus.publish(event)

        assert result is True
        assert len(bus.event_history) == 1

    def test_multiple_subscribers_same_event(self) -> None:
        bus = EventBus()
        received1: list[Event] = []
        received2: list[Event] = []

        bus.subscribe(EventType.DATASET_UPDATED, received1.append)
        bus.subscribe(EventType.DATASET_UPDATED, received2.append)

        bus.publish(Event(event_type=EventType.DATASET_UPDATED, source="s", data={}))

        # Both subscribers should receive the event
        assert len(received1) == 1
        assert len(received2) == 1


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
        bus.publish(Event(
            event_type=EventType.MODEL_TRAINING_STARTED,
            source="trainer",
            data={"model_name": "my_model", "epochs": 10},
        ))

        bus.publish(Event(
            event_type=EventType.MODEL_TRAINING_COMPLETED,
            source="trainer",
            data={"final_accuracy": 0.92, "duration": 3600},
        ))

        bus.publish(Event(
            event_type=EventType.MODEL_REGISTERED,
            source="registry",
            data={"model_version": "1.0.0"},
        ))

        assert len(workflow_events) == 3
        assert workflow_events[0].event_type == EventType.MODEL_TRAINING_STARTED
        assert workflow_events[1].event_type == EventType.MODEL_TRAINING_COMPLETED
        assert workflow_events[2].event_type == EventType.MODEL_REGISTERED
