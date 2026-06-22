# Complete Python API Reference

> **Version**: 1.0.0  
> **Last Updated**: 2026-06-22  
> **Package**: `codex-ml` (PyPI)  
> **Python**: 3.9+  
> **Status**: Production-Ready  

---

## Table of Contents

1. [Core Module Overview](#core-module-overview)
2. [Training Module](#training-module)
3. [Evaluation Module](#evaluation-module)
4. [Data Module](#data-module)
5. [Configuration Module](#configuration-module)
6. [Models Module](#models-module)
7. [Utilities Module](#utilities-module)
8. [Exception Hierarchy](#exception-hierarchy)
9. [Type Hints Reference](#type-hints-reference)
10. [Performance Considerations](#performance-considerations)

---

## Core Module Overview

### `src.codex_ml`

The main package providing ML training, evaluation, and inference capabilities.

```python
from src.codex_ml import (
    train,
    evaluate,
    CodexModel,
    CodexConfig,
    CodexData,
)
```

#### Available Exports

| Name | Type | Purpose |
|------|------|---------|
| `train` | Function | Main training entry point |
| `evaluate` | Function | Model evaluation interface |
| `CodexModel` | Class | Base model class |
| `CodexConfig` | Class | Configuration management |
| `CodexData` | Class | Data loading and processing |
| `__version__` | str | Package version |

---

## Training Module

### `src.codex_ml.training`

Provides training pipelines and engine abstractions.

#### Class: `TrainingEngine`

```python
class TrainingEngine:
    """
    Base training engine for model training workflows.

    Attributes:
        model (torch.nn.Module): Neural network model
        optimizer (torch.optim.Optimizer): Optimization algorithm
        config (TrainingConfig): Training configuration
        device (str): Computation device ('cpu', 'cuda', 'mps')
    """

    def __init__(
        self,
        model: torch.nn.Module,
        config: TrainingConfig,
        device: str = 'cuda' if torch.cuda.is_available() else 'cpu'
    ) -> None:
        """
        Initialize training engine.

        Args:
            model: PyTorch model to train
            config: Training configuration object
            device: Computation device (default: auto-detect)

        Raises:
            ValueError: If device is not available
            TypeError: If model is not nn.Module
        """
        ...

    def train_epoch(
        self,
        train_loader: torch.utils.data.DataLoader,
        val_loader: Optional[torch.utils.data.DataLoader] = None
    ) -> Dict[str, float]:
        """
        Train for one epoch.

        Args:
            train_loader: Training data loader
            val_loader: Optional validation data loader

        Returns:
            Dictionary with metrics:
            - 'loss': Average training loss
            - 'val_loss': Average validation loss (if val_loader provided)
            - 'lr': Current learning rate
            - 'time_sec': Epoch duration in seconds

        Raises:
            RuntimeError: If training fails

        Example:
            >>> metrics = engine.train_epoch(train_loader, val_loader)
            >>> print(f"Loss: {metrics['loss']:.4f}")
        """
        ...

    def train_steps(
        self,
        num_steps: int,
        train_loader: torch.utils.data.DataLoader
    ) -> Dict[str, List[float]]:
        """
        Train for N steps instead of epochs.

        Args:
            num_steps: Number of training steps
            train_loader: Training data loader

        Returns:
            Dictionary with loss history:
            - 'losses': List of loss values per step
            - 'steps': List of step numbers

        Yields during training:
            Progress information every 10 steps
        """
        ...

    def save_checkpoint(
        self,
        path: str,
        include_optimizer: bool = True,
        include_config: bool = True
    ) -> None:
        """
        Save training checkpoint.

        Args:
            path: Save path (e.g., 'checkpoints/epoch_5.pt')
            include_optimizer: Include optimizer state
            include_config: Include configuration

        Raises:
            IOError: If path is not writable

        Example:
            >>> engine.save_checkpoint('checkpoint.pt')
        """
        ...

    def load_checkpoint(
        self,
        path: str,
        load_optimizer: bool = True,
        strict: bool = True
    ) -> None:
        """
        Load training checkpoint.

        Args:
            path: Checkpoint path to load
            load_optimizer: Load optimizer state
            strict: Strict model loading

        Raises:
            FileNotFoundError: If checkpoint not found
            RuntimeError: If incompatible checkpoint format
        """
        ...
```

#### Class: `HFTrainer`

```python
class HFTrainer(TrainingEngine):
    """
    Hugging Face Transformers trainer wrapper.

    Extends TrainingEngine with Hugging Face specific features.
    """

    def __init__(
        self,
        model: transformers.PreTrainedModel,
        args: transformers.TrainingArguments,
        train_dataset: datasets.Dataset,
        eval_dataset: Optional[datasets.Dataset] = None,
        data_collator: Optional[Callable] = None,
        callbacks: Optional[List] = None
    ) -> None:
        """
        Initialize Hugging Face Trainer.

        Args:
            model: Pre-trained Hugging Face model
            args: Training arguments configuration
            train_dataset: Training dataset
            eval_dataset: Validation dataset
            data_collator: Custom data collator function
            callbacks: List of trainer callbacks

        Example:
            >>> from transformers import AutoModelForCausalLM
            >>> model = AutoModelForCausalLM.from_pretrained('gpt2')
            >>> trainer = HFTrainer(model=model, args=args, ...)
        """
        ...

    def train(
        self,
        resume_from_checkpoint: Optional[str] = None
    ) -> transformers.trainer_utils.TrainOutput:
        """
        Execute training loop.

        Args:
            resume_from_checkpoint: Path to checkpoint to resume from

        Returns:
            TrainOutput with training metrics

        Raises:
            ValueError: If training arguments invalid
        """
        ...

    def evaluate(
        self,
        eval_dataset: Optional[datasets.Dataset] = None
    ) -> Dict[str, float]:
        """
        Evaluate model on dataset.

        Args:
            eval_dataset: Dataset to evaluate on (uses eval_dataset if None)

        Returns:
            Dictionary of evaluation metrics
        """
        ...
```

#### Function: `train()`

```python
def train(
    config: Union[str, TrainingConfig],
    output_dir: str = './outputs',
    resume_from_checkpoint: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Main training function.

    Args:
        config: Path to config file or TrainingConfig object
        output_dir: Output directory for checkpoints and logs
        resume_from_checkpoint: Optional checkpoint path to resume from
        **kwargs: Additional arguments to override config

    Returns:
        Dictionary containing:
        - 'model': Trained model
        - 'metrics': Final metrics
        - 'checkpoints': List of saved checkpoints

    Raises:
        FileNotFoundError: If config file not found
        ValueError: If configuration invalid

    Example:
        >>> results = train(
        ...     config='configs/training/base.yaml',
        ...     output_dir='./checkpoints',
        ...     batch_size=32
        ... )
        >>> model = results['model']
    """
    ...
```

---

## Evaluation Module

### `src.codex_ml.evaluation`

Provides evaluation metrics and assessment utilities.

#### Class: `Evaluator`

```python
class Evaluator:
    """
    Model evaluation coordinator.

    Supports multiple evaluation modes and metric computation.
    """

    def __init__(
        self,
        model: torch.nn.Module,
        device: str = 'cuda' if torch.cuda.is_available() else 'cpu',
        num_workers: int = 4
    ) -> None:
        """
        Initialize evaluator.

        Args:
            model: Model to evaluate
            device: Computation device
            num_workers: Number of data loading workers
        """
        ...

    def evaluate(
        self,
        eval_loader: torch.utils.data.DataLoader,
        metrics: List[str] = ['loss', 'accuracy', 'f1']
    ) -> Dict[str, float]:
        """
        Evaluate model on dataset.

        Args:
            eval_loader: Evaluation data loader
            metrics: List of metrics to compute

        Returns:
            Dictionary mapping metric names to values

        Supported metrics:
        - 'loss': Classification/regression loss
        - 'accuracy': Accuracy (classification)
        - 'f1': F1 score (classification)
        - 'precision': Precision (classification)
        - 'recall': Recall (classification)
        - 'bleu': BLEU score (generation)
        - 'rouge': ROUGE score (generation)
        - 'perplexity': Perplexity (language model)
        """
        ...

    def evaluate_on_file(
        self,
        file_path: str,
        file_format: str = 'json',
        batch_size: int = 32
    ) -> Dict[str, float]:
        """
        Evaluate on data from file.

        Args:
            file_path: Path to evaluation file
            file_format: Format of file ('json', 'csv', 'parquet')
            batch_size: Batch size for evaluation

        Returns:
            Evaluation metrics dictionary
        """
        ...

    def compute_metric(
        self,
        predictions: np.ndarray,
        references: np.ndarray,
        metric_name: str
    ) -> float:
        """
        Compute single metric.

        Args:
            predictions: Model predictions
            references: Ground truth labels
            metric_name: Name of metric

        Returns:
            Metric value
        """
        ...
```

#### Function: `evaluate()`

```python
def evaluate(
    model: torch.nn.Module,
    eval_path: str,
    config: Union[str, EvalConfig],
    **kwargs
) -> Dict[str, float]:
    """
    Main evaluation function.

    Args:
        model: Model to evaluate
        eval_path: Path to evaluation data
        config: Evaluation configuration
        **kwargs: Additional arguments

    Returns:
        Dictionary of evaluation metrics

    Example:
        >>> metrics = evaluate(
        ...     model=model,
        ...     eval_path='data/test.jsonl',
        ...     config='configs/eval.yaml'
        ... )
    """
    ...
```

---

## Data Module

### `src.codex_ml.data`

Data loading, preprocessing, and pipeline utilities.

#### Class: `CodexData`

```python
class CodexData:
    """
    High-level data interface for loading and preprocessing.

    Attributes:
        path (str): Data path
        split (str): Data split ('train', 'val', 'test')
        batch_size (int): Batch size
        num_workers (int): Number of data loading workers
    """

    def __init__(
        self,
        path: str,
        split: str = 'train',
        batch_size: int = 32,
        num_workers: int = 4,
        tokenizer: Optional[Any] = None,
        max_length: int = 512,
        preprocessing_fn: Optional[Callable] = None
    ) -> None:
        """
        Initialize data loader.

        Args:
            path: Path to data file or directory
            split: Which split to load
            batch_size: Batch size
            num_workers: Number of parallel workers
            tokenizer: Optional tokenizer for text data
            max_length: Maximum sequence length
            preprocessing_fn: Optional preprocessing function

        Raises:
            FileNotFoundError: If path not found
            ValueError: If split invalid
        """
        ...

    def __iter__(self):
        """Iterate over batches."""
        ...

    def __len__(self) -> int:
        """Return number of batches."""
        ...

    @property
    def dataset(self) -> datasets.Dataset:
        """Get underlying dataset."""
        ...

    def get_loader(self) -> torch.utils.data.DataLoader:
        """
        Get PyTorch DataLoader.

        Returns:
            Configured DataLoader instance
        """
        ...

    def preprocess(
        self,
        fn: Callable,
        batched: bool = True,
        remove_columns: Optional[List[str]] = None
    ) -> 'CodexData':
        """
        Apply preprocessing function.

        Args:
            fn: Preprocessing function
            batched: Process in batches
            remove_columns: Columns to remove after preprocessing

        Returns:
            Self for chaining
        """
        ...

    def save(self, path: str) -> None:
        """Save dataset to disk."""
        ...

    def load(self, path: str) -> None:
        """Load dataset from disk."""
        ...
```

#### Function: `load_data()`

```python
def load_data(
    path: str,
    split: str = 'train',
    limit: Optional[int] = None,
    cache_dir: str = '.cache',
    **kwargs
) -> CodexData:
    """
    Load data with automatic format detection.

    Args:
        path: Path to data (file or directory)
        split: Data split to load
        limit: Maximum examples to load
        cache_dir: Directory for caching
        **kwargs: Additional loader arguments

    Returns:
        CodexData instance

    Supported formats:
    - JSON/JSONL
    - CSV/TSV
    - Parquet
    - HuggingFace Datasets
    - Arrow/IPC

    Example:
        >>> data = load_data('data/train.jsonl')
        >>> for batch in data:
        ...     print(batch['input_ids'].shape)
    """
    ...
```

---

## Configuration Module

### `src.codex_ml.config`

Configuration management and schema validation.

#### Class: `CodexConfig`

```python
class CodexConfig:
    """
    Configuration container with type validation.

    Supports loading from files, environment variables, and direct assignment.
    """

    def __init__(
        self,
        **kwargs
    ) -> None:
        """
        Initialize configuration.

        Args:
            **kwargs: Configuration parameters

        Example:
            >>> config = CodexConfig(
            ...     model_name='gpt2',
            ...     batch_size=32,
            ...     learning_rate=1e-4
            ... )
        """
        ...

    @classmethod
    def from_file(cls, path: str) -> 'CodexConfig':
        """
        Load configuration from file.

        Args:
            path: Path to config file (YAML or JSON)

        Returns:
            CodexConfig instance

        Raises:
            FileNotFoundError: If file not found
        """
        ...

    @classmethod
    def from_env(cls) -> 'CodexConfig':
        """
        Load configuration from environment variables.

        Environment variable pattern: CODEX_<PARAM_NAME>

        Returns:
            CodexConfig instance
        """
        ...

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        ...

    def to_yaml(self, path: str) -> None:
        """Save configuration to YAML file."""
        ...

    def to_json(self, path: str) -> None:
        """Save configuration to JSON file."""
        ...

    def update(self, **kwargs) -> None:
        """Update configuration values."""
        ...

    def validate(self) -> bool:
        """
        Validate configuration against schema.

        Returns:
            True if valid

        Raises:
            ValueError: If validation fails
        """
        ...
```

---

## Models Module

### `src.codex_ml.models`

Pre-configured model factory and architectures.

#### Function: `create_model()`

```python
def create_model(
    model_name: str,
    pretrained: bool = True,
    num_labels: Optional[int] = None,
    config_overrides: Optional[Dict] = None,
    **kwargs
) -> torch.nn.Module:
    """
    Create model by name.

    Args:
        model_name: Model identifier (e.g., 'gpt2', 'bert-base')
        pretrained: Load pretrained weights
        num_labels: Number of output labels (for classification)
        config_overrides: Configuration overrides
        **kwargs: Additional model arguments

    Returns:
        Initialized model

    Supported models:
    - gpt2, gpt2-medium, gpt2-large
    - bert-base-uncased, bert-large-uncased
    - distilbert-base-uncased
    - roberta-base, roberta-large
    - t5-small, t5-base, t5-large
    - custom local models

    Example:
        >>> model = create_model('gpt2', pretrained=True)
        >>> model = create_model('bert-base-uncased', num_labels=2)
    """
    ...
```

#### Class: `CodexModel`

```python
class CodexModel(torch.nn.Module):
    """
    Base model wrapper with unified interface.

    Provides training and inference utilities on top of base model.
    """

    def __init__(
        self,
        model_name: str,
        device: str = 'cuda' if torch.cuda.is_available() else 'cpu'
    ) -> None:
        """
        Initialize model.

        Args:
            model_name: Identifier or path to model
            device: Computation device
        """
        ...

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        **kwargs
    ) -> torch.Tensor:
        """
        Forward pass.

        Args:
            input_ids: Token IDs [batch_size, seq_length]
            attention_mask: Attention mask [batch_size, seq_length]
            **kwargs: Additional model-specific arguments

        Returns:
            Model output tensor
        """
        ...

    def generate(
        self,
        input_ids: torch.Tensor,
        max_length: int = 100,
        top_k: int = 50,
        top_p: float = 0.95,
        temperature: float = 1.0,
        num_return_sequences: int = 1,
        **kwargs
    ) -> torch.Tensor:
        """
        Generate text.

        Args:
            input_ids: Input token IDs
            max_length: Maximum generation length
            top_k: Top-k sampling parameter
            top_p: Top-p (nucleus) sampling parameter
            temperature: Sampling temperature
            num_return_sequences: Number of sequences to generate
            **kwargs: Additional generation arguments

        Returns:
            Generated token IDs
        """
        ...

    def freeze_backbone(self) -> None:
        """Freeze all parameters except classification head."""
        ...

    def get_num_parameters(self) -> int:
        """Return total number of parameters."""
        ...

    def get_trainable_parameters(self) -> int:
        """Return number of trainable parameters."""
        ...
```

---

## Utilities Module

### `src.codex_ml.utils`

Helper functions for common tasks.

#### Function: `set_seed()`

```python
def set_seed(seed: int) -> None:
    """
    Set random seed for reproducibility.

    Sets seed for Python, NumPy, PyTorch, and CUDA.

    Args:
        seed: Random seed value

    Example:
        >>> set_seed(42)
    """
    ...
```

#### Function: `get_device()`

```python
def get_device(device: Optional[str] = None) -> torch.device:
    """
    Get computation device.

    Args:
        device: Device specification ('cpu', 'cuda', 'mps', or None for auto)

    Returns:
        torch.device instance

    Example:
        >>> device = get_device()  # Auto-detect
        >>> device = get_device('cuda')
    """
    ...
```

#### Class: `Timer`

```python
class Timer:
    """Context manager for timing code blocks."""

    def __enter__(self) -> 'Timer':
        """Start timer."""
        ...

    def __exit__(self, *args) -> None:
        """Stop timer and print elapsed time."""
        ...

    @property
    def elapsed(self) -> float:
        """Return elapsed time in seconds."""
        ...
```

---

## Exception Hierarchy

```python
# Base exception
class CodexException(Exception):
    """Base exception for all codex-ml exceptions."""
    pass

# Configuration exceptions
class ConfigurationError(CodexException):
    """Configuration-related error."""
    pass

class InvalidConfigError(ConfigurationError):
    """Invalid configuration error."""
    pass

# Data exceptions
class DataError(CodexException):
    """Data loading/processing error."""
    pass

class DataNotFoundError(DataError):
    """Data file not found."""
    pass

class DataFormatError(DataError):
    """Invalid data format."""
    pass

# Model exceptions
class ModelError(CodexException):
    """Model-related error."""
    pass

class ModelNotFoundError(ModelError):
    """Model not found."""
    pass

class InferenceError(ModelError):
    """Inference execution error."""
    pass

# Training exceptions
class TrainingError(CodexException):
    """Training-related error."""
    pass

class CheckpointError(TrainingError):
    """Checkpoint save/load error."""
    pass

# Evaluation exceptions
class EvaluationError(CodexException):
    """Evaluation-related error."""
    pass

class MetricComputationError(EvaluationError):
    """Metric computation error."""
    pass
```

---

## Type Hints Reference

Common type hints used throughout the API:

```python
from typing import (
    Any, Dict, List, Optional, Tuple, Union, Callable
)
import torch
import numpy as np

# Common type aliases
Device = Union[str, torch.device]
Tensor = torch.Tensor
Array = np.ndarray
PathLike = Union[str, Path]
OptionalDict = Optional[Dict[str, Any]]

# Function signatures
Preprocessor = Callable[[Dict[str, Any]], Dict[str, Any]]
MetricFn = Callable[[np.ndarray, np.ndarray], float]
LossFn = Callable[[Tensor, Tensor], Tensor]
```

---

## Performance Considerations

### Memory Optimization

```python
# Use mixed precision training
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()

for batch in dataloader:
    with autocast():
        output = model(batch)
        loss = criterion(output, batch['labels'])

    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
```

## Distributed Training

```python
# Multi-GPU training with DistributedDataParallel
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel

dist.init_process_group(backend='nccl')
model = model.to(rank)
model = DistributedDataParallel(model)
```

## Batch Size Guidelines

| GPU Memory | Recommended Batch Size |
|------------|------------------------|
| 8 GB | 8-16 |
| 16 GB | 16-32 |
| 32 GB | 32-64 |
| 48 GB | 64-128 |

---

## References

- [PyTorch Documentation](https://pytorch.org/docs/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
