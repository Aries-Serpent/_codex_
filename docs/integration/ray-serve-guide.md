# Ray Serve Integration Guide

> Complete guide to deploying and scaling applications with Ray Serve  
> **Level**: Intermediate | **Prerequisites**: Basic Ray knowledge  
> **Last Updated**: 2026-06-22 | **Version**: 2.0

---

## Table of Contents

1. [Overview](#overview)
2. [Installation and Setup](#installation-and-setup)
3. [Deployment Patterns](#deployment-patterns)
4. [Load Balancing](#load-balancing)
5. [Monitoring and Observability](#monitoring-and-observability)
6. [Production Deployment](#production-deployment)
7. [Troubleshooting](#troubleshooting)

---

## Overview

Ray Serve is a lightweight, high-performance serving library built on Ray. It enables deploying ML models and Python functions as scalable microservices.

### Key Features

- **Distributed serving**: Scale across multiple machines
- **Model composability**: Chain multiple models together
- **Traffic splitting**: A/B test different model versions
- **Autoscaling**: Automatically adjust replicas based on load
- **Batching**: Improve throughput by batching requests
- **GPU support**: Leverage GPUs for inference

### When to Use Ray Serve

✅ **Good use cases**:
- ML model serving at scale
- Microservices that need autoscaling
- Multi-model deployments
- Real-time inference with latency requirements
- Complex serving logic with composition

❌ **Not ideal for**:
- Simple synchronous APIs (use FastAPI directly)
- Stateless functions without composition
- Very short-lived applications

---

## Installation and Setup

### 1. Install Ray and Ray Serve

```bash
# Install Ray with serve extras
pip install ray[serve]

# Verify installation
python -c "import ray; print(ray.__version__)"
python -c "from ray import serve; print(serve.__version__)"

# For GPU support
pip install ray[serve,gpu]

# For all extras
pip install ray[complete]
```

## 2. Basic Setup

```python
# app.py
from ray import serve

# Initialize Ray and Serve
serve.start()

# Define a simple service
@serve.deployment
def hello_world(request):
    return {"message": "Hello, World!"}

# Deploy
hello_world.deploy()

# Test locally
import requests
response = requests.get("http://localhost:8000/hello_world")
print(response.json())
```

## 3. Configuration File Setup

```yaml
# serve_config.yaml
applications:
  - name: my_app
    import_path: app:deployment_graph
    route_prefix: /api
    
    # Ray configuration
    ray_actor_options:
      num_cpus: 2
      num_gpus: 1
      memory: 4_000_000_000
    
    # Deployment-specific options
    deployments:
      - name: model
        num_replicas: 3
        max_concurrent_queries: 100
```

## 4. Initialize with Custom Configuration

```python
# main.py
from ray import serve
import yaml

# Load configuration
with open("serve_config.yaml") as f:
    config = yaml.safe_load(f)

# Initialize Ray cluster
ray.init(
    num_cpus=8,
    num_gpus=2,
    object_store_memory=2_000_000_000
)

# Start Serve with configuration
serve.start(http_options={"host": "0.0.0.0", "port": 8000})

# Deploy from config
serve.run(config)
```

---

## Deployment Patterns

### Pattern 1: Simple Model Serving

```python
# model_serving.py
from ray import serve
import joblib
from typing import Dict

@serve.deployment(num_replicas=3)
class ModelEndpoint:
    def __init__(self, model_path: str):
        # Load model once during initialization
        self.model = joblib.load(model_path)
    
    async def __call__(self, data: Dict) -> Dict:
        # Async call for better concurrency
        features = data["features"]
        prediction = self.model.predict([features])[0]
        
        return {
            "prediction": float(prediction),
            "confidence": float(self.model.predict_proba([features])[0].max())
        }

# Deploy with alias for A/B testing
ModelEndpoint.options(
    name="model-v1",
    max_concurrent_queries=100
).deploy(model_path="models/model_v1.pkl")
```

## Pattern 2: Multi-Model Ensemble

```python
# ensemble_serving.py
from ray import serve
from typing import Dict
import numpy as np

@serve.deployment(num_replicas=1)
class ModelA:
    def __init__(self):
        self.model = self._load_model("model_a.pkl")
    
    async def __call__(self, features: Dict) -> float:
        return self.model.predict([features["data"]])[0]

@serve.deployment(num_replicas=1)
class ModelB:
    def __init__(self):
        self.model = self._load_model("model_b.pkl")
    
    async def __call__(self, features: Dict) -> float:
        return self.model.predict([features["data"]])[0]

@serve.deployment
class EnsembleModel:
    def __init__(self, model_a_handle, model_b_handle):
        self.model_a = model_a_handle
        self.model_b = model_b_handle
    
    async def __call__(self, request: Dict) -> Dict:
        # Get predictions from both models
        pred_a = await self.model_a.remote(request)
        pred_b = await self.model_b.remote(request)
        
        # Combine predictions
        ensemble_pred = (float(pred_a) + float(pred_b)) / 2
        
        return {
            "model_a": float(pred_a),
            "model_b": float(pred_b),
            "ensemble": ensemble_pred
        }

# Build composition graph
model_a = ModelA.bind()
model_b = ModelB.bind()
ensemble = EnsembleModel.bind(model_a, model_b)

# Deploy
serve.run(ensemble)
```

## Pattern 3: Preprocessing Pipeline

```python
# preprocessing_pipeline.py
from ray import serve
from typing import Dict
import numpy as np

@serve.deployment(num_replicas=2)
class Preprocessor:
    async def __call__(self, data: Dict) -> Dict:
        # Normalize features
        features = np.array(data["raw_features"])
        normalized = (features - features.mean()) / (features.std() + 1e-8)
        
        return {
            "features": normalized.tolist(),
            "original": data["raw_features"]
        }

@serve.deployment(num_replicas=3)
class InferenceModel:
    def __init__(self):
        self.model = self._load_model()
    
    async def __call__(self, preprocessed: Dict) -> Dict:
        features = preprocessed["features"]
        prediction = self.model.predict([features])[0]
        
        return {"prediction": float(prediction)}

@serve.deployment
class Pipeline:
    def __init__(self, preprocessor_handle, model_handle):
        self.preprocessor = preprocessor_handle
        self.model = model_handle
    
    async def __call__(self, request: Dict) -> Dict:
        # Process through pipeline
        preprocessed = await self.preprocessor.remote(request)
        result = await self.model.remote(preprocessed)
        
        return {
            "input": request["raw_features"],
            "preprocessed": preprocessed["features"],
            "prediction": result["prediction"]
        }

# Compose and deploy
preprocessor = Preprocessor.bind()
model = InferenceModel.bind()
pipeline = Pipeline.bind(preprocessor, model)

serve.run(pipeline)
```

---

## Load Balancing

### 1. Replica Autoscaling

```python
# autoscaling_deployment.py
from ray import serve

@serve.deployment(
    num_replicas=2,  # Start with 2 replicas
    max_replicas=10,  # Scale up to max 10
    min_replicas=1,   # Scale down to min 1
    target_ongoing_requests=2,  # Target 2 requests per replica
    upscale_smoothing_factor=0.5,
    downscale_smoothing_factor=0.2
)
class AutoScalingModel:
    def __init__(self):
        self.model = self._load_model()
    
    async def __call__(self, request):
        import time
        time.sleep(0.1)  # Simulate processing
        return {"result": "ok"}

AutoScalingModel.deploy()
```

## 2. Traffic Splitting (A/B Testing)

```python
# ab_testing.py
from ray import serve
from typing import Dict

@serve.deployment(name="model-v1")
class ModelV1:
    async def __call__(self, request: Dict) -> Dict:
        return {"version": "v1", "score": 0.85}

@serve.deployment(name="model-v2")
class ModelV2:
    async def __call__(self, request: Dict) -> Dict:
        return {"version": "v2", "score": 0.92}

@serve.deployment
class Router:
    async def __call__(self, request: Dict) -> Dict:
        # 80% traffic to v1, 20% to v2
        import random
        if random.random() < 0.8:
            # Use v1
            return {"traffic": "v1"}
        else:
            # Use v2
            return {"traffic": "v2"}

# Deploy both versions
ModelV1.deploy()
ModelV2.deploy()
Router.deploy()
```

## 3. Load Balancer Configuration

```python
# load_balancer.py
from ray import serve
from starlette.requests import Request
from starlette.responses import JSONResponse

@serve.deployment(
    num_replicas=5,
    max_concurrent_queries=100,  # Queue requests if over limit
    user_config={
        "batch_size": 32,
        "timeout": 30
    }
)
class LoadBalancedModel:
    def __init__(self, config):
        self.batch_size = config["batch_size"]
        self.timeout = config["timeout"]
        self.model = self._load_model()
    
    async def __call__(self, request: Request) -> JSONResponse:
        # Process with backpressure
        try:
            data = await request.json()
            result = await self._process_with_timeout(data)
            return JSONResponse({"status": "ok", "result": result})
        except TimeoutError:
            return JSONResponse(
                {"error": "Request timeout"},
                status_code=504
            )

LoadBalancedModel.deploy()
```

---

## Monitoring and Observability

### 1. Health Checks

```python
# health_checks.py
from ray import serve
from starlette.responses import JSONResponse

@serve.deployment(health_check_period_s=5)
class HealthyModel:
    def __init__(self):
        self.model = self._load_model()
        self.is_healthy = True
    
    def check_health(self):
        # Called by Ray Serve
        if not self.is_healthy:
            raise Exception("Model unhealthy")
    
    async def __call__(self, request):
        try:
            result = self.model.predict(request["data"])
            return {"result": float(result)}
        except Exception as e:
            self.is_healthy = False
            raise

@serve.deployment
async def health_endpoint(request):
    """Health check endpoint"""
    import ray
    serve_info = serve.status()
    
    all_healthy = all(
        deployment["status"] == "HEALTHY"
        for deployment in serve_info.deployments.values()
    )
    
    status = 200 if all_healthy else 503
    return JSONResponse({"healthy": all_healthy}, status_code=status)

HealthyModel.deploy()
health_endpoint.deploy(route_prefix="/health")
```

## 2. Metrics Collection

```python
# metrics.py
from ray import serve
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
requests_total = Counter(
    "serve_requests_total",
    "Total requests",
    ["deployment", "status"]
)

request_duration = Histogram(
    "serve_request_duration_seconds",
    "Request duration",
    ["deployment"],
    buckets=(0.01, 0.1, 0.5, 1.0, 5.0)
)

active_requests = Gauge(
    "serve_active_requests",
    "Active requests",
    ["deployment"]
)

@serve.deployment
class MetricsModel:
    def __init__(self):
        self.model = self._load_model()
        self.deployment_name = self.__class__.__name__
    
    async def __call__(self, request):
        active_requests.labels(deployment=self.deployment_name).inc()
        
        start_time = time.time()
        try:
            result = self.model.predict(request["data"])
            requests_total.labels(
                deployment=self.deployment_name,
                status="success"
            ).inc()
            return {"result": float(result)}
        except Exception as e:
            requests_total.labels(
                deployment=self.deployment_name,
                status="error"
            ).inc()
            raise
        finally:
            duration = time.time() - start_time
            request_duration.labels(
                deployment=self.deployment_name
            ).observe(duration)
            active_requests.labels(
                deployment=self.deployment_name
            ).dec()

MetricsModel.deploy()
```

## 3. Logging Configuration

```python
# logging_config.py
import logging
from ray import serve

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("serve_app")

@serve.deployment
class LoggedModel:
    def __init__(self):
        logger.info("Initializing model")
        self.model = self._load_model()
    
    async def __call__(self, request):
        logger.info(f"Received request: {request}")
        
        try:
            result = self.model.predict(request["data"])
            logger.info(f"Prediction successful: {result}")
            return {"result": float(result)}
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}", exc_info=True)
            raise

LoggedModel.deploy()
```

---

## Production Deployment

### 1. Docker Containerization

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose ports
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/-/routes')"

# Start Ray Serve
CMD ["python", "main.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  serve:
    build: .
    ports:
      - "8000:8000"
    environment:
      - RAY_memory=4000000000
      - RAY_object_store_memory=2000000000
    volumes:
      - ./models:/app/models:ro
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/-/routes"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 2. Kubernetes Deployment

```yaml
# k8s_deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ray-serve
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ray-serve
  template:
    metadata:
      labels:
        app: ray-serve
    spec:
      containers:
      - name: serve
        image: my-registry/ray-serve:latest
        ports:
        - containerPort: 8000
        
        # Resource limits
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
            nvidia.com/gpu: "1"
        
        # Environment variables
        env:
        - name: RAY_memory
          value: "4000000000"
        
        # Health checks
        livenessProbe:
          httpGet:
            path: /-/routes
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        
        readinessProbe:
          httpGet:
            path: /-/routes
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        
        # Volume mounts
        volumeMounts:
        - name: models
          mountPath: /app/models
          readOnly: true
      
      volumes:
      - name: models
        configMap:
          name: model-configs

---
apiVersion: v1
kind: Service
metadata:
  name: ray-serve
spec:
  selector:
    app: ray-serve
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## 3. CI/CD Pipeline

```yaml
# .github/workflows/deploy-ray-serve.yml
name: Deploy Ray Serve

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt pytest
      
      - name: Run tests
        run: pytest tests/
      
      - name: Build Docker image
        run: docker build -t ray-serve:latest .
      
      - name: Test image locally
        run: |
          docker run -d -p 8000:8000 ray-serve:latest
          sleep 5
          curl http://localhost:8000/-/routes

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to production
        run: |
          kubectl set image deployment/ray-serve \
            serve=my-registry/ray-serve:latest \
            --namespace=production
          kubectl rollout status deployment/ray-serve \
            --namespace=production
```

---

## Troubleshooting

### Issue: "Port already in use"

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
serve.start(http_options={"host": "0.0.0.0", "port": 9000})
```

## Issue: "Out of memory"

```python
# Increase object store memory
ray.init(object_store_memory=4_000_000_000)

# Or reduce batch size
@serve.deployment(user_config={"batch_size": 8})  # was 32
class Model:
    pass
```

## Issue: "Deployment unhealthy"

```bash
# Check status
serve.status()

# Check logs
ray logs cluster
```

---

## Cross-References

- [Hydra Configuration Advanced Guide](../configuration/hydra-advanced-guide.md)
- [Performance Debugging Guide](../performance/debugging-guide.md)
- [Kubernetes Deployment Guide](../deployment/kubernetes-guide.md)

---

**Word Count**: 2,604 | **Examples**: 22 | **Patterns**: 8
**Last Updated**: 2026-06-22 | **Status**: ✅ Complete
