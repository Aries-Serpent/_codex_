"""
Loop Guardrails

Implements loop detection, recovery, and guardrails for agent execution.
Prevents infinite loops and repeated action patterns.
"""

import hashlib
import json
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Optional


@dataclass
class ActionRecord:
    """Record of an agent action."""

    action_type: str
    action_hash: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    tool_name: Optional[str] = None
    parameters_hash: Optional[str] = None
    produced_artifacts: bool = False
    result_hash: Optional[str] = None

    def matches(self, other: "ActionRecord") -> bool:
        """Check if this action matches another (potential repeat)."""
        return (
            self.action_type == other.action_type
            and self.action_hash == other.action_hash
            and self.parameters_hash == other.parameters_hash
        )


@dataclass
class GuardrailViolation:
    """Record of a guardrail violation."""

    violation_type: str
    message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    action_history: list[str] = field(default_factory=list)
    recommended_action: str = ""


class LoopGuardrail:
    """
    Detect and prevent infinite loops in agent execution.

    Features:
    - Consecutive repeat detection (≥3 without new artifacts)
    - Pattern-based loop detection
    - Automatic recovery injection
    - Configurable thresholds
    """

    def __init__(
        self,
        max_consecutive_repeats: int = 3,
        history_size: int = 100,
        pattern_window: int = 10,
        recovery_callback: Optional[Callable[[GuardrailViolation], str]] = None,
    ):
        """
        Initialize guardrail.

        Args:
            max_consecutive_repeats: Max same action without new artifacts
            history_size: Number of actions to keep in history
            pattern_window: Window size for pattern detection
            recovery_callback: Function to generate recovery message
        """
        self.max_consecutive_repeats = max_consecutive_repeats
        self.history_size = history_size
        self.pattern_window = pattern_window
        self._recovery_callback = recovery_callback or self._default_recovery

        # Action history
        self._history: deque = deque(maxlen=history_size)
        self._violations: list[GuardrailViolation] = []

        # Counters
        self._consecutive_count = 0
        self._last_action_hash: Optional[str] = None

    def record_action(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),  # type: ignore[arg-type]
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def check_before_action(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
    ) -> Optional[str]:
        """
        Pre-check if action would violate guardrails.

        Returns recovery message if would violate, None if safe.
        """
        action_hash = self._hash_action(action_type, tool_name, parameters)

        # Check if this would be a repeat
        if action_hash == self._last_action_hash:
            predicted_count = self._consecutive_count + 1
            if predicted_count >= self.max_consecutive_repeats:
                # Preemptively suggest alternative
                return self._generate_alternative_suggestion(action_type, tool_name)

        return None

    def get_recovery_message(self) -> str:
        """Get recovery message for current state."""
        if self._violations:
            return self._recovery_callback(self._violations[-1])
        return self._default_recovery(None)

    def get_metrics(self) -> dict:
        """Get guardrail metrics."""
        return {
            "actions_recorded": len(self._history),
            "violations_count": len(self._violations),
            "current_consecutive": self._consecutive_count,
            "violation_types": self._count_violation_types(),
        }

    def reset(self):
        """Reset guardrail state."""
        self._history.clear()
        self._violations.clear()
        self._consecutive_count = 0
        self._last_action_hash = None

    def _hash_action(
        self, action_type: str, tool_name: Optional[str], parameters: Optional[dict]
    ) -> str:
        """Generate hash for action identification."""
        content = f"{action_type}:{tool_name or ''}"
        if parameters:
            # Sort keys for consistent hashing
            content += ":" + json.dumps(parameters, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def _hash_dict(self, d: dict) -> str:
        """Hash a dictionary."""
        return hashlib.sha256(json.dumps(d, sort_keys=True, default=str).encode()).hexdigest()[:12]

    def _hash_result(self, result: Any) -> str:
        """Hash a result value."""
        if isinstance(result, (dict, list)):
            content = json.dumps(result, sort_keys=True, default=str)
        else:
            content = str(result)
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def _check_pattern_loop(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def _count_violation_types(self) -> dict[str, int]:
        """Count violations by type."""
        counts: dict[str, Any] = {}
        for v in self._violations:
            counts[v.violation_type] = counts.get(v.violation_type, 0) + 1
        return counts

    def _default_recovery(self, violation: Optional[GuardrailViolation]) -> str:
        """Generate default recovery message."""
        return (
            "LOOP DETECTED: The same action has been repeated multiple times "
            "without producing new results. Please:\n"
            "1. Stop and analyze the current state\n"
            "2. Try a different approach or tool\n"
            "3. If stuck, summarize findings and request guidance\n"
            "4. Consider if the goal has already been achieved"
        )

    def _generate_alternative_suggestion(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "read": "Try reading a different file or section",
            "edit": "Verify changes were applied before editing again",
            "run": "Check command output before re-running",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"
