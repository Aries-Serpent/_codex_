# Codex ML Quick Start by Profile

This guide shows how to get started with each of Codex ML's three installation profiles.

## Installation

All profiles use the same `codex_ml-0.1.0-py3-none-any.whl` wheel package, with optional dependencies selected at install time.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

---

## 🔵 Core Profile: Lightweight & Offline-First (8-15 MB)

**Use when:** Building edge devices, offline environments, or minimal deployments with zero external dependencies beyond stdlib.

### Installation

```bash
# From wheel file
python -m pip install codex_ml-0.1.0-py3-none-any.whl

# Or explicitly with core profile
python -m pip install 'codex-ml[core]'
```

### What's Included

- Configuration management (Hydra, OmegaConf)
- CLI interface (Typer)
- Code parsing (libcst, parso, tree-sitter)
- Safety enforcement (cryptography, secure defaults)
- Security policies (network isolation)

### Quick Example

```python
from codex_ml.config import Config
from codex_ml.safety import PromptSanitizer
from pathlib import Path

# Load configuration
config = Config.from_env()

# Create sanitizer (core feature)
sanitizer = PromptSanitizer(strict_mode=True)

# Use it
try:
    result = sanitizer.sanitize("user input here")
    print(f"Sanitized: {result}")
except ValueError as e:
    print(f"Unsafe input: {e}")

# Access configuration
print(f"Config loaded from: {config.config_path}")
```

### Verify Installation

```bash
# Check what's installed
pip show codex-ml
python -c "from codex_ml.config import Config; print('Core profile OK')"
```

---

## 🟢 Runtime Profile: Production Inference & APIs (20-35 MB)

**Use when:** Deploying to production, building APIs, running inference at scale, or pattern-learning systems.

### Installation

```bash
python -m pip install 'codex-ml[runtime]'
```

### What's Included (in addition to core)

- PyTorch & Transformers (inference)
- SentenceTransformers (embeddings)
- Ray Serve (distributed inference)
- FastAPI (API servers)
- Datasets (data loading)
- Cognitive Brain OODA loop

### Quick Example

```python
from codex_ml.config import Config
from cognitive_brain import Planner, MemoryInterface, ObservationData, Decision
from codex_ml.serving import ModelServer
import asyncio

async def main():
    # Initialize planner with memory
    memory: MemoryInterface = None  # Will use default memory manager
    planner = Planner(memory=memory)
    
    # Create observation
    observation = ObservationData(
        context="User query: What is machine learning?",
        metadata={"source": "api", "user_id": "123"}
    )
    
    # Execute OODA loop
    orientation = planner.observe(observation)
    decision = planner.decide(orientation)
    result = planner.act(decision)
    
    print(f"Decision: {result.action}")
    print(f"Confidence: {result.confidence}")
    
    # Start inference server
    config = Config.from_env()
    server = ModelServer(config=config)
    await server.start(host="0.0.0.0", port=8000)

asyncio.run(main())
```

### Verify Installation

```bash
# Check dependencies
pip show torch transformers ray
python -c "from cognitive_brain import Planner; print('Runtime profile OK')"
```

### Start an API Server

```bash
# If your application has a FastAPI server
python -m your_app.api --host 0.0.0.0 --port 8000
```

---

## 🟣 Full Profile: Development & Testing (100+ MB)

**Use when:** Developing locally, running full test suites, building custom training pipelines, or experimenting with all features.

### Installation

```bash
python -m pip install 'codex-ml[full]'
```

### What's Included (everything)

- All core profile features
- All runtime profile features
- Pytest & test utilities
- Jupyter & notebooks
- Model training tools
- Mutation testing
- Documentation generation
- Plugin system

### Quick Example

```python
from codex_ml import train, evaluate
from cognitive_brain import Planner, MemoryPattern, PatternSet
from pathlib import Path
import asyncio

async def main():
    # Full development workflow
    planner = Planner()
    
    # Create pattern library
    patterns = PatternSet(
        patterns=[
            MemoryPattern(
                condition={"type": "query"},
                action={"response": "search"},
                confidence=0.95
            )
        ]
    )
    
    # Train (full profile feature)
    training_config = {
        "model": "sentence-transformers/all-MiniLM-L6-v2",
        "epochs": 3,
        "batch_size": 32
    }
    
    # This is a simplified example - see docs/ml/ for real training pipelines
    print("Training setup complete")
    
    # Evaluate (full profile feature)
    metrics = evaluate(
        dataset="path/to/dataset",
        model=planner,
        metrics=["accuracy", "f1"]
    )
    print(f"Metrics: {metrics}")

asyncio.run(main())
```

### Run Full Test Suite

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific test category
pytest tests/test_training/ -v
```

### Generate Documentation

```bash
# Build local MkDocs site
mkdocs serve

# Or static build
mkdocs build
```

---

## Choosing Your Profile

| Need | Profile | Why |
|------|---------|-----|
| Edge device, offline | **Core** | Minimal footprint, no network |
| Production API | **Runtime** | Everything needed for serving |
| Local development | **Full** | All tools for experimentation |
| Embedded system | **Core** | Only stdlib + essential config |
| Microservice | **Runtime** | FastAPI + inference ready |
| ML research | **Full** | Training, evaluation, experiments |

---

## Profile Migration

### From Core → Runtime

```bash
# Upgrade existing installation
pip install 'codex-ml[runtime]'

# Your code using ObservationData, Decision, etc. will now work
from cognitive_brain import Planner
```

### From Runtime → Full

```bash
# Upgrade for development
pip install 'codex-ml[full]'

# Now test suite and training tools available
pytest tests/
```

### Downgrade (Runtime → Core)

```bash
# Uninstall and reinstall core only
pip uninstall codex-ml -y
pip install 'codex-ml[core]'
```

---

## Offline Installation

All profiles support offline installation. Use `OFFLINE_BOOTSTRAP.sh`:

```bash
./OFFLINE_BOOTSTRAP.sh \
  --wheelhouse ./wheelhouse \
  --artifact ./dist/codex_ml-0.1.0-py3-none-any.whl
```

See [../release/OFFLINE_DEPLOYMENT.md](../release/OFFLINE_DEPLOYMENT.md) for details.

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'torch'"

You need the runtime or full profile:
```bash
pip install 'codex-ml[runtime]'  # or [full]
```

### "ModuleNotFoundError: No module named 'pytest'"

You need the full profile:
```bash
pip install 'codex-ml[full]'
```

### Check Installed Profile

```bash
pip show codex-ml
# Look at the "Location" and check which optional deps are installed
pip list | grep -E "torch|transformers|pytest"
```

### Import Errors After Profile Change

After changing profiles, ensure dependencies are installed:
```bash
pip install --upgrade 'codex-ml[runtime]'  # Fresh install
python -c "from cognitive_brain import Planner; print('OK')"
```

---

## Next Steps

- **Core users:** See [../.codex/archive/misc/INSTALL.md](../.codex/archive/misc/INSTALL.md) for offline deployment
- **Runtime users:** Check [docs/api/reference/INTEGRATION.md](docs/api/reference/INTEGRATION.md) for API integration
- **Full profile:** See [docs/](docs/) for development guides and API reference
- **All users:** Review [README.md](README.md) for overview

---

## Support

- **Documentation:** [docs/](docs/)
- **Issue tracker:** https://github.com/Aries-Serpent/_codex_/issues
- **License:** MIT
