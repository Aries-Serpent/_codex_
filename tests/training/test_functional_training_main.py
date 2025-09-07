from pathlib import Path

from omegaconf import DictConfig

from training import functional_training


def test_main_passes_cfg(monkeypatch, tmp_path: Path):
    calls = {}

    def fake_run_hf(texts, output_dir, *, seed, gradient_accumulation_steps):
        calls["seed"] = seed
        calls["gas"] = gradient_accumulation_steps
        return {"loss": 0.0}

    monkeypatch.setattr(functional_training, "run_hf_trainer", fake_run_hf)

    def fake_load_cfg(*, allow_fallback, overrides):
        return DictConfig({"training": {"seed": 123, "gradient_accumulation_steps": 7}})

    monkeypatch.setattr(functional_training, "load_training_cfg", fake_load_cfg)

    functional_training.main(["--texts", "hi", "--output-dir", str(tmp_path)])
    assert calls["seed"] == 123
    assert calls["gas"] == 7
