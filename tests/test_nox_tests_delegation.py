import importlib


class _DummySession:
    """Minimal stand-in for nox.Session just to capture notify() calls."""

    def __init__(self) -> None:
        self.notified = []

    # nox exposes Session.notify(name: str), we only need the name
    def notify(self, name: str) -> None:  # pragma: no cover - trivial
        self.notified.append(name)


def test_tests_session_delegates_to_coverage():
    # Import user noxfile; the decorated function remains callable.
    noxfile = importlib.import_module("noxfile")
    sess = _DummySession()
    # Call the session function directly; ensure delegation happens.
    noxfile.tests(sess)
    assert "coverage" in sess.notified, "nox 'tests' session must notify 'coverage'"
