"""Reasoning engine for cognitive brain operations.

This module provides reasoning capabilities including strategy implementation,
chaining, and hypothesis exploration for complex cognitive tasks.
"""

from __future__ import annotations

from typing import Any, Callable


class ReasoningEngine:
    """Reasoning engine for cognitive brain decision-making.

    Implements various reasoning strategies and provides methods for
    chaining reasoning operations, maintaining reasoning state, and
    supporting multiple reasoning approaches.

    Attributes:
        _strategy (str): Current reasoning strategy
        _reasoning_history (list): History of reasoning operations
    """

    def __init__(self, strategy: str = "default") -> None:
        """Initialize the reasoning engine with a strategy.

        Args:
            strategy: Name of the reasoning strategy to use (default: "default")
        """
        self._strategy = strategy
        self._reasoning_history: list[dict[str, Any]] = []

    def reason_about(self, problem: Any, context: dict[str, Any] | None = None) -> Any:
        """Perform reasoning about a given problem.

        Analyzes the problem using the configured strategy and returns
        a reasoning result that may include hypotheses, steps, or conclusions.

        Args:
            problem: The problem to reason about
            context: Optional context information for reasoning

        Returns:
            Reasoning result containing hypothesis or conclusion

        Raises:
            ValueError: If problem is not valid for reasoning
        """
        if problem is None:
            raise ValueError("Problem cannot be None")

        reasoning_record = {
            "strategy": self._strategy,
            "problem": problem,
            "context": context or {},
            "result": None,
        }

        # Implement basic reasoning (can be strategy-specific)
        if self._strategy == "default":
            result = self._default_reasoning(problem, context or {})
        else:
            result = self._default_reasoning(problem, context or {})

        reasoning_record["result"] = result
        self._reasoning_history.append(reasoning_record)
        return result

    def _default_reasoning(self, problem: Any, context: dict[str, Any]) -> dict[str, Any]:
        """Default reasoning strategy implementation.

        Args:
            problem: The problem to reason about
            context: Context information for reasoning

        Returns:
            Dictionary containing reasoning results
        """
        return {
            "hypothesis": f"Reasoning about: {problem}",
            "confidence": 0.5,
            "steps": 1,
            "context_used": len(context),
        }

    def chain_reasoning(self, problems: list[Any], context: dict[str, Any] | None = None) -> list[Any]:
        """Chain reasoning operations across multiple problems.

        Performs sequential reasoning where each step builds on previous
        reasoning results.

        Args:
            problems: List of problems to reason about sequentially
            context: Optional context for chained reasoning

        Returns:
            List of reasoning results for each problem
        """
        results = []
        current_context = context or {}

        for problem in problems:
            result = self.reason_about(problem, current_context)
            results.append(result)
            # Update context with result for next step
            current_context.update({"previous_result": result})

        return results

    def set_strategy(self, strategy: str) -> None:
        """Change the reasoning strategy.

        Args:
            strategy: Name of the new strategy to use

        Returns:
            None
        """
        self._strategy = strategy

    def get_history(self) -> list[dict[str, Any]]:
        """Get the history of reasoning operations.

        Returns:
            List of reasoning records
        """
        return self._reasoning_history.copy()

    def clear_history(self) -> None:
        """Clear the reasoning history.

        Returns:
            None
        """
        self._reasoning_history.clear()

    def set_custom_reasoner(self, reasoner: Callable[[Any, dict], Any]) -> None:
        """Set a custom reasoning function.

        Args:
            reasoner: Callable that takes (problem, context) and returns result

        Returns:
            None
        """
        self._custom_reasoner = reasoner

    def reason_with_custom(self, problem: Any, context: dict[str, Any] | None = None) -> Any:
        """Perform reasoning using a custom reasoning function.

        Args:
            problem: The problem to reason about
            context: Optional context information

        Returns:
            Result from the custom reasoner
        """
        if not hasattr(self, "_custom_reasoner"):
            raise RuntimeError("No custom reasoner set; use set_custom_reasoner()")
        return self._custom_reasoner(problem, context or {})
