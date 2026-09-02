"""
Fixtures and utilities for end-to-end training pipeline tests.

This module provides fixtures for testing the complete training pipeline:
- Synthetic data generation
- Model initialization
- Tokenization and batching
- Training loops
- Checkpointing
- Metrics collection
"""

import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pytest
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset


class SyntheticCodeDataset(Dataset):
    """Synthetic dataset for code training."""

    def __init__(
        self,
        num_samples: int = 128,
        seq_length: int = 256,
        vocab_size: int = 10000,
        seed: int = 42,
    ):
        """
        Initialize synthetic dataset.

        Args:
            num_samples: Number of training samples
            seq_length: Sequence length
            vocab_size: Vocabulary size
            seed: Random seed for reproducibility
        """
        self.num_samples = num_samples
        self.seq_length = seq_length
        self.vocab_size = vocab_size

        torch.manual_seed(seed)

        # Generate synthetic token sequences
        self.input_ids = torch.randint(
            1, vocab_size, (num_samples, seq_length), dtype=torch.long
        )
        # Generate random attention masks
        self.attention_masks = torch.ones(
            (num_samples, seq_length), dtype=torch.long
        )
        # Generate random labels (for language modeling)
        self.labels = torch.randint(
            1, vocab_size, (num_samples, seq_length), dtype=torch.long
        )

    def __len__(self) -> int:
        """Return dataset length."""
        return self.num_samples

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """Return sample."""
        return {
            "input_ids": self.input_ids[idx],
            "attention_mask": self.attention_masks[idx],
            "labels": self.labels[idx],
        }


class MiniTransformerModel(nn.Module):
    """Minimal Transformer model for testing."""

    def __init__(
        self,
        vocab_size: int = 10000,
        hidden_dim: int = 128,
        num_layers: int = 2,
        num_heads: int = 4,
        max_seq_length: int = 256,
    ):
        """
        Initialize model.

        Args:
            vocab_size: Vocabulary size
            hidden_dim: Hidden dimension
            num_layers: Number of transformer layers
            num_heads: Number of attention heads
            max_seq_length: Maximum sequence length
        """
        super().__init__()

        self.embedding = nn.Embedding(vocab_size, hidden_dim)
        self.positional_encoding = nn.Embedding(max_seq_length, hidden_dim)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_dim,
            nhead=num_heads,
            dim_feedforward=hidden_dim * 4,
            batch_first=True,
            dropout=0.1,
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer, num_layers=num_layers
        )

        self.output_projection = nn.Linear(hidden_dim, vocab_size)
        self.loss_fn = nn.CrossEntropyLoss()

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        labels: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        """
        Forward pass.

        Args:
            input_ids: Input token IDs
            attention_mask: Attention mask
            labels: Target labels for loss computation

        Returns:
            Logits and optional loss
        """
        seq_length = input_ids.shape[1]
        position_ids = torch.arange(seq_length, device=input_ids.device).unsqueeze(
            0
        )

        # Embedding
        embeddings = self.embedding(input_ids)
        position_embeddings = self.positional_encoding(position_ids)
        embeddings = embeddings + position_embeddings

        # Transformer encoding
        encoder_output = self.transformer_encoder(embeddings)

        # Output projection
        logits = self.output_projection(encoder_output)

        # Loss computation
        loss = None
        if labels is not None:
            loss = self.loss_fn(
                logits.view(-1, logits.shape[-1]), labels.view(-1)
            )

        return logits, loss


@pytest.fixture
def device() -> torch.device:
    """Get device for training (CPU or CUDA)."""
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


@pytest.fixture
def model_config() -> Dict[str, Any]:
    """Model configuration."""
    return {
        "vocab_size": 10000,
        "hidden_dim": 128,
        "num_layers": 2,
        "num_heads": 4,
        "max_seq_length": 256,
    }


@pytest.fixture
def training_config() -> Dict[str, Any]:
    """Training configuration."""
    return {
        "batch_size": 32,
        "learning_rate": 1e-3,
        "num_epochs": 2,
        "num_warmup_steps": 100,
        "gradient_accumulation_steps": 1,
        "max_grad_norm": 1.0,
    }


@pytest.fixture
def data_config() -> Dict[str, Any]:
    """Data configuration."""
    return {
        "num_train_samples": 256,
        "num_val_samples": 64,
        "seq_length": 256,
        "vocab_size": 10000,
    }


@pytest.fixture
def synthetic_train_dataset(data_config: Dict[str, Any]) -> SyntheticCodeDataset:
    """Create synthetic training dataset."""
    return SyntheticCodeDataset(
        num_samples=data_config["num_train_samples"],
        seq_length=data_config["seq_length"],
        vocab_size=data_config["vocab_size"],
        seed=42,
    )


@pytest.fixture
def synthetic_val_dataset(data_config: Dict[str, Any]) -> SyntheticCodeDataset:
    """Create synthetic validation dataset."""
    return SyntheticCodeDataset(
        num_samples=data_config["num_val_samples"],
        seq_length=data_config["seq_length"],
        vocab_size=data_config["vocab_size"],
        seed=43,
    )


@pytest.fixture
def train_dataloader(
    synthetic_train_dataset: SyntheticCodeDataset,
    training_config: Dict[str, Any],
) -> DataLoader:
    """Create training dataloader."""
    return DataLoader(
        synthetic_train_dataset,
        batch_size=training_config["batch_size"],
        shuffle=True,
    )


@pytest.fixture
def val_dataloader(
    synthetic_val_dataset: SyntheticCodeDataset,
    training_config: Dict[str, Any],
) -> DataLoader:
    """Create validation dataloader."""
    return DataLoader(
        synthetic_val_dataset,
        batch_size=training_config["batch_size"],
        shuffle=False,
    )


@pytest.fixture
def model(
    device: torch.device,
    model_config: Dict[str, Any],
) -> MiniTransformerModel:
    """Create mini transformer model."""
    model = MiniTransformerModel(**model_config)
    return model.to(device)


@pytest.fixture
def optimizer(
    model: MiniTransformerModel,
    training_config: Dict[str, Any],
) -> optim.Adam:
    """Create optimizer."""
    return optim.Adam(model.parameters(), lr=training_config["learning_rate"])


@pytest.fixture
def lr_scheduler(
    optimizer: optim.Adam,
    training_config: Dict[str, Any],
) -> optim.lr_scheduler.LambdaLR:
    """Create learning rate scheduler."""
    total_steps = training_config["num_epochs"] * 10  # Approximate
    warmup_steps = training_config["num_warmup_steps"]

    def lr_lambda(current_step: int) -> float:
        if current_step < warmup_steps:
            return float(current_step) / float(max(1, warmup_steps))
        return max(0.0, float(1.0 - (current_step - warmup_steps) / (total_steps - warmup_steps)))

    return optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)


@pytest.fixture
def checkpoint_dir() -> Path:
    """Create temporary checkpoint directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def training_metrics() -> Dict[str, List[float]]:
    """Training metrics tracker."""
    return {
        "train_loss": [],
        "train_perplexity": [],
        "val_loss": [],
        "val_perplexity": [],
        "learning_rate": [],
        "epoch_times": [],
    }


class TrainingState:
    """Container for training state."""

    def __init__(
        self,
        model: MiniTransformerModel,
        optimizer: optim.Optimizer,
        device: torch.device,
    ):
        """Initialize training state."""
        self.model = model
        self.optimizer = optimizer
        self.device = device
        self.global_step = 0
        self.epoch = 0
        self.best_loss = float("inf")

    def save_checkpoint(
        self,
        checkpoint_path: Path,
        metrics: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Save training checkpoint."""
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        checkpoint = {
            "epoch": self.epoch,
            "global_step": self.global_step,
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "best_loss": self.best_loss,
        }
        if metrics:
            checkpoint["metrics"] = metrics
        torch.save(checkpoint, checkpoint_path)

    def load_checkpoint(self, checkpoint_path: Path) -> Dict[str, Any]:
        """Load training checkpoint."""
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        self.epoch = checkpoint["epoch"]
        self.global_step = checkpoint["global_step"]
        self.best_loss = checkpoint["best_loss"]
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        return checkpoint.get("metrics", {})


@pytest.fixture
def training_state(
    model: MiniTransformerModel,
    optimizer: optim.Optimizer,
    device: torch.device,
) -> TrainingState:
    """Create training state."""
    return TrainingState(model, optimizer, device)
