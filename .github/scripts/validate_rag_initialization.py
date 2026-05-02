#!/usr/bin/env python3
"""
Validate that RAG modules initialize without meta tensor errors.

This script performs a smoke test to verify that SentenceTransformer models
load correctly without hitting PyTorch 2.6+ meta tensor issues.

Run: python .github/scripts/validate_rag_initialization.py

Exit codes:
    0: All checks passed
    1: Validation failed
"""

from __future__ import annotations

import sys


def check_model_tensors(model_name: str = "all-MiniLM-L6-v2") -> bool:
    """
    Verify model initializes without meta tensors.

    Args:
        model_name: Name of the SentenceTransformer model to test

    Returns:
        True if all checks pass, False otherwise
    """
    try:
        from sentence_transformers import SentenceTransformer

        import torch
    except ImportError as e:
        print(f"⚠️  Import failed: {e}")
        print("   Install dependencies: pip install sentence-transformers torch")
        return False

    print(f"Testing model: {model_name}")

    # Initialize model (using default device handling per repository convention)
    # Note: Do NOT pass device parameter directly - per stored memory pattern
    try:
        model = SentenceTransformer(model_name)
        model.eval()
    except Exception as e:
        print(f"❌ Model initialization failed: {e}")
        return False

    # Check for meta tensors
    meta_params = []
    total_params = 0

    for name, param in model.named_parameters():
        total_params += 1
        if param.device.type == "meta":
            meta_params.append(name)

    if meta_params:
        print(f"❌ Found {len(meta_params)} meta tensors:")
        for name in meta_params[:5]:  # Show first 5
            print(f"   - {name}")
        if len(meta_params) > 5:
            print(f"   ... and {len(meta_params) - 5} more")
        return False

    print(f"✅ All {total_params} parameters materialized correctly")

    # Test inference
    try:
        test_text = "This is a test sentence."
        embeddings = model.encode(test_text, convert_to_tensor=True)

        assert embeddings.device.type == "cpu", f"Unexpected device: {embeddings.device}"
        embeddings_has_nan = torch.isnan(embeddings).any()
        assert not embeddings_has_nan, "NaN detected in embeddings"

        print(f"✅ Inference successful: {embeddings.shape}")
        return True

    except Exception as e:
        print(f"❌ Inference failed: {e}")
        return False


def main() -> int:
    """Run all validation checks."""
    print("=" * 60)
    print("RAG Module Meta Tensor Validation")
    print("=" * 60)

    success = check_model_tensors()

    if success:
        print("\n✅ All checks passed - RAG module is healthy")
        return 0
    else:
        print("\n❌ Validation failed - meta tensor issues detected")
        return 1


if __name__ == "__main__":
    sys.exit(main())
