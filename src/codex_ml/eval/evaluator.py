"""Evaluation scaffolding for _codex_.

Provides a minimal evaluate() function for smoke tests. Real implementations
should compute metrics over predictions vs targets and support NDJSON/CSV
outputs.
"""


def evaluate_constant(predictions, targets) -> float:
    """Return a dummy accuracy-style score for smoke tests."""
    if not predictions:
        return 0.0
    correct = sum(1 for p, t in zip(predictions, targets) if p == t)
    return correct / max(len(predictions), 1)
