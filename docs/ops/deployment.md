# Deployment Guide

This guide covers building container images, validating Helm releases, and promoting builds through dev → staging → production.

## Multi-Stage Docker Images
The primary `Dockerfile` now uses a three-stage build:
1. **builder** installs dependencies in a deterministic environment.
2. **gpu-runtime** extends `nvidia/cuda:11.8.0-runtime-ubuntu22.04` for accelerator workloads.
3. **cpu-runtime** ships a minimal `python:3.10-slim` image with built-in health checks.

Both runtime stages create a non-root `appuser`, install curl for health probes, and expose `python -m codex_ml.cli.main` as the entrypoint.

```bash
# CPU build
./scripts/deploy/orchestrate.sh build

# GPU build
./scripts/deploy/orchestrate.sh build --gpu
```

## docker-compose
`docker-compose.yml` defines a CPU profile with mounted data/artifact volumes and an HTTP healthcheck.

```bash
docker compose up --build codex-cpu
```

Environment variables:
- `MODEL_NAME`, `TOKENIZER_NAME`, `MAX_NEW_TOKENS` control inference defaults.
- `API_RATE_LIMIT` enforces middleware throttling.

## Helm Deployment
Updated chart values introduce replicas, resource requests, liveness/readiness probes, and autoscaling.

```bash
helm lint deploy/helm
helm template codex deploy/helm
```

Override values per environment using `--values` or `--set` flags. For production, ensure GPU nodes are available to satisfy `nvidia.com/gpu` limits.

## CI/CD Integration
1. Run pre-commit hooks (`black`, `ruff`, `mypy`, `pytest-quick`).
2. Execute targeted deployment tests:
   ```bash
   pytest tests/deployment/ -k "health or orchestrate"
   ```
3. Build and push container via orchestrator script with `--dry-run` in CI to validate commands.

## Runbooks & Architecture
- [DEPLOYMENT_RUNBOOK.md](DEPLOYMENT_RUNBOOK.md) – step-by-step promotion and rollback procedure.
- [deployment_architecture.md](deployment_architecture.md) – infrastructure overview and scaling guidance.

## Environment Matrix
| Environment | Purpose | Notes |
|-------------|---------|-------|
| Development | Local iteration via docker compose | Uses CPU runtime, minimal replicas |
| Staging | Pre-production parity | Enable readiness probes and autoscaling |
| Production | Customer traffic | GPU runtime, SLO monitoring, incident response on-call |

## Smoke Tests
After deploying, validate endpoints:
```bash
pytest tests/deployment/test_api_integration.py -k health
curl https://codex.example.com/ready
```

## Secrets Management
Inject API keys and model credentials via Kubernetes Secrets. Avoid hard-coding values in `values.yaml`; reference environment variables instead.
