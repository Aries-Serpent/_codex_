"""
Attention Scoring Module

This module provides tools for analyzing attention patterns in transformer models.
It supports:
- Extracting attention weights from transformer layers
- Computing attention scores for input tokens
- Analyzing attention flow between tokens
- Identifying important tokens based on attention patterns
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np

import torch

logger = logging.getLogger(__name__)


@dataclass
class AttentionAnalysis:
    """Results from attention analysis."""

    # Attention weights shape: (num_layers, num_heads, seq_len, seq_len)
    attention_weights: np.ndarray

    # Token importance scores shape: (seq_len,)
    token_importance: np.ndarray

    # Attention flow between tokens shape: (seq_len, seq_len)
    attention_flow: np.ndarray

    # Layer names
    layer_names: list[str]

    # Token IDs
    token_ids: Optional[list[int]] = None

    # Token strings (if provided)
    tokens: Optional[list[str]] = None


class AttentionScorer:
    """
    Analyzer for transformer attention patterns.

    This class provides methods to extract and analyze attention weights from
    transformer models, computing importance scores and attention flow patterns.

    Example:
        >>> from transformers import AutoModel, AutoTokenizer
        >>> model = AutoModel.from_pretrained("bert-base-uncased")
        >>> tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
        >>>
        >>> scorer = AttentionScorer(model)
        >>> text = "The quick brown fox jumps over the lazy dog"
        >>> inputs = tokenizer(text, return_tensors="pt")
        >>>
        >>> analysis = scorer.analyze_attention(
        ...     input_ids=inputs["input_ids"],
        ...     tokens=tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        ... )
        >>>
        >>> # Get most important tokens
        >>> important_indices = np.argsort(analysis.token_importance)[-5:]
        >>> logger.info([analysis.tokens[i] for i in important_indices])
    """

    def __init__(
        self,
        model: Optional[object] = None,
        normalize: bool = True,
        device: Optional[str | object] = None,
        epsilon: float = 1e-10,
    ):
        """
        Initialize the attention scorer.

        Args:
            model: Transformer model with attention mechanisms
            normalize: Whether to normalize attention scores
            device: Device to run analysis on (cuda/cpu)
            epsilon: Small value for numerical stability in normalization
        """
        self.model = model
        self.normalize = normalize
        self.epsilon = epsilon
        self.device = torch.device(device or "cpu")
        if model is not None:
            to = getattr(model, "to", None)
            if callable(to):
                try:
                    to(self.device)
                except (TypeError, ValueError, RuntimeError) as exc:
                    logger.debug(
                        "Model .to(%s) failed; continuing with the current model placement",
                        self.device,
                        exc_info=True,
                    )
            eval_model = getattr(model, "eval", None)
            if callable(eval_model):
                eval_model()

    @staticmethod
    def _to_numpy(value: object) -> np.ndarray:
        """Convert tensors or array-like attention values to a NumPy array."""
        if value is None:
            raise TypeError("Attention weights must not be None")
        detach = getattr(value, "detach", None)
        if callable(detach):
            value = detach()
        cpu = getattr(value, "cpu", None)
        if callable(cpu):
            value = cpu()
        numpy = getattr(value, "numpy", None)
        if callable(numpy):
            value = numpy()
        return np.asarray(value)

    def extract_attention_weights(
        self,
        input_ids: object,
        attention_mask: Optional[object] = None,
    ) -> object:
        """
        Extract attention weights from all layers of the model.

        Args:
            input_ids: Input token IDs (batch_size, seq_len)
            attention_mask: Attention mask (batch_size, seq_len)

        Returns:
            Tuple of (attention_weights, layer_names)
            - attention_weights: List of attention tensors per layer
            - layer_names: Names of the layers
        """
        if isinstance(input_ids, np.ndarray) or not hasattr(input_ids, "to"):
            return self._validate_attention_array(input_ids)

        input_ids = input_ids.to(self.device)
        if attention_mask is not None:
            attention_mask = attention_mask.to(self.device)

        attention_weights = []
        layer_names = []

        # Hook to capture attention weights
        def attention_hook(module, input, output) -> None:
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ["attention", "attn"]):
                if hasattr(module, "forward"):
                    hook = module.register_forward_hook(attention_hook)
                    hooks.append(hook)
                    layer_names.append(name)

        # Forward pass
        with torch.no_grad():
            try:
                # Try standard Hugging Face interface
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    output_attentions=True,
                )

                # Extract attention from outputs if available
                if hasattr(outputs, "attentions") and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.warning("Could not extract attention using standard interface: <ERROR_TYPE>")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def _validate_attention_array(self, weights: object) -> np.ndarray:
        array = self._to_numpy(weights)
        if array.size == 0:
            raise ValueError("Attention weights must not be empty")
        if array.ndim not in (2, 3, 4):
            raise ValueError("Attention weights must be 2D, 3D, or 4D")
        return np.nan_to_num(array, copy=True, nan=0.0, posinf=0.0, neginf=0.0)

    def compute_token_importance(
        self, attention_weights: object, method: str = "mean"
    ) -> np.ndarray:
        """
        Compute importance score for each token based on attention patterns.

        Args:
            attention_weights: List of attention tensors from each layer
            method: Method to compute importance ('mean', 'max', 'norm')

        Returns:
            Token importance scores (seq_len,)
        """
        if attention_weights is None:
            raise TypeError("Attention weights must not be None")
        if method not in {"mean", "max", "norm"}:
            raise ValueError(f"Unknown method: {method}")

        if isinstance(attention_weights, (list, tuple)):
            if not attention_weights:
                raise ValueError("No attention weights provided")
            stacked = np.stack(
                [self._validate_attention_array(weights) for weights in attention_weights]
            )
        else:
            stacked = self._validate_attention_array(attention_weights)

        if stacked.ndim == 4:
            numpy_attention = stacked
        elif stacked.ndim == 3:
            numpy_attention = stacked[np.newaxis, ...]
        elif stacked.ndim == 2:
            numpy_attention = stacked[np.newaxis, np.newaxis, ...]
        elif stacked.ndim == 5:
            if stacked.shape[1] != 1:
                raise ValueError("Attention weights must use a single batch item")
            numpy_attention = stacked[:, 0, ...]
        else:
            raise ValueError("Attention weights must be 2D, 3D, or 4D")

        # Stack attention weights across layers
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked = numpy_attention

        if method == "mean":
            # Average attention received by each token
            importance = stacked.mean(axis=(0, 1, 2))
        elif method == "max":
            # Max attention received by each token
            importance = stacked.max(axis=2).mean(axis=(0, 1))
        elif method == "norm":
            aggregated = stacked.mean(axis=(0, 1))
            importance = np.linalg.norm(aggregated, axis=0)
        else:
            raise ValueError(f"Unknown method: {method}")

        importance = np.nan_to_num(np.asarray(importance, dtype=float), nan=0.0)
        importance = np.maximum(importance, 0.0)
        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def compute_attention_flow(
        self, attention_weights: object, layer_aggregation: str = "mean"
    ) -> np.ndarray:
        """
        Compute attention flow matrix between tokens.

        Args:
            attention_weights: List of attention tensors from each layer
            layer_aggregation: How to aggregate across layers ('mean', 'last', 'sum')

        Returns:
            Attention flow matrix (seq_len, seq_len)
        """
        if attention_weights is None:
            raise TypeError("Attention weights must not be None")

        if isinstance(attention_weights, (list, tuple)):
            if not attention_weights:
                raise ValueError("No attention weights provided")
            arrays = [self._validate_attention_array(weights) for weights in attention_weights]
            try:
                stacked = np.stack(arrays)
            except ValueError as exc:
                raise ValueError("Attention weight layers must have matching shapes") from exc
        else:
            stacked = self._validate_attention_array(attention_weights)

        if stacked.ndim == 5:
            stacked = stacked.mean(axis=(0, 2))
        elif stacked.ndim == 4:
            stacked = stacked.mean(axis=(0, 1))
        elif stacked.ndim == 3:
            stacked = stacked.mean(axis=0)
        elif stacked.ndim != 2:
            raise ValueError("Attention weights must be 2D, 3D, or 4D")

        if isinstance(attention_weights, (list, tuple)) and stacked.ndim == 3:
            if layer_aggregation == "mean":
                flow = stacked.mean(axis=0)
            elif layer_aggregation == "last":
                flow = stacked[-1]
            elif layer_aggregation == "sum":
                flow = stacked.sum(axis=0)
            else:
                raise ValueError(f"Unknown aggregation: {layer_aggregation}")
        elif stacked.ndim == 2:
            flow = stacked
        else:
            if layer_aggregation == "mean":
                flow = stacked.mean(axis=0)
            elif layer_aggregation == "last":
                flow = stacked[-1]
            elif layer_aggregation == "sum":
                flow = stacked.sum(axis=0)
            else:
                raise ValueError(f"Unknown aggregation: {layer_aggregation}")

        flow = np.nan_to_num(np.abs(np.asarray(flow, dtype=float)), nan=0.0)
        maximum = float(flow.max()) if flow.size else 0.0
        if maximum > self.epsilon:
            flow = flow / maximum
        return flow

    def analyze_attention_flow(self, attention_weights: object) -> np.ndarray:
        """NumPy-compatible alias for attention flow analysis."""
        return self.compute_attention_flow(attention_weights)

    def create_layer_mapping(self, layer_names: list[str]) -> dict[str, int]:
        """Map layer names to their positions."""
        return {name: index for index, name in enumerate(layer_names)}

    def analyze_by_layer(
        self, attention_weights: object, layer_names: Optional[list[str]] = None
    ) -> AttentionAnalysis:
        """Analyze attention weights while preserving layer names."""
        return self.full_analysis(
            attention_weights=attention_weights,
            layer_names=layer_names,
        )

    def analyze_attention_heads(self, attention_weights: object) -> list[np.ndarray]:
        """Split attention weights into individual head matrices."""
        weights = self._validate_attention_array(attention_weights)
        if weights.ndim == 4:
            heads = [weights[0, head] for head in range(weights.shape[1])]
        elif weights.ndim == 3:
            heads = [weights[head] for head in range(weights.shape[0])]
        elif weights.ndim == 2:
            heads = [weights]
        else:
            raise ValueError("Attention weights must be 2D, 3D, or 4D")
        return heads

    def rank_attention_heads(self, attention_weights: object) -> np.ndarray:
        """Rank attention heads by mean attention strength."""
        heads = self.analyze_attention_heads(attention_weights)
        importance = np.asarray([head.mean() for head in heads], dtype=float)
        importance = np.abs(np.nan_to_num(importance, nan=0.0))
        if self.normalize and importance.sum() > self.epsilon:
            importance = importance / importance.sum()
        return importance

    def detect_head_specialization(
        self, attention_weights: object
    ) -> dict[str, dict[str, float | str]]:
        """Describe simple positional and distributed patterns for each head."""
        heads = self.analyze_attention_heads(attention_weights)
        specialization: dict[str, dict[str, float | str]] = {}
        for index, head in enumerate(heads):
            if head.shape[0] == head.shape[1] and head.size:
                diagonal = float(np.abs(np.diag(head)).mean())
                distributed = float(np.abs(head).mean())
            else:
                diagonal = 0.0
                distributed = float(np.abs(head).mean())
            specialization[f"head_{index}"] = {
                "diagonal_attention": diagonal,
                "specialization": "positional" if diagonal >= distributed else "distributed",
            }
        return specialization

    def full_analysis(
        self,
        attention_weights: Optional[object] = None,
        layer_names: Optional[list[str]] = None,
        token_ids: Optional[list[int]] = None,
        tokens: Optional[list[str]] = None,
        **kwargs: object,
    ) -> AttentionAnalysis:
        """Run a complete NumPy attention analysis for utility-style callers."""
        if attention_weights is None:
            attention_weights = kwargs.get("weights")
        if attention_weights is None:
            raise TypeError("attention_weights must not be None")

        weights = self._validate_attention_array(attention_weights)
        importance = self.compute_token_importance(weights)
        flow = self.analyze_attention_flow(weights)

        if weights.ndim == 4:
            num_layers = weights.shape[0]
            seq_len = weights.shape[-1]
        elif weights.ndim == 3:
            num_layers = weights.shape[0]
            seq_len = weights.shape[-1]
        else:
            num_layers = 1
            seq_len = weights.shape[-1]

        if layer_names is None:
            layer_names = [f"layer_{index}" for index in range(num_layers)]
        if token_ids is None and seq_len:
            token_ids = list(range(seq_len))

        return AttentionAnalysis(
            attention_weights=weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=token_ids,
            tokens=tokens,
        )

    def analyze_attention(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[list[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean",
    ) -> AttentionAnalysis:
        """
        Perform complete attention analysis on input.

        Args:
            input_ids: Input token IDs (batch_size, seq_len)
            attention_mask: Attention mask (batch_size, seq_len)
            tokens: Token strings for visualization
            importance_method: Method for computing token importance
            flow_aggregation: Method for aggregating attention flow

        Returns:
            AttentionAnalysis object with all results
        """
        # Extract attention weights
        attn_weights, layer_names = self.extract_attention_weights(input_ids, attention_mask)

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(attn_weights, method=importance_method)

        # Compute attention flow
        flow = self.compute_attention_flow(attn_weights, layer_aggregation=flow_aggregation)

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([attn[0].numpy() for attn in attn_weights])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens,
        )

    def get_top_attended_tokens(
        self, analysis: AttentionAnalysis, top_k: int = 5
    ) -> list[tuple[int, float, Optional[str]]]:
        """
        Get the top-k most attended tokens.

        Args:
            analysis: AttentionAnalysis result
            top_k: Number of top tokens to return

        Returns:
            List of (token_index, importance_score, token_string) tuples
        """
        top_indices = np.argsort(analysis.token_importance)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            token_str = analysis.tokens[idx] if analysis.tokens else None
            results.append((int(idx), float(analysis.token_importance[idx]), token_str))

        return results
