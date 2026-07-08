"""Smoke tests for :mod:`codex_ml.training.event_integration`."""

from __future__ import annotations

import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def test_emitter_uses_publisher_and_emits_events():
    class DummyEvent:
        def __init__(self, event_type, source, data):
            self.event_type = event_type
            self.source = source
            self.data = data

    class DummyEventBus:
        def publish(self, event):
            return True

    class DummyEventType:
        MODEL_TRAINING_STARTED = "started"
        MODEL_TRAINING_COMPLETED = "completed"
        MODEL_TRAINING_FAILED = "failed"
        DRIFT_DETECTED = "drift"
        MODEL_DEPLOYED = "deployed"

    sys.modules.setdefault(
        "codex_ml.training.base",
        types.SimpleNamespace(
            Event=DummyEvent,
            EventBus=DummyEventBus,
            EventPublisher=DummyEventBus,
            EventType=DummyEventType,
        ),
    )

    from codex_ml.training.event_integration import TrainingEventEmitter

    publisher = MagicMock()
    publisher.publish.return_value = True

    emitter = TrainingEventEmitter(publisher=publisher)

    assert emitter.emit_training_started("demo", {"lr": 1e-3}) is True
    assert emitter.emit_training_completed("demo", {"acc": 0.9}) is True
    assert emitter.emit_training_failed("demo", "boom") is True
    assert emitter.emit_drift_detected("concept", 0.5, 0.2) is True
    assert emitter.emit_model_deployed("demo", "v1") is True

    assert publisher.publish.call_count == 5, "Count must be greater than zero"


def test_emitter_falls_back_to_event_bus(monkeypatch):
    """When no cloud env vars are set, the local publisher is used."""

    monkeypatch.delenv("AZURE_EVENT_GRID_ENDPOINT", raising=False)
    monkeypatch.delenv("AWS_EVENT_BUS_NAME", raising=False)

    from codex_ml.training.event_integration import TrainingEventEmitter

    emitter = TrainingEventEmitter()
    assert emitter.emit_training_started("demo", {}) is True
