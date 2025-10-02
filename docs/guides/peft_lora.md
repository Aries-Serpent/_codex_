# PEFT / LoRA (optional)

LoRA adapters can be toggled on without changing your base weights. This repo treats PEFT as **opt-in**:

```bash
pip install -e '.[ml]'        # includes transformers+peft
```

Minimal example (see `codex_ml/models/peft_hooks.py`):

```python
from codex_ml.models.peft_hooks import build_lora, LoraBuildCfg
model = ...  # any tiny HF model (CPU is fine)
model = build_lora(model, LoraBuildCfg(r=8, target_modules=["query","value"]))
```

## Factory integration

Use `codex_ml.modeling.factory.build_model` to wire dtype/device placement and
LoRA hooks in a reusable way. The helper respects the
`CODEX_ML_ENABLE_PEFT` environment variable so the same configuration can run in
environments without PEFT installed:

```python
from codex_ml.modeling.factory import (
    ENV_ENABLE_PEFT,
    ModelFactoryConfig,
    PeftAdapterConfig,
    build_model,
)

# Optional: gate LoRA activation per environment
os.environ[ENV_ENABLE_PEFT] = "1"

factory_config = ModelFactoryConfig(
    model_name_or_path="decoder_only",
    dtype="float16",
    device_map="cpu",
    enable_peft=True,
    peft=PeftAdapterConfig(path="local-adapter", r=4, target_modules=["weight"]),
)

model = build_model(factory_config)
```

If `CODEX_ML_ENABLE_PEFT` is unset (or set to `0`/`false`) the helper logs a
message and loads the base model without attempting to apply adapters. This
prevents crashes on machines that lack PEFT while keeping the configuration
portable.

> Implementation references: HuggingFace PEFT docs for LoRA configuration and application.
See the official docs for latest API details.
 
