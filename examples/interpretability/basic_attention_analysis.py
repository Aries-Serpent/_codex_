"""
Basic Attention Analysis Example

This example demonstrates how to use the AttentionScorer to analyze
attention patterns in a transformer model.

Note: This example uses sys.path.insert() for demonstration purposes.
In production code, install the package properly with: pip install -e .
"""

import sys
from pathlib import Path

# Add src to path for development/demo purposes only
# In production, install the package with: pip install -e .
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))

import torch
from transformers import AutoModel, AutoTokenizer
from codex.interpretability import AttentionScorer


def main():
    """Run basic attention analysis."""
    print("Loading model and tokenizer...")
    model_name = "distilbert-base-uncased"
    
    try:
        model = AutoModel.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
    except Exception as e:
        print(f"Error loading model: {e}")
        print("This example requires the transformers library.")
        print("Install with: pip install transformers")
        return
    
    # Create scorer
    print("\nCreating AttentionScorer...")
    scorer = AttentionScorer(model, device='cpu')
    
    # Analyze sample text
    text = "The quick brown fox jumps over the lazy dog"
    print(f"\nAnalyzing text: '{text}'")
    
    inputs = tokenizer(text, return_tensors="pt")
    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
    
    print(f"Tokens: {tokens}")
    
    # Perform analysis
    print("\nPerforming attention analysis...")
    analysis = scorer.analyze_attention(
        input_ids=inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        tokens=tokens
    )
    
    # Display results
    print(f"\nAttention Analysis Results:")
    print(f"  Number of layers: {len(analysis.layer_names)}")
    print(f"  Top 5 Most Important Tokens:")
    top_tokens = scorer.get_top_attended_tokens(analysis, top_k=5)
    for idx, score, token in top_tokens:
        print(f"    {token:15s} (index {idx:2d}): {score:.4f}")
    
    print("\nAnalysis complete!")


if __name__ == "__main__":
    main()
