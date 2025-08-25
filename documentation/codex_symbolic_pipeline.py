"""Toy symbolic pipeline with minimal ML loops.

The module mimics the pretrain → SFT → RLHF workflow using deterministic
bag-of-words models so that unit tests can exercise real token counting,
loss computation, and PPO-like updates without external dependencies.

It is compatible with both deterministic and stochastic training for
testing, and covers safety/regularization and proper seed handling.
"""

from __future__ import annotations

import json
import math
import random
import re
from collections import Counter, defaultdict
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
    "hf_pretrain",
    "hf_sft",
    "hf_train_reward_model",
    "hf_rlhf_ppo",
    "loss_sft_hf",
    "loss_rlhf_hf",
]

TOKEN_RE = re.compile(r"\w+|[^\w\s]")

def tokenize(text: str) -> List[str]:
    """Simple deterministic tokenizer used for the toy pipeline."""
    return TOKEN_RE.findall(text.lower())

def _normalize(probs: Dict[str, float]) -> Dict[str, float]:
    total = sum(probs.values())
    if total <= 0:
        raise ValueError("probabilities must sum to a positive value")
    return {t: p / total for t, p in probs.items()}

# ----------------------------- Config -----------------------------

@dataclass
class Weights:
    alpha: float = 1.0  # weight for SFT loss
    beta: float = 1.0   # weight for RLHF term
    gamma: float = 0.1  # weight for regularization

@dataclass
class PretrainCfg:
    context_len: int = 4096
    objective: str = "next_token_prediction"
    lr: float = 1e-2
    epochs: int = 1
    seed: int = 0

    def __post_init__(self) -> None:
        if self.context_len <= 0 or self.lr <= 0 or self.epochs <= 0:
            raise ValueError("invalid PretrainCfg")

@dataclass
class SFTCfg:
    lr: float = 1e-2
    epochs: int = 1
    batch_size: int = 32
    seed: int = 0

@dataclass
class RewardModelCfg:
    lr: float = 0.1
    epochs: int = 5
    seed: int = 0

    def __post_init__(self) -> None:
        if self.lr <= 0 or self.epochs <= 0:
            raise ValueError("invalid RewardModelCfg")

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
            or self.lr <= 0
            or self.epochs <= 0
        ):
            raise ValueError("invalid RLHFCfg")

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

EPS = 1e-8
DANGEROUS_TOKENS = {"rm", "drop", "delete"}

def safety_penalty(token_probs: Dict[str, float]) -> float:
    return sum(token_probs.get(tok, 0.0) for tok in DANGEROUS_TOKENS)

def kl_divergence(p: Dict[str, float], q: Dict[str, float]) -> float:
    """Kullback–Leibler divergence KL(p||q) for discrete distributions."""
    return sum(p[t] * math.log(p[t] / (q.get(t, EPS))) for t in p)

# --------------------------- Primitives ---------------------------

def pretrain(corpus: List[str], cfg: PretrainCfg) -> ModelHandle:
    """Train unigram model on corpus and return a model handle."""
    if not corpus:
        raise ValueError("corpus must not be empty")
    rng = random.Random(cfg.seed)
    vocab: Dict[str, int] = {}
    for doc in corpus:
        for tok in tokenize(doc)[: cfg.context_len]:
            vocab[tok] = vocab.get(tok, 0) + 1
    total = sum(vocab.values())
    token_probs = {t: c / total for t, c in vocab.items()} if total > 0 else {}
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
    for _ in range(cfg.epochs):
        shuffled = demos[:]
        rng.shuffle(shuffled)
        for i in range(0, len(shuffled), cfg.batch_size):
            batch = shuffled[i : i + cfg.batch_size]
            tokens: List[str] = []
            for ex in batch:
                tokens.extend(tokenize(ex["completion"]))
            if not tokens:
                continue
            loss = -sum(math.log(token_probs.get(t, EPS)) for t in tokens) / len(tokens)
            losses.append(loss)
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
        }
    )
    return ModelHandle(model.name, "M1.SFT", model.meta)

def train_reward_model(
    prefs: List[Tuple[str, str, str, int]],
    base: ModelHandle,
    cfg: RewardModelCfg = RewardModelCfg(),
) -> RewardModelHandle:
    """Train a simple logistic regression reward model on preferences."""
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
            if tok in token_index:
                vec[token_index[tok]] += 1.0
        return vec

    for _ in range(cfg.epochs):
        shuffled = prefs[:]
        rng.shuffle(shuffled)
        for _, a, b, label in shuffled:
            fa, fb = featurise(a), featurise(b)
            diff = [x - y for x, y in zip(fa, fb)]
            logit = sum(w * d for w, d in zip(weights, diff))
            pred = 1 / (1 + math.exp(-logit))
            grad = [(pred - label) * d for d in diff]
            for i, g in enumerate(grad):
                weights[i] -= cfg.lr * g

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
        "cfg": cfg.__dict__,
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
        return rng.choices(tokens, probs, k=length) if tokens else []

    def reward_of(tokens: List[str]) -> float:
        idx = rm.meta["token_index"]
        weights = rm.meta["weights"]
        score = 0.0
        for t in tokens:
            if t in idx:
                score += weights[idx[t]]
        return score

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
                token_probs[t] *= clipped
            total = sum(token_probs.values())
            if total > 0:
                for k in token_probs:
                    token_probs[k] /= total

    model.meta.update({"token_probs": token_probs})
    return ModelHandle(model.name, "M2.RLHF", model.meta)

# ---------------------------- Loss Terms --------------------------

def loss_sft(model: ModelHandle, demos: List[Dict[str, Any