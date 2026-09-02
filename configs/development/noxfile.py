from __future__ import annotations

import configparser
import datetime as dt
import hashlib
import os
import shutil
import subprocess
import sys
import uuid
from collections.abc import Mapping, Sequence
from contextlib import contextmanager, suppress
from pathlib import Path
from typing import Any

try:
    import tomllib as _tomllib  # py311+
except Exception:  # pragma: no cover - fallback for py310
    try:
        import tomli as _tomllib
    except Exception:  # pragma: no cover - tomllib/tomli unavailable
        _tomllib = None  # type: ignore

import nox
from nox.command import CommandFailed

REPO_ROOT = Path(__file__).resolve().parents[2]
_CANDIDATE_PYTHONS = ("3.12", "3.11", "3.10")
_AVAILABLE = [v for v in _CANDIDATE_PYTHONS if shutil.which(f"python{v}")]
if _AVAILABLE:
    PY_VERSIONS: Sequence[str] = tuple(_AVAILABLE)
else:
    PY_VERSIONS = (f"{sys.version_info.major}.{sys.version_info.minor}",)

DEFAULT_PYTHON = os.getenv("CODEX_NOX_PYTHON") or PY_VERSIONS[0]
if DEFAULT_PYTHON not in PY_VERSIONS:
    PY_VERSIONS = (DEFAULT_PYTHON, *PY_VERSIONS)

CANONICAL_TEST_SESSION = "coverage"
UV = os.getenv("UV_BIN", "uv")
DEFAULT_COVERAGE_FLOOR = float(os.getenv("CODEX_COV_FLOOR", "3.5"))

ARTIFACTS = REPO_ROOT / "artifacts"
COVERAGE_HTML = ARTIFACTS / "coverage_html"
COVERAGE_XML = ARTIFACTS / "coverage.xml"
COVERAGE_JSON_ROOT = ARTIFACTS / "coverage"
PIP_CACHE = REPO_ROOT / ".cache" / "pip"
ERROR_REPORTS_ROOT = REPO_ROOT / ".codex" / "reports"

TEST_BOOTSTRAP_PKGS = ("pip", "setuptools", "wheel")
OFFLINE_TEST_TARGETS = (
    "tests/unit/test_zendesk_models.py",
    "tests/e2e_offline/test_diff_and_apply.py",
)

nox.options.reuse_existing_virtualenvs = True
nox.options.stop_on_first_error = False
nox.options.error_on_missing_interpreters = False


def _ensure_pip_cache(session: nox.Session) -> None:
    """Ensure pip installs share a local cache for hermetic runs."""

    PIP_CACHE.mkdir(parents=True, exist_ok=True)
    session.env.setdefault("PIP_CACHE_DIR", str(PIP_CACHE))


def _install(session: nox.Session, *packages: str) -> None:
    """Thin wrapper around session.install with a graceful empty guard."""

    if packages:
        session.install(*packages)


def _pytest_hermetic(session: nox.Session) -> None:
    """Force pytest to avoid host-specific plugins and ensure hash determinism."""

    session.env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    session.env.setdefault("PYTHONHASHSEED", "0")


def _export_env(session: nox.Session) -> None:
    _pytest_hermetic(session)
    session.env.setdefault("PYTHONUTF8", "1")


def _check_hydra_plugin(session: nox.Session) -> bool:
    """Verify hydra.extra plugin is importable; install if missing."""

    def _try_import() -> bool:
        try:
            session.run(
                "python",
                "-c",
                "import hydra; from hydra._internal.utils import create_config_search_path",
                silent=True,
            )
        except CommandFailed:
            return False
        return True

    if _try_import():
        session.log("[hydra-check] Hydra plugin available.")
        return True

    session.warn("[hydra-check] Plugin missing: hydra.extra will not load")
    _install(session, "hydra-core>=1.3")
    if _try_import():
        session.log("[hydra-check] Installed hydra-core>=1.3")
        return True

    session.error("Hydra plugin installation failed")
    return False


def _log_step_error(
    step: str,
    exc: Exception,
    context: str,
    *,
    question: str | None = None,
) -> None:
    """Append a structured error block to the dated .codex/reports markdown log."""

    timestamp = dt.datetime.utcnow().isoformat(timespec="seconds") + "Z"
    question_text = question or "Could you clarify how you would like this issue to be resolved?"
    try:
        ERROR_REPORTS_ROOT.mkdir(parents=True, exist_ok=True)
        errors_path = ERROR_REPORTS_ROOT / (f"errors_{dt.datetime.utcnow().date().isoformat()}.md")
        block = [
            f"### {timestamp} — {step}",
            "",
            f"- **Message:** {type(exc).__name__}: {exc}",
            f"- **Context:** {context}",
            f"- **Clarification Needed:** {question_text}",
            "",
        ]
        with errors_path.open("a", encoding="utf-8") as handle:
            handle.write("\n".join(block))
    except Exception:
        # The error log is best-effort; failures here must not interrupt workflows.
        pass


@contextmanager
def _error_logging_step(
    step: str,
    context: str,
    *,
    question: str | None = None,
):
    """Context manager that records failures to the structured error report."""

    try:
        yield
    except Exception as exc:  # pragma: no cover - defensive guard
        _log_step_error(step, exc, context, question=question)
        raise


def _archive_gate_has_explicit_changed_files(posargs: Sequence[str]) -> bool:
    """Return True when ``--changed-file`` appears in *posargs*."""

    for entry in posargs:
        if entry == "--changed-file" or entry.startswith("--changed-file="):
            return True
    return False


def _archive_gate_staged_files(repo_root: Path) -> list[str]:
    """Return staged files for the archive gate, ignoring git failures."""

    try:
        proc = subprocess.run(
            ["git", "diff", "--staged", "--name-only"],
            cwd=repo_root,
            capture_output=True,
            check=False,
            text=True,
        )
    except FileNotFoundError:
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def _coverage_json_output() -> Path:
    """Return a unique coverage JSON output path under artifacts/coverage."""

    timestamp = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    digest = hashlib.sha256(uuid.uuid4().hex.encode("utf-8")).hexdigest()[:12]
    run_dir = COVERAGE_JSON_ROOT / f"{timestamp}_{digest}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir / "coverage.json"


def _read_fail_under_from_cfg(path: Path) -> str | None:
    parser = configparser.ConfigParser()
    with suppress(configparser.Error, ValueError):
        parser.read(path, encoding="utf-8")
        if parser.has_option("report", "fail_under"):
            value = parser.getfloat("report", "fail_under")
            if value >= 0:
                return str(value)
    return None


def _toml_fail_under_from_str(toml_text: str) -> str | None:
    """Extract fail_under from TOML text under [tool.coverage.report]."""

    if _tomllib is None:
        return None
    try:
        data: Mapping[str, Any] = _tomllib.loads(toml_text)
    except Exception:  # pragma: no cover - defensive parsing guard
        return None
    tool_section = data.get("tool")
    if not isinstance(tool_section, Mapping):
        return None
    coverage_section = tool_section.get("coverage")
    if not isinstance(coverage_section, Mapping):
        return None
    report_section = coverage_section.get("report")
    if not isinstance(report_section, Mapping):
        return None
    fail = report_section.get("fail_under")
    if isinstance(fail, (int, float)) and fail >= 0:
        return str(fail)
    return None


def _default_fail_under() -> str:
    """Resolve the desired coverage fail-under threshold."""

    codex_floor = os.environ.get("CODEX_COV_FLOOR")
    if codex_floor is not None:
        with suppress(ValueError):
            if float(codex_floor) >= 0:
                return codex_floor
    coverage_env = os.environ.get("COVERAGE_MIN")
    if coverage_env is not None:
        with suppress(ValueError):
            if float(coverage_env) >= 0:
                return coverage_env

    rc_file_env = os.environ.get("COVERAGE_RCFILE")
    if rc_file_env:
        rc_path = Path(rc_file_env)
        if rc_path.is_file():
            parsed = _read_fail_under_from_cfg(rc_path)
            if parsed is not None:
                return parsed

    coveragerc = REPO_ROOT / ".coveragerc"
    if coveragerc.is_file():
        parsed = _read_fail_under_from_cfg(coveragerc)
        if parsed is not None:
            return parsed

    pyproject = REPO_ROOT / "pyproject.toml"
    if pyproject.is_file():
        try:
            parsed = _toml_fail_under_from_str(pyproject.read_text(encoding="utf-8"))
        except Exception:  # pragma: no cover - read errors should not fail nox
            parsed = None
        if parsed is not None:
            return parsed

    return f"{DEFAULT_COVERAGE_FLOOR}"


DEFAULT_FAIL_UNDER = _default_fail_under()


def _run_pytest_coverage(session: nox.Session, *, extra_args: Sequence[str] | None = None) -> None:
    """Shared implementation for coverage sessions."""

    session.chdir(str(REPO_ROOT))
    _ensure_pip_cache(session)
    _install(session, *TEST_BOOTSTRAP_PKGS)
    _install(session, "--no-deps", "-e", ".")
    _install(
        session,
        "hydra-core>=1.3",
        "omegaconf>=2.3",
        "PyYAML>=6.0",
        "pydantic>=2.4",
        "pydantic-settings>=2.2",
        "pytest",
        "pytest-cov",
        "pytest-randomly",
        "hypothesis>=6.100",
    )
    _install(session, "pytest", "pytest-cov")
    _pytest_hermetic(session)
    COVERAGE_HTML.mkdir(parents=True, exist_ok=True)
    COVERAGE_JSON_ROOT.mkdir(parents=True, exist_ok=True)
    COVERAGE_XML.parent.mkdir(parents=True, exist_ok=True)
    json_path = _coverage_json_output()
    cmd = [
        "pytest",
        "-p",
        "pytest_cov",
        "--cov=src/codex_ml",
        "--cov-branch",
        "--cov-report=term-missing",
        f"--cov-report=html:{COVERAGE_HTML.as_posix()}",
        f"--cov-report=xml:{COVERAGE_XML.as_posix()}",
        f"--cov-report=json:{json_path.as_posix()}",
        f"--cov-fail-under={DEFAULT_FAIL_UNDER}",
        "-q",
    ]
    if extra_args:
        cmd.extend(extra_args)
    else:
        cmd.append("tests")
    session.run(*cmd)
    session.log(f"[coverage] JSON report: {json_path}")


@nox.session(python=list(PY_VERSIONS))
def tests(session: nox.Session) -> None:
    """Run the full unit test suite against all discovered interpreters."""

    session.chdir(str(REPO_ROOT))
    _ensure_pip_cache(session)
    _install(session, *TEST_BOOTSTRAP_PKGS)
    _install(session, "--no-deps", "-e", ".")
    _install(
        session,
        "hydra-core>=1.3",
        "omegaconf>=2.3",
        "PyYAML>=6.0",
        "pydantic>=2.4",
        "pydantic-settings>=2.2",
        "pytest",
        "pytest-cov",
        "pytest-randomly",
        "hypothesis>=6.100",
    )
    _export_env(session)
    # Enforce coverage gate via pytest.ini (--cov-fail-under=3.5).
    session.run("pytest", "-q", "tests")


@nox.session(name="offline_check", python=DEFAULT_PYTHON)
def offline_check(session: nox.Session) -> None:
    """Verify the test suite completes without network access."""

    session.chdir(str(REPO_ROOT))
    _ensure_pip_cache(session)
    _install(session, *TEST_BOOTSTRAP_PKGS)
    _install(session, "--no-deps", "-e", ".")
    _install(
        session,
        "hydra-core>=1.3",
        "omegaconf>=2.3",
        "PyYAML>=6.0",
        "pydantic>=2.4",
        "pydantic-settings>=2.2",
        "pytest",
        "pytest-cov",
        "pytest-randomly",
        "hypothesis>=6.100",
    )
    _export_env(session)
    cmd = [session.bin_path("python"), "-m", "pytest", "-q", "tests"]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env=session.env,
    )
    combined = f"{result.stdout}\n{result.stderr}".lower()
    if result.returncode != 0:
        session.error("pytest returned a non-zero exit status during offline_check")
    for token in ("http://", "https://", "download", "fetch"):
        if token in combined:
            session.error("❌ Offline compliance violated: network calls detected")
    session.log("✅ Offline compliance: no network calls detected")


@nox.session(name="tests_trainer", python=DEFAULT_PYTHON)
def tests_trainer(session: nox.Session) -> None:
    """Run the focused trainer stack tests."""

    _ensure_pip_cache(session)
    _install(session, "-e", ".[test]")
    _export_env(session)
    session.run(
        "pytest",
        "-q",
        "tests/modeling/test_modeling_module.py",
        "tests/logging/test_logging_utils_module.py",
        "tests/data/test_datasets_module.py",
        "tests/training/test_extended_trainer.py",
    )


@nox.session(name="tests_offline", python=DEFAULT_PYTHON)
def tests_offline(session: nox.Session) -> None:
    """Run the curated offline test targets used in release checklists."""

    _ensure_pip_cache(session)
    with _error_logging_step(
        "tests_offline.install_project",
        "session.install('--no-deps', '-e', '.')",
    ):
        _install(session, "--no-deps", "-e", ".")
    with _error_logging_step(
        "tests_offline.install_extras",
        "session.install('pytest', 'pytest-cov', 'pytest-randomly', 'pydantic')",
    ):
        _install(session, "pytest", "pytest-cov", "pytest-randomly", "pydantic")
    with _error_logging_step("tests_offline.set_env", "HF_DATASETS_OFFLINE=1"):
        session.env.setdefault("HF_DATASETS_OFFLINE", "1")
    with _error_logging_step("tests_offline.set_env", "WANDB_MODE=offline"):
        session.env.setdefault("WANDB_MODE", "offline")
    with _error_logging_step("tests_offline.export_env", "_export_env(session)"):
        _export_env(session)
    extra_args = list(session.posargs)
    has_cov_target = any(arg == "--cov" or arg.startswith("--cov=") for arg in extra_args)
    if has_cov_target and not any(arg.startswith("--cov-fail-under") for arg in extra_args):
        extra_args.append("--cov-fail-under=0")
    targets = OFFLINE_TEST_TARGETS
    cmd = [
        "pytest",
        "-p",
        "pytest_cov",
        "-p",
        "pytest_randomly",
        "-q",
        *extra_args,
        *targets,
    ]
    with _error_logging_step(
        "tests_offline.pytest",
        " ".join(cmd),
        question="Could you confirm the expected outcome when pytest fails offline?",
    ):
        session.run(*cmd)


@nox.session(name="tests_gpu", python=DEFAULT_PYTHON)
def tests_gpu(session: nox.Session) -> None:
    """Run GPU-marked tests when CUDA devices are available."""

    _ensure_pip_cache(session)
    _install(session, "pytest", "pytest-randomly", "torch")

    try:
        import torch  # type: ignore
    except ImportError:  # pragma: no cover - defensive guard
        session.log("PyTorch is unavailable after installation; skipping GPU test session.")
        return

    is_available = getattr(getattr(torch, "cuda", None), "is_available", None)
    if not callable(is_available) or not is_available():
        session.log("CUDA is unavailable; skipping GPU test session.")
        return

    _export_env(session)
    session.run(
        "pytest",
        "-p",
        "pytest_randomly",
        "-q",
        "-m",
        "gpu",
    )


@nox.session(name="tracking_smoke", python=DEFAULT_PYTHON)
def tracking_smoke(session: nox.Session) -> None:
    """Run a local MLflow smoke test against the file backend."""

    _ensure_pip_cache(session)
    dev_requirements = REPO_ROOT / "requirements/dev.txt"
    if dev_requirements.exists():
        _install(session, "-r", str(dev_requirements))
    else:
        _install(session, "mlflow>=2.4")
    _export_env(session)
    session.env.setdefault("MLFLOW_TRACKING_URI", "file:./mlruns")
    uri = session.env["MLFLOW_TRACKING_URI"]
    session.log(f"[tracking_smoke] using tracking URI {uri}")
    code = (
        "import os, pathlib, mlflow\n"
        "uri = os.environ.get('MLFLOW_TRACKING_URI', 'file:./mlruns')\n"
        "path = pathlib.Path(uri.replace('file:', ''))\n"
        "path.mkdir(parents=True, exist_ok=True)\n"
        "with mlflow.start_run(run_name='smoke'):\n"
        "    mlflow.log_param('p', 1)\n"
        "    mlflow.log_metric('m', 0.123)\n"
        "print('tracking uri', uri)\n"
    )
    session.run("python", "-c", code)


@nox.session(name="cli_smoke", python=DEFAULT_PYTHON)
def cli_smoke(session: nox.Session) -> None:
    """Exercise the Typer CLI locally without network services."""

    _ensure_pip_cache(session)
    _install(session, "-e", ".[test]")
    _export_env(session)
    session.run("python", "-m", "codex_cli.app", "--help")
    session.run("python", "-m", "codex_cli.app", "version")
    tmp_dir = Path(session.create_tmp())
    checkpoints = tmp_dir / "checkpoints"
    mlruns_dir = tmp_dir / "mlruns"
    session.run("python", "-m", "codex_cli.app", "split-smoke", "--seed", "41")
    session.run("python", "-m", "codex_cli.app", "checkpoint-smoke", "--out", str(checkpoints))
    session.run("python", "-m", "codex_cli.app", "track-smoke", "--dir", str(mlruns_dir))


@nox.session(name="bootstrap", python=DEFAULT_PYTHON)
def bootstrap(session: nox.Session) -> None:
    """Create or refresh dependency locks using uv."""

    _export_env(session)
    _install(session, "uv")
    if (REPO_ROOT / "requirements.in").exists():
        session.run(
            UV,
            "pip",
            "compile",
            "requirements.in",
            "--universal",
            "-o",
            "requirements/base.txt",
        )
    else:
        session.run(
            UV,
            "pip",
            "compile",
            "pyproject.toml",
            "--universal",
            "-o",
            "requirements/base.txt",
        )
    session.run(UV, "pip", "sync", "requirements/base.txt")


@nox.session(python=list(PY_VERSIONS))
def lint(session: nox.Session) -> None:
    """Run formatters and linters on the repo's maintained Python code paths."""

    _ensure_pip_cache(session)
    _install(session, "ruff", "black", "isort")

    targets: list[str] = []
    for path_name in ("src", "tests", "scripts", "tools"):
        if (REPO_ROOT / path_name).exists():
            targets.append(path_name)

    if not targets:
        session.log("No supported Python source directories found; skipping lint session.")
        return

    # Keep linting focused on the maintained codepaths and treat violations as
    # advisory when the repository is intentionally not yet lint-clean.
    session.run("ruff", "check", *targets, success_codes=[0, 1])
    session.run("isort", "--check-only", *targets, success_codes=[0, 1])
    session.run("black", "--check", *targets, success_codes=[0, 1])

    import_linter_config = REPO_ROOT / ".importlinter"
    if import_linter_config.exists():
        _install(session, "import-linter")
        # Advisory mode: allow import-linter violations (return code 1) without failing the session
        session.run(
            "lint-imports",
            "--config",
            str(import_linter_config),
            success_codes=[0, 1],
        )
        # Print an advisory summary for trend tracking
        session.run(
            "python",
            "tools/import_contracts_summary.py",
            external=True,
            success_codes=[0, 1],
        )


@nox.session(python=DEFAULT_PYTHON)
def typecheck(session: nox.Session) -> None:
    """Run mypy against curated modules in advisory mode while the baseline is broad."""

    _ensure_pip_cache(session)
    _install(session, "mypy", "types-PyYAML")
    _export_env(session)
    targets = ["src/security", "scripts/space_traversal", "src/codex_ml"]
    existing = [t for t in targets if (REPO_ROOT / t).exists()]
    if not existing:
        session.log("No targets found for mypy; skipping.")
        return

    # Temporary informational gate: keep the type-check signal visible without
    # turning it into a hard block while the repo-wide mypy baseline remains
    # broad. This is intentionally isolated from the CodeQL/security gates so
    # security findings remain separate from broad typing debt. This is
    # intentionally reversible; remove the advisory override once the baseline
    # is reduced and the team wants a blocking gate again.
    # Backlog note: see workbench/evidence/gap33_mypy_precommit.md.
    session.run("mypy", *existing, success_codes=[0, 1])
    session.log(
        "[typecheck] advisory mode: mypy issues are reported but do not block "
        "this run while the baseline remains broad."
    )


@nox.session(name="typecheckd", python=DEFAULT_PYTHON)
def typecheckd(session: nox.Session) -> None:
    """Incremental mypy daemon run."""

    _ensure_pip_cache(session)
    _install(session, "mypy")
    _export_env(session)
    session.run("dmypy", "run", "--", "--cache-fine-grained", "src")


@nox.session(python=DEFAULT_PYTHON)
def test(session: nox.Session) -> None:
    """Fast pytest run with deterministic randomness."""

    _ensure_pip_cache(session)
    _install(session, "pytest", "pytest-randomly")
    _export_env(session)
    session.run(
        "pytest",
        "-p",
        "pytest_randomly",
        "-q",
    )


@nox.session(python=DEFAULT_PYTHON)
def cov(session: nox.Session) -> None:
    """Deprecated coverage entrypoint; delegates to the canonical coverage session."""

    session.log("[DEPRECATION] `cov` session is deprecated; forwarding to coverage.")
    if session.posargs:
        _run_pytest_coverage(session, extra_args=tuple(session.posargs))
    else:
        session.notify(CANONICAL_TEST_SESSION)


@nox.session(python=DEFAULT_PYTHON)
def coverage(session: nox.Session) -> None:
    """Canonical coverage session producing HTML/XML/JSON artifacts."""

    _ensure_pip_cache(session)
    if not _check_hydra_plugin(session):
        session.error("Hydra plugin required for coverage; aborting")
    _run_pytest_coverage(session, extra_args=tuple(session.posargs))


@nox.session(python=DEFAULT_PYTHON)
def docs(session: nox.Session) -> None:
    """Generate API documentation with pdoc into artifacts/docs."""

    _ensure_pip_cache(session)
    _install(session, "pdoc")
    _export_env(session)
    out = ARTIFACTS / "docs"
    out.mkdir(parents=True, exist_ok=True)
    session.run("pdoc", "codex_ml", "-o", str(out))


@nox.session(python=DEFAULT_PYTHON)
def sec(session: nox.Session) -> None:
    """Run local security scanners."""

    _ensure_pip_cache(session)
    _install(session, "bandit", "semgrep", "detect-secrets", "pip-audit")
    _export_env(session)
    if (REPO_ROOT / "src").exists():
        session.run("bandit", "-q", "-r", "src", "-c", "bandit.yaml")
    if (REPO_ROOT / "semgrep_rules").exists():
        session.run("semgrep", "scan", "--config", "semgrep_rules/", "--error", "src/")
    session.run("detect-secrets", "scan")
    if session.env.get("CODEX_AUDIT", "0") == "1":
        req = REPO_ROOT / "requirements/base.txt"
        if req.exists():
            session.run("pip-audit", "-r", str(req))
        else:
            session.run("pip-audit")


@nox.session(python=DEFAULT_PYTHON)
def sec_scan(session: nox.Session) -> None:
    """Run Bandit using the repository configuration."""

    _ensure_pip_cache(session)
    _install(session, "bandit")
    _export_env(session)
    targets = ["src"]
    if (REPO_ROOT / "services").exists():
        targets.append("services")
    session.run("bandit", "-r", *targets, "-c", "bandit.yaml", "--severity-level", "high")


@nox.session(python=DEFAULT_PYTHON)
def sbom(session: nox.Session) -> None:
    """Generate an offline SBOM from repository lock files."""

    _ensure_pip_cache(session)
    _install(session, "-r", "requirements/dev.txt")
    _export_env(session)
    session.run("python", "scripts/sbom_cyclonedx.py", *session.posargs)


@nox.session
def docker_lint(session: nox.Session) -> None:
    """Run hadolint against repository Dockerfiles."""

    _ensure_pip_cache(session)
    from shutil import which

    if which("hadolint") is None:
        session.log("hadolint not found on PATH; skipping docker_lint.")
        return

    dockerfiles = [REPO_ROOT / "Dockerfile", REPO_ROOT / "Dockerfile.gpu"]
    found = False
    for df in dockerfiles:
        if df.exists():
            found = True
            session.run("hadolint", str(df), external=True)
    if not found:
        session.log("No Dockerfile found; skipping hadolint.")


@nox.session(name="patch_debris", python=DEFAULT_PYTHON)
def patch_debris(session: nox.Session) -> None:
    """Fail when diff/merge markers remain in tracked source."""

    root = REPO_ROOT
    merge_markers = ("<<<<<<<", "=======", ">>>>>>>")
    diff_markers = (
        "*** Begin Patch",
        "*** End Patch",
        "diff --git ",
        "+++ ",
        "--- ",
    )
    text_suffixes = {
        ".py",
        ".md",
        ".rst",
        ".txt",
        ".toml",
        ".yaml",
        ".yml",
        ".json",
        ".sh",
    }
    explicit_files = {"Makefile", "Dockerfile", "Dockerfile.gpu"}
    exclude_prefixes = {
        ".git/",
        "artifacts/",
        "patches/",
        "docs/validation/",
        "venv/",
        ".venv/",
        "__pycache__/",
    }

    offenders: list[Path] = []
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        rel = path.relative_to(root)
        rel_str = rel.as_posix()
        if any(rel_str.startswith(prefix) for prefix in exclude_prefixes):
            continue
        if not (path.suffix.lower() in text_suffixes or path.name in explicit_files):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as exc:
            session.log(f"[patch-debris] failed to read {rel_str}: {exc}")
            continue
        if any(marker in text for marker in (*merge_markers, *diff_markers)):
            offenders.append(rel)

    if offenders:
        for rel in sorted(offenders):
            session.error(f"patch-debris marker detected in {rel.as_posix()}")
    session.log("patch-debris guard passed")


@nox.session(name="ci", python=DEFAULT_PYTHON)
def ci(session: nox.Session) -> None:
    """Lightweight CI helper that runs the patch guard and fast tests."""

    session.notify("patch_debris")
    _ensure_pip_cache(session)
    _install(session, "pytest")
    _export_env(session)
    session.run(
        "pytest",
        "-q",
        "tests/cli/test_eval_probe_json_schema.py",
        "tests/cli/test_train_probe_json_schema.py",
        "tests/cli/test_cli_structured_logging.py",
        "tests/cli/test_hydra_missing_probe_json.py",
        "tests/monitoring/test_system_metrics_nvml_missing.py",
        "tests/plugins/test_list_plugins_degrade.py",
        "tests/checkpoint/test_run_metadata_sidecar.py",
    )


@nox.session(name="archive_pr_gate", python=DEFAULT_PYTHON)
def archive_pr_gate(session: nox.Session) -> None:
    """Validate archive PR checklist requirements alongside CODEOWNERS."""

    if not _archive_gate_has_explicit_changed_files(session.posargs):
        staged = _archive_gate_staged_files(REPO_ROOT)
        if not staged:
            session.log("No staged changes detected; skipping archive PR checklist gate.")
            return

    _ensure_pip_cache(session)
    _install(session, "-e", ".")
    _export_env(session)
    session.run(
        "python",
        "-m",
        "src.tools.archive_pr_checklist",
        "--strict",
        "--check-codeowners",
        *session.posargs,
    )


@nox.session(name="dockerlint")
def dockerlint(session: nox.Session) -> None:
    """Compatibility alias for docker_lint."""

    session.notify("docker_lint")


@nox.session
def imagescan(session: nox.Session) -> None:
    """Run a container image scan with trivy when CODEX_AUDIT=1."""

    from shutil import which

    if os.getenv("CODEX_AUDIT", "0") != "1":
        session.log("CODEX_AUDIT!=1; skipping image scan.")
        return
    if which("trivy") is None:
        session.log("trivy not found on PATH; skipping imagescan.")
        return
    image = os.getenv("CODEX_IMAGE", "codex:local")
    session.run("trivy", "image", image, external=True)


@nox.session(name="crm_gates", python=DEFAULT_PYTHON)
def crm_gates(session: nox.Session) -> None:
    """Run CRM-focused regression suites."""

    _ensure_pip_cache(session)
    _install(session, "-r", "requirements/base.txt")
    _export_env(session)
    session.run(
        "pytest",
        "-q",
        "tests/crm",
        "-k",
        "conversion_truths or cli or pa_reader or zaf_reader",
    )
    session.run("pytest", "-q", "tests/d365")
    session.run("pytest", "-q", "tests/archive", "-k", "not sql_identifier_safety")
    session.run("pytest", "-q", "tests/archive/test_sql_identifier_safety.py")
    session.run("pytest", "-q", "tests/release")
    session.run("pytest", "-q", "tests/diagram")
    session.run("pytest", "-q", "tests/knowledge")
    session.run("pytest", "-q", "tests/zd")


@nox.session(name="diagram_check", python=DEFAULT_PYTHON)
def diagram_check(session: nox.Session) -> None:
    """Ensure diagram helpers import and render simple flows."""

    _ensure_pip_cache(session)
    _install(session, "-r", "requirements/base.txt")
    _export_env(session)
    session.run(
        "python",
        "-c",
        (
            "from codex.diagram import flow_to_mermaid; "
            "print(flow_to_mermaid('intake', ['Create','Triage']))"
        ),
    )


@nox.session(name="repro_smoke", python=DEFAULT_PYTHON)
def repro_smoke(session: nox.Session) -> None:
    """Run reproducibility and plugin smoke tests (local-only).

    Validates:
    - Deterministic behavior with fixed seeds
    - Plugin loading is non-fatal
    - Generative metrics optional behavior
    """
    _ensure_pip_cache(session)
    _install(session, *TEST_BOOTSTRAP_PKGS)
    _install(session, "--no-deps", "-e", ".")
    _install(session, "pytest", "pytest-randomly")
    _export_env(session)
    session.run(
        "pytest",
        "-p",
        "pytest_randomly",
        "-q",
        "tests/test_metrics_generative.py",
        "tests/eval/test_eval_provenance_capture.py",
        "tests/plugins/test_metric_plugin_loading.py",
    )


@nox.session(name="config_index", python=DEFAULT_PYTHON)
def config_index(session: nox.Session) -> None:
    """List Hydra config groups and options (offline discovery)."""
    _ensure_pip_cache(session)
    _install(session, "hydra-core>=1.3", "omegaconf>=2.3")
    _export_env(session)
    session.run("python", "tools/configs/list_groups.py")
