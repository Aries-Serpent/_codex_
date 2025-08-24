# ================================================================
# ChatGPT Codex — Pseudocode Scaffold (mirrors symbolic objective)
# ================================================================
# Symbolic pipeline:
#   Let M0 = Base Codex (pretrained on text+code)
#   M0 — SFT(curated demos) → M1 — RLHF(reward model, PPO) → M2 (Final)
#
# Objective (schematic):
#   U(M) = α·L_SFT(M; D_code) + β·L_RLHF(M; R) + γ·Ω(M)
#
# Notes:
#   - Pretraining creates M0 (foundation).
#   - SFT aligns with curated demonstrations D_code.
#   - RLHF optimizes policy against a learned Reward Model (e.g., PPO).
#   - Ω(M) can encode safety/regularization terms.
#   - Deterministic seeds default to 0 for reproducibility.
# ---------------------------------------------------------------

from __future__ import annotations

import json
import math
import random
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

# ----------------------------- Config -----------------------------


@dataclass
class Weights:
    alpha: float = 1.0  # weight for SFT loss
    beta: float = 1.0  # weight for RLHF term
    gamma: float = 0.1  # weight for regularization


@dataclass
class PretrainCfg:
    context_len: int = 4096
    objective: str = "next_token_prediction"
    lr: float = 1e-4
    epochs: int = 1
    seed: int = 0


@dataclass
class SFTCfg:
    lr: float = 5e-6
    epochs: int = 3
    batch_size: int = 32
    seed: int = 0


@dataclass
class RLHFCfg:
    algo: str = "PPO"
    ppo_clip: float = 0.2
    kl_penalty: float = 0.1
    epochs: int = 4
    lr: float = 1e-4
    batch_size: int = 8
    seed: int = 0


# ----------------------------- Handles ----------------------------


@dataclass
class ModelHandle:
    name: str
    stage: str
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RewardModelHandle:
    name: str
    base_model: str
    meta: Dict[str, Any] = field(default_factory=dict)


TOKEN_RE = re.compile(r"\w+|[^\s\w]", re.UNICODE)

# Small constant used for numerical stability when taking logarithms.
EPS = 1e-8


def tokenize(text: str) -> List[str]:
    """Split ``text`` into case-insensitive word/punctuation tokens."""

    return TOKEN_RE.findall(text.lower())


def kl_divergence(p: Dict[str, float], q: Dict[str, float]) -> float:
    """Kullback–Leibler divergence ``KL(p || q)`` for discrete distributions."""

    return sum(p[t] * math.log(p[t] / (q.get(t, EPS))) for t in p)


# --------------------------- Primitives ---------------------------


def pretrain(corpus: List[str], cfg: PretrainCfg) -> ModelHandle:
    """Train a unigram model on ``corpus`` and return a model handle."""

    if not corpus:
        raise ValueError("corpus must not be empty")
    rng = random.Random(cfg.seed)
    vocab: Dict[str, int] = {}
    for text in corpus:
        for tok in tokenize(text):
            vocab[tok] = vocab.get(tok, 0) + 1
    total = sum(vocab.values())
    token_probs = {t: c / total for t, c in vocab.items()}
    meta = {
        "vocab": vocab,
        "token_probs": token_probs,
        "base_token_probs": token_probs.copy(),
        "tokens_seen": total,
        "seed": cfg.seed,
        "lr": cfg.lr,
        "epochs": cfg.epochs,
        "rng_state": rng.getstate(),
    }
    return ModelHandle("Codex-Base", "M0.Pretrained", meta)


def sft(model: ModelHandle, demos: List[Dict[str, Any]], cfg: SFTCfg) -> ModelHandle:
    """Supervised fine-tuning using completion demonstrations."""

    if not demos:
        raise ValueError("demos must not be empty")
    rng = random.Random(cfg.seed)
    token_probs = model.meta["token_probs"].copy()
    vocab = model.meta["vocab"].copy()
    losses: List[float] = []
    tokens_seen = 0
    for _ in range(cfg.epochs):
        rng.shuffle(demos)
        for i in range(0, len(demos), cfg.batch_size):
            batch = demos[i : i + cfg.batch_size]
            tokens: List[str] = []
            for ex in batch:
                tokens.extend(tokenize(ex["completion"]))
            if not tokens:
                continue
            loss = -sum(math.log(token_probs.get(t, EPS)) for t in tokens) / len(tokens)
            losses.append(loss)
            tokens_seen += len(tokens)
            for t in tokens:
                vocab[t] = vocab.get(t, 0) + 1
            total = sum(vocab.values())
            for t in vocab:
                token_probs[t] = vocab[t] / total
    model.meta.update(
        {
            "token_probs": token_probs,
            "vocab": vocab,
            "sft_loss": float(sum(losses) / len(losses)) if losses else 0.0,
            "tokens_seen_sft": tokens_seen,
        }
    )
    return ModelHandle(model.name, "M1.SFT", model.meta)


def train_reward_model(
    prefs: List[Tuple[str, str, str, int]], base: ModelHandle
) -> RewardModelHandle:
    """Train a simple logistic regression reward model on preferences."""

    if not prefs:
        raise ValueError("prefs must not be empty")
    vocab = base.meta.get("vocab")
    if not vocab:
        raise ValueError("base model missing vocab")
    token_index = {tok: i for i, tok in enumerate(vocab.keys())}
    weights = [0.0] * len(token_index)
    lr = 0.1
    rng = random.Random(0)

    def featurise(text: str) -> List[float]:
        vec = [0.0] * len(token_index)
        for tok in tokenize(text):
            if tok in token_index:
                vec[token_index[tok]] += 1.0
        return vec

    for _ in range(5):
        rng.shuffle(prefs)
        for _, a, b, label in prefs:
            fa, fb = featurise(a), featurise(b)
            diff = [x - y for x, y in zip(fa, fb)]
            logit = sum(w * d for w, d in zip(weights, diff))
            pred = 1 / (1 + math.exp(-logit))
            grad = [(pred - label) * d for d in diff]
            for i, g in enumerate(grad):
                weights[i] -= lr * g

    correct = 0
    for _, a, b, label in prefs:
        fa, fb = featurise(a), featurise(b)
        diff = [x - y for x, y in zip(fa, fb)]
        logit = sum(w * d for w, d in zip(weights, diff))
        pred = 1 if logit > 0 else 0
        correct += int(pred == label)
    acc = correct / len(prefs)
    meta = {
        "weights": weights,
        "token_index": token_index,
        "accuracy": acc,
        "prefs": list(prefs),
    }
    return RewardModelHandle("RM-Codex", base.name, meta)


def rlhf_ppo(model: ModelHandle, rm: RewardModelHandle, cfg: RLHFCfg) -> ModelHandle:
    """Policy optimisation with a reward model and KL regularisation."""

    prefs = rm.meta.get("prefs")
    if not prefs:
        raise ValueError("reward model missing training data")
    token_probs = model.meta["token_probs"].copy()
    base_probs = model.meta["token_probs"].copy()
    rng = random.Random(cfg.seed)

    def sample_completion(length: int = 4) -> List[str]:
        tokens = list(token_probs.keys())
        probs = list(token_probs.values())
        return rng.choices(tokens, probs, k=length)

    def reward_of(tokens: List[str]) -> float:
        idx = rm.meta["token_index"]
        weights = rm.meta["weights"]
        score = 0.0
        for t in tokens:
            if t in idx:
                score += weights[idx[t]]
        return score

    avg_reward = 0.0
    for _ in range(cfg.epochs):
        rewards: List[float] = []
        for prompt, _, _, _ in prefs:
            completion = sample_completion()
            r = reward_of(completion)
            rewards.append(r)
            baseline = sum(rewards) / len(rewards)
            adv = r - baseline - cfg.kl_penalty * kl_divergence(token_probs, base_probs)
            ratio = math.exp(cfg.lr * adv)
            clipped = max(1 - cfg.ppo_clip, min(1 + cfg.ppo_clip, ratio))
            for t in completion:
                token_probs[t] *= clipped
            total = sum(token_probs.values())
            for k in token_probs:
                token_probs[k] /= total
        if rewards:
            avg_reward = sum(rewards) / len(rewards)

    model.meta.update(
        {
            "token_probs": token_probs,
            "avg_reward": avg_reward,
            "ppo_clip": cfg.ppo_clip,
            "kl_penalty": cfg.kl_penalty,
            "epochs_rlhf": cfg.epochs,
            "lr_rlhf": cfg.lr,
        }
    )
    return ModelHandle(model.name, "M2.RLHF", model.meta)


# ---------------------------- Loss Terms --------------------------


def loss_sft(model: ModelHandle, demos: List[Dict[str, Any]]) -> float:
    """Cross-entropy of demo completions under ``model``."""

    token_probs = model.meta["token_probs"]
    tokens: List[str] = []
    for ex in demos:
        tokens.extend(tokenize(ex["completion"]))
    if not tokens:
        return 0.0
    return -sum(math.log(token_probs.get(t, EPS)) for t in tokens) / len(tokens)


def loss_rlhf(model: ModelHandle, rm: RewardModelHandle) -> float:
    """Negative reward for greedy completions under ``model``."""

    idx = rm.meta["token_index"]
    weights = rm.meta["weights"]
    token_probs = model.meta["token_probs"]
    top_tokens = [
        t for t, _ in sorted(token_probs.items(), key=lambda x: x[1], reverse=True)[:4]
    ]
    reward = sum(weights[idx[t]] if t in idx else 0.0 for t in top_tokens)
    return -reward


def regularizer(model: ModelHandle) -> float:
    """Deterministic KL regularisation against the pretrained model."""

    return kl_divergence(model.meta["token_probs"], model.meta["base_token_probs"])


def objective_U(
    alpha: float, beta: float, gamma: float, Lsft: float, Lrlhf: float, Omega: float
) -> float:
    """
    U(M) = α·L_SFT + β·L_RLHF + γ·Ω
    """
    return alpha * Lsft + beta * Lrlhf + gamma * Omega


# --------------------------- Orchestration ------------------------


def run_codex_symbolic_pipeline(
    *,
    corpus: List[str],
    demos: List[Dict[str, Any]],
    prefs: List[Tuple[str, str, str, int]],
    w: Weights = Weights(),
    pre_cfg: PretrainCfg = PretrainCfg(),
    sft_cfg: SFTCfg = SFTCfg(),
    rlhf_cfg: RLHFCfg = RLHFCfg(),
) -> Dict[str, Any]:
    """
    Mirrors symbolic math exactly:
      M0 = pretrain(corpus)
      M1 = sft(M0, demos)
      RM = train_reward_model(prefs, M1)
      M2 = rlhf_ppo(M1, RM)
      U(M2) = α·L_SFT(M2; D_code) + β·L_RLHF(M2; R) + γ·Ω(M2)
    """
    # Stages
    M0 = pretrain(corpus, pre_cfg)
    M1 = sft(M0, demos, sft_cfg)
    RM = train_reward_model(prefs, M1)
    M2 = rlhf_ppo(M1, RM, rlhf_cfg)

    # Losses & Objective
    Lsft = loss_sft(M2, demos)
    Lrl = loss_rlhf(M2, RM)
    Om = regularizer(M2)
    U = objective_U(w.alpha, w.beta, w.gamma, Lsft, Lrl, Om)

    return {
        "symbolic": "M0 — SFT → M1 — RLHF(PPO) → M2;  U = α·L_SFT + β·L_RLHF + γ·Ω",
        "weights": w.__dict__,
        "handles": {
            "M0": M0.__dict__,
            "M1": M1.__dict__,
            "RM": RM.__dict__,
            "M2": M2.__dict__,
        },
        "losses": {"L_SFT": Lsft, "L_RLHF": Lrl, "Omega": Om},
        "objective_U": U,
    }


# ---------------------- Framework binding example ----------------------


def hf_pretrain(corpus: List[str], cfg: PretrainCfg) -> ModelHandle:
    """Bind the pretraining stage to Hugging Face Transformers.

    This function shows how the symbolic ``pretrain`` stub can map to a real
    implementation using `transformers.Trainer`.  It trains ``distilgpt2`` on
    ``corpus`` and returns a :class:`ModelHandle` containing the resulting
    model and tokenizer.
    """

    from datasets import Dataset
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        Trainer,
        TrainingArguments,
    )

    dataset = Dataset.from_dict({"text": corpus})
    tokenizer = AutoTokenizer.from_pretrained("distilgpt2")

    def tok(ex):  # tokenise on the fly
        return tokenizer(ex["text"], truncation=True)

    tokenised = dataset.map(tok, remove_columns=["text"])
    model = AutoModelForCausalLM.from_pretrained("distilgpt2")
    args = TrainingArguments(
        output_dir="/tmp/pretrain",
        per_device_train_batch_size=2,
        num_train_epochs=cfg.epochs,
        learning_rate=cfg.lr,
        logging_strategy="no",
        save_strategy="no",
    )
    trainer = Trainer(model=model, args=args, train_dataset=tokenised)
    trainer.train()
    meta = {
        "hf_model": model,
        "tokenizer": tokenizer,
        "tokens_seen": len("".join(corpus)),
    }
    return ModelHandle("distilgpt2", "M0.Pretrained", meta)


def hf_sft(model: ModelHandle, demos: List[Dict[str, Any]], cfg: SFTCfg) -> ModelHandle:
    """Supervised fine‑tuning using Hugging Face's ``Trainer``."""

    from datasets import Dataset
    from transformers import Trainer, TrainingArguments

    tokenizer = model.meta["tokenizer"]
    dataset = Dataset.from_dict(demos)

    def tok(ex):
        return tokenizer(ex["completion"], truncation=True)

    tokenised = dataset.map(tok, remove_columns=list(demos[0].keys()))
    args = TrainingArguments(
        output_dir="/tmp/sft",
        per_device_train_batch_size=cfg.batch_size,
        num_train_epochs=cfg.epochs,
        learning_rate=cfg.lr,
        logging_strategy="no",
        save_strategy="no",
    )
    trainer = Trainer(model=model.meta["hf_model"], args=args, train_dataset=tokenised)
    trainer.train()
    return ModelHandle(model.name, "M1.SFT", {**model.meta, "samples": len(demos)})


def hf_train_reward_model(
    prefs: List[Tuple[str, str, str, int]], base: ModelHandle
) -> RewardModelHandle:
    """Train a simple reward model using the ``transformers`` stack."""

    from datasets import Dataset
    from torch import nn
    from transformers import AutoModel, AutoTokenizer, Trainer, TrainingArguments

    tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
    model = AutoModel.from_pretrained("distilbert-base-uncased")

    def preprocess(example: Dict[str, Any]) -> Dict[str, Any]:
        text = example["prompt"] + tokenizer.sep_token + example["completion"]
        return tokenizer(text, truncation=True)

    entries = []
    for p, a, b, label in prefs:
        entries.append({"prompt": p, "completion": a, "label": label})
        entries.append({"prompt": p, "completion": b, "label": 1 - label})

    dataset = Dataset.from_list(entries).map(preprocess)
    args = TrainingArguments(
        output_dir="/tmp/rm",
        per_device_train_batch_size=2,
        num_train_epochs=1,
        learning_rate=5e-5,
        logging_strategy="no",
        save_strategy="no",
    )
    rm_head = nn.Linear(model.config.hidden_size, 1)

    class RMModel(nn.Module):  # pragma: no cover - illustrative
        def __init__(self) -> None:
            super().__init__()
            self.model = model
            self.head = rm_head

        def forward(self, **inputs):
            out = self.model(**inputs)
            return self.head(out.last_hidden_state[:, 0, :])

    rm_model = RMModel()
    trainer = Trainer(model=rm_model, args=args, train_dataset=dataset)
    trainer.train()
    meta = {"rm_model": rm_model, "tokenizer": tokenizer, "prefs": prefs}
    return RewardModelHandle("RM-HF", base.name, meta)


def hf_rlhf_ppo(model: ModelHandle, rm: RewardModelHandle, cfg: RLHFCfg) -> ModelHandle:
    """Optimise the policy with PPO using ``trl``'s ``PPOTrainer``."""

    from transformers import AutoTokenizer
    from trl import PPOConfig, PPOTrainer

    tokenizer = AutoTokenizer.from_pretrained("distilgpt2")
    ppo_config = PPOConfig(batch_size=cfg.batch_size, learning_rate=cfg.lr)
    trainer = PPOTrainer(
        model=model.meta["hf_model"],
        ref_model=model.meta["hf_model"],
        tokenizer=tokenizer,
        reward_model=rm.meta["rm_model"],
        config=ppo_config,
    )
    trainer.train()
    return ModelHandle(model.name, "M2.RLHF", model.meta)


def loss_sft_hf(model: ModelHandle, demos: List[Dict[str, Any]]) -> float:
    """Cross‑entropy loss of demo completions under the HF model."""

    import torch

    tokenizer = model.meta["tokenizer"]
    hf_model = model.meta["hf_model"]
    losses: List[float] = []
    for ex in demos:
        tok = tokenizer(ex["completion"], return_tensors="pt")
        with torch.no_grad():
            out = hf_model(**tok, labels=tok["input_ids"])
        losses.append(out.loss.item())
    return sum(losses) / max(1, len(losses))


def loss_rlhf_hf(model: ModelHandle, rm: RewardModelHandle) -> float:
    """Negative reward estimated from the HF reward model."""

    import torch

    tokenizer = rm.meta["tokenizer"]
    rm_model = rm.meta["rm_model"]
    prompt = tokenizer("hello", return_tensors="pt").input_ids
    gen_ids = model.meta["hf_model"].generate(prompt, max_length=8)
    sample = tokenizer.decode(gen_ids[0])
    with torch.no_grad():
        inputs = tokenizer(sample, return_tensors="pt")
        reward = rm_model(**inputs).mean().item()
    return -reward


# --------------------------- Example Run --------------------------

if __name__ == "__main__":
    toy_corpus = ["def add(a,b): return a+b", "SELECT * FROM users;", "# docs..."]
    toy_demos = [
        {
            "prompt": "Write a CLI that echoes input",
            "completion": "argparse-based CLI ...",
        },
        {
            "prompt": "Create a Bash script to gzip a folder",
            "completion": "tar -czf ...",
        },
    ]
    toy_prefs = [
        ("sum", "def add(a,b): return a+b", "def add(a,b): return a-b", 1),
        ("sql", "SELECT * FROM users;", "DROP TABLE users;", 1),
    ]

    summary = run_codex_symbolic_pipeline(
        corpus=toy_corpus,
        demos=toy_demos,
        prefs=toy_prefs,
        w=Weights(alpha=1.0, beta=1.2, gamma=0.05),
        pre_cfg=PretrainCfg(context_len=4096, lr=1e-4, epochs=1),
        sft_cfg=SFTCfg(lr=5e-6, epochs=3, batch_size=32),
        rlhf_cfg=RLHFCfg(algo="PPO", ppo_clip=0.2, kl_penalty=0.1, epochs=4),
    )
    print(json.dumps(summary, indent=2))
