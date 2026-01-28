#!/usr/bin/env python3
"""
Test script to validate RAG module meta tensor handling.
Tests the safe_model_load function and RAG initialization.
"""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_safe_model_load():
    """Test safe_model_load utility"""
    try:
        from codex.rag.utils import safe_model_load
        logger.info("✓ safe_model_load imported successfully")
        
        # Test with a mock model object
        class MockModel:
            def __init__(self):
                self.device = None
            
            def to(self, device):
                self.device = device
                return self
            
            def eval(self):
                return self
        
        mock_model = MockModel()
        result = safe_model_load(mock_model, device="cpu")
        
        assert result is not None
        logger.info("✓ safe_model_load works with mock model")
        return True
        
    except Exception as e:
        logger.error(f"✗ safe_model_load test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_embeddings_provider():
    """Test embeddings provider with TF-IDF fallback"""
    try:
        from codex.rag.embeddings import create_embedding_provider
        logger.info("✓ create_embedding_provider imported successfully")
        
        # Use TF-IDF provider (no network required)
        provider = create_embedding_provider(provider_type="tfidf", use_cache=False)
        logger.info(f"✓ Created embedding provider: {provider.__class__.__name__}")
        
InternalError: Failed to generate text due to: An error occurred (ThrottlingException) when calling the InvokeModel operation (reached max retries: 0): Too many requests, please wait before trying again.