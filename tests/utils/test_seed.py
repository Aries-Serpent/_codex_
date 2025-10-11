import random

import pytest

from codex_ml.utils.seed import set_seed


@pytest.mark.parametrize("seed", [7, 123])
def test_seed_repro(seed: int) -> None:
    expected = random.Random(seed).randint(0, 100000)
    set_seed(seed)
    assert random.randint(0, 100000) == expected

    try:
        import numpy as np
    except Exception:  # pragma: no cover - optional dependency guard
        np = None  # type: ignore[assignment]
    if np is not None:
        baseline = int(np.random.RandomState(seed).randint(0, 100000))
        set_seed(seed)
        assert int(np.random.randint(0, 100000)) == baseline

    try:
        import torch
    except Exception:  # pragma: no cover - optional dependency guard
        torch = None  # type: ignore[assignment]
    if torch is not None and hasattr(torch, "randint"):
        generator = None
        if hasattr(torch, "Generator"):
            try:
                generator = torch.Generator().manual_seed(seed)
            except Exception:  # pragma: no cover - optional dependency guard
                generator = None
        baseline_tensor = int(
            torch.randint(0, 100000, (1,), generator=generator).item()  # type: ignore[arg-type]
        )
        set_seed(seed)
        value = int(torch.randint(0, 100000, (1,)).item())
        assert value == baseline_tensor
