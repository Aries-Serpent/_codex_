"""
Codex Dummy Plugin Package

This package provides codex dummy plugin functionality.
"""


class DummyModel:

    def __init__(self) -> None:
        self.name = "dummy"

    def predict(self, x):
        return x
