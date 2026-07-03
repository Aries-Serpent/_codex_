# Deployment Procedures Guide - Phase 9.3.4

**Document Version:** 1.0  
**Last Updated:** 2026-07-07 08:00 UTC  
**Scope:** Canary, Regional, and Full Production Deployments  

---

## Quick Reference

| Phase | Traffic | Replicas | Duration | RTO on Failure |
|-------|---------|----------|----------|----------------|
| Canary | 10% | 1-2 | 15 min | <5 min |
| Regional | 50% | 3-4 | 15 min | <10 min |
| Full | 100% | 5 | Continuous | <2 min |

---

## Pre-Deployment Verification Checklist

```bash
#!/bin/bash
# Run this before each deployment phase

echo "🔍 Pre-Deployment Verification"
echo "=============================="

# 1. Check cluster health
echo "1️⃣  Kubernetes Cluster..."
kubectl cluster-info
kubectl get nodes -o wide

# 2. Check monitoring
echo "2️⃣  Monitoring Infrastructure..."
kubectl get deployment -n monitoring

# 3. Check current deployment
echo "3️⃣  Current Deployment State..."
kubectl get deployment codex-ml-server -n codex-ml -o wide
kubectl get pods -n codex-ml

# 4. Verify networking
echo "4️⃣  Service Endpoints..."
kubectl get svc codex-api-service -n codex-ml -o wide

# 5. Check storage
echo "5️⃣  Persistent Volumes..."
kubectl get pvc -n monitoring

# 6. Verify RBAC
echo "6️⃣  Service Accounts..."
kubectl get sa -n codex-ml

echo ""
echo "✅ All systems ready for deployment"
```

---

## Monitoring Commands Reference

```bash
# Watch pod status
kubectl get pods -n codex-ml --watch

# Check deployment status
kubectl rollout status deployment/codex-ml-server -n codex-ml

# View pod logs (last 100 lines)
kubectl logs -n codex-ml deployment/codex-ml-server --tail=100

# Stream logs (follow mode)
kubectl logs -n codex-ml deployment/codex-ml-server -f

# Check resource usage
kubectl top pods -n codex-ml
kubectl top nodes

# Verify metrics in Prometheus
curl -s "http://prometheus:9090/api/v1/query?query=up"

# Access Grafana dashboards
# URL: http://grafana.local/d/codex-ml-metrics

# Check AlertManager status
curl -s http://alertmanager:9093/api/v1/alerts

# View specific pod details
kubectl describe pod <pod-name> -n codex-ml

# Get pod events
kubectl get events -n codex-ml --sort-by='.lastTimestamp'
```

---

## Emergency Commands

```bash
# Quick rollback
kubectl rollout undo deployment/codex-ml-server -n codex-ml

# Pause rollout
kubectl rollout pause deployment/codex-ml-server -n codex-ml

# Resume rollout
kubectl rollout resume deployment/codex-ml-server -n codex-ml

# Force restart pods
kubectl rollout restart deployment/codex-ml-server -n codex-ml

# Delete and recreate deployment
kubectl delete deployment codex-ml-server -n codex-ml
kubectl apply -f manifests/k8s/base/deployment.yaml

# Drain node for maintenance
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# Scale deployment manually
kubectl scale deployment codex-ml-server --replicas=5 -n codex-ml

# Check logs from crashed pod
kubectl logs -n codex-ml <pod-name> --previous

# Get detailed pod status
kubectl get pod <pod-name> -n codex-ml -o yaml
```

---

## Rollback Decision Tree

```
Issue Detected?
    ↓ YES
    ├─ Error Rate > 5%?
    │   ├─ YES → Execute Canary Rollback
    │   │   └─ Command: kubectl rollout undo deployment/codex-ml-server -n codex-ml
    │   └─ NO → Continue monitoring
    │
    ├─ Pod Crash Looping?
    │   ├─ YES → Check logs & rollback
    │   │   └─ Command: kubectl logs -n codex-ml <pod> --previous
    │   └─ NO → Continue monitoring
    │
    ├─ CPU/Memory Exhaustion?
    │   ├─ YES → Scale up or rollback
    │   │   └─ Command: kubectl scale deployment ... --replicas=6
    │   └─ NO → Continue monitoring
    │
    └─ All metrics green?
        ├─ YES → Proceed to next phase
        └─ NO → Pause & investigate
```

---

## Metrics Dashboard URLs

After deployment, access monitoring dashboards at:

- **Prometheus:** http://prometheus.local:9090
- **Grafana:** http://grafana.local:3000
  - Dashboard: "Codex ML Metrics"
- **AlertManager:** http://alertmanager.local:9093

---

## Documentation Organization

See detailed guides in `.codex/`:
- `PHASE_9_3_TRACK_4_PREP_CHECKLIST.md` - Complete preparation checklist
- `INCIDENT_RESPONSE_RUNBOOK.md` - Incident procedures
- `HEALTH_CHECK_PROCEDURES.md` - Health monitoring guide
- `ROLLBACK_PROCEDURES.md` - Detailed rollback guide

