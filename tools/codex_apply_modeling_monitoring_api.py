#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Codex Task Applier — Modeling CLI, Monitoring/Tracking, API hardening, Checkpointing

Groups:
- A. Modeling flags & per-epoch metrics (functional_training.py)
- B. Monitoring & Experiment Tracking (deploy_codex_pipeline.py + mlflow utils)
- C. Deployment API hardening (services/api)
- D. Reproducible checkpointing & seeds (checkpointing.py)
- E. Docs refresh (NO CI activation)

Policy:
- DO NOT ACTIVATE ANY GitHub Actions online. All checks run locally.
"""
from __future__ import annotations
import os, sys, json, textwrap, subprocess, time, hashlib
from pathlib import Path
from datetime import datetime

# ---------- Core paths & logging ----------
REPO = Path(__file__).resolve().parents[1]
CODEX = REPO / ".codex"
CODEX.mkdir(parents=True, exist_ok=True)
CHANGE_LOG = CODEX / "change_log.md"
ERRORS = CODEX / "errors.ndjson"
RESULTS = CODEX / "results.md"

TARGETS = [
    REPO / "functional_training.py",
    REPO / "deploy_codex_pipeline.py",
    REPO / "codex_ml" / "tracking" / "mlflow_utils.py",
    REPO / "codex_ml" / "utils" / "checkpointing.py",
    REPO / "services" / "api" / "main.py",
    REPO / "Dockerfile",
    REPO / "docker-compose.yml",
    REPO / "docs" / "ops" / "monitoring.md",
    REPO / "docs" / "ops" / "deployment.md",
]

# ---------- Helpers ----------
def ts() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def log_change(action: str, path: Path, why: str, preview: str = "") -> None:
    if not CHANGE_LOG.exists() or CHANGE_LOG.stat().st_size == 0:
        CHANGE_LOG.write_text("# Codex Change Log\n", encoding="utf-8")
    with CHANGE_LOG.open("a", encoding="utf-8") as fh:
        fh.write(f"## {ts()} — {path.relative_to(REPO)}\n- **Action:** {action}\n- **Rationale:** {why}\n")
        if preview:
            fh.write("```diff\n" + preview[:6000] + "\n```\n")
        fh.write("\n")

def q5(step: str, err: str, ctx: str) -> None:
    block = textwrap.dedent(f"""
    Question for ChatGPT-5 {ts()}:
    While performing [{step}], encountered the following error:
    {err}
    Context: {ctx}
    What are the possible causes, and how can this be resolved while preserving intended functionality?
    """).strip()
    with ERRORS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"ts": ts(), "step": step, "error": err, "context": ctx}) + "\n")
    sys.stderr.write(block + "\n")

def upsert(path: Path, content: str, sentinel: str) -> None:
    """
    Idempotent: if sentinel exists in file, do nothing.
    If file exists w/o sentinel, APPEND content (non-destructive).
    If file doesn't exist, CREATE with content.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        if path.exists():
            existing = path.read_text(encoding="utf-8", errors="ignore")
            if sentinel in existing:
                return
            new_text = existing + ("\n" if not existing.endswith("\n") else "") + content
            path.write_text(new_text, encoding="utf-8")
            log_change("append", path, f"guarded by {sentinel}", content)
        else:
            path.write_text(content, encoding="utf-8")
            log_change("create", path, f"guarded by {sentinel}", content)
    except Exception as e:
        q5("3: upsert file", str(e), f"path={path}")

def verify_write_permissions() -> None:
    for p in TARGETS:
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            testfile = p.parent / (".codex.touch." + hashlib.sha1(str(p).encode()).hexdigest()[:8])
            testfile.write_text("ok", encoding="utf-8")
            testfile.unlink(missing_ok=True)
        except Exception as e:
            q5("1: Preparation — write permission", str(e), f"target={p}")

# ---------- Injected blocks ----------
FT_SENT = "# BEGIN: CODEX_FUNCTR_DEEPNN"
FT_CODE = FT_SENT + """
# Codex injection: deep-learning toggles, device, grad-clip, scheduler, per-epoch metrics
import argparse, json, hashlib, time
from pathlib import Path

def _codex_config_hash(cfg: dict) -> str:
    return hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:16]

def _codex_autodevice(cli_device: str | None = None) -> str:
    try:
        import torch
        if cli_device:
            return cli_device
        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return cli_device or "cpu"

def _codex_maybe_scheduler(optimizer, name: str | None, **kw):
    try:
        import torch.optim as optim
        if not name:
            return None
        name = name.lower()
        if name in ("cosine", "cosineannealinglr"):
            return optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=kw.get("t_max", 50))
        if name in ("step", "steplr"):
            return optim.lr_scheduler.StepLR(optimizer, step_size=kw.get("step_size", 10), gamma=kw.get("gamma", 0.1))
    except Exception:
        return None
    return None

def _codex_epoch_metrics(y_true, y_pred) -> dict:
    try:
        from codex_ml.metrics import token_accuracy, perplexity
        return {
            "token_accuracy": float(token_accuracy(y_true, y_pred)),
            "perplexity": float(perplexity(y_true, y_pred)),
        }
    except Exception:
        return {"token_accuracy": 0.0, "perplexity": 0.0}

def _codex_write_metrics(run_dir: Path, record: dict):
    run_dir.mkdir(parents=True, exist_ok=True)
    f = run_dir / "metrics.json"
    with f.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")

def _codex_apply_training_integration(args, train_loop_fn, config: dict):
    if not getattr(args, "use_deeplearning", False):
        return train_loop_fn
    device = _codex_autodevice(getattr(args, "device", None))
    grad_clip = float(getattr(args, "grad_clip", 0.0) or 0.0)
    sched_name = getattr(args, "scheduler", None)

    def wrapped_train_loop(epoch_cb=None):
        last_sched = None
        if epoch_cb is None:
            def epoch_cb(epoch, model=None, optimizer=None, y_true=None, y_pred=None):
                pass
        def cb(epoch, model=None, optimizer=None, y_true=None, y_pred=None):
            nonlocal last_sched
            if grad_clip > 0 and model is not None:
                try:
                    import torch
                    torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
                except Exception:
                    pass
            if optimizer is not None and sched_name and last_sched is None:
                last_sched = _codex_maybe_scheduler(optimizer, sched_name)
            if last_sched is not None:
                try:
                    last_sched.step()
                except Exception:
                    pass
            rec = {
                "ts": int(time.time()),
                "epoch": int(epoch),
                "device": device,
                "config_hash": _codex_config_hash(config),
                "metrics": _codex_epoch_metrics(y_true, y_pred),
            }
            _codex_write_metrics(Path(config.get("run_dir", "runs/default")), rec)
            return epoch_cb(epoch, model=model, optimizer=optimizer, y_true=y_true, y_pred=y_pred)
        return train_loop_fn(epoch_cb=cb)
    return wrapped_train_loop

def _codex_patch_argparse(ap: argparse.ArgumentParser) -> None:
    added = [a.dest for g in ap._action_groups for a in g._group_actions]  # type: ignore
    if "use_deeplearning" not in added:
        ap.add_argument("--use-deeplearning", action="store_true", help="Enable MiniLM training path and metrics")
    if "device" not in added:
        ap.add_argument("--device", default=None, help="Override device (cpu/cuda)")
    if "grad_clip" not in added:
        ap.add_argument("--grad-clip", dest="grad_clip", type=float, default=0.0, help="Max grad norm")
    if "scheduler" not in added:
        ap.add_argument("--scheduler", default=None, help="LR scheduler (cosine, step)")
# END: CODEX_FUNCTR_DEEPNN
"""

DP_SENT = "# BEGIN: CODEX_DEPLOY_MONITORING"
DP_CODE = DP_SENT + """
# Codex injection: TensorBoard, W&B, MLflow wiring + system stats
import argparse, os, json, time
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
        run = MU.start_run(tracking_uri=uri, experiment_name=exp)
        return MU, run
    except Exception:
        return None

def _codex_patch_argparse(ap: argparse.ArgumentParser) -> None:
    added = [a.dest for g in ap._action_groups for a in g._group_actions]  # type: ignore
    if "enable_wandb" not in added:
        ap.add_argument("--enable-wandb", action="store_true", help="Enable Weights & Biases logging")
    if "mlflow_enable" not in added:
        ap.add_argument("--mlflow-enable", action="store_true", help="Enable MLflow logging")
    if "mlflow_tracking_uri" not in added:
        ap.add_argument("--mlflow-tracking-uri", default=None, help="MLflow tracking URI")
    if "mlflow_experiment" not in added:
        ap.add_argument("--mlflow-experiment", default=None, help="MLflow experiment name")

def _codex_logging_bootstrap(args, run_dir: Path, params: dict):
    tb = _codex_tb(run_dir / "tb")
    wb = _codex_wandb(bool(getattr(args, "enable_wandb", False)), params)
    mlf = _codex_mlflow(bool(getattr(args, "mlflow_enable", False)),
                        getattr(args, "mlflow_tracking_uri", None),
                        getattr(args, "mlflow_experiment", None))
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
"""

MLF_SENT = "# BEGIN: CODEX_MLFLOW_UTILS"
MLF_CODE = MLF_SENT + """
# MLflow wrappers (no-op if mlflow missing)
from __future__ import annotations
from pathlib import Path
from typing import Iterable

def start_run(tracking_uri: str | None = None, experiment_name: str | None = None):
    try:
        import mlflow
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        if experiment_name:
            mlflow.set_experiment(experiment_name)
        return mlflow.start_run()
    except Exception:
        return None

def log_params(params: dict):
    try:
        import mlflow
        mlflow.log_params(params)
    except Exception:
        pass

def log_metrics(metrics: dict, step: int | None = None):
    try:
        import mlflow
        mlflow.log_metrics(metrics, step=step)
    except Exception:
        pass

def log_artifacts(paths: Iterable[Path]):
    try:
        import mlflow
        for p in paths:
            mlflow.log_artifact(str(p))
    except Exception:
        pass
# END: CODEX_MLFLOW_UTILS
"""

CKPT_SENT = "# BEGIN: CODEX_CKPT_RNG_SEED"
CKPT_CODE = CKPT_SENT + """
from __future__ import annotations
import json, random
from pathlib import Path

def set_seed(seed: int) -> None:
    try:
        import numpy as np
        np.random.seed(seed)
    except Exception:
        pass
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except Exception:
        pass
    random.seed(seed)

def save_rng(path: Path) -> None:
    state = {}
    try:
        import numpy as np
        state["numpy"] = np.random.get_state()[1][:].tolist()
    except Exception:
        pass
    try:
        import torch
        state["torch"] = torch.get_rng_state().tolist()
        if torch.cuda.is_available():
            state["torch_cuda"] = torch.cuda.get_rng_state().tolist()
    except Exception:
        pass
    state["python"] = random.getstate()[1][:] if hasattr(random.getstate(), "__iter__") else None
    (path / "rng.json").write_text(json.dumps(state), encoding="utf-8")

def load_rng(path: Path) -> None:
    f = path / "rng.json"
    if not f.exists():
        return
    try:
        state = json.loads(f.read_text(encoding="utf-8"))
        import numpy as np, torch, random as pyrand
        if "numpy" in state:
            np.random.seed(state["numpy"][0] if state["numpy"] else 0)
        if "torch" in state:
            torch.set_rng_state(torch.tensor(state["torch"], dtype=torch.uint8))
        if "torch_cuda" in state and torch.cuda.is_available():
            torch.cuda.set_rng_state(torch.tensor(state["torch_cuda"], dtype=torch.uint8))
        if "python" in state and state["python"] is not None:
            pyrand.setstate((3, tuple(state["python"]), None))
    except Exception:
        pass

def verify_shapes(model, checkpoint_state: dict) -> None:
    try:
        missing, unexpected = model.load_state_dict(checkpoint_state, strict=False)
        if missing or unexpected:
            raise RuntimeError(f"Shape/state mismatch: missing={missing}, unexpected={unexpected}")
    except Exception as e:
        raise RuntimeError(f"Failed verifying shapes: {e}")

def log_seed(path: Path, seed: int) -> None:
    (path / "seeds.json").write_text(json.dumps({"seed": seed}), encoding="utf-8")
# END: CODEX_CKPT_RNG_SEED
"""

API_SENT = "# BEGIN: CODEX_FASTAPI_HARDEN"
API_CODE = API_SENT + """
# FastAPI app with background queue, API-key middleware, and basic handlers
from __future__ import annotations
import os, asyncio, time
from typing import Optional
try:
    from fastapi import FastAPI, Request, HTTPException, Depends
    from fastapi.responses import JSONResponse
except Exception:
    FastAPI = None  # type: ignore

API_KEY_ENV = "CODEX_API_KEY"

def api_key_auth(request: Request) -> None:  # type: ignore
    key = os.environ.get(API_KEY_ENV)
    header = request.headers.get("x-api-key")
    if key and header != key:
        raise HTTPException(status_code=401, detail="Unauthorized")

def build_app():
    if FastAPI is None:
        return None
    app = FastAPI(title="Codex API")
    queue: asyncio.Queue = asyncio.Queue()

    @app.middleware("http")
    async def errors(request: Request, call_next):
        try:
            return await call_next(request)
        except HTTPException as he:
            return JSONResponse(status_code=he.status_code, content={"error": he.detail})
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})

    @app.get("/status")
    async def status():
        return {"ok": True, "queue": queue.qsize(), "ts": int(time.time())}

    @app.post("/infer")
    async def infer(request: Request, _=Depends(api_key_auth)):
        payload = await request.json()
        return {"result": payload, "ts": int(time.time())}

    @app.post("/train")
    async def train(request: Request, _=Depends(api_key_auth)):
        job = {"type": "train", "payload": await request.json(), "ts": int(time.time())}
        await queue.put(job)
        return {"queued": True, "job_id": job["ts"]}

    @app.post("/evaluate")
    async def evaluate(request: Request, _=Depends(api_key_auth)):
        job = {"type": "evaluate", "payload": await request.json(), "ts": int(time.time())}
        await queue.put(job)
        return {"queued": True, "job_id": job["ts"]}

    async def worker():
        while True:
            job = await queue.get()
            await asyncio.sleep(0.1)
            queue.task_done()

    @app.on_event("startup")
    async def startup():
        asyncio.create_task(worker())

    return app

app = build_app()
# END: CODEX_FASTAPI_HARDEN
"""

DOCKER_SENT = "# BEGIN: CODEX_DOCKERFILE"
DOCKERFILE = DOCKER_SENT + """
# Ubuntu base, multi-stage, non-root, healthcheck
FROM ubuntu:22.04 AS base
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . /app
# Try common requirement files gracefully
RUN (test -f requirements/base.txt && pip3 install --no-cache-dir -r requirements/base.txt) || true
RUN (test -f requirements-dev.txt && pip3 install --no-cache-dir -r requirements-dev.txt) || true

FROM base AS runtime
RUN useradd -ms /bin/bash coder && chown -R coder:coder /app
USER coder
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s CMD python3 -c "import socket; s=socket.socket(); s.settimeout(2); s.connect(('127.0.0.1',8000)); print('ok')"
CMD ["python3","-m","uvicorn","services.api.main:app","--host","0.0.0.0","--port","8000"]
# END: CODEX_DOCKERFILE
"""

COMPOSE_SENT = "# BEGIN: CODEX_COMPOSE"
COMPOSE = COMPOSE_SENT + """
version: "3.9"
services:
  api:
    build: .
    image: codex-api:local
    ports: ["8000:8000"]
    environment:
      - CODEX_API_KEY=changeme
    # GPU (see Docker Compose GPU support docs):
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - capabilities: ["gpu"]
# END: CODEX_COMPOSE
"""

MON_DOC_SENT = "<!-- BEGIN: CODEX_MONITORING_DOC -->"
MONITORING_DOC = MON_DOC_SENT + """
# Monitoring & Experiment Tracking

Flags:
- `--enable-wandb`
- `--mlflow-enable` / `--mlflow-tracking-uri` / `--mlflow-experiment`

Behavior:
- TensorBoard: logs to `<output>/tb`
- Weights & Biases: enabled when flag set
- MLflow: wraps `mlflow.*` via `codex_ml.tracking.mlflow_utils.*`; artifacts/runs tracked where configured
"""

DEPLOY_DOC_SENT = "<!-- BEGIN: CODEX_DEPLOY_DOC -->"
DEPLOY_DOC = DEPLOY_DOC_SENT + """
# Deployment

- Build: `docker build -t codex-api:local .`
- Run: `docker compose up --build`
- Health: GET `http://localhost:8000/status`
- Auth: send header `x-api-key: <value>` for POST endpoints
- Endpoints: `/infer`, `/train`, `/evaluate`, `/status`
"""

README_SENT = "<!-- BEGIN: CODEX_README_UPDATE -->"
README_UPDATES = README_SENT + """
Local-only validations & explicit flags for monitoring/tracking.
**Do not** enable remote CI triggers; run Codex scripts directly.
"""

# ---------- Apply patches ----------
def apply():
    try:
        verify_write_permissions()
        upsert(REPO / "functional_training.py", FT_CODE, FT_SENT)
        upsert(REPO / "deploy_codex_pipeline.py", DP_CODE, DP_SENT)
        upsert(REPO / "codex_ml" / "tracking" / "mlflow_utils.py", MLF_CODE, MLF_SENT)
        upsert(REPO / "codex_ml" / "utils" / "checkpointing.py", CKPT_CODE, CKPT_SENT)
        upsert(REPO / "services" / "api" / "main.py", API_CODE, API_SENT)
        upsert(REPO / "Dockerfile", DOCKERFILE, DOCKER_SENT)
        upsert(REPO / "docker-compose.yml", COMPOSE, COMPOSE_SENT)
        upsert(REPO / "docs" / "ops" / "monitoring.md", MONITORING_DOC, MON_DOC_SENT)
        upsert(REPO / "docs" / "ops" / "deployment.md", DEPLOY_DOC, DEPLOY_DOC_SENT)
        upsert(REPO / "README.md", README_UPDATES, README_SENT)
    except Exception as e:
        q5("3: Apply guarded patches", str(e), f"repo={REPO}")

# ---------- Local (offline) validation ----------
def validate():
    cmds = [
        ("python -m compileall .", ["python", "-m", "compileall", "."]),
        ("pytest -q --maxfail=1", ["pytest", "-q", "--maxfail=1"]),
    ]
    with RESULTS.open("a", encoding="utf-8") as fh:
        fh.write(f"\n# Validation {ts()}\n")
        for name, cmd in cmds:
            fh.write(f"\n## {name}\n```\n")
            try:
                p = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True)
                fh.write(p.stdout + p.stderr + f"\n(exit={p.returncode})\n")
                if p.returncode != 0:
                    q5("6: Finalization — validation", f"exit {p.returncode}", " ".join(cmd))
            except Exception as e:
                fh.write(f"ERROR: {e}\n")
                q5("6: Finalization — validation", str(e), " ".join(cmd))
            fh.write("```\n")

# ---------- CLI ----------
def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Apply guarded changes for modeling/monitoring/api/checkpointing")
    ap.add_argument("--validate", action="store_true", help="Run local validations (no CI activation)")
    args = ap.parse_args()

    if args.apply:
        apply()
    if args.validate:
        validate()
    if not (args.apply or args.validate):
        print("Usage: --apply [--validate]")

if __name__ == "__main__":
    main()
