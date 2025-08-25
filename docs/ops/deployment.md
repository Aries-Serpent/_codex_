<!-- BEGIN: CODEX_DEPLOY_DOC -->
# Deployment (Docker + Compose)

## Build
```bash
IMAGE=codex-api:local bash scripts/deploy/build.sh
```

## Run (CPU by default)
```bash
bash scripts/deploy/run.sh
```
If a compatible NVIDIA GPU is detected (nvidia-smi present), the run script will attempt `--gpus all`.

## Compose (manual)
```bash
docker compose up -d
curl -fsS http://localhost:8000/status
```

## Use the API
```bash
curl -fsS http://localhost:8000/status | jq .
curl -fsS -X POST http://localhost:8000/infer -H 'Content-Type: application/json' -d '{"prompt":"hello"}'
curl -fsS -X POST http://localhost:8000/train -H 'Content-Type: application/json' -d '{"epochs": 2}'
```
Artifacts are written under the named volume `codex_artifacts` and visible inside the container at `/artifacts`.

Policy: DO NOT ACTIVATE ANY GitHub Actions Online files. All validations must run within the Codex environment.
