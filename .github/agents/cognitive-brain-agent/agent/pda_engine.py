"""
PDA Engine - Perceive-Decide-Act Loop Implementation.

Provides the core PDA loop pattern for cognitive processing tasks.
"""
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class PDAPhase(Enum):
    """PDA Loop phases."""
    PERCEIVE = "perceive"
    DECIDE = "decide"
    ACT = "act"
    AFTERMATH = "aftermath"


@dataclass
class PerceptionResult:
    """Result from perception phase.

    Attributes:
        features: Extracted features from input
        patterns: Matched patterns from memory
        context: Additional context information
        confidence: Perception confidence score
    """
    features: dict[str, Any] = field(default_factory=dict)
    patterns: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0


@dataclass
class DecisionResult:
    """Result from decision phase.

    Attributes:
        action: Selected action identifier
        alternatives: Alternative actions considered
        confidence: Decision confidence score
        reasoning: Explanation for decision
    """
    action: str
    alternatives: list[str] = field(default_factory=list)
    confidence: float = 1.0
    reasoning: str = ""


@dataclass
class ActionResult:
    """Result from action phase.

    Attributes:
        success: Whether action succeeded
        output: Action output data
        duration_ms: Execution time in milliseconds
        side_effects: Any side effects produced
    """
    success: bool
    output: Any = None
    duration_ms: float = 0.0
    side_effects: list[str] = field(default_factory=list)


@dataclass
class AfterMathResult:
    """Result from aftermath phase.

    Attributes:
        reward: Calculated reward
        patterns_extracted: New patterns extracted
        learning_updates: Number of learning updates
        metrics: Performance metrics
    """
    reward: float = 0.0
    patterns_extracted: list[str] = field(default_factory=list)
    learning_updates: int = 0
    metrics: dict[str, float] = field(default_factory=dict)


class PDAEngine:
    """PDA Loop Engine for cognitive processing.

    Implements the Perceive-Decide-Act pattern with AfterMath processing
    for continuous learning and improvement.

    Example:
        engine = PDAEngine()

        @engine.perceiver
        def my_perceiver(input_data):
            return PerceptionResult(features={'key': 'value'})

        @engine.decider
        def my_decider(perception):
            return DecisionResult(action='process')

        @engine.actor
        def my_actor(decision, context):
            return ActionResult(success=True, output={'result': 'done'})

        result = engine.run(input_data)
    """

    def __init__(self):
        """Initialize PDA Engine."""
        self._perceiver: Optional[Callable] = None
        self._decider: Optional[Callable] = None
        self._actor: Optional[Callable] = None
        self._aftermath_handler: Optional[Callable] = None

        self.current_phase: Optional[PDAPhase] = None
        self.run_history: list[dict[str, Any]] = []

    def perceiver(self, func: Callable) -> Callable:
        """Decorator to register perceiver function.

        Args:
            func: Function that takes input_data and returns PerceptionResult

        Returns:
            The decorated function
        """
        self._perceiver = func
        return func

    def decider(self, func: Callable) -> Callable:
        """Decorator to register decider function.

        Args:
            func: Function that takes PerceptionResult and returns DecisionResult

        Returns:
            The decorated function
        """
        self._decider = func
        return func

    def actor(self, func: Callable) -> Callable:
        """Decorator to register actor function.

        Args:
            func: Function that takes DecisionResult and context, returns ActionResult

        Returns:
            The decorated function
        """
        self._actor = func
        return func

    def aftermath(self, func: Callable) -> Callable:
        """Decorator to register aftermath handler.

        Args:
            func: Function that takes all results and returns AfterMathResult

        Returns:
            The decorated function
        """
        self._aftermath_handler = func
        return func

    def run(self, input_data: Any, context: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Run the full PDA loop.

        Args:
            input_data: Input data to process
            context: Optional context dictionary

        Returns:
            Dictionary with all phase results
        """
        context = context or {}
        results = {
            'input': input_data,
            'context': context,
            'phases': {},
            'success': False,
        }

        start_time = time.time()

        try:
            # Phase 1: Perceive
            self.current_phase = PDAPhase.PERCEIVE
            if self._perceiver:
                perception = self._perceiver(input_data)
            else:
                perception = PerceptionResult()
            results['phases']['perceive'] = perception

            # Phase 2: Decide
            self.current_phase = PDAPhase.DECIDE
            if self._decider:
                decision = self._decider(perception)
            else:
                decision = DecisionResult(action='default')
            results['phases']['decide'] = decision

            # Phase 3: Act
            self.current_phase = PDAPhase.ACT
            action_start = time.time()
            if self._actor:
                action_result = self._actor(decision, context)
            else:
                action_result = ActionResult(success=True)
            action_result.duration_ms = (time.time() - action_start) * 1000
            results['phases']['act'] = action_result

            # Phase 4: AfterMath
            self.current_phase = PDAPhase.AFTERMATH
            if self._aftermath_handler:
                aftermath = self._aftermath_handler(perception, decision, action_result)
            else:
                aftermath = AfterMathResult()
            results['phases']['aftermath'] = aftermath

            results['success'] = action_result.success

        except Exception as e:
            results['error'] = str(e)
            results['success'] = False

        finally:
            self.current_phase = None
            results['total_duration_ms'] = (time.time() - start_time) * 1000

        self.run_history.append(results)
        return results

    def get_statistics(self) -> dict[str, Any]:
        """Get engine statistics.

        Returns:
            Statistics dictionary
        """
        if not self.run_history:
            return {'runs': 0}

        successes = sum(1 for r in self.run_history if r.get('success', False))
        durations = [r.get('total_duration_ms', 0) for r in self.run_history]

        return {
            'runs': len(self.run_history),
            'success_rate': successes / len(self.run_history),
            'avg_duration_ms': sum(durations) / len(durations),
            'min_duration_ms': min(durations),
            'max_duration_ms': max(durations),
        }

    def clear_history(self) -> None:
        """Clear run history."""
        self.run_history.clear()
