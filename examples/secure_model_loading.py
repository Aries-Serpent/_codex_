"""
Secure PyTorch Model Loading Example

This example demonstrates how to safely load PyTorch models using the
safe_torch_loader utility to prevent RCE vulnerabilities (CVE-2024-XXXXX).

SECURITY BEST PRACTICES:
1. Always use weights_only=True when loading models
2. Only load models from trusted sources
3. When saving models for distribution, save state_dict (not full model objects)
4. Use torch.save() only for models you trust completely
5. For production, consider using safetensors format instead of pickle

Example of safe save/load pattern:
    # SAFE: Save only the state dictionary
    torch.save(model.state_dict(), 'model.pth')
    
    # SAFE: Load with weights_only=True
    model = MyModel()
    state_dict = torch.load('model.pth', weights_only=True)
    model.load_state_dict(state_dict)
    
    # UNSAFE: Saving/loading full model objects
    torch.save(model, 'model.pth')  # Can include arbitrary Python objects
    model = torch.load('model.pth')  # Vulnerable to RCE attacks
"""
import logging
from pathlib import Path
from typing import Optional

import torch
import torch.nn as nn

# Import security utilities
from utils.safe_torch_loader import safe_load
from utils.torch_resource_manager import torch_resource_guard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecureModelLoader:
    """
    Production-ready model loader with security best practices.
    
    Features:
    - Secure model loading with weights_only=True
    - Automatic resource cleanup
    - Error handling and logging
    - Device management
    """
    
    def __init__(self, model_class: type[nn.Module], device: str = "cpu"):
        """
        Initialize secure model loader.
        
        Args:
            model_class: PyTorch model class to instantiate
            device: Device to load model on ('cpu' or 'cuda')
        """
        self.model_class = model_class
        self.device = device
        self.model: Optional[nn.Module] = None
    
    def load_model(self, checkpoint_path: str) -> nn.Module:
        """
        Securely load model from checkpoint.
        
        Args:
            checkpoint_path: Path to model checkpoint file
        
        Returns:
            Loaded model instance
        
        Raises:
            FileNotFoundError: If checkpoint doesn't exist
            RuntimeError: If loading fails
        """
        checkpoint_path = Path(checkpoint_path)
        
        logger.info(f"Loading model from {checkpoint_path}")
        
        # Use resource guard for automatic cleanup
        with torch_resource_guard():
            # Load checkpoint securely
            checkpoint = safe_load(
                str(checkpoint_path),
                map_location=self.device,
            )
            
            # Initialize model
            self.model = self.model_class()
            
            # Load state dict
            if isinstance(checkpoint, dict):
                # Handle checkpoint with metadata
                if "model_state_dict" in checkpoint:
                    self.model.load_state_dict(checkpoint["model_state_dict"])
                elif "state_dict" in checkpoint:
                    self.model.load_state_dict(checkpoint["state_dict"])
                else:
                    # Assume checkpoint is the state dict itself
                    self.model.load_state_dict(checkpoint)
            else:
                # Direct state dict
                self.model.load_state_dict(checkpoint)
            
            # Move to device and set to eval mode
            self.model = self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"✅ Model loaded successfully on {self.device}")
            
            return self.model
    
    def predict(self, input_data: torch.Tensor) -> torch.Tensor:
        """
        Run inference with loaded model.
        
        Args:
            input_data: Input tensor
        
        Returns:
            Model predictions
        
        Raises:
            RuntimeError: If model not loaded
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        with torch_resource_guard():
            with torch.no_grad():
                input_data = input_data.to(self.device)
                output = self.model(input_data)
        
        return output


# Example usage
def main():
    """Example usage of secure model loader."""
    
    # Define a simple model
    class SimpleModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.fc = nn.Linear(10, 5)
        
        def forward(self, x):
            return self.fc(x)
    
    # Create and save a test model
    test_model = SimpleModel()
    test_checkpoint_path = "/tmp/test_secure_model.pth"
    
    logger.info("Saving test model...")
    # SECURITY NOTE: We save the state_dict (not the full model object)
    # This is compatible with weights_only=True loading and is the recommended
    # practice for distributing models. Only save full model objects for
    # trusted, internal use cases.
    torch.save(test_model.state_dict(), test_checkpoint_path)
    
    # Load model securely
    logger.info("Loading model securely...")
    loader = SecureModelLoader(SimpleModel, device="cpu")
    loaded_model = loader.load_model(test_checkpoint_path)
    
    # Run inference
    logger.info("Running inference...")
    test_input = torch.randn(1, 10)
    output = loader.predict(test_input)
    
    logger.info(f"✅ Inference successful! Output shape: {output.shape}")
    
    # Cleanup
    Path(test_checkpoint_path).unlink()
    logger.info("✅ Test completed successfully")


if __name__ == "__main__":
    main()
