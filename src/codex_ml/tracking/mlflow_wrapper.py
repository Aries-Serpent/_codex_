"""Experiment tracking scaffolding for _codex_.

This does NOT import mlflow; it merely defines a placeholder API to be wired
later. The goal is to provide a stable import path.
"""


def log_metric(name: str, value: float) -> None:
    # Placeholder no-op implementation
    _ = (name, value)
