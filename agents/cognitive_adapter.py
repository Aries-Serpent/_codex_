"""
Cognitive Adapter for Legacy Agents

Provides an adapter layer to help legacy agents transition to the new
cognitive architecture without requiring immediate full refactoring.

Part of Phase 1.4: ABC Enforcement
"""
from __future__ import annotations

import logging

# Import cognitive brain ABCs
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, Optional

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root / "src"))

from cognitive_brain.base import (  # noqa: E402
    ActionResult,
    Decision,
    MemoryInterface,
    ObservationData,
    OrientationResult,
    Planner,
)

logger = logging.getLogger(__name__)


class SimpleDictMemory(MemoryInterface):
    """
    Simple in-memory implementation of MemoryInterface.

    Suitable for lightweight agents or testing. For production use,
    implement a persistent memory backend.
    """

    def __init__(self):
        """Initialize the simple dictionary memory."""
        self._storage: Dict[str, Any] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._history: Dict[str, list[tuple[datetime, Any]]] = {}

    def store(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Store a value in memory."""
        try:
            self._storage[key] = value
            if metadata:
                self._metadata[key] = metadata

            # Store in history
            if key not in self._history:
                self._history[key] = []
            self._history[key].append((datetime.now(UTC), value))

            return True
        except Exception as e:
            logger.error(f"Failed to store {key}: {e}")
            return False

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value from memory."""
        return self._storage.get(key)

    def search(self, query: Dict[str, Any], limit: int = 10) -> list[tuple[str, Any]]:
        """Search memory based on query criteria."""
        results = []

        for key, value in self._storage.items():
            # Simple matching: check if query items match metadata
            metadata = self._metadata.get(key, {})
            match = all(
                metadata.get(q_key) == q_value
                for q_key, q_value in query.items()
            )

            if match:
                results.append((key, value))
                if len(results) >= limit:
                    break

        return results

    def delete(self, key: str) -> bool:
        """Delete a value from memory."""
        try:
            if key in self._storage:
                del self._storage[key]
                self._metadata.pop(key, None)
                # Keep history for audit trail
            return True
        except Exception as e:
            logger.error(f"Failed to delete {key}: {e}")
            return False

    def clear(self) -> bool:
        """Clear all memory."""
        try:
            self._storage.clear()
            self._metadata.clear()
            self._history.clear()
            return True
        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")
            return False

    def get_history(self, key: str, limit: int = 10) -> list[tuple[datetime, Any]]:
        """Get historical versions of a value."""
        history = self._history.get(key, [])
        return history[-limit:][::-1]  # Return most recent first


class LegacyAgentAdapter(Planner):
    """
    Adapter to wrap legacy agents into the new Planner interface.

    This allows gradual migration of existing agents to the new
    cognitive architecture without breaking existing functionality.

    Usage:
        class MyLegacyAgent:
            def process(self, data):
                # Legacy logic
                return result

        # Wrap legacy agent
        adapter = LegacyAgentAdapter(MyLegacyAgent())
        result = adapter.ooda_loop({"input": "data"})
    """

    def __init__(self, legacy_agent: Any, memory: Optional[MemoryInterface] = None):
        """
        Initialize the adapter with a legacy agent.

        Args:
            legacy_agent: The legacy agent instance to wrap
            memory: Optional memory interface (creates SimpleDictMemory if not provided)
        """
        self.legacy_agent = legacy_agent
        self.memory = memory or SimpleDictMemory()
        logger.info(f"Wrapped legacy agent: {type(legacy_agent).__name__}")

    def observe(self, input_data: Dict[str, Any]) -> ObservationData:
        """
        Observe: Wrap input data in ObservationData structure.

        For legacy agents, this simply packages the input.
        """
        return ObservationData(
            timestamp=datetime.now(UTC),
            source="legacy_agent",
            data=input_data,
            metadata={"agent_type": type(self.legacy_agent).__name__}
        )

    def orient(self, observation: ObservationData) -> OrientationResult:
        """
        Orient: Prepare context for legacy agent processing.

        For legacy agents, this extracts the raw data and prepares
        it for the legacy process() method.
        """
        # Legacy agents may not have orientation logic
        # Just pass through with context
        return OrientationResult(
            context={"observation": observation.data},
            analysis="Legacy agent - no explicit orientation",
            confidence=1.0,
            alternatives=[]
        )

    def decide(self, orientation: OrientationResult) -> Decision:
        """
        Decide: Determine action for legacy agent.

        For legacy agents, the decision is to call their process() method.
        """
        return Decision(
            action="process_legacy",
            parameters=orientation.context,
            reasoning="Execute legacy agent process method",
            confidence=1.0,
            timestamp=datetime.now(UTC)
        )

    def act(self, decision: Decision) -> ActionResult:
        """
        Act: Execute the legacy agent's process method.

        This is where the actual legacy agent logic is invoked.
        """
        try:
            # Extract input data
            input_data = decision.parameters.get("observation", {})

            # Call legacy agent's process method
            if hasattr(self.legacy_agent, "process"):
                output = self.legacy_agent.process(input_data)
            elif hasattr(self.legacy_agent, "execute"):
                output = self.legacy_agent.execute(input_data)
            elif hasattr(self.legacy_agent, "run"):
                output = self.legacy_agent.run(input_data)
            else:
                # Fallback: call the agent directly
                output = self.legacy_agent(input_data)

            return ActionResult(
                success=True,
                output=output,
                metrics={"execution_time": 0.0},
                errors=[]
            )

        except Exception as e:
            logger.error(f"Legacy agent execution failed: {e}")
            return ActionResult(
                success=False,
                output=None,
                metrics={"execution_time": 0.0},
                errors=[str(e)]
            )


def wrap_legacy_agent(agent: Any, memory: Optional[MemoryInterface] = None) -> Planner:
    """
    Convenience function to wrap a legacy agent.

    Args:
        agent: Legacy agent instance
        memory: Optional memory interface

    Returns:
        Planner-compliant wrapped agent
    """
    return LegacyAgentAdapter(agent, memory)


# Example migration guide
