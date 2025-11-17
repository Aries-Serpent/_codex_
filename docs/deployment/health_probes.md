# Health Probes & Kubernetes Readiness

Codex services expose lightweight health endpoints for operators and orchestrators. Combine the HTTP checks with
Kubernetes probes or load balancer health checks to detect degraded dependencies early.

## Available endpoints

| Path | Purpose | Response |
| --- | --- | --- |
| `GET /health` | Comprehensive dependency report | JSON `HealthReport` with per-check status |
| `GET /ready` | Readiness probe | `{ "ready": true }` when `HealthChecker` reports `healthy` |
| `GET /live` | Liveness probe | Optional endpoint that always returns HTTP 200 when the process is running |

Register the endpoints in your FastAPI application:

```python
from fastapi import FastAPI
from codex_ml.monitoring.health import HealthChecker, HealthStatus

app = FastAPI()
checker = HealthChecker()

@app.get("/health")
async def health():
    report = await checker.check_dependencies()
    return report.dict()

@app.get("/ready")
async def ready():
    report = await checker.check_dependencies()
    return {"ready": report.status == HealthStatus.HEALTHY}
```text

> **Tip:** Keep the liveness probe inexpensive—avoid GPU initialisation or large file I/O. Readiness checks can be
> more thorough because they run less frequently.

## Kubernetes deployment example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: codex-ml-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: codex-ml-api
  template:
    metadata:
      labels:
        app: codex-ml-api
    spec:
      containers:
        - name: codex
          image: ghcr.io/example/codex-ml:latest
          ports:
            - containerPort: 8000
          readinessProbe:
            httpGet:
              path: /ready
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
```text

## Dashboards and alerting

* Export the health report logs to `.codex/health/*.ndjson` (enabled by default via `record_health_event`).
* Feed the Prometheus metrics into Grafana to trigger alerts when the `codex_ml_active_sessions` gauge is zero for
  longer than expected.
* Combine session logs with probe data to trace regressions across rollouts.
