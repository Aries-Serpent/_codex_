from __future__ import annotations

from codex_ml.training import unified_training


class _DummyCuda:
    def __init__(self, available: bool = True) -> None:
        self.available = available
        self.seed_calls: list[int] = []

    def is_available(self) -> bool:
        return self.available

    def manual_seed_all(self, seed: int) -> None:
        self.seed_calls.append(seed)


class _DummyTorch:
    def __init__(self) -> None:
        self.manual_seed_calls: list[int] = []
        self.cuda = _DummyCuda()

    def manual_seed(self, seed: int) -> None:
        self.manual_seed_calls.append(seed)


def test_seed_all_invokes_torch_monkeypatched(monkeypatch) -> None:
    dummy = _DummyTorch()
    monkeypatch.setattr(unified_training, "torch", dummy)
    unified_training._seed_all(99)
    assert dummy.manual_seed_calls == [99]
    assert dummy.cuda.seed_calls == [99]
