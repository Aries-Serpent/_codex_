# Getting Started Guide for API Consumers

**Last Updated:** 2026-07-08  
**Target Audience:** Backend developers, API integrators, SDK users, third-party developers  
**Estimated Time:** 10-15 minutes to first API call

## 🎯 Your Goal

Integrate Codex ML into your applications via REST APIs, Python SDK, or client libraries. This guide covers authentication, rate limiting, error handling, and common API patterns.

---

## Phase 1: API Access Setup (5 minutes)

### Step 1: Get API Credentials

```bash
# Option A: Via Web Dashboard
# Visit: https://codex-ml.dev/dashboard/api-keys
# Generate a new API key with:
# - Name: "My App Integration"
# - Permissions: ["predict:read", "model:list"]
# - Rate limit: "100 requests/minute"
# Copy your API key (save securely!)

# Option B: Via CLI
codex auth login  # Opens browser for OAuth2 flow
codex api-key create \
  --name "My App Integration" \
  --scopes predict:read,model:list \
  --rate-limit "100/minute"
```

### Step 2: Store Credentials Securely

**Python (.env file):**

```bash
# .env
CODEX_API_KEY=sk-proj-abc123...xyz
CODEX_API_BASE=https://api.codex-ml.dev/v1
```

**Environment Variables:**

```bash
export CODEX_API_KEY=sk-proj-abc123...xyz
export CODEX_API_BASE=https://api.codex-ml.dev/v1
```

**Secrets Manager (Production):**

```python
# Use AWS Secrets Manager, Azure Key Vault, etc.
import boto3

client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='codex/api-key')
api_key = secret['SecretString']
```

---

## Phase 2: Python SDK (Recommended)

### Install SDK

```bash
pip install codex-ml
```

### First API Call

```python
from codex_ml import CodexML
from codex_ml.models import PredictionRequest

# Initialize client
client = CodexML(
    api_key="sk-proj-abc123...xyz",
    api_base="https://api.codex-ml.dev/v1"
)

# Single prediction
request = PredictionRequest(
    model_id="sentiment-classifier",
    model_version="1.0.0",
    inputs={
        "text": "This product is amazing!"
    }
)

response = client.predict(request)
print(f"Prediction: {response.output['label']}")
print(f"Confidence: {response.output['confidence']:.2%}")
```

### Batch Predictions

```python
# Batch predict with up to 1000 samples per request
batch_request = PredictionRequest(
    model_id="sentiment-classifier",
    model_version="1.0.0",
    inputs=[
        {"text": "This is great!"},
        {"text": "This is terrible."},
        {"text": "It's okay."},
    ]
)

batch_response = client.predict_batch(batch_request)
for prediction in batch_response.outputs:
    print(f"Label: {prediction['label']}")
```

### Async Predictions (for long-running tasks)

```python
import asyncio
from codex_ml import AsyncCodexML

async def main():
    async with AsyncCodexML(api_key="sk-proj-...") as client:
        # Submit async job
        job = await client.predict_async(
            model_id="sentiment-classifier",
            inputs={"text": "Long text..."}
        )
        print(f"Job ID: {job.job_id}")
        
        # Poll for results
        result = await job.wait()
        print(f"Result: {result}")

asyncio.run(main())
```

### Error Handling

```python
from codex_ml import CodexML, CodexMLError, RateLimitError, ModelNotFoundError

client = CodexML(api_key="sk-proj-...")

try:
    response = client.predict({
        "model_id": "sentiment-classifier",
        "inputs": {"text": "..."}
    })
except RateLimitError as e:
    # Handle rate limiting - implement backoff
    print(f"Rate limited. Retry after {e.retry_after_seconds}s")
    time.sleep(e.retry_after_seconds)
    response = client.predict(...)
except ModelNotFoundError as e:
    print(f"Model not found: {e.model_id}")
except CodexMLError as e:
    print(f"API error: {e.message}")
    print(f"Error code: {e.error_code}")
    print(f"Request ID: {e.request_id}")
```

---

## Phase 3: REST API Directly

### HTTP Client Setup

**Using requests library:**

```python
import requests
import json

BASE_URL = "https://api.codex-ml.dev/v1"
API_KEY = "sk-proj-abc123...xyz"

headers = {
    "Authorization": f"******",
    "Content-Type": "application/json",
}

def predict(model_id, text):
    response = requests.post(
        f"{BASE_URL}/predict",
        headers=headers,
        json={
            "model_id": model_id,
            "model_version": "latest",
            "inputs": {"text": text}
        }
    )
    response.raise_for_status()
    return response.json()

# Usage
result = predict("sentiment-classifier", "This is great!")
print(result)
```

**Using curl (command line):**

```bash
curl -X POST https://api.codex-ml.dev/v1/predict \
  -H "Authorization: ******" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "sentiment-classifier",
    "model_version": "latest",
    "inputs": {
      "text": "This is great!"
    }
  }'
```

### API Endpoints

**List Models**

```bash
GET /v1/models
Authorization: ******
```

Response:
```json
{
  "models": [
    {
      "id": "sentiment-classifier",
      "name": "Sentiment Classifier",
      "versions": ["1.0.0", "1.0.1"],
      "latest_version": "1.0.1",
      "task": "text-classification",
      "inputs": {
        "text": {"type": "string", "description": "Input text"}
      },
      "outputs": {
        "label": {"type": "string", "values": ["positive", "negative", "neutral"]},
        "confidence": {"type": "float"}
      }
    }
  ]
}
```

**Get Model Details**

```bash
GET /v1/models/{model_id}/versions/{version}
Authorization: ******
```

**Make Prediction**

```bash
POST /v1/predict
Authorization: ******
Content-Type: application/json

{
  "model_id": "sentiment-classifier",
  "model_version": "1.0.1",
  "inputs": {
    "text": "This is great!"
  },
  "return_confidence": true,
  "timeout_seconds": 30
}
```

Response:
```json
{
  "prediction_id": "pred-uuid-123",
  "model_id": "sentiment-classifier",
  "model_version": "1.0.1",
  "outputs": {
    "label": "positive",
    "confidence": 0.95
  },
  "latency_ms": 45,
  "timestamp": "2026-07-08T05:44:23Z"
}
```

---

## Phase 4: Advanced Features

### Streaming Responses

```python
# For large outputs or real-time updates
from codex_ml import CodexML

client = CodexML(api_key="sk-proj-...")

with client.predict_stream(
    model_id="text-generator",
    inputs={"prompt": "Once upon a time..."}
) as stream:
    for chunk in stream:
        print(chunk.text, end='', flush=True)
```

### Custom Headers & Metadata

```python
client = CodexML(api_key="sk-proj-...")

response = client.predict(
    model_id="sentiment-classifier",
    inputs={"text": "..."},
    # Custom headers
    headers={
        "X-User-ID": "user123",
        "X-Request-ID": "req-uuid",
        "X-Custom-Header": "value"
    },
    # Metadata (logged for debugging)
    metadata={
        "environment": "production",
        "version": "1.2.3",
        "source": "my-app"
    }
)

# Access request ID for debugging
print(f"Request ID: {response.request_id}")
```

### Caching for Repeated Requests

```python
from codex_ml import CodexML
from codex_ml.caching import RequestCache

# Enable local caching
cache = RequestCache(ttl_seconds=3600)
client = CodexML(
    api_key="sk-proj-...",
    cache=cache
)

# First call: hits API
result1 = client.predict({"model_id": "...", "inputs": {"text": "hello"}})

# Second call: served from cache (0ms latency)
result2 = client.predict({"model_id": "...", "inputs": {"text": "hello"}})

# Cache stats
print(f"Cache hits: {cache.hits}")
print(f"Cache misses: {cache.misses}")
print(f"Hit rate: {cache.hit_rate:.1%}")
```

### Rate Limiting & Backoff

```python
from codex_ml import CodexML
from codex_ml.ratelimit import ExponentialBackoff

# Automatic exponential backoff on rate limiting
client = CodexML(
    api_key="sk-proj-...",
    retry_strategy=ExponentialBackoff(
        max_retries=3,
        base_delay_seconds=1,
        max_delay_seconds=60
    )
)

# Will automatically retry with backoff on 429 (rate limit)
response = client.predict(...)
```

---

## Phase 5: Troubleshooting

### Common Errors

**401 Unauthorized**
```python
# Check: API key is valid and not expired
# Solution: Regenerate from dashboard or CLI
codex api-key create --name "new-key"
```

**429 Too Many Requests**
```python
# You're hitting rate limits
# Solution: Implement backoff or upgrade plan
import time
time.sleep(60)  # Wait before retrying
```

**422 Validation Error**
```python
# Input format is incorrect
# Solution: Check API schema
models = client.models.list()
schema = models['sentiment-classifier']['inputs']
print(f"Expected inputs: {schema}")
```

**502 Bad Gateway**
```python
# Service temporarily unavailable
# Solution: Implement retry logic
from codex_ml.ratelimit import ExponentialBackoff
client = CodexML(
    api_key="...",
    retry_strategy=ExponentialBackoff(max_retries=5)
)
```

### Debug Mode

```python
import logging
from codex_ml import CodexML

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

client = CodexML(
    api_key="sk-proj-...",
    debug=True  # Logs all requests/responses
)

response = client.predict(...)
# Will print: Request ID, headers, payload, response time, etc.
```

---

## 📚 Documentation

- **Full API Reference**: [API Docs](../api/API_REFERENCE.md)
- **Python SDK Docs**: [SDK Documentation](../api/PYTHON_SDK.md)
- **Examples**: [Code Examples](../examples/)
- **Status Page**: [API Status](https://status.codex-ml.dev)

## 🆘 Getting Help

- **API Questions**: [Discussions](https://github.com/Aries-Serpent/_codex_/discussions?discussions_q=api)
- **Report Bugs**: [Create Issue](https://github.com/Aries-Serpent/_codex_/issues/new?labels=api)
- **Support**: [support@codex-ml.dev](mailto:support@codex-ml.dev)

---

**Happy integrating! 🚀**
