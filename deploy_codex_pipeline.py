# BEGIN: CODEX_DEPLOY_MONITORING
# Codex injection: TensorBoard, W&B, MLflow wiring + system stats
import argparse
from pathlib import Path


def _codex_stats():
    out = {}
    try:
        import psutil

        out["cpu_pct"] = psutil.cpu_percent(interval=0.1)
        out["mem_pct"] = psutil.virtual_memory().percent
    except Exception:
        pass
    try:
        import pynvml

        pynvml.nvmlInit()
        h = pynvml.nvmlDeviceGetHandleByIndex(0)
        mi = pynvml.nvmlDeviceGetMemoryInfo(h)
        out["gpu_name"] = pynvml.nvmlDeviceGetName(h).decode()
        out["gpu_mem_total"] = int(mi.total)
        out["gpu_mem_used"] = int(mi.used)
    except Exception:
        pass
    return out


def _codex_tb(log_dir: Path):
    try:
        from torch.utils.tensorboard import SummaryWriter

        return SummaryWriter(log_dir=str(log_dir))
    except Exception:
        return None


def _codex_wandb(enable: bool, cfg: dict):
    if not enable:
        return None
    try:
        import wandb

        wandb.init(project=cfg.get("wandb_project", "codex"), config=cfg)
        return wandb
    except Exception:
        return None


def _codex_mlflow(enable: bool, uri: str | None, exp: str | None):
    if not enable:
        return None
    try:
        from codex_ml.tracking import mlflow_utils as MU

        cfg = MU.MlflowConfig(
            tracking_uri=uri or MU.MlflowConfig().tracking_uri,
            experiment=exp or MU.MlflowConfig().experiment,
        )
        run = MU.start_run(cfg)
        return MU, run
    except Exception:
        return None


def _codex_patch_argparse(ap: argparse.ArgumentParser) -> None:
    added = [a.dest for g in ap._action_groups for a in g._group_actions]  # type: ignore
    if "enable_wandb" not in added:
        ap.add_argument(
            "--enable-wandb", action="store_true", help="Enable Weights & Biases logging"
        )
    if "mlflow_enable" not in added:
        ap.add_argument("--mlflow-enable", action="store_true", help="Enable MLflow logging")
    if "mlflow_tracking_uri" not in added:
        ap.add_argument("--mlflow-tracking-uri", default=None, help="MLflow tracking URI")
    if "mlflow_experiment" not in added:
        ap.add_argument("--mlflow-experiment", default=None, help="MLflow experiment name")


def _codex_logging_bootstrap(args, run_dir: Path, params: dict):
    tb = _codex_tb(run_dir / "tb")
    wb = _codex_wandb(bool(getattr(args, "enable_wandb", False)), params)
    mlf = _codex_mlflow(
        bool(getattr(args, "mlflow_enable", False)),
        getattr(args, "mlflow_tracking_uri", None),
        getattr(args, "mlflow_experiment", None),
    )
    return {"tb": tb, "wandb": wb, "mlf": mlf, "stats": _codex_stats()}


def _codex_log_all(handles, step: int, metrics: dict, artifacts: list[Path] | None = None):
    if handles.get("tb"):
        try:
            for k, v in metrics.items():
                handles["tb"].add_scalar(k, float(v), global_step=step)
        except Exception:
            pass
    if handles.get("wandb"):
        try:
            handles["wandb"].log(dict(metrics, step=step))
        except Exception:
            pass
    if handles.get("mlf"):
        try:
            MU, run = handles["mlf"]
            MU.log_metrics(metrics, step=step)
            for art in artifacts or []:
                MU.log_artifacts([art])
        except Exception:
            pass


# END: CODEX_DEPLOY_MONITORING
