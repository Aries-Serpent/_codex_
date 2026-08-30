pytest.importorskip("mlflow")
"""
Test Training Contracts

Test module for training contracts.
"""

from __future__ import annotations

import pytest

from codex_ml.interfaces.contracts import TrainingContractError
from codex_ml.training.loop import train_epoch


class _BatchAwareModel:
    def step(self, batch, state):
        if "input_ids" not in batch:
            raise KeyError("input_ids missing from batch")
        return {"loss": float(batch["input_ids"][0])}


class _StrictModel:
    def step(self, batch, state):
        return {"loss": batch["missing"]}


def test_train_epoch_uses_real_batch_for_validation():
    dataloader = [{"input_ids": [1, 2], "attention_mask": [1, 1]}]
    result = train_epoch(_BatchAwareModel(), dataloader, state={"epoch": 0})
    assert result["loss_mean"] == 1.0, "Result must not be empty"
    assert result["loss_last"] == 1.0, "Result must not be empty"


def test_train_epoch_contract_rejects_invalid_batch():
    dataloader = [{"input_ids": [1]}]
    with pytest.raises(TrainingContractError):
        train_epoch(_StrictModel(), dataloader, state={})


def test_train_epoch_contract_rejects_empty_dataloader():
    with pytest.raises(TrainingContractError):
        train_epoch(_BatchAwareModel(), [], state={})
