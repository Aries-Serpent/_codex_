# Rollback Procedures Playbook
**Generated:** 2026-06-20T09:24:14.493018Z
**Status:** DRAFT - Review before production use

---

## Table of Contents
1. Quick Reference (5-minute rollback)
2. Detailed Procedures (step-by-step)
3. Emergency Procedures (panic button)
4. Validation Procedures
5. Known Issues and Edge Cases

---

## 1. Quick Reference (5-Minute Rollback)

**Use this section for rapid rollback in production incidents.**

### Rollback codex-ml-server

```bash
# Get current revision
kubectl rollout history deployment/codex-ml-server -n default

# Rollback to previous revision
kubectl rollout undo deployment/codex-ml-server -n default

# Wait for rollback to complete
kubectl rollout status deployment/codex-ml-server -n default --timeout=5m
```

### Rollback codex-ml-server

```bash
# Get current revision
kubectl rollout history deployment/codex-ml-server -n default

# Rollback to previous revision
kubectl rollout undo deployment/codex-ml-server -n default

# Wait for rollback to complete
kubectl rollout status deployment/codex-ml-server -n default --timeout=5m
```

### Rollback codex-ml-server

```bash
# Get current revision
kubectl rollout history deployment/codex-ml-server -n default

# Rollback to previous revision
kubectl rollout undo deployment/codex-ml-server -n default

# Wait for rollback to complete
kubectl rollout status deployment/codex-ml-server -n default --timeout=5m
```

---

## 2. Detailed Procedures (Step-by-Step)

### Pre-Rollback Checks

1. **Verify cluster connectivity:**
   ```bash
   kubectl cluster-info
   ```

2. **Check current deployment status:**
   ```bash
   kubectl get deployment codex-ml-server -n default
   kubectl describe deployment codex-ml-server -n default
   ```

   ```bash
   kubectl get deployment codex-ml-server -n default
   kubectl describe deployment codex-ml-server -n default
   ```

   ```bash
   kubectl get deployment codex-ml-server -n default
   kubectl describe deployment codex-ml-server -n default
   ```

3. **Check pod status:**
   ```bash
   kubectl get pods -n default
   kubectl get pods --all-namespaces
   ```

### Rollout History

**Deployment:** codex-ml-server (namespace: default)
- **Replicas:** 5
- **Strategy:** RollingUpdate
- **Images:** codex-ml:latest

**Rollback procedure for codex-ml-server:**

```bash
# Step 1: View rollout history
kubectl rollout history deployment/codex-ml-server -n default

# Step 2: Get details for specific revision (optional)
kubectl rollout history deployment/codex-ml-server -n default --revision=<N>

# Step 3: Perform rollback to previous revision
kubectl rollout undo deployment/codex-ml-server -n default

# OR: Rollback to specific revision
kubectl rollout undo deployment/codex-ml-server -n default --to-revision=<N>

# Step 4: Monitor rollback progress
kubectl rollout status deployment/codex-ml-server -n default --timeout=10m

# Step 5: Verify pods are running
kubectl get pods -n default -l app=unknown
```

**Deployment:** codex-ml-server (namespace: default)
- **Replicas:** 1
- **Strategy:** RollingUpdate
- **Images:** codex-ml:latest

**Rollback procedure for codex-ml-server:**

```bash
# Step 1: View rollout history
kubectl rollout history deployment/codex-ml-server -n default

# Step 2: Get details for specific revision (optional)
kubectl rollout history deployment/codex-ml-server -n default --revision=<N>

# Step 3: Perform rollback to previous revision
kubectl rollout undo deployment/codex-ml-server -n default

# OR: Rollback to specific revision
kubectl rollout undo deployment/codex-ml-server -n default --to-revision=<N>

# Step 4: Monitor rollback progress
kubectl rollout status deployment/codex-ml-server -n default --timeout=10m

# Step 5: Verify pods are running
kubectl get pods -n default -l app=unknown
```

**Deployment:** codex-ml-server (namespace: default)
- **Replicas:** 3
- **Strategy:** RollingUpdate
- **Images:** codex-ml:latest

**Rollback procedure for codex-ml-server:**

```bash
# Step 1: View rollout history
kubectl rollout history deployment/codex-ml-server -n default

# Step 2: Get details for specific revision (optional)
kubectl rollout history deployment/codex-ml-server -n default --revision=<N>

# Step 3: Perform rollback to previous revision
kubectl rollout undo deployment/codex-ml-server -n default

# OR: Rollback to specific revision
kubectl rollout undo deployment/codex-ml-server -n default --to-revision=<N>

# Step 4: Monitor rollback progress
kubectl rollout status deployment/codex-ml-server -n default --timeout=10m

# Step 5: Verify pods are running
kubectl get pods -n default -l app=codex-ml
```

---

## 3. Emergency Procedures (Panic Button)

**Use only in severe incidents. For controlled rollback, use Detailed Procedures.**

### Emergency Rollback: codex-ml-server

```bash
# Option 1: Kill all pods (Kubernetes will restart with previous image)
kubectl delete pods --all -n default

# Option 2: Immediate rollback
kubectl set image deployment/codex-ml-server codex-ml=codex-ml:stable -n default --record

# Option 3: Scale down and up
kubectl scale deployment codex-ml-server --replicas=0 -n default
sleep 10
kubectl scale deployment codex-ml-server --replicas=3 -n default
```

### Emergency Rollback: codex-ml-server

```bash
# Option 1: Kill all pods (Kubernetes will restart with previous image)
kubectl delete pods --all -n default

# Option 2: Immediate rollback
kubectl set image deployment/codex-ml-server codex-ml=codex-ml:stable -n default --record

# Option 3: Scale down and up
kubectl scale deployment codex-ml-server --replicas=0 -n default
sleep 10
kubectl scale deployment codex-ml-server --replicas=3 -n default
```

### Emergency Rollback: codex-ml-server

```bash
# Option 1: Kill all pods (Kubernetes will restart with previous image)
kubectl delete pods --all -n default

# Option 2: Immediate rollback
kubectl set image deployment/codex-ml-server codex-ml=codex-ml:stable -n default --record

# Option 3: Scale down and up
kubectl scale deployment codex-ml-server --replicas=0 -n default
sleep 10
kubectl scale deployment codex-ml-server --replicas=3 -n default
```

---

## 4. Validation Procedures

### Health Checks

```bash
# Check deployment health
kubectl get deployment codex-ml-server -n default -o json | jq '.status'

kubectl get deployment codex-ml-server -n default -o json | jq '.status'

kubectl get deployment codex-ml-server -n default -o json | jq '.status'

# Check pod health
kubectl get pods -n default -o wide

# Check service endpoints
kubectl get endpoints codex-ml-service -n default
```

### Success Criteria

- ✅ All 5 replicas are Running
- ✅ All replicas are Ready (1/1)
- ✅ All 1 replicas are Running
- ✅ All replicas are Ready (1/1)
- ✅ All 3 replicas are Running
- ✅ All replicas are Ready (1/1)
- ✅ No CrashLoopBackOff pods
- ✅ Health endpoints responding
- ✅ Metrics available

---

## 5. Known Issues and Edge Cases

### Issue: Insufficient Resources
- **Symptom:** Pods stuck in Pending
- **Solution:** Check resource requests/limits; scale down other workloads

### Issue: Image Pull Errors
- **Symptom:** Pods stuck in ImagePullBackOff
- **Solution:** Verify image registry credentials; check network connectivity

### Issue: CrashLoopBackOff
- **Symptom:** Pods restart continuously
- **Solution:** Check logs: `kubectl logs <pod> -n <ns>`; verify environment variables

### Issue: Service Connection Refused
- **Symptom:** Connection refused to service endpoint
- **Solution:** Verify service selector labels; check pod network policies

---

## Deployment RPO/RTO

| Metric | Value | Notes |
|--------|-------|-------|
| codex-ml-server | RTO: 10-15 minutes | Strategy: RollingUpdate |
| codex-ml-server | RTO: 2-3 minutes | Strategy: RollingUpdate |
| codex-ml-server | RTO: 6-9 minutes | Strategy: RollingUpdate |

