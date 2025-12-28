# Inference Deployment Guide

Complete guide for deploying ML models to production inference environments.

## Overview

This guide covers deployment strategies, infrastructure setup, scaling considerations, and best practices for production ML inference systems.

## Deployment Patterns

### Pattern 1: REST API (FastAPI/Flask)

**Best for:** Real-time predictions, microservices architecture

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch

app = FastAPI()
model = None

class PredictionRequest(BaseModel):
    data: list
    model_version: str = "v1"

class PredictionResponse(BaseModel):
    prediction: list
    confidence: float
    model_version: str

@app.on_event("startup")
async def load_model():
    """Load model on startup."""
    global model
    model = torch.load("model.pt")
    model.eval()

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Make prediction."""
    try:
        with torch.no_grad():
            output = model(torch.tensor(request.data))
        
        return PredictionResponse(
            prediction=output.tolist(),
            confidence=float(output.max()),
            model_version=request.model_version
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Pattern 2: Batch Processing

**Best for:** High-throughput, non-real-time workloads

```python
import boto3
from concurrent.futures import ThreadPoolExecutor

class BatchInferenceProcessor:
    def __init__(self, model, batch_size=32):
        self.model = model
        self.batch_size = batch_size
        self.s3 = boto3.client('s3')
    
    def process_batch_file(self, input_file, output_file):
        """Process entire batch file."""
        # Read input data
        data = self._read_input(input_file)
        
        # Process in batches
        results = []
        for i in range(0, len(data), self.batch_size):
            batch = data[i:i + self.batch_size]
            predictions = self.model.predict(batch)
            results.extend(predictions)
        
        # Write results
        self._write_output(output_file, results)
    
    def process_s3_batch(self, bucket, prefix):
        """Process all files in S3 prefix."""
        objects = self.s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for obj in objects.get('Contents', []):
                input_key = obj['Key']
                output_key = input_key.replace('input/', 'output/')
                
                future = executor.submit(
                    self.process_batch_file,
                    f"s3://{bucket}/{input_key}",
                    f"s3://{bucket}/{output_key}"
                )
                futures.append(future)
            
            # Wait for completion
            for future in futures:
                future.result()
```

### Pattern 3: Streaming (Kafka/RabbitMQ)

**Best for:** Event-driven architectures, real-time pipelines

```python
from kafka import KafkaConsumer, KafkaProducer
import json

class StreamingInference:
    def __init__(self, model, input_topic, output_topic):
        self.model = model
        self.consumer = KafkaConsumer(
            input_topic,
            bootstrap_servers=['localhost:9092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.output_topic = output_topic
    
    def run(self):
        """Process messages continuously."""
        for message in self.consumer:
            try:
                # Get input data
                input_data = message.value
                
                # Make prediction
                prediction = self.model.predict(input_data)
                
                # Send result
                self.producer.send(
                    self.output_topic,
                    {
                        'request_id': input_data['id'],
                        'prediction': prediction,
                        'timestamp': time.time()
                    }
                )
            except Exception as e:
                logger.error(f"Processing error: {e}")
```

## Infrastructure Setup

### Docker Containerization

**Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy model and code
COPY model.pt .
COPY app/ ./app/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  inference-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MODEL_PATH=/models/model.pt
      - LOG_LEVEL=INFO
    volumes:
      - ./models:/models
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped
```

### Kubernetes Deployment

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-inference
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ml-inference
  template:
    metadata:
      labels:
        app: ml-inference
    spec:
      containers:
      - name: inference
        image: myregistry/ml-inference:v1.0
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
            nvidia.com/gpu: 1
          limits:
            memory: "4Gi"
            cpu: "2000m"
            nvidia.com/gpu: 1
        env:
        - name: MODEL_PATH
          value: "/models/model.pt"
        volumeMounts:
        - name: model-storage
          mountPath: /models
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
      volumes:
      - name: model-storage
        persistentVolumeClaim:
          claimName: model-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: ml-inference-service
spec:
  selector:
    app: ml-inference
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ml-inference-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ml-inference
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## Scaling Strategies

### Horizontal Scaling

**Load Balancer Config (nginx):**
```nginx
upstream inference_backend {
    least_conn;
    server inference1:8000 weight=1 max_fails=3 fail_timeout=30s;
    server inference2:8000 weight=1 max_fails=3 fail_timeout=30s;
    server inference3:8000 weight=1 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    
    location /predict {
        proxy_pass http://inference_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_connect_timeout 5s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /health {
        access_log off;
        proxy_pass http://inference_backend;
    }
}
```

### Vertical Scaling

**Resource Optimization:**
- Start with 2 CPU cores, 4GB RAM
- Scale to 4-8 cores for CPU-bound workloads
- Add GPU for deep learning models
- Monitor and adjust based on metrics

### Auto-scaling Rules

```python
# AWS Auto Scaling Policy
{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
        "PredefinedMetricType": "ASGAverageCPUUtilization"
    },
    "ScaleInCooldown": 300,
    "ScaleOutCooldown": 60
}
```

## Model Versioning

### Blue-Green Deployment

```python
class ModelRouter:
    def __init__(self):
        self.models = {
            'blue': load_model('model_v1.pt'),
            'green': load_model('model_v2.pt')
        }
        self.active = 'blue'
    
    def predict(self, data, version=None):
        """Route to active model version."""
        model_version = version or self.active
        return self.models[model_version].predict(data)
    
    def switch_version(self):
        """Switch active version."""
        self.active = 'green' if self.active == 'blue' else 'blue'
```

### Canary Deployment

```python
import random

class CanaryRouter:
    def __init__(self, stable_model, canary_model, canary_percent=10):
        self.stable = stable_model
        self.canary = canary_model
        self.canary_percent = canary_percent
    
    def predict(self, data):
        """Route % of traffic to canary."""
        if random.random() * 100 < self.canary_percent:
            return self.canary.predict(data), 'canary'
        return self.stable.predict(data), 'stable'
```

## Monitoring & Observability

### Health Endpoints

```python
@app.get("/health")
async def health_check():
    """Liveness probe."""
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/ready")
async def readiness_check():
    """Readiness probe - check model loaded."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "ready", "model_loaded": True}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

## Security

### API Authentication

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

@app.post("/predict")
async def predict(
    request: PredictionRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Protected endpoint."""
    if not verify_token(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return make_prediction(request)
```

### Input Validation

```python
from pydantic import BaseModel, validator

class PredictionRequest(BaseModel):
    data: list
    
    @validator('data')
    def validate_data(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Data cannot be empty')
        if len(v) > 1000:
            raise ValueError('Data too large')
        return v
```

## Best Practices

### Deployment Checklist

- [ ] Model artifacts versioned and stored
- [ ] Docker image built and tested
- [ ] Health/readiness endpoints implemented
- [ ] Monitoring and alerting configured
- [ ] Auto-scaling rules defined
- [ ] Load testing completed
- [ ] Rollback plan documented
- [ ] Security review passed

### Production Readiness

**Infrastructure:**
- Multi-region deployment for HA
- Load balancing configured
- Auto-scaling enabled
- Backup and recovery tested

**Monitoring:**
- Metrics collection enabled
- Dashboards created
- Alerts configured
- On-call rotation established

**Security:**
- Authentication/authorization
- Input validation
- Rate limiting
- Security scanning

## Troubleshooting

### Common Issues

**OOM Errors:**
- Reduce batch size
- Enable gradient checkpointing
- Use model quantization
- Scale vertically

**High Latency:**
- Enable batching
- Add caching layer
- Optimize preprocessing
- Use faster hardware

**Cold Starts:**
- Keep models warm
- Use reserved instances
- Implement connection pooling
- Optimize model loading

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [AWS SageMaker](https://docs.aws.amazon.com/sagemaker/)
- [MLOps Principles](https://ml-ops.org/)

## Related Guides

- [Inference Monitoring](inference_monitoring.md)
- [Inference Performance](inference_performance.md)
- [Production ML Guide](../docs/ml_ops/production_guide.md)
