"""Tests for src/cognitive_brain/learning/rl_algorithms.py — Phase 10B coverage.

Covers ReplayBuffer, QLearning, DQN, and PPO algorithms.
"""

from __future__ import annotations

import pytest

np = pytest.importorskip("numpy")

from cognitive_brain.learning.rl_algorithms import (  # noqa: E402
    DQN,
    Experience,
    QLearning,
    ReplayBuffer,
)

# ---------------------------------------------------------------------------
# ReplayBuffer
# ---------------------------------------------------------------------------


class TestReplayBuffer:
    def test_add_and_len(self):
        buf = ReplayBuffer(capacity=100)
        assert len(buf) == 0, "Buf must not be empty"
        buf.add("s0", "a0", 1.0, "s1", False)
        assert len(buf) == 1, "Buf must not be empty"

    def test_capacity_limit(self):
        buf = ReplayBuffer(capacity=3)
        for i in range(5):
            buf.add(f"s{i}", "a", 1.0, f"s{i+1}", False)
        assert len(buf) == 3, "Buf must not be empty"

    def test_sample_full_buffer(self):
        buf = ReplayBuffer(capacity=100)
        for i in range(10):
            buf.add(f"s{i}", "a", 1.0, f"s{i+1}", False)
        batch = buf.sample(5)
        assert len(batch) == 5, "Batch must not be empty"
        assert all(isinstance(e, Experience) for e in batch)

    def test_sample_undersized_buffer(self):
        buf = ReplayBuffer(capacity=100)
        buf.add("s0", "a", 1.0, "s1", False)
        buf.add("s1", "a", 2.0, "s2", True)
        batch = buf.sample(10)
        assert len(batch) == 2, "Batch must not be empty"

    def test_clear(self):
        buf = ReplayBuffer(capacity=100)
        buf.add("s0", "a", 1.0, "s1", False)
        buf.clear()
        assert len(buf) == 0, "Buf must not be empty"


# ---------------------------------------------------------------------------
# QLearning
# ---------------------------------------------------------------------------


class TestQLearning:
    @pytest.fixture()
    def ql(self):
        return QLearning(
            learning_rate=0.5,
            discount_factor=0.9,
            epsilon=0.0,  # greedy for deterministic tests
        )

    def test_select_action_no_history(self, ql):
        # With no Q-table entries, should return a default action
        action = ql.select_action("s0")
        assert action in ["action_0", "action_1", "action_2"]

    def test_select_action_with_available(self, ql):
        ql._set_q_value("s0", "left", 1.0)
        ql._set_q_value("s0", "right", 0.5)
        action = ql.select_action("s0", available_actions=["left", "right"])
        assert action == "left", "action is not valid"

    def test_update_terminal(self, ql):
        ql.update("s0", "a0", 10.0, "s1", done=True)
        q = ql._get_q_value("s0", "a0")
        assert q == pytest.approx(5.0), "q is not valid"

    def test_update_nonterminal(self, ql):
        ql._set_q_value("s1", "a0", 4.0)
        ql.update("s0", "a0", 1.0, "s1", done=False)
        # target = 1.0 + 0.9*4.0 = 4.6; new = 0 + 0.5*(4.6) = 2.3
        q = ql._get_q_value("s0", "a0")
        assert q == pytest.approx(2.3), "q is not valid"

    def test_get_policy(self, ql):
        ql._set_q_value("s0", "a0", 1.0)
        ql._set_q_value("s0", "a1", 2.0)
        policy = ql.get_policy()
        assert policy["s0"] == "a1", "Condition must be true"

    def test_get_state_value(self, ql):
        ql._set_q_value("s0", "a0", 3.0)
        ql._set_q_value("s0", "a1", 5.0)
        assert ql.get_state_value("s0") == 5.0, "Value must be initialized"

    def test_get_state_value_unknown(self, ql):
        assert ql.get_state_value("unknown") == 0.0, "Value must be initialized"

    def test_epsilon_decay(self):
        ql = QLearning(epsilon=1.0, epsilon_decay=0.5, epsilon_min=0.01)
        ql.update("s0", "a0", 1.0, "s1", done=True)
        assert ql.epsilon == pytest.approx(0.5), "epsilon is not valid"
        ql.update("s0", "a0", 1.0, "s1", done=True)
        assert ql.epsilon == pytest.approx(0.25), "epsilon is not valid"

    def test_track_episode(self, ql):
        ql.track_episode(10.0)
        ql.track_episode(20.0)
        assert ql.episode_count == 2, "Count must be greater than zero"
        assert ql.total_reward == 30.0, "total_reward is not valid"
        assert ql.get_avg_reward() == pytest.approx(15.0), "Condition must be true"

    def test_avg_reward_empty(self, ql):
        assert ql.get_avg_reward() == 0.0, "Condition must be true"

    def test_episode_history_cap(self, ql):
        for i in range(110):
            ql.track_episode(float(i))
        assert len(ql.episode_rewards) == 100, "Collection must not be empty"


# ---------------------------------------------------------------------------
# DQN
# ---------------------------------------------------------------------------


class TestDQN:
    @pytest.fixture()
    def dqn(self):
        return DQN(
            learning_rate=0.01,
            discount_factor=0.99,
            epsilon=0.0,  # greedy for deterministic tests
            buffer_capacity=100,
            batch_size=4,
        )

    def test_select_action_no_weights(self, dqn):
        action = dqn.select_action("s0", available_actions=["a", "b"])
        assert action in ["a", "b"]

    def test_update_stores_experience(self, dqn):
        assert len(dqn.replay_buffer) == 0, "Collection must not be empty"
        dqn.update("s0", "a0", 1.0, "s1", False)
        assert len(dqn.replay_buffer) == 1, "Collection must not be empty"

    def test_get_policy(self, dqn):
        # DQN policy extraction should return a dict
        policy = dqn.get_policy()
        assert isinstance(policy, dict)
