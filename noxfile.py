import os
from contextlib import suppress
from pathlib import Path

import nox

# Prefer reusing environments to avoid reinstalls.
# CLI equivalent: `nox -r` (alias of --reuse-existing-virtualenvs / --reuse-venv=yes).
# See Nox docs for reuse & backends (including `uv` and `--no-venv`).
# https://nox.thea.codes/en/stable/usage.html
nox.options.reuse_existing_virtualenvs = True


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


@nox.session
def lint(session):
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
    _install(session, "pytest", "pytest-cov")
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
    """Install runtime dependencies before running the coverage gate."""

    # Install a CPU-only wheel for torch to avoid pulling large CUDA runtimes.
    _install(
        session,
        "torch==2.3.1+cpu",
        "--index-url",
        "https://download.pytorch.org/whl/cpu",
    )

    # Install remaining requirements excluding torch, then delegate to coverage.
    base_requirements = [
        req
        for req in Path("requirements/base.txt").read_text().splitlines()
        if req and not req.startswith("torch")
    ]
    _install(
        session,
        "pytest",
        "pytest-cov",
        "langchain",
        "charset-normalizer>=3.0.0",
        "chardet>=5.0.0",
        *base_requirements,
        "mlflow",
        "httpx",
        "peft==0.10.0",
        "click",
        "fastapi",
        "accelerate>=0.27.0",
    )

    coverage(session)


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
