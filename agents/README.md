# Autonomous Agent System (`agents/`)

**Purpose**: Autonomous AI agents with physics-inspired optimization, workflow navigation, and quantum-inspired decision making.

**Last Updated**: Previous Cycle-12-30  
**Version**: 2.0.0  
**Status**: 🟢 Production Ready

---

## 📚 Quick Navigation

- **New to agents?** → Start with [Key Components](#-key-components)
- **Building an agent?** → See [Development Standards](#-development-standards)
- **Contributing?** → Check [Normalization Checklist](NORMALIZATION_CHECKLIST.md)
- **Integration?** → View [Usage Examples](#-usage-examples)

---

## 📁 Structure

```
agents/
├── workflow_navigator.py          # Tokenized workflow execution
├── quantum_game_theory.py         # Quantum-inspired decisions
├── physics_orchestrator.py        # 6 physics paradigms orchestration
├── advanced_physics_calculators.py # Chaos, fractal, fluid, EM, wave, relativity
├── mental_mapping.py              # Context tracking & state management
├── code_analyzer.py               # Static code analysis
├── exceptions.py                  # Agent-specific exceptions
└── TOKENIZED_WORKFLOWS.md         # Workflow catalog
```

---

## 🚀 Key Components

### 1. **WorkflowNavigator** (`workflow_navigator.py`)
Tokenized workflow execution engine.

**Usage**:
```python
from agents.workflow_navigator import WorkflowNavigator

navigator = WorkflowNavigator()
navigator.execute('AUDIT_EXEC')  # Run full audit pipeline
navigator.execute('DOC_GEN')     # Generate documentation
```

**Tokens**: `audit`, `decide`, `docs`, `organize`, `review`, `heal`

**Documentation**: [TOKENIZED_WORKFLOWS.md](TOKENIZED_WORKFLOWS.md)

### 2. **Quantum Game Theory** (`quantum_game_theory.py`)
Quantum-inspired decision making and optimization.

**Features**:
- Quantum state representations
- Superposition-based decision exploration
- Entanglement for coordinated decisions
- Measurement-based action selection

**API**:
- `QuantumStrategy` - Strategy representation
- `QuantumDecision` - Decision making with coherence
- `StrategyState(strategies, weights)` - Weighted strategy combinations

### 3. **Physics Orchestrator** (`physics_orchestrator.py`)
6 physics paradigms for optimization.

**Paradigms**:
1. **Chaos Theory** - Sensitivity and bifurcation analysis
2. **Fractal Geometry** - Self-similar pattern recognition
3. **Fluid Dynamics** - Flow optimization
4. **Electromagnetic Fields** - Field-based interactions
5. **Wave Propagation** - Wave-based coordination
6. **Relativity** - Spacetime-aware scheduling

**Usage**:
```python
from agents.physics_orchestrator import PhysicsOrchestrator

orchestrator = PhysicsOrchestrator()
result = orchestrator.optimize(task, context)
```

### 4. **Advanced Physics Calculators** (`advanced_physics_calculators.py`)
Detailed physics calculations implementing standard equations.

**Components**:
- `ChaosAnalyzer` - Lyapunov exponents, bifurcation
- `FractalCalculator` - Box-counting dimension
- `FluidChannel` - Reynolds number, Navier-Stokes
- `EMFieldSolver` - Poisson equation for EM fields
- `WavePropagator` - Wave equation solver
- `RelativityScheduler` - Lorentz transformations

**Equations**: All use standard physics formulations (Lyapunov, Reynolds, Poisson, wave equation, Lorentz)

### 5. **Mental Mapping** (`mental_mapping.py`)
Context tracking and state management for agents.

**Features**:
- Deterministic timestamp abstraction
- Context persistence
- State tracking
- Memory management

**API**:
```python
from agents.mental_mapping import get_timestamp, set_clock, reset_clock

# Deterministic timestamps for tests
set_clock("Previous Cycle-01-01T00:00:00Z")
timestamp = get_timestamp()
reset_clock()
```

### 6. **Code Analyzer** (`code_analyzer.py`)
Static code analysis capabilities for agents.

**Features**:
- AST parsing
- Complexity analysis
- Pattern detection
- Quality metrics

---

## 🤖 Agent Architecture

### Design Philosophy
- **Autonomous**: Self-directed with minimal human intervention
- **Physics-Inspired**: Leverage natural optimization patterns
- **Context-Aware**: Maintain state across operations
- **Adaptive**: Learn and improve from feedback

### Workflow Execution
```
Request → WorkflowNavigator → Agent Orchestration
  ↓
Task Execution (with physics optimization)
  ↓
Context Tracking (via mental_mapping)
  ↓
Result Verification → State Persistence
```

### Integration Points
- **Codex Pipeline**: Agents can trigger ingestion, analysis, transformation
- **MCP System**: Agents can package code for ChatGPT
- **CI/CD**: Agents can manage workflows and deployments
- **Documentation**: Agents can generate and update docs

---

## 🎯 Tokenized Workflows

Quick access tokens for common operations:

| Token | Workflow | Description |
|-------|----------|-------------|
| `audit` | AUDIT_EXEC | Full audit pipeline |
| `decide` | DECISION_FLOW | Decision making process |
| `docs` | DOC_GEN | Documentation generation |
| `organize` | REPO_ORGANIZE | Repository organization |
| `review` | CODE_REVIEW | Code review workflow |
| `heal` | SELF_HEAL | Self-healing operations |

**Full Catalog**: [TOKENIZED_WORKFLOWS.md](TOKENIZED_WORKFLOWS.md)

---

## 🔧 Development Standards

### Naming Conventions

**Files**: Use `snake_case.py`
```python
workflow_navigator.py  # ✅ Correct
WorkflowNavigator.py   # ❌ Wrong
```

**Classes**: Use `PascalCase`
```python
class WorkflowNavigator:  # ✅ Correct
class workflow_navigator:  # ❌ Wrong
```

**Functions/Methods**: Use `snake_case`
```python
def execute_workflow():  # ✅ Correct
def ExecuteWorkflow():   # ❌ Wrong
```

### Entry Points

**Standard entry points** for executable agents:
- `.execute()` - For workflow-style agents
- `.run()` - For service-style agents  
- `.optimize()` - For optimization agents
- `.decide()` - For decision-making agents

### Type Hints

**Required** for all public APIs:
```python
from typing import Optional, List, Dict, Union

def execute_workflow(
    workflow_id: str,
    context: Optional[Dict[str, Any]] = None
) -> WorkflowResult:
    """Execute workflow with context."""
    ...
```

**Current coverage**: 85% (target: 100%)

### Error Handling

**Use specific exceptions** from `agents.exceptions`:
```python
from agents.exceptions import WorkflowError, AgentError

try:
    result = agent.execute(task)
except WorkflowError as e:
    logger.error(f"Workflow failed: {e}")
    raise
except Exception as e:
    logger.exception("Unexpected error")
    raise AgentError(f"Agent failure: {e}") from e
```

**Avoid bare except** - Use specific exception types or log context.

### Documentation

**Required docstrings**:
```python
def execute_workflow(workflow_id: str, context: Optional[Dict] = None) -> WorkflowResult:
    """
    Execute a registered workflow with optional context.
    
    Args:
        workflow_id: Unique workflow identifier
        context: Optional execution context with parameters
        
    Returns:
        WorkflowResult with status and outputs
        
    Raises:
        WorkflowError: If workflow execution fails
        ValueError: If workflow_id is invalid
        
    Example:
        >>> navigator = WorkflowNavigator()
        >>> result = navigator.execute_workflow('AUDIT_EXEC')
        >>> print(result.status)
        'success'
    """
    ...
```

**Docstring format**: Google style (preferred)

### Testing Requirements

**All agents must have**:
- Unit tests (>80% coverage)
- Integration tests where applicable
- Property-based tests for complex logic
- Deterministic test timestamps (use `mental_mapping`)

**Example**:
```python
from agents.mental_mapping import set_clock, reset_clock

def test_agent_with_timestamp():
    set_clock("Previous Cycle-01-01T00:00:00Z")
    try:
        result = agent.execute_with_timestamp()
        assert result.timestamp == "Previous Cycle-01-01T00:00:00Z"
    finally:
        reset_clock()
```

### Code Quality

**Required checks before commit**:
```bash
# Lint
ruff check agents/

# Type check
mypy agents/

# Format
black agents/
isort agents/

# Test
pytest tests/agents/ -v
```

**See also**: [Normalization Checklist](NORMALIZATION_CHECKLIST.md)

---

## 🔧 Development

### Running Tests
```bash
# Agent tests
pytest tests/agents/

# Specific agent
pytest tests/agents/test_workflow_navigator.py

# With property-based testing
pytest tests/agents/test_property_based.py
```

### Best Practices
1. Use `hasattr()` guards before calling optional methods
2. Use `mental_mapping` for deterministic timestamps in tests
3. Leverage `StrategyState(strategies=...)` API correctly
4. Use `DecisionState(coherence=...)` not `confidence`

---

## 📚 Documentation

- [Tokenized Workflows](TOKENIZED_WORKFLOWS.md) - Workflow catalog
- [Advanced Physics Guide](../docs/ADVANCED_PHYSICS_GUIDE.md) - Physics equations
- [Agent Guidelines](../docs/agent/OPERATIONAL_GUIDELINES.md) - Operational guide
- [Cognitive Map](../docs/system/CODEBASE_COGNITIVE_MAP.md) - System architecture

---

## 🚀 Genesis Protocol

**Status**: Templates ready, awaiting secret injection

**Files**:
- `.codex/autonomous_agent.yaml` - Agent configuration
- `.codex/guardrails.md` - Operational policies
- `scripts/autonomous_agent.py` - Agent orchestrator (SAFE_MODE=True)

**Setup**: See [Genesis Setup Guide](../docs/admin/GENESIS_SETUP_GUIDE.md)

---

## 🤝 Contributing

See [Contributing Guide](../docs/CONTRIBUTING.md) for development workflow.

---

**Owner**: Agent Development Team  
**Last Updated**: Previous Cycle-12-30
