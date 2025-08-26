#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Codex Orchestrator: Experiment Tracking (MLflow utilities, flags, docs).

Creates:
- codex_ml/tracking/mlflow_utils.py (lazy MLflow import, safe no-ops)
- codex_ml/tracking/__init__.py
- codex_ml/tracking/cli.py (flag helpers)
- docs/ops/experiment_tracking.md

Validation:
- File-only logging always runs.
- If mlflow is installed and --mlflow-enable is set, log a minimal run to the given experiment.

Policy:
- DO NOT ACTIVATE ANY GitHub Actions Online files. ALL GitHub Actions such as pre-commit, validation, etc MUST EXPLICITLY RUN WITHIN THE CODEX ENVIRONMENT.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import textwrap
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

REPO = Path(__file__).resolve().parents[1]
CODEX = REPO / ".codex"
CODEX.mkdir(parents=True, exist_ok=True)
CHANGE_LOG = CODEX / "change_log.md"
ERRORS = CODEX / "errors.ndjson"
RESULTS = CODEX / "results.md"
sys.path.insert(0, str(REPO / "src"))


def ts() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def log_change(action: str, path: Path, why: str, preview: str = "") -> None:
    if not CHANGE_LOG.exists() or CHANGE_LOG.stat().st_size == 0:
        CHANGE_LOG.write_text("# Codex Change Log\n", encoding="utf-8")
    with CHANGE_LOG.open("a", encoding="utf-8") as fh:
        fh.write(f"## {ts()} — {path.relative_to(REPO)}\n- **Action:** {action}\n- **Rationale:** {why}\n")
        if preview:
            fh.write("```text\n" + preview[:4000] + "\n```\n")
        fh.write("\n")


def q5(step: str, err: str, ctx: str) -> None:
    rq = textwrap.dedent(
        f"""
        Question for ChatGPT-5 {ts()}:
        While performing [{step}], encountered the following error:
        {err}
        Context: {ctx}
        What are the possible causes, and how can this be resolved while preserving intended functionality?
        """
    )
    with ERRORS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"ts": ts(), "step": step, "error": err, "context": ctx}) + "\n")
    sys.stderr.write(rq + "\n")


def upsert(path: Path, content: str, sentinel: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and sentinel in path.read_text(encoding="utf-8", errors="ignore"):
        return
    path.write_text(content, encoding="utf-8")
    log_change("upsert", path, f"insert guarded by {sentinel}", content)


# ----------------- codex_ml/tracking/mlflow_utils.py -----------------
UTILS_SENT = "# BEGIN: CODEX_MLFLOW_UTILS"
UTILS_CODE = UTILS_SENT + '''
from __future__ import annotations

import contextlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

# Lazy import of mlflow
try:  # pragma: no cover
    import mlflow as _mlf  # type: ignore
    _HAS_MLFLOW = True
except Exception:  # pragma: no cover
    _HAS_MLFLOW = False
    _mlf = None  # type: ignore


@dataclass
class MlflowConfig:
    enable: bool = False
    tracking_uri: str = "./mlruns"
    experiment: str = "codex-experiments"


def start_run(cfg: MlflowConfig):
    """Context manager that yields the active run or False when disabled.

    Raises:
        RuntimeError: if MLflow was requested but is unavailable.
    """
    if not cfg.enable:
        @contextlib.contextmanager
        def _noop():
            yield False
        return _noop()
    if not _HAS_MLFLOW:
        raise RuntimeError("MLflow requested but not installed")
    _mlf.set_tracking_uri(cfg.tracking_uri)
    _mlf.set_experiment(cfg.experiment)
    return _mlf.start_run()


def log_params(d: Mapping[str, Any], *, enabled: bool = False) -> None:
    if enabled and _HAS_MLFLOW:
        _mlf.log_params(dict(d))  # type: ignore


def log_metrics(d: Mapping[str, float], step: Optional[int] = None, *, enabled: bool = False) -> None:
    if enabled and _HAS_MLFLOW:
        _mlf.log_metrics(dict(d), step=step)  # type: ignore


def log_artifacts(path: str | Path, *, enabled: bool = False) -> None:
    if enabled and _HAS_MLFLOW:
        _mlf.log_artifacts(str(path))  # type: ignore


def ensure_local_artifacts(run_dir: Path, summary: Dict[str, Any], seeds: Dict[str, Any]) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (run_dir / "seeds.json").write_text(json.dumps(seeds, indent=2), encoding="utf-8")
# END: CODEX_MLFLOW_UTILS
'''

# ----------------- codex_ml/tracking/__init__.py -----------------
INIT_SENT = "# BEGIN: CODEX_MLFLOW_INIT"
INIT_CODE = INIT_SENT + '''
from .mlflow_utils import (
    MlflowConfig,
    ensure_local_artifacts,
    log_artifacts,
    log_metrics,
    log_params,
    start_run,
)

__all__ = [
    "MlflowConfig",
    "start_run",
    "log_params",
    "log_metrics",
    "log_artifacts",
    "ensure_local_artifacts",
]
# END: CODEX_MLFLOW_INIT
'''

# ----------------- codex_ml/tracking/cli.py -----------------
CLI_SENT = "# BEGIN: CODEX_MLFLOW_CLI"
CLI_CODE = CLI_SENT + '''
from __future__ import annotations

import argparse

from .mlflow_utils import MlflowConfig


def add_mlflow_flags(parser: argparse.ArgumentParser) -> None:
    g = parser.add_argument_group("MLflow")
    g.add_argument(
        "--mlflow-enable",
        action="store_true",
        default=False,
        help="Enable MLflow logging (optional dependency).",
    )
    g.add_argument(
        "--mlflow-tracking-uri",
        default="./mlruns",
        help="MLflow tracking URI or path (default: ./mlruns).",
    )
    g.add_argument(
        "--mlflow-experiment",
        default="codex-experiments",
        help="MLflow experiment name.",
    )


def mlflow_from_args(args) -> MlflowConfig:
    return MlflowConfig(
        enable=bool(getattr(args, "mlflow_enable", False)),
        tracking_uri=str(getattr(args, "mlflow_tracking_uri", "./mlruns")),
        experiment=str(getattr(args, "mlflow_experiment", "codex-experiments")),
    )
# END: CODEX_MLFLOW_CLI
'''

# ----------------- docs/ops/experiment_tracking.md -----------------
DOCS_SENT = "<!-- BEGIN: CODEX_MLFLOW_DOCS -->"
DOCS_CODE = DOCS_SENT + '''
# Experiment Tracking (MLflow)

This project provides optional MLflow integration that can be enabled via CLI flags.
If MLflow is not installed, tracking gracefully degrades to local JSON artifact logging.

## CLI Flags
- `--mlflow-enable` — turn on MLflow logging.
- `--mlflow-tracking-uri` — defaults to `./mlruns` (local file store).
- `--mlflow-experiment` — experiment name (default `codex-experiments`).

## Programmatic Usage
```python
from codex_ml.tracking import MlflowConfig, start_run, log_params, log_metrics, log_artifacts, ensure_local_artifacts
from pathlib import Path
cfg = MlflowConfig(enable=True, tracking_uri="./mlruns", experiment="demo")
run_dir = Path("output/experiments/12345")
with start_run(cfg) as run:
    enabled = bool(run)
    log_params({"model": "demo"}, enabled=enabled)
    log_metrics({"accuracy": 0.9}, step=1, enabled=enabled)
    ensure_local_artifacts(run_dir, {"status": "ok"}, {"seed": 42})
    log_artifacts(run_dir, enabled=enabled)
```

## Reproducibility

* Fix random seeds across libraries.
* Log `seeds.json` and config snapshot along with checkpoints.
* Re-running with the same seed **should** yield identical metrics (subject to nondeterministic ops).

> **Policy:** DO NOT ACTIVATE ANY GitHub Actions Online files. Run validations locally in the Codex environment.
'''


def apply() -> None:
    try:
        upsert(REPO / "src" / "codex_ml" / "tracking" / "mlflow_utils.py", UTILS_CODE, UTILS_SENT)
        upsert(REPO / "src" / "codex_ml" / "tracking" / "__init__.py", INIT_CODE, INIT_SENT)
        upsert(REPO / "src" / "codex_ml" / "tracking" / "cli.py", CLI_CODE, CLI_SENT)
        upsert(REPO / "docs" / "ops" / "experiment_tracking.md", DOCS_CODE, DOCS_SENT)
    except Exception as e:  # pragma: no cover
        q5("3: Best-Effort Construction — write files", str(e), f"path={REPO}")


def _set_global_seeds(seed: int) -> Dict[str, Any]:
    try:
        import numpy as np  # type: ignore
    except Exception:  # pragma: no cover
        np = None  # type: ignore

    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    if np is not None:
        try:
            np.random.seed(seed)  # type: ignore
        except Exception:  # pragma: no cover
            pass
    return {"python": seed, "numpy": seed if np is not None else None}


def validate_run(enable_mlflow: bool, tracking_uri: str, experiment: str) -> None:
    from codex_ml.tracking import (
        MlflowConfig,
        ensure_local_artifacts,
        log_artifacts,
        log_metrics,
        log_params,
        start_run,
    )

    run_id = f"run-{int(time.time())}"
    out_dir = REPO / "output" / "experiments" / run_id
    seeds = _set_global_seeds(1234)
    summary = {"run_id": run_id, "metric@seed1234": 0.1234}
    cfg = MlflowConfig(enable=enable_mlflow, tracking_uri=tracking_uri, experiment=experiment)

    enabled = False
    try:
        with start_run(cfg) as run:
            enabled = bool(run)
            log_params({"run_id": run_id, "seed": 1234}, enabled=enabled)
            log_metrics({"loss": 1.0, "acc": 0.5}, step=1, enabled=enabled)
    except Exception as e:
        q5(
            "3.1: start_run",
            str(e),
            f"enable={enable_mlflow}, uri={tracking_uri}, exp={experiment}",
        )

    ensure_local_artifacts(out_dir, summary, seeds)
    ckpt = out_dir / "checkpoints" / "epoch-1"
    ckpt.mkdir(parents=True, exist_ok=True)
    (ckpt / "ckpt.bin").write_bytes(b"demo")
    try:
        log_artifacts(out_dir, enabled=enabled)
    except Exception as e:  # pragma: no cover
        q5("3.3: log_artifacts", str(e), f"path={out_dir}")

    with RESULTS.open("a", encoding="utf-8") as fh:
        fh.write(f"\n# Validation {ts()}\n")
        fh.write(f"- Created local artifacts at: {out_dir}\n")
        fh.write(f"- MLflow enabled: {enable_mlflow}\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="create MLflow utilities, CLI flags, docs")
    ap.add_argument("--validate", action="store_true", help="run local validation (file logging, optional MLflow)")
    ap.add_argument("--mlflow-enable", action="store_true", default=False)
    ap.add_argument("--mlflow-tracking-uri", default="./mlruns")
    ap.add_argument("--mlflow-experiment", default="codex-experiments")
    args = ap.parse_args()

    if args.apply:
        apply()
    if args.validate:
        validate_run(args.mlflow_enable, args.mlflow_tracking_uri, args.mlflow_experiment)
    if not (args.apply or args.validate):
        print(
            "Usage: --apply [--validate] [--mlflow-enable] [--mlflow-tracking-uri URI] [--mlflow-experiment NAME]"
        )


if __name__ == "__main__":
    main()
