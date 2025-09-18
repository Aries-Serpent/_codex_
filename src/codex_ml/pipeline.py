"""End-to-end Codex pipeline implementation used in offline CI.

The previous placeholder returned synthetic metrics only when the
``CODEX_FALLBACK`` environment variable was set, making it impossible to run
tests or CLI commands without enabling the fallback.  This module now provides
real, deterministic logic that exercises each stage of the pipeline while
remaining lightweight enough for local development.
"""

from __future__ import annotations

import json
import logging
import os
import random
import time
from collections import Counter
from contextlib import contextmanager
from pathlib import Path
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


@contextmanager
def _temporary_env(overrides: Mapping[str, Optional[str]]):
    """Temporarily apply environment variable overrides."""

    previous: Dict[str, Optional[str]] = {}
    try:
        for key, value in overrides.items():
            previous[key] = os.environ.get(key)
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        yield
    finally:  # pragma: no cover - defensive cleanup
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


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


def _augment_prompts(
    prompts: Iterable[str], rng: Optional[random.Random] = None
) -> list[dict[str, str]]:
    augmented: list[dict[str, str]] = []
    templates = [
        "Response: Consult Codex knowledge base for best practices.",
        "Response: Provide actionable remediation steps.",
        "Response: Summarise findings and reference policy IDs.",
        "Response: Escalate to the automation checklist for review.",
    ]
    for index, prompt in enumerate(prompts):
        if not isinstance(prompt, str):
            continue
        cleaned = prompt.strip()
        if not cleaned:
            continue
        if rng is None:
            suffix = templates[index % len(templates)]
        else:
            suffix = rng.choice(templates)
        augmented.append({"prompt": cleaned, "completion": f"{cleaned}\n\n{suffix}"})
    return augmented


def _coerce_string_list(value: Any, *, name: str) -> list[str]:
    if value is None:
        raise ValueError(f"{name} must be provided")
    if isinstance(value, (str, bytes)):
        raise ValueError(f"{name} must be a sequence of strings")
    if not isinstance(value, Sequence):
        raise ValueError(f"{name} must be a sequence")
    result: list[str] = []
    for idx, item in enumerate(value):
        if not isinstance(item, str):
            raise ValueError(f"{name}[{idx}] must be a string")
        result.append(item)
    return result


def _coerce_demo_list(value: Any) -> list[Mapping[str, Any]]:
    if value is None:
        raise ValueError("demos must be provided")
    if not isinstance(value, Sequence):
        raise ValueError("demos must be a sequence of mappings")
    demos: list[Mapping[str, Any]] = []
    for idx, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"demos[{idx}] must be a mapping")
        demos.append(dict(item))
    return demos


def _coerce_pairwise_list(value: Any) -> list[Tuple[str, str, str, int]]:
    if value is None:
        raise ValueError("pairwise comparisons must be provided")
    if not isinstance(value, Sequence):
        raise ValueError("pairwise comparisons must be a sequence")
    pairs: list[Tuple[str, str, str, int]] = []
    for idx, item in enumerate(value):
        if isinstance(item, Mapping):
            try:
                label = str(item["label"])
                chosen = str(item["chosen"])
                rejected = str(item["rejected"])
                preference = int(item.get("preference", 1))
            except KeyError as exc:
                raise ValueError(f"pairwise[{idx}] missing key {exc.args[0]}") from exc
            except Exception as exc:
                raise ValueError(f"pairwise[{idx}] has invalid values") from exc
        elif isinstance(item, Sequence) and len(item) == 4:
            label, chosen, rejected, preference = item
            if not all(isinstance(x, str) for x in (label, chosen, rejected)):
                raise ValueError(f"pairwise[{idx}] must contain three strings and an integer")
            try:
                preference = int(preference)
            except Exception as exc:
                raise ValueError(f"pairwise[{idx}] preference must be an integer") from exc
        else:
            raise ValueError("pairwise comparisons must be mappings or four-tuples")
        pairs.append((label, chosen, rejected, preference))
    return pairs


def _as_positive_float(value: Any, name: str, *, allow_zero: bool = False) -> float:
    try:
        result = float(value)
    except Exception as exc:  # pragma: no cover - defensive
        raise ValueError(f"{name} must be a number") from exc
    if allow_zero:
        if result < 0:
            raise ValueError(f"{name} must be non-negative")
    elif result <= 0:
        raise ValueError(f"{name} must be positive")
    return result


def _as_positive_int(value: Any, name: str) -> int:
    try:
        result = int(value)
    except Exception as exc:  # pragma: no cover - defensive
        raise ValueError(f"{name} must be an integer") from exc
    if result <= 0:
        raise ValueError(f"{name} must be positive")
    return result


def _maybe_int(value: Any, name: str) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except Exception as exc:  # pragma: no cover - defensive
        raise ValueError(f"{name} must be an integer") from exc


def _coerce_bool(value: Any, name: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off"}:
            return False
    raise ValueError(f"{name} must be a boolean value")


def _parse_weights(data: Any) -> TrainingWeights:
    mapping = data or {}
    if not isinstance(mapping, Mapping):
        raise ValueError("weights must be a mapping")
    alpha = _as_positive_float(mapping.get("alpha", 1.0), "weights.alpha")
    beta = _as_positive_float(mapping.get("beta", 1.0), "weights.beta")
    gamma = _as_positive_float(mapping.get("gamma", 0.1), "weights.gamma")
    return TrainingWeights(alpha=alpha, beta=beta, gamma=gamma)


def _parse_pretraining(data: Any) -> PretrainingConfig:
    mapping = data or {}
    if not isinstance(mapping, Mapping):
        raise ValueError("pretraining must be a mapping")
    model_size = str(mapping.get("model_size", "placeholder"))
    context_length = _as_positive_int(
        mapping.get("context_length", 2048), "pretraining.context_length"
    )
    return PretrainingConfig(model_size=model_size, context_length=context_length)


def _parse_sft(data: Any) -> SFTConfig:
    mapping = data or {}
    if not isinstance(mapping, Mapping):
        raise ValueError("sft must be a mapping")
    batch_size = _as_positive_int(mapping.get("batch_size", 16), "sft.batch_size")
    learning_rate = _as_positive_float(mapping.get("learning_rate", 1e-4), "sft.learning_rate")
    epochs = _as_positive_int(mapping.get("epochs", 1), "sft.epochs")
    return SFTConfig(batch_size=batch_size, learning_rate=learning_rate, epochs=epochs)


def _parse_rlhf(data: Any) -> RLHFConfig:
    mapping = data or {}
    if not isinstance(mapping, Mapping):
        raise ValueError("rlhf must be a mapping")
    algorithm = str(mapping.get("algorithm", "PPO"))
    kl_penalty = _as_positive_float(
        mapping.get("kl_penalty", 0.05), "rlhf.kl_penalty", allow_zero=True
    )
    ppo_epochs = _as_positive_int(mapping.get("ppo_epochs", 1), "rlhf.ppo_epochs")
    return RLHFConfig(algorithm=algorithm, kl_penalty=kl_penalty, ppo_epochs=ppo_epochs)


def _parse_validation(data: Any) -> ValidationThresholds:
    mapping = data or {}
    if not isinstance(mapping, Mapping):
        raise ValueError("validation must be a mapping")
    syntax_ok = _as_positive_float(
        mapping.get("syntax_ok", 0.8), "validation.syntax_ok", allow_zero=True
    )
    logic_ok = _as_positive_float(
        mapping.get("logic_ok", 0.8), "validation.logic_ok", allow_zero=True
    )
    security_ok = _as_positive_float(
        mapping.get("security_ok", 0.8), "validation.security_ok", allow_zero=True
    )
    perf_ok = _as_positive_float(mapping.get("perf_ok", 0.6), "validation.perf_ok", allow_zero=True)
    for name, value in {
        "validation.syntax_ok": syntax_ok,
        "validation.logic_ok": logic_ok,
        "validation.security_ok": security_ok,
        "validation.perf_ok": perf_ok,
    }.items():
        if value > 1:
            raise ValueError(f"{name} must be between 0 and 1")
    return ValidationThresholds(
        syntax_ok=syntax_ok,
        logic_ok=logic_ok,
        security_ok=security_ok,
        perf_ok=perf_ok,
    )


def _build_component_env(mapping: Any) -> Dict[str, Optional[str]]:
    if not mapping:
        return {}
    if not isinstance(mapping, Mapping):
        raise ValueError("components must be a mapping")
    overrides: Dict[str, Optional[str]] = {}
    spec = {
        "tokenizer": ("CODEX_TOKENIZER_PATH", "CODEX_TOKENIZER_KWARGS"),
        "reward_model": ("CODEX_REWARD_PATH", "CODEX_REWARD_KWARGS"),
        "rl_agent": ("CODEX_RL_PATH", "CODEX_RL_KWARGS"),
    }
    for key, value in mapping.items():
        if key not in spec:
            continue
        path_env, kwargs_env = spec[key]
        if isinstance(value, str):
            overrides[path_env] = value
        elif isinstance(value, Mapping):
            path = value.get("path")
            if path:
                overrides[path_env] = str(path)
            if "kwargs" in value and value["kwargs"] is not None:
                try:
                    overrides[kwargs_env] = json.dumps(value["kwargs"])
                except TypeError as exc:  # pragma: no cover - defensive
                    raise ValueError(f"components.{key}.kwargs must be JSON serialisable") from exc
        else:
            raise ValueError(f"components.{key} must be a string or mapping")
    return overrides


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
    seed: Optional[int] = None,
    summary_path: Optional[str] = None,
    log_summary: bool = True,
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

    rng = random.Random(seed) if seed is not None else None
    synthetic = _augment_prompts(synth_prompts or [], rng) if synth_prompts else []

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

    if seed is not None:
        summary["seed"] = seed

    if summary_path:
        target = Path(summary_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    log_payload = {
        "passed": validation["passed"],
        "seed": seed,
        "syntax": validation["syntax"],
        "logic": validation["logic"],
        "security": validation["security"],
        "performance": validation["performance"],
    }

    log_line = json.dumps(log_payload, sort_keys=True)
    if log_summary:
        logger.info("codex_pipeline_summary=%s", log_line)
    else:  # pragma: no cover - disabled logging path
        logger.debug("codex_pipeline_summary=%s", log_line)

    return summary


def run_codex_pipeline_from_config(
    config: Mapping[str, Any],
    *,
    seed: Optional[int] = None,
    summary_path: Optional[str] = None,
    log_summary: Optional[bool] = None,
) -> Dict[str, Any]:
    """Execute the pipeline using a dictionary-style configuration.

    Parameters
    ----------
    config:
        Mapping describing the corpus, demonstrations, pairwise preferences and
        per-stage settings.  The structure mirrors
        ``configs/pipeline_inputs/smoke.yaml``.
    seed:
        Optional override for ``config['seed']``.  When provided the seed is
        used to initialise the deterministic helpers that augment synthetic
        prompts.
    summary_path:
        Optional override for ``config['summary_path']``.  When present the
        pipeline writes the JSON summary to this location.
    log_summary:
        Override for ``config['log_summary']``; set to ``False`` to disable the
        structured INFO log entry.
    """

    if not isinstance(config, Mapping):
        raise TypeError("config must be a mapping")

    corpus = _coerce_string_list(config.get("corpus"), name="corpus")
    demos = _coerce_demo_list(config.get("demos"))
    pairwise_source = config.get("pairwise") or config.get("pairwise_prefs")
    pairwise = _coerce_pairwise_list(pairwise_source)

    weights = _parse_weights(config.get("weights"))
    pre_cfg = _parse_pretraining(config.get("pretraining"))
    sft_cfg = _parse_sft(config.get("sft"))
    rlhf_cfg = _parse_rlhf(config.get("rlhf"))
    val_cfg = _parse_validation(config.get("validation"))

    synth_prompts = None
    if "synth_prompts" in config and config.get("synth_prompts") is not None:
        synth_prompts = _coerce_string_list(config.get("synth_prompts"), name="synth_prompts")

    selected_seed = seed
    if selected_seed is None and "seed" in config:
        selected_seed = _maybe_int(config.get("seed"), "seed")

    selected_summary_path = summary_path
    if selected_summary_path is None and config.get("summary_path") is not None:
        selected_summary_path = str(config.get("summary_path"))

    if log_summary is None:
        log_flag = True
        if "log_summary" in config:
            log_flag = _coerce_bool(config.get("log_summary"), "log_summary")
    else:
        log_flag = log_summary

    overrides = _build_component_env(config.get("components"))

    with _temporary_env(overrides):
        return run_codex_pipeline(
            corpus=corpus,
            demos=demos,
            pairwise_prefs=pairwise,
            weights=weights,
            pre_cfg=pre_cfg,
            sft_cfg=sft_cfg,
            rlhf_cfg=rlhf_cfg,
            val_t=val_cfg,
            synth_prompts=synth_prompts,
            seed=selected_seed,
            summary_path=selected_summary_path,
            log_summary=log_flag,
        )
