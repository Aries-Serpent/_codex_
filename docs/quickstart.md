# Codex Quickstart

This quickstart demonstrates an end-to-end workflow entirely on your local
machine: tokenizer setup → training → evaluation.  All commands are
copy-pasteable and avoid network access by default.

## 1. Bootstrap the environment

```bash
uv sync --extra test --extra cli  # installs optional deps and the hydra.extra pytest plugin
source .venv/bin/activate
# or, if you prefer pip: pip install -e '.[test]' to stage the same extras
```
## 2. (Optional) prepare the offline defaults

To follow the offline-first examples you can populate the lightweight catalogue
bundled with Codex ML.  Copy or symlink the model, tokenizer, dataset and metric
artefacts into the directories below (relative to the repository root):

```text
artifacts/models/gpt2/
artifacts/models/tinyllama/
data/offline/tiny_corpus.txt
data/offline/weighted_accuracy.json
```
You can also set the environment variables described in
[`guides/offline_catalogue.md`](guides/offline_catalogue.md) to point
at alternative locations.  Skip this step entirely if you prefer the minimal
MiniLM baseline – the remaining commands continue to work.

## 3. Tokenize sample data

Register the toy tokenizer plugin and encode text without touching external
services.

```bash
python examples/tokenize.py
```
Expected output:

```json
{
  "text": "Codex makes registries fun!",
  "encoded": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
  "decoded": "Codex makes registries fun!"
}
```
## 4. Run a deterministic training session

### Data handling essentials

Large JSONL corpora no longer need to be read into memory.  Stream them with
`codex_ml.data.jsonl_stream.iter_jsonl()` and split deterministically with a
single seed:

```python
from codex_ml.data.jsonl_stream import iter_jsonl
from codex_ml.data.split_utils import deterministic_split

records = list(iter_jsonl("data/offline/tiny_corpus.jsonl"))
train, val, test = deterministic_split(records, seed=1234, val_fraction=0.15, test_fraction=0.05)
```

When caching shards, call `codex_ml.data.cache.write_jsonl_with_crc()` to emit a
`.crc32` sidecar.  The checksum is derived from the streaming
`codex_ml.data.integrity.crc32_file()` helper and lets you verify cached shards
before loading them back into memory.

Finally, construct DataLoaders with the reproducible factory so worker seeding
and RNG generators share the same configuration seed:

```python
from codex_ml.training import TrainingRunConfig, build_dataloader

cfg = TrainingRunConfig(batch_size=16, num_workers=2, pin_memory=True)
dataloader = build_dataloader(dataset, cfg)
```

```bash
export CODEX_MLFLOW_ENABLE=0  # keep MLflow disabled unless you opt-in
python examples/train_toy.py
# or redirect metrics: python -m codex_ml.train_loop --epochs 1 --art-dir artifacts/custom-metrics
# or compose via Hydra: python -m codex_ml.cli.hydra_main experiment=debug training.max_epochs=3
```

> **Tip:** set `training.mlflow_enable=true` (and optionally
> `training.mlflow_tracking_uri=file:.codex/mlruns`) to record the same run in a
> local MLflow store. The shim mirrors training/eval metrics and writes
> `<checkpoint_dir>/mlflow/metrics.ndjson` plus a `config.json` snapshot that are
> uploaded as run artefacts.

### Structured configs & multirun sweeps

The Hydra entrypoint registers a typed `AppConfig` in code, so overrides are
validated before a run starts. Compose presets and ad-hoc flags side-by-side:

```bash
python -m codex_ml.cli.hydra_main experiment=fast training.max_epochs=2
```

Hydra's `-m/--multirun` mode fans out parameter grids locally. The command below
launches four runs (2×2 sweep) and stores results under `multirun/` with
auto-numbered job IDs in `hydra.job.num`:

```bash
python -m codex_ml.cli.hydra_main -m training.batch_size=4,8 training.learning_rate=3e-4,1e-4
```

Each subdirectory captures the effective config and stdout/stderr for easy
post-run comparison.

Prefer a saved preset? Compose the offline-friendly sweep stub and layer any
extra overrides you need:

```bash
python -m codex_ml.cli.hydra_main --config-path conf/examples --config-name sweep_offline -m \
  training.max_epochs=1
```

The helper YAML locks Hydra's output folders under `.codex/hydra/` so you can
inspect multirun artefacts without touching remote services.
The script writes checkpoints and NDJSON logs under `runs/examples/`.  Each run
creates a timestamped directory containing:

* `metrics.ndjson` – per-step metrics
* `metrics.json` – append-only list of metric payloads
* `environment.json` / `environment.ndjson` – runtime metadata and git commit
* `pip-freeze.txt` – dependency manifest captured automatically
* `dataset_checksums.json` – hashes for any dataset files passed via the training API
* `params.ndjson` – run parameters (seed, dataset, etc.)
* `config.json` / `config.ndjson` – resolved configuration snapshot
* `provenance.ndjson` – git commit, hostname and other reproducibility data

Checkpoints land under `<run>/checkpoints/` by default. Use
`codex_ml.utils.checkpoint.prune_best_k(<dir>, k)` to keep only the newest _k_
snapshots, and call `load_checkpoint(..., strict=True)` if you want resumes to
abort whenever a SHA-256 digest is missing or mismatched.

### Evaluate during training

Evaluation runs every epoch by default when a validation DataLoader is present
and writes NDJSON:

```bash
tail -n +1 .codex/metrics.ndjson
```

Each record includes `eval_loss`, `perplexity`, and `token_accuracy` (when logits
and labels are available).  Adjust the cadence with
`training.eval_every_epochs`.

### LoRA switch

Enable LoRA in config:

```bash
codex-train training.lora_enable=true training.lora_r=8 training.lora_alpha=16 training.lora_dropout=0.05
```

See [`docs/examples/lora_quickstart.md`](examples/lora_quickstart.md) for a minimal snippet.

### Tune gradient accumulation & evaluation cadence

The functional trainer exposes the most common loop knobs directly on the
`training` config block:

| Setting | Description |
| --- | --- |
| `training.gradient_accumulation` | Accumulate gradients over multiple batches to fit larger effective batch sizes on limited hardware. |
| `training.amp_enable` | Toggle automatic mixed precision (AMP). Combine with `training.amp_dtype` to pick `fp16` or `bf16`. |
| `training.eval_every_epochs` | Run the lightweight evaluation loop every _n_ epochs. Set to a large value to skip eval. |
| `training.metrics_out` | Path to the append-only NDJSON log (defaults to `.codex/metrics.ndjson`). |

> **Effective batch size:** within a single process the trainer applies
> `gradient_accumulation` batches before stepping the optimiser.  The effective
> batch therefore equals `batch_size × gradient_accumulation × world_size`
> (with `world_size = 1` for this loop).

Evaluation metrics and training timing data are appended to the NDJSON file so
you can tail progress without any external services:

```bash
tail -f .codex/metrics.ndjson
```
### Padding, truncation and caching

Codex ML exposes the Hugging Face-style padding and truncation flags directly
through `TrainingRunConfig`.  Set `padding` to `True` (default) to pad batches to
the longest sequence or to `'max_length'`/`False` to fine-tune behaviour, and
use `truncation=True` plus `max_length=<int>` to cap overly long prompts during
training.  When a `DataCollatorWithPadding` dependency is available it is wired
automatically for dynamic padding at batch time.

Repeated calls to the same tokenizer inputs are cached in a lightweight
in-memory LRU keyed by text and padding arguments.  To disable caching for
debugging or benchmarking set `CODEX_ML_TOKEN_CACHE_DISABLE=1` in the
environment before launching training.

## 5. Inspect results & aggregate metrics

```bash
python examples/mlflow_offline.py runs/examples/<latest-run>
python examples/evaluate_toy.py
```
Use the printed `mlflow ui --backend-store-uri ...` command to explore the run
offline.  TensorBoard summaries are saved alongside the run when enabled.

## 5b. Logging & Monitoring (optional)

Codex ML keeps telemetry opt-in so you can decide when to light up dashboards.

* **TensorBoard** – pass `tensorboard=true` (or set `TrainConfig.tensorboard = True`)
  and optionally override `tensorboard_dir` (default `runs/codex`). Launch a
  dashboard locally with:

  ```bash
  tensorboard --logdir runs/codex
  ```

* **Weights & Biases (offline)** – export `WANDB_MODE=offline`, set
  `WANDB_PROJECT` if you want a custom namespace, and enable via
  `TrainConfig.wandb_enable = True`. The shim buffers events locally; run
  `wandb sync` later to upload if desired.

* **System metrics NDJSON** – background sampling writes CPU/RAM (and GPU when
  NVML is present) into `.codex/metrics.ndjson` by default. Adjust with
  `TrainConfig.metrics_out` or disable by setting
  `TrainConfig.system_metrics_interval = 0`. TensorBoard/W&B receive the same
  scalar stream when enabled.

## 6. Next steps

* Fine-tune chat models via `examples/chat_finetune.py`
* Explore the registries and plugin system in `docs/dev/plugins.md`
* Link your own datasets via `docs/examples/training-configs.md`
* Register lightweight model constructors via `codex_ml.hf_loader.register_causal_lm`

## 7. Optional: plug in custom causal LMs

You can register bespoke constructors that sidestep Hugging Face entirely –
useful for deterministic fixtures or research prototypes.  Registered
constructors receive the same keyword arguments as the default loader, so you
can react to AMP dtype or LoRA settings.

```python
from codex_ml.hf_loader import register_causal_lm, load_causal_lm


@register_causal_lm("toy-causal")
def build_toy_model(*, device=None, dtype=None, peft_cfg=None):
    model = MyToyModel()
    if device:
        model.to(device)
    return model


model = load_causal_lm("toy-causal", device="cuda", dtype="bf16")
```

Passing `dtype="bf16"` or `dtype="fp16"` maps to `torch.bfloat16` /
`torch.float16` automatically.  Hardware support varies – on CPU the loader
falls back gracefully when the dtype is unsupported.  LoRA/PEFT dictionaries are
also forwarded so registries can decide whether to attach adapters.
