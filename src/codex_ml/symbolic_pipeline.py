# [Python]: Functional Toy Training Pipeline
# > Generated: 2025-08-25 01:52:10 UTC | Author: mbaetiong
"""
Functional training pipeline for Codex-like toy models.

This module implements a lightweight, deterministic, and dependency-free
training pipeline that mirrors a realistic workflow:

  M0 — pretrain (unigram) →
  M1 — supervised fine-tuning (SFT) →
  RM — reward model (logistic regression on prefs) →
  M2 — RLHF (PPO-like updates)

Design goals:
- Reproducible (deterministic RNG seeds)
- Fast and small (pure stdlib)
- Testable: exposes token counting, losses, and model handles
- Safe: includes a simple safety penalty/regularizer term

Public API (__all__) includes configuration dataclasses, primitives and the
orchestration function run_codex_symbolic_pipeline for running the full flow.
"""

from __future__ import annotations

import json
import math
import random
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

__all__ = [
    "Weights",
    "PretrainCfg",
    "SFTCfg",
    "RewardModelCfg",
    "RLHFCfg",
    "ModelHandle",
    "RewardModelHandle",
    "tokenize",
    "pretrain",
    "sft",
    "train_reward_model",
    "rlhf_ppo",
    "loss_sft",
    "loss_rlhf",
    "regularizer",
    "objective_U",
    "run_codex_symbolic_pipeline",
]

# ---------------------------------------------------------------------------
# Tokenisation / utilities
# ---------------------------------------------------------------------------

TOKEN_RE = re.compile(r"\w+|[^\w\s]", re.UNICODE)
EPS = 1e-8  # numerical stability for logs
DANGEROUS_TOKENS = {"rm", "drop", "delete"}


def tokenize(text: str) -> List[str]:
    """Deterministic lower-case word/punctuation tokenizer."""
    return TOKEN_RE.findall(text.lower())


def _normalize(probs: Dict[str, float]) -> Dict[str, float]:
    total = sum(probs.values())
    if total <= 0:
        raise ValueError("probabilities must sum to a positive value")
    return {t: p / total for t, p in probs.items()}


def safety_penalty(token_probs: Dict[str, float]) -> float:
    """Return total probability mass of tokens flagged as dangerous."""
    return sum(token_probs.get(tok, 0.0) for tok in DANGEROUS_TOKENS)


def kl_divergence(p: Dict[str, float], q: Dict[str, float]) -> float:
    """KL(p || q) for discrete distributions (natural log)."""
    return sum(p[t] * math.log(p[t] / (q.get(t, EPS))) for t in p)


# ---------------------------------------------------------------------------
# Configuration dataclasses
# ---------------------------------------------------------------------------

@dataclass
class Weights:
    alpha: float = 1.0
    beta: float = 1.0
    gamma: float = 0.1


@dataclass
class PretrainCfg:
    context_len: int = 4096
    objective: str = "next_token_prediction"
    lr: float = 1e-2
    epochs: int = 1
    seed: int = 0

    def __post_init__(self) -> None:
        if self.context_len <= 0 or self.lr <= 0 or self.epochs <= 0:
            raise ValueError("invalid PretrainCfg parameters")


@dataclass
class SFTCfg:
    lr: float = 1e-2
    epochs: int = 1
    batch_size: int = 32
    seed: int = 0

    def __post_init__(self) -> None:
        if self.lr <= 0 or self.epochs <= 0 or self.batch_size <= 0:
            raise ValueError("invalid SFTCfg parameters")


@dataclass
class RewardModelCfg:
    lr: float = 0.1
    epochs: int = 5
    seed: int = 0

    def __post_init__(self) -> None:
        if self.lr <= 0 or self.epochs <= 0:
            raise ValueError("invalid RewardModelCfg parameters")


@dataclass
class RLHFCfg:
    algo: str = "PPO"
    ppo_clip: float = 0.2
    kl_penalty: float = 0.1
    epochs: int = 1
    lr: float = 1e-2
    batch_size: int = 8
    seed: int = 0

    def __post_init__(self) -> None:
        if (
            self.ppo_clip <= 0
            or self.kl_penalty < 0
            or self.epochs <= 0
            or self.lr <= 0
        ):
            raise ValueError("invalid RLHFCfg parameters")


# ---------------------------------------------------------------------------
# Model handles
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Training primitives
# ---------------------------------------------------------------------------

def pretrain(corpus: List[str], cfg: PretrainCfg) -> ModelHandle:
    """
    Build a unigram model over the corpus and return a ModelHandle for M0.
    Records vocab counts, token probabilities and bookkeeping metadata.
    """
    if not corpus:
        raise ValueError("corpus must not be empty")
    rng = random.Random(cfg.seed)
    vocab: Dict[str, int] = {}
    for text in corpus:
        toks = tokenize(text)[: cfg.context_len]
        for t in toks:
            vocab[t] = vocab.get(t, 0) + 1
    total = sum(vocab.values())
    if total == 0:
        token_probs: Dict[str, float] = {}
    else:
        token_probs = {t: c / total for t, c in vocab.items()}
    meta = {
        "vocab": vocab,
        "token_probs": token_probs,
        "base_token_probs": token_probs.copy(),
        "tokens_seen": total,
        "context_len": cfg.context_len,
        "objective": cfg.objective,
        "seed": cfg.seed,
        "lr": cfg.lr,
        "epochs": cfg.epochs,
        "rng_state": rng.getstate(),
    }
    return ModelHandle("Codex-Base", "M0.Pretrained", meta)


def sft(model: ModelHandle, demos: List[Dict[str, Any]], cfg: SFTCfg) -> ModelHandle:
    """
    Supervised fine-tuning using demo completions. Updates unigram counts
    and token probabilities using simple frequency updates per batch.
    """
    if not demos:
        raise ValueError("demos must not be empty")
    rng = random.Random(cfg.seed)
    token_probs: Dict[str, float] = model.meta.get("token_probs", {}).copy()
    vocab: Dict[str, int] = model.meta.get("vocab", {}).copy()
    losses: List[float] = []
    tokens_seen = 0
    for _ in range(cfg.epochs):
        rng.shuffle(demos)
        for i in range(0, len(demos), cfg.batch_size):
            batch = demos[i : i + cfg.batch_size]
            tokens: List[str] = []
            for ex in batch:
                tokens.extend(tokenize(ex.get("completion", "")))
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
    avg_loss = float(sum(losses) / len(losses)) if losses else 0.0
    model.meta.update(
        {
            "token_probs": token_probs,
            "vocab": vocab,
            "sft_loss": avg_loss,
            "num_samples": len(demos),
            "tokens_seen_sft": tokens_seen,
            "lr": cfg.lr,
            "epochs": cfg.epochs,
            "batch_size": cfg.batch_size,
            "seed": cfg.seed,
        }
    )
    return ModelHandle(model.name, "M1.SFT", model.meta)


def train_reward_model(
    prefs: List[Tuple[str, str, str, int]],
    base: ModelHandle,
    cfg: RewardModelCfg = RewardModelCfg(),
) -> RewardModelHandle:
    """
    Train a lightweight logistic-regression reward model on preference pairs.
    Returns a RewardModelHandle with weights and a token->index map.
    """
    if not prefs:
        raise ValueError("prefs must not be empty")
    vocab = base.meta.get("vocab")
    if not vocab:
        raise ValueError("base model missing vocab")
    token_index = {tok: i for i, tok in enumerate(vocab.keys())}
    weights = [0.0] * len(token_index)
    rng = random.Random(cfg.seed)

    def featurise(text: str) -> List[float]:
        vec = [0.0] * len(token_index)
        for tok in tokenize(text):
            idx = token_index.get(tok)
            if idx is not None:
                vec[idx] += 1.0
        return vec

    for _ in range(cfg.epochs):
        rng.shuffle(prefs)
        for _, a, b, label in prefs:
            fa = featurise(a)
            fb = featurise(b)
            diff = [x - y for x, y in zip(fa, fb)]
            logit = sum(w * d for w, d in zip(weights, diff))
            pred = 1 / (1 + math.exp(-logit))
            grad = [(pred - label) * d for d in diff]
            for i, g in enumerate(grad):
                weights[i] -= cfg.lr * g

    # evaluation (simple accuracy)
    correct = 0
    for _, a, b, label in prefs:
        fa = featurise(a)
        fb = featurise(b)
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
        "cfg": {"lr": cfg.lr, "epochs": cfg.epochs, "seed": cfg.seed},
    }
    return RewardModelHandle("RM-Codex", base.name, meta)


def rlhf_ppo(model: ModelHandle, rm: RewardModelHandle, cfg: RLHFCfg) -> ModelHandle:
    """
    PPO-inspired policy optimisation using the reward model.
    Performs simulated completions, scores them with RM and updates token_probs
    with PPO-style ratio clipping and KL penalty relative to base_token_probs.
    """
    prefs = rm.meta.get("prefs")
    if not prefs:
        raise ValueError("reward model missing training data")
    token_probs = model.meta.get("token_probs", {}).copy()
    base_probs = model.meta.get("base_token_probs", token_probs.copy())
    rng = random.Random(cfg.seed)

    def sample_completion(length: int = 4) -> List[str]:
        tokens = list(token_probs.keys())
        probs = list(token_probs.values())
        if not tokens:
            return []
        return rng.choices(tokens, weights=probs, k=length)

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
            if not completion:
                continue
            r = reward_of(completion)
            rewards.append(r)
            baseline = sum(rewards) / len(rewards)
            adv = r - baseline - cfg.kl_penalty * kl_divergence(token_probs, base_probs)
            ratio = math.exp(cfg.lr * adv)
            clipped = max(1 - cfg.ppo_clip, min(1 + cfg.ppo_clip, ratio))
            for t in completion:
                token_probs[t] = token_probs.get(t, 0.0) * clipped
            total = sum(token_probs.values())
            if total > 0:
                for k in list(token_probs.keys()):
                    token_probs[k] = token_probs[k] / total
        if rewards:
            avg_reward = sum(rewards) / len(rewards)

    model.meta.update(
        {
            "token_probs": token_probs,
            "ppo_clip": cfg.ppo_clip,
            "kl_penalty": cfg.kl_penalty,
            "epochs_rlhf": cfg.epochs,
            "lr_rlhf": cfg.lr,
            "algo": cfg.algo,
            "seed_rlhf": cfg.seed,
            "avg_reward": avg_reward,
        }
    )
    return ModelHandle(model.name, "M2.RLHF", model.meta)


# ---------------------------------------------------------------------------
# Loss terms / regularizer / objective
# ---------------------------------------------------------------------------

def loss_sft(model: ModelHandle, demos: List[Dict[str, Any]]) -> float:
    """Cross-entropy loss on demo completions under the model's unigram distribution."""
    token_probs = model.meta.get("token_probs", {})
    tokens: List[str] = []
    for ex in demos:
        tokens.extend(tokenize(ex.get("completion", "")))
    if not tokens:
        return 0.0
    return -sum(math.log(token_probs.get(t, EPS)) for t in tokens) / len(tokens)


def loss_rlhf(model: ModelHandle, rm: RewardModelHandle) -> float:
    """Negative reward computed from top model tokens under the reward model."""
    token_probs = model.meta.get("token_probs", {})
    idx = rm.meta.get("token_index", {})
    weights = rm.meta.get("weights", [])
    # approximate by scoring top-k tokens
    top_tokens = [t for t, _ in sorted(token_probs.items(), key=lambda x: x[1], reverse=True)[:4]]
    reward = sum(weights[idx[t]] if t in idx else 0.0 for t in top_tokens)
    return -reward


def regularizer(model: ModelHandle) -> float:
    """KL divergence from base plus simple safety penalty."""
    token_probs = model.meta.get("token_probs", {})
    base_probs = model.meta.get("base_token_probs", token_probs.copy())
    kl = kl_divergence(token_probs, base_probs) if token_probs and base_probs else 0.0
    penalty = safety_penalty(token_probs)
    return kl + penalty


def objective_U(alpha: float, beta: float, gamma: float, Lsft: float, Lrlhf: float, Omega: float) -> float:
    """Combined objective U = α·L_SFT + β·L_RLHF + γ·Ω."""
    return alpha * Lsft + beta * Lrlhf + gamma * Omega


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def run_codex_symbolic_pipeline(
    *,
    corpus: List[str],
    demos: List[Dict[str, Any]],
    prefs: List[Tuple[str, str, str, int]],
    w: Weights = Weights(),
    pre_cfg: PretrainCfg = PretrainCfg(),
    sft_cfg: SFTCfg = SFTCfg(),
    rm_cfg: RewardModelCfg = RewardModelCfg(),
    rlhf_cfg: RLHFCfg = RLHFCfg(),
) -> Dict[str, Any]:
    """Run the end-to-end pipeline and return a summary dict with handles and metrics."""
    if not corpus:
        raise ValueError("corpus must be non-empty")
    if not demos:
        raise ValueError("demos must be non-empty")
    if not prefs:
        raise ValueError("prefs must be non-empty")

    M0 = pretrain(corpus, pre_cfg)
    M1 = sft(M0, demos, sft_cfg)
    RM = train_reward_model(prefs, M1, rm_cfg)
    M2 = rlhf_ppo(M1, RM, rlhf_cfg)

    Lsft = loss_sft(M2, demos)
    Lrl = loss_rlhf(M2, RM)
    Om = regularizer(M2)
    U = objective_U(w.alpha, w.beta, w.gamma, Lsft, Lrl, Om)

    return {
        "symbolic": "M0 — SFT → M1 — RLHF(PPO) → M2; U = α·L_SFT + β·L_RLHF + γ·Ω",
        "weights": {"alpha": w.alpha, "beta": w.beta, "gamma": w.gamma},
        "handles": {
            "M0": M0.__dict__,
            "M1": M1.__dict__,
            "RM": RM.__dict__,
            "M2": M2.__dict__,
        },
        "losses": {"L_SFT": Lsft, "L_RLHF": Lrl, "Omega": Om},
        "objective_U": U,
    }


# ---------------------------------------------------------------------------
# Example usage (manual)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    toy_corpus = ["def add(a,b): return a+b", "SELECT * FROM users;", "# docs..."]
    toy_demos = [
        {"prompt": "Write a CLI that echoes input", "completion": "print(input())"},
        {"prompt": "Create a Bash script to gzip a folder", "completion": "tar -czf folder.tar.gz folder"},
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
        pre_cfg=PretrainCfg(seed=0, lr=1e-2, epochs=1),
        sft_cfg=SFTCfg(seed=0, lr=1e-2, epochs=1, batch_size=2),
        rm_cfg=RewardModelCfg(seed=0, lr=0.1, epochs=3),
        rlhf_cfg=RLHFCfg(seed=0, epochs=1, lr=1e-2, ppo_clip=0.2, kl_penalty=0.1),
    )
    print(json.dumps(summary, indent=2))
