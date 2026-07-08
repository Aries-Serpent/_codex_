"""
Test Readme Has Quickstart

Test module for readme has quickstart.
"""

import re
from pathlib import Path


def test_readme_contains_quickstart_snippets() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    readme = (repo_root / "README.md").read_text(encoding="utf-8")

    assert "## Quickstart" in readme, "Expected Quickstart heading to remain in README.md"

    normalized_readme = re.sub(r"\s+", " ", readme.replace("\\\n", " "))
    expected_snippet = (
        "codex-train experiment=debug "
        "training.max_epochs=1 training.batch_size=2 "
        "data.train_path=data/train.jsonl data.eval_path=data/eval.jsonl "
        "logging.tensorboard=false logging.mlflow_enable=false "
        "training.output_dir=artifacts/runs/quickstart"
    )
    assert (expected_snippet in normalized_readme), "Expected codex-train Quickstart example to remain in README.md"
