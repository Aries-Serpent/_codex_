import random

import pytest

np = pytest.importorskip("numpy")
torch = pytest.importorskip("torch")


def test_overfit_smoke() -> None:
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(7)
    random.seed(7)
    np.random.seed(7)

    features = torch.randn(64, 8)
    true_weights = torch.randn(8, 1)
    targets = features @ true_weights + 0.01 * torch.randn(64, 1)

    params = torch.zeros(8, 1, requires_grad=True)
    optimiser = torch.optim.SGD([params], lr=0.2)

    loss_history: list[float] = []
    for _ in range(60):
        optimiser.zero_grad()
        loss = ((features @ params - targets) ** 2).mean()
        loss.backward()
        optimiser.step()
        loss_history.append(loss.item())

    assert loss_history[-1] < 1e-2
    assert loss_history[-1] <= min(loss_history) + 1e-6
