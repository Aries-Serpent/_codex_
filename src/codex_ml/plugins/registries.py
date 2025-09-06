"""Concrete plugin registries used by codex_ml."""

from __future__ import annotations

from typing import Tuple

from .registry import Registry


def _load(
    reg: Registry, group: str, flag: bool, require_api: str = "v1"
) -> Tuple[int, dict[str, str]]:
    if flag:
        return reg.load_from_entry_points(group, require_api=require_api)
    return 0, {}


# Individual registries ----------------------------------------------------

tokenizers = Registry("tokenizers")
models = Registry("models")
datasets = Registry("datasets")
metrics = Registry("metrics")
trainers = Registry("trainers")
reward_models = Registry("reward_models")
rl_agents = Registry("rl_agents")


# Entry-point loaders ------------------------------------------------------


def load_tokenizer_entry_points(flag: bool = False, group: str = "codex_ml.tokenizers"):
    return _load(tokenizers, group, flag)


def load_model_entry_points(flag: bool = False, group: str = "codex_ml.models"):
    return _load(models, group, flag)


def load_dataset_entry_points(flag: bool = False, group: str = "codex_ml.datasets"):
    return _load(datasets, group, flag)


def load_metric_entry_points(flag: bool = False, group: str = "codex_ml.metrics"):
    return _load(metrics, group, flag)


def load_trainer_entry_points(flag: bool = False, group: str = "codex_ml.trainers"):
    return _load(trainers, group, flag)


def load_reward_model_entry_points(flag: bool = False, group: str = "codex_ml.reward_models"):
    return _load(reward_models, group, flag)


def load_rl_agent_entry_points(flag: bool = False, group: str = "codex_ml.rl_agents"):
    return _load(rl_agents, group, flag)
