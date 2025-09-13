class DummyModel:
    """Minimal object to prove entry-point discovery works."""

    def __init__(self) -> None:
        self.name = "dummy"

    def predict(self, x):
        return x
