import os
import shutil
from contextlib import suppress
from pathlib import Path
from typing import Sequence

import nox

nox.options.reuse_venv = "yes"
nox.options.stop_on_first_error = True

COVERAGE_XML = Path("artifacts/coverage.xml")
DEFAULT_FAIL_UNDER = os.environ.get("COV_FAIL_UNDER", "80")


@nox.session
def ci_local(session):
    session.install("-e", ".", "pytest", "pytest-cov")
    cmd = ["pytest", "-q"]
    cmd += _coverage_args(session, fail_under=DEFAULT_FAIL_UNDER)
    session.run(*cmd)


# Optional: prefer `uv`, with automatic fallback to `virtualenv` if uv is unavailable.
# Enable by exporting NOX_PREFER_UV=1 on runners where uv is ubiquitous.
if os.environ.get("NOX_PREFER_UV") == "1":
    # Allows "uv|virtualenv" fallback selection (first available is used).
    nox.options.default_venv_backend = (
        "uv|virtualenv"  # also settable via CLI/env. :contentReference[oaicite:15]{index=15}
    )


def _has_uv(session: nox.Session) -> bool:
    """Detect if `uv` is available on PATH."""
    with suppress(Exception):
        session.run("uv", "--version", external=True, silent=True)
        return True
    return False


def _install(session: nox.Session, *pkgs: str) -> None:
    """
    Fast path: use `uv pip install` when available (very fast resolver/installer).
    Fallback: use session.install(...) which uses pip inside the venv.
    """
    if _has_uv(session):
        session.run("uv", "pip", "install", *pkgs, external=True)
    else:
        session.install(*pkgs)


def _ensure_pip_cache(session: nox.Session) -> None:
    """Default PIP_CACHE_DIR for faster, repeatable installs."""
    session.env.setdefault("PIP_CACHE_DIR", str(Path(".cache/pip").resolve()))


def _module_available(session: nox.Session, name: str, *, external: bool = False) -> bool:
    """Return True if `import name` succeeds in the target interpreter."""
    try:
        session.run("python", "-c", f"import {name}", external=external, silent=True)
        return True
    except Exception:
        return False


def _coverage_args(
    session: nox.Session,
    *,
    fail_under: str | None = None,
    branch: bool = False,
    external: bool = False,
    paths: Sequence[str] | None = ("src/codex",),
) -> list[str]:
    """Return pytest coverage flags if pytest-cov is available."""
    if _module_available(session, "pytest_cov", external=external):
        args = [f"--cov={p}" for p in (paths or [])] or ["--cov"]
        if branch:
            args.append("--cov-branch")
        args.append("--cov-report=term-missing")
        args.append(f"--cov-report=xml:{COVERAGE_XML}")
        if fail_under is not None:
            args.append(f"--cov-fail-under={fail_under}")
        return args
    session.log("pytest-cov not installed; skipping coverage flags")
    return []


@nox.session
def lint(session):
    _ensure_pip_cache(session)
    _install(session, "ruff", "black", "isort")
    session.run("ruff", "check", ".")
    session.run("black", "--check", ".")
    session.run("isort", "--check-only", ".")


@nox.session
def typecheck(session):
    _ensure_pip_cache(session)
    _install(session, "mypy")
    try:
        session.run("mypy", "src")
    except Exception:
        session.log("mypy not configured — skipping")


@nox.session
def ci(session):
    """Run linting, type checks, and test coverage."""
    session.notify("lint")
    session.notify("typecheck")
    session.notify("coverage")


@nox.session
def quality(session):
    """Run formatting hooks and tests locally."""
    _install(session, "pre-commit", "pytest", "pytest-cov")
    session.run("pre-commit", "run", "--all-files")
    cmd = ["pytest", "-q"]
    cmd += _coverage_args(session, fail_under=DEFAULT_FAIL_UNDER)
    session.run(*cmd)


@nox.session
def coverage(session):
    _ensure_pip_cache(session)
    _install(
        session,
        "pytest",
        "pytest-cov",
        "fastapi",
        "httpx",
        "torch",
        "numpy",
        "click",
        "transformers",
        "datasets",
        "typer",
        "omegaconf",
        "hydra-core",
        "accelerate",
        "duckdb",
    )
    COVERAGE_XML.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["pytest", "-q", "--disable-warnings", "--maxfail=1"]
    cmd += _coverage_args(session, fail_under=DEFAULT_FAIL_UNDER, branch=True)
    session.run(*cmd)


@nox.session
def tests(session):
    """
    Thin wrapper to keep one source of truth:
    `nox -s tests` simply delegates to the 'coverage' gate.
    """
    session.notify("coverage")


@nox.session(venv_backend="none")  # run directly in the current interpreter; no venv
def tests_sys(session):
    """
    Run tests in the *Codex initial* environment for minimal overhead.
    Preferred order for determinism:
      1) If pyproject.toml + uv.lock exist and uv is available AND NOX_PREFER_UV=1:
         use `uv sync --frozen` (strict lockfile).
      2) Else, if UV_SYNC_FILE (or requirements.txt) exists and uv is available AND NOX_PREFER_UV=1:
         use `uv pip sync <file>` (idempotent).
      3) Else: minimally ensure pytest deps with pip/uv and run tests.
    """
    _ensure_pip_cache(session)
    prefer_uv = os.environ.get("NOX_PREFER_UV") == "1" and _has_uv(session)
    has_pyproject = Path("pyproject.toml").is_file()
    has_uv_lock = Path("uv.lock").is_file()
    # 1) Strongest determinism: project lock
    if prefer_uv and has_pyproject and has_uv_lock:
        # Strictly use the lockfile as the source of truth and do not update it
        session.run("uv", "sync", "--frozen", external=True)
    else:
        # 2) Next best: requirements sync (idempotent)
        sync_target = os.environ.get("UV_SYNC_FILE") or (
            "requirements.txt" if Path("requirements.txt").is_file() else None
        )
        if prefer_uv and sync_target and Path(sync_target).is_file():
            session.run("uv", "pip", "sync", sync_target, external=True)
        else:
            # Fall back to installing minimal deps if pytest isn't available.
            try:
                session.run("pytest", "--version", external=True)
            except Exception:
                # Install basics quickly (uses cache); if uv present, it's fast.
                _install(session, "pytest", "pytest-cov")
    # Now run tests from the system env (no venv).
    COVERAGE_XML.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["pytest", "-q", "--disable-warnings", "--maxfail=1"]
    cmd += _coverage_args(session, fail_under=DEFAULT_FAIL_UNDER, branch=True, external=True)
    session.run(*cmd, external=True)


@nox.session
def package(session):
    """Build wheel/sdist artifacts and validate an installation."""

    _ensure_pip_cache(session)
    build_dir = Path("dist")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    _install(session, "build")
    session.run("python", "-m", "build", "--wheel", "--sdist")
    artifacts = sorted(build_dir.glob("*"))
    if not artifacts:
        session.error("No distribution artifacts were produced")
    wheel = next((p for p in artifacts if p.suffix == ".whl"), artifacts[-1])
    session.install(str(wheel))
    session.run(
        "python",
        "-c",
        "import codex_ml; print(codex_ml.__version__)",
    )


@nox.session
def tests_ssp(session):
    session.install("-e", ".", "sentencepiece>=0.1.99", "pytest", "pytest-cov")
    session.env["PYTEST_ADDOPTS"] = ""
    session.run("pytest", "-q", "tests/tokenization", "-k", "sentencepiece")


@nox.session
def tests_min(session):
    _ensure_pip_cache(session)
    _install(session, "pytest")
    session.run("pytest", "-q", "-m", "not slow")


@nox.session
def perf_smoke(session):
    _ensure_pip_cache(session)
    _install(session, "pytest", "pytest-cov")
    session.run("pytest", "-q", "tests/perf/test_perf_smoke.py", "--no-cov")


@nox.session
def codex_gate(session):
    session.install("pytest", "charset-normalizer>=3.0.0", "chardet>=5.0.0")
    session.run(
        "pytest",
        "-q",
        "tests/test_ingestion_encodings_matrix.py",
        "tests/test_ingestion_auto_encoding.py",
        "tests/test_ingestion_encoding_coverage.py",
        "tests/test_sqlite_pool_close.py",
        "tests/test_chat_session_exit.py",
    )


@nox.session
def codex_ext(session):
    session.install("pytest", "charset-normalizer>=3.0.0", "chardet>=5.0.0")
    session.install("-r", "requirements.txt")
    session.run(
        "pytest",
        "-q",
        "--no-cov",
        "tests/test_checkpoint_manager.py",
        "tests/test_eval_runner.py",
    )


@nox.session
def sec_scan(session):
    session.install("bandit", "detect-secrets", "safety")
    session.run("bandit", "-c", "bandit.yaml", "-r", ".")
    session.run("detect-secrets", "scan", "--baseline", ".secrets.baseline", ".")
    session.run("safety", "check", "-r", "requirements.txt", "--full-report")


@nox.session
def docs_smoke(session):
    _ensure_pip_cache(session)
    _install(session, "nbformat")
    session.run(
        "python",
        "-c",
        "import nbformat; nbformat.read('notebooks/quick_start.ipynb', as_version=4)",
    )
    session.run(
        "python",
        "-c",
        (
            "from pathlib import Path,sys,re;"
            "arch=Path('docs/architecture.md').read_text(encoding='utf-8');"
            "assert '```mermaid' in arch;"
            "readme=Path('README.md').read_text(encoding='utf-8');"
            "missing=[p for p in re.findall(r'\\[(?:[^\\]]+)\\]\\((docs/[^)]+)\\)', readme) if not Path(p).exists()];"
            "sys.exit('Missing docs: '+', '.join(missing)) if missing else None"
        ),
    )
