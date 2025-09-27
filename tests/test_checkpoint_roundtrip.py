from __future__ import annotations

import random

import pytest

from codex_ml.utils.checkpoint import load_checkpoint, save_checkpoint

np = pytest.importorskip("numpy")
torch = pytest.importorskip("torch")


@pytest.mark.parametrize("use_scheduler", [True, False])
def test_checkpoint_roundtrip_restores_states(tmp_path, use_scheduler):
    random.seed(2024)
    np.random.seed(2024)
    torch.manual_seed(2024)
    if torch.cuda.is_available():  # pragma: no cover - optional GPU
        torch.cuda.manual_seed_all(2024)

    py_state = random.getstate()
    np_state = np.random.get_state()
    torch_state = torch.random.get_rng_state()
    cuda_state = torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None

    def sample_sequences():
        random.setstate(py_state)
        np.random.set_state(np_state)
        torch.random.set_rng_state(torch_state)
        if cuda_state is not None:  # pragma: no cover - gpu optional
            torch.cuda.set_rng_state_all(cuda_state)
        return (
            [random.random() for _ in range(4)],
            np.random.random(4),
            torch.rand(4),
        )

    expected_py, expected_np, expected_torch = sample_sequences()

    # Restore initial state before saving.
    random.setstate(py_state)
    np.random.set_state(np_state)
    torch.random.set_rng_state(torch_state)
    if cuda_state is not None:  # pragma: no cover - gpu optional
        torch.cuda.set_rng_state_all(cuda_state)

    model = torch.nn.Linear(4, 2)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=1) if use_scheduler else None

    ckpt_dir = tmp_path / "ckpt"
    save_checkpoint(
        model=model,
        optimizer=optimizer,
        scheduler=scheduler,
        out_dir=ckpt_dir,
        metadata={"epoch": 1},
    )

    # Disturb RNG state to ensure load restores it.
    random.random()
    np.random.random()
    torch.rand(1)

    reloaded = torch.nn.Linear(4, 2)
    re_opt = torch.optim.Adam(reloaded.parameters(), lr=0.01)
    re_sched = torch.optim.lr_scheduler.StepLR(re_opt, step_size=1) if use_scheduler else None

    metadata = load_checkpoint(
        model=reloaded,
        optimizer=re_opt,
        scheduler=re_sched,
        ckpt_dir=ckpt_dir,
    )

    assert metadata["epoch"] == 1

    restored_py = [random.random() for _ in range(4)]
    restored_np = np.random.random(4)
    restored_torch = torch.rand(4)

    assert restored_py == expected_py
    np.testing.assert_allclose(restored_np, expected_np)
    assert torch.allclose(restored_torch, expected_torch)

    for orig, copy in zip(model.state_dict().values(), reloaded.state_dict().values()):
        assert torch.allclose(orig, copy)

    if scheduler and re_sched:
        assert scheduler.get_last_lr() == pytest.approx(re_sched.get_last_lr())
