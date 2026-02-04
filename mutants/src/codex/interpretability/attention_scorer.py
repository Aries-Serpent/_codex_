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
from typing import List, Optional, Tuple, Union

import numpy as np

import torch

logger = logging.getLogger(__name__)
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


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
    layer_names: List[str]

    # Token IDs
    token_ids: Optional[List[int]] = None

    # Token strings (if provided)
    tokens: Optional[List[str]] = None


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
        >>> print([analysis.tokens[i] for i in important_indices])
    """

    def xǁAttentionScorerǁ__init____mutmut_orig(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1e-10
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

    def xǁAttentionScorerǁ__init____mutmut_1(
        self,
        model: torch.nn.Module,
        normalize: bool = False,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1e-10
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

    def xǁAttentionScorerǁ__init____mutmut_2(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1.0000000001
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

    def xǁAttentionScorerǁ__init____mutmut_3(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1e-10
    ):
        """
        Initialize the attention scorer.

        Args:
            model: Transformer model with attention mechanisms
            normalize: Whether to normalize attention scores
            device: Device to run analysis on (cuda/cpu)
            epsilon: Small value for numerical stability in normalization
        """
        self.model = None
        self.normalize = normalize
        self.epsilon = epsilon
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        self.model.to(self.device)
        self.model.eval()

    def xǁAttentionScorerǁ__init____mutmut_4(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1e-10
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
        self.normalize = None
        self.epsilon = epsilon
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        self.model.to(self.device)
        self.model.eval()

    def xǁAttentionScorerǁ__init____mutmut_5(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1e-10
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
        self.epsilon = None
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        self.model.to(self.device)
        self.model.eval()

    def xǁAttentionScorerǁ__init____mutmut_6(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1e-10
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
        if device is not None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        self.model.to(self.device)
        self.model.eval()

    def xǁAttentionScorerǁ__init____mutmut_7(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1e-10
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
            self.device = None
        else:
            self.device = torch.device(device)
        self.model.to(self.device)
        self.model.eval()

    def xǁAttentionScorerǁ__init____mutmut_8(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1e-10
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
            self.device = torch.device(None)
        else:
            self.device = torch.device(device)
        self.model.to(self.device)
        self.model.eval()

    def xǁAttentionScorerǁ__init____mutmut_9(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1e-10
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
            self.device = torch.device("XXcudaXX" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        self.model.to(self.device)
        self.model.eval()

    def xǁAttentionScorerǁ__init____mutmut_10(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1e-10
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
            self.device = torch.device("CUDA" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        self.model.to(self.device)
        self.model.eval()

    def xǁAttentionScorerǁ__init____mutmut_11(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1e-10
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
            self.device = torch.device("cuda" if torch.cuda.is_available() else "XXcpuXX")
        else:
            self.device = torch.device(device)
        self.model.to(self.device)
        self.model.eval()

    def xǁAttentionScorerǁ__init____mutmut_12(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1e-10
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
            self.device = torch.device("cuda" if torch.cuda.is_available() else "CPU")
        else:
            self.device = torch.device(device)
        self.model.to(self.device)
        self.model.eval()

    def xǁAttentionScorerǁ__init____mutmut_13(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1e-10
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
            self.device = None
        self.model.to(self.device)
        self.model.eval()

    def xǁAttentionScorerǁ__init____mutmut_14(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1e-10
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
            self.device = torch.device(None)
        self.model.to(self.device)
        self.model.eval()

    def xǁAttentionScorerǁ__init____mutmut_15(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1e-10
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
        self.model.to(None)
        self.model.eval()
    
    xǁAttentionScorerǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAttentionScorerǁ__init____mutmut_1': xǁAttentionScorerǁ__init____mutmut_1, 
        'xǁAttentionScorerǁ__init____mutmut_2': xǁAttentionScorerǁ__init____mutmut_2, 
        'xǁAttentionScorerǁ__init____mutmut_3': xǁAttentionScorerǁ__init____mutmut_3, 
        'xǁAttentionScorerǁ__init____mutmut_4': xǁAttentionScorerǁ__init____mutmut_4, 
        'xǁAttentionScorerǁ__init____mutmut_5': xǁAttentionScorerǁ__init____mutmut_5, 
        'xǁAttentionScorerǁ__init____mutmut_6': xǁAttentionScorerǁ__init____mutmut_6, 
        'xǁAttentionScorerǁ__init____mutmut_7': xǁAttentionScorerǁ__init____mutmut_7, 
        'xǁAttentionScorerǁ__init____mutmut_8': xǁAttentionScorerǁ__init____mutmut_8, 
        'xǁAttentionScorerǁ__init____mutmut_9': xǁAttentionScorerǁ__init____mutmut_9, 
        'xǁAttentionScorerǁ__init____mutmut_10': xǁAttentionScorerǁ__init____mutmut_10, 
        'xǁAttentionScorerǁ__init____mutmut_11': xǁAttentionScorerǁ__init____mutmut_11, 
        'xǁAttentionScorerǁ__init____mutmut_12': xǁAttentionScorerǁ__init____mutmut_12, 
        'xǁAttentionScorerǁ__init____mutmut_13': xǁAttentionScorerǁ__init____mutmut_13, 
        'xǁAttentionScorerǁ__init____mutmut_14': xǁAttentionScorerǁ__init____mutmut_14, 
        'xǁAttentionScorerǁ__init____mutmut_15': xǁAttentionScorerǁ__init____mutmut_15
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAttentionScorerǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁAttentionScorerǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁAttentionScorerǁ__init____mutmut_orig)
    xǁAttentionScorerǁ__init____mutmut_orig.__name__ = 'xǁAttentionScorerǁ__init__'

    def xǁAttentionScorerǁextract_attention_weights__mutmut_orig(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_1(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        input_ids = None
        if attention_mask is not None:
            attention_mask = attention_mask.to(self.device)

        attention_weights = []
        layer_names = []

        # Hook to capture attention weights
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_2(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        input_ids = input_ids.to(None)
        if attention_mask is not None:
            attention_mask = attention_mask.to(self.device)

        attention_weights = []
        layer_names = []

        # Hook to capture attention weights
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_3(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        if attention_mask is None:
            attention_mask = attention_mask.to(self.device)

        attention_weights = []
        layer_names = []

        # Hook to capture attention weights
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_4(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
            attention_mask = None

        attention_weights = []
        layer_names = []

        # Hook to capture attention weights
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_5(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
            attention_mask = attention_mask.to(None)

        attention_weights = []
        layer_names = []

        # Hook to capture attention weights
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_6(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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

        attention_weights = None
        layer_names = []

        # Hook to capture attention weights
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_7(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        layer_names = None

        # Hook to capture attention weights
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_8(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) or len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_9(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) >= 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_10(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 2:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_11(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = None
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_12(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[2]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_13(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_14(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(None)

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_15(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = None
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_16(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(None):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_17(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key not in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_18(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.upper() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_19(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['XXattentionXX', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_20(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['ATTENTION', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_21(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'XXattnXX']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_22(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'ATTN']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_23(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(None, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_24(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, None):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_25(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr('forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_26(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, ):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_27(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'XXforwardXX'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_28(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'FORWARD'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_29(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
                    hook = None
                    hooks.append(hook)
                    layer_names.append(name)

        # Forward pass
        with torch.no_grad():
            try:
                # Try standard Hugging Face interface
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_30(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
                    hook = module.register_forward_hook(None)
                    hooks.append(hook)
                    layer_names.append(name)

        # Forward pass
        with torch.no_grad():
            try:
                # Try standard Hugging Face interface
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_31(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
                    hook = module.register_forward_hook(attention_hook)
                    hooks.append(None)
                    layer_names.append(name)

        # Forward pass
        with torch.no_grad():
            try:
                # Try standard Hugging Face interface
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_32(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
                    hook = module.register_forward_hook(attention_hook)
                    hooks.append(hook)
                    layer_names.append(None)

        # Forward pass
        with torch.no_grad():
            try:
                # Try standard Hugging Face interface
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_33(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
                    hook = module.register_forward_hook(attention_hook)
                    hooks.append(hook)
                    layer_names.append(name)

        # Forward pass
        with torch.no_grad():
            try:
                # Try standard Hugging Face interface
                outputs = None

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_34(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
                    hook = module.register_forward_hook(attention_hook)
                    hooks.append(hook)
                    layer_names.append(name)

        # Forward pass
        with torch.no_grad():
            try:
                # Try standard Hugging Face interface
                outputs = self.model(
                    input_ids=None,
                    attention_mask=attention_mask,
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_35(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
                    hook = module.register_forward_hook(attention_hook)
                    hooks.append(hook)
                    layer_names.append(name)

        # Forward pass
        with torch.no_grad():
            try:
                # Try standard Hugging Face interface
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=None,
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_36(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=None
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_37(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
                    hook = module.register_forward_hook(attention_hook)
                    hooks.append(hook)
                    layer_names.append(name)

        # Forward pass
        with torch.no_grad():
            try:
                # Try standard Hugging Face interface
                outputs = self.model(
                    attention_mask=attention_mask,
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_38(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
                    hook = module.register_forward_hook(attention_hook)
                    hooks.append(hook)
                    layer_names.append(name)

        # Forward pass
        with torch.no_grad():
            try:
                # Try standard Hugging Face interface
                outputs = self.model(
                    input_ids=input_ids,
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_39(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_40(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=False
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_41(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') or outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_42(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(None, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_43(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, None) and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_44(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr('attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_45(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, ) and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_46(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'XXattentionsXX') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_47(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'ATTENTIONS') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_48(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = None
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_49(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = None
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_50(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(None)]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_51(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(None)
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_52(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=None, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_53(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, attention_mask=None)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_54(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names

    def xǁAttentionScorerǁextract_attention_weights__mutmut_55(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def attention_hook(module, input, output):
            # output is typically (hidden_states, attention_probs)
            if isinstance(output, tuple) and len(output) > 1:
                attn = output[1]
                if attn is not None:
                    attention_weights.append(attn.detach().cpu())

        # Register hooks on attention modules
        hooks = []
        for name, module in self.model.named_modules():
            # Common attention module names in transformers
            if any(key in name.lower() for key in ['attention', 'attn']):
                if hasattr(module, 'forward'):
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
                    output_attentions=True
                )

                # Extract attention from outputs if available
                if hasattr(outputs, 'attentions') and outputs.attentions:
                    attention_weights = [attn.detach().cpu() for attn in outputs.attentions]
                    layer_names = [f"layer_{i}" for i in range(len(attention_weights))]
            except Exception as e:
                logger.warning(f"Could not extract attention using standard interface: {e}")
                # Try forward pass with hooks
                self.model(input_ids=input_ids, )

        # Remove hooks
        for hook in hooks:
            hook.remove()

        return attention_weights, layer_names
    
    xǁAttentionScorerǁextract_attention_weights__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAttentionScorerǁextract_attention_weights__mutmut_1': xǁAttentionScorerǁextract_attention_weights__mutmut_1, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_2': xǁAttentionScorerǁextract_attention_weights__mutmut_2, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_3': xǁAttentionScorerǁextract_attention_weights__mutmut_3, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_4': xǁAttentionScorerǁextract_attention_weights__mutmut_4, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_5': xǁAttentionScorerǁextract_attention_weights__mutmut_5, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_6': xǁAttentionScorerǁextract_attention_weights__mutmut_6, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_7': xǁAttentionScorerǁextract_attention_weights__mutmut_7, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_8': xǁAttentionScorerǁextract_attention_weights__mutmut_8, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_9': xǁAttentionScorerǁextract_attention_weights__mutmut_9, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_10': xǁAttentionScorerǁextract_attention_weights__mutmut_10, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_11': xǁAttentionScorerǁextract_attention_weights__mutmut_11, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_12': xǁAttentionScorerǁextract_attention_weights__mutmut_12, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_13': xǁAttentionScorerǁextract_attention_weights__mutmut_13, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_14': xǁAttentionScorerǁextract_attention_weights__mutmut_14, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_15': xǁAttentionScorerǁextract_attention_weights__mutmut_15, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_16': xǁAttentionScorerǁextract_attention_weights__mutmut_16, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_17': xǁAttentionScorerǁextract_attention_weights__mutmut_17, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_18': xǁAttentionScorerǁextract_attention_weights__mutmut_18, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_19': xǁAttentionScorerǁextract_attention_weights__mutmut_19, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_20': xǁAttentionScorerǁextract_attention_weights__mutmut_20, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_21': xǁAttentionScorerǁextract_attention_weights__mutmut_21, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_22': xǁAttentionScorerǁextract_attention_weights__mutmut_22, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_23': xǁAttentionScorerǁextract_attention_weights__mutmut_23, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_24': xǁAttentionScorerǁextract_attention_weights__mutmut_24, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_25': xǁAttentionScorerǁextract_attention_weights__mutmut_25, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_26': xǁAttentionScorerǁextract_attention_weights__mutmut_26, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_27': xǁAttentionScorerǁextract_attention_weights__mutmut_27, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_28': xǁAttentionScorerǁextract_attention_weights__mutmut_28, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_29': xǁAttentionScorerǁextract_attention_weights__mutmut_29, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_30': xǁAttentionScorerǁextract_attention_weights__mutmut_30, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_31': xǁAttentionScorerǁextract_attention_weights__mutmut_31, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_32': xǁAttentionScorerǁextract_attention_weights__mutmut_32, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_33': xǁAttentionScorerǁextract_attention_weights__mutmut_33, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_34': xǁAttentionScorerǁextract_attention_weights__mutmut_34, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_35': xǁAttentionScorerǁextract_attention_weights__mutmut_35, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_36': xǁAttentionScorerǁextract_attention_weights__mutmut_36, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_37': xǁAttentionScorerǁextract_attention_weights__mutmut_37, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_38': xǁAttentionScorerǁextract_attention_weights__mutmut_38, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_39': xǁAttentionScorerǁextract_attention_weights__mutmut_39, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_40': xǁAttentionScorerǁextract_attention_weights__mutmut_40, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_41': xǁAttentionScorerǁextract_attention_weights__mutmut_41, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_42': xǁAttentionScorerǁextract_attention_weights__mutmut_42, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_43': xǁAttentionScorerǁextract_attention_weights__mutmut_43, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_44': xǁAttentionScorerǁextract_attention_weights__mutmut_44, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_45': xǁAttentionScorerǁextract_attention_weights__mutmut_45, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_46': xǁAttentionScorerǁextract_attention_weights__mutmut_46, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_47': xǁAttentionScorerǁextract_attention_weights__mutmut_47, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_48': xǁAttentionScorerǁextract_attention_weights__mutmut_48, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_49': xǁAttentionScorerǁextract_attention_weights__mutmut_49, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_50': xǁAttentionScorerǁextract_attention_weights__mutmut_50, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_51': xǁAttentionScorerǁextract_attention_weights__mutmut_51, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_52': xǁAttentionScorerǁextract_attention_weights__mutmut_52, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_53': xǁAttentionScorerǁextract_attention_weights__mutmut_53, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_54': xǁAttentionScorerǁextract_attention_weights__mutmut_54, 
        'xǁAttentionScorerǁextract_attention_weights__mutmut_55': xǁAttentionScorerǁextract_attention_weights__mutmut_55
    }
    
    def extract_attention_weights(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAttentionScorerǁextract_attention_weights__mutmut_orig"), object.__getattribute__(self, "xǁAttentionScorerǁextract_attention_weights__mutmut_mutants"), args, kwargs, self)
        return result 
    
    extract_attention_weights.__signature__ = _mutmut_signature(xǁAttentionScorerǁextract_attention_weights__mutmut_orig)
    xǁAttentionScorerǁextract_attention_weights__mutmut_orig.__name__ = 'xǁAttentionScorerǁextract_attention_weights'

    def xǁAttentionScorerǁcompute_token_importance__mutmut_orig(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_1(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "XXmeanXX"
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
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_2(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "MEAN"
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
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_3(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
    ) -> np.ndarray:
        """
        Compute importance score for each token based on attention patterns.

        Args:
            attention_weights: List of attention tensors from each layer
            method: Method to compute importance ('mean', 'max', 'norm')

        Returns:
            Token importance scores (seq_len,)
        """
        if attention_weights:
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
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_4(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
            raise ValueError(None)

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
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_5(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
            raise ValueError("XXNo attention weights providedXX")

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
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_6(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
            raise ValueError("no attention weights provided")

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
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_7(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
            raise ValueError("NO ATTENTION WEIGHTS PROVIDED")

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
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_8(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
        stacked = None

        if method == "mean":
            # Average attention received by each token
            importance = stacked.mean(dim=(0, 1, 2)).numpy()
        elif method == "max":
            # Max attention received by each token
            importance = stacked.max(dim=2)[0].mean(dim=(0, 1)).numpy()
        elif method == "norm":
            # L2 norm of attention received by each token across layers and heads
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_9(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
        stacked = torch.stack(None)

        if method == "mean":
            # Average attention received by each token
            importance = stacked.mean(dim=(0, 1, 2)).numpy()
        elif method == "max":
            # Max attention received by each token
            importance = stacked.max(dim=2)[0].mean(dim=(0, 1)).numpy()
        elif method == "norm":
            # L2 norm of attention received by each token across layers and heads
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_10(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
        stacked = torch.stack([attn[1] for attn in attention_weights])

        if method == "mean":
            # Average attention received by each token
            importance = stacked.mean(dim=(0, 1, 2)).numpy()
        elif method == "max":
            # Max attention received by each token
            importance = stacked.max(dim=2)[0].mean(dim=(0, 1)).numpy()
        elif method == "norm":
            # L2 norm of attention received by each token across layers and heads
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_11(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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

        if method != "mean":
            # Average attention received by each token
            importance = stacked.mean(dim=(0, 1, 2)).numpy()
        elif method == "max":
            # Max attention received by each token
            importance = stacked.max(dim=2)[0].mean(dim=(0, 1)).numpy()
        elif method == "norm":
            # L2 norm of attention received by each token across layers and heads
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_12(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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

        if method == "XXmeanXX":
            # Average attention received by each token
            importance = stacked.mean(dim=(0, 1, 2)).numpy()
        elif method == "max":
            # Max attention received by each token
            importance = stacked.max(dim=2)[0].mean(dim=(0, 1)).numpy()
        elif method == "norm":
            # L2 norm of attention received by each token across layers and heads
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_13(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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

        if method == "MEAN":
            # Average attention received by each token
            importance = stacked.mean(dim=(0, 1, 2)).numpy()
        elif method == "max":
            # Max attention received by each token
            importance = stacked.max(dim=2)[0].mean(dim=(0, 1)).numpy()
        elif method == "norm":
            # L2 norm of attention received by each token across layers and heads
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_14(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
            importance = None
        elif method == "max":
            # Max attention received by each token
            importance = stacked.max(dim=2)[0].mean(dim=(0, 1)).numpy()
        elif method == "norm":
            # L2 norm of attention received by each token across layers and heads
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_15(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
            importance = stacked.mean(dim=None).numpy()
        elif method == "max":
            # Max attention received by each token
            importance = stacked.max(dim=2)[0].mean(dim=(0, 1)).numpy()
        elif method == "norm":
            # L2 norm of attention received by each token across layers and heads
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_16(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
            importance = stacked.mean(dim=(1, 1, 2)).numpy()
        elif method == "max":
            # Max attention received by each token
            importance = stacked.max(dim=2)[0].mean(dim=(0, 1)).numpy()
        elif method == "norm":
            # L2 norm of attention received by each token across layers and heads
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_17(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
            importance = stacked.mean(dim=(0, 2, 2)).numpy()
        elif method == "max":
            # Max attention received by each token
            importance = stacked.max(dim=2)[0].mean(dim=(0, 1)).numpy()
        elif method == "norm":
            # L2 norm of attention received by each token across layers and heads
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_18(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
            importance = stacked.mean(dim=(0, 1, 3)).numpy()
        elif method == "max":
            # Max attention received by each token
            importance = stacked.max(dim=2)[0].mean(dim=(0, 1)).numpy()
        elif method == "norm":
            # L2 norm of attention received by each token across layers and heads
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_19(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
        elif method != "max":
            # Max attention received by each token
            importance = stacked.max(dim=2)[0].mean(dim=(0, 1)).numpy()
        elif method == "norm":
            # L2 norm of attention received by each token across layers and heads
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_20(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
        elif method == "XXmaxXX":
            # Max attention received by each token
            importance = stacked.max(dim=2)[0].mean(dim=(0, 1)).numpy()
        elif method == "norm":
            # L2 norm of attention received by each token across layers and heads
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_21(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
        elif method == "MAX":
            # Max attention received by each token
            importance = stacked.max(dim=2)[0].mean(dim=(0, 1)).numpy()
        elif method == "norm":
            # L2 norm of attention received by each token across layers and heads
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_22(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
            importance = None
        elif method == "norm":
            # L2 norm of attention received by each token across layers and heads
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_23(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
            importance = stacked.max(dim=2)[0].mean(dim=None).numpy()
        elif method == "norm":
            # L2 norm of attention received by each token across layers and heads
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_24(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
            importance = stacked.max(dim=None)[0].mean(dim=(0, 1)).numpy()
        elif method == "norm":
            # L2 norm of attention received by each token across layers and heads
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_25(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
            importance = stacked.max(dim=3)[0].mean(dim=(0, 1)).numpy()
        elif method == "norm":
            # L2 norm of attention received by each token across layers and heads
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_26(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
            importance = stacked.max(dim=2)[1].mean(dim=(0, 1)).numpy()
        elif method == "norm":
            # L2 norm of attention received by each token across layers and heads
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_27(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
            importance = stacked.max(dim=2)[0].mean(dim=(1, 1)).numpy()
        elif method == "norm":
            # L2 norm of attention received by each token across layers and heads
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_28(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
            importance = stacked.max(dim=2)[0].mean(dim=(0, 2)).numpy()
        elif method == "norm":
            # L2 norm of attention received by each token across layers and heads
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_29(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
        elif method != "norm":
            # L2 norm of attention received by each token across layers and heads
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_30(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
        elif method == "XXnormXX":
            # L2 norm of attention received by each token across layers and heads
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_31(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
        elif method == "NORM":
            # L2 norm of attention received by each token across layers and heads
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_32(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = None  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_33(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=None)  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_34(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(1, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_35(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 2))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_36(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = None  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_37(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=None).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_38(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=1).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_39(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(None)

        if self.normalize:
            importance = importance / (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_40(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = None

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_41(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance * (importance.sum() + self.epsilon)

        return importance

    def xǁAttentionScorerǁcompute_token_importance__mutmut_42(
        self,
        attention_weights: List[torch.Tensor],
        method: str = "mean"
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
            # Shape: (num_layers, num_heads, seq_len) -> mean across (layers, heads) -> norm of seq_len
            aggregated = stacked.mean(dim=(0, 1))  # (seq_len, seq_len)
            importance = aggregated.mean(dim=0).numpy()  # Average incoming attention per token
        else:
            raise ValueError(f"Unknown method: {method}")

        if self.normalize:
            importance = importance / (importance.sum() - self.epsilon)

        return importance
    
    xǁAttentionScorerǁcompute_token_importance__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAttentionScorerǁcompute_token_importance__mutmut_1': xǁAttentionScorerǁcompute_token_importance__mutmut_1, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_2': xǁAttentionScorerǁcompute_token_importance__mutmut_2, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_3': xǁAttentionScorerǁcompute_token_importance__mutmut_3, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_4': xǁAttentionScorerǁcompute_token_importance__mutmut_4, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_5': xǁAttentionScorerǁcompute_token_importance__mutmut_5, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_6': xǁAttentionScorerǁcompute_token_importance__mutmut_6, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_7': xǁAttentionScorerǁcompute_token_importance__mutmut_7, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_8': xǁAttentionScorerǁcompute_token_importance__mutmut_8, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_9': xǁAttentionScorerǁcompute_token_importance__mutmut_9, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_10': xǁAttentionScorerǁcompute_token_importance__mutmut_10, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_11': xǁAttentionScorerǁcompute_token_importance__mutmut_11, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_12': xǁAttentionScorerǁcompute_token_importance__mutmut_12, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_13': xǁAttentionScorerǁcompute_token_importance__mutmut_13, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_14': xǁAttentionScorerǁcompute_token_importance__mutmut_14, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_15': xǁAttentionScorerǁcompute_token_importance__mutmut_15, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_16': xǁAttentionScorerǁcompute_token_importance__mutmut_16, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_17': xǁAttentionScorerǁcompute_token_importance__mutmut_17, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_18': xǁAttentionScorerǁcompute_token_importance__mutmut_18, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_19': xǁAttentionScorerǁcompute_token_importance__mutmut_19, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_20': xǁAttentionScorerǁcompute_token_importance__mutmut_20, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_21': xǁAttentionScorerǁcompute_token_importance__mutmut_21, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_22': xǁAttentionScorerǁcompute_token_importance__mutmut_22, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_23': xǁAttentionScorerǁcompute_token_importance__mutmut_23, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_24': xǁAttentionScorerǁcompute_token_importance__mutmut_24, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_25': xǁAttentionScorerǁcompute_token_importance__mutmut_25, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_26': xǁAttentionScorerǁcompute_token_importance__mutmut_26, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_27': xǁAttentionScorerǁcompute_token_importance__mutmut_27, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_28': xǁAttentionScorerǁcompute_token_importance__mutmut_28, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_29': xǁAttentionScorerǁcompute_token_importance__mutmut_29, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_30': xǁAttentionScorerǁcompute_token_importance__mutmut_30, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_31': xǁAttentionScorerǁcompute_token_importance__mutmut_31, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_32': xǁAttentionScorerǁcompute_token_importance__mutmut_32, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_33': xǁAttentionScorerǁcompute_token_importance__mutmut_33, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_34': xǁAttentionScorerǁcompute_token_importance__mutmut_34, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_35': xǁAttentionScorerǁcompute_token_importance__mutmut_35, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_36': xǁAttentionScorerǁcompute_token_importance__mutmut_36, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_37': xǁAttentionScorerǁcompute_token_importance__mutmut_37, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_38': xǁAttentionScorerǁcompute_token_importance__mutmut_38, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_39': xǁAttentionScorerǁcompute_token_importance__mutmut_39, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_40': xǁAttentionScorerǁcompute_token_importance__mutmut_40, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_41': xǁAttentionScorerǁcompute_token_importance__mutmut_41, 
        'xǁAttentionScorerǁcompute_token_importance__mutmut_42': xǁAttentionScorerǁcompute_token_importance__mutmut_42
    }
    
    def compute_token_importance(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAttentionScorerǁcompute_token_importance__mutmut_orig"), object.__getattribute__(self, "xǁAttentionScorerǁcompute_token_importance__mutmut_mutants"), args, kwargs, self)
        return result 
    
    compute_token_importance.__signature__ = _mutmut_signature(xǁAttentionScorerǁcompute_token_importance__mutmut_orig)
    xǁAttentionScorerǁcompute_token_importance__mutmut_orig.__name__ = 'xǁAttentionScorerǁcompute_token_importance'

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_orig(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
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

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_1(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "XXmeanXX"
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

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_2(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "MEAN"
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

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_3(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
    ) -> np.ndarray:
        """
        Compute attention flow matrix between tokens.

        Args:
            attention_weights: List of attention tensors from each layer
            layer_aggregation: How to aggregate across layers ('mean', 'last', 'sum')

        Returns:
            Attention flow matrix (seq_len, seq_len)
        """
        if attention_weights:
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

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_4(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
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
            raise ValueError(None)

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

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_5(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
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
            raise ValueError("XXNo attention weights providedXX")

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

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_6(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
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
            raise ValueError("no attention weights provided")

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

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_7(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
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
            raise ValueError("NO ATTENTION WEIGHTS PROVIDED")

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

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_8(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
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
        stacked = None

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

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_9(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
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
        stacked = torch.stack(None)

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

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_10(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
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
        stacked = torch.stack([attn[1] for attn in attention_weights])

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

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_11(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
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
        stacked = None

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

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_12(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
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
        stacked = stacked.mean(dim=None)

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

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_13(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
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
        stacked = stacked.mean(dim=2)

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

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_14(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
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
        if layer_aggregation != "mean":
            flow = stacked.mean(dim=0).numpy()
        elif layer_aggregation == "last":
            flow = stacked[-1].numpy()
        elif layer_aggregation == "sum":
            flow = stacked.sum(dim=0).numpy()
        else:
            raise ValueError(f"Unknown aggregation: {layer_aggregation}")

        return flow

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_15(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
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
        if layer_aggregation == "XXmeanXX":
            flow = stacked.mean(dim=0).numpy()
        elif layer_aggregation == "last":
            flow = stacked[-1].numpy()
        elif layer_aggregation == "sum":
            flow = stacked.sum(dim=0).numpy()
        else:
            raise ValueError(f"Unknown aggregation: {layer_aggregation}")

        return flow

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_16(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
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
        if layer_aggregation == "MEAN":
            flow = stacked.mean(dim=0).numpy()
        elif layer_aggregation == "last":
            flow = stacked[-1].numpy()
        elif layer_aggregation == "sum":
            flow = stacked.sum(dim=0).numpy()
        else:
            raise ValueError(f"Unknown aggregation: {layer_aggregation}")

        return flow

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_17(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
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
            flow = None
        elif layer_aggregation == "last":
            flow = stacked[-1].numpy()
        elif layer_aggregation == "sum":
            flow = stacked.sum(dim=0).numpy()
        else:
            raise ValueError(f"Unknown aggregation: {layer_aggregation}")

        return flow

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_18(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
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
            flow = stacked.mean(dim=None).numpy()
        elif layer_aggregation == "last":
            flow = stacked[-1].numpy()
        elif layer_aggregation == "sum":
            flow = stacked.sum(dim=0).numpy()
        else:
            raise ValueError(f"Unknown aggregation: {layer_aggregation}")

        return flow

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_19(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
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
            flow = stacked.mean(dim=1).numpy()
        elif layer_aggregation == "last":
            flow = stacked[-1].numpy()
        elif layer_aggregation == "sum":
            flow = stacked.sum(dim=0).numpy()
        else:
            raise ValueError(f"Unknown aggregation: {layer_aggregation}")

        return flow

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_20(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
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
        elif layer_aggregation != "last":
            flow = stacked[-1].numpy()
        elif layer_aggregation == "sum":
            flow = stacked.sum(dim=0).numpy()
        else:
            raise ValueError(f"Unknown aggregation: {layer_aggregation}")

        return flow

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_21(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
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
        elif layer_aggregation == "XXlastXX":
            flow = stacked[-1].numpy()
        elif layer_aggregation == "sum":
            flow = stacked.sum(dim=0).numpy()
        else:
            raise ValueError(f"Unknown aggregation: {layer_aggregation}")

        return flow

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_22(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
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
        elif layer_aggregation == "LAST":
            flow = stacked[-1].numpy()
        elif layer_aggregation == "sum":
            flow = stacked.sum(dim=0).numpy()
        else:
            raise ValueError(f"Unknown aggregation: {layer_aggregation}")

        return flow

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_23(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
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
            flow = None
        elif layer_aggregation == "sum":
            flow = stacked.sum(dim=0).numpy()
        else:
            raise ValueError(f"Unknown aggregation: {layer_aggregation}")

        return flow

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_24(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
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
            flow = stacked[+1].numpy()
        elif layer_aggregation == "sum":
            flow = stacked.sum(dim=0).numpy()
        else:
            raise ValueError(f"Unknown aggregation: {layer_aggregation}")

        return flow

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_25(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
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
            flow = stacked[-2].numpy()
        elif layer_aggregation == "sum":
            flow = stacked.sum(dim=0).numpy()
        else:
            raise ValueError(f"Unknown aggregation: {layer_aggregation}")

        return flow

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_26(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
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
        elif layer_aggregation != "sum":
            flow = stacked.sum(dim=0).numpy()
        else:
            raise ValueError(f"Unknown aggregation: {layer_aggregation}")

        return flow

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_27(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
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
        elif layer_aggregation == "XXsumXX":
            flow = stacked.sum(dim=0).numpy()
        else:
            raise ValueError(f"Unknown aggregation: {layer_aggregation}")

        return flow

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_28(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
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
        elif layer_aggregation == "SUM":
            flow = stacked.sum(dim=0).numpy()
        else:
            raise ValueError(f"Unknown aggregation: {layer_aggregation}")

        return flow

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_29(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
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
            flow = None
        else:
            raise ValueError(f"Unknown aggregation: {layer_aggregation}")

        return flow

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_30(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
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
            flow = stacked.sum(dim=None).numpy()
        else:
            raise ValueError(f"Unknown aggregation: {layer_aggregation}")

        return flow

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_31(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
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
            flow = stacked.sum(dim=1).numpy()
        else:
            raise ValueError(f"Unknown aggregation: {layer_aggregation}")

        return flow

    def xǁAttentionScorerǁcompute_attention_flow__mutmut_32(
        self,
        attention_weights: List[torch.Tensor],
        layer_aggregation: str = "mean"
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
            raise ValueError(None)

        return flow
    
    xǁAttentionScorerǁcompute_attention_flow__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAttentionScorerǁcompute_attention_flow__mutmut_1': xǁAttentionScorerǁcompute_attention_flow__mutmut_1, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_2': xǁAttentionScorerǁcompute_attention_flow__mutmut_2, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_3': xǁAttentionScorerǁcompute_attention_flow__mutmut_3, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_4': xǁAttentionScorerǁcompute_attention_flow__mutmut_4, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_5': xǁAttentionScorerǁcompute_attention_flow__mutmut_5, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_6': xǁAttentionScorerǁcompute_attention_flow__mutmut_6, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_7': xǁAttentionScorerǁcompute_attention_flow__mutmut_7, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_8': xǁAttentionScorerǁcompute_attention_flow__mutmut_8, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_9': xǁAttentionScorerǁcompute_attention_flow__mutmut_9, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_10': xǁAttentionScorerǁcompute_attention_flow__mutmut_10, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_11': xǁAttentionScorerǁcompute_attention_flow__mutmut_11, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_12': xǁAttentionScorerǁcompute_attention_flow__mutmut_12, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_13': xǁAttentionScorerǁcompute_attention_flow__mutmut_13, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_14': xǁAttentionScorerǁcompute_attention_flow__mutmut_14, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_15': xǁAttentionScorerǁcompute_attention_flow__mutmut_15, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_16': xǁAttentionScorerǁcompute_attention_flow__mutmut_16, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_17': xǁAttentionScorerǁcompute_attention_flow__mutmut_17, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_18': xǁAttentionScorerǁcompute_attention_flow__mutmut_18, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_19': xǁAttentionScorerǁcompute_attention_flow__mutmut_19, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_20': xǁAttentionScorerǁcompute_attention_flow__mutmut_20, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_21': xǁAttentionScorerǁcompute_attention_flow__mutmut_21, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_22': xǁAttentionScorerǁcompute_attention_flow__mutmut_22, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_23': xǁAttentionScorerǁcompute_attention_flow__mutmut_23, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_24': xǁAttentionScorerǁcompute_attention_flow__mutmut_24, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_25': xǁAttentionScorerǁcompute_attention_flow__mutmut_25, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_26': xǁAttentionScorerǁcompute_attention_flow__mutmut_26, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_27': xǁAttentionScorerǁcompute_attention_flow__mutmut_27, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_28': xǁAttentionScorerǁcompute_attention_flow__mutmut_28, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_29': xǁAttentionScorerǁcompute_attention_flow__mutmut_29, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_30': xǁAttentionScorerǁcompute_attention_flow__mutmut_30, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_31': xǁAttentionScorerǁcompute_attention_flow__mutmut_31, 
        'xǁAttentionScorerǁcompute_attention_flow__mutmut_32': xǁAttentionScorerǁcompute_attention_flow__mutmut_32
    }
    
    def compute_attention_flow(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAttentionScorerǁcompute_attention_flow__mutmut_orig"), object.__getattribute__(self, "xǁAttentionScorerǁcompute_attention_flow__mutmut_mutants"), args, kwargs, self)
        return result 
    
    compute_attention_flow.__signature__ = _mutmut_signature(xǁAttentionScorerǁcompute_attention_flow__mutmut_orig)
    xǁAttentionScorerǁcompute_attention_flow__mutmut_orig.__name__ = 'xǁAttentionScorerǁcompute_attention_flow'

    def xǁAttentionScorerǁanalyze_attention__mutmut_orig(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_1(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "XXmeanXX",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_2(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "MEAN",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_3(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "XXmeanXX"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_4(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "MEAN"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_5(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = None

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_6(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            None, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_7(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, None
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_8(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_9(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_10(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_11(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError(None)

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_12(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("XXFailed to extract attention weights from modelXX")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_13(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_14(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("FAILED TO EXTRACT ATTENTION WEIGHTS FROM MODEL")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_15(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = None

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_16(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            None, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_17(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=None
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_18(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_19(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_20(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = None

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_21(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            None, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_22(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=None
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_23(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_24(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_25(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = None

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_26(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack(None)

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_27(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[1].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_28(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=None,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_29(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=None,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_30(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=None,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_31(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=None,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_32(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_33(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=None
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_34(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_35(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_36(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_37(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_38(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_39(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is not None else None,
            )

    def xǁAttentionScorerǁanalyze_attention__mutmut_40(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[1].tolist() if input_ids is not None else None,
            tokens=tokens
        )

    def xǁAttentionScorerǁanalyze_attention__mutmut_41(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        tokens: Optional[List[str]] = None,
        importance_method: str = "mean",
        flow_aggregation: str = "mean"
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
        attn_weights, layer_names = self.extract_attention_weights(
            input_ids, attention_mask
        )

        if not attn_weights:
            raise ValueError("Failed to extract attention weights from model")

        # Compute token importance
        importance = self.compute_token_importance(
            attn_weights, method=importance_method
        )

        # Compute attention flow
        flow = self.compute_attention_flow(
            attn_weights, layer_aggregation=flow_aggregation
        )

        # Stack attention weights for output
        # Shape: (num_layers, num_heads, seq_len, seq_len)
        stacked_weights = np.stack([
            attn[0].numpy() for attn in attn_weights
        ])

        return AttentionAnalysis(
            attention_weights=stacked_weights,
            token_importance=importance,
            attention_flow=flow,
            layer_names=layer_names,
            token_ids=input_ids[0].tolist() if input_ids is None else None,
            tokens=tokens
        )
    
    xǁAttentionScorerǁanalyze_attention__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAttentionScorerǁanalyze_attention__mutmut_1': xǁAttentionScorerǁanalyze_attention__mutmut_1, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_2': xǁAttentionScorerǁanalyze_attention__mutmut_2, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_3': xǁAttentionScorerǁanalyze_attention__mutmut_3, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_4': xǁAttentionScorerǁanalyze_attention__mutmut_4, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_5': xǁAttentionScorerǁanalyze_attention__mutmut_5, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_6': xǁAttentionScorerǁanalyze_attention__mutmut_6, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_7': xǁAttentionScorerǁanalyze_attention__mutmut_7, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_8': xǁAttentionScorerǁanalyze_attention__mutmut_8, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_9': xǁAttentionScorerǁanalyze_attention__mutmut_9, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_10': xǁAttentionScorerǁanalyze_attention__mutmut_10, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_11': xǁAttentionScorerǁanalyze_attention__mutmut_11, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_12': xǁAttentionScorerǁanalyze_attention__mutmut_12, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_13': xǁAttentionScorerǁanalyze_attention__mutmut_13, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_14': xǁAttentionScorerǁanalyze_attention__mutmut_14, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_15': xǁAttentionScorerǁanalyze_attention__mutmut_15, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_16': xǁAttentionScorerǁanalyze_attention__mutmut_16, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_17': xǁAttentionScorerǁanalyze_attention__mutmut_17, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_18': xǁAttentionScorerǁanalyze_attention__mutmut_18, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_19': xǁAttentionScorerǁanalyze_attention__mutmut_19, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_20': xǁAttentionScorerǁanalyze_attention__mutmut_20, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_21': xǁAttentionScorerǁanalyze_attention__mutmut_21, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_22': xǁAttentionScorerǁanalyze_attention__mutmut_22, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_23': xǁAttentionScorerǁanalyze_attention__mutmut_23, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_24': xǁAttentionScorerǁanalyze_attention__mutmut_24, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_25': xǁAttentionScorerǁanalyze_attention__mutmut_25, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_26': xǁAttentionScorerǁanalyze_attention__mutmut_26, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_27': xǁAttentionScorerǁanalyze_attention__mutmut_27, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_28': xǁAttentionScorerǁanalyze_attention__mutmut_28, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_29': xǁAttentionScorerǁanalyze_attention__mutmut_29, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_30': xǁAttentionScorerǁanalyze_attention__mutmut_30, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_31': xǁAttentionScorerǁanalyze_attention__mutmut_31, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_32': xǁAttentionScorerǁanalyze_attention__mutmut_32, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_33': xǁAttentionScorerǁanalyze_attention__mutmut_33, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_34': xǁAttentionScorerǁanalyze_attention__mutmut_34, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_35': xǁAttentionScorerǁanalyze_attention__mutmut_35, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_36': xǁAttentionScorerǁanalyze_attention__mutmut_36, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_37': xǁAttentionScorerǁanalyze_attention__mutmut_37, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_38': xǁAttentionScorerǁanalyze_attention__mutmut_38, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_39': xǁAttentionScorerǁanalyze_attention__mutmut_39, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_40': xǁAttentionScorerǁanalyze_attention__mutmut_40, 
        'xǁAttentionScorerǁanalyze_attention__mutmut_41': xǁAttentionScorerǁanalyze_attention__mutmut_41
    }
    
    def analyze_attention(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAttentionScorerǁanalyze_attention__mutmut_orig"), object.__getattribute__(self, "xǁAttentionScorerǁanalyze_attention__mutmut_mutants"), args, kwargs, self)
        return result 
    
    analyze_attention.__signature__ = _mutmut_signature(xǁAttentionScorerǁanalyze_attention__mutmut_orig)
    xǁAttentionScorerǁanalyze_attention__mutmut_orig.__name__ = 'xǁAttentionScorerǁanalyze_attention'

    def xǁAttentionScorerǁget_top_attended_tokens__mutmut_orig(
        self,
        analysis: AttentionAnalysis,
        top_k: int = 5
    ) -> List[Tuple[int, float, Optional[str]]]:
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
            results.append((
                int(idx),
                float(analysis.token_importance[idx]),
                token_str
            ))

        return results

    def xǁAttentionScorerǁget_top_attended_tokens__mutmut_1(
        self,
        analysis: AttentionAnalysis,
        top_k: int = 6
    ) -> List[Tuple[int, float, Optional[str]]]:
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
            results.append((
                int(idx),
                float(analysis.token_importance[idx]),
                token_str
            ))

        return results

    def xǁAttentionScorerǁget_top_attended_tokens__mutmut_2(
        self,
        analysis: AttentionAnalysis,
        top_k: int = 5
    ) -> List[Tuple[int, float, Optional[str]]]:
        """
        Get the top-k most attended tokens.

        Args:
            analysis: AttentionAnalysis result
            top_k: Number of top tokens to return

        Returns:
            List of (token_index, importance_score, token_string) tuples
        """
        top_indices = None

        results = []
        for idx in top_indices:
            token_str = analysis.tokens[idx] if analysis.tokens else None
            results.append((
                int(idx),
                float(analysis.token_importance[idx]),
                token_str
            ))

        return results

    def xǁAttentionScorerǁget_top_attended_tokens__mutmut_3(
        self,
        analysis: AttentionAnalysis,
        top_k: int = 5
    ) -> List[Tuple[int, float, Optional[str]]]:
        """
        Get the top-k most attended tokens.

        Args:
            analysis: AttentionAnalysis result
            top_k: Number of top tokens to return

        Returns:
            List of (token_index, importance_score, token_string) tuples
        """
        top_indices = np.argsort(None)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            token_str = analysis.tokens[idx] if analysis.tokens else None
            results.append((
                int(idx),
                float(analysis.token_importance[idx]),
                token_str
            ))

        return results

    def xǁAttentionScorerǁget_top_attended_tokens__mutmut_4(
        self,
        analysis: AttentionAnalysis,
        top_k: int = 5
    ) -> List[Tuple[int, float, Optional[str]]]:
        """
        Get the top-k most attended tokens.

        Args:
            analysis: AttentionAnalysis result
            top_k: Number of top tokens to return

        Returns:
            List of (token_index, importance_score, token_string) tuples
        """
        top_indices = np.argsort(analysis.token_importance)[+top_k:][::-1]

        results = []
        for idx in top_indices:
            token_str = analysis.tokens[idx] if analysis.tokens else None
            results.append((
                int(idx),
                float(analysis.token_importance[idx]),
                token_str
            ))

        return results

    def xǁAttentionScorerǁget_top_attended_tokens__mutmut_5(
        self,
        analysis: AttentionAnalysis,
        top_k: int = 5
    ) -> List[Tuple[int, float, Optional[str]]]:
        """
        Get the top-k most attended tokens.

        Args:
            analysis: AttentionAnalysis result
            top_k: Number of top tokens to return

        Returns:
            List of (token_index, importance_score, token_string) tuples
        """
        top_indices = np.argsort(analysis.token_importance)[-top_k:][::+1]

        results = []
        for idx in top_indices:
            token_str = analysis.tokens[idx] if analysis.tokens else None
            results.append((
                int(idx),
                float(analysis.token_importance[idx]),
                token_str
            ))

        return results

    def xǁAttentionScorerǁget_top_attended_tokens__mutmut_6(
        self,
        analysis: AttentionAnalysis,
        top_k: int = 5
    ) -> List[Tuple[int, float, Optional[str]]]:
        """
        Get the top-k most attended tokens.

        Args:
            analysis: AttentionAnalysis result
            top_k: Number of top tokens to return

        Returns:
            List of (token_index, importance_score, token_string) tuples
        """
        top_indices = np.argsort(analysis.token_importance)[-top_k:][::-2]

        results = []
        for idx in top_indices:
            token_str = analysis.tokens[idx] if analysis.tokens else None
            results.append((
                int(idx),
                float(analysis.token_importance[idx]),
                token_str
            ))

        return results

    def xǁAttentionScorerǁget_top_attended_tokens__mutmut_7(
        self,
        analysis: AttentionAnalysis,
        top_k: int = 5
    ) -> List[Tuple[int, float, Optional[str]]]:
        """
        Get the top-k most attended tokens.

        Args:
            analysis: AttentionAnalysis result
            top_k: Number of top tokens to return

        Returns:
            List of (token_index, importance_score, token_string) tuples
        """
        top_indices = np.argsort(analysis.token_importance)[-top_k:][::-1]

        results = None
        for idx in top_indices:
            token_str = analysis.tokens[idx] if analysis.tokens else None
            results.append((
                int(idx),
                float(analysis.token_importance[idx]),
                token_str
            ))

        return results

    def xǁAttentionScorerǁget_top_attended_tokens__mutmut_8(
        self,
        analysis: AttentionAnalysis,
        top_k: int = 5
    ) -> List[Tuple[int, float, Optional[str]]]:
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
            token_str = None
            results.append((
                int(idx),
                float(analysis.token_importance[idx]),
                token_str
            ))

        return results

    def xǁAttentionScorerǁget_top_attended_tokens__mutmut_9(
        self,
        analysis: AttentionAnalysis,
        top_k: int = 5
    ) -> List[Tuple[int, float, Optional[str]]]:
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
            results.append(None)

        return results

    def xǁAttentionScorerǁget_top_attended_tokens__mutmut_10(
        self,
        analysis: AttentionAnalysis,
        top_k: int = 5
    ) -> List[Tuple[int, float, Optional[str]]]:
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
            results.append((
                int(None),
                float(analysis.token_importance[idx]),
                token_str
            ))

        return results

    def xǁAttentionScorerǁget_top_attended_tokens__mutmut_11(
        self,
        analysis: AttentionAnalysis,
        top_k: int = 5
    ) -> List[Tuple[int, float, Optional[str]]]:
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
            results.append((
                int(idx),
                float(None),
                token_str
            ))

        return results
    
    xǁAttentionScorerǁget_top_attended_tokens__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAttentionScorerǁget_top_attended_tokens__mutmut_1': xǁAttentionScorerǁget_top_attended_tokens__mutmut_1, 
        'xǁAttentionScorerǁget_top_attended_tokens__mutmut_2': xǁAttentionScorerǁget_top_attended_tokens__mutmut_2, 
        'xǁAttentionScorerǁget_top_attended_tokens__mutmut_3': xǁAttentionScorerǁget_top_attended_tokens__mutmut_3, 
        'xǁAttentionScorerǁget_top_attended_tokens__mutmut_4': xǁAttentionScorerǁget_top_attended_tokens__mutmut_4, 
        'xǁAttentionScorerǁget_top_attended_tokens__mutmut_5': xǁAttentionScorerǁget_top_attended_tokens__mutmut_5, 
        'xǁAttentionScorerǁget_top_attended_tokens__mutmut_6': xǁAttentionScorerǁget_top_attended_tokens__mutmut_6, 
        'xǁAttentionScorerǁget_top_attended_tokens__mutmut_7': xǁAttentionScorerǁget_top_attended_tokens__mutmut_7, 
        'xǁAttentionScorerǁget_top_attended_tokens__mutmut_8': xǁAttentionScorerǁget_top_attended_tokens__mutmut_8, 
        'xǁAttentionScorerǁget_top_attended_tokens__mutmut_9': xǁAttentionScorerǁget_top_attended_tokens__mutmut_9, 
        'xǁAttentionScorerǁget_top_attended_tokens__mutmut_10': xǁAttentionScorerǁget_top_attended_tokens__mutmut_10, 
        'xǁAttentionScorerǁget_top_attended_tokens__mutmut_11': xǁAttentionScorerǁget_top_attended_tokens__mutmut_11
    }
    
    def get_top_attended_tokens(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAttentionScorerǁget_top_attended_tokens__mutmut_orig"), object.__getattribute__(self, "xǁAttentionScorerǁget_top_attended_tokens__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_top_attended_tokens.__signature__ = _mutmut_signature(xǁAttentionScorerǁget_top_attended_tokens__mutmut_orig)
    xǁAttentionScorerǁget_top_attended_tokens__mutmut_orig.__name__ = 'xǁAttentionScorerǁget_top_attended_tokens'
