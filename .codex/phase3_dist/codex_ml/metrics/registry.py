"""Lightweight metric registry with deterministic implementations.

Metrics are registered via the @register_metric decorator and looked up
with get_metric. Each metric callable follows the convention:

    metric(preds, targets, **kwargs) -> float | dict | None

where preds and targets are sequences (strings or integers). Metrics
must be deterministic and side-effect free.
"""

from __future__ import annotations

import importlib
import json
import logging
import math
import os
import re
import threading
from collections import Counter
from collections.abc import Callable, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from codex_ml.registry.base import Registry, RegistryConflictError

logger = logging.getLogger(__name__)

metric_registry = Registry("metric")
# Plain dict checked before metric_registry — allows test mocking via monkeypatch.setitem
_METRIC_REGISTRY: dict[str, Callable[..., object]] = {}
_METRIC_PLUGINS_LOADED = False
_METRIC_PLUGINS_LOCK = threading.Lock()
_PLUGIN_CONFLICT_LOGGED: set[str] = set()


def _error_log_path() -> Path:
    base_dir = Path(os.environ.get("CODEX_ERROR_REPORTS_DIR", "_codex_reports"))
    date_str = datetime.now(timezone.utc).date().isoformat()
    return base_dir / f"errors_{date_str}.md"


def append_error_entry(step_name: str, message: str, context: str, question: str) -> None:
    """Append a structured error entry to the daily error report."""

    timestamp = datetime.now(timezone.utc).isoformat()
    block = (
        f"### {step_name}\n"
        f"- Timestamp: {timestamp}\n"
        f"- Message: {message}\n"
        f"- Context: {context}\n"
        f"- Clarification: {question}\n\n"
    )
    try:
        log_path = _error_log_path()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(block)
    except (IOError, OSError):
        logger.warning("Exception occurred", exc_info=True)
        # Error reporting should never raise further exceptions.


def _repo_root() -> Path:
    """Find the repository root by looking for pyproject.toml."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").is_file():
            return parent
    # Fallback
    fallback_index = min(3, len(current.parents) - 1)
    return current.parents[fallback_index]


def _policy_config_path() -> Path:
    """Return path to metrics plugin policy config file."""
    return _repo_root() / "configs" / "metrics_plugin_policy.toml"


def _load_policy_from_file() -> Optional[str]:
    """Load policy from config file if it exists."""
    path = _policy_config_path()
    if not path.is_file():
        return None
    try:
        raw = path.read_text(encoding="utf-8")
    except (IOError, OSError):
        logger.warning("Exception occurred", exc_info=True)
        return None
    # Minimal TOML parse: look for 'policy = "<value>"'
    for line in raw.splitlines():
        line = line.strip()
        if line.lower().startswith("policy"):
            parts = line.split("=", 1)
            if len(parts) == 2:
                return parts[1].strip().strip("\"'")
    return None


def _get_plugin_policy() -> str:
    """Get the active plugin conflict resolution policy.

    Sources (in order of precedence):
    1. CODEX_METRIC_PLUGIN_POLICY environment variable
    2. configs/metrics_plugin_policy.toml file
    3. Default: prefer_local

    Valid policies: prefer_local, prefer_plugin, alias_plugin, shadow_warn, error
    """
    env_val = os.getenv("CODEX_METRIC_PLUGIN_POLICY", "").strip().lower()
    if not env_val:
        file_val = _load_policy_from_file()
        env_val = (file_val or "").strip().lower()

    valid = {"prefer_local", "prefer_plugin", "alias_plugin", "shadow_warn", "error"}
    return env_val if env_val in valid else "prefer_local"


def _resolve_plugin_conflict(name: str, fn: Callable[..., object]) -> None:
    """Resolve a plugin metric conflict according to the active policy.

    Parameters
    ----------
    name:
        The metric name that has a conflict.
    fn:
        The plugin-provided callable.
    """
    policy = _get_plugin_policy()

    # Check if we've already logged this conflict to avoid spam
    should_log = name not in _PLUGIN_CONFLICT_LOGGED
    if should_log:
        _PLUGIN_CONFLICT_LOGGED.add(name)

    if policy == "prefer_plugin":
        # Override existing with plugin
        metric_registry.register(name, fn, override=True, source="entry_point")
        if should_log:
            append_error_entry(
                "metric-plugin.conflict-resolution",
                f"Plugin metric '{name}' overrode existing local implementation.",
                f"name={name}; policy={policy}; retained=plugin",
                "Override applied per policy.",
            )
    elif policy == "alias_plugin":
        # Keep both: local under original name, plugin under alias
        alias_name = f"plugin:{name}"
        metric_registry.register(alias_name, fn, override=True, source="entry_point")
        if should_log:
            append_error_entry(
                "metric-plugin.conflict-resolution",
                f"Plugin metric '{name}' registered as alias '{alias_name}'.",
                f"name={name}; policy={policy}; retained=local+alias",
                "Both implementations retained under separate names.",
            )
    elif policy == "shadow_warn":
        # Keep local, just log the shadow
        if should_log:
            append_error_entry(
                "metric-plugin.conflict-resolution",
                f"Plugin metric '{name}' ignored (local retained).",
                f"name={name}; policy={policy}; retained=local",
                "Shadow recorded; no override performed.",
            )
    elif policy == "error":
        # Re-raise original conflict (strict legacy mode)
        raise RegistryConflictError(
            f"Duplicate registration for 'metric' '{name}'. "
            f"Existing source: local, new source: entry_point."
        )
    else:  # prefer_local (default)
        # Keep local, suppress plugin
        if should_log:
            append_error_entry(
                "metric-plugin.conflict-resolution",
                f"Plugin metric '{name}' suppressed (local retained).",
                f"name={name}; policy={policy}; retained=local",
                "No override per default policy.",
            )


def _register_metric_from_plugin(
    name: str,
    fn: Callable[..., object] | None = None,
    *,
    override: bool = False,
) -> Callable[..., object]:
    """Register a plugin-provided metric marking the source as entry point.

    Applies conflict resolution policy when duplicate registration detected.
    """
    try:
        return metric_registry.register(
            name,
            fn,
            override=override,
            source="entry_point",
        )
    except RegistryConflictError as e:
        type(e).__name__
        logger.warning("RegistryConflictError: <ERROR_TYPE>", exc_info=True)
        if fn is None:
            append_error_entry(
                "metric-plugin.register",
                f"Conflict without callable for '{name}'",
                f"name={name}",
                "Plugin provided no callable; cannot resolve conflict.",
            )
            raise
        # Apply policy-based conflict resolution
        _resolve_plugin_conflict(name, fn)
        # Return the metric (may be original or overridden depending on policy)
        return metric_registry.get(name)
    except Exception as exc:  # pragma: no cover - defensive logging
        append_error_entry(
            "metric-plugin.register",
            str(exc),
            f"name={name}",
            "Can the plugin metric be validated or renamed?",
        )
        raise


def init_metric_plugins(*, force: bool = False) -> int:
    """Best-effort discovery of external metrics via entry points (idempotent).

    Uses a lock to ensure thread-safe initialization and sets the loaded flag
    early to prevent recursive discovery during plugin loading.
    """
    global _METRIC_PLUGINS_LOADED

    with _METRIC_PLUGINS_LOCK:
        if force:
            _METRIC_PLUGINS_LOADED = False

        if _METRIC_PLUGINS_LOADED:
            return 0

        # Set early to prevent recursive reload triggering duplicates
        _METRIC_PLUGINS_LOADED = True

    try:
        from codex_ml.plugins import load_plugins
    except (ImportError, AttributeError):
        logger.warning("Exception occurred", exc_info=True)
        return 0

    return load_plugins("codex_ml.metrics", register=_register_metric_from_plugin)


def _ensure_metric_plugins_loaded() -> None:
    if _METRIC_PLUGINS_LOADED:
        return

    init_metric_plugins()


def register(
    name: str,
    fn: Callable[..., object] | None = None,
    *,
    override: bool = False,
) -> Callable[[Callable[..., object]], Callable[..., object]] | Callable[..., object]:
    """Register ``fn`` under ``name`` in the metric registry."""

    def decorator(target: Callable[..., object]) -> Callable[..., object]:
        try:
            metric_registry.register(name, target, override=override)
        except RegistryConflictError as exc:
            append_error_entry(
                "metric.register",
                str(exc),
                f"name={name}",
                "Should this metric override the existing registration using override=True?",
            )
            raise
        except Exception as exc:  # pragma: no cover - defensive logging
            append_error_entry(
                "metric.register",
                str(exc),
                f"name={name}",
                "Is the metric implementation valid or does it need different parameters?",
            )
            raise
        return target

    if fn is not None:
        return decorator(fn)
    return decorator


def register_metric(
    name: str,
    fn: Callable[..., object] | None = None,
    *,
    override: bool = False,
) -> Callable[[Callable[..., object]], Callable[..., object]] | Callable[..., object]:
    """Backward-compatible wrapper around :func:`register`."""

    return register(name, fn, override=override)


def _register_builtin_metrics() -> None:
    """Register built-in generative metrics after register_metric is defined."""
    importlib.import_module("codex_ml.metrics.generative")


_register_builtin_metrics()


def get(name: str) -> Callable[..., object]:
    """Return the metric callable registered under name.

    ``_METRIC_REGISTRY`` is checked first so that test code can inject
    mock implementations via ``monkeypatch.setitem`` without touching the
    real registry.
    """
    if name in _METRIC_REGISTRY:
        return _METRIC_REGISTRY[name]
    _ensure_metric_plugins_loaded()
    return metric_registry.get(name)


def get_metric(name: str) -> Callable[..., object]:
    """Backward-compatible wrapper around :func:`get`."""

    return get(name)


def list_metrics() -> list[str]:
    _ensure_metric_plugins_loaded()
    return metric_registry.list()


def alias_metric(alias: str, target: str, *, override: bool = True) -> None:
    """Create an alias for an existing metric.

    Parameters
    ----------
    alias:
        The new alias name to register.
    target:
        The existing metric name to alias.
    override:
        Allow replacing an existing registration. Defaults to True.

    Notes
    -----
    This creates a thin wrapper that defers lookup to the target metric
    at call time, ensuring both names always resolve to the same implementation.
    """

    def _alias_wrapper(*args, **kwargs) -> None:
        fn = metric_registry.get(target)
        return fn(*args, **kwargs)

    metric_registry.register(alias, _alias_wrapper, override=override)


def _resolve_metric_resource(
    name: str,
    path: str | os.PathLike[str] | None,
    *,
    filename: str,
    specific_env: str | None = None,
) -> Path:
    candidates = []
    if path:
        provided = Path(path).expanduser()
        target = provided / filename if provided.is_dir() else provided
        if target.exists():
            return target
        raise FileNotFoundError(
            f"Offline metric resource '{name}' expected at {target}. Provide an existing file or directory."  # noqa: E501
        )

    if specific_env:
        env_value = os.environ.get(specific_env)
        if env_value:
            env_path = Path(env_value).expanduser()
            if env_path.is_dir():
                env_path = env_path / filename
            candidates.append(env_path)

    offline_root = os.environ.get("CODEX_ML_OFFLINE_METRICS_DIR")
    if offline_root:
        offline_path = Path(offline_root).expanduser()
        candidates.append(offline_path / filename if offline_path.is_dir() else offline_path)

    repo_root = _repo_root()
    candidates.append(repo_root / "data" / "offline" / filename)
    candidates.append(repo_root / "artifacts" / "metrics" / filename)

    checked: list[str] = []
    for candidate in candidates:
        resolved = candidate.expanduser()
        checked.append(str(resolved))
        if resolved.exists():
            return resolved

    checked_msg = ", ".join(checked) if checked else "<no candidates>"
    raise FileNotFoundError(
        f"Offline metric resource '{name}' not found. Checked: {checked_msg}. Provide `weights_path` or "  # noqa: E501
        f"set CODEX_ML_OFFLINE_METRICS_DIR / {specific_env or 'CODEX_ML_WEIGHTED_ACCURACY_PATH'} to point to the file."  # noqa: E501
    )


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------


def _norm_str(
    s: str,
    *,
    lowercase: bool = True,
    strip: bool = True,
    remove_punct: bool = False,
) -> str:
    s = str(s)
    if lowercase:
        s = s.lower()
    if strip:
        s = s.strip()
    if remove_punct:
        s = re.sub(r"[\W_]+", " ", s)
    return " ".join(s.split())


# ---------------------------------------------------------------------------
# Built-in metrics
# ---------------------------------------------------------------------------


@register_metric("accuracy@token")
def token_accuracy(
    preds: Sequence[int], targets: Sequence[int], *, ignore_index: int = -100
) -> float:
    """Token-level accuracy with optional ignore_index."""
    correct = 0
    total = 0
    for p, t in zip(preds, targets, strict=False):
        ti = int(t)
        if ti == ignore_index:
            continue
        total += 1
        correct += int(p) == ti
    return float(correct / total) if total else 0.0


# Provide a shorter alias for minimal metric registries/tests.
register_metric("token_accuracy")(token_accuracy)  # type: ignore[arg-type]


@register_metric("ppl")
def perplexity(nll_or_sum, n_tokens: Optional[int] = None) -> float:
    """Perplexity from negative log-likelihood.

    Backward compatible signatures:
    - perplexity([nll_i...]) -> exp(mean(nll))
    - perplexity(nll_sum, n_tokens) -> exp(nll_sum / n_tokens)
    """
    # Variant A: list/sequence of NLL
    if n_tokens is None:
        seq = list(nll_or_sum)
        if not seq:
            return float("inf")
        avg = sum(float(x) for x in seq) / len(seq)
        try:
            return float(math.exp(avg))
        except OverflowError:  # pragma: no cover
            return float("inf")
    # Variant B: sum and count
    total = float(nll_or_sum)
    count = int(n_tokens or 0)
    if count <= 0:
        return float("inf")
    try:
        return float(math.exp(total / count))
    except OverflowError:  # pragma: no cover
        return float("inf")


@register_metric("exact_match")
def exact_match(
    preds: Sequence[str], targets: Sequence[str], *, remove_punct: bool = False
) -> float:
    """Deterministic, whitespace-insensitive exact match."""
    matches = 0
    for p, t in zip(preds, targets, strict=False):
        if _norm_str(p, remove_punct=remove_punct) == _norm_str(t, remove_punct=remove_punct):
            matches += 1
    return float(matches / max(1, len(preds)))


@register_metric("f1")
def f1(preds: Sequence[str], targets: Sequence[str]) -> float:
    """Average per-example F1 over whitespace tokens (bag-of-words)."""
    scores = []
    for p, t in zip(preds, targets, strict=False):
        p_tok = _norm_str(p).split()
        t_tok = _norm_str(t).split()
        if not p_tok and not t_tok:
            scores.append(1.0)
            continue
        common = Counter(p_tok) & Counter(t_tok)
        tp = sum(common.values())
        precision = tp / len(p_tok) if p_tok else 0.0
        recall = tp / len(t_tok) if t_tok else 0.0
        scores.append(
            2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        )
    return float(sum(scores) / len(scores)) if scores else 0.0


def _distinct_ngrams(preds: Sequence[str], n: int) -> float:
    toks = [tok for p in preds for tok in _norm_str(p, remove_punct=True).split()]
    ngrams = (
        toks if n <= 1 else [" ".join(toks[i : i + n]) for i in range(max(0, len(toks) - n + 1))]
    )
    total = len(ngrams)
    return float(len(set(ngrams)) / total) if total else 0.0


@register_metric("dist-1")
def dist_1(preds: Sequence[str], targets: Sequence[str] | None = None) -> float:
    return _distinct_ngrams(preds, 1)


@register_metric("dist-2")
def dist_2(preds: Sequence[str], targets: Sequence[str] | None = None) -> float:
    return _distinct_ngrams(preds, 2)


@register_metric("bleu")
def bleu(preds: Sequence[str], targets: Sequence[str]) -> Optional[float]:
    """Corpus BLEU via NLTK if available; returns None otherwise."""
    try:  # pragma: no cover - optional dependency
        from nltk.translate.bleu_score import SmoothingFunction, corpus_bleu
    except (ImportError, AttributeError):  # pragma: no cover
        return None
    cand = [_norm_str(p, remove_punct=True).split() for p in preds]
    ref = [[_norm_str(t, remove_punct=True).split()] for t in targets]
    if not cand:
        return None
    smoothie = SmoothingFunction().method3
    try:
        return float(corpus_bleu(ref, cand, smoothing_function=smoothie))
    except Exception:  # pragma: no cover - numerical issue
        return None


@register_metric("rougeL")
def rouge_l(preds: Sequence[str], targets: Sequence[str]) -> Optional[float]:
    """ROUGE-L F-measure via rouge_score; returns None if unavailable."""
    try:  # pragma: no cover - optional dependency
        from rouge_score import rouge_scorer
    except (ImportError, AttributeError):  # pragma: no cover
        return None
    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    scores = [
        scorer.score(_norm_str(t, remove_punct=False), _norm_str(p, remove_punct=False))[
            "rougeL"
        ].fmeasure
        for p, t in zip(preds, targets, strict=False)
    ]
    return float(sum(scores) / len(scores)) if scores else None


@register_metric("offline:weighted-accuracy")
def weighted_accuracy(
    preds: Sequence[str | int],
    targets: Sequence[str | int],
    *,
    weights_path: str | os.PathLike[str] | None = None,
) -> float:
    """Weighted accuracy that loads class weights from a local JSON fixture."""

    weights_file = _resolve_metric_resource(
        "offline:weighted-accuracy",
        weights_path,
        filename="weighted_accuracy.json",
        specific_env="CODEX_ML_WEIGHTED_ACCURACY_PATH",
    )
    try:
        weights = json.loads(weights_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover - malformed fixture
        raise ValueError(f"Invalid weight specification in {weights_file}: {exc}") from exc

    total = 0.0
    correct = 0.0
    for pred, target in zip(preds, targets, strict=False):
        label = str(target)
        weight = float(weights.get(label, 1.0))
        total += weight
        if str(pred) == label:
            correct += weight
    return float(correct / total) if total else 0.0


@register_metric("chrf")
def chrf(preds: Sequence[str], targets: Sequence[str]) -> Optional[float]:
    """chrF metric via sacrebleu (preferred) or NLTK; None on failure."""
    # Try sacrebleu first
    try:  # pragma: no cover - optional dependency
        from sacrebleu.metrics import CHRF

        scorer = CHRF()
        return float(scorer.corpus_score(preds, [targets]).score)
    except (ImportError, AttributeError) as e:
        type(e).__name__
        logger.warning("Exception: <ERROR_TYPE>", exc_info=True)
    # Fallback to nltk
    try:  # pragma: no cover - optional dependency
        from nltk.translate.chrf_score import corpus_chrf

        return float(corpus_chrf(targets, preds))
    except (ImportError, AttributeError):  # pragma: no cover
        return None


__all__ = [
    "_METRIC_REGISTRY",
    "alias_metric",
    "append_error_entry",
    "get",
    "get_metric",
    "init_metric_plugins",
    "list_metrics",
    "metric_registry",
    "register",
    "register_metric",
]
