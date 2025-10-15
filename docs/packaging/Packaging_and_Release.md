# Packaging & Release (Local-First)

This guide covers the local packaging workflow introduced for week 3.

## Build artifacts

```bash
make build    # build wheel + sdist under ./dist/
make wheel    # wheel only
make sdist    # sdist only
```

Each target installs `build` on demand and prints a short listing of the `dist/` directory for quick inspection.

## Local installation

```bash
pip install dist/<artifact>.whl
# or for editable development installs
make install-local
```

`install-local` installs the project in editable mode together with the `dev` and `test` extras so linters and tests are ready to run.

## CLI entry points

The CLI scripts now flow through safe wrappers:

```bash
codex-train --help
python -m codex_ml  # continues to dispatch to the Hydra entrypoint
```

An evaluation CLI stub (`codex-eval`) is present and exits with a helpful message until the implementation lands.

## Optional extras

New optional dependency groups:

- `plugins` – metadata shim for Python < 3.10.
- `dist` – `torch` CPU/CUDA meta-package for distributed helpers.
- `tokenizers` – installs the `tokenizers` library when needed.

These join the existing extras to keep installations explicit and modular.
