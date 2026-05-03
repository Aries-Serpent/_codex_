"""
Experiments Module

This module provides functionality for experiments.

Usage:
    from tracking.experiments import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


import json  # noqa: E402
import time  # noqa: E402
import uuid  # noqa: E402
from dataclasses import asdict, dataclass  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402

from .offline import NDJSONLogger  # noqa: E402


@dataclass
class RunInfo:
    run_id: str
    experiment_name: str
    git_hash: str
    config_version: str
    data_version: str


def _run_dir(base_dir: str | Path, run_id: str) -> Path:
    path = Path(base_dir) / run_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def _logger_for(run_dir: Path) -> NDJSONLogger:
    return NDJSONLogger(run_dir / "events.ndjson", max_bytes=10_000_000, backup_count=2)


def _write_metadata(run_dir: Path, run_info: RunInfo) -> None:
    meta_path = run_dir / "run_info.json"
    meta_path.write_text(json.dumps(asdict(run_info), indent=2), encoding="utf-8")


def start_run(run_info: RunInfo, base_dir: str | Path = "artifacts/experiments") -> Path:
    run_dir = _run_dir(base_dir, run_info.run_id)
    _write_metadata(run_dir, run_info)
    logger = _logger_for(run_dir)
    logger.write(
        {
            "type": "start",
            "ts": time.time(),
            "run_id": run_info.run_id,
            "experiment": run_info.experiment_name,
            "git_hash": run_info.git_hash,
            "config_version": run_info.config_version,
            "data_version": run_info.data_version,
        }
    )
    return run_dir


def log_metric(
    run_info: RunInfo,
    name: str,
    value: float,
    step: int | None = None,
    base_dir: str | Path = "artifacts/experiments",
) -> None:
    run_dir = _run_dir(base_dir, run_info.run_id)
    logger = _logger_for(run_dir)
    logger.write(
        {
            "type": "metric",
            "ts": time.time(),
            "run_id": run_info.run_id,
            "name": name,
            "value": float(value),
            "step": step,
        }
    )


def finish_run(
    run_info: RunInfo,
    status: str = "completed",
    base_dir: str | Path = "artifacts/experiments",
) -> Path:
    run_dir = _run_dir(base_dir, run_info.run_id)
    logger = _logger_for(run_dir)
    logger.write(
        {
            "type": "finish",
            "ts": time.time(),
            "run_id": run_info.run_id,
            "status": status,
        }
    )
    return run_dir


def load_events(run_dir: Path) -> list[dict[str, Any]]:
    events_path = run_dir / "events.ndjson"
    if not events_path.exists():
        return []
    events: list[dict[str, Any]] = []
    with events_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                logger.debug("Exception caught, continuing", exc_info=True)
                continue
    return events


def new_run_info(
    experiment_name: str,
    *,
    git_hash: str = "unknown",
    config_version: str = "local",
    data_version: str = "unspecified",
    run_id: str | None = None,
) -> RunInfo:
    return RunInfo(
        run_id=run_id or uuid.uuid4().hex[:12],
        experiment_name=experiment_name,
        git_hash=git_hash,
        config_version=config_version,
        data_version=data_version,
    )
