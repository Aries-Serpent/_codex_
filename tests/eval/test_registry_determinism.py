from codex_ml.metrics.registry import get_metric


def test_metric_registry_determinism():
    acc = get_metric("accuracy@token")
    preds = [1, 0, 1]
    targets = [1, 1, 1]
    first = acc(preds, targets)
    second = acc(preds, targets)
    assert first == second

    em = get_metric("exact_match")
    preds_s = ["Hello", "world!"]
    targets_s = ["hello", "world"]
    assert em(preds_s, targets_s) == em(preds_s, targets_s)
