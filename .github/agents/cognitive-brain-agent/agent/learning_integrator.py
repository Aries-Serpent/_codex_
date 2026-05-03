"""
Learning Integrator - Integration layer between Cognitive Brain and Learning Engine.

Provides seamless integration of Q-learning with the Cognitive Brain system.
"""
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

# Try imports
try:
    from ...core.adaptive_learning import AdaptiveLearningEngine, RewardShaper
except ImportError:
    AdaptiveLearningEngine = None
    RewardShaper = None


@dataclass
class LearningConfig:
    """Configuration for learning integration.

    Attributes:
        learning_rate: Initial learning rate (adapts ±20%)
        discount_factor: Future reward discount
        epsilon: Exploration rate
        batch_size: Replay batch size
        memory_capacity: Replay buffer capacity
        target_k1: Target k₁ value for optimization
    """
    learning_rate: float = 0.12
    discount_factor: float = 0.95
    epsilon: float = 0.1
    epsilon_decay: float = 0.995
    epsilon_min: float = 0.01
    batch_size: int = 64
    memory_capacity: int = 100_000
    target_k1: float = 0.33


@dataclass
class LearningMetrics:
    """Metrics for learning performance.

    Attributes:
        episodes: Total episodes completed
        avg_reward: Moving average reward
        q_convergence: Q-value convergence measure
        k1_current: Current k₁ value
        improvement_rate: Rate of improvement
    """
    episodes: int = 0
    avg_reward: float = 0.0
    q_convergence: float = 0.0
    k1_current: float = 0.35
    improvement_rate: float = 0.0


class LearningIntegrator:
    """Integrates Q-learning with Cognitive Brain system.

    Provides a unified interface for:
    - Learning engine management
    - Brain memory integration
    - Policy persistence
    - Performance monitoring

    Example:
        integrator = LearningIntegrator()
        integrator.initialize()

        # Process a decision
        action = integrator.select_action(state)
        reward = integrator.process_outcome(state, action, result)

        # Get performance
        metrics = integrator.get_metrics()
    """

    def __init__(
        self,
        config: Optional[LearningConfig] = None,
        brain: Optional[Any] = None,
        policy_path: Optional[Path] = None,
    ):
        """Initialize learning integrator.

        Args:
            config: Learning configuration
            brain: CognitiveBrain instance for memory integration
            policy_path: Path to save/load policy
        """
        self.config = config or LearningConfig()
        self.brain = brain
        self.policy_path = policy_path

        self.engine: Optional[Any] = None
        self.reward_shaper: Optional[Any] = None
        self.metrics = LearningMetrics()

        # Action registry
        self.actions: list[str] = []

        # Session tracking
        self.session_rewards: list[float] = []
        self.initialized = False

    def initialize(self, actions: Optional[list[str]] = None) -> None:
        """Initialize the learning engine.

        Args:
            actions: List of available actions
        """
        if AdaptiveLearningEngine is None:
            # Fallback if import failed
            self.initialized = False
            return

        self.engine = AdaptiveLearningEngine(
            learning_rate=self.config.learning_rate,
            discount_factor=self.config.discount_factor,
            epsilon=self.config.epsilon,
            epsilon_decay=self.config.epsilon_decay,
            epsilon_min=self.config.epsilon_min,
            buffer_capacity=self.config.memory_capacity,
            batch_size=self.config.batch_size,
        )

        if RewardShaper:
            self.reward_shaper = RewardShaper()

        # Register actions
        self.actions = actions or [
            'approve', 'reject', 'defer', 'escalate',
            'optimize', 'validate', 'skip',
        ]
        self.engine.register_actions(self.actions)

        # Load existing policy if available
        if self.policy_path and self.policy_path.exists():
            self._load_policy()

        self.initialized = True

    def select_action(self, state: dict[str, Any]) -> str:
        """Select action using Q-learning.

        Args:
            state: Current state features

        Returns:
            Selected action identifier
        """
        if not self.initialized or not self.engine:
            # Default action without learning
            return self.actions[0] if self.actions else 'default'

        # Augment state with brain memory if available
        if self.brain:
            state = self._augment_state_with_memory(state)

        return self.engine.select_action(state)

    def process_outcome(
        self,
        state: dict[str, Any],
        action: str,
        success: bool,
        output: Optional[dict[str, Any]] = None,
        next_state: Optional[dict[str, Any]] = None,
    ) -> float:
        """Process action outcome and update learning.

        Args:
            state: State when action was taken
            action: Action that was taken
            success: Whether action succeeded
            output: Action output with metrics
            next_state: Resulting state

        Returns:
            Calculated reward
        """
        if not self.initialized or not self.engine:
            return 1.0 if success else -1.0

        # Calculate reward
        reward = self._calculate_reward(success, output)

        # Update Q-values
        next_state = next_state or state
        self.engine.update(
            state=state,
            action=action,
            reward=reward,
            next_state=next_state,
            done=True,
        )

        # Learn from replay
        self.engine.learn_from_replay()

        # Track session reward
        self.session_rewards.append(reward)

        # Store in brain memory if available
        if self.brain:
            self._store_in_memory(state, action, reward, success)

        return reward

    def end_episode(self) -> LearningMetrics:
        """End current learning episode.

        Returns:
            Updated learning metrics
        """
        if not self.initialized or not self.engine:
            return self.metrics

        # Calculate episode reward
        episode_reward = sum(self.session_rewards) if self.session_rewards else 0.0

        # End episode in engine
        self.engine.end_episode(episode_reward)

        # Update metrics
        self.metrics.episodes = self.engine.state.episodes
        self.metrics.avg_reward = self.engine.state.avg_reward
        self.metrics.q_convergence = self.engine.state.q_value_convergence

        # Calculate improvement rate
        if len(self.session_rewards) > 1:
            recent = self.session_rewards[-10:]
            older = self.session_rewards[-20:-10] if len(self.session_rewards) >= 20 else []
            if older:
                self.metrics.improvement_rate = (
                    (sum(recent) / len(recent)) - (sum(older) / len(older))
                )

        # Clear session rewards
        self.session_rewards.clear()

        # Auto-save policy
        if self.policy_path:
            self._save_policy()

        return self.metrics

    def _calculate_reward(self, success: bool, output: Optional[dict[str, Any]]) -> float:
        """Calculate reward using reward shaper.

        Args:
            success: Whether action succeeded
            output: Action output with metrics

        Returns:
            Shaped reward value
        """
        if self.reward_shaper and output:
            reward, _ = self.reward_shaper.compute_reward(
                accuracy=output.get('accuracy', 0.8 if success else 0.2),
                speed=output.get('speed', 0.7),
                confidence=output.get('confidence', 0.6),
                coherence=output.get('coherence', 0.5),
                error_count=0 if success else 1,
            )
            return reward

        # Simple reward
        return 1.0 if success else -0.5

    def _augment_state_with_memory(self, state: dict[str, Any]) -> dict[str, Any]:
        """Augment state with relevant memory patterns.

        Args:
            state: Original state

        Returns:
            Augmented state with memory features
        """
        if not self.brain or not hasattr(self.brain, 'get_relevant_patterns'):
            return state

        # Get relevant patterns from memory
        patterns = self.brain.get_relevant_patterns(state)

        # Add pattern features
        augmented = state.copy()
        augmented['memory_patterns'] = len(patterns)
        augmented['memory_confidence'] = max((p.confidence for p in patterns), default=0.0)

        return augmented

    def _store_in_memory(
        self,
        state: dict[str, Any],
        action: str,
        reward: float,
        success: bool,
    ) -> None:
        """Store experience in brain memory.

        Args:
            state: State when action was taken
            action: Action taken
            reward: Reward received
            success: Whether succeeded
        """
        if not self.brain or not hasattr(self.brain, 'store_experience'):
            return

        self.brain.store_experience(
            state=state,
            action=action,
            reward=reward,
            success=success,
        )

    def _save_policy(self) -> None:
        """Save current policy to file."""
        if not self.engine or not self.policy_path:
            return

        policy = self.engine.save_policy()
        self.policy_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.policy_path, 'w') as f:
            json.dump(policy, f, indent=2, default=str)

    def _load_policy(self) -> None:
        """Load policy from file."""
        if not self.engine or not self.policy_path:
            return

        try:
            with open(self.policy_path, 'r') as f:
                policy = json.load(f)
            self.engine.load_policy(policy)
        except Exception:
            pass  # Start fresh if loading fails

    def get_metrics(self) -> LearningMetrics:
        """Get current learning metrics.

        Returns:
            Learning metrics
        """
        if self.engine:
            self.metrics.episodes = self.engine.state.episodes
            self.metrics.avg_reward = self.engine.state.avg_reward
            self.metrics.q_convergence = self.engine.state.q_value_convergence

        return self.metrics

    def get_statistics(self) -> dict[str, Any]:
        """Get comprehensive statistics.

        Returns:
            Statistics dictionary
        """
        stats = {
            'initialized': self.initialized,
            'actions': self.actions,
            'metrics': {
                'episodes': self.metrics.episodes,
                'avg_reward': self.metrics.avg_reward,
                'q_convergence': self.metrics.q_convergence,
                'improvement_rate': self.metrics.improvement_rate,
            },
        }

        if self.engine:
            stats['engine'] = self.engine.get_statistics()

        if self.reward_shaper:
            stats['reward_shaper'] = self.reward_shaper.get_statistics()

        return stats
