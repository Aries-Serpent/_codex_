"""Toy metric plugin used in documentation and automated tests."""

__all__ = ["build", "toy_metric"]


def toy_metric(preds):
    """Return a constant score to keep the example deterministic."""

    return 1.0


def build():
    """Factory used by registry tests."""

    return {"name": "toy_metric"}
