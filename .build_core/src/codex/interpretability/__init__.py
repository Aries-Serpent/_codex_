"""
ML Interpretability Module

This module provides tools for interpreting and analyzing machine learning models,
with a focus on transformer architectures. It includes utilities for:

- Attention scoring and visualization
- MLP (Multi-Layer Perceptron) activation analysis
- Feature importance scoring
- Model decision explanation

The module is designed to work with PyTorch models, particularly those from the
Hugging Face Transformers library.
"""

from .attention_scorer import AttentionScorer
from .mlp_scorer import MLPScorer

__all__ = ["AttentionScorer", "MLPScorer"]

__version__ = "0.1.0"
