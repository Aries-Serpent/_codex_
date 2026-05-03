"""
Adaptive Learning Engine for Cognitive Brain.

Implements Q-learning based reinforcement learning for continuous
decision quality optimization.

Phase 8.3 Implementation:
- AdaptiveLearningEngine: Q-learning with ε-greedy action selection
- RewardShaper: Multi-component reward function
- ExperienceReplayBuffer: Prioritized experience replay
"""
import hashlib
import random
from collections import deque
from dataclasses import dataclass
from typing import Any


@dataclass
class Experience:
    """Single experience tuple for replay buffer.

    Attributes:
        state: Current state representation
        action: Action taken
        reward: Reward received
        next_state: Resulting state
        done: Whether episode ended
        td_error: Temporal difference error for prioritization
    """
    state: str
    action: str
    reward: float
    next_state: str
    done: bool = False
    td_error: float = 1.0  # Default priority


@dataclass
class LearningState:
    """Tracks learning progress and statistics.

    Attributes:
        episodes: Total episodes completed
        total_reward: Cumulative reward
        avg_reward: Moving average reward
        learning_rate: Current adaptive learning rate
        epsilon: Current exploration rate
        q_value_convergence: Measure of Q-value stability
    """
    episodes: int = 0
    total_reward: float = 0.0
    avg_reward: float = 0.0
    learning_rate: float = 0.12
    epsilon: float = 0.1
    q_value_convergence: float = 0.0
    best_reward: float = float('-inf')
    improvements: int = 0


class ExperienceReplayBuffer:
    """Prioritized experience replay buffer.

    Implements a circular buffer with TD-error based prioritization
    for efficient learning from past experiences.

    Attributes:
        capacity: Maximum buffer size (default: 100,000)
        alpha: Priority exponent (default: 0.6)
        beta: Importance sampling exponent (default: 0.4)
        epsilon: Small constant for numerical stability
    """

    def __init__(
        self,
        capacity: int = 100_000,
        alpha: float = 0.6,
        beta: float = 0.4,
        epsilon: float = 1e-6,
    ):
        """Initialize the replay buffer.

        Args:
            capacity: Maximum number of experiences to store
            alpha: Priority exponent (0 = uniform, 1 = full prioritization)
            beta: Importance sampling correction exponent
            epsilon: Small constant added to priorities
        """
        self.capacity = capacity
        self.alpha = alpha
        self.beta = beta
        self.epsilon = epsilon
        self.buffer: deque = deque(maxlen=capacity)
        self.priorities: deque = deque(maxlen=capacity)
        self._rng = random.Random()  # nosec B311 - Not for crypto

    def add(self, experience: Experience) -> None:
        """Add an experience to the buffer.

        Args:
            experience: The experience tuple to store
        """
        # New experiences get max priority
        max_priority = max(self.priorities) if self.priorities else 1.0
        self.buffer.append(experience)
        self.priorities.append(max_priority)

    def sample(self, batch_size: int = 64) -> tuple[list[Experience], list[float]]:
        """Sample a batch of experiences with prioritization.

        Args:
            batch_size: Number of experiences to sample

        Returns:
            Tuple of (experiences, importance_weights)
        """
        if len(self.buffer) == 0:
            return [], []

        batch_size = min(batch_size, len(self.buffer))

        # Calculate sampling probabilities
        priorities_array = list(self.priorities)
        priorities_sum = sum(p ** self.alpha for p in priorities_array)
        probabilities = [(p ** self.alpha) / priorities_sum for p in priorities_array]

        # Sample indices based on priorities
        indices = self._rng.choices(
            range(len(self.buffer)),
            weights=probabilities,
            k=batch_size
        )

        # Calculate importance sampling weights
        n = len(self.buffer)
        weights = []
        for idx in indices:
            prob = probabilities[idx]
            weight = (1.0 / (n * prob)) ** self.beta
            weights.append(weight)

        # Normalize weights
        max_weight = max(weights)
        weights = [w / max_weight for w in weights]

        experiences = [self.buffer[i] for i in indices]
        return experiences, weights

    def update_priorities(self, indices: list[int], td_errors: list[float]) -> None:
        """Update priorities based on TD errors.

        Args:
            indices: Buffer indices to update
            td_errors: New TD errors for priority calculation
        """
        for idx, td_error in zip(indices, td_errors):
            if 0 <= idx < len(self.priorities):
                self.priorities[idx] = abs(td_error) + self.epsilon

    def __len__(self) -> int:
        return len(self.buffer)

    def clear(self) -> None:
        """Clear the buffer."""
        self.buffer.clear()
        self.priorities.clear()


class RewardShaper:
    """Multi-component reward function with potential-based shaping.

    Computes rewards based on multiple factors:
    - Accuracy: Correctness of decisions
    - Speed: Computational efficiency
    - Confidence: Decision certainty
    - Coherence: Pattern consistency
    - Error penalty: Cost of mistakes

    Default weights:
        R = 0.4·accuracy + 0.25·speed + 0.2·confidence + 0.1·coherence - 0.05·error_penalty
    """

    def __init__(
        self,
        accuracy_weight: float = 0.4,
        speed_weight: float = 0.25,
        confidence_weight: float = 0.2,
        coherence_weight: float = 0.1,
        error_penalty_weight: float = 0.05,
        adaptive_weights: bool = True,
    ):
        """Initialize reward shaper.

        Args:
            accuracy_weight: Weight for accuracy component
            speed_weight: Weight for speed component
            confidence_weight: Weight for confidence component
            coherence_weight: Weight for coherence component
            error_penalty_weight: Weight for error penalty
            adaptive_weights: Whether to adapt weights based on performance
        """
        self.weights = {
            'accuracy': accuracy_weight,
            'speed': speed_weight,
            'confidence': confidence_weight,
            'coherence': coherence_weight,
            'error_penalty': error_penalty_weight,
        }
        self.adaptive_weights = adaptive_weights
        self.component_history: dict[str, list[float]] = {k: [] for k in self.weights}
        self.reward_history: list[float] = []

    def compute_reward(
        self,
        accuracy: float,
        speed: float,
        confidence: float,
        coherence: float,
        error_count: int = 0,
    ) -> tuple[float, dict[str, float]]:
        """Compute shaped reward from components.

        Args:
            accuracy: Decision accuracy [0, 1]
            speed: Normalized speed metric [0, 1]
            confidence: Decision confidence [0, 1]
            coherence: Pattern coherence [0, 1]
            error_count: Number of errors made

        Returns:
            Tuple of (total_reward, component_rewards)
        """
        # Compute component rewards
        components = {
            'accuracy': accuracy * self.weights['accuracy'],
            'speed': speed * self.weights['speed'],
            'confidence': confidence * self.weights['confidence'],
            'coherence': coherence * self.weights['coherence'],
            'error_penalty': -error_count * self.weights['error_penalty'],
        }

        # Total reward
        total_reward = sum(components.values())

        # Track history for adaptive weights
        for key, value in components.items():
            self.component_history[key].append(value)
            # Keep limited history
            if len(self.component_history[key]) > 1000:
                self.component_history[key].pop(0)

        self.reward_history.append(total_reward)
        if len(self.reward_history) > 1000:
            self.reward_history.pop(0)

        return total_reward, components

    def compute_potential(self, state: dict[str, float]) -> float:
        """Compute potential function for shaping.

        Potential-based shaping: F(s, s') = γΦ(s') - Φ(s)

        Args:
            state: State features dictionary

        Returns:
            Potential value for the state
        """
        # Potential based on distance to optimal state
        accuracy = state.get('accuracy', 0.5)
        coherence = state.get('coherence', 0.5)

        # Higher potential for states closer to optimal
        return 0.5 * accuracy + 0.5 * coherence

    def adapt_weights(self, performance_trend: float) -> None:
        """Adapt weights based on performance trend.

        Args:
            performance_trend: Positive = improving, negative = declining
        """
        if not self.adaptive_weights:
            return

        # If performance declining, increase accuracy weight
        if performance_trend < -0.1:
            adjustment = 0.02
            self.weights['accuracy'] = min(0.6, self.weights['accuracy'] + adjustment)
            self.weights['speed'] = max(0.1, self.weights['speed'] - adjustment / 2)
            self.weights['coherence'] = max(0.05, self.weights['coherence'] - adjustment / 2)

        # If performance improving, balance weights
        elif performance_trend > 0.1:
            # Gradually return to defaults
            for key in self.weights:
                default = {'accuracy': 0.4, 'speed': 0.25, 'confidence': 0.2,
                          'coherence': 0.1, 'error_penalty': 0.05}[key]
                self.weights[key] += 0.01 * (default - self.weights[key])

    def get_statistics(self) -> dict[str, float]:
        """Get reward statistics.

        Returns:
            Dictionary of statistics
        """
        if not self.reward_history:
            return {'avg_reward': 0.0, 'max_reward': 0.0, 'min_reward': 0.0}

        return {
            'avg_reward': sum(self.reward_history) / len(self.reward_history),
            'max_reward': max(self.reward_history),
            'min_reward': min(self.reward_history),
            'total_samples': len(self.reward_history),
        }


class AdaptiveLearningEngine:
    """Q-learning based adaptive learning engine.

    Implements reinforcement learning for continuous decision quality
    optimization with:
    - ε-greedy action selection
    - Dynamic learning rate adaptation (±20%)
    - Experience replay for sample efficiency
    - Q-value convergence monitoring

    Parameters:
        learning_rate: Initial learning rate (default: 0.12, adapts ±20%)
        discount_factor: Future reward discount (default: 0.95)
        epsilon: Initial exploration rate (default: 0.1, decays to 0.01)
        epsilon_decay: Decay rate per episode (default: 0.995)
        epsilon_min: Minimum exploration rate (default: 0.01)
    """

    def __init__(
        self,
        learning_rate: float = 0.12,
        discount_factor: float = 0.95,
        epsilon: float = 0.1,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01,
        buffer_capacity: int = 100_000,
        batch_size: int = 64,
    ):
        """Initialize the learning engine.

        Args:
            learning_rate: Initial learning rate
            discount_factor: Discount factor (gamma)
            epsilon: Initial exploration rate
            epsilon_decay: Epsilon decay rate
            epsilon_min: Minimum epsilon value
            buffer_capacity: Replay buffer capacity
            batch_size: Batch size for learning
        """
        self.base_learning_rate = learning_rate
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.batch_size = batch_size

        # Q-table (state -> action -> value)
        self.q_table: dict[str, dict[str, float]] = {}

        # Experience replay
        self.replay_buffer = ExperienceReplayBuffer(capacity=buffer_capacity)

        # Reward shaper
        self.reward_shaper = RewardShaper()

        # Learning state tracking
        self.state = LearningState(learning_rate=learning_rate, epsilon=epsilon)

        # Action space
        self.actions: list[str] = []

        # Q-value history for convergence
        self.q_history: list[float] = []

        # Random generator
        self._rng = random.Random()  # nosec B311 - Not for crypto

    def register_actions(self, actions: list[str]) -> None:
        """Register available actions.

        Args:
            actions: List of action identifiers
        """
        self.actions = actions

    def _get_state_key(self, state: dict[str, Any]) -> str:
        """Convert state dictionary to hashable key.

        Args:
            state: State feature dictionary

        Returns:
            Hashable string key
        """
        # Create deterministic string representation
        # Using full sha256 hexdigest for state hashing to minimize collisions
        sorted_items = sorted(state.items())
        state_str = str(sorted_items)
        return hashlib.sha256(state_str.encode()).hexdigest()

    def get_q_value(self, state: str, action: str) -> float:
        """Get Q-value for state-action pair.

        Args:
            state: State key
            action: Action identifier

        Returns:
            Q-value (0.0 if not seen)
        """
        if state not in self.q_table:
            return 0.0
        return self.q_table[state].get(action, 0.0)

    def get_max_q_value(self, state: str) -> float:
        """Get maximum Q-value for a state.

        Args:
            state: State key

        Returns:
            Maximum Q-value across all actions
        """
        if state not in self.q_table or not self.q_table[state]:
            return 0.0
        return max(self.q_table[state].values())

    def select_action(self, state: dict[str, Any]) -> str:
        """Select action using ε-greedy policy.

        Args:
            state: Current state features

        Returns:
            Selected action identifier
        """
        if not self.actions:
            raise ValueError("No actions registered. Call register_actions() first.")

        state_key = self._get_state_key(state)

        # Exploration
        if self._rng.random() < self.epsilon:
            return self._rng.choice(self.actions)

        # Exploitation
        if state_key not in self.q_table:
            return self._rng.choice(self.actions)

        # Select action with highest Q-value
        action_values = self.q_table[state_key]
        if not action_values:
            return self._rng.choice(self.actions)

        max_q = max(action_values.values())
        best_actions = [a for a, q in action_values.items() if q == max_q]
        return self._rng.choice(best_actions)

    def update(
        self,
        state: dict[str, Any],
        action: str,
        reward: float,
        next_state: dict[str, Any],
        done: bool = False,
    ) -> float:
        """Update Q-value based on experience.

        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Resulting state
            done: Whether episode ended

        Returns:
            TD error
        """
        state_key = self._get_state_key(state)
        next_state_key = self._get_state_key(next_state)

        # Initialize Q-table entry if needed
        if state_key not in self.q_table:
            self.q_table[state_key] = {}
        if action not in self.q_table[state_key]:
            self.q_table[state_key][action] = 0.0

        # Calculate TD target
        current_q = self.q_table[state_key][action]
        if done:
            target = reward
        else:
            target = reward + self.discount_factor * self.get_max_q_value(next_state_key)

        # TD error
        td_error = target - current_q

        # Update Q-value
        self.q_table[state_key][action] += self.learning_rate * td_error

        # Store experience
        experience = Experience(
            state=state_key,
            action=action,
            reward=reward,
            next_state=next_state_key,
            done=done,
            td_error=td_error,
        )
        self.replay_buffer.add(experience)

        # Track Q-value for convergence
        self.q_history.append(self.q_table[state_key][action])
        if len(self.q_history) > 1000:
            self.q_history.pop(0)

        return td_error

    def learn_from_replay(self) -> float:
        """Learn from experience replay buffer.

        Returns:
            Average TD error from batch
        """
        if len(self.replay_buffer) < self.batch_size:
            return 0.0

        experiences, weights = self.replay_buffer.sample(self.batch_size)

        td_errors = []
        for exp, weight in zip(experiences, weights):
            # Calculate TD target
            current_q = self.get_q_value(exp.state, exp.action)
            if exp.done:
                target = exp.reward
            else:
                target = exp.reward + self.discount_factor * self.get_max_q_value(exp.next_state)

            td_error = target - current_q
            td_errors.append(td_error)

            # Weighted update
            if exp.state not in self.q_table:
                self.q_table[exp.state] = {}
            if exp.action not in self.q_table[exp.state]:
                self.q_table[exp.state][exp.action] = 0.0

            self.q_table[exp.state][exp.action] += self.learning_rate * td_error * weight

        return sum(abs(e) for e in td_errors) / len(td_errors) if td_errors else 0.0

    def end_episode(self, total_reward: float) -> None:
        """End current episode and update statistics.

        Args:
            total_reward: Total reward for the episode
        """
        self.state.episodes += 1
        self.state.total_reward += total_reward

        # Update moving average
        alpha = 0.1  # Smoothing factor
        self.state.avg_reward = alpha * total_reward + (1 - alpha) * self.state.avg_reward

        # Track improvements
        if total_reward > self.state.best_reward:
            self.state.best_reward = total_reward
            self.state.improvements += 1

        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        self.state.epsilon = self.epsilon

        # Adapt learning rate
        self._adapt_learning_rate()

        # Update Q-value convergence
        self._update_convergence()

    def _adapt_learning_rate(self) -> None:
        """Adapt learning rate based on performance (±20%)."""
        if self.state.episodes < 10:
            return

        # Calculate performance trend
        if len(self.q_history) >= 100:
            recent = self.q_history[-50:]
            older = self.q_history[-100:-50]
            trend = (sum(recent) / len(recent)) - (sum(older) / len(older))

            # Adapt learning rate
            if trend > 0.1:  # Improving - can reduce learning rate
                self.learning_rate = max(
                    self.base_learning_rate * 0.8,
                    self.learning_rate * 0.99
                )
            elif trend < -0.1:  # Declining - increase learning rate
                self.learning_rate = min(
                    self.base_learning_rate * 1.2,
                    self.learning_rate * 1.01
                )

            self.state.learning_rate = self.learning_rate

    def _update_convergence(self) -> None:
        """Update Q-value convergence measure."""
        if len(self.q_history) < 100:
            self.state.q_value_convergence = 0.0
            return

        recent = self.q_history[-50:]
        variance = sum((x - sum(recent)/len(recent))**2 for x in recent) / len(recent)

        # Lower variance = higher convergence
        self.state.q_value_convergence = 1.0 / (1.0 + variance)

    def get_statistics(self) -> dict[str, Any]:
        """Get learning statistics.

        Returns:
            Dictionary of statistics
        """
        return {
            'episodes': self.state.episodes,
            'total_reward': self.state.total_reward,
            'avg_reward': self.state.avg_reward,
            'best_reward': self.state.best_reward,
            'improvements': self.state.improvements,
            'learning_rate': self.state.learning_rate,
            'epsilon': self.state.epsilon,
            'q_value_convergence': self.state.q_value_convergence,
            'q_table_size': len(self.q_table),
            'replay_buffer_size': len(self.replay_buffer),
            'reward_stats': self.reward_shaper.get_statistics(),
        }

    def save_policy(self) -> dict[str, Any]:
        """Save current policy for persistence.

        Returns:
            Dictionary containing policy data
        """
        return {
            'q_table': self.q_table,
            'state': {
                'episodes': self.state.episodes,
                'total_reward': self.state.total_reward,
                'avg_reward': self.state.avg_reward,
                'learning_rate': self.state.learning_rate,
                'epsilon': self.state.epsilon,
                'best_reward': self.state.best_reward,
                'improvements': self.state.improvements,
            },
            'actions': self.actions,
            'parameters': {
                'base_learning_rate': self.base_learning_rate,
                'discount_factor': self.discount_factor,
                'epsilon_decay': self.epsilon_decay,
                'epsilon_min': self.epsilon_min,
            },
        }

    def load_policy(self, policy_data: dict[str, Any]) -> None:
        """Load saved policy.

        Args:
            policy_data: Dictionary from save_policy()
        """
        self.q_table = policy_data.get('q_table', {})
        self.actions = policy_data.get('actions', [])

        if 'state' in policy_data:
            state_data = policy_data['state']
            self.state.episodes = state_data.get('episodes', 0)
            self.state.total_reward = state_data.get('total_reward', 0.0)
            self.state.avg_reward = state_data.get('avg_reward', 0.0)
            self.state.learning_rate = state_data.get('learning_rate', self.base_learning_rate)
            self.state.epsilon = state_data.get('epsilon', 0.1)
            self.state.best_reward = state_data.get('best_reward', float('-inf'))
            self.state.improvements = state_data.get('improvements', 0)
            self.epsilon = self.state.epsilon
            self.learning_rate = self.state.learning_rate
