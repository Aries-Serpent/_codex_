"""Utilities for writing run metadata alongside metric logs."""

from __future__ import annotations

import datetime as _dt
from typing import Mapping, MutableMapping, Optional

__all__ = ["log_run_metadata"]


def log_run_metadata(
    logger: MutableMapping[str, object] | object,
    *,
    seed: int,
    deterministic: bool,
    resume: bool,
    dataset_format: Optional[str] = None,
    dataset_source: Optional[str] = None,
    train_examples: Optional[int] = None,
    eval_examples: Optional[int] = None,
    extras: Optional[Mapping[str, object]] = None,
) -> None:
    """Record a metadata blob describing the current training run.

    ``logger`` is expected to provide a :py:meth:`log` method accepting a mapping.
    The shim gracefully accepts dictionaries to keep unit tests lightweight.
    """

    payload: dict[str, object] = {
        "timestamp": _dt.datetime.utcnow().isoformat() + "Z",
        "seed": int(seed),
        "deterministic": bool(deterministic),
        "resume": bool(resume),
    }
    if dataset_format is not None:
        payload["dataset_format"] = dataset_format
    if dataset_source is not None:
        payload["dataset_source"] = dataset_source
    if train_examples is not None:
        payload["train_examples"] = int(train_examples)
    if eval_examples is not None:
        payload["eval_examples"] = int(eval_examples)
    if extras:
        payload.update(dict(extras))

    if hasattr(logger, "log"):
        logger.log(payload)  # type: ignore[call-arg]
    elif isinstance(logger, MutableMapping):
        logger.update(payload)
