# Production Deployment Troubleshooting Guide
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Last Updated**: 2026-07-08  
**Version**: 1.0  
**Audience**: DevOps engineers, operations teams, support engineers  
**Tier**: Production-Ready

---

## Table of Contents

1. [Deployment Troubleshooting](#deployment-troubleshooting)
2. [Application Issues](#application-issues)
3. [Database Issues](#database-issues)
4. [Infrastructure Issues](#infrastructure-issues)
5. [Performance Issues](#performance-issues)
6. [Security Issues](#security-issues)
7. [Disaster Recovery Procedures](#disaster-recovery-procedures)

---

## Deployment Troubleshooting

### Issue: Container Fails to Start

**Symptoms**: Container repeatedly crashes or fails to start

**Diagnostic Steps**:
```bash
# 1. Check container logs
docker logs <container-id>
# or for Kubernetes
kubectl logs -f <pod-name> -n <namespace>

# 2. Check container status
docker inspect <container-id>
# or for Kubernetes
kubectl describe pod <pod-name> -n <namespace>

# 3. Check resource limits
docker stats
# or for Kubernetes
kubectl top pods -n <namespace>

# 4. Verify image integrity
docker pull <image>
docker run --rm <image> /bin/bash -c "echo 'OK'"

# 5. Check environment variables
docker inspect <container-id> | grep -A 20 "Env"
# or for Kubernetes
kubectl get pod <pod-name> -n <namespace> -o yaml | grep -A 20 "env:"
```

**Common Root Causes**:

1. **Missing Environment Variables**
   ```bash
   # Check application startup logs
   # Look for: "ERROR: Missing environment variable X"
   
   # Solution: Add missing environment variable
   # For Docker
   docker run -e DATABASE_URL=... -e API_KEY=...
   
   # For Kubernetes
   kubectl set env deployment/codex-ml DATABASE_URL=... API_KEY=...
   ```

2. **Port Already in Use**
   ```bash
   # Check if port is in use
   lsof -i :8000
   netstat -tlnp | grep 8000
   
   # Solution: Use different port or kill conflicting process
   kill -9 <pid>
   ```

3. **Insufficient Disk Space**
   ```bash
   # Check disk usage
   df -h
   docker system df
   
   # Solution: Clean up unused containers/images
   docker system prune -a
   docker image prune
   ```

4. **Memory Issues**
   ```bash
   # Check memory limits
   docker stats <container-id>
   
   # Solution: Increase memory limit
   docker run -m 4g <image>
   
   # For Kubernetes
   kubectl set resources deployment codex-ml \
     --limits=memory=4Gi,cpu=2 \
     --requests=memory=2Gi,cpu=1
   ```

### Issue: Service Not Responding

**Symptoms**: Service is running but not responding to requests

**Diagnostic Steps**:
```bash
# 1. Check service health
curl -v http://localhost:8000/health

# 2. Check service connectivity
nc -zv localhost 8000
telnet localhost 8000

# 3. Check service listening ports
netstat -tlnp | grep 8000
ss -tlnp | grep 8000

# 4. Check firewall rules
sudo iptables -L -n
sudo firewall-cmd --list-all

# 5. Check for process crashes
dmesg | tail -50
journalctl -xe -u docker
```

**Solutions**:
```bash
# Restart service
docker restart <container-id>
# or for Kubernetes
kubectl rollout restart deployment/codex-ml -n <namespace>

# Check recent crashes
docker events --filter "type=container"

# Tail logs with timestamps
docker logs --timestamps --tail 100 <container-id>
```

---

## Application Issues

### Issue: High Memory Usage

**Symptoms**: Container memory keeps increasing, leading to OOM kills

**Investigation**:
```bash
# 1. Monitor memory over time
while true; do
  docker stats --no-stream <container-id> | tail -1
  sleep 5
done

# 2. Identify memory leaks in logs
grep -i "memory\|leak\|oom" /var/log/docker.log

# 3. Check garbage collection in application
# Look for GC logs in application output

# 4. Analyze heap dumps (if Java/similar)
jstat -gc -h3 <pid> 1s
```

**Solutions**:
```bash
# Increase container memory limit
docker update --memory 4g <container-id>

# For Kubernetes
kubectl set resources deployment codex-ml \
  --limits=memory=4Gi \
  --requests=memory=2Gi -n <namespace>

# Enable memory swap
docker run --memory 4g --memory-swap 8g <image>

# Implement memory caching/pooling
# Code-level optimization required
```

### Issue: High CPU Usage

**Symptoms**: CPU utilization constantly above 80%

**Investigation**:
```bash
# 1. Monitor CPU per process
top -b -n 1 | head -20
ps aux --sort=-%cpu | head -10

# 2. Check thread count
ps -eLf | wc -l

# 3. Profile CPU
docker exec <container> top -b -n 1

# 4. Check for busy-waiting
docker exec <container> strace -c -p <pid>
```

**Solutions**:
```bash
# Scale horizontally
docker service scale codex-ml=5

# For Kubernetes
kubectl scale deployment codex-ml --replicas=5 -n <namespace>

# Optimize application code
# - Use connection pooling
# - Cache expensive computations
# - Use async/await for I/O operations

# Tune application settings
# - Reduce worker threads
# - Adjust batch sizes
# - Optimize database queries
```

### Issue: Response Time Degradation

**Symptoms**: API responses slow, taking > 5 seconds

**Investigation**:
```bash
# 1. Check response times with Apache Bench
ab -n 100 -c 10 http://localhost:8000/api/health

# 2. Check for slow queries
# Enable query logging in database
SET log_statement = 'all';
EXPLAIN ANALYZE <slow-query>;

# 3. Monitor network latency
ping <database-host>
iperf3 -c <host> -t 10

# 4. Check resource utilization
vmstat 1 10
iostat -x 1 10
```

**Solutions**:
```bash
# Add caching layer
# - Implement Redis caching
# - Use CDN for static content
# - Cache database query results

# Optimize queries
EXPLAIN ANALYZE <query>;
CREATE INDEX <index> ON <table>(<column>);

# Scale database
# - Read replicas for read-heavy workloads
# - Connection pooling
# - Database sharding for large datasets
```

---

## Database Issues

### Issue: Database Connection Pool Exhaustion

**Symptoms**: "Connection pool full" or "Too many connections" errors

**Investigation**:
```bash
# 1. Check current connections
psql -U postgres -d codex -c "SELECT count(*) FROM pg_stat_activity;"

# 2. Identify idle connections
psql -U postgres -d codex -c \
  "SELECT pid, usename, state FROM pg_stat_activity WHERE state = 'idle';"

# 3. Check connection limits
psql -U postgres -d codex -c "SHOW max_connections;"

# 4. Monitor connection pool
# Check application pool metrics in monitoring system
```

**Solutions**:
```sql
-- Increase connection limit
ALTER SYSTEM SET max_connections = 1000;
SELECT pg_reload_conf();

-- Terminate idle connections
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'idle' 
AND query_start < NOW() - INTERVAL '30 minutes';

-- Monitor and tune application pool
-- Reduce connections per application instance
-- Use connection pooling (PgBouncer, HikariCP)

-- Enable connection pooling
PgBouncer configuration:
[databases]
codex = host=localhost port=5432 dbname=codex

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
```

### Issue: Replication Lag

**Symptoms**: Secondary database lags behind primary, stale reads

**Investigation**:
```bash
# 1. Check replication lag
psql -U postgres -d codex -c \
  "SELECT client_addr, state, sync_state, write_lag FROM pg_stat_replication;"

# 2. Monitor WAL positions
psql -U postgres -d codex -c "SELECT pg_current_wal_lsn();"
psql -U postgres -h replica_host -d codex -c "SELECT pg_last_wal_replay_lsn();"

# 3. Check network connectivity
ping <replica-host>
iperf3 -c <replica-host>
```

**Solutions**:
```sql
-- Increase WAL buffer
ALTER SYSTEM SET wal_buffers = '16MB';

-- Tune replication settings
ALTER SYSTEM SET max_wal_senders = 10;
ALTER SYSTEM SET wal_keep_size = '1GB';

-- Monitor synchronous replication
ALTER SYSTEM SET synchronous_commit = 'remote_apply';

-- Reload configuration
SELECT pg_reload_conf();

-- Check replica is catching up
MONITOR: Watch write_lag and flush_lag in pg_stat_replication
```

### Issue: Slow Queries

**Symptoms**: Specific queries take excessive time

**Diagnostic Steps**:
```bash
# 1. Enable query logging
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_duration = true;
ALTER SYSTEM SET log_min_duration_statement = 1000;  # Log queries > 1s
SELECT pg_reload_conf();

# 2. Analyze slow query
EXPLAIN ANALYZE <query>;

# 3. Check indexes
SELECT * FROM pg_stat_user_indexes;

# 4. Check table statistics
ANALYZE <table>;
```

**Solutions**:
```sql
-- Create missing indexes
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_transaction_date ON transactions(created_at);

-- Update statistics
ANALYZE <table>;

-- Rewrite inefficient query
-- Before
SELECT * FROM orders o 
JOIN customers c ON o.customer_id = c.id 
WHERE c.country = 'US' AND o.created_at > '2026-01-01';

-- After (with proper indexes and JOIN optimization)
CREATE INDEX idx_customers_country ON customers(country);
CREATE INDEX idx_orders_customer_date ON orders(customer_id, created_at);

SELECT o.* FROM orders o 
WHERE o.customer_id IN (
  SELECT id FROM customers WHERE country = 'US'
) AND o.created_at > '2026-01-01';
```

---

## Infrastructure Issues

### Issue: Kubernetes Pod Stuck in Pending State

**Symptoms**: Pod never starts, status = Pending

**Investigation**:
```bash
# 1. Check pod events
kubectl describe pod <pod-name> -n <namespace>

# 2. Check node resources
kubectl top nodes
kubectl describe nodes | grep -A 10 "Allocated resources"

# 3. Check resource requests/limits
kubectl get pod <pod-name> -n <namespace> -o yaml | grep -A 10 "resources:"

# 4. Check node selector constraints
kubectl get pod <pod-name> -n <namespace> -o yaml | grep -A 5 "nodeSelector:"
```

**Solutions**:
```bash
# Solution 1: Insufficient node resources
# Scale cluster
kubectl scale deployment <deployment> --replicas=5

# Or add more nodes
# For EKS
eksctl create nodegroup ...

# For AKS
az aks nodepool add ...

# For GKE
gcloud container node-pools create ...

# Solution 2: Node selector not matching
kubectl get nodes --show-labels
kubectl label nodes <node-name> <label-key>=<label-value>

# Solution 3: Resource request too high
kubectl set resources deployment <deployment> \
  --requests=memory=1Gi,cpu=500m
```

### Issue: Network Connectivity Problems

**Symptoms**: Pods cannot communicate, DNS not resolving

**Investigation**:
```bash
# 1. Test DNS resolution
kubectl run -it --rm debug --image=busybox --restart=Never -- \
  nslookup kubernetes.default

# 2. Test connectivity to service
kubectl run -it --rm debug --image=busybox --restart=Never -- \
  wget -O- http://codex-ml-service:80

# 3. Check network policies
kubectl get networkpolicies -A

# 4. Check CoreDNS
kubectl get pods -n kube-system
kubectl logs -n kube-system -l k8s-app=kube-dns
```

**Solutions**:
```bash
# Solution 1: DNS issues
# Restart CoreDNS
kubectl rollout restart deployment/coredns -n kube-system

# Clear DNS cache
kubectl run -it --rm debug --image=busybox --restart=Never -- \
  sh -c "cat /etc/resolv.conf"

# Solution 2: Network policy blocking traffic
kubectl get networkpolicy -A
kubectl delete networkpolicy <policy-name>

# Solution 3: Service not found
kubectl get svc -A | grep <service-name>
kubectl describe svc <service-name> -n <namespace>
```

---

## Performance Issues

### Issue: Load Balancer Response Time High

**Symptoms**: Increased latency at load balancer level

**Investigation**:
```bash
# 1. Check ALB/CLB metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name TargetResponseTime \
  --dimensions Name=LoadBalancer,Value=<alb-name> \
  --start-time 2026-07-08T00:00:00Z \
  --end-time 2026-07-08T01:00:00Z \
  --period 300 \
  --statistics Average

# 2. Check target health
aws elbv2 describe-target-health \
  --target-group-arn <target-group-arn>

# 3. Check active connections
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name ActiveConnectionCount
```

**Solutions**:
```bash
# Scale targets
aws autoscaling set-desired-capacity \
  --auto-scaling-group-name <asg-name> \
  --desired-capacity 10

# Optimize target
# - Reduce response time in application
# - Increase worker processes
# - Add caching layer

# Check for connection draining issues
aws elbv2 modify-target-group-attributes \
  --target-group-arn <target-group-arn> \
  --attributes Key=deregistration_delay.timeout_seconds,Value=30
```

---

## Security Issues

### Issue: Unauthorized API Access

**Symptoms**: Requests being rejected with 401/403 errors

**Investigation**:
```bash
# 1. Check authentication logs
grep "401\|403\|Unauthorized" /var/log/application.log

# 2. Verify JWT token
jwt.io  # Paste token for inspection

# 3. Check API key validity
curl -H "Authorization: ******" http://api/endpoint

# 4. Check RBAC policies
kubectl get rolebindings -A
```

**Solutions**:
```bash
# Regenerate API credentials
# For JWT tokens
python -c "import jwt; print(jwt.encode({'user': 'admin'}, 'secret', 'HS256'))"

# For API keys
curl -X POST http://api/auth/generate-key

# Update authorization headers
curl -H "Authorization: ******" http://api/endpoint

# Check permission scope
curl -X GET "http://api/me" -H "Authorization: ******"
```

### Issue: SSL/TLS Certificate Expiration

**Symptoms**: Browser warning, HTTPS requests failing

**Investigation**:
```bash
# 1. Check certificate expiration
openssl x509 -in /path/to/cert.pem -text -noout | grep "Not After"

# 2. Check certificate in use
openssl s_client -connect <domain>:443 -showcerts

# 3. Check certificate renewal status
# For Let's Encrypt
certbot certificates

# For AWS Certificate Manager
aws acm describe-certificate --certificate-arn <arn>
```

**Solutions**:
```bash
# Renew certificate
certbot renew --force-renewal

# Update certificate in load balancer
aws acm-pca issue-certificate \
  --certificate-authority-arn <ca-arn> \
  --csr fileb://csr.pem

# Or create new certificate
aws acm request-certificate \
  --domain-name example.com \
  --validation-method DNS

# Update certificate in service
kubectl create secret tls tls-secret \
  --cert=path/to/cert.crt \
  --key=path/to/key.key \
  --dry-run=client -o yaml | kubectl apply -f -
```

---

## Disaster Recovery Procedures

### Failover Checklist

```
Automated Failover Workflow
├─ Detect Primary Failure (Health check timeout)
├─ Validate Secondary Health
├─ Update DNS Records (Route 53)
├─ Promote Secondary Database
├─ Scale Up Secondary Application
├─ Run Post-Failover Validation
│  ├─ Test API endpoints
│  ├─ Verify database connectivity
│  ├─ Check application metrics
│  └─ Confirm data consistency
└─ Notify Operations Team

Manual Failover Steps
1. Assess primary region status
2. Execute failover scripts
3. Update DNS/load balancer
4. Monitor secondary metrics
5. Prepare primary recovery
6. Test failback procedure
```

### Database Recovery Procedure

```bash
# 1. Identify backup to restore
aws s3 ls s3://backup-bucket/postgres/

# 2. Create recovery instance
aws rds create-db-instance-from-db-snapshot \
  --db-instance-identifier recovered-db \
  --db-snapshot-identifier <snapshot-id>

# 3. Verify recovery
psql -h <recovered-db-endpoint> -U admin -d codex

# 4. Run recovery tests
./scripts/validate-db-recovery.sh

# 5. Switchover to recovered database
# Update connection strings and restart application
```

---

## Common Error Messages & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `CrashLoopBackOff` | Application crash loop | Check logs, fix startup error, redeploy |
| `ImagePullBackOff` | Cannot pull image | Verify image exists, check registry auth |
| `OOMKilled` | Out of memory | Increase memory limit, optimize code |
| `Connection refused` | Port not listening | Verify port number, check firewall |
| `Timeout` | Service not responding | Check service health, increase timeout |
| `Permission denied` | Insufficient permissions | Update RBAC, check file permissions |
| `TLS handshake failed` | Certificate issue | Verify certificate, update cert chain |

---

## Emergency Contacts & Escalation

```
Level 1: On-call Engineer
- Response time: 5 minutes
- Handles: Basic troubleshooting
- Contact: Slack @on-call

Level 2: Senior DevOps Engineer
- Response time: 15 minutes
- Handles: Complex infrastructure issues
- Contact: PagerDuty

Level 3: Engineering Manager
- Response time: 30 minutes
- Handles: Critical outages, decisions
- Contact: Phone on-call

Incident Command Center
- P1 (Critical): Declare incident
- P2 (Major): Notify stakeholders
- P3 (Minor): Log for review
```

---

**Remember**: Always check application logs first, then infrastructure logs. Document all issues and solutions for future reference.

