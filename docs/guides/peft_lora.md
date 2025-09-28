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

> Implementation references: HuggingFace PEFT docs for LoRA configuration and application. 
See the official docs for latest API details. 
 
