# Cognitive Brain Core API Documentation

Welcome to the **Cognitive Brain Core API Documentation**!

## Quick Links

- [Complete API Reference](api/index.md)
- [Getting Started](guides/quickstart.md)
- [Examples](guides/examples.md)
- [Changelog](CHANGELOG.md)

## Phase 8.7: Universal Intelligence

Complete meta-learning framework with 170 tests.

**Components:**
- Universal Task Interface
- Meta-Policy Router (MAML/Reptile)
- Abstraction Engine
- Grounding Layer
- Pattern Store
- Safety Monitor
- EXP-10 Validation

## Installation

\`\`\`bash
pip install -e .
\`\`\`

## Quick Example

\`\`\`python
from github.agents.core.universal_intelligence import UniversalTaskInterface, TaskSpec

spec = TaskSpec(
    environment="gridworld",
    initial_state={"x": 0, "y": 0, "goal": {"x": 5, "y": 5}},
    reward_spec={"id": "reward:v1"},
    termination={"max_steps": 100},
)

uti = UniversalTaskInterface(seed=12345)
result = uti.execute_task(spec)
\`\`\`
