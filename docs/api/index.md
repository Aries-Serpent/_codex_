# API Reference

Complete API reference for all Cognitive Brain and Codex ML modules.

---

## Quick Start

### Build & View API Docs

| Flag | Default | Effect |
|------|---------|--------|
| SKIP_OPTIONAL | 1 | Hint code to skip optional ML deps |
| FAIL_ON_MISSING | 0 | Strict import gate for doc build |

```bash
# Safe local build
SKIP_OPTIONAL=1 bash scripts/docs_build.sh

# Strict build (use on main merges)
FAIL_ON_MISSING=1 SKIP_OPTIONAL=0 bash scripts/docs_build.sh
```

### Outputs

| Path | Description |
|------|-------------|
| artifacts/docs/ | Generated docs (pdoc if available) |
| artifacts/docs_manifest.sha | SHA256 list for determinism |

---

## Core Modules

### Universal Intelligence Components

#### Universal Task Interface (UTI)

```python
from github.agents.core.universal_intelligence import UniversalTaskInterface, TaskSpec

spec = TaskSpec(
    environment="gridworld",
    initial_state={"x": 0, "y": 0, "goal": {"x": 5, "y": 5}},
    reward_spec={"id": "reward:v1"},
    termination={"max_steps": 100},
)

uti = UniversalTaskInterface(seed=12345)
result = uti.execute_task(spec)
```

#### Key Classes

- **UniversalTaskInterface** - Main entry point for task execution
- **TaskSpec** - Task specification dataclass
- **TaskResult** - Task execution result

#### Environment Adapters

- **EnvironmentAdapter** - Base adapter class
- **GridWorldAdapter** - Grid world environment
- **BanditAdapter** - Multi-armed bandit environment
- **ClassificationAdapter** - Classification task adapter

#### Meta-Policy Router

- **MetaPolicyRouter** - Routes tasks to optimal meta-learning strategies
- **MAMLState** - MAML algorithm state
- **ReptileState** - Reptile algorithm state
- **StrategyPerformance** - Strategy performance metrics
- **DynamicHyperparamTuner** - Hyperparameter tuning
- **StrategyBenchmark** - Strategy benchmarking

#### Abstraction Engine

- **AbstractionEngine** - Concept abstraction and reasoning
- **Concept** - Concept representation
- **Relation** - Relation between concepts
- **Analogy** - Analogical reasoning

#### Grounding Layer

- **GroundingLayer** - Action grounding and validation
- **GroundedAction** - Grounded action representation
- **ActionConstraint** - Action constraints
- **ValidationResult** - Validation result

#### Pattern Store

- **UniversalPatternStore** - Pattern storage and retrieval
- **Pattern** - Pattern representation

#### Safety Monitor

- **SafetyMonitor** - Safety monitoring and enforcement
- **DomainBaseline** - Domain-specific baselines

#### EXP-10 Validation

- **EXP10BenchmarkHarness** - EXP-10 benchmark harness

---

## Building API Documentation

### Quick Start

```bash
# Using nox (recommended - deterministic offline build)
nox -s docs_build

# Or using the build script directly  
bash scripts/docs_build.sh

# Or using the Python tool directly
python tools/build_api_docs.py
```

The generated documentation will be written to `artifacts/docs/api/` (local only, git-ignored).

### Build Options

**Using the shell script (recommended):**

```bash
# Default build (includes all available modules)
bash scripts/docs_build.sh

# Skip modules requiring optional dependencies
SKIP_OPTIONAL=1 bash scripts/docs_build.sh

# Strict mode: fail if any requested modules are missing (CI use)
FAIL_ON_MISSING=1 bash scripts/docs_build.sh

# Combine options
SKIP_OPTIONAL=1 FAIL_ON_MISSING=1 bash scripts/docs_build.sh

# Custom output directory
OUTPUT_DIR=/path/to/output bash scripts/docs_build.sh
```

**Using nox:**

```bash
# Default build
nox -s docs_build

# Skip optional modules
SKIP_OPTIONAL=1 nox -s docs_build

# Strict mode
FAIL_ON_MISSING=1 nox -s docs_build
```

### Build Modes

#### Default Mode
- Includes all importable modules (core + optional ML when installed)
- Gracefully skips unavailable optional modules
- Exit code 0 on success

#### Skip Optional Mode (`SKIP_OPTIONAL=1`)
- Only builds documentation for core modules
- Excludes `codex_ml` and other optional packages
- Faster build, no ML dependencies required
- Ideal for minimal environments

#### Strict Mode (`FAIL_ON_MISSING=1`)
- Fails build if any requested modules are unavailable
- Exit code 3 on missing modules
- Ideal for CI/CD validation
- Ensures complete dependency installation

---

## API Documentation Structure

The API documentation covers the following main modules:

- **codex_ml** - Core ML utilities: training, evaluation, metrics, models
  - `codex_ml.training` - Training engine and loops
  - `codex_ml.eval` - Evaluation runner and metrics
  - `codex_ml.models` - Model factories and wrappers
  - `codex_ml.data` - Data loaders and preprocessing
  - `codex_ml.metrics` - Metrics registry and implementations
  - `codex_ml.plugins` - Plugin system and registries
  - `codex_ml.tracking` - MLflow and experiment tracking
  - `codex_ml.peft` - LoRA/QLoRA adapters (optional)
  - `codex_ml.distributed` - Distributed training utilities (optional)

- **codex.cli** - Command-line interface and entry points
  
- **codex.logging** - Session logging and telemetry

---

## Prerequisites

### Required Dependencies

API documentation generation requires:

- Python 3.11+
- pdoc3 (automatically installed by the build script)

### Optional Dependencies

Some modules require optional dependencies to import successfully:

- **LoRA/PEFT modules**: `peft`, `accelerate`
- **Distributed training**: `torch.distributed`, `accelerate`
- **Metrics**: `nltk`, `rouge-score`, `sacrebleu`

When building in minimal environments, use `--skip-optional` to exclude these modules.

---

## Documentation Standards

### Docstring Format

All public modules, classes, and functions should have docstrings following these conventions:

```python
def example_function(param1: str, param2: int = 0) -> dict:
    """
    Brief one-line summary of the function.
    
    More detailed description if needed. Explain the purpose,
    behavior, and any important notes.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (default: 0)
        
    Returns:
        Dictionary containing result data
        
    Raises:
        ValueError: When param1 is empty
        
    Example:
        >>> result = example_function("test", 42)
        >>> print(result)
        {'status': 'success'}
    """
    ...
```

---

## Viewing Documentation

After building, open the documentation in your browser:

```bash
# On macOS
open artifacts/docs/api/index.html

# On Linux
xdg-open artifacts/docs/api/index.html

# Or use Python's HTTP server
python -m http.server -d artifacts/docs/api 8000
# Then navigate to http://localhost:8000
```

---

## Troubleshooting

### Import Errors During Build

If the build fails due to import errors:

1. **Check optional dependencies**: Use `--skip-optional` to exclude modules requiring optional packages
2. **Install missing packages**: Install the package with extras: `pip install -e .[all]`
3. **Set environment variable**: `CODEX_SKIP_OPTIONAL_IMPORTS=1 python tools/build_api_docs.py`

### pdoc3 Installation Issues

```bash
# Install manually
pip install pdoc3

# Or use a specific version
pip install pdoc3==0.10.0
```

### Empty or Missing Documentation

If modules appear without documentation:

1. Ensure the module has a top-level docstring
2. Check that functions/classes have docstrings
3. Verify the module is in `MODULES_TO_DOCUMENT` in `tools/build_api_docs.py`

---

## Maintenance

### Adding New Modules

To document new modules, edit `tools/build_api_docs.py`:

```python
MODULES_TO_DOCUMENT = [
    "codex_ml",
    "codex.cli",
    "codex.logging",
    "your_new_module",  # Add here
]
```

### CI/CD Integration

The build script is designed for local-only use. To integrate with CI:

1. Add a nox session (already included)
2. Run as part of documentation deployment pipeline
3. Publish artifacts to a documentation hosting service

---

## Related Documentation

- **User Guides**: See `docs/guides/` for tutorials and how-tos
- **Architecture**: See `docs/architecture/` for system design docs
- **Examples**: See `examples/` for code examples
- **Testing**: See `tests/` for usage examples in tests

---

## Helper Functions

- `calculate_safe_quantum_advantage` - Calculate quantum advantage safely
- `estimate_task_complexity` - Estimate task complexity
- `validate_task_spec_schema` - Validate task specification schema

## Constants

- `K1_TARGET` - K1 target value
- `K1_STRETCH_TARGET` - K1 stretch target
- `QUANTUM_ADVANTAGE_TARGET` - Quantum advantage target
- `NEGATIVE_TRANSFER_THRESHOLD` - Negative transfer threshold
- `FORGETTING_THRESHOLD` - Forgetting threshold
- `STRATEGIES` - Available strategies

---

Last updated: 2026-01-17
