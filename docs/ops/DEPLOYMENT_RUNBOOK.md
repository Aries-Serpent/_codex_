# Production Deployment Runbook

## Prerequisites
- Kubernetes cluster with GPU node pool available
- Helm 3.x installed locally
- Docker registry credentials configured via `docker login`

## Deployment Steps
1. Build image:
   ```bash
   ./scripts/deploy/orchestrate.sh build --gpu
   ```
2. Push to registry:
   ```bash
   ./scripts/deploy/orchestrate.sh push
   ```
3. Deploy Helm chart:
   ```bash
   helm upgrade --install codex deploy/helm/
   ```
4. Verify health probes:
   ```bash
   kubectl get pods -l app=codex
   curl https://codex.example.com/health
   ```
5. Run smoke tests:
   ```bash
   ./scripts/deploy/orchestrate.sh run --dry-run
   pytest tests/deployment/test_api_integration.py -k health
   ```

## Rollback Procedure
1. Identify last known good chart version using `helm history codex`.
2. Roll back:
   ```bash
   helm rollback codex <revision>
   ```
3. Validate `/ready` endpoint until status returns 200.

## Observability
| Metric | SLO | Monitoring |
|--------|-----|------------|
| Availability | 99.9% | Prometheus + Alertmanager |
| Latency p95 | < 200ms | Grafana dashboards |
| Error Rate | < 0.1% | Sentry alerts |

## Incident Response
Escalation and communication steps are documented in [docs/security/incident_response.md](../security/incident_response.md).
