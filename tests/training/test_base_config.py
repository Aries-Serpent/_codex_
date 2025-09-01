from pathlib import Path

from training.engine_hf_trainer import load_training_arguments


def test_base_config_load(tmp_path):
    cfg = load_training_arguments(
        Path("configs/training/base.yaml"),
        tmp_path,
        None,
    )
    assert cfg.output_dir == str(tmp_path)
    assert cfg.gradient_accumulation_steps == 1
