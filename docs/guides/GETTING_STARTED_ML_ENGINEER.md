## Getting Started Guide for ML Engineers
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Last Updated: 2026-07-08
**Target Audience:** ML engineers, MLOps professionals, production ML specialists
**Estimated Time:** 20-25 minutes to production deployment

## Your Goal

Deploy, monitor, and scale ML models in production with Production reliability, versioning, and observability. This guide covers the full ML lifecycle from model registration to canary deployment.

---

## Phase 1: MLOps Environment Setup (5 minutes)

### Prerequisites

- Python 3.10+
- Docker & Kubernetes (optional, recommended)
- Git for version control
- Cloud CLI (AWS, GCP, or Azure)

### Local MLOps Setup

```bash
# Create MLOps workspace
mkdir ~/codex-mlops && cd ~/codex-mlops

# Set up Python environment
python -m venv .venv
source .venv/bin/activate

# Install Codex ML with production stack
pip install --upgrade pip
pip install 'codex-ml[mlops,cloud]'

# Initialize MLOps project
codex mlops init \
 --project-name my-ml-service \
 --cloud-provider aws \
 --region us-west-2

# Verify setup
codex mlops status
```

### Kubernetes Cluster Setup (Optional)

```bash
# Use kind for local testing
kind create cluster --name codex-ml-dev

# Deploy Codex ML operator
kubectl apply -f manifests/codex-ml-operator.yaml

# Verify deployment
kubectl get pods -n codex-ml-system
```

---

## Phase 2: Model Registration & Versioning (5 minutes)

### Register Your Model

```python
from codex_ml.mlops import ModelRegistry, ModelCard

# Connect to model registry (S3, Azure Blob, or Hugging Face Hub)
registry = ModelRegistry(
 backend='huggingface', # or 's3', 'azure', 'gcs'
 repo_id='my-org/sentiment-classifier',
 hf_token='hf_xxxxxxxxxxxx'
)

# Create model card
model_card = ModelCard(
 name='sentiment-classifier',
 version='1.0.0',
 task='text-classification',
 framework='pytorch',
 model_id='distilbert-base-uncased',
 
 # Metadata
 description='Classifies sentiment (positive, negative, neutral)',
 intended_use='Production classification API',
 training_data='Internal sentiment dataset (1M samples)',
 training_date='2026-07-08',
 
 # Performance metrics
 metrics={
 'accuracy': 0.895,
 'f1_score': 0.892,
 'precision': 0.891,
 'recall': 0.893,
 'inference_latency_ms': 45, # On GPU
 'inference_throughput': 20, # Samples/sec/GPU
 },
 
 # Model card fields
 limitations='Works best on English text, struggles with sarcasm',
 biases='May show demographic biases in training data',
 considerations='Test on your specific domain before deployment',
)

# Register with metadata
registry.register(
 model=model,
 model_card=model_card,
 artifacts={
 'model': 'outputs/model.safetensors',
 'config': 'config.json',
 'tokenizer': 'tokenizer.json',
 },
 tags=['production', 'sentiment', 'v1.0'],
 is_private=False # Make public for Hugging Face Hub
)

print(f" Model registered: {registry.latest_version()}")
```

### Version Control & Lineage

```python
# View version history
versions = registry.list_versions()
for v in versions:
 print(f"{v.version}: {v.status} | Acc: {v.metrics['accuracy']:.1%} | "
 f"Created: {v.created_at}")

# Retrieve specific version
model_v1 = registry.get('sentiment-classifier', version='1.0.0')

# Track lineage
lineage = registry.get_lineage('sentiment-classifier')
print(f"Training data {lineage['data_uri']}")
print(f"Training script {lineage['script_uri']}")
print(f"Hyperparameters {lineage['params']}")

# Compare versions
diff = registry.compare_versions('1.0.0', '1.0.1')
print(f"Metrics change: {diff['metrics']}")
print(f"Model size change: {diff['model_size_mb']}")
```

---

## Phase 3: Production Serving (5 minutes)

### Option A: Ray Serve (Recommended for Python)

```python
from codex_ml.serving import RayServeDeployment, ModelServer
from pathlib import Path
import ray

# Start Ray
ray.init()

# Create deployment
deployment = RayServeDeployment(
 name='sentiment-classifier',
 model_path='s3://my-bucket/models/sentiment-v1.0',
 
 # Replica configuration
 num_replicas=4,
 num_gpus=1, # Per replica
 resources={'custom_resource': 1},
 
 # Performance tuning
 batch_size=32,
 max_batch_wait_ms=100,
 
 # Health checks
 health_check_period_s=10,
 health_check_timeout_s=5,
)

# Deploy
deployment.deploy()

# Test endpoint
import requests
response = requests.post(
 'http://localhost:8000/predict',
 json={'text': 'This is great!'}
)
print(response.json()) # {'label': 'positive', 'confidence': 0.95}
```

### Option B: FastAPI (for REST APIs)

```python
from codex_ml.serving import FastAPIServer
from fastapi import FastAPI
from pydantic import BaseModel

class PredictionRequest(BaseModel):
 text: str
 return_probabilities: bool = False

# Create server
server = FastAPIServer(
 app_name='sentiment-api',
 model_path='outputs/sentiment-v1.0',
 task='text-classification',
)

# Add custom endpoints
@server.app.post('/predict')
async def predict(request: PredictionRequest):
 """Predict sentiment for given text."""
 result = server.model.predict(request.text)
 
 if request.return_probabilities:
 result['probabilities'] = {
 'positive': 0.75,
 'negative': 0.15,
 'neutral': 0.10,
 }
 
 return result

@server.app.post('/batch-predict')
async def batch_predict(requests: list[PredictionRequest]):
 """Batch prediction endpoint."""
 return [server.model.predict(r.text) for r in requests]

# Run
if __name__ == '__main__':
 import uvicorn
 uvicorn.run(server.app, host='0.0.0.0', port=8000)
```

### Option C: Docker Containerization

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy model and code
COPY models/ ./models/
COPY app.py .

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
 CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Serve
CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t sentiment-api:v1.0 .
docker run -p 8000:8000 \
 -e MODEL_PATH=/app/models/sentiment-v1.0 \
 sentiment-api:v1.0

# Test
curl -X POST http://localhost:8000/predict \
 -H "Content-Type: application/json" \
 -d '{"text": "This is great!"}'
```

---

## Phase 4: Monitoring & Observability (5 minutes)

### Deployment Monitoring

```python
from codex_ml.monitoring import DeploymentMonitor, AlertManager

# Create monitor
monitor = DeploymentMonitor(
 deployment_name='sentiment-classifier',
 service_type='ray-serve', # or 'kubernetes'
)

# Collect metrics
metrics = monitor.collect_metrics(period_minutes=5)
print(f"Requests/sec: {metrics['throughput']}")
print(f"Avg latency: {metrics['latency_p50']:.0f}ms")
print(f"P99 latency: {metrics['latency_p99']:.0f}ms")
print(f"Error rate: {metrics['error_rate']:.2%}")
print(f"GPU utilization: {metrics['gpu_utilization']:.1%}")

# Set up alerts
alert_manager = AlertManager()
alert_manager.add_rule(
 name='high_latency',
 metric='latency_p99',
 threshold_ms=500,
 duration_minutes=2,
 action='slack',
 webhook='https://hooks.slack.com/...'
)

alert_manager.add_rule(
 name='model_drift',
 metric='prediction_distribution_drift',
 threshold=0.3, # KL divergence threshold
 action='auto_retrain',
)
```

### Model Performance Tracking

```python
from codex_ml.monitoring import ModelPerformanceMonitor

# Monitor production predictions
perf_monitor = ModelPerformanceMonitor(
 model_version='1.0.0',
 expected_metrics={
 'accuracy': 0.89,
 'precision': 0.89,
 'recall': 0.89,
 },
 drift_threshold=0.05, # Alert if metrics drop 5%
)

# Log predictions (from your serving code)
perf_monitor.log_prediction(
 input='This is great!',
 predicted_label='positive',
 predicted_confidence=0.95,
 ground_truth='positive', # If available
)

# Check for data drift and model drift
drift_report = perf_monitor.check_drift()
if drift_report['detected']:
 print(f" Data drift detected!")
 print(f" Feature distribution shift: {drift_report['drift_magnitude']:.2%}")
 print(f" Recommendation: {drift_report['recommendation']}")
 
 # Auto-trigger retraining if needed
 if drift_report['recommendation'] == 'retrain':
 print(" Auto-triggering retraining pipeline...")
 # trigger_retraining_pipeline()
```

### Logging & Tracing

```python
from codex_ml.observability import DistributedTracing
import logging

# Set up distributed tracing
tracer = DistributedTracing(
 service_name='sentiment-api',
 jaeger_host='localhost',
 jaeger_port=6831,
)

# Enable structured logging
logger = logging.getLogger(__name__)
logger.info('Prediction request', extra={
 'user_id': 'user123',
 'model_version': '1.0.0',
 'text_length': len(text),
 'trace_id': tracer.current_trace_id,
})

# Trace inference latency
with tracer.span('model_inference'):
 prediction = model.predict(text)
 
with tracer.span('post_processing'):
 result = format_result(prediction)
```

---

## Phase 5: Canary & Blue-Green Deployments (5 minutes)

### Canary Deployment

```python
from codex_ml.deployment import CanaryDeployment

# Create canary deployment
canary = CanaryDeployment(
 service_name='sentiment-classifier',
 stable_version='1.0.0', # Current production
 canary_version='1.1.0', # New version to test
 
 # Gradual traffic shift
 initial_traffic_percent=5, # Start with 5%
 increment_percent=10, # Increase by 10% every interval
 interval_minutes=10, # Every 10 minutes
 
 # Success criteria
 error_rate_threshold=0.01, # Allow max 1% errors
 latency_p99_threshold_ms=600, # P99 latency < 600ms
 
 # Rollback criteria
 auto_rollback_on_error=True,
)

# Deploy
canary.start()

# Monitor progress
while canary.is_running():
 status = canary.get_status()
 print(f"Traffic split: {status['stable']}% {status['canary']}%")
 print(f"Canary error rate: {status['canary_error_rate']:.2%}")
 print(f"Canary latency: {status['canary_latency_ms']:.0f}ms")
 
 if status['should_rollback']:
 print(" Rollback triggered - reverting to stable version")
 canary.rollback()
 break
 
 if status['canary_percent'] == 100:
 print(" Canary deployment successful!")
 canary.complete()
 break
 
 time.sleep(30) # Check every 30 seconds
```

### Blue-Green Deployment

```python
from codex_ml.deployment import BlueGreenDeployment

# Create blue-green deployment
bg = BlueGreenDeployment(
 service_name='sentiment-classifier',
 blue_version='1.0.0', # Current production
 green_version='1.1.0', # New version ready
)

# Deploy green environment (zero downtime)
print(" Blue (production) running...")
print(" Green (staging) starting...")
bg.deploy_green()

# Run smoke tests on green
smoke_tests = bg.run_smoke_tests()
print(f"Smoke tests passed: {smoke_tests['passed']}/{smoke_tests['total']}")

if not smoke_tests['all_passed']:
 print(" Smoke tests failed - keeping blue production")
 bg.destroy_green()
else:
 # Switch traffic instantly
 print(" Switching traffic blue green...")
 bg.switch_traffic()
 print(" Green is now production!")
 
 # Keep blue as fallback for quick rollback
 time.sleep(300) # Wait 5 minutes
 bg.destroy_blue() # Safe to destroy old environment
```

---

## Phase 6: Advanced MLOps Tasks

### A/B Testing Deployments

```python
from codex_ml.deployment import ABTestDeployment

ab_test = ABTestDeployment(
 service_name='sentiment-classifier',
 variant_a_version='1.0.0',
 variant_b_version='1.1.0',
 
 # Segment traffic by user
 segmentation_strategy='user_id_hash', # or 'geographic', 'random'
 traffic_split_percent=50, # 50/50 split
 
 # Metrics to track
 metrics=['accuracy', 'latency', 'user_satisfaction'],
)

ab_test.start()

# After running (e.g., 1 week)
results = ab_test.get_results()
print(f"Variant A accuracy: {results['variant_a']['accuracy']:.2%}")
print(f"Variant B accuracy: {results['variant_b']['accuracy']:.2%}")
print(f"Improvement: {results['improvement']:.2%}")

if results['variant_b_winner']:
 ab_test.promote_variant_b()
```

### Auto-Scaling Configuration

```yaml
# kubernetes/sentiment-classifier-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
 name: sentiment-classifier-hpa
spec:
 scaleTargetRef:
 apiVersion: apps/v1
 kind: Deployment
 name: sentiment-classifier
 
 minReplicas: 2
 maxReplicas: 20
 
 metrics:
 # Scale on CPU
 - type: Resource
 resource:
 name: cpu
 target:
 type: Utilization
 averageUtilization: 70
 
 # Scale on memory
 - type: Resource
 resource:
 name: memory
 target:
 type: Utilization
 averageUtilization: 80
 
 # Scale on custom metrics (requests/sec)
 - type: Pods
 pods:
 metric:
 name: http_requests_per_second
 target:
 type: AverageValue
 averageValue: "1000"
 
 behavior:
 scaleDown:
 stabilizationWindowSeconds: 300
 policies:
 - type: Percent
 value: 50
 periodSeconds: 60
 scaleUp:
 stabilizationWindowSeconds: 0
 policies:
 - type: Percent
 value: 100
 periodSeconds: 15
 - type: Pods
 value: 4
 periodSeconds: 15
 selectPolicy: Max
```

Deploy:
```bash
kubectl apply -f kubernetes/sentiment-classifier-hpa.yaml
kubectl get hpa # Monitor
```

---

## Next Steps

- **CI/CD Pipeline**: [GitHub Actions Setup](./CI_CD_SETUP.md)
- **Kubernetes Guide**: [K8s Deployment](../admin/KUBERNETES_DEPLOYMENT.md)
- **Cost Optimization**: [FinOps Guide](./FINOPS_GUIDE.md)
- **Disaster Recovery**: [DR Planning](../admin/DISASTER_RECOVERY.md)

## 🆘 Getting Help

- **MLOps Discussions**: [GitHub Discussions](https://github.com/Aries-Serpent/_codex_/discussions?discussions_q=mlops)
- **Production Issues**: [Create an Issue](https://github.com/Aries-Serpent/_codex_/issues/new?labels=mlops)
- **Community Support**: [Slack Channel](https://slack.codex-ml.com)

---

**Welcome to enterprise ML! **
