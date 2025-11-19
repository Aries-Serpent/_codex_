# [Guide]: Docker & Kubernetes Deployment
> Generated: 2025-11-19 04:46:57 UTC | Author: mbaetiong  
Roles: [Audit Orchestrator], [Capability Cartographer] ⚡ Energy: 5  
Physics: Path🛤️ Fields🔄 Patterns👁️ Redundancy🔀 Balance⚖️

## 1. Build & Run (CPU)
```bash
docker build -t codex-ml:cpu -f Dockerfile .
docker run --rm -it \
  -v "$(pwd)/data:/app/data:ro" \
  -v "$(pwd)/checkpoints:/app/checkpoints" \
  -v "$(pwd)/logs:/app/logs" \
  codex-ml:cpu \
  python training/engine_hf_trainer.py --config configs/training/base.yaml
```

## 2. Build & Run (GPU)
```bash
docker build -t codex-ml:gpu -f Dockerfile.gpu .
docker run --rm -it --gpus all \
  -e CUDA_VISIBLE_DEVICES=0 \
  -v "$(pwd)/data:/app/data:ro" \
  -v "$(pwd)/checkpoints:/app/checkpoints" \
  -v "$(pwd)/logs:/app/logs" \
  codex-ml:gpu \
  python training/engine_hf_trainer.py --config configs/training/base.yaml --device cuda
```

## 3. Docker Compose
```bash
docker compose up -d training-cpu
# or
docker compose up -d training-gpu
```

## 4. Kubernetes
Apply manifests (ensure a GPU node pool for GPU variant):
```bash
kubectl apply -f deploy/kubernetes/configmap.yaml
kubectl apply -f deploy/kubernetes/deployment.yaml
```

## 5. Offline Mode
Ensure environment variables (see .env.example) force offline execution:
- CODEX_OFFLINE_MODE=1
- HF_DATASETS_OFFLINE=1
- WANDB_MODE=disabled
- MLFLOW_TRACKING_URI=file:///app/logs/mlruns

## 6. Health & Logs
- Liveness probe ensures CUDA presence for GPU pods.
- Logs are written to /app/logs by default; mount PersistentVolumes for retention.

## 7. Security Notes
- Images run as non-root user.
- Avoid mounting sensitive host paths.
- Use private registries for pushing images; scan images post-build.
