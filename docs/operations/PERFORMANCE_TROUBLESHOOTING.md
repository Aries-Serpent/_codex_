# Performance Troubleshooting Playbook

**Version**: 1.0  
**Last Updated**: 2026-06-22  
**Maintainer**: Performance Engineering  
**SLA Target**: Response time p95 < 200ms, p99 < 500ms  

---

## Executive Summary

This playbook provides systematic procedures for identifying and resolving performance issues in production. It includes metrics interpretation, bottleneck identification techniques, and resolution strategies.

**Performance SLA Targets**:
- **Response Time (p95)**: < 200ms
- **Response Time (p99)**: < 500ms
- **Error Rate**: < 0.1%
- **Cache Hit Ratio**: > 80%
- **Database Query Time**: < 50ms (p95)

---

## Performance Metrics Interpretation

### 1.1 Key Performance Indicators (KPIs)

| Metric | Healthy Range | Warning | Critical |
|--------|---------------|---------|----------|
| Response Time (p95) | < 150ms | 150-200ms | > 200ms |
| Response Time (p99) | < 300ms | 300-500ms | > 500ms |
| Error Rate | < 0.01% | 0.01-0.1% | > 0.1% |
| CPU Utilization | 30-60% | 60-80% | > 80% |
| Memory Utilization | 40-70% | 70-85% | > 85% |
| Database Pool Utilization | 20-40% | 40-70% | > 70% |
| Cache Hit Ratio | > 85% | 70-85% | < 70% |
| Disk I/O Wait | < 5% | 5-10% | > 10% |

### 1.2 Querying Key Metrics

**Response Time Metrics**:

```bash
# Query p95 response time
curl 'http://localhost:9090/api/v1/query?query=histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))'

# Query p99 response time
curl 'http://localhost:9090/api/v1/query?query=histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))'

# Response time by endpoint
curl 'http://localhost:9090/api/v1/query?query=histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{handler="/api/v1/resource"}[5m]))'
```

**Resource Utilization**:

```bash
# CPU utilization
curl 'http://localhost:9090/api/v1/query?query=rate(process_cpu_seconds_total[5m])'

# Memory usage
curl 'http://localhost:9090/api/v1/query?query=process_resident_memory_bytes'

# Kubernetes node resources
kubectl top nodes
kubectl top pods -n production --containers
```

**Cache Performance**:

```bash
# Redis cache hit ratio
redis-cli -h $REDIS_ENDPOINT INFO stats | grep -E "hits|misses"

# Calculate hit ratio
redis-cli -h $REDIS_ENDPOINT INFO stats | awk '/hits:/{hits=$2} /misses:/{misses=$2} END{if(hits+misses>0) print "Hit Ratio: " (hits/(hits+misses))*100"%"}'
```

**Database Performance**:

```bash
# Query execution time
curl 'http://localhost:9090/api/v1/query?query=rate(pg_query_duration_seconds_bucket[5m])'

# Connection pool usage
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d codex_prod \
  -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"

# Slow query log
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d codex_prod \
  -c "SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

---

## Bottleneck Identification

### 2.1 Application-Level Bottlenecks

**Detection Procedure**:

```bash
# Step 1: Check application metrics in Prometheus
curl 'http://localhost:9090/api/v1/query?query=rate(http_request_duration_seconds_sum[5m])'

# Step 2: Check for high memory allocation rate
curl 'http://localhost:9090/api/v1/query?query=rate(go_memstats_alloc_bytes_total[5m])'

# Step 3: Check for goroutine leaks
curl 'http://localhost:9090/api/v1/query?query=go_goroutines'

# Step 4: Analyze CPU usage
kubectl top pods -n production -l app=codex-api --containers
```

**Common Application Bottlenecks**:

| Symptom | Root Cause | Investigation | Fix |
|---------|-----------|-----------------|-----|
| High CPU (> 80%) | CPU-intensive operation | Profile: `pprof` CPU profile | Optimize algorithm, add caching |
| Memory growing | Memory leak | Check allocation rate | Fix leak, add GC tuning |
| Goroutine leak | Goroutines not terminating | Monitor goroutine count | Add context cancellation |
| GC pauses | Large heaps | Tune GC settings | Reduce allocation rate |

**Profiling Application**:

```bash
# Get CPU profile from running application
kubectl port-forward -n production svc/codex-api 6060:6060 &
curl http://localhost:6060/debug/pprof/profile?seconds=30 > cpu.prof
go tool pprof cpu.prof
# In pprof: top10, list [function]

# Get memory profile
curl http://localhost:6060/debug/pprof/heap > mem.prof
go tool pprof mem.prof
```

### 2.2 Database Bottlenecks

**Detection Procedure**:

```bash
# Step 1: Check query performance
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d codex_prod \
  -c "SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY total_time DESC LIMIT 20;"

# Step 2: Check for missing indexes
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d codex_prod \
  -c "SELECT schemaname, tablename, indexname FROM pg_indexes WHERE schemaname NOT IN ('pg_catalog', 'information_schema');"

# Step 3: Check table bloat
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d codex_prod \
  -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) FROM pg_tables ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC LIMIT 10;"

# Step 4: Check connection pool status
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d codex_prod \
  -c "SELECT pid, usename, application_name, state, query_start FROM pg_stat_activity WHERE state != 'idle';"
```

**Database Performance Issues**:

| Issue | Symptom | Resolution |
|-------|---------|-----------|
| Slow queries | Response time > 200ms | Add index, optimize query |
| Inefficient query plan | Full table scan | Update table stats: `ANALYZE` |
| Connection pool exhaustion | "too many connections" error | Increase pool size, add connection retry |
| Lock contention | Queries waiting on locks | Check for long-running transactions |
| Index bloat | Index size > data size | Reindex: `REINDEX INDEX index_name` |

**Query Optimization Example**:

```bash
# Identify slow query
SLOW_QUERY="SELECT * FROM orders WHERE user_id = $1 AND created_at > now() - INTERVAL '30 days';"

# Explain query plan
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d codex_prod \
  -c "EXPLAIN (ANALYZE, BUFFERS) ${SLOW_QUERY}"

# If doing seq scan, create index
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d codex_prod \
  -c "CREATE INDEX idx_orders_user_created ON orders(user_id, created_at);"

# Verify index usage
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d codex_prod \
  -c "EXPLAIN (ANALYZE, BUFFERS) ${SLOW_QUERY}"
```

### 2.3 Cache Bottlenecks

**Detection Procedure**:

```bash
# Step 1: Check cache hit ratio
redis-cli -h $REDIS_ENDPOINT INFO stats

# Step 2: Check Redis memory usage
redis-cli -h $REDIS_ENDPOINT INFO memory | grep -E "used_memory|used_memory_human|maxmemory"

# Step 3: Check eviction policy
redis-cli -h $REDIS_ENDPOINT CONFIG GET maxmemory-policy

# Step 4: Check hot keys
redis-cli -h $REDIS_ENDPOINT --hotkeys
```

**Cache Optimization**:

| Issue | Cause | Fix |
|-------|-------|-----|
| Low hit ratio (< 70%) | Cache misses too high | Increase cache size, improve cache key strategy |
| High evictions | Cache full | Increase Redis memory, reduce TTL |
| Stale cache | Data not refreshing | Reduce TTL, implement cache invalidation |

**Cache Warming Strategy**:

```bash
# Pre-populate hot keys at startup
redis-cli -h $REDIS_ENDPOINT MSET \
  "config:feature-flags" '{"feature_a": true}' \
  "user-profile:trending" '[{"id":1}, {"id":2}]' \
  "leaderboard:top-100" '[...]'
```

### 2.4 Network and Infrastructure Bottlenecks

**Detection Procedure**:

```bash
# Step 1: Check network utilization
kubectl exec -n production pod-name -- ss -i | head -20

# Step 2: Check for packet loss
kubectl exec -n production pod-name -- ping -c 10 $DB_HOST

# Step 3: Check DNS resolution time
time kubectl exec -n production pod-name -- nslookup $DB_HOST

# Step 4: Monitor disk I/O
kubectl top nodes
iostat -x 1 10
```

**Infrastructure Bottlenecks**:

| Issue | Detection | Fix |
|-------|-----------|-----|
| Network saturation | High packet loss, retransmits | Add network bandwidth, enable compression |
| DNS slowness | nslookup > 100ms | Use local DNS cache, upgrade nameservers |
| Disk I/O contention | I/O wait > 10% | Add faster storage, optimize queries |
| Pod scheduling | Pending pods | Add cluster nodes, optimize resource requests |

---

## Resolution Strategies

### 3.1 Application Performance Optimization

**Strategy 1: Add Caching Layer**

```bash
# For frequently accessed data
# Before: Direct DB query for every request
# After: Cache in Redis with 5-minute TTL

# Example: Cache user profile
# In application code:
profile = redis.get(f"user-profile:{user_id}")
if not profile:
    profile = db.query(f"SELECT * FROM users WHERE id = {user_id}")
    redis.set(f"user-profile:{user_id}", profile, ex=300)
return profile
```

**Strategy 2: Optimize Database Queries**

```bash
# Bad query (full table scan):
SELECT * FROM orders WHERE customer_name LIKE '%John%'

# Good query (with index):
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
SELECT * FROM orders WHERE customer_id = 123

# Or use partial index for common filters:
CREATE INDEX idx_active_orders ON orders(customer_id) WHERE status = 'active';
```

**Strategy 3: Implement Connection Pooling**

```bash
# Configure connection pool in application
# Parameters:
# - Min connections: 5
# - Max connections: 50
# - Idle timeout: 300s
# - Max lifetime: 1800s

CONN_POOL_CONFIG="
pool_size: 50
max_overflow: 10
pool_recycle: 3600
pool_pre_ping: true
"
```

**Strategy 4: Batch Operations**

```bash
# Bad: Individual queries in loop
for user in users:
    db.query(f"INSERT INTO logs VALUES ({user.id}, ...)")

# Good: Batch insert
batch_insert_sql = "INSERT INTO logs (user_id, ...) VALUES " + \
    ",".join([f"({user.id}, ...)" for user in users])
db.execute(batch_insert_sql)
```

### 3.2 Database Optimization

**Optimization 1: Index Addition**

```bash
# Identify missing index need
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d codex_prod << EOF
-- Check for seq scans on large tables
SELECT schemaname, tablename, seq_scan
FROM pg_stat_user_tables
WHERE seq_scan > 1000
ORDER BY seq_scan DESC;
EOF

# Create needed indexes
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d codex_prod \
  -c "CREATE INDEX idx_orders_status_created ON orders(status, created_at);"
```

**Optimization 2: Query Refactoring**

```bash
# Original slow query (N+1 problem):
SELECT * FROM posts;
FOR EACH post:
    SELECT * FROM comments WHERE post_id = post.id;

# Optimized query (JOIN):
SELECT p.*, c.*
FROM posts p
LEFT JOIN comments c ON p.id = c.post_id
ORDER BY p.id, c.id;
```

**Optimization 3: Partitioning Large Tables**

```bash
# Create partitioned table for time-series data
CREATE TABLE events (
    id BIGSERIAL,
    timestamp TIMESTAMP,
    data JSONB
) PARTITION BY RANGE (timestamp);

CREATE TABLE events_2024_01 PARTITION OF events
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

### 3.3 Cache Strategy Adjustment

**Strategy 1: Multi-Level Caching**

```
Request → L1 Cache (In-Process)
  │ (Hit) → Return
  │ (Miss) → L2 Cache (Redis)
    │ (Hit) → Load to L1, Return
    │ (Miss) → Database
      │ Load to L2, Return
```

**Strategy 2: Cache Invalidation Pattern**

```bash
# TTL-based invalidation (safe, simple)
redis.set(f"user:{user_id}", data, ex=300)  # 5 min TTL

# Event-based invalidation (accurate)
# When user updates:
redis.delete(f"user:{user_id}")
redis.delete(f"user-profile:{user_id}")

# Hybrid approach (TTL + event)
redis.set(f"user:{user_id}", data, ex=3600)  # 1 hour TTL
# On update, delete immediately (event-based)
# But still expires if no update occurs
```

### 3.4 Infrastructure Scaling

**Strategy 1: Horizontal Scaling**

```bash
# Increase pod replicas for load distribution
kubectl scale deployment codex-api --replicas=20 -n production

# Verify distribution
kubectl get pods -n production -o wide | grep codex-api
```

**Strategy 2: Resource Limit Adjustment**

```bash
# Increase CPU/Memory allocation
kubectl set resources deployment codex-api \
  -n production \
  --requests=cpu=500m,memory=512Mi \
  --limits=cpu=1000m,memory=1Gi
```

**Strategy 3: Auto-scaling Configuration**

```bash
# Create HPA for automatic scaling
kubectl autoscale deployment codex-api \
  -n production \
  --min=10 --max=50 \
  --cpu-percent=70
```

---

## Performance Testing and Validation

### 4.1 Load Testing

**Setup Load Test**:

```bash
# Using Apache Bench
ab -n 10000 -c 100 http://${API_ENDPOINT}/api/v1/health

# Using Apache JMeter
jmeter -n -t load-test.jmx -l results.jtl -j jmeter.log

# Using Gatling
gatling.sh -s com.example.SampleSimulation
```

**Analyze Results**:

```
Requests per second: 1000
Mean response time: 150ms
Std deviation: 45ms
Min: 50ms
Max: 450ms
p95: 200ms
p99: 350ms
Error rate: 0%

Assessment: ✓ PASS - All metrics within SLA
```

### 4.2 Stress Testing

```bash
# Gradually increase load until failure
# Monitor metrics throughout

# Start with 100 RPS
ab -n 100000 -c 100 http://${API_ENDPOINT}/...

# Increase to 500 RPS
ab -n 500000 -c 500 http://${API_ENDPOINT}/...

# Identify breaking point
# Acceptable degradation:
# - Response time can increase 2-3x
# - Error rate should remain < 1%
# - System should recover when load returns to normal
```

---

## Performance Monitoring Dashboard

**Key Dashboard Panels**:

1. **Response Time Dashboard**
   - p50, p95, p99 latency
   - Latency by endpoint
   - Latency trend (24h, 7d)

2. **Error Rate Dashboard**
   - Overall error rate
   - Error rate by endpoint
   - Error types breakdown

3. **Resource Utilization Dashboard**
   - CPU usage by pod
   - Memory usage by pod
   - Network I/O

4. **Database Dashboard**
   - Query execution time
   - Connection pool utilization
   - Slow queries log

5. **Cache Dashboard**
   - Hit/miss ratio
   - Eviction rate
   - Redis memory usage

---

## Quick Reference: Common Performance Issues

| Issue | Root Cause | Quick Check | Fix |
|-------|-----------|-------------|-----|
| High response time | DB overload | `PGPASSWORD=$DB_PASSWORD psql ... -c "SELECT count(*) FROM pg_stat_activity WHERE state='active';"` | Add DB replicas, optimize queries | <!-- pragma: allowlist secret -->
| High error rate | OOM killer | `kubectl describe pod pod-name \| grep OOMKilled` | Increase memory, find leak |
| CPU spike | Runaway process | `kubectl top pods -n production` | Kill pod, deploy fix |
| Cache misses | Invalid strategy | `redis-cli INFO stats` | Adjust cache key pattern |
| Slow API | N+1 queries | `PGPASSWORD=$DB_PASSWORD psql ... -c "SELECT query, calls FROM pg_stat_statements ORDER BY calls DESC LIMIT 10;"` | Use JOIN, add index | <!-- pragma: allowlist secret -->

---

**Document Version**: 1.0  
**Last Reviewed**: 2024-01-15  
**Next Review Date**: 2024-02-15
