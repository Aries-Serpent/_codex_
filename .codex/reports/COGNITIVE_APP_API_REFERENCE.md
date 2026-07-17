# Cognitive App API Reference
**Version:** v0.2.0 (Development)  
**Backend Status:** Mock API (v0.3.0 pending)  
**Last Updated:** 2026-07-17

---

## Overview

The Cognitive App provides a comprehensive API for quantum decision-making, memory management, code generation, and agent orchestration. This reference covers the planned backend API structure and current development patterns.

### Current Status
- **Frontend:** React components with mock data
- **Backend:** Planned for v0.3.0 (FastAPI)
- **Mocking:** Comprehensive fallback data included
- **WebSocket:** Planned for real-time updates

---

## Table of Contents

1. [Quantum Decision API](#quantum-decision-api)
2. [Memory Management API](#memory-management-api)
3. [Code Generation API](#code-generation-api)
4. [Agent Orchestration API](#agent-orchestration-api)
5. [Real-Time Updates (WebSocket)](#real-time-updates-websocket)
6. [Error Handling](#error-handling)
7. [Authentication](#authentication)
8. [Rate Limiting](#rate-limiting)
9. [Code Examples](#code-examples)

---

## Quantum Decision API

### Get Quantum State

Retrieve current quantum metrics and system state.

```
GET /api/quantum/state
```

**Parameters:** None

**Response:** (200 OK)
```json
{
  "k1_factor": 0.35,
  "quantum_advantage": 2.86,
  "coherence": 0.685,
  "superposition_count": 12,
  "phase": 8,
  "timestamp": "2026-07-17T20:37:41Z",
  "status": "active"
}
```

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `k1_factor` | float | Quantum advantage factor (target ≤ 0.35) |
| `quantum_advantage` | float | Speed advantage over classical (2.86×) |
| `coherence` | float | Wave function coherence (0.0–1.0) |
| `superposition_count` | int | Active parallel scenarios |
| `phase` | int | Current phase (1–8) |
| `timestamp` | ISO 8601 | Response timestamp |
| `status` | string | System status: "active", "idle", "error" |

**Example (JavaScript):**
```javascript
const response = await fetch('/api/quantum/state');
const data = await response.json();
console.log(`Quantum advantage: ${data.quantum_advantage}x`);
```

---

### Make Quantum Decision

Execute quantum decision algorithm with provided scenarios.

```
POST /api/quantum/decide
```

**Request Body:**
```json
{
  "scenarios": [
    {
      "id": "scenario_1",
      "description": "Deploy to production",
      "probability": 0.7,
      "risk_level": "medium"
    },
    {
      "id": "scenario_2",
      "description": "Wait for more testing",
      "probability": 0.3,
      "risk_level": "low"
    }
  ],
  "params": {
    "coherence_threshold": 0.6,
    "timeout_ms": 5000,
    "paradigm": "fluid"
  }
}
```

**Response:** (200 OK)
```json
{
  "decision": "scenario_1",
  "confidence": 0.92,
  "collapsed_state": {
    "k1_factor": 0.34,
    "coherence": 0.71
  },
  "execution_time_ms": 234,
  "trace": "Superposition → Entanglement → Collapse → Decision"
}
```

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `decision` | string | Selected scenario ID |
| `confidence` | float | Decision confidence (0.0–1.0) |
| `collapsed_state` | object | Quantum state post-collapse |
| `execution_time_ms` | int | Algorithm execution time |
| `trace` | string | Decision process trace |

---

### Get Decision History

Retrieve historical decisions with metrics.

```
GET /api/quantum/history?limit=10&offset=0
```

**Query Parameters:**
- `limit` (int, default 10): Max results per page
- `offset` (int, default 0): Pagination offset
- `since` (ISO 8601, optional): Filter by date

**Response:** (200 OK)
```json
{
  "decisions": [
    {
      "id": "decision_001",
      "timestamp": "2026-07-17T20:30:00Z",
      "decision": "scenario_1",
      "confidence": 0.92,
      "execution_time_ms": 234
    }
  ],
  "total": 45,
  "page": 1,
  "pages": 5
}
```

---

## Memory Management API

### Search Memories

Full-text search across STM and LTM patterns.

```
GET /api/memory/search?q=<query>&limit=20&offset=0
```

**Query Parameters:**
- `q` (string, required): Search query
- `limit` (int, default 20): Max results
- `offset` (int, default 0): Pagination offset
- `type` (string, optional): Filter by type ("stm", "ltm", or both)

**Response:** (200 OK)
```json
{
  "results": [
    {
      "id": "pattern_042",
      "title": "Deploy Pattern",
      "type": "ltm",
      "content": "Automated deployment workflow",
      "access_count": 15,
      "relevance_score": 0.94,
      "last_accessed": "2026-07-17T19:45:00Z"
    }
  ],
  "total": 47,
  "execution_time_ms": 89,
  "page": 1
}
```

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Pattern ID |
| `title` | string | Pattern name |
| `type` | string | "stm" or "ltm" |
| `content` | string | Pattern description |
| `access_count` | int | Total accesses |
| `relevance_score` | float | Search relevance (0.0–1.0) |
| `last_accessed` | ISO 8601 | Last access time |

---

### Get Memory Statistics

Retrieve current memory system metrics.

```
GET /api/memory/stats
```

**Response:** (200 OK)
```json
{
  "stm_count": 24,
  "ltm_count": 156,
  "stm_capacity": 100,
  "ltm_capacity": 1000,
  "cache_hit_rate": 0.32,
  "cache_miss_rate": 0.68,
  "compression_ratio": 0.60,
  "total_searches": 1203,
  "consolidations": 8,
  "last_consolidation": "2026-07-17T15:20:00Z"
}
```

---

### Consolidate Memory

Promote STM entries to LTM based on access patterns.

```
POST /api/memory/consolidate
```

**Request Body:** (optional)
```json
{
  "threshold": 3,
  "force_all": false
}
```

**Response:** (200 OK)
```json
{
  "promoted_count": 7,
  "promoted_items": [
    {
      "id": "stm_012",
      "title": "Pattern 12",
      "reason": "access_count >= threshold (3)"
    }
  ],
  "consolidation_time_ms": 145,
  "new_stm_count": 17,
  "new_ltm_count": 163
}
```

---

### Create Memory Pattern

Store a new pattern in STM/LTM.

```
POST /api/memory/create
```

**Request Body:**
```json
{
  "title": "New Pattern",
  "content": "Pattern description",
  "tags": ["tag1", "tag2"],
  "type": "stm"
}
```

**Response:** (201 Created)
```json
{
  "id": "pattern_new_001",
  "title": "New Pattern",
  "content": "Pattern description",
  "tags": ["tag1", "tag2"],
  "type": "stm",
  "created_at": "2026-07-17T20:37:41Z"
}
```

---

## Code Generation API

### Generate Code

Generate code from natural language prompt.

```
POST /api/code/generate
```

**Request Body:**
```json
{
  "prompt": "Create a function to sort an array of objects by name",
  "language": "python",
  "context": "async function with error handling",
  "model": "codex-default"
}
```

**Response:** (200 OK)
```json
{
  "code": "async def sort_by_name(items):\n    try:\n        return sorted(items, key=lambda x: x.get('name', ''))\n    except Exception as e:\n        raise ValueError(f'Sort failed: {e}')",
  "language": "python",
  "complexity": {
    "cyclomatic": 2,
    "cognitive": 3,
    "maintainability": 85
  },
  "quality_score": 0.88,
  "execution_time_ms": 342,
  "confidence": 0.92
}
```

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `code` | string | Generated code |
| `language` | string | Target language |
| `complexity` | object | Code metrics |
| `quality_score` | float | Quality rating (0.0–1.0) |
| `execution_time_ms` | int | Generation time |
| `confidence` | float | Confidence in result (0.0–1.0) |

---

### Analyze Code

Analyze code quality and generate suggestions.

```
POST /api/code/analyze
```

**Request Body:**
```json
{
  "code": "function add(a, b) { return a + b; }",
  "language": "javascript"
}
```

**Response:** (200 OK)
```json
{
  "metrics": {
    "lines": 1,
    "complexity": 1,
    "maintainability": 95,
    "test_coverage": 0
  },
  "issues": [
    {
      "severity": "info",
      "code": "missing-doc",
      "message": "Missing JSDoc comment"
    }
  ],
  "suggestions": [
    "Add parameter validation",
    "Add JSDoc comments",
    "Consider adding type hints"
  ],
  "execution_time_ms": 156
}
```

---

### Get Code Templates

Retrieve available code templates.

```
GET /api/code/templates?language=python&category=data
```

**Query Parameters:**
- `language` (string, optional): Filter by language
- `category` (string, optional): Filter by category

**Response:** (200 OK)
```json
{
  "templates": [
    {
      "id": "template_001",
      "name": "Sort Function",
      "language": "python",
      "category": "data",
      "code": "def sort_list(items):\n    return sorted(items)",
      "description": "Sort a list of items"
    }
  ],
  "total": 24,
  "languages": ["python", "javascript", "typescript", "go", "rust"]
}
```

---

## Agent Orchestration API

### List Agents

Get available agents.

```
GET /api/agents?status=active&limit=50
```

**Query Parameters:**
- `status` (string, optional): Filter by status ("active", "idle", "offline")
- `limit` (int, default 50): Max results
- `offset` (int, default 0): Pagination offset

**Response:** (200 OK)
```json
{
  "agents": [
    {
      "id": "agent_001",
      "name": "Code Auditor",
      "status": "active",
      "current_task": "task_123",
      "performance": {
        "tasks_completed": 156,
        "success_rate": 0.98,
        "avg_execution_ms": 234
      }
    }
  ],
  "total": 8
}
```

---

### Create Workflow Token

Create a custom workflow token.

```
POST /api/agents/tokens/create
```

**Request Body:**
```json
{
  "name": "CUSTOM_AUDIT",
  "description": "Custom audit workflow",
  "paradigm": "fluid",
  "trigger_conditions": ["on_push", "on_schedule"],
  "dependencies": ["AUDIT_EXEC"]
}
```

**Response:** (201 Created)
```json
{
  "id": "token_custom_001",
  "name": "CUSTOM_AUDIT",
  "description": "Custom audit workflow",
  "paradigm": "fluid",
  "status": "ready",
  "created_at": "2026-07-17T20:37:41Z"
}
```

---

### Execute Workflow

Execute a workflow with specified tokens.

```
POST /api/agents/orchestrate
```

**Request Body:**
```json
{
  "workflow_tokens": ["AUDIT_EXEC", "DOC_GEN", "REVIEW"],
  "params": {
    "timeout_ms": 30000,
    "parallel": true,
    "on_failure": "stop"
  }
}
```

**Response:** (202 Accepted)
```json
{
  "execution_id": "exec_001",
  "status": "running",
  "workflow_tokens": ["AUDIT_EXEC", "DOC_GEN", "REVIEW"],
  "progress": 0,
  "created_at": "2026-07-17T20:37:41Z"
}
```

---

### Get Execution Status

Monitor workflow execution.

```
GET /api/agents/execute/{execution_id}
```

**Response:** (200 OK)
```json
{
  "execution_id": "exec_001",
  "status": "running",
  "progress": 67,
  "current_token": "DOC_GEN",
  "tasks": [
    {
      "token": "AUDIT_EXEC",
      "status": "completed",
      "duration_ms": 2340,
      "result": "8 issues found"
    },
    {
      "token": "DOC_GEN",
      "status": "running",
      "progress": 45
    }
  ],
  "eta_ms": 1200
}
```

---

## Real-Time Updates (WebSocket)

### Connect to WebSocket

```javascript
const ws = new WebSocket('wss://api.example.com/ws/cognitive');

ws.addEventListener('message', (event) => {
  const data = JSON.parse(event.data);
  console.log('Real-time update:', data);
});
```

### Quantum Updates

```
Channel: ws://api/ws/quantum
Event: quantum:update
Payload: { state: QuantumState, phase: int }

Event: quantum:decision
Payload: { decision: string, confidence: float }
```

### Memory Updates

```
Channel: ws://api/ws/memory
Event: memory:consolidation
Payload: { progress: float, promoted_count: int }

Event: memory:search
Payload: { results: MemoryPattern[], query: string }
```

### Agent Updates

```
Channel: ws://api/ws/agents
Event: agent:task_started
Payload: { agent_id: string, task_id: string }

Event: agent:task_completed
Payload: { agent_id: string, result: TaskResult }

Event: agent:status
Payload: { agent_id: string, status: string }
```

---

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Missing required field: 'prompt'",
    "status": 400,
    "details": {
      "field": "prompt",
      "reason": "required"
    }
  }
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `INVALID_REQUEST` | 400 | Invalid request parameters |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Access denied |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource already exists |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

---

## Authentication

### API Key Authentication (Planned)

```javascript
const response = await fetch('/api/quantum/state', {
  headers: {
    'Authorization': '******'
  }
});
```

### OAuth 2.0 (Future)

```javascript
const token = await getOAuthToken();
const response = await fetch('/api/quantum/state', {
  headers: {
    'Authorization': `******
  }
});
```

---

## Rate Limiting

### Rate Limit Headers

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1689525600
```

### Rate Limit Tiers

| Tier | Requests/Hour | Concurrent |
|------|---------------|-----------|
| Free | 100 | 1 |
| Pro | 10,000 | 10 |
| Enterprise | Unlimited | 100 |

---

## Code Examples

### React Hook Integration

```typescript
import { useQuantumState } from '@/hooks/use-quantum-state';
import { useMemorySystem } from '@/hooks/use-memory-system';

function MyComponent() {
  const { state: quantum } = useQuantumState(true, 10000);
  const { state: memory, searchMemories } = useMemorySystem(true, 10000);

  const handleSearch = (query: string) => {
    searchMemories(query);
  };

  return (
    <div>
      <p>Quantum Advantage: {quantum?.quantum_advantage}x</p>
      <p>STM Count: {memory?.stm_count}</p>
      <button onClick={() => handleSearch('pattern')}>Search</button>
    </div>
  );
}
```

### Direct API Calls

```typescript
// Quantum decision
const response = await fetch('/api/quantum/decide', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    scenarios: [
      { id: 'opt1', description: 'Deploy' },
      { id: 'opt2', description: 'Wait' }
    ]
  })
});

const result = await response.json();
console.log(`Decision: ${result.decision} (${result.confidence * 100}% confidence)`);
```

### Error Handling

```typescript
try {
  const response = await fetch('/api/code/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt: 'Generate code' })
  });

  if (!response.ok) {
    const error = await response.json();
    console.error(`Error: ${error.error.code} - ${error.error.message}`);
    return;
  }

  const data = await response.json();
  console.log('Generated code:', data.code);
} catch (error) {
  console.error('Network error:', error);
}
```

---

## Pagination

### Offset-Based Pagination

```
GET /api/memory/search?q=pattern&limit=20&offset=40
```

Response includes:
- `total`: Total number of results
- `page`: Current page number
- `pages`: Total pages
- `limit`: Results per page

### Cursor-Based Pagination

Future implementation will use cursor-based pagination for better scalability.

---

## Versioning

### API Versioning

```
GET /api/v1/quantum/state
GET /api/v2/quantum/state
```

Current version: **v1** (stable)

---

## Deprecation Policy

APIs will be deprecated with:
- 30-day notice
- Migration guide provided
- Support for 2 API versions simultaneously
- Warning headers in responses

---

## Support & Issues

- **Documentation:** [GitHub Wiki](https://github.com/Aries-Serpent/_codex_/wiki)
- **Issues:** [GitHub Issues](https://github.com/Aries-Serpent/_codex_/issues)
- **API Status:** [Status Page](https://status.example.com)

---

*Last Updated: 2026-07-17 | API Version: v0.2.0 | Backend Status: Development (v0.3.0)*
