"""End-to-end Codex pipeline implementation used in offline CI.

The previous placeholder returned synthetic metrics only when the
``CODEX_FALLBACK`` environment variable was set, making it impossible to run
tests or CLI commands without enabling the fallback.  This module now provides
real, deterministic logic that exercises each stage of the pipeline while
remaining lightweight enough for local development.
"""

from __future__ import annotations

import logging
import os
import time
from collections import Counter
from statistics import fmean
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence, Tuple

from .config import (
    PretrainingConfig,
    RLHFConfig,
    SFTConfig,
    TrainingWeights,
    ValidationThresholds,
)
from .interfaces.registry import get_component
from .interfaces.reward_model import HeuristicRewardModel, RewardModel
from .interfaces.rl import BanditRLAgent, RLAgent
from .interfaces.tokenizer import TokenizerAdapter, WhitespaceTokenizer, get_tokenizer

logger = logging.getLogger(__name__)

DEFAULT_REWARD_PATH = "codex_ml.interfaces.reward_model:HeuristicRewardModel"
DEFAULT_RL_PATH = "codex_ml.interfaces.rl:BanditRLAgent"


def _resolve_tokenizer() -> TokenizerAdapter:
    name = os.getenv("CODEX_TOKENIZER_NAME", "whitespace")
    kwargs_env = os.getenv("CODEX_TOKENIZER_KWARGS")
    kwargs: Dict[str, Any] = {}
    if kwargs_env:
        try:
            import json

            kwargs = json.loads(kwargs_env)
        except Exception:  # pragma: no cover - invalid env config
            logger.warning("Failed to decode CODEX_TOKENIZER_KWARGS; using defaults")
    try:
        tokenizer = get_tokenizer(name, **kwargs)
        logger.info("Using tokenizer: %s", tokenizer.__class__.__name__)
        return tokenizer
    except Exception as exc:  # pragma: no cover - fallback path
        logger.warning("Falling back to WhitespaceTokenizer: %s", exc)
        return WhitespaceTokenizer()


def _resolve_reward_model() -> RewardModel:
    try:
        model = get_component("CODEX_REWARD_PATH", DEFAULT_REWARD_PATH)
        logger.info("Using reward model: %s", model.__class__.__name__)
        return model
    except Exception as exc:  # pragma: no cover - fallback path
        logger.warning("Falling back to HeuristicRewardModel: %s", exc)
        return HeuristicRewardModel()


def _resolve_rl_agent() -> RLAgent:
    try:
        agent = get_component("CODEX_RL_PATH", DEFAULT_RL_PATH)
        logger.info("Using RL agent: %s", agent.__class__.__name__)
        return agent
    except Exception as exc:  # pragma: no cover - fallback path
        logger.warning("Falling back to BanditRLAgent: %s", exc)
        return BanditRLAgent()


def _clean_corpus(corpus: Sequence[str]) -> list[str]:
    cleaned: list[str] = []
    for idx, doc in enumerate(corpus):
        if not isinstance(doc, str):
            raise ValueError(f"corpus[{idx}] must be a string")
        text = doc.strip()
        if not text:
            continue
        cleaned.append(text)
    if not cleaned:
        raise ValueError("corpus must contain at least one non-empty document")
    return cleaned


def _prepare_demos(demos: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    prepared: list[dict[str, Any]] = []
    for idx, item in enumerate(demos):
        if not isinstance(item, Mapping):
            raise ValueError(f"demos[{idx}] must be a mapping")
        prompt = item.get("prompt")
        completion = item.get("completion")
        if not isinstance(prompt, str) or not isinstance(completion, str):
            raise ValueError(f"demos[{idx}] must include string prompt and completion")
        metadata = item.get("metadata")
        prepared.append(
            {
                "prompt": prompt.strip(),
                "completion": completion.strip(),
                "metadata": metadata if isinstance(metadata, Mapping) else None,
            }
        )
    if not prepared:
        raise ValueError("demos must contain at least one example")
    return prepared


def _prepare_pairwise(
    prefs: Sequence[Tuple[str, str, str, int]],
) -> list[Tuple[str, str, str, int]]:
    prepared: list[Tuple[str, str, str, int]] = []
    for idx, entry in enumerate(prefs):
        if len(entry) != 4:
            raise ValueError("pairwise preferences must contain four elements")
        label, chosen, rejected, preference = entry
        if not all(isinstance(x, str) for x in (label, chosen, rejected)):
            raise ValueError(f"pairwise[{idx}] must contain strings for label/chosen/rejected")
        if not isinstance(preference, int):
            raise ValueError(f"pairwise[{idx}] preference must be an integer")
        prepared.append((label.strip(), chosen.strip(), rejected.strip(), preference))
    if not prepared:
        raise ValueError("pairwise_prefs must contain at least one comparison")
    return prepared


def _run_pretraining_stage(
    docs: Sequence[str], tokenizer: TokenizerAdapter, cfg: PretrainingConfig
) -> dict[str, Any]:
    start = time.perf_counter()
    vocab: Counter[str] = Counter()
    token_counts: list[int] = []
    for text in docs:
        tokens = [tok for tok in text.split() if tok]
        vocab.update(tokens)
        token_counts.append(len(tokens))

    total_tokens = sum(token_counts)
    average_tokens = fmean(token_counts)
    max_tokens = max(token_counts)
    context_utilization = min(1.0, max_tokens / max(1, cfg.context_length))

    duration = time.perf_counter() - start
    logger.debug("Pretraining stage completed in %.3fs", duration)
    return {
        "documents": len(docs),
        "total_tokens": total_tokens,
        "avg_tokens_per_doc": average_tokens,
        "max_tokens_per_doc": max_tokens,
        "unique_tokens": len(vocab),
        "context_utilization": context_utilization,
        "tokenizer_vocab_size": tokenizer.vocab_size,
        "duration_s": duration,
    }


def _run_sft_stage(
    demos: Sequence[dict[str, Any]],
    reward_model: RewardModel,
    cfg: SFTConfig,
) -> dict[str, Any]:
    start = time.perf_counter()
    completion_lengths = [len(item["completion"].split()) for item in demos]
    prompt_lengths = [len(item["prompt"].split()) for item in demos]
    rewards = reward_model.batch_evaluate(
        [(item["prompt"], item["completion"]) for item in demos],
        metadatas=[item.get("metadata") for item in demos],
    )
    reward_summary = reward_model.learn(demos)

    duration = time.perf_counter() - start
    logger.debug("SFT stage completed in %.3fs", duration)
    return {
        "examples": len(demos),
        "avg_prompt_tokens": fmean(prompt_lengths),
        "avg_completion_tokens": fmean(completion_lengths),
        "mean_reward": fmean(rewards),
        "min_reward": min(rewards),
        "max_reward": max(rewards),
        "reward_training": reward_summary,
        "config": {
            "batch_size": cfg.batch_size,
            "learning_rate": cfg.learning_rate,
            "epochs": cfg.epochs,
        },
        "duration_s": duration,
    }


def _run_rlhf_stage(
    pairs: Sequence[Tuple[str, str, str, int]],
    reward_model: RewardModel,
    agent: RLAgent,
    cfg: RLHFConfig,
) -> dict[str, Any]:
    start = time.perf_counter()
    actions: list[str] = []
    rewards: list[float] = []
    correct = 0
    agent_updates = 0
    agent_reward_total = 0.0
    for label, chosen, rejected, preference in pairs:
        state = {"label": label, "candidates": [chosen, rejected]}
        selected = agent.act(state)
        reward_chosen = reward_model.evaluate(label, chosen)
        reward_rejected = reward_model.evaluate(label, rejected)
        delta = reward_chosen - reward_rejected
        preferred = chosen if preference >= 0 else rejected
        if selected == preferred:
            correct += 1
            reward_value = abs(delta)
        else:
            reward_value = -abs(delta)
        actions.append(selected)
        rewards.append(reward_value)
        metrics = agent.update({"actions": [selected], "rewards": [reward_value]})
        agent_updates += metrics.get("updates", 1)
        agent_reward_total += metrics.get("mean_reward", reward_value)

    agent_metrics = {
        "updates": agent_updates,
        "mean_reward": agent_reward_total / agent_updates if agent_updates else 0.0,
    }
    duration = time.perf_counter() - start
    logger.debug("RLHF stage completed in %.3fs", duration)
    return {
        "comparisons": len(pairs),
        "win_rate": correct / len(pairs) if pairs else 0.0,
        "mean_reward_delta": fmean(rewards) if rewards else 0.0,
        "agent_metrics": agent_metrics,
        "config": {
            "algorithm": cfg.algorithm,
            "kl_penalty": cfg.kl_penalty,
            "ppo_epochs": cfg.ppo_epochs,
        },
        "duration_s": duration,
    }


def _compute_validation(
    pre: Mapping[str, Any],
    sft: Mapping[str, Any],
    rlhf: Mapping[str, Any],
    thresholds: ValidationThresholds,
) -> dict[str, Any]:
    syntax_score = 1.0 if pre["documents"] > 0 else 0.0
    logic_score = max(0.0, min(1.0, (sft["mean_reward"] + 1) / 2))
    min_reward = sft["min_reward"]
    security_score = 1.0 if min_reward >= 0 else max(0.0, 1.0 + min_reward)
    perf_score = max(0.0, 1.0 - pre["context_utilization"] / 2 + rlhf["win_rate"] / 2)

    passed = (
        syntax_score >= thresholds.syntax_ok
        and logic_score >= thresholds.logic_ok
        and security_score >= thresholds.security_ok
        and perf_score >= thresholds.perf_ok
    )

    return {
        "syntax": syntax_score,
        "logic": logic_score,
        "security": security_score,
        "performance": perf_score,
        "passed": passed,
        "thresholds": {
            "syntax_ok": thresholds.syntax_ok,
            "logic_ok": thresholds.logic_ok,
            "security_ok": thresholds.security_ok,
            "perf_ok": thresholds.perf_ok,
        },
    }


def _augment_prompts(prompts: Iterable[str]) -> list[dict[str, str]]:
    augmented: list[dict[str, str]] = []
    for prompt in prompts:
        if not isinstance(prompt, str):
            continue
        cleaned = prompt.strip()
        if not cleaned:
            continue
        augmented.append(
            {
                "prompt": cleaned,
                "completion": f"{cleaned}\n\nResponse: Consult Codex knowledge base for best practices.",
            }
        )
    return augmented


def run_codex_pipeline(
    *,
    corpus: Sequence[str],
    demos: Sequence[Dict[str, str]],
    pairwise_prefs: Sequence[Tuple[str, str, str, int]],
    weights: TrainingWeights,
    pre_cfg: PretrainingConfig,
    sft_cfg: SFTConfig,
    rlhf_cfg: RLHFConfig,
    val_t: ValidationThresholds,
    synth_prompts: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    """Execute the Codex training pipeline with deterministic heuristics.

    The function performs lightweight preprocessing and evaluation of the
    provided data.  It is intentionally CPU only and avoids network access so
    that smoke tests and offline CI runs complete quickly.
    """

    docs = _clean_corpus(corpus)
    demo_items = _prepare_demos(demos)
    pairwise_items = _prepare_pairwise(pairwise_prefs)

    tokenizer = _resolve_tokenizer()
    reward_model = _resolve_reward_model()
    rl_agent = _resolve_rl_agent()

    pre_summary = _run_pretraining_stage(docs, tokenizer, pre_cfg)
    sft_summary = _run_sft_stage(demo_items, reward_model, sft_cfg)
    rlhf_summary = _run_rlhf_stage(pairwise_items, reward_model, rl_agent, rlhf_cfg)
    validation = _compute_validation(pre_summary, sft_summary, rlhf_summary, val_t)

    synthetic = _augment_prompts(synth_prompts or []) if synth_prompts else []

    summary: Dict[str, Any] = {
        "stages": {
            "pretraining": pre_summary,
            "sft": sft_summary,
            "rlhf": rlhf_summary,
            "validation": validation,
        },
        "weights": {
            "alpha": weights.alpha,
            "beta": weights.beta,
            "gamma": weights.gamma,
        },
        "config": {
            "pretraining": {
                "model_size": pre_cfg.model_size,
                "context_length": pre_cfg.context_length,
            },
            "sft": {
                "batch_size": sft_cfg.batch_size,
                "learning_rate": sft_cfg.learning_rate,
                "epochs": sft_cfg.epochs,
            },
            "rlhf": {
                "algorithm": rlhf_cfg.algorithm,
                "kl_penalty": rlhf_cfg.kl_penalty,
                "ppo_epochs": rlhf_cfg.ppo_epochs,
            },
            "validation": {
                "syntax_ok": val_t.syntax_ok,
                "logic_ok": val_t.logic_ok,
                "security_ok": val_t.security_ok,
                "perf_ok": val_t.perf_ok,
            },
        },
        "components": {
            "tokenizer": tokenizer.__class__.__name__,
            "reward_model": reward_model.__class__.__name__,
            "rl_agent": rl_agent.__class__.__name__,
        },
        "synthetic_responses": synthetic,
    }

    logger.info(
        "Pipeline complete — passed=%s syntax=%.2f logic=%.2f security=%.2f performance=%.2f",
        validation["passed"],
        validation["syntax"],
        validation["logic"],
        validation["security"],
        validation["performance"],
    )

    return summary
