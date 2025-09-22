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


# Shared helpers ------------------------------------------------------------


def _repo_root() -> Path:
    """Return the repository root (workspace of the checkout)."""

    return Path(__file__).resolve().parents[3]


def _require_path(
    alias: str,
    candidate: Path,
    *,
    kind: str,
    expect_dir: bool,
    required_files: tuple[str, ...] | None = None,
) -> Path:
    """Ensure ``candidate`` exists and optionally contains ``required_files``."""

    resolved = candidate.expanduser()
    if expect_dir:
        if not resolved.exists() or not resolved.is_dir():
            raise FileNotFoundError(
                f"Local {kind} for '{alias}' expected at {resolved}. "
                "Provide an existing directory or update the registry configuration."
            )
        if required_files:
            missing = [name for name in required_files if not (resolved / name).exists()]
            if missing:
                raise FileNotFoundError(
                    f"Local {kind} for '{alias}' missing required files {missing} under {resolved}."
                )
        return resolved
    if not resolved.exists():
        raise FileNotFoundError(
            f"Local {kind} for '{alias}' expected at {resolved}. Provide an existing file or update the registry configuration."
        )
    return resolved


def _guard_model_resources(
    alias: str,
    cfg: Mapping[str, Any],
    *,
    default_subdir: str,
    specific_env: str | None = None,
) -> Path:
    """Validate that offline checkpoints for ``alias`` exist locally."""

    for key in (
        "local_path",
        "path",
        "model_path",
        "pretrained_model_name_or_path",
        "model_id",
    ):
        value = cfg.get(key)
        if value:
            candidate = Path(str(value))
            return _require_path(alias, candidate, kind="model weights", expect_dir=True)

    checked: list[str] = []
    if specific_env:
        env_value = os.environ.get(specific_env)
        if env_value:
            candidate = Path(env_value)
            try:
                return _require_path(alias, candidate, kind="model weights", expect_dir=True)
            except FileNotFoundError:
                checked.append(str(candidate.expanduser()))

    offline_root = os.environ.get("CODEX_ML_OFFLINE_MODELS_DIR")
    if offline_root:
        candidate = Path(offline_root) / default_subdir
        try:
            return _require_path(alias, candidate, kind="model weights", expect_dir=True)
        except FileNotFoundError:
            checked.append(str(candidate.expanduser()))

    repo_candidate = _repo_root() / "artifacts" / "models" / default_subdir
    try:
        return _require_path(alias, repo_candidate, kind="model weights", expect_dir=True)
    except FileNotFoundError:
        checked.append(str(repo_candidate))

    details = ", ".join(checked) if checked else "<no candidates>"
    raise FileNotFoundError(
        f"Local model weights for '{alias}' not found. Checked: {details}. Set `local_path`, "
        "CODEX_ML_OFFLINE_MODELS_DIR or the specific environment override to point at the checkpoint."
    )


def _guard_tokenizer_resources(
    alias: str,
    kwargs: Mapping[str, Any],
    *,
    default_subdir: str,
    specific_env: str | None = None,
) -> Path:
    """Ensure offline tokenizer vocabularies exist for ``alias``."""

    value = kwargs.get("name_or_path")
    if value:
        candidate = Path(str(value))
        return _require_path(alias, candidate, kind="tokenizer assets", expect_dir=True)

    checked: list[str] = []
    if specific_env:
        env_value = os.environ.get(specific_env)
        if env_value:
            candidate = Path(env_value)
            try:
                return _require_path(alias, candidate, kind="tokenizer assets", expect_dir=True)
            except FileNotFoundError:
                checked.append(str(candidate.expanduser()))

    offline_root = os.environ.get("CODEX_ML_OFFLINE_MODELS_DIR") or os.environ.get(
        "CODEX_ML_OFFLINE_TOKENIZERS_DIR"
    )
    if offline_root:
        candidate = Path(offline_root) / default_subdir
        try:
            return _require_path(alias, candidate, kind="tokenizer assets", expect_dir=True)
        except FileNotFoundError:
            checked.append(str(candidate.expanduser()))

    repo_candidate = _repo_root() / "artifacts" / "models" / default_subdir
    try:
        return _require_path(alias, repo_candidate, kind="tokenizer assets", expect_dir=True)
    except FileNotFoundError:
        checked.append(str(repo_candidate))

    details = ", ".join(checked) if checked else "<no candidates>"
    raise FileNotFoundError(
        f"Tokenizer assets for '{alias}' not found. Checked: {details}. Provide `name_or_path` or set offline environment variables."
    )


def _guard_dataset_fixture(
    alias: str,
    *,
    filename: str,
    path: str | Path | None = None,
    specific_env: str | None = None,
) -> Path:
    """Ensure offline dataset fixture ``filename`` exists."""

    if path:
        candidate = Path(path)
        target = candidate / filename if candidate.is_dir() else candidate
        return _require_path(alias, target, kind="dataset", expect_dir=False)

    checked: list[str] = []
    if specific_env:
        env_value = os.environ.get(specific_env)
        if env_value:
            env_path = Path(env_value)
            target = env_path / filename if Path(env_path).is_dir() else env_path
            try:
                return _require_path(alias, target, kind="dataset", expect_dir=False)
            except FileNotFoundError:
                checked.append(str(target.expanduser()))

    offline_root = os.environ.get("CODEX_ML_OFFLINE_DATASETS_DIR")
    if offline_root:
        candidate = Path(offline_root) / filename
        try:
            return _require_path(alias, candidate, kind="dataset", expect_dir=False)
        except FileNotFoundError:
            checked.append(str(candidate.expanduser()))

    repo_candidate = _repo_root() / "data" / "offline" / filename
    try:
        return _require_path(alias, repo_candidate, kind="dataset", expect_dir=False)
    except FileNotFoundError:
        checked.append(str(repo_candidate))

    details = ", ".join(checked) if checked else "<no candidates>"
    raise FileNotFoundError(
        f"Dataset fixture for '{alias}' not found. Checked: {details}. Provide `path` or set CODEX_ML_OFFLINE_DATASETS_DIR."
    )


def _guard_metric_fixture(
    alias: str,
    *,
    filename: str,
    path: str | Path | None = None,
    specific_env: str | None = None,
) -> Path:
    """Ensure offline metric resource ``filename`` exists."""

    if path:
        candidate = Path(path)
        target = candidate / filename if candidate.is_dir() else candidate
        return _require_path(alias, target, kind="metric resource", expect_dir=False)

    checked: list[str] = []
    if specific_env:
        env_value = os.environ.get(specific_env)
        if env_value:
            env_path = Path(env_value)
            target = env_path / filename if env_path.is_dir() else env_path
            try:
                return _require_path(alias, target, kind="metric resource", expect_dir=False)
            except FileNotFoundError:
                checked.append(str(target.expanduser()))

    offline_root = os.environ.get("CODEX_ML_OFFLINE_METRICS_DIR")
    if offline_root:
        candidate = Path(offline_root) / filename
        try:
            return _require_path(alias, candidate, kind="metric resource", expect_dir=False)
        except FileNotFoundError:
            checked.append(str(candidate.expanduser()))

    repo_data = _repo_root() / "data" / "offline" / filename
    repo_artifact = _repo_root() / "artifacts" / "metrics" / filename
    for candidate in (repo_data, repo_artifact):
        try:
            return _require_path(alias, candidate, kind="metric resource", expect_dir=False)
        except FileNotFoundError:
            checked.append(str(candidate))

    details = ", ".join(checked) if checked else "<no candidates>"
    raise FileNotFoundError(
        f"Metric resource for '{alias}' not found. Checked: {details}. Provide `weights_path` or set CODEX_ML_OFFLINE_METRICS_DIR."
    )


def _guard_repo_file(alias: str, relative: str, *, description: str) -> Path:
    """Ensure a repository file is present for lightweight shims."""

    candidate = _repo_root() / relative
    return _require_path(alias, candidate, kind=description, expect_dir=False)


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


def _instantiate_trainer(alias: str, **kwargs: Any) -> Any:
    from codex_ml.registry.trainers import get_trainer

    trainer = get_trainer(alias)
    if callable(trainer) and kwargs:
        return trainer(**kwargs)
    return trainer


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

    resolved = _guard_tokenizer_resources(
        "gpt2-offline",
        kwargs,
        default_subdir="gpt2",
        specific_env="CODEX_ML_GPT2_TOKENIZER_PATH",
    )
    local_kwargs = dict(kwargs)
    local_kwargs.setdefault("name_or_path", str(resolved))
    return _instantiate_tokenizer("gpt2-offline", **local_kwargs)


@tokenizers.register(
    "tinyllama-offline",
    backend="codex_ml.registry.tokenizers",
    target="tinyllama-offline",
    offline_default=True,
)
def _tokenizer_tinyllama_offline(**kwargs: Any):
    """Resolve TinyLLaMA tokenizer assets without network access."""

    resolved = _guard_tokenizer_resources(
        "tinyllama-offline",
        kwargs,
        default_subdir="tinyllama",
        specific_env="CODEX_ML_TINYLLAMA_TOKENIZER_PATH",
    )
    local_kwargs = dict(kwargs)
    local_kwargs.setdefault("name_or_path", str(resolved))
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

    merged_cfg = _merge_model_cfg(cfg, **kwargs)
    resolved = _guard_model_resources(
        "gpt2-offline",
        merged_cfg,
        default_subdir="gpt2",
        specific_env="CODEX_ML_GPT2_PATH",
    )
    merged_cfg.setdefault("local_files_only", True)
    merged_cfg.setdefault("local_path", str(resolved))
    return _instantiate_model("gpt2-offline", merged_cfg)


@models.register(
    "tinyllama-offline",
    backend="codex_ml.models.registry",
    target="tinyllama-offline",
    offline_default=True,
)
def _model_tinyllama_offline(cfg: Any = None, **kwargs: Any):
    """Instantiate the offline TinyLLaMA checkpoint when weights are present locally."""

    merged_cfg = _merge_model_cfg(cfg, **kwargs)
    resolved = _guard_model_resources(
        "tinyllama-offline",
        merged_cfg,
        default_subdir="tinyllama",
        specific_env="CODEX_ML_TINYLLAMA_PATH",
    )
    merged_cfg.setdefault("local_files_only", True)
    merged_cfg.setdefault("local_path", str(resolved))
    return _instantiate_model("tinyllama-offline", merged_cfg)


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

    local_kwargs = dict(kwargs)
    resolved = _guard_dataset_fixture(
        "offline:tiny-corpus",
        filename="tiny_corpus.txt",
        path=local_kwargs.get("path"),
        specific_env="CODEX_ML_TINY_CORPUS_PATH",
    )
    local_kwargs.setdefault("path", str(resolved))
    return _instantiate_dataset("offline:tiny-corpus", **local_kwargs)


@trainers.register(
    "functional",
    backend="codex_ml.registry.trainers",
    target="functional",
    offline_default=True,
)
def _trainer_functional(**kwargs: Any):
    """Expose the deterministic functional trainer shim."""

    _guard_repo_file(
        "functional-trainer",
        "training/functional_training.py",
        description="functional trainer shim",
    )
    return _instantiate_trainer("functional", **kwargs)


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

    local_kwargs = dict(kwargs)
    resolved = _guard_metric_fixture(
        "offline:weighted-accuracy",
        filename="weighted_accuracy.json",
        path=local_kwargs.get("weights_path"),
        specific_env="CODEX_ML_WEIGHTED_ACCURACY_PATH",
    )
    local_kwargs.setdefault("weights_path", str(resolved))
    return _instantiate_metric("offline:weighted-accuracy", **local_kwargs)


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
