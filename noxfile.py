import os
from contextlib import suppress
from pathlib import Path

import nox

# Prefer reusing environments to avoid reinstalls.
# CLI equivalent: `nox -r` (alias of --reuse-existing-virtualenvs / --reuse-venv=yes).
# See Nox docs for reuse & backends (including `uv` and `--no-venv`).
# https://nox.thea.codes/en/stable/usage.html
nox.options.reuse_existing_virtualenvs = (
    True  # `nox -r` equivalent (reuse venvs). :contentReference[oaicite:14]{index=14}
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


@nox.session
def lint(session):
    _ensure_pip_cache(session)
    _install(session, "ruff", "black", "isort")
    session.run("ruff", "check", ".")
    session.run("black", "--check", ".")
    session.run("isort", "--check-only", ".")


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
    _install(session, "pytest", "pytest-cov", "fastapi", "httpx", "torch")
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


@nox.session(
    venv_backend="none"
)  # run directly in the current interpreter; no venv. :contentReference[oaicite:16]{index=16}
def tests_sys(session):
    """
    Run tests in the *Codex initial* environment for minimal overhead.
    Prefers `uv` tooling with a safe fallback to pip, and honors PIP_CACHE_DIR.
    """
    _ensure_pip_cache(session)
    # If a lock/requirements file is provided, prefer idempotent sync.
    sync_target = os.environ.get("UV_SYNC_FILE")  # e.g., "requirements.txt"
    if _has_uv(session) and sync_target and Path(sync_target).is_file():
        session.run(
            "uv", "pip", "sync", sync_target, external=True
        )  # idempotent. :contentReference[oaicite:17]{index=17}
    else:
        # Fall back to installing minimal deps if pytest isn't available.
        with suppress(Exception):
            session.run("pytest", "--version")
        if session.last_result and session.last_result.exit_code != 0:
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
        external=True,  # using tools from the host env
    )


@nox.session(
    venv_backend="venv", venv_params=["--system-site-packages"]
)  # let venv see base packages. :contentReference[oaicite:18]{index=18}
def tests_ssp(session):
    """
    Tests in an isolated venv that *can see* system site-packages.
    Useful if base env already has heavy libs (CUDA, torch, etc.).
    """
    _ensure_pip_cache(session)
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
