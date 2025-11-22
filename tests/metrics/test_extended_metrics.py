from codex_ml.metrics.evaluator import batch_metrics


def test_batch_metrics_text_metrics():
    outputs = {"predictions": ["hello world", "quick fox"]}
    batch = {"references": ["hello world", "quick brown fox"]}

    metrics = batch_metrics(outputs, batch)

    assert metrics["exact_match"] == 0.5
    assert 0.0 <= metrics["bleu1"] <= 1.0
    assert 0.0 <= metrics["rouge1"] <= 1.0
