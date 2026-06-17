# Integration Guide

## Third-Party Integrations

This guide covers integrating Codex ML with popular ML platforms and tools.

## Hugging Face Hub Integration

### Loading Models from Hub

```python
from transformers import AutoModel, AutoTokenizer  # pragma: allowlist secret
from src.codex_ml.models import CodexMLModel

# Load pretrained model
model_name = "bert-base-uncased"
model = AutoModel.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)  # pragma: allowlist secret

# Wrap in Codex pipeline
codex_model = CodexMLModel(
    model=model,
    tokenizer=tokenizer  # pragma: allowlist secret
)
```

### Pushing Models to Hub

```python
from transformers import AutoModel

# Train your model
model.train()
# ... training code ...

# Push to Hub
model.push_to_hub(
    "my-model-name",
    organization="my-org",
    private=False
)

# Later: pull from Hub
model = AutoModel.from_pretrained("my-org/my-model-name")
```

### Loading Datasets from Hub

```python
from datasets import load_dataset
from src.ingestion.pipeline import IngestionPipeline

# Load dataset
dataset = load_dataset("glue", "sst2")

# Convert to JSONL for Codex pipeline
import json

with open("data/sst2.jsonl", "w") as f:
    for example in dataset["train"]:
        json.dump({
            "text": example["sentence"],
            "label": example["label"]
        }, f)
        f.write("\n")

# Process with Codex
pipeline = IngestionPipeline()
result = pipeline.ingest_file("data/sst2.jsonl")
```

## MLflow Integration

### Experiment Tracking

```python
import mlflow
from src.codex_ml.training.trainer import Trainer
from omegaconf import OmegaConf

# Initialize MLflow
mlflow.set_experiment("codex-ml-experiments")

with mlflow.start_run(run_name="bert-fine-tuning"):
    # Load config
    config = OmegaConf.load("configs/training/bert.yaml")
    
    # Log config
    mlflow.log_params(OmegaConf.to_container(config))
    
    # Create trainer
    trainer = Trainer(config=config)
    
    # Train (metrics logged automatically)
    trainer.train(
        train_data="data/train.jsonl",
        eval_data="data/eval.jsonl"
    )
    
    # Log model
    mlflow.pytorch.log_model(trainer.model, "model")
    
    # Log artifacts
    mlflow.log_artifacts("logs/")

# View results
# Open MLflow UI: mlflow ui
```

### Model Registry

```python
import mlflow
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Register model
run_id = mlflow.active_run().info.run_id
model_uri = f"runs:/{run_id}/model"

mv = mlflow.register_model(
    model_uri=model_uri,
    name="codex-bert-classifier"
)

# Transition to production
client.transition_model_version_stage(
    name="codex-bert-classifier",
    version=mv.version,
    stage="Production"
)

# Load production model
production_model = mlflow.pytorch.load_model(
    "models:/codex-bert-classifier/Production"
)
```

## Ray Integration

### Distributed Training

```python
from ray.train import RunConfig, ScalingConfig
from ray.train.torch import TorchTrainer
from src.codex_ml.training.trainer import Trainer

def train_func(config):
    """Training function for Ray."""
    trainer = Trainer(config=config)
    trainer.train()

# Configure scaling
scaling_config = ScalingConfig(
    num_workers=4,
    use_gpu=True,
    trainer_resources={"GPU": 1, "CPU": 4}
)

# Create Ray trainer
ray_trainer = TorchTrainer(
    train_loop_per_worker=train_func,
    scaling_config=scaling_config,
    run_config=RunConfig(name="distributed-training")
)

# Train
result = ray_trainer.fit()
```

### Ray Serve (Model Serving)

```python
from ray import serve
import json

serve.start()

@serve.deployment(num_replicas=3)
class CodexModel:
    def __init__(self, model_path):
        # Load model
        self.model = load_model(model_path)
    
    async def __call__(self, request):
        """Handle prediction requests."""
        data = await request.json()
        texts = data.get("texts", [])
        
        # Batch predict
        predictions = self.model.predict(texts)
        
        return {
            "predictions": predictions.tolist()
        }

# Deploy
serve.run(
    CodexModel.bind(model_path="./model"),
    name="codex-serve"
)

# Query
import requests
response = requests.post(
    "http://localhost:8000",
    json={"texts": ["Sample text"]}
)
print(response.json())
```

## Apache Spark Integration

### Distributed Processing with Spark

```python
from pyspark.sql import SparkSession
from src.ingestion.pipeline import IngestionPipeline

# Create Spark session
spark = SparkSession.builder \
    .appName("CodexML") \
    .getOrCreate()

# Read data
df = spark.read.json("data/train.jsonl")

# Apply Codex transformations (UDF)
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

def preprocess_text(text):
    from src.ingestion.pipeline import IngestionPipeline
    config = PipelineConfig(lowercase=True, strip_whitespace=True)
    pipeline = IngestionPipeline(config)
    return pipeline.transform_record({"text": text})

preprocess_udf = udf(preprocess_text, StringType())
df_processed = df.withColumn("text", preprocess_udf(df.text))

# Write processed data
df_processed.write.json("data/processed/")
```

## Apache Airflow Integration

### ML Pipeline Orchestration

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def ingest_data():
    from src.ingestion.pipeline import IngestionPipeline
    pipeline = IngestionPipeline()
    result = pipeline.ingest_file("data/raw.csv", "data/processed.jsonl")
    return result.records_processed

def generate_embeddings():
    from src.rag.pipelines.embedding import EmbeddingPipeline
    embedder = EmbeddingPipeline()
    embeddings, docs = embedder.embed_documents("data/processed.jsonl")
    return len(embeddings)

def train_model():
    from src.codex_ml.training.trainer import Trainer
    trainer = Trainer()
    trainer.train(
        train_data="data/train.jsonl",
        eval_data="data/eval.jsonl"
    )
    return "success"

# Define DAG
default_args = {
    'start_date': datetime(2024, 1, 1),
    'retries': 1
}

with DAG('codex_ml_pipeline', default_args=default_args) as dag:
    # Tasks
    t_ingest = PythonOperator(
        task_id='ingest',  # pragma: allowlist secret
        python_callable=ingest_data
    )
    
    t_embed = PythonOperator(
        task_id='embed',  # pragma: allowlist secret
        python_callable=generate_embeddings
    )
    
    t_train = PythonOperator(
        task_id='train',  # pragma: allowlist secret
        python_callable=train_model
    )
    
    # Dependencies
    t_ingest >> t_embed >> t_train
```

## Weights & Biases Integration

### Experiment Tracking with W&B

```python
import wandb
from src.codex_ml.training.trainer import Trainer

# Initialize W&B
wandb.init(
    project="codex-ml",
    entity="my-team",
    config={
        "model": "bert-base-uncased",
        "batch_size": 32,
        "learning_rate": 2e-5
    }
)

# Train with logging
trainer = Trainer(config=wandb.config)
trainer.train(
    train_data="data/train.jsonl",
    eval_data="data/eval.jsonl",
    callbacks=[WandbCallback()]  # If using Hugging Face Trainer
)

# Log artifacts
wandb.log_artifact("checkpoints/model.pt")

# Finish run
wandb.finish()

# View dashboard: https://wandb.ai/my-team/codex-ml
```

## TensorBoard Integration

### Visualizing Training Metrics

```python
from torch.utils.tensorboard import SummaryWriter
from src.codex_ml.training.trainer import Trainer

writer = SummaryWriter('runs/bert-experiment')

# Training loop
for epoch in range(num_epochs):
    for batch_idx, (inputs, targets) in enumerate(train_loader):
        outputs = model(inputs)
        loss = criterion(outputs, targets)
        
        # Log metrics
        global_step = epoch * len(train_loader) + batch_idx
        writer.add_scalar('Loss/train', loss.item(), global_step)
        writer.add_scalar('Accuracy/train', accuracy, global_step)
        
        loss.backward()
        optimizer.step()

writer.close()

# View: tensorboard --logdir=runs
```

## Docker Integration

### Running Codex in Container

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy code
COPY . .

# Run training
CMD ["python", "train.py"]
```

Build and run:
```bash
docker build -t codex-ml:latest .
docker run --gpus all -v $(pwd)/data:/data codex-ml:latest
```

### Docker Compose for Multi-Service Setup

```yaml
version: '3.8'

services:
  codex-train:
    build: .
    image: codex-ml:latest
    volumes:
      - ./data:/data
      - ./checkpoints:/checkpoints
    environment:
      - CUDA_VISIBLE_DEVICES=0
    command: python train.py

  mlflow:
    image: ghcr.io/mlflow/mlflow:latest
    ports:
      - "5000:5000"
    volumes:
      - ./mlflow:/mlflow
    command: mlflow server --host 0.0.0.0

  tensorboard:
    image: tensorflow/tensorflow:latest
    ports:
      - "6006:6006"
    volumes:
      - ./logs:/logs
    command: tensorboard --logdir=/logs
```

## OpenAI API Integration

### Using Codex with GPT

```python
import openai
from src.rag.pipelines.retrieval import RetrieverPipeline

# Initialize
openai.api_key = "sk-..."  # pragma: allowlist secret
retriever = RetrieverPipeline(k=5)

# RAG workflow
query = "How do transformers work?"
context_docs = retriever.retrieve(query)
context = "\n".join([doc['document'] for doc in context_docs])

# Call GPT
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are an AI expert."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
    ],
    temperature=0.7
)

print(response.choices[0].message.content)
```

## See Also

- [Quickstart Guide](./QUICKSTART.md)
- [Configuration Guide](./CONFIGURATION_GUIDE.md)
- [RAG API Reference](./RAG_API_REFERENCE.md)
- [Troubleshooting Guide](./TROUBLESHOOTING.md)
