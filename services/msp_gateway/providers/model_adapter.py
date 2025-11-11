"""
Model Adapter Interface
Provides abstraction for local model inference
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ModelAdapter(ABC):
    """Abstract base class for model adapters"""
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text from prompt
        
        Returns:
            Dictionary with 'text', 'tokens_used', and 'model' keys
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, str]:
        """Get model information"""
        pass


class LocalTransformersAdapter(ModelAdapter):
    """Adapter for local Hugging Face Transformers models"""
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        device: str = "cpu",
        max_length: int = 512,
    ):
        self.model_path = model_path or "gpt2"  # Default to GPT-2 for testing
        self.device = device
        self.max_length = max_length
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self):
        """Load model and tokenizer"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            logger.info(f"Loading model: {self.model_path}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                device_map=self.device if self.device != "cpu" else None,
            )
            
            if self.device == "cpu":
                self.model = self.model.to("cpu")
            
            # Set pad token if not set
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text from prompt"""
        if not self.model or not self.tokenizer:
            raise RuntimeError("Model not loaded")
        
        # Tokenize input
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True)
        
        if self.device == "cpu":
            inputs = {k: v.to("cpu") for k, v in inputs.items()}
        
        # Generate
        import torch
        with torch.no_grad():
            outputs = self.model.generate(
                inputs["input_ids"],
                attention_mask=inputs.get("attention_mask"),
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=temperature > 0,
                pad_token_id=self.tokenizer.pad_token_id,
                **kwargs
            )
        
        # Decode
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Remove prompt from output
        if generated_text.startswith(prompt):
            generated_text = generated_text[len(prompt):].strip()
        
        # Count tokens
        output_tokens = len(outputs[0])
        input_tokens = len(inputs["input_ids"][0])
        
        return {
            "text": generated_text,
            "tokens_used": output_tokens,
            "input_tokens": input_tokens,
            "model": self.model_path,
        }
    
    def get_model_info(self) -> Dict[str, str]:
        """Get model information"""
        return {
            "model_path": self.model_path,
            "device": self.device,
            "backend": "transformers",
        }


class MockModelAdapter(ModelAdapter):
    """Mock adapter for testing without actual model"""
    
    def __init__(self):
        logger.info("Using mock model adapter (no actual inference)")
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate mock response"""
        mock_response = (
            f"This is a mock response to your query. "
            f"In production, a real model would generate text based on: '{prompt[:50]}...'"
        )
        
        return {
            "text": mock_response,
            "tokens_used": len(mock_response.split()),
            "input_tokens": len(prompt.split()),
            "model": "mock-model",
        }
    
    def get_model_info(self) -> Dict[str, str]:
        """Get model information"""
        return {
            "model_path": "mock",
            "device": "cpu",
            "backend": "mock",
        }


def create_model_adapter(
    backend: str = "mock",
    model_path: Optional[str] = None,
    device: str = "cpu",
    **kwargs
) -> ModelAdapter:
    """Factory function to create model adapter
    
    Args:
        backend: Backend type ('transformers', 'mock')
        model_path: Path to model weights
        device: Device for inference
        **kwargs: Additional arguments
    
    Returns:
        ModelAdapter instance
    """
    if backend == "transformers" or backend == "local":
        return LocalTransformersAdapter(model_path, device, **kwargs)
    elif backend == "mock":
        return MockModelAdapter()
    else:
        raise ValueError(f"Unknown backend: {backend}")
