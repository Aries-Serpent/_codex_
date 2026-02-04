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
from typing import Optional, Union, Dict, List, Tuple
import torch
import numpy as np
from dataclasses import dataclass

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
class MLPAnalysis:
    """Results from MLP analysis."""
    
    # MLP activations shape: (num_layers, hidden_dim)
    activations: np.ndarray
    
    # Neuron importance scores shape: (num_layers, hidden_dim)
    neuron_importance: np.ndarray
    
    # Layer-wise activation statistics
    layer_stats: Dict[str, np.ndarray]
    
    # Layer names
    layer_names: List[str]
    
    # Input shape
    input_shape: Tuple[int, ...]


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
        ...     print(f"Layer {layer_idx}: {neurons}")
    """
    
    def xǁMLPScorerǁ__init____mutmut_orig(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1e-10
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
    
    def xǁMLPScorerǁ__init____mutmut_1(
        self,
        model: torch.nn.Module,
        normalize: bool = False,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1e-10
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
    
    def xǁMLPScorerǁ__init____mutmut_2(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1.0000000001
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
    
    def xǁMLPScorerǁ__init____mutmut_3(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1e-10
    ):
        """
        Initialize the MLP scorer.
        
        Args:
            model: Transformer model with MLP layers
            normalize: Whether to normalize activation scores
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
    
    def xǁMLPScorerǁ__init____mutmut_4(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1e-10
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
        self.normalize = None
        self.epsilon = epsilon
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        self.model.to(self.device)
        self.model.eval()
    
    def xǁMLPScorerǁ__init____mutmut_5(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1e-10
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
        self.epsilon = None
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        self.model.to(self.device)
        self.model.eval()
    
    def xǁMLPScorerǁ__init____mutmut_6(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1e-10
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
        if device is not None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        self.model.to(self.device)
        self.model.eval()
    
    def xǁMLPScorerǁ__init____mutmut_7(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1e-10
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
            self.device = None
        else:
            self.device = torch.device(device)
        self.model.to(self.device)
        self.model.eval()
    
    def xǁMLPScorerǁ__init____mutmut_8(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1e-10
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
            self.device = torch.device(None)
        else:
            self.device = torch.device(device)
        self.model.to(self.device)
        self.model.eval()
    
    def xǁMLPScorerǁ__init____mutmut_9(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1e-10
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
            self.device = torch.device("XXcudaXX" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        self.model.to(self.device)
        self.model.eval()
    
    def xǁMLPScorerǁ__init____mutmut_10(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1e-10
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
            self.device = torch.device("CUDA" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        self.model.to(self.device)
        self.model.eval()
    
    def xǁMLPScorerǁ__init____mutmut_11(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1e-10
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
            self.device = torch.device("cuda" if torch.cuda.is_available() else "XXcpuXX")
        else:
            self.device = torch.device(device)
        self.model.to(self.device)
        self.model.eval()
    
    def xǁMLPScorerǁ__init____mutmut_12(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1e-10
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
            self.device = torch.device("cuda" if torch.cuda.is_available() else "CPU")
        else:
            self.device = torch.device(device)
        self.model.to(self.device)
        self.model.eval()
    
    def xǁMLPScorerǁ__init____mutmut_13(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1e-10
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
            self.device = None
        self.model.to(self.device)
        self.model.eval()
    
    def xǁMLPScorerǁ__init____mutmut_14(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1e-10
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
            self.device = torch.device(None)
        self.model.to(self.device)
        self.model.eval()
    
    def xǁMLPScorerǁ__init____mutmut_15(
        self,
        model: torch.nn.Module,
        normalize: bool = True,
        device: Optional[Union[str, torch.device]] = None,
        epsilon: float = 1e-10
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
        self.model.to(None)
        self.model.eval()
    
    xǁMLPScorerǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMLPScorerǁ__init____mutmut_1': xǁMLPScorerǁ__init____mutmut_1, 
        'xǁMLPScorerǁ__init____mutmut_2': xǁMLPScorerǁ__init____mutmut_2, 
        'xǁMLPScorerǁ__init____mutmut_3': xǁMLPScorerǁ__init____mutmut_3, 
        'xǁMLPScorerǁ__init____mutmut_4': xǁMLPScorerǁ__init____mutmut_4, 
        'xǁMLPScorerǁ__init____mutmut_5': xǁMLPScorerǁ__init____mutmut_5, 
        'xǁMLPScorerǁ__init____mutmut_6': xǁMLPScorerǁ__init____mutmut_6, 
        'xǁMLPScorerǁ__init____mutmut_7': xǁMLPScorerǁ__init____mutmut_7, 
        'xǁMLPScorerǁ__init____mutmut_8': xǁMLPScorerǁ__init____mutmut_8, 
        'xǁMLPScorerǁ__init____mutmut_9': xǁMLPScorerǁ__init____mutmut_9, 
        'xǁMLPScorerǁ__init____mutmut_10': xǁMLPScorerǁ__init____mutmut_10, 
        'xǁMLPScorerǁ__init____mutmut_11': xǁMLPScorerǁ__init____mutmut_11, 
        'xǁMLPScorerǁ__init____mutmut_12': xǁMLPScorerǁ__init____mutmut_12, 
        'xǁMLPScorerǁ__init____mutmut_13': xǁMLPScorerǁ__init____mutmut_13, 
        'xǁMLPScorerǁ__init____mutmut_14': xǁMLPScorerǁ__init____mutmut_14, 
        'xǁMLPScorerǁ__init____mutmut_15': xǁMLPScorerǁ__init____mutmut_15
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMLPScorerǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁMLPScorerǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁMLPScorerǁ__init____mutmut_orig)
    xǁMLPScorerǁ__init____mutmut_orig.__name__ = 'xǁMLPScorerǁ__init__'
    
    def xǁMLPScorerǁ_is_mlp_layer__mutmut_orig(self, layer_name: str) -> bool:
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
        if leaf_name in {"dense", "feedforward"}:
            return True
        return False
        
    
    def xǁMLPScorerǁ_is_mlp_layer__mutmut_1(self, layer_name: str) -> bool:
        """
        Determine if a layer is an MLP/FFN layer based on its name.
        
        Args:
            layer_name: Name of the layer
            
        Returns:
            True if the layer is an MLP layer to analyze
        """
        name_lower = None
        leaf_name = name_lower.split(".")[-1]

        # Only hook the top-level MLP/FFN modules, not their internal linear layers.
        if leaf_name in {"mlp", "ffn", "intermediate"}:
            if leaf_name == "intermediate":
                return True
            return True
        # Fallback to common naming for standalone blocks.
        if leaf_name in {"dense", "feedforward"}:
            return True
        return False
        
    
    def xǁMLPScorerǁ_is_mlp_layer__mutmut_2(self, layer_name: str) -> bool:
        """
        Determine if a layer is an MLP/FFN layer based on its name.
        
        Args:
            layer_name: Name of the layer
            
        Returns:
            True if the layer is an MLP layer to analyze
        """
        name_lower = layer_name.upper()
        leaf_name = name_lower.split(".")[-1]

        # Only hook the top-level MLP/FFN modules, not their internal linear layers.
        if leaf_name in {"mlp", "ffn", "intermediate"}:
            if leaf_name == "intermediate":
                return True
            return True
        # Fallback to common naming for standalone blocks.
        if leaf_name in {"dense", "feedforward"}:
            return True
        return False
        
    
    def xǁMLPScorerǁ_is_mlp_layer__mutmut_3(self, layer_name: str) -> bool:
        """
        Determine if a layer is an MLP/FFN layer based on its name.
        
        Args:
            layer_name: Name of the layer
            
        Returns:
            True if the layer is an MLP layer to analyze
        """
        name_lower = layer_name.lower()
        leaf_name = None

        # Only hook the top-level MLP/FFN modules, not their internal linear layers.
        if leaf_name in {"mlp", "ffn", "intermediate"}:
            if leaf_name == "intermediate":
                return True
            return True
        # Fallback to common naming for standalone blocks.
        if leaf_name in {"dense", "feedforward"}:
            return True
        return False
        
    
    def xǁMLPScorerǁ_is_mlp_layer__mutmut_4(self, layer_name: str) -> bool:
        """
        Determine if a layer is an MLP/FFN layer based on its name.
        
        Args:
            layer_name: Name of the layer
            
        Returns:
            True if the layer is an MLP layer to analyze
        """
        name_lower = layer_name.lower()
        leaf_name = name_lower.split(None)[-1]

        # Only hook the top-level MLP/FFN modules, not their internal linear layers.
        if leaf_name in {"mlp", "ffn", "intermediate"}:
            if leaf_name == "intermediate":
                return True
            return True
        # Fallback to common naming for standalone blocks.
        if leaf_name in {"dense", "feedforward"}:
            return True
        return False
        
    
    def xǁMLPScorerǁ_is_mlp_layer__mutmut_5(self, layer_name: str) -> bool:
        """
        Determine if a layer is an MLP/FFN layer based on its name.
        
        Args:
            layer_name: Name of the layer
            
        Returns:
            True if the layer is an MLP layer to analyze
        """
        name_lower = layer_name.lower()
        leaf_name = name_lower.split("XX.XX")[-1]

        # Only hook the top-level MLP/FFN modules, not their internal linear layers.
        if leaf_name in {"mlp", "ffn", "intermediate"}:
            if leaf_name == "intermediate":
                return True
            return True
        # Fallback to common naming for standalone blocks.
        if leaf_name in {"dense", "feedforward"}:
            return True
        return False
        
    
    def xǁMLPScorerǁ_is_mlp_layer__mutmut_6(self, layer_name: str) -> bool:
        """
        Determine if a layer is an MLP/FFN layer based on its name.
        
        Args:
            layer_name: Name of the layer
            
        Returns:
            True if the layer is an MLP layer to analyze
        """
        name_lower = layer_name.lower()
        leaf_name = name_lower.split(".")[+1]

        # Only hook the top-level MLP/FFN modules, not their internal linear layers.
        if leaf_name in {"mlp", "ffn", "intermediate"}:
            if leaf_name == "intermediate":
                return True
            return True
        # Fallback to common naming for standalone blocks.
        if leaf_name in {"dense", "feedforward"}:
            return True
        return False
        
    
    def xǁMLPScorerǁ_is_mlp_layer__mutmut_7(self, layer_name: str) -> bool:
        """
        Determine if a layer is an MLP/FFN layer based on its name.
        
        Args:
            layer_name: Name of the layer
            
        Returns:
            True if the layer is an MLP layer to analyze
        """
        name_lower = layer_name.lower()
        leaf_name = name_lower.split(".")[-2]

        # Only hook the top-level MLP/FFN modules, not their internal linear layers.
        if leaf_name in {"mlp", "ffn", "intermediate"}:
            if leaf_name == "intermediate":
                return True
            return True
        # Fallback to common naming for standalone blocks.
        if leaf_name in {"dense", "feedforward"}:
            return True
        return False
        
    
    def xǁMLPScorerǁ_is_mlp_layer__mutmut_8(self, layer_name: str) -> bool:
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
        if leaf_name not in {"mlp", "ffn", "intermediate"}:
            if leaf_name == "intermediate":
                return True
            return True
        # Fallback to common naming for standalone blocks.
        if leaf_name in {"dense", "feedforward"}:
            return True
        return False
        
    
    def xǁMLPScorerǁ_is_mlp_layer__mutmut_9(self, layer_name: str) -> bool:
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
        if leaf_name in {"XXmlpXX", "ffn", "intermediate"}:
            if leaf_name == "intermediate":
                return True
            return True
        # Fallback to common naming for standalone blocks.
        if leaf_name in {"dense", "feedforward"}:
            return True
        return False
        
    
    def xǁMLPScorerǁ_is_mlp_layer__mutmut_10(self, layer_name: str) -> bool:
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
        if leaf_name in {"MLP", "ffn", "intermediate"}:
            if leaf_name == "intermediate":
                return True
            return True
        # Fallback to common naming for standalone blocks.
        if leaf_name in {"dense", "feedforward"}:
            return True
        return False
        
    
    def xǁMLPScorerǁ_is_mlp_layer__mutmut_11(self, layer_name: str) -> bool:
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
        if leaf_name in {"mlp", "XXffnXX", "intermediate"}:
            if leaf_name == "intermediate":
                return True
            return True
        # Fallback to common naming for standalone blocks.
        if leaf_name in {"dense", "feedforward"}:
            return True
        return False
        
    
    def xǁMLPScorerǁ_is_mlp_layer__mutmut_12(self, layer_name: str) -> bool:
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
        if leaf_name in {"mlp", "FFN", "intermediate"}:
            if leaf_name == "intermediate":
                return True
            return True
        # Fallback to common naming for standalone blocks.
        if leaf_name in {"dense", "feedforward"}:
            return True
        return False
        
    
    def xǁMLPScorerǁ_is_mlp_layer__mutmut_13(self, layer_name: str) -> bool:
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
        if leaf_name in {"mlp", "ffn", "XXintermediateXX"}:
            if leaf_name == "intermediate":
                return True
            return True
        # Fallback to common naming for standalone blocks.
        if leaf_name in {"dense", "feedforward"}:
            return True
        return False
        
    
    def xǁMLPScorerǁ_is_mlp_layer__mutmut_14(self, layer_name: str) -> bool:
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
        if leaf_name in {"mlp", "ffn", "INTERMEDIATE"}:
            if leaf_name == "intermediate":
                return True
            return True
        # Fallback to common naming for standalone blocks.
        if leaf_name in {"dense", "feedforward"}:
            return True
        return False
        
    
    def xǁMLPScorerǁ_is_mlp_layer__mutmut_15(self, layer_name: str) -> bool:
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
            if leaf_name != "intermediate":
                return True
            return True
        # Fallback to common naming for standalone blocks.
        if leaf_name in {"dense", "feedforward"}:
            return True
        return False
        
    
    def xǁMLPScorerǁ_is_mlp_layer__mutmut_16(self, layer_name: str) -> bool:
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
            if leaf_name == "XXintermediateXX":
                return True
            return True
        # Fallback to common naming for standalone blocks.
        if leaf_name in {"dense", "feedforward"}:
            return True
        return False
        
    
    def xǁMLPScorerǁ_is_mlp_layer__mutmut_17(self, layer_name: str) -> bool:
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
            if leaf_name == "INTERMEDIATE":
                return True
            return True
        # Fallback to common naming for standalone blocks.
        if leaf_name in {"dense", "feedforward"}:
            return True
        return False
        
    
    def xǁMLPScorerǁ_is_mlp_layer__mutmut_18(self, layer_name: str) -> bool:
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
                return False
            return True
        # Fallback to common naming for standalone blocks.
        if leaf_name in {"dense", "feedforward"}:
            return True
        return False
        
    
    def xǁMLPScorerǁ_is_mlp_layer__mutmut_19(self, layer_name: str) -> bool:
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
            return False
        # Fallback to common naming for standalone blocks.
        if leaf_name in {"dense", "feedforward"}:
            return True
        return False
        
    
    def xǁMLPScorerǁ_is_mlp_layer__mutmut_20(self, layer_name: str) -> bool:
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
        if leaf_name not in {"dense", "feedforward"}:
            return True
        return False
        
    
    def xǁMLPScorerǁ_is_mlp_layer__mutmut_21(self, layer_name: str) -> bool:
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
        if leaf_name in {"XXdenseXX", "feedforward"}:
            return True
        return False
        
    
    def xǁMLPScorerǁ_is_mlp_layer__mutmut_22(self, layer_name: str) -> bool:
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
        if leaf_name in {"DENSE", "feedforward"}:
            return True
        return False
        
    
    def xǁMLPScorerǁ_is_mlp_layer__mutmut_23(self, layer_name: str) -> bool:
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
        if leaf_name in {"dense", "XXfeedforwardXX"}:
            return True
        return False
        
    
    def xǁMLPScorerǁ_is_mlp_layer__mutmut_24(self, layer_name: str) -> bool:
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
        if leaf_name in {"dense", "FEEDFORWARD"}:
            return True
        return False
        
    
    def xǁMLPScorerǁ_is_mlp_layer__mutmut_25(self, layer_name: str) -> bool:
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
        if leaf_name in {"dense", "feedforward"}:
            return False
        return False
        
    
    def xǁMLPScorerǁ_is_mlp_layer__mutmut_26(self, layer_name: str) -> bool:
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
        if leaf_name in {"dense", "feedforward"}:
            return True
        return True
        
    
    xǁMLPScorerǁ_is_mlp_layer__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMLPScorerǁ_is_mlp_layer__mutmut_1': xǁMLPScorerǁ_is_mlp_layer__mutmut_1, 
        'xǁMLPScorerǁ_is_mlp_layer__mutmut_2': xǁMLPScorerǁ_is_mlp_layer__mutmut_2, 
        'xǁMLPScorerǁ_is_mlp_layer__mutmut_3': xǁMLPScorerǁ_is_mlp_layer__mutmut_3, 
        'xǁMLPScorerǁ_is_mlp_layer__mutmut_4': xǁMLPScorerǁ_is_mlp_layer__mutmut_4, 
        'xǁMLPScorerǁ_is_mlp_layer__mutmut_5': xǁMLPScorerǁ_is_mlp_layer__mutmut_5, 
        'xǁMLPScorerǁ_is_mlp_layer__mutmut_6': xǁMLPScorerǁ_is_mlp_layer__mutmut_6, 
        'xǁMLPScorerǁ_is_mlp_layer__mutmut_7': xǁMLPScorerǁ_is_mlp_layer__mutmut_7, 
        'xǁMLPScorerǁ_is_mlp_layer__mutmut_8': xǁMLPScorerǁ_is_mlp_layer__mutmut_8, 
        'xǁMLPScorerǁ_is_mlp_layer__mutmut_9': xǁMLPScorerǁ_is_mlp_layer__mutmut_9, 
        'xǁMLPScorerǁ_is_mlp_layer__mutmut_10': xǁMLPScorerǁ_is_mlp_layer__mutmut_10, 
        'xǁMLPScorerǁ_is_mlp_layer__mutmut_11': xǁMLPScorerǁ_is_mlp_layer__mutmut_11, 
        'xǁMLPScorerǁ_is_mlp_layer__mutmut_12': xǁMLPScorerǁ_is_mlp_layer__mutmut_12, 
        'xǁMLPScorerǁ_is_mlp_layer__mutmut_13': xǁMLPScorerǁ_is_mlp_layer__mutmut_13, 
        'xǁMLPScorerǁ_is_mlp_layer__mutmut_14': xǁMLPScorerǁ_is_mlp_layer__mutmut_14, 
        'xǁMLPScorerǁ_is_mlp_layer__mutmut_15': xǁMLPScorerǁ_is_mlp_layer__mutmut_15, 
        'xǁMLPScorerǁ_is_mlp_layer__mutmut_16': xǁMLPScorerǁ_is_mlp_layer__mutmut_16, 
        'xǁMLPScorerǁ_is_mlp_layer__mutmut_17': xǁMLPScorerǁ_is_mlp_layer__mutmut_17, 
        'xǁMLPScorerǁ_is_mlp_layer__mutmut_18': xǁMLPScorerǁ_is_mlp_layer__mutmut_18, 
        'xǁMLPScorerǁ_is_mlp_layer__mutmut_19': xǁMLPScorerǁ_is_mlp_layer__mutmut_19, 
        'xǁMLPScorerǁ_is_mlp_layer__mutmut_20': xǁMLPScorerǁ_is_mlp_layer__mutmut_20, 
        'xǁMLPScorerǁ_is_mlp_layer__mutmut_21': xǁMLPScorerǁ_is_mlp_layer__mutmut_21, 
        'xǁMLPScorerǁ_is_mlp_layer__mutmut_22': xǁMLPScorerǁ_is_mlp_layer__mutmut_22, 
        'xǁMLPScorerǁ_is_mlp_layer__mutmut_23': xǁMLPScorerǁ_is_mlp_layer__mutmut_23, 
        'xǁMLPScorerǁ_is_mlp_layer__mutmut_24': xǁMLPScorerǁ_is_mlp_layer__mutmut_24, 
        'xǁMLPScorerǁ_is_mlp_layer__mutmut_25': xǁMLPScorerǁ_is_mlp_layer__mutmut_25, 
        'xǁMLPScorerǁ_is_mlp_layer__mutmut_26': xǁMLPScorerǁ_is_mlp_layer__mutmut_26
    }
    
    def _is_mlp_layer(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMLPScorerǁ_is_mlp_layer__mutmut_orig"), object.__getattribute__(self, "xǁMLPScorerǁ_is_mlp_layer__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _is_mlp_layer.__signature__ = _mutmut_signature(xǁMLPScorerǁ_is_mlp_layer__mutmut_orig)
    xǁMLPScorerǁ_is_mlp_layer__mutmut_orig.__name__ = 'xǁMLPScorerǁ_is_mlp_layer'
    def xǁMLPScorerǁextract_mlp_activations__mutmut_orig(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def mlp_hook(module, input, output):
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
            except Exception as e:
                logger.error(f"Error during forward pass: {e}")
                raise
        
        # Remove hooks
        for hook in hooks:
            hook.remove()
        
        return mlp_activations, layer_names
    def xǁMLPScorerǁextract_mlp_activations__mutmut_1(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        input_ids = None
        if attention_mask is not None:
            attention_mask = attention_mask.to(self.device)
        
        mlp_activations = []
        layer_names = []
        
        # Hook to capture MLP activations
        def mlp_hook(module, input, output):
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
            except Exception as e:
                logger.error(f"Error during forward pass: {e}")
                raise
        
        # Remove hooks
        for hook in hooks:
            hook.remove()
        
        return mlp_activations, layer_names
    def xǁMLPScorerǁextract_mlp_activations__mutmut_2(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        input_ids = input_ids.to(None)
        if attention_mask is not None:
            attention_mask = attention_mask.to(self.device)
        
        mlp_activations = []
        layer_names = []
        
        # Hook to capture MLP activations
        def mlp_hook(module, input, output):
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
            except Exception as e:
                logger.error(f"Error during forward pass: {e}")
                raise
        
        # Remove hooks
        for hook in hooks:
            hook.remove()
        
        return mlp_activations, layer_names
    def xǁMLPScorerǁextract_mlp_activations__mutmut_3(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        if attention_mask is None:
            attention_mask = attention_mask.to(self.device)
        
        mlp_activations = []
        layer_names = []
        
        # Hook to capture MLP activations
        def mlp_hook(module, input, output):
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
            except Exception as e:
                logger.error(f"Error during forward pass: {e}")
                raise
        
        # Remove hooks
        for hook in hooks:
            hook.remove()
        
        return mlp_activations, layer_names
    def xǁMLPScorerǁextract_mlp_activations__mutmut_4(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
            attention_mask = None
        
        mlp_activations = []
        layer_names = []
        
        # Hook to capture MLP activations
        def mlp_hook(module, input, output):
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
            except Exception as e:
                logger.error(f"Error during forward pass: {e}")
                raise
        
        # Remove hooks
        for hook in hooks:
            hook.remove()
        
        return mlp_activations, layer_names
    def xǁMLPScorerǁextract_mlp_activations__mutmut_5(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
            attention_mask = attention_mask.to(None)
        
        mlp_activations = []
        layer_names = []
        
        # Hook to capture MLP activations
        def mlp_hook(module, input, output):
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
            except Exception as e:
                logger.error(f"Error during forward pass: {e}")
                raise
        
        # Remove hooks
        for hook in hooks:
            hook.remove()
        
        return mlp_activations, layer_names
    def xǁMLPScorerǁextract_mlp_activations__mutmut_6(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        
        mlp_activations = None
        layer_names = []
        
        # Hook to capture MLP activations
        def mlp_hook(module, input, output):
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
            except Exception as e:
                logger.error(f"Error during forward pass: {e}")
                raise
        
        # Remove hooks
        for hook in hooks:
            hook.remove()
        
        return mlp_activations, layer_names
    def xǁMLPScorerǁextract_mlp_activations__mutmut_7(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        layer_names = None
        
        # Hook to capture MLP activations
        def mlp_hook(module, input, output):
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
            except Exception as e:
                logger.error(f"Error during forward pass: {e}")
                raise
        
        # Remove hooks
        for hook in hooks:
            hook.remove()
        
        return mlp_activations, layer_names
    def xǁMLPScorerǁextract_mlp_activations__mutmut_8(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def mlp_hook(module, input, output):
            # Capture the output of MLP layers
            if isinstance(output, torch.Tensor):
                mlp_activations.append(None)
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
            except Exception as e:
                logger.error(f"Error during forward pass: {e}")
                raise
        
        # Remove hooks
        for hook in hooks:
            hook.remove()
        
        return mlp_activations, layer_names
    def xǁMLPScorerǁextract_mlp_activations__mutmut_9(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def mlp_hook(module, input, output):
            # Capture the output of MLP layers
            if isinstance(output, torch.Tensor):
                mlp_activations.append(output.detach().cpu())
            elif isinstance(output, tuple):
                mlp_activations.append(None)
        
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
            except Exception as e:
                logger.error(f"Error during forward pass: {e}")
                raise
        
        # Remove hooks
        for hook in hooks:
            hook.remove()
        
        return mlp_activations, layer_names
    def xǁMLPScorerǁextract_mlp_activations__mutmut_10(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def mlp_hook(module, input, output):
            # Capture the output of MLP layers
            if isinstance(output, torch.Tensor):
                mlp_activations.append(output.detach().cpu())
            elif isinstance(output, tuple):
                mlp_activations.append(output[1].detach().cpu())
        
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
            except Exception as e:
                logger.error(f"Error during forward pass: {e}")
                raise
        
        # Remove hooks
        for hook in hooks:
            hook.remove()
        
        return mlp_activations, layer_names
    def xǁMLPScorerǁextract_mlp_activations__mutmut_11(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def mlp_hook(module, input, output):
            # Capture the output of MLP layers
            if isinstance(output, torch.Tensor):
                mlp_activations.append(output.detach().cpu())
            elif isinstance(output, tuple):
                mlp_activations.append(output[0].detach().cpu())
        
        # Register hooks on MLP/FFN modules
        hooks = None
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
            except Exception as e:
                logger.error(f"Error during forward pass: {e}")
                raise
        
        # Remove hooks
        for hook in hooks:
            hook.remove()
        
        return mlp_activations, layer_names
    def xǁMLPScorerǁextract_mlp_activations__mutmut_12(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def mlp_hook(module, input, output):
            # Capture the output of MLP layers
            if isinstance(output, torch.Tensor):
                mlp_activations.append(output.detach().cpu())
            elif isinstance(output, tuple):
                mlp_activations.append(output[0].detach().cpu())
        
        # Register hooks on MLP/FFN modules
        hooks = []
        for name, module in self.model.named_modules():
            if self._is_mlp_layer(None):
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
            except Exception as e:
                logger.error(f"Error during forward pass: {e}")
                raise
        
        # Remove hooks
        for hook in hooks:
            hook.remove()
        
        return mlp_activations, layer_names
    def xǁMLPScorerǁextract_mlp_activations__mutmut_13(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def mlp_hook(module, input, output):
            # Capture the output of MLP layers
            if isinstance(output, torch.Tensor):
                mlp_activations.append(output.detach().cpu())
            elif isinstance(output, tuple):
                mlp_activations.append(output[0].detach().cpu())
        
        # Register hooks on MLP/FFN modules
        hooks = []
        for name, module in self.model.named_modules():
            if self._is_mlp_layer(name):
                hook = None
                hooks.append(hook)
                layer_names.append(name)
        
        # Forward pass
        with torch.no_grad():
            try:
                self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                )
            except Exception as e:
                logger.error(f"Error during forward pass: {e}")
                raise
        
        # Remove hooks
        for hook in hooks:
            hook.remove()
        
        return mlp_activations, layer_names
    def xǁMLPScorerǁextract_mlp_activations__mutmut_14(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def mlp_hook(module, input, output):
            # Capture the output of MLP layers
            if isinstance(output, torch.Tensor):
                mlp_activations.append(output.detach().cpu())
            elif isinstance(output, tuple):
                mlp_activations.append(output[0].detach().cpu())
        
        # Register hooks on MLP/FFN modules
        hooks = []
        for name, module in self.model.named_modules():
            if self._is_mlp_layer(name):
                hook = module.register_forward_hook(None)
                hooks.append(hook)
                layer_names.append(name)
        
        # Forward pass
        with torch.no_grad():
            try:
                self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                )
            except Exception as e:
                logger.error(f"Error during forward pass: {e}")
                raise
        
        # Remove hooks
        for hook in hooks:
            hook.remove()
        
        return mlp_activations, layer_names
    def xǁMLPScorerǁextract_mlp_activations__mutmut_15(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def mlp_hook(module, input, output):
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
                hooks.append(None)
                layer_names.append(name)
        
        # Forward pass
        with torch.no_grad():
            try:
                self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                )
            except Exception as e:
                logger.error(f"Error during forward pass: {e}")
                raise
        
        # Remove hooks
        for hook in hooks:
            hook.remove()
        
        return mlp_activations, layer_names
    def xǁMLPScorerǁextract_mlp_activations__mutmut_16(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def mlp_hook(module, input, output):
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
                layer_names.append(None)
        
        # Forward pass
        with torch.no_grad():
            try:
                self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                )
            except Exception as e:
                logger.error(f"Error during forward pass: {e}")
                raise
        
        # Remove hooks
        for hook in hooks:
            hook.remove()
        
        return mlp_activations, layer_names
    def xǁMLPScorerǁextract_mlp_activations__mutmut_17(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def mlp_hook(module, input, output):
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
                    input_ids=None,
                    attention_mask=attention_mask,
                )
            except Exception as e:
                logger.error(f"Error during forward pass: {e}")
                raise
        
        # Remove hooks
        for hook in hooks:
            hook.remove()
        
        return mlp_activations, layer_names
    def xǁMLPScorerǁextract_mlp_activations__mutmut_18(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def mlp_hook(module, input, output):
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
                    attention_mask=None,
                )
            except Exception as e:
                logger.error(f"Error during forward pass: {e}")
                raise
        
        # Remove hooks
        for hook in hooks:
            hook.remove()
        
        return mlp_activations, layer_names
    def xǁMLPScorerǁextract_mlp_activations__mutmut_19(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def mlp_hook(module, input, output):
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
                    attention_mask=attention_mask,
                )
            except Exception as e:
                logger.error(f"Error during forward pass: {e}")
                raise
        
        # Remove hooks
        for hook in hooks:
            hook.remove()
        
        return mlp_activations, layer_names
    def xǁMLPScorerǁextract_mlp_activations__mutmut_20(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def mlp_hook(module, input, output):
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
                    )
            except Exception as e:
                logger.error(f"Error during forward pass: {e}")
                raise
        
        # Remove hooks
        for hook in hooks:
            hook.remove()
        
        return mlp_activations, layer_names
    def xǁMLPScorerǁextract_mlp_activations__mutmut_21(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[torch.Tensor], List[str]]:
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
        def mlp_hook(module, input, output):
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
            except Exception as e:
                logger.error(None)
                raise
        
        # Remove hooks
        for hook in hooks:
            hook.remove()
        
        return mlp_activations, layer_names
    
    xǁMLPScorerǁextract_mlp_activations__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMLPScorerǁextract_mlp_activations__mutmut_1': xǁMLPScorerǁextract_mlp_activations__mutmut_1, 
        'xǁMLPScorerǁextract_mlp_activations__mutmut_2': xǁMLPScorerǁextract_mlp_activations__mutmut_2, 
        'xǁMLPScorerǁextract_mlp_activations__mutmut_3': xǁMLPScorerǁextract_mlp_activations__mutmut_3, 
        'xǁMLPScorerǁextract_mlp_activations__mutmut_4': xǁMLPScorerǁextract_mlp_activations__mutmut_4, 
        'xǁMLPScorerǁextract_mlp_activations__mutmut_5': xǁMLPScorerǁextract_mlp_activations__mutmut_5, 
        'xǁMLPScorerǁextract_mlp_activations__mutmut_6': xǁMLPScorerǁextract_mlp_activations__mutmut_6, 
        'xǁMLPScorerǁextract_mlp_activations__mutmut_7': xǁMLPScorerǁextract_mlp_activations__mutmut_7, 
        'xǁMLPScorerǁextract_mlp_activations__mutmut_8': xǁMLPScorerǁextract_mlp_activations__mutmut_8, 
        'xǁMLPScorerǁextract_mlp_activations__mutmut_9': xǁMLPScorerǁextract_mlp_activations__mutmut_9, 
        'xǁMLPScorerǁextract_mlp_activations__mutmut_10': xǁMLPScorerǁextract_mlp_activations__mutmut_10, 
        'xǁMLPScorerǁextract_mlp_activations__mutmut_11': xǁMLPScorerǁextract_mlp_activations__mutmut_11, 
        'xǁMLPScorerǁextract_mlp_activations__mutmut_12': xǁMLPScorerǁextract_mlp_activations__mutmut_12, 
        'xǁMLPScorerǁextract_mlp_activations__mutmut_13': xǁMLPScorerǁextract_mlp_activations__mutmut_13, 
        'xǁMLPScorerǁextract_mlp_activations__mutmut_14': xǁMLPScorerǁextract_mlp_activations__mutmut_14, 
        'xǁMLPScorerǁextract_mlp_activations__mutmut_15': xǁMLPScorerǁextract_mlp_activations__mutmut_15, 
        'xǁMLPScorerǁextract_mlp_activations__mutmut_16': xǁMLPScorerǁextract_mlp_activations__mutmut_16, 
        'xǁMLPScorerǁextract_mlp_activations__mutmut_17': xǁMLPScorerǁextract_mlp_activations__mutmut_17, 
        'xǁMLPScorerǁextract_mlp_activations__mutmut_18': xǁMLPScorerǁextract_mlp_activations__mutmut_18, 
        'xǁMLPScorerǁextract_mlp_activations__mutmut_19': xǁMLPScorerǁextract_mlp_activations__mutmut_19, 
        'xǁMLPScorerǁextract_mlp_activations__mutmut_20': xǁMLPScorerǁextract_mlp_activations__mutmut_20, 
        'xǁMLPScorerǁextract_mlp_activations__mutmut_21': xǁMLPScorerǁextract_mlp_activations__mutmut_21
    }
    
    def extract_mlp_activations(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMLPScorerǁextract_mlp_activations__mutmut_orig"), object.__getattribute__(self, "xǁMLPScorerǁextract_mlp_activations__mutmut_mutants"), args, kwargs, self)
        return result 
    
    extract_mlp_activations.__signature__ = _mutmut_signature(xǁMLPScorerǁextract_mlp_activations__mutmut_orig)
    xǁMLPScorerǁextract_mlp_activations__mutmut_orig.__name__ = 'xǁMLPScorerǁextract_mlp_activations'
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_orig(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_1(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "XXmean_absXX"
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_2(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "MEAN_ABS"
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_3(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
    ) -> np.ndarray:
        """
        Compute importance score for each neuron based on activation patterns.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            method: Method to compute importance ('mean_abs', 'max', 'variance')
            
        Returns:
            Neuron importance scores (num_layers, hidden_dim)
        """
        if mlp_activations:
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_4(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
            raise ValueError(None)
        
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_5(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
            raise ValueError("XXNo MLP activations providedXX")
        
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_6(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
            raise ValueError("no mlp activations provided")
        
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_7(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
            raise ValueError("NO MLP ACTIVATIONS PROVIDED")
        
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_8(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
        
        importance_per_layer = None
        
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_9(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
            
            if method != "mean_abs":
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_10(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
            
            if method == "XXmean_absXX":
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_11(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
            
            if method == "MEAN_ABS":
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_12(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                if activation.dim() != 3:
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_13(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                if activation.dim() == 4:
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_14(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                    importance = None
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_15(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                    importance = activation.abs().mean(dim=None).numpy()
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_16(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                    importance = activation.abs().mean(dim=(1, 1)).numpy()
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_17(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                    importance = activation.abs().mean(dim=(0, 2)).numpy()
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_18(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                    importance = None
                    
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_19(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                    importance = activation.abs().mean(dim=None).numpy()
                    
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_20(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                    importance = activation.abs().mean(dim=1).numpy()
                    
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_21(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                    
            elif method != "max":
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_22(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                    
            elif method == "XXmaxXX":
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_23(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                    
            elif method == "MAX":
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_24(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                if activation.dim() != 3:
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_25(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                if activation.dim() == 4:
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_26(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                    importance = None
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_27(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                    importance = activation.abs().amax(dim=None).numpy()
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_28(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                    importance = activation.abs().amax(dim=(1, 1)).numpy()
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_29(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                    importance = activation.abs().amax(dim=(0, 2)).numpy()
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_30(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                    importance = None
                    
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_31(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                    importance = activation.abs().amax(dim=None).numpy()
                    
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_32(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                    importance = activation.abs().amax(dim=1).numpy()
                    
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_33(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                    
            elif method != "variance":
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_34(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                    
            elif method == "XXvarianceXX":
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_35(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                    
            elif method == "VARIANCE":
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_36(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                if activation.dim() != 3:
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_37(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                if activation.dim() == 4:
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
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_38(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                    importance = None
                else:
                    importance = activation.var(dim=0).numpy()
            else:
                raise ValueError(f"Unknown method: {method}")
            
            if self.normalize and importance.sum() > self.epsilon:
                importance = importance / importance.sum()
            
            importance_per_layer.append(importance)
        
        # Stack all layers
        return np.stack(importance_per_layer)
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_39(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                    importance = activation.var(dim=None).numpy()
                else:
                    importance = activation.var(dim=0).numpy()
            else:
                raise ValueError(f"Unknown method: {method}")
            
            if self.normalize and importance.sum() > self.epsilon:
                importance = importance / importance.sum()
            
            importance_per_layer.append(importance)
        
        # Stack all layers
        return np.stack(importance_per_layer)
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_40(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                    importance = activation.var(dim=(1, 1)).numpy()
                else:
                    importance = activation.var(dim=0).numpy()
            else:
                raise ValueError(f"Unknown method: {method}")
            
            if self.normalize and importance.sum() > self.epsilon:
                importance = importance / importance.sum()
            
            importance_per_layer.append(importance)
        
        # Stack all layers
        return np.stack(importance_per_layer)
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_41(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                    importance = activation.var(dim=(0, 2)).numpy()
                else:
                    importance = activation.var(dim=0).numpy()
            else:
                raise ValueError(f"Unknown method: {method}")
            
            if self.normalize and importance.sum() > self.epsilon:
                importance = importance / importance.sum()
            
            importance_per_layer.append(importance)
        
        # Stack all layers
        return np.stack(importance_per_layer)
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_42(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                    importance = None
            else:
                raise ValueError(f"Unknown method: {method}")
            
            if self.normalize and importance.sum() > self.epsilon:
                importance = importance / importance.sum()
            
            importance_per_layer.append(importance)
        
        # Stack all layers
        return np.stack(importance_per_layer)
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_43(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                    importance = activation.var(dim=None).numpy()
            else:
                raise ValueError(f"Unknown method: {method}")
            
            if self.normalize and importance.sum() > self.epsilon:
                importance = importance / importance.sum()
            
            importance_per_layer.append(importance)
        
        # Stack all layers
        return np.stack(importance_per_layer)
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_44(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                    importance = activation.var(dim=1).numpy()
            else:
                raise ValueError(f"Unknown method: {method}")
            
            if self.normalize and importance.sum() > self.epsilon:
                importance = importance / importance.sum()
            
            importance_per_layer.append(importance)
        
        # Stack all layers
        return np.stack(importance_per_layer)
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_45(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                raise ValueError(None)
            
            if self.normalize and importance.sum() > self.epsilon:
                importance = importance / importance.sum()
            
            importance_per_layer.append(importance)
        
        # Stack all layers
        return np.stack(importance_per_layer)
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_46(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
            
            if self.normalize or importance.sum() > self.epsilon:
                importance = importance / importance.sum()
            
            importance_per_layer.append(importance)
        
        # Stack all layers
        return np.stack(importance_per_layer)
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_47(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
            
            if self.normalize and importance.sum() >= self.epsilon:
                importance = importance / importance.sum()
            
            importance_per_layer.append(importance)
        
        # Stack all layers
        return np.stack(importance_per_layer)
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_48(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                importance = None
            
            importance_per_layer.append(importance)
        
        # Stack all layers
        return np.stack(importance_per_layer)
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_49(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
                importance = importance * importance.sum()
            
            importance_per_layer.append(importance)
        
        # Stack all layers
        return np.stack(importance_per_layer)
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_50(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
            
            importance_per_layer.append(None)
        
        # Stack all layers
        return np.stack(importance_per_layer)
    
    def xǁMLPScorerǁcompute_neuron_importance__mutmut_51(
        self,
        mlp_activations: List[torch.Tensor],
        method: str = "mean_abs"
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
        return np.stack(None)
    
    xǁMLPScorerǁcompute_neuron_importance__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMLPScorerǁcompute_neuron_importance__mutmut_1': xǁMLPScorerǁcompute_neuron_importance__mutmut_1, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_2': xǁMLPScorerǁcompute_neuron_importance__mutmut_2, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_3': xǁMLPScorerǁcompute_neuron_importance__mutmut_3, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_4': xǁMLPScorerǁcompute_neuron_importance__mutmut_4, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_5': xǁMLPScorerǁcompute_neuron_importance__mutmut_5, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_6': xǁMLPScorerǁcompute_neuron_importance__mutmut_6, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_7': xǁMLPScorerǁcompute_neuron_importance__mutmut_7, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_8': xǁMLPScorerǁcompute_neuron_importance__mutmut_8, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_9': xǁMLPScorerǁcompute_neuron_importance__mutmut_9, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_10': xǁMLPScorerǁcompute_neuron_importance__mutmut_10, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_11': xǁMLPScorerǁcompute_neuron_importance__mutmut_11, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_12': xǁMLPScorerǁcompute_neuron_importance__mutmut_12, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_13': xǁMLPScorerǁcompute_neuron_importance__mutmut_13, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_14': xǁMLPScorerǁcompute_neuron_importance__mutmut_14, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_15': xǁMLPScorerǁcompute_neuron_importance__mutmut_15, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_16': xǁMLPScorerǁcompute_neuron_importance__mutmut_16, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_17': xǁMLPScorerǁcompute_neuron_importance__mutmut_17, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_18': xǁMLPScorerǁcompute_neuron_importance__mutmut_18, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_19': xǁMLPScorerǁcompute_neuron_importance__mutmut_19, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_20': xǁMLPScorerǁcompute_neuron_importance__mutmut_20, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_21': xǁMLPScorerǁcompute_neuron_importance__mutmut_21, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_22': xǁMLPScorerǁcompute_neuron_importance__mutmut_22, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_23': xǁMLPScorerǁcompute_neuron_importance__mutmut_23, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_24': xǁMLPScorerǁcompute_neuron_importance__mutmut_24, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_25': xǁMLPScorerǁcompute_neuron_importance__mutmut_25, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_26': xǁMLPScorerǁcompute_neuron_importance__mutmut_26, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_27': xǁMLPScorerǁcompute_neuron_importance__mutmut_27, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_28': xǁMLPScorerǁcompute_neuron_importance__mutmut_28, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_29': xǁMLPScorerǁcompute_neuron_importance__mutmut_29, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_30': xǁMLPScorerǁcompute_neuron_importance__mutmut_30, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_31': xǁMLPScorerǁcompute_neuron_importance__mutmut_31, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_32': xǁMLPScorerǁcompute_neuron_importance__mutmut_32, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_33': xǁMLPScorerǁcompute_neuron_importance__mutmut_33, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_34': xǁMLPScorerǁcompute_neuron_importance__mutmut_34, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_35': xǁMLPScorerǁcompute_neuron_importance__mutmut_35, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_36': xǁMLPScorerǁcompute_neuron_importance__mutmut_36, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_37': xǁMLPScorerǁcompute_neuron_importance__mutmut_37, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_38': xǁMLPScorerǁcompute_neuron_importance__mutmut_38, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_39': xǁMLPScorerǁcompute_neuron_importance__mutmut_39, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_40': xǁMLPScorerǁcompute_neuron_importance__mutmut_40, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_41': xǁMLPScorerǁcompute_neuron_importance__mutmut_41, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_42': xǁMLPScorerǁcompute_neuron_importance__mutmut_42, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_43': xǁMLPScorerǁcompute_neuron_importance__mutmut_43, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_44': xǁMLPScorerǁcompute_neuron_importance__mutmut_44, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_45': xǁMLPScorerǁcompute_neuron_importance__mutmut_45, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_46': xǁMLPScorerǁcompute_neuron_importance__mutmut_46, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_47': xǁMLPScorerǁcompute_neuron_importance__mutmut_47, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_48': xǁMLPScorerǁcompute_neuron_importance__mutmut_48, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_49': xǁMLPScorerǁcompute_neuron_importance__mutmut_49, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_50': xǁMLPScorerǁcompute_neuron_importance__mutmut_50, 
        'xǁMLPScorerǁcompute_neuron_importance__mutmut_51': xǁMLPScorerǁcompute_neuron_importance__mutmut_51
    }
    
    def compute_neuron_importance(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMLPScorerǁcompute_neuron_importance__mutmut_orig"), object.__getattribute__(self, "xǁMLPScorerǁcompute_neuron_importance__mutmut_mutants"), args, kwargs, self)
        return result 
    
    compute_neuron_importance.__signature__ = _mutmut_signature(xǁMLPScorerǁcompute_neuron_importance__mutmut_orig)
    xǁMLPScorerǁcompute_neuron_importance__mutmut_orig.__name__ = 'xǁMLPScorerǁcompute_neuron_importance'
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_orig(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_1(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = None
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_2(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'XXmeanXX': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_3(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'MEAN': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_4(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'XXstdXX': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_5(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'STD': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_6(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'XXminXX': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_7(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'MIN': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_8(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'XXmaxXX': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_9(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'MAX': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_10(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'XXsparsityXX': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_11(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'SPARSITY': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_12(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() != 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_13(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 4:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_14(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = None
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_15(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(None, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_16(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, None)
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_17(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_18(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, )
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_19(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(+1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_20(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-2, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_21(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(None))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_22(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(+1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_23(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-2))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_24(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = None
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_25(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(None)
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_26(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['XXmeanXX'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_27(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['MEAN'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_28(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=None).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_29(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=1).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_30(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(None)
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_31(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['XXstdXX'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_32(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['STD'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_33(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=None).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_34(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=1).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_35(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(None)
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_36(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['XXminXX'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_37(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['MIN'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_38(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=None)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_39(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=1)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_40(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[1].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_41(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(None)
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_42(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['XXmaxXX'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_43(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['MAX'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_44(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=None)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_45(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=1)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_46(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[1].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_47(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = None
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_48(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=None).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_49(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() <= 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_50(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 1.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_51(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=1).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_52(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(None)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_53(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['XXsparsityXX'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_54(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['SPARSITY'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(v) for k, v in stats.items()}
    
    def xǁMLPScorerǁcompute_activation_statistics__mutmut_55(
        self,
        mlp_activations: List[torch.Tensor]
    ) -> Dict[str, np.ndarray]:
        """
        Compute activation statistics across layers.
        
        Args:
            mlp_activations: List of activation tensors from each layer
            
        Returns:
            Dictionary with statistics (mean, std, min, max, sparsity)
        """
        stats = {
            'mean': [],
            'std': [],
            'min': [],
            'max': [],
            'sparsity': []  # Fraction of near-zero activations
        }
        
        for activation in mlp_activations:
            # Flatten spatial dimensions
            if activation.dim() == 3:
                flat = activation.reshape(-1, activation.size(-1))
            else:
                flat = activation
            
            stats['mean'].append(flat.mean(dim=0).numpy())
            stats['std'].append(flat.std(dim=0).numpy())
            stats['min'].append(flat.min(dim=0)[0].numpy())
            stats['max'].append(flat.max(dim=0)[0].numpy())
            
            # Sparsity: fraction of activations below threshold
            sparsity = (flat.abs() < 0.01).float().mean(dim=0).numpy()
            stats['sparsity'].append(sparsity)
        
        # Stack across layers
        return {k: np.stack(None) for k, v in stats.items()}
    
    xǁMLPScorerǁcompute_activation_statistics__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMLPScorerǁcompute_activation_statistics__mutmut_1': xǁMLPScorerǁcompute_activation_statistics__mutmut_1, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_2': xǁMLPScorerǁcompute_activation_statistics__mutmut_2, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_3': xǁMLPScorerǁcompute_activation_statistics__mutmut_3, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_4': xǁMLPScorerǁcompute_activation_statistics__mutmut_4, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_5': xǁMLPScorerǁcompute_activation_statistics__mutmut_5, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_6': xǁMLPScorerǁcompute_activation_statistics__mutmut_6, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_7': xǁMLPScorerǁcompute_activation_statistics__mutmut_7, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_8': xǁMLPScorerǁcompute_activation_statistics__mutmut_8, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_9': xǁMLPScorerǁcompute_activation_statistics__mutmut_9, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_10': xǁMLPScorerǁcompute_activation_statistics__mutmut_10, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_11': xǁMLPScorerǁcompute_activation_statistics__mutmut_11, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_12': xǁMLPScorerǁcompute_activation_statistics__mutmut_12, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_13': xǁMLPScorerǁcompute_activation_statistics__mutmut_13, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_14': xǁMLPScorerǁcompute_activation_statistics__mutmut_14, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_15': xǁMLPScorerǁcompute_activation_statistics__mutmut_15, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_16': xǁMLPScorerǁcompute_activation_statistics__mutmut_16, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_17': xǁMLPScorerǁcompute_activation_statistics__mutmut_17, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_18': xǁMLPScorerǁcompute_activation_statistics__mutmut_18, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_19': xǁMLPScorerǁcompute_activation_statistics__mutmut_19, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_20': xǁMLPScorerǁcompute_activation_statistics__mutmut_20, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_21': xǁMLPScorerǁcompute_activation_statistics__mutmut_21, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_22': xǁMLPScorerǁcompute_activation_statistics__mutmut_22, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_23': xǁMLPScorerǁcompute_activation_statistics__mutmut_23, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_24': xǁMLPScorerǁcompute_activation_statistics__mutmut_24, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_25': xǁMLPScorerǁcompute_activation_statistics__mutmut_25, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_26': xǁMLPScorerǁcompute_activation_statistics__mutmut_26, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_27': xǁMLPScorerǁcompute_activation_statistics__mutmut_27, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_28': xǁMLPScorerǁcompute_activation_statistics__mutmut_28, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_29': xǁMLPScorerǁcompute_activation_statistics__mutmut_29, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_30': xǁMLPScorerǁcompute_activation_statistics__mutmut_30, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_31': xǁMLPScorerǁcompute_activation_statistics__mutmut_31, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_32': xǁMLPScorerǁcompute_activation_statistics__mutmut_32, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_33': xǁMLPScorerǁcompute_activation_statistics__mutmut_33, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_34': xǁMLPScorerǁcompute_activation_statistics__mutmut_34, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_35': xǁMLPScorerǁcompute_activation_statistics__mutmut_35, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_36': xǁMLPScorerǁcompute_activation_statistics__mutmut_36, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_37': xǁMLPScorerǁcompute_activation_statistics__mutmut_37, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_38': xǁMLPScorerǁcompute_activation_statistics__mutmut_38, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_39': xǁMLPScorerǁcompute_activation_statistics__mutmut_39, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_40': xǁMLPScorerǁcompute_activation_statistics__mutmut_40, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_41': xǁMLPScorerǁcompute_activation_statistics__mutmut_41, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_42': xǁMLPScorerǁcompute_activation_statistics__mutmut_42, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_43': xǁMLPScorerǁcompute_activation_statistics__mutmut_43, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_44': xǁMLPScorerǁcompute_activation_statistics__mutmut_44, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_45': xǁMLPScorerǁcompute_activation_statistics__mutmut_45, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_46': xǁMLPScorerǁcompute_activation_statistics__mutmut_46, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_47': xǁMLPScorerǁcompute_activation_statistics__mutmut_47, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_48': xǁMLPScorerǁcompute_activation_statistics__mutmut_48, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_49': xǁMLPScorerǁcompute_activation_statistics__mutmut_49, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_50': xǁMLPScorerǁcompute_activation_statistics__mutmut_50, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_51': xǁMLPScorerǁcompute_activation_statistics__mutmut_51, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_52': xǁMLPScorerǁcompute_activation_statistics__mutmut_52, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_53': xǁMLPScorerǁcompute_activation_statistics__mutmut_53, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_54': xǁMLPScorerǁcompute_activation_statistics__mutmut_54, 
        'xǁMLPScorerǁcompute_activation_statistics__mutmut_55': xǁMLPScorerǁcompute_activation_statistics__mutmut_55
    }
    
    def compute_activation_statistics(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMLPScorerǁcompute_activation_statistics__mutmut_orig"), object.__getattribute__(self, "xǁMLPScorerǁcompute_activation_statistics__mutmut_mutants"), args, kwargs, self)
        return result 
    
    compute_activation_statistics.__signature__ = _mutmut_signature(xǁMLPScorerǁcompute_activation_statistics__mutmut_orig)
    xǁMLPScorerǁcompute_activation_statistics__mutmut_orig.__name__ = 'xǁMLPScorerǁcompute_activation_statistics'
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_orig(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
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
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_1(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "XXmean_absXX"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
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
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_2(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "MEAN_ABS"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
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
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_3(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = None
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
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
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_4(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            None, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
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
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_5(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, None
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
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
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_6(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
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
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_7(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
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
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_8(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
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
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_9(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError(None)
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
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
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_10(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("XXFailed to extract MLP activations from modelXX")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
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
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_11(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("failed to extract mlp activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
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
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_12(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("FAILED TO EXTRACT MLP ACTIVATIONS FROM MODEL")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
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
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_13(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = None
        
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
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_14(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            None, method=importance_method
        )
        
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
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_15(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=None
        )
        
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
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_16(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            method=importance_method
        )
        
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
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_17(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, )
        
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
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_18(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
        # Compute activation statistics
        stats = None
        
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
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_19(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
        # Compute activation statistics
        stats = self.compute_activation_statistics(None)
        
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
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_20(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
        # Compute activation statistics
        stats = self.compute_activation_statistics(activations)
        
        # Stack activations for output
        # Average across batch and sequence dimensions
        stacked_activations = None
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
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_21(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
        # Compute activation statistics
        stats = self.compute_activation_statistics(activations)
        
        # Stack activations for output
        # Average across batch and sequence dimensions
        stacked_activations = []
        for act in activations:
            if act.dim() != 3:
                stacked_activations.append(act.mean(dim=(0, 1)).numpy())
            else:
                stacked_activations.append(act.mean(dim=0).numpy())
        
        stacked_activations = np.stack(stacked_activations)
        
        return MLPAnalysis(
            activations=stacked_activations,
            neuron_importance=importance,
            layer_stats=stats,
            layer_names=layer_names,
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_22(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
        # Compute activation statistics
        stats = self.compute_activation_statistics(activations)
        
        # Stack activations for output
        # Average across batch and sequence dimensions
        stacked_activations = []
        for act in activations:
            if act.dim() == 4:
                stacked_activations.append(act.mean(dim=(0, 1)).numpy())
            else:
                stacked_activations.append(act.mean(dim=0).numpy())
        
        stacked_activations = np.stack(stacked_activations)
        
        return MLPAnalysis(
            activations=stacked_activations,
            neuron_importance=importance,
            layer_stats=stats,
            layer_names=layer_names,
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_23(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
        # Compute activation statistics
        stats = self.compute_activation_statistics(activations)
        
        # Stack activations for output
        # Average across batch and sequence dimensions
        stacked_activations = []
        for act in activations:
            if act.dim() == 3:
                stacked_activations.append(None)
            else:
                stacked_activations.append(act.mean(dim=0).numpy())
        
        stacked_activations = np.stack(stacked_activations)
        
        return MLPAnalysis(
            activations=stacked_activations,
            neuron_importance=importance,
            layer_stats=stats,
            layer_names=layer_names,
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_24(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
        # Compute activation statistics
        stats = self.compute_activation_statistics(activations)
        
        # Stack activations for output
        # Average across batch and sequence dimensions
        stacked_activations = []
        for act in activations:
            if act.dim() == 3:
                stacked_activations.append(act.mean(dim=None).numpy())
            else:
                stacked_activations.append(act.mean(dim=0).numpy())
        
        stacked_activations = np.stack(stacked_activations)
        
        return MLPAnalysis(
            activations=stacked_activations,
            neuron_importance=importance,
            layer_stats=stats,
            layer_names=layer_names,
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_25(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
        # Compute activation statistics
        stats = self.compute_activation_statistics(activations)
        
        # Stack activations for output
        # Average across batch and sequence dimensions
        stacked_activations = []
        for act in activations:
            if act.dim() == 3:
                stacked_activations.append(act.mean(dim=(1, 1)).numpy())
            else:
                stacked_activations.append(act.mean(dim=0).numpy())
        
        stacked_activations = np.stack(stacked_activations)
        
        return MLPAnalysis(
            activations=stacked_activations,
            neuron_importance=importance,
            layer_stats=stats,
            layer_names=layer_names,
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_26(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
        # Compute activation statistics
        stats = self.compute_activation_statistics(activations)
        
        # Stack activations for output
        # Average across batch and sequence dimensions
        stacked_activations = []
        for act in activations:
            if act.dim() == 3:
                stacked_activations.append(act.mean(dim=(0, 2)).numpy())
            else:
                stacked_activations.append(act.mean(dim=0).numpy())
        
        stacked_activations = np.stack(stacked_activations)
        
        return MLPAnalysis(
            activations=stacked_activations,
            neuron_importance=importance,
            layer_stats=stats,
            layer_names=layer_names,
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_27(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
        # Compute activation statistics
        stats = self.compute_activation_statistics(activations)
        
        # Stack activations for output
        # Average across batch and sequence dimensions
        stacked_activations = []
        for act in activations:
            if act.dim() == 3:
                stacked_activations.append(act.mean(dim=(0, 1)).numpy())
            else:
                stacked_activations.append(None)
        
        stacked_activations = np.stack(stacked_activations)
        
        return MLPAnalysis(
            activations=stacked_activations,
            neuron_importance=importance,
            layer_stats=stats,
            layer_names=layer_names,
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_28(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
        # Compute activation statistics
        stats = self.compute_activation_statistics(activations)
        
        # Stack activations for output
        # Average across batch and sequence dimensions
        stacked_activations = []
        for act in activations:
            if act.dim() == 3:
                stacked_activations.append(act.mean(dim=(0, 1)).numpy())
            else:
                stacked_activations.append(act.mean(dim=None).numpy())
        
        stacked_activations = np.stack(stacked_activations)
        
        return MLPAnalysis(
            activations=stacked_activations,
            neuron_importance=importance,
            layer_stats=stats,
            layer_names=layer_names,
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_29(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
        # Compute activation statistics
        stats = self.compute_activation_statistics(activations)
        
        # Stack activations for output
        # Average across batch and sequence dimensions
        stacked_activations = []
        for act in activations:
            if act.dim() == 3:
                stacked_activations.append(act.mean(dim=(0, 1)).numpy())
            else:
                stacked_activations.append(act.mean(dim=1).numpy())
        
        stacked_activations = np.stack(stacked_activations)
        
        return MLPAnalysis(
            activations=stacked_activations,
            neuron_importance=importance,
            layer_stats=stats,
            layer_names=layer_names,
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_30(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
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
        
        stacked_activations = None
        
        return MLPAnalysis(
            activations=stacked_activations,
            neuron_importance=importance,
            layer_stats=stats,
            layer_names=layer_names,
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_31(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
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
        
        stacked_activations = np.stack(None)
        
        return MLPAnalysis(
            activations=stacked_activations,
            neuron_importance=importance,
            layer_stats=stats,
            layer_names=layer_names,
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_32(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
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
            activations=None,
            neuron_importance=importance,
            layer_stats=stats,
            layer_names=layer_names,
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_33(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
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
            neuron_importance=None,
            layer_stats=stats,
            layer_names=layer_names,
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_34(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
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
            layer_stats=None,
            layer_names=layer_names,
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_35(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
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
            layer_names=None,
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_36(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
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
            input_shape=None
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_37(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
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
            neuron_importance=importance,
            layer_stats=stats,
            layer_names=layer_names,
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_38(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
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
            layer_stats=stats,
            layer_names=layer_names,
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_39(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
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
            layer_names=layer_names,
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_40(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
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
            input_shape=input_ids.shape
        )
    
    def xǁMLPScorerǁanalyze_mlp__mutmut_41(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        importance_method: str = "mean_abs"
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
        activations, layer_names = self.extract_mlp_activations(
            input_ids, attention_mask
        )
        
        if not activations:
            raise ValueError("Failed to extract MLP activations from model")
        
        # Compute neuron importance
        importance = self.compute_neuron_importance(
            activations, method=importance_method
        )
        
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
            )
    
    xǁMLPScorerǁanalyze_mlp__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMLPScorerǁanalyze_mlp__mutmut_1': xǁMLPScorerǁanalyze_mlp__mutmut_1, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_2': xǁMLPScorerǁanalyze_mlp__mutmut_2, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_3': xǁMLPScorerǁanalyze_mlp__mutmut_3, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_4': xǁMLPScorerǁanalyze_mlp__mutmut_4, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_5': xǁMLPScorerǁanalyze_mlp__mutmut_5, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_6': xǁMLPScorerǁanalyze_mlp__mutmut_6, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_7': xǁMLPScorerǁanalyze_mlp__mutmut_7, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_8': xǁMLPScorerǁanalyze_mlp__mutmut_8, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_9': xǁMLPScorerǁanalyze_mlp__mutmut_9, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_10': xǁMLPScorerǁanalyze_mlp__mutmut_10, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_11': xǁMLPScorerǁanalyze_mlp__mutmut_11, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_12': xǁMLPScorerǁanalyze_mlp__mutmut_12, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_13': xǁMLPScorerǁanalyze_mlp__mutmut_13, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_14': xǁMLPScorerǁanalyze_mlp__mutmut_14, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_15': xǁMLPScorerǁanalyze_mlp__mutmut_15, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_16': xǁMLPScorerǁanalyze_mlp__mutmut_16, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_17': xǁMLPScorerǁanalyze_mlp__mutmut_17, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_18': xǁMLPScorerǁanalyze_mlp__mutmut_18, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_19': xǁMLPScorerǁanalyze_mlp__mutmut_19, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_20': xǁMLPScorerǁanalyze_mlp__mutmut_20, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_21': xǁMLPScorerǁanalyze_mlp__mutmut_21, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_22': xǁMLPScorerǁanalyze_mlp__mutmut_22, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_23': xǁMLPScorerǁanalyze_mlp__mutmut_23, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_24': xǁMLPScorerǁanalyze_mlp__mutmut_24, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_25': xǁMLPScorerǁanalyze_mlp__mutmut_25, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_26': xǁMLPScorerǁanalyze_mlp__mutmut_26, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_27': xǁMLPScorerǁanalyze_mlp__mutmut_27, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_28': xǁMLPScorerǁanalyze_mlp__mutmut_28, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_29': xǁMLPScorerǁanalyze_mlp__mutmut_29, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_30': xǁMLPScorerǁanalyze_mlp__mutmut_30, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_31': xǁMLPScorerǁanalyze_mlp__mutmut_31, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_32': xǁMLPScorerǁanalyze_mlp__mutmut_32, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_33': xǁMLPScorerǁanalyze_mlp__mutmut_33, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_34': xǁMLPScorerǁanalyze_mlp__mutmut_34, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_35': xǁMLPScorerǁanalyze_mlp__mutmut_35, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_36': xǁMLPScorerǁanalyze_mlp__mutmut_36, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_37': xǁMLPScorerǁanalyze_mlp__mutmut_37, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_38': xǁMLPScorerǁanalyze_mlp__mutmut_38, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_39': xǁMLPScorerǁanalyze_mlp__mutmut_39, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_40': xǁMLPScorerǁanalyze_mlp__mutmut_40, 
        'xǁMLPScorerǁanalyze_mlp__mutmut_41': xǁMLPScorerǁanalyze_mlp__mutmut_41
    }
    
    def analyze_mlp(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMLPScorerǁanalyze_mlp__mutmut_orig"), object.__getattribute__(self, "xǁMLPScorerǁanalyze_mlp__mutmut_mutants"), args, kwargs, self)
        return result 
    
    analyze_mlp.__signature__ = _mutmut_signature(xǁMLPScorerǁanalyze_mlp__mutmut_orig)
    xǁMLPScorerǁanalyze_mlp__mutmut_orig.__name__ = 'xǁMLPScorerǁanalyze_mlp'
    
    def xǁMLPScorerǁget_top_neurons__mutmut_orig(
        self,
        analysis: MLPAnalysis,
        top_k: int = 10
    ) -> Dict[int, List[Tuple[int, float]]]:
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
                (int(idx), float(layer_importance[idx]))
                for idx in top_indices
            ]
        
        return top_neurons
    
    def xǁMLPScorerǁget_top_neurons__mutmut_1(
        self,
        analysis: MLPAnalysis,
        top_k: int = 11
    ) -> Dict[int, List[Tuple[int, float]]]:
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
                (int(idx), float(layer_importance[idx]))
                for idx in top_indices
            ]
        
        return top_neurons
    
    def xǁMLPScorerǁget_top_neurons__mutmut_2(
        self,
        analysis: MLPAnalysis,
        top_k: int = 10
    ) -> Dict[int, List[Tuple[int, float]]]:
        """
        Get the top-k most important neurons in each layer.
        
        Args:
            analysis: MLPAnalysis result
            top_k: Number of top neurons to return per layer
            
        Returns:
            Dictionary mapping layer_idx to list of (neuron_idx, importance_score) tuples
        """
        top_neurons = None
        
        for layer_idx in range(analysis.neuron_importance.shape[0]):
            layer_importance = analysis.neuron_importance[layer_idx]
            top_indices = np.argsort(layer_importance)[-top_k:][::-1]
            
            top_neurons[layer_idx] = [
                (int(idx), float(layer_importance[idx]))
                for idx in top_indices
            ]
        
        return top_neurons
    
    def xǁMLPScorerǁget_top_neurons__mutmut_3(
        self,
        analysis: MLPAnalysis,
        top_k: int = 10
    ) -> Dict[int, List[Tuple[int, float]]]:
        """
        Get the top-k most important neurons in each layer.
        
        Args:
            analysis: MLPAnalysis result
            top_k: Number of top neurons to return per layer
            
        Returns:
            Dictionary mapping layer_idx to list of (neuron_idx, importance_score) tuples
        """
        top_neurons = {}
        
        for layer_idx in range(None):
            layer_importance = analysis.neuron_importance[layer_idx]
            top_indices = np.argsort(layer_importance)[-top_k:][::-1]
            
            top_neurons[layer_idx] = [
                (int(idx), float(layer_importance[idx]))
                for idx in top_indices
            ]
        
        return top_neurons
    
    def xǁMLPScorerǁget_top_neurons__mutmut_4(
        self,
        analysis: MLPAnalysis,
        top_k: int = 10
    ) -> Dict[int, List[Tuple[int, float]]]:
        """
        Get the top-k most important neurons in each layer.
        
        Args:
            analysis: MLPAnalysis result
            top_k: Number of top neurons to return per layer
            
        Returns:
            Dictionary mapping layer_idx to list of (neuron_idx, importance_score) tuples
        """
        top_neurons = {}
        
        for layer_idx in range(analysis.neuron_importance.shape[1]):
            layer_importance = analysis.neuron_importance[layer_idx]
            top_indices = np.argsort(layer_importance)[-top_k:][::-1]
            
            top_neurons[layer_idx] = [
                (int(idx), float(layer_importance[idx]))
                for idx in top_indices
            ]
        
        return top_neurons
    
    def xǁMLPScorerǁget_top_neurons__mutmut_5(
        self,
        analysis: MLPAnalysis,
        top_k: int = 10
    ) -> Dict[int, List[Tuple[int, float]]]:
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
            layer_importance = None
            top_indices = np.argsort(layer_importance)[-top_k:][::-1]
            
            top_neurons[layer_idx] = [
                (int(idx), float(layer_importance[idx]))
                for idx in top_indices
            ]
        
        return top_neurons
    
    def xǁMLPScorerǁget_top_neurons__mutmut_6(
        self,
        analysis: MLPAnalysis,
        top_k: int = 10
    ) -> Dict[int, List[Tuple[int, float]]]:
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
            top_indices = None
            
            top_neurons[layer_idx] = [
                (int(idx), float(layer_importance[idx]))
                for idx in top_indices
            ]
        
        return top_neurons
    
    def xǁMLPScorerǁget_top_neurons__mutmut_7(
        self,
        analysis: MLPAnalysis,
        top_k: int = 10
    ) -> Dict[int, List[Tuple[int, float]]]:
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
            top_indices = np.argsort(None)[-top_k:][::-1]
            
            top_neurons[layer_idx] = [
                (int(idx), float(layer_importance[idx]))
                for idx in top_indices
            ]
        
        return top_neurons
    
    def xǁMLPScorerǁget_top_neurons__mutmut_8(
        self,
        analysis: MLPAnalysis,
        top_k: int = 10
    ) -> Dict[int, List[Tuple[int, float]]]:
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
            top_indices = np.argsort(layer_importance)[+top_k:][::-1]
            
            top_neurons[layer_idx] = [
                (int(idx), float(layer_importance[idx]))
                for idx in top_indices
            ]
        
        return top_neurons
    
    def xǁMLPScorerǁget_top_neurons__mutmut_9(
        self,
        analysis: MLPAnalysis,
        top_k: int = 10
    ) -> Dict[int, List[Tuple[int, float]]]:
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
            top_indices = np.argsort(layer_importance)[-top_k:][::+1]
            
            top_neurons[layer_idx] = [
                (int(idx), float(layer_importance[idx]))
                for idx in top_indices
            ]
        
        return top_neurons
    
    def xǁMLPScorerǁget_top_neurons__mutmut_10(
        self,
        analysis: MLPAnalysis,
        top_k: int = 10
    ) -> Dict[int, List[Tuple[int, float]]]:
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
            top_indices = np.argsort(layer_importance)[-top_k:][::-2]
            
            top_neurons[layer_idx] = [
                (int(idx), float(layer_importance[idx]))
                for idx in top_indices
            ]
        
        return top_neurons
    
    def xǁMLPScorerǁget_top_neurons__mutmut_11(
        self,
        analysis: MLPAnalysis,
        top_k: int = 10
    ) -> Dict[int, List[Tuple[int, float]]]:
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
            
            top_neurons[layer_idx] = None
        
        return top_neurons
    
    def xǁMLPScorerǁget_top_neurons__mutmut_12(
        self,
        analysis: MLPAnalysis,
        top_k: int = 10
    ) -> Dict[int, List[Tuple[int, float]]]:
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
                (int(None), float(layer_importance[idx]))
                for idx in top_indices
            ]
        
        return top_neurons
    
    def xǁMLPScorerǁget_top_neurons__mutmut_13(
        self,
        analysis: MLPAnalysis,
        top_k: int = 10
    ) -> Dict[int, List[Tuple[int, float]]]:
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
                (int(idx), float(None))
                for idx in top_indices
            ]
        
        return top_neurons
    
    xǁMLPScorerǁget_top_neurons__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMLPScorerǁget_top_neurons__mutmut_1': xǁMLPScorerǁget_top_neurons__mutmut_1, 
        'xǁMLPScorerǁget_top_neurons__mutmut_2': xǁMLPScorerǁget_top_neurons__mutmut_2, 
        'xǁMLPScorerǁget_top_neurons__mutmut_3': xǁMLPScorerǁget_top_neurons__mutmut_3, 
        'xǁMLPScorerǁget_top_neurons__mutmut_4': xǁMLPScorerǁget_top_neurons__mutmut_4, 
        'xǁMLPScorerǁget_top_neurons__mutmut_5': xǁMLPScorerǁget_top_neurons__mutmut_5, 
        'xǁMLPScorerǁget_top_neurons__mutmut_6': xǁMLPScorerǁget_top_neurons__mutmut_6, 
        'xǁMLPScorerǁget_top_neurons__mutmut_7': xǁMLPScorerǁget_top_neurons__mutmut_7, 
        'xǁMLPScorerǁget_top_neurons__mutmut_8': xǁMLPScorerǁget_top_neurons__mutmut_8, 
        'xǁMLPScorerǁget_top_neurons__mutmut_9': xǁMLPScorerǁget_top_neurons__mutmut_9, 
        'xǁMLPScorerǁget_top_neurons__mutmut_10': xǁMLPScorerǁget_top_neurons__mutmut_10, 
        'xǁMLPScorerǁget_top_neurons__mutmut_11': xǁMLPScorerǁget_top_neurons__mutmut_11, 
        'xǁMLPScorerǁget_top_neurons__mutmut_12': xǁMLPScorerǁget_top_neurons__mutmut_12, 
        'xǁMLPScorerǁget_top_neurons__mutmut_13': xǁMLPScorerǁget_top_neurons__mutmut_13
    }
    
    def get_top_neurons(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMLPScorerǁget_top_neurons__mutmut_orig"), object.__getattribute__(self, "xǁMLPScorerǁget_top_neurons__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_top_neurons.__signature__ = _mutmut_signature(xǁMLPScorerǁget_top_neurons__mutmut_orig)
    xǁMLPScorerǁget_top_neurons__mutmut_orig.__name__ = 'xǁMLPScorerǁget_top_neurons'
    
    def xǁMLPScorerǁget_dead_neurons__mutmut_orig(
        self,
        analysis: MLPAnalysis,
        threshold: float = 0.99
    ) -> Dict[int, List[int]]:
        """
        Identify "dead" neurons with very sparse activations.
        
        Args:
            analysis: MLPAnalysis result
            threshold: Sparsity threshold (0-1) to consider a neuron dead
            
        Returns:
            Dictionary mapping layer_idx to list of dead neuron indices
        """
        dead_neurons = {}
        
        sparsity = analysis.layer_stats['sparsity']
        
        for layer_idx in range(sparsity.shape[0]):
            dead_indices = np.where(sparsity[layer_idx] > threshold)[0]
            dead_neurons[layer_idx] = dead_indices.tolist()
        
        return dead_neurons
    
    def xǁMLPScorerǁget_dead_neurons__mutmut_1(
        self,
        analysis: MLPAnalysis,
        threshold: float = 1.99
    ) -> Dict[int, List[int]]:
        """
        Identify "dead" neurons with very sparse activations.
        
        Args:
            analysis: MLPAnalysis result
            threshold: Sparsity threshold (0-1) to consider a neuron dead
            
        Returns:
            Dictionary mapping layer_idx to list of dead neuron indices
        """
        dead_neurons = {}
        
        sparsity = analysis.layer_stats['sparsity']
        
        for layer_idx in range(sparsity.shape[0]):
            dead_indices = np.where(sparsity[layer_idx] > threshold)[0]
            dead_neurons[layer_idx] = dead_indices.tolist()
        
        return dead_neurons
    
    def xǁMLPScorerǁget_dead_neurons__mutmut_2(
        self,
        analysis: MLPAnalysis,
        threshold: float = 0.99
    ) -> Dict[int, List[int]]:
        """
        Identify "dead" neurons with very sparse activations.
        
        Args:
            analysis: MLPAnalysis result
            threshold: Sparsity threshold (0-1) to consider a neuron dead
            
        Returns:
            Dictionary mapping layer_idx to list of dead neuron indices
        """
        dead_neurons = None
        
        sparsity = analysis.layer_stats['sparsity']
        
        for layer_idx in range(sparsity.shape[0]):
            dead_indices = np.where(sparsity[layer_idx] > threshold)[0]
            dead_neurons[layer_idx] = dead_indices.tolist()
        
        return dead_neurons
    
    def xǁMLPScorerǁget_dead_neurons__mutmut_3(
        self,
        analysis: MLPAnalysis,
        threshold: float = 0.99
    ) -> Dict[int, List[int]]:
        """
        Identify "dead" neurons with very sparse activations.
        
        Args:
            analysis: MLPAnalysis result
            threshold: Sparsity threshold (0-1) to consider a neuron dead
            
        Returns:
            Dictionary mapping layer_idx to list of dead neuron indices
        """
        dead_neurons = {}
        
        sparsity = None
        
        for layer_idx in range(sparsity.shape[0]):
            dead_indices = np.where(sparsity[layer_idx] > threshold)[0]
            dead_neurons[layer_idx] = dead_indices.tolist()
        
        return dead_neurons
    
    def xǁMLPScorerǁget_dead_neurons__mutmut_4(
        self,
        analysis: MLPAnalysis,
        threshold: float = 0.99
    ) -> Dict[int, List[int]]:
        """
        Identify "dead" neurons with very sparse activations.
        
        Args:
            analysis: MLPAnalysis result
            threshold: Sparsity threshold (0-1) to consider a neuron dead
            
        Returns:
            Dictionary mapping layer_idx to list of dead neuron indices
        """
        dead_neurons = {}
        
        sparsity = analysis.layer_stats['XXsparsityXX']
        
        for layer_idx in range(sparsity.shape[0]):
            dead_indices = np.where(sparsity[layer_idx] > threshold)[0]
            dead_neurons[layer_idx] = dead_indices.tolist()
        
        return dead_neurons
    
    def xǁMLPScorerǁget_dead_neurons__mutmut_5(
        self,
        analysis: MLPAnalysis,
        threshold: float = 0.99
    ) -> Dict[int, List[int]]:
        """
        Identify "dead" neurons with very sparse activations.
        
        Args:
            analysis: MLPAnalysis result
            threshold: Sparsity threshold (0-1) to consider a neuron dead
            
        Returns:
            Dictionary mapping layer_idx to list of dead neuron indices
        """
        dead_neurons = {}
        
        sparsity = analysis.layer_stats['SPARSITY']
        
        for layer_idx in range(sparsity.shape[0]):
            dead_indices = np.where(sparsity[layer_idx] > threshold)[0]
            dead_neurons[layer_idx] = dead_indices.tolist()
        
        return dead_neurons
    
    def xǁMLPScorerǁget_dead_neurons__mutmut_6(
        self,
        analysis: MLPAnalysis,
        threshold: float = 0.99
    ) -> Dict[int, List[int]]:
        """
        Identify "dead" neurons with very sparse activations.
        
        Args:
            analysis: MLPAnalysis result
            threshold: Sparsity threshold (0-1) to consider a neuron dead
            
        Returns:
            Dictionary mapping layer_idx to list of dead neuron indices
        """
        dead_neurons = {}
        
        sparsity = analysis.layer_stats['sparsity']
        
        for layer_idx in range(None):
            dead_indices = np.where(sparsity[layer_idx] > threshold)[0]
            dead_neurons[layer_idx] = dead_indices.tolist()
        
        return dead_neurons
    
    def xǁMLPScorerǁget_dead_neurons__mutmut_7(
        self,
        analysis: MLPAnalysis,
        threshold: float = 0.99
    ) -> Dict[int, List[int]]:
        """
        Identify "dead" neurons with very sparse activations.
        
        Args:
            analysis: MLPAnalysis result
            threshold: Sparsity threshold (0-1) to consider a neuron dead
            
        Returns:
            Dictionary mapping layer_idx to list of dead neuron indices
        """
        dead_neurons = {}
        
        sparsity = analysis.layer_stats['sparsity']
        
        for layer_idx in range(sparsity.shape[1]):
            dead_indices = np.where(sparsity[layer_idx] > threshold)[0]
            dead_neurons[layer_idx] = dead_indices.tolist()
        
        return dead_neurons
    
    def xǁMLPScorerǁget_dead_neurons__mutmut_8(
        self,
        analysis: MLPAnalysis,
        threshold: float = 0.99
    ) -> Dict[int, List[int]]:
        """
        Identify "dead" neurons with very sparse activations.
        
        Args:
            analysis: MLPAnalysis result
            threshold: Sparsity threshold (0-1) to consider a neuron dead
            
        Returns:
            Dictionary mapping layer_idx to list of dead neuron indices
        """
        dead_neurons = {}
        
        sparsity = analysis.layer_stats['sparsity']
        
        for layer_idx in range(sparsity.shape[0]):
            dead_indices = None
            dead_neurons[layer_idx] = dead_indices.tolist()
        
        return dead_neurons
    
    def xǁMLPScorerǁget_dead_neurons__mutmut_9(
        self,
        analysis: MLPAnalysis,
        threshold: float = 0.99
    ) -> Dict[int, List[int]]:
        """
        Identify "dead" neurons with very sparse activations.
        
        Args:
            analysis: MLPAnalysis result
            threshold: Sparsity threshold (0-1) to consider a neuron dead
            
        Returns:
            Dictionary mapping layer_idx to list of dead neuron indices
        """
        dead_neurons = {}
        
        sparsity = analysis.layer_stats['sparsity']
        
        for layer_idx in range(sparsity.shape[0]):
            dead_indices = np.where(None)[0]
            dead_neurons[layer_idx] = dead_indices.tolist()
        
        return dead_neurons
    
    def xǁMLPScorerǁget_dead_neurons__mutmut_10(
        self,
        analysis: MLPAnalysis,
        threshold: float = 0.99
    ) -> Dict[int, List[int]]:
        """
        Identify "dead" neurons with very sparse activations.
        
        Args:
            analysis: MLPAnalysis result
            threshold: Sparsity threshold (0-1) to consider a neuron dead
            
        Returns:
            Dictionary mapping layer_idx to list of dead neuron indices
        """
        dead_neurons = {}
        
        sparsity = analysis.layer_stats['sparsity']
        
        for layer_idx in range(sparsity.shape[0]):
            dead_indices = np.where(sparsity[layer_idx] >= threshold)[0]
            dead_neurons[layer_idx] = dead_indices.tolist()
        
        return dead_neurons
    
    def xǁMLPScorerǁget_dead_neurons__mutmut_11(
        self,
        analysis: MLPAnalysis,
        threshold: float = 0.99
    ) -> Dict[int, List[int]]:
        """
        Identify "dead" neurons with very sparse activations.
        
        Args:
            analysis: MLPAnalysis result
            threshold: Sparsity threshold (0-1) to consider a neuron dead
            
        Returns:
            Dictionary mapping layer_idx to list of dead neuron indices
        """
        dead_neurons = {}
        
        sparsity = analysis.layer_stats['sparsity']
        
        for layer_idx in range(sparsity.shape[0]):
            dead_indices = np.where(sparsity[layer_idx] > threshold)[1]
            dead_neurons[layer_idx] = dead_indices.tolist()
        
        return dead_neurons
    
    def xǁMLPScorerǁget_dead_neurons__mutmut_12(
        self,
        analysis: MLPAnalysis,
        threshold: float = 0.99
    ) -> Dict[int, List[int]]:
        """
        Identify "dead" neurons with very sparse activations.
        
        Args:
            analysis: MLPAnalysis result
            threshold: Sparsity threshold (0-1) to consider a neuron dead
            
        Returns:
            Dictionary mapping layer_idx to list of dead neuron indices
        """
        dead_neurons = {}
        
        sparsity = analysis.layer_stats['sparsity']
        
        for layer_idx in range(sparsity.shape[0]):
            dead_indices = np.where(sparsity[layer_idx] > threshold)[0]
            dead_neurons[layer_idx] = None
        
        return dead_neurons
    
    xǁMLPScorerǁget_dead_neurons__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMLPScorerǁget_dead_neurons__mutmut_1': xǁMLPScorerǁget_dead_neurons__mutmut_1, 
        'xǁMLPScorerǁget_dead_neurons__mutmut_2': xǁMLPScorerǁget_dead_neurons__mutmut_2, 
        'xǁMLPScorerǁget_dead_neurons__mutmut_3': xǁMLPScorerǁget_dead_neurons__mutmut_3, 
        'xǁMLPScorerǁget_dead_neurons__mutmut_4': xǁMLPScorerǁget_dead_neurons__mutmut_4, 
        'xǁMLPScorerǁget_dead_neurons__mutmut_5': xǁMLPScorerǁget_dead_neurons__mutmut_5, 
        'xǁMLPScorerǁget_dead_neurons__mutmut_6': xǁMLPScorerǁget_dead_neurons__mutmut_6, 
        'xǁMLPScorerǁget_dead_neurons__mutmut_7': xǁMLPScorerǁget_dead_neurons__mutmut_7, 
        'xǁMLPScorerǁget_dead_neurons__mutmut_8': xǁMLPScorerǁget_dead_neurons__mutmut_8, 
        'xǁMLPScorerǁget_dead_neurons__mutmut_9': xǁMLPScorerǁget_dead_neurons__mutmut_9, 
        'xǁMLPScorerǁget_dead_neurons__mutmut_10': xǁMLPScorerǁget_dead_neurons__mutmut_10, 
        'xǁMLPScorerǁget_dead_neurons__mutmut_11': xǁMLPScorerǁget_dead_neurons__mutmut_11, 
        'xǁMLPScorerǁget_dead_neurons__mutmut_12': xǁMLPScorerǁget_dead_neurons__mutmut_12
    }
    
    def get_dead_neurons(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMLPScorerǁget_dead_neurons__mutmut_orig"), object.__getattribute__(self, "xǁMLPScorerǁget_dead_neurons__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_dead_neurons.__signature__ = _mutmut_signature(xǁMLPScorerǁget_dead_neurons__mutmut_orig)
    xǁMLPScorerǁget_dead_neurons__mutmut_orig.__name__ = 'xǁMLPScorerǁget_dead_neurons'
    
    def xǁMLPScorerǁcompare_inputs__mutmut_orig(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_1(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
        analysis_1 = None
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_2(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
        analysis_1 = self.analyze_mlp(None, attention_mask_1)
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_3(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
        analysis_1 = self.analyze_mlp(input_ids_1, None)
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_4(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
        analysis_1 = self.analyze_mlp(attention_mask_1)
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_5(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
        analysis_1 = self.analyze_mlp(input_ids_1, )
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_6(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
        analysis_2 = None
        
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_7(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
        analysis_2 = self.analyze_mlp(None, attention_mask_2)
        
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_8(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
        analysis_2 = self.analyze_mlp(input_ids_2, None)
        
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_9(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
        analysis_2 = self.analyze_mlp(attention_mask_2)
        
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_10(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
        analysis_2 = self.analyze_mlp(input_ids_2, )
        
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_11(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
        if analysis_1.activations.shape[1] != analysis_2.activations.shape[0]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_12(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
        if analysis_1.activations.shape[0] == analysis_2.activations.shape[0]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_13(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
        if analysis_1.activations.shape[0] != analysis_2.activations.shape[1]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_14(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
            raise ValueError(None)
        
        # Compute differences
        diff = analysis_1.activations - analysis_2.activations
        
        # Compute correlation per layer
        correlations = []
        for layer_idx in range(analysis_1.activations.shape[0]):
            act1 = analysis_1.activations[layer_idx]
            act2 = analysis_2.activations[layer_idx]
            
            # Check for constant arrays (zero variance) to avoid correlation errors
            if np.std(act1) < 1e-10 or np.std(act2) < 1e-10:
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_15(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
            raise ValueError("XXModels have different number of layersXX")
        
        # Compute differences
        diff = analysis_1.activations - analysis_2.activations
        
        # Compute correlation per layer
        correlations = []
        for layer_idx in range(analysis_1.activations.shape[0]):
            act1 = analysis_1.activations[layer_idx]
            act2 = analysis_2.activations[layer_idx]
            
            # Check for constant arrays (zero variance) to avoid correlation errors
            if np.std(act1) < 1e-10 or np.std(act2) < 1e-10:
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_16(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
            raise ValueError("models have different number of layers")
        
        # Compute differences
        diff = analysis_1.activations - analysis_2.activations
        
        # Compute correlation per layer
        correlations = []
        for layer_idx in range(analysis_1.activations.shape[0]):
            act1 = analysis_1.activations[layer_idx]
            act2 = analysis_2.activations[layer_idx]
            
            # Check for constant arrays (zero variance) to avoid correlation errors
            if np.std(act1) < 1e-10 or np.std(act2) < 1e-10:
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_17(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
            raise ValueError("MODELS HAVE DIFFERENT NUMBER OF LAYERS")
        
        # Compute differences
        diff = analysis_1.activations - analysis_2.activations
        
        # Compute correlation per layer
        correlations = []
        for layer_idx in range(analysis_1.activations.shape[0]):
            act1 = analysis_1.activations[layer_idx]
            act2 = analysis_2.activations[layer_idx]
            
            # Check for constant arrays (zero variance) to avoid correlation errors
            if np.std(act1) < 1e-10 or np.std(act2) < 1e-10:
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_18(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
        diff = None
        
        # Compute correlation per layer
        correlations = []
        for layer_idx in range(analysis_1.activations.shape[0]):
            act1 = analysis_1.activations[layer_idx]
            act2 = analysis_2.activations[layer_idx]
            
            # Check for constant arrays (zero variance) to avoid correlation errors
            if np.std(act1) < 1e-10 or np.std(act2) < 1e-10:
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_19(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
        diff = analysis_1.activations + analysis_2.activations
        
        # Compute correlation per layer
        correlations = []
        for layer_idx in range(analysis_1.activations.shape[0]):
            act1 = analysis_1.activations[layer_idx]
            act2 = analysis_2.activations[layer_idx]
            
            # Check for constant arrays (zero variance) to avoid correlation errors
            if np.std(act1) < 1e-10 or np.std(act2) < 1e-10:
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_20(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
        correlations = None
        for layer_idx in range(analysis_1.activations.shape[0]):
            act1 = analysis_1.activations[layer_idx]
            act2 = analysis_2.activations[layer_idx]
            
            # Check for constant arrays (zero variance) to avoid correlation errors
            if np.std(act1) < 1e-10 or np.std(act2) < 1e-10:
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_21(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
        for layer_idx in range(None):
            act1 = analysis_1.activations[layer_idx]
            act2 = analysis_2.activations[layer_idx]
            
            # Check for constant arrays (zero variance) to avoid correlation errors
            if np.std(act1) < 1e-10 or np.std(act2) < 1e-10:
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_22(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
        for layer_idx in range(analysis_1.activations.shape[1]):
            act1 = analysis_1.activations[layer_idx]
            act2 = analysis_2.activations[layer_idx]
            
            # Check for constant arrays (zero variance) to avoid correlation errors
            if np.std(act1) < 1e-10 or np.std(act2) < 1e-10:
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_23(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
            act1 = None
            act2 = analysis_2.activations[layer_idx]
            
            # Check for constant arrays (zero variance) to avoid correlation errors
            if np.std(act1) < 1e-10 or np.std(act2) < 1e-10:
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_24(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
            act2 = None
            
            # Check for constant arrays (zero variance) to avoid correlation errors
            if np.std(act1) < 1e-10 or np.std(act2) < 1e-10:
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_25(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
            if np.std(act1) < 1e-10 and np.std(act2) < 1e-10:
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_26(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
            if np.std(None) < 1e-10 or np.std(act2) < 1e-10:
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_27(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
            if np.std(act1) <= 1e-10 or np.std(act2) < 1e-10:
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_28(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
            if np.std(act1) < 1.0000000001 or np.std(act2) < 1e-10:
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_29(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
            if np.std(act1) < 1e-10 or np.std(None) < 1e-10:
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_30(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
            if np.std(act1) < 1e-10 or np.std(act2) <= 1e-10:
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_31(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
            if np.std(act1) < 1e-10 or np.std(act2) < 1.0000000001:
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_32(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = None
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_33(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 2.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_34(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(None, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_35(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, None) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_36(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_37(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, ) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_38(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 1.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_39(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = None
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_40(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(None, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_41(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, None)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_42(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_43(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, )[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_44(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[1, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_45(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 2]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_46(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(None)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_47(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = None
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_48(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(None, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_49(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=None)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_50(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_51(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, )
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_52(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=2)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_53(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'XXdiffXX': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_54(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'DIFF': diff,
            'correlation': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_55(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'XXcorrelationXX': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_56(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'CORRELATION': np.array(correlations),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_57(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(None),
            'l2_distance': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_58(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'XXl2_distanceXX': distances
        }
    
    def xǁMLPScorerǁcompare_inputs__mutmut_59(
        self,
        input_ids_1: torch.Tensor,
        input_ids_2: torch.Tensor,
        attention_mask_1: Optional[torch.Tensor] = None,
        attention_mask_2: Optional[torch.Tensor] = None,
    ) -> Dict[str, np.ndarray]:
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
                # If either array is constant, correlation is undefined; use 0 or 1 based on equality
                corr = 1.0 if np.allclose(act1, act2) else 0.0
            else:
                corr = np.corrcoef(act1, act2)[0, 1]
            
            correlations.append(corr)
        
        # Compute L2 distance per layer
        distances = np.linalg.norm(diff, axis=1)
        
        return {
            'diff': diff,
            'correlation': np.array(correlations),
            'L2_DISTANCE': distances
        }
    
    xǁMLPScorerǁcompare_inputs__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMLPScorerǁcompare_inputs__mutmut_1': xǁMLPScorerǁcompare_inputs__mutmut_1, 
        'xǁMLPScorerǁcompare_inputs__mutmut_2': xǁMLPScorerǁcompare_inputs__mutmut_2, 
        'xǁMLPScorerǁcompare_inputs__mutmut_3': xǁMLPScorerǁcompare_inputs__mutmut_3, 
        'xǁMLPScorerǁcompare_inputs__mutmut_4': xǁMLPScorerǁcompare_inputs__mutmut_4, 
        'xǁMLPScorerǁcompare_inputs__mutmut_5': xǁMLPScorerǁcompare_inputs__mutmut_5, 
        'xǁMLPScorerǁcompare_inputs__mutmut_6': xǁMLPScorerǁcompare_inputs__mutmut_6, 
        'xǁMLPScorerǁcompare_inputs__mutmut_7': xǁMLPScorerǁcompare_inputs__mutmut_7, 
        'xǁMLPScorerǁcompare_inputs__mutmut_8': xǁMLPScorerǁcompare_inputs__mutmut_8, 
        'xǁMLPScorerǁcompare_inputs__mutmut_9': xǁMLPScorerǁcompare_inputs__mutmut_9, 
        'xǁMLPScorerǁcompare_inputs__mutmut_10': xǁMLPScorerǁcompare_inputs__mutmut_10, 
        'xǁMLPScorerǁcompare_inputs__mutmut_11': xǁMLPScorerǁcompare_inputs__mutmut_11, 
        'xǁMLPScorerǁcompare_inputs__mutmut_12': xǁMLPScorerǁcompare_inputs__mutmut_12, 
        'xǁMLPScorerǁcompare_inputs__mutmut_13': xǁMLPScorerǁcompare_inputs__mutmut_13, 
        'xǁMLPScorerǁcompare_inputs__mutmut_14': xǁMLPScorerǁcompare_inputs__mutmut_14, 
        'xǁMLPScorerǁcompare_inputs__mutmut_15': xǁMLPScorerǁcompare_inputs__mutmut_15, 
        'xǁMLPScorerǁcompare_inputs__mutmut_16': xǁMLPScorerǁcompare_inputs__mutmut_16, 
        'xǁMLPScorerǁcompare_inputs__mutmut_17': xǁMLPScorerǁcompare_inputs__mutmut_17, 
        'xǁMLPScorerǁcompare_inputs__mutmut_18': xǁMLPScorerǁcompare_inputs__mutmut_18, 
        'xǁMLPScorerǁcompare_inputs__mutmut_19': xǁMLPScorerǁcompare_inputs__mutmut_19, 
        'xǁMLPScorerǁcompare_inputs__mutmut_20': xǁMLPScorerǁcompare_inputs__mutmut_20, 
        'xǁMLPScorerǁcompare_inputs__mutmut_21': xǁMLPScorerǁcompare_inputs__mutmut_21, 
        'xǁMLPScorerǁcompare_inputs__mutmut_22': xǁMLPScorerǁcompare_inputs__mutmut_22, 
        'xǁMLPScorerǁcompare_inputs__mutmut_23': xǁMLPScorerǁcompare_inputs__mutmut_23, 
        'xǁMLPScorerǁcompare_inputs__mutmut_24': xǁMLPScorerǁcompare_inputs__mutmut_24, 
        'xǁMLPScorerǁcompare_inputs__mutmut_25': xǁMLPScorerǁcompare_inputs__mutmut_25, 
        'xǁMLPScorerǁcompare_inputs__mutmut_26': xǁMLPScorerǁcompare_inputs__mutmut_26, 
        'xǁMLPScorerǁcompare_inputs__mutmut_27': xǁMLPScorerǁcompare_inputs__mutmut_27, 
        'xǁMLPScorerǁcompare_inputs__mutmut_28': xǁMLPScorerǁcompare_inputs__mutmut_28, 
        'xǁMLPScorerǁcompare_inputs__mutmut_29': xǁMLPScorerǁcompare_inputs__mutmut_29, 
        'xǁMLPScorerǁcompare_inputs__mutmut_30': xǁMLPScorerǁcompare_inputs__mutmut_30, 
        'xǁMLPScorerǁcompare_inputs__mutmut_31': xǁMLPScorerǁcompare_inputs__mutmut_31, 
        'xǁMLPScorerǁcompare_inputs__mutmut_32': xǁMLPScorerǁcompare_inputs__mutmut_32, 
        'xǁMLPScorerǁcompare_inputs__mutmut_33': xǁMLPScorerǁcompare_inputs__mutmut_33, 
        'xǁMLPScorerǁcompare_inputs__mutmut_34': xǁMLPScorerǁcompare_inputs__mutmut_34, 
        'xǁMLPScorerǁcompare_inputs__mutmut_35': xǁMLPScorerǁcompare_inputs__mutmut_35, 
        'xǁMLPScorerǁcompare_inputs__mutmut_36': xǁMLPScorerǁcompare_inputs__mutmut_36, 
        'xǁMLPScorerǁcompare_inputs__mutmut_37': xǁMLPScorerǁcompare_inputs__mutmut_37, 
        'xǁMLPScorerǁcompare_inputs__mutmut_38': xǁMLPScorerǁcompare_inputs__mutmut_38, 
        'xǁMLPScorerǁcompare_inputs__mutmut_39': xǁMLPScorerǁcompare_inputs__mutmut_39, 
        'xǁMLPScorerǁcompare_inputs__mutmut_40': xǁMLPScorerǁcompare_inputs__mutmut_40, 
        'xǁMLPScorerǁcompare_inputs__mutmut_41': xǁMLPScorerǁcompare_inputs__mutmut_41, 
        'xǁMLPScorerǁcompare_inputs__mutmut_42': xǁMLPScorerǁcompare_inputs__mutmut_42, 
        'xǁMLPScorerǁcompare_inputs__mutmut_43': xǁMLPScorerǁcompare_inputs__mutmut_43, 
        'xǁMLPScorerǁcompare_inputs__mutmut_44': xǁMLPScorerǁcompare_inputs__mutmut_44, 
        'xǁMLPScorerǁcompare_inputs__mutmut_45': xǁMLPScorerǁcompare_inputs__mutmut_45, 
        'xǁMLPScorerǁcompare_inputs__mutmut_46': xǁMLPScorerǁcompare_inputs__mutmut_46, 
        'xǁMLPScorerǁcompare_inputs__mutmut_47': xǁMLPScorerǁcompare_inputs__mutmut_47, 
        'xǁMLPScorerǁcompare_inputs__mutmut_48': xǁMLPScorerǁcompare_inputs__mutmut_48, 
        'xǁMLPScorerǁcompare_inputs__mutmut_49': xǁMLPScorerǁcompare_inputs__mutmut_49, 
        'xǁMLPScorerǁcompare_inputs__mutmut_50': xǁMLPScorerǁcompare_inputs__mutmut_50, 
        'xǁMLPScorerǁcompare_inputs__mutmut_51': xǁMLPScorerǁcompare_inputs__mutmut_51, 
        'xǁMLPScorerǁcompare_inputs__mutmut_52': xǁMLPScorerǁcompare_inputs__mutmut_52, 
        'xǁMLPScorerǁcompare_inputs__mutmut_53': xǁMLPScorerǁcompare_inputs__mutmut_53, 
        'xǁMLPScorerǁcompare_inputs__mutmut_54': xǁMLPScorerǁcompare_inputs__mutmut_54, 
        'xǁMLPScorerǁcompare_inputs__mutmut_55': xǁMLPScorerǁcompare_inputs__mutmut_55, 
        'xǁMLPScorerǁcompare_inputs__mutmut_56': xǁMLPScorerǁcompare_inputs__mutmut_56, 
        'xǁMLPScorerǁcompare_inputs__mutmut_57': xǁMLPScorerǁcompare_inputs__mutmut_57, 
        'xǁMLPScorerǁcompare_inputs__mutmut_58': xǁMLPScorerǁcompare_inputs__mutmut_58, 
        'xǁMLPScorerǁcompare_inputs__mutmut_59': xǁMLPScorerǁcompare_inputs__mutmut_59
    }
    
    def compare_inputs(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMLPScorerǁcompare_inputs__mutmut_orig"), object.__getattribute__(self, "xǁMLPScorerǁcompare_inputs__mutmut_mutants"), args, kwargs, self)
        return result 
    
    compare_inputs.__signature__ = _mutmut_signature(xǁMLPScorerǁcompare_inputs__mutmut_orig)
    xǁMLPScorerǁcompare_inputs__mutmut_orig.__name__ = 'xǁMLPScorerǁcompare_inputs'
