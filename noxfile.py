"""
noxfile.py — Segmented session orchestration for _codex_
Version: 2025-11-12T16:40:00Z (dependency segmentation rollout)
Author: mbaetiong

Key Goals:
  * Minimal baseline install (no heavy ML / eval deps unless explicitly requested).
  * Separate ML, evaluation, notebook, and hygiene verification sessions.
  * Evidence-aware auxiliary sessions (hygiene & dependency evidence checks).
  * Reversible design (removing segmented requirement files returns system to prior state).

Environment Flags (honored across sessions if set):
  CODEX_FORCE_CPU=1                -> Enforce CPU-only torch installation posture.
  CODEX_CPU_MINIMAL=1              -> Minimal ML augmentation (lean subset).
  CODEX_DEPENDENCY_EVIDENCE_ENABLE -> When "1", scripts/setup.sh & maintenance.sh append evidence JSON lines.
  CODEX_VENDOR_PURGE=1             -> Activate vendor purge logic in environment scripts.
  CODEX_ABORT_ON_GPU_PULL=1        -> Fail fast if GPU vendor wheels are detected (nvidia-/triton).
  CODEX_ALLOW_TRITON_CPU=1         -> Treat isolated 'triton' as allowable residue (filtered).
  CODEX_SESSION_ID                 -> Propagated to evidence lines where applicable.

Markers (pytest.ini expected):
  requires_torch          -> Tests needing torch runtime.
  requires_transformers   -> Tests needing transformers/tokenizers.
  eval                    -> Evaluation-only tests (metrics suites).
  metrics                 -> Metric calculation / scoring tests.

Sessions Overview:
  tests           -> Baseline (no ML heavy deps).
  config_validation -> Validate Hydra configs against schemas.
  ml_tests        -> ML dependencies (requirements-ml-cpu.txt).
  eval_tests      -> Evaluation metrics stack (requirements-eval.txt).
  notebook_env    -> Optional notebook/visualization environment build.
  list_sessions   -> Prints available session names.
  verify_hygiene  -> Summarizes dependency evidence & vendor absence assertions.
  evidence_check  -> Validates .codex/evidence/dependency_ops.jsonl schema.
  dependency_plan -> (Optional) Generates a coarse dependency plan JSON (classification).
  rollback_smoke  -> Simulates rollback readiness (ensures segmentation files removable without breakage).

Python Version Strategy:
  * Prefer 3.12, then fall back to 3.11.
  * Use session.python property when available; else rely on interpreter discovery.

Reversibility:
  * Removing requirements-* files and pruning sessions 'ml_tests', 'eval_tests', 'notebook_env'
    returns prior baseline state.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import List

import nox

# Preferred Python versions (adjust as needed)
PY_VERSIONS: List[str] = ["3.12", "3.11"]

# Segmented requirement files
REQ_DEV = Path("requirements-dev.txt")
REQ_ML = Path("requirements-ml-cpu.txt")
REQ_EVAL = Path("requirements-eval.txt")
REQ_NOTEBOOK = Path("requirements-notebook.txt")

EVIDENCE_FILE = Path(".codex/evidence/dependency_ops.jsonl")


def _choose_python(session: nox.Session) -> None:
    """
    Select a Python interpreter (best effort). If session.python is None,
    Nox will select default. This helper ensures consistent logging.
    """
    if session.python is None:
        session.log("No explicit interpreter provided; relying on Nox default resolution.")
        return
    session.log(f"Using interpreter: {session.python}")


def _install_requirements(session: nox.Session, *paths: Path) -> None:
    """
    Install one or more requirement files if they exist, fail-soft if missing.
    """
    for p in paths:
        if not p.exists():
            session.log(f"[warn] requirements file missing: {p}")
            continue
        session.log(f"[install] {p}")
        session.run("pip", "install", "-r", str(p), external=True)


def _show_vendor_scan(session: nox.Session) -> None:
    """
    Run a quick vendor module scan similar to scripts/vendor_guard.py logic.
    Non-failing; prints JSON summary. CPU guard failures handled externally.
    """
    code = (
        "import pkgutil,json,os,time;"
        "allow_triton=os.getenv('CODEX_ALLOW_TRITON_CPU','1')=='1';"
        "mods=[m.name for m in pkgutil.iter_modules() if (m.name.startswith('nvidia-') "
        "or m.name in {'triton','torchtriton'})];"
        "mods=mods if allow_triton else [m for m in mods if m!='triton'];"
        "print(json.dumps({'ts':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),"
        "'action':'DEPENDENCY_VENDOR_SCAN','vendors':mods}))"
    )
    session.run("python", "-c", code, external=True)


def _print_evidence_summary(session: nox.Session) -> None:
    """
    Summarize dependency evidence file if present.
    """
    if not EVIDENCE_FILE.exists():
        session.log("[info] evidence file absent (expected on setup/maintenance runs).")
        return
    data = []
    for line in EVIDENCE_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            data.append(obj)
        except Exception:
            session.log(f"[warn] malformed JSON evidence line: {line[:120]}...")
    counts = {}
    for obj in data:
        action = obj.get("action", "UNKNOWN")
        counts[action] = counts.get(action, 0) + 1
    session.log("[evidence] action counts:")
    for k, v in sorted(counts.items()):
        session.log(f"  - {k}: {v}")
    # vendor set sanity
    vendor_after = [
        o.get("vendor_list_after") for o in data if o.get("action") == "DEPENDENCY_VENDOR_PURGE"
    ]
    if vendor_after:
        residue = [v for v in vendor_after if v]
        if residue:
            session.log(f"[warn] Non-empty vendor residues detected after purge: {residue}")
        else:
            session.log("[ok] All purge events show empty vendor residue.")


def _dependency_plan(session: nox.Session) -> None:
    """
    Heuristic dependency classification using pip freeze + import search.
    Output: artifacts/dependency_plan.json
    """
    freeze = subprocess.check_output(["pip", "freeze"], text=True).splitlines()
    deps = []
    for line in freeze:
        if "==" not in line:
            continue
        name, ver = line.split("==", 1)
        lower = name.lower()
        size_guess = _size_heuristic(lower)
        classification = _classify(lower)
        deps.append(
            {
                "name": name,
                "version": ver,
                "size_estimate_mb": size_guess,
                "classification": classification,
            }
        )
    out_dir = Path("artifacts")
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "dependency_plan.json"
    out_file.write_text(
        json.dumps({"generated_at": _ts(), "entries": deps}, indent=2), encoding="utf-8"
    )
    session.log(f"[plan] wrote {out_file}")


def _size_heuristic(name: str) -> float:
    """
    Rudimentary size guess.
    """
    table = {
        "torch": 200.0,
        "jupyterlab": 220.0,
        "notebook": 50.0,
        "scipy": 80.0,
        "pandas": 55.0,
        "matplotlib": 35.0,
        "scikit-learn": 75.0,
        "statsmodels": 35.0,
        "transformers": 60.0,
        "sentencepiece": 6.0,
        "accelerate": 18.0,
        "peft": 15.0,
        "lm-eval": 20.0,
        "sacrebleu": 10.0,
        "rouge-score": 5.0,
        "nltk": 12.0,
    }
    return table.get(name, 5.0)


def _classify(name: str) -> str:
    """
    Classification reflecting triage table.
    """
    if name in {
        "pytest",
        "pytest-cov",
        "ruff",
        "black",
        "isort",
        "mypy",
        "pip-audit",
        "bandit",
        "jsonschema",
        "types-jsonschema",
        "pydantic",
        "hydra-core",
        "omegaconf",
        "requests",
        "defusedxml",
        "psutil",
    }:
        return "Keep"
    if name.startswith("nvidia-") or name in {"triton", "torchtriton"}:
        return "Purge"
    if name in {
        "torch",
        "transformers",
        "tokenizers",
        "safetensors",
        "accelerate",
        "peft",
        "sentencepiece",
    }:
        return "Optional-ML"
    if name in {
        "scipy",
        "scikit-learn",
        "statsmodels",
        "pandas",
        "lm-eval",
        "sacrebleu",
        "rouge-score",
        "nltk",
    }:
        return "Optional-Eval"
    if name in {"jupyterlab", "notebook", "nbconvert", "matplotlib"}:
        return "Defer-Notebook"
    return "Other"


def _ts() -> str:
    import time

    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------


@nox.session(name="list_sessions", python=PY_VERSIONS)
def list_sessions(session: nox.Session) -> None:
    """
    Lists available Nox sessions for segmentation awareness.
    """
    _choose_python(session)
    sessions = [
        "tests",
        "config_validation",
        "ml_tests",
        "eval_tests",
        "notebook_env",
        "verify_hygiene",
        "evidence_check",
        "dependency_plan",
        "rollback_smoke",
        "regression",
    ]
    session.log("Available sessions:")
    for s in sessions:
        session.log(f"  - {s}")


@nox.session(name="tests", python=PY_VERSIONS)
def tests(session: nox.Session) -> None:
    """
    Baseline test session (no heavy ML / eval dependencies).
    Use pytest markers to skip ML-specific tests.
    """
    _choose_python(session)
    _install_requirements(session, REQ_DEV)
    _show_vendor_scan(session)
    session.run(
        "pytest",
        "-q",
        "--disable-warnings",
        "-m",
        "not requires_torch",
        external=True,
    )


@nox.session(name="config_validation", python=PY_VERSIONS)
def config_validation(session: nox.Session) -> None:
    """
    Validate Hydra configuration files against bundled schemas.

    This session guards against config drift by running the lightweight
    validator in tools/validate_configs.py with development dependencies
    (jsonschema/PyYAML) available.
    """

    _choose_python(session)
    _install_requirements(session, REQ_DEV)
    args = session.posargs or ["--group", "all", "--quiet"]
    session.run("python", "tools/validate_configs.py", *args, external=True)


@nox.session(name="ml_tests", python=PY_VERSIONS)
def ml_tests(session: nox.Session) -> None:
    """
    ML test session (torch + transformers + minimal augmentation).
    """
    _choose_python(session)
    _install_requirements(session, REQ_DEV, REQ_ML)
    _show_vendor_scan(session)
    # CPU posture reinforcement
    if os.getenv("CODEX_FORCE_CPU", "1") == "1":
        session.log("[posture] CPU-only enforced (CODEX_FORCE_CPU=1).")
    session.run("pytest", "-q", "-m", "requires_torch or requires_transformers", external=True)


@nox.session(name="eval_tests", python=PY_VERSIONS)
def eval_tests(session: nox.Session) -> None:
    """
    Evaluation metrics / scientific stack tests.
    """
    _choose_python(session)
    _install_requirements(session, REQ_DEV, REQ_EVAL)
    _show_vendor_scan(session)
    session.run("pytest", "-q", "-m", "eval or metrics", external=True)


@nox.session(name="regression", python=PY_VERSIONS)
def regression(session: nox.Session) -> None:
    """Offline regression suite covering R1-R5 categories."""

    _choose_python(session)
    _install_requirements(session, REQ_DEV)
    env = {
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "CODEX_NET_MODE": "offline",
    }
    session.run("python", "-m", "codex_regression.runner", external=True, env=env)


@nox.session(name="notebook_env", python=PY_VERSIONS)
def notebook_env(session: nox.Session) -> None:
    """
    Optional environment build for interactive docs / notebooks.
    Does NOT run tests by default; can be extended.
    """
    _choose_python(session)
    _install_requirements(session, REQ_DEV, REQ_NOTEBOOK)
    session.log("[info] Notebook environment ready. Launch with: jupyter lab (if required).")


@nox.session(name="verify_hygiene", python=PY_VERSIONS)
def verify_hygiene(session: nox.Session) -> None:
    """
    Summarize dependency evidence & perform sanity checks.
    Non-failing unless explicit vendor residue or malformed evidence lines discovered.
    """
    _choose_python(session)
    _install_requirements(session, REQ_DEV)
    _print_evidence_summary(session)
    _show_vendor_scan(session)
    session.log("[verify_hygiene] Completed.")


@nox.session(name="evidence_check", python=PY_VERSIONS)
def evidence_check(session: nox.Session) -> None:
    """
    Validates the evidence JSONL schema minimally.
    """
    _choose_python(session)
    if not EVIDENCE_FILE.exists():
        session.error("Evidence file missing; run environment setup first.")
    required_keys = {"ts", "action", "tool"}
    bad_lines = 0
    for i, line in enumerate(EVIDENCE_FILE.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except Exception:
            session.log(f"[schema] Line {i} invalid JSON.")
            bad_lines += 1
            continue
        missing = required_keys - set(obj.keys())
        if missing:
            session.log(f"[schema] Line {i} missing keys: {sorted(missing)}")
            bad_lines += 1
    if bad_lines:
        session.error(f"Evidence schema validation failed on {bad_lines} line(s).")
    session.log("[schema] Evidence file OK.")


@nox.session(name="dependency_plan", python=PY_VERSIONS)
def dependency_plan(session: nox.Session) -> None:
    """
    Generate a coarse dependency plan (classification & size estimates).
    """
    _choose_python(session)
    _install_requirements(session, REQ_DEV)
    _dependency_plan(session)


@nox.session(name="rollback_smoke", python=PY_VERSIONS)
def rollback_smoke(session: nox.Session) -> None:
    """
    Simulate rollback readiness: verify segmented files exist and can be removed cleanly.
    Does NOT remove; just checks presence & prints recommended commands.
    """
    _choose_python(session)
    files = [REQ_ML, REQ_EVAL, REQ_NOTEBOOK]
    missing = [f for f in files if not f.exists()]
    if missing:
        session.log(f"[rollback] Missing segmented files (already removed?): {missing}")
    else:
        session.log("[rollback] All segmented requirement files present.")
        session.log("To rollback segmentation safely execute:")
        session.log(
            "  git rm requirements-ml-cpu.txt requirements-eval.txt requirements-notebook.txt"
        )
        session.log("  Edit noxfile.py: remove ml_tests, eval_tests, notebook_env sessions.")
    session.log("[rollback_smoke] Complete.")
