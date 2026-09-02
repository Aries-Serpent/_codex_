"""
MLP Scoring Module

This module provides tools for analyzing MLP (Multi-Layer Perceptron) activations
in transformer models. It supports:
- Extracting MLP activations from transformer layers
- Computing neuron importance scores
- Analyzing activation patterns
- Identifying critical neurons for model predictions
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np
import torch

logger = logging.getLogger(__name__)


@dataclass
class MLPAnalysis:
    """Results from MLP analysis."""

    # MLP activations shape: (num_layers, hidden_dim)
    activations: np.ndarray

    # Neuron importance scores shape: (num_layers, hidden_dim)
    neuron_importance: np.ndarray

    # Layer-wise activation statistics
    layer_stats: dict[str, np.ndarray]

    # Layer names
    layer_names: list[str]

    # Input shape
    input_shape: tuple[int, ...]


class MLPScorer:
    """
    Analyzer for MLP activations in transformer models.

    This class provides methods to extract and analyze MLP layer activations,
    computing neuron importance and activation patterns.

    Example:
        >>> from transformers import AutoModel, AutoTokenizer
        >>> model = AutoModel.from_pretrained("bert-base-uncased")
        >>> tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
        >>>
        >>> scorer = MLPScorer(model)
        >>> text = "The quick brown fox jumps over the lazy dog"
        >>> inputs = tokenizer(text, return_tensors="pt")
        >>>
        >>> analysis = scorer.analyze_mlp(
        ...     input_ids=inputs["input_ids"],
        ...     attention_mask=inputs["attention_mask"]
        ... )
        >>>
        >>> # Get top activated neurons in each layer
        >>> top_neurons = scorer.get_top_neurons(analysis, top_k=10)
        >>> for layer_idx, neurons in top_neurons.items():
        ...     logger.info(f"Layer {layer_idx}: {neurons}")
    """

    def __init__(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[str | torch.device] = None,
        epsilon: float = 1e-10,
    ):
        """
        Initialize the MLP scorer.

        Args:
            model: Transformer model with MLP layers
            normalize: Whether to normalize activation scores
            device: Device to run analysis on (cuda/cpu)
            epsilon: Small value for numerical stability in normalization
        """
        self.model = model
        self.normalize = normalize
        self.epsilon = epsilon
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        self.model.to(self.device)
        self.model.eval()

    def _is_mlp_layer(self, layer_name: str) -> bool:
        """
        Determine if a layer is an MLP/FFN layer based on its name.

        Args:
            layer_name: Name of the layer

        Returns:
            True if the layer is an MLP layer to analyze
        """
        name_lower = layer_name.lower()
        leaf_name = name_lower.split(".")[-1]

        # Only hook the top-level MLP/FFN modules, not their internal linear layers.
        if leaf_name in {"mlp", "ffn", "intermediate"}:
            if leaf_name == "intermediate":
                return True
            return True
        # Fallback to common naming for standalone blocks.
        return leaf_name in {"dense", "feedforward"}

    def extract_mlp_activations(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> tuple[list[torch.Tensor], list[str]]:
        """
        Extract MLP activations from all layers of the model.

        Args:
            input_ids: Input token IDs (batch_size, seq_len)
            attention_mask: Attention mask (batch_size, seq_len)

        Returns:
            Tuple of (mlp_activations, layer_names)
            - mlp_activations: List of activation tensors per layer
            - layer_names: Names of the MLP layers
        """
        input_ids = input_ids.to(self.device)
        if attention_mask is not None:
            attention_mask = attention_mask.to(self.device)

        mlp_activations = []
        layer_names = []

        # Hook to capture MLP activations
        def mlp_hook(module, input, output) -> None:
            # Capture the output of MLP layers
            if isinstance(output, torch.Tensor):
                mlp_activations.append(output.detach().cpu())
            elif isinstance(output, tuple):
                mlp_activations.append(output[0].detach().cpu())

        # Register hooks on MLP/FFN modules
        hooks = []
        for name, module in self.model.named_modules():
            if self._is_mlp_layer(name):
                hook = module.register_forward_hook(mlp_hook)
                hooks.append(hook)
                layer_names.append(name)

        # Forward pass
        with torch.no_grad():
            try:
                self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                )
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.error("Error during forward pass: <ERROR_TYPE>")
                raise

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return mlp_activations, layer_names

    def compute_neuron_importance(
        self, mlp_activations: list[torch.Tensor], method: str = "mean_abs"
    ) -> np.ndarray:
        """
        Compute importance score for each neuron based on activation patterns.

        Args:
            mlp_activations: List of activation tensors from each layer
            method: Method to compute importance ('mean_abs', 'max', 'variance')

        Returns:
            Neuron importance scores (num_layers, hidden_dim)
        """
        if not mlp_activations:
            raise ValueError("No MLP activations provided")

        importance_per_layer = []

        for activation in mlp_activations:
            # activation shape: (batch_size, seq_len, hidden_dim)
            # or (batch_size, hidden_dim)

            if method == "mean_abs":
                # Mean absolute activation across batch and sequence
                if activation.dim() == 3:
                    importance = activation.abs().mean(dim=(0, 1)).numpy()
                else:
                    importance = activation.abs().mean(dim=0).numpy()

            elif method == "max":
                # Max activation across batch and sequence
                if activation.dim() == 3:
                    importance = activation.abs().amax(dim=(0, 1)).numpy()
                else:
                    importance = activation.abs().amax(dim=0).numpy()

            elif method == "variance":
                # Variance of activations
                if activation.dim() == 3:
                    importance = activation.var(dim=(0, 1)).numpy()
                else:
                    importance = activation.var(dim=0).numpy()
            else:
                raise ValueError(f"Unknown method: {method}")

            if self.normalize and importance.sum() > self.epsilon:
                importance = importance / importance.sum()

            importance_per_layer.append(importance)

        # Stack all layers
        return np.stack(importance_per_layer)

    def compute_activation_statistics(
        self, mlp_activations: list[torch.Tensor]
    ) -> dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.

        Args:
            mlp_activations: List of activation tensors from each layer

        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats: dict[str, list[float]] = {
            "mean": [],
            "std": [],
            "min": [],
            "max": [],
            "sparsity": [],  # Fraction of near-zero activations
        }

        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation

            stats["mean"].append(flat.mean(dim=0).numpy())
            stats["std"].append(flat.std(dim=0).numpy())
            stats["min"].append(flat.min(dim=0)[0].numpy())
            stats["max"].append(flat.max(dim=0)[0].numpy())

            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats["sparsity"].append(sparsity)

        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}

    def analyze_mlp(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs",
    ) -> MLPAnalysis:
        """
        Perform complete MLP analysis on input.

        Args:
            input_ids: Input token IDs (batch_size, seq_len)
            attention_mask: Attention mask (batch_size, seq_len)
            importance_method: Method for computing neuron importance

        Returns:
            MLPAnalysis object with all results
        """
        # Extract MLP activations
        activations, layer_names = self.extract_mlp_activations(input_ids, attention_mask)

        if not activations:
            raise ValueError("Failed to extract MLP activations from model")

        # Compute neuron importance
        importance = self.compute_neuron_importance(activations, method=importance_method)

        # Compute activation statistics
        stats = self.compute_activation_statistics(activations)

        # Stack activations for output
        # Average across batch and sequence dimensions
        stacked_activations = []
        for act in activations:
            if act.dim() == 3:
                stacked_activations.append(act.mean(dim=(0, 1)).numpy())
            else:
                stacked_activations.append(act.mean(dim=0).numpy())

        stacked_activations = np.stack(stacked_activations)

        return MLPAnalysis(
            activations=stacked_activations,
            neuron_importance=importance,
            layer_stats=stats,
            layer_names=layer_names,
            input_shape=input_ids.shape,
        )

    def get_top_neurons(
        self, analysis: MLPAnalysis, top_k: int = 10
    ) -> dict[int, list[tuple[int, float]]]:
        """
        Get the top-k most important neurons in each layer.

        Args:
            analysis: MLPAnalysis result
            top_k: Number of top neurons to return per layer

        Returns:
            Dictionary mapping layer_idx to list of (neuron_idx, importance_score) tuples
        """
        top_neurons = {}

        for layer_idx in range(analysis.neuron_importance.shape[0]):
            layer_importance = analysis.neuron_importance[layer_idx]
            top_indices = np.argsort(layer_importance)[-top_k:][::-1]

            top_neurons[layer_idx] = [
                (int(idx), float(layer_importance[idx])) for idx in top_indices
            ]

        return top_neurons

    def get_dead_neurons(
        self, analysis: MLPAnalysis, threshold: float = 0.99
    ) -> dict[int, list[int]]:
        """
        Identify "dead" neurons with very sparse activations.

        Args:
            analysis: MLPAnalysis result
            threshold: Sparsity threshold (0-1) to consider a neuron dead

        Returns:
            Dictionary mapping layer_idx to list of dead neuron indices
        """
        dead_neurons = {}

        sparsity = analysis.layer_stats["sparsity"]

        for layer_idx in range(sparsity.shape[0]):
            dead_indices = np.where(sparsity[layer_idx] > threshold)[0]
            dead_neurons[layer_idx] = dead_indices.tolist()

        return dead_neurons

    def compare_inputs(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> dict[str, np.ndarray]:
        """
        Compare MLP activations between two different inputs.

        Args:
            input_ids_1: First input token IDs
            input_ids_2: Second input token IDs
            attention_mask_1: First attention mask
            attention_mask_2: Second attention mask

        Returns:
            Dictionary with comparison metrics (diff, correlation, distance)
        """
        # Analyze both inputs
        analysis_1 = self.analyze_mlp(input_ids_1, attention_mask_1)
        analysis_2 = self.analyze_mlp(input_ids_2, attention_mask_2)

        # Ensure same number of layers
        if analysis_1.activations.shape[0] != analysis_2.activations.shape[0]:
            raise ValueError("Models have different number of layers")

        # Compute differences
        diff = analysis_1.activations - analysis_2.activations

        # Compute correlation per layer
        correlations = []
        for layer_idx in range(analysis_1.activations.shape[0]):
            act1 = analysis_1.activations[layer_idx]
            act2 = analysis_2.activations[layer_idx]

            # Check for constant arrays (zero variance) to avoid correlation errors
            if np.std(act1) < 1e-10 or np.std(act2) < 1e-10:
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality  # noqa: E501
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]

            correlations.append(corr)

        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)

        return {
            "diff": diff,
            "correlation": np.array(correlations),
            "l2_distance": distances,
        }
