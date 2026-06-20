# Critical Business Paths for Verification

**Generated:** Auto-extracted from codebase analysis

## Authentication Flow

**Description:** GitHub OAuth authentication and session establishment

**Entry Point:** `/auth/github`

**Key Steps:**
- Receive OAuth code from GitHub
- Exchange code for access token
- Fetch user information
- Create/update session
- Set session cookies

**Expected Latency:** 1500ms

**Error Handling:** Redirect to login on failure, log OAuth errors

---

## Mcp Api Request

**Description:** Process MCP API requests through facade

**Entry Point:** `POST /mcp/v1/jsonrpc`

**Key Steps:**
- Parse JSON-RPC request
- Validate request format
- Route to appropriate adapter
- Execute adapter command
- Format response
- Return to client

**Expected Latency:** 3000ms

**Error Handling:** Return JSON-RPC error object, log to observability system

---

## Health Check

**Description:** Service health verification

**Entry Point:** `GET /health or GET /mcp/v1/health`

**Key Steps:**
- Load adapter
- Query adapter health
- Compile health status
- Return JSON response

**Expected Latency:** 500ms

**Error Handling:** Return degraded status, continue serving

---

## Data Persistence

**Description:** Store and retrieve data from backend

**Entry Point:** `Adapter query/store methods`

**Key Steps:**
- Validate data format
- Connect to backend
- Execute database query
- Process results
- Return formatted data

**Expected Latency:** 2000ms

**Error Handling:** Transaction rollback, error logging, client notification

---

## Vector Retrieval

**Description:** Semantic search using vector embeddings

**Entry Point:** `RAG query pipeline`

**Key Steps:**
- Receive query text
- Generate embeddings
- Query vector store
- Rank results
- Retrieve full documents
- Format results

**Expected Latency:** 5000ms

**Error Handling:** Fallback to keyword search, log embedding errors

---

## Error Recovery

**Description:** Handle errors and maintain service availability

**Entry Point:** `Middleware/exception handlers`

**Key Steps:**
- Catch exception
- Log error details
- Check retry policy
- Attempt retry if appropriate
- Return error response

**Expected Latency:** 1000ms

**Error Handling:** Circuit breaker pattern, graceful degradation

---

