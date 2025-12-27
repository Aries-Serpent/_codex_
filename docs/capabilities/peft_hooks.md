# PEFT Hooks - Parameter-Efficient Fine-Tuning

## Overview

**Status**: ✅ Complete - Comprehensive PEFT techniques and integration patterns documented

> **Note**: Code examples throughout this document include imports at the beginning of each snippet for clarity and standalone usage. This is intentional to make each example self-contained and easy to copy.

This capability covers Parameter-Efficient Fine-Tuning (PEFT) techniques and hooks for adapting large models with minimal trainable parameters.

## Planned Content

This document will cover:
- **LoRA**: Low-Rank Adaptation implementation
- **Prefix Tuning**: Learnable prefix tokens
- **Adapter Layers**: Lightweight adapter modules
- **PEFT Library Integration**: Using HuggingFace PEFT
- **Hook Mechanisms**: Custom hooks for PEFT training

## PEFT Techniques

### LoRA (Low-Rank Adaptation)
Fine-tune models by learning low-rank decomposition matrices while keeping original weights frozen.

### Adapter Layers
Insert small trainable modules between frozen transformer layers.

### Prefix Tuning
Learn continuous task-specific vectors prepended to the input.

## Current Implementation

PEFT patterns are integrated throughout _codex_ for efficient model adaptation:
- **agents/** modules - Model adaptation with LoRA, adapters, and prefix tuning
- **tests/** - PEFT testing examples and validation
- **HuggingFace PEFT integration** - Seamless use of the PEFT library
- **Custom hooks** - PyTorch forward/backward hooks for fine-grained control

### Helper Functions

The examples below use these helper functions (see [train_loop.md](train_loop.md) for full implementation):

```python
import torch

def train_epoch(model, train_loader, optimizer, device="cuda"):
    """Basic training epoch - single pass through dataset.
    
    Args:
        model: PyTorch model to train
        train_loader: DataLoader with training data
        optimizer: PyTorch optimizer
        device: Device to train on
    
    Returns:
        Average loss for the epoch
    """
    model.train()
    total_loss = 0.0
    
    for batch in train_loader:
        inputs, targets = batch
        inputs, targets = inputs.to(device), targets.to(device)
        
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = torch.nn.functional.cross_entropy(outputs, targets)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
    
    return total_loss / len(train_loader)
```

### LoRA Implementation

```python
import torch
import torch.nn as nn
from peft import LoraConfig, get_peft_model, TaskType

def apply_lora_to_model(base_model, rank=8, alpha=32, dropout=0.1):
    """Apply LoRA to a transformer model."""
    lora_config = LoraConfig(
        r=rank,  # Rank of the low-rank matrices
        lora_alpha=alpha,  # Scaling factor
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],  # Target attention layers
        lora_dropout=dropout,
        bias="none",
        task_type=TaskType.CAUSAL_LM,
    )
    
    peft_model = get_peft_model(base_model, lora_config)
    
    # Print trainable parameters
    peft_model.print_trainable_parameters()
    # Output: trainable params: 4,194,304 || all params: 1,3427,968,320 || trainable%: 0.31%
    
    return peft_model


# Training with LoRA
model = apply_lora_to_model(base_model)
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)

for epoch in range(num_epochs):
    train_epoch(model, train_loader, optimizer)
```

### Adapter Layers

```python
class AdapterLayer(nn.Module):
    """Lightweight adapter module inserted between frozen layers."""
    
    def __init__(self, input_dim, bottleneck_dim=64):
        super().__init__()
        self.down_project = nn.Linear(input_dim, bottleneck_dim)
        self.activation = nn.GELU()
        self.up_project = nn.Linear(bottleneck_dim, input_dim)
        self.layer_norm = nn.LayerNorm(input_dim)
    
    def forward(self, x):
        # Residual connection
        residual = x
        x = self.down_project(x)
        x = self.activation(x)
        x = self.up_project(x)
        return self.layer_norm(x + residual)


def add_adapters_to_transformer(model, bottleneck_dim=64):
    """Insert adapter layers into a transformer model."""
    for layer in model.transformer.layers:
        # Freeze original parameters
        for param in layer.parameters():
            param.requires_grad = False
        
        # Add adapter after attention
        layer.adapter_attn = AdapterLayer(layer.hidden_size, bottleneck_dim)
        
        # Add adapter after feed-forward
        layer.adapter_ffn = AdapterLayer(layer.hidden_size, bottleneck_dim)
    
    return model
```

### Prefix Tuning

```python
import torch
from peft import PrefixTuningConfig, get_peft_model, TaskType

def apply_prefix_tuning(base_model, num_virtual_tokens=20):
    """Apply prefix tuning to a model."""
    prefix_config = PrefixTuningConfig(
        task_type=TaskType.CAUSAL_LM,
        num_virtual_tokens=num_virtual_tokens,
        encoder_hidden_size=base_model.config.hidden_size,
        prefix_projection=True,  # Use MLP for prefix generation
    )
    
    peft_model = get_peft_model(base_model, prefix_config)
    return peft_model
```

### Custom PEFT Hooks

```python
class PEFTForwardHook:
    """Custom forward hook for monitoring PEFT activations."""
    
    def __init__(self):
        self.activations = {}
    
    def __call__(self, module, input, output):
        """Store activations for analysis."""
        self.activations[module.__class__.__name__] = output.detach()
        return output


class PEFTBackwardHook:
    """Custom backward hook for gradient monitoring."""
    
    def __init__(self):
        self.gradients = {}
    
    def __call__(self, module, grad_input, grad_output):
        """Store gradients for analysis."""
        self.gradients[module.__class__.__name__] = grad_output[0].detach()


def register_peft_hooks(model):
    """Register hooks on PEFT modules."""
    forward_hook = PEFTForwardHook()
    backward_hook = PEFTBackwardHook()
    
    for name, module in model.named_modules():
        if "lora" in name.lower() or "adapter" in name.lower():
            module.register_forward_hook(forward_hook)
            module.register_full_backward_hook(backward_hook)
    
    return forward_hook, backward_hook
```

### Multi-Task PEFT

```python
import torch
from peft import LoraConfig, get_peft_model

def create_multi_task_peft_model(base_model, tasks):
    """Create a model with task-specific LoRA adapters."""
    task_models = {}
    
    for task_name in tasks:
        lora_config = LoraConfig(
            r=8,
            lora_alpha=32,
            target_modules=["q_proj", "v_proj"],
            modules_to_save=[f"task_head_{task_name}"],  # Task-specific heads
        )
        task_models[task_name] = get_peft_model(base_model, lora_config)
    
    return task_models


# Training on multiple tasks
task_models = create_multi_task_peft_model(base_model, ["classification", "generation"])

for epoch in range(num_epochs):
    # Train classification task
    train_epoch(task_models["classification"], classification_loader, optimizer_cls)
    
    # Train generation task
    train_epoch(task_models["generation"], generation_loader, optimizer_gen)
```

## Related Capabilities

- **functional-training**: Training pipeline integration
- **experiment-management**: PEFT experiment tracking
- **inference-serving**: Serving PEFT-adapted models

## Example Usage

```python
from peft import LoraConfig, get_peft_model

# Configure LoRA
lora_config = LoraConfig(
    r=8,  # Rank
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1,
)

# Apply to model
model = get_peft_model(base_model, lora_config)
```

## Best Practices

1. **Choose the Right Technique**
   - **LoRA**: Best for large models, 0.1-1% of parameters trainable
   - **Adapters**: Good balance, 1-5% of parameters trainable
   - **Prefix Tuning**: Efficient for generation tasks, fixed compute cost
   - **Full Fine-Tuning**: Use only for small models or when necessary

2. **Hyperparameter Selection**
   - LoRA rank (r): Start with 8, increase to 16/32 for complex tasks
   - LoRA alpha: Typically 2-4x the rank (e.g., alpha=32 for r=8)
   - Adapter bottleneck: 64-256 dimensions depending on model size
   - Prefix length: 10-30 virtual tokens

3. **Memory Management**
   - PEFT reduces memory by 3-10x vs full fine-tuning
   - Combine with gradient checkpointing for further savings
   - Use 8-bit/4-bit base models with bitsandbytes

4. **Merging Adapters**
   ```python
   # Merge LoRA weights into base model for inference
   model = model.merge_and_unload()
   ```

5. **Multi-Adapter Serving**
   ```python
   # Serve multiple adapters from single base model
   base_model.load_adapter("adapter_task1", adapter_name="task1")
   base_model.load_adapter("adapter_task2", adapter_name="task2")
   base_model.set_adapter("task1")  # Switch active adapter
   ```

## Integration Points

- **Training Loops**: Integrate PEFT models with standard training (see [train_loop.md](train_loop.md))
- **Checkpointing**: Save only adapter weights, not full model (see [checkpointing.md](checkpointing.md))
- **Experiment Tracking**: Log adapter configurations (see [experiment_management.md](experiment_management.md))
- **Inference**: Load adapters dynamically at serving time (see [inference_serving.md](inference_serving.md))

## Performance Comparison

| Method | Trainable % | Memory | Training Speed | Quality |
|--------|-------------|--------|----------------|---------|
| Full Fine-Tuning | 100% | High | Baseline | 100% |
| LoRA (r=8) | 0.3% | 30% | 1.5x faster | 95-99% |
| Adapters | 2% | 40% | 1.3x faster | 97-100% |
| Prefix Tuning | 0.1% | 25% | 1.6x faster | 90-95% |

## Advanced Topics

### QLoRA - Quantized LoRA
```python
import torch
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
)

base_model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b",
    quantization_config=bnb_config,
)

# Apply LoRA to quantized model
model = apply_lora_to_model(base_model)
```

### IA3 - Infused Adapter by Inhibiting and Amplifying Inner Activations
```python
import torch
from peft import IA3Config, get_peft_model, TaskType

ia3_config = IA3Config(
    task_type=TaskType.CAUSAL_LM,
    target_modules=["k_proj", "v_proj", "down_proj"],
    feedforward_modules=["down_proj"],
)

model = get_peft_model(base_model, ia3_config)
```

## References

- [HuggingFace PEFT Library](https://huggingface.co/docs/peft)
- [LoRA Paper (Hu et al., 2021)](https://arxiv.org/abs/2106.09685)
- [QLoRA Paper (Dettmers et al., 2023)](https://arxiv.org/abs/2305.14314)
- [Adapter Layers (Houlsby et al., 2019)](https://arxiv.org/abs/1902.00751)
- [Prefix Tuning (Li & Liang, 2021)](https://arxiv.org/abs/2101.00190)
- [Training Loops](train_loop.md)
- [Functional Training](functional_training.md)
- [Experiment Management](experiment_management.md)
- [Inference Serving](inference_serving.md)
