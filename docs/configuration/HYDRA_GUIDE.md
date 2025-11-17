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
```text

## Base Config Example
```yaml
# configs/base/base.yaml
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
```text

## Experiment Overrides
```yaml
# configs/experimental/experiment.yaml
trainer:
  batch_size: 64

logging:
  level: DEBUG
```text

## Environment Overrides (Optional)
```yaml
# configs/base/environment/dev.yaml
paths:
  data_dir: data/dev/
```text

## Composition Order
1) base.yaml
2) env/<env>.yaml (optional)
3) experiment.yaml (optional)
4) Process env vars (last-write-wins)

## CLI Patterns
Recommended CLI flags (if a tool supports them):
```bash
python -m codex_ml.cli.config trainer.seed=42 logging.level=WARNING
```text

### Typer bridge and offline defaults

The Typer-based `codex-ml` shim now mirrors Hydra defaults even when the CLI is
invoked in an offline shell. When you pass `--config path/to/train.yaml` the
command applies the same precedence order as Hydra (CLI overrides → config →
built-in defaults). Regression tests under
`tests/codex_ml/test_cli_train_config_bridge.py` load a temporary YAML payload
and assert that:

- YAML-only values (e.g. `training.epochs`, `gradient_accumulation_steps`) are
  propagated into `UnifiedTrainingConfig`.
- Explicit CLI flags such as `--epochs` or `--grad-accum` take priority over
  the YAML defaults.
- Offline toggles (e.g. `--mlflow`, `--wandb`) remain deterministic so you can
  compose reproducible runs without Hydra installed.

Run the focused check with:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/codex_ml/test_cli_train_config_bridge.py -q
```text

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

base = load_yaml(Path("configs/base/base.yaml"))
env_cfg = load_yaml(Path("configs/base/environment/dev.yaml"))
exp = load_yaml(Path("configs/experimental/experiment.yaml"))

cfg = merge(base, merge(env_cfg, exp))
```text

## Environment Variable Conventions
- TRAINER_SEED → trainer.seed
- TRAINER_BATCH_SIZE → trainer.batch_size
- LOGGING_LEVEL → logging.level

Example:
```bash
export TRAINER_BATCH_SIZE=128
python train.py
```text

## Determinism Tips
- Fix random seeds across libs (torch, numpy, random).
- Set deterministic flags (e.g., cudnn.deterministic=true).
- Avoid time-based randomness in configs.
- Programmatic defaults (`codex_ml.cli.config.AppConfig`) keep `training.seed=42`, `training.deterministic=true`, and WAN integrations disabled, enabling reproducible local runs without extra wiring.

## Validation Checks (Pre-Commit)
- YAML parses successfully (no schema violation).
- Required keys present (trainer.seed, paths.artifacts_dir).
- Disallow duplicate keys (yaml loader with SafeLoader).

### Hydra Defaults Audit CLI
- Run `python -m codex_ml.cli.config --audit last --path configs/base/default.yaml` to confirm `_self_` is the trailing entry and no unresolved `${...}` placeholders remain.
- CI/tests exercise the same command through `tests/configuration/test_hydra_validation.py::test_configuration_cli_audit_enforces_self_last` so regressions surface immediately.
- Use `--audit present` for legacy configs that only need `_self_` somewhere in the list.

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
```text

## Testing Guidance
- Test YAML parseability.
- Test composition order deterministically.
- Test environment override precedence.
- Exercise the Typer CLI bridge to guarantee config defaults and CLI overrides
  remain reproducible offline (`pytest tests/codex_ml/test_cli_train_config_bridge.py`).

## Quality Gates
- Missing base.yaml → warn.
- Non-deterministic fields in configs → flag.
- Paths not under repo → warn.

## Appendix: Migration to Hydra (Optional)
- Keep YAML shapes compatible with OmegaConf.
- Use defaults list to manage composition.
- Avoid custom resolvers initially.

*End of Guide*
