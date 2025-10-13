import shutil

import nox

# Auto-detect available interpreters to avoid session bootstrap failures.
# Falls back to 3.12 only if no others are found.
_CANDIDATES = ("3.12", "3.11", "3.10")
PY_VERSIONS = tuple(v for v in _CANDIDATES if shutil.which(f"python{v}")) or ("3.12",)


@nox.session(python=list(PY_VERSIONS))
def tests(session: nox.Session) -> None:
    """Run unit tests in a lightweight environment."""
    session.install("pytest")
    session.run("pytest", "-q")


@nox.session(python=list(PY_VERSIONS))
def lint(session: nox.Session) -> None:
    """Run formatters/linters that are safe offline."""
    session.install("ruff", "black", "isort")
    session.run("ruff", "check", ".")
    session.run("isort", "--check-only", ".")
    session.run("black", "--check", ".")
