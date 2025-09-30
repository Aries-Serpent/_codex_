import importlib


def test_logging_mismatch_and_dataset_gate_smoke(monkeypatch, capsys):
    # Smoke test that calling run_training logs dtype/dataset info without crashing.
    tl = importlib.import_module("src.codex_ml.train_loop")

    # Force artifacts under a tmp dir to avoid repo pollution
    from pathlib import Path
    tmp = Path.cwd() / "_tmp_artifacts"
    if tmp.exists():
        # best-effort cleanup
        try:
            import shutil

            shutil.rmtree(tmp)
        except Exception:
            pass

    result = tl.run_training(
        epochs=1,
        steps_per_epoch=1,
        grad_accum=1,
        learning_rate=1e-3,
        art_dir=str(tmp),
        model_name="minilm",
        device=None,
        dtype=None,  # Let default path execute
        return_state=False,
    )
    assert isinstance(result, dict)
