import nox

# Reuse virtualenvs between runs to avoid slow reinstalls.
# Preferred spelling since Nox 2025.x:
nox.options.reuse_existing_virtualenvs = True

COV_THRESHOLD = 70


@nox.session
def lint(session):
    session.install("ruff", "black", "isort")
    session.run("ruff", "check", ".")
    session.run("black", "--check", ".")
    session.run("isort", "--check-only", ".")


@nox.session
def quality(session):
    """Run formatting hooks and tests locally."""
    session.install("pre-commit", "pytest", "pytest-cov")
    session.run("pre-commit", "run", "--all-files")
    session.run(
        "pytest",
        "--cov=src/codex_ml",
        f"--cov-fail-under={COV_THRESHOLD}",
        "-q",
    )


@nox.session
def coverage(session):
    session.install("pytest", "pytest-cov")
    session.run("coverage", "erase", external=True)
    session.env["COVERAGE_RCFILE"] = ".coveragerc"
    session.run(
        "pytest",
        "--cov-config=.coveragerc",
        "--cov-branch",
        "--cov",
        "--cov-report=term",
        "--cov-report=xml",
        f"--cov-fail-under={COV_THRESHOLD}",
        *session.posargs,
    )


@nox.session
def tests(session):
    """Thin wrapper to delegate to the coverage gate."""
    session.notify("coverage")


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
