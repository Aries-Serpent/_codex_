# metrics/collector.py
# Lightweight metrics collector for ChatGPT-Codex sandbox runs.
# - Computes repo/state metrics (S, rho_dev, K_arch, Lambda_auto)
# - Logs to SQLite (CODEX_LOG_DB_PATH) keyed by CODEX_SESSION_ID
# - Optionally logs to MLflow if MLFLOW_TRACKING_URI is set
# - Emits JSON logs to stdout; optionally opens a short OpenTelemetry span if available
#
# Usage:
#   python -m metrics.collector --root . --artifacts $ARTIFACTS_DIR
#
# Environment (consumed if present):
#   CODEX_SESSION_ID, CODEX_LOG_DB_PATH, ARTIFACTS_DIR, CODEX_OFFLINE, CODEX_FORCE_CPU,
#   GITHUB_SHA, GITHUB_REF_NAME, CI, MLFLOW_TRACKING_URI
#
# This module avoids non-stdlib deps; MLflow/OTel are optional.

from __future__ import annotations

import argparse
import ast
import collections
import datetime as dt
import json
import logging
import math
import os
import platform
import sqlite3
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Set, Tuple


# ---------- logging (JSON) ----------
class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "ts": dt.datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "msg": record.getMessage(),
            "logger": record.name,
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info:
            payload["stack"] = record.stack_info
        return json.dumps(payload)


logger = logging.getLogger("codex.metrics.collector")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
logger.setLevel(logging.INFO)
logger.addHandler(handler)


# ---------- optional MLflow ----------
def _try_mlflow():
    try:
        import mlflow  # type: ignore

        return mlflow
    except Exception:
        return None


# ---------- optional OpenTelemetry (trace-only, best-effort) ----------
def _otel_span(name: str):
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider

        # Exporter is configured via env (e.g., OTEL_EXPORTER_OTLP_ENDPOINT); if none configured,
        # span still helps if an auto-instrumentation agent is present.
        prov = TracerProvider()
        trace.set_tracer_provider(prov)
        tracer = trace.get_tracer("codex.metrics")
        return tracer.start_as_current_span(name)
    except Exception:
        # no-op context manager
        class _Null:
            def __enter__(self):
                return None

            def __exit__(self, *exc):
                return False

        return _Null()


# ---------- data classes ----------
@dataclass
class RunInfo:
    session_id: str
    ts: float
    branch: str
    commit: str
    python: str
    ci: str
    offline: int
    force_cpu: int


@dataclass
class Snapshot:
    src_loc: int
    tests_loc: int
    test_density: float
    modules: int
    import_edges: int
    scc_cycles: int
    cycle_nodes: int
    curvature_proxy: float
    lambda_auto_index: float
    rho_dev_proxy: float
    S_proxy: int


# ---------- repo scan helpers ----------


def _count_loc(p: Path) -> int:
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return 0
    return sum(
        1
        for line in txt.splitlines()
        if line.strip() and not line.strip().startswith(("#", ";", "//"))
    )


def _scan_repo(root: Path) -> Tuple[Snapshot, Dict[str, int]]:
    src = root / "src"
    tests = root / "tests"
    py_files = list(src.rglob("*.py")) if src.exists() else []
    test_files = list(tests.rglob("test_*.py")) if tests.exists() else []

    src_loc = sum(_count_loc(f) for f in py_files)
    tests_loc = sum(_count_loc(f) for f in test_files)
    test_density = (tests_loc / src_loc) if src_loc else 0.0

    # module map
    module_map = {}
    for f in py_files:
        rel = f.relative_to(src)
        mod = ".".join(rel.with_suffix("").parts)
        module_map[f] = mod

    # import graph (internal)
    nodes: Set[str] = set(module_map.values())
    graph = collections.defaultdict(set)  # mod -> {dep_mod}
    for f, mod in module_map.items():
        try:
            tree = ast.parse(f.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    name = n.name
                    # heuristic: any dotted import that could map inward
                    cand = name
                    while cand and cand not in nodes and "." in cand:
                        cand = cand.rsplit(".", 1)[0]
                    if cand in nodes:
                        graph[mod].add(cand)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    cand = node.module
                    while cand and cand not in nodes and "." in cand:
                        cand = cand.rsplit(".", 1)[0]
                    if cand in nodes:
                        graph[mod].add(cand)

    adj = {n: set() for n in nodes}
    for src_mod, deps in graph.items():
        for dep_mod in deps:
            if dep_mod in nodes:
                adj[src_mod].add(dep_mod)

    edges = sum(len(v) for v in adj.values())

    # Tarjan SCC
    sys.setrecursionlimit(1000000)
    index = 0
    indices = {}
    lowlink = {}
    stack = []
    onstack = set()
    sccs = []

    def strongconnect(v):
        nonlocal index
        indices[v] = index
        lowlink[v] = index
        index += 1
        stack.append(v)
        onstack.add(v)
        for w in adj.get(v, ()):
            if w not in indices:
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif w in onstack:
                lowlink[v] = min(lowlink[v], indices[w])
        if lowlink[v] == indices[v]:
            comp = []
            while True:
                w = stack.pop()
                onstack.remove(w)
                comp.append(w)
                if w == v:
                    break
            sccs.append(comp)

    for v in nodes:
        if v not in indices:
            strongconnect(v)

    cycles = [component for component in sccs if len(component) > 1]
    cyc_nodes = {node for component in cycles for node in component}
    cyc_edges = 0
    for u in cyc_nodes:
        for v in adj[u]:
            if v in cyc_nodes:
                cyc_edges += 1
    curvature_proxy = (cyc_edges / edges) if edges else 0.0

    # automation index (7-point heuristic)
    parts = 0
    if (root / ".github/workflows").exists():
        parts += 1
    if (root / "tox.ini").exists():
        parts += 1
    if (root / "noxfile.py").exists():
        parts += 1
    if (root / ".pre-commit-config.yaml").exists():
        parts += 1
    if (
        (root / "requirements.lock").exists()
        or (root / "uv.lock").exists()
        or (root / "poetry.lock").exists()
    ):
        parts += 1
    if tests.exists() and test_files:
        parts += 1
    # coverage gate heuristic (string search, cheap)
    cov_gate = False
    tox_path = root / "tox.ini"
    if tox_path.exists():
        try:
            txt = tox_path.read_text(encoding="utf-8", errors="ignore")
            cov_gate = "COV_FAIL_UNDER" in txt or "--cov-fail-under" in txt
        except Exception:
            pass
    if cov_gate:
        parts += 1

    lambda_auto_index = parts / 7.0

    modules = len(nodes)
    S_proxy = len(test_files)
    rho_dev_proxy = ((src_loc / modules) * test_density) if modules else 0.0

    # test areas from file names (very light)
    from collections import Counter

    cats = Counter()
    for f in test_files:
        name = f.name.lower()
        if "api" in name:
            cats["api"] += 1
        if "cli" in name:
            cats["cli"] += 1
        if any(word in name for word in ("infer", "train", "lora")):
            cats["ml"] += 1
        if any(word in name for word in ("safety", "guard")):
            cats["safety"] += 1
        if "token" in name:
            cats["tokenization"] += 1
        if any(word in name for word in ("db", "sqlite")):
            cats["db"] += 1

    return Snapshot(
        src_loc=src_loc,
        tests_loc=tests_loc,
        test_density=test_density,
        modules=modules,
        import_edges=edges,
        scc_cycles=len(cycles),
        cycle_nodes=len(cyc_nodes),
        curvature_proxy=curvature_proxy,
        lambda_auto_index=lambda_auto_index,
        rho_dev_proxy=rho_dev_proxy,
        S_proxy=S_proxy,
    ), dict(cats)


# ---------- SQLite persistence ----------
def _ensure_db(db: Path):
    db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db) as con:
        cur = con.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS codex_runs (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              session_id TEXT,
              ts REAL,
              branch TEXT,
              commit TEXT,
              python TEXT,
              ci TEXT,
              offline INTEGER,
              force_cpu INTEGER
            )
        """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS codex_metrics (
              run_id INTEGER,
              key TEXT,
              value REAL,
              FOREIGN KEY(run_id) REFERENCES codex_runs(id)
            )
        """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_runs_session_ts ON codex_runs(session_id, ts)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_metrics_run ON codex_metrics(run_id)")
        con.commit()


def _insert_run(db: Path, run: RunInfo) -> int:
    with sqlite3.connect(db) as con:
        cur = con.cursor()
        cur.execute(
            """INSERT INTO codex_runs(session_id, ts, branch, commit, python, ci, offline, force_cpu)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                run.session_id,
                run.ts,
                run.branch,
                run.commit,
                run.python,
                run.ci,
                run.offline,
                run.force_cpu,
            ),
        )
        run_id = cur.lastrowid
        con.commit()
        return run_id


def _insert_metrics(db: Path, run_id: int, metrics: Dict[str, float]):
    rows = [(run_id, k, float(v)) for k, v in metrics.items()]
    with sqlite3.connect(db) as con:
        con.executemany("INSERT INTO codex_metrics(run_id, key, value) VALUES (?, ?, ?)", rows)
        con.commit()


def _get_prev_S(db: Path, session_id: str) -> Tuple[float, float] | None:
    # returns (ts, S) of the most recent prior run in same session
    with sqlite3.connect(db) as con:
        cur = con.cursor()
        cur.execute(
            """
            SELECT r.ts, m.value
            FROM codex_runs r
            JOIN codex_metrics m ON m.run_id = r.id
            WHERE r.session_id = ? AND m.key = 'S_proxy'
            ORDER BY r.ts DESC LIMIT 1
        """,
            (session_id,),
        )
        row = cur.fetchone()
        if row:
            return float(row[0]), float(row[1])
        return None


# ---------- main ----------
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--artifacts", type=Path, default=Path(os.getenv("ARTIFACTS_DIR", "artifacts")))
    args = ap.parse_args(argv)

    session_id = os.getenv("CODEX_SESSION_ID") or f"local-{int(time.time())}"
    db_path = Path(os.getenv("CODEX_LOG_DB_PATH", "codex_metrics.db"))
    branch = os.getenv("GITHUB_REF_NAME", os.getenv("BRANCH_NAME", "local"))
    commit = os.getenv("GITHUB_SHA", os.getenv("COMMIT_SHA", "local"))
    ci = os.getenv("CI", "false")
    offline = 1 if os.getenv("CODEX_OFFLINE", "0") == "1" else 0
    force_cpu = 1 if os.getenv("CODEX_FORCE_CPU", "0") == "1" else 0

    run = RunInfo(
        session_id=session_id,
        ts=time.time(),
        branch=branch,
        commit=commit,
        python=platform.python_version(),
        ci=ci,
        offline=offline,
        force_cpu=force_cpu,
    )

    with _otel_span("codex.metrics.collector"):
        snap, cats = _scan_repo(args.root)
        _ensure_db(db_path)
        run_id = _insert_run(db_path, run)

        # Friedmann-like terms
        metrics = {
            "S_proxy": snap.S_proxy,
            "rho_dev_proxy": snap.rho_dev_proxy,
            "K_arch": snap.curvature_proxy,
            "Lambda_auto": snap.lambda_auto_index,
            "src_loc": snap.src_loc,
            "tests_loc": snap.tests_loc,
            "test_density": snap.test_density,
            "modules": snap.modules,
            "import_edges": snap.import_edges,
            "scc_cycles": snap.scc_cycles,
            "cycle_nodes": snap.cycle_nodes,
        }

        # compute H = d ln S / dt from previous run in same session
        prev = _get_prev_S(db_path, session_id)
        if prev and snap.S_proxy > 0 and prev[1] > 0:
            dt_sec = max(1.0, run.ts - prev[0])
            H = (math.log(snap.S_proxy) - math.log(prev[1])) / dt_sec
        else:
            H = 0.0
        metrics["H_proxy"] = H

        _insert_metrics(db_path, run_id, metrics)

        # Optionally log to MLflow
        mlflow = _try_mlflow()
        if mlflow and os.getenv("MLFLOW_TRACKING_URI"):
            try:
                from codex_ml.tracking.mlflow_guard import bootstrap_offline_tracking

                env_uri = os.getenv("MLFLOW_TRACKING_URI", "")
                os.environ.setdefault("CODEX_MLFLOW_LOCAL_DIR", str(args.artifacts / "mlruns"))
                Path(os.environ["CODEX_MLFLOW_LOCAL_DIR"]).mkdir(parents=True, exist_ok=True)
                force_local = not env_uri or not (
                    env_uri.startswith("file:")
                    or env_uri.startswith("/")
                    or env_uri.startswith(".")
                )
                local_uri = bootstrap_offline_tracking(force=force_local) or env_uri
                mlflow.set_tracking_uri(local_uri)
            except Exception as exc:
                logger.warning("Skipping MLflow logging; failed to enforce local backend: %s", exc)
            else:
                with mlflow.start_run(run_name=session_id):
                    mlflow.log_params(
                        {
                            "branch": branch,
                            "commit": commit,
                            "python": run.python,
                            "ci": ci,
                            "offline": offline,
                            "force_cpu": force_cpu,
                        }
                    )
                    mlflow.log_metrics(metrics)

        # Persist a compact JSON snapshot into artifacts
        args.artifacts.mkdir(parents=True, exist_ok=True)
        out = args.artifacts / f"metrics_{session_id}_{int(run.ts)}.json"
        with out.open("w", encoding="utf-8") as f:
            json.dump(
                {
                    "run": asdict(run),
                    "snapshot": asdict(snap),
                    "categories": cats,
                    "metrics": metrics,
                },
                f,
                indent=2,
            )

        logger.info(
            f"metrics_collector_completed session={session_id} run_id={run_id} db={str(db_path)} out={str(out)}"
        )


if __name__ == "__main__":
    main()
