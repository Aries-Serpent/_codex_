# Offline default catalogue

Codex ML now ships a small catalogue of offline-ready components spanning
models, tokenizers, datasets, metrics, trainers, reward models and RL agents.
This guide summarises the expected local file layout and shows how to activate
each default without relying on network access.

## Directory layout

Place the unpacked artefacts under the repository root so the registry helpers
can resolve them deterministically:

``` text
artifacts/
  models/
    gpt2/
      config.json
      pytorch_model.bin
      tokenizer.json  # optional: kept here for parity with HF caches
    tinyllama/
      config.json
      pytorch_model.bin
      tokenizer.model
      tokenizer_config.json
    tiny_sequence_model/
      model.json
    tiny_tokenizer/
      vocab.json
  rl/
    scripted_agent/
      policy.json

data/
  offline/
    tiny_corpus.txt
    weighted_accuracy.json
    length_reward.json
    trainer_functional.json
```
You may also point the loaders at bespoke directories via the following
environment variables:

- `CODEX_ML_OFFLINE_MODELS_DIR` (shared models/tokenizers root)
- `CODEX_ML_GPT2_PATH`, `CODEX_ML_GPT2_TOKENIZER_PATH`
- `CODEX_ML_TINYLLAMA_PATH`, `CODEX_ML_TINYLLAMA_TOKENIZER_PATH`
- `CODEX_ML_OFFLINE_DATASETS_DIR`
- `CODEX_ML_TINY_CORPUS_PATH`
- `CODEX_ML_OFFLINE_METRICS_DIR`
- `CODEX_ML_WEIGHTED_ACCURACY_PATH`
- `CODEX_ML_TINY_TOKENIZER_PATH`
- `CODEX_ML_TINY_SEQUENCE_PATH`
- `CODEX_ML_FUNCTIONAL_TRAINER_CONFIG`
- `CODEX_ML_OFFLINE_CONFIGS_DIR`
- `CODEX_ML_LENGTH_REWARD_PATH`
- `CODEX_ML_SCRIPTED_AGENT_PATH`
- `CODEX_ML_OFFLINE_RL_DIR`

## Hydra overrides

Each component has a dedicated Hydra fragment so offline configurations can be
composed declaratively:

```bash
python -m codex_ml.cli train \
  -cn config \
  model=offline/gpt2 \
  tokenizer=offline/gpt2 \
  data=offline/tiny_corpus \
  training=offline/functional \
  interfaces=offline
```
The shortcut preset ``offline/catalogue`` mirrors ``config.yaml`` while
activating every offline fragment in one go:

```bash
python -m codex_ml.cli train -cn offline/catalogue
```
Evaluations can opt into the weighted accuracy baseline with either of the
configurations above or manually via:

```bash
python -m codex_ml.cli evaluate -cn config metrics/offline/weighted_accuracy
```
The fragments live under `configs/{model,tokenizer,data,metrics}/offline/` and
mirror the directory layout above.

## Tiny fixtures preset

For completely dependency-free smoke tests the repository now includes a "tiny"
stack of fixtures: a six-token vocabulary, a scripted response model, a
deterministic trainer configuration, a JSON-configurable length-based reward
model and a scripted RL policy. Enable them with the dedicated preset:

```bash
python -m codex_ml.cli train -cn offline/tiny_fixtures
```
The preset wires in the following plugin entries:

| Component      | Plugin name             | Fixture location |
|----------------|-------------------------|------------------|
| Tokenizer      | `offline:tiny-vocab`    | `artifacts/models/tiny_tokenizer/vocab.json` |
| Model          | `offline:tiny-sequence` | `artifacts/models/tiny_sequence_model/model.json` |
| Dataset        | `offline:tiny-corpus`   | `data/offline/tiny_corpus.txt` |
| Metric         | `offline:weighted-accuracy` | `data/offline/weighted_accuracy.json` |
| Trainer        | `offline:functional`    | `data/offline/trainer_functional.json` |
| Reward model   | `offline:length`        | `data/offline/length_reward.json` |
| RL agent       | `offline:scripted`      | `artifacts/rl/scripted_agent/policy.json` |

Each fixture can be overridden with the environment variables listed above, so
air-gapped deployments can swap in bespoke assets without editing the repo.

## Accessing the catalogue programmatically

The plugin registries expose the same defaults so integration tests and user
code can fetch components without importing the lower-level registries:

```python
from codex_ml.plugins.registries import datasets, metrics, models, reward_models, rl_agents, tokenizers, trainers

tokenizer = tokenizers.resolve_and_instantiate("offline:tiny-vocab")
model = models.resolve_and_instantiate("offline:tiny-sequence")
records = datasets.resolve_and_instantiate("offline:tiny-corpus")
weighted_acc = metrics.resolve_and_instantiate("offline:weighted-accuracy")
trainer = trainers.resolve_and_instantiate("offline:functional")
length_rm = reward_models.resolve_and_instantiate("offline:length")
agent = rl_agents.resolve_and_instantiate("offline:scripted")
```
Missing files raise `FileNotFoundError` with the list of searched locations,
ensuring offline environments fail fast instead of silently contacting remote
endpoints.

## Inspecting entries from the CLI

The Typer-powered plugin CLI exposes the bundled catalogue and highlights
whether entry-point discovery succeeds. Example invocations:

```bash
python -m codex_ml.cli.plugins_cli list models
python -m codex_ml.cli.plugins_cli list datasets
python -m codex_ml.cli.plugins_cli list metrics
python -m codex_ml.cli.plugins_cli list trainers
python -m codex_ml.cli.plugins_cli list reward_models
```
All commands run entirely offline; if a requested asset is missing, the
registry surfaces the precise paths that were checked.

## Opting out

Projects that prefer a minimal footprint can skip the overrides above and stick
with the tiny built-ins:

- Use `model.name=MiniLM` to keep the in-repo transformer stub.
- Use `tokenizer.name=hf` with `name_or_path` pointing to a minimal vocabulary.
- Remove `data=offline/tiny_corpus` and supply your own `dataset_loader.path`.
- Drop `metrics/offline/weighted_accuracy` to avoid shipping JSON weights.
- Swap `reward_model.plugin=offline:length` for `offline:heuristic` when you
  prefer fully in-memory behaviour.
- Replace `rl_agent.plugin=offline:scripted` with your own policy loader if the
  scripted agent is too opinionated.

These choices keep the installation lightweight while leaving the offline
catalogue available for teams that need reproducible baselines.
