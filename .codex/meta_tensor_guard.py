#!/usr/bin/env python3
"""
Meta-Tensor Guard Implementation for RAG Module
Prevents tensor materialization errors and validates embeddings
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MetaTensorGuard:
    """Guards against tensor materialization errors in RAG embeddings."""
    
    def __init__(self, guard_log_file: Optional[Path] = None):
        self.guard_log_file = guard_log_file or Path(__file__).parent / "guard_activations.jsonl"
        self.activations = []
        self.stats = {
            "total_guards": 0,
            "tensor_shape_validations": 0,
            "device_mismatch_detections": 0,
            "fallback_activations": 0,
            "timestamp": datetime.now().isoformat(),
            "errors": []
        }
    
    def validate_embeddings_shape(self, embeddings: Any, expected_dims: int = 2) -> Tuple[bool, Optional[str]]:
        """
        Validate embedding tensor shape.
        
        Expected: 2D tensor of shape (batch_size, embedding_dim)
        """
        
        self.stats["tensor_shape_validations"] += 1
        
        try:
            # Check if it's a tensor-like object
            if not hasattr(embeddings, 'shape') and not hasattr(embeddings, '__len__'):
                return False, "Embeddings object has no shape or length attribute"
            
            # Get shape
            if hasattr(embeddings, 'shape'):
                shape = embeddings.shape
            else:
                shape = (len(embeddings),) if embeddings else (0,)
            
            # Validate dimensions
            if len(shape) != expected_dims:
                msg = f"Expected {expected_dims}D tensor, got {len(shape)}D with shape {shape}"
                self._log_activation("shape_mismatch", msg, {"shape": str(shape), "expected_dims": expected_dims})
                return False, msg
            
            # Validate non-zero batch size
            if shape[0] == 0:
                msg = f"Batch size is 0 (shape: {shape})"
                self._log_activation("empty_batch", msg, {"shape": str(shape)})
                return False, msg
            
            return True, None
            
        except Exception as e:
            msg = f"Error during shape validation: {e}"
            self._log_activation("validation_error", msg, {"error": str(e)})
            return False, msg
    
    def validate_embeddings_dtype(self, embeddings: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate embedding tensor dtype.
        
        Expected: float32 or float64
        """
        
        try:
            if not hasattr(embeddings, 'dtype'):
                return True, None  # Can't validate dtype, assume OK
            
            dtype_str = str(embeddings.dtype).lower()
            
            # Check for valid float types
            if 'float' not in dtype_str:
                msg = f"Invalid dtype: {embeddings.dtype}. Expected float32 or float64."
                self._log_activation("dtype_error", msg, {"dtype": str(embeddings.dtype)})
                return False, msg
            
            return True, None
            
        except Exception as e:
            msg = f"Error during dtype validation: {e}"
            self._log_activation("dtype_validation_error", msg, {"error": str(e)})
            return False, msg
    
    def detect_device_mismatch(self, embeddings: Any, expected_device: str = "cpu") -> Optional[Dict[str, Any]]:
        """
        Detect GPU/CPU device mismatches.
        
        Logs warning if device mismatch is detected.
        """
        
        self.stats["device_mismatch_detections"] += 1
        
        try:
            if not hasattr(embeddings, 'device'):
                return None  # Can't determine device
            
            actual_device = str(embeddings.device).lower()
            
            # Parse device strings
            if 'cuda' in actual_device and expected_device == 'cpu':
                info = {
                    "type": "device_mismatch",
                    "actual": actual_device,
                    "expected": expected_device,
                    "severity": "warning"
                }
                self._log_activation("device_mismatch", f"GPU tensor on CPU environment", info)
                logger.warning(f"GPU tensor detected but CPU expected: {actual_device}")
                return info
            elif 'cpu' in actual_device and expected_device in ['cuda', 'gpu']:
                info = {
                    "type": "device_mismatch",
                    "actual": actual_device,
                    "expected": expected_device,
                    "severity": "warning"
                }
                self._log_activation("device_mismatch", f"CPU tensor on GPU environment", info)
                logger.warning(f"CPU tensor detected but GPU expected: {actual_device}")
                return info
            
            return None  # No mismatch
            
        except Exception as e:
            logger.warning(f"Error during device mismatch detection: {e}")
            return None
    
    def validate_all_guards(self, embeddings: Any, expected_device: str = "cpu") -> Tuple[bool, List[str]]:
        """
        Run all guard validations on embeddings.
        
        Returns: (is_valid, error_messages)
        """
        
        self.stats["total_guards"] += 1
        errors = []
        
        # Shape validation
        shape_valid, shape_msg = self.validate_embeddings_shape(embeddings)
        if not shape_valid:
            errors.append(shape_msg)
        
        # Dtype validation
        dtype_valid, dtype_msg = self.validate_embeddings_dtype(embeddings)
        if not dtype_valid:
            errors.append(dtype_msg)
        
        # Device mismatch detection
        device_mismatch = self.detect_device_mismatch(embeddings, expected_device)
        if device_mismatch:
            errors.append(f"Device mismatch: {device_mismatch}")
        
        if errors:
            self.stats["errors"].extend(errors)
        
        return len(errors) == 0, errors
    
    def fallback_to_lexical_search(self, query: str, documents: List[Dict]) -> List[Dict]:
        """
        Fallback to lexical (keyword) search when embeddings fail.
        
        Simple keyword matching as fallback.
        """
        
        self.stats["fallback_activations"] += 1
        self._log_activation("fallback_triggered", f"Falling back to lexical search for: {query[:50]}...", {
            "query_length": len(query),
            "document_count": len(documents)
        })
        
        logger.info(f"Activating fallback lexical search for query: {query[:50]}...")
        
        # Simple keyword matching
        query_words = set(query.lower().split())
        scored_docs = []
        
        for doc in documents:
            content = doc.get("content", "").lower()
            matches = sum(1 for word in query_words if word in content)
            if matches > 0:
                scored_docs.append({
                    "doc": doc,
                    "score": matches / len(query_words),
                    "method": "lexical_fallback"
                })
        
        # Sort by score
        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        
        return [item["doc"] for item in scored_docs[:3]]  # Return top 3
    
    def _log_activation(self, activation_type: str, message: str, context: Optional[Dict] = None) -> None:
        """Log a guard activation."""
        
        activation = {
            "timestamp": datetime.now().isoformat(),
            "type": activation_type,
            "message": message,
            "context": context or {}
        }
        
        self.activations.append(activation)
        logger.info(f"Guard activation: {activation_type} - {message}")
    
    def save_guard_log(self) -> None:
        """Save guard activations to log file."""
        
        try:
            with open(self.guard_log_file, 'a') as f:
                for activation in self.activations:
                    f.write(json.dumps(activation) + "\n")
            
            logger.info(f"Guard log saved to {self.guard_log_file}")
        except Exception as e:
            logger.error(f"Error saving guard log: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get guard statistics."""
        return {
            **self.stats,
            "activation_count": len(self.activations),
            "activations": self.activations
        }


class EmbeddingValidator:
    """Validates embedding indexes for consistency and correctness."""
    
    def __init__(self):
        self.guard = MetaTensorGuard()
    
    def validate_index(self, index_path: Path) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate a RAG index file for correctness.
        
        Checks:
        - File exists and is readable
        - Valid JSON structure
        - Chunks have required fields
        - Metadata is present
        """
        
        results = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "chunks_validated": 0,
            "issues": []
        }
        
        try:
            # Check file exists
            if not index_path.exists():
                results["errors"].append(f"Index file not found: {index_path}")
                return False, results
            
            # Read and parse JSON
            with open(index_path, 'r') as f:
                index_data = json.load(f)
            
            # Validate structure
            if "chunks" not in index_data:
                results["errors"].append("Index missing 'chunks' field")
                return False, results
            
            if "metadata" not in index_data:
                results["warnings"].append("Index missing 'metadata' field")
            
            # Validate chunks
            chunks = index_data.get("chunks", [])
            required_fields = ["path", "content", "hash"]
            
            for i, chunk in enumerate(chunks):
                results["chunks_validated"] += 1
                
                # Check required fields
                for field in required_fields:
                    if field not in chunk:
                        results["issues"].append(f"Chunk {i} missing field: {field}")
                
                # Check content is non-empty
                if not chunk.get("content", "").strip():
                    results["issues"].append(f"Chunk {i} has empty content")
            
            # Summary
            if not results["errors"]:
                results["valid"] = True
            
            return results["valid"], results
            
        except json.JSONDecodeError as e:
            results["errors"].append(f"Invalid JSON: {e}")
            return False, results
        except Exception as e:
            results["errors"].append(f"Error validating index: {e}")
            return False, results


def main():
    """Demo the meta-tensor guard."""
    
    print("=" * 70)
    print("META-TENSOR GUARD SYSTEM")
    print("=" * 70)
    
    guard = MetaTensorGuard()
    
    # Simulate guard activation scenarios
    print("\n[*] Testing guard activations...")
    
    # Scenario 1: Valid embeddings (mock)
    print("\n[1] Valid embeddings (mock simulation)")
    class MockEmbeddings:
        def __init__(self):
            self.shape = (10, 384)
            self.dtype = "float32"
            self.device = "cpu"
    
    embeddings = MockEmbeddings()
    valid, errors = guard.validate_all_guards(embeddings, "cpu")
    print(f"    Valid: {valid}, Errors: {errors}")
    
    # Scenario 2: Invalid shape
    print("\n[2] Invalid tensor shape (1D instead of 2D)")
    class InvalidShape:
        def __init__(self):
            self.shape = (384,)  # 1D
            self.dtype = "float32"
            self.device = "cpu"
    
    embeddings = InvalidShape()
    valid, errors = guard.validate_all_guards(embeddings, "cpu")
    print(f"    Valid: {valid}, Errors: {errors}")
    
    # Scenario 3: Device mismatch
    print("\n[3] Device mismatch (GPU tensor)")
    class GPUEmbeddings:
        def __init__(self):
            self.shape = (10, 384)
            self.dtype = "float32"
            self.device = "cuda:0"
    
    embeddings = GPUEmbeddings()
    valid, errors = guard.validate_all_guards(embeddings, "cpu")
    print(f"    Valid: {valid}, Errors: {errors}")
    
    # Save stats
    print("\n[*] Guard Statistics:")
    stats = guard.get_stats()
    print(json.dumps({
        "total_guards": stats["total_guards"],
        "tensor_shape_validations": stats["tensor_shape_validations"],
        "device_mismatch_detections": stats["device_mismatch_detections"],
        "fallback_activations": stats["fallback_activations"],
        "error_count": len(stats["errors"]),
        "activation_count": stats["activation_count"]
    }, indent=2))
    
    # Test index validation
    print("\n[*] Testing index validation...")
    validator = EmbeddingValidator()
    index_path = Path(__file__).parent / "rag_indexes" / "core_index.json"
    
    if index_path.exists():
        valid, results = validator.validate_index(index_path)
        print(f"    Valid: {valid}")
        print(f"    Chunks validated: {results.get('chunks_validated', 0)}")
        print(f"    Issues: {len(results.get('issues', []))}")
    
    print("\n" + "=" * 70)
    print("GUARD SYSTEM READY")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
