# Integration Guide
**Last Updated:** 2026-07-11
**Version:** v0.2.0

## Embedding in an External Repository

### Profile-Specific Integration

Choose the appropriate profile for your deployment:

#### **Core Profile** — Lightweight, Offline-First

```bash
# Install
pip install codex-ml[core]

# Minimal setup (configuration only)
from codex_ml.config import Config
from codex_ml.safety import PromptSanitizer

config = Config.from_env()
sanitizer = PromptSanitizer(strict_mode=True)
```

**Use when:** Building edge devices, offline environments, or minimal integrations with zero external dependencies beyond stdlib.

#### **Runtime Profile** — Production Inference & APIs

```bash
# Install
pip install codex-ml[runtime]

# Full inference + pattern learning
from codex_ml.serving import ModelServer
from cognitive_brain import Planner, MemoryManager

server = ModelServer(config=config)
planner = Planner(memory=MemoryManager())
```

**Use when:** Deploying to production, building APIs, running inference at scale, or pattern-learning systems.

#### **Full Profile** — Development & Testing

```bash
# Install
pip install codex-ml[full]

# All features: training, testing, admin tools
from codex_ml import train, evaluate, serve
from codex_ml.cli import main as cli_main
```

**Use when:** Developing locally, running full test suites, or building custom training pipelines.

### Integration Steps (All Profiles)

1. Install desired profile into project virtualenv.
2. Copy `.codex/network-policy.yaml` and keep fail-closed defaults.
3. Configure local persistence paths for session data.
4. Run smoke checks before enabling optional integrations.

## Cognitive Brain API Surface (Stable)

- `ObservationData`
- `OrientationResult`
- `Decision`
- `ActionResult`
- `Planner`
- `MemoryInterface`
- `MemoryPattern`
- `QuantumMemoryManager`
- `Pattern`
- `PatternSet`

## Example Import

```python
from cognitive_brain import ActionResult, Decision, ObservationData, OrientationResult, Planner
```

If your environment uses a prefixed package layout, resolve imports via your
installed distribution path (for example, through repository `src/`-mapped
packages) and keep this API surface consistent.

## Safe Networking Integration

Always gate outbound calls:

```python
from safety.network_policy import enforce_network_policy

enforce_network_policy("https://approved-host.example")
```
