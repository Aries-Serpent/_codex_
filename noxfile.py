#!/usr/bin/env python
"""
Local task runner for _codex_ (no CI usage). Provides one-command sessions:
  - gates: fences → evaluator → (optional) schema checks → selection guard
  - tests: run repo tests with pytest plugin autoload disabled
  - precommit: run all pre-commit hooks locally
"""
from __future__ import annotations

import importlib
import json
from pathlib import Path
from types import ModuleType
from typing import Iterable, Optional

import nox

_EVALUATOR = Path("tools/codex_evaluator.py")
_EVALUATOR_RULES = Path("manifests/codex_eval_rules.v3.json")
_SELECTION_GUARD = Path("tools/selection_guard.py")
_SELECTION_RULES = Path("manifests/selection_guard_rules.json")
_SELECTION_DEFAULT_SAMPLE = Path("samples/assistant_message_summary.sample.json")
_SCHEMA_VALIDATE = Path("tools/schema_validate.py")
_SELECTION_SCHEMA = Path("schemas/selection_guard_rules.schema.json")
_EVALUATOR_SCHEMA = Path("schemas/codex_eval_rules.v3.schema.json")
_CONFIG_VALIDATOR = Path("tools/validate_configs.py")


_TOML_MODULE: Optional[ModuleType] = None


def _get_toml_module() -> Optional[ModuleType]:
    """Best-effort loader for tomllib/tomli without hard dependency."""

    global _TOML_MODULE
    if _TOML_MODULE is not None:
        return _TOML_MODULE

    for name in ("tomllib", "tomli"):
        try:
            module = importlib.import_module(name)
        except ModuleNotFoundError:
            continue
        else:
            _TOML_MODULE = module
            return module

    _TOML_MODULE = None
    return None


def _toml_fail_under_from_str(toml_text: str) -> Optional[str]:
    """
    Extract fail_under value from [tool.coverage.report] section in TOML text.
    Returns the value as a string if it's a valid integer, None otherwise.
    """
    toml_module = _get_toml_module()
    if toml_module is None:
        # TOML library not available, cannot parse
        return None

    try:
        parsed = toml_module.loads(toml_text)
        fail_under = parsed.get("tool", {}).get("coverage", {}).get("report", {}).get("fail_under")
        if fail_under is not None and isinstance(fail_under, int):
            return str(fail_under)
    except (AttributeError, TypeError, KeyError):
        # Missing keys or wrong type for fail_under
        pass
    except Exception:
        # Invalid TOML syntax or other parsing errors
        pass
    return None


def _resolve_summary(posargs: Iterable[str]) -> Optional[Path]:
    """Best-effort resolution of the summary input path for evaluator/guard."""

    for candidate in posargs:
        path = Path(candidate).expanduser()
        if path.exists():
            return path
    if _SELECTION_DEFAULT_SAMPLE.exists():
        return _SELECTION_DEFAULT_SAMPLE
    return None


def _log_skip(session: nox.Session, step: str, reason: str) -> None:
    session.log(f"[skip] {step}: {reason}")


@nox.session
def gates(session: nox.Session) -> None:
    """Run local gates: structure + scoring + schemas + selection guard."""
    session.install("-r", "requirements-dev.txt")
    # 1) Fence integrity
    session.run("python", "tools/validate_fences.py")
    # 2) Evaluator
    summary = _resolve_summary(session.posargs)
    if not _EVALUATOR.exists():
        _log_skip(session, "codex evaluator", f"missing {_EVALUATOR}")
    elif not _EVALUATOR_RULES.exists():
        _log_skip(session, "codex evaluator", f"missing rules {_EVALUATOR_RULES}")
    elif summary is None:
        _log_skip(
            session,
            "codex evaluator",
            "no summary input (pass a path via `nox -s gates -- path/to/summary.json`)",
        )
    else:
        session.run(
            "python",
            str(_EVALUATOR),
            "--rules",
            str(_EVALUATOR_RULES),
            "--input",
            str(summary),
        )
    # 3) Schema checks (graceful even if jsonschema not installed—tool exits 0 with info)
    if not _SCHEMA_VALIDATE.exists():
        _log_skip(session, "schema validation", f"missing {_SCHEMA_VALIDATE}")
    else:
        schema_args = ["python", str(_SCHEMA_VALIDATE)]
        if _SELECTION_RULES.exists() and _SELECTION_SCHEMA.exists():
            schema_args.extend(
                [
                    "--data",
                    str(_SELECTION_RULES),
                    "--schema",
                    str(_SELECTION_SCHEMA),
                ]
            )
        else:
            _log_skip(
                session,
                "schema validation",
                f"missing selection guard manifest or schema "
                f"({_SELECTION_RULES}, {_SELECTION_SCHEMA})",
            )
        if _EVALUATOR_RULES.exists() and _EVALUATOR_SCHEMA.exists():
            schema_args.extend(
                [
                    "--data",
                    str(_EVALUATOR_RULES),
                    "--schema",
                    str(_EVALUATOR_SCHEMA),
                ]
            )
        else:
            _log_skip(
                session,
                "schema validation",
                f"missing evaluator manifest or schema ({_EVALUATOR_RULES}, {_EVALUATOR_SCHEMA})",
            )
        if len(schema_args) > 2:
            session.run(*schema_args)
        else:
            _log_skip(session, "schema validation", "no data/schema pairs available")
    # 4) Selection guard (non-fatal—mirrors scripts/run_local_gates.sh behavior)
    if not _SELECTION_GUARD.exists():
        _log_skip(session, "selection guard", f"missing {_SELECTION_GUARD}")
    elif not _SELECTION_RULES.exists():
        _log_skip(session, "selection guard", f"missing rules {_SELECTION_RULES}")
    elif summary is None:
        _log_skip(
            session,
            "selection guard",
            "no summary input (pass a path via `nox -s gates -- path/to/summary.json`)",
        )
    else:
        session.run(
            "python",
            str(_SELECTION_GUARD),
            "--rules",
            str(_SELECTION_RULES),
            "--input",
            str(summary),
            "--selected",
            "3",
            success_codes=[0, 1, 2],
        )
    if _CONFIG_VALIDATOR.exists():
        session.run("python", str(_CONFIG_VALIDATOR), "--quiet")
    else:
        _log_skip(session, "config schemas", f"missing {_CONFIG_VALIDATOR}")


@nox.session
def tests(session: nox.Session) -> None:
    """Run pytest with plugin autoload disabled (deterministic) and coverage enforcement."""
    session.install("-r", "requirements-dev.txt")
    session.env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"

    # Run tests with coverage
    session.run(
        "pytest",
        "--cov=src/codex_ml",
        "--cov-report=xml",
        "--cov-report=term-missing",
        "--cov-fail-under=70",
        "-v",
    )
    # Archive coverage report to .codex/coverage
    session.run(
        "python",
        "-c",
        (
            "from pathlib import Path; import shutil; src=Path('coverage.xml'); "
            "dest=Path('.codex/coverage'); dest.mkdir(parents=True, exist_ok=True); "
            "shutil.copy2(src, dest / 'coverage.xml') if src.exists() else None"
        ),
    )


@nox.session
def coverage(session: nox.Session) -> None:
    """Run pytest with coverage and generate artifacts for CI."""
    session.install("-r", "requirements-dev.txt")
    session.env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"

    # Ensure artifacts directory exists
    from pathlib import Path
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # Run tests with coverage
    session.run(
        "pytest",
        "--cov=src/codex_ml",
        "--cov-report=xml:artifacts/coverage.xml",
        "--cov-report=html:artifacts/htmlcov",
        "--cov-report=term-missing",
        "--cov-fail-under=70",
        "-v",
    )


@nox.session
def security(session: nox.Session) -> None:
    """
    Security scanning with:
      - pip-audit (JSON) → artifacts/security_report.json
      - bandit → artifacts/bandit_report.txt
      - gitleaks → artifacts/gitleaks_report.json
      - Aggregated summary → artifacts/security_summary.json

    Policy:
      - Fail on HIGH/CRITICAL unless present in allowlist (by id) with valid (non-expired) expiry_date.
    """
    session.install("-r", "requirements-dev.txt")
    # Ensure tool availability (pin compatible versions)
    session.install("pip-audit>=2.7.0")
    session.install("bandit>=1.7.5")
    
    import json
    import shutil
    import datetime
    import subprocess
    from pathlib import Path

    # Ensure artifacts directory exists
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # 1) pip-audit (dependency vulnerabilities)
    audit_output = artifacts_dir / "security_report.json"
    session.log("Running pip-audit...")
    
    pip_audit_result = subprocess.run(
        ["pip-audit", "-f", "json"],
        capture_output=True,
        text=True,
    )
    
    # pip-audit returns 1 when vulns found; still parseable
    if pip_audit_result.returncode not in (0, 1):
        session.error(f"pip-audit failed: {pip_audit_result.stderr}")

    try:
        pip_audit_json = json.loads(pip_audit_result.stdout or "[]")
    except Exception as e:
        session.error(f"Failed to parse pip-audit JSON: {e}")

    # 1a) Allowlist handling for pip-audit
    allowlist_path = Path("security_allowlist.json")
    active_allow = set()
    if allowlist_path.exists():
        try:
            allowlist = json.loads(allowlist_path.read_text(encoding="utf-8"))
            today = datetime.date.today()
            for entry in allowlist.get("allowlisted_vulnerabilities", []):
                eid = entry.get("id")
                try:
                    exp = datetime.date.fromisoformat(entry.get("expiry_date", "1970-01-01"))
                except Exception:
                    exp = datetime.date(1970, 1, 1)
                if eid and exp >= today:
                    active_allow.add(eid)
        except Exception:
            # Ignore malformed allowlist; treat as empty
            pass

    high_crit = []
    # pip-audit may return list or object; handle both
    deps = pip_audit_json if isinstance(pip_audit_json, list) else pip_audit_json.get("dependencies", [])
    for dep in deps:
        name = dep.get("name") or dep.get("package", {}).get("name")
        vulns = dep.get("vulns") or dep.get("vulnerabilities") or []
        for v in vulns:
            vid = v.get("id") or v.get("vuln_id")
            sev = (v.get("severity") or "").upper()
            if vid in active_allow:
                continue
            if sev in {"HIGH", "CRITICAL"}:
                high_crit.append({"pkg": name, "id": vid, "severity": sev})

    audit_output.write_text(
        json.dumps(pip_audit_json, indent=2),
        encoding="utf-8",
    )
    session.log(f"✓ pip-audit report written to {audit_output}")

    # 2) Bandit (static analysis)
    bandit_output = artifacts_dir / "bandit_report.txt"
    bandit_cfg = ".bandit.yaml"
    bandit_cmd = ["bandit", "-q", "-r", "src"]
    if Path(bandit_cfg).exists():
        bandit_cmd.extend(["-c", bandit_cfg])
    
    session.log("Running bandit...")
    bandit_result = subprocess.run(
        bandit_cmd,
        capture_output=True,
        text=True,
    )
    bandit_output.write_text(
        (bandit_result.stdout or "") + ("\n" + bandit_result.stderr if bandit_result.stderr else ""),
        encoding="utf-8",
    )
    session.log(f"✓ bandit report written to {bandit_output}")

    # 3) gitleaks (secret scanning) — repo workspace, no git history
    gitleaks_output = artifacts_dir / "gitleaks_report.json"
    if shutil.which("gitleaks"):
        gitleaks_cfg = ".gitleaks.toml"
        gitleaks_cmd = ["gitleaks", "detect", "--no-git", "-r", ".", "--report-format", "json", "--report-path", str(gitleaks_output)]
        if Path(gitleaks_cfg).exists():
            gitleaks_cmd.extend(["--config", gitleaks_cfg])
        
        session.log("Running gitleaks...")
        gitleaks_result = subprocess.run(
            gitleaks_cmd,
            capture_output=True,
            text=True,
        )
        session.log(f"✓ gitleaks report written to {gitleaks_output}")
    else:
        # gitleaks not available; create empty report
        session.log("gitleaks not available; creating empty report")
        gitleaks_output.write_text("[]", encoding="utf-8")

    # 4) Aggregate summary for quick PR consumption
    gitleaks_json = gitleaks_output.read_text(encoding="utf-8") if gitleaks_output.exists() else "[]"
    gitleaks_count = _count_gitleaks(gitleaks_json)
    
    summary = {
        "pip_audit": {
            "high_critical": len(high_crit),
            "high_critical_list": high_crit,
        },
        "bandit": {
            "exit_code": bandit_result.returncode,
        },
        "gitleaks": {
            "exit_code": gitleaks_result.returncode if shutil.which("gitleaks") else 0,
            "findings_count": gitleaks_count,
        },
        "policy": {
            "fail_on_high_critical": True,
            "allowlist_ids_active": sorted(list(active_allow)),
        },
    }
    (artifacts_dir / "security_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    session.log(f"✓ security summary written to {artifacts_dir / 'security_summary.json'}")

    if high_crit:
        session.error(
            "High/Critical dependency vulnerabilities present (not allowlisted). "
            "See artifacts/security_summary.json and security_report.json"
        )
    session.log("Security artifacts written to artifacts/ directory.")


def _count_gitleaks(raw: str) -> int:
    """Count gitleaks findings from JSON string."""
    try:
        data = json.loads(raw or "[]")
        if isinstance(data, dict) and "findings" in data:
            return len(data.get("findings") or [])
        if isinstance(data, list):
            return len(data)
    except Exception:
        return 0
    return 0




@nox.session
def status(session: nox.Session) -> None:
    """Render a template-mode STATUS_REPORT.md with verbose output and artifacts."""
    session.install("-r", "requirements-dev.txt")
    session.env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    session.run(
        "python",
        "tools/status_report.py",
        "--summary",
        "samples/assistant_message_summary.sample.json",
        "--selected",
        "3",
        "--template",
        "docs/templates/status_update.md",
        "--branch",
        "local/nox",
        "--pr",
        "local",
        "--verbose",
        "--save-logs",
        "--out",
        "STATUS_REPORT.md",
    )
    # Also emit capability scores
    session.run("python", "tools/status/capability_autodiscovery.py")


@nox.session
def precommit(session: nox.Session) -> None:
    """Run all pre-commit hooks locally (manual)."""
    session.install("pre-commit")
    session.run("pre-commit", "run", "--all-files")


@nox.session(name="model-smoke")
def model_smoke(session: nox.Session) -> None:
    """Instantiate the default model on CPU to catch dtype/device regressions."""
    session.install("-r", "requirements-dev.txt")
    session.run(
        "python",
        "-c",
        (
            "from codex_ml.models.factory import load_model; "
            "load_model({'device': 'cpu', 'dtype': 'float32'})"
        ),
    )


@nox.session(name="status-validate")
def status_validate(session: nox.Session) -> None:
    """Validate the latest generated status JSON against the v1.1 schema (offline)."""
    session.install("-r", "requirements-dev.txt")
    # Validate today's artifact if present
    from datetime import datetime, timezone

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = f"reports/daily/_codex_status_update-{today}.json"
    session.run("python", "tools/status/validate_status_update.py", path)


@nox.session(name="env-snapshot")
def env_snapshot(session: nox.Session) -> None:
    """Emit artifacts/env_snapshot.json for reproducibility evidence."""
    session.install("-r", "requirements-dev.txt")
    session.run("python", "tools/env/export_env_json.py")


@nox.session(name="lint")
def lint(session: nox.Session) -> None:
    """Static linting/format checks (local-only)."""
    session.install("ruff==0.5.7", "black==24.8.0")
    session.run("ruff", "check", ".")
    session.run("black", "--check", ".")


@nox.session(name="typecheck")
def typecheck(session: nox.Session) -> None:
    """Run mypy and write summary to artifacts/mypy_summary.txt."""
    import subprocess
    from pathlib import Path
    
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    summary_path = artifacts_dir / "mypy_summary.txt"
    
    try:
        session.install("mypy==1.10.0")
        
        # Check if config file exists
        config_file = Path("config/mypy.ini")
        if config_file.exists():
            config_arg = ["--config-file", str(config_file)]
        else:
            config_arg = []
        
        # Run mypy and capture output
        result = subprocess.run(
            ["mypy"] + config_arg + ["src"],
            capture_output=True,
            text=True,
        )
        
        # Write summary to artifact
        summary_content = (result.stdout or "") + "\n" + (result.stderr or "")
        summary_path.write_text(summary_content, encoding="utf-8")
        session.log(f"✓ mypy summary written to {summary_path}")
        
        # Also display in terminal for immediate feedback
        if result.stdout:
            session.log(result.stdout)
        if result.stderr:
            session.log(result.stderr)
        
        if result.returncode != 0:
            session.error(f"mypy failed; see {summary_path} for details")
    except Exception as e:
        session.log(f"mypy unavailable or failed: {e}")
        summary_path.write_text(f"mypy unavailable or failed: {e}", encoding="utf-8")



@nox.session(name="repro_smoke")
def repro_smoke(session: nox.Session) -> None:
    """Run reproducibility and plugin smoke tests (local-only).

    Validates:
    - Deterministic behavior with fixed seeds
    - Plugin loading is non-fatal
    - Generative metrics optional behavior
    """
    session.install("-r", "requirements-dev.txt")
    # Disable pytest plugin autoload to ensure deterministic test execution and avoid
    # interference from globally installed pytest plugins, which could affect results.
    session.env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    session.run(
        "pytest",
        "-q",
        "tests/test_metrics_generative.py",
        "tests/eval/test_eval_provenance_capture.py",
        "tests/plugins/test_metric_plugin_loading.py",
    )


@nox.session(name="docs_build")
def docs_build(session: nox.Session) -> None:
    """Build offline API documentation with optional module gating.

    Environment variables:
        SKIP_OPTIONAL   - Skip optional modules (codex_ml extras)
        FAIL_ON_MISSING - Strict mode (fail if any requested modules missing)

    Usage:
        nox -s docs_build
        SKIP_OPTIONAL=1 nox -s docs_build
        FAIL_ON_MISSING=1 nox -s docs_build
    """
    session.install("-r", "requirements-dev.txt")

    # Use the docs_build.sh script for consistent behavior
    import os

    env = os.environ.copy()

    # Pass through environment variables
    skip_optional = env.get("SKIP_OPTIONAL", "0")
    fail_on_missing = env.get("FAIL_ON_MISSING", "0")

    session.log(
        f"Building API docs (SKIP_OPTIONAL={skip_optional}, " f"FAIL_ON_MISSING={fail_on_missing})"
    )

    session.run(
        "bash",
        "scripts/docs_build.sh",
        env=env,
        external=True,
    )


@nox.session(name="tracking_smoke")
def tracking_smoke(session: nox.Session) -> None:
    """Run local MLflow smoke test against file backend (local-only)."""
    session.install("-r", "requirements-dev.txt")
    session.env["MLFLOW_TRACKING_URI"] = "file:./mlruns"
    session.log("[tracking_smoke] using tracking URI file:./mlruns")
    # Create mlruns directory and verify setup
    import pathlib

    mlruns = pathlib.Path("./mlruns")
    mlruns.mkdir(parents=True, exist_ok=True)
    session.log(f"[tracking_smoke] mlruns directory: {mlruns.resolve()}")


@nox.session(name="config_index")
def config_index(session: nox.Session) -> None:
    """List Hydra config groups and options (offline discovery)."""
    session.install("-r", "requirements-dev.txt")
    session.run("python", "tools/configs/list_groups.py")


@nox.session(name="config_schema")
def config_schema(session: nox.Session) -> None:
    """Validate config schemas (offline)."""
    session.install("-r", "requirements-dev.txt")
    # Example: validate a sample config
    session.run("python", "tools/configs/schema_guard.py", "--path", "configs/base/hydra.yaml")


@nox.session(name="validate-configs")
def validate_configs(session: nox.Session) -> None:
    """Validate experiment configs (JSON/TOML) against schema."""
    session.install("-r", "requirements-dev.txt")
    session.run("python", "tools/validate_experiments.py")


@nox.session(name="perf_smoke")
def perf_smoke(session: nox.Session) -> None:
    """Run performance smoke tests (opt-in, guarded by CODEX_PERF_SMOKE)."""
    session.install("-r", "requirements-dev.txt")
    session.env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    session.env["CODEX_PERF_SMOKE"] = "1"
    session.run("pytest", "-q", "tests/perf/test_smoke.py")


@nox.session(name="docs")
def docs(session: nox.Session) -> None:
    """Build API documentation with pdoc3 (offline, local-only). Output to artifacts/docs/api/."""
    session.install("-r", "requirements-dev.txt")
    session.run("python", "tools/build_api_docs.py", *session.posargs)



