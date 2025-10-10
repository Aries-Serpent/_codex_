# Deployment Architecture

## High-Level Components
- **Ingress Controller** – Routes HTTPS traffic to the Codex API service.
- **Codex API Deployment** – FastAPI application scaled via Kubernetes Deployment.
- **Model Artifact Storage** – Mounted volume or object store containing model weights.
- **Observability Stack** – Prometheus + Grafana + Loki for metrics and logs.

## Data Flow
1. Client sends request to ingress.
2. Request forwarded to Codex API pod where security middleware validates payload.
3. API interacts with model runtime and returns response through ingress.
4. Logs and metrics emitted to monitoring stack.

## Scaling Strategy
- `replicaCount: 3` ensures baseline redundancy.
- Horizontal Pod Autoscaler scales between 2 and 10 pods at 70% CPU utilization.
- GPU workloads scheduled via `nvidia.com/gpu` resource limits defined in `values.yaml`.

## Health & Readiness
- `/health` liveness probe checks runtime heartbeat.
- `/ready` readiness probe verifies model availability and dependency checks.

## Deployment Workflow
1. Build multi-stage Docker image (CPU or GPU runtime).
2. Push to registry with semantic tag (e.g., `1.0.0`).
3. Deploy Helm chart with environment-specific values.
4. Monitor pods via `kubectl`, Prometheus alerts, and run smoke tests.

## Secrets & Configuration
- Secrets injected via Kubernetes Secret objects referenced in Helm values.
- Rate limits and API keys configured through environment variables.

## Diagram (Textual)
```text
Client -> Ingress -> Codex API Service -> Model Runtime
                   \-> Observability Stack
```
