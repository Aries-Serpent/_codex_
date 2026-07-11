# API Reference - Phase 15-16
**Last Updated:** 2026-07-11
**Version:** v0.2.1

> Complete reference for all 11 FastAPI endpoints in the Phase 15-16 system.

**Version**: 0.1.0 | **Last Updated**: 2026-07-11

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication & Rate Limiting](#authentication--rate-limiting)
3. [Decision API](#decision-api)
4. [Memory API](#memory-api)
5. [Workflow API](#workflow-api)
6. [Error Handling](#error-handling)
7. [Code Examples](#code-examples)

---

## Getting Started

### Base URL

```
Development:  http://localhost:8000
Production:   https://api.codex-ml.io
```

### Required Headers

```http
Authorization: ******
Content-Type: application/json
```

### Response Format

All responses follow JSON:API standard:

```json
{
  "data": { /* response payload */ },
  "meta": {
    "timestamp": "2026-07-11T04:00:00Z",
    "request_id": "req_abc123"
  }
}
```

---

## Authentication & Rate Limiting

### Authentication Methods

1. **API Key** (Recommended for production)
   ```http
   Authorization: ******
   ```

2. **Session Token** (For CLI/SDK)
   ```http
   Authorization: ******
   Cookie: session_id=sess_abc123
   ```

### Rate Limiting

**Limits**: 1,000 requests per minute per API key

**Headers**:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1657500000
```

**Exceeded Limit Response**:
```http
HTTP/429 Too Many Requests

{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "API rate limit exceeded",
    "retry_after_seconds": 60
  }
}
```

---

## Decision API

Records and retrieves autonomous decisions with full audit trail.

### 1. POST /api/decisions/submit

Submit a new autonomous decision.

**Request**:
```http
POST /api/decisions/submit HTTP/1.1
Authorization: ******
Content-Type: application/json

{
  "lane_name": "security",
  "decision_type": "vulnerability_remediation",
  "rationale": "CVE-2026-12345 detected in dependency X",
  "impact": "Upgrading dependency X from v1.0 to v1.2 (security patch)",
  "phase": "15-16",
  "confidence": 0.95,
  "metadata": {
    "cve_id": "CVE-2026-12345",
    "severity": "HIGH",
    "affected_module": "authentication"
  }
}
```

**Response** (201 Created):
```json
{
  "data": {
    "id": "dec_8901a2b3c4d5e6f7",
    "lane_name": "security",
    "decision_type": "vulnerability_remediation",
    "timestamp": "2026-07-11T04:00:00Z",
    "status": "recorded"
  },
  "meta": {
    "timestamp": "2026-07-11T04:00:00Z",
    "request_id": "req_xyz789"
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid lane_name or missing required fields
- `409 Conflict`: Duplicate decision detected (same lane + type + rationale)
- `429 Too Many Requests`: Rate limit exceeded

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/decisions/submit \
  -H "Authorization: ******" \
  -H "Content-Type: application/json" \
  -d '{
    "lane_name": "security",
    "decision_type": "vulnerability_remediation",
    "rationale": "CVE-2026-12345 detected",
    "impact": "Upgrading dependency",
    "phase": "15-16",
    "confidence": 0.95
  }'
```

### 2. GET /api/decisions/{decision_id}

Retrieve a specific decision by ID.

**Request**:
```http
GET /api/decisions/dec_8901a2b3c4d5e6f7 HTTP/1.1
Authorization: ******
```

**Response** (200 OK):
```json
{
  "data": {
    "id": "dec_8901a2b3c4d5e6f7",
    "lane_name": "security",
    "decision_type": "vulnerability_remediation",
    "rationale": "CVE-2026-12345 detected",
    "impact": "Upgrading dependency X from v1.0 to v1.2",
    "timestamp": "2026-07-11T04:00:00Z",
    "phase": "15-16",
    "confidence": 0.95,
    "metadata": {
      "cve_id": "CVE-2026-12345"
    }
  },
  "meta": {
    "timestamp": "2026-07-11T04:00:00Z"
  }
}
```

**Error Responses**:
- `404 Not Found`: Decision ID doesn't exist

**cURL Example**:
```bash
curl http://localhost:8000/api/decisions/dec_8901a2b3c4d5e6f7 \
  -H "Authorization: ******"
```

**Python Example**:
```python
import requests

api_key = "YOUR_API_KEY"
headers = {"Authorization": f"******"}

response = requests.get(
    "http://localhost:8000/api/decisions/dec_8901a2b3c4d5e6f7",
    headers=headers
)
decision = response.json()["data"]
print(f"Decision: {decision['rationale']}")
print(f"Confidence: {decision['confidence']}")
```

### 3. GET /api/decisions/recent

Retrieve recent decisions with optional filtering.

**Request Parameters**:
| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| limit | int | 10 | 100 | Number of decisions to return |
| offset | int | 0 | - | Pagination offset |
| lane_name | string | - | - | Filter by lane (e.g., "security") |

**Request**:
```http
GET /api/decisions/recent?limit=20&lane_name=security HTTP/1.1
Authorization: ******
```

**Response** (200 OK):
```json
{
  "data": {
    "decisions": [
      {
        "id": "dec_newest",
        "lane_name": "security",
        "decision_type": "vulnerability_remediation",
        "rationale": "...",
        "timestamp": "2026-07-11T04:10:00Z",
        "confidence": 0.95
      },
      {
        "id": "dec_older",
        "lane_name": "security",
        "decision_type": "optimization",
        "rationale": "...",
        "timestamp": "2026-07-11T03:50:00Z",
        "confidence": 0.87
      }
    ],
    "pagination": {
      "total": 42,
      "limit": 20,
      "offset": 0,
      "next_offset": 20
    }
  },
  "meta": {
    "timestamp": "2026-07-11T04:00:00Z"
  }
}
```

**cURL Example**:
```bash
curl "http://localhost:8000/api/decisions/recent?limit=20&lane_name=security" \
  -H "Authorization: ******"
```

### 4. GET /api/decisions/history

Retrieve decision history with advanced filtering.

**Request Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | int | 1 | Page number |
| page_size | int | 20 | Items per page (max: 100) |
| lane_name | string | - | Filter by lane |
| decision_type | string | - | Filter by type |
| start_date | datetime | - | Filter decisions after date |
| end_date | datetime | - | Filter decisions before date |

**Request**:
```http
GET /api/decisions/history?page=1&page_size=20&lane_name=stability HTTP/1.1
Authorization: ******
```

**Response** (200 OK):
```json
{
  "data": {
    "decisions": [ /* array of decision objects */ ],
    "pagination": {
      "current_page": 1,
      "page_size": 20,
      "total_items": 156,
      "total_pages": 8,
      "has_next": true,
      "has_prev": false
    }
  },
  "meta": {
    "timestamp": "2026-07-11T04:00:00Z"
  }
}
```

**Python Example**:
```python
import requests
from datetime import datetime, timedelta

headers = {"Authorization": f"******"}

# Get security decisions from last 7 days
start_date = (datetime.utcnow() - timedelta(days=7)).isoformat()
params = {
    "lane_name": "security",
    "start_date": start_date,
    "page_size": 50
}

response = requests.get(
    "http://localhost:8000/api/decisions/history",
    headers=headers,
    params=params
)
history = response.json()["data"]["decisions"]
```

---

## Memory API

Manage short-term and long-term memory for pattern storage and retrieval.

### 5. POST /api/memory/store

Store a pattern or learning in long-term memory.

**Request**:
```http
POST /api/memory/store HTTP/1.1
Authorization: ******
Content-Type: application/json

{
  "lane_name": "ci",
  "pattern_type": "flaky_test",
  "content": {
    "test_name": "test_concurrent_access",
    "flakiness_rate": 0.15,
    "root_cause": "Race condition in mutex",
    "fix": "Add proper synchronization primitive",
    "affected_files": ["src/concurrent/lock.py"]
  },
  "confidence": 0.88,
  "tags": ["concurrency", "mutex", "test-reliability"]
}
```

**Response** (201 Created):
```json
{
  "data": {
    "id": "mem_pattern_001",
    "lane_name": "ci",
    "pattern_type": "flaky_test",
    "created_at": "2026-07-11T04:00:00Z",
    "expires_at": null
  },
  "meta": {
    "timestamp": "2026-07-11T04:00:00Z"
  }
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/memory/store \
  -H "Authorization: ******" \
  -H "Content-Type: application/json" \
  -d '{
    "lane_name": "ci",
    "pattern_type": "flaky_test",
    "content": {
      "test_name": "test_concurrent_access",
      "root_cause": "Race condition"
    },
    "confidence": 0.88
  }'
```

### 6. GET /api/memory/retrieve

Retrieve patterns from long-term memory.

**Request Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| lane_name | string | - | Filter by lane |
| pattern_type | string | - | Filter by pattern type |
| tag | string | - | Filter by tag |
| limit | int | 10 | Max patterns to return |
| min_confidence | float | 0.5 | Minimum confidence score |

**Request**:
```http
GET /api/memory/retrieve?lane_name=security&pattern_type=auth_bypass&limit=5 HTTP/1.1
Authorization: ******
```

**Response** (200 OK):
```json
{
  "data": {
    "patterns": [
      {
        "id": "mem_sec_001",
        "lane_name": "security",
        "pattern_type": "auth_bypass",
        "content": {
          "vulnerability": "JWT signature not validated",
          "fix": "Verify algorithm matches expected value"
        },
        "confidence": 0.92,
        "usage_count": 23,
        "last_used": "2026-07-10T18:30:00Z",
        "created_at": "2026-07-01T10:00:00Z"
      }
    ],
    "total": 1
  },
  "meta": {
    "timestamp": "2026-07-11T04:00:00Z"
  }
}
```

**Python Example**:
```python
# Retrieve security patterns
response = requests.get(
    "http://localhost:8000/api/memory/retrieve",
    headers=headers,
    params={
        "lane_name": "security",
        "pattern_type": "auth_bypass",
        "limit": 10
    }
)

patterns = response.json()["data"]["patterns"]
for pattern in patterns:
    print(f"Pattern: {pattern['content']}")
    print(f"Confidence: {pattern['confidence']}")
```

### 7. POST /api/memory/stm-push

Push data to short-term memory (session cache).

**Request**:
```http
POST /api/memory/stm-push HTTP/1.1
Authorization: ******
Content-Type: application/json

{
  "key": "current_phase_state",
  "value": {
    "phase": 15,
    "lane": "security",
    "decisions_count": 12
  },
  "ttl_seconds": 1800
}
```

**Response** (201 Created):
```json
{
  "data": {
    "key": "current_phase_state",
    "stored_at": "2026-07-11T04:00:00Z",
    "ttl_seconds": 1800
  },
  "meta": {
    "timestamp": "2026-07-11T04:00:00Z"
  }
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/memory/stm-push \
  -H "Authorization: ******" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "session_phase",
    "value": {"phase": 15},
    "ttl_seconds": 3600
  }'
```

### 8. GET /api/memory/stats

Get memory system statistics.

**Request**:
```http
GET /api/memory/stats HTTP/1.1
Authorization: ******
```

**Response** (200 OK):
```json
{
  "data": {
    "stm": {
      "total_entries": 156,
      "memory_bytes": 245000,
      "avg_ttl_seconds": 2100,
      "expired_entries": 34
    },
    "ltm": {
      "total_patterns": 287,
      "memory_bytes": 3200000,
      "by_type": {
        "ci_failure": 45,
        "flaky_test": 67,
        "security": 89,
        "performance": 51,
        "documentation": 35
      }
    },
    "top_patterns": [
      {
        "type": "security",
        "pattern_name": "sql_injection",
        "count": 23,
        "avg_confidence": 0.91,
        "last_used": "2026-07-11T03:50:00Z"
      }
    ],
    "cache_efficiency": {
      "hit_rate": 0.87,
      "miss_rate": 0.13,
      "avg_lookup_ms": 2.3
    }
  },
  "meta": {
    "timestamp": "2026-07-11T04:00:00Z"
  }
}
```

**Python Example**:
```python
response = requests.get(
    "http://localhost:8000/api/memory/stats",
    headers=headers
)
stats = response.json()["data"]
print(f"Total LTM Patterns: {stats['ltm']['total_patterns']}")
print(f"Cache Hit Rate: {stats['cache_efficiency']['hit_rate']:.1%}")
```

---

## Workflow API

Manage workflow execution status and gating.

### 9. GET /api/workflows/status

Get current workflow execution status.

**Request Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| phase | string | Filter by phase |
| lane | string | Filter by lane |

**Request**:
```http
GET /api/workflows/status?phase=15 HTTP/1.1
Authorization: ******
```

**Response** (200 OK):
```json
{
  "data": {
    "workflows": [
      {
        "id": "wf_001",
        "name": "code-quality-suite",
        "status": "running",
        "phase": "15-16",
        "lane": "quality",
        "progress_percent": 75,
        "started_at": "2026-07-11T03:30:00Z",
        "estimated_completion": "2026-07-11T04:15:00Z"
      },
      {
        "id": "wf_002",
        "name": "security-scanning",
        "status": "passed",
        "phase": "15-16",
        "lane": "security",
        "progress_percent": 100,
        "completed_at": "2026-07-11T04:00:00Z"
      }
    ]
  },
  "meta": {
    "timestamp": "2026-07-11T04:00:00Z"
  }
}
```

**cURL Example**:
```bash
curl "http://localhost:8000/api/workflows/status?phase=15-16" \
  -H "Authorization: ******"
```

### 10. POST /api/workflows/gate-check

Check if workflow passes all required gates.

**Request**:
```http
POST /api/workflows/gate-check HTTP/1.1
Authorization: ******
Content-Type: application/json

{
  "workflow_name": "documentation-refresh",
  "phase": 15,
  "checks_required": ["link_validation", "markdown_lint", "spell_check"],
  "lane_name": "documentation"
}
```

**Response** (200 OK):
```json
{
  "data": {
    "workflow_name": "documentation-refresh",
    "gate_passed": true,
    "checks": [
      {
        "name": "link_validation",
        "status": "passed",
        "message": "0 broken links found",
        "duration_seconds": 12.5
      },
      {
        "name": "markdown_lint",
        "status": "passed",
        "message": "All files pass linting rules",
        "duration_seconds": 5.2
      },
      {
        "name": "spell_check",
        "status": "passed",
        "message": "No spelling errors detected",
        "duration_seconds": 8.1
      }
    ],
    "overall_duration_seconds": 26.8
  },
  "meta": {
    "timestamp": "2026-07-11T04:00:00Z"
  }
}
```

**Failed Gate Example** (200 OK but gate_passed=false):
```json
{
  "data": {
    "workflow_name": "documentation-refresh",
    "gate_passed": false,
    "checks": [
      {
        "name": "link_validation",
        "status": "failed",
        "message": "46 broken links found:\n - docs/guides/GETTING_STARTED_API_CONSUMER.md: ../api/API_REFERENCE.md\n - ...",
        "duration_seconds": 15.2
      }
    ]
  }
}
```

**Python Example**:
```python
# Check if documentation workflow passes all gates
response = requests.post(
    "http://localhost:8000/api/workflows/gate-check",
    headers=headers,
    json={
        "workflow_name": "documentation-refresh",
        "phase": 15,
        "checks_required": ["link_validation", "markdown_lint"],
        "lane_name": "documentation"
    }
)

result = response.json()["data"]
if result["gate_passed"]:
    print(" All gates passed!")
else:
    for check in result["checks"]:
        if check["status"] != "passed":
            print(f" {check['name']}: {check['message']}")
```

### 11. GET /api/workflows/rate-limit

Get rate limit status for current API key.

**Request**:
```http
GET /api/workflows/rate-limit HTTP/1.1
Authorization: ******
```

**Response** (200 OK - Normal):
```json
{
  "data": {
    "requests_current": 523,
    "requests_max": 1000,
    "window_seconds": 60,
    "reset_time": "2026-07-11T04:10:00Z",
    "throttled": false,
    "remaining_requests": 477,
    "requests_percent_used": 52.3
  },
  "meta": {
    "timestamp": "2026-07-11T04:00:00Z"
  }
}
```

**Response** (200 OK - Throttled):
```json
{
  "data": {
    "requests_current": 1000,
    "requests_max": 1000,
    "window_seconds": 60,
    "reset_time": "2026-07-11T04:10:00Z",
    "throttled": true,
    "remaining_requests": 0,
    "requests_percent_used": 100,
    "retry_after_seconds": 45
  },
  "meta": {
    "timestamp": "2026-07-11T04:00:00Z"
  }
}
```

**cURL Example**:
```bash
curl http://localhost:8000/api/workflows/rate-limit \
  -H "Authorization: ******"
```

---

## Error Handling

### Standard Error Response

All errors follow this format:

```json
{
  "error": {
    "code": "error_code",
    "message": "Human-readable message",
    "details": {
      "field": "error details"
    }
  },
  "meta": {
    "timestamp": "2026-07-11T04:00:00Z",
    "request_id": "req_abc123"
  }
}
```

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | GET request returned data |
| 201 | Created | POST request created resource |
| 400 | Bad Request | Invalid request body |
| 401 | Unauthorized | Missing/invalid API key |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate resource |
| 422 | Unprocessable | Invalid field values |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Internal error |

### Common Error Codes

| Code | Description |
|------|-------------|
| `invalid_request` | Malformed request |
| `auth_required` | No authorization header |
| `auth_invalid` | Invalid API key |
| `resource_not_found` | Resource doesn't exist |
| `rate_limit_exceeded` | Too many requests |
| `validation_error` | Input validation failed |
| `duplicate_resource` | Resource already exists |
| `internal_error` | Server error |

---

## Code Examples

### Python SDK

```python
"""Phase 15-16 API - Python SDK Examples"""

import requests
from datetime import datetime, timedelta

class CodexClient:
    def __init__(self, base_url="http://localhost:8000", api_key=""):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"******",
            "Content-Type": "application/json"
        }
    
    def submit_decision(self, lane_name, decision_type, rationale, impact, confidence):
        """Record a new decision."""
        payload = {
            "lane_name": lane_name,
            "decision_type": decision_type,
            "rationale": rationale,
            "impact": impact,
            "phase": "15-16",
            "confidence": confidence
        }
        response = requests.post(
            f"{self.base_url}/api/decisions/submit",
            headers=self.headers,
            json=payload
        )
        return response.json()["data"]
    
    def get_decision(self, decision_id):
        """Get decision details."""
        response = requests.get(
            f"{self.base_url}/api/decisions/{decision_id}",
            headers=self.headers
        )
        return response.json()["data"]
    
    def store_pattern(self, lane_name, pattern_type, content, confidence, tags):
        """Store a pattern in memory."""
        payload = {
            "lane_name": lane_name,
            "pattern_type": pattern_type,
            "content": content,
            "confidence": confidence,
            "tags": tags
        }
        response = requests.post(
            f"{self.base_url}/api/memory/store",
            headers=self.headers,
            json=payload
        )
        return response.json()["data"]
    
    def get_patterns(self, lane_name, pattern_type=None, limit=10):
        """Retrieve patterns from memory."""
        params = {
            "lane_name": lane_name,
            "limit": limit
        }
        if pattern_type:
            params["pattern_type"] = pattern_type
        
        response = requests.get(
            f"{self.base_url}/api/memory/retrieve",
            headers=self.headers,
            params=params
        )
        return response.json()["data"]["patterns"]

# Usage
client = CodexClient(api_key="your_api_key")

# Record a decision
decision = client.submit_decision(
    lane_name="security",
    decision_type="vulnerability_fix",
    rationale="CVE-2026-12345 found in dependency",
    impact="Upgrade library X",
    confidence=0.95
)
print(f"Decision recorded: {decision['id']}")

# Store a pattern
pattern = client.store_pattern(
    lane_name="ci",
    pattern_type="flaky_test",
    content={"test": "test_race_condition", "fix": "Add mutex"},
    confidence=0.88,
    tags=["concurrency"]
)
print(f"Pattern stored: {pattern['id']}")

# Retrieve patterns
patterns = client.get_patterns(lane_name="security")
for p in patterns:
    print(f"Found pattern: {p['pattern_type']}")
```

### JavaScript/Node.js

```javascript
/**Phase 15-16 API - JavaScript Examples*/

class CodexClient {
  constructor(baseUrl = "http://localhost:8000", apiKey = "") {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  async submitDecision(laneN, decisionType, rationale, impact, confidence) {
    const response = await fetch(
      `${this.baseUrl}/api/decisions/submit`,
      {
        method: "POST",
        headers: {
          "Authorization": `******
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          lane_name: laneName,
          decision_type: decisionType,
          rationale,
          impact,
          phase: "15-16",
          confidence
        })
      }
    );
    return (await response.json()).data;
  }

  async getPatterns(laneName, patternType = null) {
    const params = new URLSearchParams({ lane_name: laneName });
    if (patternType) params.append("pattern_type", patternType);
    
    const response = await fetch(
      `${this.baseUrl}/api/memory/retrieve?${params}`,
      {
        headers: {
          "Authorization": `******
        }
      }
    );
    return (await response.json()).data.patterns;
  }
}

// Usage
const client = new CodexClient(
  "http://localhost:8000",
  "your_api_key"
);

(async () => {
  const decision = await client.submitDecision(
    "security",
    "vulnerability_fix",
    "CVE-2026-12345 found",
    "Upgrade library",
    0.95
  );
  console.log(`Decision: ${decision.id}`);

  const patterns = await client.getPatterns("security");
  patterns.forEach(p => console.log(`Pattern: ${p.pattern_type}`));
})();
```

### cURL Cheat Sheet

```bash
# Set variables
API_KEY="your_api_key"
BASE_URL="http://localhost:8000"

# Submit decision
curl -X POST $BASE_URL/api/decisions/submit \
  -H "Authorization: ******" \
  -H "Content-Type: application/json" \
  -d '{
    "lane_name": "security",
    "decision_type": "optimization",
    "rationale": "Reduce noise",
    "impact": "20% less alerts",
    "confidence": 0.9
  }'

# Get recent decisions
curl "$BASE_URL/api/decisions/recent?limit=10" \
  -H "Authorization: ******"

# Retrieve security patterns
curl "$BASE_URL/api/memory/retrieve?lane_name=security&limit=5" \
  -H "Authorization: ******"

# Check workflow gates
curl -X POST $BASE_URL/api/workflows/gate-check \
  -H "Authorization: ******" \
  -d '{
    "workflow_name": "ci-suite",
    "phase": 15,
    "checks_required": ["tests", "lint"],
    "lane_name": "quality"
  }'

# Check rate limit
curl "$BASE_URL/api/workflows/rate-limit" \
  -H "Authorization: ******"
```

---

**Related Documentation**:
- [Architecture Overview](./ARCHITECTURE_PHASE_15_16.md)
- [Pattern Library Guide](./PATTERN_LIBRARY_GUIDE.md)
- [Error Handling Guide](../guides/ERROR_HANDLING.md)

