import nox

@nox.session(python=["3.9", "3.10", "3.11", "3.12"])
def tests(session):
    session.install("pytest", "charset-normalizer>=3.0.0", "chardet>=5.0.0")
    session.run("pytest", "-q")

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
