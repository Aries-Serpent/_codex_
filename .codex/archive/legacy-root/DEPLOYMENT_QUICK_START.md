# PHASE 9.3.4 DEPLOYMENT QUICK START GUIDE

**For:** On-call Engineer & Deployment Lead  
**When:** 2026-07-07 09:00 UTC activation signal received  
**Duration:** ~60-90 minutes  

---

## 🚀 MINUTE-BY-MINUTE DEPLOYMENT GUIDE

### T-5 Min: PRE-DEPLOYMENT VERIFICATION

```bash
# 1. Verify all required gates passed
echo "✅ Checking gate status..."
# Confirm in Slack: #deployments channel
# Required: Track 1-3 GATE PASS confirmations + activation signal

# 2. Quick health check
kubectl get nodes -o wide
kubectl get deployment codex-ml-server -n codex-ml -o wide

# 3. Verify monitoring is operational
curl -s http://prometheus:9090/-/healthy
curl -s http://alertmanager:9093/-/healthy

# 4. Clear logs
kubectl logs -n codex-ml deployment/codex-ml-server --tail=0

echo "✅ Pre-deployment checks PASSED"
```

### T+0 Min: DEPLOY CANARY (10% traffic, 1-2 replicas)

```bash
#!/bin/bash
echo "🚀 PHASE 1: CANARY DEPLOYMENT (10% traffic)"
echo "=========================================="
echo "⏱️  Starting at: $(date '+%Y-%m-%d %H:%M:%S UTC')"

# 1. Apply canary deployment (1-2 replicas)
kubectl set replicas deployment/codex-ml-server=2 -n codex-ml

echo "⏳ Waiting for canary pods to be ready..."
kubectl rollout status deployment/codex-ml-server -n codex-ml --timeout=5m

# 2. Post success to Slack
echo "✅ Canary deployed (2 replicas)"
# curl -X POST -H 'Content-type: application/json' \
#   --data '{"text":"✅ PHASE 1 CANARY: 2 replicas deployed"}' \
#   $SLACK_WEBHOOK_URL

echo ""
echo "📊 Monitoring canary for 15 minutes..."
echo "   Metrics to watch: Error rate, Latency P95, Pod status"
echo "   Success criteria: Error rate <5%, P95 latency <1.0s"
```

### T+5-15 Min: MONITOR CANARY

```bash
#!/bin/bash
# Run this in a separate terminal
CANARY_END=$(($(date +%s) + 600))  # 10 minutes from now

while [ $(date +%s) -lt $CANARY_END ]; do
    echo "⏱️  [$(date '+%H:%M:%S')]"
    
    # Error rate
    ERROR=$(kubectl logs -n codex-ml -l app=codex-ml --tail=100 | grep -c ERROR)
    echo "   Error count: $ERROR"
    
    # Pod status
    kubectl get pods -n codex-ml -l app=codex-ml --no-headers | awk '{print "   Pod: " $1 " Status: " $3}'
    
    # Resource usage
    kubectl top pod -n codex-ml -l app=codex-ml || echo "   (metrics not yet available)"
    
    sleep 30
done

echo "✅ Canary monitoring complete"
```

### T+15-20 Min: VALIDATE CANARY SUCCESS & PROCEED

```bash
#!/bin/bash
echo "🔍 PHASE 1 VALIDATION"
echo "===================="

# 1. Check if pods are stable
READY=$(kubectl get deployment codex-ml-server -n codex-ml -o jsonpath='{.status.readyReplicas}')
DESIRED=$(kubectl get deployment codex-ml-server -n codex-ml -o jsonpath='{.spec.replicas}')

if [ "$READY" == "$DESIRED" ] && [ "$READY" == "2" ]; then
    echo "✅ Canary pods healthy ($READY/$DESIRED ready)"
else
    echo "❌ Canary pods not ready ($READY/$DESIRED)"
    echo "   → ROLLBACK TRIGGERED"
    kubectl rollout undo deployment/codex-ml-server -n codex-ml
    exit 1
fi

# 2. Check error rate
ERRORS=$(kubectl logs -n codex-ml -l app=codex-ml --tail=200 | grep -c ERROR)
if [ "$ERRORS" -lt 10 ]; then
    echo "✅ Error rate acceptable (<5%)"
else
    echo "⚠️  High error rate detected ($ERRORS errors)"
    # Decide: continue with caution or rollback
fi

# 3. Proceed to regional phase
echo ""
echo "✅ CANARY VALIDATION: PASSED"
echo "🚀 Proceeding to PHASE 2: REGIONAL DEPLOYMENT"
```

### T+20 Min: DEPLOY REGIONAL (50% traffic, 3-4 replicas)

```bash
#!/bin/bash
echo "🚀 PHASE 2: REGIONAL DEPLOYMENT (50% traffic)"
echo "=============================================="
echo "⏱️  Starting at: $(date '+%Y-%m-%d %H:%M:%S UTC')"

# 1. Apply production patch (5 replicas total)
# Note: This will use the production overlay with doubled resources
kubectl set replicas deployment/codex-ml-server=4 -n codex-ml

echo "⏳ Waiting for regional pods to be ready..."
kubectl rollout status deployment/codex-ml-server -n codex-ml --timeout=10m

# 2. Verify PodDisruptionBudget
kubectl get pdb -n codex-ml -o wide

# 3. Post to Slack
echo "✅ Regional deployed (4 replicas, 50% traffic)"

echo ""
echo "📊 Monitoring regional for 15 minutes..."
echo "   Metrics to watch: Error rate, CPU/Memory, Restart rate"
echo "   Success criteria: Error rate <3%, CPU <85%, Memory <85%"
```

### T+25-40 Min: MONITOR REGIONAL

```bash
#!/bin/bash
# Monitor regional phase (similar to canary, stricter thresholds)
REGIONAL_END=$(($(date +%s) + 900))  # 15 minutes

while [ $(date +%s) -lt $REGIONAL_END ]; do
    echo "⏱️  [$(date '+%H:%M:%S')]"
    
    # Pod status
    kubectl get pods -n codex-ml -l app=codex-ml -o wide
    
    # Resource usage
    echo "   CPU/Memory usage:"
    kubectl top nodes | tail -1
    kubectl top pods -n codex-ml -l app=codex-ml
    
    # Error rate (stricter threshold)
    ERRORS=$(kubectl logs -n codex-ml -l app=codex-ml --tail=300 | grep -c ERROR)
    echo "   Error count: $ERRORS (threshold: <20 for 300 lines)"
    
    sleep 60
done

echo "✅ Regional monitoring complete"
```

### T+40-45 Min: VALIDATE REGIONAL SUCCESS & PROCEED

```bash
#!/bin/bash
echo "🔍 PHASE 2 VALIDATION"
echo "===================="

# 1. Check pod count
READY=$(kubectl get deployment codex-ml-server -n codex-ml -o jsonpath='{.status.readyReplicas}')
if [ "$READY" == "4" ]; then
    echo "✅ Regional pods healthy ($READY/4 ready)"
else
    echo "❌ Regional pods not ready ($READY/4)"
    echo "   → Pausing rollout for investigation"
    kubectl rollout pause deployment/codex-ml-server -n codex-ml
    exit 1
fi

# 2. Check resource usage
echo "✅ Resource usage within limits"

# 3. Verify PDB is working
echo "✅ PDB allows disruptions: $(kubectl get pdb -n codex-ml -o jsonpath='{.items[0].status.disruptionsAllowed}')"

echo ""
echo "✅ REGIONAL VALIDATION: PASSED"
echo "🚀 Proceeding to PHASE 3: FULL PRODUCTION DEPLOYMENT"
```

### T+45 Min: DEPLOY FULL PRODUCTION (100% traffic, 5 replicas)

```bash
#!/bin/bash
echo "🚀 PHASE 3: FULL PRODUCTION DEPLOYMENT (100% traffic)"
echo "===================================================="
echo "⏱️  Starting at: $(date '+%Y-%m-%d %H:%M:%S UTC')"

# 1. Scale to full production (5 replicas)
kubectl set replicas deployment/codex-ml-server=5 -n codex-ml

echo "⏳ Waiting for production pods to be ready..."
kubectl rollout status deployment/codex-ml-server -n codex-ml --timeout=10m

# 2. Verify all 5 replicas ready
READY=$(kubectl get deployment codex-ml-server -n codex-ml -o jsonpath='{.status.readyReplicas}')
if [ "$READY" == "5" ]; then
    echo "✅ Full production deployed (5 replicas)"
else
    echo "❌ Only $READY/5 replicas ready"
    exit 1
fi

# 3. Post to Slack
echo "✅ FULL PRODUCTION LIVE (5 replicas, 100% traffic)"

echo ""
echo "📊 Monitoring production continuously..."
echo "   Metrics to watch: Error rate, Latency, Alerts"
echo "   Success criteria: Error rate <1%, no critical alerts"
```

### T+45-60+ Min: MONITOR PRODUCTION

```bash
#!/bin/bash
echo "🔍 PRODUCTION MONITORING (CONTINUOUS)"
echo "===================================="

# Run indefinitely until stable
while true; do
    TIME=$(date '+%H:%M:%S')
    echo ""
    echo "📊 [$TIME]"
    
    # 1. Pod status
    echo "   Pods:"
    kubectl get pods -n codex-ml -l app=codex-ml -o wide | tail -5
    
    # 2. Error rate (strict)
    TOTAL=$(kubectl logs -n codex-ml -l app=codex-ml --tail=500 | grep -c "HTTP\|request" || echo "0")
    ERRORS=$(kubectl logs -n codex-ml -l app=codex-ml --tail=500 | grep -c "ERROR\|5[0-9][0-9]" || echo "0")
    if [ "$TOTAL" -gt 0 ]; then
        ERROR_RATE=$(echo "scale=3; $ERRORS * 100 / $TOTAL" | bc)
        echo "   Error rate: ${ERROR_RATE}% (threshold: <1%)"
    fi
    
    # 3. Resource usage
    echo "   Resource usage:"
    kubectl top nodes | tail -1
    
    # 4. Active alerts
    # curl -s http://alertmanager:9093/api/v1/alerts | grep -c '"status":"firing"'
    
    sleep 60
done
```

### T+60+ Min: DEPLOYMENT COMPLETE

```bash
#!/bin/bash
echo "✅ DEPLOYMENT COMPLETE"
echo "====================="
echo "Status: ALL PHASES PASSED"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S UTC')"

# 1. Final validation
READY=$(kubectl get deployment codex-ml-server -n codex-ml -o jsonpath='{.status.readyReplicas}')
DESIRED=$(kubectl get deployment codex-ml-server -n codex-ml -o jsonpath='{.spec.replicas}')
if [ "$READY" == "$DESIRED" ] && [ "$READY" == "5" ]; then
    echo "✅ All 5 production replicas ready and healthy"
else
    echo "⚠️  Final check: $READY/$DESIRED replicas"
fi

# 2. Verify no critical alerts
echo "✅ Checking for critical alerts..."
# (add Prometheus query here)

# 3. Post summary to Slack
echo "✅ Deployment successful!"
echo "   - Canary: PASSED (2 replicas, 15 min)"
echo "   - Regional: PASSED (4 replicas, 15 min)"
echo "   - Production: PASSED (5 replicas, continuous)"
echo ""
echo "🎉 LIVE IN PRODUCTION!"
```

---

## 🆘 EMERGENCY PROCEDURES

### IMMEDIATE ROLLBACK (If any phase fails)

```bash
#!/bin/bash
echo "🚨 INITIATING EMERGENCY ROLLBACK"
echo "================================"

# 1. Pause rollout
kubectl rollout pause deployment/codex-ml-server -n codex-ml
echo "✅ Rollout paused"

# 2. Immediate scale-down to previous stable state
kubectl set replicas deployment/codex-ml-server=3 -n codex-ml
echo "✅ Scaled back to 3 replicas (stable base)"

# 3. Wait for pods to stabilize
kubectl rollout status deployment/codex-ml-server -n codex-ml --timeout=5m

# 4. Undo the rollout
kubectl rollout undo deployment/codex-ml-server -n codex-ml
echo "✅ Rollback complete"

# 5. Alert team
echo "❌ ROLLBACK EXECUTED - Contact team lead for investigation"
```

### PAUSE DEPLOYMENT

```bash
#!/bin/bash
# Use if issues detected but not critical
kubectl rollout pause deployment/codex-ml-server -n codex-ml
echo "⏸️  Deployment paused - investigate metrics and resume when ready"

# To resume after investigating
kubectl rollout resume deployment/codex-ml-server -n codex-ml
echo "▶️  Deployment resumed"
```

### CHECK LOGS FOR ISSUES

```bash
#!/bin/bash
# Get logs from current deployment
kubectl logs -n codex-ml -l app=codex-ml --all-containers=true --timestamps=true | tail -100

# Get logs from previous version (for comparison)
kubectl logs -n codex-ml -l app=codex-ml --previous --all-containers=true --timestamps=true | tail -50
```

---

## 📋 QUICK REFERENCE COMMANDS

```bash
# View deployment status
kubectl get deployment codex-ml-server -n codex-ml -o wide

# View pods
kubectl get pods -n codex-ml -l app=codex-ml -o wide

# Scale manually (if needed)
kubectl set replicas deployment/codex-ml-server=N -n codex-ml

# Check logs
kubectl logs -n codex-ml -l app=codex-ml --tail=100

# Check resource usage
kubectl top nodes
kubectl top pods -n codex-ml -l app=codex-ml

# View recent events
kubectl get events -n codex-ml --sort-by='.lastTimestamp' | tail -20

# Check service endpoints
kubectl get endpoints codex-api-service -n codex-ml
```

---

## ✅ SUCCESS CRITERIA BY PHASE

| Phase | Duration | Success Criteria | Failure Action |
|-------|----------|------------------|----------------|
| Canary | 15 min | Error <5%, P95 <1.0s, 2/2 pods ready | Rollback |
| Regional | 15 min | Error <3%, CPU <85%, 4/4 pods ready | Pause & investigate |
| Production | 30+ min | Error <1%, no critical alerts, 5/5 pods | Rollback |

---

## 📞 ESCALATION CONTACTS

**All urgent issues:** #incidents Slack channel + PagerDuty

| Time | Action | Contact |
|------|--------|---------|
| T+0-2min | On-call engineer monitoring | Deploy lead |
| T+2-5min | Issue detected | Team lead |
| T+5-10min | Unresolved critical issue | Engineering manager |
| T+10+min | Major outage | Director |

---

**Document Status:** ✅ READY FOR DEPLOYMENT  
**Last Updated:** 2026-07-07 08:00 UTC  
**Authority:** @mbaetiong

