import random

import pytest

np = pytest.importorskip("numpy")
torch = pytest.importorskip("torch")


def test_overfit_smoke() -> None:
    try:
        torch.use_deterministic_algorithms(True)
    except Exception as exc:  # pragma: no cover - backend dependent
        pytest.skip(f"deterministic algorithms not supported: {exc}")

    torch.manual_seed(7)
    random.seed(7)
    np.random.seed(7)

    device = torch.device("cpu")
    features = torch.randn(64, 8, device=device)
    true_weights = torch.randn(8, 1, device=device)
    targets = features @ true_weights + 0.01 * torch.randn(64, 1, device=device)

    params = torch.zeros(8, 1, device=device, requires_grad=True)
    optimiser = torch.optim.SGD([params], lr=0.2)

    loss_history: list[float] = []
    for _ in range(60):
        optimiser.zero_grad()
        preds = features @ params
        loss = ((preds - targets) ** 2).mean()
        loss.backward()
        optimiser.step()
        loss_history.append(float(loss.detach()))

    assert loss_history[-1] < 1e-2
    best_loss = min(loss_history)
    assert loss_history[-1] <= best_loss + 1e-8
