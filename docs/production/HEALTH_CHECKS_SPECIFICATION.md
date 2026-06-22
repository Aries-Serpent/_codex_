# Production Health Checks Specification

**Last Updated:** 2026-06-22
**Version**: 1.0.0
**Status**: Deployment Ready
**Date**: 2026-06-14

---

## 📋 Overview

This document specifies all health check endpoints for production services, their SLAs, failure modes, and remediation procedures.

---

## 🏥 Health Check Categories

### Category A: Liveness Probes
**Purpose**: Determine if service is running (Kubernetes kubelet uses for restart decisions)
**Endpoint**: `GET /health/live`
**Interval**: 10 seconds
**Timeout**: 2 seconds
**Response**: HTTP 200 OK (always, unless process is dead)

```json
{
  "status": "alive",
  "timestamp": "2026-06-14T15:30:45.123Z",
  "uptime_seconds": 86400,
  "pid": 12345,
  "version": "1.2.3"
}
```

### Category B: Readiness Probes
**Purpose**: Determine if service can accept traffic (Kubernetes load balancer uses for traffic routing)
**Endpoint**: `GET /health/ready`
**Interval**: 30 seconds
**Timeout**: 5 seconds
**Response**: HTTP 200 OK if ready, HTTP 503 Service Unavailable if not ready

```json
{
  "status": "ready",
  "ready_since": "2026-06-14T15:20:00.000Z",
  "checks": {
    "database": {
      "status": "ok",
      "latency_ms": 5,
      "connections": 45,
      "max_connections": 100
    },
    "cache": {
      "status": "ok",
      "latency_ms": 2,
      "memory_mb": 512,
      "max_memory_mb": 1024
    },
    "message_queue": {
      "status": "ok",
      "latency_ms": 10,
      "queue_depth": 234
    },
    "disk_space": {
      "status": "ok",
      "used_gb": 45,
      "total_gb": 100,
      "threshold_gb": 80
    },
    "memory": {
      "status": "ok",
      "used_mb": 2048,
      "total_mb": 4096,
      "threshold_mb": 3686
    }
  }
}
```

### Category C: Detailed Health
**Purpose**: Deep status check for operators and dashboards
**Endpoint**: `GET /health/detailed`
**Interval**: 60 seconds
**Timeout**: 10 seconds
**Response**: HTTP 200 OK with detailed status

```json
{
  "status": "healthy",
  "timestamp": "2026-06-14T15:30:45.123Z",
  "health_dimensions": {
    "security": {
      "status": "healthy",
      "metrics": {
        "failed_auth_attempts_5m": 3,
        "failed_auth_threshold": 100,
        "suspicious_ips": 0,
        "rate_limited_clients": 5,
        "tls_errors_5m": 0
      }
    },
    "performance": {
      "status": "healthy",
      "metrics": {
        "p50_latency_ms": 45,
        "p95_latency_ms": 120,
        "p99_latency_ms": 350,
        "request_rate": 1200,
        "error_rate": 0.0015,
        "cpu_percent": 45,
        "memory_percent": 62
      }
    },
    "availability": {
      "status": "healthy",
      "metrics": {
        "uptime_percentage": 99.98,
        "last_restart": "7d ago",
        "failed_dependencies": 0,
        "ongoing_deployments": 0
      }
    },
    "state": {
      "status": "healthy",
      "metrics": {
        "data_consistency_check": "passed",
        "schema_violations": 0,
        "stale_cache_items": 0,
        "config_drift": false
      }
    },
    "resource": {
      "status": "healthy",
      "metrics": {
        "cpu_percent": 45,
        "memory_percent": 62,
        "disk_percent": 35,
        "open_file_handles": 156,
        "network_connections": 89
      }
    }
  },
  "dependencies": {
    "database": {
      "status": "connected",
      "latency_ms": 5,
      "pool_utilization": 0.45,
      "pool_connections": 45,
      "pool_max": 100,
      "errors_5m": 0
    },
    "cache": {
      "status": "connected",
      "latency_ms": 2,
      "hit_ratio": 0.92,
      "memory_mb": 512,
      "errors_5m": 0
    },
    "message_queue": {
      "status": "connected",
      "latency_ms": 10,
      "pending_messages": 234,
      "lag_seconds": 0.5,
      "consumer_lag": 0.5,
      "errors_5m": 0
    },
    "elasticsearch": {
      "status": "connected",
      "latency_ms": 20,
      "indices": 45,
      "disk_usage_gb": 120,
      "errors_5m": 0
    },
    "external_api": {
      "status": "available",
      "latency_ms": 150,
      "success_rate": 0.9999,
      "errors_5m": 0
    }
  },
  "active_alerts": [
    {
      "name": "high_memory_usage",
      "severity": "warning",
      "description": "Memory usage at 62%, approaching threshold of 85%",
      "triggered_at": "2026-06-14T15:25:00.000Z"
    }
  ]
}
```

---

## 📊 Service Health Check Matrix

| Service | Liveness | Readiness | Detailed | Database | Cache | Queue | Disk | Memory |
|---------|----------|-----------|----------|----------|-------|-------|------|--------|
| **API Gateway** | ✅ 10s/2s | ✅ 30s/5s | ✅ 60s/10s | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Auth Service** | ✅ 10s/2s | ✅ 30s/5s | ✅ 60s/10s | ✅ | ✅ | ✅ | ✅ | ✅ |
| **User Service** | ✅ 10s/2s | ✅ 30s/5s | ✅ 60s/10s | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Order Service** | ✅ 10s/2s | ✅ 30s/5s | ✅ 60s/10s | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Payment Service** | ✅ 10s/2s | ✅ 30s/5s | ✅ 60s/10s | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Analytics Service** | ✅ 10s/2s | ✅ 60s/10s | ✅ 120s/15s | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Notification Service** | ✅ 10s/2s | ✅ 30s/5s | ✅ 60s/10s | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 🔍 Dependency Health Checks

### Database Health Check

**Check Type**: Direct connection test + query
**Timeout**: 5 seconds
**Interval**: 60 seconds

```python
def check_database():
    try:
        start = time.time()
        result = db.execute("SELECT 1")  # Simple query
        latency = (time.time() - start) * 1000
        
        pool_size = db.pool.qsize()
        pool_max = db.pool.maxsize
        
        return {
            "status": "connected" if latency < 5000 else "slow",
            "latency_ms": latency,
            "pool_connections": pool_max - pool_size,
            "pool_max": pool_max,
            "errors_5m": get_error_count("database", "5m")
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "disconnected",
            "error": str(e),
            "errors_5m": get_error_count("database", "5m")
        }
```

### Cache Health Check

**Check Type**: Set/Get operation
**Timeout**: 2 seconds
**Interval**: 30 seconds

```python
def check_cache():
    try:
        start = time.time()
        test_key = f"_health_check_{uuid.uuid4()}"
        cache.set(test_key, "ok", ex=10)
        value = cache.get(test_key)
        latency = (time.time() - start) * 1000
        cache.delete(test_key)
        
        info = cache.info()
        hit_ratio = info.hits / (info.hits + info.misses) if (info.hits + info.misses) > 0 else 0
        
        return {
            "status": "connected" if value == "ok" and latency < 2000 else "degraded",
            "latency_ms": latency,
            "hit_ratio": hit_ratio,
            "memory_mb": info.used_memory / (1024 * 1024),
            "errors_5m": get_error_count("cache", "5m")
        }
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        return {
            "status": "disconnected",
            "error": str(e),
            "errors_5m": get_error_count("cache", "5m")
        }
```

### Message Queue Health Check

**Check Type**: Publish test message + check lag
**Timeout**: 5 seconds
**Interval**: 60 seconds

```python
def check_message_queue():
    try:
        start = time.time()
        test_id = str(uuid.uuid4())
        
        # Publish test message
        producer.send("_health_check", 
                     {"test_id": test_id, "timestamp": time.time()})
        
        latency = (time.time() - start) * 1000
        
        # Check consumer lag
        lag = get_consumer_lag()
        
        return {
            "status": "connected" if latency < 5000 and lag < 60 else "degraded",
            "latency_ms": latency,
            "pending_messages": get_queue_depth(),
            "lag_seconds": lag,
            "errors_5m": get_error_count("queue", "5m")
        }
    except Exception as e:
        logger.error(f"Queue health check failed: {e}")
        return {
            "status": "disconnected",
            "error": str(e),
            "errors_5m": get_error_count("queue", "5m")
        }
```

---

## ⚠️ Health Check Failure Modes

### Scenario 1: Database Slow (Latency >5s)

**Detection**:
- Database latency increases above 5 seconds
- Query timeouts increase
- Connection pool utilization >80%

**Readiness Impact**:
- Return HTTP 503 (Service Unavailable)
- Kubernetes removes from load balancer
- Auto-scaling may trigger

**Remediation**:
1. Check database connections (connection leaks?)
2. Check slow query log
3. Check replication lag (if replicated)
4. Restart connection pool / redeploy pod

### Scenario 2: Cache Connection Lost

**Detection**:
- Cache health check fails consistently
- Cache miss rate increases
- Response latency increases

**Readiness Impact**:
- Readiness check may still pass (service degrades, not fails)
- But warning alert triggers
- Dashboard shows cache as red

**Remediation**:
1. Check cache connectivity
2. Restart cache client
3. Failover to secondary cache
4. Redeploy pod if issue persists

### Scenario 3: Message Queue Lag >60s

**Detection**:
- Consumer lag exceeds 60 seconds
- Queue depth increases
- Event processing latency increases

**Readiness Impact**:
- Readiness check fails if lag is critical
- Return HTTP 503
- Kubernetes stops routing traffic

**Remediation**:
1. Scale up consumer group
2. Check for poison messages
3. Check downstream processing
4. Drain and replay messages if corrupted

### Scenario 4: Disk Space >85%

**Detection**:
- Disk usage exceeds 85% threshold
- Log files unable to rotate
- New writes may start failing

**Readiness Impact**:
- Readiness check fails if >90%
- Warning alert at >85%
- Kubernetes removes from load balancer

**Remediation**:
1. Increase disk space (cloud)
2. Archive old logs
3. Clean up temporary files
4. Monitor for runaway processes

### Scenario 5: Memory >85%

**Detection**:
- Memory usage exceeds 85% threshold
- OOM killer may start evicting processes
- GC frequency increases

**Readiness Impact**:
- Warning alert at >85%
- Critical alert at >95%
- Pod may be evicted by Kubernetes

**Remediation**:
1. Increase memory allocation
2. Check for memory leaks
3. Optimize cache/buffer sizes
4. Scale horizontally

---

## 📈 SLA Targets

| Metric | Target | Threshold |
|--------|--------|-----------|
| **Liveness Probe Success Rate** | 99.9% | Failures >0.1% = page |
| **Readiness Probe Success Rate** | 99.8% | Failures >0.2% = warning |
| **Detailed Health Success Rate** | 99.5% | Failures >0.5% = info |
| **Liveness Response Time** | <200ms | p95 >500ms = warning |
| **Readiness Response Time** | <500ms | p95 >1s = warning |
| **Detailed Health Response Time** | <1s | p95 >2s = warning |
| **Database Check Success** | 99.9% | Failures = critical alert |
| **Cache Check Success** | 99.8% | Failures = warning alert |
| **Queue Check Success** | 99.5% | Failures = warning alert |
| **Disk Space Available** | >10GB | <5GB = critical alert |
| **Memory Available** | >50% | <15% = critical alert |

---

## 🧪 Testing Procedures

### Load Test: Health Check Endpoints

```bash
# Generate 1000 req/s for 5 minutes
ab -n 300000 -c 1000 http://localhost:8080/health/live
ab -n 100000 -c 500 http://localhost:8080/health/ready
ab -n 50000 -c 100 http://localhost:8080/health/detailed
```

**Expected Results**:
- P99 latency <200ms (live), <500ms (ready), <1s (detailed)
- 0% errors
- No timeouts

## Failover Test: Dependency Degradation

```bash
# 1. Kill database connection
docker pause postgres-container
# Expected: readiness returns 503 within 5 seconds
# Dashboard shows database as red
# Auto-scaling may trigger

# 2. Recover database
docker unpause postgres-container
# Expected: readiness returns 200 within 30 seconds
# Traffic resumed

# 3. Kill cache
docker pause redis-container
# Expected: readiness may still return 200 (degrades, not fails)
# Dashboard shows cache as red
# Response latency increases

# 4. Simulate high database latency
tc qdisc add dev eth0 root netem delay 10000ms
# Expected: readiness latency increases
# Warning alert triggers

# 5. Remove latency
tc qdisc del dev eth0 root
# Expected: readiness latency returns to normal
```

## Chaos Testing: Failure Injection

```python
# Inject temporary failures for 1 minute, then recover
@app.before_request
def inject_failure():
    if request.endpoint == 'health_ready':
        if random.random() < 0.1:  # 10% failure rate
            return {"status": "failed"}, 503

# Monitor alert triggers and auto-recovery
```

---

## 🚀 Deployment Checklist

- [ ] All services have `/health/live` endpoint
- [ ] All services have `/health/ready` endpoint
- [ ] All services have `/health/detailed` endpoint
- [ ] Health endpoints tested independently
- [ ] Health endpoints tested under load (1000 req/s)
- [ ] Kubernetes liveness probes configured
- [ ] Kubernetes readiness probes configured
- [ ] Health check SLAs documented
- [ ] Failure scenarios tested
- [ ] Failover recovery tested
- [ ] Dashboard panels configured
- [ ] Alerts configured for health check failures
- [ ] Runbooks prepared
- [ ] On-call team trained

---

**Last Updated**: 2026-06-14 | **Next Review**: 2026-07-14 | **Owned by**: Platform Engineering
