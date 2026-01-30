#!/usr/bin/env python3
"""
Test script to validate RAG module meta tensor handling.
Tests the safe_model_load function and RAG initialization.
"""

import logging
import sys
from pathlib import Path

# Add src to path - fix for scripts/maintenance/ location
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root / "src"))

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
        
        # Test embedding generation
        test_texts = ["hello world", "test embedding"]
        embeddings = provider.encode(test_texts)
        logger.info(f"✓ Generated embeddings shape: {len(embeddings)} x {len(embeddings[0]) if len(embeddings) > 0 else 0}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Embeddings provider test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("RAG Meta Tensor Validation Tests")
    logger.info("=" * 60)
    
    results = []
    
    logger.info("\n[Test 1/2] Testing safe_model_load utility...")
    results.append(("safe_model_load", test_safe_model_load()))
    
    logger.info("\n[Test 2/2] Testing embeddings provider...")
    results.append(("embeddings_provider", test_embeddings_provider()))
    
    logger.info("\n" + "=" * 60)
    logger.info("Test Results Summary")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"  {status}: {name}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())