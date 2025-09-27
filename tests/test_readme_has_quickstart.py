from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "needle",
    ["## Quickstart", "codex-train training.max_epochs=1 training.batch_size=2"],
)
def test_readme_contains_quickstart_snippets(needle: str) -> None:
    repo_root = Path(__file__).resolve().parent.parent
    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    assert needle in readme, f"Expected to find {needle!r} in README.md"
