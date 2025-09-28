import pytest

from codex_ml.utils.checkpoint import load_checkpoint, save_checkpoint

pytestmark = pytest.mark.requires_torch

torch = pytest.importorskip("torch")


def test_save_and_load_checkpoint(tmp_path):
    model = torch.nn.Linear(4, 2)
    optimiser = torch.optim.SGD(model.parameters(), lr=0.1)
    scheduler = torch.optim.lr_scheduler.StepLR(optimiser, step_size=1)
    for _ in range(2):
        optimiser.zero_grad()
        loss = model(torch.ones(1, 4)).sum()
        loss.backward()
        optimiser.step()
        scheduler.step()
    out_dir = save_checkpoint(
        model=model,
        optimizer=optimiser,
        scheduler=scheduler,
        out_dir=tmp_path / "ckpt",
        metadata={"epoch": 1, "seed": 1234},
    )
    reloaded = torch.nn.Linear(4, 2)
    re_opt = torch.optim.SGD(reloaded.parameters(), lr=0.1)
    re_sched = torch.optim.lr_scheduler.StepLR(re_opt, step_size=1)
    metadata = load_checkpoint(
        model=reloaded,
        optimizer=re_opt,
        scheduler=re_sched,
        ckpt_dir=out_dir,
    )
    for original, copied in zip(model.state_dict().values(), reloaded.state_dict().values()):
        assert torch.allclose(original, copied)
    assert metadata["epoch"] == 1
    assert metadata["seed"] == 1234
