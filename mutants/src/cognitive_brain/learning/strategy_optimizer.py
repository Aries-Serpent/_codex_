"""
Strategy Optimizer for Adaptive Learning.

Optimizes decision strategies using Reinforcement Learning algorithms.
Integrates with OutcomeAnalyzer to learn from AfterMath feedback.

AfterMath: Phase 8.3 - Adaptive Learning Engine
PDA: Active - Continuous strategy improvement
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

import numpy as np

from cognitive_brain.learning.outcome_analyzer import OutcomeAnalyzer
from cognitive_brain.learning.rl_algorithms import DQN, PPO, QLearning, RLAlgorithm
from cognitive_brain.models.learning_outcome import LearningOutcome

logger = logging.getLogger(__name__)


class AlgorithmType(Enum):
    """Types of RL algorithms available."""

    Q_LEARNING = "q_learning"
    DQN = "dqn"
    PPO = "ppo"


@dataclass
class StrategyMetrics:
    """
    Metrics for strategy performance.

    Attributes:
        algorithm_type: Type of RL algorithm used
        episodes_trained: Number of training episodes
        average_reward: Average reward over recent episodes
        improvement_percentage: Improvement over baseline
        convergence_episode: Episode where convergence detected
        is_converged: Whether strategy has converged
        performance_stability: Standard deviation of recent performance
    """

    algorithm_type: AlgorithmType
    episodes_trained: int
    average_reward: float
    improvement_percentage: float
    convergence_episode: Optional[int] = None
    is_converged: bool = False
    performance_stability: float = 1.0


class StrategyOptimizer:
    """
    Optimize decision strategies using Reinforcement Learning.

    Integrates with OutcomeAnalyzer to continuously learn from past outcomes
    and improve future decision strategies.

    PDA Loop:
        - [PLAN] Select RL algorithm based on problem characteristics
        - [DO] Train algorithm on historical outcomes
        - [ASSESS] Evaluate strategy improvement, adjust parameters

    AfterMath Integration:
        Continuously learns from past outcomes to improve future decisions.
        Feeds back into decision engine for adaptive behavior.

    Attributes:
        outcome_analyzer: Analyzer for extracting learnings from outcomes
        algorithm: Current RL algorithm instance
        baseline_performance: Baseline performance for comparison
        metrics: Current strategy metrics
    """

    def __init__(
        self,
        outcome_analyzer: Optional[OutcomeAnalyzer] = None,
        algorithm_type: AlgorithmType = AlgorithmType.Q_LEARNING,
    ):
        """
        Initialize strategy optimizer.

        Args:
            outcome_analyzer: Outcome analyzer instance
            algorithm_type: Type of RL algorithm to use
        """
        self.outcome_analyzer = outcome_analyzer or OutcomeAnalyzer()
        self.algorithm_type = algorithm_type
        self.algorithm: Optional[RLAlgorithm] = None
        self.baseline_performance: Optional[float] = None
        self.metrics: Optional[StrategyMetrics] = None

        # Training statistics
        self.training_history: list[float] = []
        self.episode_count = 0
        self.convergence_threshold = 0.01  # For detecting convergence
        self.convergence_window = 100  # Episodes to check for convergence

        # Initialize algorithm
        self._initialize_algorithm()

        logger.info(f"StrategyOptimizer initialized with {algorithm_type.value}")

    def _initialize_algorithm(self):
        """Initialize the selected RL algorithm."""
        if self.algorithm_type == AlgorithmType.Q_LEARNING:
            self.algorithm = QLearning(
                learning_rate=0.1,
                discount_factor=0.99,
                epsilon=0.1,
                epsilon_decay=0.995,
                epsilon_min=0.01,
            )
        elif self.algorithm_type == AlgorithmType.DQN:
            self.algorithm = DQN(
                learning_rate=0.001,
                discount_factor=0.99,
                epsilon=0.1,
                epsilon_decay=0.995,
                epsilon_min=0.01,
                buffer_capacity=10000,
                batch_size=32,
            )
        elif self.algorithm_type == AlgorithmType.PPO:
            self.algorithm = PPO(
                learning_rate=0.0003,
                discount_factor=0.99,
                clip_ratio=0.2,
                gae_lambda=0.95,
                epochs_per_update=4,
            )
        else:
            raise ValueError(f"Unknown algorithm type: {self.algorithm_type}")

    def select_algorithm(self, outcomes: list[LearningOutcome]) -> AlgorithmType:
        """
        Select best RL algorithm based on problem characteristics.

        PDA: PLAN - Analyze problem to choose appropriate algorithm

        Args:
            outcomes: Historical learning outcomes

        Returns:
            Recommended algorithm type
        """
        if not outcomes:
            return AlgorithmType.Q_LEARNING  # Default for simple problems

        # Analyze problem characteristics
        avg_complexity = np.mean([o.context.complexity for o in outcomes])
        num_agents = np.mean([len(o.context.agent_ids) for o in outcomes])

        # Decision logic
        if avg_complexity < 0.3 and num_agents <= 2:
            # Simple problem: Q-Learning
            return AlgorithmType.Q_LEARNING
        if avg_complexity < 0.7:
            # Moderate complexity: DQN
            return AlgorithmType.DQN
        # Complex problem: PPO
        return AlgorithmType.PPO

    def optimize_strategy(
        self,
        outcomes: list[LearningOutcome],
        max_episodes: int = 1000,
        target_improvement: float = 0.2,
    ) -> dict[str, Any]:
        """
        Optimize strategy from historical outcomes.

        PDA Loop:
            - [PLAN] Convert outcomes to RL environment
            - [DO] Train RL algorithm
            - [ASSESS] Measure improvement and convergence

        Args:
            outcomes: Historical learning outcomes to learn from
            max_episodes: Maximum training episodes
            target_improvement: Target improvement percentage (e.g., 0.2 for 20%)

        Returns:
            Optimization results and metrics
        """
        if not outcomes:
            logger.warning("No outcomes provided for optimization")
            return self._get_results()

        logger.info(f"Optimizing strategy on {len(outcomes)} outcomes")

        # Convert outcomes to training data
        states, actions, rewards = self._prepare_training_data(outcomes)

        # Calculate baseline performance
        self.baseline_performance = np.mean(rewards)
        logger.info(f"Baseline performance: {self.baseline_performance:.3f}")

        # Training loop
        converged = False
        for episode in range(max_episodes):
            episode_reward = self._train_episode(states, actions, rewards)
            self.training_history.append(episode_reward)
            self.episode_count += 1

            # Track episode in algorithm
            self.algorithm.track_episode(episode_reward)  # type: ignore[union-attr]

            # Check convergence
            if episode >= self.convergence_window and self._check_convergence():
                converged = True
                logger.info(f"Converged at episode {episode}")
                break

            # Check if target improvement reached
            current_improvement = self._calculate_improvement()
            if current_improvement >= target_improvement:
                logger.info(
                    f"Target improvement {target_improvement:.1%} reached at episode {episode}"
                )
                break

            # Log progress periodically
            if (episode + 1) % 100 == 0:
                avg_reward = np.mean(self.training_history[-100:])
                logger.info(
                    f"Episode {episode + 1}: "
                    f"Avg Reward={avg_reward:.3f}, "
                    f"Improvement={current_improvement:.1%}"
                )

        # Update metrics
        self._update_metrics(converged)

        logger.info(f"Optimization complete: {self.episode_count} episodes")
        return self._get_results()

    def _prepare_training_data(
        self, outcomes: list[LearningOutcome]
    ) -> tuple[list[Any], list[Any], list[float]]:
        """
        Convert outcomes to RL training data.

        Args:
            outcomes: Learning outcomes

        Returns:
            Tuple of (states, actions, rewards)
        """
        states = []
        actions = []
        rewards = []

        for outcome in outcomes:
            # State: encode context
            state = self._encode_state(outcome.context)
            states.append(state)

            # Action: encode decision (simplified)
            action = f"action_{hash(outcome.decision_id) % 3}"
            actions.append(action)

            # Reward: from outcome
            rewards.append(outcome.reward)

        return states, actions, rewards

    def _encode_state(self, context) -> str:
        """
        Encode decision context as state.

        Args:
            context: Decision context

        Returns:
            Encoded state string
        """
        # Discretize continuous values
        complexity_bin = int(context.complexity * 3)  # 0, 1, or 2
        pressure_bin = int(context.time_pressure * 3)

        return f"state_c{complexity_bin}_p{pressure_bin}"

    def _train_episode(self, states: list[Any], actions: list[Any], rewards: list[float]) -> float:
        """
        Train one episode.

        Args:
            states: List of states
            actions: List of actions
            rewards: List of rewards

        Returns:
            Episode reward
        """
        episode_reward = 0.0

        # Simulate episode by stepping through data
        for i in range(len(states)):
            state = states[i]
            action = actions[i]
            reward = rewards[i]
            next_state = states[(i + 1) % len(states)]
            done = i == len(states) - 1

            # Update algorithm
            self.algorithm.update(state, action, reward, next_state, done)  # type: ignore[union-attr]
            episode_reward += reward

        return episode_reward / len(states)

    def _check_convergence(self) -> bool:
        """
        Check if training has converged.

        Convergence detected when performance variance drops below threshold.

        Returns:
            True if converged
        """
        if len(self.training_history) < self.convergence_window:
            return False

        recent_rewards = self.training_history[-self.convergence_window :]
        std_dev = np.std(recent_rewards)

        return std_dev < self.convergence_threshold

    def _calculate_improvement(self) -> float:
        """
        Calculate improvement over baseline.

        Returns:
            Improvement percentage (0.2 = 20% improvement)
        """
        if self.baseline_performance is None or self.baseline_performance == 0:
            return 0.0

        if not self.training_history:
            return 0.0

        # Use recent average
        window = min(100, len(self.training_history))
        current_performance = np.mean(self.training_history[-window:])

        return (current_performance - self.baseline_performance) / abs(self.baseline_performance)

    def _update_metrics(self, converged: bool):
        """
        Update strategy metrics.

        Args:
            converged: Whether training converged
        """
        avg_reward = np.mean(self.training_history[-100:]) if self.training_history else 0.0
        improvement = self._calculate_improvement()

        # Calculate stability (lower is better)
        stability = (
            np.std(self.training_history[-100:]) if len(self.training_history) >= 100 else 1.0
        )

        # Find convergence episode
        convergence_episode = None
        if converged:
            # Backtrack to find when convergence started
            for i in range(len(self.training_history) - self.convergence_window, 0, -1):
                window = self.training_history[i : i + self.convergence_window]
                if np.std(window) < self.convergence_threshold:
                    convergence_episode = i
                else:
                    break

        self.metrics = StrategyMetrics(
            algorithm_type=self.algorithm_type,
            episodes_trained=self.episode_count,
            average_reward=avg_reward,
            improvement_percentage=improvement,
            convergence_episode=convergence_episode,
            is_converged=converged,
            performance_stability=stability,
        )

    def _get_results(self) -> dict[str, Any]:
        """
        Get optimization results.

        Returns:
            Results dictionary
        """
        return {
            "algorithm": self.algorithm_type.value,
            "episodes_trained": self.episode_count,
            "baseline_performance": self.baseline_performance,
            "final_performance": (
                np.mean(self.training_history[-100:]) if self.training_history else 0.0
            ),
            "improvement_percentage": self._calculate_improvement(),
            "converged": self.metrics.is_converged if self.metrics else False,
            "convergence_episode": self.metrics.convergence_episode if self.metrics else None,
            "training_history": self.training_history.copy(),
            "policy": self.algorithm.get_policy() if self.algorithm else None,
        }

    def get_strategy(self) -> dict[str, Any]:
        """
        Get current optimized strategy.

        Returns:
            Strategy representation
        """
        if self.algorithm is None:
            return {}

        return {
            "algorithm": self.algorithm_type.value,
            "policy": self.algorithm.get_policy(),
            "metrics": {
                "episodes": self.episode_count,
                "avg_reward": self.algorithm.get_avg_reward(),
                "improvement": self._calculate_improvement(),
            },
        }

    def apply_strategy(self, state: Any) -> Any:
        """
        Apply optimized strategy to select action for given state.

        Args:
            state: Current state

        Returns:
            Recommended action
        """
        if self.algorithm is None:
            raise ValueError("No algorithm initialized")

        return self.algorithm.select_action(state)

    def get_metrics(self) -> Optional[StrategyMetrics]:
        """
        Get current strategy metrics.

        Returns:
            Strategy metrics or None if not yet optimized
        """
        return self.metrics

    def reset(self):
        """Reset optimizer to initial state."""
        self._initialize_algorithm()
        self.baseline_performance = None
        self.metrics = None
        self.training_history.clear()
        self.episode_count = 0
        logger.info("StrategyOptimizer reset")
