import shutil

import nox

# Auto-detect available interpreters to avoid session bootstrap failures.
# Falls back to 3.12 only if no others are found.
_CANDIDATES = ("3.12", "3.11", "3.10")
PY_VERSIONS = tuple(v for v in _CANDIDATES if shutil.which(f"python{v}")) or ("3.12",)
TEST_BOOTSTRAP_PKGS = ("pip", "setuptools", "wheel")


@nox.session(python=list(PY_VERSIONS))
def tests(session: nox.Session) -> None:
    """Run unit tests in a lightweight environment."""
    session.env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    # Install the project (with the test extra) so imports like ``codex_ml.config.settings``
    # resolve all of their runtime dependencies before pytest starts collecting tests.
    # This mirrors the previous session behaviour where dependencies were available
    # via the virtualenv bootstrap.
    session.install(*TEST_BOOTSTRAP_PKGS)
    session.install("-e", ".[test]")
    session.run("pytest", "-q")


@nox.session(python=list(PY_VERSIONS))
def lint(session: nox.Session) -> None:
    """Run formatters/linters that are safe offline."""
    session.install("ruff", "black", "isort")
    session.run("ruff", "check", ".")
    session.run("isort", "--check-only", ".")
    session.run("black", "--check", ".")
