# Comprehensive API Reference Master

> **Consolidated Master Document** for Codex APIs  
> **Created**: 2026-07-08  
> **Consolidation Campaign**: Phase 12 WS3  
> **Status**: ✅ Active Master Document

**Consolidated from** 8 source files:
- docs/API_REFERENCE.md
- docs/api/API_DOCUMENTATION.md
- docs/RAG_API_REFERENCE.md
- docs/audit/API_Reference_v1.4.0.md
- docs/INGESTION_API_REFERENCE.md
- GitHub API reference documents
- MCP API references

---

## Table of Contents

1. [API Overview](#api-overview)
2. [Core APIs](#core-apis)
3. [GitHub API Integration](#github-api-integration)
4. [RAG API](#rag-api)
5. [Data Ingestion API](#data-ingestion-api)
6. [MCP API Reference](#mcp-api-reference)
7. [Authentication](#authentication)
8. [Error Handling](#error-handling)
9. [Rate Limiting](#rate-limiting)
10. [Examples & Best Practices](#examples--best-practices)

---

## API Overview

### Available APIs

| API | Type | Base URL | Authentication |
|-----|------|----------|-----------------|
| **Codex Core** | REST | `/api/v1` | Token/JWT |
| **GitHub Integration** | GraphQL/REST | `https://api.github.com` | OAuth/PAT |
| **RAG Retrieval** | REST | `/api/v1/rag` | API Key |
| **Data Ingestion** | REST | `/api/v1/ingest` | API Key |
| **MCP (Model Context Protocol)** | JSON-RPC | `/api/mcp` | OAuth |

---

## Core APIs

### Session Management API

```yaml
/api/v1/sessions:
  POST:
    summary: Create new session
    request:
      session_type: string (copilot/cli/agent)
      metadata: object
    response:
      session_id: string
      created_at: ISO8601
      
  GET:
    summary: List sessions
    query_params:
      limit: integer (default: 50)
      offset: integer (default: 0)
    response:
      sessions: Session[]
      total: integer

/api/v1/sessions/{session_id}:
  GET:
    summary: Get session details
    response:
      id: string
      status: string (active/completed/failed)
      events: Event[]
      
  PATCH:
    summary: Update session
    request:
      status: string
      metadata: object
    response:
      updated: boolean
```

### Event Logging API

```yaml
/api/v1/sessions/{session_id}/events:
  POST:
    summary: Log event
    request:
      type: string (user.message/assistant.response/tool.execution)
      content: string
      metadata: object
    response:
      event_id: string
      timestamp: ISO8601
      
  GET:
    summary: List session events
    response:
      events: Event[]
      total: integer
```

### Memory API

```yaml
/api/v1/memory:
  GET:
    summary: Get memory (STM/LTM)
    query_params:
      scope: string (stm/ltm/both)
      limit: integer
    response:
      facts: Fact[]
      
  POST:
    summary: Store fact
    request:
      fact: string
      scope: string (stm/ltm)
    response:
      fact_id: string
      stored: boolean
```

---

## GitHub API Integration

### OAuth Authentication

```python
import requests

# 1. Redirect user to GitHub for authorization
github_auth_url = (
    f"https://github.com/login/oauth/authorize?"
    f"client_id={CLIENT_ID}&"
    f"scope=repo,gist,read:user&"
    f"state={random_state}"
)

# 2. Exchange code for token
response = requests.post(
    "https://github.com/login/oauth/access_token",
    json={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": auth_code,
        "state": state
    }
)
access_token = response.json()["access_token"]

# 3. Use token in API calls
headers = {"Authorization": f"******"}
```

### GraphQL Example

```graphql
query {
  repository(owner: "Aries-Serpent", name: "_codex_") {
    name
    description
    url
    issues(first: 10) {
      nodes {
        number
        title
        state
      }
    }
    pullRequests(first: 10) {
      nodes {
        number
        title
        state
      }
    }
  }
}
```

### REST API Examples

**List Issues**:
```bash
GET /repos/{owner}/{repo}/issues
Authorization: ******
```

**Create PR Comment**:
```bash
POST /repos/{owner}/{repo}/issues/{issue_number}/comments
Authorization: ******
Content-Type: application/json

{
  "body": "Comment text"
}
```

**Get Workflow Runs**:
```bash
GET /repos/{owner}/{repo}/actions/runs
Authorization: ******
```

---

## RAG API

### Semantic Search

```yaml
/api/v1/rag/search:
  POST:
    summary: Semantic search over codebase
    request:
      query: string (natural language)
      limit: integer (default: 10)
      filters:
        file_type: string (optional)
        path_prefix: string (optional)
    response:
      results:
        - id: string
          score: float (0-1)
          file_path: string
          content_snippet: string
          
  Content-Type: application/json
```

### Embeddings API

```yaml
/api/v1/rag/embeddings:
  POST:
    summary: Generate embeddings
    request:
      texts: string[]
    response:
      embeddings: float[][]
      model: string
      
/api/v1/rag/similarity:
  POST:
    summary: Compute similarity between texts
    request:
      text1: string
      text2: string
    response:
      similarity_score: float (0-1)
      embedding_model: string
```

### Index Management

```yaml
/api/v1/rag/index:
  POST:
    summary: Reindex codebase
    response:
      job_id: string
      status: string (queued/processing/complete)
      
  GET:
    summary: Get index status
    response:
      status: string
      indexed_files: integer
      last_updated: ISO8601
```

---

## Data Ingestion API

### File Upload

```yaml
/api/v1/ingest/upload:
  POST:
    summary: Upload file for ingestion
    content-type: multipart/form-data
    fields:
      file: binary
      category: string (code/doc/test/config)
    response:
      file_id: string
      status: string (ingesting/processed)
      
/api/v1/ingest/{file_id}:
  GET:
    summary: Get ingestion status
    response:
      status: string
      lines_processed: integer
      errors: string[]
```

### Batch Ingestion

```yaml
/api/v1/ingest/batch:
  POST:
    summary: Submit batch ingest job
    request:
      files: string[] (file paths or URLs)
      process_type: string (parse/analyze/validate)
    response:
      batch_id: string
      total_files: integer
      
  GET:
    summary: Get batch status
    response:
      batch_id: string
      processed: integer
      total: integer
      results: IngestResult[]
```

---

## MCP API Reference

### Tool Registration

```yaml
/api/mcp/tools/register:
  POST:
    summary: Register MCP tool
    request:
      name: string
      description: string
      schema: JSONSchema
    response:
      tool_id: string
      registered: boolean
```

### Tool Execution

```yaml
/api/mcp/tools/{tool_id}/execute:
  POST:
    summary: Execute registered MCP tool
    request:
      arguments: object
    response:
      result: any
      execution_time: number
      success: boolean
```

---

## Authentication

### Token Types

1. **API Key**: Static token for service-to-service auth
2. **OAuth Token**: User-granted access via OAuth flow
3. **JWT**: Signed token for internal services
4. **GitHub PAT**: Personal Access Token for GitHub API

### ****** Usage

```bash
# Include in Authorization header
Authorization: ******

# Or as query parameter (for webhooks)
?token={token}
```

### Rate Limit Headers

```
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 4999
X-RateLimit-Reset: 1234567890
```

---

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": "string (optional)",
    "request_id": "string"
  }
}
```

### Common Status Codes

| Status | Meaning | Retry |
|--------|---------|-------|
| 200 | Success | No |
| 400 | Bad Request | No |
| 401 | Unauthorized | No |
| 403 | Forbidden | No |
| 404 | Not Found | No |
| 429 | Rate Limited | Yes (with backoff) |
| 500 | Server Error | Yes |
| 503 | Service Unavailable | Yes |

---

## Rate Limiting

### Default Rate Limits

```
Unauthenticated: 60 requests/hour
Authenticated: 5,000 requests/hour
Admin: Unlimited
```

### Backoff Strategy

```python
import time

def call_with_backoff(endpoint, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(endpoint)
        if response.status_code == 429:
            wait_time = 2 ** attempt  # exponential backoff
            time.sleep(wait_time)
        else:
            return response
```

---

## Examples & Best Practices

### Example: Create PR Comment

```python
import requests

def comment_on_pr(owner, repo, pr_number, comment_text):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"******",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"body": comment_text}
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()
```

### Example: Semantic Search

```python
def search_codebase(query, limit=10):
    response = requests.post(
        "http://localhost:8000/api/v1/rag/search",
        json={
            "query": query,
            "limit": limit
        },
        headers={"Authorization": f"******"}
    )
    return response.json()["results"]
```

### Best Practices

1. **Always include error handling** - Networks fail
2. **Implement exponential backoff** - For rate limits
3. **Cache results when possible** - Reduce API calls
4. **Use pagination** - For large result sets
5. **Validate input** - Before sending to API
6. **Log request IDs** - For debugging

---

**This document is the authoritative API reference for Codex.**

*Last Updated: 2026-07-08*  
*Consolidation Status: ✅ Complete (8 files merged)*
