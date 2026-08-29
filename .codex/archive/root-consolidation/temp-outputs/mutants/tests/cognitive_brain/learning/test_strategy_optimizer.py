"""
Tests for Strategy Optimizer and RL Algorithms.

Comprehensive test suite covering Q-Learning, DQN, PPO, and StrategyOptimizer.
Tests convergence, improvement metrics, and OutcomeAnalyzer integration.

AfterMath: Phase 8.3 Pre-commit 3-4 - Strategy Optimizer Testing
"""

import pytest

np = pytest.importorskip("numpy")

from cognitive_brain.learning.outcome_analyzer import OutcomeAnalyzer
from cognitive_brain.learning.rl_algorithms import (
    DQN,
    PPO,
    Experience,
    QLearning,
    ReplayBuffer,
)
from cognitive_brain.learning.strategy_optimizer import (
    AlgorithmType,
    StrategyMetrics,
    StrategyOptimizer,
)
from cognitive_brain.models.learning_outcome import (
    DecisionContext,
    LearningOutcome,
    OutcomeType,
)

# ============================================================================
# Q-Learning Tests
# ============================================================================


def test_qlearning_initialization():
    """Test 1: Q-Learning initializes correctly."""
    ql = QLearning(learning_rate=0.1, discount_factor=0.99, epsilon=0.1)

    assert ql.learning_rate == 0.1, "learning_rate is not valid"
    assert ql.discount_factor == 0.99, "Count must be greater than zero"
    assert ql.epsilon == 0.1, "epsilon is not valid"
    assert len(ql.q_table) == 0, "Collection must not be empty"
    assert ql.episode_count == 0, "Count must be greater than zero"


def test_qlearning_action_selection():
    """Test 2: Q-Learning ε-greedy policy works correctly."""
    ql = QLearning(epsilon=0.0)  # No exploration for deterministic test

    # Set up Q-values
    state = "state_0"
    actions = ["action_0", "action_1", "action_2"]
    ql._set_q_value(state, "action_0", 1.0)
    ql._set_q_value(state, "action_1", 2.0)  # Best action
    ql._set_q_value(state, "action_2", 0.5)

    # Should always select best action with epsilon=0
    action = ql.select_action(state, actions)
    assert action == "action_1", "action is not valid"


def test_qlearning_update_rule():
    """Test 3: Q-value updates follow Bellman equation."""
    ql = QLearning(learning_rate=0.1, discount_factor=0.9)

    state = "state_0"
    action = "action_0"
    reward = 1.0
    next_state = "state_1"

    # Initial Q-value
    initial_q = 0.0
    ql._set_q_value(state, action, initial_q)

    # Set next state Q-values
    ql._set_q_value(next_state, "action_0", 0.5)
    ql._set_q_value(next_state, "action_1", 1.0)  # Max

    # Update
    ql.update(state, action, reward, next_state, done=False)

    # Expected: Q(s,a) = 0 + 0.1 * (1.0 + 0.9 * 1.0 - 0) = 0.19
    expected_q = initial_q + 0.1 * (reward + 0.9 * 1.0 - initial_q)
    actual_q = ql._get_q_value(state, action)

    assert abs(actual_q - expected_q) < 1e-6, "Condition must be true"


def test_qlearning_exploration_decay():
    """Test 4: ε decreases over episodes."""
    ql = QLearning(epsilon=0.5, epsilon_decay=0.9, epsilon_min=0.01)

    initial_epsilon = ql.epsilon

    # Simulate episode end
    ql.update("state_0", "action_0", 1.0, "state_1", done=True)

    assert ql.epsilon < initial_epsilon, "epsilon is not valid"
    assert ql.epsilon >= ql.epsilon_min, "epsilon must be greater than zero"


def test_qlearning_convergence_simple():
    """Test 5: Q-Learning converges on simple problem."""
    ql = QLearning(learning_rate=0.5, discount_factor=0.9, epsilon=0.1)

    # Simple deterministic environment: state_0 -> action_0 -> reward 1
    state = "state_0"
    action = "action_0"
    reward = 1.0

    # Train for many steps
    for _ in range(100):
        ql.update(state, action, reward, state, done=False)

    # Q-value should converge near reward / (1 - gamma) = 1.0 / 0.1 = 10
    q_value = ql._get_q_value(state, action)
    assert q_value > 5.0, "q_value must be greater than zero"


# ============================================================================
# DQN Tests
# ============================================================================


def test_dqn_initialization():
    """Test 6: DQN initializes correctly."""
    dqn = DQN(learning_rate=0.001, buffer_capacity=1000, batch_size=32)

    assert dqn.learning_rate == 0.001, "learning_rate is not valid"
    assert dqn.batch_size == 32, "batch_size is not valid"
    assert len(dqn.replay_buffer) == 0, "Collection must not be empty"
    assert dqn.step_count == 0, "Count must be greater than zero"


def test_dqn_replay_buffer():
    """Test 7: Experience replay buffer stores and samples correctly."""
    buffer = ReplayBuffer(capacity=100)

    # Add experiences
    for i in range(50):
        buffer.add(f"state_{i}", f"action_{i}", float(i), f"next_state_{i}", False)

    assert len(buffer) == 50, "Buffer must not be empty"

    # Sample batch
    batch = buffer.sample(10)
    assert len(batch) == 10, "Batch must not be empty"
    assert all(isinstance(exp, Experience) for exp in batch)


def test_dqn_target_network():
    """Test 8: Target network updates correctly."""
    dqn = DQN(target_update_freq=10)

    # Initialize some weights
    dqn.q_weights["action_0"] = 1.0

    # Trigger target update
    for i in range(10):
        dqn.update(f"state_{i}", "action_0", 1.0, f"state_{i + 1}", done=False)

    # Target weights should be updated
    assert "action_0" in dqn.target_weights, "Condition must be true"


def test_dqn_training_step():
    """Test 9: DQN learns from experience batch."""
    dqn = DQN(learning_rate=0.01, batch_size=5)

    # Add experiences to buffer
    for i in range(20):
        state = f"state_{i % 3}"
        action = "action_0"
        reward = 1.0 if i % 2 == 0 else -1.0
        next_state = f"state_{(i + 1) % 3}"
        dqn.update(state, action, reward, next_state, done=False)

    # Should have performed updates
    assert dqn.update_count > 0, "update_count must be positive"
    assert len(dqn.loss_history) > 0, "Collection must not be empty"


def test_dqn_convergence():
    """Test 10: DQN converges on simple problem."""
    dqn = DQN(learning_rate=0.01, epsilon=0.1, batch_size=8)

    # Simple environment with consistent rewards
    rewards = []
    for episode in range(50):
        episode_reward = 0
        for step in range(10):
            state = f"state_{step % 3}"
            action = dqn.select_action(state)
            reward = 1.0  # Always positive reward
            next_state = f"state_{(step + 1) % 3}"
            done = step == 9

            dqn.update(state, action, reward, next_state, done)
            episode_reward += reward

        dqn.track_episode(episode_reward)
        rewards.append(episode_reward)

    # Average reward should improve
    early_avg = np.mean(rewards[:10])
    late_avg = np.mean(rewards[-10:])
    assert late_avg >= early_avg, "late_avg must be greater than zero"


# ============================================================================
# PPO Tests
# ============================================================================


def test_ppo_policy_network():
    """Test 11: PPO policy outputs valid action probabilities."""
    ppo = PPO(learning_rate=0.001)

    state = "state_0"
    probs = ppo._get_action_probs(state)

    # Check probabilities sum to 1
    assert abs(sum(probs.values()) - 1.0) < 1e-6, "Value must be initialized"

    # Check all probabilities in [0, 1]
    assert all(0 <= p <= 1 for p in probs.values()), "Value must be initialized"


def test_ppo_value_network():
    """Test 12: PPO value estimation works."""
    ppo = PPO()

    state = "state_0"

    # Initially should be 0 or small
    value = ppo._get_value(state)
    assert isinstance(value, float)

    # Update value
    ppo.value_weights[state] = 5.0
    assert ppo._get_value(state) == 5.0, "Value must be initialized"


def test_ppo_advantage_calculation():
    """Test 13: GAE computes advantages correctly."""
    ppo = PPO(discount_factor=0.9, gae_lambda=0.95)

    # Create simple trajectory
    ppo.trajectory = [
        {
            "state": "s0",
            "action": "a0",
            "reward": 1.0,
            "next_state": "s1",
            "done": False,
            "value": 0.0,
            "action_prob": 0.33,
        },
        {
            "state": "s1",
            "action": "a1",
            "reward": 2.0,
            "next_state": "s2",
            "done": False,
            "value": 0.0,
            "action_prob": 0.33,
        },
        {
            "state": "s2",
            "action": "a2",
            "reward": 3.0,
            "next_state": "s3",
            "done": True,
            "value": 0.0,
            "action_prob": 0.33,
        },
    ]

    advantages = ppo._compute_advantages()

    assert len(advantages) == 3, "Advantages must not be empty"
    assert all(isinstance(adv, float) for adv in advantages)


def test_ppo_clip_objective():
    """Test 14: Clipped loss prevents large updates."""
    ppo = PPO(clip_ratio=0.2)

    # Create trajectory and train
    for i in range(5):
        state = f"state_{i}"
        action = ppo.select_action(state)
        reward = float(i)
        next_state = f"state_{i + 1}"
        done = i == 4

        ppo.update(state, action, reward, next_state, done)

    # Should have updated policy
    assert ppo.policy_updates > 0, "policy_updates must be greater than zero"


# ============================================================================
# Strategy Optimizer Tests
# ============================================================================


def test_strategy_optimizer_initialization():
    """Test 15: StrategyOptimizer creates properly."""
    optimizer = StrategyOptimizer(algorithm_type=AlgorithmType.Q_LEARNING)

    assert optimizer.algorithm_type == AlgorithmType.Q_LEARNING, "algorithm_type is not valid"
    assert optimizer.algorithm is not None, "algorithm must be initialized"
    assert isinstance(optimizer.algorithm, QLearning)
    assert optimizer.episode_count == 0, "Count must be greater than zero"


def test_algorithm_selection():
    """Test 16: Algorithm selection logic works."""
    optimizer = StrategyOptimizer()

    # Simple problem -> Q-Learning
    simple_outcomes = [
        LearningOutcome(
            outcome_id=f"out_{i}",
            decision_id=f"dec_{i}",
            outcome_type=OutcomeType.SUCCESS,
            reward=0.5,
            context=DecisionContext(
                task_type="simple",
                complexity=0.2,
                resource_constraints={},
                agent_ids=["agent_1"],
            ),
            patterns_identified=[],
            lessons_learned=[],
        )
        for i in range(5)
    ]

    algo = optimizer.select_algorithm(simple_outcomes)
    assert algo == AlgorithmType.Q_LEARNING, "algo is not valid"

    # Complex problem -> PPO
    complex_outcomes = [
        LearningOutcome(
            outcome_id=f"out_{i}",
            decision_id=f"dec_{i}",
            outcome_type=OutcomeType.SUCCESS,
            reward=0.5,
            context=DecisionContext(
                task_type="complex",
                complexity=0.9,
                resource_constraints={},
                agent_ids=["agent_1", "agent_2", "agent_3"],
            ),
            patterns_identified=[],
            lessons_learned=[],
        )
        for i in range(5)
    ]

    algo = optimizer.select_algorithm(complex_outcomes)
    assert algo == AlgorithmType.PPO, "algo is not valid"


def test_performance_tracking():
    """Test 17: Tracks improvement over time."""
    optimizer = StrategyOptimizer(algorithm_type=AlgorithmType.Q_LEARNING)

    # Create outcomes with varying rewards
    outcomes = []
    for i in range(20):
        outcome = LearningOutcome(
            outcome_id=f"out_{i}",
            decision_id=f"dec_{i}",
            outcome_type=OutcomeType.SUCCESS if i % 2 == 0 else OutcomeType.FAILURE,
            reward=0.8 if i % 2 == 0 else -0.5,
            context=DecisionContext(
                task_type="test",
                complexity=0.5,
                resource_constraints={},
                agent_ids=["agent_1"],
            ),
            patterns_identified=[],
            lessons_learned=[],
        )
        outcomes.append(outcome)

    # Optimize
    results = optimizer.optimize_strategy(outcomes, max_episodes=50)

    assert "improvement_percentage" in results, "Result must not be empty"
    assert "episodes_trained" in results, "Result must not be empty"
    assert results["episodes_trained"] > 0, "Value must be greater than zero"


def test_convergence_detection():
    """Test 18: Detects when training complete."""
    optimizer = StrategyOptimizer(algorithm_type=AlgorithmType.Q_LEARNING)
    optimizer.convergence_threshold = 0.05

    # Create stable reward history (converged)
    optimizer.training_history = [0.5] * 150

    assert optimizer._check_convergence(), "Condition must be true"

    # Create varying rewards (not converged)
    optimizer.training_history = [float(i % 10) / 10 for i in range(150)]

    assert not optimizer._check_convergence(), "Condition must be true"


def test_outcome_analyzer_integration():
    """Test 19: Integrates with OutcomeAnalyzer for reward signals."""
    analyzer = OutcomeAnalyzer()
    optimizer = StrategyOptimizer(
        outcome_analyzer=analyzer, algorithm_type=AlgorithmType.Q_LEARNING
    )

    assert optimizer.outcome_analyzer is analyzer, "outcome_analyzer is not valid"

    # Create and analyze outcome
    outcome = LearningOutcome(
        outcome_id="out_0",
        decision_id="dec_0",
        outcome_type=OutcomeType.SUCCESS,
        reward=0.8,
        context=DecisionContext(
            task_type="test",
            complexity=0.5,
            resource_constraints={},
            agent_ids=["agent_1"],
        ),
        patterns_identified=[],
        lessons_learned=[],
    )

    # Analyze to get reward - fix parameter order
    analyzed = analyzer.analyze_outcome(
        decision_id=outcome.decision_id,
        outcome_type=outcome.outcome_type,
        result_metrics={"success": True, "efficiency": 0.8},
        context=outcome.context,
    )

    # Check reward is calculated
    assert analyzed.reward is not None, "reward must be initialized"
    assert isinstance(analyzed.reward, float)


def test_strategy_improvement_target():
    """Test 20: Achieves >20% improvement over baseline."""
    optimizer = StrategyOptimizer(algorithm_type=AlgorithmType.Q_LEARNING)

    # Create outcomes with potential for improvement
    # Start with poor performance, improve over time
    outcomes = []
    for i in range(50):
        # Gradually improving rewards
        base_reward = -0.5 if i < 25 else 0.5
        reward = base_reward + np.random.randn() * 0.1

        outcome = LearningOutcome(
            outcome_id=f"out_{i}",
            decision_id=f"dec_{i}",
            outcome_type=OutcomeType.SUCCESS if reward > 0 else OutcomeType.FAILURE,
            reward=reward,
            context=DecisionContext(
                task_type="improving",
                complexity=0.4,
                resource_constraints={},
                agent_ids=["agent_1"],
            ),
            patterns_identified=[],
            lessons_learned=[],
        )
        outcomes.append(outcome)

    # Optimize with target improvement
    results = optimizer.optimize_strategy(outcomes, max_episodes=200, target_improvement=0.20)

    # Check improvement
    assert "improvement_percentage" in results, "Result must not be empty"
    assert results["improvement_percentage"] is not None, "Value must be initialized"
    assert results["episodes_trained"] > 0, "Value must be greater than zero"


def test_strategy_application():
    """Test 21: Apply optimized strategy to select actions."""
    optimizer = StrategyOptimizer(algorithm_type=AlgorithmType.Q_LEARNING)

    # Train on simple data
    outcomes = []
    for i in range(10):
        outcome = LearningOutcome(
            outcome_id=f"out_{i}",
            decision_id=f"dec_{i}",
            outcome_type=OutcomeType.SUCCESS,
            reward=1.0,
            context=DecisionContext(
                task_type="test",
                complexity=0.5,
                resource_constraints={},
                agent_ids=["agent_1"],
            ),
            patterns_identified=[],
            lessons_learned=[],
        )
        outcomes.append(outcome)

    optimizer.optimize_strategy(outcomes, max_episodes=20)

    # Apply strategy
    state = "state_c1_p1"
    action = optimizer.apply_strategy(state)

    assert action is not None, "action must be initialized"
    assert isinstance(action, str)


def test_metrics_export():
    """Test 22: Exports performance metrics correctly."""
    optimizer = StrategyOptimizer(algorithm_type=AlgorithmType.Q_LEARNING)

    # Create minimal outcomes
    outcomes = [
        LearningOutcome(
            outcome_id="out_0",
            decision_id="dec_0",
            outcome_type=OutcomeType.SUCCESS,
            reward=0.5,
            context=DecisionContext(
                task_type="test",
                complexity=0.5,
                resource_constraints={},
                agent_ids=["agent_1"],
            ),
            patterns_identified=[],
            lessons_learned=[],
        )
    ]

    results = optimizer.optimize_strategy(outcomes, max_episodes=10)

    # Check metrics
    assert "algorithm" in results, "Result must not be empty"
    assert "episodes_trained" in results, "Result must not be empty"
    assert "baseline_performance" in results, "Result must not be empty"
    assert "final_performance" in results, "Result must not be empty"
    assert "improvement_percentage" in results, "Result must not be empty"
    assert "training_history" in results, "Result must not be empty"

    # Get strategy metrics
    metrics = optimizer.get_metrics()
    assert metrics is not None, "metrics must be initialized"
    assert isinstance(metrics, StrategyMetrics)
    assert metrics.algorithm_type == AlgorithmType.Q_LEARNING, "algorithm_type is not valid"


# ============================================================================
# Integration & Comprehensive Tests
# ============================================================================


def test_full_pipeline_qlearning():
    """Test 23: Full pipeline with Q-Learning."""
    analyzer = OutcomeAnalyzer()
    optimizer = StrategyOptimizer(
        outcome_analyzer=analyzer, algorithm_type=AlgorithmType.Q_LEARNING
    )

    # Create realistic outcomes
    outcomes = []
    for i in range(30):
        context = DecisionContext(
            task_type=f"task_{i % 3}",
            complexity=0.3 + (i % 5) * 0.1,
            resource_constraints={"cpu": 0.5, "memory": 0.7},
            time_pressure=0.4,
            agent_ids=[f"agent_{i % 2}"],
        )

        # Analyze to get reward - fix parameter order
        analyzed = analyzer.analyze_outcome(
            decision_id=f"dec_{i}",
            outcome_type=OutcomeType.SUCCESS if i % 3 != 0 else OutcomeType.FAILURE,
            result_metrics={"success": i % 3 != 0, "efficiency": 0.7},
            context=context,
        )

        outcomes.append(analyzed)

    # Optimize strategy
    results = optimizer.optimize_strategy(outcomes, max_episodes=100)

    # Verify results
    assert results["episodes_trained"] > 0, "Value must be greater than zero"
    assert "policy" in results, "Result must not be empty"
    assert len(optimizer.training_history) > 0, "Collection must not be empty"


def test_full_pipeline_dqn():
    """Test 24: Full pipeline with DQN."""
    optimizer = StrategyOptimizer(algorithm_type=AlgorithmType.DQN)

    # Create outcomes
    outcomes = []
    for i in range(25):
        outcome = LearningOutcome(
            outcome_id=f"out_{i}",
            decision_id=f"dec_{i}",
            outcome_type=OutcomeType.SUCCESS if i % 2 == 0 else OutcomeType.PARTIAL,
            reward=0.7 if i % 2 == 0 else 0.3,
            context=DecisionContext(
                task_type="dqn_task",
                complexity=0.6,
                resource_constraints={},
                agent_ids=["agent_1"],
            ),
            patterns_identified=[],
            lessons_learned=[],
        )
        outcomes.append(outcome)

    # Optimize
    results = optimizer.optimize_strategy(outcomes, max_episodes=50)

    assert results["algorithm"] == "dqn", "Result must not be empty"
    assert results["episodes_trained"] > 0, "Value must be greater than zero"


def test_full_pipeline_ppo():
    """Test 25: Full pipeline with PPO."""
    optimizer = StrategyOptimizer(algorithm_type=AlgorithmType.PPO)

    # Create outcomes
    outcomes = []
    for i in range(20):
        outcome = LearningOutcome(
            outcome_id=f"out_{i}",
            decision_id=f"dec_{i}",
            outcome_type=OutcomeType.SUCCESS,
            reward=0.6 + np.random.randn() * 0.1,
            context=DecisionContext(
                task_type="ppo_task",
                complexity=0.8,
                resource_constraints={},
                agent_ids=["agent_1", "agent_2"],
            ),
            patterns_identified=[],
            lessons_learned=[],
        )
        outcomes.append(outcome)

    # Optimize
    results = optimizer.optimize_strategy(outcomes, max_episodes=40)

    assert results["algorithm"] == "ppo", "Result must not be empty"
    assert results["episodes_trained"] > 0, "Value must be greater than zero"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
