import nox

COV_THRESHOLD = 80


@nox.session
def lint(session):
    session.install("ruff")
    session.run("ruff", "check", "--fix", ".")
    session.run("ruff", "format", ".")


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


@nox.session(python=["3.9", "3.10", "3.11", "3.12"])
def tests(session):
    session.install(
        "pytest",
        "pytest-cov",
        "charset-normalizer>=3.0.0",
        "chardet>=5.0.0",
    )
    session.run(
        "pytest",
        "--cov=src/codex_ml",
        f"--cov-fail-under={COV_THRESHOLD}",
        "-q",
        *session.posargs,
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


@nox.session
def coverage(session):
    session.install("pytest", "pytest-cov")
    session.run(
        "pytest",
        "--cov=src/codex_ml",
        "--cov-report=xml",
        f"--cov-fail-under={COV_THRESHOLD}",
        *session.posargs,
    )
