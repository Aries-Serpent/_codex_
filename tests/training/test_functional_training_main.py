from pathlib import Path
from typing import Any, Dict

from omegaconf import OmegaConf

from training import functional_training


def test_main_invokes_hf_trainer(monkeypatch, tmp_path: Path):
    called: Dict[str, Any] = {}

    def fake_run(texts, output_dir, **kwargs):
        called["texts"] = list(texts)
        called["output_dir"] = output_dir
        called["kwargs"] = kwargs
        return {"train": 0.0}

    monkeypatch.setattr(functional_training, "run_hf_trainer", fake_run)

    def fake_loader(*_, **__):
        return OmegaConf.create({"training": {"seed": 7, "gradient_accumulation_steps": 3}})

    monkeypatch.setattr(functional_training, "load_training_cfg", fake_loader)

    functional_training.main(["--engine", "hf", "--texts", "a", "b", "--output-dir", str(tmp_path)])

    assert called["texts"] == ["a", "b"]
    assert called["output_dir"] == tmp_path
    assert called["kwargs"]["seed"] == 7
    assert called["kwargs"]["gradient_accumulation_steps"] == 3
    assert called["kwargs"]["hydra_cfg"]["seed"] == 7
    assert called["kwargs"]["hydra_cfg"]["gradient_accumulation_steps"] == 3
