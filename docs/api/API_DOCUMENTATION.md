# API Reference Documentation

> **Version**: 1.0.0  
> **Generated**: 2025-12-11  
> **Auto-sync**: Updates with code changes via CI

---

## Overview

This document provides comprehensive API documentation for the _codex_ repository, covering all public modules, classes, and functions.

---

## Table of Contents

1. [Agent APIs](#agent-apis)
2. [ML Core APIs](#ml-core-apis)
3. [Integration APIs](#integration-apis)
4. [Utility APIs](#utility-apis)

---

## Agent APIs

### AgentMemorySystem

**Module**: `agents.agent_memory`

SQLite-backed persistent memory system for AI agents.

```python
from agents.agent_memory import AgentMemorySystem

# Initialize
memory = AgentMemorySystem(agent_id="my_agent", db_path=Path("memory.db"))

# Start a task
frame = memory.start_task("Fix security vulnerability")

# Store a decision
memory_id = memory.store_decision(
    task_id="task_001",
    decision="Use input validation",
    rationale="Prevents injection attacks",
    context={"file": "auth.py"}
)

# Retrieve similar contexts
contexts = memory.retrieve_similar_context(
    task_description="security input validation",
    limit=5
)

# Get pattern library
patterns = memory.get_pattern_library()

# Invalidate old contexts
count = memory.invalidate_stale_contexts(age_days=30)

# Complete task
memory.complete_task(success=True, summary="Fixed vulnerability")
```

#### Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `start_task` | `task_description: str` | `ContextFrame` | Start a new task context |
| `store_decision` | `task_id, decision, rationale, context` | `str` | Store decision, returns memory ID |
| `retrieve_similar_context` | `task_description, limit=5` | `List[Dict]` | Find relevant past contexts |
| `get_pattern_library` | None | `List[Dict]` | Get all decision patterns |
| `invalidate_stale_contexts` | `age_days=30` | `int` | Clean old contexts, returns count |
| `record_decision` | `decision, alternatives, confidence, reasoning` | `MemoryEntry` | Record decision with alternatives |
| `record_lesson` | `lesson, success` | `MemoryEntry` | Record lesson learned |
| `get_guidance` | `situation: str` | `Dict` | Get guidance for situation |
| `complete_task` | `success, summary` | None | Complete current task |
| `get_stats` | None | `Dict` | Get memory statistics |

---

### SelfHealingEngine

**Module**: `agents.self_healing`

Automated issue detection and remediation engine.

```python
from agents.self_healing import SelfHealingEngine

# Initialize
engine = SelfHealingEngine(repo_path=".")

# Run health check
report = engine.run_health_check()
print(f"Health Score: {report.health_score}/100")

# Get issues
for issue in report.issues:
    print(f"- {issue.issue_type}: {issue.description}")
    print(f"  Fix: {issue.suggested_fix}")

# Apply fixes (dry run)
results = engine.apply_fixes(dry_run=True)
```

#### Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `run_health_check` | None | `HealthReport` | Analyze repository health |
| `detect_issues` | None | `List[Issue]` | Detect all issues |
| `suggest_fixes` | `issues: List[Issue]` | `List[Fix]` | Generate fix suggestions |
| `apply_fixes` | `dry_run=True` | `Dict` | Apply fixes to codebase |

---

### QuantumGameTheory

**Module**: `agents.quantum_game_theory`

Physics-inspired game theory for Blue/Red team simulations.

```python
from agents.quantum_game_theory import (
    ClassicalGameEngine,
    QuantumInspiredGameEngine,
    BlueRedTeamSimulator
)

# Classical game
classical = ClassicalGameEngine(
    strategy_sizes=(3, 3),
    payoff_a=[[3, 0, 5], [1, 2, 1], [0, 1, 4]],
    payoff_b=[[3, 1, 0], [0, 2, 1], [5, 1, 4]]
)
eq = classical.find_nash_equilibrium()

# Quantum-inspired game
quantum = QuantumInspiredGameEngine(
    strategy_sizes=(3, 3),
    payoff_a=payoff_a,
    payoff_b=payoff_b
)
quantum.apply_entanglement(strength=0.5)
result = quantum.measure_strategy()

# Blue/Red team simulation
simulator = BlueRedTeamSimulator()
results = simulator.run_simulation(rounds=100)
```

---

## ML Core APIs

### PluginSandbox

**Module**: `src.codex_ml.plugins.plugin_sandbox`

Secure plugin execution environment.

```python
from codex_ml.plugins.plugin_sandbox import PluginSandbox, PluginMetadata

# Create sandbox
sandbox = PluginSandbox(
    max_memory_mb=512,
    max_execution_time=30.0,
    allowed_imports=["numpy", "pandas"]
)

# Register plugin
sandbox.register_plugin(
    name="my_plugin",
    module_path="plugins/my_plugin.py"
)

# Execute plugin
result = sandbox.execute_plugin(
    name="my_plugin",
    method="process",
    args={"data": input_data}
)

# Check quarantine status
metadata = sandbox.get_plugin_metadata("my_plugin")
if metadata.is_quarantine_expired(quarantine_duration=3600):
    sandbox.restore_plugin("my_plugin")
```

---

### HARIntegration

**Module**: `src.codex_ml.integrations.har_integration`

HTTP Archive (HAR) recording and replay.

```python
from codex_ml.integrations.har_integration import (
    HARRecorder,
    HARCache,
    HARReplayer
)

# Record HTTP transactions
recorder = HARRecorder()
recorder.start_recording()
# ... make HTTP requests ...
har_log = recorder.stop_recording()
recorder.save("transactions.har")

# Cache responses
cache = HARCache(cache_dir=".har_cache")
cache.cache_response(request, response)
cached = cache.get_cached_response(request)

# Replay transactions
replayer = HARReplayer("transactions.har")
for entry in replayer.entries:
    response = replayer.replay_entry(entry)
```

---

### Scalability Utilities

**Module**: `src.codex_ml.utils.scalability`

Performance and scalability utilities.

```python
from codex_ml.utils.scalability import (
    LRUCache,
    RateLimiter,
    CircuitBreaker,
    LoadBalancer,
    ResourcePool,
    PerformanceMonitor
)

# LRU Cache
cache = LRUCache(max_size=1000)
cache.put("key", "value")
value = cache.get("key")

# Rate Limiter
limiter = RateLimiter(rate=100, per_seconds=1)
if limiter.acquire():
    # Process request
    pass

# Circuit Breaker
breaker = CircuitBreaker(failure_threshold=5, reset_timeout=30)
with breaker:
    # Protected operation
    result = risky_operation()

# Load Balancer
balancer = LoadBalancer(
    endpoints=["server1", "server2", "server3"],
    strategy="round_robin"
)
endpoint = balancer.get_endpoint()

# Resource Pool
pool = ResourcePool(factory=create_connection, max_size=10)
with pool.acquire() as conn:
    conn.execute(query)

# Performance Monitor
monitor = PerformanceMonitor()

@monitor.timed("operation_name")
def my_operation():
    pass

stats = monitor.get_stats("operation_name")
```

---

## Integration APIs

### Event System

**Module**: `src.codex_ml.events.base`

Event publishing and subscription.

```python
from codex_ml.events import EventPublisher, Event

# Create publisher
publisher = EventPublisher()

# Subscribe to events
def on_model_trained(event: Event):
    print(f"Model trained: {event.data}")

publisher.subscribe("model.trained", on_model_trained)

# Publish events
publisher.publish(Event(
    type="model.trained",
    data={"model_id": "model_001", "accuracy": 0.95}
))
```

---

## Utility APIs

### Stub Cleanup

**Module**: `scripts.stub_cleanup`

AST-based stub detection and cleanup.

```python
from scripts.stub_cleanup import (
    analyze_file,
    analyze_directory,
    generate_report,
    StubDetector
)

# Analyze single file
result = analyze_file(Path("src/module.py"))
print(f"Found {result.total_stubs} stubs")

# Analyze directory
result = analyze_directory(
    Path("src/"),
    exclude_abstract=True,
    exclude_patterns=["**/test_*.py"]
)

# Generate report
report = generate_report(result, format="markdown")
print(report)
```

---

## Error Handling

All APIs use consistent error handling:

```python
from codex_ml.exceptions import (
    CodexError,          # Base exception
    PluginError,         # Plugin-related errors
    ValidationError,     # Input validation errors
    ConfigurationError,  # Configuration errors
    ResourceError,       # Resource allocation errors
)

try:
    result = api_call()
except ValidationError as e:
    logger.error(f"Invalid input: {e}")
except PluginError as e:
    logger.error(f"Plugin failed: {e}")
except CodexError as e:
    logger.error(f"Operation failed: {e}")
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CODEX_SESSION_ID` | Session identifier | Auto-generated |
| `CODEX_LOG_DB_PATH` | SQLite database path | `.codex/logs.db` |
| `CODEX_FORCE_CPU` | Disable GPU | `0` |
| `CODEX_BATCH_SIZE` | Default batch size | `32` |
| `CODEX_MAX_MEMORY_MB` | Memory limit | `4096` |

---

## Versioning

APIs follow semantic versioning:
- **Major**: Breaking changes
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes

---

## See Also

- [Architecture Blueprint](../ARCHITECTURE_BLUEPRINT.md)
- [Contributing Guide](./CONTRIBUTING.md)
- [Quick Start](../onboarding/QUICK_START.md)
