from pathlib import Path

from omegaconf import OmegaConf

from training import functional_training


def test_main_passes_cfg(monkeypatch, tmp_path: Path):
    calls = {}

    def fake_run_hf(texts, output_dir, **kwargs):
        # Record relevant propagated values
        calls["seed"] = kwargs.get("seed")
        calls["gas"] = kwargs.get("gradient_accumulation_steps")
        # Simulate a trainer result
        return {"loss": 0.0}

    monkeypatch.setattr(functional_training, "run_hf_trainer", fake_run_hf)

    def fake_load_cfg(*, allow_fallback, overrides):
        assert allow_fallback is True
        # Minimal training block resembling loaded config
        return OmegaConf.create({"training": {"seed": 123, "gradient_accumulation_steps": 7}})

    monkeypatch.setattr(functional_training, "load_training_cfg", fake_load_cfg)

    # Engine selection should default to HF if not specified; ensure required args are passed
    functional_training.main(["--texts", "hi", "--output-dir", str(tmp_path)])
    assert calls["seed"] == 123
    assert calls["gas"] == 7