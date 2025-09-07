from pathlib import Path

from omegaconf import OmegaConf

import training.functional_training as ft


def test_main_invokes_run_hf_trainer(monkeypatch, tmp_path: Path):
    cfg = OmegaConf.create({"training": {"texts": ["hi"], "seed": 123}})
    monkeypatch.setattr(ft, "load_training_cfg", lambda **kwargs: cfg)
    called = {}

    def fake_run(texts, output_dir, **kwargs):
        called["texts"] = list(texts)
        called["output_dir"] = output_dir
        called.update(kwargs)
        return {"loss": 0.0}

    monkeypatch.setattr(ft, "run_hf_trainer", fake_run)
    ft.main(["--output-dir", str(tmp_path), "--engine", "hf"])
    assert called["texts"] == ["hi"]
    assert called["output_dir"] == tmp_path
    assert called["seed"] == 123
