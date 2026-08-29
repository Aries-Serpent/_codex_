"""
Causal Event Logger

Enhances event-based logging with explicit causal links between events.
Implements process philosophy event ontology.

Reference: .codex/docs/PHILOSOPHICAL_FRAMEWORK.md#event-ontology
Philosophical Foundation: Process Philosophy - Event-based ontology

Core Concepts:
- Events are fundamental (not substances/entities)
- Causation is explicit relationship between events
- Every event has a causal history
- Reality is process, not static being

This module extends existing event logging with:
1. Causal link tracking (event A caused event B)
2. Causal chain reconstruction
3. Event genealogy analysis
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

LOGGER = logging.getLogger(__name__)


class CausalRelationType(Enum):
    """Types of causal relationships between events."""

    DIRECT_CAUSE = "direct_cause"  # A directly caused B
    ENABLING = "enabling"  # A enabled B (necessary but not sufficient)
    INHIBITING = "inhibiting"  # A prevented B
    CONTRIBUTING = "contributing"  # A contributed to B (partial cause)
    TEMPORAL = "temporal"  # A occurred before B (correlation, not causation)


@dataclass
class Event:
    """
    An event in the process philosophy ontology.

    Events are the fundamental units of reality, not substances or entities.
    """

    event_id: str
    event_type: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __hash__(self) -> int:
        return hash(self.event_id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Event):
            return False
        return self.event_id == other.event_id


@dataclass
class CausalLink:
    """
    A causal relationship between two events.

    Makes causation explicit: event A caused (or contributed to) event B.
    """

    cause_event_id: str
    effect_event_id: str
    relation_type: CausalRelationType
    strength: float = 1.0  # 0.0 (weak) to 1.0 (strong)
    confidence: float = 1.0  # 0.0 (uncertain) to 1.0 (certain)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not 0.0 <= self.strength <= 1.0:
            raise ValueError(f"Strength must be 0.0-1.0, got {self.strength}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")


@dataclass
class CausalChain:
    """
    A chain of causally linked events.

    Represents a process: event_1 → event_2 → event_3 → ...
    """

    events: list[Event]
    links: list[CausalLink]

    def __len__(self) -> int:
        return len(self.events)

    def get_root_cause(self) -> Optional[Event]:
        """Get the first event in the chain (root cause)."""
        return self.events[0] if self.events else None

    def get_final_effect(self) -> Optional[Event]:
        """Get the last event in the chain (final effect)."""
        return self.events[-1] if self.events else None


class CausalEventLogger:
    """
    Logs events with explicit causal links.

    Implements process philosophy by treating events as fundamental
    and making causation explicit.

    Example:
        >>> logger = CausalEventLogger()
        >>> event_1 = logger.log_event("user_action", {"action": "click_button"})
        >>> event_2 = logger.log_event("api_call", {"endpoint": "/submit"})
        >>> logger.link_events(event_1, event_2, CausalRelationType.DIRECT_CAUSE)
        >>> chain = logger.get_causal_chain(event_2.event_id)
        >>> logger.info(f"Causal chain length: {len(chain)}")
    """

    def __init__(self) -> None:
        self.events: dict[str, Event] = {}
        self.causal_links: list[CausalLink] = []
        self.causation_graph: dict[str, list[str]] = {}  # event_id -> caused_events
        self.reverse_graph: dict[str, list[str]] = {}  # event_id -> causing_events
        LOGGER.info("CausalEventLogger initialized")

    def log_event(
        self,
        event_type: str,
        data: Optional[dict[str, Any]] = None,
        event_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        caused_by: Optional[list[str]] = None,
    ) -> Event:
        """
        Log an event with optional causal information.

        Args:
            event_type: Type of event (e.g., "user_action", "api_call")
            data: Event data
            event_id: Optional custom event ID (auto-generated if not provided)
            metadata: Optional metadata
            caused_by: Optional list of event IDs that caused this event

        Returns:
            The logged event
        """
        if event_id is None:
            # Generate unique event ID
            timestamp_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
            event_id = f"{event_type}_{timestamp_ms}"

        event = Event(
            event_id=event_id,
            event_type=event_type,
            data=data or {},
            metadata=metadata or {},
        )

        self.events[event_id] = event

        # Initialize graph entries
        if event_id not in self.causation_graph:
            self.causation_graph[event_id] = []
        if event_id not in self.reverse_graph:
            self.reverse_graph[event_id] = []

        # Link to causing events if provided
        if caused_by:
            for cause_id in caused_by:
                if cause_id in self.events:
                    self.link_events(
                        self.events[cause_id],
                        event,
                        CausalRelationType.DIRECT_CAUSE,
                    )

        LOGGER.debug(f"Logged event: {event_id} (type: {event_type})")
        return event

    def link_events(
        self,
        cause: Event,
        effect: Event,
        relation_type: CausalRelationType,
        strength: float = 1.0,
        confidence: float = 1.0,
        metadata: Optional[dict[str, Any]] = None,
    ) -> CausalLink:
        """
        Create a causal link between two events.

        Args:
            cause: The causing event
            effect: The effect event
            relation_type: Type of causal relationship
            strength: Strength of causation (0.0 to 1.0)
            confidence: Confidence in the causal claim (0.0 to 1.0)
            metadata: Optional metadata

        Returns:
            The created causal link
        """
        # Ensure both events are logged
        if cause.event_id not in self.events:
            self.events[cause.event_id] = cause
        if effect.event_id not in self.events:
            self.events[effect.event_id] = effect

        link = CausalLink(
            cause_event_id=cause.event_id,
            effect_event_id=effect.event_id,
            relation_type=relation_type,
            strength=strength,
            confidence=confidence,
            metadata=metadata or {},
        )

        self.causal_links.append(link)

        # Update causation graph
        if cause.event_id not in self.causation_graph:
            self.causation_graph[cause.event_id] = []
        self.causation_graph[cause.event_id].append(effect.event_id)

        # Update reverse graph
        if effect.event_id not in self.reverse_graph:
            self.reverse_graph[effect.event_id] = []
        self.reverse_graph[effect.event_id].append(cause.event_id)

        LOGGER.debug(
            f"Linked events: {cause.event_id} -> {effect.event_id} "
            f"({relation_type.value}, strength={strength:.2f})"
        )
        return link

    def get_causal_chain(self, event_id: str, max_depth: int = 10) -> CausalChain:
        """
        Get the causal chain leading to an event.

        Traces back from the given event to root causes.

        Args:
            event_id: ID of the event to trace back from
            max_depth: Maximum depth to trace (prevents infinite loops)

        Returns:
            CausalChain from root causes to the given event
        """
        if event_id not in self.events:
            LOGGER.warning(f"Event not found: {event_id}")
            return CausalChain(events=[], links=[])

        # Trace back to root causes
        chain_events: list[Event] = []
        chain_links: list[CausalLink] = []
        visited: set[str] = set()

        def trace_back(current_id: str, depth: int) -> None:
            if depth > max_depth or current_id in visited:
                return

            visited.add(current_id)
            current_event = self.events[current_id]

            # Get causing events
            causing_ids = self.reverse_graph.get(current_id, [])

            if not causing_ids:
                # This is a root cause
                chain_events.insert(0, current_event)
                return

            # Recursively trace back
            for cause_id in causing_ids:
                trace_back(cause_id, depth + 1)

                # Add link
                link = self._find_link(cause_id, current_id)
                if link and link not in chain_links:
                    chain_links.append(link)

            # Add current event
            if current_event not in chain_events:
                chain_events.append(current_event)

        trace_back(event_id, 0)

        return CausalChain(events=chain_events, links=chain_links)

    def get_effects(self, event_id: str) -> list[Event]:
        """
        Get all events that were caused by the given event.

        Args:
            event_id: ID of the causing event

        Returns:
            List of effect events
        """
        effect_ids = self.causation_graph.get(event_id, [])
        return [self.events[eid] for eid in effect_ids if eid in self.events]

    def get_causes(self, event_id: str) -> list[Event]:
        """
        Get all events that caused the given event.

        Args:
            event_id: ID of the effect event

        Returns:
            List of causing events
        """
        cause_ids = self.reverse_graph.get(event_id, [])
        return [self.events[cid] for cid in cause_ids if cid in self.events]

    def _find_link(self, cause_id: str, effect_id: str) -> Optional[CausalLink]:
        """Find the causal link between two events."""
        for link in self.causal_links:
            if link.cause_event_id == cause_id and link.effect_event_id == effect_id:
                return link
        return None

    def get_root_causes(self) -> list[Event]:
        """
        Get all events that have no causes (root causes).

        Returns:
            List of root cause events
        """
        root_causes = []
        for event_id, event in self.events.items():
            if not self.reverse_graph.get(event_id):
                root_causes.append(event)
        return root_causes

    def get_terminal_effects(self) -> list[Event]:
        """
        Get all events that caused no other events (terminal effects).

        Returns:
            List of terminal effect events
        """
        terminal_effects = []
        for event_id, event in self.events.items():
            if not self.causation_graph.get(event_id):
                terminal_effects.append(event)
        return terminal_effects

    def export_causation_graph(self) -> dict[str, Any]:
        """
        Export the causation graph for visualization.

        Returns:
            Dictionary with nodes (events) and edges (causal links)
        """
        nodes = [
            {
                "id": event.event_id,
                "type": event.event_type,
                "timestamp": event.timestamp.isoformat(),
            }
            for event in self.events.values()
        ]

        edges = [
            {
                "source": link.cause_event_id,
                "target": link.effect_event_id,
                "relation": link.relation_type.value,
                "strength": link.strength,
                "confidence": link.confidence,
            }
            for link in self.causal_links
        ]

        return {
            "nodes": nodes,
            "edges": edges,
            "stats": {
                "total_events": len(self.events),
                "total_links": len(self.causal_links),
                "root_causes": len(self.get_root_causes()),
                "terminal_effects": len(self.get_terminal_effects()),
            },
        }

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about events and causal links."""
        return {
            "total_events": len(self.events),
            "total_links": len(self.causal_links),
            "root_causes": len(self.get_root_causes()),
            "terminal_effects": len(self.get_terminal_effects()),
            "avg_causes_per_event": (
                sum(len(causes) for causes in self.reverse_graph.values()) / len(self.events)
                if self.events
                else 0.0
            ),
            "avg_effects_per_event": (
                sum(len(effects) for effects in self.causation_graph.values()) / len(self.events)
                if self.events
                else 0.0
            ),
        }
