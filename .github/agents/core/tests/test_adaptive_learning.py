"""
Tests for Adaptive Learning Engine (Phase 8.7 Universal Intelligence / Phase 8.8, evolved from earlier Phase 8.3 work).

Comprehensive test suite covering:
- Q-learning functionality
- Reward shaping
- Experience replay
- Integration tests
- Performance tests
"""
import pytest
from unittest.mock import MagicMock, patch

import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adaptive_learning import (
    AdaptiveLearningEngine,
    RewardShaper,
    ExperienceReplayBuffer,
    Experience,
    LearningState,
)


class TestExperienceReplayBuffer:
    """Tests for ExperienceReplayBuffer."""

    def test_create_buffer(self):
        """Test creating empty buffer."""
        buffer = ExperienceReplayBuffer(capacity=1000)
        assert len(buffer) == 0

    def test_add_experience(self):
        """Test adding experiences."""
        buffer = ExperienceReplayBuffer(capacity=100)
        exp = Experience(
            state="s1",
            action="a1",
            reward=1.0,
            next_state="s2",
        )
        buffer.add(exp)
        assert len(buffer) == 1

    def test_capacity_limit(self):
        """Test buffer respects capacity."""
        buffer = ExperienceReplayBuffer(capacity=10)
        for i in range(20):
            exp = Experience(
                state=f"s{i}",
                action="a",
                reward=float(i),
                next_state=f"s{i+1}",
            )
            buffer.add(exp)
        assert len(buffer) == 10

    def test_sample_empty(self):
        """Test sampling from empty buffer."""
        buffer = ExperienceReplayBuffer()
        experiences, weights = buffer.sample(10)
        assert len(experiences) == 0
        assert len(weights) == 0

    def test_sample_batch(self):
        """Test sampling a batch."""
        buffer = ExperienceReplayBuffer(capacity=100)
        for i in range(50):
            exp = Experience(
                state=f"s{i}",
                action="a",
                reward=float(i),
                next_state=f"s{i+1}",
            )
            buffer.add(exp)
        
        experiences, weights = buffer.sample(10)
        assert len(experiences) == 10
        assert len(weights) == 10
        assert all(0 <= w <= 1 for w in weights)

    def test_clear(self):
        """Test clearing buffer."""
        buffer = ExperienceReplayBuffer(capacity=100)
        for i in range(10):
            buffer.add(Experience(state=f"s{i}", action="a", reward=1.0, next_state="s"))
        buffer.clear()
        assert len(buffer) == 0


class TestRewardShaper:
    """Tests for RewardShaper."""

    def test_create_shaper(self):
        """Test creating reward shaper."""
        shaper = RewardShaper()
        assert shaper.weights['accuracy'] == 0.4
        assert shaper.weights['speed'] == 0.25

    def test_compute_reward(self):
        """Test reward computation."""
        shaper = RewardShaper()
        reward, components = shaper.compute_reward(
            accuracy=0.9,
            speed=0.8,
            confidence=0.7,
            coherence=0.6,
            error_count=0,
        )
        assert reward > 0
        assert 'accuracy' in components
        assert 'speed' in components

    def test_reward_with_errors(self):
        """Test reward with error penalty."""
        shaper = RewardShaper()
        reward_no_error, _ = shaper.compute_reward(0.9, 0.8, 0.7, 0.6, error_count=0)
        reward_with_error, _ = shaper.compute_reward(0.9, 0.8, 0.7, 0.6, error_count=5)
        assert reward_with_error < reward_no_error

    def test_potential_computation(self):
        """Test potential-based shaping."""
        shaper = RewardShaper()
        state = {'accuracy': 0.8, 'coherence': 0.7}
        potential = shaper.compute_potential(state)
        assert 0 <= potential <= 1

    def test_adaptive_weights(self):
        """Test weight adaptation."""
        shaper = RewardShaper(adaptive_weights=True)
        initial_accuracy = shaper.weights['accuracy']
        
        # Simulate declining performance
        shaper.adapt_weights(performance_trend=-0.2)
        assert shaper.weights['accuracy'] >= initial_accuracy

    def test_statistics(self):
        """Test getting statistics."""
        shaper = RewardShaper()
        for _ in range(10):
            shaper.compute_reward(0.8, 0.7, 0.6, 0.5)
        
        stats = shaper.get_statistics()
        assert 'avg_reward' in stats
        assert 'total_samples' in stats
        assert stats['total_samples'] == 10


class TestAdaptiveLearningEngine:
    """Tests for AdaptiveLearningEngine."""

    def test_create_engine(self):
        """Test creating learning engine."""
        engine = AdaptiveLearningEngine()
        assert engine.learning_rate == 0.12
        assert engine.epsilon == 0.1
        assert engine.discount_factor == 0.95

    def test_register_actions(self):
        """Test registering actions."""
        engine = AdaptiveLearningEngine()
        engine.register_actions(['approve', 'reject', 'defer'])
        assert len(engine.actions) == 3

    def test_select_action_no_actions(self):
        """Test action selection with no actions raises error."""
        engine = AdaptiveLearningEngine()
        with pytest.raises(ValueError):
            engine.select_action({'feature': 1.0})

    def test_select_action(self):
        """Test action selection."""
        engine = AdaptiveLearningEngine()
        engine.register_actions(['a1', 'a2', 'a3'])
        action = engine.select_action({'feature': 1.0})
        assert action in ['a1', 'a2', 'a3']

    def test_update_q_value(self):
        """Test Q-value update."""
        engine = AdaptiveLearningEngine()
        engine.register_actions(['a1', 'a2'])
        
        state = {'feature': 1.0}
        td_error = engine.update(
            state=state,
            action='a1',
            reward=1.0,
            next_state={'feature': 2.0},
        )
        
        assert td_error != 0
        assert len(engine.replay_buffer) == 1

    def test_get_q_value(self):
        """Test getting Q-value."""
        engine = AdaptiveLearningEngine()
        engine.register_actions(['a1'])
        
        # Update to create Q-value
        engine.update(
            state={'f': 1},
            action='a1',
            reward=1.0,
            next_state={'f': 2},
        )
        
        state_key = engine._get_state_key({'f': 1})
        q_value = engine.get_q_value(state_key, 'a1')
        assert q_value > 0

    def test_get_max_q_value(self):
        """Test getting max Q-value."""
        engine = AdaptiveLearningEngine()
        engine.register_actions(['a1', 'a2'])
        
        # Unknown state returns 0
        assert engine.get_max_q_value('unknown') == 0.0

    def test_learn_from_replay(self):
        """Test learning from replay buffer."""
        engine = AdaptiveLearningEngine(batch_size=5)
        engine.register_actions(['a1', 'a2'])
        
        # Add experiences
        for i in range(10):
            engine.update(
                state={'f': i},
                action='a1',
                reward=float(i),
                next_state={'f': i + 1},
            )
        
        avg_td = engine.learn_from_replay()
        assert avg_td >= 0

    def test_end_episode(self):
        """Test ending episode."""
        engine = AdaptiveLearningEngine()
        initial_epsilon = engine.epsilon
        
        engine.end_episode(total_reward=10.0)
        
        assert engine.state.episodes == 1
        assert engine.state.total_reward == 10.0
        assert engine.epsilon < initial_epsilon  # Decayed

    def test_epsilon_decay(self):
        """Test epsilon decays over episodes."""
        engine = AdaptiveLearningEngine(epsilon=0.5, epsilon_decay=0.9)
        
        for _ in range(10):
            engine.end_episode(1.0)
        
        assert engine.epsilon < 0.5

    def test_epsilon_min_bound(self):
        """Test epsilon doesn't go below minimum."""
        engine = AdaptiveLearningEngine(epsilon=0.1, epsilon_min=0.05, epsilon_decay=0.5)
        
        for _ in range(100):
            engine.end_episode(1.0)
        
        assert engine.epsilon >= 0.05

    def test_learning_rate_adaptation(self):
        """Test learning rate adapts."""
        engine = AdaptiveLearningEngine()
        engine.register_actions(['a1'])
        
        # Generate enough history
        for i in range(200):
            engine.update({'f': i}, 'a1', float(i), {'f': i + 1})
            if i % 10 == 0:
                engine.end_episode(float(i))
        
        # Learning rate should be within ±20% of base
        assert 0.8 * engine.base_learning_rate <= engine.learning_rate <= 1.2 * engine.base_learning_rate

    def test_get_statistics(self):
        """Test getting statistics."""
        engine = AdaptiveLearningEngine()
        engine.register_actions(['a1'])
        
        engine.update({'f': 1}, 'a1', 1.0, {'f': 2})
        engine.end_episode(1.0)
        
        stats = engine.get_statistics()
        assert 'episodes' in stats
        assert 'avg_reward' in stats
        assert 'q_table_size' in stats
        assert stats['episodes'] == 1

    def test_save_load_policy(self):
        """Test saving and loading policy."""
        engine = AdaptiveLearningEngine()
        engine.register_actions(['a1', 'a2'])
        
        # Train
        for i in range(10):
            engine.update({'f': i}, 'a1', float(i), {'f': i + 1})
        engine.end_episode(10.0)
        
        # Save
        policy = engine.save_policy()
        assert 'q_table' in policy
        assert 'actions' in policy
        
        # Load into new engine
        new_engine = AdaptiveLearningEngine()
        new_engine.load_policy(policy)
        
        assert new_engine.actions == ['a1', 'a2']
        assert new_engine.state.episodes == 1

    def test_convergence_tracking(self):
        """Test Q-value convergence tracking."""
        engine = AdaptiveLearningEngine()
        engine.register_actions(['a1'])
        
        # Generate stable Q-values
        for i in range(200):
            engine.update({'f': 0}, 'a1', 1.0, {'f': 0})
        engine.end_episode(1.0)
        
        # Should have some convergence measure
        assert engine.state.q_value_convergence >= 0


class TestIntegration:
    """Integration tests for Adaptive Learning Engine."""

    def test_full_learning_cycle(self):
        """Test complete learning cycle."""
        engine = AdaptiveLearningEngine(
            learning_rate=0.1,
            epsilon=0.3,
            batch_size=5,
        )
        engine.register_actions(['good', 'bad'])
        
        # Simulate learning episodes
        for episode in range(20):
            state = {'complexity': episode % 5}
            total_reward = 0
            
            for step in range(10):
                action = engine.select_action(state)
                
                # Reward good actions
                reward = 1.0 if action == 'good' else -0.5
                total_reward += reward
                
                next_state = {'complexity': (episode + step) % 5}
                engine.update(state, action, reward, next_state)
                state = next_state
                
                # Learn from replay
                engine.learn_from_replay()
            
            engine.end_episode(total_reward)
        
        # Engine should have learned
        assert engine.state.episodes == 20
        assert engine.state.improvements > 0

    def test_reward_shaper_integration(self):
        """Test reward shaper with engine."""
        engine = AdaptiveLearningEngine()
        shaper = engine.reward_shaper
        
        reward, _ = shaper.compute_reward(
            accuracy=0.9,
            speed=0.8,
            confidence=0.7,
            coherence=0.6,
        )
        
        assert reward > 0
        
        # Use shaped reward in learning
        engine.register_actions(['a1'])
        engine.update({'f': 1}, 'a1', reward, {'f': 2})
        
        assert len(engine.replay_buffer) == 1


class TestPerformance:
    """Performance tests for Adaptive Learning Engine."""

    def test_buffer_performance(self):
        """Test buffer handles large capacity."""
        buffer = ExperienceReplayBuffer(capacity=100_000)
        
        # Add many experiences
        for i in range(10_000):
            buffer.add(Experience(
                state=f"s{i}",
                action="a",
                reward=1.0,
                next_state=f"s{i+1}",
            ))
        
        # Should sample quickly
        experiences, _ = buffer.sample(64)
        assert len(experiences) == 64

    def test_q_table_scaling(self):
        """Test Q-table handles many states."""
        engine = AdaptiveLearningEngine()
        engine.register_actions(['a1', 'a2', 'a3'])
        
        # Add many unique states
        for i in range(1000):
            engine.update(
                state={'f1': i, 'f2': i * 2},
                action='a1',
                reward=1.0,
                next_state={'f1': i + 1, 'f2': (i + 1) * 2},
            )
        
        assert len(engine.q_table) == 1000

    def test_learning_stability(self):
        """Test learning remains stable over many episodes."""
        engine = AdaptiveLearningEngine()
        engine.register_actions(['a1', 'a2'])
        
        rewards = []
        for ep in range(100):
            total = 0
            for _ in range(10):
                engine.update({'f': ep}, 'a1', 1.0, {'f': ep + 1})
                total += 1
            engine.end_episode(total)
            rewards.append(total)
        
        # Learning should be stable (no crashes, reasonable values)
        assert len(rewards) == 100
        assert engine.state.avg_reward > 0
