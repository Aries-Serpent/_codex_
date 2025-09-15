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

When LoRA is active the HF training engine emits a warning and forces
`gradient_accumulation_steps` to `1` to ensure adapter parameters receive full
updates.

## Adding new models

Use `codex_ml.registry.register_model` to attach new constructors or ship an
entry point in your package (see [docs/dev/plugins.md](../dev/plugins.md)).
Example configurations are listed in
[docs/examples/training-configs.md](../examples/training-configs.md).
