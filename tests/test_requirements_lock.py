"""Basic sanity checks around dependency locking."""

from pathlib import Path


def test_requirements_lock_exists() -> None:
    """Ensure the repository ships with a requirements.lock file.

    Pytest's working directory may vary depending on the runner. Resolve the
    path relative to this test file so the assertion holds even when the tests
    execute from within a virtualenv-specific directory.
    """

    root = Path(__file__).resolve().parent.parent
    assert (root / "requirements.lock").is_file()
