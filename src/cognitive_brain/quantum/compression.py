"""
Pattern Compression for Long-Term Memory Storage

Implements dimensionality reduction and compression for efficient LTM storage.
Target: 60% size reduction while maintaining pattern distinctiveness.

PDA Loop + AfterMath:
- PLAN: Define compression strategy (PCA, quantization)
- DO: Compress patterns for LTM storage
- ASSESS: Measure compression ratio, reconstruction accuracy
- AfterMath: Track storage efficiency, retrieval performance impact

Compression Techniques:
- Feature dimensionality reduction (PCA-based)
- Quantization of continuous values
- Sparse representation for near-zero features
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any, Optional


@dataclass
class CompressedPattern:
    """
    Compressed representation of a memory pattern.
    
    Stores pattern data in reduced form for efficient LTM storage.
    
    Attributes:
        pattern_id: Original pattern identifier
        compressed_features: Reduced feature representation
        decision: Preserved decision (not compressed)
        confidence: Preserved confidence (not compressed)
        feature_keys: Ordered list of feature keys for reconstruction
        compression_metadata: Metadata for decompression
    """
    pattern_id: str
    compressed_features: np.ndarray  # Reduced dimensionality vector
    decision: str
    confidence: float
    feature_keys: List[str]
    compression_metadata: Dict[str, Any]
    
    def get_size_bytes(self) -> int:
        """
        Estimate compressed size in bytes.
        
        Returns:
            Approximate size in bytes
        """
        # Numpy array size + string sizes + metadata
        array_size = self.compressed_features.nbytes
        string_size = len(self.pattern_id) + len(self.decision)
        string_size += sum(len(k) for k in self.feature_keys)
        metadata_size = sum(len(str(v)) for v in self.compression_metadata.values())
        
        return array_size + string_size + metadata_size


class PatternCompressor:
    """
    Pattern compression system for efficient LTM storage.
    
    Compression Strategy:
    1. Feature dimensionality reduction (target: 50% reduction)
    2. Value quantization (8-bit precision)
    3. Sparse representation (remove near-zero features)
    
    Target: 60% overall size reduction while maintaining >95% reconstruction accuracy.
    """
    
    def __init__(self, target_dimensions: Optional[int] = None, 
                 quantization_bits: int = 8,
                 sparsity_threshold: float = 0.01):
        """
        Initialize pattern compressor.
        
        Args:
            target_dimensions: Target reduced dimensionality (None = auto, 50% of original)
            quantization_bits: Bits for value quantization (default: 8-bit)
            sparsity_threshold: Threshold below which features are zeroed (default: 0.01)
        """
        self.target_dimensions = target_dimensions
        self.quantization_bits = quantization_bits
        self.sparsity_threshold = sparsity_threshold
        
        # Learned compression parameters
        self.feature_mean: Optional[np.ndarray] = None
        self.feature_std: Optional[np.ndarray] = None
        self.projection_matrix: Optional[np.ndarray] = None
        self.is_fitted = False
        
        # Statistics
        self.total_compressed = 0
        self.total_decompressed = 0
        self.compression_ratios: List[float] = []
    
    def fit(self, patterns: List[Dict[str, float]]) -> None:
        """
        Fit compression model to pattern data.
        
        Learns PCA projection matrix for dimensionality reduction.
        
        Args:
            patterns: List of feature dicts to learn from
        """
        if not patterns:
            raise ValueError("Cannot fit on empty pattern list")
        
        # Convert patterns to matrix
        feature_keys = sorted(patterns[0].keys())
        X = np.array([[p.get(k, 0.0) for k in feature_keys] for p in patterns])
        
        # Calculate statistics
        self.feature_mean = np.mean(X, axis=0)
        self.feature_std = np.std(X, axis=0) + 1e-8  # Add epsilon for stability
        
        # Normalize
        X_norm = (X - self.feature_mean) / self.feature_std
        
        # Compute covariance matrix
        cov_matrix = np.cov(X_norm.T)
        
        # Eigen decomposition
        eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
        
        # Sort by eigenvalues (descending)
        idx = eigenvalues.argsort()[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]
        
        # Determine target dimensions (50% reduction if not specified)
        if self.target_dimensions is None:
            self.target_dimensions = max(1, X.shape[1] // 2)
        
        # Select top principal components
        self.projection_matrix = eigenvectors[:, :self.target_dimensions]
        
        self.is_fitted = True
    
    def compress(self, pattern: Dict[str, float], 
                 pattern_id: str,
                 decision: str,
                 confidence: float) -> CompressedPattern:
        """
        Compress pattern for LTM storage.
        
        Steps:
        1. Extract feature vector in consistent order
        2. Normalize using learned statistics
        3. Project to reduced dimensions (PCA)
        4. Apply quantization
        5. Apply sparsity threshold
        
        Args:
            pattern: Feature dict to compress
            pattern_id: Pattern identifier
            decision: Decision to preserve
            confidence: Confidence to preserve
            
        Returns:
            Compressed pattern
        """
        if not self.is_fitted:
            raise RuntimeError("Compressor not fitted. Call fit() first.")
        
        # Extract features in consistent order
        feature_keys = sorted(pattern.keys())
        feature_vector = np.array([pattern.get(k, 0.0) for k in feature_keys])
        
        # Normalize
        feature_vector_norm = (feature_vector - self.feature_mean) / self.feature_std
        
        # Project to reduced dimensions
        compressed_vector = self.projection_matrix.T @ feature_vector_norm
        
        # Apply sparsity threshold
        compressed_vector[np.abs(compressed_vector) < self.sparsity_threshold] = 0.0
        
        # Quantize
        compressed_vector_quantized = self._quantize(compressed_vector)
        
        # Create compressed pattern
        compressed = CompressedPattern(
            pattern_id=pattern_id,
            compressed_features=compressed_vector_quantized,
            decision=decision,
            confidence=confidence,
            feature_keys=feature_keys,
            compression_metadata={
                'original_dimensions': len(feature_keys),
                'compressed_dimensions': self.target_dimensions,
                'quantization_bits': self.quantization_bits,
                'sparsity_threshold': self.sparsity_threshold
            }
        )
        
        # Update statistics
        self.total_compressed += 1
        original_size = len(feature_keys) * 8  # Assume 64-bit floats
        compressed_size = compressed.get_size_bytes()
        ratio = compressed_size / original_size if original_size > 0 else 1.0
        self.compression_ratios.append(ratio)
        
        return compressed
    
    def decompress(self, compressed: CompressedPattern) -> Dict[str, float]:
        """
        Reconstruct pattern from compressed form.
        
        Note: This is a lossy reconstruction. Some information is lost in compression.
        
        Args:
            compressed: Compressed pattern to reconstruct
            
        Returns:
            Reconstructed feature dict (approximate)
        """
        if not self.is_fitted:
            raise RuntimeError("Compressor not fitted. Call fit() first.")
        
        # Dequantize
        compressed_vector = self._dequantize(compressed.compressed_features)
        
        # Project back to original space
        reconstructed_norm = self.projection_matrix @ compressed_vector
        
        # Denormalize
        reconstructed = reconstructed_norm * self.feature_std + self.feature_mean
        
        # Convert back to dict
        reconstructed_dict = {
            k: float(reconstructed[i])
            for i, k in enumerate(compressed.feature_keys)
        }
        
        self.total_decompressed += 1
        
        return reconstructed_dict
    
    def get_compression_ratio(self) -> float:
        """
        Get average compression ratio.
        
        Returns:
            Average compression ratio (e.g., 0.4 = 60% size reduction)
        """
        if not self.compression_ratios:
            return 1.0
        return float(np.mean(self.compression_ratios))
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get compression statistics.
        
        Returns:
            Dictionary with compression metrics
        """
        return {
            'total_compressed': self.total_compressed,
            'total_decompressed': self.total_decompressed,
            'avg_compression_ratio': self.get_compression_ratio(),
            'target_dimensions': self.target_dimensions,
            'is_fitted': self.is_fitted,
            'quantization_bits': self.quantization_bits
        }
    
    def _quantize(self, vector: np.ndarray) -> np.ndarray:
        """
        Quantize vector to reduce precision.
        
        Args:
            vector: Vector to quantize
            
        Returns:
            Quantized vector
        """
        # Map to quantization levels
        max_val = np.max(np.abs(vector)) + 1e-8
        levels = 2 ** self.quantization_bits
        
        # Quantize
        quantized = np.round(vector / max_val * (levels // 2)) / (levels // 2) * max_val
        
        return quantized
    
    def _dequantize(self, vector: np.ndarray) -> np.ndarray:
        """
        Dequantize vector (no-op, already in float form).
        
        Args:
            vector: Quantized vector
            
        Returns:
            Dequantized vector (same as input in this implementation)
        """
        return vector
