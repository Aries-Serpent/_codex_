"""Helpers for recording run-level metadata alongside metric logs."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Mapping, MutableMapping, Sequence

from codex_ml.tracking.git_tag import current_commit

CommitLookup = Callable[[], str | None]


def _stringify_path(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (str, Path)):
        text = str(value).strip()
        return text or None
    try:
        return str(value)
    except Exception:
        return None


def _coerce_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except Exception:
        return None


def build_run_metadata(
    *,
    seed: int | None = None,
    deterministic: bool | None = None,
    resume: bool | None = None,
    dataset_format: str | None = None,
    dataset_source: Any | None = None,
    train_examples: Any | None = None,
    eval_examples: Any | None = None,
    missing_optional: Sequence[str] | None = None,
    extras: Mapping[str, Any] | None = None,
    commit_lookup: CommitLookup | None = None,
) -> MutableMapping[str, Any]:
    """Construct a metadata payload suitable for NDJSON or CSV logs."""

    payload: MutableMapping[str, Any] = {"phase": "metadata"}

    lookup = commit_lookup or current_commit
    if lookup is not None:
        try:
            commit = lookup()
        except Exception:
            commit = None
        if commit:
            payload["git_commit"] = commit

    seed_value = _coerce_int(seed)
    if seed_value is not None:
        payload["seed"] = seed_value

    if deterministic is not None:
        payload["deterministic"] = bool(deterministic)

    if resume is not None:
        payload["resume"] = bool(resume)

    if dataset_format:
        payload["dataset_format"] = str(dataset_format)

    source = _stringify_path(dataset_source)
    if source:
        payload["dataset_source"] = source

    train_count = _coerce_int(train_examples)
    if train_count is not None:
        payload["train_examples"] = train_count

    eval_count = _coerce_int(eval_examples)
    if eval_count is not None:
        payload["eval_examples"] = eval_count

    if missing_optional:
        cleaned = sorted({str(item) for item in missing_optional if item})
        if cleaned:
            payload["missing_optional"] = cleaned

    if extras:
        for key, value in extras.items():
            if value is None:
                continue
            payload[str(key)] = value

    return payload


def log_run_metadata(
    logger: Any,
    *,
    seed: int | None = None,
    deterministic: bool | None = None,
    resume: bool | None = None,
    dataset_format: str | None = None,
    dataset_source: Any | None = None,
    train_examples: Any | None = None,
    eval_examples: Any | None = None,
    missing_optional: Sequence[str] | None = None,
    extras: Mapping[str, Any] | None = None,
    commit_lookup: CommitLookup | None = None,
) -> MutableMapping[str, Any]:
    """Log metadata to ``logger`` if it exposes a ``log`` method."""

    payload = build_run_metadata(
        seed=seed,
        deterministic=deterministic,
        resume=resume,
        dataset_format=dataset_format,
        dataset_source=dataset_source,
        train_examples=train_examples,
        eval_examples=eval_examples,
        missing_optional=missing_optional,
        extras=extras,
        commit_lookup=commit_lookup,
    )

    log_method = getattr(logger, "log", None)
    if callable(log_method):
        log_method(payload)
    return payload


__all__ = ["build_run_metadata", "log_run_metadata", "CommitLookup"]
