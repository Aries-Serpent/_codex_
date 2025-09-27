# Deployment (Docker + Compose)

The deployment workflow is optimised for offline and air-gapped environments. This page
covers packaging with `pyproject.toml`, the CLI entry point, and the Docker images used
for CPU and GPU executions.

## Packaging & installation

The repository now exposes a standards-compliant `pyproject.toml`. Install in editable
mode (recommended for local development) or build a wheel if publishing to an internal
index:

```bash
# Editable install with the ML + logging extras
pip install -e '.[ml,logging]'

# Build an sdist/wheel artefact for archival/offline installs
python -m build
```

The console script `codex-train` resolves to `codex_ml.cli.hydra_main:main`. Invoke it
directly instead of calling `python -m ...`:

```bash
codex-train training.max_epochs=1 data.path=/data/offline
```

Optional extras:

* `ml` – PyTorch, Transformers, Accelerate, PEFT.
* `logging` – TensorBoard, MLflow, and Weights & Biases.
* `dev` – pytest, pytest-cov, pytest-randomly, ruff.

Mix and match extras to fit the local environment (`pip install -e '.[ml,logging,dev]'`).

## Docker images

Two Dockerfiles are provided and pinned to reproducible base images:

* `Dockerfile` – CPU image based on `python:3.10.14-slim`.
* `Dockerfile.gpu` – GPU image based on `nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04`.

Both images create a non-root `appuser`, install the package in editable mode, and expose
`codex-train` as the container entrypoint.

### Build locally

```bash
# CPU build
make codex-image

# GPU build (requires the NVIDIA Container Toolkit)
make codex-image-gpu
```

### Run locally

```bash
# Show CLI usage from the CPU image
make codex-run

# GPU variant (adds --gpus all)
make codex-run-gpu
```

The Make targets mount the repository into `/app` for offline configuration overrides.
Extend the `docker run` command with additional flags (e.g., `-v /models:/models` or
`-e CODEX_DATA_DIR=/data`) as needed.

### Compose / custom orchestration

For bespoke deployments, use the built images in `docker compose` or another orchestrator.
Ensure the CUDA tag matches the host driver when targeting GPUs and prefer multi-stage
pipelines that cache model weights or datasets to local volumes.

## Offline hints

* Pre-download model weights and tokenizer files to a shared volume, then mount that
  directory into `/app/.cache`.
* Bake `pip` wheels into an internal artefact repository or wheelhouse and point
  `pip install` at it with `--no-index --find-links`.
* Keep `CODEX_SAFETY_BYPASS=0` in production; flip to `1` only for controlled offline
  experimentation.

Policy reminder: DO NOT ACTIVATE GitHub Actions or other hosted CI. All checks must run
within the Codex environment or self-hosted infrastructure.
