#!/usr/bin/env python3
"""
Monitoring Integrations Orchestrator
- TensorBoard scalars/histograms
- Optional Weights & Biases (guarded by --enable-wandb and env WANDB_PROJECT)
- Optional MLflow (local file store under output_dir/mlruns)
- System metrics (CPU/RAM; GPU via pynvml) on a background thread
- Docs writer: docs/ops/monitoring.md
- Codex logs: .codex/change_log.md, .codex/errors.ndjson, .codex/results.md

IMPORTANT: DO NOT ACTIVATE ANY GitHub Actions Online files.
All validations MUST run within the Codex environment (this CLI).
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import threading
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional

# ---------------- Codex bookkeeping ----------------
REPO = Path(__file__).resolve().parents[1]
CODEX = REPO / ".codex"
CODEX.mkdir(parents=True, exist_ok=True)
CHANGE_LOG = CODEX / "change_log.md"
ERRORS = CODEX / "errors.ndjson"
RESULTS = CODEX / "results.md"


def ts() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def append(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(text)


def q5(step: str, err: str, ctx: str) -> None:
    """Emit ChatGPT-5 research question + log as ndjson."""
    question = (
        f"Question for ChatGPT-5 {ts()}:\n"
        f"While performing [{step}], encountered the following error:\n{err}\n"
        f"Context: {ctx}\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?\n"
    )
    sys.stderr.write(question + "\n")
    append(
        ERRORS,
        json.dumps({"ts": ts(), "step": step, "error": err, "context": ctx}) + "\n",
    )


def log_change(title: str, path: Path, rationale: str, body_snippet: str = "") -> None:
    if not CHANGE_LOG.exists():
        CHANGE_LOG.write_text("# Codex Change Log\n", encoding="utf-8")
    entry = (
        f"## {ts()} — {path.relative_to(REPO)}\n"
        f"- **Action:** {title}\n"
        f"- **Rationale:** {rationale}\n"
    )
    if body_snippet:
        entry += f"```text\n{body_snippet[:4000]}\n```\n"
    entry += "\n"
    append(CHANGE_LOG, entry)


# ---------------- Optional imports with graceful fallback ----------------


def try_import(module_name: str):
    try:
        return __import__(module_name)
    except Exception:
        return None


torch = try_import("torch")
# Prefer torch.utils.tensorboard if torch exists; otherwise try tensorboardX
SummaryWriter = None
if torch is not None:
    try:
        from torch.utils.tensorboard import SummaryWriter as _SW  # type: ignore

        SummaryWriter = _SW
    except Exception:
        SummaryWriter = None
if SummaryWriter is None:
    tbx = try_import("tensorboardX")
    if tbx is not None:
        SummaryWriter = getattr(tbx, "SummaryWriter", None)

wandb = try_import("wandb")
mlflow = try_import("mlflow")
psutil = try_import("psutil")
pynvml = try_import("pynvml")


# ---------------- System metrics thread ----------------
class SystemMetrics(threading.Thread):
    def __init__(self, interval_s: float, log_fn: Callable[[Dict[str, Any]], None]):
        super().__init__(daemon=True)
        self.interval_s = interval_s
        self.log_fn = log_fn
        self._stop = threading.Event()
        self.gpu_ok = False
        if pynvml:
            try:
                pynvml.nvmlInit()
                self.gpu_ok = True
            except Exception:
                self.gpu_ok = False

    def run(self) -> None:
        while not self._stop.is_set():
            try:
                payload: Dict[str, Any] = {"ts": ts()}
                if psutil:
                    vm = psutil.virtual_memory()
                    payload.update(
                        {
                            "cpu_percent": psutil.cpu_percent(interval=None),
                            "ram_used_mb": vm.used / (1024**2),
                            "ram_total_mb": vm.total / (1024**2),
                        }
                    )
                if self.gpu_ok:
                    try:
                        count = pynvml.nvmlDeviceGetCount()
                        gpus = []
                        for i in range(count):
                            h = pynvml.nvmlDeviceGetHandleByIndex(i)
                            util = pynvml.nvmlDeviceGetUtilizationRates(h)
                            mem = pynvml.nvmlDeviceGetMemoryInfo(h)
                            gpus.append(
                                {
                                    "index": i,
                                    "gpu_util": util.gpu,
                                    "mem_util": util.memory,
                                    "mem_used_mb": mem.used / (1024**2),
                                    "mem_total_mb": mem.total / (1024**2),
                                }
                            )
                        payload["gpus"] = gpus
                    except Exception as e:
                        payload["gpu_error"] = f"{type(e).__name__}: {e}"
                self.log_fn(payload)
            except Exception as e:
                q5(
                    "SystemMetrics:collect",
                    f"{type(e).__name__}: {e}",
                    "Collecting system metrics",
                )
            finally:
                time.sleep(self.interval_s)

    def stop(self) -> None:
        self._stop.set()
        if self.gpu_ok:
            try:
                pynvml.nvmlShutdown()
            except Exception:
                pass


# ---------------- Monitoring Session ----------------
class MonitoringSession:
    """Wraps TB/W&B/MLflow with safe, optional initialization."""

    def __init__(
        self,
        output_dir: Path,
        run_name: str,
        enable_tb: bool,
        enable_wandb: bool,
        enable_mlflow: bool,
        metrics_interval: float = 5.0,
    ) -> None:
        self.output_dir = output_dir
        self.run_name = run_name
        self.enable_tb = enable_tb
        self.enable_wandb = enable_wandb and (os.getenv("WANDB_PROJECT") is not None)
        self.enable_mlflow = enable_mlflow
        self.metrics_interval = metrics_interval

        self.tb = None
        self.wb = None
        self.mlf = None
        self.metrics_thread: Optional[SystemMetrics] = None

        self.tb_dir = output_dir / "tensorboard"
        self.artifacts = output_dir / "artifacts"
        self.logs = output_dir / "logs"
        self.mlruns = output_dir / "mlruns"

        self.tb_dir.mkdir(parents=True, exist_ok=True)
        self.artifacts.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)
        if self.enable_mlflow:
            self.mlruns.mkdir(parents=True, exist_ok=True)

    def _log_exception(self, where: str) -> None:
        append(
            self.logs / "monitoring_errors.log",
            f"[{ts()}] error in {where}\n{traceback.format_exc()}\n",
        )

    def __enter__(self) -> "MonitoringSession":
        if self.enable_tb and SummaryWriter is not None:
            try:
                self.tb = SummaryWriter(log_dir=str(self.tb_dir))
            except Exception as e:
                q5(
                    "TB:init",
                    f"{type(e).__name__}: {e}",
                    "Initialize TensorBoard SummaryWriter",
                )
                self._log_exception("tb_init")
        if self.enable_wandb and wandb is not None:
            try:
                self.wb = wandb.init(
                    project=os.environ["WANDB_PROJECT"],
                    name=self.run_name,
                    dir=str(self.output_dir),
                    settings=wandb.Settings(start_method="thread", _disable_stats=True),
                )
            except Exception as e:
                q5(
                    "W&B:init",
                    f"{type(e).__name__}: {e}",
                    "Initialize wandb (project/name/dir)",
                )
                self._log_exception("wandb_init")
        if self.enable_mlflow and mlflow is not None:
            try:
                mlflow.set_tracking_uri(f"file:{self.mlruns}")
                mlflow.set_experiment(self.run_name)
                self.mlf = mlflow.start_run(run_name=self.run_name)
            except Exception as e:
                q5(
                    "MLflow:init",
                    f"{type(e).__name__}: {e}",
                    "Initialize MLflow local file store",
                )
                self._log_exception("mlflow_init")
        try:
            self.metrics_thread = SystemMetrics(
                self.metrics_interval, self.log_system_metrics
            )
            self.metrics_thread.start()
        except Exception as e:
            q5(
                "SysMetrics:start",
                f"{type(e).__name__}: {e}",
                "Start system metrics thread",
            )
            self._log_exception("metrics_start")
        return self

    def log_scalar(self, tag: str, value: float, step: int) -> None:
        try:
            if self.tb:
                self.tb.add_scalar(tag, value, step)
            if self.wb:
                wandb.log({tag: value, "step": step})
            if self.mlf:
                mlflow.log_metric(tag, value, step=step)
        except Exception as e:
            q5(
                "log_scalar",
                f"{type(e).__name__}: {e}",
                f"tag={tag}, value={value}, step={step}",
            )

    def log_histogram(self, tag: str, values, step: int, bins: int = 64) -> None:
        try:
            if self.tb and hasattr(self.tb, "add_histogram"):
                self.tb.add_histogram(tag, values, step, bins=bins)
            if self.wb:
                try:
                    self.wb.log({tag: wandb.Histogram(np_histogram=(values, bins))})
                except Exception:
                    pass
            if self.mlf:
                p = self.artifacts / f"{tag.replace('/', '_')}_hist_step{step}.json"
                with p.open("w", encoding="utf-8") as f:
                    json.dump(
                        {
                            "tag": tag,
                            "step": step,
                            "bins": bins,
                            "values_len": len(values),
                        },
                        f,
                    )
                mlflow.log_artifact(str(p))
        except Exception as e:
            q5(
                "log_histogram",
                f"{type(e).__name__}: {e}",
                f"tag={tag}, step={step}, bins={bins}",
            )

    def log_artifact(
        self, local_path: Path, artifact_name: Optional[str] = None
    ) -> None:
        try:
            if self.mlf:
                mlflow.log_artifact(str(local_path), artifact_path=artifact_name or "")
            if self.wb:
                wandb.save(str(local_path))
        except Exception as e:
            q5("log_artifact", f"{type(e).__name__}: {e}", f"path={local_path}")

    def log_system_metrics(self, payload: dict) -> None:
        try:
            append(self.logs / "system_metrics.jsonl", json.dumps(payload) + "\n")
            step = int(time.time())
            if "cpu_percent" in payload:
                self.log_scalar(
                    "system/cpu_percent", float(payload["cpu_percent"]), step
                )
            if "ram_used_mb" in payload:
                self.log_scalar(
                    "system/ram_used_mb", float(payload["ram_used_mb"]), step
                )
        except Exception as e:
            q5(
                "log_system_metrics",
                f"{type(e).__name__}: {e}",
                "write & route metrics",
            )

    def __exit__(self, exc_type, exc, tb) -> bool:
        try:
            if self.metrics_thread:
                self.metrics_thread.stop()
            if self.mlf:
                try:
                    mlflow.end_run(status="FAILED" if exc_type else "FINISHED")
                except Exception:
                    pass
            if self.tb:
                try:
                    self.tb.flush()
                    self.tb.close()
                except Exception:
                    pass
            if self.wb:
                try:
                    wandb.finish(exit_code=1 if exc_type else 0)
                except Exception:
                    pass
        except Exception as e:
            q5("MonitoringSession:exit", f"{type(e).__name__}: {e}", "teardown")
        return False


# ---------------- Docs writer ----------------
def write_monitoring_docs() -> None:
    path = REPO / "docs" / "ops" / "monitoring.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    body = (
        "# Monitoring & Experiment Tracking\n\n"
        "This project provides optional integration for:\n"
        "- **TensorBoard** (scalars, histograms): logs under `runs/<run-name>/tensorboard/`\n"
        "- **Weights & Biases (W&B)**: enable with `--enable-wandb` and environment `WANDB_PROJECT=<your_project>`\n"
        "- **MLflow** (local file store): logs to `runs/<run-name>/mlruns/`\n\n"
        "## Quickstart\n\n"
        "```bash\n"
        "python tools/monitoring_integrate.py --run-name demo --enable-tensorboard --enable-mlflow\n"
        "# With Weights & Biases\n"
        "WANDB_PROJECT=myproj python tools/monitoring_integrate.py --run-name demo --enable-tensorboard --enable-wandb\n"
        "```\n\n"
        "### Viewing\n"
        "- TensorBoard: `tensorboard --logdir runs/demo/tensorboard`\n"
        "- MLflow UI: `mlflow ui --backend-store-uri file:runs/demo/mlruns`\n\n"
        "All executions run locally via CLI. Do NOT activate any GitHub Actions online files.\n"
    )
    path.write_text(body, encoding="utf-8")
    log_change("create", path, "Add monitoring documentation", body)


# ---------------- Demo loop (no model required) ----------------
def demo_training_loop(mon: MonitoringSession, steps: int = 50) -> None:
    """Logs synthetic metrics to validate integrations."""
    for step in range(steps):
        loss = math.exp(-step / 20) + random.uniform(0, 0.02)
        acc = 1.0 - loss + random.uniform(0, 0.01)
        mon.log_scalar("train/loss", loss, step)
        mon.log_scalar("train/accuracy", acc, step)
        values = [random.gauss(0, 1) for _ in range(2048)]
        mon.log_histogram("train/activation_dist", values, step, bins=64)
        if step % 10 == 0:
            snap = mon.artifacts / f"snapshot_step{step}.json"
            snap.write_text(
                json.dumps({"step": step, "loss": loss, "acc": acc}, indent=2),
                encoding="utf-8",
            )
            mon.log_artifact(snap, artifact_name="snapshots")
        time.sleep(0.1)


# ---------------- CLI ----------------
def main() -> None:
    ap = argparse.ArgumentParser(
        description="Integrate monitoring (TB/W&B/MLflow) with system metrics."
    )
    ap.add_argument("--run-name", default="demo", help="Name for this run.")
    ap.add_argument(
        "--output-root", default="runs", help="Root directory for run outputs."
    )
    ap.add_argument(
        "--enable-tensorboard", action="store_true", help="Enable TensorBoard logging."
    )
    ap.add_argument(
        "--enable-wandb",
        action="store_true",
        help="Enable W&B logging (requires WANDB_PROJECT).",
    )
    ap.add_argument(
        "--enable-mlflow",
        action="store_true",
        help="Enable MLflow local file tracking.",
    )
    ap.add_argument(
        "--metrics-interval",
        type=float,
        default=5.0,
        help="System metrics interval in seconds.",
    )
    ap.add_argument("--steps", type=int, default=50, help="Demo steps to run.")
    ap.add_argument(
        "--write-docs", action="store_true", help="Also write docs/ops/monitoring.md."
    )
    args = ap.parse_args()

    out = REPO / args.output_root / args.run_name
    out.mkdir(parents=True, exist_ok=True)
    log_change("create", out, "Prepare monitoring output dir")

    if args.write_docs:
        try:
            write_monitoring_docs()
        except Exception as e:
            q5("Docs:write", f"{type(e).__name__}: {e}", "docs/ops/monitoring.md")

    try:
        with MonitoringSession(
            out,
            args.run_name,
            enable_tb=args.enable_tensorboard,
            enable_wandb=args.enable_wandb,
            enable_mlflow=args.enable_mlflow,
            metrics_interval=args.metrics_interval,
        ) as mon:
            demo_training_loop(mon, steps=args.steps)
    except Exception as e:
        q5(
            "Run:monitoring_session",
            f"{type(e).__name__}: {e}",
            "starting or running monitoring session",
        )

    summary = {
        "ts": ts(),
        "acceptance": {
            "tensorboard_dir": str(out / "tensorboard"),
            "mlflow_dir": str(out / "mlruns"),
            "artifacts_dir": str(out / "artifacts"),
            "wandb_enabled": bool(args.enable_wandb and os.getenv("WANDB_PROJECT")),
        },
        "note": "TensorBoard should display scalars/histograms; W&B logs if enabled; MLflow artifacts recorded.",
    }
    append(RESULTS, json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        q5("TopLevel", f"{type(e).__name__}: {e}", "monitoring_integrate main")
        raise
