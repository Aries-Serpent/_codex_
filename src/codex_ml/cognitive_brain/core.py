"""Core cognitive brain functionality.

This module provides the main CognitiveBrain class that integrates
reasoning engines, context management, and decision-making capabilities.
"""

from __future__ import annotations

from typing import Any

from .context_manager import ContextManager
from .reasoning import ReasoningEngine


class CognitiveBrain:
    """Main cognitive brain component for codex_ml.

    Integrates reasoning engines, context management, and provides
    the main interface for cognitive operations in the codex_ml system.

    The CognitiveBrain coordinates multiple components:
    - ReasoningEngine: Performs reasoning operations
    - ContextManager: Manages reasoning context and state
    - Configuration: Settings for brain operation

    Attributes:
        config (dict): Configuration dictionary for the brain
        reasoning_engine (ReasoningEngine): Engine for reasoning operations
        context_manager (ContextManager): Manager for reasoning context
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize the CognitiveBrain.

        Args:
            config: Optional configuration dictionary for brain initialization

        Example:
            >>> config = {"strategy": "default", "temperature": 0.7}
            >>> brain = CognitiveBrain(config)
            >>> brain.initialize()
        """
        self.config = config or {}
        self.reasoning_engine = ReasoningEngine(
            strategy=self.config.get("strategy", "default")
        )
        self.context_manager = ContextManager()
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the cognitive brain.

        Prepares the brain for operation, setting up reasoning engines,
        context managers, and loading any configured parameters.

        Returns:
            None

        Raises:
            RuntimeError: If initialization fails
        """
        if self._initialized:
            return

        # Set up reasoning engine with config
        if "strategy" in self.config:
            self.reasoning_engine.set_strategy(self.config["strategy"])

        # Initialize context with config values
        if "initial_context" in self.config:
            for key, value in self.config["initial_context"].items():
                self.context_manager.store_context(key, value)

        self._initialized = True

    def process_input(self, input_data: Any) -> Any:
        """Process input through the cognitive brain.

        Takes input data, processes it through the reasoning engine,
        and returns a result based on reasoning operations.

        Args:
            input_data: Input to process through the brain

        Returns:
            Processed result from reasoning

        Raises:
            RuntimeError: If brain is not initialized
        """
        if not self._initialized:
            raise RuntimeError("Brain not initialized; call initialize() first")

        # Store input in context
        self.context_manager.store_context("current_input", input_data)

        # Perform reasoning
        result = self.reasoning_engine.reason_about(input_data, self.context_manager.get_all_context())

        return result

    def generate_output(self, reasoning_result: Any) -> Any:
        """Generate output from reasoning results.

        Takes reasoning results and generates final output, applying
        any post-processing or formatting as needed.

        Args:
            reasoning_result: Result from reasoning operations

        Returns:
            Final output to be returned to caller
        """
        if reasoning_result is None:
            raise ValueError("reasoning_result cannot be None")

        # Generate output from reasoning result
        output = {
            "result": reasoning_result,
            "context": self.context_manager.get_all_context(),
            "reasoning_history_length": len(self.reasoning_engine.get_history()),
        }

        return output

    def reset(self) -> None:
        """Reset the cognitive brain to initial state.

        Clears context, resets reasoning engine, and prepares for
        new cognitive operations.

        Returns:
            None
        """
        self.context_manager.clear_context()
        self.reasoning_engine.clear_history()
        self._initialized = False

    def get_status(self) -> dict[str, Any]:
        """Get current status of the cognitive brain.

        Returns information about initialization state, configuration,
        and reasoning history.

        Returns:
            Dictionary containing status information
        """
        return {
            "initialized": self._initialized,
            "config": self.config.copy(),
            "strategy": self.reasoning_engine._strategy,
            "reasoning_history_length": len(self.reasoning_engine.get_history()),
            "context_size": len(self.context_manager.get_all_context()),
        }
