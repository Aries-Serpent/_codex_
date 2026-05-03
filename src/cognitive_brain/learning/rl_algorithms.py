"""
Reinforcement Learning Algorithms for Strategy Optimization.

Implements Q-Learning, Deep Q-Network (DQN), and Proximal Policy Optimization (PPO)
for adaptive decision-making in the cognitive brain.

AfterMath: Phase 8.3 - Adaptive Learning Engine
PDA: Active - Continuous strategy improvement through RL
"""

import logging
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from typing import Any, Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class Experience:
    """Single experience tuple for replay buffer."""

    state: Any
    action: Any
    reward: float
    next_state: Any
    done: bool


class ReplayBuffer:
    """
    Experience replay buffer for DQN.

    Stores transitions and samples random batches for training.

    PDA Loop:
        - [PLAN] Store diverse experiences
        - [DO] Sample random batches
        - [AFTERMATH] Track buffer statistics
    """

    def __init__(self, capacity: int = 10000):
        """
        Initialize replay buffer.

        Args:
            capacity: Maximum number of experiences to store
        """
        self.buffer: deque[Any] = deque(maxlen=capacity)
        self.capacity = capacity

    def add(self, state: Any, action: Any, reward: float, next_state: Any, done: bool):
        """Add experience to buffer."""
        experience = Experience(state, action, reward, next_state, done)
        self.buffer.append(experience)

    def sample(self, batch_size: int) -> list[Experience]:
        """
        Sample random batch of experiences.

        Args:
            batch_size: Number of experiences to sample

        Returns:
            List of sampled experiences
        """
        if len(self.buffer) < batch_size:
            return list(self.buffer)

        indices = np.random.choice(len(self.buffer), batch_size, replace=False)
        return [self.buffer[i] for i in indices]

    def __len__(self) -> int:
        """Return current buffer size."""
        return len(self.buffer)

    def clear(self):
        """Clear all experiences."""
        self.buffer.clear()


class RLAlgorithm(ABC):
    """
    Base class for RL algorithms.

    Defines interface for all RL algorithms used in strategy optimization.

    AfterMath: Tracks algorithm performance across episodes
    """

    def __init__(self, learning_rate: float = 0.1, discount_factor: float = 0.99):
        """
        Initialize RL algorithm.

        Args:
            learning_rate: Learning rate (α)
            discount_factor: Discount factor (γ)
        """
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.episode_count = 0
        self.total_reward = 0.0
        self.episode_rewards: list[float] = []

    @abstractmethod
    def select_action(self, state: Any) -> Any:
        """
        Select action given current state.

        Args:
            state: Current state

        Returns:
            Selected action
        """

    @abstractmethod
    def update(self, state: Any, action: Any, reward: float, next_state: Any, done: bool):
        """
        Update algorithm with experience.

        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Episode termination flag
        """

    @abstractmethod
    def get_policy(self) -> dict[Any, Any]:
        """
        Get current policy.

        Returns:
            Current policy representation
        """

    def track_episode(self, reward: float):
        """
        Track episode statistics.

        Args:
            reward: Total episode reward
        """
        self.episode_count += 1
        self.total_reward += reward
        self.episode_rewards.append(reward)

        if len(self.episode_rewards) > 100:
            self.episode_rewards.pop(0)

    def get_avg_reward(self, window: int = 100) -> float:
        """
        Get average reward over recent episodes.

        Args:
            window: Number of recent episodes

        Returns:
            Average reward
        """
        if not self.episode_rewards:
            return 0.0

        recent = self.episode_rewards[-window:]
        return float(np.mean(recent))


class QLearning(RLAlgorithm):
    """
    Q-Learning with tabular Q-values.

    Suitable for discrete state and action spaces. Uses ε-greedy exploration.

    PDA Loop:
        - [PLAN] Select action via ε-greedy policy
        - [DO] Execute action, observe reward
        - [ASSESS] Update Q-table, adjust ε

    AfterMath: Stores Q-values for strategy persistence

    Attributes:
        q_table: Q-values for (state, action) pairs
        epsilon: Exploration rate
        epsilon_decay: Decay rate for epsilon
        epsilon_min: Minimum exploration rate
    """

    def __init__(
        self,
        learning_rate: float = 0.1,
        discount_factor: float = 0.99,
        epsilon: float = 0.1,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01,
    ):
        """
        Initialize Q-Learning algorithm.

        Args:
            learning_rate: Learning rate (α)
            discount_factor: Discount factor (γ)
            epsilon: Initial exploration rate
            epsilon_decay: Decay rate for epsilon
            epsilon_min: Minimum epsilon value
        """
        super().__init__(learning_rate, discount_factor)
        self.q_table: dict[tuple[Any, Any], float] = {}
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.state_visits: dict[Any, int] = {}
        self.update_count = 0

    def _get_q_value(self, state: Any, action: Any) -> float:
        """Get Q-value for state-action pair."""
        return self.q_table.get((state, action), 0.0)

    def _set_q_value(self, state: Any, action: Any, value: float):
        """Set Q-value for state-action pair."""
        self.q_table[(state, action)] = value

    def select_action(self, state: Any, available_actions: Optional[list[Any]] = None) -> Any:
        """
        Select action using ε-greedy policy.

        Args:
            state: Current state
            available_actions: List of available actions

        Returns:
            Selected action
        """
        if available_actions is None:
            # Get all actions seen from this state
            available_actions = [a for (s, a) in self.q_table if s == state]
            if not available_actions:
                # Explore if no actions known
                return np.random.choice(["action_0", "action_1", "action_2"])

        # ε-greedy selection
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(available_actions)
        # Exploit: best known action
        q_values = [self._get_q_value(state, a) for a in available_actions]
        max_q = max(q_values)
        # Handle ties randomly
        best_actions = [a for a, q in zip(available_actions, q_values, strict=False) if q == max_q]
        return np.random.choice(best_actions)

    def update(self, state: Any, action: Any, reward: float, next_state: Any, done: bool):
        """
        Update Q-values using Bellman equation.

        Q(s,a) ← Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]

        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Episode termination flag
        """
        current_q = self._get_q_value(state, action)

        if done:
            # Terminal state: no future reward
            target_q = reward
        else:
            # Get max Q-value for next state
            next_actions = [a for (s, a) in self.q_table if s == next_state]
            if next_actions:
                next_q_values = [self._get_q_value(next_state, a) for a in next_actions]
                max_next_q = max(next_q_values)
            else:
                max_next_q = 0.0

            target_q = reward + self.discount_factor * max_next_q

        # Q-learning update
        new_q = current_q + self.learning_rate * (target_q - current_q)
        self._set_q_value(state, action, new_q)

        # Track statistics
        self.update_count += 1
        self.state_visits[state] = self.state_visits.get(state, 0) + 1

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def get_policy(self) -> dict[Any, Any]:
        """
        Get greedy policy from Q-table.

        Returns:
            Mapping from states to best actions
        """
        policy = {}
        states = set(s for (s, a) in self.q_table)

        for state in states:
            actions = [a for (s, a) in self.q_table if s == state]
            if actions:
                q_values = [self._get_q_value(state, a) for a in actions]
                best_action = actions[np.argmax(q_values)]
                policy[state] = best_action

        return policy

    def get_state_value(self, state: Any) -> float:
        """
        Get value of state (max Q-value over actions).

        Args:
            state: State to evaluate

        Returns:
            State value
        """
        actions = [a for (s, a) in self.q_table if s == state]
        if not actions:
            return 0.0

        q_values = [self._get_q_value(state, a) for a in actions]
        return max(q_values)


class DQN(RLAlgorithm):
    """
    Deep Q-Network with neural network approximation.

    Uses experience replay and target network for stable training.
    Simplified implementation without actual neural network (uses linear approximation).

    PDA Loop:
        - [PLAN] Store experience in replay buffer
        - [DO] Sample batch and update Q-network
        - [ASSESS] Track loss and update target network

    Architecture (Conceptual):
        - Input: State vector (variable size)
        - Hidden 1: Dense(128, ReLU)
        - Hidden 2: Dense(64, ReLU)
        - Output: Action Q-values

    Training:
        - Experience replay buffer: 10,000 transitions
        - Target network: Soft update (τ=0.005) every 100 steps
        - Batch size: 32
        - Update frequency: Every 4 steps

    Note: This is a simplified version using linear function approximation
    instead of deep neural network for compatibility without PyTorch/TensorFlow.
    """

    def __init__(
        self,
        learning_rate: float = 0.001,
        discount_factor: float = 0.99,
        epsilon: float = 0.1,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01,
        buffer_capacity: int = 10000,
        batch_size: int = 32,
        update_frequency: int = 4,
        target_update_freq: int = 100,
    ):
        """
        Initialize DQN algorithm.

        Args:
            learning_rate: Learning rate for optimizer
            discount_factor: Discount factor (γ)
            epsilon: Initial exploration rate
            epsilon_decay: Decay rate for epsilon
            epsilon_min: Minimum epsilon
            buffer_capacity: Replay buffer size
            batch_size: Training batch size
            update_frequency: Steps between updates
            target_update_freq: Steps between target network updates
        """
        super().__init__(learning_rate, discount_factor)
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.batch_size = batch_size
        self.update_frequency = update_frequency
        self.target_update_freq = target_update_freq

        # Replay buffer
        self.replay_buffer = ReplayBuffer(buffer_capacity)

        # Simplified linear Q-network (weights for state features)
        self.q_weights: dict[Any, np.ndarray] = {}
        self.target_weights: dict[Any, np.ndarray] = {}

        # Training statistics
        self.step_count = 0
        self.update_count = 0
        self.loss_history: list[float] = []

    def _get_q_values(self, state: Any, use_target: bool = False) -> dict[Any, float]:
        """
        Get Q-values for all actions in state.

        Args:
            state: Current state
            use_target: Whether to use target network

        Returns:
            Dictionary mapping actions to Q-values
        """
        weights = self.target_weights if use_target else self.q_weights

        # Simple linear approximation: Q(s,a) = w_a · features(s)
        # For simplicity, use hash of state as feature
        state_feature = float(hash(str(state)) % 1000) / 1000.0

        q_values = {}
        for action in ["action_0", "action_1", "action_2"]:
            if action not in weights:
                weights[action] = np.random.randn() * 0.01
            q_values[action] = weights[action] * state_feature

        return q_values

    def select_action(self, state: Any) -> Any:
        """
        Select action using ε-greedy policy.

        Args:
            state: Current state

        Returns:
            Selected action
        """
        if np.random.random() < self.epsilon:
            # Explore
            return np.random.choice(["action_0", "action_1", "action_2"])
        # Exploit
        q_values = self._get_q_values(state)
        return max(q_values, key=q_values.get)  # type: ignore[arg-type]

    def update(self, state: Any, action: Any, reward: float, next_state: Any, done: bool):
        """
        Store experience and perform batch update.

        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Episode termination flag
        """
        # Store experience in replay buffer
        self.replay_buffer.add(state, action, reward, next_state, done)
        self.step_count += 1

        # Periodic updates
        if (
            self.step_count % self.update_frequency == 0
            and len(self.replay_buffer) >= self.batch_size
        ):
            self._train_step()

        # Update target network
        if self.step_count % self.target_update_freq == 0:
            self._update_target_network()

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def _train_step(self):
        """Perform single training step on batch."""
        # Sample batch from replay buffer
        batch = self.replay_buffer.sample(self.batch_size)

        total_loss = 0.0

        for exp in batch:
            # Current Q-value
            q_values = self._get_q_values(exp.state)
            current_q = q_values[exp.action]

            # Target Q-value
            if exp.done:
                target_q = exp.reward
            else:
                next_q_values = self._get_q_values(exp.next_state, use_target=True)
                max_next_q = max(next_q_values.values())
                target_q = exp.reward + self.discount_factor * max_next_q

            # Compute loss
            loss = (target_q - current_q) ** 2
            total_loss += loss

            # Update weights (simplified gradient descent)
            state_feature = float(hash(str(exp.state)) % 1000) / 1000.0
            gradient = 2 * (current_q - target_q) * state_feature
            self.q_weights[exp.action] -= self.learning_rate * gradient

        avg_loss = total_loss / len(batch)
        self.loss_history.append(avg_loss)
        self.update_count += 1

    def _update_target_network(self):
        """Soft update of target network weights."""
        tau = 0.005  # Soft update parameter

        for action in self.q_weights:
            if action not in self.target_weights:
                self.target_weights[action] = self.q_weights[action]
            else:
                self.target_weights[action] = (
                    tau * self.q_weights[action] + (1 - tau) * self.target_weights[action]
                )

    def get_policy(self) -> dict[Any, Any]:
        """
        Get greedy policy from Q-network.

        Returns:
            Policy (simplified representation)
        """
        return {"type": "DQN", "weights": dict(self.q_weights), "epsilon": self.epsilon}


class PPO(RLAlgorithm):
    """
    Proximal Policy Optimization with actor-critic architecture.

    Simplified implementation using linear approximation for both
    policy (actor) and value (critic) networks.

    PDA Loop:
        - [PLAN] Collect trajectories using current policy
        - [DO] Compute advantages with GAE
        - [ASSESS] Update policy with clipped objective

    Networks (Conceptual):
        - Actor (Policy): π(a|s) - action probabilities
        - Critic (Value): V(s) - state value estimate

    Training:
        - Clip ratio: 0.2
        - GAE λ: 0.95 for advantage estimation
        - Epochs per update: 4
        - Batch size: 64
        - KL divergence target: 0.01

    Note: Simplified version with linear approximation.
    """

    def __init__(
        self,
        learning_rate: float = 0.0003,
        discount_factor: float = 0.99,
        clip_ratio: float = 0.2,
        gae_lambda: float = 0.95,
        epochs_per_update: int = 4,
    ):
        """
        Initialize PPO algorithm.

        Args:
            learning_rate: Learning rate for both networks
            discount_factor: Discount factor (γ)
            clip_ratio: PPO clipping parameter (ε)
            gae_lambda: GAE lambda parameter
            epochs_per_update: Training epochs per update
        """
        super().__init__(learning_rate, discount_factor)
        self.clip_ratio = clip_ratio
        self.gae_lambda = gae_lambda
        self.epochs_per_update = epochs_per_update

        # Policy network (actor) - action probabilities
        self.policy_weights: dict[str, float] = {
            "action_0": 0.0,
            "action_1": 0.0,
            "action_2": 0.0,
        }

        # Value network (critic) - state values
        self.value_weights: dict[Any, float] = {}

        # Trajectory buffer
        self.trajectory: list[dict] = []

        # Statistics
        self.policy_updates = 0
        self.value_loss_history: list[float] = []
        self.policy_loss_history: list[float] = []

    def _get_action_probs(self, state: Any) -> dict[str, float]:
        """
        Get action probabilities from policy network.

        Args:
            state: Current state

        Returns:
            Action probabilities
        """
        # Compute logits
        state_feature = float(hash(str(state)) % 1000) / 1000.0
        logits = {
            action: self.policy_weights[action] * state_feature for action in self.policy_weights
        }

        # Softmax to get probabilities
        max_logit = max(logits.values())
        exp_logits = {a: np.exp(logit_val - max_logit) for a, logit_val in logits.items()}
        total = sum(exp_logits.values())
        return {a: e / total for a, e in exp_logits.items()}

    def _get_value(self, state: Any) -> float:
        """
        Get state value from critic network.

        Args:
            state: State to evaluate

        Returns:
            State value
        """
        if state not in self.value_weights:
            self.value_weights[state] = 0.0

        return self.value_weights[state]

    def select_action(self, state: Any) -> Any:
        """
        Sample action from policy.

        Args:
            state: Current state

        Returns:
            Sampled action
        """
        probs = self._get_action_probs(state)
        actions = list(probs.keys())
        probabilities = list(probs.values())

        return np.random.choice(actions, p=probabilities)

    def update(self, state: Any, action: Any, reward: float, next_state: Any, done: bool):
        """
        Store transition in trajectory buffer.

        PPO updates happen on complete trajectories, not single transitions.

        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Episode termination flag
        """
        # Store transition
        self.trajectory.append(
            {
                "state": state,
                "action": action,
                "reward": reward,
                "next_state": next_state,
                "done": done,
                "value": self._get_value(state),
                "action_prob": self._get_action_probs(state)[action],
            }
        )

        # Update when episode ends
        if done:
            self._update_policy()
            self.trajectory.clear()

    def _compute_advantages(self) -> list[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages: list[Any] = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"] if i + 1 < len(self.trajectory) else 0.0
                )
                delta = (
                    transition["reward"] + self.discount_factor * next_value - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def _update_policy(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages, strict=False)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(
                self.trajectory, advantages, returns, strict=False
            ):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[transition["action"]]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += self.learning_rate * gradient

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def get_policy(self) -> dict[Any, Any]:
        """
        Get current policy.

        Returns:
            Policy representation
        """
        return {
            "type": "PPO",
            "policy_weights": dict(self.policy_weights),
            "value_weights": dict(self.value_weights),
        }
