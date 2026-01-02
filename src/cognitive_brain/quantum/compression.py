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

import logging
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Any, Optional


# Configure logging
logger = logging.getLogger(__name__)


# Constants
DEFAULT_QUANTIZATION_BITS = 8
DEFAULT_SPARSITY_THRESHOLD = 0.01
EPSILON_STABILITY = 1e-8  # For numerical stability in calculations


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
    Enhanced pattern compression system for efficient LTM storage.
    
    Compression Strategy:
    1. Adaptive dimensionality reduction (target: 65% reduction, variance-based)
    2. Variable quantization (4-8 bits based on feature importance)
    3. Sparse representation (remove near-zero features)
    4. Feature importance weighting
    
    Target: 70% overall size reduction while maintaining >95% reconstruction accuracy.
    
    Enhancements (Phase 8.1.1):
    - Adaptive PCA: Retain 95% variance instead of fixed 50% dimensions
    - Variable quantization: Use fewer bits for less important features
    - Feature importance scoring for intelligent compression
    """
    
    def __init__(self, target_dimensions: Optional[int] = None, 
                 quantization_bits: int = 8,
                 sparsity_threshold: float = 0.01,
                 variance_threshold: float = 0.95):
        """
        Initialize enhanced pattern compressor.
        
        Args:
            target_dimensions: Target reduced dimensionality (None = auto, variance-based)
            quantization_bits: Max bits for value quantization (default: 8-bit)
            sparsity_threshold: Threshold below which features are zeroed (default: 0.01)
            variance_threshold: Variance to retain in adaptive PCA (default: 0.95)
        """
        self.target_dimensions = target_dimensions
        self.quantization_bits = quantization_bits
        self.sparsity_threshold = sparsity_threshold
        self.variance_threshold = variance_threshold
        
        # Learned compression parameters
        self.feature_mean: Optional[np.ndarray] = None
        self.feature_std: Optional[np.ndarray] = None
        self.projection_matrix: Optional[np.ndarray] = None
        self.feature_importance: Optional[np.ndarray] = None  # New: importance scores
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
            patterns: List of feature dicts to learn from. All patterns must share
                the exact same set of feature keys; patterns with mismatched keys
                will cause a ValueError to be raised.
        """
        if not patterns:
            raise ValueError("Cannot fit on empty pattern list")
        
        # Convert patterns to matrix and validate key consistency
        feature_keys = sorted(patterns[0].keys())
        base_keys_set = set(feature_keys)
        
        for idx, p in enumerate(patterns[1:], start=1):
            current_keys = set(p.keys())
            if current_keys != base_keys_set:
                missing = sorted(base_keys_set - current_keys)
                extra = sorted(current_keys - base_keys_set)
                raise ValueError(
                    f"All patterns must share the same feature keys. "
                    f"Pattern at index {idx} has mismatched keys. "
                    f"Missing keys: {missing}; Extra keys: {extra}"
                )
        
        X = np.array([[p.get(k, 0.0) for k in feature_keys] for p in patterns])
        
        # Store feature keys for later use
        self.feature_keys = feature_keys
        
        # Calculate statistics
        self.feature_mean = np.mean(X, axis=0)
        feature_std_raw = np.std(X, axis=0)
        
        # Handle zero-variance features
        # Features with zero variance get std=1.0 to avoid division issues
        # (they won't contribute to compression anyway)
        self.feature_std = np.where(
            feature_std_raw < EPSILON_STABILITY,
            1.0,  # Set to 1.0 for zero-variance features
            feature_std_raw + EPSILON_STABILITY  # Add epsilon for numerical stability
        )
        
        # Normalize
        X_norm = (X - self.feature_mean) / self.feature_std
        
        # Compute covariance matrix
        cov_matrix = np.cov(X_norm.T)
        
        # Eigen decomposition
        eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
        
        # Sort by eigenvalues (descending)
        # Reorder eigenvalues to match sorted eigenvectors
        idx = eigenvalues.argsort()[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]
        
        # Calculate explained variance for adaptive dimension selection
        explained_variance_ratio = eigenvalues / eigenvalues.sum()
        
        # ENHANCEMENT: Adaptive PCA based on variance threshold
        if self.target_dimensions is None:
            # Find minimum dimensions to retain variance_threshold (default 95%)
            cumulative_variance = np.cumsum(explained_variance_ratio)
            self.target_dimensions = np.argmax(cumulative_variance >= self.variance_threshold) + 1
            # Ensure at least 1 dimension and at most 65% reduction (35% of original)
            min_dims = 1
            max_dims = max(1, int(X.shape[1] * 0.35))  # 65% reduction target
            self.target_dimensions = max(min_dims, min(self.target_dimensions, max_dims))
        
        # Calculate feature importance scores based on loadings
        # Higher importance = more contribution to top principal components
        loadings = eigenvectors[:, :self.target_dimensions]
        self.feature_importance = np.sum(np.abs(loadings), axis=1)
        self.feature_importance /= self.feature_importance.sum()  # Normalize
        
        # Log compression info
        actual_variance = explained_variance_ratio[:self.target_dimensions].sum()
        reduction_pct = (1 - self.target_dimensions / X.shape[1]) * 100
        logger.info(
            f"Enhanced compression: {X.shape[1]}→{self.target_dimensions} dimensions "
            f"({reduction_pct:.1f}% reduction), retaining {actual_variance:.1%} variance"
        )
        
        # Select top principal components
        self.projection_matrix = eigenvectors[:, :self.target_dimensions]
        
        self.is_fitted = True
    
    def get_importance_scores(self) -> Dict[str, float]:
        """
        Get feature importance scores after fitting.
        
        Returns:
            Dictionary mapping feature names to importance scores (0.0-1.0)
            
        Raises:
            RuntimeError: If compressor has not been fitted yet
        """
        if not self.is_fitted or self.feature_importance is None:
            raise RuntimeError("Compressor must be fitted before getting importance scores")
        
        return {
            feature: importance 
            for feature, importance in zip(self.feature_keys, self.feature_importance)
        }
    
    def compress(self, pattern: Dict[str, float], 
                 pattern_id: str,
                 decision: str,
                 confidence: float) -> CompressedPattern:
        """
        Compress pattern for LTM storage with enhanced variable quantization.
        
        Steps:
        1. Extract feature vector in consistent order
        2. Normalize features
        3. Project to lower-dimensional space (PCA)
        4. Apply variable quantization based on feature importance
        5. Apply sparsity threshold
        
        Enhancements:
        - Variable quantization: 4-bit for low importance, 8-bit for high importance
        - Importance-weighted precision allocation
        
        Args:
            pattern: Feature dictionary
            pattern_id: Pattern identifier
            decision: Decision associated with pattern
            confidence: Confidence score
            
        Returns:
            Compressed pattern for LTM storage
            
        Raises:
            RuntimeError: If compressor has not been fitted yet
        """
        if not self.is_fitted:
            raise RuntimeError("Compressor must be fitted before compressing patterns")
        
        if self.projection_matrix is None:
            raise RuntimeError("Projection matrix is None - fit() may have failed")
        
        # Extract features in consistent order
        feature_vec = np.array([pattern.get(k, 0.0) for k in self.feature_keys])
        
        # Normalize
        normalized = (feature_vec - self.feature_mean) / self.feature_std
        
        # Project to lower-dimensional space
        compressed_vec = self.projection_matrix.T @ normalized
        
        # ENHANCEMENT: Variable quantization based on component importance
        # Components with higher variance (earlier in PCA) get more bits
        component_importance = np.linspace(1.0, 0.5, len(compressed_vec))  # Decay from 1.0 to 0.5
        variable_bits = (self.quantization_bits * component_importance).astype(int)
        variable_bits = np.clip(variable_bits, 4, self.quantization_bits)  # 4-8 bit range
        
        # Apply variable quantization per component
        quantized = np.zeros_like(compressed_vec)
        for i, (val, bits) in enumerate(zip(compressed_vec, variable_bits)):
            max_val = 2 ** (bits - 1) - 1  # Leave 1 bit for sign
            quantized[i] = np.clip(np.round(val * max_val) / max_val, -1.0, 1.0)
        
        # Apply sparsity threshold
        quantized[np.abs(quantized) < self.sparsity_threshold] = 0.0
        
        # Create compressed pattern
        compressed = CompressedPattern(
            pattern_id=pattern_id,
            compressed_features=quantized,
            decision=decision,
            confidence=confidence,
            feature_keys=self.feature_keys,
            compression_metadata={
                "original_dims": len(self.feature_keys),
                "compressed_dims": len(quantized),
                "variable_bits": variable_bits.tolist(),
                "sparsity": float(np.sum(quantized == 0) / len(quantized))
            }
        )
        
        # Calculate and track compression ratio
        original_size = len(self.feature_keys) * 8  # 64-bit (8 bytes) per feature
        # Compute logical compressed size based on variable quantization
        compressed_size = sum(variable_bits) / 8.0  # Convert bits to bytes
        
        compression_ratio = 1.0 - (compressed_size / original_size)
        self.compression_ratios.append(compression_ratio)
        self.total_compressed += 1
        
        logger.debug(
            f"Compressed pattern {pattern_id}: {original_size}→{compressed_size:.1f} bytes "
            f"({compression_ratio:.1%} reduction, {compressed.compression_metadata['sparsity']:.1%} sparse)"
        )
        
        return compressed
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
        
        # Extract features in consistent order (use stored feature keys)
        feature_vector = np.array([pattern.get(k, 0.0) for k in self.feature_keys])
        
        # Validate dimensions match training data
        expected_length = len(self.feature_mean)
        if len(feature_vector) != expected_length:
            raise ValueError(
                f"Pattern dimension mismatch: got {len(feature_vector)} features, "
                f"expected {expected_length} (from training data)"
            )
        
        # Normalize
        feature_vector_norm = (feature_vector - self.feature_mean) / self.feature_std
        
        # Project to reduced dimensions
        compressed_vector = self.projection_matrix.T @ feature_vector_norm
        
        # Apply sparsity threshold
        compressed_vector[np.abs(compressed_vector) < self.sparsity_threshold] = 0.0
        
        # Quantize
        compressed_vector_quantized = self._quantize(compressed_vector)
        
        # Create compressed pattern (use stored feature keys)
        compressed = CompressedPattern(
            pattern_id=pattern_id,
            compressed_features=compressed_vector_quantized,
            decision=decision,
            confidence=confidence,
            feature_keys=self.feature_keys,
            compression_metadata={
                'original_dimensions': len(self.feature_keys),
                'compressed_dimensions': self.target_dimensions,
                'quantization_bits': self.quantization_bits,
                'sparsity_threshold': self.sparsity_threshold
            }
        )
        
        # Update statistics with logical compression ratio
        # Note: We use logical size (based on quantization_bits) rather than actual
        # numpy storage size to measure compression effectiveness independent of implementation.
        # This gives a consistent metric across different storage backends.
        self.total_compressed += 1
        original_size = len(self.feature_keys) * 8  # 64-bit floats (logical)
        compressed_size = self.target_dimensions * (self.quantization_bits / 8.0)  # Logical compressed size
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
