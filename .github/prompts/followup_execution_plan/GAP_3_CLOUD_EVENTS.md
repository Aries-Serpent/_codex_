# Gap 3: Cloud Event Integration

**Priority:** Low  
**Category:** Training & Model Management  
**Azure MLOps Capability:** Row 28  
**Current State:** ❌ Not Implemented (88% complete)

---

## Gap Description

### Current Implementation
- ✅ Local event system for drift detection
- ✅ Event-driven retraining pipeline
- ✅ Model registry with lifecycle hooks
- ❌ No Azure Event Grid integration
- ❌ No AWS EventBridge integration
- ❌ No GCP Cloud Pub/Sub integration
- ❌ No cloud-native event orchestration

### Azure MLOps Requirement (Level 4)
> **Row 28:** "Azure Event Grid life cycle events emitted for pipeline orchestration"  
> Expectation: Cloud-native event system for model lifecycle, training triggers, and pipeline orchestration.

---

## Objective

Implement cloud event integration to enable:
1. Cloud-native event emission and consumption
2. Model lifecycle event tracking
3. Cross-service event orchestration
4. Event-driven pipeline triggers
5. Multi-cloud event support

---

## Implementation Tasks

### Task 1: Event Abstraction Layer
**File:** `src/codex_ml/events/base.py`

```python
"""Base event system with cloud provider abstraction."""
from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable

logger = logging.getLogger(__name__)

__all__ = [
    "EventType",
    "Event",
    "EventPublisher",
    "EventSubscriber",
    "EventBus",
]


class EventType(str, Enum):
    """Model lifecycle event types."""
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
    """Base event class.
    
    Attributes:
        event_type: Type of event
        source: Event source identifier
        data: Event payload
        event_id: Unique event ID
        timestamp: Event timestamp
        metadata: Additional metadata
    """
    event_type: EventType
    source: str
    data: Dict[str, Any]
    event_id: str
    timestamp: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> dict:
        """Convert event to dictionary."""
        result = asdict(self)
        result["event_type"] = self.event_type.value
        return result
    
    def to_json(self) -> str:
        """Convert event to JSON string."""
        return json.dumps(self.to_dict())


class EventPublisher(ABC):
    """Abstract event publisher."""
    
    @abstractmethod
    def publish(self, event: Event) -> bool:
        """Publish an event.
        
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
            events: List of events to publish
            
        Returns:
            True if all successful
        """
        pass


class EventSubscriber(ABC):
    """Abstract event subscriber."""
    
    @abstractmethod
    def subscribe(self, event_type: EventType, handler: Callable[[Event], None]):
        """Subscribe to event type.
        
        Args:
            event_type: Type of event to subscribe to
            handler: Callback function
        """
        pass
    
    @abstractmethod
    def unsubscribe(self, event_type: EventType):
        """Unsubscribe from event type.
        
        Args:
            event_type: Type of event to unsubscribe from
        """
        pass


class EventBus:
    """Local event bus for development and testing."""
    
    def __init__(self):
        """Initialize event bus."""
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.event_history: List[Event] = []
    
    def publish(self, event: Event) -> bool:
        """Publish event to subscribers.
        
        Args:
            event: Event to publish
            
        Returns:
            True if successful
        """
        self.event_history.append(event)
        
        handlers = self.subscribers.get(event.event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in event handler: {e}")
        
        logger.info(f"Published event: {event.event_type.value}")
        return True
    
    def subscribe(self, event_type: EventType, handler: Callable[[Event], None]):
        """Subscribe to event type.
        
        Args:
            event_type: Event type
            handler: Handler function
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
        logger.info(f"Subscribed to {event_type.value}")
    
    def get_history(self, event_type: Optional[EventType] = None) -> List[Event]:
        """Get event history.
        
        Args:
            event_type: Filter by event type
            
        Returns:
            List of events
        """
        if event_type:
            return [e for e in self.event_history if e.event_type == event_type]
        return self.event_history.copy()
```

### Task 2: Azure Event Grid Integration
**File:** `src/codex_ml/events/azure_events.py`

```python
"""Azure Event Grid integration."""
from __future__ import annotations

import os
import logging
from typing import List

from .base import Event, EventPublisher

logger = logging.getLogger(__name__)

__all__ = ["AzureEventPublisher"]


class AzureEventPublisher(EventPublisher):
    """Azure Event Grid event publisher."""
    
    def __init__(self, topic_endpoint: str = None, topic_key: str = None):
        """Initialize Azure Event Grid publisher.
        
        Args:
            topic_endpoint: Event Grid topic endpoint
            topic_key: Topic access key
        """
        self.topic_endpoint = topic_endpoint or os.getenv("AZURE_EVENT_GRID_ENDPOINT")
        self.topic_key = topic_key or os.getenv("AZURE_EVENT_GRID_KEY")
        
        if not self.topic_endpoint or not self.topic_key:
            logger.warning("Azure Event Grid credentials not configured")
            self._client = None
        else:
            self._client = self._create_client()
    
    def _create_client(self):
        """Create Event Grid client."""
        try:
            from azure.eventgrid import EventGridPublisherClient
            from azure.core.credentials import AzureKeyCredential
            
            credential = AzureKeyCredential(self.topic_key)
            return EventGridPublisherClient(self.topic_endpoint, credential)
        except ImportError:
            logger.error("azure-eventgrid package not installed")
            return None
    
    def publish(self, event: Event) -> bool:
        """Publish event to Azure Event Grid.
        
        Args:
            event: Event to publish
            
        Returns:
            True if successful
        """
        if not self._client:
            logger.warning("Azure Event Grid client not initialized")
            return False
        
        try:
            from azure.eventgrid import EventGridEvent
            
            eg_event = EventGridEvent(
                subject=f"codex-ml/{event.source}",
                event_type=event.event_type.value,
                data=event.data,
                data_version="1.0",
            )
            
            self._client.send([eg_event])
            logger.info(f"Published to Azure Event Grid: {event.event_type.value}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish to Azure Event Grid: {e}")
            return False
    
    def publish_batch(self, events: List[Event]) -> bool:
        """Publish batch of events.
        
        Args:
            events: List of events
            
        Returns:
            True if all successful
        """
        if not self._client:
            return False
        
        try:
            from azure.eventgrid import EventGridEvent
            
            eg_events = [
                EventGridEvent(
                    subject=f"codex-ml/{e.source}",
                    event_type=e.event_type.value,
                    data=e.data,
                    data_version="1.0",
                )
                for e in events
            ]
            
            self._client.send(eg_events)
            logger.info(f"Published {len(events)} events to Azure Event Grid")
            return True
        except Exception as e:
            logger.error(f"Failed to publish batch: {e}")
            return False
```

### Task 3: AWS EventBridge Integration
**File:** `src/codex_ml/events/aws_events.py`

```python
"""AWS EventBridge integration."""
from __future__ import annotations

import os
import json
import logging
from typing import List

from .base import Event, EventPublisher

logger = logging.getLogger(__name__)

__all__ = ["AWSEventPublisher"]


class AWSEventPublisher(EventPublisher):
    """AWS EventBridge event publisher."""
    
    def __init__(self, event_bus_name: str = None):
        """Initialize AWS EventBridge publisher.
        
        Args:
            event_bus_name: EventBridge bus name
        """
        self.event_bus_name = event_bus_name or os.getenv("AWS_EVENT_BUS_NAME", "default")
        self._client = self._create_client()
    
    def _create_client(self):
        """Create EventBridge client."""
        try:
            import boto3
            return boto3.client('events')
        except ImportError:
            logger.error("boto3 package not installed")
            return None
        except Exception as e:
            logger.error(f"Failed to create EventBridge client: {e}")
            return None
    
    def publish(self, event: Event) -> bool:
        """Publish event to AWS EventBridge.
        
        Args:
            event: Event to publish
            
        Returns:
            True if successful
        """
        if not self._client:
            logger.warning("AWS EventBridge client not initialized")
            return False
        
        try:
            response = self._client.put_events(
                Entries=[
                    {
                        'Source': f'codex-ml.{event.source}',
                        'DetailType': event.event_type.value,
                        'Detail': json.dumps(event.data),
                        'EventBusName': self.event_bus_name,
                    }
                ]
            )
            
            if response['FailedEntryCount'] == 0:
                logger.info(f"Published to AWS EventBridge: {event.event_type.value}")
                return True
            else:
                logger.error(f"Failed to publish: {response}")
                return False
        except Exception as e:
            logger.error(f"Failed to publish to AWS EventBridge: {e}")
            return False
    
    def publish_batch(self, events: List[Event]) -> bool:
        """Publish batch of events.
        
        Args:
            events: List of events
            
        Returns:
            True if all successful
        """
        if not self._client:
            return False
        
        try:
            entries = [
                {
                    'Source': f'codex-ml.{e.source}',
                    'DetailType': e.event_type.value,
                    'Detail': json.dumps(e.data),
                    'EventBusName': self.event_bus_name,
                }
                for e in events
            ]
            
            response = self._client.put_events(Entries=entries)
            
            if response['FailedEntryCount'] == 0:
                logger.info(f"Published {len(events)} events to AWS EventBridge")
                return True
            else:
                logger.error(f"Some events failed: {response}")
                return False
        except Exception as e:
            logger.error(f"Failed to publish batch: {e}")
            return False
```

### Task 4: Event Integration with Training Pipeline
**File:** `src/codex_ml/training/event_integration.py`

```python
"""Integrate events with training pipeline."""
import logging
import uuid
from datetime import datetime
from pathlib import Path

from codex_ml.events.base import Event, EventType, EventBus
from codex_ml.events.azure_events import AzureEventPublisher
from codex_ml.events.aws_events import AWSEventPublisher

logger = logging.getLogger(__name__)


class TrainingEventEmitter:
    """Emit events during training lifecycle."""
    
    def __init__(self, publisher=None):
        """Initialize event emitter.
        
        Args:
            publisher: Event publisher (defaults to local EventBus)
        """
        if publisher is None:
            # Try cloud publishers, fall back to local
            self.publisher = self._create_publisher()
        else:
            self.publisher = publisher
    
    def _create_publisher(self):
        """Create appropriate event publisher."""
        # Try Azure first
        try:
            azure_pub = AzureEventPublisher()
            if azure_pub._client:
                logger.info("Using Azure Event Grid publisher")
                return azure_pub
        except Exception:
            pass
        
        # Try AWS
        try:
            aws_pub = AWSEventPublisher()
            if aws_pub._client:
                logger.info("Using AWS EventBridge publisher")
                return aws_pub
        except Exception:
            pass
        
        # Fall back to local
        logger.info("Using local EventBus")
        return EventBus()
    
    def emit_training_started(self, model_name: str, config: dict):
        """Emit training started event."""
        event = Event(
            event_type=EventType.MODEL_TRAINING_STARTED,
            source="training-pipeline",
            data={
                "model_name": model_name,
                "config": config,
            },
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
        )
        self.publisher.publish(event)
    
    def emit_training_completed(self, model_name: str, metrics: dict):
        """Emit training completed event."""
        event = Event(
            event_type=EventType.MODEL_TRAINING_COMPLETED,
            source="training-pipeline",
            data={
                "model_name": model_name,
                "metrics": metrics,
            },
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
        )
        self.publisher.publish(event)
    
    def emit_drift_detected(self, drift_type: str, score: float):
        """Emit drift detected event."""
        event = Event(
            event_type=EventType.DRIFT_DETECTED,
            source="drift-monitor",
            data={
                "drift_type": drift_type,
                "score": score,
                "action": "retraining_required",
            },
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
        )
        self.publisher.publish(event)
```

### Task 5: Configuration and Documentation
**File:** `configs/events/event_config.yaml`

```yaml
# Event system configuration

# Event publisher type: local, azure, aws, gcp
publisher_type: local

# Azure Event Grid configuration
azure:
  enabled: false
  topic_endpoint: ${oc.env:AZURE_EVENT_GRID_ENDPOINT}
  topic_key: ${oc.env:AZURE_EVENT_GRID_KEY}

# AWS EventBridge configuration
aws:
  enabled: false
  event_bus_name: ${oc.env:AWS_EVENT_BUS_NAME,default}
  region: ${oc.env:AWS_REGION,us-east-1}

# GCP Cloud Pub/Sub configuration
gcp:
  enabled: false
  project_id: ${oc.env:GCP_PROJECT_ID}
  topic_name: ${oc.env:GCP_PUBSUB_TOPIC}

# Event filtering
filters:
  # Only emit these event types
  allowed_types:
    - model.training.completed
    - model.deployed
    - drift.detected
  
  # Minimum severity to emit
  min_severity: INFO

# Event batching
batching:
  enabled: true
  max_batch_size: 100
  max_wait_seconds: 30

# Retry configuration
retry:
  enabled: true
  max_attempts: 3
  backoff_multiplier: 2.0
```

---

## Testing & Validation

### Unit Tests
**File:** `tests/test_events.py`

```python
"""Tests for event system."""
import pytest
from codex_ml.events.base import Event, EventType, EventBus


def test_event_bus():
    """Test local event bus."""
    bus = EventBus()
    received = []
    
    def handler(event):
        received.append(event)
    
    bus.subscribe(EventType.MODEL_TRAINING_STARTED, handler)
    
    event = Event(
        event_type=EventType.MODEL_TRAINING_STARTED,
        source="test",
        data={"model": "test_model"},
        event_id="123",
        timestamp="Previous Cycle-01-01T00:00:00",
    )
    
    bus.publish(event)
    
    assert len(received) == 1
    assert received[0].event_type == EventType.MODEL_TRAINING_STARTED
```

---

## Documentation Updates

### New Files
1. `docs/events/cloud_integration.md` - Cloud event setup guide
2. `docs/events/event_types.md` - Event type reference
3. `examples/events/` - Example event handlers

### Updates
1. `README.md` - Add cloud events section
2. `AGENTS.md` - Document event configuration
3. `.env.example` - Add event credentials template

---

## Success Criteria

✅ **Complete when:**
1. Event abstraction layer implemented
2. Azure/AWS/GCP integrations functional
3. Training pipeline emitting events
4. Tests passing (>80% coverage)
5. Documentation complete
6. Row 28 marked as ✅ Met

**Expected Improvement:**
- Training & Model Management: 88% → 100% (+12%)
- Overall Score: 94% → 96% (+2%)
