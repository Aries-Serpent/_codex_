"""Concrete plugin registries used by codex_ml."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Tuple

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


# Bundled offline-friendly defaults -----------------------------------------


def _instantiate_tokenizer(alias: str, **kwargs: Any) -> Any:
    from codex_ml.registry.tokenizers import get_tokenizer

    return get_tokenizer(alias, **kwargs)


def _merge_model_cfg(cfg: Any = None, **overrides: Any) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    if cfg is not None:
        if not isinstance(cfg, Mapping):
            raise TypeError(
                "Model configuration must be a mapping when using the plugin catalogue; "
                f"received {type(cfg).__name__}."
            )
        merged.update(cfg)  # type: ignore[arg-type]
    merged.update(overrides)
    return merged


def _instantiate_model(alias: str, cfg: Any = None, **kwargs: Any) -> Any:
    from codex_ml.models.registry import get_model

    merged_cfg = _merge_model_cfg(cfg, **kwargs)
    return get_model(alias, merged_cfg)


def _instantiate_dataset(alias: str, **kwargs: Any) -> Any:
    from codex_ml.data.registry import get_dataset

    return get_dataset(alias, **kwargs)


def _instantiate_metric(alias: str, **kwargs: Any) -> Any:
    from codex_ml.metrics.registry import get_metric

    metric_fn = get_metric(alias)
    if not kwargs:
        return metric_fn

    bound_kwargs = dict(kwargs)

    def _bound_metric(*args: Any, **call_kwargs: Any) -> Any:
        params = dict(bound_kwargs)
        params.update(call_kwargs)
        return metric_fn(*args, **params)

    return _bound_metric


@tokenizers.register("hf", backend="codex_ml.registry.tokenizers", target="hf")
def _tokenizer_hf(**kwargs: Any):
    """Expose the standard Hugging Face tokenizer adapter via the plugin registry."""

    return _instantiate_tokenizer("hf", **kwargs)


@tokenizers.register(
    "gpt2-offline",
    backend="codex_ml.registry.tokenizers",
    target="gpt2-offline",
    offline_default=True,
)
def _tokenizer_gpt2_offline(**kwargs: Any):
    """Resolve GPT-2 tokenizer files from offline caches only."""

    return _instantiate_tokenizer("gpt2-offline", **kwargs)


@tokenizers.register(
    "tinyllama-offline",
    backend="codex_ml.registry.tokenizers",
    target="tinyllama-offline",
    offline_default=True,
)
def _tokenizer_tinyllama_offline(**kwargs: Any):
    """Resolve TinyLLaMA tokenizer assets without network access."""

    return _instantiate_tokenizer("tinyllama-offline", **kwargs)


@models.register("minilm", backend="codex_ml.models.registry", target="MiniLM")
def _model_minilm(cfg: Any = None, **kwargs: Any):
    """Expose the MiniLM reference model through the plugin catalogue."""

    return _instantiate_model("MiniLM", cfg, **kwargs)


@models.register(
    "decoder_only",
    backend="codex_ml.models.registry",
    target="decoder_only",
)
def _model_decoder_only(cfg: Any = None, **kwargs: Any):
    """Expose the decoder-only transformer baseline."""

    return _instantiate_model("decoder_only", cfg, **kwargs)


@models.register(
    "gpt2-offline",
    backend="codex_ml.models.registry",
    target="gpt2-offline",
    offline_default=True,
)
def _model_gpt2_offline(cfg: Any = None, **kwargs: Any):
    """Instantiate the offline GPT-2 checkpoint when weights are present locally."""

    return _instantiate_model("gpt2-offline", cfg, **kwargs)


@models.register(
    "tinyllama-offline",
    backend="codex_ml.models.registry",
    target="tinyllama-offline",
    offline_default=True,
)
def _model_tinyllama_offline(cfg: Any = None, **kwargs: Any):
    """Instantiate the offline TinyLLaMA checkpoint when weights are present locally."""

    return _instantiate_model("tinyllama-offline", cfg, **kwargs)


@datasets.register("lines", backend="codex_ml.data.registry", target="lines")
def _dataset_lines(**kwargs: Any):
    """Load a plain-text dataset with deterministic shuffling support."""

    return _instantiate_dataset("lines", **kwargs)


@datasets.register(
    "offline:tiny-corpus",
    backend="codex_ml.data.registry",
    target="offline:tiny-corpus",
    offline_default=True,
)
def _dataset_tiny_corpus(**kwargs: Any):
    """Load the bundled tiny corpus fixture exclusively from local paths."""

    return _instantiate_dataset("offline:tiny-corpus", **kwargs)


@metrics.register("accuracy@token", backend="codex_ml.metrics.registry")
def _metric_token_accuracy(**kwargs: Any):  # noqa: D401 - simple proxy
    return _instantiate_metric("accuracy@token", **kwargs)


@metrics.register("ppl", backend="codex_ml.metrics.registry")
def _metric_perplexity(**kwargs: Any):  # noqa: D401 - simple proxy
    return _instantiate_metric("ppl", **kwargs)


@metrics.register("exact_match", backend="codex_ml.metrics.registry")
def _metric_exact_match(**kwargs: Any):  # noqa: D401 - simple proxy
    return _instantiate_metric("exact_match", **kwargs)


@metrics.register("f1", backend="codex_ml.metrics.registry")
def _metric_f1(**kwargs: Any):  # noqa: D401 - simple proxy
    return _instantiate_metric("f1", **kwargs)


@metrics.register("dist-1", backend="codex_ml.metrics.registry")
def _metric_dist_1(**kwargs: Any):  # noqa: D401 - simple proxy
    return _instantiate_metric("dist-1", **kwargs)


@metrics.register("dist-2", backend="codex_ml.metrics.registry")
def _metric_dist_2(**kwargs: Any):  # noqa: D401 - simple proxy
    return _instantiate_metric("dist-2", **kwargs)


@metrics.register(
    "offline:weighted-accuracy",
    backend="codex_ml.metrics.registry",
    target="offline:weighted-accuracy",
    offline_default=True,
)
def _metric_weighted_accuracy(**kwargs: Any):
    """Expose the weighted accuracy metric with offline JSON fixtures."""

    return _instantiate_metric("offline:weighted-accuracy", **kwargs)


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
