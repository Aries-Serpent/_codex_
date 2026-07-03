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
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[str | torch.device] = None,
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
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        self.model.to(self.device)
        self.model.eval()

    def extract_attention_weights(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> tuple[list[torch.Tensor], list[str]]:
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

    def compute_token_importance(
        self, attention_weights: list[torch.Tensor], method: str = "mean"
    ) -> np.ndarray:
        """
        Compute importance score for each token based on attention patterns.

        Args:
            attention_weights: List of attention tensors from each layer
            method: Method to compute importance ('mean', 'max', 'norm')

        Returns:
            Token importance scores (seq_len,)
        """
        if not attention_weights:
            raise ValueError("No attention weights provided")

        # Stack attention weights across layers
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked = torch.stack([attn[0] for attn in attention_weights])

        if method == "mean":
            # Average attention received by each token
            importance = stacked.mean(dim=(0, 1, 2)).numpy()
        elif method == "max":
            # Max attention received by each token
            importance = stacked.max(dim=2)[0].mean(dim=(0, 1)).numpy()
        elif method == "norm":
            # L2 norm of attention received by each token across layers and heads
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len  # noqa: E501
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def compute_attention_flow(
        self, attention_weights: list[torch.Tensor], layer_aggregation: str = "mean"
    ) -> np.ndarray:
        """
        Compute attention flow matrix between tokens.

        Args:
            attention_weights: List of attention tensors from each layer
            layer_aggregation: How to aggregate across layers ('mean', 'last', 'sum')

        Returns:
            Attention flow matrix (seq_len, seq_len)
        """
        if not attention_weights:
            raise ValueError("No attention weights provided")

        # Stack attention weights: (num_layers, num_heads, seq_len, seq_len)
        stacked = torch.stack([attn[0] for attn in attention_weights])

        # Average across heads first
        stacked = stacked.mean(dim=1)

        # Aggregate across layers
        if layer_aggregation == "mean":
            flow = stacked.mean(dim=0).numpy()
        elif layer_aggregation == "last":
            flow = stacked[-1].numpy()
        elif layer_aggregation == "sum":
            flow = stacked.sum(dim=0).numpy()
        else:
            raise ValueError(f"Unknown aggregation: {layer_aggregation}")

        return flow

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
