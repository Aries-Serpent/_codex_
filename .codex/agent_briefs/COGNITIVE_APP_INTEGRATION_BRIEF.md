# COGNITIVE APP INTEGRATION BRIEF — API REFERENCE & USAGE GUIDE

**Version:** 2.0.0  
**Created:** 2026-07-11T02:11:00Z  
**Status:** READY FOR ALL AGENTS  
**Scope:** All custom agents (security, coverage, stability, complexity, docs)  
**Campaign:** Cognitive App Enhancement — Phase 15  

---

## 1. OVERVIEW

This brief provides a **unified API reference and integration guide** for all agents using the enhanced Cognitive App backend. It defines:

- **11 REST endpoints** with schemas and error codes
- **Decision visualization workflow** (submit → visualize → feedback)
- **Memory system integration** (store patterns, retrieve prior decisions)
- **Rate limiting and quota budgeting** strategies
- **Security & authentication** (token handling, HMAC validation)
- **Observability & debugging** (OTel tracing, structured logging)

**All agents MUST follow this guide** for consistent integration with Cognitive App.

---

## 2. COGNITIVE APP ENDPOINT REFERENCE

### 2.1 Decision Visualization APIs

#### POST /api/decisions/submit
**Submit a decision candidate with confidence scoring**

```bash
curl -X POST http://localhost:8765/api/decisions/submit \
  -H "Content-Type: application/json" \
  -H "Authorization: ******" \
  -d '{
    "lane": "security",
    "candidate": "Fix CVE-2026-XXXXX in src/auth/token_handler.py",
    "confidence_score": 0.92,
    "k1_factor": 0.28,
    "coherence_metric": 0.87,
    "superposition_state": ["APPROVED", "NEEDS_REVIEW"]
  }'
```

**Response (200 OK):**
```json
{
  "decision_id": "dec_8f3c9d1e",
  "lane": "security",
  "candidate": "Fix CVE-2026-XXXXX...",
  "confidence_score": 0.92,
  "k1_factor": 0.28,
  "coherence_metric": 0.87,
  "superposition_state": ["APPROVED", "NEEDS_REVIEW"],
  "timestamp": "2026-07-12T16:30:00Z",
  "status": "submitted"
}
```

**Error Codes:**
- **400 Bad Request:** Invalid candidate schema
- **401 Unauthorized:** Missing/invalid token
- **429 Too Many Requests:** Rate limited

**Schema Requirements:**
- `lane`: One of [security, coverage, stability, complexity, docs]
- `candidate`: String, 10-500 chars, describes the decision
- `confidence_score`: Float, 0.0-1.0
- `k1_factor`: Float, 0.0-1.0 (decision quality metric; lower is better)
- `coherence_metric`: Float, 0.0-1.0 (superposition state coherence)
- `superposition_state`: Array of strings, represents parallel execution paths

#### GET /api/decisions/{decision_id}
**Retrieve a specific decision and its current state**

```bash
curl http://localhost:8765/api/decisions/dec_8f3c9d1e \
  -H "Authorization: ******"
```

**Response (200 OK):**
```json
{
  "decision_id": "dec_8f3c9d1e",
  "lane": "security",
  "candidate": "Fix CVE-2026-XXXXX...",
  "confidence_score": 0.92,
  "k1_factor": 0.28,
  "coherence_metric": 0.87,
  "superposition_state": ["APPROVED", "NEEDS_REVIEW"],
  "timestamp": "2026-07-12T16:30:00Z",
  "status": "approved",
  "feedback": "Approved by orchestrator. Ready for execution."
}
```

**Error Codes:**
- **404 Not Found:** Decision ID doesn't exist
- **401 Unauthorized:** Missing/invalid token

#### GET /api/decisions/recent
**List recent decisions with optional filtering**

```bash
# Get 10 most recent security lane decisions
curl 'http://localhost:8765/api/decisions/recent?lane=security&limit=10' \
  -H "Authorization: ******"

# Get decisions from last hour with status=submitted
curl 'http://localhost:8765/api/decisions/recent?lane=coverage&status=submitted&since=1h' \
  -H "Authorization: ******"
```

**Response (200 OK):**
```json
{
  "decisions": [
    {
      "decision_id": "dec_8f3c9d1e",
      "lane": "security",
      "candidate": "Fix CVE-2026-XXXXX...",
      "confidence_score": 0.92,
      "status": "submitted",
      "timestamp": "2026-07-12T16:30:00Z"
    },
    { "..." }
  ],
  "count": 10,
  "has_more": true
}
```

**Query Parameters:**
- `lane` (optional): Filter by lane name
- `limit` (optional, default: 10): Max results to return
- `status` (optional): Filter by status [submitted, approved, rejected]
- `since` (optional): Return decisions from last N minutes/hours (e.g., "30m", "2h")

#### GET /api/decisions/history
**Query-able decision history with full filtering**

```bash
# Get all security lane decisions
curl 'http://localhost:8765/api/decisions/history?lane=security' \
  -H "Authorization: ******"

# Get high-confidence decisions
curl 'http://localhost:8765/api/decisions/history?lane=coverage&confidence_min=0.80' \
  -H "Authorization: ******"

# Get decisions from campaign PR #1234
curl 'http://localhost:8765/api/decisions/history?campaign_pr=1234' \
  -H "Authorization: ******"
```

**Response (200 OK):**
```json
{
  "decisions": [
    {
      "decision_id": "dec_8f3c9d1e",
      "lane": "security",
      "candidate": "...",
      "confidence_score": 0.92,
      "k1_factor": 0.28,
      "coherence_metric": 0.87,
      "status": "approved",
      "timestamp": "2026-07-12T16:30:00Z"
    }
  ],
  "count": 245,
  "aggregates": {
    "avg_confidence": 0.84,
    "avg_k1_factor": 0.31,
    "avg_coherence": 0.81,
    "success_rate": 0.92
  }
}
```

**Query Parameters:**
- `lane` (optional): Filter by lane
- `status` (optional): Filter by status
- `confidence_min` (optional): Return only decisions with confidence ≥X
- `confidence_max` (optional): Return only decisions with confidence ≤X
- `k1_max` (optional): Return only decisions with k1_factor ≤X
- `campaign_pr` (optional): Filter by campaign PR number
- `limit` (optional, default: 50): Max results
- `offset` (optional, default: 0): Pagination offset

---

### 2.2 Memory Management APIs

#### POST /api/memory/store
**Store a pattern in Long-Term Memory (LTM)**

```bash
curl -X POST http://localhost:8765/api/memory/store \
  -H "Content-Type: application/json" \
  -H "Authorization: ******" \
  -d '{
    "pattern_name": "security-patterns-v1",
    "lane": "security",
    "description": "Successfully fixed CVE-2026-XXXXX using token rotation mechanism",
    "confidence": 0.88,
    "usage_count": 1,
    "tags": ["security", "token-rotation", "cve-fix"]
  }'
```

**Response (201 Created):**
```json
{
  "pattern_id": "pat_9c2b4f5e",
  "pattern_name": "security-patterns-v1",
  "lane": "security",
  "description": "...",
  "confidence": 0.88,
  "usage_count": 1,
  "compressed_size_bytes": 245,
  "compression_ratio": 0.62,
  "stored_timestamp": "2026-07-12T16:35:00Z"
}
```

**Error Codes:**
- **400 Bad Request:** Invalid pattern schema
- **401 Unauthorized:** Missing/invalid token
- **507 Insufficient Storage:** LTM full (rare, cleanup triggered)

**Schema Requirements:**
- `pattern_name`: String, unique identifier for pattern type
- `lane`: One of [security, coverage, stability, complexity, docs]
- `description`: String, 10-1000 chars
- `confidence`: Float, 0.0-1.0
- `usage_count`: Integer ≥1
- `tags` (optional): Array of strings for categorization

#### GET /api/memory/retrieve/{pattern_name}
**Retrieve patterns from LTM by name**

```bash
# Get all security patterns
curl http://localhost:8765/api/memory/retrieve/security-patterns \
  -H "Authorization: ******"

# Get patterns with minimum confidence threshold
curl 'http://localhost:8765/api/memory/retrieve/test-generation?confidence_min=0.80' \
  -H "Authorization: ******"
```

**Response (200 OK):**
```json
{
  "pattern_name": "security-patterns",
  "patterns": [
    {
      "pattern_id": "pat_9c2b4f5e",
      "description": "Fix CVE-2026-XXXXX...",
      "confidence": 0.88,
      "usage_count": 3,
      "last_used": "2026-07-11T20:00:00Z",
      "compressed": true
    }
  ],
  "count": 5,
  "cache_hit": true,
  "cache_hit_rate": 0.33
}
```

**Query Parameters:**
- `confidence_min` (optional): Return only patterns with confidence ≥X
- `limit` (optional, default: 20): Max patterns
- `sort_by` (optional, default: usage_count): Sort by [usage_count, confidence, last_used]

#### POST /api/memory/stm/push
**Push item to Short-Term Memory (STM)**

```bash
curl -X POST http://localhost:8765/api/memory/stm/push \
  -H "Content-Type: application/json" \
  -H "Authorization: ******" \
  -d '{
    "content": "Current campaign: Phase 15. Lane security objective: Fix 8+ vulns.",
    "context": "orchestrator",
    "lifetime_seconds": 3600
  }'
```

**Response (201 Created):**
```json
{
  "stm_id": "stm_f7e2a1d3",
  "content": "Current campaign...",
  "context": "orchestrator",
  "expires_at": "2026-07-12T17:35:00Z"
}
```

#### GET /api/memory/stats
**Get memory system health metrics**

```bash
curl http://localhost:8765/api/memory/stats \
  -H "Authorization: ******"
```

**Response (200 OK):**
```json
{
  "stm": {
    "capacity": 100,
    "current_size": 34,
    "eviction_count": 5
  },
  "ltm": {
    "pattern_count": 156,
    "total_uncompressed_bytes": 89432,
    "total_compressed_bytes": 55848,
    "compression_ratio": 0.625,
    "retention_days": 90
  },
  "cache": {
    "hit_rate": 0.33,
    "hit_count": 324,
    "miss_count": 651
  }
}
```

---

### 2.3 Workflow Monitoring APIs

#### GET /api/workflows/status
**Get real-time workflow health and status**

```bash
curl http://localhost:8765/api/workflows/status \
  -H "Authorization: ******"
```

**Response (200 OK):**
```json
{
  "workflows": [
    {
      "name": "pre-release-validation",
      "status": "passing",
      "last_run": "2026-07-12T16:30:00Z",
      "run_count_7d": 12,
      "success_rate": 0.92
    }
  ],
  "health": {
    "total_workflows": 142,
    "passing": 138,
    "failing": 4,
    "disabled": 0
  }
}
```

#### POST /api/workflows/gate
**Check CI gate compliance (WEC enforcement)**

```bash
curl -X POST http://localhost:8765/api/workflows/gate \
  -H "Content-Type: application/json" \
  -H "Authorization: ******" \
  -d '{
    "pr_number": 1234,
    "required_checks": [
      "auto-approve-workflows",
      "agent-auth-delegation",
      "pre-release-validation"
    ],
    "action": "check"
  }'
```

**Response (200 OK):**
```json
{
  "pr_number": 1234,
  "passed": true,
  "message": "All required checks passed",
  "checks": {
    "auto-approve-workflows": "passed",
    "agent-auth-delegation": "passed",
    "pre-release-validation": "passed"
  }
}
```

#### GET /api/workflows/rate-limit
**Get current GitHub API rate limit status**

```bash
curl http://localhost:8765/api/workflows/rate-limit \
  -H "Authorization: ******"
```

**Response (200 OK):**
```json
{
  "limit": 5000,
  "remaining": 4820,
  "used": 180,
  "reset_time": "2026-07-12T23:40:00Z",
  "reset_seconds": 28640,
  "safe_to_proceed": true
}
```

---

## 3. DECISION VISUALIZATION WORKFLOW

### Step 1: Submit Decision Candidate
Agent collects decision data and submits:

```python
import requests
import json

decision = {
    "lane": "security",
    "candidate": "Fix CVE-2026-XXXXX in src/auth/token_handler.py",
    "confidence_score": 0.92,
    "k1_factor": 0.28,
    "coherence_metric": 0.87,
    "superposition_state": ["APPROVED", "NEEDS_REVIEW"]
}

response = requests.post(
    "http://localhost:8765/api/decisions/submit",
    json=decision,
    headers={"Authorization": f"******"}
)

decision_id = response.json()["decision_id"]
print(f"Decision submitted: {decision_id}")
```

### Step 2: Monitor & Visualize
Orchestrator queries decision status:

```python
# Poll every 5 minutes
response = requests.get(
    f"http://localhost:8765/api/decisions/{decision_id}",
    headers={"Authorization": f"******"}
)

decision_state = response.json()
print(f"Status: {decision_state['status']}")
print(f"Confidence: {decision_state['confidence_score']:.2%}")
print(f"Feedback: {decision_state.get('feedback', 'N/A')}")
```

### Step 3: Provide Feedback / Iterate
Once decision approved by orchestrator, lane executes and reports outcome:

```python
# Lane executes decision, then updates memory
requests.post(
    "http://localhost:8765/api/memory/store",
    json={
        "pattern_name": "security-fix-success",
        "lane": "security",
        "description": f"Successfully applied: {decision_state['candidate']}",
        "confidence": 0.92,
        "usage_count": 1
    },
    headers={"Authorization": f"******"}
)
```

---

## 4. MEMORY SYSTEM INTEGRATION

### Storing Patterns (After Lane Completion)
```python
# Lane 1 (Security) stores vuln fix patterns
patterns_to_store = [
    {
        "pattern_name": "cve-token-rotation-fix",
        "lane": "security",
        "description": "Fix token rotation timing issue by adding barrier synchronization",
        "confidence": 0.88,
        "usage_count": 1,
        "tags": ["token-rotation", "security-fix"]
    },
    {
        "pattern_name": "cve-scope-validation",
        "lane": "security",
        "description": "Validate OAuth scope before token generation",
        "confidence": 0.91,
        "usage_count": 1,
        "tags": ["oauth", "security-fix"]
    }
]

for pattern in patterns_to_store:
    requests.post(
        "http://localhost:8765/api/memory/store",
        json=pattern,
        headers={"Authorization": f"******"}
    )
```

### Retrieving Patterns (At Lane Start)
```python
# Lane 2 (Coverage) retrieves test generation patterns from prior campaigns
response = requests.get(
    "http://localhost:8765/api/memory/retrieve/test-generation-strategy?confidence_min=0.80",
    headers={"Authorization": f"******"}
)

prior_patterns = response.json()["patterns"]
print(f"Found {len(prior_patterns)} high-confidence test patterns")

# Apply first N patterns
for pattern in prior_patterns[:5]:
    print(f"Reusing: {pattern['description']}")
    # Apply pattern to current lane
    apply_pattern(pattern)
```

### Cache Hit Rate Optimization
```python
# Query memory stats to track cache performance
response = requests.get(
    "http://localhost:8765/api/memory/stats",
    headers={"Authorization": f"******"}
)

stats = response.json()
cache_hit_rate = stats["cache"]["hit_rate"]
print(f"Cache hit rate: {cache_hit_rate:.2%}")

# If below 32% baseline, analyze misses
if cache_hit_rate < 0.32:
    print("⚠️ Cache hit rate below baseline. Consider:")
    print("  - Increase pattern reuse (retrieve more prior patterns)")
    print("  - Improve pattern_name consistency")
    print("  - Check LTM retention window")
```

---

## 5. RATE LIMITING & QUOTA BUDGETING

### Rate Limit Awareness
```python
import time

def call_with_rate_limit_awareness(endpoint, method="GET", data=None, max_retries=3):
    for attempt in range(max_retries):
        # Check rate limit before calling
        rate_response = requests.get(
            "http://localhost:8765/api/workflows/rate-limit",
            headers={"Authorization": f"******"}
        )
        rate_data = rate_response.json()
        
        if rate_data["remaining"] < 100:
            # Back off if low
            backoff_seconds = 30 * (2 ** attempt)  # Exponential backoff
            print(f"Rate limit low ({rate_data['remaining']} remaining). Backing off {backoff_seconds}s")
            time.sleep(backoff_seconds)
            continue
        
        # Safe to proceed
        if method == "GET":
            return requests.get(endpoint, headers={"Authorization": f"******"})
        elif method == "POST":
            return requests.post(endpoint, json=data, headers={"Authorization": f"******"})
    
    raise Exception("Rate limit: max retries exceeded")
```

### Budget Planning
```python
# Estimate API calls needed for 5-lane campaign
estimated_calls = {
    "decisions_submitted": 5 * 8,  # 5 lanes × 8 decisions each
    "decisions_retrieved": 5 * 24,  # 5 lanes × 24 queries (every 10min × 4h)
    "memory_store": 5 * 5,  # 5 lanes × 5 patterns stored
    "memory_retrieve": 5 * 3,  # 5 lanes × 3 retrieve calls
    "workflow_checks": 8,  # Every 30min × 4h
    "rate_limit_checks": 24,  # Every 10min × 4h
}

total = sum(estimated_calls.values())
print(f"Estimated API calls: {total}")
print(f"Starting rate limit: 5000")
print(f"Buffer remaining: {5000 - total}")

if (5000 - total) < 500:
    print("⚠️ WARNING: Low buffer. Consider staggering lane execution.")
```

---

## 6. SECURITY & AUTHENTICATION

### Token Handling
```bash
# Always use token fallback chain
export COGNITIVE_APP_TOKEN="${CODEX_MASTER_KEY:-${CODEX_BACKUP_KEY:-$GITHUB_TOKEN}}"

# Verify token is set
if [ -z "$COGNITIVE_APP_TOKEN" ]; then
    echo "ERROR: No token available. Check CODEX_MASTER_KEY, CODEX_BACKUP_KEY, GITHUB_TOKEN"
    exit 1
fi

# Use in requests
curl -H "Authorization: ******" \
    http://localhost:8765/api/decisions/recent
```

### HMAC Validation (Webhook Verification)
The Cognitive App validates webhook signatures using HMAC-SHA256:

```python
import hmac
import hashlib
import json

def verify_webhook_signature(payload, signature, secret):
    """Verify GitHub webhook signature"""
    computed_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    expected_header = f"sha256={computed_signature}"
    return hmac.compare_digest(expected_header, signature)

# All webhooks received by /webhook/github are validated
# No additional action needed by agents
```

### Log Injection Prevention
All logged values are sanitized via `sanitize_for_log()`:

```python
from codex.logging_safe import sanitize_for_log

# Before: user_input = "test\nDEBUG: backdoor accessed"
# After sanitization: "test\\nDEBUG: backdoor accessed" (control chars escaped)

log_message = f"Decision: {sanitize_for_log(user_candidate)}"
```

---

## 7. ERROR HANDLING & RETRY STRATEGIES

### Retry Strategy
```python
import time
from functools import wraps

def retry_on_failure(max_attempts=3, backoff_seconds=5):
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        raise
                    wait_time = backoff_seconds * (2 ** (attempt - 1))
                    print(f"Attempt {attempt} failed: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
        return wrapper
    return decorator

@retry_on_failure(max_attempts=3, backoff_seconds=5)
def submit_decision(decision):
    return requests.post(
        "http://localhost:8765/api/decisions/submit",
        json=decision,
        headers={"Authorization": f"******"},
        timeout=10
    )
```

### Common Errors
| HTTP Code | Meaning | Recovery |
|-----------|---------|----------|
| 400 | Invalid schema | Review decision fields against API docs |
| 401 | Invalid token | Check token chain (CODEX_MASTER_KEY, CODEX_BACKUP_KEY) |
| 404 | Resource not found | Verify decision_id or pattern_name exists |
| 429 | Rate limited | Back off exponentially, check rate-limit endpoint |
| 500 | Server error | Retry with exponential backoff, escalate if persistent |
| 503 | Service unavailable | Cognitive App crashed; restart uvicorn server |

---

## 8. OBSERVABILITY & DEBUGGING

### OpenTelemetry Tracing
All API calls include OTel spans with these standard attributes:

```yaml
span_name: "orchestrator.decision_submit"
attributes:
  lane: "security"
  decision_id: "dec_8f3c9d1e"
  confidence_score: 0.92
  http_method: "POST"
  http_status_code: 200
  duration_ms: 45
  user: "orchestrator-agent"
  pr_number: 1234
```

**Query spans in observability backend:**
```sql
SELECT * FROM spans
WHERE span_name LIKE 'orchestrator.%'
  AND attributes.lane = 'security'
  AND timestamp > NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC
```

### Structured Logging
```python
import logging
import json

logger = logging.getLogger("cognitive_app_integration")

# Log decision submission
logger.info(json.dumps({
    "event": "decision_submitted",
    "decision_id": "dec_8f3c9d1e",
    "lane": "security",
    "confidence_score": 0.92,
    "timestamp": "2026-07-12T16:30:00Z"
}))

# Log error with context
logger.error(json.dumps({
    "event": "rate_limit_exhausted",
    "remaining": 0,
    "reset_seconds": 28640,
    "backoff_attempts": 3,
    "total_delay_seconds": 210
}))
```

---

**Integration Brief Complete.** ✅  
**All Agents Use This Guide** for Cognitive App API integration.  
**Questions?** Refer to `.codex/COGNITIVE_APP_ENHANCEMENT_CAMPAIGN_PLAN_PHASE_15.md`
