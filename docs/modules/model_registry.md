# Model Registry

The model registry provides a lightweight mechanism to construct models by name
and optionally apply LoRA adapters.

## Available models

- `MiniLM` – small transformer used for tests.
- `bert-base-uncased` – delegates to Hugging Face and honours the
  `local_files_only` flag when pulling from cache.
- `gpt2-offline` – loads GPT-2 style checkpoints from disk. The loader inspects
  `CODEX_ML_GPT2_PATH`, then `${CODEX_ML_OFFLINE_MODELS_DIR}/gpt2`, and finally
  `${repo}/artifacts/models/gpt2`.
- `tinyllama-offline` – resolves TinyLLaMA checkpoints with the same offline
  safeguards, preferring `CODEX_ML_TINYLLAMA_PATH`.

## Base configuration

```yaml
# configs/model/base.yaml
model:
  name: sshleifer/tiny-gpt2
  tokenizer_name: sshleifer/tiny-gpt2
  dtype: float32
  device: cpu
  trust_remote_code: false
  load_config: {}
  lora:
    enabled: false
    r: 8
    alpha: 16
    dropout: 0.05
    target_modules:
      - q_proj
      - v_proj
```
## Offline GPT-2

```bash
python -m codex_ml.cli train -cn config model=offline/gpt2
```
`configs/model/offline/gpt2.yaml` binds `model.name` to `gpt2-offline` and
populates `model.local_path` with
`${CODEX_ML_GPT2_PATH}` → `${CODEX_ML_OFFLINE_MODELS_DIR}/gpt2` →
`${hydra:runtime.cwd}/artifacts/models/gpt2`.

## Offline TinyLLaMA

```bash
python -m codex_ml.cli train -cn config model=offline/tinyllama
```
`configs/model/offline/tinyllama.yaml` mirrors the GPT-2 fragment while checking
`CODEX_ML_TINYLLAMA_PATH` and the shared offline model directory.

## LoRA adapters

Enable LoRA adapters via command line overrides:

```bash
python -m codex_ml.cli train model.lora.enabled=true model.lora.r=4
```
When LoRA is active the HF training engine emits a warning and forces
`gradient_accumulation_steps` to `1` to ensure adapter parameters receive full
updates.

## Adding new models

Use `codex_ml.registry.register_model` to attach new constructors or ship an
entry point in your package (see [docs/dev/plugins.md](../dev/plugins.md)).
Example configurations are listed in
[docs/examples/training-configs.md](../examples/training-configs.md).
