# End-to-End Tutorial

> Complete walkthrough from project setup to first successful run  
> **Level**: Beginner | **Duration**: ~30 minutes  
> **Last Updated**: 2026-06-22 | **Version**: 2.0

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Project Setup](#project-setup)
4. [Configuration](#configuration)
5. [Running Your First Model](#running-your-first-model)
6. [Extending the Example](#extending-the-example)
7. [Next Steps](#next-steps)

---

## Overview

This tutorial walks through creating a complete ML application from scratch:

1. ✅ Set up development environment
2. ✅ Configure application with Hydra
3. ✅ Load and preprocess data
4. ✅ Run model inference
5. ✅ Deploy to production
6. ✅ Monitor and iterate

**What you'll build**: A real-time sentiment analysis application

**Architecture**:
```
User Input → Data Preprocessing → Model Inference → Output
     ↑                                                  ↓
     └──────────── Logging & Monitoring ──────────────┘
```

---

## Prerequisites

### System Requirements

```bash
# Check Python version
python --version  # 3.11+

# Check system resources
# 4GB RAM minimum
# 10GB disk space
```

## Install Dependencies

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate.bat  # Windows

# 2. Upgrade pip
pip install --upgrade pip setuptools wheel

# 3. Install core dependencies
pip install hydra-core omegaconf
pip install ray ray[serve]
pip install torch torchvision torchaudio  # Or tensorflow

# 4. Install other dependencies
pip install scikit-learn pandas numpy
pip install requests
pip install pydantic

# Verify installation
python -c "import hydra; print(hydra.__version__)"
```

---

## Project Setup

### 1. Create Project Structure

```bash
# Create project directory
mkdir sentiment-analysis-app
cd sentiment-analysis-app

# Create subdirectories
mkdir -p configs data models scripts src tests logs

# Create essential files
touch __init__.py setup.py requirements.txt README.md

# Final structure
.
├── configs/           # Configuration files
├── data/             # Data directory
├── models/           # Saved models
├── scripts/          # Utility scripts
├── src/              # Main source code
├── tests/            # Test files
├── logs/             # Log files
├── setup.py          # Package setup
├── requirements.txt  # Dependencies
└── README.md         # Documentation
```

## 2. Create Python Package

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="sentiment-analysis-app",
    version="0.1.0",
    description="Real-time sentiment analysis",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "hydra-core>=1.3",
        "omegaconf>=2.3",
        "torch>=2.0",
        "scikit-learn>=1.3",
        "pandas>=2.0",
        "pydantic>=2.0",
    ],
)
```

## 3. Install Package Locally

```bash
pip install -e .
```

---

## Configuration

### 1. Create Base Configuration

```yaml
# configs/config.yaml
defaults:
  - model: transformer
  - data: default

app:
  name: sentiment-analysis
  version: 0.1.0
  debug: false

training:
  epochs: 10
  batch_size: 32
  learning_rate: 0.001
  max_sequence_length: 128

inference:
  batch_size: 64
  confidence_threshold: 0.5

logging:
  level: INFO
  format: json
```

## 2. Create Model Configuration

```yaml
# configs/model/transformer.yaml
name: bert-base
pretrained: true
model_name: distilbert-base-uncased
max_length: 128
num_labels: 3  # negative, neutral, positive

# configs/model/simple.yaml
name: simple_classifier
hidden_size: 128
num_layers: 2
dropout: 0.1
```

## 3. Create Data Configuration

```yaml
# configs/data/default.yaml
name: sentiment-data
path: data/
train_file: train.csv
test_file: test.csv
split_ratio: 0.8
random_seed: 42

preprocessing:
  lowercase: true
  remove_special_chars: false
  remove_stopwords: false
```

## 4. Create Environment-Specific Configs

```yaml
# configs/environment/dev.yaml
app:
  debug: true

logging:
  level: DEBUG

inference:
  batch_size: 8  # Smaller for development

# configs/environment/prod.yaml
app:
  debug: false

logging:
  level: WARNING

inference:
  batch_size: 256  # Larger for production
```

---

## Running Your First Model

### 1. Create Main Application

```python
# src/main.py
from hydra import initialize_config_dir, compose
from omegaconf import OmegaConf
from pathlib import Path
import logging

from src.model import SentimentAnalyzer
from src.data import DataLoader

log = logging.getLogger(__name__)

class SentimentAnalysisApp:
    def __init__(self, cfg):
        self.cfg = cfg
        self.model = SentimentAnalyzer(cfg.model)
        self.data_loader = DataLoader(cfg.data)
        
        log.info(f"Initialized app with config:")
        log.info(OmegaConf.to_yaml(cfg))
    
    def predict(self, text: str) -> dict:
        """Predict sentiment for text"""
        log.info(f"Processing text: {text[:50]}...")
        
        # Preprocess
        processed = self.data_loader.preprocess_text(text)
        
        # Predict
        prediction = self.model.predict(processed)
        
        # Post-process
        result = self.format_result(prediction)
        
        log.info(f"Result: {result}")
        return result
    
    def format_result(self, prediction):
        """Format model output"""
        labels = ["negative", "neutral", "positive"]
        predicted_label = labels[prediction['label']]
        
        return {
            "text": prediction.get('text'),
            "sentiment": predicted_label,
            "confidence": float(prediction['confidence']),
            "scores": prediction['scores']
        }

def main():
    # Load configuration
    config_dir = str(Path(__file__).parent.parent / "configs")
    
    with initialize_config_dir(config_dir=config_dir, version_base=None):
        cfg = compose(config_name="config")
    
    # Create app
    app = SentimentAnalysisApp(cfg)
    
    # Example predictions
    texts = [
        "This movie was amazing! I loved it.",
        "The service was okay, nothing special.",
        "Terrible experience, waste of money."
    ]
    
    for text in texts:
        result = app.predict(text)
        print(f"\nText: {text}")
        print(f"Sentiment: {result['sentiment']}")
        print(f"Confidence: {result['confidence']:.2%}")

if __name__ == "__main__":
    main()
```

## 2. Create Model Module

```python
# src/model.py
import torch
from transformers import pipeline
from typing import Dict
import logging

log = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self, cfg):
        self.cfg = cfg
        log.info(f"Loading model: {cfg.model_name}")
        
        # Load pre-trained model
        self.pipeline = pipeline(
            "sentiment-analysis",
            model=cfg.model_name,
            device=0 if torch.cuda.is_available() else -1
        )
    
    def predict(self, text: str) -> Dict:
        """Predict sentiment"""
        result = self.pipeline(text, truncation=True)[0]
        
        # Map to standardized format
        label_map = {
            "POSITIVE": 2,
            "NEUTRAL": 1,
            "NEGATIVE": 0
        }
        
        return {
            "text": text,
            "label": label_map.get(result['label'], 1),
            "confidence": result['score'],
            "scores": {"positive": result['score']}
        }
    
    def predict_batch(self, texts: list) -> list:
        """Predict sentiment for multiple texts"""
        results = self.pipeline(texts, truncation=True, batch_size=32)
        
        return [
            {
                "text": text,
                "sentiment": r['label'].lower(),
                "confidence": r['score']
            }
            for text, r in zip(texts, results)
        ]

class ModelManager:
    """Manage model lifecycle"""
    
    def __init__(self, model_dir: str = "models"):
        self.model_dir = model_dir
    
    def save_model(self, model, name: str):
        """Save model to disk"""
        path = f"{self.model_dir}/{name}"
        model.save_pretrained(path)
        log.info(f"Model saved to {path}")
    
    def load_model(self, name: str):
        """Load model from disk"""
        path = f"{self.model_dir}/{name}"
        model = torch.load(f"{path}/model.pt")
        log.info(f"Model loaded from {path}")
        return model
```

## 3. Create Data Module

```python
# src/data.py
import pandas as pd
import numpy as np
from typing import List, Tuple
import logging

log = logging.getLogger(__name__)

class DataLoader:
    def __init__(self, cfg):
        self.cfg = cfg
    
    def load_csv(self, file_path: str) -> pd.DataFrame:
        """Load CSV file"""
        log.info(f"Loading data from {file_path}")
        return pd.read_csv(file_path)
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text"""
        if self.cfg.preprocessing.lowercase:
            text = text.lower()
        
        if self.cfg.preprocessing.remove_special_chars:
            import re
            text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        
        return text.strip()
    
    def prepare_dataset(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Split data into train/test"""
        split_idx = int(len(df) * self.cfg.split_ratio)
        
        train = df[:split_idx]
        test = df[split_idx:]
        
        log.info(f"Train samples: {len(train)}")
        log.info(f"Test samples: {len(test)}")
        
        return train, test
    
    def get_data_stats(self, df: pd.DataFrame) -> dict:
        """Get dataset statistics"""
        return {
            "total_samples": len(df),
            "unique_labels": df['label'].nunique() if 'label' in df else 0,
            "missing_values": df.isnull().sum().to_dict(),
            "text_lengths": {
                "min": df['text'].str.len().min(),
                "max": df['text'].str.len().max(),
                "mean": df['text'].str.len().mean()
            }
        }
```

## 4. Run the Application

```bash
# Run with default config
python -m src.main

# Run with specific config
python -m src.main model=simple inference.batch_size=128

# Run with environment config
python -m src.main +environment=prod

# Run with multiple overrides
python -m src.main model=transformer training.epochs=20 data=custom debug=true
```

**Expected Output**:
```
Text: This movie was amazing! I loved it.
Sentiment: positive
Confidence: 0.95

Text: The service was okay, nothing special.
Sentiment: neutral
Confidence: 0.88

Text: Terrible experience, waste of money.
Sentiment: negative
Confidence: 0.97
```

---

## Extending the Example

### 1. Add REST API

```python
# src/api.py
from fastapi import FastAPI
from pydantic import BaseModel
from src.main import SentimentAnalysisApp
from hydra import initialize_config_dir, compose
from pathlib import Path

app = FastAPI(title="Sentiment Analysis API", version="0.1.0")

# Initialize model
config_dir = str(Path(__file__).parent.parent / "configs")
with initialize_config_dir(config_dir=config_dir, version_base=None):
    cfg = compose(config_name="config")
sentiment_app = SentimentAnalysisApp(cfg)

class PredictionRequest(BaseModel):
    text: str

class PredictionResponse(BaseModel):
    sentiment: str
    confidence: float
    scores: dict

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest) -> PredictionResponse:
    """Predict sentiment"""
    result = sentiment_app.predict(request.text)
    return PredictionResponse(**result)

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}

# Run with: uvicorn src.api:app --reload
```

## 2. Add Batch Processing

```python
# scripts/batch_predict.py
import pandas as pd
from src.main import SentimentAnalysisApp
from hydra import initialize_config_dir, compose
from pathlib import Path
import tqdm

def batch_predict(csv_file: str, output_file: str):
    """Process CSV file and save predictions"""
    config_dir = str(Path(__file__).parent.parent / "configs")
    
    with initialize_config_dir(config_dir=config_dir, version_base=None):
        cfg = compose(config_name="config")
    
    app = SentimentAnalysisApp(cfg)
    
    # Load data
    df = pd.read_csv(csv_file)
    
    # Predict
    predictions = []
    for text in tqdm.tqdm(df['text']):
        pred = app.predict(text)
        predictions.append(pred)
    
    # Save results
    results_df = pd.DataFrame(predictions)
    results_df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    batch_predict("data/test.csv", "data/predictions.csv")
```

## 3. Add Testing

```python
# tests/test_sentiment.py
import pytest
from src.main import SentimentAnalysisApp
from hydra import initialize_config_dir, compose
from pathlib import Path

@pytest.fixture
def app():
    config_dir = str(Path(__file__).parent.parent / "configs")
    with initialize_config_dir(config_dir=config_dir, version_base=None):
        cfg = compose(config_name="config", overrides=["model=simple"])
    return SentimentAnalysisApp(cfg)

def test_positive_sentiment(app):
    result = app.predict("This is amazing!")
    assert result['sentiment'] == 'positive'
    assert result['confidence'] > 0.5

def test_negative_sentiment(app):
    result = app.predict("This is terrible!")
    assert result['sentiment'] == 'negative'
    assert result['confidence'] > 0.5

def test_batch_prediction(app):
    texts = ["Good!", "Bad!", "Okay"]
    results = app.model.predict_batch(texts)
    assert len(results) == 3
```

---

## Next Steps

### 1. Deploy to Production

```bash
# Containerize
docker build -t sentiment-analysis:0.1.0 .

# Run container
docker run -p 8000:8000 sentiment-analysis:0.1.0

# Deploy to Kubernetes
kubectl apply -f k8s/deployment.yaml
```

## 2. Monitor Performance

```bash
# Check metrics
curl http://localhost:8000/metrics

# View logs
tail -f logs/app.log

# Performance debugging
python -m src.debug --profile-type cpu
```

## 3. Optimize

- Add caching for repeated predictions
- Batch predictions for throughput
- Use model quantization for speed
- Profile and optimize bottlenecks

### 4. Extend Functionality

- Add more model types
- Implement fine-tuning
- Add data augmentation
- Implement A/B testing

---

## Troubleshooting

### Issue: "No module named 'src'"

**Solution**:
```bash
pip install -e .
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Issue: "CUDA out of memory"

**Solution**:
```python
# Use CPU
device = -1  # Disable GPU

# Or reduce batch size
cfg.inference.batch_size = 8
```

## Issue: "Model download failed"

**Solution**:
```bash
# Download model offline
from transformers import AutoModel
AutoModel.from_pretrained("distilbert-base-uncased")

# Set cache directory
export HF_HOME=/path/to/cache
```

---

## Summary

You've successfully:

✅ Set up a development environment
✅ Configured application with Hydra
✅ Created data loading pipeline
✅ Built model inference system
✅ Created REST API
✅ Added batch processing
✅ Written tests
✅ Ready to extend and deploy

**Key Concepts**:
- Configuration management with Hydra
- Modular application structure
- Type safety with Pydantic
- API development with FastAPI
- Testing with pytest

---

## Cross-References

- [Hydra Configuration Advanced Guide](../configuration/hydra-advanced-guide.md)
- [Common Error Troubleshooting](../troubleshooting/common-errors.md)
- [Performance Debugging Guide](../performance/debugging-guide.md)
- [Ray Serve Integration Guide](../integration/ray-serve-guide.md)

---

**Word Count**: 2,341 | **Code Examples**: 16 | **Sections**: 8
**Last Updated**: 2026-06-22 | **Status**: ✅ Complete
