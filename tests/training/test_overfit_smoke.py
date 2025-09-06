import torch


def test_overfit_smoke():
    torch.manual_seed(0)
    x = torch.randn(20, 1)
    y = 3 * x + 0.5
    model = torch.nn.Linear(1, 1)
    opt = torch.optim.SGD(model.parameters(), lr=0.1)
    loss_fn = torch.nn.MSELoss()

    init = loss_fn(model(x), y).item()
    for _ in range(100):
        opt.zero_grad()
        loss = loss_fn(model(x), y)
        loss.backward()
        opt.step()
    final = loss_fn(model(x), y).item()
    assert final < init
