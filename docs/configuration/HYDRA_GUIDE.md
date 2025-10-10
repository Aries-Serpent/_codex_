# [Doc]: Configuration & Overrides Guide (Hydra-Compatible Patterns)
> Generated: 2025-10-10 19:58:59 UTC | Author: mbaetiong
🧠 Roles: [Audit Orchestrator], [Capability Cartographer] ⚡ Energy: 5

## Purpose
Document deterministic, offline-friendly configuration practices compatible with Hydra/OmegaConf patterns while remaining robust without optional dependencies.

## Principles
- Deterministic: Avoid random ordering; prefer explicit defaults.
- Layered: base.yaml → env/cli overrides → experiment.yaml
- Offline: No network-bound resolvers; local file references only.
- Minimal Writes: Configs remain under `configs/`.

## Directory Layout (Suggested)
```text
configs/
├── base.yaml
├── experiment.yaml
└── env/
    ├── dev.yaml
    └── prod.yaml
```

## Base Config Example
```yaml
# configs/base.yaml
trainer:
  seed: 123
  batch_size: 32
  deterministic: true

logging:
  level: INFO
  format: ndjson

paths:
  data_dir: data/
  artifacts_dir: artifacts/
```

## Experiment Overrides
```yaml
# configs/experiment.yaml
trainer:
  batch_size: 64

logging:
  level: DEBUG
```

## Environment Overrides (Optional)
```yaml
# configs/env/dev.yaml
paths:
  data_dir: data/dev/
```

## Composition Order
1) base.yaml
2) env/<env>.yaml (optional)
3) experiment.yaml (optional)
4) Process env vars (last-write-wins)

## CLI Patterns
Recommended CLI flags (if a tool supports them):
```bash
python -m codex_ml.cli.config trainer.seed=42 logging.level=WARNING
```

## Programmatic Merge (Generic YAML)
```python
from pathlib import Path
import yaml

def load_yaml(p: Path) -> dict:
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}

def merge(a: dict, b: dict) -> dict:
    out = dict(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = merge(out[k], v)
        else:
            out[k] = v
    return out

base = load_yaml(Path("configs/base.yaml"))
env_cfg = load_yaml(Path("configs/env/dev.yaml"))
exp = load_yaml(Path("configs/experiment.yaml"))

cfg = merge(base, merge(env_cfg, exp))
```

## Environment Variable Conventions
- TRAINER_SEED → trainer.seed
- TRAINER_BATCH_SIZE → trainer.batch_size
- LOGGING_LEVEL → logging.level

Example:
```bash
export TRAINER_BATCH_SIZE=128
python train.py
```

## Determinism Tips
- Fix random seeds across libs (torch, numpy, random).
- Set deterministic flags (e.g., cudnn.deterministic=true).
- Avoid time-based randomness in configs.

## Validation Checks (Pre-Commit)
- YAML parses successfully (no schema violation).
- Required keys present (trainer.seed, paths.artifacts_dir).
- Disallow duplicate keys (yaml loader with SafeLoader).

## Common Pitfalls
- Overlapping keys with different types (dict vs str).
- Silent override of critical flags (document override policy).
- External resolvers requiring network.

## Offline Safety
- No external includes; only local relative paths.
- Validate all referenced paths exist before runtime.

## Example Minimal Loader (No Hydra Dependency)
```python
import os

def apply_env_overrides(cfg: dict) -> dict:
    new = dict(cfg)
    if "TRAINER_SEED" in os.environ:
        new.setdefault("trainer", {})
        new["trainer"]["seed"] = int(os.environ["TRAINER_SEED"])
    return new
```

## Testing Guidance
- Test YAML parseability.
- Test composition order deterministically.
- Test environment override precedence.

## Quality Gates
- Missing base.yaml → warn.
- Non-deterministic fields in configs → flag.
- Paths not under repo → warn.

## Appendix: Migration to Hydra (Optional)
- Keep YAML shapes compatible with OmegaConf.
- Use defaults list to manage composition.
- Avoid custom resolvers initially.

*End of Guide*
