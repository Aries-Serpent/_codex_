# Aries-Serpent ML v0.2.0-beta3 Quick Start Guide
**Last Updated:** 2026-07-11
**Version:** v0.2.0

Welcome! This guide shows you how to get started with the Aries-Serpent ML package.

## Installation

### From PyPI (Recommended)
```bash
pip install aries-serpent-ml
```

### From Source
```bash
# Clone and install
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_
pip install -e ".[ml]"
```

### From Distribution Archive
```bash
tar -xzf aries-serpent-ml-0.1.0-beta3.tar.gz
cd aries-serpent-ml-0.1.0-beta3
pip install .
```

## Quick Examples

### Example 1: BERT Sentiment Classification (5 lines)

```python
from codex_ml import ModelHandle
from codex_ml.hf_loader import load_model

# Load a pre-trained BERT model
model = load_model("bert-base-uncased")

# Make predictions
texts = ["I love this product!", "This is awful."]
predictions = model.predict(texts)

print(predictions)  # [positive, negative]
```

### Example 2: GPT-2 Fine-Tuning (10 lines)

```python
from codex_ml import TrainingWeights
from codex_ml.codex_model import CodexModel

# Initialize model
model = CodexModel.from_pretrained("gpt2")

# Fine-tuning config
weights = TrainingWeights(
    learning_rate=2e-5,
    batch_size=32,
    epochs=3
)

# Start training
model.train(train_dataset, weights)
model.save("./my_finetuned_gpt2")
```

### Example 3: Custom Metrics (Data Validation)

```python
from codex_ml import MetricRegistry, F1Score, RecallScore

# Register custom metrics
registry = MetricRegistry()
registry.register("f1", F1Score())
registry.register("recall", RecallScore())

# Compute metrics
f1 = registry.get("f1")(predictions, ground_truth)
recall = registry.get("recall")(predictions, ground_truth)

print(f"F1: {f1:.3f}, Recall: {recall:.3f}")
```

### Example 4: Inference Optimization

```python
from codex_ml.codex_model import CodexModel

# Load model (inference mode)
model = CodexModel.from_pretrained("bert-base-uncased", 
                                   mode="inference")

# Batch inference (optimized)
batch_texts = ["text1", "text2", "text3", ...]
results = model.predict_batch(batch_texts, batch_size=64)

# Get latency metrics
latency = model.get_inference_latency()
print(f"Inference latency: {latency:.2f}ms/sample")
```

## Core APIs

### Model Loading
- `load_model(name)` - Load pre-trained models
- `CodexModel.from_pretrained()` - Full control over model loading
- `ModelHandle` - Encapsulates model metadata

### Training
- `TrainingWeights` - Configuration for training
- `SFTConfig` - Supervised fine-tuning configuration
- `RLHFConfig` - Reinforcement Learning from Human Feedback

### Evaluation
- `MetricRegistry` - Register and retrieve metrics
- Built-in metrics: `F1Score`, `RecallScore`, `BLEUScore`
- `EvaluatorProtocol` - Protocol for custom evaluators

### Checkpointing
- `CheckpointManager` - Save/load model checkpoints
- `load_checkpoint()` / `save_checkpoint()` - Direct checkpoint operations
- Automatic best-k checkpoint retention

## Configuration

### Using Hydra Configuration

```python
from codex_ml.config_schema import PretrainingConfig
from hydra import compose, initialize_config_dir
import os

# Load config
config_dir = os.path.join(os.getcwd(), "configs")
with initialize_config_dir(config_dir=config_dir, version_base="1.1"):
    cfg = compose(config_name="training")
    print(cfg)
```

### Key Configuration Options
- `model_name` - Pre-trained model identifier
- `learning_rate` - Training learning rate
- `batch_size` - Training batch size
- `max_epochs` - Maximum epochs
- `checkpoint_dir` - Where to save checkpoints

## Integration with Aries-Serpent Core

The ML package is designed to work seamlessly with the Aries-Serpent core utilities:

```python
from codex.protocols.ml_protocols import TrainerProtocol, ModelProtocol
from codex_ml.codex_model import CodexModel

# Use protocol-based architecture for flexible training
model: ModelProtocol = CodexModel.from_pretrained("bert-base-uncased")
# Trainer will accept any ModelProtocol implementation
```

## Advanced Usage

### Custom Dataset Protocol

```python
from codex.protocols.ml_protocols import DatasetProtocol
from typing import Iterator

class MyDataset(DatasetProtocol):
    def __iter__(self) -> Iterator:
        # Implement your dataset loading logic
        pass
    
    def __len__(self) -> int:
        # Return dataset size
        pass

# Use with trainer
trainer.fit(MyDataset())
```

### Protocol-Based Trainer Hookup

```python
from codex_ml.codex_model import CodexModel
from codex.protocols.ml_protocols import TrainerProtocol

# Any object implementing TrainerProtocol can work with our models
class CustomTrainer(TrainerProtocol):
    def fit(self, model, dataset, config):
        # Your custom training logic
        pass

trainer = CustomTrainer()
model = CodexModel.from_pretrained("bert-base-uncased")
trainer.fit(model, dataset, training_config)
```

## Performance Benchmarks

### BERT Inference (CPU)
- Model: bert-base-uncased
- Sequence Length: 128
- Batch Size: 32
- Latency: ~45-60ms/sample
- Throughput: ~16-22 samples/sec

### GPT-2 Generation (CPU)
- Model: gpt2
- Max Length: 100 tokens
- Batch Size: 8
- Latency: ~150-200ms/sample
- Throughput: ~5-7 samples/sec

### Fine-tuning (GPU)
- Model: roberta-base
- Dataset: 10K samples
- Batch Size: 32
- Epochs: 3
- Time: ~15-20 minutes (on V100)
- Final Loss: ~0.15

## Troubleshooting

### Import Errors
```python
# If you get "No module named 'torch'"
pip install torch transformers

# For GPU support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Memory Issues
```python
# Reduce batch size
config.batch_size = 8  # from 32

# Use gradient checkpointing
model.enable_gradient_checkpointing()

# Use mixed precision
trainer.use_mixed_precision = True
```

### Model Loading Failures
```python
# Verify HuggingFace is accessible
from transformers import AutoModel
model = AutoModel.from_pretrained("bert-base-uncased")

# Or download manually
# https://huggingface.co/bert-base-uncased
```

## Documentation & Resources

- **Full API Docs**: See `docs/ml/API_REFERENCE.md`
- **Fine-tuning Guide**: See `docs/ml/FINE_TUNING.md`
- **Integration Patterns**: See `docs/ml/INTEGRATION_PATTERNS.md`
- **GitHub Issues**: https://github.com/Aries-Serpent/_codex_/issues
- **Discussions**: https://github.com/Aries-Serpent/_codex_/discussions

## What's Next?

1. **Explore Examples**: Check out `examples/ml/` for complete working examples
2. **Run Benchmarks**: Execute `scripts/ml/benchmark_inference.py`
3. **Join Community**: Share your use cases on GitHub Discussions
4. **Report Issues**: Found a bug? Open an issue on GitHub

## Version Info

- **Package**: aries-serpent-ml
- **Version**: 0.1.0-beta3
- **Release Date**: July 9, 2026
- **Python**: 3.12+
- **License**: Apache 2.0

---

**Happy ML Training! **

For questions or feedback, please reach out on GitHub Discussions or open an issue.
