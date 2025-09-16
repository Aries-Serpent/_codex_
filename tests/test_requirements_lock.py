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


def test_requirements_lock_notes_python_target() -> None:
    """The lock header documents the Python version used for pinning."""

    lock_path = Path(__file__).resolve().parent.parent / "requirements.lock"
    lines = lock_path.read_text(encoding="utf-8").splitlines()

    header_lines: list[str] = []
    for line in lines:
        if not line.strip():
            continue
        if not line.startswith("#"):
            break
        header_lines.append(line.lower())

    assert any("python lock target" in line for line in header_lines)
