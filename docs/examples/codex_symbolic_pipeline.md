# Codex Symbolic Pipeline — Example

**Last Updated:** 2026-06-22

The `codex_symbolic_pipeline` module is a **self-contained, dependency-free** reference
implementation of the Pretraining → SFT → RLHF training workflow.  
It uses deterministic bag-of-words models so that unit tests can exercise real token
counting, loss computation, and PPO-like updates without any external ML library.

Source: [`docs/examples/codex_symbolic_pipeline.py`](https://github.com/Aries-Serpent/_codex_/blob/main/docs/examples/codex_symbolic_pipeline.py)  
Production module: [`src/codex_ml/symbolic_pipeline.py`](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/symbolic_pipeline.py)

---

## Public API

| Symbol | Kind | Purpose |
|--------|------|---------|
| `tokenize(text)` | function | Deterministic regex tokeniser (lowercase) |
| `pretrain(corpus, cfg)` | function | Stage 1 — next-token unigram pretraining |
| `sft(model, demos, cfg)` | function | Stage 2 — supervised fine-tuning on demos |
| `train_reward_model(prefs, cfg)` | function | Train logistic reward model from preference pairs |
| `rlhf_ppo(model, rm, cfg)` | function | Stage 3 — PPO update against reward model |
| `Weights` | dataclass | Mutable token probability table |
| `PretrainCfg` | dataclass | Pretraining hyperparameters (epochs, lr, seed) |
| `SFTCfg` | dataclass | SFT hyperparameters |
| `RewardModelCfg` | dataclass | Reward model training config |
| `RLHFCfg` | dataclass | PPO hyperparameters (kl_coef, steps, …) |
| `ModelHandle` | dataclass | Wraps `Weights` + disallowed-token set |
| `RewardModelHandle` | dataclass | Wraps reward model weights |

---

## Quickstart

```python
from docs.examples.codex_symbolic_pipeline import (
    pretrain, sft, train_reward_model, rlhf_ppo,
    PretrainCfg, SFTCfg, RewardModelCfg, RLHFCfg,
)

# --- Stage 1: Pretrain ---
corpus = ["def foo(): pass", "x = 1 + 2", "print('hello')"]
m0 = pretrain(corpus, PretrainCfg(epochs=3, lr=0.1, seed=0))

# --- Stage 2: SFT ---
demos = [{"prompt": "def add(a, b):", "response": "return a + b"}]
m1 = sft(m0, demos, SFTCfg(epochs=2, lr=0.05, seed=0))

# --- Stage 3: RLHF ---
prefs = [{"prompt": "def add", "chosen": "return a + b", "rejected": "pass"}]
rm = train_reward_model(prefs, RewardModelCfg(epochs=3, lr=0.1, seed=0))
m2 = rlhf_ppo(m1, rm, RLHFCfg(steps=5, lr=0.01, kl_coef=0.1, seed=0))

print("Pipeline complete. Final model token count:", len(m2.weights.probs))
```

---

## Running the pipeline end-to-end

```bash
# From repo root
python deploy/deploy_codex_pipeline.py \
  --corpus  data/corpus.jsonl \
  --demos   data/demos.jsonl \
  --prefs   data/prefs.jsonl \
  --output-dir runs/exp1
```

```bash
# Validate reproducibility
pytest tests/test_deploy_codex_pipeline.py -v
```

---

## Pipeline stages

### Stage 1 — Pretraining

```
Corpus (text/code) ──► tokenize ──► unigram LM ──► M₀ Weights
```

Builds a unigram probability table via maximum-likelihood estimation across
`cfg.epochs` passes over the corpus.  Token probabilities are L1-normalised after
each epoch; a safety penalty suppresses disallowed tokens.

### Stage 2 — Supervised Fine-Tuning (SFT)

```
M₀ + Demos ──► teacher-forcing cross-entropy ──► M₁ Weights
```

Updates the pretrained weights by increasing probability mass on
demonstration response tokens.  Uses `cfg.lr` as a simple additive step size.

### Stage 3 — RLHF (PPO)

```
M₁ + Reward Model ──► PPO update (KL-regularised) ──► M₂ Weights
```

Samples prompts from the demonstration set, scores each response with the
reward model, applies a PPO-style gradient step, and regularises with a
KL-divergence penalty to the pretrained model to prevent reward hacking.

---

## Objective function (schematic)

$$
\min_{M}\; \mathcal{L}(M)
= \alpha\,\mathcal{L}_{\text{SFT}}(M;\,D_{\text{demos}})
+ \beta\,\mathcal{L}_{\text{RLHF}}(M;\,R)
+ \gamma\,\Omega(M)
$$

where $\Omega(M)$ is the safety regulariser and $R$ is the trained reward model.

---

## Tests

```bash
pytest tests/ -k "symbolic" -v
```

The test suite covers: deterministic reproducibility (seed=0), empty corpus
edge-cases, mis-specified config errors, and safety-penalty enforcement.

---

## See also

- [Symbolic Training architecture](../training/symbolic_training.md)
- [End-to-End CPU tutorial](../tutorials/end_to_end_cpu.md)
- [Deploy Pipeline](../deployment/deploy_pipeline.md)
