# Configuration Management

All project configuration files live in this directory. The tree is organised by environment (base shared defaults), domain (training, evaluation, deployment), and contributor tooling (development). Each subdirectory contains YAML or structured data that can be composed with Hydra or loaded directly by utilities in `src/codex_ml`.

## Directory Overview

```text
configs/
├── base/                # Shared defaults and cross-domain presets
├── training/            # Training pipelines, data catalogues, sweeps, tokenizers
├── evaluation/          # Evaluation presets, metrics, offline templates
├── deployment/          # Runtime integrations, CRM fixtures, plugin manifests
├── development/         # Local tooling configs (nox, pytest, Makefile, examples)
├── schemas/             # Structured config schema helpers and documentation
└── experimental/        # Legacy or exploratory configuration samples
```

## Common Entry Points

- **Hydra defaults**: `configs/base/hydra.yaml` mirrors the legacy `conf/config.yaml` defaults list.
- **Application defaults**: `configs/base/app.yaml` composes model/data/tokenizer/training fragments for the primary CLI entrypoints.
- **Training**: `configs/training/base.yaml` defines functional trainer defaults. Data fragments live under `configs/training/data/`, and sweeps under `configs/training/sweeps/`.
- **Evaluation**: `configs/evaluation/base.yaml` and `configs/evaluation/offline.yaml` provide online and offline runners. Custom metrics belong in `configs/evaluation/metrics/`.
- **Deployment**: CRM and integration templates (for example Dynamics 365 manifests) live under `configs/deployment/`, including the hhg logistics domain configs in `configs/deployment/hhg_logistics/`.
- **Development tooling**: Local lint/test harnesses live under `configs/development/` (`noxfile.py`, `pytest.ini`, `Makefile`). `make setup` now requires `requirements/lock.txt` and installs dependencies from the lock file plus `requirements/dev.txt --no-deps` to guarantee reproducible toolchains.

## Usage Examples

Compose with Hydra:

```bash
python -m codex_ml.cli.train --config configs/training/base.yaml \
  training.learning_rate=5e-5 training.checkpoint.keep_best_k=2

python -m codex_ml.cli.evaluate --config configs/evaluation/base.yaml

python -m codex_ml.cli.config --audit last --path configs/base/hydra.yaml
```

Tokenizer training:

```bash
codex tokenizer train --config configs/training/tokenization/base.yaml
```

## Adding New Configurations

1. Choose the correct domain directory (training/evaluation/deployment/development/experimental).
2. Prefer descriptive filenames (for example `gpu.yaml`, `offline.yaml`, `debug.yaml`).
3. Document new configuration surfaces in `docs/` when they introduce CLI flags or defaults.
4. Update tests or automation that reference explicit config paths.

## Validation

- Run `pytest tests/configuration` to ensure all YAML parses cleanly.
- Optional: `python -m codex_ml.cli.config --info defaults` to verify Hydra defaults order.

For schema helpers see [`configs/schemas/README.md`](schemas/README.md).
