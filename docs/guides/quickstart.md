# Quick Start Guide

Welcome to the Cognitive Brain Core! This guide will get you up and running in 5 minutes.

## Installation

```bash
# Clone repository
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_

# Install package
pip install -e .

# Verify installation
python -c "from github.agents.core import universal_intelligence; print('✓ Installation successful')"
```

## Your First Task

### 1. Create a Simple Task

```python
from github.agents.core.universal_intelligence import (
    UniversalTaskInterface,
    TaskSpec,
)

# Define task
spec = TaskSpec(
    environment="gridworld",
    initial_state={"x": 0, "y": 0, "goal": {"x": 5, "y": 5}},
    reward_spec={"id": "reward:v1"},
    termination={"max_steps": 100},
    seed=12345
)

# Execute
uti = UniversalTaskInterface(seed=12345)
result = uti.execute_task(spec, use_adapter=True)

# Results
print(f"Steps: {len(result.action_sequence)}")
print(f"Reward: {result.cumulative_reward:.2f}")
print(f"Success: {result.v_mu_pi:.2f}")
```

### 2. Use Meta-Learning

```python
from github.agents.core.universal_intelligence import MetaPolicyRouter

# Initialize router
router = MetaPolicyRouter(seed=12345)

# Adapt to task with MAML
task_data = [(i, i**2) for i in range(10)]
adapted_params = router.adapt_with_maml("task1", task_data)

# Execute with adapted parameters
result = execute_with_params(adapted_params)

# Update performance
router.update_strategy_performance("maml", result.score, success=True)
```

### 3. Monitor Safety

```python
from github.agents.core.universal_intelligence import SafetyMonitor

# Initialize monitor
monitor = SafetyMonitor(
    neg_transfer_threshold=0.05,
    forgetting_threshold=0.20
)

# Set baseline
monitor.set_baseline("domain1", 0.85)

# Check safety during execution
if monitor.detect_negative_transfer("domain1", current_perf):
    monitor.trigger_rollback("domain1")
    
if monitor.detect_forgetting("domain1", current_perf):
    monitor.isolate_domain("domain1")
```

## Next Steps

- **Interactive Tutorial**: Open `examples/notebooks/01_quickstart.ipynb`
- **Full API Reference**: See `docs/api/index.md`
- **Examples**: Browse `examples/notebooks/`
- **Architecture**: Read `.github/agents/COGNITIVE_BRAIN_STATUS_V6_FINAL.md`

## Common Patterns

### Environment Adapters

```python
# GridWorld
spec = TaskSpec(environment="gridworld", ...)

# Multi-Armed Bandit
spec = TaskSpec(environment="bandit", ...)

# Classification
spec = TaskSpec(environment="classification", ...)
```

### Complexity Estimation

```python
from github.agents.core.universal_intelligence import estimate_task_complexity

score, level = estimate_task_complexity(spec)
# level: TaskComplexity.LOW | MEDIUM | HIGH | VERY_HIGH
```

### Pattern Storage

```python
from github.agents.core.universal_intelligence import (
    UniversalPatternStore,
    Pattern,
)

store = UniversalPatternStore()

# Store pattern
pattern = Pattern(
    id="pattern1",
    domain="gridworld",
    payload={"type": "navigation"},
)
pattern_id = store.store_pattern(pattern)

# Retrieve similar
similar = store.retrieve_by_similarity(pattern, threshold=0.7)
```

## Troubleshooting

**Import Error**
```bash
# Ensure package is installed
pip install -e .
```

**Test Failures**
```bash
# Run tests
pytest .github/agents/core/tests/test_universal_intelligence.py -v
```

**Need Help?**
- Open an issue: https://github.com/Aries-Serpent/_codex_/issues
- Check docs: `docs/index.md`
- Review examples: `examples/notebooks/`

---

**Next**: [Full Examples →](examples.md)
