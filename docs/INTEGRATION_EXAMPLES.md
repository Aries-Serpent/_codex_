# Integration Examples - Aries-Serpent v0.1.0
**Last Updated:** 2026-07-11

**Document Type:** Developer Guide with Code Examples  
**Audience:** Developers, System Integrators  
**Last Updated: 2026-07-09

## Example 1: Basic API Usage with FastAPI

**Use Case:** Simple HTTP API call to query patterns

```python
# example1_basic_api.py
import httpx
import asyncio

async def query_patterns():
    """Query patterns via REST API"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/query",
            json={
                "text": "User login with unusual IP address",
                "context": {"user_id": "123", "ip": "192.168.1.1"}
            }
        )
        
        result = response.json()
        print(f"Status: {response.status_code}")
        print(f"Matched Patterns: {result.get('patterns', [])}")
        print(f"Confidence: {result.get('confidence')}")
        
        return result

if __name__ == "__main__":
    result = asyncio.run(query_patterns())
```

**Running the example:**
```bash
# Start the API server
python -m codex.api.main

# In another terminal
python example1_basic_api.py

# Expected output:
# Status: 200
# Matched Patterns: ['unusual_login', 'security_alert']
# Confidence: 0.95
```

## Example 2: ML Inference Example

**Use Case:** Run inference on a model and get predictions

```python
# example2_ml_inference.py
from codex.ml.inference import InferenceEngine
from codex.config import ConfigManager
import torch

def run_inference():
    """Load model and run inference"""
    
    # Initialize configuration
    config = ConfigManager.load_config(config_name="inference")
    
    # Initialize inference engine
    engine = InferenceEngine(config)
    
    # Load model
    model = engine.load_model("gpt2")
    model.eval()
    
    # Prepare input
    text = "The future of AI is"
    input_ids = engine.tokenizer.encode(text, return_tensors="pt")
    
    # Run inference
    with torch.no_grad():
        outputs = model.generate(
            input_ids,
            max_length=50,
            num_return_sequences=3,
            temperature=0.7
        )
    
    # Decode results
    results = [
        engine.tokenizer.decode(output, skip_special_tokens=True)
        for output in outputs
    ]
    
    for i, result in enumerate(results, 1):
        print(f"Generation {i}: {result}")
    
    return results

if __name__ == "__main__":
    run_inference()
```

**Running the example:**
```bash
python example2_ml_inference.py

# Expected output:
# Generation 1: The future of AI is bright and promising...
# Generation 2: The future of AI is uncertain but fascinating...
# Generation 3: The future of AI is already here...
```

## Example 3: Custom Protocol Implementation

**Use Case:** Implement custom protocol handler for domain-specific messages

```python
# example3_protocol_handler.py
from codex.core.protocol import ProtocolHandler, Message, Response
from typing import Dict, Any

class CustomDomainProtocol(ProtocolHandler):
    """Custom protocol for domain-specific integration"""
    
    async def process_message(self, msg: Message) -> Response:
        """Process custom message format"""
        
        if msg.type == "domain_query":
            return await self._handle_query(msg.payload)
        elif msg.type == "domain_learn":
            return await self._handle_learning(msg.payload)
        else:
            return Response(status="error", message="Unknown message type")
    
    async def _handle_query(self, payload: Dict[str, Any]) -> Response:
        """Handle domain-specific query"""
        
        # Extract domain-specific fields
        domain_id = payload.get("domain_id")
        query_text = payload.get("text")
        
        # Call Cognitive Brain
        patterns = await self.cognitive_brain.recognize_patterns(query_text)
        
        # Apply domain-specific logic
        filtered_patterns = [
            p for p in patterns
            if p.domain == domain_id
        ]
        
        return Response(
            status="success",
            data={"patterns": filtered_patterns}
        )
    
    async def _handle_learning(self, payload: Dict[str, Any]) -> Response:
        """Handle domain-specific learning"""
        
        event = payload.get("event")
        outcome = payload.get("outcome")
        
        # Learn from feedback
        await self.cognitive_brain.learn_from_feedback(
            event=event,
            outcome=outcome
        )
        
        return Response(status="success")

# Usage
async def main():
    protocol = CustomDomainProtocol()
    
    message = Message(
        type="domain_query",
        payload={
            "domain_id": "finance",
            "text": "Detect fraudulent transactions"
        }
    )
    
    response = await protocol.process_message(message)
    print(f"Response: {response}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Example 4: Kubernetes Integration

**Use Case:** Deploy custom job in Kubernetes and monitor results

```python
# example4_k8s_integration.py
from kubernetes import client, config, watch
import asyncio

def deploy_inference_job():
    """Deploy inference job to Kubernetes"""
    
    # Load K8s config
    config.load_incluster_config()
    
    # Create batch API client
    batch_v1 = client.BatchV1Api()
    
    # Define job
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name="inference-job-001"),
        spec=client.V1JobSpec(
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={"app": "inference"}),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="inference",
                            image="aries-serpent:0.1.0-inference",
                            command=["python", "-m", "codex.ml.run_inference"],
                            env=[
                                client.V1EnvVar(
                                    name="MODEL_NAME",
                                    value="gpt2"
                                )
                            ],
                            resources=client.V1ResourceRequirements(
                                requests={"cpu": "1", "memory": "2Gi"},
                                limits={"cpu": "2", "memory": "4Gi"}
                            )
                        )
                    ],
                    restart_policy="Never"
                )
            ),
            backoff_limit=3
        )
    )
    
    # Create job
    api_response = batch_v1.create_namespaced_job(
        body=job,
        namespace="aries-prod"
    )
    
    print(f"Job created: {api_response.metadata.name}")
    
    # Watch job status
    watch_job(api_response.metadata.name)

def watch_job(job_name: str):
    """Watch job for completion"""
    
    batch_v1 = client.BatchV1Api()
    w = watch.Watch()
    
    for event in w.stream(
        batch_v1.list_namespaced_job,
        namespace="aries-prod",
        field_selector=f"metadata.name={job_name}",
        timeout_seconds=300
    ):
        job = event['object']
        status = job.status
        
        if status.succeeded:
            print(f"Job {job_name} completed successfully")
            w.stop()
            break
        elif status.failed:
            print(f"Job {job_name} failed")
            w.stop()
            break
        else:
            print(f"Job status: {status.active} active, {status.failed} failed")

if __name__ == "__main__":
    deploy_inference_job()
```

## Example 5: Docker Compose with Custom Services

**Use Case:** Multi-service deployment with custom configuration

```yaml
# example5_docker-compose.yml
version: '3.9'

services:
  # Main API service
  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: ******postgres:5432/aries
      REDIS_URL: redis://:password@redis:6379
      COGNITIVE_BRAIN_MODE: distributed
    depends_on:
      - postgres
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s

  # ML inference service
  inference:
    build:
      context: .
      dockerfile: Dockerfile.inference
    environment:
      DATABASE_URL: ******postgres:5432/aries
      MODEL_CACHE_DIR: /models
    volumes:
      - model_cache:/models
    depends_on:
      - postgres
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G

  # Database
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: aries
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s

  # Cache
  redis:
    image: redis:7-alpine
    command: redis-server --requirepass password
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
  model_cache:
```

**Running:**
```bash
docker-compose -f example5_docker-compose.yml up -d
```

## Running All Examples

**Quick test script:**
```bash
#!/bin/bash
# run_examples.sh

echo "Example 1: Basic API Usage"
python example1_basic_api.py

echo -e "\nExample 2: ML Inference"
python example2_ml_inference.py

echo -e "\nExample 3: Custom Protocol"
python example3_protocol_handler.py

echo -e "\nExample 4: K8s Integration"
# kubectl apply -f example4_k8s_job.yaml

echo -e "\nExample 5: Docker Compose"
docker-compose -f example5_docker-compose.yml up -d
```

## Example Requirements

All examples require:

```txt
# requirements-examples.txt
codex-ml>=0.1.0
httpx>=0.25.0
torch>=2.0.0
transformers>=4.30.0
kubernetes>=24.0.0
```

**Install:**
```bash
pip install -r requirements-examples.txt
```

## Troubleshooting Examples

| Issue | Solution |
|-------|----------|
| API connection refused | Ensure API server running: `python -m codex.api.main` |
| Model not found | Download models: `python -m codex.ml.download_models` |
| K8s auth failed | Setup kubeconfig: `kubectl config use-context <cluster>` |
| Port already in use | Change port: `docker run -p 8001:8000 ...` |

---

**Status:**  COMPLETE  
**Last Updated: 2026-07-09
