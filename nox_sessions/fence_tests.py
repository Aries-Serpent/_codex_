import nox


@nox.session
def fence_tests(session: nox.Session) -> None:
    """
    Deterministic, offline fence-validator tests.
    - Disables pytest plugin autoload for stability (see pytest docs).
    """
    session.install("pytest")
    session.env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    # Run both the pure-function tests and the small CLI wrapper test if present.
    session.run("pytest", "-q", "tests/tools/test_validate_fences.py")
