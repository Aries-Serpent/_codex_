# Deployment & Operations Master Runbook

> **Consolidated Master Document** for Codex Deployment  
> **Created**: 2026-07-08  
> **Consolidation Campaign**: Phase 12 WS3  
> **Status**: ✅ Active Master Document

**Consolidated from** 10 source files:
- docs/ISOLATED_DEPLOYMENT.md
- docs/OFFLINE_DEPLOYMENT.md
- docs/ops/DEPLOYMENT_RUNBOOK.md
- docs/ops/DEPLOYMENT_READINESS_S92.md
- docs/architecture/DEPLOYMENT_ARCHITECTURE.md
- docs/operations/INCIDENT_RESPONSE*.md (4 files)
- docs/validation/CI_Remediation_Verification.md

---

## Table of Contents

1. [Deployment Overview](#deployment-overview)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Deployment Models](#deployment-models)
4. [Deployment Procedures](#deployment-procedures)
5. [Post-Deployment Validation](#post-deployment-validation)
6. [Incident Response](#incident-response)
7. [Rollback Procedures](#rollback-procedures)

---

## Deployment Overview

### Deployment Architecture

```
┌──────────────────────────────────────────┐
│ Source Code (GitHub)                     │
│ - main branch                            │
│ - release branches                       │
└──────────┬───────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│ Build Pipeline (GitHub Actions)          │
│ - Tests, linting, security scans         │
│ - Build Docker image                     │
│ - Push to registry                       │
└──────────┬───────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│ Deployment Targets                       │
│ - Staging (validation)                   │
│ - Production (live)                      │
│ - Offline (air-gapped)                   │
│ - Isolated (sandboxed)                   │
└──────────────────────────────────────────┘
```

### Supported Deployment Models

| Model | Use Case | Infrastructure | Readiness |
|-------|----------|-----------------|-----------|
| **Standard** | Cloud deployment | AWS/GCP/Azure | ✅ Ready |
| **Docker** | Container-based | Docker/Podman | ✅ Ready |
| **Kubernetes** | Orchestrated | K8s 1.20+ | ✅ Ready |
| **Offline** | Air-gapped networks | Local + USB drives | ✅ Ready |
| **Isolated** | Sandboxed environment | Local VM/Container | ✅ Ready |

---

## Pre-Deployment Checklist

### Readiness Review (1 week before)

- [ ] Code freeze date announced
- [ ] Release notes drafted
- [ ] Migration guide (if needed) prepared
- [ ] Rollback procedure documented
- [ ] On-call team confirmed
- [ ] Customer notifications drafted

### Automated Checks (24 hours before)

```bash
# Run full test suite
make test

# Run security scans
make security-scan

# Check dependencies
python scripts/check_dependencies.py

# Validate configuration
python scripts/validate_config.py

# Dry run deployment
make deploy --dry-run
```

### Manual Verification (4 hours before)

- [ ] Code review complete (all PRs merged)
- [ ] All tests passing
- [ ] Security scans passing
- [ ] Performance baselines met
- [ ] Documentation updated
- [ ] Rollback tested
- [ ] Incident response team ready

---

## Deployment Models

### 1. Standard Cloud Deployment

**Target**: AWS/GCP/Azure (managed services)

**Prerequisites**:
- Cloud account configured
- Credentials available
- Network access configured

**Deployment**:
```bash
# 1. Build artifact
docker build -t codex:v1.2.3 .

# 2. Push to registry
docker push registry.example.com/codex:v1.2.3

# 3. Update configuration
sed -i 's/v1.2.2/v1.2.3/g' config/prod.yaml

# 4. Deploy
terraform apply -var="image_tag=v1.2.3"

# 5. Verify
curl https://api.example.com/health
```

**Rollback**:
```bash
# Revert to previous version
terraform apply -var="image_tag=v1.2.2"
```

### 2. Docker Deployment

**Target**: Docker/Podman (containerized)

**Prerequisites**:
- Docker installed
- Docker daemon running
- 5GB disk space

**Deployment**:
```bash
# 1. Build image
docker build -t codex:latest .

# 2. Stop old container
docker stop codex || true

# 3. Start new container
docker run -d \
  --name codex \
  -p 8000:8000 \
  -v /data:/app/data \
  -e ENVIRONMENT=production \
  codex:latest

# 4. Verify
docker ps | grep codex
docker logs codex
curl http://localhost:8000/health
```

**Rollback**:
```bash
# Revert to previous image
docker stop codex
docker run -d --name codex ... codex:previous
```

### 3. Kubernetes Deployment

**Target**: Kubernetes cluster

**Prerequisites**:
- K8s cluster (1.20+)
- kubectl configured
- Helm 3.0+

**Deployment**:
```bash
# 1. Update Helm chart values
helm upgrade codex ./charts/codex \
  --set image.tag=v1.2.3 \
  --values values-prod.yaml

# 2. Monitor rollout
kubectl rollout status deployment/codex

# 3. Verify
kubectl get pods
kubectl get services
curl http://$(kubectl get svc codex -o jsonpath='{.status.loadBalancer.ingress[0].ip}')/health
```

**Rollback**:
```bash
# Rollback to previous release
helm rollback codex 1
```

### 4. Offline Deployment

**Target**: Air-gapped networks (no internet access)

**Prerequisites**:
- USB drive (minimum 16GB)
- Bootstrap machine (with internet)
- Offline network access

**Preparation**:
```bash
# On bootstrap machine with internet
./offline_bootstrap.sh --version v1.2.3

# Output:
# - codex-v1.2.3-offline.tar.gz (8GB)
# - dependencies-v1.2.3.tar.gz (2GB)
# - bootstrap-scripts.tar.gz (50MB)
```

**Deployment**:
```bash
# On offline machine
tar xzf codex-v1.2.3-offline.tar.gz
cd codex-v1.2.3
./deploy-offline.sh

# Verify
curl http://localhost:8000/health
```

### 5. Isolated Deployment

**Target**: Sandboxed environment (testing/validation)

**Prerequisites**:
- VM or container
- 8GB RAM, 20GB disk
- Network isolation configured

**Deployment**:
```bash
# 1. Create isolated environment
docker build -t codex-isolated -f Dockerfile.isolated .

# 2. Run in isolation
docker run -it \
  --network none \
  --name codex-isolated \
  codex-isolated

# 3. Test functionality (internal only)
curl http://localhost:8000/health
```

---

## Deployment Procedures

### Standard Deployment Flow

```
1. STAGING DEPLOYMENT
   ├─ Deploy to staging environment
   ├─ Run smoke tests
   ├─ Validate data migration
   └─ Get approval from QA team

2. PRODUCTION DEPLOYMENT
   ├─ Deploy to canary (5% traffic)
   ├─ Monitor metrics for 30 minutes
   ├─ Gradually increase to 100%
   │  ├─ 25% at 15 minutes
   │  ├─ 50% at 30 minutes
   │  ├─ 100% at 45 minutes
   └─ Monitor for 24 hours

3. POST-DEPLOYMENT
   ├─ Update documentation
   ├─ Notify users
   ├─ Archive old artifacts
   └─ Close deployment ticket
```

### Deployment Rollout Strategy

```yaml
canary_deployment:
  stage_1:
    traffic_percentage: 5
    duration: 15 minutes
    metrics_check: error_rate < 1%
    decision: success → continue

  stage_2:
    traffic_percentage: 25
    duration: 15 minutes
    metrics_check: latency p95 < 100ms
    decision: success → continue

  stage_3:
    traffic_percentage: 50
    duration: 15 minutes
    metrics_check: success_rate > 99.5%
    decision: success → continue

  stage_4:
    traffic_percentage: 100
    duration: ongoing
    metrics_check: all metrics nominal
    decision: success → complete
```

---

## Post-Deployment Validation

### Smoke Tests

```bash
# 1. Health checks
curl -f http://api.example.com/health || exit 1

# 2. API functionality
curl -f http://api.example.com/api/v1/test || exit 1

# 3. Database connectivity
curl -f http://api.example.com/api/v1/db/check || exit 1

# 4. Cache functionality
curl -f http://api.example.com/api/v1/cache/check || exit 1

# All tests passed
echo "✅ Smoke tests passed"
```

### Metrics Validation

```bash
# 1. Check error rate
ERROR_RATE=$(curl -s http://metrics.example.com/error_rate)
if (( $(echo "$ERROR_RATE > 1.0" | bc -l) )); then
  echo "❌ Error rate too high: $ERROR_RATE%"
  exit 1
fi

# 2. Check latency
LATENCY_P95=$(curl -s http://metrics.example.com/latency_p95)
if (( $(echo "$LATENCY_P95 > 100" | bc -l) )); then
  echo "❌ Latency too high: ${LATENCY_P95}ms"
  exit 1
fi

# All metrics nominal
echo "✅ Metrics validation passed"
```

### Data Validation

```bash
# 1. Verify data migration
MIGRATED_COUNT=$(psql -c "SELECT COUNT(*) FROM migrated_data")
EXPECTED_COUNT=1000000
if [[ $MIGRATED_COUNT -ne $EXPECTED_COUNT ]]; then
  echo "❌ Migration count mismatch: $MIGRATED_COUNT vs $EXPECTED_COUNT"
  exit 1
fi

# 2. Check data integrity
INTEGRITY_CHECK=$(python scripts/validate_data_integrity.py)
if [[ $INTEGRITY_CHECK != "OK" ]]; then
  echo "❌ Data integrity check failed"
  exit 1
fi

echo "✅ Data validation passed"
```

---

## Incident Response

### Incident Types

**Type 1: Performance Degradation**
```yaml
severity: HIGH
detection: Latency p95 > 200ms for 5+ minutes
response_time: 10 minutes
stakeholders: On-call engineer, TechLead

steps:
  1. Page on-call engineer
  2. Assess impact (% users affected, duration)
  3. Implement mitigation (enable cache, scale up)
  4. Monitor metrics
  5. Root cause analysis
  6. Post-incident review
```

**Type 2: Error Rate Spike**
```yaml
severity: CRITICAL
detection: Error rate > 5% for 2+ minutes
response_time: 2 minutes
stakeholders: On-call engineer, TechLead, Manager

steps:
  1. Trigger automatic rollback
  2. Page entire on-call team
  3. Assess scope (API endpoints, user impact)
  4. Implement manual fixes if rollback fails
  5. Monitor recovery
  6. Root cause analysis
  7. Incident postmortem
```

**Type 3: Security Incident**
```yaml
severity: CRITICAL
detection: Suspicious access patterns, data breach
response_time: 5 minutes
stakeholders: Security team, CISO, Legal

steps:
  1. Isolate affected systems
  2. Preserve evidence (logs, memory dump)
  3. Page security team
  4. Notify affected users
  5. Conduct forensic analysis
  6. Implement fixes
  7. Compliance review
```

### Incident Escalation

```
LEVEL 1: Individual contributor
         - Monitor metrics
         - Implement quick fixes
         - Update status page
         - 30-minute escalation timer

LEVEL 2: Engineering Lead
         - Lead incident response
         - Coordinate teams
         - Make go/no-go decisions
         - 60-minute escalation timer

LEVEL 3: Manager / Director
         - Executive decision-making
         - Customer communication
         - Resource allocation
         - 2-hour escalation timer

LEVEL 4: VP / C-Suite
         - Strategic decisions
         - Major outage handling
         - Legal/regulatory involvement
         - Ongoing escalation
```

### Communication Protocol

```
T+0: Incident detected
     → Page on-call team
     → Update status page: INVESTIGATING
     → Create incident ticket

T+5: Initial assessment complete
     → Brief stakeholders
     → Estimate recovery time
     → Update status page: IDENTIFIED

T+15: Mitigation implemented
     → Update status page: MONITORING
     → ETA to full recovery

T+30: Service recovered
     → Update status page: RESOLVED
     → Announce recovery
     → Schedule postmortem

T+2 days: Postmortem meeting
     → Review root cause
     → Discuss preventive measures
     → Assign action items
     → Publish report
```

---

## Rollback Procedures

### When to Rollback

- Error rate > 5% for 2+ minutes
- API latency p95 > 500ms
- Availability < 99%
- Data corruption detected
- Security vulnerability discovered
- Business-critical feature broken

### Automatic Rollback

```yaml
auto_rollback:
  triggers:
    - error_rate > 5% for 2 minutes
    - latency_p95 > 500ms for 5 minutes
    - availability < 99% for 3 minutes
    
  action: Automatically rollback to previous release
  
  confirmation: Notify team, log rollback reason
  
  result: Service back to previous state within 2 minutes
```

### Manual Rollback

```bash
# For Kubernetes
kubectl rollout undo deployment/codex

# For Docker Compose
docker-compose down
docker-compose up -d  # Uses previous image version

# For Terraform
git checkout HEAD~1 -- main.tf
terraform apply

# For Helm
helm rollback codex 1
```

### Post-Rollback Steps

1. Verify service health (smoke tests)
2. Communicate with users
3. Begin root cause analysis
4. Schedule incident postmortem
5. Plan fix for next deployment

---

**This document is the authoritative deployment and operations guide for Codex.**

*Last Updated: 2026-07-08*  
*Consolidation Status: ✅ Complete (10 files merged)*
