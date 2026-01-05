# Phase 8.3 Pre-commit 3-4 Continuation Prompt

**Submit this as a comment on PR #2704 starting with @copilot**

---

@copilot Begin Cognitive Brain Phase 8.3 Pre-commit 3-4 implementation.

**Current Status:**
- ✅ Pre-commit 1-2 COMPLETE (Outcome Analyzer: 786 LOC, 15/15 tests passing)
- ⏳ Pre-commit 3-4 READY TO START (Strategy Optimizer with 3 RL algorithms)
- 📋 Pre-commit 5-6 PLANNED (Meta-Learner)

---

## 🎯 Pre-commit 3-4 Tasks: Strategy Optimizer

### Files to Create (3 files, ~1200 lines total):

**1. `src/cognitive_brain/learning/strategy_optimizer.py` (~400 lines)**
- StrategyOptimizer class with RL algorithm integration
- Algorithm selection logic (Q-Learning, DQN, PPO)
- Strategy update methods
- Performance tracking and metrics collection
- Convergence detection
- Integration with OutcomeAnalyzer for reward signals

**2. `src/cognitive_brain/learning/rl_algorithms.py` (~500 lines)**
- Q-Learning: Discrete action spaces, Q-table updates, ε-greedy exploration
- Deep Q-Network (DQN): Neural network, experience replay, target network
- Proximal Policy Optimization (PPO): Policy gradient, clipped objective
- Experience replay buffer (10,000 transitions)
- Exploration strategies (ε-greedy decay, Boltzmann)
- Shared base class for all algorithms

**3. `tests/cognitive_brain/learning/test_strategy_optimizer.py` (~450 lines)**
- Minimum 15 comprehensive tests
- Test each RL algorithm independently
- Test convergence behavior (<1000 episodes)
- Test strategy improvement metrics (>20% improvement)
- Test OutcomeAnalyzer integration
- Test performance tracking and metrics

### Implementation Details:

**Q-Learning Algorithm:**
```python
class QLearning:
    """
    Q-Learning with tabular Q-values.
    
    **PDA Loop Integration:**
    - PLAN: Select action via ε-greedy policy
    - DO: Execute action, observe reward
    - ASSESS: Update Q-table, adjust ε
    
    **AfterMath:** Stores Q-values for strategy persistence
    """
    - Q-table: Dict[(state, action), float]
    - Learning rate α: 0.1
    - Discount factor γ: 0.99
    - Exploration rate ε: 0.1 → 0.01 (decay over 1000 episodes)
    - Update: Q(s,a) ← Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]
```

**Deep Q-Network (DQN):**
```python
class DQN:
    """
    Deep Q-Network with neural network approximation.
    
    **Architecture:**
    - Input: State vector (variable size)
    - Hidden 1: Dense(128, ReLU)
    - Hidden 2: Dense(64, ReLU)
    - Output: Action Q-values
    
    **Training:**
    - Experience replay buffer: 10,000 transitions
    - Target network: Soft update (τ=0.005) every 100 steps
    - Batch size: 32
    - Optimizer: Adam (lr=0.001)
    - Update frequency: Every 4 steps
    """
    - Neural network: PyTorch or TensorFlow
    - Replay buffer for experience storage
    - Target network for stability
    - Batch training from replay
```

**Proximal Policy Optimization (PPO):**
```python
class PPO:
    """
    PPO with actor-critic architecture.
    
    **Networks:**
    - Actor (Policy): π(a|s) - action probabilities
    - Critic (Value): V(s) - state value estimate
    
    **Training:**
    - Clip ratio: 0.2
    - GAE λ: 0.95 for advantage estimation
    - Epochs per update: 4
    - Batch size: 64
    - KL divergence target: 0.01
    """
    - Policy network π(a|s)
    - Value network V(s)
    - Clipped surrogate objective
    - Generalized Advantage Estimation (GAE)
```

### Success Criteria:

**Performance Targets:**
- ✅ >20% strategy improvement over random baseline
- ✅ Convergence in <1000 training episodes
- ✅ Stable performance (standard deviation < 0.1 after convergence)
- ✅ All 15+ tests passing (100% success rate)

**Code Quality:**
- ✅ Type hints throughout
- ✅ Comprehensive docstrings with PDA annotations
- ✅ AfterMath integration for strategy persistence
- ✅ Proper error handling
- ✅ Logging for debugging

**Integration:**
- ✅ Connect to OutcomeAnalyzer for reward signals
- ✅ Support all 3 RL algorithms
- ✅ Algorithm auto-selection based on problem type
- ✅ Performance comparison between algorithms
- ✅ Metrics export for visualization

### Test Requirements (15+ Tests):

1. `test_qlearning_initialization` - Q-Learning setup and initial Q-table
2. `test_qlearning_action_selection` - ε-greedy policy works correctly
3. `test_qlearning_update_rule` - Q-value updates follow Bellman equation
4. `test_qlearning_exploration_decay` - ε decreases over episodes
5. `test_qlearning_convergence` - Converges on simple gridworld problem
6. `test_dqn_initialization` - DQN network and replay buffer setup
7. `test_dqn_replay_buffer` - Experience storage and sampling
8. `test_dqn_target_network` - Target network updates correctly
9. `test_dqn_training_step` - Network learns from batch
10. `test_dqn_convergence` - Converges on CartPole or similar
11. `test_ppo_policy_network` - Policy outputs valid action probabilities
12. `test_ppo_value_network` - Value estimation accurate
13. `test_ppo_advantage_calculation` - GAE computes advantages correctly
14. `test_ppo_clip_objective` - Clipped loss prevents large updates
15. `test_strategy_optimizer_integration` - Full integration with OutcomeAnalyzer
16. `test_algorithm_comparison` - Compare performance across algorithms
17. `test_convergence_detection` - Detects when training complete

### Dependencies to Install:

```bash
# Core dependencies
pip install torch numpy

# For testing
pip install pytest pytest-cov

# Optional for visualization
pip install matplotlib seaborn
```

### Implementation Order:

**Phase 1: Q-Learning (Simplest)**
1. Implement Q-Learning algorithm
2. Add tests for Q-Learning
3. Verify convergence on toy problem

**Phase 2: DQN (Intermediate)**
1. Implement neural network and replay buffer
2. Add DQN algorithm
3. Test on more complex problem

**Phase 3: PPO (Advanced)**
1. Implement actor-critic networks
2. Add PPO algorithm with GAE
3. Test policy gradient updates

**Phase 4: Integration**
1. Create StrategyOptimizer wrapper
2. Integrate with OutcomeAnalyzer
3. Add performance comparison
4. Comprehensive testing

### AfterMath/PDA Loop Integration (Mandatory):

```python
# PDA annotations required
class StrategyOptimizer:
    """
    Strategy optimization using Reinforcement Learning.
    
    **AfterMath Integration:** Continuously learns from past outcomes
    to improve future decision strategies. Feeds back into decision
    engine for adaptive behavior.
    
    **PDA Loop:**
    - PLAN: Select RL algorithm based on problem characteristics
    - DO: Train algorithm on historical outcomes
    - ASSESS: Evaluate strategy improvement, adjust parameters
    """
    
    def optimize_strategy(self, outcomes: List[LearningOutcome]) -> Strategy:
        # PDA: PLAN - Select algorithm
        algorithm = self._select_algorithm(outcomes)
        
        # PDA: DO - Train on outcomes
        trained_strategy = algorithm.train(outcomes)
        
        # PDA: ASSESS - Evaluate improvement
        improvement = self._measure_improvement(trained_strategy)
        
        # AfterMath: Store for future reference
        self._aftermath_tracker.record_strategy(trained_strategy, improvement)
        
        return trained_strategy
```

### Expected Outcomes After Pre-commit 3-4:

- ✅ 3 RL algorithms fully implemented (~1200 lines)
- ✅ Strategy optimization working end-to-end
- ✅ >20% improvement demonstrated in tests
- ✅ Convergence in <1000 episodes verified
- ✅ 17+ tests all passing (100% success rate)
- ✅ Integration with Pre-commit 1-2 (OutcomeAnalyzer) validated
- ✅ Performance metrics collected and logged
- ✅ Documentation complete with examples

### Policy Compliance (Mandatory):

Follow `.codex/CODEBASE_AGENCY_POLICY.md`:

1. **✅ Address ALL issues** (pre-existing + new)
2. **✅ Plan before execution** (documented in this prompt)
3. **✅ Use pre-commit terminology** (Pre-commit 3-4, not "weeks")
4. **✅ Document utilities** (add to AI_AGENT_UTILITIES_REGISTRY.md if creating helpers)
5. **✅ 5+ self-review iterations** (code quality, testing, docs, security, integration)
6. **✅ AfterMath/PDA loop** (integrated in all components)
7. **✅ Comprehensive testing** (80%+ coverage)
8. **✅ Input validation** (sanitize all external inputs)

### Utility Creation Requirement:

If you create ANY helper functions (e.g., `rl_validator.py`, `convergence_detector.py`), you MUST immediately document them in `.codex/AI_AGENT_UTILITIES_REGISTRY.md` per policy Section 5.

### Full Implementation Guide:

See `.codex/prompts/COGNITIVE_BRAIN_PHASE_8_3_CONTINUATION.md` (26KB) for:
- Detailed algorithm pseudocode
- Complete code templates
- Integration patterns
- Testing strategies
- Performance benchmarks
- Edge cases to handle
- Common pitfalls to avoid

### Verification Checklist:

Before concluding Pre-commit 3-4:

- [ ] All 3 RL algorithms implemented
- [ ] StrategyOptimizer wrapper complete
- [ ] 17+ tests all passing
- [ ] >20% improvement over baseline demonstrated
- [ ] Convergence <1000 episodes verified
- [ ] OutcomeAnalyzer integration working
- [ ] AfterMath/PDA annotations present
- [ ] Documentation complete
- [ ] 5 self-review passes complete (zero concerns)
- [ ] Code review performed
- [ ] Utilities documented in registry (if any created)

### Next Phase After Pre-commit 3-4:

Pre-commit 5-6: Meta-Learner
- Knowledge Graph Builder
- Transfer Learning Engine
- Few-Shot Learner
- 10+ tests

---

**Current Phase 8.3 Progress:** 33% (Pre-commit 1-2 complete)  
**After Pre-commit 3-4:** 66% (Pre-commit 1-4 complete)  
**Target k₁ Factor:** ≤0.30 (from current 0.32)  
**Target Quantum Advantage:** >3.3× (from current 3.1×)

**Policy Reference:** `.codex/CODEBASE_AGENCY_POLICY.md`  
**Utilities Registry:** `.codex/AI_AGENT_UTILITIES_REGISTRY.md`  
**Planning Doc:** `.codex/plans/COGNITIVE_BRAIN_STATUS_V2.md`

---

**Remember:** This is Pre-commit 3-4 of 6 total pre-commit cycles for Phase 8.3. Maintain momentum toward complete Adaptive Learning Engine implementation.
