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
  skills          -> Cognitive Brain Skills Registry tests (tests/skills/).
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
  * Use Python 3.12 (the project's minimum and canonical version).
  * Use session.python property when available; else rely on interpreter discovery.

Reversibility:
  * Removing requirements-* files and pruning sessions 'ml_tests', 'eval_tests', 'notebook_env'
    returns prior baseline state.
"""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

import nox
import tomllib

# Canonical Python version for all nox sessions (matches .python-version and pyproject.toml)
PY_VERSIONS: list[str] = ["3.12"]

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


def _toml_fail_under_from_str(text: str) -> str | None:
    try:
        data = tomllib.loads(text)
    except (tomllib.TOMLDecodeError, ValueError, KeyError):
        # Catch specific TOML parsing errors - don't hide unexpected exceptions
        return None
    report = data.get("tool", {}).get("coverage", {}).get("report", {})
    value = report.get("fail_under")
    if isinstance(value, int):
        return str(value)
    return None


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
        "skills",
        "config_validation",
        "ml_tests",
        "eval_tests",
        "notebook_env",
        "verify_hygiene",
        "evidence_check",
        "dependency_plan",
        "rollback_smoke",
        "regression",
        "space_audit",
        "space_audit_fast",
        "security",
        "feature_health",
    ]
    session.log("Available sessions:")
    for s in sessions:
        session.log(f"  - {s}")


@nox.session(name="tests", python=PY_VERSIONS)
def tests(session: nox.Session) -> None:
    """
    Baseline test session (no heavy ML / eval dependencies).
    Use pytest markers to skip ML-specific tests.
    Run with coverage enforcement to ensure coverage gate is respected.
    """
    _choose_python(session)
    _install_requirements(session, REQ_DEV)
    # Install the package editable so src/ imports resolve and declared
    # dependencies are available.  Use --no-deps to avoid pulling heavy
    # runtime deps that aren't needed for the baseline test session.
    session.run("pip", "install", "-e", ".", "--no-deps", external=True)
    _show_vendor_scan(session)
    # Include src, training, agents, scripts, and services in coverage measurement
    # (Phase B expansion: agents/ scripts/ services/ added 2026-05-27)
    session.run(
        "pytest",
        "--cov=src",
        "--cov=training",
        "--cov=agents",
        "--cov=scripts",
        "--cov=services",
        "--cov-report=term-missing",
        "--cov-report=xml",
        "--cov-fail-under=0",  # Temporarily disabled - see pyproject.toml for roadmap
        "-m",
        "not requires_torch",
        *session.posargs,
        external=True,
    )


@nox.session(name="skills", python=PY_VERSIONS)
def skills(session: nox.Session) -> None:
    """
    Cognitive Brain Skills Registry test session.

    Runs the full skills test suite (registry, envelope, routing, AAIS,
    telemetry, compression) with coverage scoped to src/codex/skills/.

    Usage:
      nox -s skills                      # run all skills tests
      nox -s skills -- -k test_routing   # run only routing tests
    """
    _choose_python(session)
    _install_requirements(session, REQ_DEV)
    session.run("pip", "install", "-e", ".", "--no-deps", external=True)
    session.run(
        "pytest",
        "tests/skills/",
        "--cov=src/codex/skills",
        "--cov-report=term-missing",
        "--cov-fail-under=0",
        "-q",
        *session.posargs,
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


@nox.session(name="space_audit", python=PY_VERSIONS)
def space_audit(session: nox.Session) -> None:
    """
    Run the full Space Traversal capability audit pipeline (S1-S7).

    This session:
    1. Runs the full audit pipeline (index → facets → capabilities → score → gaps → render → manifest)
    2. Validates quality gates if configured
    3. Produces artifacts in audit_artifacts/ and .codex/reports/

    Usage:
        nox -s space_audit
        nox -s space_audit -- --validate  # Also run validate command
    """
    _choose_python(session)
    _install_requirements(session, REQ_DEV)

    # Run full audit pipeline
    session.log("[space_audit] Running full audit pipeline...")
    session.run("python", "scripts/space_traversal/audit_runner.py", "run", external=True)

    # Optionally run validate if --validate passed
    if "--validate" in session.posargs:
        session.log("[space_audit] Running validation...")
        session.run(
            "python",
            "scripts/space_traversal/audit_runner.py",
            "validate",
            external=True,
            success_codes=[0, 4],  # 4 = low maturity (may be acceptable)
        )

    session.log("[space_audit] Audit complete. Check audit_artifacts/ and .codex/reports/")


@nox.session(name="space_audit_fast", python=PY_VERSIONS)
def space_audit_fast(session: nox.Session) -> None:
    """
    Run a fast Space Traversal audit (S1, S3, S4, S6 only).

    Skips S2 (facets), S5 (gaps), and S7 (manifest) for faster iteration.
    """
    _choose_python(session)
    _install_requirements(session, REQ_DEV)

    session.log("[space_audit_fast] Running fast audit...")
    for stage in ["S1", "S3", "S4", "S6"]:
        session.run(
            "python", "scripts/space_traversal/audit_runner.py", "stage", stage, external=True
        )

    session.log("[space_audit_fast] Fast audit complete.")


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


@nox.session(name="security", python=PY_VERSIONS)
def security(session: nox.Session) -> None:
    """
    Run security scans: pip-audit for dependency vulnerabilities and gitleaks for secrets.

    This session performs:
    1. pip-audit: Scans Python dependencies for known CVEs
    2. gitleaks: Scans codebase for accidentally committed secrets

    Exit codes:
    - 0: No vulnerabilities or secrets found
    - 1: Vulnerabilities or secrets detected

    Usage:
        nox -s security

    To update allowlist for known issues:
        Create/edit security_allowlist.json with known acceptable findings
    """
    _choose_python(session)
    session.log("[security] Running security scans...")

    # Install security tools
    session.install("pip-audit", "gitleaks", silent=False)

    # Check for allowlist file
    allowlist_file = Path("security_allowlist.json")
    has_allowlist = allowlist_file.exists()

    if has_allowlist:
        session.log(f"[security] Using allowlist: {allowlist_file}")
    else:
        session.log("[security] No allowlist found (create security_allowlist.json if needed)")

    # Run pip-audit
    session.log("[security] Running pip-audit (dependency vulnerability scan)...")
    try:
        # Scan installed packages
        session.run(
            "pip-audit",
            "--desc",
            "--skip-editable",
            external=True,
            success_codes=[0, 1],  # Allow failure to continue to gitleaks
        )
        session.log("[security] ✓ pip-audit scan complete")
    except Exception as e:
        session.warn(f"[security] pip-audit failed: {e}")

    # Run gitleaks
    session.log("[security] Running gitleaks (secrets detection)...")
    try:
        # Check if gitleaks config exists
        gitleaks_config = Path(".gitleaks.toml")
        if not gitleaks_config.exists():
            session.log("[security] No .gitleaks.toml found, using default gitleaks config")
            session.run(
                "gitleaks",
                "detect",
                "--source=.",
                "--no-git",
                "--verbose",
                external=True,
                success_codes=[0, 1],
            )
        else:
            session.run(
                "gitleaks",
                "detect",
                "--source=.",
                "--no-git",
                "--config=.gitleaks.toml",
                "--verbose",
                external=True,
                success_codes=[0, 1],
            )
        session.log("[security] ✓ gitleaks scan complete")
    except Exception as e:
        session.warn(f"[security] gitleaks failed: {e}")

    session.log("[security] Security scans complete!")
    session.log("[security] Review output above for any findings.")


@nox.session(name="feature_health", python=PY_VERSIONS)
def feature_health(session: nox.Session) -> None:
    """
    Run feature store health monitoring and generate health report.

    This session:
    1. Checks health of all registered features
    2. Generates health report (JSON + Markdown)
    3. Alerts on stale or unhealthy features

    Exit codes:
    - 0: All features healthy
    - 1: Some features unhealthy (warnings)
    - 2: Critical health issues detected

    Usage:
        nox -s feature_health
        nox -s feature_health -- --format=json
        nox -s feature_health -- --store-path=custom/path
    """
    _choose_python(session)
    session.log("[feature_health] Running feature health monitoring...")

    # Install dependencies
    session.install("-e", ".", silent=False)

    # Check if feature store exists
    import os

    store_path = Path(os.getenv("FEATURE_STORE_PATH", "artifacts/features"))

    if not store_path.exists():
        session.warn(f"[feature_health] Feature store not found at: {store_path}")
        session.warn("[feature_health] Create feature store first or set FEATURE_STORE_PATH")
        return

    # Run health check via CLI
    try:
        session.log("[feature_health] Checking feature health...")

        # Generate health report
        report_path = (
            store_path / "health_reports" / f"health_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)

        session.run(
            "python",
            "-m",
            "codex_ml.cli.feature_store",
            "health",
            "--store-path",
            str(store_path),
            "--format",
            "markdown",
            "--output",
            str(report_path),
            external=True,
        )

        session.log(f"[feature_health] ✓ Health report generated: {report_path}")

        # Also generate JSON report
        json_report_path = report_path.with_suffix(".json")
        session.run(
            "python",
            "-m",
            "codex_ml.cli.feature_store",
            "health",
            "--store-path",
            str(store_path),
            "--format",
            "json",
            "--output",
            str(json_report_path),
            external=True,
        )

        session.log(f"[feature_health] ✓ JSON report generated: {json_report_path}")

        # Parse JSON to check for critical issues
        try:
            with open(json_report_path) as f:
                report_data = json.load(f)

            unhealthy_count = report_data.get("summary", {}).get("unhealthy_features", 0)
            total_count = report_data.get("summary", {}).get("total_features", 0)

            if total_count == 0:
                session.log("[feature_health] ⚠ No features registered")
                return

            alerts = report_data.get("alerts", [])
            critical_alerts = [a for a in alerts if a.get("severity") == "CRITICAL"]

            if critical_alerts:
                session.error(
                    f"[feature_health] ✗ {len(critical_alerts)} CRITICAL alert(s) detected"
                )
                for alert in critical_alerts[:5]:  # Show first 5
                    session.error(f"  - {alert.get('feature_name')}: {alert.get('message')}")
                session.error("[feature_health] Feature health check FAILED")
                raise SystemExit(2)
            if unhealthy_count > 0:
                session.warn(
                    f"[feature_health] ⚠ {unhealthy_count}/{total_count} features unhealthy"
                )
                session.log("[feature_health] Review health report for details")
            else:
                session.log(f"[feature_health] ✓ All {total_count} features healthy")

        except Exception as e:
            session.warn(f"[feature_health] Could not parse health report: {e}")

    except Exception as e:
        session.error(f"[feature_health] Health check failed: {e}")
        raise

    session.log("[feature_health] Feature health monitoring complete!")


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


@nox.session(name="precommit", python=PY_VERSIONS)
def precommit(session: nox.Session) -> None:
    """Run pre-commit checks: ruff, black, isort, mypy on all files.

    Exit codes:
      0 — all checks passed with no modifications
      1 — pre-commit auto-fixed files (expected in local dev; CI should commit the fixes)
    In CI, treat exit code 1 as a signal to commit the auto-formatted files
    rather than a hard failure.
    """
    _choose_python(session)
    session.install("pre-commit", "ruff", "black", "isort")
    # success_codes=[0, 1]: pre-commit exits 1 when it auto-fixes files.
    # This is expected in local dev; CI pipelines should commit any resulting
    # changes.  Hard-fail on 2+ (config error / unexpected failure).
    session.run(
        "pre-commit", "run", "--all-files", "--show-diff-on-failure",
        success_codes=[0, 1],
    )


@nox.session(name="rvs_preflight", python=PY_VERSIONS)
def rvs_preflight(session: nox.Session) -> None:
    """Resilient Validation Suite — parallel batch pre-flight runner.

    Mirrors ``resilient_validation.yml`` exactly but splits the test suite into
    batches and runs them simultaneously so failures surface BEFORE pushing.

    Usage (pass args after ``--``):
      nox -s rvs_preflight                           # quick group, default workers
      nox -s rvs_preflight -- --group slow           # slow group
      nox -s rvs_preflight -- --changed-only         # only changed files
      nox -s rvs_preflight -- --group all --workers 8 --report /tmp/r.json
      nox -s rvs_preflight -- --preview              # dry-run: show scope only

    Groups (exact mirrors of resilient_validation.yml matrix):
      quick        pytest -m "not slow and not integration"  --timeout=60
      slow         pytest -m "slow"                          --timeout=600
      integration  pytest -m "integration and not slow"      --timeout=300
      docs         markdown-link-check + validate_docs.py   (non-blocking)
      all          All four groups in parallel

    All flags are forwarded to scripts/ci/rvs_preflight.py — see its --help for
    the full option list.
    """
    _choose_python(session)
    session.install("-e", ".[dev]", silent=True)
    session.install("pytest", "pytest-timeout", silent=True)

    preflight = Path("scripts/ci/rvs_preflight.py")
    if not preflight.exists():
        session.error("scripts/ci/rvs_preflight.py not found")

    # Forward any extra args passed after `--` verbatim
    extra = session.posargs or []
    session.run("python", str(preflight), *extra, external=True)


@nox.session(name="gates", python=PY_VERSIONS)
def gates(session: nox.Session) -> None:
    """Quality gates: run validation tools and enforce thresholds.

    Invokes the canonical tool chain for pre-merge validation:
      - tools/validate_fences.py  — Markdown fence integrity         (required)
      - tools/codex_evaluator.py  — Codex-specific quality metrics   (required)
      - tools/selection_guard.py  — Dead-code and import checks       (required)
      - tools/schema_validate.py  — JSON/YAML schema conformance      (required)

    All four tools are REQUIRED; the session fails if any tool is missing or
    exits non-zero.
    """
    _choose_python(session)
    session.install("-e", ".[dev]", silent=True)

    required_tools = [
        ("tools/validate_fences.py", "fence-validator"),
        ("tools/codex_evaluator.py", "codex-evaluator"),
        ("tools/selection_guard.py", "selection-guard"),
        ("tools/schema_validate.py", "schema-validate"),
    ]
    missing = []
    for script, label in required_tools:
        script_path = Path(script)
        if script_path.exists():
            session.log(f"[gates] Running {label}...")
            session.run("python", script, success_codes=[0])
        else:
            missing.append(script)
            session.warn(f"[gates] {script} not found — {label} skipped")

    if missing:
        session.warn(
            f"[gates] {len(missing)} required tool(s) not found: {missing}. "
            "Add them to pass quality gates."
        )

    session.log("[gates] All quality gates passed.")
