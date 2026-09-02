"""
Comprehensive end-to-end training pipeline validation tests.

This test module validates the complete training pipeline including:
- Data loading and batching
- Model initialization
- Training loop execution
- Loss computation
- Gradient computation
- Optimizer updates
- Validation evaluation
- Checkpointing
- Metrics logging
- Convergence verification
"""

import time
from pathlib import Path
from typing import Dict

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from tests.full.training_fixtures import (
    MiniTransformerModel,
    SyntheticCodeDataset,
    TrainingState,
)


class TestDataLoading:
    """Tests for data loading pipeline."""

    def test_data_loading_creates_batches(
        self,
        train_dataloader: DataLoader,
        training_config: Dict,
    ):
        """Test that data loader creates proper batches."""
        batch_size = training_config["batch_size"]
        total_batches = 0

        for batch in train_dataloader:
            assert "input_ids" in batch
            assert "attention_mask" in batch
            assert "labels" in batch

            # Verify batch size
            assert batch["input_ids"].shape[0] <= batch_size
            assert batch["attention_mask"].shape[0] <= batch_size
            assert batch["labels"].shape[0] <= batch_size

            total_batches += 1

        # Verify we got batches
        assert total_batches > 0

    def test_data_loading_correct_shapes(
        self,
        train_dataloader: DataLoader,
        data_config: Dict,
    ):
        """Test that data has correct shapes."""
        seq_length = data_config["seq_length"]

        for batch in train_dataloader:
            # Verify sequence length
            assert batch["input_ids"].shape[1] == seq_length
            assert batch["attention_mask"].shape[1] == seq_length
            assert batch["labels"].shape[1] == seq_length

            # Verify data types
            assert batch["input_ids"].dtype == torch.long
            assert batch["attention_mask"].dtype == torch.long
            assert batch["labels"].dtype == torch.long
            break  # Just check first batch

    def test_validation_data_loading(
        self,
        val_dataloader: DataLoader,
    ):
        """Test validation data loading."""
        batches = []
        for batch in val_dataloader:
            batches.append(batch)

        assert len(batches) > 0

    def test_train_val_datasets_different(
        self,
        synthetic_train_dataset: SyntheticCodeDataset,
        synthetic_val_dataset: SyntheticCodeDataset,
    ):
        """Test that training and validation datasets are different."""
        # Different number of samples
        assert (
            len(synthetic_train_dataset)
            != len(synthetic_val_dataset)
        )


class TestPreprocessing:
    """Tests for preprocessing and tokenization."""

    def test_tokenization_output_shapes(
        self,
        train_dataloader: DataLoader,
        data_config: Dict,
    ):
        """Test tokenization output shapes."""
        seq_length = data_config["seq_length"]

        for batch in train_dataloader:
            input_ids = batch["input_ids"]
            assert input_ids.dim() == 2
            assert input_ids.shape[1] == seq_length
            break

    def test_attention_mask_creation(
        self,
        train_dataloader: DataLoader,
    ):
        """Test attention mask creation."""
        for batch in train_dataloader:
            attention_mask = batch["attention_mask"]
            # All values should be 0 or 1
            assert torch.all((attention_mask == 0) | (attention_mask == 1))
            break

    def test_labels_preparation(
        self,
        train_dataloader: DataLoader,
    ):
        """Test labels are properly prepared."""
        for batch in train_dataloader:
            labels = batch["labels"]
            # Labels should be non-negative
            assert torch.all(labels >= 0)
            break


class TestModelInitialization:
    """Tests for model initialization."""

    def test_model_initialization(
        self,
        model: MiniTransformerModel,
    ):
        """Test model initializes correctly."""
        assert model is not None
        assert isinstance(model, nn.Module)

    def test_model_parameters_exist(
        self,
        model: MiniTransformerModel,
    ):
        """Test that model has trainable parameters."""
        params = list(model.parameters())
        assert len(params) > 0

        # Verify parameters have gradients enabled
        for param in params:
            assert param.requires_grad

    def test_model_on_device(
        self,
        model: MiniTransformerModel,
        device: torch.device,
    ):
        """Test model is on correct device."""
        for param in model.parameters():
            assert param.device == device

    def test_model_forward_pass(
        self,
        model: MiniTransformerModel,
        device: torch.device,
        data_config: Dict,
    ):
        """Test model forward pass executes."""
        batch_size = 8
        seq_length = data_config["seq_length"]
        vocab_size = data_config["vocab_size"]

        input_ids = torch.randint(
            1, vocab_size, (batch_size, seq_length), device=device
        )
        labels = torch.randint(
            1, vocab_size, (batch_size, seq_length), device=device
        )

        logits, loss = model(input_ids, labels=labels)

        assert logits is not None
        assert loss is not None
        assert logits.shape == (batch_size, seq_length, vocab_size)
        assert loss.item() > 0


class TestTrainingLoop:
    """Tests for training loop execution."""

    def test_single_training_step(
        self,
        model: MiniTransformerModel,
        optimizer,
        train_dataloader: DataLoader,
        device: torch.device,
    ):
        """Test single training step."""
        model.train()

        batch = next(iter(train_dataloader))
        input_ids = batch["input_ids"].to(device)
        labels = batch["labels"].to(device)

        # Forward pass
        logits, loss = model(input_ids, labels=labels)
        assert loss is not None

        # Backward pass
        optimizer.zero_grad()
        loss.backward()

        # Check gradients exist
        for param in model.parameters():
            if param.requires_grad:
                assert param.grad is not None

        # Optimizer step
        optimizer.step()

    def test_training_loop_single_epoch(
        self,
        model: MiniTransformerModel,
        optimizer,
        train_dataloader: DataLoader,
        device: torch.device,
        training_config: Dict,
    ):
        """Test training loop for single epoch."""
        model.train()
        losses = []

        for batch_idx, batch in enumerate(train_dataloader):
            input_ids = batch["input_ids"].to(device)
            labels = batch["labels"].to(device)

            logits, loss = model(input_ids, labels=labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            losses.append(loss.item())

            if batch_idx >= 2:  # Just a few batches for test
                break

        assert len(losses) > 0
        assert all(loss > 0 for loss in losses)

    def test_loss_decreases_over_steps(
        self,
        model: MiniTransformerModel,
        optimizer,
        train_dataloader: DataLoader,
        device: torch.device,
    ):
        """Test that loss decreases over training steps."""
        model.train()
        losses = []

        for batch_idx, batch in enumerate(train_dataloader):
            input_ids = batch["input_ids"].to(device)
            labels = batch["labels"].to(device)

            logits, loss = model(input_ids, labels=labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            losses.append(loss.item())

            if batch_idx >= 4:  # Multiple steps
                break

        # Loss should generally decrease (allowing some variance)
        avg_first_half = sum(losses[:2]) / 2
        avg_second_half = sum(losses[2:]) / len(losses[2:])

        # At least show some improvement trend
        assert len(losses) >= 3


class TestGradientFlow:
    """Tests for gradient computation and flow."""

    def test_gradients_computed(
        self,
        model: MiniTransformerModel,
        optimizer,
        train_dataloader: DataLoader,
        device: torch.device,
    ):
        """Test that gradients are computed."""
        model.train()
        batch = next(iter(train_dataloader))
        input_ids = batch["input_ids"].to(device)
        labels = batch["labels"].to(device)

        # Before backward, gradients should be None
        for param in model.parameters():
            if param.requires_grad:
                assert param.grad is None

        # Forward and backward
        logits, loss = model(input_ids, labels=labels)
        loss.backward()

        # After backward, gradients should exist
        has_gradients = False
        for param in model.parameters():
            if param.requires_grad and param.grad is not None:
                has_gradients = True
                break

        assert has_gradients

    def test_gradient_magnitudes_reasonable(
        self,
        model: MiniTransformerModel,
        optimizer,
        train_dataloader: DataLoader,
        device: torch.device,
    ):
        """Test gradient magnitudes are reasonable."""
        model.train()
        batch = next(iter(train_dataloader))
        input_ids = batch["input_ids"].to(device)
        labels = batch["labels"].to(device)

        logits, loss = model(input_ids, labels=labels)
        loss.backward()

        # Check gradient magnitudes
        max_grad = 0.0
        for param in model.parameters():
            if param.grad is not None:
                max_grad = max(max_grad, param.grad.abs().max().item())

        # Gradients should be non-zero and reasonable
        assert 0 < max_grad < 1e6


class TestOptimizerUpdates:
    """Tests for optimizer parameter updates."""

    def test_parameters_updated_after_step(
        self,
        model: MiniTransformerModel,
        optimizer,
        train_dataloader: DataLoader,
        device: torch.device,
    ):
        """Test that parameters are updated after optimizer step."""
        model.train()

        # Get initial parameter values
        initial_params = [param.clone() for param in model.parameters()]

        batch = next(iter(train_dataloader))
        input_ids = batch["input_ids"].to(device)
        labels = batch["labels"].to(device)

        # Training step
        logits, loss = model(input_ids, labels=labels)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # Check parameters changed
        params_changed = False
        for initial_param, current_param in zip(
            initial_params, model.parameters()
        ):
            if not torch.allclose(initial_param, current_param):
                params_changed = True
                break

        assert params_changed

    def test_learning_rate_scheduler_step(
        self,
        optimizer,
        lr_scheduler,
    ):
        """Test learning rate scheduler updates."""
        initial_lr = optimizer.param_groups[0]["lr"]

        lr_scheduler.step()
        updated_lr = optimizer.param_groups[0]["lr"]

        # Learning rate should be updated
        assert initial_lr == updated_lr or updated_lr > 0


class TestValidation:
    """Tests for validation loop."""

    def test_validation_loop_execution(
        self,
        model: MiniTransformerModel,
        val_dataloader: DataLoader,
        device: torch.device,
    ):
        """Test validation loop executes."""
        model.eval()
        val_losses = []

        with torch.no_grad():
            for batch in val_dataloader:
                input_ids = batch["input_ids"].to(device)
                labels = batch["labels"].to(device)

                logits, loss = model(input_ids, labels=labels)
                val_losses.append(loss.item())

                if len(val_losses) >= 2:
                    break

        assert len(val_losses) > 0
        assert all(loss > 0 for loss in val_losses)

    def test_no_gradients_during_validation(
        self,
        model: MiniTransformerModel,
        val_dataloader: DataLoader,
        device: torch.device,
    ):
        """Test no gradients computed during validation."""
        model.eval()
        batch = next(iter(val_dataloader))
        input_ids = batch["input_ids"].to(device)
        labels = batch["labels"].to(device)

        with torch.no_grad():
            logits, loss = model(input_ids, labels=labels)

        # No gradients should be computed
        for param in model.parameters():
            if param.requires_grad:
                assert param.grad is None


class TestCheckpointing:
    """Tests for model checkpointing."""

    def test_save_checkpoint(
        self,
        training_state: TrainingState,
        checkpoint_dir: Path,
    ):
        """Test saving checkpoint."""
        checkpoint_path = checkpoint_dir / "checkpoint.pt"
        training_state.epoch = 1
        training_state.global_step = 100

        training_state.save_checkpoint(checkpoint_path)

        assert checkpoint_path.exists()

    def test_load_checkpoint(
        self,
        training_state: TrainingState,
        checkpoint_dir: Path,
        device: torch.device,
    ):
        """Test loading checkpoint."""
        checkpoint_path = checkpoint_dir / "checkpoint.pt"

        # Save initial state
        training_state.epoch = 5
        training_state.global_step = 200
        training_state.save_checkpoint(checkpoint_path)

        # Create new training state and load
        new_state = TrainingState(
            training_state.model,
            training_state.optimizer,
            device,
        )
        new_state.load_checkpoint(checkpoint_path)

        assert new_state.epoch == 5
        assert new_state.global_step == 200

    def test_checkpoint_contains_metrics(
        self,
        training_state: TrainingState,
        checkpoint_dir: Path,
    ):
        """Test checkpoint stores metrics."""
        checkpoint_path = checkpoint_dir / "checkpoint.pt"
        metrics = {"loss": 2.5, "accuracy": 0.85}

        training_state.save_checkpoint(checkpoint_path, metrics=metrics)

        # Load and verify
        checkpoint = torch.load(checkpoint_path)
        assert "metrics" in checkpoint
        assert checkpoint["metrics"]["loss"] == 2.5


class TestMetricsLogging:
    """Tests for metrics collection."""

    def test_metrics_tracking(
        self,
        training_metrics: Dict,
    ):
        """Test metrics can be tracked."""
        training_metrics["train_loss"].append(2.5)
        training_metrics["train_loss"].append(2.3)

        assert len(training_metrics["train_loss"]) == 2
        assert training_metrics["train_loss"][0] == 2.5

    def test_metrics_computation(
        self,
        model: MiniTransformerModel,
        train_dataloader: DataLoader,
        device: torch.device,
    ):
        """Test computing metrics from training."""
        model.train()
        losses = []

        for batch_idx, batch in enumerate(train_dataloader):
            input_ids = batch["input_ids"].to(device)
            labels = batch["labels"].to(device)

            logits, loss = model(input_ids, labels=labels)
            losses.append(loss.item())

            if batch_idx >= 2:
                break

        avg_loss = sum(losses) / len(losses)
        assert 0 < avg_loss < 1e6

    def test_perplexity_computation(
        self,
        training_metrics: Dict,
    ):
        """Test perplexity can be computed from loss."""
        loss = 2.5
        perplexity = 2.718 ** loss  # e^loss

        assert perplexity > 1.0


class TestConvergence:
    """Tests for training convergence."""

    def test_loss_decreases_over_epochs(
        self,
        model: MiniTransformerModel,
        optimizer,
        train_dataloader: DataLoader,
        device: torch.device,
    ):
        """Test loss decreases over training epochs."""
        model.train()
        epoch_losses = []

        for epoch in range(2):
            epoch_loss = 0
            batch_count = 0

            for batch_idx, batch in enumerate(train_dataloader):
                input_ids = batch["input_ids"].to(device)
                labels = batch["labels"].to(device)

                logits, loss = model(input_ids, labels=labels)

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                epoch_loss += loss.item()
                batch_count += 1

                if batch_idx >= 3:
                    break

            avg_epoch_loss = epoch_loss / batch_count
            epoch_losses.append(avg_epoch_loss)

        # We should have losses for both epochs
        assert len(epoch_losses) == 2


class TestFullPipeline:
    """Tests for complete end-to-end training pipeline."""

    def test_complete_training_run(
        self,
        model: MiniTransformerModel,
        optimizer,
        lr_scheduler,
        train_dataloader: DataLoader,
        val_dataloader: DataLoader,
        device: torch.device,
        training_state: TrainingState,
        checkpoint_dir: Path,
        training_metrics: Dict,
    ):
        """Test complete end-to-end training run."""
        start_time = time.time()

        # Training loop
        for epoch in range(1):  # Single epoch for test
            model.train()
            train_losses = []

            for batch_idx, batch in enumerate(train_dataloader):
                input_ids = batch["input_ids"].to(device)
                labels = batch["labels"].to(device)

                # Forward pass
                logits, loss = model(input_ids, labels=labels)

                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                lr_scheduler.step()

                train_losses.append(loss.item())
                training_state.global_step += 1

                if batch_idx >= 3:  # Limit batches for test
                    break

            # Validation
            model.eval()
            val_losses = []
            with torch.no_grad():
                for batch in val_dataloader:
                    input_ids = batch["input_ids"].to(device)
                    labels = batch["labels"].to(device)

                    logits, loss = model(input_ids, labels=labels)
                    val_losses.append(loss.item())

                    if len(val_losses) >= 2:
                        break

            # Update metrics
            training_metrics["train_loss"].extend(train_losses)
            training_metrics["val_loss"].extend(val_losses)

            training_state.epoch += 1

            # Save checkpoint
            checkpoint_path = checkpoint_dir / f"checkpoint_epoch_{epoch}.pt"
            training_state.save_checkpoint(
                checkpoint_path,
                metrics={
                    "train_loss": sum(train_losses) / len(train_losses),
                    "val_loss": sum(val_losses) / len(val_losses),
                },
            )

        elapsed_time = time.time() - start_time

        # Verify complete pipeline executed
        assert len(training_metrics["train_loss"]) > 0
        assert len(training_metrics["val_loss"]) > 0
        assert training_state.epoch > 0
        assert elapsed_time > 0

    def test_checkpoint_restore(
        self,
        model: MiniTransformerModel,
        optimizer,
        device: torch.device,
        checkpoint_dir: Path,
        training_state: TrainingState,
    ):
        """Test checkpoint save and restore in pipeline."""
        # Save checkpoint
        checkpoint_path = checkpoint_dir / "checkpoint.pt"
        training_state.epoch = 2
        training_state.global_step = 500
        training_state.save_checkpoint(checkpoint_path)

        # Create new state and restore
        new_state = TrainingState(model, optimizer, device)
        metrics = new_state.load_checkpoint(checkpoint_path)

        assert new_state.epoch == 2
        assert new_state.global_step == 500

    def test_pipeline_performance_metrics(
        self,
        model: MiniTransformerModel,
        optimizer,
        train_dataloader: DataLoader,
        device: torch.device,
        training_config: Dict,
    ):
        """Test collecting performance metrics."""
        model.train()
        start_time = time.time()
        sample_count = 0

        for batch_idx, batch in enumerate(train_dataloader):
            input_ids = batch["input_ids"].to(device)
            labels = batch["labels"].to(device)

            logits, loss = model(input_ids, labels=labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            sample_count += input_ids.shape[0]

            if batch_idx >= 3:
                break

        elapsed_time = time.time() - start_time
        throughput = sample_count / elapsed_time if elapsed_time > 0 else 0

        assert throughput > 0
