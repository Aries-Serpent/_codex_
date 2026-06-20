# Health Check Expected Responses Reference

This document provides reference examples of expected health check responses.

## GET /health Endpoint Responses

### Healthy Response (200 OK)

```json
{
  "service": "mcp-facade",
  "status": "ok",
  "adapter": "zendesk_adapter",
  "adapter_status": {
    "status": "ok"
  }
}
```

**Interpretation:** Service is fully operational, adapter is connected and responsive.

### Degraded Response (200 OK)

```json
{
  "service": "mcp-facade",
  "status": "degraded",
  "adapter": "zendesk_adapter",
  "adapter_status": {
    "status": "degraded",
    "reason": "High latency detected"
  }
}
```

**Interpretation:** Service is operational but experiencing issues. Investigate before deployment.

### Unhealthy Response (503 Service Unavailable)

```json
{
  "service": "mcp-facade",
  "status": "unhealthy",
  "adapter": "zendesk_adapter",
  "adapter_status": {
    "status": "disconnected",
    "error": "Connection refused"
  }
}
```

**Interpretation:** Service is not operational. Halt deployment and investigate.

## GET /mcp/v1/health Endpoint Responses

### Healthy Response (200 OK)

```json
{
  "status": "ok",
  "adapter": "zendesk_adapter",
  "adapter_status": {
    "status": "ok",
    "connected": true,
    "latency_ms": 45,
    "last_check": "2026-06-20T09:25:08Z"
  }
}
```

**Interpretation:** MCP service is fully operational with good response times.

### Response With Adapter Metrics

```json
{
  "status": "ok",
  "adapter": "zendesk_adapter",
  "adapter_status": {
    "status": "ok",
    "connected": true,
    "latency_ms": 125,
    "requests_total": 5234,
    "requests_error": 12,
    "error_rate": 0.23,
    "uptime_seconds": 86400
  }
}
```

**Interpretation:** Service operational with detailed metrics available.

### Degraded With Latency Warning

```json
{
  "status": "degraded",
  "adapter": "zendesk_adapter",
  "adapter_status": {
    "status": "ok",
    "connected": true,
    "latency_ms": 1250,
    "warning": "Response time exceeds SLA (500ms)"
  }
}
```

**Interpretation:** Service operational but performance degraded. Investigate cause.

### Failed Connection

```json
{
  "status": "unhealthy",
  "adapter": "zendesk_adapter",
  "adapter_status": {
    "status": "disconnected",
    "connected": false,
    "error": "Connection timeout after 30s",
    "last_successful_check": "2026-06-20T09:15:00Z"
  }
}
```

**Interpretation:** Adapter connection lost. Restart services and verify configuration.

## Response Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | OK - Service responding | ✅ OK to proceed (check status field) |
| 400 | Bad Request - Invalid parameters | ❌ Fix request, retry |
| 401 | Unauthorized - Authentication failed | ❌ Verify credentials |
| 403 | Forbidden - Access denied | ❌ Verify permissions |
| 404 | Not Found - Endpoint doesn't exist | ❌ Verify endpoint path |
| 500 | Internal Server Error | ❌ Critical - Check logs |
| 502 | Bad Gateway | ❌ Check backend connectivity |
| 503 | Service Unavailable | ❌ Service down - Check status |
| Timeout | Request timeout (>30s) | ❌ Service hung or overloaded |

## Adapter Status Values

### Zendesk Adapter

**Healthy Status:**
```json
{
  "status": "ok",
  "adapter_name": "zendesk_adapter",
  "api_version": "v2",
  "connected": true,
  "organization": "example.zendesk.com",
  "auth_method": "oauth2",
  "latency_ms": 50
}
```

**Degraded Status:**
```json
{
  "status": "degraded",
  "adapter_name": "zendesk_adapter",
  "connected": true,
  "latency_ms": 800,
  "warning": "API rate limit approaching",
  "requests_remaining": 150
}
```

**Disconnected Status:**
```json
{
  "status": "disconnected",
  "adapter_name": "zendesk_adapter",
  "connected": false,
  "error": "Authentication token expired",
  "last_error_time": "2026-06-20T09:25:00Z"
}
```

### Mock Adapter

**Healthy Status (for testing):**
```json
{
  "status": "ok",
  "adapter_name": "mock_adapter",
  "simulated": true,
  "latency_ms": 10
}
```

## Performance Metrics in Responses

When detailed metrics are available, expect:

```json
{
  "status": "ok",
  "metrics": {
    "requests_total": 5234,
    "requests_success": 5222,
    "requests_error": 12,
    "success_rate": 99.77,
    "error_rate": 0.23,
    "avg_latency_ms": 125,
    "p50_latency_ms": 95,
    "p95_latency_ms": 245,
    "p99_latency_ms": 450,
    "uptime_seconds": 86400
  }
}
```

**Field Descriptions:**
- `requests_total`: Total requests processed since startup
- `requests_success`: Successful requests
- `requests_error`: Failed requests
- `success_rate`: Percentage of successful requests
- `error_rate`: Percentage of failed requests
- `avg_latency_ms`: Average response time in milliseconds
- `p50_latency_ms`: 50th percentile latency (median)
- `p95_latency_ms`: 95th percentile latency
- `p99_latency_ms`: 99th percentile latency
- `uptime_seconds`: Seconds since service started

## Timestamp Formats

Health check responses use ISO 8601 timestamp format:

```
2026-06-20T09:25:08Z       (UTC timezone)
2026-06-20T09:25:08+00:00  (Alternative ISO format)
```

## Response Size

**Expected Response Size:**
- Basic health check: 200-300 bytes
- Detailed health check: 500-1000 bytes
- With metrics: 1000-2000 bytes

**Maximum acceptable size:** 5000 bytes

## Response Time Expectations

**By Endpoint:**

| Endpoint | Healthy | Degraded | Timeout |
|----------|---------|----------|---------|
| /health | < 100ms | 100-500ms | > 500ms |
| /mcp/v1/health | < 200ms | 200-500ms | > 500ms |

## Common Response Patterns

### Pattern 1: All Systems OK

```json
{
  "service": "ok",
  "database": "ok",
  "cache": "ok",
  "adapter": "ok",
  "overall": "healthy"
}
```

### Pattern 2: Cascade Failure

```json
{
  "service": "ok",
  "database": "unhealthy",  ← Database down
  "cache": "ok",
  "adapter": "degraded",    ← Adapter affected by DB failure
  "overall": "unhealthy"
}
```

### Pattern 3: Graceful Degradation

```json
{
  "service": "ok",
  "database": "ok",
  "cache": "disabled",      ← Cache offline
  "adapter": "ok",
  "fallback": "enabled",    ← Using fallback mechanism
  "overall": "degraded"
}
```

## Testing Response Validation

When testing health endpoints, validate:

1. **Structure**: Response is valid JSON
2. **Required Fields**: Contains `status` or `error` field
3. **Status Code**: Matches documented behavior
4. **Response Time**: Within SLA
5. **Timestamp**: Present and valid ISO 8601 format

### Test Script Example

```bash
#!/bin/bash

# Test health endpoint
response=$(curl -s -w "\n%{http_code}" http://localhost:8000/health)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

# Validate
if [ "$http_code" = "200" ]; then
    echo "✅ HTTP 200 OK"
else
    echo "❌ HTTP $http_code"
    exit 1
fi

# Check required fields
if echo "$body" | jq -e '.status' > /dev/null; then
    status=$(echo "$body" | jq -r '.status')
    echo "✅ Status: $status"
else
    echo "❌ Missing status field"
    exit 1
fi

# Validate status value
if [ "$status" = "ok" ] || [ "$status" = "degraded" ]; then
    echo "✅ Valid status value"
else
    echo "❌ Invalid status value: $status"
    exit 1
fi
```

## Related Documentation

- [HEALTH_CHECK_PROCEDURES.md](./HEALTH_CHECK_PROCEDURES.md)
- [SUCCESS_CRITERIA_BY_ENVIRONMENT.md](./SUCCESS_CRITERIA_BY_ENVIRONMENT.md)
- [CRITICAL_PATHS_FOR_VERIFICATION.md](./CRITICAL_PATHS_FOR_VERIFICATION.md)
