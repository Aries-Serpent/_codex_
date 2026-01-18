# Examples

Comprehensive examples for all Cognitive Brain components.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Meta-Learning](#meta-learning)
3. [Pattern Store](#pattern-store)
4. [Safety Monitoring](#safety-monitoring)
5. [Benchmarking](#benchmarking)

---

## Basic Usage

### Execute Simple Task

```python
from github.agents.core.universal_intelligence import (
    UniversalTaskInterface,
    TaskSpec,
)

spec = TaskSpec(
    environment="gridworld",
    initial_state={"x": 0, "y": 0, "goal": {"x": 5, "y": 5}},
    reward_spec={"id": "reward:v1"},
    termination={"max_steps": 50},
    seed=12345
)

uti = UniversalTaskInterface(seed=12345)
result = uti.execute_task(spec, use_adapter=True)
```

---

## Meta-Learning

### MAML Adaptation

```python
from github.agents.core.universal_intelligence import MetaPolicyRouter

router = MetaPolicyRouter(seed=12345)

# Prepare task data
task_data = [(x, x**2) for x in range(10)]

# Adapt with MAML
adapted = router.adapt_with_maml("regression_task", task_data)

# Use adapted parameters
print(f"Adapted params: {adapted}")
```

### Reptile Adaptation

```python
# Adapt with Reptile (simpler, more stable)
adapted = router.adapt_with_reptile("regression_task", task_data)
```

### Strategy Selection

```python
# Get probability distribution
probs = router.get_probability_distribution()

# Measure (collapse superposition)
selected = router.measure()

# Get hyperparameters
hyperparams = router.get_hyperparams(selected)
```

---

## Pattern Store

### Store and Retrieve Patterns

```python
from github.agents.core.universal_intelligence import (
    UniversalPatternStore,
    Pattern,
)

store = UniversalPatternStore()

# Store pattern
pattern = Pattern(
    id="nav_pattern_1",
    domain="gridworld",
    payload={"strategy": "shortest_path", "cost": "manhattan"},
    version="1.0.0",
)
pattern_id = store.store_pattern(pattern)

# Retrieve by similarity
query_pattern = Pattern(
    id="query",
    domain="gridworld",
    payload={"strategy": "path_finding"},
)
similar = store.retrieve_by_similarity(query_pattern, threshold=0.7)

# Cross-domain retrieval
cross_domain = store.retrieve_cross_domain("gridworld", limit=5)
```

### Pattern Versioning

```python
# Update pattern version
pattern_v2 = Pattern(
    id="nav_pattern_1",
    domain="gridworld",
    payload={"strategy": "a_star", "heuristic": "euclidean"},
    version="2.0.0",
)
store.store_pattern(pattern_v2)

# Deprecate old version
old_pattern = store.retrieve_patterns(pattern_ids=["nav_pattern_1_v1"])[0]
old_pattern.deprecated = True
```

---

## Safety Monitoring

### Basic Safety Checks

```python
from github.agents.core.universal_intelligence import SafetyMonitor

monitor = SafetyMonitor(
    neg_transfer_threshold=0.05,
    forgetting_threshold=0.20
)

# Set baseline for domain
monitor.set_baseline("navigation", 0.85)

# During execution, check safety
current_performance = 0.75

if monitor.detect_negative_transfer("navigation", current_performance):
    print("⚠️ Negative transfer detected!")
    if monitor.trigger_rollback("navigation"):
        print("✓ Rolled back to baseline")

if monitor.detect_forgetting("navigation", current_performance):
    print("⚠️ Forgetting detected!")
    monitor.isolate_domain("navigation")
    print("✓ Domain isolated")
```

### Safety Constraints

```python
# Check if domain is isolated
if monitor.is_domain_isolated("navigation"):
    print("Domain is in quarantine")

# Get safety report
report = monitor.get_safety_report()
print(f"Isolated domains: {report['isolated_domains']}")
print(f"Rollback count: {report['rollback_count']}")
```

---

## Benchmarking

### Run EXP-10 Benchmark

```python
from github.agents.core.universal_intelligence import (
    EXP10BenchmarkHarness,
    UniversalTaskInterface,
)

# Create harness
harness = EXP10BenchmarkHarness(seed=12345)

# Create UTI
uti = UniversalTaskInterface(seed=12345)

# Run benchmark
results = harness.run_benchmark(uti)

# Validate k₁ target
k1_valid = harness.validate_k1_target(results)
print(f"k₁ validation: {'✓ PASS' if k1_valid else '✗ FAIL'}")

# Test transfer
zero_shot_valid = harness.test_zero_shot_transfer(uti)
few_shot_valid = harness.test_few_shot_transfer(uti, k=10)

print(f"Zero-shot: {'✓ PASS' if zero_shot_valid else '✗ FAIL'}")
print(f"Few-shot: {'✓ PASS' if few_shot_valid else '✗ FAIL'}")

# Export metrics
harness.export_metrics(results, ".github/agents/metrics/phase8_7")
```

---

## Advanced Examples

See Jupyter notebooks in `examples/notebooks/`:
1. `01_quickstart.ipynb` - Basic usage
2. `02_meta_learning.ipynb` - Deep dive into MAML/Reptile
3. `03_safety_monitoring.ipynb` - Safety mechanisms
4. `04_pattern_store.ipynb` - Pattern management
5. `05_benchmarking.ipynb` - EXP-10 validation

---

**Next**: [Architecture →](../architecture.md)
