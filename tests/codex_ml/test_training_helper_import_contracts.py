"""Real initialization regressions for the packaged training providers."""

from pathlib import Path

import pytest

import torch
from codex_ml import _train_init_helpers as helpers
from codex_ml.train_loop import ToyDataset
from codex_ml.training.dp_config import DifferentialPrivacyConfig
from torch import nn
from torch.utils.data import DataLoader


@pytest.mark.parametrize(
    "policy,dtype",
    [(None, torch.long), ("to_fp32", torch.float32), ("to_model_dtype", torch.float64)],
)
def test_helper_builds_canonical_dataset_and_casting_loader(
    policy: str | None, dtype: torch.dtype, tmp_path: Path
) -> None:
    dataset, loader = helpers.setup_dataset_and_loader(
        3, 32, 42, policy, torch.float64, torch.device("cpu"), tmp_path
    )

    assert isinstance(dataset, ToyDataset)
    assert isinstance(loader, DataLoader)
    assert loader.dataset is dataset
    assert len(dataset) == 64
    assert dataset[0].shape == (16,)
    assert dataset[0].dtype == torch.long
    batch = next(iter(loader))
    assert len(batch) == 3
    assert all(tokens.shape == (16,) and tokens.dtype == dtype for tokens in batch)
    assert all(torch.all((tokens >= 0) & (tokens < 32)) for tokens in batch)
    expected = ToyDataset(num_samples=64, seq_len=16, vocab_size=32, seed=42)
    assert all(torch.equal(dataset[index], expected[index]) for index in range(len(dataset)))


@pytest.mark.parametrize("dp_settings", [None, DifferentialPrivacyConfig(enabled=False)])
def test_helper_builds_real_optimizer_without_optional_opacus(
    dp_settings: DifferentialPrivacyConfig | None,
) -> None:
    model = nn.Linear(10, 1)
    loader = DataLoader(torch.ones(4, 10), batch_size=2)
    wrapped_model, optimizer, wrapped_loader, privacy_engine = helpers.setup_optimizer_with_dp(
        model, 0.001, torch.float32, dp_settings, loader
    )

    assert wrapped_model is model
    assert wrapped_loader is loader
    assert isinstance(optimizer, torch.optim.Adam)
    assert privacy_engine is None
    assert optimizer.param_groups[0]["lr"] == 0.001
    before = [parameter.detach().clone() for parameter in model.parameters()]
    optimizer.zero_grad(set_to_none=True)
    model(torch.ones(2, 10)).sum().backward()
    optimizer.step()
    assert all(
        not torch.equal(old, new) for old, new in zip(before, model.parameters(), strict=True)
    )
