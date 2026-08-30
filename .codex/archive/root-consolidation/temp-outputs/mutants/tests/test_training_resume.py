"""
pytest.importorskip("mlflow")
Test Training Resume

Test module for training resume.
"""

import pytest

from codex_ml.training import run_functional_training
from codex_ml.utils.hf_pinning import HFModelUnavailableError
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

    first = None
    try:
        first = run_functional_training(base_config, resume=False)
    except (HFModelUnavailableError, ValueError) as exc:
        # HFModelUnavailableError: network/model unavailable in CI.
        # ValueError: remote HF identifier used without an explicit commit-hash
        #   revision (CODEX_HF_REVISION / HF_REVISION env var not set in CI).
        pytest.skip(f"HuggingFace model unavailable (no network/revision in CI): {exc}")
    assert first is not None, "first must be initialized"
    assert first["resumed_from"] is None, "Condition must be true"
    if first.get("checkpoint_dir") is None:
        pytest.skip("functional training checkpointing requires optional deps")

    resumed_config = dict(base_config)
    resumed_config["max_epochs"] = 3

    second = run_functional_training(resumed_config, resume=True)
    assert second["resumed_from"] is not None, "Value must be initialized"
    assert any(metric["epoch"] == 2 for metric in second["metrics"]), "Condition must be true"

    checkpoint_root = tmp_path / "run" / "checkpoints"
    assert (checkpoint_root / "epoch-2").exists(), "Condition must be true"
