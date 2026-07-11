# Quick Start: Cognitive Brain v0.1.0
**Last Updated:** 2026-07-11
**Version:** v0.2.1

Welcome to **Cognitive Brain** — a lightweight AI coordination framework for autonomous agents. Get up and running in 5 minutes.

---

## Installation

### Via PyPI
```bash
pip install aries-serpent-cognitive-brain==0.1.0
```

### Via ZIP Archive
```bash
unzip aries-serpent-cognitive-brain-0.1.0.zip
cd aries-serpent-cognitive-brain-0.1.0
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### Verify
```bash
python -c "from codex.cognitive import brain; print('✓ Installed!')"
```

**Requirements:** Python 3.12+, no external dependencies, works offline

---

## Your First Program (5-minute Walkthrough)

### Basic OODA Loop
```python
from codex.cognitive import brain, AgentContext

# Create context
context = AgentContext(agent_id="my-agent", task="analyze_data")

# Execute OODA cycle
decision = brain.decide(context)
print(f"Decision: {decision.action}")

# Advance to next step
brain.advance("DATA_ANALYSIS", "TASK-001")
```

### Pattern Recognition
```python
from codex.cognitive import brain, LearningFeedback

# Learn pattern
feedback = LearningFeedback(
    pattern_name="optimize_ml",
    context_snapshot={"intent": "optimize", "domain": "ml"},
    outcome="success",
    confidence=0.92
)
brain.learn(feedback)

# Retrieve similar patterns
matches = brain.retrieve_patterns(query="optimize ml tasks")
```

### Quantum Planning
```python
from codex.cognitive import QuantumPlansetEngine, PlanStep, StepStatus

engine = QuantumPlansetEngine(mode="offline")
steps = [
    PlanStep(id="step-1", name="Observe", status=StepStatus.PENDING),
    PlanStep(id="step-2", name="Decide", status=StepStatus.PENDING),
]
result = engine.execute(steps=steps, context={"goal": "optimize"})
```

---

## API Reference (21 Public APIs)

**Entry Point:**
- `brain` — Module singleton for all operations

**Agent Communication (5 APIs):**
- `AgentBrainAPI` — Agent-brain interface
- `AgentSessionContext` — Session state
- `CompletionReport` — Task completion
- `CognitiveBrain` — Core orchestrator
- `AGENT_CAPABILITIES` — Ability registry

**Brain Queries (5 APIs):**
- `AgentBrainInterface` — Query/learn interface
- `AgentContext` — Agent metadata
- `PatternMatch` — Search results
- `LearningFeedback` — Learning signals
- `BrainResponse` — Brain decisions

**Multi-Step Planning (4 APIs):**
- `PlansetOrchestrator` — Workflow orchestrator
- `PlansetRecord` — Execution history
- `PromptSet` — Grouped prompts
- `OrchestrationState` — Workflow state

**Quantum Planning (6 APIs):**
- `QuantumPlansetEngine` — OODA executor
- `QuantumPlanset` — Plan structure
- `PlanStep` — Plan components
- `StepStatus` — Step status enum
- `ImprovementArea` — Optimization targets
- `PhysicsParams` — Tuning parameters

---

## Common Patterns

### Offline Mode (Default)
```python
# No network, no credentials, all local
session = brain.session("agent-id", mode="offline")
decision = brain.decide(context)
```

### Custom Decision Logic
```python
engine = QuantumPlansetEngine(
    improvement_areas=["speed", "accuracy", "cost"]
)
result = engine.execute(steps, context={"budget": 100})
```

### Pattern Learning Loop
```python
# 1. Learn
brain.learn(feedback)

# 2. Retrieve
matches = brain.retrieve_patterns(query)

# 3. Decide
decision = brain.decide(matches)
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ImportError: No module named 'codex.cognitive'` | `pip install aries-serpent-cognitive-brain` |
| `ModuleNotFoundError` | Check Python 3.12+: `python --version` |
| Slow pattern retrieval | Use `limit=10, min_confidence=0.8` |
| Circular dependency | Restart Python / clear `__pycache__` |

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
brain.decide(context)
```

---

## Next Steps

- **[Full Docs](https://aries-serpent.github.io/_codex_/cognitive/)** — Complete reference
- **[Examples](https://github.com/aries-serpent/_codex_/tree/main/examples/cognitive)** — Real-world patterns
- **[Architecture](https://aries-serpent.github.io/_codex_/architecture/)** — How it works
- **[Discussions](https://github.com/aries-serpent/_codex_/discussions)** — Ask questions
- **[Contributing](https://github.com/aries-serpent/_codex_/blob/main/CONTRIBUTING.md)** — Help build

---

## Summary

 **Installation**: PyPI or ZIP archive  
 **First Program**: Working OODA loop  
 **21 APIs**: Complete reference  
 **Code Examples**: Copy-paste ready  
 **Troubleshooting**: Common solutions  
 **Offline**: No network required  

**Ready to build?** Start with examples or dive into full documentation.

---

**Version**: 0.1.0 | **Updated**: 2026-07-09 | **License**: Apache 2.0 | **Python**: 3.12+
