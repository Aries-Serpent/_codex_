## Getting Started Guide for Data Scientists
**Last Updated:** 2026-07-11
**Version:** v0.2.0

**Last Updated: 2026-07-08
**Target Audience:** Data scientists, ML researchers, model developers
**Estimated Time:** 15-20 minutes to first model

## Your Goal

Transform raw data into trained ML models using Codex ML's integrated training pipeline. This guide covers data loading, model training, evaluation, and experimentation tracking.

---

## Phase 1: Environment Setup (5 minutes)

### Option A: Docker (Recommended)

```bash
# Pull the data science optimized image
docker run -it \
 -v $(pwd)/data:/workspace/data \
 -v $(pwd)/outputs:/workspace/outputs \
 --gpus all \
 codex-ml:data-science
```

### Option B: Local Virtual Environment

```bash
# Create a fresh environment
python -m venv ~/codex-ds
source ~/codex-ds/bin/activate

# Install Codex ML with ML stack
pip install --upgrade pip
pip install 'codex-ml[ml]'

# Verify installation
python -c "from codex_ml.training import TrainingEngine; print(' Ready to train!')"
```

### Verify Your Setup

```bash
# Check PyTorch is GPU-enabled
python -c "import torch; print(f'GPU Available: {torch.cuda.is_available()}')"

# Check Hugging Face access
python -c "from transformers import AutoModel; print(' Transformers ready')"

# Check configuration system
codex config show
```

---

## Phase 2: Your First Training Job (10 minutes)

### Step 1: Prepare Your Data

Create a CSV with your data:

```csv
text,label
"This is great!",positive
"This is terrible.",negative
"Mixed feelings here.",neutral
```

Save as `data/sentiment.csv`

### Step 2: Configure Training

Create `config/sentiment_experiment.yaml`:

```yaml
experiment_name: sentiment-v1
output_dir: outputs/sentiment-v1

model:
 name: distilbert-base-uncased
 task: sequence-classification
 num_labels: 3

training:
 max_epochs: 3
 batch_size: 16
 learning_rate: 2e-5
 warmup_steps: 100
 
data:
 train_split: 0.8
 val_split: 0.1
 test_split: 0.1
 text_column: text
 label_column: label

optimization:
 precision: bf16 # Use mixed precision
 gradient_accumulation_steps: 2
```

### Step 3: Train

```bash
codex train \
 --config-path config/sentiment_experiment.yaml \
 --data-path data/sentiment.csv \
 --output-dir outputs/sentiment-v1

# Alternative using Python API
python -c "
from codex_ml.training import TrainingEngine
from pathlib import Path

engine = TrainingEngine.from_config('config/sentiment_experiment.yaml')
metrics = engine.train(Path('data/sentiment.csv'))
print(f'Accuracy: {metrics[\"accuracy\"]:.2%}')
print(f'Model saved to: {engine.output_dir}')
"
```

### Step 4: Evaluate

```bash
codex evaluate \
 --model-path outputs/sentiment-v1/final \
 --data-path data/sentiment.csv \
 --metrics accuracy f1 precision recall

# Output will show:
# Accuracy: 89.5%
# F1 Score: 0.892
# Precision: 0.891
# Recall: 0.893
```

---

## Phase 3: Experiment Tracking (5 minutes)

### Option A: Built-in Experiment Logger

```python
from codex_ml.training import TrainingEngine, ExperimentTracker

# All training runs are automatically logged
tracker = ExperimentTracker()

# View your experiments
experiments = tracker.list_experiments()
for exp in experiments:
 print(f"{exp.name}: {exp.status} (Acc: {exp.metrics['accuracy']:.2%})")

# Compare runs side-by-side
tracker.compare_experiments([
 'sentiment-v1',
 'sentiment-v2', 
 'sentiment-v3'
])
```

### Option B: MLflow Integration

```python
from codex_ml.training import TrainingEngine
import mlflow

mlflow.set_experiment("sentiment-analysis")

with mlflow.start_run(run_name="v1-baseline"):
 engine = TrainingEngine.from_config('config/sentiment_experiment.yaml')
 metrics = engine.train(Path('data/sentiment.csv'))
 
 # Auto-log metrics
 mlflow.log_metrics(metrics)
 mlflow.log_artifact("config/sentiment_experiment.yaml")
 mlflow.log_model(engine.model, "model")

# View in MLflow UI
# mlflow ui --host 0.0.0.0 --port 5000
```

---

## Phase 4: Advanced Workflows

### Hyperparameter Tuning

```python
from codex_ml.training import TrainingEngine, HyperparameterTuner

# Define parameter space
param_space = {
 'learning_rate': [1e-5, 2e-5, 5e-5],
 'batch_size': [8, 16, 32],
 'num_epochs': [3, 5, 7],
}

# Run grid search
tuner = HyperparameterTuner(
 config_template='config/sentiment_experiment.yaml',
 param_space=param_space,
 metric_to_optimize='accuracy',
 n_trials=27 # 3^3 grid
)

best_config, best_metrics = tuner.tune(
 data_path='data/sentiment.csv',
 output_dir='outputs/hp-tuning'
)

print(f"Best accuracy: {best_metrics['accuracy']:.2%}")
print(f"Best config:\n{best_config}")
```

### Transfer Learning with LoRA

```python
from codex_ml.training import TrainingEngine, LoRAAdapter

# Use pre-trained model with LoRA fine-tuning
config = {
 'model': {
 'name': 'mistral-7b',
 'task': 'causal-lm',
 'use_lora': True, # Enable LoRA
 },
 'lora': {
 'r': 8, # LoRA rank
 'lora_alpha': 16, # Scaling factor
 'lora_dropout': 0.05, # Regularization
 'target_modules': ['q_proj', 'v_proj'], # Which layers to adapt
 },
 'training': {
 'max_epochs': 3,
 'batch_size': 16,
 'learning_rate': 2e-4,
 'precision': 'bf16',
 }
}

engine = TrainingEngine(config)
metrics = engine.train(Path('data/sentiment.csv'))
```

### Data Caching & Preprocessing

```python
from codex_ml.data import DataLoader, Preprocessor

# Load with caching
loader = DataLoader(cache_dir='./cache')
dataset = loader.load_csv('data/sentiment.csv')

# Preprocess pipeline
preprocessor = Preprocessor(steps=[
 ('tokenize', {'max_length': 128}),
 ('normalize', {'lowercase': True, 'remove_special': True}),
 ('augment', {'techniques': ['backtranslate']}),
])

processed = preprocessor.fit_transform(dataset)
# Auto-cached for future runs
```

---

## Phase 5: Troubleshooting

### Issue: Out of Memory (OOM)

**Solution:**
```yaml
training:
 batch_size: 8 # Reduce from 16
 gradient_accumulation_steps: 4 # Compensate for less frequent updates
 precision: bf16 # Use mixed precision
```

Or reduce model size:
```yaml
model:
 name: distilbert-base-uncased # Smaller than bert-base
 # or
 name: TinyBERT-6L-768D # Even smaller
```

### Issue: Training Too Slow

**Solution:**
```python
# Use data parallel training across multiple GPUs
engine = TrainingEngine(
 config='config/sentiment_experiment.yaml',
 distributed=True,
 num_gpus=4
)

# Or sample your data during development
small_dataset = dataset.sample(frac=0.1) # Use 10% for quick iteration
```

### Issue: Poor Model Performance

**Solution:**
```python
# 1. Check data quality
from codex_ml.data import DataQualityAnalyzer
analyzer = DataQualityAnalyzer()
report = analyzer.analyze(dataset)
print(report) # Shows missing values, imbalance, etc.

# 2. Visualize attention
from codex_ml.interpretability import AttentionVisualizer
visualizer = AttentionVisualizer(model)
visualizer.plot(text="Your sample text")

# 3. Analyze errors
from codex_ml.analysis import ErrorAnalyzer
error_analyzer = ErrorAnalyzer(model, test_dataset)
hard_examples = error_analyzer.find_hard_examples(k=20)
```

---

## Phase 6: Production Export

### Export for Deployment

```python
from codex_ml.serving import ModelExporter

exporter = ModelExporter(model, task='sequence-classification')

# Export to ONNX (fast inference, portable)
exporter.export_onnx('outputs/model.onnx')

# Export to TorchScript (preserves dynamic shapes)
exporter.export_torchscript('outputs/model.pt')

# Export for serverless (small, quantized)
exporter.export_quantized(
 'outputs/model-quantized.onnx',
 quantization_bits=8
)
```

### Quick Inference

```python
from codex_ml.serving import LocalPredictor

predictor = LocalPredictor('outputs/sentiment-v1/final')

# Single prediction
result = predictor.predict("This product is !")
print(f"Prediction: {result['label']} (confidence: {result['confidence']:.2%})")

# Batch prediction
results = predictor.predict_batch([
 "Great product!",
 "Terrible experience.",
 "It's okay, nothing special.",
])

for text, pred in zip(texts, results):
 print(f"{text} {pred['label']}")
```

---

## Next Steps

- **Explore Fine-tuning**: Check [Fine-tuning Guide](./FINE_TUNING_GUIDE.md)
- **Build Ensemble**: See [Ensemble Methods](./ENSEMBLE_GUIDE.md)
- **Optimize Speed**: Read [Performance Optimization](./PERFORMANCE_OPTIMIZATION.md)
- **Deploy to Cloud**: Follow [Cloud Deployment](../admin/CLOUD_DEPLOYMENT.md)

## 🆘 Getting Help

- **Ask Questions**: [GitHub Discussions](https://github.com/Aries-Serpent/_codex_/discussions)
- **Report Issues**: [GitHub Issues](https://github.com/Aries-Serpent/_codex_/issues)
- **Chat with Community**: [Discord Server](https://discord.gg/codex-ml)

---

**Happy experimenting! **
