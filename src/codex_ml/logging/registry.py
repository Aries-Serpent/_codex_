"""
Logging registry integration draft.

build_loggers(opts) creates list of logger instances.

Supported sinks:
- NDJSONLogger (default)
- MLflowLogger (optional; offline-only; lazy import; disabled by default)

System metrics optional via psutil (flag use_sys_metrics).
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import time
import os

try:
    import psutil  # optional
except ImportError:  # pragma: no cover
    psutil = None


class NDJSONLogger:
    def __init__(self, path: Path, sys_metrics: bool = False):
        self.path = path
        self.sys_metrics = sys_metrics
        self._fh = open(self.path, "a", encoding="utf-8")

    def _sys_metrics(self) -> Dict[str, Any]:
        if not self.sys_metrics or psutil is None:
            return {}
        p = psutil.Process()
        return {
            "mem_rss_mb": round(p.memory_info().rss / (1024 * 1024), 2),
            "cpu_percent": psutil.cpu_percent(interval=None),
        }

    def log(self, record: Dict[str, Any]) -> None:
        rec = dict(record)
        rec["ts"] = time.time()
        rec.update(self._sys_metrics())
        self._fh.write(json.dumps(rec) + "\n")
        self._fh.flush()

    def close(self) -> None:
        try:
            self._fh.close()
        except Exception:  # pragma: no cover
            pass


class MLflowLogger:  # minimal stub, optional
    def __init__(self, sys_metrics: bool = False):  # pragma: no cover (requires mlflow)
        self.sys_metrics = sys_metrics
        try:
            import mlflow

            mlflow.set_tracking_uri("file:" + str(Path("mlruns").absolute()))
            mlflow.start_run()
            self.mlflow = mlflow
        except Exception:
            self.mlflow = None

    def log(self, record: Dict[str, Any]) -> None:  # pragma: no cover
        if self.mlflow is None:
            return
        for k, v in record.items():
            if isinstance(v, (int, float)):
                self.mlflow.log_metric(k, v)
        if self.sys_metrics:
            pass

    def close(self) -> None:  # pragma: no cover
        if self.mlflow:
            try:
                self.mlflow.end_run()
            except Exception:
                pass


def build_loggers(opts: Dict[str, Any]) -> List:
    output_dir = Path(opts.get("output_dir", "runs/logs"))
    output_dir.mkdir(parents=True, exist_ok=True)

    sys_metrics = bool(opts.get("sys_metrics", False))
    use_mlflow = bool(opts.get("use_mlflow", False))

    ndjson_path = output_dir / "metrics.ndjson"

    loggers: List = [NDJSONLogger(ndjson_path, sys_metrics=sys_metrics)]

    if use_mlflow:
        try:
            loggers.append(MLflowLogger(sys_metrics=sys_metrics))
        except Exception:  # pragma: no cover
            pass

    return loggers
