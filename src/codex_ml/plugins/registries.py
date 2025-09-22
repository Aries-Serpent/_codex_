"""Concrete plugin registries used by codex_ml."""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
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


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _resolve_offline_model_path(
    alias: str,
    cfg: Mapping[str, Any],
    *,
    default_remote: str,
    default_subdir: str,
    specific_env: str | None = None,
) -> str:
    local_only = bool(cfg.get("local_files_only", True))

    for key in (
        "local_path",
        "path",
        "model_path",
        "pretrained_model_name_or_path",
        "model_id",
    ):
        value = cfg.get(key)
        if value:
            candidate = Path(str(value)).expanduser()
            if candidate.exists():
                return str(candidate)
            if not local_only:
                return str(value)
            raise FileNotFoundError(
                "Checkpoint for '{alias}' expected at {candidate}. Provide a valid path or set "
                "`local_files_only=false` to allow fetching '{remote}'.".format(
                    alias=alias, candidate=candidate, remote=default_remote
                )
            )

    checked: list[str] = []

    if specific_env:
        env_value = os.environ.get(specific_env)
        if env_value:
            env_path = Path(env_value).expanduser()
            checked.append(f"${specific_env} -> {env_path}")
            if env_path.exists():
                return str(env_path)
            if not local_only:
                return str(env_path)
            raise FileNotFoundError(
                f"Environment variable {specific_env} points to {env_path}, but no checkpoint was found."
            )

    offline_root = os.environ.get("CODEX_ML_OFFLINE_MODELS_DIR")
    if offline_root:
        offline_path = Path(offline_root).expanduser()
        candidate = offline_path / default_subdir if offline_path.is_dir() else offline_path
        checked.append(str(candidate))
        if candidate.exists():
            return str(candidate)

    repo_candidate = _repo_root() / "artifacts" / "models" / default_subdir
    checked.append(str(repo_candidate))
    if repo_candidate.exists():
        return str(repo_candidate)

    if local_only:
        details = ", ".join(checked) if checked else "<no candidates>"
        raise FileNotFoundError(
            "Local checkpoint for '{alias}' not found. Checked: {details}. Provide `model.local_path` or "
            "set CODEX_ML_OFFLINE_MODELS_DIR to point at the weights, or disable offline mode with "
            "`local_files_only=false` to fallback to '{remote}'.".format(
                alias=alias, details=details, remote=default_remote
            )
        )

    return default_remote


def _resolve_offline_tokenizer_path(
    alias: str,
    kwargs: Mapping[str, Any],
    *,
    default_subdir: str,
    specific_env: str | None = None,
) -> str:
    explicit = kwargs.get("name_or_path")
    if explicit:
        candidate = Path(str(explicit)).expanduser()
        if candidate.exists():
            return str(candidate)
        raise FileNotFoundError(
            f"Tokenizer assets for '{alias}' expected at {candidate}. Provide a valid path or set "
            "CODEX_ML_OFFLINE_TOKENIZERS_DIR / CODEX_ML_OFFLINE_MODELS_DIR."
        )

    checked: list[str] = []

    if specific_env:
        env_value = os.environ.get(specific_env)
        if env_value:
            env_path = Path(env_value).expanduser()
            checked.append(f"${specific_env} -> {env_path}")
            if env_path.exists():
                return str(env_path)
            raise FileNotFoundError(
                f"Environment variable {specific_env} points to {env_path}, but tokenizer files were not found."
            )

    offline_root = os.environ.get("CODEX_ML_OFFLINE_TOKENIZERS_DIR") or os.environ.get(
        "CODEX_ML_OFFLINE_MODELS_DIR"
    )
    if offline_root:
        offline_path = Path(offline_root).expanduser()
        candidate = offline_path / default_subdir if offline_path.is_dir() else offline_path
        checked.append(str(candidate))
        if candidate.exists():
            return str(candidate)

    repo_candidate = _repo_root() / "artifacts" / "models" / default_subdir
    checked.append(str(repo_candidate))
    if repo_candidate.exists():
        return str(repo_candidate)

    details = ", ".join(checked) if checked else "<no candidates>"
    raise FileNotFoundError(
        f"Tokenizer assets for '{alias}' not found. Checked: {details}. Provide `name_or_path` or "
        "configure CODEX_ML_OFFLINE_TOKENIZERS_DIR / CODEX_ML_OFFLINE_MODELS_DIR."
    )


def _resolve_offline_dataset_path(
    alias: str,
    path: str | os.PathLike[str] | None,
    *,
    filename: str,
    specific_env: str | None = None,
) -> str:
    if path:
        provided = Path(path).expanduser()
        target = provided / filename if provided.is_dir() else provided
        if target.exists():
            return str(target)
        raise FileNotFoundError(
            f"Dataset fixture '{alias}' expected at {target}. Provide an existing file or directory."
        )

    checked: list[str] = []

    if specific_env:
        env_value = os.environ.get(specific_env)
        if env_value:
            env_path = Path(env_value).expanduser()
            candidate = env_path / filename if env_path.is_dir() else env_path
            checked.append(str(candidate))
            if candidate.exists():
                return str(candidate)

    offline_root = os.environ.get("CODEX_ML_OFFLINE_DATASETS_DIR")
    if offline_root:
        root_path = Path(offline_root).expanduser()
        candidate = root_path / filename if root_path.is_dir() else root_path
        checked.append(str(candidate))
        if candidate.exists():
            return str(candidate)

    repo_candidate = _repo_root() / "data" / "offline" / filename
    checked.append(str(repo_candidate))
    if repo_candidate.exists():
        return str(repo_candidate)

    details = ", ".join(checked) if checked else "<no candidates>"
    raise FileNotFoundError(
        f"Dataset fixture '{alias}' not found. Checked: {details}. Provide `path` or set "
        "CODEX_ML_TINY_CORPUS_PATH / CODEX_ML_OFFLINE_DATASETS_DIR."
    )


def _resolve_offline_metric_path(
    alias: str,
    path: str | os.PathLike[str] | None,
    *,
    filename: str,
    specific_env: str | None = None,
) -> str:
    if path:
        provided = Path(path).expanduser()
        target = provided / filename if provided.is_dir() else provided
        if target.exists():
            return str(target)
        raise FileNotFoundError(
            f"Offline metric resource '{alias}' expected at {target}. Provide an existing file or directory."
        )

    checked: list[str] = []

    if specific_env:
        env_value = os.environ.get(specific_env)
        if env_value:
            env_path = Path(env_value).expanduser()
            candidate = env_path / filename if env_path.is_dir() else env_path
            checked.append(str(candidate))
            if candidate.exists():
                return str(candidate)

    offline_root = os.environ.get("CODEX_ML_OFFLINE_METRICS_DIR")
    if offline_root:
        root_path = Path(offline_root).expanduser()
        candidate = root_path / filename if root_path.is_dir() else root_path
        checked.append(str(candidate))
        if candidate.exists():
            return str(candidate)

    repo_candidate = _repo_root() / "data" / "offline" / filename
    checked.append(str(repo_candidate))
    if repo_candidate.exists():
        return str(repo_candidate)

    details = ", ".join(checked) if checked else "<no candidates>"
    raise FileNotFoundError(
        f"Offline metric resource '{alias}' not found. Checked: {details}. Provide `weights_path` or set "
        "CODEX_ML_WEIGHTED_ACCURACY_PATH / CODEX_ML_OFFLINE_METRICS_DIR."
    )


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

    resolved = _resolve_offline_tokenizer_path(
        "gpt2-offline",
        kwargs,
        default_subdir="gpt2",
        specific_env="CODEX_ML_GPT2_TOKENIZER_PATH",
    )
    local_kwargs = dict(kwargs)
    local_kwargs["name_or_path"] = resolved
    return _instantiate_tokenizer("gpt2-offline", **local_kwargs)


@tokenizers.register(
    "tinyllama-offline",
    backend="codex_ml.registry.tokenizers",
    target="tinyllama-offline",
    offline_default=True,
)
def _tokenizer_tinyllama_offline(**kwargs: Any):
    """Resolve TinyLLaMA tokenizer assets without network access."""

    resolved = _resolve_offline_tokenizer_path(
        "tinyllama-offline",
        kwargs,
        default_subdir="tinyllama",
        specific_env="CODEX_ML_TINYLLAMA_TOKENIZER_PATH",
    )
    local_kwargs = dict(kwargs)
    local_kwargs["name_or_path"] = resolved
    return _instantiate_tokenizer("tinyllama-offline", **local_kwargs)


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

    config = _merge_model_cfg(cfg, **kwargs)
    resolved = _resolve_offline_model_path(
        "gpt2-offline",
        config,
        default_remote="gpt2",
        default_subdir="gpt2",
        specific_env="CODEX_ML_GPT2_PATH",
    )
    config.setdefault("local_files_only", True)
    if Path(resolved).expanduser().exists():
        config.setdefault("local_path", resolved)
    config["pretrained_model_name_or_path"] = resolved
    return _instantiate_model("gpt2-offline", config)


@models.register(
    "tinyllama-offline",
    backend="codex_ml.models.registry",
    target="tinyllama-offline",
    offline_default=True,
)
def _model_tinyllama_offline(cfg: Any = None, **kwargs: Any):
    """Instantiate the offline TinyLLaMA checkpoint when weights are present locally."""

    config = _merge_model_cfg(cfg, **kwargs)
    resolved = _resolve_offline_model_path(
        "tinyllama-offline",
        config,
        default_remote="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        default_subdir="tinyllama",
        specific_env="CODEX_ML_TINYLLAMA_PATH",
    )
    config.setdefault("local_files_only", True)
    if Path(resolved).expanduser().exists():
        config.setdefault("local_path", resolved)
    config["pretrained_model_name_or_path"] = resolved
    return _instantiate_model("tinyllama-offline", config)


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

    resolved = _resolve_offline_dataset_path(
        "offline:tiny-corpus",
        kwargs.get("path"),
        filename="tiny_corpus.txt",
        specific_env="CODEX_ML_TINY_CORPUS_PATH",
    )
    local_kwargs = dict(kwargs)
    local_kwargs["path"] = resolved
    return _instantiate_dataset("offline:tiny-corpus", **local_kwargs)


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

    resolved = _resolve_offline_metric_path(
        "offline:weighted-accuracy",
        kwargs.get("weights_path"),
        filename="weighted_accuracy.json",
        specific_env="CODEX_ML_WEIGHTED_ACCURACY_PATH",
    )
    local_kwargs = dict(kwargs)
    local_kwargs["weights_path"] = resolved
    return _instantiate_metric("offline:weighted-accuracy", **local_kwargs)


@trainers.register(
    "offline:functional",
    backend="codex_ml.registry.trainers",
    target="functional",
    offline_default=True,
)
def _trainer_functional(**kwargs: Any):
    """Expose the functional trainer with optional bound keyword arguments."""

    from codex_ml.registry.trainers import get_trainer

    trainer = get_trainer("functional")
    if not callable(trainer):
        raise TypeError("Trainer 'functional' did not resolve to a callable")

    if not kwargs:
        return trainer

    def _bound_trainer(*args: Any, **call_kwargs: Any) -> Any:
        merged = dict(kwargs)
        merged.update(call_kwargs)
        return trainer(*args, **merged)

    return _bound_trainer


@reward_models.register(
    "offline:heuristic",
    backend="codex_ml.interfaces.reward_model",
    target="HeuristicRewardModel",
    offline_default=True,
)
def _reward_model_heuristic(**kwargs: Any):
    """Return the deterministic heuristic reward model for offline usage."""

    from codex_ml.interfaces.reward_model import HeuristicRewardModel

    return HeuristicRewardModel(**kwargs)


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
