from pathlib import Path

import pytest

pytest.importorskip("omegaconf")
pytest.importorskip("torch")
pytest.importorskip("transformers")
pytest.importorskip("numpy")
pytest.importorskip("datasets")
pytest.importorskip("accelerate")
pytest.importorskip("yaml")

from training.engine_hf_trainer import load_training_arguments


def test_load_training_arguments_flags(tmp_path: Path):
    args = load_training_arguments(
        None, tmp_path, precision="fp16", hydra_cfg={"gradient_accumulation_steps": 3}
    )
    assert args.fp16 is True
    assert args.gradient_accumulation_steps == 3
