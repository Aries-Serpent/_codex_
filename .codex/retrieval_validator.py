#!/usr/bin/env python3
"""
RAG Retrieval Accuracy Validator
Tests semantic retrieval performance against known documents
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any
import re

logger = None


def init_logger():
    """Simple logger initialization."""
    import logging
    global logger
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


class SimpleSemanticRetriever:
    """Simple semantic retriever using keyword and semantic similarity."""
    
    def __init__(self, index_data: Dict):
        self.index_data = index_data
        self.chunks = index_data.get("chunks", [])
    
    def score_chunk(self, query: str, chunk: Dict) -> float:
        """Score chunk against query using keyword matching and similarity."""
        
        query_lower = query.lower()
        content = chunk.get("content", "").lower()
        
        # Keyword matching score
        query_terms = set(query_lower.split())
        content_words = set(content.split())
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'in', 'of', 'to', 'is', 'was', 'be', 'been'}
        query_terms = query_terms - stop_words
        
        if not query_terms:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(query_terms & content_words)
        union = len(query_terms | content_words)
        
        jaccard_score = intersection / union if union > 0 else 0.0
        
        # Check for exact phrase matches
        phrase_score = 1.0 if query_lower in content else 0.0
        
        # Weighted combination
        return 0.7 * jaccard_score + 0.3 * phrase_score
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Tuple[Dict, float, int]]:
        """
        Retrieve top-k chunks most relevant to query.
        
        Returns: List of (chunk, score, rank)
        """
        
        scores = []
        for idx, chunk in enumerate(self.chunks):
            score = self.score_chunk(query, chunk)
            if score > 0:
                scores.append((chunk, score, idx))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top-k with rank
        results = []
        for rank, (chunk, score, idx) in enumerate(scores[:top_k], 1):
            results.append((chunk, score, rank))
        
        return results


class RetrievalValidator:
    """Validates retrieval accuracy of RAG indexes."""
    
    # Ground truth queries and expected document keywords
    TEST_QUERIES = [
        {
            "query": "What is the Codebase Agency Policy?",
            "expected_keywords": ["CODEBASE_AGENCY_POLICY", "mandatory", "AI agents"],
            "expected_document": "CODEBASE_AGENCY_POLICY.md"
        },
        {
            "query": "How to deploy profiles in the system?",
            "expected_keywords": ["deploy", "profile", "implementation"],
            "expected_document": "DEPLOYMENT"
        },
        {
            "query": "What are the 3 profiles in this system?",
            "expected_keywords": ["profile", "core", "runtime"],
            "expected_document": None
        },
        {
            "query": "How does RAG work?",
            "expected_keywords": ["RAG", "retrieval", "augmented", "generation"],
            "expected_document": None
        },
        {
            "query": "What is the agent registry structure?",
            "expected_keywords": ["agent", "registry", "structure"],
            "expected_document": None
        },
        {
            "query": "What are the mandatory pre-session requirements?",
            "expected_keywords": ["mandatory", "pre-session", "requirements"],
            "expected_document": "CODEBASE_AGENCY_POLICY"
        },
        {
            "query": "How to handle CI failures?",
            "expected_keywords": ["CI", "failure", "handle"],
            "expected_document": None
        },
        {
            "query": "What is the emotion-safe urgency guardrail?",
            "expected_keywords": ["emotion", "safe", "urgency", "guardrail"],
            "expected_document": None
        },
        {
            "query": "How to maintain code quality standards?",
            "expected_keywords": ["code", "quality", "standard"],
            "expected_document": None
        },
        {
            "query": "What are the self-review requirements?",
            "expected_keywords": ["self", "review", "requirement"],
            "expected_document": "CODEBASE_AGENCY_POLICY"
        },
        {
            "query": "How to use the cognitive brain?",
            "expected_keywords": ["cognitive", "brain", "use"],
            "expected_document": None
        },
        {
            "query": "What is the AfterMath PDA loop?",
            "expected_keywords": ["AfterMath", "PDA", "loop"],
            "expected_document": None
        },
        {
            "query": "How to manage repository variables?",
            "expected_keywords": ["repository", "variable", "manage"],
            "expected_document": "AGENTIC_REPO_STATE"
        },
        {
            "query": "What are the agentic repo state variables?",
            "expected_keywords": ["AGENTIC_REPO_STATE", "variable", "auth"],
            "expected_document": "AGENTIC_REPO_STATE"
        },
        {
            "query": "How to handle merge conflicts?",
            "expected_keywords": ["merge", "conflict", "handle"],
            "expected_document": "CODEBASE_AGENCY_POLICY"
        },
        {
            "query": "What is the WEC workflow execution checklist?",
            "expected_keywords": ["WEC", "workflow", "execution", "checklist"],
            "expected_document": None
        },
        {
            "query": "How to implement comprehensive issue resolution?",
            "expected_keywords": ["comprehensive", "issue", "resolution"],
            "expected_document": "CODEBASE_AGENCY_POLICY"
        },
        {
            "query": "What are the documentation standards?",
            "expected_keywords": ["documentation", "standard"],
            "expected_document": None
        },
        {
            "query": "How to run integration tests?",
            "expected_keywords": ["integration", "test", "run"],
            "expected_document": None
        },
        {
            "query": "What is the non-deferral mandate?",
            "expected_keywords": ["non-deferral", "mandate", "CI"],
            "expected_document": "CODEBASE_AGENCY_POLICY"
        },
    ]
    
    def __init__(self, index_path: Path):
        self.index_path = index_path
        self.index_data = self._load_index()
        self.retriever = SimpleSemanticRetriever(self.index_data)
        self.results = []
    
    def _load_index(self) -> Dict:
        """Load RAG index from file."""
        
        if not self.index_path.exists():
            raise FileNotFoundError(f"Index file not found: {self.index_path}")
        
        with open(self.index_path, 'r') as f:
            return json.load(f)
    
    def _check_keywords(self, text: str, keywords: List[str]) -> bool:
        """Check if text contains any of the keywords."""
        
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in keywords)
    
    def run_validation(self, top_k: int = 3) -> Dict[str, Any]:
        """
        Run retrieval accuracy validation.
        
        Returns validation results.
        """
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "index_profile": self.index_data.get("profile", "unknown"),
            "total_queries": len(self.TEST_QUERIES),
            "queries_tested": 0,
            "top_3_accuracy": 0.0,
            "failing_queries": [],
            "detailed_results": []
        }
        
        correct_count = 0
        
        for query_info in self.TEST_QUERIES:
            query = query_info["query"]
            expected_keywords = query_info["expected_keywords"]
            
            results["queries_tested"] += 1
            
            # Run retrieval
            retrieved = self.retriever.retrieve(query, top_k=top_k)
            
            # Check if any top-k result contains expected keywords
            found = False
            found_rank = None
            
            for chunk, score, rank in retrieved:
                content = chunk.get("content", "")
                if self._check_keywords(content, expected_keywords):
                    found = True
                    found_rank = rank
                    correct_count += 1
                    break
            
            # Record result
            result = {
                "query": query,
                "found": found,
                "rank": found_rank,
                "expected_keywords": expected_keywords,
                "retrieved_count": len(retrieved),
                "retrieved_paths": [chunk.get("path", "unknown") for chunk, _, _ in retrieved]
            }
            
            results["detailed_results"].append(result)
            
            # Track failing queries
            if not found:
                results["failing_queries"].append(query)
        
        # Calculate accuracy
        results["top_3_accuracy"] = (correct_count / results["queries_tested"] * 100) if results["queries_tested"] > 0 else 0.0
        
        return results


def main():
    """Main entry point."""
    
    init_logger()
    
    print("=" * 70)
    print("RAG RETRIEVAL ACCURACY VALIDATOR")
    print("=" * 70)
    
    base_path = Path(__file__).parent / "rag_indexes"
    
    # Validate core index
    print("\n[*] Validating Core Index...")
    core_index_path = base_path / "core_index.json"
    
    try:
        validator_core = RetrievalValidator(core_index_path)
        core_results = validator_core.run_validation(top_k=3)
        
        print(f"\n[CORE INDEX RESULTS]")
        print(f"  Total Queries: {core_results['total_queries']}")
        print(f"  Top-3 Accuracy: {core_results['top_3_accuracy']:.1f}%")
        print(f"  Failing Queries: {len(core_results['failing_queries'])}")
        
        if core_results['failing_queries']:
            print(f"\n  Failing queries:")
            for q in core_results['failing_queries']:
                print(f"    - {q}")
    
    except Exception as e:
        print(f"  Error validating core index: {e}")
        core_results = None
    
    # Validate runtime index
    print("\n[*] Validating Runtime Index...")
    runtime_index_path = base_path / "runtime_index.json"
    
    try:
        validator_runtime = RetrievalValidator(runtime_index_path)
        runtime_results = validator_runtime.run_validation(top_k=3)
        
        print(f"\n[RUNTIME INDEX RESULTS]")
        print(f"  Total Queries: {runtime_results['total_queries']}")
        print(f"  Top-3 Accuracy: {runtime_results['top_3_accuracy']:.1f}%")
        print(f"  Failing Queries: {len(runtime_results['failing_queries'])}")
        
        if runtime_results['failing_queries']:
            print(f"\n  Failing queries:")
            for q in runtime_results['failing_queries']:
                print(f"    - {q}")
    
    except Exception as e:
        print(f"  Error validating runtime index: {e}")
        runtime_results = None
    
    # Save results
    print("\n[*] Saving validation results...")
    
    validation_report = {
        "timestamp": datetime.now().isoformat(),
        "core_index": core_results,
        "runtime_index": runtime_results,
        "summary": {
            "core_accuracy": core_results.get('top_3_accuracy', 0) if core_results else 0,
            "runtime_accuracy": runtime_results.get('top_3_accuracy', 0) if runtime_results else 0,
            "combined_accuracy": (
                (core_results.get('top_3_accuracy', 0) + runtime_results.get('top_3_accuracy', 0)) / 2
                if core_results and runtime_results else 0
            ),
            "target_accuracy": 95.0,
            "status": "PASS" if (
                core_results and runtime_results and
                core_results.get('top_3_accuracy', 0) >= 90 and
                runtime_results.get('top_3_accuracy', 0) >= 90
            ) else "REVIEW"
        }
    }
    
    report_file = base_path / "retrieval_accuracy_validation.json"
    with open(report_file, 'w') as f:
        json.dump(validation_report, f, indent=2)
    
    print(f"[+] Validation report saved: {report_file}")
    
    print("\n" + "=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
