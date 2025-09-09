# Model Registry

The model registry provides a lightweight mechanism to construct models by name
and optionally apply LoRA adapters.

## Available models

- `MiniLM` – small transformer used for tests.
- `bert-base-uncased` – example entry that delegates to
  `transformers.AutoModelForCausalLM`.  The model must be available in the local
  HuggingFace cache.

## Configuration

```yaml
model:
  name: MiniLM
  pretrained_model_name_or_path: null
  dtype: float32
  device: cpu
  lora:
    enabled: false
    r: 8
    alpha: 16
    dropout: 0.1
```

Enable LoRA adapters via command line overrides:

```bash
python -m codex_ml.cli.main model.lora.enabled=true model.lora.r=4
```

## Adding new models

Extend `MODEL_REGISTRY` in `codex_ml.models.registry` or use the
`@register_model` decorator to register a constructor function.
