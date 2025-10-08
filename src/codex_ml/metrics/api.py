"""Stable metrics import surface.

Prefer importing from here in user code and docs:
    from codex_ml.metrics.api import accuracy, micro_f1, macro_f1, perplexity, token_accuracy, bleu, rouge_l

This module re-exports from the actual implementation locations, with
best-effort fallbacks to keep imports stable as the tree evolves.
"""

from __future__ import annotations

from typing import Any, Callable


def _pick(*candidates: str) -> Callable[..., Any]:
    last_err: Exception | None = None
    for path in candidates:
        try:
            module_path, name = path.rsplit(".", 1)
            mod = __import__(module_path, fromlist=[name])
            return getattr(mod, name)
        except Exception as e:  # pragma: no cover - best-effort fallback
            last_err = e
            continue
    raise ImportError(
        f"None of the metric providers are available for {candidates!r}"
    ) from last_err


# Common metrics used across evaluation/training.
accuracy = _pick("codex_ml.metrics.text.accuracy", "codex_ml.eval.metrics.accuracy")
micro_f1 = _pick("codex_ml.metrics.text.micro_f1", "codex_ml.eval.metrics.micro_f1")
macro_f1 = _pick("codex_ml.metrics.text.macro_f1", "codex_ml.eval.metrics.macro_f1")
bleu = _pick("codex_ml.metrics.text.bleu", "codex_ml.eval.metrics.bleu")
rouge_l = _pick("codex_ml.metrics.text.rouge_l", "codex_ml.eval.metrics.rouge_l")
perplexity = _pick("codex_ml.metrics.sequence.perplexity", "codex_ml.eval.metrics.perplexity")
token_accuracy = _pick(
    "codex_ml.metrics.sequence.token_accuracy", "codex_ml.eval.metrics.token_accuracy"
)

__all__ = [
    "accuracy",
    "micro_f1",
    "macro_f1",
    "bleu",
    "rouge_l",
    "perplexity",
    "token_accuracy",
]
