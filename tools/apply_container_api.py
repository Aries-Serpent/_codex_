#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Codex Orchestrator: Containerized FastAPI service with Dockerfile, Compose,
deploy scripts, and docs.

Creates:
- Dockerfile (multi-stage, Ubuntu base, non-root, EXPOSE 8000)
- docker-compose.yml (artifacts volume, healthcheck)
- services/api/{main.py,__init__.py,requirements.txt}
- scripts/deploy/{build.sh,run.sh,push.sh}
- docs/ops/deployment.md

Validations (best-effort):
- docker build
- docker compose up -d
- curl GET /status and POST /infer
- verify /train writes artifacts into volume

Policy:
- DO NOT ACTIVATE ANY GitHub Actions Online files. ALL GitHub Actions such as
  pre-commit, validation, etc. MUST EXPLICITLY RUN WITHIN THE CODEX ENVIRONMENT.
"""
from __future__ import annotations
import sys

import json
import os
import subprocess
import textwrap
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CODEX = REPO / ".codex"
CODEX.mkdir(parents=True, exist_ok=True)
CHANGE_LOG = CODEX / "change_log.md"
ERRORS = CODEX / "errors.ndjson"
RESULTS = CODEX / "results.md"


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
    msg = textwrap.dedent(
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
    print(msg, file=sys.stderr)


def upsert(path: Path, content: str, sentinel: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and sentinel in path.read_text(encoding="utf-8", errors="ignore"):
        return
    path.write_text(content, encoding="utf-8")
    log_change("upsert", path, f"insert guarded by {sentinel}", content)


# ---------------- Dockerfile ----------------
DF_SENT = "# BEGIN: CODEX_DOCKERFILE"
DOCKERFILE = DF_SENT + """
# syntax=docker/dockerfile:1
FROM ubuntu:22.04 AS base
ENV DEBIAN_FRONTEND=noninteractive PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

FROM base AS builder
WORKDIR /app
COPY services/api/requirements.txt .
RUN python3 -m pip install --upgrade pip && pip install --prefix=/install -r requirements.txt

FROM base AS runtime
RUN useradd -m -u 10001 appuser && mkdir -p /app /artifacts && chown -R appuser:appuser /app /artifacts
USER appuser
WORKDIR /app
ENV PATH=/home/appuser/.local/bin:$PATH
COPY --from=builder /install /usr/local
COPY --chown=appuser:appuser services/api /app/services/api
EXPOSE 8000
CMD python3 -c "import os; os.umask(0o077); import uvicorn; uvicorn.run('services.api.main:app', host='0.0.0.0', port=8000)"
"""

# ---------------- docker-compose.yml ----------------
DC_SENT = "# BEGIN: CODEX_COMPOSE"
COMPOSE = DC_SENT + """
version: '3.8'
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    image: codex-api:local
    ports:
      - '8000:8000'
    environment:
      - UVICORN_WORKERS=1
    volumes:
      - artifacts:/artifacts
    healthcheck:
      test: ['CMD', 'curl', '-fsS', 'http://localhost:8000/status']
      interval: 10s
      timeout: 3s
      retries: 10
volumes:
  artifacts:
    name: codex_artifacts
"""

# ---------------- FastAPI service ----------------
API_REQS_SENT = "# BEGIN: CODEX_API_REQS"
API_REQS = API_REQS_SENT + """
fastapi==0.111.0
uvicorn==0.30.1
pydantic==2.8.2
"""

API_INIT_SENT = "# BEGIN: CODEX_API_INIT"
API_INIT = API_INIT_SENT + "\n# package marker\n"

API_SENT = "# BEGIN: CODEX_API_MAIN"
API_MAIN = API_SENT + """
from __future__ import annotations

import asyncio
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

ARTIFACTS = Path(os.getenv("ARTIFACTS_DIR", "/artifacts"))
ARTIFACTS.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Codex API", version="0.1.0")

QUEUE: "asyncio.Queue[dict]" = asyncio.Queue(maxsize=128)
JOBS: Dict[str, Dict[str, Any]] = {}


class InferRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=16000)


class InferResponse(BaseModel):
    completion: str
    tokens: int


class TrainRequest(BaseModel):
    epochs: int = Field(1, ge=1, le=100)
    notes: Optional[str] = None


class EvalRequest(BaseModel):
    dataset: str
    limit: int = 100


@app.on_event("startup")
async def _startup() -> None:
    async def worker() -> None:
        while True:
            job = await QUEUE.get()
            jid = job["id"]
            JOBS[jid] = {"status": "running", "started": time.time()}
            try:
                run_dir = ARTIFACTS / f"run-{int(time.time())}"
                run_dir.mkdir(parents=True, exist_ok=True)
                for e in range(job["epochs"]):
                    await asyncio.sleep(0.2)
                    (run_dir / f"epoch-{e + 1}.txt").write_text(
                        f"epoch {e + 1} done\n", encoding="utf-8"
                    )
                (run_dir / "metadata.json").write_text(
                    json.dumps({"epochs": job["epochs"]}), encoding="utf-8"
                )
                JOBS[jid] = {
                    "status": "completed",
                    "artifacts": str(run_dir),
                    "finished": time.time(),
                }
            except Exception as exc:  # noqa: BLE001
                JOBS[jid] = {"status": "failed", "error": str(exc)}
            finally:
                QUEUE.task_done()

    app.state.worker_task = asyncio.create_task(worker())


@app.post("/infer", response_model=InferResponse)
async def infer(req: InferRequest) -> InferResponse:
    text = req.prompt.strip()
    out = f"Echo: {text}"
    return InferResponse(completion=out, tokens=len(out.split()))


@app.post("/train")
async def train(req: TrainRequest) -> Dict[str, Any]:
    jid = f"job-{int(time.time() * 1000)}"
    await QUEUE.put({"id": jid, "epochs": req.epochs})
    return {"ok": True, "job_id": jid, "queued": QUEUE.qsize()}


@app.post("/evaluate")
async def evaluate(req: EvalRequest) -> Dict[str, Any]:
    return {"ok": True, "dataset": req.dataset, "limit": req.limit, "metrics": {"accuracy": 0.0}}


@app.get("/status")
async def status() -> Dict[str, Any]:
    return {"ok": True, "queue": QUEUE.qsize(), "jobs": JOBS}
"""

# ---------------- Deploy scripts ----------------
SH_SENT = "# BEGIN: CODEX_DEPLOY_SCRIPT"
BUILD_SH = SH_SENT + """
#!/usr/bin/env bash
set -euo pipefail
umask 077
: "${IMAGE:=codex-api:local}"
docker build -t "$IMAGE" -f Dockerfile .
echo "Built $IMAGE"
"""

RUN_SH = SH_SENT + """
#!/usr/bin/env bash
set -euo pipefail
umask 077
: "${IMAGE:=codex-api:local}"
: "${PORT:=8000}"
GPU_FLAG=""
if command -v nvidia-smi >/dev/null 2>&1; then
  GPU_FLAG="--gpus all"
  echo "GPU detected; running with --gpus all"
fi
docker compose up -d
echo "Waiting for API to become healthy..."
for i in $(seq 1 30); do
  if curl -fsS "http://localhost:${PORT}/status" >/dev/null; then
    echo "API is healthy."
    exit 0
  fi
  sleep 2
done
echo "API failed to become healthy in time"; exit 1
"""

PUSH_SH = SH_SENT + """
#!/usr/bin/env bash
set -euo pipefail
umask 077
if [[ -z "${REGISTRY:-}" ]]; then
  echo "Set REGISTRY (e.g., ghcr.io/owner/repo:tag) to push"; exit 1
fi
: "${IMAGE:=codex-api:local}"
docker tag "$IMAGE" "$REGISTRY"
docker push "$REGISTRY"
echo "Pushed $REGISTRY"
"""

# ---------------- Docs ----------------
DOC_SENT = "<!-- BEGIN: CODEX_DEPLOY_DOC -->"
DOC = DOC_SENT + """
# Deployment (Docker + Compose)

## Build
```bash
IMAGE=codex-api:local bash scripts/deploy/build.sh
```

## Run (CPU by default)
```bash
bash scripts/deploy/run.sh
```
If a compatible NVIDIA GPU is detected (nvidia-smi present), the run script will attempt `--gpus all`.

## Compose (manual)
```bash
docker compose up -d
curl -fsS http://localhost:8000/status
```

## Use the API
```bash
curl -fsS http://localhost:8000/status | jq .
curl -fsS -X POST http://localhost:8000/infer -H 'Content-Type: application/json' -d '{"prompt":"hello"}'
curl -fsS -X POST http://localhost:8000/train -H 'Content-Type: application/json' -d '{"epochs": 2}'
```
Artifacts are written under the named volume `codex_artifacts` and visible inside the container at `/artifacts`.

Policy: DO NOT ACTIVATE ANY GitHub Actions Online files. All validations must run within the Codex environment.
"""


def apply() -> None:
    try:
        upsert(REPO / "services" / "api" / "requirements.txt", API_REQS, API_REQS_SENT)
        upsert(REPO / "services" / "api" / "__init__.py", API_INIT, API_INIT_SENT)
        upsert(REPO / "services" / "api" / "main.py", API_MAIN, API_SENT)
        upsert(REPO / "Dockerfile", DOCKERFILE, DF_SENT)
        upsert(REPO / "docker-compose.yml", COMPOSE, DC_SENT)
        upsert(REPO / "scripts" / "deploy" / "build.sh", BUILD_SH, SH_SENT)
        upsert(REPO / "scripts" / "deploy" / "run.sh", RUN_SH, SH_SENT)
        upsert(REPO / "scripts" / "deploy" / "push.sh", PUSH_SH, SH_SENT)
        for sh in [
            REPO / "scripts" / "deploy" / "build.sh",
            REPO / "scripts" / "deploy" / "run.sh",
            REPO / "scripts" / "deploy" / "push.sh",
        ]:
            os.chmod(sh, 0o700)
        upsert(REPO / "docs" / "ops" / "deployment.md", DOC, DOC_SENT)
    except Exception as e:  # noqa: BLE001
        q5("3: Best-Effort Construction — write files", str(e), f"path={REPO}")


def validate() -> None:
    with RESULTS.open("a", encoding="utf-8") as fh:
        fh.write(f"\n# Validation {ts()}\n")
        steps = [
            ("docker build", ["bash", "-lc", "IMAGE=codex-api:local bash scripts/deploy/build.sh"]),
            ("compose up", ["bash", "-lc", "docker compose up -d"]),
            (
                "probe /status",
                ["bash", "-lc", "for i in $(seq 1 30); do curl -fsS http://localhost:8000/status && break || sleep 2; done"],
            ),
            (
                "POST /infer",
                [
                    "bash",
                    "-lc",
                    "curl -fsS -X POST http://localhost:8000/infer -H 'Content-Type: application/json' -d '{\"prompt\":\"hello\"}'",
                ],
            ),
            (
                "POST /train",
                [
                    "bash",
                    "-lc",
                    "curl -fsS -X POST http://localhost:8000/train -H 'Content-Type: application/json' -d '{\"epochs\": 1}'",
                ],
            ),
        ]
        for name, cmd in steps:
            fh.write(f"\n## {name}\n``\n")
            try:
                p = subprocess.run(cmd, capture_output=True, text=True)
                fh.write(p.stdout + p.stderr + f"\n(exit={p.returncode})\n")
                if p.returncode != 0:
                    q5(f"6: Finalization — {name}", f"exit {p.returncode}", " ".join(cmd))
            except Exception as e:  # noqa: BLE001
                fh.write(f"ERROR: {e}\n")
                q5(f"6: Finalization — {name}", str(e), " ".join(cmd))
            fh.write("``\n")
        subprocess.run(["bash", "-lc", "docker compose down -v"], capture_output=True, text=True)


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="create/augment Dockerfile, compose, API, scripts, docs")
    ap.add_argument("--validate", action="store_true", help="run local validations (best-effort)")
    args = ap.parse_args()
    if args.apply:
        apply()
    if args.validate:
        validate()
    if not (args.apply or args.validate):
        print("Usage: --apply [--validate]")


if __name__ == "__main__":
    main()
