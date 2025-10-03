import pytest

from codex_ml.training import run_functional_training
from tests.helpers.optional_dependencies import import_optional_dependency

import_optional_dependency("torch")
import_optional_dependency("transformers")


def test_run_functional_training_resume(tmp_path):
    dataset_path = tmp_path / "train.jsonl"
    dataset_path.write_text(
        '{"text": "first sample"}\n{"text": "second sample"}\n', encoding="utf-8"
    )
    base_config = {
        "seed": 11,
        "output_dir": str(tmp_path / "run"),
        "max_epochs": 2,
        "dataset": {
            "train_path": str(dataset_path),
            "format": "jsonl",
        },
    }

    first = run_functional_training(base_config, resume=False)
    assert first["resumed_from"] is None
    if first.get("checkpoint_dir") is None:
        pytest.skip("functional training checkpointing requires optional deps")

    resumed_config = dict(base_config)
    resumed_config["max_epochs"] = 3

    second = run_functional_training(resumed_config, resume=True)
    assert second["resumed_from"] is not None
    assert any(metric["epoch"] == 2 for metric in second["metrics"])

    checkpoint_root = tmp_path / "run" / "checkpoints"
    assert (checkpoint_root / "epoch-2").exists()
