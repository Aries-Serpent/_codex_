# LoRA Quickstart

This example shows how to wrap a base Causal LM with LoRA and run a single step.

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model

tok = AutoTokenizer.from_pretrained("gpt2")
base = AutoModelForCausalLM.from_pretrained("gpt2")
cfg = LoraConfig(r=8, lora_alpha=16, lora_dropout=0.05, target_modules=["q_proj", "v_proj"])  # adjust to model
model = get_peft_model(base, cfg)

ids = tok("hello world", return_tensors="pt").input_ids
loss = model(input_ids=ids, labels=ids).loss
print(float(loss))
```

> Tip: enable mixed precision in the training config for consumer GPUs.
