from codex_ml.metrics.registry import get_metric


def test_registry_determinism():
    metric = get_metric("exact_match")
    preds = ["Hello", "world"]
    targets = ["hello", "world"]
    r1 = metric(preds, targets)
    r2 = metric(preds, targets)
    assert r1 == r2 == 1.0
