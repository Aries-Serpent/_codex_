from codex_ml.train_loop import demo_epoch


def test_demo_epoch_includes_grad_accum():
    metrics = demo_epoch(0, grad_accum=4)
    assert metrics["grad_accum"] == 4
