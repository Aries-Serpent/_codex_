# Integration Examples

**Version:** 0.1.0  
**Last Updated:** 2026-07-09  
**Audience:** Developers, Integration Engineers

---

## Table of Contents

1. [Cognitive Brain Scoring](#cognitive-brain-scoring)
2. [ML Fine-Tuning](#ml-fine-tuning)
3. [Inference Pipeline](#inference-pipeline)
4. [API Integration](#api-integration)
5. [Kubernetes Integration](#kubernetes-integration)

---

## Cognitive Brain Scoring

**Use case:** Score decisions for deployment automation

```python
from codex.cognitive_brain import IntelligenceScorer

# Initialize scorer
scorer = IntelligenceScorer()

# Define decision
decision = {
    "action": "deploy",
    "environment": "production",
    "confidence": 0.95,
    "risk_level": "low"
}

# Score the decision
score = scorer.score_decision(decision)
print(f"Intelligence Score: {score}")
# Output: 0.85-0.95 range

# Threshold-based action
if score > 0.8:
    print("✅ APPROVED: Deploy to production")
else:
    print("⏸️ HOLD: Review decision before deploying")
```

---

## ML Fine-Tuning

**Use case:** Fine-tune model on domain-specific data

```python
from codex.ml import TrainerFactory
from codex.core import Hydra

# Load configuration
cfg = Hydra.load_config("training.yaml")

# Create trainer
trainer = TrainerFactory.create("bert", cfg)

# Prepare data
train_data = load_data("data/train.csv")
eval_data = load_data("data/eval.csv")

# Fine-tune model
metrics = trainer.fine_tune(train_data, eval_data)

# Evaluate results
print(f"Final Accuracy: {metrics['accuracy']:.2%}")
print(f"Final F1: {metrics['f1']:.2%}")

# Save fine-tuned model
trainer.save_model("models/finetuned-bert")
```

---

## Inference Pipeline

**Use case:** Run inference on batches of text

```python
from codex.ml import InferencePipeline

# Create pipeline
pipeline = InferencePipeline("bert-base-uncased")

# Prepare texts
texts = [
    "This movie is great!",
    "I didn't like it.",
    "Absolutely fantastic!"
]

# Run inference
predictions = pipeline(texts, batch_size=32)

# Process results
for text, pred in zip(texts, predictions):
    print(f"Text: {text}")
    print(f"Prediction: {pred.label} (confidence: {pred.score:.2%})")
    print()
```

---

## API Integration

**Use case:** Call Codex API from external application

### cURL Example

```bash
# Health check
curl http://localhost:8000/health

# Score endpoint
curl -X POST http://localhost:8000/api/score \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "action": "deploy",
      "environment": "production"
    }
  }'

# Response
{
  "score": 0.89,
  "confidence": 0.95,
  "recommendation": "approve"
}
```

### Python Requests Example

```python
import requests
import json

# API endpoint
url = "http://localhost:8000/api/score"

# Request payload
payload = {
    "data": {
        "action": "deploy",
        "environment": "production",
        "risk_level": "low"
    }
}

# Make request
response = requests.post(url, json=payload)

# Handle response
if response.status_code == 200:
    result = response.json()
    print(f"Score: {result['score']}")
    print(f"Recommendation: {result['recommendation']}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

async function scoreDecision(data) {
  try {
    const response = await axios.post('http://localhost:8000/api/score', {
      data: data
    });
    return response.data;
  } catch (error) {
    console.error('Error:', error.message);
    throw error;
  }
}

// Usage
scoreDecision({
  action: 'deploy',
  environment: 'production'
}).then(result => {
  console.log(`Score: ${result.score}`);
  console.log(`Recommendation: ${result.recommendation}`);
});
```

---

## Kubernetes Integration

**Use case:** Deploy and call Codex in Kubernetes cluster

### Port-Forward Method

```bash
# Port-forward service
kubectl port-forward svc/codex-api-service 8000:8000 -n codex

# In another terminal, call API
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/score -d '{...}'
```

### In-Cluster Service Discovery

```python
import requests

# Use Kubernetes service DNS
url = "http://codex-api-service.codex.svc.cluster.local:8000/api/score"

response = requests.post(url, json={
    "data": {
        "action": "deploy"
    }
})

print(response.json())
```

### Client Pod Integration

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: client-pod
spec:
  containers:
  - name: client
    image: python:3.12
    command:
    - /bin/sh
    - -c
    - |
      pip install requests
      python -c "
      import requests
      url = 'http://codex-api-service:8000/api/score'
      result = requests.post(url, json={'data': {'action': 'deploy'}})
      print(result.json())
      "
```

---

## Error Handling

All examples should include error handling:

```python
import requests
from requests.exceptions import Timeout, ConnectionError

try:
    response = requests.post(
        'http://localhost:8000/api/score',
        json={'data': {...}},
        timeout=10
    )
    response.raise_for_status()
    result = response.json()
except Timeout:
    print("Request timeout - service may be overloaded")
except ConnectionError:
    print("Cannot reach service - check network/deployment")
except requests.HTTPError as e:
    print(f"HTTP error: {e.response.status_code}")
    print(e.response.json())
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

**Last Updated:** 2026-07-09  
**GitHub:** [Issues](https://github.com/Aries-Serpent/_codex_/issues)
