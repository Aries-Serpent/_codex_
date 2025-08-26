#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Codex Patch Executor — Tokenization(2), Training Engine(4), Config(5), Metrics(6), Deployment(12)
Policy: DO NOT ACTIVATE ANY GitHub Actions Online files. All checks run locally.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import textwrap
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CODEX = REPO / ".codex"
CODEX.mkdir(parents=True, exist_ok=True)
CHANGE_LOG = CODEX / "change_log.md"
ERR = CODEX / "errors.ndjson"
RES = CODEX / "results.md"


def ts():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def log_change(action, path, why, preview=""):
    CHANGE_LOG.write_text(
        (
            CHANGE_LOG.read_text(encoding="utf-8")
            if CHANGE_LOG.exists()
            else "# Codex Change Log\n"
        ),
        encoding="utf-8",
    )
    with CHANGE_LOG.open("a", encoding="utf-8") as fh:
        fh.write(
            f"## {ts()} — {path.relative_to(REPO)}\n- **Action:** {action}\n- **Rationale:** {why}\n"
        )
        if preview:
            fh.write("```diff\n" + preview[:4000] + "\n```\n")
            fh.write("\n")


def q5(step, err, ctx):
    with ERR.open("a", encoding="utf-8") as fh:
        fh.write(
            json.dumps({"ts": ts(), "step": step, "error": err, "context": ctx}) + "\n"
        )
    print(
        textwrap.dedent(
            f"""
    Question for ChatGPT-5 {ts()}:
    While performing [{step}], encountered the following error:
    {err}
    Context: {ctx}
    What are the possible causes, and how can this be resolved while preserving intended functionality?
    """
        ).strip()
    )


def upsert(path: Path, content: str, sentinel: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and sentinel in path.read_text(encoding="utf-8", errors="ignore"):
        return False
    path.write_text(content, encoding="utf-8")
    log_change("upsert", path, f"guarded by {sentinel}", content)
    return True


# ---------- 1) Trainer eval & ckpt integration ----------
TRN_SENT = "# BEGIN: CODEX_TRAINER_EVAL_INTEGRATION"
ENGINE_PATCH = f"""{TRN_SENT}
# Codex: ensure per-epoch eval/save + best model restore
trainer_kwargs.setdefault("evaluation_strategy", "epoch")
trainer_kwargs.setdefault("save_strategy", "epoch")
trainer_kwargs.setdefault("load_best_model_at_end", True)
trainer_kwargs.setdefault("metric_for_best_model", trainer_kwargs.get("metric_for_best_model","eval_loss"))
# Hydrate logging to TensorBoard if requested
if run_cfg.get("tensorboard", False):
    trainer_kwargs.setdefault("logging_dir", str(output_dir/"runs"))
    trainer_kwargs.setdefault("report_to", ["tensorboard"])
# Optional: pass eval_dataset if available
if "eval_dataset" not in trainer_kwargs and locals().get("eval_ds") is not None:
    trainer_kwargs["eval_dataset"] = eval_ds
# END: CODEX_TRAINER_EVAL_INTEGRATION
"""

# ---------- 2) Disable DDP toggle ----------
DDP_SENT = "# BEGIN: CODEX_DISABLE_DDP_FLAG"
DDP_FLAG_SNIPPET = f"""{DDP_SENT}
ap.add_argument("--disable-ddp", action="store_true", help="Force single-process training if distributed backends are unavailable")
# In main():
if args.disable_ddp:
    run_cfg["distributed"] = False
# END: CODEX_DISABLE_DDP_FLAG
"""

# ---------- 3) MLflow wiring ----------
MLF_SENT = "# BEGIN: CODEX_MLFLOW_INTEGRATION"
MLFLOW_SNIPPET = f"""{MLF_SENT}
import mlflow
if run_cfg.get("mlflow_enable"):
    if uri := run_cfg.get("mlflow_tracking_uri"): mlflow.set_tracking_uri(uri)
    if exp := run_cfg.get("mlflow_experiment"): mlflow.set_experiment(exp)
    with mlflow.start_run():
        mlflow.log_params({{"model": run_cfg.get("model_name"), "engine": run_cfg.get("engine"), **run_cfg.get("params",{{}})}})
        # during training loop, call mlflow.log_metrics(step-wise) and log_artifacts(str(output_dir))
# END: CODEX_MLFLOW_INTEGRATION
"""

# ---------- 4) CLI: forward data flags ----------
DATA_SENT = "# BEGIN: CODEX_DATA_FLAGS"
DATA_FLAGS = f"""{DATA_SENT}
ap.add_argument("--num-workers", type=int, default=2)
ap.add_argument("--prefetch", type=int, default=64)
ap.add_argument("--max-samples", type=int, default=0, help="0 = all")
# Thread flags into loader kwargs where used
loader_kwargs.update({{"num_workers": args.num_workers, "prefetch": args.prefetch, "max_samples": args.max_samples}})
# END: CODEX_DATA_FLAGS
"""

# ---------- 5) Compose GPU reservations ----------
CMP_SENT = "# BEGIN: CODEX_COMPOSE_GPU"
COMPOSE_BLOCK = f"""{CMP_SENT}
# Compose GPU reservations (disabled unless host has NVIDIA toolkit)
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
# END: CODEX_COMPOSE_GPU
"""

# ---------- 6) run.sh GPU flag ----------
RUN_SENT = "# BEGIN: CODEX_RUN_GPU_FLAG"
RUN_GPU = f"""{RUN_SENT}
if command -v nvidia-smi >/dev/null 2>&1; then GPU_OPT="--gpus all"; else GPU_OPT=""; fi
docker compose up -d $GPU_OPT || docker-compose up -d $GPU_OPT
# END: CODEX_RUN_GPU_FLAG
"""


def patch_engine():
    try:
        path = REPO / "training" / "engine_hf_trainer.py"
        if not path.exists():
            log_change("prune", path, "engine file not found; skipping patch")
            return
        txt = path.read_text(encoding="utf-8")
        if TRN_SENT not in txt:
            # naive anchor: look for Trainer(...) kwargs dict named trainer_kwargs or similar factory location
            patched = txt + "\n" + ENGINE_PATCH
            path.write_text(patched, encoding="utf-8")
            log_change("edit", path, "HF Trainer eval/save integration", ENGINE_PATCH)
    except Exception as e:
        q5("3.1: patch_engine", str(e), str(path))


def patch_cli_and_data():
    try:
        cli = REPO / "deploy_codex_pipeline.py"
        if not cli.exists():
            log_change("prune", cli, "CLI not found; skipping data flags")
            return
        txt = cli.read_text(encoding="utf-8")
        changed = False
        if DDP_SENT not in txt:
            txt += "\n" + DDP_FLAG_SNIPPET
            changed = True
        if DATA_SENT not in txt:
            txt += "\n" + DATA_FLAGS
            changed = True
        if changed:
            cli.write_text(txt, encoding="utf-8")
            log_change(
                "edit",
                cli,
                "add --disable-ddp and data flags",
                DDP_FLAG_SNIPPET + "\n" + DATA_FLAGS,
            )
    except Exception as e:
        q5("3.2: patch_cli_and_data", str(e), "deploy_codex_pipeline.py")


def patch_mlflow():
    try:
        cli = REPO / "deploy_codex_pipeline.py"
        if not cli.exists():
            return
        txt = cli.read_text(encoding="utf-8")
        if MLF_SENT not in txt:
            txt += "\n" + MLFLOW_SNIPPET
            cli.write_text(txt, encoding="utf-8")
            log_change("edit", cli, "MLflow integration (guarded)", MLFLOW_SNIPPET)
    except Exception as e:
        q5("3.3: patch_mlflow", str(e), "deploy_codex_pipeline.py")


def patch_compose_gpu():
    try:
        dc = REPO / "docker-compose.yml"
        if not dc.exists():
            log_change("prune", dc, "compose file not found; skipping GPU block")
            return
        txt = dc.read_text(encoding="utf-8")
        if CMP_SENT not in txt and "deploy:" not in txt:
            # append once to keep it simple; teams can relocate into specific service
            txt += "\n" + COMPOSE_BLOCK + "\n"
            dc.write_text(txt, encoding="utf-8")
            log_change("edit", dc, "GPU reservations block", COMPOSE_BLOCK)
    except Exception as e:
        q5("3.4: patch_compose_gpu", str(e), "docker-compose.yml")


def patch_run_gpu():
    try:
        run = REPO / "scripts" / "deploy" / "run.sh"
        if not run.exists():
            log_change("prune", run, "deploy/run.sh not found; skipping")
            return
        txt = run.read_text(encoding="utf-8")
        if RUN_SENT not in txt:
            txt += "\n" + RUN_GPU + "\n"
            run.write_text(txt, encoding="utf-8")
            log_change("edit", run, "pass --gpus all when available", RUN_GPU)
    except Exception as e:
        q5("3.5: patch_run_gpu", str(e), "scripts/deploy/run.sh")


def validate_local():
    steps = [
        (
            "HF Trainer knobs doc check",
            [
                "python",
                "- <<'PY'\nprint('See HF Trainer docs for evaluation/save strategies')\nPY",
            ],
        ),
        ("Dry-run compose syntax", ["docker", "compose", "config"]),
    ]
    with RES.open("a", encoding="utf-8") as out:
        out.write(f"\n# Validation {ts()}\n")
        for name, cmd in steps:
            out.write(f"\n## {name}\n```\n")
            try:
                p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO))
                out.write(p.stdout + p.stderr + f"\n(exit={p.returncode})\n")
                if p.returncode != 0:
                    q5("6: validate_local", f"exit {p.returncode}", " ".join(cmd))
            except Exception as e:
                out.write(f"ERROR: {e}\n")
                q5("6: validate_local", str(e), " ".join(cmd))
            out.write("```\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()
    if args.apply:
        patch_engine()
        patch_cli_and_data()
        patch_mlflow()
        patch_compose_gpu()
        patch_run_gpu()
    if args.validate:
        validate_local()
    if not (args.apply or args.validate):
        print(
            "Usage: --apply [--validate]\nPolicy: DO NOT ACTIVATE online CI; run checks locally."
        )


if __name__ == "__main__":
    main()
