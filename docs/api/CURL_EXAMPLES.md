# cURL Examples - Complete API Integration Guide
**Last Updated:** 2026-07-11
**Version:** v0.2.1

This guide provides ready-to-use cURL commands for all Codex API endpoints.

## Table of Contents

1. [Health & Info](#health--info)
2. [Text Generation](#text-generation)
3. [Authentication](#authentication)
4. [RAG Operations](#rag-operations)
5. [Advanced Scenarios](#advanced-scenarios)
6. [Error Handling](#error-handling)

---

## Health & Info

### Check Main API Health

```bash
curl -X GET http://localhost:8000/health
```

**Pretty-printed response:**
```bash
curl -s -X GET http://localhost:8000/health | jq .
```

**With verbose output:**
```bash
curl -v http://localhost:8000/health
```

### Check RAG API Health

```bash
curl -X GET http://localhost:8001/rag/health
```

### Get API Information

```bash
curl -X GET http://localhost:8000/
```

---

## Text Generation

### Simple Text Generation

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is machine learning?"}'
```

### With Pretty Printing

```bash
curl -s -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain quantum computing"}' | jq .
```

### Long Prompt

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Provide a comprehensive explanation of deep learning, including neural networks, backpropagation, and common architectures used in modern AI systems."
  }'
```

### Save Response to File

```bash
curl -s -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a technical summary"}' > response.json

cat response.json | jq .output
```

### Extract Only Generated Text

```bash
curl -s -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello"}' | jq -r '.output'
```

---

## Authentication

### Register New User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "MySecurePass123!",
    "name": "John Doe"
  }'
```

### Login & Save Token

```bash
# Login and extract token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "MySecurePass123!"
  }' | jq -r '.access_token')

echo "Token: $TOKEN"
```

### Use Token in Subsequent Requests

```bash
# Set token as variable
TOKEN="your_jwt_token_here"

# Use in request
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: ******"
```

### Refresh Token

```bash
TOKEN="your_current_token"

curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Authorization: ******" | jq .
```

### Full Authentication Workflow

```bash
#!/bin/bash

# 1. Register new user
echo "=== Registering user ==="
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "TestPass123!",
    "name": "Test User"
  }')
echo "$REGISTER_RESPONSE" | jq .

# 2. Login and get token
echo -e "\n=== Logging in ==="
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "TestPass123!"
  }')
echo "$LOGIN_RESPONSE" | jq .

TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
echo "Token: $TOKEN"

# 3. Use token for protected operations
echo -e "\n=== Using token (logout) ==="
curl -s -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: ******" | jq .

# 4. Refresh token
echo -e "\n=== Refreshing token ==="
curl -s -X POST http://localhost:8000/api/auth/refresh \
  -H "Authorization: ******" | jq .
```

---

## RAG Operations

### Get RAG System Metrics

```bash
curl -s http://localhost:8001/rag/metrics | jq .
```

### List All Indices

```bash
curl -s http://localhost:8001/rag/indices | jq .
```

### Build a RAG Index

```bash
curl -X POST http://localhost:8001/rag/build \
  -H "Content-Type: application/json" \
  -d '{
    "index_name": "my_knowledge_base",
    "documents": [
      {
        "id": "doc_001",
        "content": "Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
        "metadata": {"source": "ai_guide.txt", "category": "ML"}
      },
      {
        "id": "doc_002",
        "content": "Deep learning uses neural networks with multiple layers to process complex patterns.",
        "metadata": {"source": "dl_guide.txt", "category": "DL"}
      },
      {
        "id": "doc_003",
        "content": "Natural language processing enables computers to understand and generate human language.",
        "metadata": {"source": "nlp_guide.txt", "category": "NLP"}
      }
    ]
  }'
```

### Query RAG Index

```bash
# Basic query
curl -X POST http://localhost:8001/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "index_name": "my_knowledge_base",
    "query": "What is machine learning?",
    "top_k": 5
  }'

# Pretty printed
curl -s -X POST http://localhost:8001/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "index_name": "my_knowledge_base",
    "query": "neural networks",
    "top_k": 10,
    "threshold": 0.5
  }' | jq .
```

### Get Index Statistics

```bash
curl -s http://localhost:8001/rag/stats/my_knowledge_base | jq .
```

### Extract Results from Query Response

```bash
curl -s -X POST http://localhost:8001/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "index_name": "my_knowledge_base",
    "query": "deep learning",
    "top_k": 3
  }' | jq '.results[] | {doc_id: .document_id, score: .score, content: .content}'
```

### Delete Index

```bash
curl -X DELETE http://localhost:8001/rag/indices/my_knowledge_base
```

### Merge Multiple Indices

```bash
curl -X POST http://localhost:8001/rag/merge \
  -H "Content-Type: application/json" \
  -d '{
    "source_indices": ["index1", "index2", "index3"],
    "target_index": "combined_index"
  }'
```

---

## Advanced Scenarios

### Full RAG Workflow

```bash
#!/bin/bash

API="http://localhost:8001"

echo "=== Building RAG Index ==="
curl -s -X POST $API/rag/build \
  -H "Content-Type: application/json" \
  -d '{
    "index_name": "workflow_demo",
    "documents": [
      {"id": "1", "content": "Python is a programming language", "metadata": {"lang": "en"}},
      {"id": "2", "content": "JavaScript runs in web browsers", "metadata": {"lang": "en"}},
      {"id": "3", "content": "Rust is a systems programming language", "metadata": {"lang": "en"}}
    ]
  }' | jq .

echo -e "\n=== Listing Indices ==="
curl -s $API/rag/indices | jq '.indices[] | {name, document_count}'

echo -e "\n=== Querying Index ==="
curl -s -X POST $API/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "index_name": "workflow_demo",
    "query": "programming languages",
    "top_k": 2
  }' | jq '.results[] | {id: .document_id, score, content}'

echo -e "\n=== Getting Statistics ==="
curl -s $API/rag/stats/workflow_demo | jq .

echo -e "\n=== Cleaning Up ==="
curl -s -X DELETE $API/rag/indices/workflow_demo | jq .
```

### Batch Document Processing

```bash
#!/bin/bash

# Process multiple documents from a file
DOCS_FILE="documents.jsonl"  # One JSON object per line

INDEX_NAME="batch_index"

# Build index from JSONL file
echo "Building index from documents..."

DOCUMENTS="["
while IFS= read -r line; do
  DOCUMENTS+="$line,"
done < "$DOCS_FILE"
DOCUMENTS="${DOCUMENTS%,}]"  # Remove trailing comma

curl -X POST http://localhost:8001/rag/build \
  -H "Content-Type: application/json" \
  -d "{
    \"index_name\": \"$INDEX_NAME\",
    \"documents\": $DOCUMENTS
  }"
```

### Rate Limit Monitoring

```bash
#!/bin/bash

# Check rate limit headers
RESPONSE=$(curl -s -i http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test"}')

echo "Rate Limit Info:"
echo "$RESPONSE" | grep -i "x-ratelimit"

# Extract remaining requests
REMAINING=$(echo "$RESPONSE" | grep "X-RateLimit-Remaining" | awk '{print $2}')
echo "Requests remaining: $REMAINING"
```

### Multiple Concurrent Queries

```bash
#!/bin/bash

# Run multiple queries in parallel
QUERIES=("machine learning" "deep learning" "neural networks" "data science")

for query in "${QUERIES[@]}"; do
  {
    curl -s -X POST http://localhost:8001/rag/query \
      -H "Content-Type: application/json" \
      -d "{
        \"index_name\": \"my_knowledge_base\",
        \"query\": \"$query\",
        \"top_k\": 3
      }" | jq ".query, .total_results"
  } &
done

wait
```

---

## Error Handling

### Handle 400 Bad Request

```bash
# Missing required field
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{}' # Missing "prompt"

# Response:
# {"detail":"field required","status_code":400}
```

### Handle 401 Unauthorized

```bash
# Invalid token
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: ******"

# Response:
# {"detail":"Invalid authentication credentials","status_code":401}
```

### Handle 404 Not Found

```bash
# Non-existent index
curl http://localhost:8001/rag/stats/nonexistent_index

# Response:
# {"detail":"Index not found","status_code":404}
```

### Handle 429 Rate Limit

```bash
#!/bin/bash

# Retry with exponential backoff
MAX_RETRIES=3
RETRY_DELAY=1

for ((attempt=1; attempt<=MAX_RETRIES; attempt++)); do
  RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/predict \
    -H "Content-Type: application/json" \
    -d '{"prompt": "test"}')
  
  HTTP_CODE=$(echo "$RESPONSE" | tail -1)
  BODY=$(echo "$RESPONSE" | head -1)
  
  if [ "$HTTP_CODE" = "200" ]; then
    echo "Success!"
    echo "$BODY" | jq .
    break
  elif [ "$HTTP_CODE" = "429" ]; then
    echo "Rate limited. Waiting ${RETRY_DELAY}s before retry ${attempt}/${MAX_RETRIES}..."
    sleep $RETRY_DELAY
    RETRY_DELAY=$((RETRY_DELAY * 2))
  else
    echo "Error: HTTP $HTTP_CODE"
    echo "$BODY"
    break
  fi
done
```

### Comprehensive Error Handler

```bash
#!/bin/bash

function api_call() {
  local method=$1
  local endpoint=$2
  local data=$3
  
  RESPONSE=$(curl -s -w "\n%{http_code}" -X "$method" "http://localhost:8000$endpoint" \
    -H "Content-Type: application/json" \
    ${data:+-d "$data"})
  
  HTTP_CODE=$(echo "$RESPONSE" | tail -1)
  BODY=$(echo "$RESPONSE" | head -1)
  
  case $HTTP_CODE in
    200|201)
      echo "$BODY"
      return 0
      ;;
    400)
      echo "Error: Bad Request - $BODY" >&2
      return 1
      ;;
    401)
      echo "Error: Unauthorized - $BODY" >&2
      return 1
      ;;
    404)
      echo "Error: Not Found - $BODY" >&2
      return 1
      ;;
    429)
      echo "Error: Rate Limit Exceeded" >&2
      return 2
      ;;
    *)
      echo "Error: HTTP $HTTP_CODE - $BODY" >&2
      return 1
      ;;
  esac
}

# Usage
api_call POST "/predict" '{"prompt": "test"}'
```

---

## Tips & Tricks

### Use Environment Variables

```bash
export API_HOST="http://localhost:8000"
export RAG_API="http://localhost:8001"
export AUTH_TOKEN=""

# Save token
AUTH_TOKEN=$(curl -s -X POST $API_HOST/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "pass"}' | jq -r '.access_token')

# Use in requests
curl -X POST $API_HOST/predict \
  -H "Authorization: ******" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test"}'
```

### Pretty Print JSON Responses

```bash
# Install jq if not present
sudo apt-get install jq

# Use with curl
curl -s http://localhost:8000/health | jq .

# Format specific field
curl -s -X POST http://localhost:8001/rag/query \
  -H "Content-Type: application/json" \
  -d '{"index_name": "test", "query": "ml"}' | jq '.results[] | {id: .document_id, score}'
```

### Debug Requests

```bash
# Verbose output with headers
curl -v http://localhost:8000/health

# Show only headers
curl -i http://localhost:8000/health

# Debug certificate issues
curl -k https://api.example.com/health

# Custom headers
curl -H "X-Custom-Header: value" http://localhost:8000/health
```

---

**Last Updated: 2026-07-08
