"""Minimal experiment tracking helper for `_codex_`.

This is intentionally lightweight and offline-only. It does NOT depend
on MLflow, W&B, or any external tracking service.

Design:

- Each run directory (e.g. runs/train/<run_id>) may contain:
  - run_manifest.yaml   (already produced by train/eval CLIs)
  - metrics.ndjson      (already produced by MetricLogger)
  - experiment_meta.json (added by this module)

- `experiment_meta.json` is a single JSON object:

  {
    "experiment_name": "...",
    "mode": "train" | "eval",
    "run_id": "...",
    "labels": { ... arbitrary key/value ... }
  }

Callers:

- `codex_ml.cli.train_minimal`
- `codex_ml.cli.eval_minimal`
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class ExperimentMeta:
    experiment_name: str
    mode: str
    run_id: str
    labels: dict[str, Any]


class ExperimentTracker:
    """Best-effort experiment metadata writer."""

    def __init__(self, run_dir: Path, mode: str, run_id: str) -> None:
        self._run_dir = Path(run_dir).expanduser().resolve()
        self._mode = mode
        self._run_id = run_id

    def log_experiment(
        self,
        experiment_name: Optional[str],
        labels: Optional[dict[str, Any]] = None,
    ) -> None:
        """Write experiment_meta.json if an experiment name is provided.

        If experiment_name is None or empty, this is a no-op.
        """

        if not experiment_name:
            return
        meta = ExperimentMeta(
            experiment_name=experiment_name,
            mode=self._mode,
            run_id=self._run_id,
            labels=labels or {},
        )
        out = self._run_dir / "experiment_meta.json"
        out.write_text(
            json.dumps(asdict(meta), indent=2, sort_keys=True),
            encoding="utf-8",
        )
