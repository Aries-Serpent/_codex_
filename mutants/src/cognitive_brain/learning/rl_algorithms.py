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
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


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

    def xǁReplayBufferǁ__init____mutmut_orig(self, capacity: int = 10000):
        """
        Initialize replay buffer.

        Args:
            capacity: Maximum number of experiences to store
        """
        self.buffer = deque(maxlen=capacity)
        self.capacity = capacity

    def xǁReplayBufferǁ__init____mutmut_1(self, capacity: int = 10001):
        """
        Initialize replay buffer.

        Args:
            capacity: Maximum number of experiences to store
        """
        self.buffer = deque(maxlen=capacity)
        self.capacity = capacity

    def xǁReplayBufferǁ__init____mutmut_2(self, capacity: int = 10000):
        """
        Initialize replay buffer.

        Args:
            capacity: Maximum number of experiences to store
        """
        self.buffer = None
        self.capacity = capacity

    def xǁReplayBufferǁ__init____mutmut_3(self, capacity: int = 10000):
        """
        Initialize replay buffer.

        Args:
            capacity: Maximum number of experiences to store
        """
        self.buffer = deque(maxlen=None)
        self.capacity = capacity

    def xǁReplayBufferǁ__init____mutmut_4(self, capacity: int = 10000):
        """
        Initialize replay buffer.

        Args:
            capacity: Maximum number of experiences to store
        """
        self.buffer = deque(maxlen=capacity)
        self.capacity = None
    
    xǁReplayBufferǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁReplayBufferǁ__init____mutmut_1': xǁReplayBufferǁ__init____mutmut_1, 
        'xǁReplayBufferǁ__init____mutmut_2': xǁReplayBufferǁ__init____mutmut_2, 
        'xǁReplayBufferǁ__init____mutmut_3': xǁReplayBufferǁ__init____mutmut_3, 
        'xǁReplayBufferǁ__init____mutmut_4': xǁReplayBufferǁ__init____mutmut_4
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁReplayBufferǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁReplayBufferǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁReplayBufferǁ__init____mutmut_orig)
    xǁReplayBufferǁ__init____mutmut_orig.__name__ = 'xǁReplayBufferǁ__init__'

    def xǁReplayBufferǁadd__mutmut_orig(self, state: Any, action: Any, reward: float, next_state: Any, done: bool):
        """Add experience to buffer."""
        experience = Experience(state, action, reward, next_state, done)
        self.buffer.append(experience)

    def xǁReplayBufferǁadd__mutmut_1(self, state: Any, action: Any, reward: float, next_state: Any, done: bool):
        """Add experience to buffer."""
        experience = None
        self.buffer.append(experience)

    def xǁReplayBufferǁadd__mutmut_2(self, state: Any, action: Any, reward: float, next_state: Any, done: bool):
        """Add experience to buffer."""
        experience = Experience(None, action, reward, next_state, done)
        self.buffer.append(experience)

    def xǁReplayBufferǁadd__mutmut_3(self, state: Any, action: Any, reward: float, next_state: Any, done: bool):
        """Add experience to buffer."""
        experience = Experience(state, None, reward, next_state, done)
        self.buffer.append(experience)

    def xǁReplayBufferǁadd__mutmut_4(self, state: Any, action: Any, reward: float, next_state: Any, done: bool):
        """Add experience to buffer."""
        experience = Experience(state, action, None, next_state, done)
        self.buffer.append(experience)

    def xǁReplayBufferǁadd__mutmut_5(self, state: Any, action: Any, reward: float, next_state: Any, done: bool):
        """Add experience to buffer."""
        experience = Experience(state, action, reward, None, done)
        self.buffer.append(experience)

    def xǁReplayBufferǁadd__mutmut_6(self, state: Any, action: Any, reward: float, next_state: Any, done: bool):
        """Add experience to buffer."""
        experience = Experience(state, action, reward, next_state, None)
        self.buffer.append(experience)

    def xǁReplayBufferǁadd__mutmut_7(self, state: Any, action: Any, reward: float, next_state: Any, done: bool):
        """Add experience to buffer."""
        experience = Experience(action, reward, next_state, done)
        self.buffer.append(experience)

    def xǁReplayBufferǁadd__mutmut_8(self, state: Any, action: Any, reward: float, next_state: Any, done: bool):
        """Add experience to buffer."""
        experience = Experience(state, reward, next_state, done)
        self.buffer.append(experience)

    def xǁReplayBufferǁadd__mutmut_9(self, state: Any, action: Any, reward: float, next_state: Any, done: bool):
        """Add experience to buffer."""
        experience = Experience(state, action, next_state, done)
        self.buffer.append(experience)

    def xǁReplayBufferǁadd__mutmut_10(self, state: Any, action: Any, reward: float, next_state: Any, done: bool):
        """Add experience to buffer."""
        experience = Experience(state, action, reward, done)
        self.buffer.append(experience)

    def xǁReplayBufferǁadd__mutmut_11(self, state: Any, action: Any, reward: float, next_state: Any, done: bool):
        """Add experience to buffer."""
        experience = Experience(state, action, reward, next_state, )
        self.buffer.append(experience)

    def xǁReplayBufferǁadd__mutmut_12(self, state: Any, action: Any, reward: float, next_state: Any, done: bool):
        """Add experience to buffer."""
        experience = Experience(state, action, reward, next_state, done)
        self.buffer.append(None)
    
    xǁReplayBufferǁadd__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁReplayBufferǁadd__mutmut_1': xǁReplayBufferǁadd__mutmut_1, 
        'xǁReplayBufferǁadd__mutmut_2': xǁReplayBufferǁadd__mutmut_2, 
        'xǁReplayBufferǁadd__mutmut_3': xǁReplayBufferǁadd__mutmut_3, 
        'xǁReplayBufferǁadd__mutmut_4': xǁReplayBufferǁadd__mutmut_4, 
        'xǁReplayBufferǁadd__mutmut_5': xǁReplayBufferǁadd__mutmut_5, 
        'xǁReplayBufferǁadd__mutmut_6': xǁReplayBufferǁadd__mutmut_6, 
        'xǁReplayBufferǁadd__mutmut_7': xǁReplayBufferǁadd__mutmut_7, 
        'xǁReplayBufferǁadd__mutmut_8': xǁReplayBufferǁadd__mutmut_8, 
        'xǁReplayBufferǁadd__mutmut_9': xǁReplayBufferǁadd__mutmut_9, 
        'xǁReplayBufferǁadd__mutmut_10': xǁReplayBufferǁadd__mutmut_10, 
        'xǁReplayBufferǁadd__mutmut_11': xǁReplayBufferǁadd__mutmut_11, 
        'xǁReplayBufferǁadd__mutmut_12': xǁReplayBufferǁadd__mutmut_12
    }
    
    def add(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁReplayBufferǁadd__mutmut_orig"), object.__getattribute__(self, "xǁReplayBufferǁadd__mutmut_mutants"), args, kwargs, self)
        return result 
    
    add.__signature__ = _mutmut_signature(xǁReplayBufferǁadd__mutmut_orig)
    xǁReplayBufferǁadd__mutmut_orig.__name__ = 'xǁReplayBufferǁadd'

    def xǁReplayBufferǁsample__mutmut_orig(self, batch_size: int) -> List[Experience]:
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

    def xǁReplayBufferǁsample__mutmut_1(self, batch_size: int) -> List[Experience]:
        """
        Sample random batch of experiences.

        Args:
            batch_size: Number of experiences to sample

        Returns:
            List of sampled experiences
        """
        if len(self.buffer) <= batch_size:
            return list(self.buffer)

        indices = np.random.choice(len(self.buffer), batch_size, replace=False)
        return [self.buffer[i] for i in indices]

    def xǁReplayBufferǁsample__mutmut_2(self, batch_size: int) -> List[Experience]:
        """
        Sample random batch of experiences.

        Args:
            batch_size: Number of experiences to sample

        Returns:
            List of sampled experiences
        """
        if len(self.buffer) < batch_size:
            return list(None)

        indices = np.random.choice(len(self.buffer), batch_size, replace=False)
        return [self.buffer[i] for i in indices]

    def xǁReplayBufferǁsample__mutmut_3(self, batch_size: int) -> List[Experience]:
        """
        Sample random batch of experiences.

        Args:
            batch_size: Number of experiences to sample

        Returns:
            List of sampled experiences
        """
        if len(self.buffer) < batch_size:
            return list(self.buffer)

        indices = None
        return [self.buffer[i] for i in indices]

    def xǁReplayBufferǁsample__mutmut_4(self, batch_size: int) -> List[Experience]:
        """
        Sample random batch of experiences.

        Args:
            batch_size: Number of experiences to sample

        Returns:
            List of sampled experiences
        """
        if len(self.buffer) < batch_size:
            return list(self.buffer)

        indices = np.random.choice(None, batch_size, replace=False)
        return [self.buffer[i] for i in indices]

    def xǁReplayBufferǁsample__mutmut_5(self, batch_size: int) -> List[Experience]:
        """
        Sample random batch of experiences.

        Args:
            batch_size: Number of experiences to sample

        Returns:
            List of sampled experiences
        """
        if len(self.buffer) < batch_size:
            return list(self.buffer)

        indices = np.random.choice(len(self.buffer), None, replace=False)
        return [self.buffer[i] for i in indices]

    def xǁReplayBufferǁsample__mutmut_6(self, batch_size: int) -> List[Experience]:
        """
        Sample random batch of experiences.

        Args:
            batch_size: Number of experiences to sample

        Returns:
            List of sampled experiences
        """
        if len(self.buffer) < batch_size:
            return list(self.buffer)

        indices = np.random.choice(len(self.buffer), batch_size, replace=None)
        return [self.buffer[i] for i in indices]

    def xǁReplayBufferǁsample__mutmut_7(self, batch_size: int) -> List[Experience]:
        """
        Sample random batch of experiences.

        Args:
            batch_size: Number of experiences to sample

        Returns:
            List of sampled experiences
        """
        if len(self.buffer) < batch_size:
            return list(self.buffer)

        indices = np.random.choice(batch_size, replace=False)
        return [self.buffer[i] for i in indices]

    def xǁReplayBufferǁsample__mutmut_8(self, batch_size: int) -> List[Experience]:
        """
        Sample random batch of experiences.

        Args:
            batch_size: Number of experiences to sample

        Returns:
            List of sampled experiences
        """
        if len(self.buffer) < batch_size:
            return list(self.buffer)

        indices = np.random.choice(len(self.buffer), replace=False)
        return [self.buffer[i] for i in indices]

    def xǁReplayBufferǁsample__mutmut_9(self, batch_size: int) -> List[Experience]:
        """
        Sample random batch of experiences.

        Args:
            batch_size: Number of experiences to sample

        Returns:
            List of sampled experiences
        """
        if len(self.buffer) < batch_size:
            return list(self.buffer)

        indices = np.random.choice(len(self.buffer), batch_size, )
        return [self.buffer[i] for i in indices]

    def xǁReplayBufferǁsample__mutmut_10(self, batch_size: int) -> List[Experience]:
        """
        Sample random batch of experiences.

        Args:
            batch_size: Number of experiences to sample

        Returns:
            List of sampled experiences
        """
        if len(self.buffer) < batch_size:
            return list(self.buffer)

        indices = np.random.choice(len(self.buffer), batch_size, replace=True)
        return [self.buffer[i] for i in indices]
    
    xǁReplayBufferǁsample__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁReplayBufferǁsample__mutmut_1': xǁReplayBufferǁsample__mutmut_1, 
        'xǁReplayBufferǁsample__mutmut_2': xǁReplayBufferǁsample__mutmut_2, 
        'xǁReplayBufferǁsample__mutmut_3': xǁReplayBufferǁsample__mutmut_3, 
        'xǁReplayBufferǁsample__mutmut_4': xǁReplayBufferǁsample__mutmut_4, 
        'xǁReplayBufferǁsample__mutmut_5': xǁReplayBufferǁsample__mutmut_5, 
        'xǁReplayBufferǁsample__mutmut_6': xǁReplayBufferǁsample__mutmut_6, 
        'xǁReplayBufferǁsample__mutmut_7': xǁReplayBufferǁsample__mutmut_7, 
        'xǁReplayBufferǁsample__mutmut_8': xǁReplayBufferǁsample__mutmut_8, 
        'xǁReplayBufferǁsample__mutmut_9': xǁReplayBufferǁsample__mutmut_9, 
        'xǁReplayBufferǁsample__mutmut_10': xǁReplayBufferǁsample__mutmut_10
    }
    
    def sample(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁReplayBufferǁsample__mutmut_orig"), object.__getattribute__(self, "xǁReplayBufferǁsample__mutmut_mutants"), args, kwargs, self)
        return result 
    
    sample.__signature__ = _mutmut_signature(xǁReplayBufferǁsample__mutmut_orig)
    xǁReplayBufferǁsample__mutmut_orig.__name__ = 'xǁReplayBufferǁsample'

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

    def xǁRLAlgorithmǁ__init____mutmut_orig(self, learning_rate: float = 0.1, discount_factor: float = 0.99):
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
        self.episode_rewards: List[float] = []

    def xǁRLAlgorithmǁ__init____mutmut_1(self, learning_rate: float = 1.1, discount_factor: float = 0.99):
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
        self.episode_rewards: List[float] = []

    def xǁRLAlgorithmǁ__init____mutmut_2(self, learning_rate: float = 0.1, discount_factor: float = 1.99):
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
        self.episode_rewards: List[float] = []

    def xǁRLAlgorithmǁ__init____mutmut_3(self, learning_rate: float = 0.1, discount_factor: float = 0.99):
        """
        Initialize RL algorithm.

        Args:
            learning_rate: Learning rate (α)
            discount_factor: Discount factor (γ)
        """
        self.learning_rate = None
        self.discount_factor = discount_factor
        self.episode_count = 0
        self.total_reward = 0.0
        self.episode_rewards: List[float] = []

    def xǁRLAlgorithmǁ__init____mutmut_4(self, learning_rate: float = 0.1, discount_factor: float = 0.99):
        """
        Initialize RL algorithm.

        Args:
            learning_rate: Learning rate (α)
            discount_factor: Discount factor (γ)
        """
        self.learning_rate = learning_rate
        self.discount_factor = None
        self.episode_count = 0
        self.total_reward = 0.0
        self.episode_rewards: List[float] = []

    def xǁRLAlgorithmǁ__init____mutmut_5(self, learning_rate: float = 0.1, discount_factor: float = 0.99):
        """
        Initialize RL algorithm.

        Args:
            learning_rate: Learning rate (α)
            discount_factor: Discount factor (γ)
        """
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.episode_count = None
        self.total_reward = 0.0
        self.episode_rewards: List[float] = []

    def xǁRLAlgorithmǁ__init____mutmut_6(self, learning_rate: float = 0.1, discount_factor: float = 0.99):
        """
        Initialize RL algorithm.

        Args:
            learning_rate: Learning rate (α)
            discount_factor: Discount factor (γ)
        """
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.episode_count = 1
        self.total_reward = 0.0
        self.episode_rewards: List[float] = []

    def xǁRLAlgorithmǁ__init____mutmut_7(self, learning_rate: float = 0.1, discount_factor: float = 0.99):
        """
        Initialize RL algorithm.

        Args:
            learning_rate: Learning rate (α)
            discount_factor: Discount factor (γ)
        """
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.episode_count = 0
        self.total_reward = None
        self.episode_rewards: List[float] = []

    def xǁRLAlgorithmǁ__init____mutmut_8(self, learning_rate: float = 0.1, discount_factor: float = 0.99):
        """
        Initialize RL algorithm.

        Args:
            learning_rate: Learning rate (α)
            discount_factor: Discount factor (γ)
        """
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.episode_count = 0
        self.total_reward = 1.0
        self.episode_rewards: List[float] = []

    def xǁRLAlgorithmǁ__init____mutmut_9(self, learning_rate: float = 0.1, discount_factor: float = 0.99):
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
        self.episode_rewards: List[float] = None
    
    xǁRLAlgorithmǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRLAlgorithmǁ__init____mutmut_1': xǁRLAlgorithmǁ__init____mutmut_1, 
        'xǁRLAlgorithmǁ__init____mutmut_2': xǁRLAlgorithmǁ__init____mutmut_2, 
        'xǁRLAlgorithmǁ__init____mutmut_3': xǁRLAlgorithmǁ__init____mutmut_3, 
        'xǁRLAlgorithmǁ__init____mutmut_4': xǁRLAlgorithmǁ__init____mutmut_4, 
        'xǁRLAlgorithmǁ__init____mutmut_5': xǁRLAlgorithmǁ__init____mutmut_5, 
        'xǁRLAlgorithmǁ__init____mutmut_6': xǁRLAlgorithmǁ__init____mutmut_6, 
        'xǁRLAlgorithmǁ__init____mutmut_7': xǁRLAlgorithmǁ__init____mutmut_7, 
        'xǁRLAlgorithmǁ__init____mutmut_8': xǁRLAlgorithmǁ__init____mutmut_8, 
        'xǁRLAlgorithmǁ__init____mutmut_9': xǁRLAlgorithmǁ__init____mutmut_9
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRLAlgorithmǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁRLAlgorithmǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁRLAlgorithmǁ__init____mutmut_orig)
    xǁRLAlgorithmǁ__init____mutmut_orig.__name__ = 'xǁRLAlgorithmǁ__init__'

    @abstractmethod
    def select_action(self, state: Any) -> Any:
        """
        Select action given current state.

        Args:
            state: Current state

        Returns:
            Selected action
        """
        pass

    @abstractmethod
    def update(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
        """
        Update algorithm with experience.

        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Episode termination flag
        """
        pass

    @abstractmethod
    def get_policy(self) -> Dict[Any, Any]:
        """
        Get current policy.

        Returns:
            Current policy representation
        """
        pass

    def xǁRLAlgorithmǁtrack_episode__mutmut_orig(self, reward: float):
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

    def xǁRLAlgorithmǁtrack_episode__mutmut_1(self, reward: float):
        """
        Track episode statistics.

        Args:
            reward: Total episode reward
        """
        self.episode_count = 1
        self.total_reward += reward
        self.episode_rewards.append(reward)

        if len(self.episode_rewards) > 100:
            self.episode_rewards.pop(0)

    def xǁRLAlgorithmǁtrack_episode__mutmut_2(self, reward: float):
        """
        Track episode statistics.

        Args:
            reward: Total episode reward
        """
        self.episode_count -= 1
        self.total_reward += reward
        self.episode_rewards.append(reward)

        if len(self.episode_rewards) > 100:
            self.episode_rewards.pop(0)

    def xǁRLAlgorithmǁtrack_episode__mutmut_3(self, reward: float):
        """
        Track episode statistics.

        Args:
            reward: Total episode reward
        """
        self.episode_count += 2
        self.total_reward += reward
        self.episode_rewards.append(reward)

        if len(self.episode_rewards) > 100:
            self.episode_rewards.pop(0)

    def xǁRLAlgorithmǁtrack_episode__mutmut_4(self, reward: float):
        """
        Track episode statistics.

        Args:
            reward: Total episode reward
        """
        self.episode_count += 1
        self.total_reward = reward
        self.episode_rewards.append(reward)

        if len(self.episode_rewards) > 100:
            self.episode_rewards.pop(0)

    def xǁRLAlgorithmǁtrack_episode__mutmut_5(self, reward: float):
        """
        Track episode statistics.

        Args:
            reward: Total episode reward
        """
        self.episode_count += 1
        self.total_reward -= reward
        self.episode_rewards.append(reward)

        if len(self.episode_rewards) > 100:
            self.episode_rewards.pop(0)

    def xǁRLAlgorithmǁtrack_episode__mutmut_6(self, reward: float):
        """
        Track episode statistics.

        Args:
            reward: Total episode reward
        """
        self.episode_count += 1
        self.total_reward += reward
        self.episode_rewards.append(None)

        if len(self.episode_rewards) > 100:
            self.episode_rewards.pop(0)

    def xǁRLAlgorithmǁtrack_episode__mutmut_7(self, reward: float):
        """
        Track episode statistics.

        Args:
            reward: Total episode reward
        """
        self.episode_count += 1
        self.total_reward += reward
        self.episode_rewards.append(reward)

        if len(self.episode_rewards) >= 100:
            self.episode_rewards.pop(0)

    def xǁRLAlgorithmǁtrack_episode__mutmut_8(self, reward: float):
        """
        Track episode statistics.

        Args:
            reward: Total episode reward
        """
        self.episode_count += 1
        self.total_reward += reward
        self.episode_rewards.append(reward)

        if len(self.episode_rewards) > 101:
            self.episode_rewards.pop(0)

    def xǁRLAlgorithmǁtrack_episode__mutmut_9(self, reward: float):
        """
        Track episode statistics.

        Args:
            reward: Total episode reward
        """
        self.episode_count += 1
        self.total_reward += reward
        self.episode_rewards.append(reward)

        if len(self.episode_rewards) > 100:
            self.episode_rewards.pop(None)

    def xǁRLAlgorithmǁtrack_episode__mutmut_10(self, reward: float):
        """
        Track episode statistics.

        Args:
            reward: Total episode reward
        """
        self.episode_count += 1
        self.total_reward += reward
        self.episode_rewards.append(reward)

        if len(self.episode_rewards) > 100:
            self.episode_rewards.pop(1)
    
    xǁRLAlgorithmǁtrack_episode__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRLAlgorithmǁtrack_episode__mutmut_1': xǁRLAlgorithmǁtrack_episode__mutmut_1, 
        'xǁRLAlgorithmǁtrack_episode__mutmut_2': xǁRLAlgorithmǁtrack_episode__mutmut_2, 
        'xǁRLAlgorithmǁtrack_episode__mutmut_3': xǁRLAlgorithmǁtrack_episode__mutmut_3, 
        'xǁRLAlgorithmǁtrack_episode__mutmut_4': xǁRLAlgorithmǁtrack_episode__mutmut_4, 
        'xǁRLAlgorithmǁtrack_episode__mutmut_5': xǁRLAlgorithmǁtrack_episode__mutmut_5, 
        'xǁRLAlgorithmǁtrack_episode__mutmut_6': xǁRLAlgorithmǁtrack_episode__mutmut_6, 
        'xǁRLAlgorithmǁtrack_episode__mutmut_7': xǁRLAlgorithmǁtrack_episode__mutmut_7, 
        'xǁRLAlgorithmǁtrack_episode__mutmut_8': xǁRLAlgorithmǁtrack_episode__mutmut_8, 
        'xǁRLAlgorithmǁtrack_episode__mutmut_9': xǁRLAlgorithmǁtrack_episode__mutmut_9, 
        'xǁRLAlgorithmǁtrack_episode__mutmut_10': xǁRLAlgorithmǁtrack_episode__mutmut_10
    }
    
    def track_episode(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRLAlgorithmǁtrack_episode__mutmut_orig"), object.__getattribute__(self, "xǁRLAlgorithmǁtrack_episode__mutmut_mutants"), args, kwargs, self)
        return result 
    
    track_episode.__signature__ = _mutmut_signature(xǁRLAlgorithmǁtrack_episode__mutmut_orig)
    xǁRLAlgorithmǁtrack_episode__mutmut_orig.__name__ = 'xǁRLAlgorithmǁtrack_episode'

    def xǁRLAlgorithmǁget_avg_reward__mutmut_orig(self, window: int = 100) -> float:
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

    def xǁRLAlgorithmǁget_avg_reward__mutmut_1(self, window: int = 101) -> float:
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

    def xǁRLAlgorithmǁget_avg_reward__mutmut_2(self, window: int = 100) -> float:
        """
        Get average reward over recent episodes.

        Args:
            window: Number of recent episodes

        Returns:
            Average reward
        """
        if self.episode_rewards:
            return 0.0

        recent = self.episode_rewards[-window:]
        return float(np.mean(recent))

    def xǁRLAlgorithmǁget_avg_reward__mutmut_3(self, window: int = 100) -> float:
        """
        Get average reward over recent episodes.

        Args:
            window: Number of recent episodes

        Returns:
            Average reward
        """
        if not self.episode_rewards:
            return 1.0

        recent = self.episode_rewards[-window:]
        return float(np.mean(recent))

    def xǁRLAlgorithmǁget_avg_reward__mutmut_4(self, window: int = 100) -> float:
        """
        Get average reward over recent episodes.

        Args:
            window: Number of recent episodes

        Returns:
            Average reward
        """
        if not self.episode_rewards:
            return 0.0

        recent = None
        return float(np.mean(recent))

    def xǁRLAlgorithmǁget_avg_reward__mutmut_5(self, window: int = 100) -> float:
        """
        Get average reward over recent episodes.

        Args:
            window: Number of recent episodes

        Returns:
            Average reward
        """
        if not self.episode_rewards:
            return 0.0

        recent = self.episode_rewards[+window:]
        return float(np.mean(recent))

    def xǁRLAlgorithmǁget_avg_reward__mutmut_6(self, window: int = 100) -> float:
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
        return float(None)

    def xǁRLAlgorithmǁget_avg_reward__mutmut_7(self, window: int = 100) -> float:
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
        return float(np.mean(None))
    
    xǁRLAlgorithmǁget_avg_reward__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRLAlgorithmǁget_avg_reward__mutmut_1': xǁRLAlgorithmǁget_avg_reward__mutmut_1, 
        'xǁRLAlgorithmǁget_avg_reward__mutmut_2': xǁRLAlgorithmǁget_avg_reward__mutmut_2, 
        'xǁRLAlgorithmǁget_avg_reward__mutmut_3': xǁRLAlgorithmǁget_avg_reward__mutmut_3, 
        'xǁRLAlgorithmǁget_avg_reward__mutmut_4': xǁRLAlgorithmǁget_avg_reward__mutmut_4, 
        'xǁRLAlgorithmǁget_avg_reward__mutmut_5': xǁRLAlgorithmǁget_avg_reward__mutmut_5, 
        'xǁRLAlgorithmǁget_avg_reward__mutmut_6': xǁRLAlgorithmǁget_avg_reward__mutmut_6, 
        'xǁRLAlgorithmǁget_avg_reward__mutmut_7': xǁRLAlgorithmǁget_avg_reward__mutmut_7
    }
    
    def get_avg_reward(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRLAlgorithmǁget_avg_reward__mutmut_orig"), object.__getattribute__(self, "xǁRLAlgorithmǁget_avg_reward__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_avg_reward.__signature__ = _mutmut_signature(xǁRLAlgorithmǁget_avg_reward__mutmut_orig)
    xǁRLAlgorithmǁget_avg_reward__mutmut_orig.__name__ = 'xǁRLAlgorithmǁget_avg_reward'


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

    def xǁQLearningǁ__init____mutmut_orig(
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
        self.q_table: Dict[Tuple[Any, Any], float] = {}
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.state_visits: Dict[Any, int] = {}
        self.update_count = 0

    def xǁQLearningǁ__init____mutmut_1(
        self,
        learning_rate: float = 1.1,
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
        self.q_table: Dict[Tuple[Any, Any], float] = {}
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.state_visits: Dict[Any, int] = {}
        self.update_count = 0

    def xǁQLearningǁ__init____mutmut_2(
        self,
        learning_rate: float = 0.1,
        discount_factor: float = 1.99,
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
        self.q_table: Dict[Tuple[Any, Any], float] = {}
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.state_visits: Dict[Any, int] = {}
        self.update_count = 0

    def xǁQLearningǁ__init____mutmut_3(
        self,
        learning_rate: float = 0.1,
        discount_factor: float = 0.99,
        epsilon: float = 1.1,
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
        self.q_table: Dict[Tuple[Any, Any], float] = {}
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.state_visits: Dict[Any, int] = {}
        self.update_count = 0

    def xǁQLearningǁ__init____mutmut_4(
        self,
        learning_rate: float = 0.1,
        discount_factor: float = 0.99,
        epsilon: float = 0.1,
        epsilon_decay: float = 1.995,
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
        self.q_table: Dict[Tuple[Any, Any], float] = {}
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.state_visits: Dict[Any, int] = {}
        self.update_count = 0

    def xǁQLearningǁ__init____mutmut_5(
        self,
        learning_rate: float = 0.1,
        discount_factor: float = 0.99,
        epsilon: float = 0.1,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 1.01,
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
        self.q_table: Dict[Tuple[Any, Any], float] = {}
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.state_visits: Dict[Any, int] = {}
        self.update_count = 0

    def xǁQLearningǁ__init____mutmut_6(
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
        super().__init__(None, discount_factor)
        self.q_table: Dict[Tuple[Any, Any], float] = {}
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.state_visits: Dict[Any, int] = {}
        self.update_count = 0

    def xǁQLearningǁ__init____mutmut_7(
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
        super().__init__(learning_rate, None)
        self.q_table: Dict[Tuple[Any, Any], float] = {}
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.state_visits: Dict[Any, int] = {}
        self.update_count = 0

    def xǁQLearningǁ__init____mutmut_8(
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
        super().__init__(discount_factor)
        self.q_table: Dict[Tuple[Any, Any], float] = {}
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.state_visits: Dict[Any, int] = {}
        self.update_count = 0

    def xǁQLearningǁ__init____mutmut_9(
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
        super().__init__(learning_rate, )
        self.q_table: Dict[Tuple[Any, Any], float] = {}
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.state_visits: Dict[Any, int] = {}
        self.update_count = 0

    def xǁQLearningǁ__init____mutmut_10(
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
        self.q_table: Dict[Tuple[Any, Any], float] = None
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.state_visits: Dict[Any, int] = {}
        self.update_count = 0

    def xǁQLearningǁ__init____mutmut_11(
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
        self.q_table: Dict[Tuple[Any, Any], float] = {}
        self.epsilon = None
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.state_visits: Dict[Any, int] = {}
        self.update_count = 0

    def xǁQLearningǁ__init____mutmut_12(
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
        self.q_table: Dict[Tuple[Any, Any], float] = {}
        self.epsilon = epsilon
        self.epsilon_decay = None
        self.epsilon_min = epsilon_min
        self.state_visits: Dict[Any, int] = {}
        self.update_count = 0

    def xǁQLearningǁ__init____mutmut_13(
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
        self.q_table: Dict[Tuple[Any, Any], float] = {}
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = None
        self.state_visits: Dict[Any, int] = {}
        self.update_count = 0

    def xǁQLearningǁ__init____mutmut_14(
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
        self.q_table: Dict[Tuple[Any, Any], float] = {}
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.state_visits: Dict[Any, int] = None
        self.update_count = 0

    def xǁQLearningǁ__init____mutmut_15(
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
        self.q_table: Dict[Tuple[Any, Any], float] = {}
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.state_visits: Dict[Any, int] = {}
        self.update_count = None

    def xǁQLearningǁ__init____mutmut_16(
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
        self.q_table: Dict[Tuple[Any, Any], float] = {}
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.state_visits: Dict[Any, int] = {}
        self.update_count = 1
    
    xǁQLearningǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁQLearningǁ__init____mutmut_1': xǁQLearningǁ__init____mutmut_1, 
        'xǁQLearningǁ__init____mutmut_2': xǁQLearningǁ__init____mutmut_2, 
        'xǁQLearningǁ__init____mutmut_3': xǁQLearningǁ__init____mutmut_3, 
        'xǁQLearningǁ__init____mutmut_4': xǁQLearningǁ__init____mutmut_4, 
        'xǁQLearningǁ__init____mutmut_5': xǁQLearningǁ__init____mutmut_5, 
        'xǁQLearningǁ__init____mutmut_6': xǁQLearningǁ__init____mutmut_6, 
        'xǁQLearningǁ__init____mutmut_7': xǁQLearningǁ__init____mutmut_7, 
        'xǁQLearningǁ__init____mutmut_8': xǁQLearningǁ__init____mutmut_8, 
        'xǁQLearningǁ__init____mutmut_9': xǁQLearningǁ__init____mutmut_9, 
        'xǁQLearningǁ__init____mutmut_10': xǁQLearningǁ__init____mutmut_10, 
        'xǁQLearningǁ__init____mutmut_11': xǁQLearningǁ__init____mutmut_11, 
        'xǁQLearningǁ__init____mutmut_12': xǁQLearningǁ__init____mutmut_12, 
        'xǁQLearningǁ__init____mutmut_13': xǁQLearningǁ__init____mutmut_13, 
        'xǁQLearningǁ__init____mutmut_14': xǁQLearningǁ__init____mutmut_14, 
        'xǁQLearningǁ__init____mutmut_15': xǁQLearningǁ__init____mutmut_15, 
        'xǁQLearningǁ__init____mutmut_16': xǁQLearningǁ__init____mutmut_16
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁQLearningǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁQLearningǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁQLearningǁ__init____mutmut_orig)
    xǁQLearningǁ__init____mutmut_orig.__name__ = 'xǁQLearningǁ__init__'

    def xǁQLearningǁ_get_q_value__mutmut_orig(self, state: Any, action: Any) -> float:
        """Get Q-value for state-action pair."""
        return self.q_table.get((state, action), 0.0)

    def xǁQLearningǁ_get_q_value__mutmut_1(self, state: Any, action: Any) -> float:
        """Get Q-value for state-action pair."""
        return self.q_table.get(None, 0.0)

    def xǁQLearningǁ_get_q_value__mutmut_2(self, state: Any, action: Any) -> float:
        """Get Q-value for state-action pair."""
        return self.q_table.get((state, action), None)

    def xǁQLearningǁ_get_q_value__mutmut_3(self, state: Any, action: Any) -> float:
        """Get Q-value for state-action pair."""
        return self.q_table.get(0.0)

    def xǁQLearningǁ_get_q_value__mutmut_4(self, state: Any, action: Any) -> float:
        """Get Q-value for state-action pair."""
        return self.q_table.get((state, action), )

    def xǁQLearningǁ_get_q_value__mutmut_5(self, state: Any, action: Any) -> float:
        """Get Q-value for state-action pair."""
        return self.q_table.get((state, action), 1.0)
    
    xǁQLearningǁ_get_q_value__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁQLearningǁ_get_q_value__mutmut_1': xǁQLearningǁ_get_q_value__mutmut_1, 
        'xǁQLearningǁ_get_q_value__mutmut_2': xǁQLearningǁ_get_q_value__mutmut_2, 
        'xǁQLearningǁ_get_q_value__mutmut_3': xǁQLearningǁ_get_q_value__mutmut_3, 
        'xǁQLearningǁ_get_q_value__mutmut_4': xǁQLearningǁ_get_q_value__mutmut_4, 
        'xǁQLearningǁ_get_q_value__mutmut_5': xǁQLearningǁ_get_q_value__mutmut_5
    }
    
    def _get_q_value(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁQLearningǁ_get_q_value__mutmut_orig"), object.__getattribute__(self, "xǁQLearningǁ_get_q_value__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _get_q_value.__signature__ = _mutmut_signature(xǁQLearningǁ_get_q_value__mutmut_orig)
    xǁQLearningǁ_get_q_value__mutmut_orig.__name__ = 'xǁQLearningǁ_get_q_value'

    def xǁQLearningǁ_set_q_value__mutmut_orig(self, state: Any, action: Any, value: float):
        """Set Q-value for state-action pair."""
        self.q_table[(state, action)] = value

    def xǁQLearningǁ_set_q_value__mutmut_1(self, state: Any, action: Any, value: float):
        """Set Q-value for state-action pair."""
        self.q_table[(state, action)] = None
    
    xǁQLearningǁ_set_q_value__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁQLearningǁ_set_q_value__mutmut_1': xǁQLearningǁ_set_q_value__mutmut_1
    }
    
    def _set_q_value(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁQLearningǁ_set_q_value__mutmut_orig"), object.__getattribute__(self, "xǁQLearningǁ_set_q_value__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _set_q_value.__signature__ = _mutmut_signature(xǁQLearningǁ_set_q_value__mutmut_orig)
    xǁQLearningǁ_set_q_value__mutmut_orig.__name__ = 'xǁQLearningǁ_set_q_value'

    def xǁQLearningǁselect_action__mutmut_orig(
        self, state: Any, available_actions: Optional[List[Any]] = None
    ) -> Any:
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
            available_actions = [a for (s, a) in self.q_table.keys() if s == state]
            if not available_actions:
                # Explore if no actions known
                return np.random.choice(["action_0", "action_1", "action_2"])

        # ε-greedy selection
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(available_actions)
        else:
            # Exploit: best known action
            q_values = [self._get_q_value(state, a) for a in available_actions]
            max_q = max(q_values)
            # Handle ties randomly
            best_actions = [
                a for a, q in zip(available_actions, q_values) if q == max_q
            ]
            return np.random.choice(best_actions)

    def xǁQLearningǁselect_action__mutmut_1(
        self, state: Any, available_actions: Optional[List[Any]] = None
    ) -> Any:
        """
        Select action using ε-greedy policy.

        Args:
            state: Current state
            available_actions: List of available actions

        Returns:
            Selected action
        """
        if available_actions is not None:
            # Get all actions seen from this state
            available_actions = [a for (s, a) in self.q_table.keys() if s == state]
            if not available_actions:
                # Explore if no actions known
                return np.random.choice(["action_0", "action_1", "action_2"])

        # ε-greedy selection
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(available_actions)
        else:
            # Exploit: best known action
            q_values = [self._get_q_value(state, a) for a in available_actions]
            max_q = max(q_values)
            # Handle ties randomly
            best_actions = [
                a for a, q in zip(available_actions, q_values) if q == max_q
            ]
            return np.random.choice(best_actions)

    def xǁQLearningǁselect_action__mutmut_2(
        self, state: Any, available_actions: Optional[List[Any]] = None
    ) -> Any:
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
            available_actions = None
            if not available_actions:
                # Explore if no actions known
                return np.random.choice(["action_0", "action_1", "action_2"])

        # ε-greedy selection
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(available_actions)
        else:
            # Exploit: best known action
            q_values = [self._get_q_value(state, a) for a in available_actions]
            max_q = max(q_values)
            # Handle ties randomly
            best_actions = [
                a for a, q in zip(available_actions, q_values) if q == max_q
            ]
            return np.random.choice(best_actions)

    def xǁQLearningǁselect_action__mutmut_3(
        self, state: Any, available_actions: Optional[List[Any]] = None
    ) -> Any:
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
            available_actions = [a for (s, a) in self.q_table.keys() if s != state]
            if not available_actions:
                # Explore if no actions known
                return np.random.choice(["action_0", "action_1", "action_2"])

        # ε-greedy selection
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(available_actions)
        else:
            # Exploit: best known action
            q_values = [self._get_q_value(state, a) for a in available_actions]
            max_q = max(q_values)
            # Handle ties randomly
            best_actions = [
                a for a, q in zip(available_actions, q_values) if q == max_q
            ]
            return np.random.choice(best_actions)

    def xǁQLearningǁselect_action__mutmut_4(
        self, state: Any, available_actions: Optional[List[Any]] = None
    ) -> Any:
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
            available_actions = [a for (s, a) in self.q_table.keys() if s == state]
            if available_actions:
                # Explore if no actions known
                return np.random.choice(["action_0", "action_1", "action_2"])

        # ε-greedy selection
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(available_actions)
        else:
            # Exploit: best known action
            q_values = [self._get_q_value(state, a) for a in available_actions]
            max_q = max(q_values)
            # Handle ties randomly
            best_actions = [
                a for a, q in zip(available_actions, q_values) if q == max_q
            ]
            return np.random.choice(best_actions)

    def xǁQLearningǁselect_action__mutmut_5(
        self, state: Any, available_actions: Optional[List[Any]] = None
    ) -> Any:
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
            available_actions = [a for (s, a) in self.q_table.keys() if s == state]
            if not available_actions:
                # Explore if no actions known
                return np.random.choice(None)

        # ε-greedy selection
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(available_actions)
        else:
            # Exploit: best known action
            q_values = [self._get_q_value(state, a) for a in available_actions]
            max_q = max(q_values)
            # Handle ties randomly
            best_actions = [
                a for a, q in zip(available_actions, q_values) if q == max_q
            ]
            return np.random.choice(best_actions)

    def xǁQLearningǁselect_action__mutmut_6(
        self, state: Any, available_actions: Optional[List[Any]] = None
    ) -> Any:
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
            available_actions = [a for (s, a) in self.q_table.keys() if s == state]
            if not available_actions:
                # Explore if no actions known
                return np.random.choice(["XXaction_0XX", "action_1", "action_2"])

        # ε-greedy selection
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(available_actions)
        else:
            # Exploit: best known action
            q_values = [self._get_q_value(state, a) for a in available_actions]
            max_q = max(q_values)
            # Handle ties randomly
            best_actions = [
                a for a, q in zip(available_actions, q_values) if q == max_q
            ]
            return np.random.choice(best_actions)

    def xǁQLearningǁselect_action__mutmut_7(
        self, state: Any, available_actions: Optional[List[Any]] = None
    ) -> Any:
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
            available_actions = [a for (s, a) in self.q_table.keys() if s == state]
            if not available_actions:
                # Explore if no actions known
                return np.random.choice(["ACTION_0", "action_1", "action_2"])

        # ε-greedy selection
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(available_actions)
        else:
            # Exploit: best known action
            q_values = [self._get_q_value(state, a) for a in available_actions]
            max_q = max(q_values)
            # Handle ties randomly
            best_actions = [
                a for a, q in zip(available_actions, q_values) if q == max_q
            ]
            return np.random.choice(best_actions)

    def xǁQLearningǁselect_action__mutmut_8(
        self, state: Any, available_actions: Optional[List[Any]] = None
    ) -> Any:
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
            available_actions = [a for (s, a) in self.q_table.keys() if s == state]
            if not available_actions:
                # Explore if no actions known
                return np.random.choice(["action_0", "XXaction_1XX", "action_2"])

        # ε-greedy selection
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(available_actions)
        else:
            # Exploit: best known action
            q_values = [self._get_q_value(state, a) for a in available_actions]
            max_q = max(q_values)
            # Handle ties randomly
            best_actions = [
                a for a, q in zip(available_actions, q_values) if q == max_q
            ]
            return np.random.choice(best_actions)

    def xǁQLearningǁselect_action__mutmut_9(
        self, state: Any, available_actions: Optional[List[Any]] = None
    ) -> Any:
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
            available_actions = [a for (s, a) in self.q_table.keys() if s == state]
            if not available_actions:
                # Explore if no actions known
                return np.random.choice(["action_0", "ACTION_1", "action_2"])

        # ε-greedy selection
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(available_actions)
        else:
            # Exploit: best known action
            q_values = [self._get_q_value(state, a) for a in available_actions]
            max_q = max(q_values)
            # Handle ties randomly
            best_actions = [
                a for a, q in zip(available_actions, q_values) if q == max_q
            ]
            return np.random.choice(best_actions)

    def xǁQLearningǁselect_action__mutmut_10(
        self, state: Any, available_actions: Optional[List[Any]] = None
    ) -> Any:
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
            available_actions = [a for (s, a) in self.q_table.keys() if s == state]
            if not available_actions:
                # Explore if no actions known
                return np.random.choice(["action_0", "action_1", "XXaction_2XX"])

        # ε-greedy selection
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(available_actions)
        else:
            # Exploit: best known action
            q_values = [self._get_q_value(state, a) for a in available_actions]
            max_q = max(q_values)
            # Handle ties randomly
            best_actions = [
                a for a, q in zip(available_actions, q_values) if q == max_q
            ]
            return np.random.choice(best_actions)

    def xǁQLearningǁselect_action__mutmut_11(
        self, state: Any, available_actions: Optional[List[Any]] = None
    ) -> Any:
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
            available_actions = [a for (s, a) in self.q_table.keys() if s == state]
            if not available_actions:
                # Explore if no actions known
                return np.random.choice(["action_0", "action_1", "ACTION_2"])

        # ε-greedy selection
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(available_actions)
        else:
            # Exploit: best known action
            q_values = [self._get_q_value(state, a) for a in available_actions]
            max_q = max(q_values)
            # Handle ties randomly
            best_actions = [
                a for a, q in zip(available_actions, q_values) if q == max_q
            ]
            return np.random.choice(best_actions)

    def xǁQLearningǁselect_action__mutmut_12(
        self, state: Any, available_actions: Optional[List[Any]] = None
    ) -> Any:
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
            available_actions = [a for (s, a) in self.q_table.keys() if s == state]
            if not available_actions:
                # Explore if no actions known
                return np.random.choice(["action_0", "action_1", "action_2"])

        # ε-greedy selection
        if np.random.random() <= self.epsilon:
            # Explore: random action
            return np.random.choice(available_actions)
        else:
            # Exploit: best known action
            q_values = [self._get_q_value(state, a) for a in available_actions]
            max_q = max(q_values)
            # Handle ties randomly
            best_actions = [
                a for a, q in zip(available_actions, q_values) if q == max_q
            ]
            return np.random.choice(best_actions)

    def xǁQLearningǁselect_action__mutmut_13(
        self, state: Any, available_actions: Optional[List[Any]] = None
    ) -> Any:
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
            available_actions = [a for (s, a) in self.q_table.keys() if s == state]
            if not available_actions:
                # Explore if no actions known
                return np.random.choice(["action_0", "action_1", "action_2"])

        # ε-greedy selection
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(None)
        else:
            # Exploit: best known action
            q_values = [self._get_q_value(state, a) for a in available_actions]
            max_q = max(q_values)
            # Handle ties randomly
            best_actions = [
                a for a, q in zip(available_actions, q_values) if q == max_q
            ]
            return np.random.choice(best_actions)

    def xǁQLearningǁselect_action__mutmut_14(
        self, state: Any, available_actions: Optional[List[Any]] = None
    ) -> Any:
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
            available_actions = [a for (s, a) in self.q_table.keys() if s == state]
            if not available_actions:
                # Explore if no actions known
                return np.random.choice(["action_0", "action_1", "action_2"])

        # ε-greedy selection
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(available_actions)
        else:
            # Exploit: best known action
            q_values = None
            max_q = max(q_values)
            # Handle ties randomly
            best_actions = [
                a for a, q in zip(available_actions, q_values) if q == max_q
            ]
            return np.random.choice(best_actions)

    def xǁQLearningǁselect_action__mutmut_15(
        self, state: Any, available_actions: Optional[List[Any]] = None
    ) -> Any:
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
            available_actions = [a for (s, a) in self.q_table.keys() if s == state]
            if not available_actions:
                # Explore if no actions known
                return np.random.choice(["action_0", "action_1", "action_2"])

        # ε-greedy selection
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(available_actions)
        else:
            # Exploit: best known action
            q_values = [self._get_q_value(None, a) for a in available_actions]
            max_q = max(q_values)
            # Handle ties randomly
            best_actions = [
                a for a, q in zip(available_actions, q_values) if q == max_q
            ]
            return np.random.choice(best_actions)

    def xǁQLearningǁselect_action__mutmut_16(
        self, state: Any, available_actions: Optional[List[Any]] = None
    ) -> Any:
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
            available_actions = [a for (s, a) in self.q_table.keys() if s == state]
            if not available_actions:
                # Explore if no actions known
                return np.random.choice(["action_0", "action_1", "action_2"])

        # ε-greedy selection
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(available_actions)
        else:
            # Exploit: best known action
            q_values = [self._get_q_value(state, None) for a in available_actions]
            max_q = max(q_values)
            # Handle ties randomly
            best_actions = [
                a for a, q in zip(available_actions, q_values) if q == max_q
            ]
            return np.random.choice(best_actions)

    def xǁQLearningǁselect_action__mutmut_17(
        self, state: Any, available_actions: Optional[List[Any]] = None
    ) -> Any:
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
            available_actions = [a for (s, a) in self.q_table.keys() if s == state]
            if not available_actions:
                # Explore if no actions known
                return np.random.choice(["action_0", "action_1", "action_2"])

        # ε-greedy selection
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(available_actions)
        else:
            # Exploit: best known action
            q_values = [self._get_q_value(a) for a in available_actions]
            max_q = max(q_values)
            # Handle ties randomly
            best_actions = [
                a for a, q in zip(available_actions, q_values) if q == max_q
            ]
            return np.random.choice(best_actions)

    def xǁQLearningǁselect_action__mutmut_18(
        self, state: Any, available_actions: Optional[List[Any]] = None
    ) -> Any:
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
            available_actions = [a for (s, a) in self.q_table.keys() if s == state]
            if not available_actions:
                # Explore if no actions known
                return np.random.choice(["action_0", "action_1", "action_2"])

        # ε-greedy selection
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(available_actions)
        else:
            # Exploit: best known action
            q_values = [self._get_q_value(state, ) for a in available_actions]
            max_q = max(q_values)
            # Handle ties randomly
            best_actions = [
                a for a, q in zip(available_actions, q_values) if q == max_q
            ]
            return np.random.choice(best_actions)

    def xǁQLearningǁselect_action__mutmut_19(
        self, state: Any, available_actions: Optional[List[Any]] = None
    ) -> Any:
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
            available_actions = [a for (s, a) in self.q_table.keys() if s == state]
            if not available_actions:
                # Explore if no actions known
                return np.random.choice(["action_0", "action_1", "action_2"])

        # ε-greedy selection
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(available_actions)
        else:
            # Exploit: best known action
            q_values = [self._get_q_value(state, a) for a in available_actions]
            max_q = None
            # Handle ties randomly
            best_actions = [
                a for a, q in zip(available_actions, q_values) if q == max_q
            ]
            return np.random.choice(best_actions)

    def xǁQLearningǁselect_action__mutmut_20(
        self, state: Any, available_actions: Optional[List[Any]] = None
    ) -> Any:
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
            available_actions = [a for (s, a) in self.q_table.keys() if s == state]
            if not available_actions:
                # Explore if no actions known
                return np.random.choice(["action_0", "action_1", "action_2"])

        # ε-greedy selection
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(available_actions)
        else:
            # Exploit: best known action
            q_values = [self._get_q_value(state, a) for a in available_actions]
            max_q = max(None)
            # Handle ties randomly
            best_actions = [
                a for a, q in zip(available_actions, q_values) if q == max_q
            ]
            return np.random.choice(best_actions)

    def xǁQLearningǁselect_action__mutmut_21(
        self, state: Any, available_actions: Optional[List[Any]] = None
    ) -> Any:
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
            available_actions = [a for (s, a) in self.q_table.keys() if s == state]
            if not available_actions:
                # Explore if no actions known
                return np.random.choice(["action_0", "action_1", "action_2"])

        # ε-greedy selection
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(available_actions)
        else:
            # Exploit: best known action
            q_values = [self._get_q_value(state, a) for a in available_actions]
            max_q = max(q_values)
            # Handle ties randomly
            best_actions = None
            return np.random.choice(best_actions)

    def xǁQLearningǁselect_action__mutmut_22(
        self, state: Any, available_actions: Optional[List[Any]] = None
    ) -> Any:
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
            available_actions = [a for (s, a) in self.q_table.keys() if s == state]
            if not available_actions:
                # Explore if no actions known
                return np.random.choice(["action_0", "action_1", "action_2"])

        # ε-greedy selection
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(available_actions)
        else:
            # Exploit: best known action
            q_values = [self._get_q_value(state, a) for a in available_actions]
            max_q = max(q_values)
            # Handle ties randomly
            best_actions = [
                a for a, q in zip(None, q_values) if q == max_q
            ]
            return np.random.choice(best_actions)

    def xǁQLearningǁselect_action__mutmut_23(
        self, state: Any, available_actions: Optional[List[Any]] = None
    ) -> Any:
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
            available_actions = [a for (s, a) in self.q_table.keys() if s == state]
            if not available_actions:
                # Explore if no actions known
                return np.random.choice(["action_0", "action_1", "action_2"])

        # ε-greedy selection
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(available_actions)
        else:
            # Exploit: best known action
            q_values = [self._get_q_value(state, a) for a in available_actions]
            max_q = max(q_values)
            # Handle ties randomly
            best_actions = [
                a for a, q in zip(available_actions, None) if q == max_q
            ]
            return np.random.choice(best_actions)

    def xǁQLearningǁselect_action__mutmut_24(
        self, state: Any, available_actions: Optional[List[Any]] = None
    ) -> Any:
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
            available_actions = [a for (s, a) in self.q_table.keys() if s == state]
            if not available_actions:
                # Explore if no actions known
                return np.random.choice(["action_0", "action_1", "action_2"])

        # ε-greedy selection
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(available_actions)
        else:
            # Exploit: best known action
            q_values = [self._get_q_value(state, a) for a in available_actions]
            max_q = max(q_values)
            # Handle ties randomly
            best_actions = [
                a for a, q in zip(q_values) if q == max_q
            ]
            return np.random.choice(best_actions)

    def xǁQLearningǁselect_action__mutmut_25(
        self, state: Any, available_actions: Optional[List[Any]] = None
    ) -> Any:
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
            available_actions = [a for (s, a) in self.q_table.keys() if s == state]
            if not available_actions:
                # Explore if no actions known
                return np.random.choice(["action_0", "action_1", "action_2"])

        # ε-greedy selection
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(available_actions)
        else:
            # Exploit: best known action
            q_values = [self._get_q_value(state, a) for a in available_actions]
            max_q = max(q_values)
            # Handle ties randomly
            best_actions = [
                a for a, q in zip(available_actions, ) if q == max_q
            ]
            return np.random.choice(best_actions)

    def xǁQLearningǁselect_action__mutmut_26(
        self, state: Any, available_actions: Optional[List[Any]] = None
    ) -> Any:
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
            available_actions = [a for (s, a) in self.q_table.keys() if s == state]
            if not available_actions:
                # Explore if no actions known
                return np.random.choice(["action_0", "action_1", "action_2"])

        # ε-greedy selection
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(available_actions)
        else:
            # Exploit: best known action
            q_values = [self._get_q_value(state, a) for a in available_actions]
            max_q = max(q_values)
            # Handle ties randomly
            best_actions = [
                a for a, q in zip(available_actions, q_values) if q != max_q
            ]
            return np.random.choice(best_actions)

    def xǁQLearningǁselect_action__mutmut_27(
        self, state: Any, available_actions: Optional[List[Any]] = None
    ) -> Any:
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
            available_actions = [a for (s, a) in self.q_table.keys() if s == state]
            if not available_actions:
                # Explore if no actions known
                return np.random.choice(["action_0", "action_1", "action_2"])

        # ε-greedy selection
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(available_actions)
        else:
            # Exploit: best known action
            q_values = [self._get_q_value(state, a) for a in available_actions]
            max_q = max(q_values)
            # Handle ties randomly
            best_actions = [
                a for a, q in zip(available_actions, q_values) if q == max_q
            ]
            return np.random.choice(None)
    
    xǁQLearningǁselect_action__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁQLearningǁselect_action__mutmut_1': xǁQLearningǁselect_action__mutmut_1, 
        'xǁQLearningǁselect_action__mutmut_2': xǁQLearningǁselect_action__mutmut_2, 
        'xǁQLearningǁselect_action__mutmut_3': xǁQLearningǁselect_action__mutmut_3, 
        'xǁQLearningǁselect_action__mutmut_4': xǁQLearningǁselect_action__mutmut_4, 
        'xǁQLearningǁselect_action__mutmut_5': xǁQLearningǁselect_action__mutmut_5, 
        'xǁQLearningǁselect_action__mutmut_6': xǁQLearningǁselect_action__mutmut_6, 
        'xǁQLearningǁselect_action__mutmut_7': xǁQLearningǁselect_action__mutmut_7, 
        'xǁQLearningǁselect_action__mutmut_8': xǁQLearningǁselect_action__mutmut_8, 
        'xǁQLearningǁselect_action__mutmut_9': xǁQLearningǁselect_action__mutmut_9, 
        'xǁQLearningǁselect_action__mutmut_10': xǁQLearningǁselect_action__mutmut_10, 
        'xǁQLearningǁselect_action__mutmut_11': xǁQLearningǁselect_action__mutmut_11, 
        'xǁQLearningǁselect_action__mutmut_12': xǁQLearningǁselect_action__mutmut_12, 
        'xǁQLearningǁselect_action__mutmut_13': xǁQLearningǁselect_action__mutmut_13, 
        'xǁQLearningǁselect_action__mutmut_14': xǁQLearningǁselect_action__mutmut_14, 
        'xǁQLearningǁselect_action__mutmut_15': xǁQLearningǁselect_action__mutmut_15, 
        'xǁQLearningǁselect_action__mutmut_16': xǁQLearningǁselect_action__mutmut_16, 
        'xǁQLearningǁselect_action__mutmut_17': xǁQLearningǁselect_action__mutmut_17, 
        'xǁQLearningǁselect_action__mutmut_18': xǁQLearningǁselect_action__mutmut_18, 
        'xǁQLearningǁselect_action__mutmut_19': xǁQLearningǁselect_action__mutmut_19, 
        'xǁQLearningǁselect_action__mutmut_20': xǁQLearningǁselect_action__mutmut_20, 
        'xǁQLearningǁselect_action__mutmut_21': xǁQLearningǁselect_action__mutmut_21, 
        'xǁQLearningǁselect_action__mutmut_22': xǁQLearningǁselect_action__mutmut_22, 
        'xǁQLearningǁselect_action__mutmut_23': xǁQLearningǁselect_action__mutmut_23, 
        'xǁQLearningǁselect_action__mutmut_24': xǁQLearningǁselect_action__mutmut_24, 
        'xǁQLearningǁselect_action__mutmut_25': xǁQLearningǁselect_action__mutmut_25, 
        'xǁQLearningǁselect_action__mutmut_26': xǁQLearningǁselect_action__mutmut_26, 
        'xǁQLearningǁselect_action__mutmut_27': xǁQLearningǁselect_action__mutmut_27
    }
    
    def select_action(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁQLearningǁselect_action__mutmut_orig"), object.__getattribute__(self, "xǁQLearningǁselect_action__mutmut_mutants"), args, kwargs, self)
        return result 
    
    select_action.__signature__ = _mutmut_signature(xǁQLearningǁselect_action__mutmut_orig)
    xǁQLearningǁselect_action__mutmut_orig.__name__ = 'xǁQLearningǁselect_action'

    def xǁQLearningǁupdate__mutmut_orig(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
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

    def xǁQLearningǁupdate__mutmut_1(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
        current_q = None

        if done:
            # Terminal state: no future reward
            target_q = reward
        else:
            # Get max Q-value for next state
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
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

    def xǁQLearningǁupdate__mutmut_2(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
        current_q = self._get_q_value(None, action)

        if done:
            # Terminal state: no future reward
            target_q = reward
        else:
            # Get max Q-value for next state
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
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

    def xǁQLearningǁupdate__mutmut_3(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
        current_q = self._get_q_value(state, None)

        if done:
            # Terminal state: no future reward
            target_q = reward
        else:
            # Get max Q-value for next state
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
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

    def xǁQLearningǁupdate__mutmut_4(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
        current_q = self._get_q_value(action)

        if done:
            # Terminal state: no future reward
            target_q = reward
        else:
            # Get max Q-value for next state
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
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

    def xǁQLearningǁupdate__mutmut_5(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
        current_q = self._get_q_value(state, )

        if done:
            # Terminal state: no future reward
            target_q = reward
        else:
            # Get max Q-value for next state
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
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

    def xǁQLearningǁupdate__mutmut_6(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            target_q = None
        else:
            # Get max Q-value for next state
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
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

    def xǁQLearningǁupdate__mutmut_7(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = None
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

    def xǁQLearningǁupdate__mutmut_8(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s != next_state]
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

    def xǁQLearningǁupdate__mutmut_9(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
            if next_actions:
                next_q_values = None
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

    def xǁQLearningǁupdate__mutmut_10(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
            if next_actions:
                next_q_values = [self._get_q_value(None, a) for a in next_actions]
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

    def xǁQLearningǁupdate__mutmut_11(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
            if next_actions:
                next_q_values = [self._get_q_value(next_state, None) for a in next_actions]
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

    def xǁQLearningǁupdate__mutmut_12(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
            if next_actions:
                next_q_values = [self._get_q_value(a) for a in next_actions]
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

    def xǁQLearningǁupdate__mutmut_13(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
            if next_actions:
                next_q_values = [self._get_q_value(next_state, ) for a in next_actions]
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

    def xǁQLearningǁupdate__mutmut_14(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
            if next_actions:
                next_q_values = [self._get_q_value(next_state, a) for a in next_actions]
                max_next_q = None
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

    def xǁQLearningǁupdate__mutmut_15(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
            if next_actions:
                next_q_values = [self._get_q_value(next_state, a) for a in next_actions]
                max_next_q = max(None)
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

    def xǁQLearningǁupdate__mutmut_16(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
            if next_actions:
                next_q_values = [self._get_q_value(next_state, a) for a in next_actions]
                max_next_q = max(next_q_values)
            else:
                max_next_q = None

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

    def xǁQLearningǁupdate__mutmut_17(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
            if next_actions:
                next_q_values = [self._get_q_value(next_state, a) for a in next_actions]
                max_next_q = max(next_q_values)
            else:
                max_next_q = 1.0

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

    def xǁQLearningǁupdate__mutmut_18(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
            if next_actions:
                next_q_values = [self._get_q_value(next_state, a) for a in next_actions]
                max_next_q = max(next_q_values)
            else:
                max_next_q = 0.0

            target_q = None

        # Q-learning update
        new_q = current_q + self.learning_rate * (target_q - current_q)
        self._set_q_value(state, action, new_q)

        # Track statistics
        self.update_count += 1
        self.state_visits[state] = self.state_visits.get(state, 0) + 1

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁQLearningǁupdate__mutmut_19(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
            if next_actions:
                next_q_values = [self._get_q_value(next_state, a) for a in next_actions]
                max_next_q = max(next_q_values)
            else:
                max_next_q = 0.0

            target_q = reward - self.discount_factor * max_next_q

        # Q-learning update
        new_q = current_q + self.learning_rate * (target_q - current_q)
        self._set_q_value(state, action, new_q)

        # Track statistics
        self.update_count += 1
        self.state_visits[state] = self.state_visits.get(state, 0) + 1

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁQLearningǁupdate__mutmut_20(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
            if next_actions:
                next_q_values = [self._get_q_value(next_state, a) for a in next_actions]
                max_next_q = max(next_q_values)
            else:
                max_next_q = 0.0

            target_q = reward + self.discount_factor / max_next_q

        # Q-learning update
        new_q = current_q + self.learning_rate * (target_q - current_q)
        self._set_q_value(state, action, new_q)

        # Track statistics
        self.update_count += 1
        self.state_visits[state] = self.state_visits.get(state, 0) + 1

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁQLearningǁupdate__mutmut_21(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
            if next_actions:
                next_q_values = [self._get_q_value(next_state, a) for a in next_actions]
                max_next_q = max(next_q_values)
            else:
                max_next_q = 0.0

            target_q = reward + self.discount_factor * max_next_q

        # Q-learning update
        new_q = None
        self._set_q_value(state, action, new_q)

        # Track statistics
        self.update_count += 1
        self.state_visits[state] = self.state_visits.get(state, 0) + 1

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁQLearningǁupdate__mutmut_22(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
            if next_actions:
                next_q_values = [self._get_q_value(next_state, a) for a in next_actions]
                max_next_q = max(next_q_values)
            else:
                max_next_q = 0.0

            target_q = reward + self.discount_factor * max_next_q

        # Q-learning update
        new_q = current_q - self.learning_rate * (target_q - current_q)
        self._set_q_value(state, action, new_q)

        # Track statistics
        self.update_count += 1
        self.state_visits[state] = self.state_visits.get(state, 0) + 1

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁQLearningǁupdate__mutmut_23(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
            if next_actions:
                next_q_values = [self._get_q_value(next_state, a) for a in next_actions]
                max_next_q = max(next_q_values)
            else:
                max_next_q = 0.0

            target_q = reward + self.discount_factor * max_next_q

        # Q-learning update
        new_q = current_q + self.learning_rate / (target_q - current_q)
        self._set_q_value(state, action, new_q)

        # Track statistics
        self.update_count += 1
        self.state_visits[state] = self.state_visits.get(state, 0) + 1

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁQLearningǁupdate__mutmut_24(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
            if next_actions:
                next_q_values = [self._get_q_value(next_state, a) for a in next_actions]
                max_next_q = max(next_q_values)
            else:
                max_next_q = 0.0

            target_q = reward + self.discount_factor * max_next_q

        # Q-learning update
        new_q = current_q + self.learning_rate * (target_q + current_q)
        self._set_q_value(state, action, new_q)

        # Track statistics
        self.update_count += 1
        self.state_visits[state] = self.state_visits.get(state, 0) + 1

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁQLearningǁupdate__mutmut_25(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
            if next_actions:
                next_q_values = [self._get_q_value(next_state, a) for a in next_actions]
                max_next_q = max(next_q_values)
            else:
                max_next_q = 0.0

            target_q = reward + self.discount_factor * max_next_q

        # Q-learning update
        new_q = current_q + self.learning_rate * (target_q - current_q)
        self._set_q_value(None, action, new_q)

        # Track statistics
        self.update_count += 1
        self.state_visits[state] = self.state_visits.get(state, 0) + 1

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁQLearningǁupdate__mutmut_26(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
            if next_actions:
                next_q_values = [self._get_q_value(next_state, a) for a in next_actions]
                max_next_q = max(next_q_values)
            else:
                max_next_q = 0.0

            target_q = reward + self.discount_factor * max_next_q

        # Q-learning update
        new_q = current_q + self.learning_rate * (target_q - current_q)
        self._set_q_value(state, None, new_q)

        # Track statistics
        self.update_count += 1
        self.state_visits[state] = self.state_visits.get(state, 0) + 1

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁQLearningǁupdate__mutmut_27(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
            if next_actions:
                next_q_values = [self._get_q_value(next_state, a) for a in next_actions]
                max_next_q = max(next_q_values)
            else:
                max_next_q = 0.0

            target_q = reward + self.discount_factor * max_next_q

        # Q-learning update
        new_q = current_q + self.learning_rate * (target_q - current_q)
        self._set_q_value(state, action, None)

        # Track statistics
        self.update_count += 1
        self.state_visits[state] = self.state_visits.get(state, 0) + 1

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁQLearningǁupdate__mutmut_28(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
            if next_actions:
                next_q_values = [self._get_q_value(next_state, a) for a in next_actions]
                max_next_q = max(next_q_values)
            else:
                max_next_q = 0.0

            target_q = reward + self.discount_factor * max_next_q

        # Q-learning update
        new_q = current_q + self.learning_rate * (target_q - current_q)
        self._set_q_value(action, new_q)

        # Track statistics
        self.update_count += 1
        self.state_visits[state] = self.state_visits.get(state, 0) + 1

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁQLearningǁupdate__mutmut_29(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
            if next_actions:
                next_q_values = [self._get_q_value(next_state, a) for a in next_actions]
                max_next_q = max(next_q_values)
            else:
                max_next_q = 0.0

            target_q = reward + self.discount_factor * max_next_q

        # Q-learning update
        new_q = current_q + self.learning_rate * (target_q - current_q)
        self._set_q_value(state, new_q)

        # Track statistics
        self.update_count += 1
        self.state_visits[state] = self.state_visits.get(state, 0) + 1

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁQLearningǁupdate__mutmut_30(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
            if next_actions:
                next_q_values = [self._get_q_value(next_state, a) for a in next_actions]
                max_next_q = max(next_q_values)
            else:
                max_next_q = 0.0

            target_q = reward + self.discount_factor * max_next_q

        # Q-learning update
        new_q = current_q + self.learning_rate * (target_q - current_q)
        self._set_q_value(state, action, )

        # Track statistics
        self.update_count += 1
        self.state_visits[state] = self.state_visits.get(state, 0) + 1

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁQLearningǁupdate__mutmut_31(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
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
        self.update_count = 1
        self.state_visits[state] = self.state_visits.get(state, 0) + 1

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁQLearningǁupdate__mutmut_32(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
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
        self.update_count -= 1
        self.state_visits[state] = self.state_visits.get(state, 0) + 1

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁQLearningǁupdate__mutmut_33(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
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
        self.update_count += 2
        self.state_visits[state] = self.state_visits.get(state, 0) + 1

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁQLearningǁupdate__mutmut_34(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
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
        self.state_visits[state] = None

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁQLearningǁupdate__mutmut_35(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
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
        self.state_visits[state] = self.state_visits.get(state, 0) - 1

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁQLearningǁupdate__mutmut_36(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
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
        self.state_visits[state] = self.state_visits.get(None, 0) + 1

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁQLearningǁupdate__mutmut_37(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
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
        self.state_visits[state] = self.state_visits.get(state, None) + 1

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁQLearningǁupdate__mutmut_38(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
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
        self.state_visits[state] = self.state_visits.get(0) + 1

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁQLearningǁupdate__mutmut_39(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
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
        self.state_visits[state] = self.state_visits.get(state, ) + 1

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁQLearningǁupdate__mutmut_40(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
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
        self.state_visits[state] = self.state_visits.get(state, 1) + 1

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁQLearningǁupdate__mutmut_41(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
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
        self.state_visits[state] = self.state_visits.get(state, 0) + 2

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁQLearningǁupdate__mutmut_42(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
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
            self.epsilon = None

    def xǁQLearningǁupdate__mutmut_43(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
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
            self.epsilon = max(None, self.epsilon * self.epsilon_decay)

    def xǁQLearningǁupdate__mutmut_44(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
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
            self.epsilon = max(self.epsilon_min, None)

    def xǁQLearningǁupdate__mutmut_45(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
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
            self.epsilon = max(self.epsilon * self.epsilon_decay)

    def xǁQLearningǁupdate__mutmut_46(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
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
            self.epsilon = max(self.epsilon_min, )

    def xǁQLearningǁupdate__mutmut_47(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            next_actions = [a for (s, a) in self.q_table.keys() if s == next_state]
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
            self.epsilon = max(self.epsilon_min, self.epsilon / self.epsilon_decay)
    
    xǁQLearningǁupdate__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁQLearningǁupdate__mutmut_1': xǁQLearningǁupdate__mutmut_1, 
        'xǁQLearningǁupdate__mutmut_2': xǁQLearningǁupdate__mutmut_2, 
        'xǁQLearningǁupdate__mutmut_3': xǁQLearningǁupdate__mutmut_3, 
        'xǁQLearningǁupdate__mutmut_4': xǁQLearningǁupdate__mutmut_4, 
        'xǁQLearningǁupdate__mutmut_5': xǁQLearningǁupdate__mutmut_5, 
        'xǁQLearningǁupdate__mutmut_6': xǁQLearningǁupdate__mutmut_6, 
        'xǁQLearningǁupdate__mutmut_7': xǁQLearningǁupdate__mutmut_7, 
        'xǁQLearningǁupdate__mutmut_8': xǁQLearningǁupdate__mutmut_8, 
        'xǁQLearningǁupdate__mutmut_9': xǁQLearningǁupdate__mutmut_9, 
        'xǁQLearningǁupdate__mutmut_10': xǁQLearningǁupdate__mutmut_10, 
        'xǁQLearningǁupdate__mutmut_11': xǁQLearningǁupdate__mutmut_11, 
        'xǁQLearningǁupdate__mutmut_12': xǁQLearningǁupdate__mutmut_12, 
        'xǁQLearningǁupdate__mutmut_13': xǁQLearningǁupdate__mutmut_13, 
        'xǁQLearningǁupdate__mutmut_14': xǁQLearningǁupdate__mutmut_14, 
        'xǁQLearningǁupdate__mutmut_15': xǁQLearningǁupdate__mutmut_15, 
        'xǁQLearningǁupdate__mutmut_16': xǁQLearningǁupdate__mutmut_16, 
        'xǁQLearningǁupdate__mutmut_17': xǁQLearningǁupdate__mutmut_17, 
        'xǁQLearningǁupdate__mutmut_18': xǁQLearningǁupdate__mutmut_18, 
        'xǁQLearningǁupdate__mutmut_19': xǁQLearningǁupdate__mutmut_19, 
        'xǁQLearningǁupdate__mutmut_20': xǁQLearningǁupdate__mutmut_20, 
        'xǁQLearningǁupdate__mutmut_21': xǁQLearningǁupdate__mutmut_21, 
        'xǁQLearningǁupdate__mutmut_22': xǁQLearningǁupdate__mutmut_22, 
        'xǁQLearningǁupdate__mutmut_23': xǁQLearningǁupdate__mutmut_23, 
        'xǁQLearningǁupdate__mutmut_24': xǁQLearningǁupdate__mutmut_24, 
        'xǁQLearningǁupdate__mutmut_25': xǁQLearningǁupdate__mutmut_25, 
        'xǁQLearningǁupdate__mutmut_26': xǁQLearningǁupdate__mutmut_26, 
        'xǁQLearningǁupdate__mutmut_27': xǁQLearningǁupdate__mutmut_27, 
        'xǁQLearningǁupdate__mutmut_28': xǁQLearningǁupdate__mutmut_28, 
        'xǁQLearningǁupdate__mutmut_29': xǁQLearningǁupdate__mutmut_29, 
        'xǁQLearningǁupdate__mutmut_30': xǁQLearningǁupdate__mutmut_30, 
        'xǁQLearningǁupdate__mutmut_31': xǁQLearningǁupdate__mutmut_31, 
        'xǁQLearningǁupdate__mutmut_32': xǁQLearningǁupdate__mutmut_32, 
        'xǁQLearningǁupdate__mutmut_33': xǁQLearningǁupdate__mutmut_33, 
        'xǁQLearningǁupdate__mutmut_34': xǁQLearningǁupdate__mutmut_34, 
        'xǁQLearningǁupdate__mutmut_35': xǁQLearningǁupdate__mutmut_35, 
        'xǁQLearningǁupdate__mutmut_36': xǁQLearningǁupdate__mutmut_36, 
        'xǁQLearningǁupdate__mutmut_37': xǁQLearningǁupdate__mutmut_37, 
        'xǁQLearningǁupdate__mutmut_38': xǁQLearningǁupdate__mutmut_38, 
        'xǁQLearningǁupdate__mutmut_39': xǁQLearningǁupdate__mutmut_39, 
        'xǁQLearningǁupdate__mutmut_40': xǁQLearningǁupdate__mutmut_40, 
        'xǁQLearningǁupdate__mutmut_41': xǁQLearningǁupdate__mutmut_41, 
        'xǁQLearningǁupdate__mutmut_42': xǁQLearningǁupdate__mutmut_42, 
        'xǁQLearningǁupdate__mutmut_43': xǁQLearningǁupdate__mutmut_43, 
        'xǁQLearningǁupdate__mutmut_44': xǁQLearningǁupdate__mutmut_44, 
        'xǁQLearningǁupdate__mutmut_45': xǁQLearningǁupdate__mutmut_45, 
        'xǁQLearningǁupdate__mutmut_46': xǁQLearningǁupdate__mutmut_46, 
        'xǁQLearningǁupdate__mutmut_47': xǁQLearningǁupdate__mutmut_47
    }
    
    def update(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁQLearningǁupdate__mutmut_orig"), object.__getattribute__(self, "xǁQLearningǁupdate__mutmut_mutants"), args, kwargs, self)
        return result 
    
    update.__signature__ = _mutmut_signature(xǁQLearningǁupdate__mutmut_orig)
    xǁQLearningǁupdate__mutmut_orig.__name__ = 'xǁQLearningǁupdate'

    def xǁQLearningǁget_policy__mutmut_orig(self) -> Dict[Any, Any]:
        """
        Get greedy policy from Q-table.

        Returns:
            Mapping from states to best actions
        """
        policy = {}
        states = set(s for (s, a) in self.q_table.keys())

        for state in states:
            actions = [a for (s, a) in self.q_table.keys() if s == state]
            if actions:
                q_values = [self._get_q_value(state, a) for a in actions]
                best_action = actions[np.argmax(q_values)]
                policy[state] = best_action

        return policy

    def xǁQLearningǁget_policy__mutmut_1(self) -> Dict[Any, Any]:
        """
        Get greedy policy from Q-table.

        Returns:
            Mapping from states to best actions
        """
        policy = None
        states = set(s for (s, a) in self.q_table.keys())

        for state in states:
            actions = [a for (s, a) in self.q_table.keys() if s == state]
            if actions:
                q_values = [self._get_q_value(state, a) for a in actions]
                best_action = actions[np.argmax(q_values)]
                policy[state] = best_action

        return policy

    def xǁQLearningǁget_policy__mutmut_2(self) -> Dict[Any, Any]:
        """
        Get greedy policy from Q-table.

        Returns:
            Mapping from states to best actions
        """
        policy = {}
        states = None

        for state in states:
            actions = [a for (s, a) in self.q_table.keys() if s == state]
            if actions:
                q_values = [self._get_q_value(state, a) for a in actions]
                best_action = actions[np.argmax(q_values)]
                policy[state] = best_action

        return policy

    def xǁQLearningǁget_policy__mutmut_3(self) -> Dict[Any, Any]:
        """
        Get greedy policy from Q-table.

        Returns:
            Mapping from states to best actions
        """
        policy = {}
        states = set(None)

        for state in states:
            actions = [a for (s, a) in self.q_table.keys() if s == state]
            if actions:
                q_values = [self._get_q_value(state, a) for a in actions]
                best_action = actions[np.argmax(q_values)]
                policy[state] = best_action

        return policy

    def xǁQLearningǁget_policy__mutmut_4(self) -> Dict[Any, Any]:
        """
        Get greedy policy from Q-table.

        Returns:
            Mapping from states to best actions
        """
        policy = {}
        states = set(s for (s, a) in self.q_table.keys())

        for state in states:
            actions = None
            if actions:
                q_values = [self._get_q_value(state, a) for a in actions]
                best_action = actions[np.argmax(q_values)]
                policy[state] = best_action

        return policy

    def xǁQLearningǁget_policy__mutmut_5(self) -> Dict[Any, Any]:
        """
        Get greedy policy from Q-table.

        Returns:
            Mapping from states to best actions
        """
        policy = {}
        states = set(s for (s, a) in self.q_table.keys())

        for state in states:
            actions = [a for (s, a) in self.q_table.keys() if s != state]
            if actions:
                q_values = [self._get_q_value(state, a) for a in actions]
                best_action = actions[np.argmax(q_values)]
                policy[state] = best_action

        return policy

    def xǁQLearningǁget_policy__mutmut_6(self) -> Dict[Any, Any]:
        """
        Get greedy policy from Q-table.

        Returns:
            Mapping from states to best actions
        """
        policy = {}
        states = set(s for (s, a) in self.q_table.keys())

        for state in states:
            actions = [a for (s, a) in self.q_table.keys() if s == state]
            if actions:
                q_values = None
                best_action = actions[np.argmax(q_values)]
                policy[state] = best_action

        return policy

    def xǁQLearningǁget_policy__mutmut_7(self) -> Dict[Any, Any]:
        """
        Get greedy policy from Q-table.

        Returns:
            Mapping from states to best actions
        """
        policy = {}
        states = set(s for (s, a) in self.q_table.keys())

        for state in states:
            actions = [a for (s, a) in self.q_table.keys() if s == state]
            if actions:
                q_values = [self._get_q_value(None, a) for a in actions]
                best_action = actions[np.argmax(q_values)]
                policy[state] = best_action

        return policy

    def xǁQLearningǁget_policy__mutmut_8(self) -> Dict[Any, Any]:
        """
        Get greedy policy from Q-table.

        Returns:
            Mapping from states to best actions
        """
        policy = {}
        states = set(s for (s, a) in self.q_table.keys())

        for state in states:
            actions = [a for (s, a) in self.q_table.keys() if s == state]
            if actions:
                q_values = [self._get_q_value(state, None) for a in actions]
                best_action = actions[np.argmax(q_values)]
                policy[state] = best_action

        return policy

    def xǁQLearningǁget_policy__mutmut_9(self) -> Dict[Any, Any]:
        """
        Get greedy policy from Q-table.

        Returns:
            Mapping from states to best actions
        """
        policy = {}
        states = set(s for (s, a) in self.q_table.keys())

        for state in states:
            actions = [a for (s, a) in self.q_table.keys() if s == state]
            if actions:
                q_values = [self._get_q_value(a) for a in actions]
                best_action = actions[np.argmax(q_values)]
                policy[state] = best_action

        return policy

    def xǁQLearningǁget_policy__mutmut_10(self) -> Dict[Any, Any]:
        """
        Get greedy policy from Q-table.

        Returns:
            Mapping from states to best actions
        """
        policy = {}
        states = set(s for (s, a) in self.q_table.keys())

        for state in states:
            actions = [a for (s, a) in self.q_table.keys() if s == state]
            if actions:
                q_values = [self._get_q_value(state, ) for a in actions]
                best_action = actions[np.argmax(q_values)]
                policy[state] = best_action

        return policy

    def xǁQLearningǁget_policy__mutmut_11(self) -> Dict[Any, Any]:
        """
        Get greedy policy from Q-table.

        Returns:
            Mapping from states to best actions
        """
        policy = {}
        states = set(s for (s, a) in self.q_table.keys())

        for state in states:
            actions = [a for (s, a) in self.q_table.keys() if s == state]
            if actions:
                q_values = [self._get_q_value(state, a) for a in actions]
                best_action = None
                policy[state] = best_action

        return policy

    def xǁQLearningǁget_policy__mutmut_12(self) -> Dict[Any, Any]:
        """
        Get greedy policy from Q-table.

        Returns:
            Mapping from states to best actions
        """
        policy = {}
        states = set(s for (s, a) in self.q_table.keys())

        for state in states:
            actions = [a for (s, a) in self.q_table.keys() if s == state]
            if actions:
                q_values = [self._get_q_value(state, a) for a in actions]
                best_action = actions[np.argmax(None)]
                policy[state] = best_action

        return policy

    def xǁQLearningǁget_policy__mutmut_13(self) -> Dict[Any, Any]:
        """
        Get greedy policy from Q-table.

        Returns:
            Mapping from states to best actions
        """
        policy = {}
        states = set(s for (s, a) in self.q_table.keys())

        for state in states:
            actions = [a for (s, a) in self.q_table.keys() if s == state]
            if actions:
                q_values = [self._get_q_value(state, a) for a in actions]
                best_action = actions[np.argmax(q_values)]
                policy[state] = None

        return policy
    
    xǁQLearningǁget_policy__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁQLearningǁget_policy__mutmut_1': xǁQLearningǁget_policy__mutmut_1, 
        'xǁQLearningǁget_policy__mutmut_2': xǁQLearningǁget_policy__mutmut_2, 
        'xǁQLearningǁget_policy__mutmut_3': xǁQLearningǁget_policy__mutmut_3, 
        'xǁQLearningǁget_policy__mutmut_4': xǁQLearningǁget_policy__mutmut_4, 
        'xǁQLearningǁget_policy__mutmut_5': xǁQLearningǁget_policy__mutmut_5, 
        'xǁQLearningǁget_policy__mutmut_6': xǁQLearningǁget_policy__mutmut_6, 
        'xǁQLearningǁget_policy__mutmut_7': xǁQLearningǁget_policy__mutmut_7, 
        'xǁQLearningǁget_policy__mutmut_8': xǁQLearningǁget_policy__mutmut_8, 
        'xǁQLearningǁget_policy__mutmut_9': xǁQLearningǁget_policy__mutmut_9, 
        'xǁQLearningǁget_policy__mutmut_10': xǁQLearningǁget_policy__mutmut_10, 
        'xǁQLearningǁget_policy__mutmut_11': xǁQLearningǁget_policy__mutmut_11, 
        'xǁQLearningǁget_policy__mutmut_12': xǁQLearningǁget_policy__mutmut_12, 
        'xǁQLearningǁget_policy__mutmut_13': xǁQLearningǁget_policy__mutmut_13
    }
    
    def get_policy(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁQLearningǁget_policy__mutmut_orig"), object.__getattribute__(self, "xǁQLearningǁget_policy__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_policy.__signature__ = _mutmut_signature(xǁQLearningǁget_policy__mutmut_orig)
    xǁQLearningǁget_policy__mutmut_orig.__name__ = 'xǁQLearningǁget_policy'

    def xǁQLearningǁget_state_value__mutmut_orig(self, state: Any) -> float:
        """
        Get value of state (max Q-value over actions).

        Args:
            state: State to evaluate

        Returns:
            State value
        """
        actions = [a for (s, a) in self.q_table.keys() if s == state]
        if not actions:
            return 0.0

        q_values = [self._get_q_value(state, a) for a in actions]
        return max(q_values)

    def xǁQLearningǁget_state_value__mutmut_1(self, state: Any) -> float:
        """
        Get value of state (max Q-value over actions).

        Args:
            state: State to evaluate

        Returns:
            State value
        """
        actions = None
        if not actions:
            return 0.0

        q_values = [self._get_q_value(state, a) for a in actions]
        return max(q_values)

    def xǁQLearningǁget_state_value__mutmut_2(self, state: Any) -> float:
        """
        Get value of state (max Q-value over actions).

        Args:
            state: State to evaluate

        Returns:
            State value
        """
        actions = [a for (s, a) in self.q_table.keys() if s != state]
        if not actions:
            return 0.0

        q_values = [self._get_q_value(state, a) for a in actions]
        return max(q_values)

    def xǁQLearningǁget_state_value__mutmut_3(self, state: Any) -> float:
        """
        Get value of state (max Q-value over actions).

        Args:
            state: State to evaluate

        Returns:
            State value
        """
        actions = [a for (s, a) in self.q_table.keys() if s == state]
        if actions:
            return 0.0

        q_values = [self._get_q_value(state, a) for a in actions]
        return max(q_values)

    def xǁQLearningǁget_state_value__mutmut_4(self, state: Any) -> float:
        """
        Get value of state (max Q-value over actions).

        Args:
            state: State to evaluate

        Returns:
            State value
        """
        actions = [a for (s, a) in self.q_table.keys() if s == state]
        if not actions:
            return 1.0

        q_values = [self._get_q_value(state, a) for a in actions]
        return max(q_values)

    def xǁQLearningǁget_state_value__mutmut_5(self, state: Any) -> float:
        """
        Get value of state (max Q-value over actions).

        Args:
            state: State to evaluate

        Returns:
            State value
        """
        actions = [a for (s, a) in self.q_table.keys() if s == state]
        if not actions:
            return 0.0

        q_values = None
        return max(q_values)

    def xǁQLearningǁget_state_value__mutmut_6(self, state: Any) -> float:
        """
        Get value of state (max Q-value over actions).

        Args:
            state: State to evaluate

        Returns:
            State value
        """
        actions = [a for (s, a) in self.q_table.keys() if s == state]
        if not actions:
            return 0.0

        q_values = [self._get_q_value(None, a) for a in actions]
        return max(q_values)

    def xǁQLearningǁget_state_value__mutmut_7(self, state: Any) -> float:
        """
        Get value of state (max Q-value over actions).

        Args:
            state: State to evaluate

        Returns:
            State value
        """
        actions = [a for (s, a) in self.q_table.keys() if s == state]
        if not actions:
            return 0.0

        q_values = [self._get_q_value(state, None) for a in actions]
        return max(q_values)

    def xǁQLearningǁget_state_value__mutmut_8(self, state: Any) -> float:
        """
        Get value of state (max Q-value over actions).

        Args:
            state: State to evaluate

        Returns:
            State value
        """
        actions = [a for (s, a) in self.q_table.keys() if s == state]
        if not actions:
            return 0.0

        q_values = [self._get_q_value(a) for a in actions]
        return max(q_values)

    def xǁQLearningǁget_state_value__mutmut_9(self, state: Any) -> float:
        """
        Get value of state (max Q-value over actions).

        Args:
            state: State to evaluate

        Returns:
            State value
        """
        actions = [a for (s, a) in self.q_table.keys() if s == state]
        if not actions:
            return 0.0

        q_values = [self._get_q_value(state, ) for a in actions]
        return max(q_values)

    def xǁQLearningǁget_state_value__mutmut_10(self, state: Any) -> float:
        """
        Get value of state (max Q-value over actions).

        Args:
            state: State to evaluate

        Returns:
            State value
        """
        actions = [a for (s, a) in self.q_table.keys() if s == state]
        if not actions:
            return 0.0

        q_values = [self._get_q_value(state, a) for a in actions]
        return max(None)
    
    xǁQLearningǁget_state_value__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁQLearningǁget_state_value__mutmut_1': xǁQLearningǁget_state_value__mutmut_1, 
        'xǁQLearningǁget_state_value__mutmut_2': xǁQLearningǁget_state_value__mutmut_2, 
        'xǁQLearningǁget_state_value__mutmut_3': xǁQLearningǁget_state_value__mutmut_3, 
        'xǁQLearningǁget_state_value__mutmut_4': xǁQLearningǁget_state_value__mutmut_4, 
        'xǁQLearningǁget_state_value__mutmut_5': xǁQLearningǁget_state_value__mutmut_5, 
        'xǁQLearningǁget_state_value__mutmut_6': xǁQLearningǁget_state_value__mutmut_6, 
        'xǁQLearningǁget_state_value__mutmut_7': xǁQLearningǁget_state_value__mutmut_7, 
        'xǁQLearningǁget_state_value__mutmut_8': xǁQLearningǁget_state_value__mutmut_8, 
        'xǁQLearningǁget_state_value__mutmut_9': xǁQLearningǁget_state_value__mutmut_9, 
        'xǁQLearningǁget_state_value__mutmut_10': xǁQLearningǁget_state_value__mutmut_10
    }
    
    def get_state_value(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁQLearningǁget_state_value__mutmut_orig"), object.__getattribute__(self, "xǁQLearningǁget_state_value__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_state_value.__signature__ = _mutmut_signature(xǁQLearningǁget_state_value__mutmut_orig)
    xǁQLearningǁget_state_value__mutmut_orig.__name__ = 'xǁQLearningǁget_state_value'


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

    def xǁDQNǁ__init____mutmut_orig(
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
        self.q_weights: Dict[Any, np.ndarray] = {}
        self.target_weights: Dict[Any, np.ndarray] = {}

        # Training statistics
        self.step_count = 0
        self.update_count = 0
        self.loss_history: List[float] = []

    def xǁDQNǁ__init____mutmut_1(
        self,
        learning_rate: float = 1.001,
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
        self.q_weights: Dict[Any, np.ndarray] = {}
        self.target_weights: Dict[Any, np.ndarray] = {}

        # Training statistics
        self.step_count = 0
        self.update_count = 0
        self.loss_history: List[float] = []

    def xǁDQNǁ__init____mutmut_2(
        self,
        learning_rate: float = 0.001,
        discount_factor: float = 1.99,
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
        self.q_weights: Dict[Any, np.ndarray] = {}
        self.target_weights: Dict[Any, np.ndarray] = {}

        # Training statistics
        self.step_count = 0
        self.update_count = 0
        self.loss_history: List[float] = []

    def xǁDQNǁ__init____mutmut_3(
        self,
        learning_rate: float = 0.001,
        discount_factor: float = 0.99,
        epsilon: float = 1.1,
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
        self.q_weights: Dict[Any, np.ndarray] = {}
        self.target_weights: Dict[Any, np.ndarray] = {}

        # Training statistics
        self.step_count = 0
        self.update_count = 0
        self.loss_history: List[float] = []

    def xǁDQNǁ__init____mutmut_4(
        self,
        learning_rate: float = 0.001,
        discount_factor: float = 0.99,
        epsilon: float = 0.1,
        epsilon_decay: float = 1.995,
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
        self.q_weights: Dict[Any, np.ndarray] = {}
        self.target_weights: Dict[Any, np.ndarray] = {}

        # Training statistics
        self.step_count = 0
        self.update_count = 0
        self.loss_history: List[float] = []

    def xǁDQNǁ__init____mutmut_5(
        self,
        learning_rate: float = 0.001,
        discount_factor: float = 0.99,
        epsilon: float = 0.1,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 1.01,
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
        self.q_weights: Dict[Any, np.ndarray] = {}
        self.target_weights: Dict[Any, np.ndarray] = {}

        # Training statistics
        self.step_count = 0
        self.update_count = 0
        self.loss_history: List[float] = []

    def xǁDQNǁ__init____mutmut_6(
        self,
        learning_rate: float = 0.001,
        discount_factor: float = 0.99,
        epsilon: float = 0.1,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01,
        buffer_capacity: int = 10001,
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
        self.q_weights: Dict[Any, np.ndarray] = {}
        self.target_weights: Dict[Any, np.ndarray] = {}

        # Training statistics
        self.step_count = 0
        self.update_count = 0
        self.loss_history: List[float] = []

    def xǁDQNǁ__init____mutmut_7(
        self,
        learning_rate: float = 0.001,
        discount_factor: float = 0.99,
        epsilon: float = 0.1,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01,
        buffer_capacity: int = 10000,
        batch_size: int = 33,
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
        self.q_weights: Dict[Any, np.ndarray] = {}
        self.target_weights: Dict[Any, np.ndarray] = {}

        # Training statistics
        self.step_count = 0
        self.update_count = 0
        self.loss_history: List[float] = []

    def xǁDQNǁ__init____mutmut_8(
        self,
        learning_rate: float = 0.001,
        discount_factor: float = 0.99,
        epsilon: float = 0.1,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01,
        buffer_capacity: int = 10000,
        batch_size: int = 32,
        update_frequency: int = 5,
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
        self.q_weights: Dict[Any, np.ndarray] = {}
        self.target_weights: Dict[Any, np.ndarray] = {}

        # Training statistics
        self.step_count = 0
        self.update_count = 0
        self.loss_history: List[float] = []

    def xǁDQNǁ__init____mutmut_9(
        self,
        learning_rate: float = 0.001,
        discount_factor: float = 0.99,
        epsilon: float = 0.1,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01,
        buffer_capacity: int = 10000,
        batch_size: int = 32,
        update_frequency: int = 4,
        target_update_freq: int = 101,
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
        self.q_weights: Dict[Any, np.ndarray] = {}
        self.target_weights: Dict[Any, np.ndarray] = {}

        # Training statistics
        self.step_count = 0
        self.update_count = 0
        self.loss_history: List[float] = []

    def xǁDQNǁ__init____mutmut_10(
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
        super().__init__(None, discount_factor)
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.batch_size = batch_size
        self.update_frequency = update_frequency
        self.target_update_freq = target_update_freq

        # Replay buffer
        self.replay_buffer = ReplayBuffer(buffer_capacity)

        # Simplified linear Q-network (weights for state features)
        self.q_weights: Dict[Any, np.ndarray] = {}
        self.target_weights: Dict[Any, np.ndarray] = {}

        # Training statistics
        self.step_count = 0
        self.update_count = 0
        self.loss_history: List[float] = []

    def xǁDQNǁ__init____mutmut_11(
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
        super().__init__(learning_rate, None)
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.batch_size = batch_size
        self.update_frequency = update_frequency
        self.target_update_freq = target_update_freq

        # Replay buffer
        self.replay_buffer = ReplayBuffer(buffer_capacity)

        # Simplified linear Q-network (weights for state features)
        self.q_weights: Dict[Any, np.ndarray] = {}
        self.target_weights: Dict[Any, np.ndarray] = {}

        # Training statistics
        self.step_count = 0
        self.update_count = 0
        self.loss_history: List[float] = []

    def xǁDQNǁ__init____mutmut_12(
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
        super().__init__(discount_factor)
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.batch_size = batch_size
        self.update_frequency = update_frequency
        self.target_update_freq = target_update_freq

        # Replay buffer
        self.replay_buffer = ReplayBuffer(buffer_capacity)

        # Simplified linear Q-network (weights for state features)
        self.q_weights: Dict[Any, np.ndarray] = {}
        self.target_weights: Dict[Any, np.ndarray] = {}

        # Training statistics
        self.step_count = 0
        self.update_count = 0
        self.loss_history: List[float] = []

    def xǁDQNǁ__init____mutmut_13(
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
        super().__init__(learning_rate, )
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.batch_size = batch_size
        self.update_frequency = update_frequency
        self.target_update_freq = target_update_freq

        # Replay buffer
        self.replay_buffer = ReplayBuffer(buffer_capacity)

        # Simplified linear Q-network (weights for state features)
        self.q_weights: Dict[Any, np.ndarray] = {}
        self.target_weights: Dict[Any, np.ndarray] = {}

        # Training statistics
        self.step_count = 0
        self.update_count = 0
        self.loss_history: List[float] = []

    def xǁDQNǁ__init____mutmut_14(
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
        self.epsilon = None
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.batch_size = batch_size
        self.update_frequency = update_frequency
        self.target_update_freq = target_update_freq

        # Replay buffer
        self.replay_buffer = ReplayBuffer(buffer_capacity)

        # Simplified linear Q-network (weights for state features)
        self.q_weights: Dict[Any, np.ndarray] = {}
        self.target_weights: Dict[Any, np.ndarray] = {}

        # Training statistics
        self.step_count = 0
        self.update_count = 0
        self.loss_history: List[float] = []

    def xǁDQNǁ__init____mutmut_15(
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
        self.epsilon_decay = None
        self.epsilon_min = epsilon_min
        self.batch_size = batch_size
        self.update_frequency = update_frequency
        self.target_update_freq = target_update_freq

        # Replay buffer
        self.replay_buffer = ReplayBuffer(buffer_capacity)

        # Simplified linear Q-network (weights for state features)
        self.q_weights: Dict[Any, np.ndarray] = {}
        self.target_weights: Dict[Any, np.ndarray] = {}

        # Training statistics
        self.step_count = 0
        self.update_count = 0
        self.loss_history: List[float] = []

    def xǁDQNǁ__init____mutmut_16(
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
        self.epsilon_min = None
        self.batch_size = batch_size
        self.update_frequency = update_frequency
        self.target_update_freq = target_update_freq

        # Replay buffer
        self.replay_buffer = ReplayBuffer(buffer_capacity)

        # Simplified linear Q-network (weights for state features)
        self.q_weights: Dict[Any, np.ndarray] = {}
        self.target_weights: Dict[Any, np.ndarray] = {}

        # Training statistics
        self.step_count = 0
        self.update_count = 0
        self.loss_history: List[float] = []

    def xǁDQNǁ__init____mutmut_17(
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
        self.batch_size = None
        self.update_frequency = update_frequency
        self.target_update_freq = target_update_freq

        # Replay buffer
        self.replay_buffer = ReplayBuffer(buffer_capacity)

        # Simplified linear Q-network (weights for state features)
        self.q_weights: Dict[Any, np.ndarray] = {}
        self.target_weights: Dict[Any, np.ndarray] = {}

        # Training statistics
        self.step_count = 0
        self.update_count = 0
        self.loss_history: List[float] = []

    def xǁDQNǁ__init____mutmut_18(
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
        self.update_frequency = None
        self.target_update_freq = target_update_freq

        # Replay buffer
        self.replay_buffer = ReplayBuffer(buffer_capacity)

        # Simplified linear Q-network (weights for state features)
        self.q_weights: Dict[Any, np.ndarray] = {}
        self.target_weights: Dict[Any, np.ndarray] = {}

        # Training statistics
        self.step_count = 0
        self.update_count = 0
        self.loss_history: List[float] = []

    def xǁDQNǁ__init____mutmut_19(
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
        self.target_update_freq = None

        # Replay buffer
        self.replay_buffer = ReplayBuffer(buffer_capacity)

        # Simplified linear Q-network (weights for state features)
        self.q_weights: Dict[Any, np.ndarray] = {}
        self.target_weights: Dict[Any, np.ndarray] = {}

        # Training statistics
        self.step_count = 0
        self.update_count = 0
        self.loss_history: List[float] = []

    def xǁDQNǁ__init____mutmut_20(
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
        self.replay_buffer = None

        # Simplified linear Q-network (weights for state features)
        self.q_weights: Dict[Any, np.ndarray] = {}
        self.target_weights: Dict[Any, np.ndarray] = {}

        # Training statistics
        self.step_count = 0
        self.update_count = 0
        self.loss_history: List[float] = []

    def xǁDQNǁ__init____mutmut_21(
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
        self.replay_buffer = ReplayBuffer(None)

        # Simplified linear Q-network (weights for state features)
        self.q_weights: Dict[Any, np.ndarray] = {}
        self.target_weights: Dict[Any, np.ndarray] = {}

        # Training statistics
        self.step_count = 0
        self.update_count = 0
        self.loss_history: List[float] = []

    def xǁDQNǁ__init____mutmut_22(
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
        self.q_weights: Dict[Any, np.ndarray] = None
        self.target_weights: Dict[Any, np.ndarray] = {}

        # Training statistics
        self.step_count = 0
        self.update_count = 0
        self.loss_history: List[float] = []

    def xǁDQNǁ__init____mutmut_23(
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
        self.q_weights: Dict[Any, np.ndarray] = {}
        self.target_weights: Dict[Any, np.ndarray] = None

        # Training statistics
        self.step_count = 0
        self.update_count = 0
        self.loss_history: List[float] = []

    def xǁDQNǁ__init____mutmut_24(
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
        self.q_weights: Dict[Any, np.ndarray] = {}
        self.target_weights: Dict[Any, np.ndarray] = {}

        # Training statistics
        self.step_count = None
        self.update_count = 0
        self.loss_history: List[float] = []

    def xǁDQNǁ__init____mutmut_25(
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
        self.q_weights: Dict[Any, np.ndarray] = {}
        self.target_weights: Dict[Any, np.ndarray] = {}

        # Training statistics
        self.step_count = 1
        self.update_count = 0
        self.loss_history: List[float] = []

    def xǁDQNǁ__init____mutmut_26(
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
        self.q_weights: Dict[Any, np.ndarray] = {}
        self.target_weights: Dict[Any, np.ndarray] = {}

        # Training statistics
        self.step_count = 0
        self.update_count = None
        self.loss_history: List[float] = []

    def xǁDQNǁ__init____mutmut_27(
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
        self.q_weights: Dict[Any, np.ndarray] = {}
        self.target_weights: Dict[Any, np.ndarray] = {}

        # Training statistics
        self.step_count = 0
        self.update_count = 1
        self.loss_history: List[float] = []

    def xǁDQNǁ__init____mutmut_28(
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
        self.q_weights: Dict[Any, np.ndarray] = {}
        self.target_weights: Dict[Any, np.ndarray] = {}

        # Training statistics
        self.step_count = 0
        self.update_count = 0
        self.loss_history: List[float] = None
    
    xǁDQNǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDQNǁ__init____mutmut_1': xǁDQNǁ__init____mutmut_1, 
        'xǁDQNǁ__init____mutmut_2': xǁDQNǁ__init____mutmut_2, 
        'xǁDQNǁ__init____mutmut_3': xǁDQNǁ__init____mutmut_3, 
        'xǁDQNǁ__init____mutmut_4': xǁDQNǁ__init____mutmut_4, 
        'xǁDQNǁ__init____mutmut_5': xǁDQNǁ__init____mutmut_5, 
        'xǁDQNǁ__init____mutmut_6': xǁDQNǁ__init____mutmut_6, 
        'xǁDQNǁ__init____mutmut_7': xǁDQNǁ__init____mutmut_7, 
        'xǁDQNǁ__init____mutmut_8': xǁDQNǁ__init____mutmut_8, 
        'xǁDQNǁ__init____mutmut_9': xǁDQNǁ__init____mutmut_9, 
        'xǁDQNǁ__init____mutmut_10': xǁDQNǁ__init____mutmut_10, 
        'xǁDQNǁ__init____mutmut_11': xǁDQNǁ__init____mutmut_11, 
        'xǁDQNǁ__init____mutmut_12': xǁDQNǁ__init____mutmut_12, 
        'xǁDQNǁ__init____mutmut_13': xǁDQNǁ__init____mutmut_13, 
        'xǁDQNǁ__init____mutmut_14': xǁDQNǁ__init____mutmut_14, 
        'xǁDQNǁ__init____mutmut_15': xǁDQNǁ__init____mutmut_15, 
        'xǁDQNǁ__init____mutmut_16': xǁDQNǁ__init____mutmut_16, 
        'xǁDQNǁ__init____mutmut_17': xǁDQNǁ__init____mutmut_17, 
        'xǁDQNǁ__init____mutmut_18': xǁDQNǁ__init____mutmut_18, 
        'xǁDQNǁ__init____mutmut_19': xǁDQNǁ__init____mutmut_19, 
        'xǁDQNǁ__init____mutmut_20': xǁDQNǁ__init____mutmut_20, 
        'xǁDQNǁ__init____mutmut_21': xǁDQNǁ__init____mutmut_21, 
        'xǁDQNǁ__init____mutmut_22': xǁDQNǁ__init____mutmut_22, 
        'xǁDQNǁ__init____mutmut_23': xǁDQNǁ__init____mutmut_23, 
        'xǁDQNǁ__init____mutmut_24': xǁDQNǁ__init____mutmut_24, 
        'xǁDQNǁ__init____mutmut_25': xǁDQNǁ__init____mutmut_25, 
        'xǁDQNǁ__init____mutmut_26': xǁDQNǁ__init____mutmut_26, 
        'xǁDQNǁ__init____mutmut_27': xǁDQNǁ__init____mutmut_27, 
        'xǁDQNǁ__init____mutmut_28': xǁDQNǁ__init____mutmut_28
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDQNǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁDQNǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁDQNǁ__init____mutmut_orig)
    xǁDQNǁ__init____mutmut_orig.__name__ = 'xǁDQNǁ__init__'

    def xǁDQNǁ_get_q_values__mutmut_orig(self, state: Any, use_target: bool = False) -> Dict[Any, float]:
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

    def xǁDQNǁ_get_q_values__mutmut_1(self, state: Any, use_target: bool = True) -> Dict[Any, float]:
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

    def xǁDQNǁ_get_q_values__mutmut_2(self, state: Any, use_target: bool = False) -> Dict[Any, float]:
        """
        Get Q-values for all actions in state.

        Args:
            state: Current state
            use_target: Whether to use target network

        Returns:
            Dictionary mapping actions to Q-values
        """
        weights = None

        # Simple linear approximation: Q(s,a) = w_a · features(s)
        # For simplicity, use hash of state as feature
        state_feature = float(hash(str(state)) % 1000) / 1000.0

        q_values = {}
        for action in ["action_0", "action_1", "action_2"]:
            if action not in weights:
                weights[action] = np.random.randn() * 0.01
            q_values[action] = weights[action] * state_feature

        return q_values

    def xǁDQNǁ_get_q_values__mutmut_3(self, state: Any, use_target: bool = False) -> Dict[Any, float]:
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
        state_feature = None

        q_values = {}
        for action in ["action_0", "action_1", "action_2"]:
            if action not in weights:
                weights[action] = np.random.randn() * 0.01
            q_values[action] = weights[action] * state_feature

        return q_values

    def xǁDQNǁ_get_q_values__mutmut_4(self, state: Any, use_target: bool = False) -> Dict[Any, float]:
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
        state_feature = float(hash(str(state)) % 1000) * 1000.0

        q_values = {}
        for action in ["action_0", "action_1", "action_2"]:
            if action not in weights:
                weights[action] = np.random.randn() * 0.01
            q_values[action] = weights[action] * state_feature

        return q_values

    def xǁDQNǁ_get_q_values__mutmut_5(self, state: Any, use_target: bool = False) -> Dict[Any, float]:
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
        state_feature = float(None) / 1000.0

        q_values = {}
        for action in ["action_0", "action_1", "action_2"]:
            if action not in weights:
                weights[action] = np.random.randn() * 0.01
            q_values[action] = weights[action] * state_feature

        return q_values

    def xǁDQNǁ_get_q_values__mutmut_6(self, state: Any, use_target: bool = False) -> Dict[Any, float]:
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
        state_feature = float(hash(str(state)) / 1000) / 1000.0

        q_values = {}
        for action in ["action_0", "action_1", "action_2"]:
            if action not in weights:
                weights[action] = np.random.randn() * 0.01
            q_values[action] = weights[action] * state_feature

        return q_values

    def xǁDQNǁ_get_q_values__mutmut_7(self, state: Any, use_target: bool = False) -> Dict[Any, float]:
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
        state_feature = float(hash(None) % 1000) / 1000.0

        q_values = {}
        for action in ["action_0", "action_1", "action_2"]:
            if action not in weights:
                weights[action] = np.random.randn() * 0.01
            q_values[action] = weights[action] * state_feature

        return q_values

    def xǁDQNǁ_get_q_values__mutmut_8(self, state: Any, use_target: bool = False) -> Dict[Any, float]:
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
        state_feature = float(hash(str(None)) % 1000) / 1000.0

        q_values = {}
        for action in ["action_0", "action_1", "action_2"]:
            if action not in weights:
                weights[action] = np.random.randn() * 0.01
            q_values[action] = weights[action] * state_feature

        return q_values

    def xǁDQNǁ_get_q_values__mutmut_9(self, state: Any, use_target: bool = False) -> Dict[Any, float]:
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
        state_feature = float(hash(str(state)) % 1001) / 1000.0

        q_values = {}
        for action in ["action_0", "action_1", "action_2"]:
            if action not in weights:
                weights[action] = np.random.randn() * 0.01
            q_values[action] = weights[action] * state_feature

        return q_values

    def xǁDQNǁ_get_q_values__mutmut_10(self, state: Any, use_target: bool = False) -> Dict[Any, float]:
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
        state_feature = float(hash(str(state)) % 1000) / 1001.0

        q_values = {}
        for action in ["action_0", "action_1", "action_2"]:
            if action not in weights:
                weights[action] = np.random.randn() * 0.01
            q_values[action] = weights[action] * state_feature

        return q_values

    def xǁDQNǁ_get_q_values__mutmut_11(self, state: Any, use_target: bool = False) -> Dict[Any, float]:
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

        q_values = None
        for action in ["action_0", "action_1", "action_2"]:
            if action not in weights:
                weights[action] = np.random.randn() * 0.01
            q_values[action] = weights[action] * state_feature

        return q_values

    def xǁDQNǁ_get_q_values__mutmut_12(self, state: Any, use_target: bool = False) -> Dict[Any, float]:
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
        for action in ["XXaction_0XX", "action_1", "action_2"]:
            if action not in weights:
                weights[action] = np.random.randn() * 0.01
            q_values[action] = weights[action] * state_feature

        return q_values

    def xǁDQNǁ_get_q_values__mutmut_13(self, state: Any, use_target: bool = False) -> Dict[Any, float]:
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
        for action in ["ACTION_0", "action_1", "action_2"]:
            if action not in weights:
                weights[action] = np.random.randn() * 0.01
            q_values[action] = weights[action] * state_feature

        return q_values

    def xǁDQNǁ_get_q_values__mutmut_14(self, state: Any, use_target: bool = False) -> Dict[Any, float]:
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
        for action in ["action_0", "XXaction_1XX", "action_2"]:
            if action not in weights:
                weights[action] = np.random.randn() * 0.01
            q_values[action] = weights[action] * state_feature

        return q_values

    def xǁDQNǁ_get_q_values__mutmut_15(self, state: Any, use_target: bool = False) -> Dict[Any, float]:
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
        for action in ["action_0", "ACTION_1", "action_2"]:
            if action not in weights:
                weights[action] = np.random.randn() * 0.01
            q_values[action] = weights[action] * state_feature

        return q_values

    def xǁDQNǁ_get_q_values__mutmut_16(self, state: Any, use_target: bool = False) -> Dict[Any, float]:
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
        for action in ["action_0", "action_1", "XXaction_2XX"]:
            if action not in weights:
                weights[action] = np.random.randn() * 0.01
            q_values[action] = weights[action] * state_feature

        return q_values

    def xǁDQNǁ_get_q_values__mutmut_17(self, state: Any, use_target: bool = False) -> Dict[Any, float]:
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
        for action in ["action_0", "action_1", "ACTION_2"]:
            if action not in weights:
                weights[action] = np.random.randn() * 0.01
            q_values[action] = weights[action] * state_feature

        return q_values

    def xǁDQNǁ_get_q_values__mutmut_18(self, state: Any, use_target: bool = False) -> Dict[Any, float]:
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
            if action in weights:
                weights[action] = np.random.randn() * 0.01
            q_values[action] = weights[action] * state_feature

        return q_values

    def xǁDQNǁ_get_q_values__mutmut_19(self, state: Any, use_target: bool = False) -> Dict[Any, float]:
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
                weights[action] = None
            q_values[action] = weights[action] * state_feature

        return q_values

    def xǁDQNǁ_get_q_values__mutmut_20(self, state: Any, use_target: bool = False) -> Dict[Any, float]:
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
                weights[action] = np.random.randn() / 0.01
            q_values[action] = weights[action] * state_feature

        return q_values

    def xǁDQNǁ_get_q_values__mutmut_21(self, state: Any, use_target: bool = False) -> Dict[Any, float]:
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
                weights[action] = np.random.randn() * 1.01
            q_values[action] = weights[action] * state_feature

        return q_values

    def xǁDQNǁ_get_q_values__mutmut_22(self, state: Any, use_target: bool = False) -> Dict[Any, float]:
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
            q_values[action] = None

        return q_values

    def xǁDQNǁ_get_q_values__mutmut_23(self, state: Any, use_target: bool = False) -> Dict[Any, float]:
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
            q_values[action] = weights[action] / state_feature

        return q_values
    
    xǁDQNǁ_get_q_values__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDQNǁ_get_q_values__mutmut_1': xǁDQNǁ_get_q_values__mutmut_1, 
        'xǁDQNǁ_get_q_values__mutmut_2': xǁDQNǁ_get_q_values__mutmut_2, 
        'xǁDQNǁ_get_q_values__mutmut_3': xǁDQNǁ_get_q_values__mutmut_3, 
        'xǁDQNǁ_get_q_values__mutmut_4': xǁDQNǁ_get_q_values__mutmut_4, 
        'xǁDQNǁ_get_q_values__mutmut_5': xǁDQNǁ_get_q_values__mutmut_5, 
        'xǁDQNǁ_get_q_values__mutmut_6': xǁDQNǁ_get_q_values__mutmut_6, 
        'xǁDQNǁ_get_q_values__mutmut_7': xǁDQNǁ_get_q_values__mutmut_7, 
        'xǁDQNǁ_get_q_values__mutmut_8': xǁDQNǁ_get_q_values__mutmut_8, 
        'xǁDQNǁ_get_q_values__mutmut_9': xǁDQNǁ_get_q_values__mutmut_9, 
        'xǁDQNǁ_get_q_values__mutmut_10': xǁDQNǁ_get_q_values__mutmut_10, 
        'xǁDQNǁ_get_q_values__mutmut_11': xǁDQNǁ_get_q_values__mutmut_11, 
        'xǁDQNǁ_get_q_values__mutmut_12': xǁDQNǁ_get_q_values__mutmut_12, 
        'xǁDQNǁ_get_q_values__mutmut_13': xǁDQNǁ_get_q_values__mutmut_13, 
        'xǁDQNǁ_get_q_values__mutmut_14': xǁDQNǁ_get_q_values__mutmut_14, 
        'xǁDQNǁ_get_q_values__mutmut_15': xǁDQNǁ_get_q_values__mutmut_15, 
        'xǁDQNǁ_get_q_values__mutmut_16': xǁDQNǁ_get_q_values__mutmut_16, 
        'xǁDQNǁ_get_q_values__mutmut_17': xǁDQNǁ_get_q_values__mutmut_17, 
        'xǁDQNǁ_get_q_values__mutmut_18': xǁDQNǁ_get_q_values__mutmut_18, 
        'xǁDQNǁ_get_q_values__mutmut_19': xǁDQNǁ_get_q_values__mutmut_19, 
        'xǁDQNǁ_get_q_values__mutmut_20': xǁDQNǁ_get_q_values__mutmut_20, 
        'xǁDQNǁ_get_q_values__mutmut_21': xǁDQNǁ_get_q_values__mutmut_21, 
        'xǁDQNǁ_get_q_values__mutmut_22': xǁDQNǁ_get_q_values__mutmut_22, 
        'xǁDQNǁ_get_q_values__mutmut_23': xǁDQNǁ_get_q_values__mutmut_23
    }
    
    def _get_q_values(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDQNǁ_get_q_values__mutmut_orig"), object.__getattribute__(self, "xǁDQNǁ_get_q_values__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _get_q_values.__signature__ = _mutmut_signature(xǁDQNǁ_get_q_values__mutmut_orig)
    xǁDQNǁ_get_q_values__mutmut_orig.__name__ = 'xǁDQNǁ_get_q_values'

    def xǁDQNǁselect_action__mutmut_orig(self, state: Any) -> Any:
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
        else:
            # Exploit
            q_values = self._get_q_values(state)
            return max(q_values, key=q_values.get)

    def xǁDQNǁselect_action__mutmut_1(self, state: Any) -> Any:
        """
        Select action using ε-greedy policy.

        Args:
            state: Current state

        Returns:
            Selected action
        """
        if np.random.random() <= self.epsilon:
            # Explore
            return np.random.choice(["action_0", "action_1", "action_2"])
        else:
            # Exploit
            q_values = self._get_q_values(state)
            return max(q_values, key=q_values.get)

    def xǁDQNǁselect_action__mutmut_2(self, state: Any) -> Any:
        """
        Select action using ε-greedy policy.

        Args:
            state: Current state

        Returns:
            Selected action
        """
        if np.random.random() < self.epsilon:
            # Explore
            return np.random.choice(None)
        else:
            # Exploit
            q_values = self._get_q_values(state)
            return max(q_values, key=q_values.get)

    def xǁDQNǁselect_action__mutmut_3(self, state: Any) -> Any:
        """
        Select action using ε-greedy policy.

        Args:
            state: Current state

        Returns:
            Selected action
        """
        if np.random.random() < self.epsilon:
            # Explore
            return np.random.choice(["XXaction_0XX", "action_1", "action_2"])
        else:
            # Exploit
            q_values = self._get_q_values(state)
            return max(q_values, key=q_values.get)

    def xǁDQNǁselect_action__mutmut_4(self, state: Any) -> Any:
        """
        Select action using ε-greedy policy.

        Args:
            state: Current state

        Returns:
            Selected action
        """
        if np.random.random() < self.epsilon:
            # Explore
            return np.random.choice(["ACTION_0", "action_1", "action_2"])
        else:
            # Exploit
            q_values = self._get_q_values(state)
            return max(q_values, key=q_values.get)

    def xǁDQNǁselect_action__mutmut_5(self, state: Any) -> Any:
        """
        Select action using ε-greedy policy.

        Args:
            state: Current state

        Returns:
            Selected action
        """
        if np.random.random() < self.epsilon:
            # Explore
            return np.random.choice(["action_0", "XXaction_1XX", "action_2"])
        else:
            # Exploit
            q_values = self._get_q_values(state)
            return max(q_values, key=q_values.get)

    def xǁDQNǁselect_action__mutmut_6(self, state: Any) -> Any:
        """
        Select action using ε-greedy policy.

        Args:
            state: Current state

        Returns:
            Selected action
        """
        if np.random.random() < self.epsilon:
            # Explore
            return np.random.choice(["action_0", "ACTION_1", "action_2"])
        else:
            # Exploit
            q_values = self._get_q_values(state)
            return max(q_values, key=q_values.get)

    def xǁDQNǁselect_action__mutmut_7(self, state: Any) -> Any:
        """
        Select action using ε-greedy policy.

        Args:
            state: Current state

        Returns:
            Selected action
        """
        if np.random.random() < self.epsilon:
            # Explore
            return np.random.choice(["action_0", "action_1", "XXaction_2XX"])
        else:
            # Exploit
            q_values = self._get_q_values(state)
            return max(q_values, key=q_values.get)

    def xǁDQNǁselect_action__mutmut_8(self, state: Any) -> Any:
        """
        Select action using ε-greedy policy.

        Args:
            state: Current state

        Returns:
            Selected action
        """
        if np.random.random() < self.epsilon:
            # Explore
            return np.random.choice(["action_0", "action_1", "ACTION_2"])
        else:
            # Exploit
            q_values = self._get_q_values(state)
            return max(q_values, key=q_values.get)

    def xǁDQNǁselect_action__mutmut_9(self, state: Any) -> Any:
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
        else:
            # Exploit
            q_values = None
            return max(q_values, key=q_values.get)

    def xǁDQNǁselect_action__mutmut_10(self, state: Any) -> Any:
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
        else:
            # Exploit
            q_values = self._get_q_values(None)
            return max(q_values, key=q_values.get)

    def xǁDQNǁselect_action__mutmut_11(self, state: Any) -> Any:
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
        else:
            # Exploit
            q_values = self._get_q_values(state)
            return max(None, key=q_values.get)

    def xǁDQNǁselect_action__mutmut_12(self, state: Any) -> Any:
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
        else:
            # Exploit
            q_values = self._get_q_values(state)
            return max(q_values, key=None)

    def xǁDQNǁselect_action__mutmut_13(self, state: Any) -> Any:
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
        else:
            # Exploit
            q_values = self._get_q_values(state)
            return max(key=q_values.get)

    def xǁDQNǁselect_action__mutmut_14(self, state: Any) -> Any:
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
        else:
            # Exploit
            q_values = self._get_q_values(state)
            return max(q_values, )
    
    xǁDQNǁselect_action__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDQNǁselect_action__mutmut_1': xǁDQNǁselect_action__mutmut_1, 
        'xǁDQNǁselect_action__mutmut_2': xǁDQNǁselect_action__mutmut_2, 
        'xǁDQNǁselect_action__mutmut_3': xǁDQNǁselect_action__mutmut_3, 
        'xǁDQNǁselect_action__mutmut_4': xǁDQNǁselect_action__mutmut_4, 
        'xǁDQNǁselect_action__mutmut_5': xǁDQNǁselect_action__mutmut_5, 
        'xǁDQNǁselect_action__mutmut_6': xǁDQNǁselect_action__mutmut_6, 
        'xǁDQNǁselect_action__mutmut_7': xǁDQNǁselect_action__mutmut_7, 
        'xǁDQNǁselect_action__mutmut_8': xǁDQNǁselect_action__mutmut_8, 
        'xǁDQNǁselect_action__mutmut_9': xǁDQNǁselect_action__mutmut_9, 
        'xǁDQNǁselect_action__mutmut_10': xǁDQNǁselect_action__mutmut_10, 
        'xǁDQNǁselect_action__mutmut_11': xǁDQNǁselect_action__mutmut_11, 
        'xǁDQNǁselect_action__mutmut_12': xǁDQNǁselect_action__mutmut_12, 
        'xǁDQNǁselect_action__mutmut_13': xǁDQNǁselect_action__mutmut_13, 
        'xǁDQNǁselect_action__mutmut_14': xǁDQNǁselect_action__mutmut_14
    }
    
    def select_action(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDQNǁselect_action__mutmut_orig"), object.__getattribute__(self, "xǁDQNǁselect_action__mutmut_mutants"), args, kwargs, self)
        return result 
    
    select_action.__signature__ = _mutmut_signature(xǁDQNǁselect_action__mutmut_orig)
    xǁDQNǁselect_action__mutmut_orig.__name__ = 'xǁDQNǁselect_action'

    def xǁDQNǁupdate__mutmut_orig(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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

    def xǁDQNǁupdate__mutmut_1(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
        self.replay_buffer.add(None, action, reward, next_state, done)
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

    def xǁDQNǁupdate__mutmut_2(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
        self.replay_buffer.add(state, None, reward, next_state, done)
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

    def xǁDQNǁupdate__mutmut_3(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
        self.replay_buffer.add(state, action, None, next_state, done)
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

    def xǁDQNǁupdate__mutmut_4(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
        self.replay_buffer.add(state, action, reward, None, done)
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

    def xǁDQNǁupdate__mutmut_5(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
        self.replay_buffer.add(state, action, reward, next_state, None)
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

    def xǁDQNǁupdate__mutmut_6(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
        self.replay_buffer.add(action, reward, next_state, done)
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

    def xǁDQNǁupdate__mutmut_7(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
        self.replay_buffer.add(state, reward, next_state, done)
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

    def xǁDQNǁupdate__mutmut_8(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
        self.replay_buffer.add(state, action, next_state, done)
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

    def xǁDQNǁupdate__mutmut_9(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
        self.replay_buffer.add(state, action, reward, done)
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

    def xǁDQNǁupdate__mutmut_10(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
        self.replay_buffer.add(state, action, reward, next_state, )
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

    def xǁDQNǁupdate__mutmut_11(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
        self.step_count = 1

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

    def xǁDQNǁupdate__mutmut_12(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
        self.step_count -= 1

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

    def xǁDQNǁupdate__mutmut_13(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
        self.step_count += 2

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

    def xǁDQNǁupdate__mutmut_14(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            self.step_count % self.update_frequency == 0 or len(self.replay_buffer) >= self.batch_size
        ):
            self._train_step()

        # Update target network
        if self.step_count % self.target_update_freq == 0:
            self._update_target_network()

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁDQNǁupdate__mutmut_15(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            self.step_count / self.update_frequency == 0
            and len(self.replay_buffer) >= self.batch_size
        ):
            self._train_step()

        # Update target network
        if self.step_count % self.target_update_freq == 0:
            self._update_target_network()

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁDQNǁupdate__mutmut_16(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            self.step_count % self.update_frequency != 0
            and len(self.replay_buffer) >= self.batch_size
        ):
            self._train_step()

        # Update target network
        if self.step_count % self.target_update_freq == 0:
            self._update_target_network()

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁDQNǁupdate__mutmut_17(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            self.step_count % self.update_frequency == 1
            and len(self.replay_buffer) >= self.batch_size
        ):
            self._train_step()

        # Update target network
        if self.step_count % self.target_update_freq == 0:
            self._update_target_network()

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁDQNǁupdate__mutmut_18(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            and len(self.replay_buffer) > self.batch_size
        ):
            self._train_step()

        # Update target network
        if self.step_count % self.target_update_freq == 0:
            self._update_target_network()

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁDQNǁupdate__mutmut_19(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
        if self.step_count / self.target_update_freq == 0:
            self._update_target_network()

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁDQNǁupdate__mutmut_20(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
        if self.step_count % self.target_update_freq != 0:
            self._update_target_network()

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁDQNǁupdate__mutmut_21(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
        if self.step_count % self.target_update_freq == 1:
            self._update_target_network()

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def xǁDQNǁupdate__mutmut_22(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            self.epsilon = None

    def xǁDQNǁupdate__mutmut_23(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            self.epsilon = max(None, self.epsilon * self.epsilon_decay)

    def xǁDQNǁupdate__mutmut_24(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            self.epsilon = max(self.epsilon_min, None)

    def xǁDQNǁupdate__mutmut_25(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            self.epsilon = max(self.epsilon * self.epsilon_decay)

    def xǁDQNǁupdate__mutmut_26(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            self.epsilon = max(self.epsilon_min, )

    def xǁDQNǁupdate__mutmut_27(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            self.epsilon = max(self.epsilon_min, self.epsilon / self.epsilon_decay)
    
    xǁDQNǁupdate__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDQNǁupdate__mutmut_1': xǁDQNǁupdate__mutmut_1, 
        'xǁDQNǁupdate__mutmut_2': xǁDQNǁupdate__mutmut_2, 
        'xǁDQNǁupdate__mutmut_3': xǁDQNǁupdate__mutmut_3, 
        'xǁDQNǁupdate__mutmut_4': xǁDQNǁupdate__mutmut_4, 
        'xǁDQNǁupdate__mutmut_5': xǁDQNǁupdate__mutmut_5, 
        'xǁDQNǁupdate__mutmut_6': xǁDQNǁupdate__mutmut_6, 
        'xǁDQNǁupdate__mutmut_7': xǁDQNǁupdate__mutmut_7, 
        'xǁDQNǁupdate__mutmut_8': xǁDQNǁupdate__mutmut_8, 
        'xǁDQNǁupdate__mutmut_9': xǁDQNǁupdate__mutmut_9, 
        'xǁDQNǁupdate__mutmut_10': xǁDQNǁupdate__mutmut_10, 
        'xǁDQNǁupdate__mutmut_11': xǁDQNǁupdate__mutmut_11, 
        'xǁDQNǁupdate__mutmut_12': xǁDQNǁupdate__mutmut_12, 
        'xǁDQNǁupdate__mutmut_13': xǁDQNǁupdate__mutmut_13, 
        'xǁDQNǁupdate__mutmut_14': xǁDQNǁupdate__mutmut_14, 
        'xǁDQNǁupdate__mutmut_15': xǁDQNǁupdate__mutmut_15, 
        'xǁDQNǁupdate__mutmut_16': xǁDQNǁupdate__mutmut_16, 
        'xǁDQNǁupdate__mutmut_17': xǁDQNǁupdate__mutmut_17, 
        'xǁDQNǁupdate__mutmut_18': xǁDQNǁupdate__mutmut_18, 
        'xǁDQNǁupdate__mutmut_19': xǁDQNǁupdate__mutmut_19, 
        'xǁDQNǁupdate__mutmut_20': xǁDQNǁupdate__mutmut_20, 
        'xǁDQNǁupdate__mutmut_21': xǁDQNǁupdate__mutmut_21, 
        'xǁDQNǁupdate__mutmut_22': xǁDQNǁupdate__mutmut_22, 
        'xǁDQNǁupdate__mutmut_23': xǁDQNǁupdate__mutmut_23, 
        'xǁDQNǁupdate__mutmut_24': xǁDQNǁupdate__mutmut_24, 
        'xǁDQNǁupdate__mutmut_25': xǁDQNǁupdate__mutmut_25, 
        'xǁDQNǁupdate__mutmut_26': xǁDQNǁupdate__mutmut_26, 
        'xǁDQNǁupdate__mutmut_27': xǁDQNǁupdate__mutmut_27
    }
    
    def update(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDQNǁupdate__mutmut_orig"), object.__getattribute__(self, "xǁDQNǁupdate__mutmut_mutants"), args, kwargs, self)
        return result 
    
    update.__signature__ = _mutmut_signature(xǁDQNǁupdate__mutmut_orig)
    xǁDQNǁupdate__mutmut_orig.__name__ = 'xǁDQNǁupdate'

    def xǁDQNǁ_train_step__mutmut_orig(self):
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

    def xǁDQNǁ_train_step__mutmut_1(self):
        """Perform single training step on batch."""
        # Sample batch from replay buffer
        batch = None

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

    def xǁDQNǁ_train_step__mutmut_2(self):
        """Perform single training step on batch."""
        # Sample batch from replay buffer
        batch = self.replay_buffer.sample(None)

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

    def xǁDQNǁ_train_step__mutmut_3(self):
        """Perform single training step on batch."""
        # Sample batch from replay buffer
        batch = self.replay_buffer.sample(self.batch_size)

        total_loss = None

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

    def xǁDQNǁ_train_step__mutmut_4(self):
        """Perform single training step on batch."""
        # Sample batch from replay buffer
        batch = self.replay_buffer.sample(self.batch_size)

        total_loss = 1.0

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

    def xǁDQNǁ_train_step__mutmut_5(self):
        """Perform single training step on batch."""
        # Sample batch from replay buffer
        batch = self.replay_buffer.sample(self.batch_size)

        total_loss = 0.0

        for exp in batch:
            # Current Q-value
            q_values = None
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

    def xǁDQNǁ_train_step__mutmut_6(self):
        """Perform single training step on batch."""
        # Sample batch from replay buffer
        batch = self.replay_buffer.sample(self.batch_size)

        total_loss = 0.0

        for exp in batch:
            # Current Q-value
            q_values = self._get_q_values(None)
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

    def xǁDQNǁ_train_step__mutmut_7(self):
        """Perform single training step on batch."""
        # Sample batch from replay buffer
        batch = self.replay_buffer.sample(self.batch_size)

        total_loss = 0.0

        for exp in batch:
            # Current Q-value
            q_values = self._get_q_values(exp.state)
            current_q = None

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

    def xǁDQNǁ_train_step__mutmut_8(self):
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
                target_q = None
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

    def xǁDQNǁ_train_step__mutmut_9(self):
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
                next_q_values = None
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

    def xǁDQNǁ_train_step__mutmut_10(self):
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
                next_q_values = self._get_q_values(None, use_target=True)
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

    def xǁDQNǁ_train_step__mutmut_11(self):
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
                next_q_values = self._get_q_values(exp.next_state, use_target=None)
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

    def xǁDQNǁ_train_step__mutmut_12(self):
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
                next_q_values = self._get_q_values(use_target=True)
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

    def xǁDQNǁ_train_step__mutmut_13(self):
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
                next_q_values = self._get_q_values(exp.next_state, )
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

    def xǁDQNǁ_train_step__mutmut_14(self):
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
                next_q_values = self._get_q_values(exp.next_state, use_target=False)
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

    def xǁDQNǁ_train_step__mutmut_15(self):
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
                max_next_q = None
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

    def xǁDQNǁ_train_step__mutmut_16(self):
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
                max_next_q = max(None)
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

    def xǁDQNǁ_train_step__mutmut_17(self):
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
                target_q = None

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

    def xǁDQNǁ_train_step__mutmut_18(self):
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
                target_q = exp.reward - self.discount_factor * max_next_q

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

    def xǁDQNǁ_train_step__mutmut_19(self):
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
                target_q = exp.reward + self.discount_factor / max_next_q

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

    def xǁDQNǁ_train_step__mutmut_20(self):
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
            loss = None
            total_loss += loss

            # Update weights (simplified gradient descent)
            state_feature = float(hash(str(exp.state)) % 1000) / 1000.0
            gradient = 2 * (current_q - target_q) * state_feature
            self.q_weights[exp.action] -= self.learning_rate * gradient

        avg_loss = total_loss / len(batch)
        self.loss_history.append(avg_loss)
        self.update_count += 1

    def xǁDQNǁ_train_step__mutmut_21(self):
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
            loss = (target_q - current_q) * 2
            total_loss += loss

            # Update weights (simplified gradient descent)
            state_feature = float(hash(str(exp.state)) % 1000) / 1000.0
            gradient = 2 * (current_q - target_q) * state_feature
            self.q_weights[exp.action] -= self.learning_rate * gradient

        avg_loss = total_loss / len(batch)
        self.loss_history.append(avg_loss)
        self.update_count += 1

    def xǁDQNǁ_train_step__mutmut_22(self):
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
            loss = (target_q + current_q) ** 2
            total_loss += loss

            # Update weights (simplified gradient descent)
            state_feature = float(hash(str(exp.state)) % 1000) / 1000.0
            gradient = 2 * (current_q - target_q) * state_feature
            self.q_weights[exp.action] -= self.learning_rate * gradient

        avg_loss = total_loss / len(batch)
        self.loss_history.append(avg_loss)
        self.update_count += 1

    def xǁDQNǁ_train_step__mutmut_23(self):
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
            loss = (target_q - current_q) ** 3
            total_loss += loss

            # Update weights (simplified gradient descent)
            state_feature = float(hash(str(exp.state)) % 1000) / 1000.0
            gradient = 2 * (current_q - target_q) * state_feature
            self.q_weights[exp.action] -= self.learning_rate * gradient

        avg_loss = total_loss / len(batch)
        self.loss_history.append(avg_loss)
        self.update_count += 1

    def xǁDQNǁ_train_step__mutmut_24(self):
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
            total_loss = loss

            # Update weights (simplified gradient descent)
            state_feature = float(hash(str(exp.state)) % 1000) / 1000.0
            gradient = 2 * (current_q - target_q) * state_feature
            self.q_weights[exp.action] -= self.learning_rate * gradient

        avg_loss = total_loss / len(batch)
        self.loss_history.append(avg_loss)
        self.update_count += 1

    def xǁDQNǁ_train_step__mutmut_25(self):
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
            total_loss -= loss

            # Update weights (simplified gradient descent)
            state_feature = float(hash(str(exp.state)) % 1000) / 1000.0
            gradient = 2 * (current_q - target_q) * state_feature
            self.q_weights[exp.action] -= self.learning_rate * gradient

        avg_loss = total_loss / len(batch)
        self.loss_history.append(avg_loss)
        self.update_count += 1

    def xǁDQNǁ_train_step__mutmut_26(self):
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
            state_feature = None
            gradient = 2 * (current_q - target_q) * state_feature
            self.q_weights[exp.action] -= self.learning_rate * gradient

        avg_loss = total_loss / len(batch)
        self.loss_history.append(avg_loss)
        self.update_count += 1

    def xǁDQNǁ_train_step__mutmut_27(self):
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
            state_feature = float(hash(str(exp.state)) % 1000) * 1000.0
            gradient = 2 * (current_q - target_q) * state_feature
            self.q_weights[exp.action] -= self.learning_rate * gradient

        avg_loss = total_loss / len(batch)
        self.loss_history.append(avg_loss)
        self.update_count += 1

    def xǁDQNǁ_train_step__mutmut_28(self):
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
            state_feature = float(None) / 1000.0
            gradient = 2 * (current_q - target_q) * state_feature
            self.q_weights[exp.action] -= self.learning_rate * gradient

        avg_loss = total_loss / len(batch)
        self.loss_history.append(avg_loss)
        self.update_count += 1

    def xǁDQNǁ_train_step__mutmut_29(self):
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
            state_feature = float(hash(str(exp.state)) / 1000) / 1000.0
            gradient = 2 * (current_q - target_q) * state_feature
            self.q_weights[exp.action] -= self.learning_rate * gradient

        avg_loss = total_loss / len(batch)
        self.loss_history.append(avg_loss)
        self.update_count += 1

    def xǁDQNǁ_train_step__mutmut_30(self):
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
            state_feature = float(hash(None) % 1000) / 1000.0
            gradient = 2 * (current_q - target_q) * state_feature
            self.q_weights[exp.action] -= self.learning_rate * gradient

        avg_loss = total_loss / len(batch)
        self.loss_history.append(avg_loss)
        self.update_count += 1

    def xǁDQNǁ_train_step__mutmut_31(self):
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
            state_feature = float(hash(str(None)) % 1000) / 1000.0
            gradient = 2 * (current_q - target_q) * state_feature
            self.q_weights[exp.action] -= self.learning_rate * gradient

        avg_loss = total_loss / len(batch)
        self.loss_history.append(avg_loss)
        self.update_count += 1

    def xǁDQNǁ_train_step__mutmut_32(self):
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
            state_feature = float(hash(str(exp.state)) % 1001) / 1000.0
            gradient = 2 * (current_q - target_q) * state_feature
            self.q_weights[exp.action] -= self.learning_rate * gradient

        avg_loss = total_loss / len(batch)
        self.loss_history.append(avg_loss)
        self.update_count += 1

    def xǁDQNǁ_train_step__mutmut_33(self):
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
            state_feature = float(hash(str(exp.state)) % 1000) / 1001.0
            gradient = 2 * (current_q - target_q) * state_feature
            self.q_weights[exp.action] -= self.learning_rate * gradient

        avg_loss = total_loss / len(batch)
        self.loss_history.append(avg_loss)
        self.update_count += 1

    def xǁDQNǁ_train_step__mutmut_34(self):
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
            gradient = None
            self.q_weights[exp.action] -= self.learning_rate * gradient

        avg_loss = total_loss / len(batch)
        self.loss_history.append(avg_loss)
        self.update_count += 1

    def xǁDQNǁ_train_step__mutmut_35(self):
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
            gradient = 2 * (current_q - target_q) / state_feature
            self.q_weights[exp.action] -= self.learning_rate * gradient

        avg_loss = total_loss / len(batch)
        self.loss_history.append(avg_loss)
        self.update_count += 1

    def xǁDQNǁ_train_step__mutmut_36(self):
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
            gradient = 2 / (current_q - target_q) * state_feature
            self.q_weights[exp.action] -= self.learning_rate * gradient

        avg_loss = total_loss / len(batch)
        self.loss_history.append(avg_loss)
        self.update_count += 1

    def xǁDQNǁ_train_step__mutmut_37(self):
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
            gradient = 3 * (current_q - target_q) * state_feature
            self.q_weights[exp.action] -= self.learning_rate * gradient

        avg_loss = total_loss / len(batch)
        self.loss_history.append(avg_loss)
        self.update_count += 1

    def xǁDQNǁ_train_step__mutmut_38(self):
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
            gradient = 2 * (current_q + target_q) * state_feature
            self.q_weights[exp.action] -= self.learning_rate * gradient

        avg_loss = total_loss / len(batch)
        self.loss_history.append(avg_loss)
        self.update_count += 1

    def xǁDQNǁ_train_step__mutmut_39(self):
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
            self.q_weights[exp.action] = self.learning_rate * gradient

        avg_loss = total_loss / len(batch)
        self.loss_history.append(avg_loss)
        self.update_count += 1

    def xǁDQNǁ_train_step__mutmut_40(self):
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
            self.q_weights[exp.action] += self.learning_rate * gradient

        avg_loss = total_loss / len(batch)
        self.loss_history.append(avg_loss)
        self.update_count += 1

    def xǁDQNǁ_train_step__mutmut_41(self):
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
            self.q_weights[exp.action] -= self.learning_rate / gradient

        avg_loss = total_loss / len(batch)
        self.loss_history.append(avg_loss)
        self.update_count += 1

    def xǁDQNǁ_train_step__mutmut_42(self):
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

        avg_loss = None
        self.loss_history.append(avg_loss)
        self.update_count += 1

    def xǁDQNǁ_train_step__mutmut_43(self):
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

        avg_loss = total_loss * len(batch)
        self.loss_history.append(avg_loss)
        self.update_count += 1

    def xǁDQNǁ_train_step__mutmut_44(self):
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
        self.loss_history.append(None)
        self.update_count += 1

    def xǁDQNǁ_train_step__mutmut_45(self):
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
        self.update_count = 1

    def xǁDQNǁ_train_step__mutmut_46(self):
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
        self.update_count -= 1

    def xǁDQNǁ_train_step__mutmut_47(self):
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
        self.update_count += 2
    
    xǁDQNǁ_train_step__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDQNǁ_train_step__mutmut_1': xǁDQNǁ_train_step__mutmut_1, 
        'xǁDQNǁ_train_step__mutmut_2': xǁDQNǁ_train_step__mutmut_2, 
        'xǁDQNǁ_train_step__mutmut_3': xǁDQNǁ_train_step__mutmut_3, 
        'xǁDQNǁ_train_step__mutmut_4': xǁDQNǁ_train_step__mutmut_4, 
        'xǁDQNǁ_train_step__mutmut_5': xǁDQNǁ_train_step__mutmut_5, 
        'xǁDQNǁ_train_step__mutmut_6': xǁDQNǁ_train_step__mutmut_6, 
        'xǁDQNǁ_train_step__mutmut_7': xǁDQNǁ_train_step__mutmut_7, 
        'xǁDQNǁ_train_step__mutmut_8': xǁDQNǁ_train_step__mutmut_8, 
        'xǁDQNǁ_train_step__mutmut_9': xǁDQNǁ_train_step__mutmut_9, 
        'xǁDQNǁ_train_step__mutmut_10': xǁDQNǁ_train_step__mutmut_10, 
        'xǁDQNǁ_train_step__mutmut_11': xǁDQNǁ_train_step__mutmut_11, 
        'xǁDQNǁ_train_step__mutmut_12': xǁDQNǁ_train_step__mutmut_12, 
        'xǁDQNǁ_train_step__mutmut_13': xǁDQNǁ_train_step__mutmut_13, 
        'xǁDQNǁ_train_step__mutmut_14': xǁDQNǁ_train_step__mutmut_14, 
        'xǁDQNǁ_train_step__mutmut_15': xǁDQNǁ_train_step__mutmut_15, 
        'xǁDQNǁ_train_step__mutmut_16': xǁDQNǁ_train_step__mutmut_16, 
        'xǁDQNǁ_train_step__mutmut_17': xǁDQNǁ_train_step__mutmut_17, 
        'xǁDQNǁ_train_step__mutmut_18': xǁDQNǁ_train_step__mutmut_18, 
        'xǁDQNǁ_train_step__mutmut_19': xǁDQNǁ_train_step__mutmut_19, 
        'xǁDQNǁ_train_step__mutmut_20': xǁDQNǁ_train_step__mutmut_20, 
        'xǁDQNǁ_train_step__mutmut_21': xǁDQNǁ_train_step__mutmut_21, 
        'xǁDQNǁ_train_step__mutmut_22': xǁDQNǁ_train_step__mutmut_22, 
        'xǁDQNǁ_train_step__mutmut_23': xǁDQNǁ_train_step__mutmut_23, 
        'xǁDQNǁ_train_step__mutmut_24': xǁDQNǁ_train_step__mutmut_24, 
        'xǁDQNǁ_train_step__mutmut_25': xǁDQNǁ_train_step__mutmut_25, 
        'xǁDQNǁ_train_step__mutmut_26': xǁDQNǁ_train_step__mutmut_26, 
        'xǁDQNǁ_train_step__mutmut_27': xǁDQNǁ_train_step__mutmut_27, 
        'xǁDQNǁ_train_step__mutmut_28': xǁDQNǁ_train_step__mutmut_28, 
        'xǁDQNǁ_train_step__mutmut_29': xǁDQNǁ_train_step__mutmut_29, 
        'xǁDQNǁ_train_step__mutmut_30': xǁDQNǁ_train_step__mutmut_30, 
        'xǁDQNǁ_train_step__mutmut_31': xǁDQNǁ_train_step__mutmut_31, 
        'xǁDQNǁ_train_step__mutmut_32': xǁDQNǁ_train_step__mutmut_32, 
        'xǁDQNǁ_train_step__mutmut_33': xǁDQNǁ_train_step__mutmut_33, 
        'xǁDQNǁ_train_step__mutmut_34': xǁDQNǁ_train_step__mutmut_34, 
        'xǁDQNǁ_train_step__mutmut_35': xǁDQNǁ_train_step__mutmut_35, 
        'xǁDQNǁ_train_step__mutmut_36': xǁDQNǁ_train_step__mutmut_36, 
        'xǁDQNǁ_train_step__mutmut_37': xǁDQNǁ_train_step__mutmut_37, 
        'xǁDQNǁ_train_step__mutmut_38': xǁDQNǁ_train_step__mutmut_38, 
        'xǁDQNǁ_train_step__mutmut_39': xǁDQNǁ_train_step__mutmut_39, 
        'xǁDQNǁ_train_step__mutmut_40': xǁDQNǁ_train_step__mutmut_40, 
        'xǁDQNǁ_train_step__mutmut_41': xǁDQNǁ_train_step__mutmut_41, 
        'xǁDQNǁ_train_step__mutmut_42': xǁDQNǁ_train_step__mutmut_42, 
        'xǁDQNǁ_train_step__mutmut_43': xǁDQNǁ_train_step__mutmut_43, 
        'xǁDQNǁ_train_step__mutmut_44': xǁDQNǁ_train_step__mutmut_44, 
        'xǁDQNǁ_train_step__mutmut_45': xǁDQNǁ_train_step__mutmut_45, 
        'xǁDQNǁ_train_step__mutmut_46': xǁDQNǁ_train_step__mutmut_46, 
        'xǁDQNǁ_train_step__mutmut_47': xǁDQNǁ_train_step__mutmut_47
    }
    
    def _train_step(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDQNǁ_train_step__mutmut_orig"), object.__getattribute__(self, "xǁDQNǁ_train_step__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _train_step.__signature__ = _mutmut_signature(xǁDQNǁ_train_step__mutmut_orig)
    xǁDQNǁ_train_step__mutmut_orig.__name__ = 'xǁDQNǁ_train_step'

    def xǁDQNǁ_update_target_network__mutmut_orig(self):
        """Soft update of target network weights."""
        tau = 0.005  # Soft update parameter

        for action in self.q_weights:
            if action not in self.target_weights:
                self.target_weights[action] = self.q_weights[action]
            else:
                self.target_weights[action] = (
                    tau * self.q_weights[action]
                    + (1 - tau) * self.target_weights[action]
                )

    def xǁDQNǁ_update_target_network__mutmut_1(self):
        """Soft update of target network weights."""
        tau = None  # Soft update parameter

        for action in self.q_weights:
            if action not in self.target_weights:
                self.target_weights[action] = self.q_weights[action]
            else:
                self.target_weights[action] = (
                    tau * self.q_weights[action]
                    + (1 - tau) * self.target_weights[action]
                )

    def xǁDQNǁ_update_target_network__mutmut_2(self):
        """Soft update of target network weights."""
        tau = 1.005  # Soft update parameter

        for action in self.q_weights:
            if action not in self.target_weights:
                self.target_weights[action] = self.q_weights[action]
            else:
                self.target_weights[action] = (
                    tau * self.q_weights[action]
                    + (1 - tau) * self.target_weights[action]
                )

    def xǁDQNǁ_update_target_network__mutmut_3(self):
        """Soft update of target network weights."""
        tau = 0.005  # Soft update parameter

        for action in self.q_weights:
            if action in self.target_weights:
                self.target_weights[action] = self.q_weights[action]
            else:
                self.target_weights[action] = (
                    tau * self.q_weights[action]
                    + (1 - tau) * self.target_weights[action]
                )

    def xǁDQNǁ_update_target_network__mutmut_4(self):
        """Soft update of target network weights."""
        tau = 0.005  # Soft update parameter

        for action in self.q_weights:
            if action not in self.target_weights:
                self.target_weights[action] = None
            else:
                self.target_weights[action] = (
                    tau * self.q_weights[action]
                    + (1 - tau) * self.target_weights[action]
                )

    def xǁDQNǁ_update_target_network__mutmut_5(self):
        """Soft update of target network weights."""
        tau = 0.005  # Soft update parameter

        for action in self.q_weights:
            if action not in self.target_weights:
                self.target_weights[action] = self.q_weights[action]
            else:
                self.target_weights[action] = None

    def xǁDQNǁ_update_target_network__mutmut_6(self):
        """Soft update of target network weights."""
        tau = 0.005  # Soft update parameter

        for action in self.q_weights:
            if action not in self.target_weights:
                self.target_weights[action] = self.q_weights[action]
            else:
                self.target_weights[action] = (
                    tau * self.q_weights[action] - (1 - tau) * self.target_weights[action]
                )

    def xǁDQNǁ_update_target_network__mutmut_7(self):
        """Soft update of target network weights."""
        tau = 0.005  # Soft update parameter

        for action in self.q_weights:
            if action not in self.target_weights:
                self.target_weights[action] = self.q_weights[action]
            else:
                self.target_weights[action] = (
                    tau / self.q_weights[action]
                    + (1 - tau) * self.target_weights[action]
                )

    def xǁDQNǁ_update_target_network__mutmut_8(self):
        """Soft update of target network weights."""
        tau = 0.005  # Soft update parameter

        for action in self.q_weights:
            if action not in self.target_weights:
                self.target_weights[action] = self.q_weights[action]
            else:
                self.target_weights[action] = (
                    tau * self.q_weights[action]
                    + (1 - tau) / self.target_weights[action]
                )

    def xǁDQNǁ_update_target_network__mutmut_9(self):
        """Soft update of target network weights."""
        tau = 0.005  # Soft update parameter

        for action in self.q_weights:
            if action not in self.target_weights:
                self.target_weights[action] = self.q_weights[action]
            else:
                self.target_weights[action] = (
                    tau * self.q_weights[action]
                    + (1 + tau) * self.target_weights[action]
                )

    def xǁDQNǁ_update_target_network__mutmut_10(self):
        """Soft update of target network weights."""
        tau = 0.005  # Soft update parameter

        for action in self.q_weights:
            if action not in self.target_weights:
                self.target_weights[action] = self.q_weights[action]
            else:
                self.target_weights[action] = (
                    tau * self.q_weights[action]
                    + (2 - tau) * self.target_weights[action]
                )
    
    xǁDQNǁ_update_target_network__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDQNǁ_update_target_network__mutmut_1': xǁDQNǁ_update_target_network__mutmut_1, 
        'xǁDQNǁ_update_target_network__mutmut_2': xǁDQNǁ_update_target_network__mutmut_2, 
        'xǁDQNǁ_update_target_network__mutmut_3': xǁDQNǁ_update_target_network__mutmut_3, 
        'xǁDQNǁ_update_target_network__mutmut_4': xǁDQNǁ_update_target_network__mutmut_4, 
        'xǁDQNǁ_update_target_network__mutmut_5': xǁDQNǁ_update_target_network__mutmut_5, 
        'xǁDQNǁ_update_target_network__mutmut_6': xǁDQNǁ_update_target_network__mutmut_6, 
        'xǁDQNǁ_update_target_network__mutmut_7': xǁDQNǁ_update_target_network__mutmut_7, 
        'xǁDQNǁ_update_target_network__mutmut_8': xǁDQNǁ_update_target_network__mutmut_8, 
        'xǁDQNǁ_update_target_network__mutmut_9': xǁDQNǁ_update_target_network__mutmut_9, 
        'xǁDQNǁ_update_target_network__mutmut_10': xǁDQNǁ_update_target_network__mutmut_10
    }
    
    def _update_target_network(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDQNǁ_update_target_network__mutmut_orig"), object.__getattribute__(self, "xǁDQNǁ_update_target_network__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _update_target_network.__signature__ = _mutmut_signature(xǁDQNǁ_update_target_network__mutmut_orig)
    xǁDQNǁ_update_target_network__mutmut_orig.__name__ = 'xǁDQNǁ_update_target_network'

    def xǁDQNǁget_policy__mutmut_orig(self) -> Dict[Any, Any]:
        """
        Get greedy policy from Q-network.

        Returns:
            Policy (simplified representation)
        """
        return {"type": "DQN", "weights": dict(self.q_weights), "epsilon": self.epsilon}

    def xǁDQNǁget_policy__mutmut_1(self) -> Dict[Any, Any]:
        """
        Get greedy policy from Q-network.

        Returns:
            Policy (simplified representation)
        """
        return {"XXtypeXX": "DQN", "weights": dict(self.q_weights), "epsilon": self.epsilon}

    def xǁDQNǁget_policy__mutmut_2(self) -> Dict[Any, Any]:
        """
        Get greedy policy from Q-network.

        Returns:
            Policy (simplified representation)
        """
        return {"TYPE": "DQN", "weights": dict(self.q_weights), "epsilon": self.epsilon}

    def xǁDQNǁget_policy__mutmut_3(self) -> Dict[Any, Any]:
        """
        Get greedy policy from Q-network.

        Returns:
            Policy (simplified representation)
        """
        return {"type": "XXDQNXX", "weights": dict(self.q_weights), "epsilon": self.epsilon}

    def xǁDQNǁget_policy__mutmut_4(self) -> Dict[Any, Any]:
        """
        Get greedy policy from Q-network.

        Returns:
            Policy (simplified representation)
        """
        return {"type": "dqn", "weights": dict(self.q_weights), "epsilon": self.epsilon}

    def xǁDQNǁget_policy__mutmut_5(self) -> Dict[Any, Any]:
        """
        Get greedy policy from Q-network.

        Returns:
            Policy (simplified representation)
        """
        return {"type": "DQN", "XXweightsXX": dict(self.q_weights), "epsilon": self.epsilon}

    def xǁDQNǁget_policy__mutmut_6(self) -> Dict[Any, Any]:
        """
        Get greedy policy from Q-network.

        Returns:
            Policy (simplified representation)
        """
        return {"type": "DQN", "WEIGHTS": dict(self.q_weights), "epsilon": self.epsilon}

    def xǁDQNǁget_policy__mutmut_7(self) -> Dict[Any, Any]:
        """
        Get greedy policy from Q-network.

        Returns:
            Policy (simplified representation)
        """
        return {"type": "DQN", "weights": dict(None), "epsilon": self.epsilon}

    def xǁDQNǁget_policy__mutmut_8(self) -> Dict[Any, Any]:
        """
        Get greedy policy from Q-network.

        Returns:
            Policy (simplified representation)
        """
        return {"type": "DQN", "weights": dict(self.q_weights), "XXepsilonXX": self.epsilon}

    def xǁDQNǁget_policy__mutmut_9(self) -> Dict[Any, Any]:
        """
        Get greedy policy from Q-network.

        Returns:
            Policy (simplified representation)
        """
        return {"type": "DQN", "weights": dict(self.q_weights), "EPSILON": self.epsilon}
    
    xǁDQNǁget_policy__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDQNǁget_policy__mutmut_1': xǁDQNǁget_policy__mutmut_1, 
        'xǁDQNǁget_policy__mutmut_2': xǁDQNǁget_policy__mutmut_2, 
        'xǁDQNǁget_policy__mutmut_3': xǁDQNǁget_policy__mutmut_3, 
        'xǁDQNǁget_policy__mutmut_4': xǁDQNǁget_policy__mutmut_4, 
        'xǁDQNǁget_policy__mutmut_5': xǁDQNǁget_policy__mutmut_5, 
        'xǁDQNǁget_policy__mutmut_6': xǁDQNǁget_policy__mutmut_6, 
        'xǁDQNǁget_policy__mutmut_7': xǁDQNǁget_policy__mutmut_7, 
        'xǁDQNǁget_policy__mutmut_8': xǁDQNǁget_policy__mutmut_8, 
        'xǁDQNǁget_policy__mutmut_9': xǁDQNǁget_policy__mutmut_9
    }
    
    def get_policy(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDQNǁget_policy__mutmut_orig"), object.__getattribute__(self, "xǁDQNǁget_policy__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_policy.__signature__ = _mutmut_signature(xǁDQNǁget_policy__mutmut_orig)
    xǁDQNǁget_policy__mutmut_orig.__name__ = 'xǁDQNǁget_policy'


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

    def xǁPPOǁ__init____mutmut_orig(
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
        self.policy_weights: Dict[str, float] = {
            "action_0": 0.0,
            "action_1": 0.0,
            "action_2": 0.0,
        }

        # Value network (critic) - state values
        self.value_weights: Dict[Any, float] = {}

        # Trajectory buffer
        self.trajectory: List[Dict] = []

        # Statistics
        self.policy_updates = 0
        self.value_loss_history: List[float] = []
        self.policy_loss_history: List[float] = []

    def xǁPPOǁ__init____mutmut_1(
        self,
        learning_rate: float = 1.0003,
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
        self.policy_weights: Dict[str, float] = {
            "action_0": 0.0,
            "action_1": 0.0,
            "action_2": 0.0,
        }

        # Value network (critic) - state values
        self.value_weights: Dict[Any, float] = {}

        # Trajectory buffer
        self.trajectory: List[Dict] = []

        # Statistics
        self.policy_updates = 0
        self.value_loss_history: List[float] = []
        self.policy_loss_history: List[float] = []

    def xǁPPOǁ__init____mutmut_2(
        self,
        learning_rate: float = 0.0003,
        discount_factor: float = 1.99,
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
        self.policy_weights: Dict[str, float] = {
            "action_0": 0.0,
            "action_1": 0.0,
            "action_2": 0.0,
        }

        # Value network (critic) - state values
        self.value_weights: Dict[Any, float] = {}

        # Trajectory buffer
        self.trajectory: List[Dict] = []

        # Statistics
        self.policy_updates = 0
        self.value_loss_history: List[float] = []
        self.policy_loss_history: List[float] = []

    def xǁPPOǁ__init____mutmut_3(
        self,
        learning_rate: float = 0.0003,
        discount_factor: float = 0.99,
        clip_ratio: float = 1.2,
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
        self.policy_weights: Dict[str, float] = {
            "action_0": 0.0,
            "action_1": 0.0,
            "action_2": 0.0,
        }

        # Value network (critic) - state values
        self.value_weights: Dict[Any, float] = {}

        # Trajectory buffer
        self.trajectory: List[Dict] = []

        # Statistics
        self.policy_updates = 0
        self.value_loss_history: List[float] = []
        self.policy_loss_history: List[float] = []

    def xǁPPOǁ__init____mutmut_4(
        self,
        learning_rate: float = 0.0003,
        discount_factor: float = 0.99,
        clip_ratio: float = 0.2,
        gae_lambda: float = 1.95,
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
        self.policy_weights: Dict[str, float] = {
            "action_0": 0.0,
            "action_1": 0.0,
            "action_2": 0.0,
        }

        # Value network (critic) - state values
        self.value_weights: Dict[Any, float] = {}

        # Trajectory buffer
        self.trajectory: List[Dict] = []

        # Statistics
        self.policy_updates = 0
        self.value_loss_history: List[float] = []
        self.policy_loss_history: List[float] = []

    def xǁPPOǁ__init____mutmut_5(
        self,
        learning_rate: float = 0.0003,
        discount_factor: float = 0.99,
        clip_ratio: float = 0.2,
        gae_lambda: float = 0.95,
        epochs_per_update: int = 5,
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
        self.policy_weights: Dict[str, float] = {
            "action_0": 0.0,
            "action_1": 0.0,
            "action_2": 0.0,
        }

        # Value network (critic) - state values
        self.value_weights: Dict[Any, float] = {}

        # Trajectory buffer
        self.trajectory: List[Dict] = []

        # Statistics
        self.policy_updates = 0
        self.value_loss_history: List[float] = []
        self.policy_loss_history: List[float] = []

    def xǁPPOǁ__init____mutmut_6(
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
        super().__init__(None, discount_factor)
        self.clip_ratio = clip_ratio
        self.gae_lambda = gae_lambda
        self.epochs_per_update = epochs_per_update

        # Policy network (actor) - action probabilities
        self.policy_weights: Dict[str, float] = {
            "action_0": 0.0,
            "action_1": 0.0,
            "action_2": 0.0,
        }

        # Value network (critic) - state values
        self.value_weights: Dict[Any, float] = {}

        # Trajectory buffer
        self.trajectory: List[Dict] = []

        # Statistics
        self.policy_updates = 0
        self.value_loss_history: List[float] = []
        self.policy_loss_history: List[float] = []

    def xǁPPOǁ__init____mutmut_7(
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
        super().__init__(learning_rate, None)
        self.clip_ratio = clip_ratio
        self.gae_lambda = gae_lambda
        self.epochs_per_update = epochs_per_update

        # Policy network (actor) - action probabilities
        self.policy_weights: Dict[str, float] = {
            "action_0": 0.0,
            "action_1": 0.0,
            "action_2": 0.0,
        }

        # Value network (critic) - state values
        self.value_weights: Dict[Any, float] = {}

        # Trajectory buffer
        self.trajectory: List[Dict] = []

        # Statistics
        self.policy_updates = 0
        self.value_loss_history: List[float] = []
        self.policy_loss_history: List[float] = []

    def xǁPPOǁ__init____mutmut_8(
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
        super().__init__(discount_factor)
        self.clip_ratio = clip_ratio
        self.gae_lambda = gae_lambda
        self.epochs_per_update = epochs_per_update

        # Policy network (actor) - action probabilities
        self.policy_weights: Dict[str, float] = {
            "action_0": 0.0,
            "action_1": 0.0,
            "action_2": 0.0,
        }

        # Value network (critic) - state values
        self.value_weights: Dict[Any, float] = {}

        # Trajectory buffer
        self.trajectory: List[Dict] = []

        # Statistics
        self.policy_updates = 0
        self.value_loss_history: List[float] = []
        self.policy_loss_history: List[float] = []

    def xǁPPOǁ__init____mutmut_9(
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
        super().__init__(learning_rate, )
        self.clip_ratio = clip_ratio
        self.gae_lambda = gae_lambda
        self.epochs_per_update = epochs_per_update

        # Policy network (actor) - action probabilities
        self.policy_weights: Dict[str, float] = {
            "action_0": 0.0,
            "action_1": 0.0,
            "action_2": 0.0,
        }

        # Value network (critic) - state values
        self.value_weights: Dict[Any, float] = {}

        # Trajectory buffer
        self.trajectory: List[Dict] = []

        # Statistics
        self.policy_updates = 0
        self.value_loss_history: List[float] = []
        self.policy_loss_history: List[float] = []

    def xǁPPOǁ__init____mutmut_10(
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
        self.clip_ratio = None
        self.gae_lambda = gae_lambda
        self.epochs_per_update = epochs_per_update

        # Policy network (actor) - action probabilities
        self.policy_weights: Dict[str, float] = {
            "action_0": 0.0,
            "action_1": 0.0,
            "action_2": 0.0,
        }

        # Value network (critic) - state values
        self.value_weights: Dict[Any, float] = {}

        # Trajectory buffer
        self.trajectory: List[Dict] = []

        # Statistics
        self.policy_updates = 0
        self.value_loss_history: List[float] = []
        self.policy_loss_history: List[float] = []

    def xǁPPOǁ__init____mutmut_11(
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
        self.gae_lambda = None
        self.epochs_per_update = epochs_per_update

        # Policy network (actor) - action probabilities
        self.policy_weights: Dict[str, float] = {
            "action_0": 0.0,
            "action_1": 0.0,
            "action_2": 0.0,
        }

        # Value network (critic) - state values
        self.value_weights: Dict[Any, float] = {}

        # Trajectory buffer
        self.trajectory: List[Dict] = []

        # Statistics
        self.policy_updates = 0
        self.value_loss_history: List[float] = []
        self.policy_loss_history: List[float] = []

    def xǁPPOǁ__init____mutmut_12(
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
        self.epochs_per_update = None

        # Policy network (actor) - action probabilities
        self.policy_weights: Dict[str, float] = {
            "action_0": 0.0,
            "action_1": 0.0,
            "action_2": 0.0,
        }

        # Value network (critic) - state values
        self.value_weights: Dict[Any, float] = {}

        # Trajectory buffer
        self.trajectory: List[Dict] = []

        # Statistics
        self.policy_updates = 0
        self.value_loss_history: List[float] = []
        self.policy_loss_history: List[float] = []

    def xǁPPOǁ__init____mutmut_13(
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
        self.policy_weights: Dict[str, float] = None

        # Value network (critic) - state values
        self.value_weights: Dict[Any, float] = {}

        # Trajectory buffer
        self.trajectory: List[Dict] = []

        # Statistics
        self.policy_updates = 0
        self.value_loss_history: List[float] = []
        self.policy_loss_history: List[float] = []

    def xǁPPOǁ__init____mutmut_14(
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
        self.policy_weights: Dict[str, float] = {
            "XXaction_0XX": 0.0,
            "action_1": 0.0,
            "action_2": 0.0,
        }

        # Value network (critic) - state values
        self.value_weights: Dict[Any, float] = {}

        # Trajectory buffer
        self.trajectory: List[Dict] = []

        # Statistics
        self.policy_updates = 0
        self.value_loss_history: List[float] = []
        self.policy_loss_history: List[float] = []

    def xǁPPOǁ__init____mutmut_15(
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
        self.policy_weights: Dict[str, float] = {
            "ACTION_0": 0.0,
            "action_1": 0.0,
            "action_2": 0.0,
        }

        # Value network (critic) - state values
        self.value_weights: Dict[Any, float] = {}

        # Trajectory buffer
        self.trajectory: List[Dict] = []

        # Statistics
        self.policy_updates = 0
        self.value_loss_history: List[float] = []
        self.policy_loss_history: List[float] = []

    def xǁPPOǁ__init____mutmut_16(
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
        self.policy_weights: Dict[str, float] = {
            "action_0": 1.0,
            "action_1": 0.0,
            "action_2": 0.0,
        }

        # Value network (critic) - state values
        self.value_weights: Dict[Any, float] = {}

        # Trajectory buffer
        self.trajectory: List[Dict] = []

        # Statistics
        self.policy_updates = 0
        self.value_loss_history: List[float] = []
        self.policy_loss_history: List[float] = []

    def xǁPPOǁ__init____mutmut_17(
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
        self.policy_weights: Dict[str, float] = {
            "action_0": 0.0,
            "XXaction_1XX": 0.0,
            "action_2": 0.0,
        }

        # Value network (critic) - state values
        self.value_weights: Dict[Any, float] = {}

        # Trajectory buffer
        self.trajectory: List[Dict] = []

        # Statistics
        self.policy_updates = 0
        self.value_loss_history: List[float] = []
        self.policy_loss_history: List[float] = []

    def xǁPPOǁ__init____mutmut_18(
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
        self.policy_weights: Dict[str, float] = {
            "action_0": 0.0,
            "ACTION_1": 0.0,
            "action_2": 0.0,
        }

        # Value network (critic) - state values
        self.value_weights: Dict[Any, float] = {}

        # Trajectory buffer
        self.trajectory: List[Dict] = []

        # Statistics
        self.policy_updates = 0
        self.value_loss_history: List[float] = []
        self.policy_loss_history: List[float] = []

    def xǁPPOǁ__init____mutmut_19(
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
        self.policy_weights: Dict[str, float] = {
            "action_0": 0.0,
            "action_1": 1.0,
            "action_2": 0.0,
        }

        # Value network (critic) - state values
        self.value_weights: Dict[Any, float] = {}

        # Trajectory buffer
        self.trajectory: List[Dict] = []

        # Statistics
        self.policy_updates = 0
        self.value_loss_history: List[float] = []
        self.policy_loss_history: List[float] = []

    def xǁPPOǁ__init____mutmut_20(
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
        self.policy_weights: Dict[str, float] = {
            "action_0": 0.0,
            "action_1": 0.0,
            "XXaction_2XX": 0.0,
        }

        # Value network (critic) - state values
        self.value_weights: Dict[Any, float] = {}

        # Trajectory buffer
        self.trajectory: List[Dict] = []

        # Statistics
        self.policy_updates = 0
        self.value_loss_history: List[float] = []
        self.policy_loss_history: List[float] = []

    def xǁPPOǁ__init____mutmut_21(
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
        self.policy_weights: Dict[str, float] = {
            "action_0": 0.0,
            "action_1": 0.0,
            "ACTION_2": 0.0,
        }

        # Value network (critic) - state values
        self.value_weights: Dict[Any, float] = {}

        # Trajectory buffer
        self.trajectory: List[Dict] = []

        # Statistics
        self.policy_updates = 0
        self.value_loss_history: List[float] = []
        self.policy_loss_history: List[float] = []

    def xǁPPOǁ__init____mutmut_22(
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
        self.policy_weights: Dict[str, float] = {
            "action_0": 0.0,
            "action_1": 0.0,
            "action_2": 1.0,
        }

        # Value network (critic) - state values
        self.value_weights: Dict[Any, float] = {}

        # Trajectory buffer
        self.trajectory: List[Dict] = []

        # Statistics
        self.policy_updates = 0
        self.value_loss_history: List[float] = []
        self.policy_loss_history: List[float] = []

    def xǁPPOǁ__init____mutmut_23(
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
        self.policy_weights: Dict[str, float] = {
            "action_0": 0.0,
            "action_1": 0.0,
            "action_2": 0.0,
        }

        # Value network (critic) - state values
        self.value_weights: Dict[Any, float] = None

        # Trajectory buffer
        self.trajectory: List[Dict] = []

        # Statistics
        self.policy_updates = 0
        self.value_loss_history: List[float] = []
        self.policy_loss_history: List[float] = []

    def xǁPPOǁ__init____mutmut_24(
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
        self.policy_weights: Dict[str, float] = {
            "action_0": 0.0,
            "action_1": 0.0,
            "action_2": 0.0,
        }

        # Value network (critic) - state values
        self.value_weights: Dict[Any, float] = {}

        # Trajectory buffer
        self.trajectory: List[Dict] = None

        # Statistics
        self.policy_updates = 0
        self.value_loss_history: List[float] = []
        self.policy_loss_history: List[float] = []

    def xǁPPOǁ__init____mutmut_25(
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
        self.policy_weights: Dict[str, float] = {
            "action_0": 0.0,
            "action_1": 0.0,
            "action_2": 0.0,
        }

        # Value network (critic) - state values
        self.value_weights: Dict[Any, float] = {}

        # Trajectory buffer
        self.trajectory: List[Dict] = []

        # Statistics
        self.policy_updates = None
        self.value_loss_history: List[float] = []
        self.policy_loss_history: List[float] = []

    def xǁPPOǁ__init____mutmut_26(
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
        self.policy_weights: Dict[str, float] = {
            "action_0": 0.0,
            "action_1": 0.0,
            "action_2": 0.0,
        }

        # Value network (critic) - state values
        self.value_weights: Dict[Any, float] = {}

        # Trajectory buffer
        self.trajectory: List[Dict] = []

        # Statistics
        self.policy_updates = 1
        self.value_loss_history: List[float] = []
        self.policy_loss_history: List[float] = []

    def xǁPPOǁ__init____mutmut_27(
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
        self.policy_weights: Dict[str, float] = {
            "action_0": 0.0,
            "action_1": 0.0,
            "action_2": 0.0,
        }

        # Value network (critic) - state values
        self.value_weights: Dict[Any, float] = {}

        # Trajectory buffer
        self.trajectory: List[Dict] = []

        # Statistics
        self.policy_updates = 0
        self.value_loss_history: List[float] = None
        self.policy_loss_history: List[float] = []

    def xǁPPOǁ__init____mutmut_28(
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
        self.policy_weights: Dict[str, float] = {
            "action_0": 0.0,
            "action_1": 0.0,
            "action_2": 0.0,
        }

        # Value network (critic) - state values
        self.value_weights: Dict[Any, float] = {}

        # Trajectory buffer
        self.trajectory: List[Dict] = []

        # Statistics
        self.policy_updates = 0
        self.value_loss_history: List[float] = []
        self.policy_loss_history: List[float] = None
    
    xǁPPOǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPPOǁ__init____mutmut_1': xǁPPOǁ__init____mutmut_1, 
        'xǁPPOǁ__init____mutmut_2': xǁPPOǁ__init____mutmut_2, 
        'xǁPPOǁ__init____mutmut_3': xǁPPOǁ__init____mutmut_3, 
        'xǁPPOǁ__init____mutmut_4': xǁPPOǁ__init____mutmut_4, 
        'xǁPPOǁ__init____mutmut_5': xǁPPOǁ__init____mutmut_5, 
        'xǁPPOǁ__init____mutmut_6': xǁPPOǁ__init____mutmut_6, 
        'xǁPPOǁ__init____mutmut_7': xǁPPOǁ__init____mutmut_7, 
        'xǁPPOǁ__init____mutmut_8': xǁPPOǁ__init____mutmut_8, 
        'xǁPPOǁ__init____mutmut_9': xǁPPOǁ__init____mutmut_9, 
        'xǁPPOǁ__init____mutmut_10': xǁPPOǁ__init____mutmut_10, 
        'xǁPPOǁ__init____mutmut_11': xǁPPOǁ__init____mutmut_11, 
        'xǁPPOǁ__init____mutmut_12': xǁPPOǁ__init____mutmut_12, 
        'xǁPPOǁ__init____mutmut_13': xǁPPOǁ__init____mutmut_13, 
        'xǁPPOǁ__init____mutmut_14': xǁPPOǁ__init____mutmut_14, 
        'xǁPPOǁ__init____mutmut_15': xǁPPOǁ__init____mutmut_15, 
        'xǁPPOǁ__init____mutmut_16': xǁPPOǁ__init____mutmut_16, 
        'xǁPPOǁ__init____mutmut_17': xǁPPOǁ__init____mutmut_17, 
        'xǁPPOǁ__init____mutmut_18': xǁPPOǁ__init____mutmut_18, 
        'xǁPPOǁ__init____mutmut_19': xǁPPOǁ__init____mutmut_19, 
        'xǁPPOǁ__init____mutmut_20': xǁPPOǁ__init____mutmut_20, 
        'xǁPPOǁ__init____mutmut_21': xǁPPOǁ__init____mutmut_21, 
        'xǁPPOǁ__init____mutmut_22': xǁPPOǁ__init____mutmut_22, 
        'xǁPPOǁ__init____mutmut_23': xǁPPOǁ__init____mutmut_23, 
        'xǁPPOǁ__init____mutmut_24': xǁPPOǁ__init____mutmut_24, 
        'xǁPPOǁ__init____mutmut_25': xǁPPOǁ__init____mutmut_25, 
        'xǁPPOǁ__init____mutmut_26': xǁPPOǁ__init____mutmut_26, 
        'xǁPPOǁ__init____mutmut_27': xǁPPOǁ__init____mutmut_27, 
        'xǁPPOǁ__init____mutmut_28': xǁPPOǁ__init____mutmut_28
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPPOǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁPPOǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁPPOǁ__init____mutmut_orig)
    xǁPPOǁ__init____mutmut_orig.__name__ = 'xǁPPOǁ__init__'

    def xǁPPOǁ_get_action_probs__mutmut_orig(self, state: Any) -> Dict[str, float]:
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
            action: self.policy_weights[action] * state_feature
            for action in self.policy_weights
        }

        # Softmax to get probabilities
        max_logit = max(logits.values())
        exp_logits = {a: np.exp(l - max_logit) for a, l in logits.items()}
        total = sum(exp_logits.values())
        probs = {a: e / total for a, e in exp_logits.items()}

        return probs

    def xǁPPOǁ_get_action_probs__mutmut_1(self, state: Any) -> Dict[str, float]:
        """
        Get action probabilities from policy network.

        Args:
            state: Current state

        Returns:
            Action probabilities
        """
        # Compute logits
        state_feature = None
        logits = {
            action: self.policy_weights[action] * state_feature
            for action in self.policy_weights
        }

        # Softmax to get probabilities
        max_logit = max(logits.values())
        exp_logits = {a: np.exp(l - max_logit) for a, l in logits.items()}
        total = sum(exp_logits.values())
        probs = {a: e / total for a, e in exp_logits.items()}

        return probs

    def xǁPPOǁ_get_action_probs__mutmut_2(self, state: Any) -> Dict[str, float]:
        """
        Get action probabilities from policy network.

        Args:
            state: Current state

        Returns:
            Action probabilities
        """
        # Compute logits
        state_feature = float(hash(str(state)) % 1000) * 1000.0
        logits = {
            action: self.policy_weights[action] * state_feature
            for action in self.policy_weights
        }

        # Softmax to get probabilities
        max_logit = max(logits.values())
        exp_logits = {a: np.exp(l - max_logit) for a, l in logits.items()}
        total = sum(exp_logits.values())
        probs = {a: e / total for a, e in exp_logits.items()}

        return probs

    def xǁPPOǁ_get_action_probs__mutmut_3(self, state: Any) -> Dict[str, float]:
        """
        Get action probabilities from policy network.

        Args:
            state: Current state

        Returns:
            Action probabilities
        """
        # Compute logits
        state_feature = float(None) / 1000.0
        logits = {
            action: self.policy_weights[action] * state_feature
            for action in self.policy_weights
        }

        # Softmax to get probabilities
        max_logit = max(logits.values())
        exp_logits = {a: np.exp(l - max_logit) for a, l in logits.items()}
        total = sum(exp_logits.values())
        probs = {a: e / total for a, e in exp_logits.items()}

        return probs

    def xǁPPOǁ_get_action_probs__mutmut_4(self, state: Any) -> Dict[str, float]:
        """
        Get action probabilities from policy network.

        Args:
            state: Current state

        Returns:
            Action probabilities
        """
        # Compute logits
        state_feature = float(hash(str(state)) / 1000) / 1000.0
        logits = {
            action: self.policy_weights[action] * state_feature
            for action in self.policy_weights
        }

        # Softmax to get probabilities
        max_logit = max(logits.values())
        exp_logits = {a: np.exp(l - max_logit) for a, l in logits.items()}
        total = sum(exp_logits.values())
        probs = {a: e / total for a, e in exp_logits.items()}

        return probs

    def xǁPPOǁ_get_action_probs__mutmut_5(self, state: Any) -> Dict[str, float]:
        """
        Get action probabilities from policy network.

        Args:
            state: Current state

        Returns:
            Action probabilities
        """
        # Compute logits
        state_feature = float(hash(None) % 1000) / 1000.0
        logits = {
            action: self.policy_weights[action] * state_feature
            for action in self.policy_weights
        }

        # Softmax to get probabilities
        max_logit = max(logits.values())
        exp_logits = {a: np.exp(l - max_logit) for a, l in logits.items()}
        total = sum(exp_logits.values())
        probs = {a: e / total for a, e in exp_logits.items()}

        return probs

    def xǁPPOǁ_get_action_probs__mutmut_6(self, state: Any) -> Dict[str, float]:
        """
        Get action probabilities from policy network.

        Args:
            state: Current state

        Returns:
            Action probabilities
        """
        # Compute logits
        state_feature = float(hash(str(None)) % 1000) / 1000.0
        logits = {
            action: self.policy_weights[action] * state_feature
            for action in self.policy_weights
        }

        # Softmax to get probabilities
        max_logit = max(logits.values())
        exp_logits = {a: np.exp(l - max_logit) for a, l in logits.items()}
        total = sum(exp_logits.values())
        probs = {a: e / total for a, e in exp_logits.items()}

        return probs

    def xǁPPOǁ_get_action_probs__mutmut_7(self, state: Any) -> Dict[str, float]:
        """
        Get action probabilities from policy network.

        Args:
            state: Current state

        Returns:
            Action probabilities
        """
        # Compute logits
        state_feature = float(hash(str(state)) % 1001) / 1000.0
        logits = {
            action: self.policy_weights[action] * state_feature
            for action in self.policy_weights
        }

        # Softmax to get probabilities
        max_logit = max(logits.values())
        exp_logits = {a: np.exp(l - max_logit) for a, l in logits.items()}
        total = sum(exp_logits.values())
        probs = {a: e / total for a, e in exp_logits.items()}

        return probs

    def xǁPPOǁ_get_action_probs__mutmut_8(self, state: Any) -> Dict[str, float]:
        """
        Get action probabilities from policy network.

        Args:
            state: Current state

        Returns:
            Action probabilities
        """
        # Compute logits
        state_feature = float(hash(str(state)) % 1000) / 1001.0
        logits = {
            action: self.policy_weights[action] * state_feature
            for action in self.policy_weights
        }

        # Softmax to get probabilities
        max_logit = max(logits.values())
        exp_logits = {a: np.exp(l - max_logit) for a, l in logits.items()}
        total = sum(exp_logits.values())
        probs = {a: e / total for a, e in exp_logits.items()}

        return probs

    def xǁPPOǁ_get_action_probs__mutmut_9(self, state: Any) -> Dict[str, float]:
        """
        Get action probabilities from policy network.

        Args:
            state: Current state

        Returns:
            Action probabilities
        """
        # Compute logits
        state_feature = float(hash(str(state)) % 1000) / 1000.0
        logits = None

        # Softmax to get probabilities
        max_logit = max(logits.values())
        exp_logits = {a: np.exp(l - max_logit) for a, l in logits.items()}
        total = sum(exp_logits.values())
        probs = {a: e / total for a, e in exp_logits.items()}

        return probs

    def xǁPPOǁ_get_action_probs__mutmut_10(self, state: Any) -> Dict[str, float]:
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
            action: self.policy_weights[action] / state_feature
            for action in self.policy_weights
        }

        # Softmax to get probabilities
        max_logit = max(logits.values())
        exp_logits = {a: np.exp(l - max_logit) for a, l in logits.items()}
        total = sum(exp_logits.values())
        probs = {a: e / total for a, e in exp_logits.items()}

        return probs

    def xǁPPOǁ_get_action_probs__mutmut_11(self, state: Any) -> Dict[str, float]:
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
            action: self.policy_weights[action] * state_feature
            for action in self.policy_weights
        }

        # Softmax to get probabilities
        max_logit = None
        exp_logits = {a: np.exp(l - max_logit) for a, l in logits.items()}
        total = sum(exp_logits.values())
        probs = {a: e / total for a, e in exp_logits.items()}

        return probs

    def xǁPPOǁ_get_action_probs__mutmut_12(self, state: Any) -> Dict[str, float]:
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
            action: self.policy_weights[action] * state_feature
            for action in self.policy_weights
        }

        # Softmax to get probabilities
        max_logit = max(None)
        exp_logits = {a: np.exp(l - max_logit) for a, l in logits.items()}
        total = sum(exp_logits.values())
        probs = {a: e / total for a, e in exp_logits.items()}

        return probs

    def xǁPPOǁ_get_action_probs__mutmut_13(self, state: Any) -> Dict[str, float]:
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
            action: self.policy_weights[action] * state_feature
            for action in self.policy_weights
        }

        # Softmax to get probabilities
        max_logit = max(logits.values())
        exp_logits = None
        total = sum(exp_logits.values())
        probs = {a: e / total for a, e in exp_logits.items()}

        return probs

    def xǁPPOǁ_get_action_probs__mutmut_14(self, state: Any) -> Dict[str, float]:
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
            action: self.policy_weights[action] * state_feature
            for action in self.policy_weights
        }

        # Softmax to get probabilities
        max_logit = max(logits.values())
        exp_logits = {a: np.exp(None) for a, l in logits.items()}
        total = sum(exp_logits.values())
        probs = {a: e / total for a, e in exp_logits.items()}

        return probs

    def xǁPPOǁ_get_action_probs__mutmut_15(self, state: Any) -> Dict[str, float]:
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
            action: self.policy_weights[action] * state_feature
            for action in self.policy_weights
        }

        # Softmax to get probabilities
        max_logit = max(logits.values())
        exp_logits = {a: np.exp(l + max_logit) for a, l in logits.items()}
        total = sum(exp_logits.values())
        probs = {a: e / total for a, e in exp_logits.items()}

        return probs

    def xǁPPOǁ_get_action_probs__mutmut_16(self, state: Any) -> Dict[str, float]:
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
            action: self.policy_weights[action] * state_feature
            for action in self.policy_weights
        }

        # Softmax to get probabilities
        max_logit = max(logits.values())
        exp_logits = {a: np.exp(l - max_logit) for a, l in logits.items()}
        total = None
        probs = {a: e / total for a, e in exp_logits.items()}

        return probs

    def xǁPPOǁ_get_action_probs__mutmut_17(self, state: Any) -> Dict[str, float]:
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
            action: self.policy_weights[action] * state_feature
            for action in self.policy_weights
        }

        # Softmax to get probabilities
        max_logit = max(logits.values())
        exp_logits = {a: np.exp(l - max_logit) for a, l in logits.items()}
        total = sum(None)
        probs = {a: e / total for a, e in exp_logits.items()}

        return probs

    def xǁPPOǁ_get_action_probs__mutmut_18(self, state: Any) -> Dict[str, float]:
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
            action: self.policy_weights[action] * state_feature
            for action in self.policy_weights
        }

        # Softmax to get probabilities
        max_logit = max(logits.values())
        exp_logits = {a: np.exp(l - max_logit) for a, l in logits.items()}
        total = sum(exp_logits.values())
        probs = None

        return probs

    def xǁPPOǁ_get_action_probs__mutmut_19(self, state: Any) -> Dict[str, float]:
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
            action: self.policy_weights[action] * state_feature
            for action in self.policy_weights
        }

        # Softmax to get probabilities
        max_logit = max(logits.values())
        exp_logits = {a: np.exp(l - max_logit) for a, l in logits.items()}
        total = sum(exp_logits.values())
        probs = {a: e * total for a, e in exp_logits.items()}

        return probs
    
    xǁPPOǁ_get_action_probs__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPPOǁ_get_action_probs__mutmut_1': xǁPPOǁ_get_action_probs__mutmut_1, 
        'xǁPPOǁ_get_action_probs__mutmut_2': xǁPPOǁ_get_action_probs__mutmut_2, 
        'xǁPPOǁ_get_action_probs__mutmut_3': xǁPPOǁ_get_action_probs__mutmut_3, 
        'xǁPPOǁ_get_action_probs__mutmut_4': xǁPPOǁ_get_action_probs__mutmut_4, 
        'xǁPPOǁ_get_action_probs__mutmut_5': xǁPPOǁ_get_action_probs__mutmut_5, 
        'xǁPPOǁ_get_action_probs__mutmut_6': xǁPPOǁ_get_action_probs__mutmut_6, 
        'xǁPPOǁ_get_action_probs__mutmut_7': xǁPPOǁ_get_action_probs__mutmut_7, 
        'xǁPPOǁ_get_action_probs__mutmut_8': xǁPPOǁ_get_action_probs__mutmut_8, 
        'xǁPPOǁ_get_action_probs__mutmut_9': xǁPPOǁ_get_action_probs__mutmut_9, 
        'xǁPPOǁ_get_action_probs__mutmut_10': xǁPPOǁ_get_action_probs__mutmut_10, 
        'xǁPPOǁ_get_action_probs__mutmut_11': xǁPPOǁ_get_action_probs__mutmut_11, 
        'xǁPPOǁ_get_action_probs__mutmut_12': xǁPPOǁ_get_action_probs__mutmut_12, 
        'xǁPPOǁ_get_action_probs__mutmut_13': xǁPPOǁ_get_action_probs__mutmut_13, 
        'xǁPPOǁ_get_action_probs__mutmut_14': xǁPPOǁ_get_action_probs__mutmut_14, 
        'xǁPPOǁ_get_action_probs__mutmut_15': xǁPPOǁ_get_action_probs__mutmut_15, 
        'xǁPPOǁ_get_action_probs__mutmut_16': xǁPPOǁ_get_action_probs__mutmut_16, 
        'xǁPPOǁ_get_action_probs__mutmut_17': xǁPPOǁ_get_action_probs__mutmut_17, 
        'xǁPPOǁ_get_action_probs__mutmut_18': xǁPPOǁ_get_action_probs__mutmut_18, 
        'xǁPPOǁ_get_action_probs__mutmut_19': xǁPPOǁ_get_action_probs__mutmut_19
    }
    
    def _get_action_probs(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPPOǁ_get_action_probs__mutmut_orig"), object.__getattribute__(self, "xǁPPOǁ_get_action_probs__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _get_action_probs.__signature__ = _mutmut_signature(xǁPPOǁ_get_action_probs__mutmut_orig)
    xǁPPOǁ_get_action_probs__mutmut_orig.__name__ = 'xǁPPOǁ_get_action_probs'

    def xǁPPOǁ_get_value__mutmut_orig(self, state: Any) -> float:
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

    def xǁPPOǁ_get_value__mutmut_1(self, state: Any) -> float:
        """
        Get state value from critic network.

        Args:
            state: State to evaluate

        Returns:
            State value
        """
        if state in self.value_weights:
            self.value_weights[state] = 0.0

        return self.value_weights[state]

    def xǁPPOǁ_get_value__mutmut_2(self, state: Any) -> float:
        """
        Get state value from critic network.

        Args:
            state: State to evaluate

        Returns:
            State value
        """
        if state not in self.value_weights:
            self.value_weights[state] = None

        return self.value_weights[state]

    def xǁPPOǁ_get_value__mutmut_3(self, state: Any) -> float:
        """
        Get state value from critic network.

        Args:
            state: State to evaluate

        Returns:
            State value
        """
        if state not in self.value_weights:
            self.value_weights[state] = 1.0

        return self.value_weights[state]
    
    xǁPPOǁ_get_value__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPPOǁ_get_value__mutmut_1': xǁPPOǁ_get_value__mutmut_1, 
        'xǁPPOǁ_get_value__mutmut_2': xǁPPOǁ_get_value__mutmut_2, 
        'xǁPPOǁ_get_value__mutmut_3': xǁPPOǁ_get_value__mutmut_3
    }
    
    def _get_value(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPPOǁ_get_value__mutmut_orig"), object.__getattribute__(self, "xǁPPOǁ_get_value__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _get_value.__signature__ = _mutmut_signature(xǁPPOǁ_get_value__mutmut_orig)
    xǁPPOǁ_get_value__mutmut_orig.__name__ = 'xǁPPOǁ_get_value'

    def xǁPPOǁselect_action__mutmut_orig(self, state: Any) -> Any:
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

    def xǁPPOǁselect_action__mutmut_1(self, state: Any) -> Any:
        """
        Sample action from policy.

        Args:
            state: Current state

        Returns:
            Sampled action
        """
        probs = None
        actions = list(probs.keys())
        probabilities = list(probs.values())

        return np.random.choice(actions, p=probabilities)

    def xǁPPOǁselect_action__mutmut_2(self, state: Any) -> Any:
        """
        Sample action from policy.

        Args:
            state: Current state

        Returns:
            Sampled action
        """
        probs = self._get_action_probs(None)
        actions = list(probs.keys())
        probabilities = list(probs.values())

        return np.random.choice(actions, p=probabilities)

    def xǁPPOǁselect_action__mutmut_3(self, state: Any) -> Any:
        """
        Sample action from policy.

        Args:
            state: Current state

        Returns:
            Sampled action
        """
        probs = self._get_action_probs(state)
        actions = None
        probabilities = list(probs.values())

        return np.random.choice(actions, p=probabilities)

    def xǁPPOǁselect_action__mutmut_4(self, state: Any) -> Any:
        """
        Sample action from policy.

        Args:
            state: Current state

        Returns:
            Sampled action
        """
        probs = self._get_action_probs(state)
        actions = list(None)
        probabilities = list(probs.values())

        return np.random.choice(actions, p=probabilities)

    def xǁPPOǁselect_action__mutmut_5(self, state: Any) -> Any:
        """
        Sample action from policy.

        Args:
            state: Current state

        Returns:
            Sampled action
        """
        probs = self._get_action_probs(state)
        actions = list(probs.keys())
        probabilities = None

        return np.random.choice(actions, p=probabilities)

    def xǁPPOǁselect_action__mutmut_6(self, state: Any) -> Any:
        """
        Sample action from policy.

        Args:
            state: Current state

        Returns:
            Sampled action
        """
        probs = self._get_action_probs(state)
        actions = list(probs.keys())
        probabilities = list(None)

        return np.random.choice(actions, p=probabilities)

    def xǁPPOǁselect_action__mutmut_7(self, state: Any) -> Any:
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

        return np.random.choice(None, p=probabilities)

    def xǁPPOǁselect_action__mutmut_8(self, state: Any) -> Any:
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

        return np.random.choice(actions, p=None)

    def xǁPPOǁselect_action__mutmut_9(self, state: Any) -> Any:
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

        return np.random.choice(p=probabilities)

    def xǁPPOǁselect_action__mutmut_10(self, state: Any) -> Any:
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

        return np.random.choice(actions, )
    
    xǁPPOǁselect_action__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPPOǁselect_action__mutmut_1': xǁPPOǁselect_action__mutmut_1, 
        'xǁPPOǁselect_action__mutmut_2': xǁPPOǁselect_action__mutmut_2, 
        'xǁPPOǁselect_action__mutmut_3': xǁPPOǁselect_action__mutmut_3, 
        'xǁPPOǁselect_action__mutmut_4': xǁPPOǁselect_action__mutmut_4, 
        'xǁPPOǁselect_action__mutmut_5': xǁPPOǁselect_action__mutmut_5, 
        'xǁPPOǁselect_action__mutmut_6': xǁPPOǁselect_action__mutmut_6, 
        'xǁPPOǁselect_action__mutmut_7': xǁPPOǁselect_action__mutmut_7, 
        'xǁPPOǁselect_action__mutmut_8': xǁPPOǁselect_action__mutmut_8, 
        'xǁPPOǁselect_action__mutmut_9': xǁPPOǁselect_action__mutmut_9, 
        'xǁPPOǁselect_action__mutmut_10': xǁPPOǁselect_action__mutmut_10
    }
    
    def select_action(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPPOǁselect_action__mutmut_orig"), object.__getattribute__(self, "xǁPPOǁselect_action__mutmut_mutants"), args, kwargs, self)
        return result 
    
    select_action.__signature__ = _mutmut_signature(xǁPPOǁselect_action__mutmut_orig)
    xǁPPOǁselect_action__mutmut_orig.__name__ = 'xǁPPOǁselect_action'

    def xǁPPOǁupdate__mutmut_orig(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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

    def xǁPPOǁupdate__mutmut_1(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
            None
        )

        # Update when episode ends
        if done:
            self._update_policy()
            self.trajectory.clear()

    def xǁPPOǁupdate__mutmut_2(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
                "XXstateXX": state,
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

    def xǁPPOǁupdate__mutmut_3(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
                "STATE": state,
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

    def xǁPPOǁupdate__mutmut_4(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
                "XXactionXX": action,
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

    def xǁPPOǁupdate__mutmut_5(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
                "ACTION": action,
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

    def xǁPPOǁupdate__mutmut_6(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
                "XXrewardXX": reward,
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

    def xǁPPOǁupdate__mutmut_7(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
                "REWARD": reward,
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

    def xǁPPOǁupdate__mutmut_8(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
                "XXnext_stateXX": next_state,
                "done": done,
                "value": self._get_value(state),
                "action_prob": self._get_action_probs(state)[action],
            }
        )

        # Update when episode ends
        if done:
            self._update_policy()
            self.trajectory.clear()

    def xǁPPOǁupdate__mutmut_9(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
                "NEXT_STATE": next_state,
                "done": done,
                "value": self._get_value(state),
                "action_prob": self._get_action_probs(state)[action],
            }
        )

        # Update when episode ends
        if done:
            self._update_policy()
            self.trajectory.clear()

    def xǁPPOǁupdate__mutmut_10(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
                "XXdoneXX": done,
                "value": self._get_value(state),
                "action_prob": self._get_action_probs(state)[action],
            }
        )

        # Update when episode ends
        if done:
            self._update_policy()
            self.trajectory.clear()

    def xǁPPOǁupdate__mutmut_11(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
                "DONE": done,
                "value": self._get_value(state),
                "action_prob": self._get_action_probs(state)[action],
            }
        )

        # Update when episode ends
        if done:
            self._update_policy()
            self.trajectory.clear()

    def xǁPPOǁupdate__mutmut_12(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
                "XXvalueXX": self._get_value(state),
                "action_prob": self._get_action_probs(state)[action],
            }
        )

        # Update when episode ends
        if done:
            self._update_policy()
            self.trajectory.clear()

    def xǁPPOǁupdate__mutmut_13(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
                "VALUE": self._get_value(state),
                "action_prob": self._get_action_probs(state)[action],
            }
        )

        # Update when episode ends
        if done:
            self._update_policy()
            self.trajectory.clear()

    def xǁPPOǁupdate__mutmut_14(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
                "value": self._get_value(None),
                "action_prob": self._get_action_probs(state)[action],
            }
        )

        # Update when episode ends
        if done:
            self._update_policy()
            self.trajectory.clear()

    def xǁPPOǁupdate__mutmut_15(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
                "XXaction_probXX": self._get_action_probs(state)[action],
            }
        )

        # Update when episode ends
        if done:
            self._update_policy()
            self.trajectory.clear()

    def xǁPPOǁupdate__mutmut_16(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
                "ACTION_PROB": self._get_action_probs(state)[action],
            }
        )

        # Update when episode ends
        if done:
            self._update_policy()
            self.trajectory.clear()

    def xǁPPOǁupdate__mutmut_17(
        self, state: Any, action: Any, reward: float, next_state: Any, done: bool
    ):
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
                "action_prob": self._get_action_probs(None)[action],
            }
        )

        # Update when episode ends
        if done:
            self._update_policy()
            self.trajectory.clear()
    
    xǁPPOǁupdate__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPPOǁupdate__mutmut_1': xǁPPOǁupdate__mutmut_1, 
        'xǁPPOǁupdate__mutmut_2': xǁPPOǁupdate__mutmut_2, 
        'xǁPPOǁupdate__mutmut_3': xǁPPOǁupdate__mutmut_3, 
        'xǁPPOǁupdate__mutmut_4': xǁPPOǁupdate__mutmut_4, 
        'xǁPPOǁupdate__mutmut_5': xǁPPOǁupdate__mutmut_5, 
        'xǁPPOǁupdate__mutmut_6': xǁPPOǁupdate__mutmut_6, 
        'xǁPPOǁupdate__mutmut_7': xǁPPOǁupdate__mutmut_7, 
        'xǁPPOǁupdate__mutmut_8': xǁPPOǁupdate__mutmut_8, 
        'xǁPPOǁupdate__mutmut_9': xǁPPOǁupdate__mutmut_9, 
        'xǁPPOǁupdate__mutmut_10': xǁPPOǁupdate__mutmut_10, 
        'xǁPPOǁupdate__mutmut_11': xǁPPOǁupdate__mutmut_11, 
        'xǁPPOǁupdate__mutmut_12': xǁPPOǁupdate__mutmut_12, 
        'xǁPPOǁupdate__mutmut_13': xǁPPOǁupdate__mutmut_13, 
        'xǁPPOǁupdate__mutmut_14': xǁPPOǁupdate__mutmut_14, 
        'xǁPPOǁupdate__mutmut_15': xǁPPOǁupdate__mutmut_15, 
        'xǁPPOǁupdate__mutmut_16': xǁPPOǁupdate__mutmut_16, 
        'xǁPPOǁupdate__mutmut_17': xǁPPOǁupdate__mutmut_17
    }
    
    def update(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPPOǁupdate__mutmut_orig"), object.__getattribute__(self, "xǁPPOǁupdate__mutmut_mutants"), args, kwargs, self)
        return result 
    
    update.__signature__ = _mutmut_signature(xǁPPOǁupdate__mutmut_orig)
    xǁPPOǁupdate__mutmut_orig.__name__ = 'xǁPPOǁupdate'

    def xǁPPOǁ_compute_advantages__mutmut_orig(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_1(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = None
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_2(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = None

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_3(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 1.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_4(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(None):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_5(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(None)):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_6(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = None

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_7(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["XXdoneXX"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_8(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["DONE"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_9(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = None
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_10(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] + transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_11(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["XXrewardXX"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_12(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["REWARD"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_13(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["XXvalueXX"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_14(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["VALUE"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_15(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = None
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_16(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = None
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_17(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i - 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_18(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 2]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_19(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["XXvalueXX"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_20(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["VALUE"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_21(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i - 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_22(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 2 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_23(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 <= len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_24(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 1.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_25(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = None
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_26(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value + transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_27(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"] - self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_28(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["XXrewardXX"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_29(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["REWARD"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_30(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor / next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_31(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["XXvalueXX"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_32(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["VALUE"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_33(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = None

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_34(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta - self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_35(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda / gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_36(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor / self.gae_lambda * gae

            advantages.insert(0, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_37(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(None, gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_38(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, None)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_39(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(gae)

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_40(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(0, )

        return advantages

    def xǁPPOǁ_compute_advantages__mutmut_41(self) -> List[float]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).

        Returns:
            List of advantage values
        """
        advantages = []
        gae = 0.0

        # Compute advantages backward from end of trajectory
        for i in reversed(range(len(self.trajectory))):
            transition = self.trajectory[i]

            if transition["done"]:
                delta = transition["reward"] - transition["value"]
                gae = delta
            else:
                next_value = (
                    self.trajectory[i + 1]["value"]
                    if i + 1 < len(self.trajectory)
                    else 0.0
                )
                delta = (
                    transition["reward"]
                    + self.discount_factor * next_value
                    - transition["value"]
                )
                gae = delta + self.discount_factor * self.gae_lambda * gae

            advantages.insert(1, gae)

        return advantages
    
    xǁPPOǁ_compute_advantages__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPPOǁ_compute_advantages__mutmut_1': xǁPPOǁ_compute_advantages__mutmut_1, 
        'xǁPPOǁ_compute_advantages__mutmut_2': xǁPPOǁ_compute_advantages__mutmut_2, 
        'xǁPPOǁ_compute_advantages__mutmut_3': xǁPPOǁ_compute_advantages__mutmut_3, 
        'xǁPPOǁ_compute_advantages__mutmut_4': xǁPPOǁ_compute_advantages__mutmut_4, 
        'xǁPPOǁ_compute_advantages__mutmut_5': xǁPPOǁ_compute_advantages__mutmut_5, 
        'xǁPPOǁ_compute_advantages__mutmut_6': xǁPPOǁ_compute_advantages__mutmut_6, 
        'xǁPPOǁ_compute_advantages__mutmut_7': xǁPPOǁ_compute_advantages__mutmut_7, 
        'xǁPPOǁ_compute_advantages__mutmut_8': xǁPPOǁ_compute_advantages__mutmut_8, 
        'xǁPPOǁ_compute_advantages__mutmut_9': xǁPPOǁ_compute_advantages__mutmut_9, 
        'xǁPPOǁ_compute_advantages__mutmut_10': xǁPPOǁ_compute_advantages__mutmut_10, 
        'xǁPPOǁ_compute_advantages__mutmut_11': xǁPPOǁ_compute_advantages__mutmut_11, 
        'xǁPPOǁ_compute_advantages__mutmut_12': xǁPPOǁ_compute_advantages__mutmut_12, 
        'xǁPPOǁ_compute_advantages__mutmut_13': xǁPPOǁ_compute_advantages__mutmut_13, 
        'xǁPPOǁ_compute_advantages__mutmut_14': xǁPPOǁ_compute_advantages__mutmut_14, 
        'xǁPPOǁ_compute_advantages__mutmut_15': xǁPPOǁ_compute_advantages__mutmut_15, 
        'xǁPPOǁ_compute_advantages__mutmut_16': xǁPPOǁ_compute_advantages__mutmut_16, 
        'xǁPPOǁ_compute_advantages__mutmut_17': xǁPPOǁ_compute_advantages__mutmut_17, 
        'xǁPPOǁ_compute_advantages__mutmut_18': xǁPPOǁ_compute_advantages__mutmut_18, 
        'xǁPPOǁ_compute_advantages__mutmut_19': xǁPPOǁ_compute_advantages__mutmut_19, 
        'xǁPPOǁ_compute_advantages__mutmut_20': xǁPPOǁ_compute_advantages__mutmut_20, 
        'xǁPPOǁ_compute_advantages__mutmut_21': xǁPPOǁ_compute_advantages__mutmut_21, 
        'xǁPPOǁ_compute_advantages__mutmut_22': xǁPPOǁ_compute_advantages__mutmut_22, 
        'xǁPPOǁ_compute_advantages__mutmut_23': xǁPPOǁ_compute_advantages__mutmut_23, 
        'xǁPPOǁ_compute_advantages__mutmut_24': xǁPPOǁ_compute_advantages__mutmut_24, 
        'xǁPPOǁ_compute_advantages__mutmut_25': xǁPPOǁ_compute_advantages__mutmut_25, 
        'xǁPPOǁ_compute_advantages__mutmut_26': xǁPPOǁ_compute_advantages__mutmut_26, 
        'xǁPPOǁ_compute_advantages__mutmut_27': xǁPPOǁ_compute_advantages__mutmut_27, 
        'xǁPPOǁ_compute_advantages__mutmut_28': xǁPPOǁ_compute_advantages__mutmut_28, 
        'xǁPPOǁ_compute_advantages__mutmut_29': xǁPPOǁ_compute_advantages__mutmut_29, 
        'xǁPPOǁ_compute_advantages__mutmut_30': xǁPPOǁ_compute_advantages__mutmut_30, 
        'xǁPPOǁ_compute_advantages__mutmut_31': xǁPPOǁ_compute_advantages__mutmut_31, 
        'xǁPPOǁ_compute_advantages__mutmut_32': xǁPPOǁ_compute_advantages__mutmut_32, 
        'xǁPPOǁ_compute_advantages__mutmut_33': xǁPPOǁ_compute_advantages__mutmut_33, 
        'xǁPPOǁ_compute_advantages__mutmut_34': xǁPPOǁ_compute_advantages__mutmut_34, 
        'xǁPPOǁ_compute_advantages__mutmut_35': xǁPPOǁ_compute_advantages__mutmut_35, 
        'xǁPPOǁ_compute_advantages__mutmut_36': xǁPPOǁ_compute_advantages__mutmut_36, 
        'xǁPPOǁ_compute_advantages__mutmut_37': xǁPPOǁ_compute_advantages__mutmut_37, 
        'xǁPPOǁ_compute_advantages__mutmut_38': xǁPPOǁ_compute_advantages__mutmut_38, 
        'xǁPPOǁ_compute_advantages__mutmut_39': xǁPPOǁ_compute_advantages__mutmut_39, 
        'xǁPPOǁ_compute_advantages__mutmut_40': xǁPPOǁ_compute_advantages__mutmut_40, 
        'xǁPPOǁ_compute_advantages__mutmut_41': xǁPPOǁ_compute_advantages__mutmut_41
    }
    
    def _compute_advantages(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPPOǁ_compute_advantages__mutmut_orig"), object.__getattribute__(self, "xǁPPOǁ_compute_advantages__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _compute_advantages.__signature__ = _mutmut_signature(xǁPPOǁ_compute_advantages__mutmut_orig)
    xǁPPOǁ_compute_advantages__mutmut_orig.__name__ = 'xǁPPOǁ_compute_advantages'

    def xǁPPOǁ_update_policy__mutmut_orig(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_1(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) <= 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_2(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 3:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_3(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = None
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_4(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = None

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_5(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] - adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_6(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["XXvalueXX"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_7(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["VALUE"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_8(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(None, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_9(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, None)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_10(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_11(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, )]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_12(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = None
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_13(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(None)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_14(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = None
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_15(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) - 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_16(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(None) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_17(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1.00000001
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_18(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = None

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_19(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) * adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_20(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv + adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_21(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(None):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_22(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = None
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_23(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 1.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_24(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = None

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_25(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 1.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_26(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(None, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_27(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, None, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_28(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, None):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_29(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_30(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_31(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, ):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_32(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = None
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_33(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(None)
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_34(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["XXstateXX"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_35(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["STATE"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_36(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss = (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_37(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss -= (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_38(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) * 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_39(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret + current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_40(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 3
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_41(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] = self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_42(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] -= self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_43(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["XXstateXX"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_44(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["STATE"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_45(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate / (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_46(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret + current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_47(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = None
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_48(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(None)[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_49(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["XXstateXX"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_50(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["STATE"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_51(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["XXactionXX"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_52(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["ACTION"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_53(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = None

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_54(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["XXaction_probXX"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_55(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["ACTION_PROB"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_56(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = None

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_57(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob * (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_58(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob - 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_59(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1.0000000001)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_60(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = None
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_61(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(None, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_62(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, None, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_63(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, None)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_64(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_65(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_66(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, )
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_67(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 + self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_68(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 2 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_69(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 - self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_70(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 2 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_71(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss = -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_72(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss -= -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_73(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += +min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_74(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(None, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_75(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, None)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_76(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_77(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, )

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_78(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio / advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_79(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio / advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_80(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = None
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_81(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) * 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_82(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(None) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_83(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) / 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_84(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(None) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_85(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(None)) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_86(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["XXstateXX"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_87(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["STATE"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_88(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1001) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_89(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1001.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_90(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = None
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_91(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage / state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_92(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] = (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_93(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] -= (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_94(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["XXactionXX"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_95(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["ACTION"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_96(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate / gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_97(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(None)
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_98(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss * len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_99(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(None)

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_100(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss * len(self.trajectory))

        self.policy_updates += 1

    def xǁPPOǁ_update_policy__mutmut_101(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates = 1

    def xǁPPOǁ_update_policy__mutmut_102(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates -= 1

    def xǁPPOǁ_update_policy__mutmut_103(self):
        """Update policy and value networks using PPO objective."""
        if len(self.trajectory) < 2:
            return

        # Compute advantages
        advantages = self._compute_advantages()
        returns = [t["value"] + adv for t, adv in zip(self.trajectory, advantages)]

        # Normalize advantages
        adv_mean = np.mean(advantages)
        adv_std = np.std(advantages) + 1e-8
        advantages = [(adv - adv_mean) / adv_std for adv in advantages]

        # Multiple epochs of updates
        for _ in range(self.epochs_per_update):
            policy_loss = 0.0
            value_loss = 0.0

            for transition, advantage, ret in zip(self.trajectory, advantages, returns):
                # Update critic (value network)
                current_value = self._get_value(transition["state"])
                value_loss += (ret - current_value) ** 2
                self.value_weights[transition["state"]] += self.learning_rate * (
                    ret - current_value
                )

                # Update actor (policy network)
                current_prob = self._get_action_probs(transition["state"])[
                    transition["action"]
                ]
                old_prob = transition["action_prob"]

                # Probability ratio
                ratio = current_prob / (old_prob + 1e-10)

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss += -min(ratio * advantage, clipped_ratio * advantage)

                # Gradient update (simplified)
                state_feature = float(hash(str(transition["state"])) % 1000) / 1000.0
                gradient = advantage * state_feature
                self.policy_weights[transition["action"]] += (
                    self.learning_rate * gradient
                )

            self.value_loss_history.append(value_loss / len(self.trajectory))
            self.policy_loss_history.append(policy_loss / len(self.trajectory))

        self.policy_updates += 2
    
    xǁPPOǁ_update_policy__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPPOǁ_update_policy__mutmut_1': xǁPPOǁ_update_policy__mutmut_1, 
        'xǁPPOǁ_update_policy__mutmut_2': xǁPPOǁ_update_policy__mutmut_2, 
        'xǁPPOǁ_update_policy__mutmut_3': xǁPPOǁ_update_policy__mutmut_3, 
        'xǁPPOǁ_update_policy__mutmut_4': xǁPPOǁ_update_policy__mutmut_4, 
        'xǁPPOǁ_update_policy__mutmut_5': xǁPPOǁ_update_policy__mutmut_5, 
        'xǁPPOǁ_update_policy__mutmut_6': xǁPPOǁ_update_policy__mutmut_6, 
        'xǁPPOǁ_update_policy__mutmut_7': xǁPPOǁ_update_policy__mutmut_7, 
        'xǁPPOǁ_update_policy__mutmut_8': xǁPPOǁ_update_policy__mutmut_8, 
        'xǁPPOǁ_update_policy__mutmut_9': xǁPPOǁ_update_policy__mutmut_9, 
        'xǁPPOǁ_update_policy__mutmut_10': xǁPPOǁ_update_policy__mutmut_10, 
        'xǁPPOǁ_update_policy__mutmut_11': xǁPPOǁ_update_policy__mutmut_11, 
        'xǁPPOǁ_update_policy__mutmut_12': xǁPPOǁ_update_policy__mutmut_12, 
        'xǁPPOǁ_update_policy__mutmut_13': xǁPPOǁ_update_policy__mutmut_13, 
        'xǁPPOǁ_update_policy__mutmut_14': xǁPPOǁ_update_policy__mutmut_14, 
        'xǁPPOǁ_update_policy__mutmut_15': xǁPPOǁ_update_policy__mutmut_15, 
        'xǁPPOǁ_update_policy__mutmut_16': xǁPPOǁ_update_policy__mutmut_16, 
        'xǁPPOǁ_update_policy__mutmut_17': xǁPPOǁ_update_policy__mutmut_17, 
        'xǁPPOǁ_update_policy__mutmut_18': xǁPPOǁ_update_policy__mutmut_18, 
        'xǁPPOǁ_update_policy__mutmut_19': xǁPPOǁ_update_policy__mutmut_19, 
        'xǁPPOǁ_update_policy__mutmut_20': xǁPPOǁ_update_policy__mutmut_20, 
        'xǁPPOǁ_update_policy__mutmut_21': xǁPPOǁ_update_policy__mutmut_21, 
        'xǁPPOǁ_update_policy__mutmut_22': xǁPPOǁ_update_policy__mutmut_22, 
        'xǁPPOǁ_update_policy__mutmut_23': xǁPPOǁ_update_policy__mutmut_23, 
        'xǁPPOǁ_update_policy__mutmut_24': xǁPPOǁ_update_policy__mutmut_24, 
        'xǁPPOǁ_update_policy__mutmut_25': xǁPPOǁ_update_policy__mutmut_25, 
        'xǁPPOǁ_update_policy__mutmut_26': xǁPPOǁ_update_policy__mutmut_26, 
        'xǁPPOǁ_update_policy__mutmut_27': xǁPPOǁ_update_policy__mutmut_27, 
        'xǁPPOǁ_update_policy__mutmut_28': xǁPPOǁ_update_policy__mutmut_28, 
        'xǁPPOǁ_update_policy__mutmut_29': xǁPPOǁ_update_policy__mutmut_29, 
        'xǁPPOǁ_update_policy__mutmut_30': xǁPPOǁ_update_policy__mutmut_30, 
        'xǁPPOǁ_update_policy__mutmut_31': xǁPPOǁ_update_policy__mutmut_31, 
        'xǁPPOǁ_update_policy__mutmut_32': xǁPPOǁ_update_policy__mutmut_32, 
        'xǁPPOǁ_update_policy__mutmut_33': xǁPPOǁ_update_policy__mutmut_33, 
        'xǁPPOǁ_update_policy__mutmut_34': xǁPPOǁ_update_policy__mutmut_34, 
        'xǁPPOǁ_update_policy__mutmut_35': xǁPPOǁ_update_policy__mutmut_35, 
        'xǁPPOǁ_update_policy__mutmut_36': xǁPPOǁ_update_policy__mutmut_36, 
        'xǁPPOǁ_update_policy__mutmut_37': xǁPPOǁ_update_policy__mutmut_37, 
        'xǁPPOǁ_update_policy__mutmut_38': xǁPPOǁ_update_policy__mutmut_38, 
        'xǁPPOǁ_update_policy__mutmut_39': xǁPPOǁ_update_policy__mutmut_39, 
        'xǁPPOǁ_update_policy__mutmut_40': xǁPPOǁ_update_policy__mutmut_40, 
        'xǁPPOǁ_update_policy__mutmut_41': xǁPPOǁ_update_policy__mutmut_41, 
        'xǁPPOǁ_update_policy__mutmut_42': xǁPPOǁ_update_policy__mutmut_42, 
        'xǁPPOǁ_update_policy__mutmut_43': xǁPPOǁ_update_policy__mutmut_43, 
        'xǁPPOǁ_update_policy__mutmut_44': xǁPPOǁ_update_policy__mutmut_44, 
        'xǁPPOǁ_update_policy__mutmut_45': xǁPPOǁ_update_policy__mutmut_45, 
        'xǁPPOǁ_update_policy__mutmut_46': xǁPPOǁ_update_policy__mutmut_46, 
        'xǁPPOǁ_update_policy__mutmut_47': xǁPPOǁ_update_policy__mutmut_47, 
        'xǁPPOǁ_update_policy__mutmut_48': xǁPPOǁ_update_policy__mutmut_48, 
        'xǁPPOǁ_update_policy__mutmut_49': xǁPPOǁ_update_policy__mutmut_49, 
        'xǁPPOǁ_update_policy__mutmut_50': xǁPPOǁ_update_policy__mutmut_50, 
        'xǁPPOǁ_update_policy__mutmut_51': xǁPPOǁ_update_policy__mutmut_51, 
        'xǁPPOǁ_update_policy__mutmut_52': xǁPPOǁ_update_policy__mutmut_52, 
        'xǁPPOǁ_update_policy__mutmut_53': xǁPPOǁ_update_policy__mutmut_53, 
        'xǁPPOǁ_update_policy__mutmut_54': xǁPPOǁ_update_policy__mutmut_54, 
        'xǁPPOǁ_update_policy__mutmut_55': xǁPPOǁ_update_policy__mutmut_55, 
        'xǁPPOǁ_update_policy__mutmut_56': xǁPPOǁ_update_policy__mutmut_56, 
        'xǁPPOǁ_update_policy__mutmut_57': xǁPPOǁ_update_policy__mutmut_57, 
        'xǁPPOǁ_update_policy__mutmut_58': xǁPPOǁ_update_policy__mutmut_58, 
        'xǁPPOǁ_update_policy__mutmut_59': xǁPPOǁ_update_policy__mutmut_59, 
        'xǁPPOǁ_update_policy__mutmut_60': xǁPPOǁ_update_policy__mutmut_60, 
        'xǁPPOǁ_update_policy__mutmut_61': xǁPPOǁ_update_policy__mutmut_61, 
        'xǁPPOǁ_update_policy__mutmut_62': xǁPPOǁ_update_policy__mutmut_62, 
        'xǁPPOǁ_update_policy__mutmut_63': xǁPPOǁ_update_policy__mutmut_63, 
        'xǁPPOǁ_update_policy__mutmut_64': xǁPPOǁ_update_policy__mutmut_64, 
        'xǁPPOǁ_update_policy__mutmut_65': xǁPPOǁ_update_policy__mutmut_65, 
        'xǁPPOǁ_update_policy__mutmut_66': xǁPPOǁ_update_policy__mutmut_66, 
        'xǁPPOǁ_update_policy__mutmut_67': xǁPPOǁ_update_policy__mutmut_67, 
        'xǁPPOǁ_update_policy__mutmut_68': xǁPPOǁ_update_policy__mutmut_68, 
        'xǁPPOǁ_update_policy__mutmut_69': xǁPPOǁ_update_policy__mutmut_69, 
        'xǁPPOǁ_update_policy__mutmut_70': xǁPPOǁ_update_policy__mutmut_70, 
        'xǁPPOǁ_update_policy__mutmut_71': xǁPPOǁ_update_policy__mutmut_71, 
        'xǁPPOǁ_update_policy__mutmut_72': xǁPPOǁ_update_policy__mutmut_72, 
        'xǁPPOǁ_update_policy__mutmut_73': xǁPPOǁ_update_policy__mutmut_73, 
        'xǁPPOǁ_update_policy__mutmut_74': xǁPPOǁ_update_policy__mutmut_74, 
        'xǁPPOǁ_update_policy__mutmut_75': xǁPPOǁ_update_policy__mutmut_75, 
        'xǁPPOǁ_update_policy__mutmut_76': xǁPPOǁ_update_policy__mutmut_76, 
        'xǁPPOǁ_update_policy__mutmut_77': xǁPPOǁ_update_policy__mutmut_77, 
        'xǁPPOǁ_update_policy__mutmut_78': xǁPPOǁ_update_policy__mutmut_78, 
        'xǁPPOǁ_update_policy__mutmut_79': xǁPPOǁ_update_policy__mutmut_79, 
        'xǁPPOǁ_update_policy__mutmut_80': xǁPPOǁ_update_policy__mutmut_80, 
        'xǁPPOǁ_update_policy__mutmut_81': xǁPPOǁ_update_policy__mutmut_81, 
        'xǁPPOǁ_update_policy__mutmut_82': xǁPPOǁ_update_policy__mutmut_82, 
        'xǁPPOǁ_update_policy__mutmut_83': xǁPPOǁ_update_policy__mutmut_83, 
        'xǁPPOǁ_update_policy__mutmut_84': xǁPPOǁ_update_policy__mutmut_84, 
        'xǁPPOǁ_update_policy__mutmut_85': xǁPPOǁ_update_policy__mutmut_85, 
        'xǁPPOǁ_update_policy__mutmut_86': xǁPPOǁ_update_policy__mutmut_86, 
        'xǁPPOǁ_update_policy__mutmut_87': xǁPPOǁ_update_policy__mutmut_87, 
        'xǁPPOǁ_update_policy__mutmut_88': xǁPPOǁ_update_policy__mutmut_88, 
        'xǁPPOǁ_update_policy__mutmut_89': xǁPPOǁ_update_policy__mutmut_89, 
        'xǁPPOǁ_update_policy__mutmut_90': xǁPPOǁ_update_policy__mutmut_90, 
        'xǁPPOǁ_update_policy__mutmut_91': xǁPPOǁ_update_policy__mutmut_91, 
        'xǁPPOǁ_update_policy__mutmut_92': xǁPPOǁ_update_policy__mutmut_92, 
        'xǁPPOǁ_update_policy__mutmut_93': xǁPPOǁ_update_policy__mutmut_93, 
        'xǁPPOǁ_update_policy__mutmut_94': xǁPPOǁ_update_policy__mutmut_94, 
        'xǁPPOǁ_update_policy__mutmut_95': xǁPPOǁ_update_policy__mutmut_95, 
        'xǁPPOǁ_update_policy__mutmut_96': xǁPPOǁ_update_policy__mutmut_96, 
        'xǁPPOǁ_update_policy__mutmut_97': xǁPPOǁ_update_policy__mutmut_97, 
        'xǁPPOǁ_update_policy__mutmut_98': xǁPPOǁ_update_policy__mutmut_98, 
        'xǁPPOǁ_update_policy__mutmut_99': xǁPPOǁ_update_policy__mutmut_99, 
        'xǁPPOǁ_update_policy__mutmut_100': xǁPPOǁ_update_policy__mutmut_100, 
        'xǁPPOǁ_update_policy__mutmut_101': xǁPPOǁ_update_policy__mutmut_101, 
        'xǁPPOǁ_update_policy__mutmut_102': xǁPPOǁ_update_policy__mutmut_102, 
        'xǁPPOǁ_update_policy__mutmut_103': xǁPPOǁ_update_policy__mutmut_103
    }
    
    def _update_policy(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPPOǁ_update_policy__mutmut_orig"), object.__getattribute__(self, "xǁPPOǁ_update_policy__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _update_policy.__signature__ = _mutmut_signature(xǁPPOǁ_update_policy__mutmut_orig)
    xǁPPOǁ_update_policy__mutmut_orig.__name__ = 'xǁPPOǁ_update_policy'

    def xǁPPOǁget_policy__mutmut_orig(self) -> Dict[Any, Any]:
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

    def xǁPPOǁget_policy__mutmut_1(self) -> Dict[Any, Any]:
        """
        Get current policy.

        Returns:
            Policy representation
        """
        return {
            "XXtypeXX": "PPO",
            "policy_weights": dict(self.policy_weights),
            "value_weights": dict(self.value_weights),
        }

    def xǁPPOǁget_policy__mutmut_2(self) -> Dict[Any, Any]:
        """
        Get current policy.

        Returns:
            Policy representation
        """
        return {
            "TYPE": "PPO",
            "policy_weights": dict(self.policy_weights),
            "value_weights": dict(self.value_weights),
        }

    def xǁPPOǁget_policy__mutmut_3(self) -> Dict[Any, Any]:
        """
        Get current policy.

        Returns:
            Policy representation
        """
        return {
            "type": "XXPPOXX",
            "policy_weights": dict(self.policy_weights),
            "value_weights": dict(self.value_weights),
        }

    def xǁPPOǁget_policy__mutmut_4(self) -> Dict[Any, Any]:
        """
        Get current policy.

        Returns:
            Policy representation
        """
        return {
            "type": "ppo",
            "policy_weights": dict(self.policy_weights),
            "value_weights": dict(self.value_weights),
        }

    def xǁPPOǁget_policy__mutmut_5(self) -> Dict[Any, Any]:
        """
        Get current policy.

        Returns:
            Policy representation
        """
        return {
            "type": "PPO",
            "XXpolicy_weightsXX": dict(self.policy_weights),
            "value_weights": dict(self.value_weights),
        }

    def xǁPPOǁget_policy__mutmut_6(self) -> Dict[Any, Any]:
        """
        Get current policy.

        Returns:
            Policy representation
        """
        return {
            "type": "PPO",
            "POLICY_WEIGHTS": dict(self.policy_weights),
            "value_weights": dict(self.value_weights),
        }

    def xǁPPOǁget_policy__mutmut_7(self) -> Dict[Any, Any]:
        """
        Get current policy.

        Returns:
            Policy representation
        """
        return {
            "type": "PPO",
            "policy_weights": dict(None),
            "value_weights": dict(self.value_weights),
        }

    def xǁPPOǁget_policy__mutmut_8(self) -> Dict[Any, Any]:
        """
        Get current policy.

        Returns:
            Policy representation
        """
        return {
            "type": "PPO",
            "policy_weights": dict(self.policy_weights),
            "XXvalue_weightsXX": dict(self.value_weights),
        }

    def xǁPPOǁget_policy__mutmut_9(self) -> Dict[Any, Any]:
        """
        Get current policy.

        Returns:
            Policy representation
        """
        return {
            "type": "PPO",
            "policy_weights": dict(self.policy_weights),
            "VALUE_WEIGHTS": dict(self.value_weights),
        }

    def xǁPPOǁget_policy__mutmut_10(self) -> Dict[Any, Any]:
        """
        Get current policy.

        Returns:
            Policy representation
        """
        return {
            "type": "PPO",
            "policy_weights": dict(self.policy_weights),
            "value_weights": dict(None),
        }
    
    xǁPPOǁget_policy__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPPOǁget_policy__mutmut_1': xǁPPOǁget_policy__mutmut_1, 
        'xǁPPOǁget_policy__mutmut_2': xǁPPOǁget_policy__mutmut_2, 
        'xǁPPOǁget_policy__mutmut_3': xǁPPOǁget_policy__mutmut_3, 
        'xǁPPOǁget_policy__mutmut_4': xǁPPOǁget_policy__mutmut_4, 
        'xǁPPOǁget_policy__mutmut_5': xǁPPOǁget_policy__mutmut_5, 
        'xǁPPOǁget_policy__mutmut_6': xǁPPOǁget_policy__mutmut_6, 
        'xǁPPOǁget_policy__mutmut_7': xǁPPOǁget_policy__mutmut_7, 
        'xǁPPOǁget_policy__mutmut_8': xǁPPOǁget_policy__mutmut_8, 
        'xǁPPOǁget_policy__mutmut_9': xǁPPOǁget_policy__mutmut_9, 
        'xǁPPOǁget_policy__mutmut_10': xǁPPOǁget_policy__mutmut_10
    }
    
    def get_policy(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPPOǁget_policy__mutmut_orig"), object.__getattribute__(self, "xǁPPOǁget_policy__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_policy.__signature__ = _mutmut_signature(xǁPPOǁget_policy__mutmut_orig)
    xǁPPOǁget_policy__mutmut_orig.__name__ = 'xǁPPOǁget_policy'
