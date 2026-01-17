#!/usr/bin/env python3
"""
TF-IDF Code Analyzer Tool

Analyzes code using TF-IDF embeddings for semantic understanding.
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from codex.rag.embeddings import TfidfEmbeddingProvider


def analyze_file(file_path: str, tfidf: bool = True):
    """Analyze a file using TF-IDF embeddings."""
    path = Path(file_path)
    
    if not path.exists():
        print(f"Error: File not found: {file_path}")
        return 1
    
    # Read file
    with open(path) as f:
        code = f.read()
    
    # Create TF-IDF provider
    provider = TfidfEmbeddingProvider()
    
    # Analyze
    embeddings = provider.encode([code])
    
    print(f"✓ Analyzed: {file_path}")
    print(f"  Embedding shape: {embeddings.shape}")
    print(f"  Dimension: {provider.get_dimension()}")
    
    return 0


def main():
    parser = argparse.ArgumentParser(description="Analyze code with TF-IDF")
    parser.add_argument("file", help="File to analyze")
    parser.add_argument("--tfidf", action="store_true", help="Use TF-IDF analysis")
    
    args = parser.parse_args()
    return analyze_file(args.file, args.tfidf)


if __name__ == "__main__":
    sys.exit(main())
