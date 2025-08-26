# BEGIN: CODEX_MLFLOW_UTILS
from __future__ import annotations

import contextlib
import json
import sys
from dataclasses import dataclass
from datetime import datetime
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


_ERRORS_PATH = Path(__file__).resolve().parents[3] / ".codex" / "errors.ndjson"


def _record_error(step: str, err: str, ctx: str) -> None:
    ts = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    _ERRORS_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {"ts": ts, "step": step, "error": err, "context": ctx}
    with _ERRORS_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
    msg = (
        f"Question for ChatGPT-5 {ts}:\n"
        f"While performing [{step}], encountered the following error:\n{err}\n"
        f"Context: {ctx}\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?\n"
    )
    print(msg, file=sys.stderr)


def _noop_cm():
    @contextlib.contextmanager
    def _noop():
        yield False

    return _noop()


def start_run(cfg: MlflowConfig):
    """Context manager that yields the active MLflow run or False when disabled."""
    if not cfg.enable:
        return _noop_cm()
    if not _HAS_MLFLOW:
        _record_error(
            "3.1:start_run", "MLflow not installed", f"uri={cfg.tracking_uri}"
        )
        return _noop_cm()
    try:
        _mlf.set_tracking_uri(cfg.tracking_uri)
        _mlf.set_experiment(cfg.experiment)
        return _mlf.start_run()
    except Exception as e:  # pragma: no cover
        _record_error(
            "3.1:start_run", str(e), f"uri={cfg.tracking_uri}, exp={cfg.experiment}"
        )
        return _noop_cm()


def log_params(d: Mapping[str, Any], *, enabled: bool = False) -> None:
    if enabled and _HAS_MLFLOW:
        try:
            _mlf.log_params(dict(d))  # type: ignore
        except Exception as e:  # pragma: no cover
            _record_error("3.2:log_params", str(e), f"params={list(d.keys())}")


def log_metrics(
    d: Mapping[str, float], step: Optional[int] = None, *, enabled: bool = False
) -> None:
    if enabled and _HAS_MLFLOW:
        try:
            _mlf.log_metrics(dict(d), step=step)  # type: ignore
        except Exception as e:  # pragma: no cover
            _record_error(
                "3.2:log_metrics", str(e), f"metrics={list(d.keys())}, step={step}"
            )


def log_artifacts(path: str | Path, *, enabled: bool = False) -> None:
    if enabled and _HAS_MLFLOW:
        p = Path(path)
        try:
            if p.is_file():
                _mlf.log_artifact(str(p))  # type: ignore
            else:
                _mlf.log_artifacts(str(p))  # type: ignore
        except Exception as e:  # pragma: no cover
            _record_error("3.3:log_artifacts", str(e), f"path={p}")


def seed_snapshot(
    seeds: Mapping[str, Any], out_dir: Path, *, enabled: bool = False
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / "seeds.json"
    p.write_text(json.dumps(seeds, indent=2), encoding="utf-8")
    if enabled and _HAS_MLFLOW:
        log_artifacts(p, enabled=True)


def ensure_local_artifacts(
    run_dir: Path,
    summary: Dict[str, Any],
    seeds: Dict[str, Any],
    *,
    enabled: bool = False,
) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    seed_snapshot(seeds, run_dir, enabled=False)
    if enabled:
        log_artifacts(run_dir, enabled=True)


# END: CODEX_MLFLOW_UTILS
