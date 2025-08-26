from functional_training import run_functional_training


def test_tb_writer_guard(monkeypatch, tmp_path):
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "torch.utils.tensorboard":
            raise ImportError
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    run_functional_training(
        corpus=["hi"],
        demos=[],
        prefs=[],
        use_deeplearning=True,
        checkpoint_dir=str(tmp_path),
        tensorboard=True,
    )
    assert (tmp_path / "metrics.json").exists()

