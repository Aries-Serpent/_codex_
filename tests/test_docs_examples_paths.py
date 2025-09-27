from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "relative_path",
    [
        Path("docs/examples/lora_quickstart.md"),
        Path("docs/examples/eval_metrics.md"),
    ],
)
def test_example_docs_present(relative_path: Path) -> None:
    repo_root = Path(__file__).resolve().parent.parent
    path = repo_root / relative_path
    assert path.exists(), f"Missing expected example doc: {relative_path}"
    content = path.read_text(encoding="utf-8").strip()
    assert content, f"Example doc {relative_path} is empty"
