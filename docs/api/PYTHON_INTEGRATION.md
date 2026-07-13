# Python Integration Guide
**Last Updated:** 2026-07-11
**Version:** v0.2.1

Complete guide for integrating the Codex API with Python using the `requests` library.

## Installation

```bash
# Install required packages
pip install requests pydantic
```

## Table of Contents

1. [Basic Setup](#basic-setup)
2. [Text Generation](#text-generation)
3. [Authentication](#authentication)
4. [RAG Operations](#rag-operations)
5. [Advanced Patterns](#advanced-patterns)
6. [Error Handling](#error-handling)
7. [Complete Examples](#complete-examples)

---

## Basic Setup

### Client Configuration

```python
import requests
from typing import Optional, Dict, Any

class CodexAPIClient:
    def __init__(self, 
                 api_url: str = "http://localhost:8000",
                 rag_url: str = "http://localhost:8001",
                 timeout: int = 30):
        self.api_url = api_url
        self.rag_url = rag_url
        self.timeout = timeout
        self.session = requests.Session()
        self.token: Optional[str] = None
    
    def set_token(self, token: str):
        """Set JWT token for authenticated requests"""
        self.token = token
        self.session.headers.update({
            "Authorization": f"******"
        })
    
    def _make_request(self, 
                      method: str,
                      url: str,
                      **kwargs) -> requests.Response:
        """Make HTTP request with error handling"""
        response = self.session.request(method, url, timeout=self.timeout, **kwargs)
        response.raise_for_status()
        return response

# Usage
client = CodexAPIClient()
```

---

## Text Generation

### Simple Prediction

```python
def predict(client: CodexAPIClient, prompt: str) -> str:
    """Generate text prediction"""
    url = f"{client.api_url}/predict"
    response = client._make_request(
        "POST",
        url,
        json={"prompt": prompt}
    )
    return response.json()["output"]

# Usage
result = predict(client, "What is machine learning?")
print(result)
```

### Batch Predictions

```python
def batch_predict(client: CodexAPIClient, 
                 prompts: list[str]) -> list[str]:
    """Generate predictions for multiple prompts"""
    results = []
    for prompt in prompts:
        try:
            result = predict(client, prompt)
            results.append(result)
        except requests.exceptions.HTTPError as e:
            print(f"Error processing '{prompt}': {e}")
            results.append(None)
    return results

# Usage
prompts = [
    "What is AI?",
    "Explain machine learning",
    "What are neural networks?"
]
results = batch_predict(client, prompts)
for prompt, result in zip(prompts, results):
    print(f"Q: {prompt}")
    print(f"A: {result}\n")
```

---

## Authentication

### Register User

```python
def register(client: CodexAPIClient,
            email: str,
            password: str,
            name: str) -> Dict[str, Any]:
    """Register a new user"""
    url = f"{client.api_url}/api/auth/register"
    response = client._make_request(
        "POST",
        url,
        json={
            "email": email,
            "password": password,
            "name": name
        }
    )
    return response.json()

# Usage
user = register(
    client,
    "newuser@example.com",
    "SecurePass123!",
    "John Doe"
)
print(f"Registered: {user['user_id']}")
```

### Login

```python
def login(client: CodexAPIClient,
         email: str,
         password: str) -> str:
    """Authenticate user and return access token"""
    url = f"{client.api_url}/api/auth/login"
    response = client._make_request(
        "POST",
        url,
        json={"email": email, "password": password}
    )
    data = response.json()
    token = data["access_token"]
    client.set_token(token)
    return token

# Usage
token = login(client, "user@example.com", "SecurePass123!")
print(f"Token: {token[:20]}...")
```

### Token Management

```python
def refresh_token(client: CodexAPIClient) -> str:
    """Refresh existing token"""
    url = f"{client.api_url}/api/auth/refresh"
    response = client._make_request("POST", url)
    data = response.json()
    new_token = data["access_token"]
    client.set_token(new_token)
    return new_token

def logout(client: CodexAPIClient):
    """Logout user"""
    url = f"{client.api_url}/api/auth/logout"
    client._make_request("POST", url)
    client.token = None
    del client.session.headers["Authorization"]

# Usage
new_token = refresh_token(client)
logout(client)
```

---

## RAG Operations

### Build Index

```python
def build_rag_index(client: CodexAPIClient,
                   index_name: str,
                   documents: list[Dict[str, Any]]) -> Dict[str, Any]:
    """Build a RAG index from documents"""
    url = f"{client.rag_url}/rag/build"
    response = client._make_request(
        "POST",
        url,
        json={
            "index_name": index_name,
            "documents": documents
        }
    )
    return response.json()

# Usage
documents = [
    {
        "id": "doc_001",
        "content": "Machine learning is a subset of AI...",
        "metadata": {"source": "guide.txt"}
    },
    {
        "id": "doc_002",
        "content": "Neural networks are inspired by brains...",
        "metadata": {"source": "guide.txt"}
    }
]

result = build_rag_index(client, "my_knowledge_base", documents)
print(f"Built index with {result['document_count']} documents")
```

### Query Index

```python
def query_rag_index(client: CodexAPIClient,
                   index_name: str,
                   query: str,
                   top_k: int = 5,
                   threshold: float = 0.0) -> Dict[str, Any]:
    """Query a RAG index"""
    url = f"{client.rag_url}/rag/query"
    response = client._make_request(
        "POST",
        url,
        json={
            "index_name": index_name,
            "query": query,
            "top_k": top_k,
            "threshold": threshold
        }
    )
    return response.json()

# Usage
results = query_rag_index(client, "my_knowledge_base", "machine learning", top_k=3)
for result in results["results"]:
    print(f"Score: {result['score']:.2f}")
    print(f"Content: {result['content'][:100]}...")
    print()
```

### List & Manage Indices

```python
def list_indices(client: CodexAPIClient) -> list[Dict[str, Any]]:
    """List all available indices"""
    url = f"{client.rag_url}/rag/indices"
    response = client._make_request("GET", url)
    return response.json()["indices"]

def get_index_stats(client: CodexAPIClient,
                   index_name: str) -> Dict[str, Any]:
    """Get statistics for an index"""
    url = f"{client.rag_url}/rag/stats/{index_name}"
    response = client._make_request("GET", url)
    return response.json()

def delete_index(client: CodexAPIClient,
                index_name: str) -> Dict[str, Any]:
    """Delete an index"""
    url = f"{client.rag_url}/rag/indices/{index_name}"
    response = client._make_request("DELETE", url)
    return response.json()

# Usage
indices = list_indices(client)
for index in indices:
    print(f"{index['name']}: {index['document_count']} docs")

stats = get_index_stats(client, "my_knowledge_base")
print(f"Vocabulary size: {stats['vocabulary_size']}")
```

---

## Advanced Patterns

### Pydantic Models for Type Safety

```python
from pydantic import BaseModel, Field
from typing import Optional

class PredictRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2048)

class PredictResponse(BaseModel):
    output: str

class Document(BaseModel):
    id: str
    content: str
    metadata: Optional[Dict[str, str]] = None

class QueryRequest(BaseModel):
    index_name: str
    query: str = Field(..., min_length=1, max_length=1024)
    top_k: int = Field(default=5, ge=1, le=100)
    threshold: float = Field(default=0.0, ge=0.0, le=1.0)

class QueryResult(BaseModel):
    document_id: str
    content: str
    score: float
    metadata: Optional[Dict[str, str]]

# Type-safe client methods
def predict_typed(client: CodexAPIClient, req: PredictRequest) -> PredictResponse:
    req.validate()  # Validate before sending
    url = f"{client.api_url}/predict"
    response = client._make_request("POST", url, json=req.dict())
    return PredictResponse(**response.json())
```

### Session Management with Context Manager

```python
from contextlib import contextmanager

class AuthenticatedSession:
    def __init__(self, client: CodexAPIClient, email: str, password: str):
        self.client = client
        self.email = email
        self.password = password
    
    def __enter__(self):
        login(self.client, self.email, self.password)
        return self.client
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        logout(self.client)

# Usage
with AuthenticatedSession(client, "user@example.com", "pass") as auth_client:
    # Protected operations
    result = predict(auth_client, "test")
    print(result)
# Auto logout after context
```

### Retry Logic with Exponential Backoff

```python
import time
from functools import wraps

def retry_with_backoff(max_attempts: int = 3, base_delay: float = 1.0):
    """Decorator for retrying failed requests"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code in [429, 503]:
                        delay = base_delay * (2 ** attempt)
                        print(f"Retrying in {delay}s... (attempt {attempt + 1}/{max_attempts})")
                        time.sleep(delay)
                    else:
                        raise
            raise Exception(f"Failed after {max_attempts} attempts")
        return wrapper
    return decorator

@retry_with_backoff(max_attempts=3)
def predict_with_retry(client: CodexAPIClient, prompt: str) -> str:
    return predict(client, prompt)

# Usage
result = predict_with_retry(client, "test")
```

### Batch Processing with Progress

```python
from tqdm import tqdm

def batch_process_documents(client: CodexAPIClient,
                           index_name: str,
                           documents: list[Dict],
                           batch_size: int = 100) -> bool:
    """Process documents in batches"""
    for i in tqdm(range(0, len(documents), batch_size), 
                  desc="Processing documents"):
        batch = documents[i:i + batch_size]
        try:
            build_rag_index(client, f"{index_name}_batch_{i}", batch)
        except Exception as e:
            print(f"Error processing batch {i}: {e}")
            return False
    return True

# Usage
import json
with open("large_dataset.jsonl") as f:
    docs = [json.loads(line) for line in f]
success = batch_process_documents(client, "large_index", docs)
```

---

## Error Handling

### Custom Exception Classes

```python
class CodexAPIError(Exception):
    """Base exception for Codex API errors"""
    pass

class ValidationError(CodexAPIError):
    """Validation error (422)"""
    pass

class AuthenticationError(CodexAPIError):
    """Authentication error (401)"""
    pass

class RateLimitError(CodexAPIError):
    """Rate limit exceeded (429)"""
    pass

class NotFoundError(CodexAPIError):
    """Resource not found (404)"""
    pass

def handle_api_error(response: requests.Response):
    """Convert HTTP errors to custom exceptions"""
    error_data = response.json()
    status = response.status_code
    
    if status == 422:
        raise ValidationError(error_data.get("detail", "Validation failed"))
    elif status == 401:
        raise AuthenticationError(error_data.get("detail", "Unauthorized"))
    elif status == 429:
        raise RateLimitError(error_data.get("detail", "Rate limited"))
    elif status == 404:
        raise NotFoundError(error_data.get("detail", "Not found"))
    else:
        raise CodexAPIError(f"HTTP {status}: {error_data.get('detail')}")

# Update client to use this
class CodexAPIClient:
    # ... existing code ...
    
    def _make_request(self, method: str, url: str, **kwargs):
        response = self.session.request(method, url, timeout=self.timeout, **kwargs)
        if not response.ok:
            handle_api_error(response)
        return response
```

### Try-Except Patterns

```python
def safe_predict(client: CodexAPIClient, prompt: str) -> Optional[str]:
    """Safely predict with error handling"""
    try:
        return predict(client, prompt)
    except ValidationError as e:
        print(f"Invalid prompt: {e}")
        return None
    except RateLimitError as e:
        print(f"Rate limited. Waiting and retrying...")
        time.sleep(5)
        return predict(client, prompt)
    except AuthenticationError:
        print("Session expired. Please re-authenticate")
        return None
    except CodexAPIError as e:
        print(f"API error: {e}")
        return None

# Usage
result = safe_predict(client, "test")
```

---

## Complete Examples

### Example 1: Full Authentication Workflow

```python
def auth_workflow_example():
    client = CodexAPIClient()
    
    try:
        # Register
        print("Registering new user...")
        user = register(client, "demo@example.com", "DemoPass123!", "Demo User")
        print(f"Registered: {user['user_id']}")
        
        # Login
        print("\nLogging in...")
        token = login(client, "demo@example.com", "DemoPass123!")
        print(f"Token obtained: {token[:20]}...")
        
        # Use authenticated endpoint
        print("\nLogout...")
        logout(client)
        print("Logged out successfully")
        
    except CodexAPIError as e:
        print(f"Error: {e}")

# Run
auth_workflow_example()
```

### Example 2: RAG Knowledge Base

```python
def rag_knowledge_base_example():
    client = CodexAPIClient()
    
    try:
        # Sample documents
        documents = [
            {
                "id": "python_intro",
                "content": "Python is a high-level programming language known for readability and simplicity.",
                "metadata": {"category": "programming", "language": "python"}
            },
            {
                "id": "python_advanced",
                "content": "Advanced Python includes decorators, metaclasses, and asynchronous programming.",
                "metadata": {"category": "programming", "language": "python"}
            },
            {
                "id": "javascript_basics",
                "content": "JavaScript is a scripting language primarily used for web development.",
                "metadata": {"category": "programming", "language": "javascript"}
            }
        ]
        
        # Build index
        print("Building knowledge base...")
        result = build_rag_index(client, "programming_kb", documents)
        print(f" Built index with {result['document_count']} documents")
        
        # Query index
        print("\nQuerying knowledge base...")
        queries = ["Python programming", "JavaScript basics"]
        
        for query in queries:
            print(f"\nQ: {query}")
            results = query_rag_index(client, "programming_kb", query, top_k=2)
            for i, result in enumerate(results["results"], 1):
                print(f"  {i}. {result['document_id']} (score: {result['score']:.2f})")
        
        # Get stats
        print("\nIndex statistics:")
        stats = get_index_stats(client, "programming_kb")
        print(f"  Documents: {stats['document_count']}")
        print(f"  Vocabulary: {stats['vocabulary_size']}")
        
    except CodexAPIError as e:
        print(f"Error: {e}")

# Run
rag_knowledge_base_example()
```

### Example 3: Batch Text Generation

```python
def batch_generation_example():
    client = CodexAPIClient()
    
    prompts = [
        "What is artificial intelligence?",
        "Explain machine learning",
        "Describe neural networks",
        "What is deep learning?",
    ]
    
    print("Generating predictions for multiple prompts...\n")
    
    results = batch_predict(client, prompts)
    
    for prompt, prediction in zip(prompts, results):
        if prediction:
            print(f"Q: {prompt}")
            print(f"A: {prediction[:100]}...\n")
        else:
            print(f"Q: {prompt}")
            print(f"A: [ERROR]\n")

# Run
batch_generation_example()
```

---

## Testing

### Unit Tests

```python
import unittest
from unittest.mock import Mock, patch

class TestCodexAPIClient(unittest.TestCase):
    def setUp(self):
        self.client = CodexAPIClient()
    
    @patch('requests.Session.request')
    def test_predict(self, mock_request):
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {"output": "Test output"}
        mock_request.return_value = mock_response
        
        # Test
        result = predict(self.client, "test prompt")
        
        # Assert
        self.assertEqual(result, "Test output")
        mock_request.assert_called_once()

if __name__ == '__main__':
    unittest.main()
```

---

**Last Updated: 2026-07-08
