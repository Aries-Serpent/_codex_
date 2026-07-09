# Quick Start: Cognitive Brain v0.1.0

Welcome to the **Cognitive Brain** — a lightweight, self-contained AI coordination and decision-making framework designed for autonomous agents and intelligent systems. This guide will get you up and running in 5 minutes.

---

## Installation

### Via PyPI (Recommended)

```bash
pip install aries-serpent-cognitive-brain==0.1.0
```

**System Requirements:**
- Python 3.12+
- No external dependencies
- Works on Linux, macOS, and Windows

### Via ZIP Archive (Offline Installation)

1. Download the `.zip` archive and extract:
   ```bash
   unzip aries-serpent-cognitive-brain-0.1.0.zip
   cd aries-serpent-cognitive-brain-0.1.0
   ```

2. Add to your Python path:
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
   ```

3. Or install in development mode:
   ```bash
   pip install -e .
   ```

### Verify Installation

```bash
python -c "from codex.cognitive import brain; print('✓ Cognitive Brain v0.1.0 installed successfully!')"
```

---

## Your First Program (5-minute Walkthrough)

### Basic OODA Loop Execution

The Cognitive Brain implements the OODA (Observe, Orient, Decide, Act) loop for intelligent decision-making:

```python
from codex.cognitive import brain, AgentContext

# Create agent context with initial state
context = AgentContext(
    agent_id="my-agent",
    task="analyze_data",
    environment="offline"
)

# Get session for this agent
session = brain.session("my-agent")

# Execute OODA cycle
decision = brain.decide(context)
print(f"Decision: {decision.action}")
print(f"Confidence: {decision.confidence}")

# Advance to next step
brain.advance("DATA_ANALYSIS", "TASK-001")
```

### Pattern Recognition Example

Learn patterns from experience:

```python
from codex.cognitive import brain, LearningFeedback

# Record successful pattern
feedback = LearningFeedback(
    pattern_name="user_intent",
    context_snapshot={"intent": "optimize", "domain": "ml"},
    outcome="success",
    confidence=0.92
)

# Store pattern for future use
brain.learn(feedback)

# Later, retrieve similar patterns
matches = brain.retrieve_patterns(query="optimize ml tasks")
for match in matches:
    print(f"Pattern: {match.name} (confidence: {match.score})")
```

### Custom Decision Logic

Integrate your own decision-making:

```python
from codex.cognitive import QuantumPlansetEngine, PlanStep, StepStatus

# Create quantum planset engine
engine = QuantumPlansetEngine(mode="offline")

# Define plan steps
steps = [
    PlanStep(id="step-1", name="Observe", status=StepStatus.PENDING),
    PlanStep(id="step-2", name="Orient", status=StepStatus.PENDING),
    PlanStep(id="step-3", name="Decide", status=StepStatus.PENDING),
    PlanStep(id="step-4", name="Act", status=StepStatus.PENDING),
]

# Execute quantum planset
result = engine.execute(steps=steps, context={"goal": "optimize_performance"})
print(f"Plan execution result: {result}")
```

---

## API Reference (21 Public APIs)

### Core Singleton Entry Point

| API | Purpose | When to Use |
|-----|---------|-----------|
| **`brain`** | Module-level singleton for all agent operations | Always; your main entry point |

### Agent Brain APIs (Agent-Brain Communication)

| API | Purpose | When to Use |
|-----|---------|-----------|
| **`AgentBrainAPI`** | Standard interface for agent-brain communication | Agents requesting decisions or context |
| **`AgentSessionContext`** | Session state and context metadata | Maintaining agent session across calls |
| **`CompletionReport`** | Task completion record with metrics | Reporting task success/failure to brain |
| **`CognitiveBrain`** | Main brain coordination engine | Core orchestration and decision-making |
| **`AGENT_CAPABILITIES`** | Registry of agent abilities and constraints | Discovering what agents can do |

### Brain Interface (Query and Learning)

| API | Purpose | When to Use |
|-----|---------|-----------|
| **`AgentBrainInterface`** | Query/learn interface for brain state | Custom integrations with brain |
| **`AgentContext`** | Agent metadata and execution context | Setting up agent environment |
| **`PatternMatch`** | Retrieved pattern with similarity score | Processing pattern search results |
| **`LearningFeedback`** | Learning signal for pattern store | Recording successes/failures |
| **`BrainResponse`** | Brain's response to agent query | Parsing brain decisions |

### Planset Orchestration (Multi-Step Planning)

| API | Purpose | When to Use |
|-----|---------|-----------|
| **`PlansetOrchestrator`** | Orchestrates multi-step prompt chains | Complex workflows with dependencies |
| **`PlansetRecord`** | Historical planset execution record | Auditing past decisions |
| **`PromptSet`** | Grouped prompts for coordinated execution | Batch processing related tasks |
| **`OrchestrationState`** | Current state of orchestration workflow | Tracking multi-step progress |

### Quantum Planset Engine (OODA Loop Execution)

| API | Purpose | When to Use |
|-----|---------|-----------|
| **`QuantumPlansetEngine`** | OODA loop executor with quantum-inspired optimization | Complex decision-making |
| **`QuantumPlanset`** | Plan structure with quantum physics properties | Advanced planning scenarios |
| **`PlanStep`** | Individual step in a quantum planset | Defining plan components |
| **`StepStatus`** | Status enum for plan steps | Tracking step progress |
| **`ImprovementArea`** | Identified improvement opportunities | Optimization and refinement |
| **`PhysicsParams`** | Physics-inspired parameters for planning | Fine-tuning decision quality |

---

## Common Patterns

### Offline-Only Mode (No Network)

```python
from codex.cognitive import brain

# Initialize in offline mode (default)
# All operations are local to your machine
session = brain.session("my-agent", mode="offline")

# No external API calls, no credentials needed
decision = brain.decide(context)
```

### Custom Decision Logic

```python
from codex.cognitive import QuantumPlansetEngine

# Initialize with custom physics parameters
engine = QuantumPlansetEngine(
    mode="offline",
    improvement_areas=["speed", "accuracy", "cost"]
)

# Execute with custom context
result = engine.execute(
    steps=your_steps,
    context={"budget": 100, "deadline": "2026-07-12"}
)
```

### Pattern Learning Workflow

```python
from codex.cognitive import brain, LearningFeedback

# 1. Define feedback
feedback = LearningFeedback(
    pattern_name="user_request",
    context_snapshot=context_dict,
    outcome="success",
    confidence=0.95
)

# 2. Learn the pattern
brain.learn(feedback)

# 3. Later, retrieve similar patterns
matches = brain.retrieve_patterns(query="similar_request")

# 4. Use for decision-making
decision = brain.decide(matches)
```

### Caching and Persistence

```python
# Cognitive Brain automatically caches:
# - Pattern matches (in-memory)
# - Session state (SQLite)
# - Decision history (for learning)

# No manual configuration needed — just use it!
```

---

## Troubleshooting

### ImportError: No module named 'codex.cognitive'

**Solution:**
```bash
# Verify installation
pip list | grep aries-serpent

# If missing, reinstall
pip install aries-serpent-cognitive-brain

# If using ZIP archive, ensure PYTHONPATH is set
export PYTHONPATH="${PYTHONPATH}:/path/to/extracted/archive/src"
```

### ModuleNotFoundError: No module named 'codex'

**Solution:**
- Ensure you're using Python 3.12+: `python --version`
- Verify installation: `python -c "from codex.cognitive import brain"`
- Check Python path: `python -c "import sys; print(sys.path)"`

### Circular Dependency Detected

**Solution:**
- Restart Python interpreter: `python -c "..." && python -c "..."`
- Clear import cache: `find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null`
- For notebooks: restart kernel

### Performance Optimization Tips

**Issue:** Slow pattern retrieval on large datasets

**Solutions:**
```python
# 1. Use indexed query (faster)
matches = brain.retrieve_patterns(
    query="my_pattern",
    limit=10,  # Limit results
    min_confidence=0.8  # Filter early
)

# 2. Batch operations
results = [
    brain.retrieve_patterns(q)
    for q in batch_of_queries
]

# 3. Use offline mode (faster)
session = brain.session("agent", mode="offline")
```

### Enable Debug Logging

```python
import logging

# Enable debug output
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("codex.cognitive")
logger.setLevel(logging.DEBUG)

# Now run your code
brain.decide(context)
```

---

## Next Steps

### 📚 Learn More
- **[Full Documentation](https://aries-serpent.github.io/_codex_/cognitive/)** — Complete API reference, architecture, internals
- **[Examples Repository](https://github.com/aries-serpent/_codex_/tree/main/examples/cognitive)** — Real-world usage patterns
- **[Architecture Guide](https://aries-serpent.github.io/_codex_/architecture/)** — How Cognitive Brain works under the hood

### 🤝 Get Help
- **[GitHub Discussions](https://github.com/aries-serpent/_codex_/discussions)** — Ask questions, share ideas
- **[Issue Tracker](https://github.com/aries-serpent/_codex_/issues)** — Report bugs or request features
- **[Contributing Guide](https://github.com/aries-serpent/_codex_/blob/main/CONTRIBUTING.md)** — Help build Cognitive Brain

### 🚀 Advanced Topics
- **[Quantum Planset Engine](./docs/quantum_planset.md)** — OODA loop optimization
- **[Pattern Store](./docs/pattern_store.md)** — Building learning systems
- **[Agent Integration](./docs/agent_integration.md)** — Integrating with your agents
- **[Session Management](./docs/session_management.md)** — Managing agent sessions

---

## Summary

You're now ready to use the Cognitive Brain! Here's what you learned:

✅ **Installation**: 2 options (PyPI or ZIP)  
✅ **First Program**: Working OODA loop in 5 minutes  
✅ **API Overview**: 21 APIs organized by use case  
✅ **Common Patterns**: Copy-paste code snippets  
✅ **Troubleshooting**: Solutions to common issues  
✅ **Next Steps**: Where to learn more  

**Ready to build intelligent agents?** Start with the examples or dive into the full documentation.

---

**Version**: 0.1.0 | **Updated**: 2026-07-09 | **License**: Apache 2.0
