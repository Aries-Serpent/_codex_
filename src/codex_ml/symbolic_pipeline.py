# ChatGPT Codex — Functional Training Pipeline
# ============================================
"""Simplified but functional training pipeline for Codex.

This module replaces the earlier symbolic scaffold with concrete
implementations for each stage of the training workflow:

* pretraining – builds a unigram language model
* supervised fine‑tuning – updates the model on demonstrations
* reward model training – logistic regression on preference pairs
* RLHF via PPO – policy gradient updates using the reward model

The components are intentionally lightweight and rely only on the Python
standard library so that the tests run quickly.  Nevertheless, the code mirrors
the structure of real world systems: tokenisation, batching, gradient updates
and evaluation metrics are implemented for each stage.  Deterministic seeding is
used throughout to guarantee reproducible outputs; each configuration defaults
to ``seed=0`` so runs are reproducible without manual seeding.  Each step
produces a :class:`ModelHandle` containing light‑weight metadata so the overall
pipeline resembles a miniature end‑to‑end training loop.
"""

from __future__ import annotations

import json
import math
import random
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

# ---------------------------------------------------------------------------
# Tokenisation utilities
# ---------------------------------------------------------------------------

TOKEN_RE = re.compile(r"\w+|[^\s\w]", re.UNICODE)

# Small constant used for numerical stability when taking logarithms.
EPS = 1e-8


def tokenize(text: str) -> List[str]:
    """Split ``text`` into case‑insensitive word/punctuation tokens."""

    return TOKEN_RE.findall(text.lower())


def kl_divergence(p: Dict[str, float], q: Dict[str, float]) -> float:
    """Kullback–Leibler divergence ``KL(p || q)`` for discrete distributions."""

    return sum(p[t] * math.log(p[t] / (q.get(t, EPS))) for t in p)


# ---------------------------------------------------------------------------
# Configuration dataclasses
# ---------------------------------------------------------------------------


@dataclass
class Weights:
    alpha: float = 1.0  # weight for SFT loss
    beta: float = 1.0  # weight for RLHF term
    gamma: float = 0.1  # weight for regularisation


@dataclass
class PretrainCfg:
    context_len: int = 4096
    objective: str = "next_token_prediction"
    lr: float = 1e-2
    epochs: int = 1
    seed: int = 0

    def __post_init__(self) -> None:  # pragma: no cover - simple validation
        if self.context_len <= 0 or self.lr <= 0 or self.epochs <= 0:
            raise ValueError("invalid PretrainCfg parameters")


@dataclass
class SFTCfg:
    lr: float = 1e-2
    epochs: int = 1
    batch_size: int = 32
    seed: int = 0

    def __post_init__(self) -> None:  # pragma: no cover - simple validation
        if self.lr <= 0 or self.epochs <= 0 or self.batch_size <= 0:
            raise ValueError("invalid SFTCfg parameters")


@dataclass
class RewardModelCfg:
    lr: float = 0.1
    epochs: int = 5
    seed: int = 0

    def __post_init__(self) -> None:  # pragma: no cover - simple validation
        if self.lr <= 0 or self.epochs <= 0:
            raise ValueError("invalid RewardModelCfg parameters")


@dataclass
class RLHFCfg:
    algo: str = "PPO"
    ppo_clip: float = 0.2
    kl_penalty: float = 0.1
    epochs: int = 1
    lr: float = 1e-2
    seed: int = 0

    def __post_init__(self) -> None:  # pragma: no cover - simple validation
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
    """Create the base model ``M0`` via next‑token prediction.

    The function builds a simple unigram language model over ``corpus`` and
    records book‑keeping metadata such as the number of tokens seen and the
    optimisation hyper‑parameters (context length, learning rate and epochs).
    A :class:`ModelHandle` for stage ``M0`` is returned with this metadata.
    """

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
        "context_len": cfg.context_len,
        "objective": cfg.objective,
        "seed": cfg.seed,
        "lr": cfg.lr,
        "epochs": cfg.epochs,
        "rng_state": rng.getstate(),
    }
    return ModelHandle("Codex-Base", "M0.Pretrained", meta)


def sft(model: ModelHandle, demos: List[Dict[str, Any]], cfg: SFTCfg) -> ModelHandle:
    """Supervised fine‑tuning of ``M0`` on curated demos to yield ``M1``.

    Each demonstration consists of a ``prompt`` and ``completion`` pair.  The
    model is updated using these examples and the metadata tracks statistics
    such as the number of samples processed, learning rate and epochs.
    """

    if not demos:
        raise ValueError("demos must not be empty")
    rng = random.Random(cfg.seed)
    token_probs = model.meta["token_probs"].copy()
    vocab = model.meta["vocab"].copy()
    losses: List[float] = []
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
            "num_samples": len(demos),
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
    """Learn a reward model from pairwise preferences.

    ``prefs`` contains tuples of the form ``(prompt, completion_a, completion_b,
    label)`` where ``label`` is ``1`` when ``completion_a`` is preferred and ``0``
    otherwise.  A light‑weight logistic regression model is trained and returned
    as a :class:`RewardModelHandle`.
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
            if tok in token_index:
                vec[token_index[tok]] += 1.0
        return vec

    for _ in range(cfg.epochs):
        rng.shuffle(prefs)
        for _, a, b, label in prefs:
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
    """Use PPO with the reward model to obtain the final model ``M2``.

    The policy is optimised against ``rm`` while applying PPO clipping and a KL
    penalty.  The updated token distribution is stored in the resulting
    :class:`ModelHandle` whose metadata also retains the PPO hyper‑parameters.
    """

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

    model.meta.update(
        {
            "token_probs": token_probs,
            "ppo_clip": cfg.ppo_clip,
            "kl_penalty": cfg.kl_penalty,
            "epochs_rlhf": cfg.epochs,
            "lr_rlhf": cfg.lr,
            "algo": cfg.algo,
            "seed_rlhf": cfg.seed,
        }
    )
    return ModelHandle(model.name, "M2.RLHF", model.meta)


# ---------------------------------------------------------------------------
# Loss terms
# ---------------------------------------------------------------------------


def loss_sft(model: ModelHandle, demos: List[Dict[str, Any]]) -> float:
    """Cross‑entropy of demo completions under ``model``."""

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
    """Combined objective ``U = α·L_SFT + β·L_RLHF + γ·Ω``."""

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
    """Run the full training pipeline and compute the combined objective.

    The orchestration mirrors the symbolic pipeline:
    ``corpus`` → :func:`pretrain` → ``demos`` → :func:`sft` →
    ``prefs`` → :func:`train_reward_model` → :func:`rlhf_ppo`.
    The resulting model ``M2`` is evaluated with :func:`loss_sft`,
    :func:`loss_rlhf` and :func:`regularizer` and combined into
    ``U = α·L_SFT + β·L_RLHF + γ·Ω``.  A JSON‑style summary with model handles,
    losses and the objective value is returned.
    """

    M0 = pretrain(corpus, pre_cfg)
    M1 = sft(M0, demos, sft_cfg)
    RM = train_reward_model(prefs, M1, rm_cfg)
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


# ---------------------------------------------------------------------------
# Example run
# ---------------------------------------------------------------------------

if __name__ == "__main__":  # pragma: no cover - manual execution helper
    toy_corpus = ["def add(a,b): return a+b", "SELECT * FROM users;", "# docs..."]
    toy_demos = [
        {"prompt": "Write a CLI", "completion": "print('hello')"},
        {"prompt": "Create a script", "completion": "echo hi"},
    ]
    toy_prefs = [("p", "good", "bad", 1)]

    summary = run_codex_symbolic_pipeline(
        corpus=toy_corpus,
        demos=toy_demos,
        prefs=toy_prefs,
        w=Weights(alpha=1.0, beta=1.2, gamma=0.05),
        pre_cfg=PretrainCfg(seed=0),
        sft_cfg=SFTCfg(seed=0),
        rlhf_cfg=RLHFCfg(seed=0),
    )
    print(json.dumps(summary, indent=2))
