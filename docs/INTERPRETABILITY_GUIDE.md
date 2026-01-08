# ML Interpretability Module

The ML Interpretability module provides tools for analyzing and interpreting machine learning models, with a focus on transformer architectures.

## Overview

This module includes two main components:

1. **AttentionScorer** - Analyzes attention patterns in transformer models
2. **MLPScorer** - Analyzes MLP (feed-forward) layer activations

## Installation

The interpretability module is included in the main `codex` package:

```bash
pip install -e .
```

## Quick Start

### Attention Analysis

```python
from transformers import AutoModel, AutoTokenizer
from codex.interpretability import AttentionScorer

# Load model and tokenizer
model = AutoModel.from_pretrained("bert-base-uncased")
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Create scorer
scorer = AttentionScorer(model)

# Analyze text
text = "The quick brown fox jumps over the lazy dog"
inputs = tokenizer(text, return_tensors="pt")

analysis = scorer.analyze_attention(
    input_ids=inputs["input_ids"],
    attention_mask=inputs["attention_mask"],
    tokens=tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
)

# Get most important tokens
top_tokens = scorer.get_top_attended_tokens(analysis, top_k=5)
for idx, score, token in top_tokens:
    print(f"{token}: {score:.4f}")
```

### MLP Analysis

```python
from codex.interpretability import MLPScorer

# Create scorer
scorer = MLPScorer(model)

# Analyze activations
analysis = scorer.analyze_mlp(
    input_ids=inputs["input_ids"],
    attention_mask=inputs["attention_mask"]
)

# Get top activated neurons per layer
top_neurons = scorer.get_top_neurons(analysis, top_k=10)
for layer_idx, neurons in top_neurons.items():
    print(f"\nLayer {layer_idx}:")
    for neuron_idx, importance in neurons:
        print(f"  Neuron {neuron_idx}: {importance:.4f}")

# Identify dead neurons
dead_neurons = scorer.get_dead_neurons(analysis, threshold=0.99)
for layer_idx, neuron_indices in dead_neurons.items():
    print(f"Layer {layer_idx} has {len(neuron_indices)} dead neurons")
```

## Features

### AttentionScorer

- **Extract attention weights** from all transformer layers
- **Compute token importance** based on attention patterns
- **Analyze attention flow** between tokens
- **Identify key tokens** that receive the most attention
- Support for multiple aggregation methods (mean, max, norm)

### MLPScorer

- **Extract MLP activations** from feed-forward layers
- **Compute neuron importance** based on activation patterns
- **Analyze activation statistics** (mean, std, min, max, sparsity)
- **Identify dead neurons** with minimal activation
- **Compare activations** between different inputs

## Advanced Usage

### Custom Importance Methods

AttentionScorer supports multiple methods for computing token importance:

```python
# Mean attention received (default)
analysis = scorer.analyze_attention(
    input_ids=inputs["input_ids"],
    importance_method="mean"
)

# Maximum attention received
analysis = scorer.analyze_attention(
    input_ids=inputs["input_ids"],
    importance_method="max"
)

# L2 norm of attention
analysis = scorer.analyze_attention(
    input_ids=inputs["input_ids"],
    importance_method="norm"
)
```

### Attention Flow Visualization

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Analyze attention
analysis = scorer.analyze_attention(
    input_ids=inputs["input_ids"],
    tokens=tokens
)

# Visualize attention flow matrix
plt.figure(figsize=(10, 8))
sns.heatmap(
    analysis.attention_flow,
    xticklabels=analysis.tokens,
    yticklabels=analysis.tokens,
    cmap='viridis'
)
plt.title("Attention Flow Between Tokens")
plt.xlabel("Target Tokens")
plt.ylabel("Source Tokens")
plt.show()
```

### Comparing Different Inputs

```python
# Prepare two different inputs
text1 = "The cat sat on the mat"
text2 = "The dog lay on the rug"

inputs1 = tokenizer(text1, return_tensors="pt")
inputs2 = tokenizer(text2, return_tensors="pt")

# Compare MLP activations
comparison = mlp_scorer.compare_inputs(
    input_ids_1=inputs1["input_ids"],
    input_ids_2=inputs2["input_ids"],
    attention_mask_1=inputs1["attention_mask"],
    attention_mask_2=inputs2["attention_mask"]
)

# Analyze differences
print("Layer-wise correlation:", comparison['correlation'])
print("Layer-wise L2 distance:", comparison['l2_distance'])
```

### Activation Statistics

```python
# Analyze MLP
analysis = mlp_scorer.analyze_mlp(
    input_ids=inputs["input_ids"],
    attention_mask=inputs["attention_mask"]
)

# Access statistics for each layer
for layer_idx, layer_name in enumerate(analysis.layer_names):
    print(f"\n{layer_name}:")
    print(f"  Mean activation: {analysis.layer_stats['mean'][layer_idx].mean():.4f}")
    print(f"  Std activation: {analysis.layer_stats['std'][layer_idx].mean():.4f}")
    print(f"  Sparsity: {analysis.layer_stats['sparsity'][layer_idx].mean():.4f}")
```

## API Reference

### AttentionScorer

#### `__init__(model, normalize=True, device=None)`
- **model**: PyTorch transformer model
- **normalize**: Whether to normalize attention scores
- **device**: Device to run analysis on (cuda/cpu)

#### `analyze_attention(input_ids, attention_mask=None, tokens=None, importance_method="mean", flow_aggregation="mean")`
- Returns `AttentionAnalysis` object with complete attention analysis

#### `get_top_attended_tokens(analysis, top_k=5)`
- Returns list of (token_index, importance_score, token_string) tuples

### MLPScorer

#### `__init__(model, normalize=True, device=None)`
- **model**: PyTorch transformer model
- **normalize**: Whether to normalize activation scores
- **device**: Device to run analysis on (cuda/cpu)

#### `analyze_mlp(input_ids, attention_mask=None, importance_method="mean_abs")`
- Returns `MLPAnalysis` object with complete MLP analysis

#### `get_top_neurons(analysis, top_k=10)`
- Returns dict mapping layer indices to lists of (neuron_index, importance) tuples

#### `get_dead_neurons(analysis, threshold=0.99)`
- Returns dict mapping layer indices to lists of dead neuron indices

#### `compare_inputs(input_ids_1, input_ids_2, attention_mask_1=None, attention_mask_2=None)`
- Returns dict with comparison metrics (diff, correlation, l2_distance)

## Performance Considerations

- **GPU Acceleration**: Both scorers automatically use GPU if available
- **Batch Processing**: Currently optimized for single examples; batch support coming soon
- **Memory Usage**: Attention analysis stores full attention matrices; use caution with long sequences
- **Hook-based Extraction**: Falls back to hook-based extraction if model doesn't support standard interfaces

## Compatibility

- **Supported Models**: All Hugging Face Transformers models (BERT, GPT-2, T5, etc.)
- **PyTorch Version**: Requires PyTorch >= 2.0
- **Python Version**: Python 3.8+

## Examples

See the `examples/interpretability/` directory for complete examples:

- `attention_analysis.py` - Complete attention analysis workflow
- `mlp_analysis.py` - MLP activation analysis
- `model_comparison.py` - Comparing different models
- `visualization.py` - Creating visualizations

## Contributing

Contributions are welcome! Please see `CONTRIBUTING.md` for guidelines.

## Citation

If you use this module in your research, please cite:

```bibtex
@software{codex_interpretability,
  title = {Codex ML Interpretability Module},
  author = {Aries-Serpent},
  year = {2024},
  url = {https://github.com/Aries-Serpent/_codex_}
}
```

## License

This module is part of the Codex project and is licensed under the same terms. See `LICENSE` for details.
