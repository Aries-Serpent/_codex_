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
import time
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


# --------------------------- Primitives ---------------------------


def pretrain(corpus: List[str], cfg: PretrainCfg) -> ModelHandle:
    """
    Pretraining stub → M0
    Returns a base model handle with token stats; bind to real trainer as needed.
    """
    tokens = sum(len(t) for t in corpus)
    time.sleep(0.01)
    return ModelHandle(
        "Codex-Base", "M0.Pretrained", {"tokens_seen": tokens, **cfg.__dict__}
    )


def sft(model: ModelHandle, demos: List[Dict[str, Any]], cfg: SFTCfg) -> ModelHandle:
    """
    Supervised Fine-Tuning → M1
    """
    time.sleep(0.01)
    return ModelHandle(model.name, "M1.SFT", {"samples": len(demos), **cfg.__dict__})


def train_reward_model(
    prefs: List[Tuple[str, str, str, int]], base: ModelHandle
) -> RewardModelHandle:
    """
    Reward-Model training from pairwise preferences:
    Each tuple: (prompt, completion_A, completion_B, label ∈ {0,1} for A preferred)
    """
    time.sleep(0.01)
    return RewardModelHandle("RM-Codex", base.name, {"pairs": len(prefs)})


def rlhf_ppo(model: ModelHandle, rm: RewardModelHandle, cfg: RLHFCfg) -> ModelHandle:
    """
    RLHF stage via PPO → M2
    """
    time.sleep(0.01)
    return ModelHandle(model.name, "M2.RLHF", {"rm": rm.name, **cfg.__dict__})


# ---------------------------- Loss Terms --------------------------


def loss_sft(model: ModelHandle, demos: List[Dict[str, Any]]) -> float:
    """
    Placeholder supervised loss L_SFT(M; D_code).
    Lower is better. Replace with real evaluation.
    """
    # Toy: inverse with log on sample count
    n = max(1, len(demos))
    return 1.0 / math.log1p(n)


def loss_rlhf(model: ModelHandle, rm: RewardModelHandle) -> float:
    """
    Placeholder RLHF term L_RLHF(M; R).
    Interpret lower as better (negative reward / regret proxy).
    Replace with PPO rollout evaluation against reward model.
    """
    # Toy: decreases as 'epochs' increase in RLHFCfg, if present
    steps = model.meta.get("epochs", 1)
    return 1.0 / (1.0 + steps)


def regularizer(model: ModelHandle) -> float:
    """
    Ω(M): safety/regularization proxy (e.g., KL to a reference model, policy entropy control).
    """
    # Toy: small constant with mild jitter, deterministically seeded
    rng = random.Random(model.meta.get("seed", 0))
    return 0.05 + 0.01 * rng.random()


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
