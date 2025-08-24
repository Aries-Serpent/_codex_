"""Toy symbolic pipeline with minimal ML loops.

The module mimics the pretrain → SFT → RLHF workflow using deterministic
bag-of-words models so that unit tests can exercise real token counting,
loss computation, and PPO-like updates without external dependencies.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

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
    beta: float = 1.0  # weight for RLHF term
    gamma: float = 0.1  # weight for regularization


@dataclass
class PretrainCfg:
    context_len: int = 4096
    objective: str = "next_token_prediction"
    lr: float = 1e-4
    epochs: int = 1

    def __post_init__(self) -> None:
        if self.context_len <= 0 or self.lr <= 0 or self.epochs <= 0:
            raise ValueError("invalid PretrainCfg")


@dataclass
class SFTCfg:
    lr: float = 5e-6
    epochs: int = 3
    batch_size: int = 32

    def __post_init__(self) -> None:
        if self.lr <= 0 or self.epochs <= 0 or self.batch_size <= 0:
            raise ValueError("invalid SFTCfg")


@dataclass
class RLHFCfg:
    algo: str = "PPO"
    ppo_clip: float = 0.2
    kl_penalty: float = 0.1
    lr: float = 1e-3
    epochs: int = 4

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


# --------------------------- Primitives ---------------------------


def pretrain(corpus: List[str], cfg: PretrainCfg) -> ModelHandle:
    """Pretraining: build a unigram model over the corpus."""
    if not corpus:
        raise ValueError("corpus is empty")
    counts: Counter[str] = Counter()
    for doc in corpus:
        counts.update(tokenize(doc)[: cfg.context_len])
    probs = _normalize(dict(counts))
    meta = {
        "tokens_seen": sum(counts.values()),
        "vocab": len(probs),
        "token_probs": probs,
        "base_probs": probs.copy(),
        **cfg.__dict__,
    }
    return ModelHandle("Codex-Base", "M0.Pretrained", meta)


def sft(model: ModelHandle, demos: List[Dict[str, Any]], cfg: SFTCfg) -> ModelHandle:
    """Supervised fine-tuning using completion token frequencies."""
    if not demos:
        raise ValueError("demos are empty")
    probs = model.meta["token_probs"].copy()
    for _ in range(cfg.epochs):
        counts: Counter[str] = Counter()
        total = 0
        for d in demos:
            tokens = tokenize(d.get("completion", ""))
            counts.update(tokens)
            total += len(tokens)
        if total == 0:
            continue
        target = {t: c / total for t, c in counts.items()}
        for t, q in target.items():
            p = probs.get(t, 1e-12)
            probs[t] = p * (1 - cfg.lr) + cfg.lr * q
        probs = _normalize(probs)
    loss = loss_sft(ModelHandle(model.name, model.stage, {"token_probs": probs}), demos)
    meta = {**model.meta, "token_probs": probs, "sft_loss": loss, "samples": len(demos)}
    return ModelHandle(model.name, "M1.SFT", meta)


def train_reward_model(
    prefs: List[Tuple[str, str, int]], base: ModelHandle
) -> RewardModelHandle:
    """Train a simple bag-of-words reward model via logistic regression."""
    if not prefs:
        raise ValueError("prefs are empty")
    weights: defaultdict[str, float] = defaultdict(float)
    lr = 0.1
    epochs = 5
    for _ in range(epochs):
        for _, a, b, label in prefs:
            fa = Counter(tokenize(a))
            fb = Counter(tokenize(b))
            diff = fa - fb
            z = sum(weights[t] * c for t, c in diff.items())
            pred = 1 / (1 + math.exp(-z))
            error = pred - label
            for t, c in diff.items():
                weights[t] -= lr * error * c
    correct = 0
    for _, a, b, label in prefs:
        fa = Counter(tokenize(a))
        fb = Counter(tokenize(b))
        diff = fa - fb
        z = sum(weights[t] * c for t, c in diff.items())
        pred = 1 / (1 + math.exp(-z))
        if (pred >= 0.5 and label == 1) or (pred < 0.5 and label == 0):
            correct += 1
    accuracy = correct / len(prefs)
    return RewardModelHandle(
        "RM-Codex",
        base.name,
        {"weights": dict(weights), "accuracy": accuracy, "pairs": len(prefs)},
    )


BANNED_TOKENS = {"drop", "delete"}


def rlhf_ppo(model: ModelHandle, rm: RewardModelHandle, cfg: RLHFCfg) -> ModelHandle:
    """RLHF stage using a minimal PPO-inspired update."""
    probs = model.meta["token_probs"].copy()
    base_probs = model.meta.get("base_probs", probs)
    weights = rm.meta["weights"]
    for _ in range(cfg.epochs):
        counts = Counter(probs)
        reward = 0.0
        for t, c in counts.items():
            reward += weights.get(t, 0.0) * c
            if t in BANNED_TOKENS:
                reward -= c  # safety penalty
        reward /= max(sum(counts.values()), 1)
        advantage = reward
        for t, c in counts.items():
            old_p = probs[t]
            update = cfg.lr * advantage * c
            new_p = old_p + update
            ratio = new_p / old_p if old_p > 0 else 1.0
            ratio = max(min(ratio, 1 + cfg.ppo_clip), 1 - cfg.ppo_clip)
            probs[t] = old_p * ratio
        probs = _normalize(probs)
    meta = {**model.meta, "token_probs": probs, "rm": rm.name, "epochs": cfg.epochs}
    meta["kl"] = regularizer(
        ModelHandle(
            model.name, model.stage, {"token_probs": probs, "base_probs": base_probs}
        )
    )
    return ModelHandle(model.name, "M2.RLHF", meta)


# ---------------------------- Loss Terms --------------------------


def loss_sft(model: ModelHandle, demos: List[Dict[str, Any]]) -> float:
    probs = model.meta["token_probs"]
    total_loss = 0.0
    total_tokens = 0
    for d in demos:
        tokens = tokenize(d.get("completion", ""))
        for t in tokens:
            p = probs.get(t, 1e-12)
            total_loss += -math.log(p)
        total_tokens += len(tokens)
    if total_tokens == 0:
        return 0.0
    return total_loss / total_tokens


def loss_rlhf(model: ModelHandle, rm: RewardModelHandle) -> float:
    probs = model.meta["token_probs"]
    weights = rm.meta["weights"]
    reward = sum(weights.get(t, 0.0) * p for t, p in probs.items())
    return -reward


def regularizer(model: ModelHandle) -> float:
    probs = model.meta["token_probs"]
    base = model.meta.get("base_probs", probs)
    kl = 0.0
    for t, p in probs.items():
        q = base.get(t, 1e-12)
        kl += p * math.log(p / q)
    return kl


def objective_U(
    alpha: float, beta: float, gamma: float, Lsft: float, Lrlhf: float, Omega: float
) -> float:
    return alpha * Lsft + beta * Lrlhf + gamma * Omega


# --------------------------- Orchestration ------------------------


def run_codex_symbolic_pipeline(
    *,
    corpus: List[str],
    demos: List[Dict[str, Any]],
    prefs: List[Tuple[str, str, int]],
    w: Weights = Weights(),
    pre_cfg: PretrainCfg = PretrainCfg(),
    sft_cfg: SFTCfg = SFTCfg(),
    rlhf_cfg: RLHFCfg = RLHFCfg(),
) -> Dict[str, Any]:
    if not corpus or not demos or not prefs:
        raise ValueError("corpus, demos and prefs must be non-empty")
    M0 = pretrain(corpus, pre_cfg)
    M1 = sft(M0, demos, sft_cfg)
    RM = train_reward_model(prefs, M1)
    M2 = rlhf_ppo(M1, RM, rlhf_cfg)

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


# --------------------------- Example Run --------------------------

if __name__ == "__main__":
    toy_corpus = ["def add(a,b): return a+b", "SELECT * FROM users;", "# docs..."]
    toy_demos = [
        {"prompt": "Write a CLI that echoes input", "completion": "print(input())"},
        {"prompt": "Create a Bash script to gzip a folder", "completion": "tar -czf"},
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
        rlhf_cfg=RLHFCfg(algo="PPO", ppo_clip=0.2, kl_penalty=0.1, lr=1e-3, epochs=4),
    )
    print(json.dumps(summary, indent=2))
