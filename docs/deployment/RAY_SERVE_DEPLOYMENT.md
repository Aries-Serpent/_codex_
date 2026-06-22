# Ray Serve Deployment Guide

> **Version**: 2.0.0  
> **Last Updated**: 2026-06-20  
> **Scope**: Complete Ray Serve production deployment  
> **Audience**: DevOps, platform engineers, system architects

---

## Quick Start: Deploy in 10 Minutes

```bash
# 1. Install Ray and Serve
pip install "ray[serve]" fastapi pydantic

# 2. Create deployment script (see example below)
cat > ray_deployment.py << 'EOF'
from fastapi import FastAPI
from ray import serve
import asyncio

app = FastAPI()

@serve.deployment
@serve.batch(max_batch_size=100, timeout_s=1)
class Predictor:
    async def predict(self, requests):
        return [{"prediction": len(r)} for r in requests]

# Deploy
serve.start()
serve.run(Predictor.bind())
EOF

# 3. Start deployment
python ray_deployment.py

# 4. Test endpoint
curl http://localhost:8000/predict -X POST -d '{"text": "hello"}'
```

---

## Architecture Overview

### Single-Node Deployment

```
┌────────────────────────────────┐
│       Your Application         │
│  (FastAPI/Flask/Custom)        │
└────────────────┬───────────────┘
                 │
                 ▼
    ┌────────────────────────┐
    │    Ray Head Node       │
    │  ├─ Serve Controller   │
    │  ├─ Autoscaler        │
    │  └─ Dashboard (8265)   │
    └────────────────────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
    ┌────────┐        ┌────────┐
    │ Worker │        │ Worker │
    │  (8 GB)│        │  (8 GB)│
    └────────┘        └────────┘
    [Replicas:2]
```

### Multi-Node Cluster Deployment (Production)

```
┌──────────────────────────────────────────┐
│         Kubernetes Cluster               │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │    Ray Head Pod                  │   │
│  │  ├─ Serve Controller             │   │
│  │  ├─ GCS (state store)            │   │
│  │  └─ Dashboard                    │   │
│  └──────────────────────────────────┘   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │    Ray Worker Pods (N replicas)  │   │
│  │  ├─ Replica 1 (replicated_model) │   │
│  │  ├─ Replica 2 (replicated_model) │   │
│  │  └─ Replica N (replicated_model) │   │
│  └──────────────────────────────────┘   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │    Ingress (Load Balancer)       │   │
│  │  Port: 8000 (API)                │   │
│  └──────────────────────────────────┘   │
└──────────────────────────────────────────┘
```

---

## Deployment Options

### Option 1: Docker Single Container (Development)

**Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
RUN pip install ray[serve] fastapi pydantic uvicorn

# Copy your code
COPY . .

# Expose ports
EXPOSE 8000 8265

# Start Ray and Serve
CMD ["python", "app.py"]
```

**Build and Run:**
```bash
docker build -t codex-ray-serve:latest .
docker run -p 8000:8000 -p 8265:8265 codex-ray-serve:latest
```

## Option 2: Kubernetes Deployment (Production)

**Kubernetes YAML:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ray-serve-config
data:
  app.py: |
    from ray import serve
    from fastapi import FastAPI
    
    app = FastAPI()
    
    @serve.deployment
    class Predictor:
        async def predict(self, request):
            return {"prediction": "ok"}
    
    serve.start()
    serve.run(Predictor.bind())

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ray-head
spec:
  selector:
    matchLabels:
      app: ray-head
  replicas: 1
  template:
    metadata:
      labels:
        app: ray-head
    spec:
      containers:
      - name: ray-head
        image: rayproject/ray:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 6379  # Redis
        - containerPort: 8265  # Dashboard
        - containerPort: 8000  # Serve API
        env:
        - name: RAY_REDIS_PASSWORD
          value: "password"
        resources:
          requests:
            cpu: "2"
            memory: "4Gi"
          limits:
            cpu: "4"
            memory: "8Gi"
        volumeMounts:
        - name: app-config
          mountPath: /app
      volumes:
      - name: app-config
        configMap:
          name: ray-serve-config

---
apiVersion: v1
kind: Service
metadata:
  name: ray-serve
spec:
  selector:
    app: ray-head
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
    name: serve
  - protocol: TCP
    port: 8265
    targetPort: 8265
    name: dashboard
  type: LoadBalancer
```

**Deploy to Kubernetes:**
```bash
kubectl apply -f ray-serve-k8s.yaml
kubectl port-forward svc/ray-serve 8000:8000
```

### Option 3: Ray Cluster (Multi-Node)

**ray_cluster.yaml:**
```yaml
cluster_name: codex-ray-cluster
max_workers: 10
upscaling_speed: 1.0

provider:
  type: kubernetes
  namespace: default
  use_internal_ips: false

auth:
  ssh_user: ubuntu
  ssh_private_key: ~/.ssh/ray_key

available_node_types:
  ray_head:
    min_workers: 1
    max_workers: 1
    resources: {"is_head": 1}
    node_config:
      apiVersion: v1
      kind: Pod
      metadata:
        name: ray-head
      spec:
        containers:
        - name: ray
          image: rayproject/ray:latest
          resources:
            requests:
              cpu: "4"
              memory: "16Gi"
  
  ray_worker:
    min_workers: 2
    max_workers: 8
    node_config:
      apiVersion: v1
      kind: Pod
      metadata:
        name: ray-worker
      spec:
        containers:
        - name: ray
          image: rayproject/ray:latest
          resources:
            requests:
              cpu: "8"
              memory: "32Gi"
```

**Start cluster:**
```bash
ray up ray_cluster.yaml
ray attach ray_cluster.yaml
```

---

## Deployment Code Examples

### Example 1: Simple FastAPI Service

```python
from ray import serve
from fastapi import FastAPI
from pydantic import BaseModel
import logging

app = FastAPI()

class PredictionRequest(BaseModel):
    text: str
    max_tokens: int = 100

@serve.deployment
class TextPredictor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing TextPredictor")

    @app.post("/predict")
    async def predict(self, request: PredictionRequest):
        self.logger.info(f"Predicting for: {request.text[:50]}...")

        # Your prediction logic here
        result = {
            "input": request.text,
            "output": "generated text",
            "tokens_used": 45
        }
        return result

# Deploy
if __name__ == "__main__":
    serve.start()
    handle = serve.run(TextPredictor.bind())
    print("Service started at http://localhost:8000")
```

**Test:**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "max_tokens": 100}'
```

## Example 2: Multi-Model Deployment with Autoscaling

```python
from ray import serve
from fastapi import FastAPI
import asyncio

app = FastAPI()

@serve.deployment(
    num_replicas=2,  # Start with 2 replicas
    max_replicas=10,  # Scale up to 10
    min_replicas=1,   # Scale down to 1
    target_ongoing_requests=5  # Scale when > 5 requests
)
class GPTModel:
    def __init__(self, model_name: str = "gpt2"):
        from transformers import AutoTokenizer, AutoModelForCausalLM

        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)

    @app.post("/generate")
    async def generate(self, prompt: str, max_tokens: int = 50):
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_length=max_tokens)
        text = self.tokenizer.decode(outputs[0])
        return {"generated_text": text}

@serve.deployment(
    num_replicas=1,
    max_replicas=5
)
class EmbeddingModel:
    def __init__(self):
        from transformers import AutoTokenizer, AutoModel

        self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

    @app.post("/embed")
    async def embed(self, text: str):
        inputs = self.tokenizer(text, return_tensors="pt")
        outputs = self.model(**inputs)
        embedding = outputs.last_hidden_state[0][0].tolist()
        return {"embedding": embedding}

# Deploy both models
if __name__ == "__main__":
    serve.start()

    gpt_handle = serve.run(GPTModel.bind())
    embed_handle = serve.run(EmbeddingModel.bind())

    print("✅ GPT Model deployed at /generate")
    print("✅ Embedding Model deployed at /embed")
    print("✅ Dashboard: http://localhost:8265")
```

## Example 3: Batch Processing

```python
from ray import serve
from fastapi import FastAPI
import time

app = FastAPI()

@serve.deployment
@serve.batch(max_batch_size=32, timeout_s=2)
class BatchPredictor:
    async def __call__(self, requests):
        # Batch process all requests together
        results = []
        for request in requests:
            # Simulate processing
            result = {
                "input": request["text"],
                "output": f"processed_{request['text']}"
            }
            results.append(result)

        return results

@app.post("/batch-predict")
async def predict(request: dict):
    return await BatchPredictor.remote(request)

if __name__ == "__main__":
    serve.start()
    serve.run(BatchPredictor.bind())
```

---

## Monitoring & Observability

### View Ray Dashboard

```bash
# Automatically opens: http://localhost:8265
ray dashboard

# Or access in browser: http://localhost:8265
```

## Monitor Metrics

```python
from ray import serve

# Get serve status
info = serve.status()
print(f"Running deployments: {info.deployments}")

# Get deployment details
deployment_status = serve.get_deployment("TextPredictor").get_status()
print(f"Replicas: {deployment_status.replica_states}")

# View metrics
metrics = serve.get_deployment("TextPredictor").list_replicas()
for replica in metrics:
    print(f"Replica {replica.id}: {replica.state}")
```

## Logging

```python
import logging

logger = logging.getLogger("ray.serve")
logger.setLevel(logging.DEBUG)

# In your deployment
@serve.deployment
class MyModel:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def __call__(self, request):
        self.logger.info(f"Processing request: {request}")
        return {"status": "ok"}
```

---

## Performance Optimization

### Batch Requests

```python
@serve.batch(max_batch_size=64, timeout_s=1)
async def predict_batch(requests):
    # Vectorized processing is more efficient
    return [process(r) for r in requests]
```

### Resource Allocation

```python
@serve.deployment(
    ray_actor_options={
        "num_cpus": 2,
        "num_gpus": 1,
        "memory": 1_000_000_000  # 1 GB
    }
)
class GPUModel:
    pass
```

### Autoscaling Configuration

```python
@serve.deployment(
    num_replicas=2,
    max_replicas=10,
    target_ongoing_requests=5  # Scale when exceeding 5 concurrent
)
class Model:
    pass
```

---

## Troubleshooting

### Issue: "Deployment failed to start"

**Solutions:**
1. Check logs: `ray logs deployment <deployment_name>`
2. Verify import statements
3. Check resource availability

### Issue: "High latency in requests"

**Solutions:**
1. Increase replicas: `max_replicas=10`
2. Enable batching for throughput
3. Check CPU/GPU utilization in dashboard
4. Profile with: `serve.get_deployment_handle("Model").remote()`

### Issue: "Out of memory errors"

**Solutions:**
1. Reduce `num_replicas`
2. Lower `max_batch_size`
3. Allocate more ray worker memory
4. Enable model quantization

---

## Production Checklist

- [ ] Ray cluster configured for your infrastructure
- [ ] All deployments have resource limits set
- [ ] Autoscaling policies defined (min/max replicas)
- [ ] Monitoring and alerting configured
- [ ] Log aggregation set up (CloudWatch, ELK, etc.)
- [ ] Health checks configured
- [ ] Load balancing verified
- [ ] Backup and disaster recovery plan
- [ ] Security: API keys, TLS configured
- [ ] Performance baselines established

---

## Next Steps

- 🔗 [Ray Serve Documentation](https://docs.ray.io/en/latest/serve/index.html)
- 🔗 [Performance Tuning](../performance.md)

**Additional guides for Kubernetes integration and monitoring are planned for future implementation.**

---

**Last Updated:** 2026-06-20 | **Version:** 2.0.0
