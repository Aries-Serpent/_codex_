"""Plugin registry utilities for codex_ml."""

from .base import BasePlugin, MetricsPlugin, ModelPlugin, TokenizerPlugin
from .loader import load_plugins
from .programmatic import PluginRegistry, registry
from .registries import (
    datasets,
    load_dataset_entry_points,
    load_metric_entry_points,
    load_model_entry_points,
    load_reward_model_entry_points,
    load_rl_agent_entry_points,
    load_tokenizer_entry_points,
    load_trainer_entry_points,
    metrics,
    models,
    reward_models,
    rl_agents,
    tokenizers,
    trainers,
)

__all__ = [
    "tokenizers",
    "models",
    "datasets",
    "metrics",
    "trainers",
    "reward_models",
    "rl_agents",
    "load_tokenizer_entry_points",
    "load_model_entry_points",
    "load_dataset_entry_points",
    "load_metric_entry_points",
    "load_trainer_entry_points",
    "load_reward_model_entry_points",
    "load_rl_agent_entry_points",
    "load_plugins",
    "BasePlugin",
    "MetricsPlugin",
    "ModelPlugin",
    "TokenizerPlugin",
    "PluginRegistry",
    "registry",
]
