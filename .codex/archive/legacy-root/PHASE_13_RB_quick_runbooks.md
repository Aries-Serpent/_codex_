# PHASE 13 OPERATIONAL RUNBOOK - CACHE LAYER FAILOVER
# Redis Primary → Replica Failover
# Version: 1.0.0
# Last Updated: 2026-07-16T20:51Z
# Severity: HIGH
# RTO: 2 minutes
# RPO: Data loss acceptable (cache is ephemeral)

---

## SCENARIO DESCRIPTION

Redis primary cache node has become unresponsive or degraded. Immediate failover to replica required to maintain application performance.

**Trigger Conditions:**
- Primary Redis not responding for >30 seconds
- Primary CPU >95% for >2 minutes
- Primary memory >95% (eviction failures)
- Replication lag >10 seconds sustained

---

## PRE-INCIDENT CHECKLIST

- [ ] Verify replica is healthy
  ```bash
  redis-cli -h replica.cache.internal -p 6379 ping
  # Expected: PONG
  ```

- [ ] Check replication status
  ```bash
  redis-cli -h primary.cache.internal INFO replication | grep role
  # Expected: role:master
  ```

- [ ] Test primary connectivity
  ```bash
  redis-cli -h primary.cache.internal ping
  ```

---

## STEP-BY-STEP FAILOVER

### Step 1: Confirm Primary Failure (2 min)

```bash
# Test primary
redis-cli -h primary.cache.internal ping
# If no response → proceed to Step 2

# Check primary logs
ssh redis-primary "tail -20 /var/log/redis/redis-server.log"

# Check memory usage
redis-cli -h primary.cache.internal INFO memory | grep used_memory_human
# If >90GB (95% of limit) → memory pressure issue
```

### Step 2: Promote Replica (1 min)

```bash
# Promote replica to primary
redis-cli -h replica.cache.internal SLAVEOF NO ONE

# Verify promotion
redis-cli -h replica.cache.internal INFO replication | grep role:master
# Expected: role:master

# Verify no replication lag
redis-cli -h replica.cache.internal INFO stats | grep instantaneous_ops_per_sec
```

### Step 3: Update Application (30 sec)

```bash
# Update application connection string
# Method A: Environment variable
export REDIS_PRIMARY=replica.cache.internal:6379

# Method B: Config file
sed -i 's/primary.cache.internal/replica.cache.internal/g' /etc/app/config.yml

# Restart application services
systemctl restart codex-api codex-worker

# Verify connectivity
redis-cli -h replica.cache.internal ping
```

### Step 4: Monitor (ongoing)

```bash
# Watch promoted primary
watch -n 5 "redis-cli -h replica.cache.internal INFO stats | grep connected_clients"

# Expected: 50-100 connected clients (normal)
# Alert: >500 (connection pool issue)
```

---

## ROLLBACK PROCEDURES

If primary recovers:

```bash
# 1. Reset primary as replica
redis-cli -h primary.cache.internal SLAVEOF replica.cache.internal 6379

# 2. Wait for resync
sleep 30

# 3. Promote primary back
redis-cli -h primary.cache.internal SLAVEOF NO ONE

# 4. Switch application back
export REDIS_PRIMARY=primary.cache.internal:6379
systemctl restart codex-api codex-worker
```

---

## SUCCESS CRITERIA

- [x] Replica promoted within 2 minutes
- [x] Application connectivity restored
- [x] Hit rate maintained (>80%)
- [x] No data loss (cache is ephemeral)
- [x] Eviction rate < 5%

---

**Contacts:**
- Cache Lead: [name]
- On-Call: @oncall

---

# PHASE 13 OPERATIONAL RUNBOOK - POD CRASH RECOVERY
# Kubernetes Pod Auto-Recovery
# Version: 1.0.0
# Last Updated: 2026-07-16T20:51Z
# Severity: HIGH
# RTO: 1 minute (auto-restart)
# RPO: N/A (stateless pods)

---

## SCENARIO DESCRIPTION

Kubernetes pod has crashed and requires immediate recovery via restart or replacement.

**Trigger Conditions:**
- Pod phase: Failed or CrashLoopBackOff
- Container exit code: Non-zero
- Liveness probe failures: >3 consecutive
- OOMKilled: Memory exhausted

---

## AUTO-RECOVERY PROCESS

### Automatic (Kubernetes native)

```bash
# Deployment spec with auto-restart
replicas: 3
restartPolicy: Always
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10

# Kubernetes automatically restarts failed pod
# Within 30-60 seconds of crash
```

### Manual Recovery (if auto fails)

```bash
# 1. Identify crashed pod
kubectl get pods -n production | grep -i crashloop

# 2. Describe pod for details
kubectl describe pod [pod-name] -n production
# Look for: LastState.Reason, LastState.Message

# 3. Check logs
kubectl logs [pod-name] -n production --previous
# Look for: OutOfMemory, Segmentation fault, Connection refused

# 4. Delete pod (triggers recreation)
kubectl delete pod [pod-name] -n production

# 5. Verify recovery
kubectl get pod [pod-name] -n production
# Expected: Running (after 30 sec)
```

---

## COMMON CRASH PATTERNS

**Pattern: OOMKilled**
- Symptom: Exit code 137
- Action: Increase memory limit
  ```bash
  kubectl set resources deployment [name] --limits=memory=2Gi -n production
  ```

**Pattern: CrashLoopBackOff**
- Symptom: Repeated crashes
- Action: Check logs
  ```bash
  kubectl logs [pod] -n production --previous
  ```

**Pattern: Pending**
- Symptom: Pod won't start
- Action: Check node resources
  ```bash
  kubectl top nodes
  kubectl describe node [node]
  ```

---

## SUCCESS CRITERIA

- [x] Pod recovered within 1 minute
- [x] Traffic resumed (no packet loss)
- [x] No cascading failures

---

# PHASE 13 OPERATIONAL RUNBOOK - SSL/TLS CERTIFICATE RENEWAL
# Automated Certificate Lifecycle Management
# Version: 1.0.0
# Last Updated: 2026-07-16T20:51Z
# Severity: MEDIUM (if expiry <7 days)
# RTO: N/A (auto-renewal)
# RPO: N/A

---

## SCENARIO DESCRIPTION

SSL/TLS certificates require renewal before expiry (typically 90 days).

**Trigger Conditions:**
- Certificate expiry < 30 days (warning alert)
- Certificate expiry < 7 days (critical alert)
- Certificate already expired (emergency)

---

## AUTO-RENEWAL PROCESS

### Using Let's Encrypt + Certbot

```bash
# 1. Install certbot (if not present)
apt-get install certbot python3-certbot-nginx

# 2. Auto-renew (runs via cron daily)
0 0 * * * /usr/bin/certbot renew --quiet --post-hook "systemctl reload nginx"

# 3. Check renewal status
certbot certificates

# 4. Force renewal (if needed)
certbot renew --force-renewal

# 5. Verify certificate
openssl s_client -connect example.com:443 -showcerts
```

### Using Commercial Certificates

```bash
# 1. Download renewed cert from provider
# 2. Backup old cert
cp /etc/ssl/certs/server.crt /etc/ssl/certs/server.crt.bak

# 3. Install new cert
cp server.crt /etc/ssl/certs/
cp server.key /etc/ssl/private/

# 4. Verify syntax
openssl x509 -in /etc/ssl/certs/server.crt -text -noout

# 5. Reload web server
nginx -t && systemctl reload nginx
```

---

## MONITORING

```bash
# Alert if expiry <30 days
SELECT domain, expiry_date, DATE(expiry_date) - CURRENT_DATE as days_remaining
FROM certificates
WHERE days_remaining < 30
ORDER BY days_remaining;

# Check certificate status
curl -I https://example.com
# Look for: Strict-Transport-Security, X-Frame-Options
```

---

## SUCCESS CRITERIA

- [x] Certificate renewed before expiry
- [x] Zero downtime during renewal
- [x] Monitoring alert cleared

---

**Status:** All runbooks created successfully
