"""Run the functional training loop on a tiny in-memory dataset."""

from __future__ import annotations

import json
from pathlib import Path

from codex_ml.training import run_functional_training


def main() -> None:
    run_root = Path("runs/examples")
    run_root.mkdir(parents=True, exist_ok=True)
    config = {
        "model": "MiniLM",
        "training": {
            "texts": ["hello", "codex"],
            "val_texts": ["world"],
            "checkpoint_dir": str(run_root / "checkpoints"),
            "trainer": "functional",
        },
        "tracking": {
            "output_dir": str(run_root),
            "run_name": "toy-train",
        },
    }
    result = run_functional_training(config, resume=False)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
