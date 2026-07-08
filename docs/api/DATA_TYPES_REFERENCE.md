# API Data Types Reference

Complete reference for all data types and schemas used in the Codex API.

## Table of Contents

1. [Core Data Types](#core-data-types)
2. [Request/Response Objects](#requestresponse-objects)
3. [Authentication Objects](#authentication-objects)
4. [RAG Objects](#rag-objects)
5. [Error Objects](#error-objects)
6. [Type Constraints](#type-constraints)

---

## Core Data Types

### Strings

```typescript
type Email = string & { readonly __brand: "Email" };
type UUID = string & { readonly __brand: "UUID" };
type ISODateTime = string & { readonly __brand: "ISODateTime" };
type JWT = string & { readonly __brand: "JWT" };
```

### Numbers

```typescript
type PercentageScore = number;  // 0.0 to 1.0
type DocumentCount = number;    // >= 0
type FileSizeBytes = number;    // >= 0
type QueryTimeMs = number;      // >= 0
```

### Timestamps

All timestamps use ISO 8601 format:
```
Format: YYYY-MM-DDTHH:MM:SSZ
Example: 2026-07-08T05:53:48Z
```

---

## Request/Response Objects

### Health Response

```typescript
interface HealthResponse {
  status: "ok" | "healthy";
  cognitive_brain?: {
    available: boolean;
    note?: string;  // if not available
  };
  pattern_compressor?: {
    available: boolean;
    n_components?: number;
  };
}
```

### Predict Request

```typescript
interface PredictRequest {
  prompt: string;  // 1-2048 characters, required
}
```

**Constraints:**
- `prompt` must not be empty
- Maximum 2048 characters
- Special characters and multi-line text allowed

### Predict Response

```typescript
interface PredictResponse {
  output: string;  // Generated text
}
```

**Fields:**
- `output`: The generated text from the model
- Guaranteed non-null and non-empty on success

---

## Authentication Objects

### Register Request

```typescript
interface RegisterRequest {
  email: string;      // Valid email, unique, required
  password: string;   // Minimum 12 chars, required
  name: string;       // 1-255 chars, required
}
```

**Email Validation:**
- Must be valid email format (user@domain.com)
- Must be unique across system
- Case-insensitive

**Password Requirements:**
- Minimum 12 characters
- Should contain uppercase, lowercase, numbers, special chars
- Stored as bcrypt hash (irreversible)

**Name Constraints:**
- Minimum 1 character
- Maximum 255 characters
- Supports unicode characters

### Login Request

```typescript
interface LoginRequest {
  email: string;      // Email of registered user
  password: string;   // User password
}
```

### Login Response

```typescript
interface LoginResponse {
  access_token: string;   // JWT token for authentication
  token_type: "bearer";   // Always "bearer"
  expires_in: number;     // Seconds (typically 3600)
  user: {
    id: string;           // Unique user ID (usr_*)
    email: string;        // User email
    name: string;         // User full name
  };
}
```

**Token Details:**
- **Type**: JSON Web Token (JWT)
- **Algorithm**: HS256
- **Duration**: 3600 seconds (1 hour)
- **Usage**: Include in Authorization header as `******

### User Object

```typescript
interface User {
  id: string;              // Format: usr_[alphanumeric]
  email: string;           // User email address
  name: string;            // User full name
  created_at: ISODateTime; // Account creation timestamp
  updated_at: ISODateTime; // Last profile update timestamp
}
```

---

## RAG Objects

### Document

```typescript
interface Document {
  id: string;                    // Unique document ID, required
  content: string;               // Document text, required, 1+ chars
  metadata?: Record<string, string>;  // Optional key-value pairs
}
```

**Document ID:**
- Must be unique within an index
- Alphanumeric and special chars allowed
- Used to identify results

**Metadata:**
- Arbitrary key-value pairs
- All values must be strings
- Preserved in query results
- Useful for filtering/sorting (client-side)

### Build Index Request

```typescript
interface BuildIndexRequest {
  index_name: string;     // 1-128 chars, alphanumeric/dash/underscore
  documents: Document[];  // 1+ documents, required
}
```

**Index Name Constraints:**
- Must match pattern: `^[A-Za-z0-9._-]{1,128}$`
- No spaces or special characters except dot, underscore, dash
- Case-sensitive

### Build Index Response

```typescript
interface BuildIndexResponse {
  index_name: string;           // Name of created index
  document_count: number;       // Number of documents indexed
  size_bytes: number;           // Index size on disk
  created_at: ISODateTime;      // Creation timestamp
}
```

### Query Request

```typescript
interface QueryRequest {
  index_name: string;    // Name of index to query
  query: string;         // Search query (1-1024 chars)
  top_k?: number;        // Results to return (1-100, default: 5)
  threshold?: number;    // Minimum score (0-1, default: 0.0)
}
```

**Query String:**
- Freeform text search
- Any characters allowed
- Typically 1-100 characters for best results
- Longer queries possible but slower

**Top K:**
- Number of results to return
- Minimum 1, maximum 100
- Default 5
- Actual results may be fewer if fewer documents match

**Threshold:**
- Minimum relevance score (0.0 = all results, 1.0 = only perfect matches)
- Range: 0.0 to 1.0
- Default 0.0 (no filtering)
- 0.5+ recommended for strict matching

### Query Result

```typescript
interface QueryResult {
  document_id: string;           // ID of matching document
  content: string;               // Document content
  score: number;                 // Relevance score (0.0-1.0)
  metadata?: Record<string, string>;  // Original metadata
}
```

**Score Interpretation:**
- 0.0-0.2: Weak match
- 0.2-0.5: Moderate match
- 0.5-0.8: Strong match
- 0.8-1.0: Very strong/exact match

### Query Response

```typescript
interface QueryResponse {
  query: string;              // Original query string
  results: QueryResult[];     // Array of matching documents
  total_results: number;      // Number of results returned
  query_time_ms: number;      // Query execution time
}
```

### Index Info

```typescript
interface IndexInfo {
  name: string;               // Index name
  document_count: number;     // Number of indexed documents
  size_bytes: number;         // Index size on disk (bytes)
  created_at: ISODateTime;    // Creation timestamp
  updated_at: ISODateTime;    // Last update timestamp
}
```

### List Indices Response

```typescript
interface ListIndicesResponse {
  indices: IndexInfo[];       // Array of index info
  total_count: number;        // Total number of indices
}
```

### Delete Index Response

```typescript
interface DeleteIndexResponse {
  index_name: string;         // Name of deleted index
  deleted_at: ISODateTime;    // Deletion timestamp
  document_count_deleted: number;  // Number of deleted documents
}
```

### Merge Indices Request

```typescript
interface MergeIndicesRequest {
  source_indices: string[];   // 2+ indices to merge
  target_index: string;       // Name for merged index
}
```

**Merge Behavior:**
- Combines all documents from source indices
- Creates new unified index
- Source indices remain unchanged
- Documents are deduplicated by ID

### Merge Indices Response

```typescript
interface MergeIndicesResponse {
  target_index: string;              // Name of merged index
  source_indices_merged: string[];   // Source indices used
  total_documents: number;           // Documents in merged index
  merged_at: ISODateTime;            // Merge completion time
}
```

### Index Stats

```typescript
interface StatsResponse {
  index_name: string;         // Index name
  document_count: number;     // Number of documents
  average_doc_length: number; // Average document length in chars
  vocabulary_size: number;    // Unique terms in index
  size_bytes: number;         // Total index size
  created_at: ISODateTime;    // Creation timestamp
}
```

### RAG Metrics

```typescript
interface MetricsResponse {
  total_indices: number;           // Number of indices
  total_documents: number;         // Total indexed documents
  total_queries: number;           // Cumulative queries processed
  average_query_time_ms: number;  // Mean query execution time
  uptime_seconds: number;          // System uptime
}
```

---

## Error Objects

### Error Response

```typescript
interface ErrorResponse {
  detail: string;              // Error message
  status_code: number;         // HTTP status code
  timestamp?: ISODateTime;     // When error occurred
}
```

### Error Types by Status Code

#### 400 Bad Request

```typescript
interface BadRequestError {
  detail: "Invalid index_name: must use only letters, digits...";
  status_code: 400;
}
```

Causes:
- Malformed request body
- Invalid parameter values
- Missing required fields

#### 401 Unauthorized

```typescript
interface UnauthorizedError {
  detail: "Invalid authentication credentials";
  status_code: 401;
}
```

Causes:
- Missing or invalid JWT token
- Expired token
- Invalid credentials

#### 403 Forbidden

```typescript
interface ForbiddenError {
  detail: "User does not have permission";
  status_code: 403;
}
```

Causes:
- User lacks required permissions
- Resource is restricted

#### 404 Not Found

```typescript
interface NotFoundError {
  detail: "Index not found";
  status_code: 404;
}
```

Causes:
- Index doesn't exist
- Document not found
- Endpoint doesn't exist

#### 422 Unprocessable Entity

```typescript
interface ValidationError {
  detail: "field required";
  status_code: 422;
}
```

Causes:
- Validation error in request body
- Invalid field value
- Type mismatch

#### 429 Too Many Requests

```typescript
interface RateLimitError {
  detail: "Rate limit exceeded";
  status_code: 429;
  retry_after?: number;  // Seconds to wait before retry
}
```

Causes:
- Exceeded endpoint rate limit
- Too many concurrent requests

#### 500 Internal Server Error

```typescript
interface InternalError {
  detail: "Internal server error";
  status_code: 500;
}
```

Causes:
- Unexpected server error
- Database error
- Processing failure

---

## Type Constraints

### Enumeration Types

#### Status Values

```typescript
type Status = "ok" | "healthy" | "error";
type TokenType = "bearer";
type HttpMethod = "GET" | "POST" | "DELETE" | "PUT" | "PATCH";
```

### Numeric Constraints

| Type | Min | Max | Default | Example |
|------|-----|-----|---------|---------|
| `top_k` | 1 | 100 | 5 | 10 |
| `threshold` | 0.0 | 1.0 | 0.0 | 0.5 |
| `expires_in` | 1 | 86400 | 3600 | 3600 |
| `document_count` | 0 | ∞ | - | 150 |

### String Length Constraints

| Field | Min | Max | Example |
|-------|-----|-----|---------|
| `prompt` | 1 | 2048 | "What is AI?" |
| `query` | 1 | 1024 | "machine learning" |
| `email` | 5 | 255 | "user@example.com" |
| `password` | 12 | 255 | "SecurePass123!" |
| `name` | 1 | 255 | "John Doe" |
| `index_name` | 1 | 128 | "my_documents" |
| `id` | 1 | 255 | "doc_001" |

### Pattern Constraints

#### Email Pattern
```
^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
```

#### Index Name Pattern
```
^[A-Za-z0-9._-]{1,128}$
```

#### UUID Pattern (User IDs, etc)
```
^[a-f0-9-]{36}$
```

---

## Nullable Fields

Fields that can be null/absent (optional):

- `User.updated_at` - null for new users
- `Document.metadata` - absent if not provided
- `QueryResult.metadata` - absent if not in document
- `HealthResponse.cognitive_brain` - absent if not available
- `HealthResponse.pattern_compressor` - absent if not available

---

## Type Safety Guidelines

### TypeScript

```typescript
// ✅ Good: Strict typing
const result: QueryResult = {
  document_id: "doc_001",
  content: "...",
  score: 0.92,
  metadata: { source: "file.txt" }
};

// ❌ Bad: Loose typing
const result: any = { ...data };
```

### Python

```python
# ✅ Good: Use Pydantic models
from pydantic import BaseModel

class Document(BaseModel):
    id: str
    content: str
    metadata: Optional[Dict[str, str]] = None

# ❌ Bad: Unvalidated dicts
document = {"id": "doc_001", ...}  # No validation
```

### Validation

Always validate data before sending:

```typescript
// ✅ Good
if (indexName.match(/^[A-Za-z0-9._-]{1,128}$/)) {
  // Proceed
}

// ❌ Bad
// Just send without validation
```

---

**Last Updated:** 2026-07-08
