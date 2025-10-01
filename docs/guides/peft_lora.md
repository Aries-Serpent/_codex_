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

The lightweight `codex_ml.models.factory.create_model` helper wraps model
construction with device/dtype handling and an opt-in LoRA toggle. Set the
environment variable `CODEX_ML_ENABLE_PEFT=1` (or pass
`enable_peft=True`) to apply adapters when a `lora` config is provided:

```python
from codex_ml.models.factory import create_model

def tiny_builder(**_):
    import torch

    return torch.nn.Linear(4, 4)

model = create_model(
    tiny_builder,
    dtype="float16",
    device="cpu",
    config={"lora": {"r": 4, "target_modules": ["weight"]}},
)
```

When PEFT is unavailable (or the flag is off) the base model is returned
unchanged, making it safe to keep the same configuration across environments.

> Implementation references: HuggingFace PEFT docs for LoRA configuration and application.
See the official docs for latest API details.
 
