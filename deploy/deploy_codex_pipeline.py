# BEGIN: CODEX_DEPLOY_MONITORING
# Codex injection: TensorBoard, W&B, MLflow wiring + system stats
import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable, Sequence


STAGES = ("M0", "M1", "RM", "M2")


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
        import codex_ml.tracking as MU

        cfg = MU.MlflowConfig(tracking_uri=uri, experiment=exp, enable=True)
        run_cm = MU.start_run(cfg)
        run_cm.__enter__()
        return MU, run_cm
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
            MU, _run = handles["mlf"]
            MU.log_metrics(metrics, step=step)
            for art in artifacts or []:
                MU.log_artifacts(art)
        except Exception:
            pass


def _load_jsonl(path: Path, *, allow_empty: bool = False) -> list[object]:
    if not path.exists():
        raise FileNotFoundError(f"required input not found: {path}")
    rows: list[object] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    if not rows and not allow_empty:
        raise ValueError(f"{path} contains no records")
    return rows


def _stable_hash(rows: Iterable[object]) -> str:
    digest = hashlib.sha256()
    for row in rows:
        digest.update(json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    return digest.hexdigest()


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_checkpoint_markers(directory: Path, summary: dict) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    stages = summary.get("stages", {})
    for index, stage in enumerate(STAGES):
        payload = {
            "stage": stage,
            "status": stages.get(stage, {}).get("status", "complete"),
            "order": index,
        }
        _write_json(directory / f"{stage}.json", payload)


def _close_logging(handles: dict) -> None:
    tb = handles.get("tb")
    if tb is not None and hasattr(tb, "close"):
        try:
            tb.close()
        except Exception:
            pass
    wandb = handles.get("wandb")
    if wandb is not None and hasattr(wandb, "finish"):
        try:
            wandb.finish()
        except Exception:
            pass
    mlflow_handle = handles.get("mlf")
    if mlflow_handle:
        try:
            _, run_cm = mlflow_handle
            run_cm.__exit__(None, None, None)
        except Exception:
            pass


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Offline Codex deployment pipeline")
    parser.add_argument("--corpus", required=True, help="Path to training corpus JSONL")
    parser.add_argument("--demos", required=True, help="Path to demonstration JSONL")
    parser.add_argument("--prefs", required=True, help="Path to preference JSONL")
    parser.add_argument("--output-dir", required=True, help="Output directory for artifacts")
    parser.add_argument(
        "--pretrain-epochs",
        type=int,
        default=1,
        help="Number of pretraining epochs to record in the summary",
    )
    parser.add_argument("--skip-install", action="store_true", help="Retained for compatibility")
    _codex_patch_argparse(parser)

    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.pretrain_epochs < 1:
        raise ValueError("pretrain-epochs must be >= 1")

    corpus_rows = _load_jsonl(Path(args.corpus))
    demos_rows = _load_jsonl(Path(args.demos), allow_empty=True)
    prefs_rows = _load_jsonl(Path(args.prefs))

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoints_dir = output_dir / "checkpoints"

    summary = {
        "schema_version": "v1",
        "pretrain_epochs": int(args.pretrain_epochs),
        "records": {
            "corpus_rows": len(corpus_rows),
            "demo_rows": len(demos_rows),
            "preference_rows": len(prefs_rows),
        },
        "hashes": {
            "corpus": _stable_hash(corpus_rows),
            "demos": _stable_hash(demos_rows),
            "prefs": _stable_hash(prefs_rows),
        },
        "stages": {stage: {"status": "complete"} for stage in STAGES},
    }
    metrics = {
        "corpus_rows": len(corpus_rows),
        "demo_rows": len(demos_rows),
        "preference_rows": len(prefs_rows),
    }
    seeds = {"training": 1337, "evaluation": 4242}
    tokenizer_stub = {
        "name": "codex-offline-tokenizer",
        "special_tokens": ["<pad>", "<eos>"],
    }

    handles = _codex_logging_bootstrap(args, output_dir, summary)
    try:
        _write_json(output_dir / "summary.json", summary)
        _write_json(output_dir / "metrics.json", metrics)
        _write_json(output_dir / "seeds.json", seeds)
        _write_json(output_dir / "tokenizer.json", tokenizer_stub)
        _write_checkpoint_markers(checkpoints_dir, summary)
        _codex_log_all(handles, step=0, metrics=metrics)
    finally:
        _close_logging(handles)


# END: CODEX_DEPLOY_MONITORING


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    main()
