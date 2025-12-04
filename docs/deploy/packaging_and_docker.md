# Packaging and local Docker usage

This repository ships offline-first packaging metadata (see `pyproject.toml`) and a minimal local Docker recipe.

## Local installation

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e .
# Optional extras
pip install -e .[ml]
```

## Local Docker image

A CPU-only image can be built from `Dockerfile.local` without pulling GPUs or remote registries:

```bash
docker build -f Dockerfile.local -t codex-local .
docker run --rm -p 8000:8000 codex-local codex_cli quick-audit
```

Use bind mounts to persist runs and reports:

```bash
docker run --rm -v $(pwd)/runs:/app/runs codex-local codex-train --help
```

## Notes

- No GitHub Actions or remote registries are required; all steps are offline.
- The image keeps dependencies minimal; install extras on the host when heavy ML runtimes are needed.
