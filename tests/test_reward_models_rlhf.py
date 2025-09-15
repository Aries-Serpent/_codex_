from __future__ import annotations

import pytest

from codex_ml.reward_models.rlhf import RewardModel, RLTrainer
from codex_ml.rl.simple_agent import RandomAgent


def test_reward_model_learn_calibrates_scale_and_bias():
    model = RewardModel()
    dataset = [
        ("p1", "a", 1.0),
        ("p2", "abcd", 2.5),
        ("p3", "abc", 2.0),
    ]

    metrics = model.learn(dataset)

    assert metrics["examples"] == pytest.approx(3.0)
    assert metrics["scale"] == pytest.approx(0.5)
    assert metrics["bias"] == pytest.approx(0.5)
    assert "base_loss" in metrics

    # After calibration, scoring a new completion should use the fitted line.
    score = model.score("prompt", "aa")
    assert score == pytest.approx(1.5)


def test_rl_trainer_updates_agent_and_reports_metrics():
    model = RewardModel()
    agent = RandomAgent()
    reward_dataset = [
        ("p1", "aa", 1.5),
        ("p2", "aaaa", 2.7),
    ]
    trainer = RLTrainer(agent, model, discount=0.9)

    trajectories = [
        {"prompt": "p1", "completion": "aa"},
        {"prompt": "p2", "completion": "aaaa", "rewards": [0.1]},
    ]

    result = trainer.train(trajectories, reward_dataset=reward_dataset)

    assert result["episodes"] == pytest.approx(2.0)
    assert result["total_reward"] > 0
    assert result["discounted_reward"] > 0
    assert "agent_loss" in result
    assert result["agent_loss"] == pytest.approx(0.0)
    assert result["reward_examples"] == pytest.approx(2.0)
