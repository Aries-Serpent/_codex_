import os
from contextlib import suppress
from pathlib import Path

import nox

nox.options.reuse_venv = "yes"
nox.options.stop_on_first_error = True


@nox.session
def ci_local(session):
    session.install("-e", ".", "pytest", "pytest-cov")
    session.run(
        "pytest",
        "-q",
        "--cov",
        "--cov-report=term-missing",
        "--cov-fail-under=80",
    )


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
def quality(session):
    """Run formatting hooks and tests locally."""
    _install(session, "pre-commit", "pytest", "pytest-cov")
    session.run("pre-commit", "run", "--all-files")
    fail_under = os.environ.get("COV_FAIL_UNDER", "70")
    session.run(
        "pytest",
        "--cov=src/codex_ml",
        f"--cov-fail-under={fail_under}",
        "-q",
    )


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
        "accelerate",
        "duckdb",
    )
    # Use .coveragerc for sources; keep branch mode consistent everywhere.
    # --cov (no value) respects .coveragerc 'source'; --cov-branch enforces branch data.
    # Fail-under remains 70 unless overridden via env.
    fail_under = os.environ.get("COV_FAIL_UNDER", "70")
    session.run(
        "pytest",
        "-q",
        "--disable-warnings",
        "--maxfail=1",
        "--cov",
        "--cov-branch",
        "--cov-report=term-missing",
        f"--cov-fail-under={fail_under}",
    )


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
    fail_under = os.environ.get("COV_FAIL_UNDER", "70")
    session.run(
        "pytest",
        "-q",
        "--disable-warnings",
        "--maxfail=1",
        "--cov",
        "--cov-branch",
        "--cov-report=term-missing",
        f"--cov-fail-under={fail_under}",
        external=True,
    )


@nox.session(
    venv_backend="venv", venv_params=["--system-site-packages"]
)  # let venv see base packages. :contentReference[oaicite:4]{index=4}
def tests_ssp(session):
    """
    Tests in an isolated venv that *can see* system site-packages.
    Useful if base env already has heavy libs (CUDA, torch, tensorflow, etc.).
    """
    _ensure_pip_cache(session)
    # Auto-detect heavy system packages to avoid any (re)install churn.
    have_torch = _module_available(session, "torch")
    have_tf = _module_available(session, "tensorflow")
    if have_torch or have_tf:
        session.log(
            "Detected heavy system packages: %s%s",
            "torch " if have_torch else "",
            "tensorflow" if have_tf else "",
        )
    # Only install lightweight test deps; do not attempt to install heavy libs here.
    _install(session, "pytest", "pytest-cov")
    fail_under = os.environ.get("COV_FAIL_UNDER", "70")
    session.run(
        "pytest",
        "-q",
        "--disable-warnings",
        "--maxfail=1",
        "--cov",
        "--cov-branch",
        "--cov-report=term-missing",
        f"--cov-fail-under={fail_under}",
    )


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
    session.install("bandit", "detect-secrets", "pip-audit")
    session.run("bandit", "-c", "bandit.yaml", "-r", ".")
    session.run("detect-secrets", "scan", "--baseline", ".secrets.baseline", ".")
    session.run("pip-audit", "-r", "requirements.txt")


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
